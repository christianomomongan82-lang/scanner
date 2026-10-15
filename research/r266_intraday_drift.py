from pathlib import Path
import pandas as pd
import numpy as np
import json, hashlib

ROOT = Path('/mnt/data/r205_index_data')
OUT = Path('/mnt/data/R266_intraday_drift_results')
OUT.mkdir(exist_ok=True)
TZ = 'America/New_York'
COSTS = [2.0, 4.0, 6.0]
SPLITS = [
    ('discovery_2016_2020', '2016-01-01', '2021-01-01'),
    ('validation_2021', '2021-01-01', '2022-01-01'),
    ('forward_2022_2025', '2022-01-01', '2026-01-01'),
]


def load_daily(path, symbol):
    df = pd.read_csv(path, compression='infer')
    df.columns = [str(c).strip().lower() for c in df.columns]
    ts = pd.to_datetime(pd.to_numeric(df['timestamp'], errors='coerce'), unit='ms', utc=True, errors='coerce')
    df = df.assign(timestamp_utc=ts).dropna(subset=['timestamp_utc'])
    for c in ['open', 'high', 'low', 'close']:
        df[c] = pd.to_numeric(df[c], errors='coerce')
    df = df.dropna(subset=['open', 'high', 'low', 'close']).sort_values('timestamp_utc')
    duplicates = int(df['timestamp_utc'].duplicated(keep='last').sum())
    df = df.drop_duplicates('timestamp_utc', keep='last').copy()
    valid = (
        (df['high'] >= df[['open', 'close']].max(axis=1)) &
        (df['low'] <= df[['open', 'close']].min(axis=1)) &
        (df['high'] >= df[['open', 'close']].min(axis=1)) &
        (df['high'] >= df['low'])
    )
    invalid = int((~valid).sum())
    df = df.loc[valid].copy()
    df['timestamp_et'] = df['timestamp_utc'].dt.tz_convert(TZ)
    df['date_et'] = df['timestamp_et'].dt.date
    df['hhmm'] = df['timestamp_et'].dt.strftime('%H:%M')
    rth = df.loc[df['hhmm'].between('09:30', '15:55')].copy()
    grouped = rth.groupby('date_et', sort=True)
    counts = grouped.size()
    unique_times = grouped['hhmm'].nunique()
    complete_dates = counts.index[(counts == 78) & (unique_times == 78)]
    rc = rth[rth['date_et'].isin(complete_dates)]
    daily = rc.groupby('date_et', sort=True).agg(
        day_high=('high', 'max'), day_low=('low', 'min'),
        bar_count=('open', 'size')
    )
    def at_time(time, field):
        s = rc.loc[rc['hhmm'].eq(time)].set_index('date_et')[field]
        return s[~s.index.duplicated(keep='last')]
    daily['open_0930'] = at_time('09:30', 'open')
    daily['close_1255'] = at_time('12:55', 'close')
    daily['open_1300'] = at_time('13:00', 'open')
    daily['open_1305'] = at_time('13:05', 'open')
    daily['close_1555'] = at_time('15:55', 'close')
    daily = daily.dropna(subset=['open_0930', 'close_1255', 'open_1300', 'open_1305', 'close_1555']).sort_index()
    daily = daily.loc[[pd.Timestamp(d).weekday() < 5 for d in daily.index]].copy()
    daily = daily.loc[((daily.day_high - daily.day_low).abs() > 1e-12)].copy()
    daily.index = pd.Index(pd.to_datetime(daily.index.astype(str)), name='date')
    # The threshold at t only uses the previous 20 completed sessions; current day's range is shifted out.
    prev_close = daily['close_1555'].shift(1)
    daily['daily_range_bps'] = ((daily['day_high'] - daily['day_low']) / prev_close) * 10000.0
    daily['prior20_median_range_bps'] = daily['daily_range_bps'].shift(1).rolling(20, min_periods=20).median()
    daily['morning_move_bps'] = (daily['close_1255'] / daily['open_0930'] - 1.0) * 10000.0
    daily['threshold_bps'] = 0.5 * daily['prior20_median_range_bps']
    daily['signal'] = np.where(
        daily['morning_move_bps'].abs() >= daily['threshold_bps'],
        np.sign(daily['morning_move_bps']), 0.0
    )
    quality = {
        'symbol': symbol,
        'file': path.name,
        'input_rows': int(len(pd.read_csv(path, compression='infer'))),
        'valid_rows': int(len(df)),
        'duplicate_timestamps_removed': duplicates,
        'invalid_ohlc_removed': invalid,
        'sha256_file': hashlib.sha256(path.read_bytes()).hexdigest(),
        'start_utc': df['timestamp_utc'].min().isoformat(),
        'end_utc': df['timestamp_utc'].max().isoformat(),
        'rth_dates': int(rth['date_et'].nunique()),
        'complete_rth_days': int(len(daily)),
        'complete_rth_dates_with_valid_20day_threshold': int(daily['prior20_median_range_bps'].notna().sum()),
    }
    return daily, quality


