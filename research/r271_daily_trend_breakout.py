#!/usr/bin/env python3
"""R271 preregistered EURUSD daily 20-session breakout continuation backtest.
Calculations run locally only. See R271_DAILY_TREND_BREAKOUT_PREREGISTRATION.md.
"""
from __future__ import annotations
import json, hashlib, zipfile, gzip, shutil, math, os
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path('/mnt/data')
ZIP_PATH = Path(os.environ.get('R271_INPUT_ZIP', str(ROOT / 'eurusd-m1-2016-2025.zip')))
OUT = ROOT / 'r271_work'
OUT.mkdir(exist_ok=True)
PIP = 0.0001
NY = 'America/New_York'
COSTS = [0.0, 0.5, 1.0, 2.0]
BOOT_REPS = 10_000
BOOT_SEED = 2712026


def pf(values):
    a = np.asarray(values, dtype=float)
    pos, neg = a[a > 0].sum(), -a[a < 0].sum()
    return float(pos / neg) if neg > 0 else (None if pos == 0 else float('inf'))


def metrics(frame, cost):
    if frame.empty:
        return {'trades': 0, 'pf': None, 'net_r': 0.0, 'mean_r': None, 'median_r': None,
                'win_rate': None, 'gross_pf': None}
    vals = frame[f'net_r_{cost:g}'].to_numpy(float)
    gross = frame['gross_r'].to_numpy(float)
    return {'trades': int(len(frame)), 'pf': pf(vals), 'net_r': float(vals.sum()),
            'mean_r': float(vals.mean()), 'median_r': float(np.median(vals)),
            'win_rate': float((vals > 0).mean()), 'gross_pf': pf(gross)}


def session_index(local_ts: pd.DatetimeIndex) -> tuple[np.ndarray, np.ndarray]:
    # Label each FX session by the local calendar date on which it closes.
    local_naive = local_ts.tz_localize(None)
    bump = (local_ts.hour >= 17).astype(np.int8)
    session_days = (local_naive.normalize() + pd.to_timedelta(bump, unit='D')).to_numpy(dtype='datetime64[ns]')
    valid = pd.DatetimeIndex(session_days).dayofweek < 5
    return session_days, np.asarray(valid)


