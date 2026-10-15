#!/usr/bin/env python3
"""R260 local-only EURUSD H1 single-hour shock reversal research.
Reads a previously downloaded GitHub Actions artifact. Does not access network or GitHub Actions.
"""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

PIP = 0.0001
COSTS = (0.0, 0.5, 1.0, 2.0)
TRAIN_START = pd.Timestamp('2017-01-01', tz='UTC')
TRAIN_END = pd.Timestamp('2021-01-01', tz='UTC')
VALID_END = pd.Timestamp('2022-01-01', tz='UTC')
FORWARD_END = pd.Timestamp('2026-01-01', tz='UTC')
Q = 0.90
HOLD_HOURS = 6
RR = 1.0

def read_bars(path: Path):
    raw = pd.read_csv(path)
    raw.columns = [str(c).replace('\ufeff', '').strip().lower() for c in raw.columns]
    tc = next((c for c in ('timestamp', 'datetime', 'date') if c in raw.columns), None)
    if tc is None:
        raise ValueError(f'No timestamp column: {path}')
    t = pd.to_numeric(raw[tc], errors='coerce')
    if t.notna().mean() > .95:
        med = float(t.abs().median())
        unit = 'ms' if med >= 1e11 else ('s' if med >= 1e8 else None)
        if unit is None: raise ValueError(f'Unknown numeric timestamp unit in {path}')
        idx = pd.to_datetime(t, unit=unit, utc=True, errors='coerce')
    else:
        idx = pd.to_datetime(raw[tc], utc=True, errors='coerce')
    missing = {'open', 'high', 'low', 'close'} - set(raw.columns)
    if missing or idx.isna().any():
        raise ValueError(f'Invalid timestamp or missing OHLC columns: {path}; {missing}')
    d = raw[['open', 'high', 'low', 'close']].apply(pd.to_numeric, errors='coerce')
    d.columns = ['Open', 'High', 'Low', 'Close']
    d.index = pd.DatetimeIndex(idx, name='timestamp_utc')
    raw_count = len(d)
    d = d.replace([np.inf, -np.inf], np.nan).dropna().sort_index()
    duplicates = int(d.index.duplicated(keep='last').sum())
    d = d.loc[~d.index.duplicated(keep='last')]
    valid = (d.High >= d[['Open', 'Close']].max(axis=1)) & (d.Low <= d[['Open', 'Close']].min(axis=1)) & (d.High >= d.Low)
    invalid = int((~valid).sum())
    d = d.loc[valid]
    if d.empty: raise ValueError(f'No valid price rows in {path}')
    diag = {'raw_rows': raw_count, 'valid_rows': len(d), 'duplicate_timestamps_removed': duplicates,
            'invalid_ohlc_removed': invalid, 'start_utc': d.index[0].isoformat(),
            'end_utc': d.index[-1].isoformat(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    return d, diag

def period_trades(trades, start, end):
    return [t for t in trades if start <= pd.Timestamp(t['entry_utc']) < end and pd.Timestamp(t['exit_utc']) < end]

def metrics(trades, start, end, cost):
    a = period_trades(trades, start, end)
    vals = np.asarray([t['gross_pips'] - cost for t in a], dtype=float)
    weeks = max((end - start).total_seconds() / (7 * 24 * 3600), 1 / 7)
    gp = float(vals[vals > 0].sum()); gl = float(-vals[vals < 0].sum())
    return {'trades': int(len(vals)), 'PF': (gp / gl if gl > 0 else None),
            'net_pips': float(vals.sum()), 'mean_net_pips_per_trade': float(vals.mean()) if len(vals) else None,
            'win_rate': float(np.mean(vals > 0)) if len(vals) else None,
            'trades_per_week': float(len(vals) / weeks)}

def weekly_block_bootstrap(trades, start, end, cost=1.0, reps=5000, seed=260, block_weeks=4):
    weeks = int(np.ceil((end - start).total_seconds() / (7 * 24 * 3600)))
    weekly_net = np.zeros(weeks, dtype=float)
    a = period_trades(trades, start, end)
    for t in a:
        ts = pd.Timestamp(t['entry_utc'])
        w = int((ts - start).total_seconds() // (7 * 24 * 3600))
        if 0 <= w < weeks: weekly_net[w] += float(t['gross_pips']) - cost
    if weeks < block_weeks or not a: return {'trades': len(a), 'weeks': weeks, 'error': 'insufficient sample'}
    rng = np.random.default_rng(seed); block_count = int(np.ceil(weeks / block_weeks))
    estimates = np.empty(reps, dtype=float)
    for k in range(reps):
        picks = rng.integers(0, weeks, size=block_count)
        ix = np.concatenate([(s + np.arange(block_weeks)) % weeks for s in picks])[:weeks]
        estimates[k] = weekly_net[ix].mean()
    return {'trades': len(a), 'weeks': weeks, 'block_weeks': block_weeks, 'reps': reps, 'seed': seed,
            'observed_net_pips': float(weekly_net.sum()),
            'observed_mean_net_pips_per_week': float(weekly_net.mean()),
            'observed_mean_net_pips_per_trade': float(np.mean([t['gross_pips'] - cost for t in a])),
            'probability_mean_weekly_net_positive': float(np.mean(estimates > 0)),
            'bootstrap_95pct_ci_mean_weekly_net_pips': [float(np.quantile(estimates, .025)), float(np.quantile(estimates, .975))]}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', required=True, help='Folder with eurusd_bid_H1.csv and eurusd_ask_H1.csv from GitHub artifact 11916174401')
    ap.add_argument('--out-dir', default='research')
    args = ap.parse_args()
    data_dir, out_dir = Path(args.data_dir), Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    bid_path, ask_path = data_dir / 'eurusd_bid_H1.csv', data_dir / 'eurusd_ask_H1.csv'
    bid, bd = read_bars(bid_path); ask, ad = read_bars(ask_path)
    common = bid.index.intersection(ask.index).sort_values()
    if len(common) < 50000: raise ValueError(f'Insufficient common BID/ASK bars: {len(common)}')
    start, end = common.min().floor('h'), common.max().floor('h')
    ix = pd.date_range(start=start, end=end, freq='h')
    b, a = bid.reindex(ix), ask.reindex(ix)
    valid = b[['Open', 'High', 'Low', 'Close']].notna().all(axis=1) & a[['Open', 'High', 'Low', 'Close']].notna().all(axis=1)
    spread = (a.Open - b.Open) / PIP
    negative_spreads = int(((spread < -1e-8) & valid).sum())
    if negative_spreads: raise ValueError(f'Negative ASK-BID open spreads: {negative_spreads}')
    valid_train = valid & (ix >= TRAIN_START) & (ix < TRAIN_END)
    training_body_pips = (b.Close - b.Open).abs() / PIP
    training_values = training_body_pips.loc[valid_train & training_body_pips.notna()]
    if len(training_values) < 1000: raise ValueError(f'Insufficient threshold samples: {len(training_values)}')
    threshold = float(training_values.quantile(Q))
    body_pips = (b.Close - b.Open) / PIP
    body = body_pips.to_numpy(float); valid_arr = valid.to_numpy(bool)
    direction = np.zeros(len(ix), dtype=np.int8)
    large = valid_arr & (np.abs(body) >= threshold)
    direction[large & (body < 0)] = 1
    direction[large & (body > 0)] = -1
    ba = {c: b[c].to_numpy(float) for c in ('Open', 'High', 'Low', 'Close')}
    aa = {c: a[c].to_numpy(float) for c in ('Open', 'High', 'Low', 'Close')}
    trades = []
    skipped = {'overlap': 0, 'missing_entry_quote': 0, 'missing_time_exit_quote': 0,
               'invalid_stop_side': 0, 'risk_below_0_5_pip': 0, 'end_of_data': 0}
    last_exit_idx = -1
    for sig_i in np.flatnonzero(direction):
        sig_i = int(sig_i); entry_i = sig_i + 1
        if entry_i >= len(ix): skipped['end_of_data'] += 1; continue
        if entry_i <= last_exit_idx: skipped['overlap'] += 1; continue
        if not valid_arr[entry_i]: skipped['missing_entry_quote'] += 1; continue
        horizon = entry_i + HOLD_HOURS
        if horizon >= len(ix): skipped['end_of_data'] += 1; continue
        off = np.flatnonzero(valid_arr[horizon:])
        if not len(off): skipped['missing_time_exit_quote'] += 1; continue
        time_exit_i = horizon + int(off[0]); d = int(direction[sig_i])
        if d == 1:
            entry, stop = aa['Open'][entry_i], ba['Low'][sig_i]
            risk = entry - stop; target = entry + RR * risk
        else:
            entry, stop = ba['Open'][entry_i], aa['High'][sig_i]
            risk = stop - entry; target = entry - RR * risk
        if not np.isfinite(risk) or risk <= 0: skipped['invalid_stop_side'] += 1; continue
        if risk < 0.5 * PIP: skipped['risk_below_0_5_pip'] += 1; continue
        exit_i = None; exit_price = None; reason = None
        for j in range(entry_i, time_exit_i):
            if not valid_arr[j]: continue
            if d == 1:
                op, hi, lo = ba['Open'][j], ba['High'][j], ba['Low'][j]
                if op <= stop: exit_i, exit_price, reason = j, op, 'STOP_GAP'; break
                if lo <= stop: exit_i, exit_price, reason = j, stop, 'STOP'; break
                if hi >= target: exit_i, exit_price, reason = j, target, 'TARGET'; break
            else:
                op, hi, lo = aa['Open'][j], aa['High'][j], aa['Low'][j]
                if op >= stop: exit_i, exit_price, reason = j, op, 'STOP_GAP'; break
                if hi >= stop: exit_i, exit_price, reason = j, stop, 'STOP'; break
                if lo <= target: exit_i, exit_price, reason = j, target, 'TARGET'; break
        if exit_i is None:
            exit_i = time_exit_i
            exit_price = ba['Open'][exit_i] if d == 1 else aa['Open'][exit_i]
            reason = 'TIME'
        gross = (exit_price - entry) / PIP * d
        trades.append({'signal_utc': ix[sig_i].isoformat(), 'entry_utc': ix[entry_i].isoformat(),
                       'exit_utc': ix[exit_i].isoformat(), 'direction': 'LONG' if d == 1 else 'SHORT',
                       'entry_price': float(entry), 'exit_price': float(exit_price), 'stop_price': float(stop),
                       'risk_pips': float(risk / PIP), 'gross_pips': float(gross),
                       'gross_R': float(gross / (risk / PIP)), 'exit_reason': reason,
                       'signal_body_pips': float(abs(body[sig_i]))})
        last_exit_idx = exit_i
    periods = [('discovery_2017_2020', TRAIN_START, TRAIN_END), ('validation_2021', TRAIN_END, VALID_END),
               ('forward_2022_2025', VALID_END, FORWARD_END),
               ('oos_2026', FORWARD_END, ix[-1] + pd.Timedelta(hours=1))]
    report = {'status': 'COMPLETED', 'round': 'R260', 'verdict': 'GAGAL',
              'execution_location': 'local session/container; no backtest executed by GitHub Actions',
              'strategy': 'EURUSD H1 single-hour shock reversal',
              'source': {'github_artifact_id': 11916174401, 'artifact_name': 'R258-multihorizon-momentum-audit.zip',
                         'bid_file': bd, 'ask_file': ad},
              'locked_parameters': {'threshold_quantile': Q, 'threshold_fit_period_utc': ['2017-01-01', '2021-01-01'],
                         'threshold_body_abs_pips': threshold, 'signal': 'counter-direction after a large completed BID candle',
                         'entry': 'next exact H1 open', 'long_entry_exit': 'ASK entry, BID stop/target/time exit',
                         'short_entry_exit': 'BID entry, ASK stop/target/time exit', 'stop': 'signal candle executable-side extreme',
                         'target_R': RR, 'max_holding_hours': HOLD_HOURS, 'max_one_open_position': True,
                         'extra_cost_stress_pips': list(COSTS)},
              'data_quality': {'common_timestamps_before_grid': int(len(common)), 'grid_hours': int(len(ix)),
                         'valid_common_hours': int(valid.sum()), 'missing_or_incomplete_grid_hours': int((~valid).sum()),
                         'negative_open_spread_rows': negative_spreads, 'spread_pips_min': float(spread.loc[valid].min()),
                         'spread_pips_median': float(spread.loc[valid].median()), 'spread_pips_p95': float(spread.loc[valid].quantile(.95)),
                         'spread_pips_max': float(spread.loc[valid].max()), 'threshold_training_observations': int(len(training_values))},
              'diagnostics': {'signal_bars': int(np.count_nonzero(direction)), 'closed_trades': len(trades),
                         'skipped': skipped, 'exit_counts': {k: int(sum(t['exit_reason'] == k for t in trades)) for k in ('STOP_GAP', 'STOP', 'TARGET', 'TIME')}},
              'periods': {}, 'forward_annual': {}}
    for name, s, e in periods: report['periods'][name] = {str(c): metrics(trades, s, e, c) for c in COSTS}
    for y in range(2022, 2026):
        s, e = pd.Timestamp(f'{y}-01-01', tz='UTC'), pd.Timestamp(f'{y+1}-01-01', tz='UTC')
        report['forward_annual'][str(y)] = {str(c): metrics(trades, s, e, c) for c in COSTS}
    report['forward_bootstrap_plus_1pip'] = weekly_block_bootstrap(trades, VALID_END, FORWARD_END, 1.0)
    d = report['periods']['discovery_2017_2020']['1.0']; v = report['periods']['validation_2021']['1.0']
    f1 = report['periods']['forward_2022_2025']['1.0']; f2 = report['periods']['forward_2022_2025']['2.0']
    o = report['periods']['oos_2026']['1.0']
    annual_qual = [report['forward_annual'][str(y)]['1.0'] for y in range(2022, 2026)
                   if report['forward_annual'][str(y)]['1.0']['trades'] >= 20]
    ci = report['forward_bootstrap_plus_1pip'].get('bootstrap_95pct_ci_mean_weekly_net_pips', [None, None])
    gates = {'validation_trades_ge_50': v['trades'] >= 50,
      'validation_PF_ge_1_05_at_plus_1pip': v['PF'] is not None and v['PF'] >= 1.05,
      'discovery_PF_ge_1_00_at_plus_1pip': d['PF'] is not None and d['PF'] >= 1.00,
      'forward_trades_ge_150': f1['trades'] >= 150,
      'forward_PF_ge_1_10_at_plus_1pip': f1['PF'] is not None and f1['PF'] >= 1.10,
      'forward_PF_ge_1_05_at_plus_2pip': f2['PF'] is not None and f2['PF'] >= 1.05,
      'forward_frequency_ge_2_per_week': f1['trades_per_week'] >= 2.0,
      'every_forward_year_with_20plus_trades_PF_ge_1_at_plus_1pip': bool(annual_qual) and all(x['PF'] is not None and x['PF'] >= 1.0 for x in annual_qual),
      'bootstrap_95pct_lower_bound_weekly_net_gt_zero_at_plus_1pip': len(ci) == 2 and ci[0] is not None and ci[0] > 0,
      'oos_trades_ge_30': o['trades'] >= 30,
      'oos_PF_ge_1_00_at_plus_1pip': o['PF'] is not None and o['PF'] >= 1.00}
    report['acceptance_gates'] = {'rule': 'All preregistered gates are mandatory.', 'gates': gates,
                                  'forward_metrics_cost_1pip': f1, 'forward_metrics_cost_2pip': f2,
                                  'qualifying_annual_forward_cohorts_cost_1pip': annual_qual}
    report['verdict'] = 'LULUS' if all(gates.values()) else 'GAGAL'
    pd.DataFrame(trades).to_csv(out_dir / 'r260_local_shock_reversal_trades.csv', index=False)
    pd.DataFrame([{'year': y, 'extra_cost_pips': c, **m} for y, mm in report['forward_annual'].items() for c, m in mm.items()]).to_csv(out_dir / 'r260_local_shock_reversal_annual.csv', index=False)
    (out_dir / 'r260_local_shock_reversal_results.json').write_text(json.dumps(report, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps(report, indent=2, allow_nan=False))

if __name__ == '__main__':
    main()
