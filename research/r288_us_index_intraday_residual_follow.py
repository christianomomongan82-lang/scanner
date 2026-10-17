#!/usr/bin/env python3
"""R288 pre-registered residual-follow test. No post-entry PnL is calculated before 2022."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

TZ = 'America/New_York'
FILES = {
    'USA500': 'usa500idxusd_m5.csv.gz',
    'USATECH': 'usatechidxusd_m5.csv.gz',
    'USA30': 'usa30idxusd_m5.csv.gz',
    'USSC2000': 'ussc2000idxusd_m5.csv.gz',
}
EXPECTED_SHA256 = {
    'USA500': 'df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee',
    'USATECH': '82b06c38f66cd1387097691baac1d45c9463b6540eea9dfe28a894d85e122f7c',
    'USA30': '8fcef9d76b31e99ae8d0175e769307ab13f930ae3ec2c17ef6baf0311ea1783a',
    'USSC2000': 'c01c97d8705453d3fa3fd4ac1d386e9c1d72ab27e3b7d57d6cde53da9dfdf6f0',
}
COSTS = (1, 2, 4)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()


def load_sessions(path: Path, symbol: str):
    d = pd.read_csv(path, compression='gzip')
    if d.columns.tolist() != ['timestamp', 'open', 'high', 'low', 'close']:
        raise ValueError(f'{symbol}: unexpected schema {d.columns.tolist()}')
    if d.timestamp.duplicated().any():
        raise ValueError(f'{symbol}: duplicate source timestamps')
    d = d.sort_values('timestamp', kind='stable').reset_index(drop=True)
    d['dt_utc'] = pd.to_datetime(d.timestamp, unit='ms', utc=True)
    d['dt'] = d.dt_utc.dt.tz_convert(TZ)
    d['date'] = d.dt.dt.strftime('%Y-%m-%d')
    d['minute'] = d.dt.dt.hour * 60 + d.dt.dt.minute
    o = ['open', 'high', 'low', 'close']
    d['valid'] = d[o].notna().all(axis=1) & (d[o] > 0).all(axis=1) & \
        (d.high >= d[['open', 'close', 'low']].max(axis=1)) & \
        (d.low <= d[['open', 'close', 'high']].min(axis=1))
    d['flat_candidate'] = (d.open == d.high) & (d.high == d.low) & \
        (d.low == d.close) & (d.close == d.close.shift(1))
    r = d[(d.dt.dt.dayofweek < 5) & d.minute.between(570, 955) &
          (d.date >= '2017-01-01') & (d.date <= '2026-12-31')].copy()
    sessions, audit = {}, []
    for day, g in r.groupby('date', sort=True):
        g = g.sort_values('timestamp').reset_index(drop=True)
        active = (float(g.high.max()) - float(g.low.min()) > 0) and (
            (g.open != g.close).any() or (g.high != g.low).any() or (g.close != g.close.shift(1)).any())
        if not active:
            continue
        midnight = pd.Timestamp(day).tz_localize(TZ)
        expected = pd.date_range(midnight + pd.Timedelta(hours=9, minutes=30),
                                 midnight + pd.Timedelta(hours=15, minutes=55), freq='5min')
        exact = len(g) == 78 and not g.dt.duplicated().any() and pd.DatetimeIndex(g.dt).equals(expected)
        reasons = []
        if len(g) != 78:
            reasons.append('bar_count_not_78')
        elif not pd.DatetimeIndex(g.dt).equals(expected):
            reasons.append('timestamp_sequence_invalid')
        if not g.valid.all():
            reasons.append('invalid_ohlc')
        if g.flat_candidate.any():
            reasons.append('repeated_flat_candidate')
        eligible = bool(exact and g.valid.all() and not g.flat_candidate.any())
        rec = {'symbol': symbol, 'date': day, 'year': int(day[:4]), 'bar_count': int(len(g)),
               'flat_candidate_count': int(g.flat_candidate.sum()), 'eligible': eligible,
               'reason': '|'.join(reasons)}
        if eligible:
            def one(minute):
                ix = np.flatnonzero(g.minute.to_numpy() == minute)
                return g.iloc[int(ix[0])] if len(ix) == 1 else None
            op10, cl1255, op1305, op1555 = one(600), one(775), one(785), one(955)
            if any(x is None for x in (op10, cl1255, op1305, op1555)):
                rec['eligible'] = False
                rec['reason'] = 'required_timestamp_missing'
            else:
                # For threshold calibration, only signal-window return is used. No PnL is computed here.
                sessions[day] = {
                    'symbol': symbol, 'date': day, 'year': int(day[:4]),
                    'signal_return': float(cl1255.close) / float(op10.open) - 1.0,
                    'entry_open': float(op1305.open), 'exit_open': float(op1555.open),
                    'entry_ts': op1305['dt'].isoformat(), 'exit_ts': op1555['dt'].isoformat(),
                }
        audit.append(rec)
    return sessions, audit, d.dt_utc.min().isoformat(), d.dt_utc.max().isoformat()


def summarize(trades, cost):
    x = np.asarray([float(t['gross_bps']) - cost for t in trades], dtype=float)
    if not len(x):
        return {'trades': 0, 'pf': None, 'net_bps': 0.0, 'mean_bps': None, 'median_bps': None,
                'max_drawdown_bps': 0.0, 'win_rate_pct': None}
    wins, loss_abs = x[x > 0].sum(), -x[x < 0].sum()
    eq = np.cumsum(x)
    peaks = np.maximum.accumulate(np.r_[0.0, eq])[1:]
    dd = peaks - eq
    return {'trades': int(len(x)), 'pf': float(wins / loss_abs) if loss_abs > 0 else None,
            'net_bps': float(x.sum()), 'mean_bps': float(x.mean()), 'median_bps': float(np.median(x)),
            'max_drawdown_bps': float(dd.max()), 'win_rate_pct': float((x > 0).mean() * 100)}


def weekly_series(trades, start_date, end_date, cost):
    idx = pd.date_range(pd.Timestamp(start_date).to_period('W').start_time,
                        pd.Timestamp(end_date).to_period('W').start_time, freq='W-MON')
    if len(idx) == 0:
        return np.zeros(0, dtype=float)
    net_by_week = {}
    for t in trades:
        day = pd.Timestamp(t['date'])
        monday = day - pd.Timedelta(days=day.weekday())
        net_by_week[monday.normalize()] = net_by_week.get(monday.normalize(), 0.0) + float(t['gross_bps']) - cost
    return np.asarray([net_by_week.get(x.normalize(), 0.0) for x in idx], dtype=float)


def circular_block_bootstrap_mean_ci(values, block=4, reps=5000, seed=288):
    v = np.asarray(values, dtype=float)
    if len(v) < block * 5:
        return {'mean_weekly_net_bps': float(v.mean()) if len(v) else None,
                'ci95_low': None, 'ci95_high': None, 'weeks': int(len(v)),
                'block_weeks': block, 'replicates': reps, 'note': 'insufficient weekly observations'}
    rng = np.random.default_rng(seed)
    n = len(v)
    n_blocks = int(np.ceil(n / block))
    starts = rng.integers(0, n, size=(reps, n_blocks))
    offsets = np.arange(block)
    samples = v[(starts[:, :, None] + offsets[None, None, :]) % n].reshape(reps, -1)[:, :n]
    means = samples.mean(axis=1)
    return {'mean_weekly_net_bps': float(v.mean()), 'ci95_low': float(np.quantile(means, .025)),
            'ci95_high': float(np.quantile(means, .975)), 'weeks': int(n), 'block_weeks': block,
            'replicates': reps, 'seed': seed}


def run(data_dir: Path, out_dir: Path):
    data_dir, out_dir = Path(data_dir), Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    sessions_by, audits, source_meta = {}, [], {}
    latest = None
    for sym, fn in FILES.items():
        pth = data_dir / fn
        actual = sha256(pth)
        if actual != EXPECTED_SHA256[sym]:
            raise ValueError(f'{sym} SHA256 mismatch: expected {EXPECTED_SHA256[sym]}, got {actual}')
        ss, au, source_min, source_max = load_sessions(pth, sym)
        sessions_by[sym] = ss
        audits.extend(au)
        source_meta[sym] = {'file': fn, 'sha256_gz': actual, 'bytes': pth.stat().st_size,
                            'eligible_sessions': len(ss), 'source_first_utc': source_min,
                            'source_last_utc': source_max}
        latest = source_max if latest is None or source_max > latest else latest
        print(f'LOADED {sym}: eligible RTH sessions={len(ss)} source_max_utc={source_max}', flush=True)

    dates = sorted(set().union(*[set(v.keys()) for v in sessions_by.values()]))
    panel = []
    for day in dates:
        available = [sessions_by[s][day] for s in FILES if day in sessions_by[s]]
        if len(available) < 3:
            continue
        med = float(np.median([x['signal_return'] for x in available]))
        for x in available:
            panel.append({**x, 'cross_section_median_return': med,
                          'residual': float(x['signal_return'] - med)})
    p = pd.DataFrame(panel)
    if p.empty:
        raise ValueError('No synchronized eligible sessions')

    thresholds = {}
    for sym in FILES:
        a = p[(p.symbol == sym) & p.year.between(2017, 2020)].residual.abs().to_numpy()
        if not len(a):
            raise ValueError(f'No 2017-2020 discovery residuals for {sym}')
        thresholds[sym] = float(np.quantile(a, .75, method='linear'))
    p['q75_abs_residual'] = p.symbol.map(thresholds)
    p['normalized_score'] = p.residual.abs() / p.q75_abs_residual.replace(0, np.nan)
    p = p.replace([np.inf, -np.inf], np.nan).dropna(subset=['normalized_score'])

    # Important: the locked child computes PnL only for 2022 onward.
    test_panel = p[p.year >= 2022]
    events = []
    for day, g in test_panel.groupby('date', sort=True):
        winner = g.sort_values(['normalized_score', 'symbol'], ascending=[False, True], kind='stable').iloc[0]
        if float(winner.normalized_score) < 1 or float(winner.residual) == 0:
            continue
        raw = (float(winner.exit_open) / float(winner.entry_open) - 1.0) * 10000.0
        follow_direction = 1 if float(winner.residual) > 0 else -1
        common = {'date': str(day), 'year': int(winner.year), 'symbol': str(winner.symbol),
                  'signal_return_pct': float(winner.signal_return * 100),
                  'cross_section_median_return_pct': float(winner.cross_section_median_return * 100),
                  'residual_pct': float(winner.residual * 100),
                  'q75_abs_residual_pct': float(winner.q75_abs_residual * 100),
                  'normalized_score': float(winner.normalized_score),
                  'entry_ts': str(winner.entry_ts), 'exit_ts': str(winner.exit_ts),
                  'entry_open_bid': float(winner.entry_open), 'exit_open_bid': float(winner.exit_open)}
        follow = {**common, 'direction': 'LONG' if follow_direction > 0 else 'SHORT',
                  'gross_bps': float(raw * follow_direction)}
        fade = {**common, 'direction': 'SHORT' if follow_direction > 0 else 'LONG',
                'gross_bps': float(-raw * follow_direction)}
        for t in (follow, fade):
            for cost in COSTS:
                t[f'net_bps_{cost}bp'] = float(t['gross_bps'] - cost)
        events.append({'follow': follow, 'fade': fade})
    follows = [e['follow'] for e in events]
    fades = [e['fade'] for e in events]

    periods = [('exploratory_2022_2025', 2022, 2025), ('later_check_2026', 2026, 2026)]
    metrics, annual = {}, {}
    for label, lo, hi in periods:
        metrics[label] = {}
        for name, stream in [('follow_candidate', follows), ('matched_fade_parent', fades)]:
            ts = [t for t in stream if lo <= t['year'] <= hi]
            metrics[label][name] = {f'{c}bp': summarize(ts, c) for c in COSTS}
        if lo == 2022:
            annual = {str(y): {f'{c}bp': summarize([t for t in follows if t['year'] == y], c)
                               for c in COSTS} for y in range(2022, 2026)}

    trades_22_25 = [t for t in follows if 2022 <= t['year'] <= 2025]
    trades_2026 = [t for t in follows if t['year'] == 2026]
    weekly = weekly_series(trades_22_25, '2022-01-03', '2025-12-29', 2)
    boot = circular_block_bootstrap_mean_ci(weekly, block=4, reps=5000, seed=288)
    cand22 = metrics['exploratory_2022_2025']['follow_candidate']
    cand26 = metrics['later_check_2026']['follow_candidate']
    positive_years = sum(annual[str(y)]['2bp']['net_bps'] > 0 for y in range(2022, 2026))
    gates = {
        '2022_2025_trades_ge_300': cand22['2bp']['trades'] >= 300,
        '2022_2025_net_positive_2bp': cand22['2bp']['net_bps'] > 0,
        '2022_2025_pf_2bp_ge_1_05': cand22['2bp']['pf'] is not None and cand22['2bp']['pf'] >= 1.05,
        '2022_2025_positive_years_ge_3_of_4': positive_years >= 3,
        '2022_2025_pf_4bp_ge_0_90': cand22['4bp']['pf'] is not None and cand22['4bp']['pf'] >= .90,
        '2022_2025_bootstrap_ci95_lower_gt_0': boot['ci95_low'] is not None and boot['ci95_low'] > 0,
        '2026_trades_ge_50': cand26['2bp']['trades'] >= 50,
        '2026_net_positive_2bp': cand26['2bp']['net_bps'] > 0,
        '2026_pf_2bp_ge_1_00': cand26['2bp']['pf'] is not None and cand26['2bp']['pf'] >= 1.00,
        '2026_net_positive_4bp': cand26['4bp']['net_bps'] > 0,
    }
    result = {
        'candidate_id': 'R288_US_INDEX_INTRADAY_RESIDUAL_FOLLOW',
        'preregistration_commit': '5cf412ad6d335d4c8f651750cd312804ef9a0c61',
        'verdict': 'LULUS' if all(gates.values()) else 'GAGAL',
        'source': source_meta, 'source_latest_utc': latest,
        'method': {
            'signal': '10:00 ET bar open to 12:55 ET bar close return minus same-date median of 3+ eligible symbols',
            'direction': 'follow signed residual',
            'event_selection': 'highest per-symbol normalized absolute residual per date; alphabetical tie-break; score >= 1',
            'frozen_threshold_fit': 'per-symbol Q75 absolute residual fitted on eligible 2017-2020 rows only',
            'entry': '13:05 ET bar open (5 minutes after the 13:00 decision)',
            'exit': '15:55 ET bar open', 'max_positions': 1,
            'costs_bps_roundtrip': list(COSTS), 'costs_are_modeled_not_observed': True,
            'post_entry_pnl_calculated_for_years': '2022-2026 only',
            'thresholds_abs_residual_pct': {k: float(v * 100) for k, v in thresholds.items()},
        },
        'coverage': {
            'valid_sessions_by_symbol': {s: len(v) for s, v in sessions_by.items()},
            'panel_rows_by_year': {str(y): int((p.year == y).sum()) for y in range(2017, 2027)},
            'eligible_dates_with_3plus_symbols_2022_2025': int(p[p.year.between(2022, 2025)].date.nunique()),
            'eligible_dates_with_3plus_symbols_2026': int(p[p.year == 2026].date.nunique()),
            'selected_trades_2022_2025': len(trades_22_25), 'selected_trades_2026': len(trades_2026),
        },
        'metrics': metrics, 'annual_follow_candidate': annual,
        'weekly_bootstrap_2022_2025_at_2bp': boot,
        'gates': gates, 'failed_gates': [k for k, v in gates.items() if not v],
        'interpretation': {
            'program_level_holdout': False,
            '2022_2025_status': 'contaminated exploratory period; not clean program-level OOS',
            '2026_status': 'later chronological check; not claimed pristine program-level holdout',
            'funded_ready': False,
            'limitations': ['M5 BID-only inputs; executable ask-side fills cannot be reconstructed',
                            '1/2/4 bp costs are assumptions, not verified CFD costs',
                            'repeated-flat-bar exclusion is heuristic',
                            'no official contract multipliers / swap / commission model',
                            'no equity-aware DLL/MLL two-phase challenge replay']
        }
    }
    ledger = []
    for e in events:
        ledger.append({'stream': 'follow_candidate', **e['follow']})
        ledger.append({'stream': 'matched_fade_parent', **e['fade']})
    pd.DataFrame(ledger).to_csv(out_dir / 'R288_trade_ledger_2022_2026.csv', index=False)
    pd.DataFrame(audits).to_csv(out_dir / 'R288_session_quality_audit.csv', index=False)
    pd.DataFrame([{'week_start': (pd.Timestamp('2022-01-03') + pd.Timedelta(weeks=i)).date().isoformat(),
                   'net_bps_2bp': float(v)} for i, v in enumerate(weekly)]).to_csv(out_dir / 'R288_weekly_net_2022_2025.csv', index=False)
    (out_dir / 'R288_results.json').write_text(json.dumps(result, indent=2, allow_nan=False) + '\n', encoding='utf-8')
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--data-dir', default='/mnt/data/r288data')
    ap.add_argument('--out-dir', default='/mnt/data/R288_outputs')
    a = ap.parse_args()
    run(Path(a.data_dir), Path(a.out_dir))
