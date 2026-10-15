#!/usr/bin/env python3
"""R261 London-window impulse continuation; local-only, no network access."""
from __future__ import annotations
import json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd

PIP = 0.0001
COSTS = (0.0, 0.5, 1.0, 2.0)
TRAIN_START = pd.Timestamp('2017-01-01', tz='UTC')
TRAIN_END = pd.Timestamp('2021-01-01', tz='UTC')
VALID_END = pd.Timestamp('2022-01-01', tz='UTC')
FORWARD_END = pd.Timestamp('2026-01-01', tz='UTC')
Q = 0.75
RR = 1.5
LONDON_TZ = 'Europe/London'


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
        if unit is None:
            raise ValueError(f'Unknown numeric timestamp unit in {path}')
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
    if d.empty:
        raise ValueError(f'No valid price rows in {path}')
    diag = {'raw_rows': raw_count, 'valid_rows': len(d), 'duplicate_timestamps_removed': duplicates,
            'invalid_ohlc_removed': invalid, 'start_utc': d.index[0].isoformat(),
            'end_utc': d.index[-1].isoformat(), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
    return d, diag


def pf(values):
    a = np.asarray(values, dtype=float)
    gp = float(a[a > 0].sum())
    gl = float(-a[a < 0].sum())
    if gl <= 0:
        return None
    return gp / gl


def period_trades(trades, start, end):
    return [t for t in trades if start <= pd.Timestamp(t['entry_utc']) < end and pd.Timestamp(t['exit_utc']) < end]


def metrics(trades, start, end, cost):
    a = period_trades(trades, start, end)
    vals = np.asarray([t['gross_pips'] - cost for t in a], dtype=float)
    weeks = max((end - start).total_seconds() / (7*24*3600), 1/7)
    return {'trades': int(len(vals)), 'PF': pf(vals), 'gross_pips': float(sum(t['gross_pips'] for t in a)),
            'net_pips': float(vals.sum()), 'mean_net_pips_per_trade': float(vals.mean()) if len(vals) else None,
            'win_rate': float(np.mean(vals > 0)) if len(vals) else None,
            'trades_per_week': float(len(vals)/weeks), 'trades_per_month': float(len(vals)/(weeks/4.345))}


def block_bootstrap(trades, start, end, cost=1.0, reps=5000, seed=261, block_weeks=4):
    weeks = int(np.ceil((end-start).total_seconds()/(7*24*3600)))
    weekly = np.zeros(weeks, dtype=float)
    a = period_trades(trades, start, end)
    for t in a:
        ts = pd.Timestamp(t['entry_utc'])
        w = int((ts-start).total_seconds() // (7*24*3600))
        if 0 <= w < weeks:
            weekly[w] += float(t['gross_pips']) - cost
    if weeks < block_weeks or not a:
        return {'trades': len(a), 'weeks': weeks, 'error': 'insufficient sample'}
    rng = np.random.default_rng(seed)
    block_count = int(np.ceil(weeks/block_weeks))
    means = np.empty(reps, dtype=float)
    for k in range(reps):
        picks = rng.integers(0, weeks, size=block_count)
        ix = np.concatenate([(s+np.arange(block_weeks)) % weeks for s in picks])[:weeks]
        means[k] = weekly[ix].mean()
    return {'trades': len(a), 'weeks': weeks, 'block_weeks': block_weeks, 'reps': reps, 'seed': seed,
            'observed_net_pips': float(weekly.sum()), 'observed_mean_net_pips_per_week': float(weekly.mean()),
            'probability_mean_weekly_net_positive': float(np.mean(means > 0)),
            'bootstrap_95pct_ci_mean_weekly_net_pips': [float(np.quantile(means,.025)), float(np.quantile(means,.975))]}


def main():
    data_dir = Path('/mnt/data/backtest_local/r258/dl/r251_fx')
    out_dir = Path('/mnt/data/backtest_local/r261_out')
    out_dir.mkdir(parents=True, exist_ok=True)
    bid_path, ask_path = data_dir/'eurusd_bid_H1.csv', data_dir/'eurusd_ask_H1.csv'
    bid, bd = read_bars(bid_path)
    ask, ad = read_bars(ask_path)
    common = bid.index.intersection(ask.index).sort_values()
    if len(common) < 50000:
        raise ValueError(f'Insufficient BID/ASK common bars: {len(common)}')
    start = common.min().floor('h')
    end = common.max().floor('h')
    ix = pd.date_range(start, end, freq='h')
    b, a = bid.reindex(ix), ask.reindex(ix)
    cols = ['Open','High','Low','Close']
    vb = b[cols].notna().all(axis=1) & (b.High >= b[['Open','Close']].max(axis=1)) & (b.Low <= b[['Open','Close']].min(axis=1)) & (b.High >= b.Low)
    va = a[cols].notna().all(axis=1) & (a.High >= a[['Open','Close']].max(axis=1)) & (a.Low <= a[['Open','Close']].min(axis=1)) & (a.High >= a.Low)
    valid = vb & va
    neg_spread = int(((a.Open - b.Open < -1e-10) & valid).sum())
    if neg_spread:
        raise ValueError(f'Negative ASK-BID spreads: {neg_spread}')
    spread = ((a.Open-b.Open)/PIP)[valid]
    if spread.empty:
        raise ValueError('No quote-side open spread data')
    london = ix.tz_convert(LONDON_TZ)
    position = {}
    for i, ts in enumerate(london):
        # Signal and exit hours never include the duplicated autumn 01:00 local hour.
        if ts.minute == 0:
            position[(ts.date(), ts.hour)] = i
    all_days = sorted({k[0] for k in position if k[1] == 5})
    skipped = {'nontrading_weekend_date': 0, 'missing_signal_or_entry_or_exit_hours': 0, 'missing_or_invalid_holding_bar': 0,
               'nonpositive_or_tiny_risk': 0, 'signal_not_triggered': 0, 'overlap': 0}
    raw_windows = []
    for day in all_days:
        # Source contains copied flat quote bars while FX is closed; weekends are not tradable samples.
        if day.weekday() >= 5:
            skipped['nontrading_weekend_date'] += 1
            continue
        ids = [position.get((day,h)) for h in range(5,17)]
        if any(i is None for i in ids):
            skipped['missing_signal_or_entry_or_exit_hours'] += 1
            continue
        if not bool(valid.iloc[ids].all()):
            skipped['missing_or_invalid_holding_bar'] += 1
            continue
        i05, i06, i07, i08 = (position[(day,h)] for h in (5,6,7,8))
        i16 = position[(day,16)]
        impulse = (float(b.Close.iloc[i07])-float(b.Open.iloc[i05]))/PIP
        raw_windows.append({'date': day.isoformat(), 'i05': i05, 'i06': i06, 'i07': i07, 'entry_i': i08,
                            'time_exit_i': i16, 'impulse_pips': impulse, 'entry_utc': ix[i08].isoformat()})
    raw = [w for w in raw_windows if TRAIN_START <= pd.Timestamp(w['entry_utc']) < TRAIN_END]
    if len(raw) < 400:
        raise ValueError(f'Too few complete training windows: {len(raw)}')
    threshold = float(np.quantile(np.abs([w['impulse_pips'] for w in raw]), Q))
    trades = []
    for w in raw_windows:
        if abs(w['impulse_pips']) < threshold or abs(w['impulse_pips']) < 1e-12:
            skipped['signal_not_triggered'] += 1
            continue
        d = 1 if w['impulse_pips'] > 0 else -1
        sig_ix = [w['i05'], w['i06'], w['i07']]
        ei, xi = w['entry_i'], w['time_exit_i']
        entry = float(a.Open.iloc[ei] if d == 1 else b.Open.iloc[ei])
        if d == 1:
            stop = float(min(b.Low.iloc[j] for j in sig_ix))
            risk = entry-stop
            target = entry+RR*risk
        else:
            stop = float(max(a.High.iloc[j] for j in sig_ix))
            risk = stop-entry
            target = entry-RR*risk
        if not np.isfinite(risk) or risk < 0.5*PIP:
            skipped['nonpositive_or_tiny_risk'] += 1
            continue
        exit_i = None; exit_px = None; reason = None
        # Evaluate executable-side bars 08 through 15. Missing bars were excluded above.
        for j in range(ei, xi):
            if d == 1:
                op, hi, lo = float(b.Open.iloc[j]), float(b.High.iloc[j]), float(b.Low.iloc[j])
                if op <= stop:
                    exit_i, exit_px, reason = j, op, 'STOP_GAP'; break
                if lo <= stop:
                    exit_i, exit_px, reason = j, stop, 'STOP'; break
                if hi >= target:
                    exit_i, exit_px, reason = j, target, 'TARGET'; break
            else:
                op, hi, lo = float(a.Open.iloc[j]), float(a.High.iloc[j]), float(a.Low.iloc[j])
                if op >= stop:
                    exit_i, exit_px, reason = j, op, 'STOP_GAP'; break
                if hi >= stop:
                    exit_i, exit_px, reason = j, stop, 'STOP'; break
                if lo <= target:
                    exit_i, exit_px, reason = j, target, 'TARGET'; break
        if exit_i is None:
            exit_i = xi
            exit_px = float(b.Open.iloc[xi] if d == 1 else a.Open.iloc[xi])
            reason = 'TIME_16_LONDON'
        gross = (float(exit_px)-entry)/PIP*d
        trades.append({'signal_date_london': w['date'], 'signal_impulse_pips': float(w['impulse_pips']),
                       'entry_utc': ix[ei].isoformat(), 'exit_utc': ix[exit_i].isoformat(),
                       'entry_london': london[ei].isoformat(), 'exit_london': london[exit_i].isoformat(),
                       'direction': 'LONG' if d==1 else 'SHORT', 'entry_price': entry, 'exit_price': float(exit_px),
                       'stop_price': stop, 'target_price': float(target), 'risk_pips': float(risk/PIP),
                       'gross_pips': float(gross), 'gross_R': float(gross/risk), 'exit_reason': reason})
    trades_df = pd.DataFrame(trades)
    trades_df.to_csv(out_dir/'R261_london_impulse_trades.csv', index=False)
    periods = [
        ('discovery_2017_2020', TRAIN_START, TRAIN_END),
        ('validation_2021', TRAIN_END, VALID_END),
        ('forward_2022_2025', VALID_END, FORWARD_END),
        ('oos_2026', FORWARD_END, ix[-1]+pd.Timedelta(hours=1)),
    ]
    metrics_out = {}
    for name, ps, pe in periods:
        metrics_out[name] = {f'extra_cost_{cost:g}_pip': metrics(trades, ps, pe, cost) for cost in COSTS}
    annual = []
    for year in range(2022, 2026):
        s,e = pd.Timestamp(f'{year}-01-01',tz='UTC'),pd.Timestamp(f'{year+1}-01-01',tz='UTC')
        annual.append({'year':year, **{f'extra_cost_{cost:g}_pip':metrics(trades,s,e,cost) for cost in COSTS}})
    bootstrap = block_bootstrap(trades, VALID_END, FORWARD_END, cost=1.0, reps=5000, seed=261, block_weeks=4)
    forward_plus1 = metrics_out['forward_2022_2025']['extra_cost_1_pip']
    gates = {
       'minimum_trades_discovery_100': metrics_out['discovery_2017_2020']['extra_cost_1_pip']['trades'] >= 100,
       'minimum_trades_validation_50': metrics_out['validation_2021']['extra_cost_1_pip']['trades'] >= 50,
       'minimum_trades_forward_50': forward_plus1['trades'] >= 50,
       'minimum_trades_oos_50': metrics_out['oos_2026']['extra_cost_1_pip']['trades'] >= 50,
       'discovery_pf_ge_1_10': (metrics_out['discovery_2017_2020']['extra_cost_1_pip']['PF'] or 0) >= 1.10,
       'validation_pf_ge_1_10': (metrics_out['validation_2021']['extra_cost_1_pip']['PF'] or 0) >= 1.10,
       'forward_pf_ge_1_10': (forward_plus1['PF'] or 0) >= 1.10,
       'oos_pf_ge_1_10': (metrics_out['oos_2026']['extra_cost_1_pip']['PF'] or 0) >= 1.10,
       'all_forward_years_positive_net_and_pf_ge_1': all((y['extra_cost_1_pip']['net_pips'] > 0 and (y['extra_cost_1_pip']['PF'] or 0)>=1.0) for y in annual),
       'bootstrap_forward_4week_ci_lower_gt_zero': bool(bootstrap.get('bootstrap_95pct_ci_mean_weekly_net_pips') and bootstrap['bootstrap_95pct_ci_mean_weekly_net_pips'][0] > 0),
    }
    verdict = 'PASS FOR FURTHER RESEARCH' if all(gates.values()) else 'FAIL'
    diag = {
       'bid':bd,'ask':ad,'common_timestamps':len(common),'grid_start_utc':ix[0].isoformat(),'grid_end_utc':ix[-1].isoformat(),
       'expected_hourly_grid_rows':len(ix),'valid_common_quote_rows':int(valid.sum()),'missing_or_incomplete_hourly_points':int((~valid).sum()),
       'negative_open_spreads':neg_spread,'open_spread_pips':{'median':float(spread.median()),'p95':float(spread.quantile(.95)),
        'p99':float(spread.quantile(.99)),'max':float(spread.max()),'min':float(spread.min())},
       'complete_london_windows':len(raw_windows),'complete_training_windows':len(raw),
       'signal_threshold_abs_impulse_pips':threshold,'threshold_quantile':Q,'complete_windows_triggered_before_risk_filters':sum(abs(w['impulse_pips'])>=threshold for w in raw_windows),
       'skipped':skipped,'trades_by_exit_reason':trades_df.exit_reason.value_counts().to_dict() if len(trades_df) else {},
       'trade_count':len(trades_df),'dates_with_trades':int(trades_df.signal_date_london.nunique()) if len(trades_df) else 0,
    }
    report = {
       'status':'COMPLETED','round':'R261','verdict':verdict,'execution_location':'Python in local ChatGPT/container session; not executed by GitHub Actions',
       'strategy':'EURUSD London-local 05:00-08:00 H1 impulse continuation, stop at three-bar range extreme, target 1.5R, time exit 16:00 London',
       'source':{'source':'GitHub Actions artifact already retained from repository','repository':'christianomomongan82-lang/scanner',
         'artifact_id':11916174401,'artifact_name':'R258-multihorizon-momentum-audit','files':{'bid':str(bid_path),'ask':str(ask_path)},
         'sha256':{'bid':bd['sha256'],'ask':ad['sha256']}},
       'parameters':{'timezone':LONDON_TZ,'training_quantile':Q,'RR':RR,'extra_costs_pips':list(COSTS),
         'periods':{'discovery':'2017-01-01 to 2020-12-31 UTC','validation':'2021 UTC','forward':'2022-2025 UTC','oos':f'2026-01-01 to {(ix[-1]+pd.Timedelta(hours=1)).isoformat()}'}},
       'data_quality':diag,'period_metrics':metrics_out,'annual_forward':annual,'forward_bootstrap_plus1pip':bootstrap,'gates':gates,
       'limitations':['H1 bars are not adequate to reproduce R189 M1 entry/exit logic.','H1 OHLC cannot verify manual-entry slippage or exact intrabar sequence when stop/target collide; stop-first is conservative.',
        'Observed BID/ASK includes quote spread only; no separately verified broker commission or live slippage.','PASS FOR FURTHER RESEARCH would not establish funded readiness.'],
    }
    (out_dir/'R261_london_impulse_results.json').write_text(json.dumps(report,indent=2,allow_nan=False))
    pd.DataFrame(annual).to_csv(out_dir/'R261_london_impulse_annual.csv',index=False)
    print(json.dumps({'verdict':verdict,'threshold_pips':threshold,'data_quality':diag,'metrics':metrics_out,'annual':annual,'bootstrap':bootstrap,'gates':gates,'out_dir':str(out_dir)},indent=2,allow_nan=False))

if __name__=='__main__':
    main()
