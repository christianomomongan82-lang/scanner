#!/usr/bin/env python3
"""R273 local-only runner; imports the stored R272 BID/ASK execution primitives."""
from __future__ import annotations
import os, json, importlib.util
from pathlib import Path
import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get('R273_DATA_DIR', '/mnt/data/r272_xauusd/data_exports/xauusd_m5_2016_2026'))
OUT_DIR = Path(os.environ.get('R273_OUTPUT_DIR', str(DATA_DIR / 'results_r273')))
os.environ['R272_DATA_DIR'] = str(DATA_DIR)
os.environ['R272_OUTPUT_DIR'] = str(OUT_DIR)
ENGINE_PATH = HERE / 'r272_xauusd_dual_module.py'
spec = importlib.util.spec_from_file_location('r272_engine_for_r273', ENGINE_PATH)
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
END_HIST = pd.Timestamp('2026-01-01T00:00:00Z')
COSTS = [0.00, 0.10, 0.30, 0.50]
PRIMARY = 0.30
BOOT_SEED = 2732026
BOOT_REPS = 10000

def subset(trades, lo, hi):
    if trades.empty:
        return trades.copy()
    ts = pd.to_datetime(trades['signal_bar_time_utc'], utc=True)
    return trades[(ts >= lo) & (ts < hi)].copy()

def m(trades, cost):
    return engine.metrics(trades, cost)

def boot(trades, cost):
    return engine.bootstrap_weekly(trades, cost, reps=BOOT_REPS, seed=BOOT_SEED)

def collect_raw_a(q, f):
    eligible = np.flatnonzero(f['valid_context'].to_numpy() & q['ny_weekday'].to_numpy() & (q['ny_minute'].to_numpy() >= 360) & (q['ny_minute'].to_numpy() <= 950))
    events = []
    for i in eligible:
        if i < 146:
            continue
        a_sig, _b_sig, skip = engine.calc_raw_signals(q, f, int(i))
        if skip or a_sig is None:
            continue
        events.append((int(i), float(f.at[i, 'net_move']), float(f.at[i, 'net_move_6h']), a_sig))
    return events, int(len(eligible))

def run_stream(q, events, stream_name):
    day_positions = {}
    for j, day in enumerate(q['ny_date'].to_numpy()):
        day_positions.setdefault(day, []).append(j)
    used_days, busy_until, trades, skips = set(), -1, [], {}
    rejected_alignment = raw_candidates = 0
    for i, n12, n6, sig in events:
        day = q.at[i, 'ny_date']
        if i <= busy_until or day in used_days:
            continue
        if stream_name == 'raw_A':
            chosen = sig
        elif stream_name == 'aligned_A':
            if n12 * n6 <= 0:
                rejected_alignment += 1
                continue
            chosen = sig
        else:
            raise ValueError(stream_name)
        raw_candidates += 1
        row = engine.build_trade_for_signal(q, day_positions, i, chosen)
        if row is None:
            skips['invalid_delayed_entry_or_RR'] = skips.get('invalid_delayed_entry_or_RR', 0) + 1
            continue
        row['stream'] = stream_name
        row['signal_year'] = int(pd.Timestamp(row['signal_bar_time_utc']).year)
        row['signal_month'] = pd.Timestamp(row['signal_bar_time_utc']).strftime('%Y-%m')
        row['six_hour_net_move_usd_per_oz'] = n6
        row['twelve_hour_net_move_usd_per_oz'] = n12
        trades.append(row)
        used_days.add(day)
        busy_until = int(row['exit_index'])
    out = pd.DataFrame(trades)
    out.attrs['skip_counts'] = skips
    out.attrs['raw_signals'] = raw_candidates
    out.attrs['rejected_alignment'] = rejected_alignment
    return out