def build_trades(delay):
    all_trades = []
    quality = {}
    for sym, filename in [('USA500', 'usa500idxusd_m5.csv.gz'), ('USATECH', 'usatechidxusd_m5.csv.gz')]:
        d, q = load_daily(ROOT / filename, sym)
        quality[sym] = q
        entry_col = 'open_1300' if delay == 'ideal' else 'open_1305'
        # Cut off before 2026 so no OOS outcomes/statistics are evaluated.
        d = d.loc[(d.index >= '2016-01-01') & (d.index < '2026-01-01')].copy()
        eligible = d.loc[(d['signal'] != 0) & d['prior20_median_range_bps'].notna()]
        for dt, r in eligible.iterrows():
            entry = float(r[entry_col])
            exit_px = float(r['close_1555'])
            direction = int(np.sign(r['signal']))
            if entry <= 0 or exit_px <= 0:
                continue
            gross_bps = direction * (exit_px / entry - 1.0) * 10000.0
            all_trades.append({
                'symbol': sym, 'entry_date': dt.strftime('%Y-%m-%d'), 'exit_date': dt.strftime('%Y-%m-%d'),
                'delay_mode': delay, 'direction': 'long' if direction > 0 else 'short',
                'morning_move_bps': float(r['morning_move_bps']),
                'prior20_median_range_bps': float(r['prior20_median_range_bps']),
                'threshold_bps': float(r['threshold_bps']),
                'entry_time_et': '13:00' if delay == 'ideal' else '13:05',
                'entry_price': entry, 'exit_price': exit_px, 'gross_bps': float(gross_bps),
            })
    trades = pd.DataFrame(all_trades)
    if len(trades):
        trades = trades.sort_values(['entry_date', 'symbol']).reset_index(drop=True)
    return trades, quality


def calc_metrics(trades, cost):
    x = trades.copy()
    if not len(x):
        return {'trades': 0, 'PF': None, 'gross_bps': 0.0, 'net_bps': 0.0, 'win_rate': None, 'max_cumulative_net_dd_bps': 0.0}
    x['net_bps'] = x['gross_bps'] - cost
    gp = float(x.loc[x['net_bps'] > 0, 'net_bps'].sum())
    gl = float(-x.loc[x['net_bps'] < 0, 'net_bps'].sum())
    pf = gp / gl if gl > 0 else (float('inf') if gp > 0 else None)
    # Aggregate both indexes by date before calculating combined-equity proxy DD.
    day_net = x.groupby('entry_date')['net_bps'].sum().sort_index().to_numpy(float)
    eq = np.cumsum(day_net)
    peak = np.maximum.accumulate(np.r_[0.0, eq])[1:]
    dd = float(np.max(peak - eq)) if len(eq) else 0.0
    return {
        'trades': int(len(x)), 'PF': None if pf is None or not np.isfinite(pf) else float(pf),
        'gross_bps': float(x['gross_bps'].sum()), 'net_bps': float(x['net_bps'].sum()),
        'win_rate': float((x['net_bps'] > 0).mean()), 'max_cumulative_net_dd_bps': dd,
        'mean_net_bps_per_trade': float(x['net_bps'].mean()),
    }