def main():
    if not ZIP_PATH.exists():
        raise FileNotFoundError(f'Input archive not found: {ZIP_PATH}; set R271_INPUT_ZIP if needed')
    zip_hash = hashlib.sha256(ZIP_PATH.read_bytes()).hexdigest()
    extracted = OUT / 'input'
    extracted.mkdir(exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH) as z:
        z.extract('eurusd_bid_M1_2016-2025.csv.gz', extracted)
        z.extract('eurusd_ask_M1_2016-2025.csv.gz', extracted)
        manifest = json.loads(z.read('manifest.json'))
    bid_path = extracted / 'eurusd_bid_M1_2016-2025.csv.gz'
    ask_path = extracted / 'eurusd_ask_M1_2016-2025.csv.gz'
    dtypes = {'timestamp': 'int64', 'open':'float32','high':'float32','low':'float32','close':'float32'}
    bid = pd.read_csv(bid_path, dtype=dtypes).rename(columns={c:f'bid_{c}' for c in ['open','high','low','close']})
    ask = pd.read_csv(ask_path, dtype=dtypes).rename(columns={c:f'ask_{c}' for c in ['open','high','low','close']})
    audit = {
        'input_sha256': zip_hash,
        'bid_rows': int(len(bid)), 'ask_rows': int(len(ask)),
        'bid_duplicate_timestamps': int(bid['timestamp'].duplicated().sum()),
        'ask_duplicate_timestamps': int(ask['timestamp'].duplicated().sum()),
        'source_feed': manifest.get('source_feed'), 'instrument': manifest.get('instrument'),
        'timeframe': manifest.get('timeframe'), 'requested_window_utc': manifest.get('requested_window_utc'),
        'monthly_requests': manifest.get('monthly_requests'),
    }
    if audit['bid_duplicate_timestamps'] or audit['ask_duplicate_timestamps']:
        raise ValueError('Duplicate input timestamps; refuse silent deduplication')
    q = bid.merge(ask, on='timestamp', how='inner', sort=True, validate='one_to_one')
    audit['common_quote_rows_before_calendar_filter'] = int(len(q))
    ts_utc = pd.to_datetime(q['timestamp'].to_numpy(dtype=np.int64), unit='ms', utc=True)
    ts_ny = ts_utc.tz_convert(NY)
    session_days, valid_calendar = session_index(ts_ny)
    q['session_day'] = session_days
    q['ts_ny_hour'] = ts_ny.hour.to_numpy()
    q['ts_ny_minute'] = ts_ny.minute.to_numpy()
    q = q.loc[valid_calendar].copy().reset_index(drop=True)
    ts_ny = ts_ny[valid_calendar]
    audit['rows_after_FX_calendar_filter'] = int(len(q))
    audit['filtered_weekend_closed_hours_rows'] = audit['common_quote_rows_before_calendar_filter'] - audit['rows_after_FX_calendar_filter']
    audit['post_filter_timestamp_duplicates'] = int(q['timestamp'].duplicated().sum())

    spread = q['ask_open'].astype(float).to_numpy() - q['bid_open'].astype(float).to_numpy()
    audit['negative_open_spread_rows'] = int((spread < -1e-8).sum())
    audit['median_open_spread_pips'] = float(np.median(spread) / PIP)
    audit['p95_open_spread_pips'] = float(np.quantile(spread, .95) / PIP)
    if audit['negative_open_spread_rows']:
        raise ValueError('Negative opening spreads found')

    g = q.groupby('session_day', sort=True, observed=True)
    daily = g.agg(
        open_bid=('bid_open','first'), high_bid=('bid_high','max'), low_bid=('bid_low','min'), close_bid=('bid_close','last'),
        high_ask=('ask_high','max'), low_ask=('ask_low','min'), close_ask=('ask_close','last'),
        open_ask=('ask_open','first'), first_ts=('timestamp','first'), last_ts=('timestamp','last'), minutes=('timestamp','size'),
        last_hour=('ts_ny_hour','last'), last_minute=('ts_ny_minute','last')
    ).reset_index()
    daily['session_day'] = pd.to_datetime(daily['session_day'])
    daily = daily.sort_values('session_day').reset_index(drop=True)
    daily['prev_close'] = daily['close_bid'].shift(1)
    daily['tr'] = np.maximum.reduce([
        (daily['high_bid'] - daily['low_bid']).to_numpy(dtype=float),
        np.abs((daily['high_bid'] - daily['prev_close']).to_numpy(dtype=float)),
        np.abs((daily['low_bid'] - daily['prev_close']).to_numpy(dtype=float)),
    ])
    daily.loc[daily['prev_close'].isna(), 'tr'] = np.nan
    daily['atr20'] = daily['tr'].shift(1).rolling(20, min_periods=20).mean()
    daily['prior20_high'] = daily['high_bid'].shift(1).rolling(20, min_periods=20).max()
    daily['prior20_low'] = daily['low_bid'].shift(1).rolling(20, min_periods=20).min()
    ts_ms = q['timestamp'].to_numpy(dtype=np.int64)
    timestamp_to_row = {int(t): i for i, t in enumerate(ts_ms)}
    q_session_idx = q['session_day'].map({pd.Timestamp(d): i for i, d in enumerate(daily['session_day'])}).to_numpy(dtype=np.int32)
    q_ts_ny = pd.to_datetime(ts_ms, unit='ms', utc=True).tz_convert(NY)
    q_h = q_ts_ny.hour.to_numpy(); q_m = q_ts_ny.minute.to_numpy()
    daily['complete_close_bar'] = (daily['last_hour'] == 16) & (daily['last_minute'] == 59)

    signals = []
    raw_breakout_count = 0
    skip_signal_counts = {'no_feature_history':0, 'missing_1659_close':0, 'missing_1705_entry_quote':0,
                          'invalid_atr_or_stop':0, 'overlap_open_position':0, 'incomplete_at_data_boundary':0}
    for i, row in daily.iterrows():
        if not np.isfinite(row['atr20']) or not np.isfinite(row['prior20_high']) or not np.isfinite(row['prior20_low']):
            continue
        close = float(row['close_bid'])
        direction = 1 if close > float(row['prior20_high']) else (-1 if close < float(row['prior20_low']) else 0)
        if direction == 0:
            continue
        raw_breakout_count += 1
        if not bool(row['complete_close_bar']):
            skip_signal_counts['missing_1659_close'] += 1
            continue
        atr = float(row['atr20'])
        if not np.isfinite(atr) or atr <= 0:
            skip_signal_counts['invalid_atr_or_stop'] += 1
            continue
        day = pd.Timestamp(row['session_day']).date()
        entry_local = pd.Timestamp(day).tz_localize(NY) + pd.Timedelta(hours=17, minutes=5)
        entry_utc_ms = int(entry_local.tz_convert('UTC').value // 1_000_000)
        entry_idx = timestamp_to_row.get(entry_utc_ms)
        if entry_idx is None:
            skip_signal_counts['missing_1705_entry_quote'] += 1
            continue
        signals.append({'daily_i':int(i), 'signal_day':str(day), 'signal_close_ms':int(row['last_ts']),
                        'direction':int(direction), 'atr':atr, 'entry_ms':entry_utc_ms,
                        'entry_idx':int(entry_idx), 'entry_local':str(entry_local)})

    bid_o = q['bid_open'].to_numpy(float); bid_h = q['bid_high'].to_numpy(float); bid_l = q['bid_low'].to_numpy(float); bid_c = q['bid_close'].to_numpy(float)
    ask_o = q['ask_open'].to_numpy(float); ask_h = q['ask_high'].to_numpy(float); ask_l = q['ask_low'].to_numpy(float); ask_c = q['ask_close'].to_numpy(float)
    sess_idx = q_session_idx
    rows = []
    last_exit_idx = -1
    for s in signals:
        sig_close_idx = timestamp_to_row.get(s['signal_close_ms'])
        if sig_close_idx is None:
            skip_signal_counts['missing_1659_close'] += 1
            continue
        if last_exit_idx >= sig_close_idx:
            skip_signal_counts['overlap_open_position'] += 1
            continue
        e = s['entry_idx']; d = s['direction']; atr = s['atr']
        entry = float(ask_o[e] if d==1 else bid_o[e])
        stop_dist = 2.0 * atr
        if stop_dist <= 0 or not np.isfinite(stop_dist):
            skip_signal_counts['invalid_atr_or_stop'] += 1
            continue
        stop = entry - d * stop_dist
        target = entry + d * (2.0 * stop_dist)
        entry_session_i = int(sess_idx[e])
        max_exit_session_i = entry_session_i + 10
        exit_i = None; exit_px = None; exit_reason = None
        for j in range(e, len(q)):
            if d == 1:
                op, hi, lo = bid_o[j], bid_h[j], bid_l[j]
                if op <= stop:
                    exit_i, exit_px, exit_reason = j, float(op), 'stop_gap'
                elif op >= target:
                    exit_i, exit_px, exit_reason = j, float(target), 'target_gap'
                elif lo <= stop:
                    exit_i, exit_px, exit_reason = j, float(stop), 'stop'
                elif hi >= target:
                    exit_i, exit_px, exit_reason = j, float(target), 'target'
            else:
                op, hi, lo = ask_o[j], ask_h[j], ask_l[j]
                if op >= stop:
                    exit_i, exit_px, exit_reason = j, float(op), 'stop_gap'
                elif op <= target:
                    exit_i, exit_px, exit_reason = j, float(target), 'target_gap'
                elif hi >= stop:
                    exit_i, exit_px, exit_reason = j, float(stop), 'stop'
                elif lo <= target:
                    exit_i, exit_px, exit_reason = j, float(target), 'target'
            if exit_i is not None:
                break
            if sess_idx[j] >= max_exit_session_i and q_h[j] == 16 and q_m[j] == 59:
                exit_i = j
                exit_px = float(bid_c[j] if d==1 else ask_c[j])
                exit_reason = 'time_10th_session_close'
                break
        if exit_i is None:
            skip_signal_counts['incomplete_at_data_boundary'] += 1
            continue
        gross_r = (d * (exit_px - entry)) / stop_dist
        row = {
            'signal_date':s['signal_day'], 'signal_year':int(pd.Timestamp(s['signal_day']).year),
            'direction':'LONG' if d==1 else 'SHORT', 'entry_time_utc':str(pd.to_datetime(ts_ms[e],unit='ms',utc=True)),
            'entry_time_ny':str(q_ts_ny[e]), 'exit_time_utc':str(pd.to_datetime(ts_ms[exit_i],unit='ms',utc=True)),
            'exit_time_ny':str(q_ts_ny[exit_i]), 'entry_price':entry, 'exit_price':float(exit_px),
            'stop_price':stop, 'target_price':target, 'atr20':atr, 'stop_distance_pips':stop_dist/PIP,
            'gross_r':float(gross_r), 'gross_pips':float(d*(exit_px-entry)/PIP),
            'exit_reason':exit_reason, 'holding_minutes':float((ts_ms[exit_i]-ts_ms[e])/60000),
            'entry_row':int(e), 'exit_row':int(exit_i), 'entry_session_index':entry_session_i,
            'exit_session_index':int(sess_idx[exit_i]),
        }
        for c in COSTS:
            row[f'net_r_{c:g}'] = float(gross_r - c/(stop_dist/PIP))
            row[f'net_pips_{c:g}'] = float(d*(exit_px-entry)/PIP - c)
        rows.append(row)
        last_exit_idx = exit_i

    trades = pd.DataFrame(rows)
    if trades.empty:
        raise RuntimeError('No trades produced; inspect data and signal mapping')
    segments = {'discovery_2016_2020':(2016,2020), 'validation_2021':(2021,2021), 'diagnostic_forward_2022_2025':(2022,2025)}
    summary = {'R271':'GAGAL_OR_EXPLORATORY', 'hypothesis':'daily 20-session close-confirmed breakout continuation',
               'input_audit':audit, 'daily_sessions':int(len(daily)), 'daily_sessions_missing_1659':int((~daily['complete_close_bar']).sum()),
               'raw_breakout_signals':int(raw_breakout_count), 'signals_with_valid_exact_entry':int(len(signals)), 'skip_counts':skip_signal_counts,
               'closed_trades':int(len(trades)), 'exit_reason_counts':{str(k):int(v) for k,v in trades['exit_reason'].value_counts().items()},
               'direction_counts':{str(k):int(v) for k,v in trades['direction'].value_counts().items()},
               'segments':{}, 'annual':{}, 'bootstrap_forward_plus_1pip':{}, 'cost_sensitivity':{},
               'reproducibility':{'runner_local_path':'research/r271_daily_trend_breakout.py', 'input_zip_sha256':zip_hash}}
    for name,(y0,y1) in segments.items():
        sub=trades[(trades['signal_year']>=y0)&(trades['signal_year']<=y1)]
        summary['segments'][name] = {f'cost_{c:g}_pip':metrics(sub,c) for c in COSTS}
    for y in range(2016,2026):
        sub=trades[trades['signal_year']==y]
        summary['annual'][str(y)] = {f'cost_{c:g}_pip':metrics(sub,c) for c in COSTS}
    for c in COSTS:
        summary['cost_sensitivity'][f'extra_cost_{c:g}_pips'] = {name: metrics(trades[(trades['signal_year']>=yr[0])&(trades['signal_year']<=yr[1])], c)
            for name,yr in segments.items()}
    forward = trades[(trades['signal_year']>=2022)&(trades['signal_year']<=2025)].copy()
    forward['entry_dt_ny'] = pd.to_datetime(forward['entry_time_utc'], utc=True).dt.tz_convert(NY).dt.tz_localize(None)
    forward['week_start'] = (forward['entry_dt_ny'].dt.normalize() - pd.to_timedelta(forward['entry_dt_ny'].dt.weekday,unit='D'))
    weeks = pd.date_range(pd.Timestamp('2022-01-03'), pd.Timestamp('2025-12-29'), freq='W-MON')
    weekly = forward.groupby('week_start')['net_r_1'].sum().reindex(weeks,fill_value=0.0).to_numpy(float)
    rng=np.random.default_rng(BOOT_SEED)
    blocks=math.ceil(len(weekly)/4)
    starts=rng.integers(0,len(weekly),size=(BOOT_REPS,blocks))
    inds=(starts[:,:,None]+np.arange(4)[None,None,:])%len(weekly)
    samples=weekly[inds].reshape(BOOT_REPS,-1)[:,:len(weekly)]
    means=samples.mean(axis=1)
    summary['bootstrap_forward_plus_1pip']={'weeks':int(len(weekly)), 'observed_mean_r_per_week':float(weekly.mean()),
        'positive_mean_fraction':float((means>0).mean()), 'ci95_mean_weekly_r':[float(np.quantile(means,.025)),float(np.quantile(means,.975))],
        'replicates':BOOT_REPS,'block_weeks':4,'seed':BOOT_SEED, 'weeks_with_trades':int((weekly!=0).sum())}
    trades.drop(columns=['entry_row','exit_row','entry_session_index','exit_session_index']).to_csv(OUT/'R271_trade_ledger.csv',index=False,float_format='%.6f')
    daily[['session_day','open_bid','high_bid','low_bid','close_bid','minutes','last_hour','last_minute','atr20','prior20_high','prior20_low','complete_close_bar']].to_csv(OUT/'R271_daily_features.csv',index=False,float_format='%.8f')
    (OUT/'R271_results.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
    d=summary['segments']['discovery_2016_2020']['cost_1_pip']
    v=summary['segments']['validation_2021']['cost_1_pip']
    f=summary['segments']['diagnostic_forward_2022_2025']['cost_1_pip']
    years=[summary['annual'][str(y)]['cost_1_pip'] for y in range(2022,2026)]
    f2=summary['segments']['diagnostic_forward_2022_2025']['cost_2_pip']
    gates={
      'discovery_positive_min50':d['net_r']>0 and d['trades']>=50,
      'validation_positive_min50':v['net_r']>0 and v['trades']>=50,
      'forward_aggregate_positive':f['net_r']>0,
      'forward_positive_at_least_3_of_4_years':sum(1 for x in years if x['net_r']>0)>=3,
      'bootstrap_lower_bound_positive':summary['bootstrap_forward_plus_1pip']['ci95_mean_weekly_r'][0]>0,
      'forward_positive_at_2pip_cost':f2['net_r']>0,
    }
    summary['historical_screen_gates']=gates
    summary['historical_screen_pass']=bool(all(gates.values()))
    summary['final_verdict']='GAGAL' if not all(gates.values()) else 'GAGAL_FOR_PROMOTION_NO_UNTOUCHED_HOLDOUT'
    (OUT/'R271_results.json').write_text(json.dumps(summary,indent=2,allow_nan=False))
    print(json.dumps({'input_audit':audit,'sessions':len(daily),'raw_signals':raw_breakout_count,
        'signals_with_exact_entry':len(signals),'trades':len(trades),'skip_counts':skip_signal_counts,
        'segments':summary['segments'],'annual':summary['annual'],'bootstrap':summary['bootstrap_forward_plus_1pip'],
        'gates':gates,'final_verdict':summary['final_verdict'],'exit_reasons':summary['exit_reason_counts']},indent=2))

if __name__=='__main__':
    main()
