#!/usr/bin/env python3
"""R269 locked London Asian-range sweep/reclaim reversal; local computation only."""
from __future__ import annotations
import json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd

PIP = 0.0001
EXTRA_COSTS = [0.0, 0.5, 1.0, 2.0]
START_EQUITY = 6000.0
RISK_FRACTION = 0.0025
LOSS_FLOOR = 5400.0
BOOT_REPS = 10000
BOOT_SEED = 2692026
BLOCK_WEEKS = 4
DATA_DIR = Path('/mnt/data/eurusd_m1_2016_2025')
ZIP_PATH = Path('/mnt/data/EURUSD-M1-Dukascopy-BID-ASK-2016-2025.zip')
OUT = Path('/mnt/data/R269_London_Asian_Sweep_Results')


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def read_side(path: Path):
    raw = pd.read_csv(path, compression='infer', dtype={'timestamp':'int64', 'open':'float64','high':'float64','low':'float64','close':'float64'})
    raw.columns = [str(c).replace('\ufeff','').strip().lower() for c in raw.columns]
    required = {'timestamp','open','high','low','close'}
    if not required.issubset(raw.columns):
        raise ValueError(f'{path.name}: missing columns {required - set(raw.columns)}')
    idx = pd.to_datetime(raw['timestamp'], unit='ms', utc=True, errors='coerce')
    bad_ts = int(idx.isna().sum())
    vals = raw[['open','high','low','close']].to_numpy(dtype=np.float64)
    finite = np.isfinite(vals).all(axis=1)
    row_valid = finite & (vals[:,1] >= vals[:,[0,3]].max(axis=1)) & (vals[:,2] <= vals[:,[0,3]].min(axis=1)) & (vals[:,1] >= vals[:,2]) & idx.notna().to_numpy()
    invalid_ohlc = int((~row_valid).sum())
    q = pd.DataFrame(vals[row_valid], columns=['Open','High','Low','Close'], index=pd.DatetimeIndex(idx[row_valid], name='timestamp_utc'))
    q.sort_index(inplace=True)
    dup = int(q.index.duplicated(keep='last').sum())
    q = q.loc[~q.index.duplicated(keep='last')]
    info = {'raw_rows': int(len(raw)), 'bad_timestamp_rows': bad_ts, 'invalid_rows_removed': invalid_ohlc,
            'duplicate_timestamps_removed': dup, 'valid_unique_rows': int(len(q)),
            'start_utc': q.index[0].isoformat(), 'end_utc': q.index[-1].isoformat(),
            'sha256': sha256(path)}
    return q, info