def metrics_by_cost(trades):
    return {f'cost_{engine.cost_to_key(c)}': m(trades, c) for c in COSTS}

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    q_full, audit = engine.load_quotes()
    q = q_full[q_full['timestamp_utc'] < END_HIST].copy().reset_index(drop=True)
    del q_full
    f = engine.features(q)
    f['net_move_6h'] = q['bid_close'].shift(1) - q['bid_close'].shift(73)
    events, eligible_n = collect_raw_a(q, f)
    streams = {name: run_stream(q, events, name) for name in ('raw_A', 'aligned_A')}
    d0, d1, d2 = pd.Timestamp('2016-01-01T00:00:00Z'), pd.Timestamp('2021-01-01T00:00:00Z'), END_HIST
    split_metrics = {}
    summary = {
        'round': 'R273', 'verdict': 'GAGAL', 'instrument': 'XAUUSD', 'timeframe': 'M5',
        'source': 'Dukascopy via dukascopy-node; raw-only artifact 12031270051; acquisition run 38859918137',
        'primary_extra_cost_usd_per_oz': PRIMARY,
        'data_audit': {k: v for k, v in audit.items() if k != 'source_manifest'},
        'historical_rows_through_2025_only': int(len(q)), 'eligible_context_bars': eligible_n,
        'raw_A_trigger_bars': int(len(events)),
        'alignment_agreeing_triggers': sum(1 for _, n12, n6, _ in events if n12 * n6 > 0),
        'alignment_disagreeing_triggers': sum(1 for _, n12, n6, _ in events if n12 * n6 <= 0),
        'holdout_2026_opened': False, 'historical_metrics': {}, 'historical_gates': {}
    }
    for name, tr in streams.items():
        disc, val = subset(tr, d0, d1), subset(tr, d1, d2)
        split_metrics[name] = {'discovery': disc, 'validation': val}
        summary['historical_metrics'][name] = {
            'discovery_2016_2020': metrics_by_cost(disc),
            'validation_2021_2025': metrics_by_cost(val),
            'discovery_bootstrap_primary': boot(disc, PRIMARY),
            'validation_bootstrap_primary': boot(val, PRIMARY),
            'execution_skip_counts': tr.attrs.get('skip_counts', {}),
            'rejected_by_alignment': tr.attrs.get('rejected_alignment', 0)
        }
        tr.drop(columns=['entry_index', 'exit_index'], errors='ignore').to_csv(OUT_DIR / f'R273_{name}_trade_ledger_development_only.csv', index=False, float_format='%.8f')
    raw_val = split_metrics['raw_A']['validation']
    child_disc, child_val = split_metrics['aligned_A']['discovery'], split_metrics['aligned_A']['validation']
    bd = boot(child_disc, PRIMARY)
    summary['historical_gates'] = {
        'child_discovery_at_least_50_trades_and_positive_net_R': len(child_disc) >= 50 and m(child_disc, PRIMARY)['net_r'] > 0,
        'child_discovery_weekly_bootstrap_lower_95_positive': bd['ci95'][0] is not None and bd['ci95'][0] > 0,
        'child_validation_at_least_100_trades_and_positive_net_R': len(child_val) >= 100 and m(child_val, PRIMARY)['net_r'] > 0,
        'child_validation_positive_at_cost_0p50': m(child_val, 0.50)['net_r'] > 0,
        'child_validation_beats_raw_A_and_retains_40pct_trades': m(child_val, PRIMARY)['net_r'] > m(raw_val, PRIMARY)['net_r'] and len(child_val) >= 0.40 * len(raw_val)
    }
    summary['final_verdict'] = 'GAGAL' if not all(summary['historical_gates'].values()) else 'HISTORICAL_SCREEN_PASS_2026_NOT_OPENED'
    (OUT_DIR / 'R273_results.json').write_text(json.dumps(summary, indent=2, allow_nan=False), encoding='utf-8')
    print(json.dumps({
        'round': 'R273', 'verdict': summary['final_verdict'], 'holdout_2026_opened': False,
        'historical_gates': summary['historical_gates'],
        'raw_A_discovery': m(split_metrics['raw_A']['discovery'], PRIMARY),
        'raw_A_validation': m(raw_val, PRIMARY),
        'aligned_A_discovery': m(child_disc, PRIMARY), 'aligned_A_validation': m(child_val, PRIMARY),
        'aligned_A_discovery_bootstrap': bd, 'aligned_A_validation_bootstrap': boot(child_val, PRIMARY)
    }, indent=2, allow_nan=False))

if __name__ == '__main__':
    main()