def period_table(trades):
    out = {}
    for name, start, end in SPLITS:
        subset = trades.loc[(trades['entry_date'] >= start) & (trades['entry_date'] < end)].copy()
        out[name] = {'combined': {f'cost_{int(c)}bps': calc_metrics(subset, c) for c in COSTS}}
        out[name]['by_symbol'] = {}
        for sym in ['USA500', 'USATECH']:
            st = subset.loc[subset['symbol'] == sym]
            out[name]['by_symbol'][sym] = {f'cost_{int(c)}bps': calc_metrics(st, c) for c in COSTS}
        if name == 'forward_2022_2025':
            out[name]['annual_combined'] = {}
            for y in range(2022, 2026):
                annual = subset.loc[subset['entry_date'].str[:4] == str(y)]
                out[name]['annual_combined'][str(y)] = {f'cost_{int(c)}bps': calc_metrics(annual, c) for c in COSTS}
    return out


def bootstrap_weekly(trades, cost, seed, reps=10000, block=4):
    start = pd.Timestamp('2022-01-01')
    end = pd.Timestamp('2026-01-01')
    nweeks = int(np.ceil((end - start).days / 7))
    weekly = np.zeros(nweeks, dtype=float)
    x = trades.loc[(trades['entry_date'] >= start.strftime('%Y-%m-%d')) & (trades['entry_date'] < end.strftime('%Y-%m-%d'))]
    for _, row in x.iterrows():
        dt = pd.Timestamp(row['entry_date'])
        idx = int((dt - start).days // 7)
        if 0 <= idx < nweeks:
            weekly[idx] += float(row['gross_bps']) - cost
    rng = np.random.default_rng(seed)
    nblocks = int(np.ceil(nweeks / block))
    boot_means = np.empty(reps, dtype=float)
    steps = np.arange(block)
    for i in range(reps):
        starts = rng.integers(0, nweeks, size=nblocks)
        ix = np.concatenate([(s + steps) % nweeks for s in starts])[:nweeks]
        boot_means[i] = weekly[ix].mean()
    return {
        'weeks_including_zero_trade_weeks': nweeks, 'reps': reps, 'seed': seed, 'block_weeks': block,
        'mean_weekly_net_bps': float(weekly.mean()),
        'probability_positive_mean': float((boot_means > 0).mean()),
        'ci95_mean_weekly_net_bps': [float(np.quantile(boot_means, 0.025)), float(np.quantile(boot_means, 0.975))],
    }


def main():
    outputs = {}
    quality = None
    for mode, seed in [('ideal', 2662026), ('delay5', 2662031)]:
        trades, q = build_trades(mode)
        quality = q
        trades.to_csv(OUT / f'R266_trades_{mode}.csv', index=False)
        p = period_table(trades)
        boot = bootstrap_weekly(trades, 4.0, seed)
        outputs[mode] = {
            'trade_count': int(len(trades)), 'periods': p, 'bootstrap_forward_at_4bps': boot,
            'by_exit_direction': trades['direction'].value_counts().to_dict() if len(trades) else {},
        }
    # Gate only the registered periods; 2026 trade performance is never summarized.
    for mode in ['ideal', 'delay5']:
        p = outputs[mode]['periods']
        discovery = p['discovery_2016_2020']['combined']['cost_4bps']
        validation = p['validation_2021']['combined']['cost_4bps']
        forward = p['forward_2022_2025']['combined']['cost_4bps']
        annual = p['forward_2022_2025']['annual_combined']
        bysym = p['forward_2022_2025']['by_symbol']
        boot = outputs[mode]['bootstrap_forward_at_4bps']
        gates = {
            'discovery_net_positive_pf_ge_1_10': discovery['net_bps'] > 0 and discovery['PF'] is not None and discovery['PF'] >= 1.10,
            'validation_net_positive_pf_ge_1_10': validation['net_bps'] > 0 and validation['PF'] is not None and validation['PF'] >= 1.10,
            'forward_trade_count_ge_100_and_net_positive_pf_ge_1_10': forward['trades'] >= 100 and forward['net_bps'] > 0 and forward['PF'] is not None and forward['PF'] >= 1.10,
            'all_forward_years_pf_ge_1_00': all(v['cost_4bps']['PF'] is not None and v['cost_4bps']['PF'] >= 1.00 for v in annual.values()),
            'both_instruments_forward_pf_ge_1_00': all(bysym[s]['cost_4bps']['PF'] is not None and bysym[s]['cost_4bps']['PF'] >= 1.00 for s in ['USA500', 'USATECH']),
            'entry_mode_bootstrap_95ci_lower_above_zero': boot['ci95_mean_weekly_net_bps'][0] > 0,
        }
        outputs[mode]['gates'] = gates
    delay_fw = outputs['delay5']['periods']['forward_2022_2025']['combined']['cost_4bps']
    outputs['delay5']['gates']['delay5_forward_net_positive_pf_ge_1_10'] = delay_fw['net_bps'] > 0 and delay_fw['PF'] is not None and delay_fw['PF'] >= 1.10
    boot_both = all(outputs[m]['bootstrap_forward_at_4bps']['ci95_mean_weekly_net_bps'][0] > 0 for m in ['ideal', 'delay5'])
    for m in ['ideal', 'delay5']:
        outputs[m]['gates']['both_entry_modes_bootstrap_95ci_lower_above_zero'] = boot_both
    all_gates = all(all(g.values()) for g in [outputs['ideal']['gates'], outputs['delay5']['gates']])
    report = {
        'study': 'R266 U.S. index afternoon continuation after a strong morning',
        'date': '2026-10-16', 'status': 'COMPLETE', 'parameters_locked': True,
        'verdict': 'PASSED HISTORICAL SCREEN ONLY' if all_gates else 'FAILED',
        'data': {
            'source': 'Existing GitHub-sourced R205 BID-only M5 snapshots; local Python calculations',
            'instruments': quality, 'ask_side_available': False,
            'trading_evaluation_cutoff_exclusive': '2026-01-01', 'oos_2026_outcomes_inspected': False,
            'cost_scenarios_bps_per_trade': COSTS,
        },
        'rules': {
            'timezone': TZ, 'signal': 'sign of 09:30 open to 12:55 bar close morning return',
            'eligibility': 'absolute morning move >= 0.5 * median daily range bps from preceding 20 complete RTH sessions; current session excluded',
            'ideal_entry': '13:00 ET bar open after 12:55 bar closes', 'delay5_entry': '13:05 ET bar open',
            'exit': '15:55 ET bar close', 'max_trades_per_symbol_session': 1, 'overnight': False,
            'cost_scenarios_bps': COSTS,
        },
        'ideal': outputs['ideal'], 'delay5': outputs['delay5'],
        'gate_summary': {'all_gates_pass': all_gates, 'ideal_gates': outputs['ideal']['gates'], 'delay5_gates': outputs['delay5']['gates']},
        'limitations': [
            'BID-only data: ASK side, observed spreads, commissions and actual slippage are unavailable.',
            'Fixed 2/4/6 bps costs are stress assumptions, not measured live execution.',
            'No funded DLL/MLL/Quick Strike replay; this is only a historical edge screen.',
            'No 2026 outcome statistics were calculated or inspected.',
        ],
    }
    (OUT / 'R266_results.json').write_text(json.dumps(report, indent=2, allow_nan=False) + '\n')
    print(json.dumps(report, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