def metric(trades: list[dict], cost: float):
    if not trades:
        return {'trades': 0, 'PF_R': None, 'net_R': 0.0, 'mean_R': None,
                'net_pips': 0.0, 'PF_pips': None, 'win_rate': None,
                'mean_reward_risk_at_entry': None, 'max_closed_equity_DD_R': 0.0}
    net_r = np.array([(t['gross_pips'] - cost) / t['risk_pips'] for t in trades], dtype=float)
    net_p = np.array([t['gross_pips'] - cost for t in trades], dtype=float)
    gp_r, gl_r = net_r[net_r > 0].sum(), -net_r[net_r < 0].sum()
    gp_p, gl_p = net_p[net_p > 0].sum(), -net_p[net_p < 0].sum()
    eq = np.cumsum(net_r)
    peak = np.maximum.accumulate(np.r_[0.0, eq])[1:]
    dd = float(np.max(peak - eq)) if len(eq) else 0.0
    return {'trades': int(len(trades)),
            'PF_R': float(gp_r/gl_r) if gl_r > 0 else ('INF' if gp_r > 0 else None),
            'net_R': float(net_r.sum()), 'mean_R': float(net_r.mean()),
            'net_pips': float(net_p.sum()),
            'PF_pips': float(gp_p/gl_p) if gl_p > 0 else ('INF' if gp_p > 0 else None),
            'win_rate': float((net_r > 0).mean()),
            'mean_reward_risk_at_entry': float(np.mean([t['reward_risk'] for t in trades])),
            'max_closed_equity_DD_R': dd}


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    bid_path = DATA_DIR / 'eurusd_bid_M1_2016-2025.csv.gz'
    ask_path = DATA_DIR / 'eurusd_ask_M1_2016-2025.csv.gz'
    bid, bq = read_side(bid_path)
    ask, aq = read_side(ask_path)
    common = bid.index.intersection(ask.index).sort_values()
    unmatched_bid = int(len(bid.index.difference(common)))
    unmatched_ask = int(len(ask.index.difference(common)))
    bid, ask = bid.loc[common], ask.loc[common]
    idx = bid.index
    spread_open = (ask['Open'].to_numpy() - bid['Open'].to_numpy()) / PIP
    neg_spread = int((spread_open < -1e-8).sum())
    if neg_spread:
        raise RuntimeError(f'Negative Ask-Bid open spreads: {neg_spread}')
    bid_arr = {c: bid[c].to_numpy(dtype=np.float64) for c in ['Open','High','Low','Close']}
    ask_arr = {c: ask[c].to_numpy(dtype=np.float64) for c in ['Open','High','Low','Close']}
    local = idx.tz_convert('Europe/London')
    local_dates = np.asarray(local.date, dtype=object)
    local_minute = local.hour.to_numpy(dtype=np.int16) * 60 + local.minute.to_numpy(dtype=np.int16)
    weekday = local.weekday.to_numpy(dtype=np.int8) < 5
    starts = np.r_[0, np.flatnonzero(local_dates[1:] != local_dates[:-1]) + 1]
    ends = np.r_[starts[1:], len(idx)]
    idx_ns = idx.asi8
    trades = []
    diagnostics = {
        'days_seen': int(len(starts)), 'weekdays_seen': 0, 'days_no_asian_range': 0,
        'days_with_candidate_signal': 0, 'days_ambiguous_first_signal': 0,
        'raw_long_signal_bars': 0, 'raw_short_signal_bars': 0,
        'selected_first_signals': 0, 'missing_exact_delay_entry': 0,
        'pre_entry_stop_or_target_invalidations': 0, 'entry_spread_rejects': 0,
        'entry_open_invalidations': 0, 'reward_risk_rejects': 0,
        'no_trade_after_rr_or_filters': 0, 'end_of_data_censored': 0,
        'stop_gap_exits': 0, 'stop_exits': 0, 'target_exits': 0, 'time_exits': 0,
        'ambiguous_intrabar_stop_first': 0
    }
    for ds, de in zip(starts, ends):
        if ds >= de or not weekday[ds]:
            continue
        diagnostics['weekdays_seen'] += 1
        mday = local_minute[ds:de]
        asi = np.flatnonzero(mday < 8*60)
        if len(asi) == 0:
            diagnostics['days_no_asian_range'] += 1
            continue
        a0, a1 = ds + int(asi[0]), ds + int(asi[-1]) + 1
        range_high = float(np.max(bid_arr['High'][a0:a1]))
        range_low = float(np.min(bid_arr['Low'][a0:a1]))
        if not np.isfinite(range_high + range_low) or range_high <= range_low:
            diagnostics['days_no_asian_range'] += 1
            continue
        day_mid = (range_high + range_low) / 2.0
        sess = np.flatnonzero((mday >= 8*60) & (mday < 12*60))
        if len(sess) == 0:
            continue
        sel = None
        ambiguous = False
        for j0 in sess:
            i = ds + int(j0)
            is_long = bid_arr['Low'][i] <= range_low - 2.0*PIP and bid_arr['Close'][i] > range_low
            is_short = bid_arr['High'][i] >= range_high + 2.0*PIP and bid_arr['Close'][i] < range_high
            if is_long:
                diagnostics['raw_long_signal_bars'] += 1
            if is_short:
                diagnostics['raw_short_signal_bars'] += 1
            if is_long or is_short:
                diagnostics['days_with_candidate_signal'] += 1
                if is_long and is_short:
                    diagnostics['days_ambiguous_first_signal'] += 1
                    ambiguous = True
                else:
                    sel = (i, 1 if is_long else -1)
                break
        if ambiguous or sel is None:
            continue
        si, direction = sel
        diagnostics['selected_first_signals'] += 1
        entry_ns = idx_ns[si] + 6 * 60 * 1_000_000_000
        ei = int(np.searchsorted(idx_ns, entry_ns))
        if ei >= len(idx_ns) or idx_ns[ei] != entry_ns:
            diagnostics['missing_exact_delay_entry'] += 1
            continue
        if ei <= si:
            diagnostics['entry_open_invalidations'] += 1
            continue
        if direction == 1:
            stop = float(bid_arr['Low'][si] - PIP)
            target = float(day_mid)
            pre_hi = bid_arr['High'][si+1:ei]
            pre_lo = bid_arr['Low'][si+1:ei]
            if len(pre_hi) and (np.any(pre_lo <= stop) or np.any(pre_hi >= target)):
                diagnostics['pre_entry_stop_or_target_invalidations'] += 1
                continue
            if bid_arr['Open'][ei] <= stop or bid_arr['Open'][ei] >= target:
                diagnostics['entry_open_invalidations'] += 1
                continue
            entry = float(ask_arr['Open'][ei])
            risk_pips = (entry - stop) / PIP
            reward_pips = (target - entry) / PIP
        else:
            stop = float(bid_arr['High'][si] + PIP)
            target = float(day_mid)
            pre_hi = ask_arr['High'][si+1:ei]
            pre_lo = ask_arr['Low'][si+1:ei]
            if len(pre_hi) and (np.any(pre_hi >= stop) or np.any(pre_lo <= target)):
                diagnostics['pre_entry_stop_or_target_invalidations'] += 1
                continue
            if ask_arr['Open'][ei] >= stop or ask_arr['Open'][ei] <= target:
                diagnostics['entry_open_invalidations'] += 1
                continue
            entry = float(bid_arr['Open'][ei])
            risk_pips = (stop - entry) / PIP
            reward_pips = (entry - target) / PIP
        espread = float(spread_open[ei])
        if not np.isfinite(espread) or espread < 0 or espread > 1.5 + 1e-12:
            diagnostics['entry_spread_rejects'] += 1
            continue
        if not np.isfinite(risk_pips) or risk_pips <= 0 or not np.isfinite(reward_pips) or reward_pips / risk_pips < 1.0:
            diagnostics['reward_risk_rejects'] += 1
            continue
        deadline_ns = idx_ns[ei] + 240 * 60 * 1_000_000_000
        exit_i = None
        exit_price = None
        exit_reason = None
        last_j = min(len(idx_ns)-1, int(np.searchsorted(idx_ns, deadline_ns)))
        if last_j == len(idx_ns)-1 and idx_ns[last_j] < deadline_ns:
            diagnostics['end_of_data_censored'] += 1
            continue
        for j in range(ei, last_j+1):
            if j > ei and idx_ns[j] >= deadline_ns:
                exit_i = j
                exit_price = float(bid_arr['Open'][j] if direction == 1 else ask_arr['Open'][j])
                exit_reason = 'TIME_240M_OPEN'
                diagnostics['time_exits'] += 1
                break
            xo = float(bid_arr['Open'][j] if direction == 1 else ask_arr['Open'][j])
            xh = float(bid_arr['High'][j] if direction == 1 else ask_arr['High'][j])
            xl = float(bid_arr['Low'][j] if direction == 1 else ask_arr['Low'][j])
            gap_stop = (xo <= stop) if direction == 1 else (xo >= stop)
            gap_target = (xo >= target) if direction == 1 else (xo <= target)
            if gap_stop:
                exit_i, exit_price, exit_reason = j, min(xo, stop) if direction == 1 else max(xo, stop), 'STOP_GAP'
                diagnostics['stop_gap_exits'] += 1
                break
            stop_hit = (xl <= stop) if direction == 1 else (xh >= stop)
            target_hit = (xh >= target) if direction == 1 else (xl <= target)
            if stop_hit and target_hit:
                diagnostics['ambiguous_intrabar_stop_first'] += 1
                exit_i, exit_price, exit_reason = j, stop, 'STOP_AMBIGUOUS_STOP_FIRST'
                diagnostics['stop_exits'] += 1
                break
            if stop_hit:
                exit_i, exit_price, exit_reason = j, stop, 'STOP'
                diagnostics['stop_exits'] += 1
                break
            if target_hit or gap_target:
                exit_i, exit_price, exit_reason = j, target, 'TARGET'
                diagnostics['target_exits'] += 1
                break
        if exit_i is None:
            exit_i = last_j
            exit_price = float(bid_arr['Open'][exit_i] if direction == 1 else ask_arr['Open'][exit_i])
            exit_reason = 'TIME_240M_OPEN'
            diagnostics['time_exits'] += 1
        gross_pips = direction * (exit_price - entry) / PIP
        trades.append({
            'trade_id': len(trades)+1, 'local_date': str(local[si].date()),
            'signal_utc': idx[si].isoformat(), 'signal_london': local[si].isoformat(),
            'entry_utc': idx[ei].isoformat(), 'entry_london': local[ei].isoformat(),
            'exit_utc': idx[exit_i].isoformat(), 'exit_london': local[exit_i].isoformat(),
            'direction': 'LONG' if direction == 1 else 'SHORT',
            'asian_high_bid': range_high, 'asian_low_bid': range_low, 'asian_mid_bid': target,
            'signal_bar_extreme_bid': float(bid_arr['Low'][si] if direction == 1 else bid_arr['High'][si]),
            'entry_price': entry, 'entry_spread_pips': espread, 'stop_price': stop,
            'target_price': target, 'risk_pips': risk_pips, 'reward_pips': reward_pips,
            'reward_risk': reward_pips/risk_pips, 'gross_pips': gross_pips,
            'exit_price': exit_price, 'exit_reason': exit_reason,
            'holding_minutes': (idx[exit_i]-idx[ei]).total_seconds()/60.0, 'entry_year': int(local[ei].year)
        })
    tdf = pd.DataFrame(trades)
    def get_trades(mask):
        return tdf.loc[mask].to_dict('records') if len(tdf) else []
    periods = {
        'discovery_2016_2020': get_trades(tdf.entry_year.between(2016,2020)) if len(tdf) else [],
        'validation_2021': get_trades(tdf.entry_year.eq(2021)) if len(tdf) else [],
        'forward_2022_2025': get_trades(tdf.entry_year.between(2022,2025)) if len(tdf) else []
    }
    results = {p: {f'extra_cost_{c:g}_pip': metric(ts,c) for c in EXTRA_COSTS} for p,ts in periods.items()}
    annual = []
    for year in range(2016,2026):
        ts = get_trades(tdf.entry_year.eq(year)) if len(tdf) else []
        annual.append({'year': year, **{f'extra_cost_{c:g}_pip': metric(ts,c) for c in EXTRA_COSTS}})
    forward = periods['forward_2022_2025']
    start = pd.Timestamp('2022-01-01T00:00:00Z')
    end = pd.Timestamp('2026-01-01T00:00:00Z')
    nweeks = int(np.ceil((end-start).total_seconds()/(7*24*3600)))
    weekly = np.zeros(nweeks, dtype=float)
    for t in forward:
        ti = pd.Timestamp(t['entry_utc'])
        wi = int((ti-start).total_seconds() // (7*24*3600))
        if 0 <= wi < nweeks:
            weekly[wi] += (float(t['gross_pips'])-1.0)/float(t['risk_pips'])
    rng = np.random.default_rng(BOOT_SEED)
    nblocks = int(np.ceil(nweeks/BLOCK_WEEKS))
    boot_means = np.empty(BOOT_REPS)
    for b in range(BOOT_REPS):
        starts_b = rng.integers(0,nweeks,size=nblocks)
        sample_idx = np.concatenate([(s+np.arange(BLOCK_WEEKS))%nweeks for s in starts_b])[:nweeks]
        boot_means[b] = weekly[sample_idx].mean()
    bootstrap = {
        'weeks_in_forward': int(nweeks), 'trades': len(forward), 'resamples': BOOT_REPS,
        'seed': BOOT_SEED, 'block_weeks': BLOCK_WEEKS,
        'mean_weekly_net_R_at_plus1pip': float(weekly.mean()),
        'probability_positive_bootstrap_mean': float((boot_means>0).mean()),
        'ci95_mean_weekly_net_R': [float(np.quantile(boot_means,.025)), float(np.quantile(boot_means,.975))]
    }
    weekday_gap = np.diff(idx_ns) / (60*1_000_000_000)
    quality = {
        'source_feed': 'Dukascopy via dukascopy-node GitHub data-only action',
        'artifact_id': 11959096102, 'artifact_zip_name': ZIP_PATH.name,
        'artifact_zip_size_bytes': ZIP_PATH.stat().st_size, 'artifact_zip_sha256': sha256(ZIP_PATH),
        'bid': bq, 'ask': aq, 'common_quote_timestamps': int(len(idx)),
        'unmatched_bid_timestamps': unmatched_bid, 'unmatched_ask_timestamps': unmatched_ask,
        'start_common_utc': idx[0].isoformat(), 'end_common_utc': idx[-1].isoformat(),
        'gaps_over_one_minute': int((weekday_gap>1).sum()),
        'total_missing_minutes_in_gaps': int(np.maximum(0, np.round(weekday_gap).astype(np.int64)-1).sum()),
        'negative_open_spreads': neg_spread,
        'entry_spread_pips': {'median':float(np.median(spread_open)), 'p95':float(np.quantile(spread_open,.95)), 'max':float(np.max(spread_open))},
        'note': 'All strategy metrics are 2016-2025 only; 2026 outcomes were not evaluated.'
    }
    pd.DataFrame(annual).to_csv(OUT/'R269_annual_metrics.csv',index=False)
    pd.DataFrame(trades).to_csv(OUT/'R269_trade_ledger.csv',index=False)
    pd.DataFrame([{ 'trade_id':t['trade_id'],'entry_utc':t['entry_utc'],'exit_utc':t['exit_utc'],
        'net_R_plus1pip':(float(t['gross_pips'])-1.0)/float(t['risk_pips']) } for t in sorted(forward,key=lambda q:q['entry_utc'])]).to_csv(OUT/'R269_forward_compound_equity.csv',index=False)
    eq, peak, max_dd_pct, breach = START_EQUITY, START_EQUITY, 0.0, None
    for t in sorted(forward,key=lambda q:q['entry_utc']):
        rnet = (float(t['gross_pips'])-1.0)/float(t['risk_pips'])
        eq = eq * (1.0 + RISK_FRACTION*rnet)
        peak = max(peak,eq)
        max_dd_pct = max(max_dd_pct,(peak-eq)/peak if peak else 1.0)
        if breach is None and eq <= LOSS_FLOOR:
            breach = {'time_utc':t['exit_utc'],'equity':eq,'trade_id':t['trade_id']}
    fwd_m1 = results['forward_2022_2025']['extra_cost_1_pip']
    fwd_m2 = results['forward_2022_2025']['extra_cost_2_pip']
    disc = results['discovery_2016_2020']['extra_cost_1_pip']
    val = results['validation_2021']['extra_cost_1_pip']
    annual_ok = sum(1 for a in annual if 2022 <= a['year'] <= 2025 and a['extra_cost_1_pip']['net_R'] > 0 and isinstance(a['extra_cost_1_pip']['PF_R'], (int,float)) and a['extra_cost_1_pip']['PF_R'] > 1.0)
    gates = {
        'discovery_plus1pip_netR_positive_and_PF_R_ge_1_10': bool(disc['net_R']>0 and isinstance(disc['PF_R'],(int,float)) and disc['PF_R']>=1.10),
        'validation_plus1pip_netR_positive_and_PF_R_ge_1_10': bool(val['net_R']>0 and isinstance(val['PF_R'],(int,float)) and val['PF_R']>=1.10),
        'forward_plus1pip_at_least_100_trades_netR_positive_PF_R_ge_1_10': bool(fwd_m1['trades']>=100 and fwd_m1['net_R']>0 and isinstance(fwd_m1['PF_R'],(int,float)) and fwd_m1['PF_R']>=1.10),
        'at_least_3_of_4_forward_years_positive_and_PF_R_gt_1': bool(annual_ok>=3),
        'forward_bootstrap_CI_lower_gt_zero': bool(bootstrap['ci95_mean_weekly_net_R'][0]>0),
        'forward_plus2pip_netR_positive_and_PF_R_ge_1': bool(fwd_m2['net_R']>0 and isinstance(fwd_m2['PF_R'],(int,float)) and fwd_m2['PF_R']>=1.0),
        'forward_compound_closed_equity_never_crosses_5400_floor': bool(breach is None)
    }
    verdict = 'LULUS' if all(gates.values()) else 'GAGAL'
    result = {
        'experiment':'R269_LONDON_ASIAN_RANGE_SWEEP_RECLAIM', 'verdict':verdict,
        'rules_version':'R269_LONDON_ASIAN_SWEEP_PREREGISTRATION.md committed before this run',
        'execution':'Python local/container only; GitHub Actions used for raw-data collection only',
        'data_quality':quality, 'locked_rules':{
            'timezone':'Europe/London local time for day/session (DST-aware)', 'asian_range':'00:00-07:59 London local',
            'signal_window':'08:00-11:59 London local, weekdays', 'sweep_threshold_pips':2.0,
            'reclaim':'BID close back inside the relevant edge of the Asian range', 'one_first_signal_per_day':True,
            'delay_minutes_after_close':5, 'entry_open_timestamp_delta_from_signal_bar':6,
            'entry_spread_cap_pips':1.5, 'stop_buffer_beyond_signal_extreme_pips':1.0,
            'target':'midpoint of Asian BID range', 'minimum_reward_risk':1.0,
            'max_holding_elapsed_minutes':240, 'intrabar_ambiguity':'stop-first',
            'cost_stresses_pips':EXTRA_COSTS,'fractional_risk':RISK_FRACTION,'starting_equity':START_EQUITY,
            'static_loss_floor':LOSS_FLOOR
        },
        'diagnostics':diagnostics, 'segment_metrics':results, 'annual_metrics':annual,
        'forward_bootstrap_plus1pip':bootstrap,
        'forward_compounding_plus1pip':{'start_equity':START_EQUITY,'risk_fraction_per_trade':RISK_FRACTION,
            'ending_equity':float(eq),'return_pct':float((eq/START_EQUITY-1)*100),
            'closed_equity_max_drawdown_from_peak_pct':float(max_dd_pct*100),
            'static_loss_floor':LOSS_FLOOR,'first_floor_breach':breach,'trades':len(forward),
            'note':'Realized/closed equity only; floating drawdown and FundedNext daily-loss mechanics are not modeled.'},
        'gates':gates, 'limitations':[
            'Independent Dukascopy feed, not exact reproduction of the missing original HistData archive.',
            'M1 OHLC cannot reveal tick ordering inside a bar; same-bar stop/target uses conservative stop-first policy.',
            'The test does not verify live broker commission/slippage distribution, platform alert/order delay distribution, or exact funded server/DST and floating DLL/MLL behavior.',
            'A LULUS economic screen is not equivalent to funded-ready approval; these constraints must be tested separately.'
        ]
    }
    (OUT/'R269_results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n')
    (OUT/'R269_verdict.txt').write_text(verdict+'\n')
    print(json.dumps({'verdict':verdict,'data_quality':quality,'diagnostics':diagnostics,
                      'segments':results,'annual':annual,'bootstrap':bootstrap,
                      'compounding':result['forward_compounding_plus1pip'],'gates':gates,
                      'output_dir':str(OUT)},indent=2,allow_nan=False))

if __name__ == '__main__':
    run()
