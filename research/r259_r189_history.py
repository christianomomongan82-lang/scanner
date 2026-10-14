#!/usr/bin/env python3
"""R259 cross-feed replay of locked R189/L80 rules on Dukascopy EURUSD M1 BID/ASK, 2016-2025.
This is explicitly NOT exact reproduction of the missing original HistData/spread archive.
Downloads one calendar month per request; a failed or empty month fails the run.
"""
from __future__ import annotations
import calendar
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(".")
DATA = ROOT / "dl" / "r259_r189_2016_2025"
OUT = ROOT / "research"
PIP = 0.0001
START = date(2016, 1, 1)
END_EXCLUSIVE = date(2026, 1, 1)
SL = 6.0
TP = 18.0
MFE_TRIGGER = 6.0
TRAIL = 0.0
TIME_STOP_BARS = 60
MAX_SPREAD_PIPS = 1.5
EXTRA_COST_STRESS = [0.0, 0.2, 0.5, 0.8, 1.0, 2.0]

def l80_fast(df, w1=11, w2=12, disp_thr=15.0, body_thr=2.0,
             late_thr=0.80, dc_thr=7, s0=3, s1=11, dedup=14):
    """Exact signal-generation logic from the locked canonical L80 implementation."""
    close = df.Close.to_numpy()
    op = df.Open.to_numpy()
    # Canonical R189 historical files use a fixed GMT-5 wall clock (no DST).
    # New Dukascopy timestamps are UTC, so map UTC bars to the original fixed session clock.
    hours = ((df.index.hour - 5) % 24).to_numpy()
    n = len(df)
    step = np.diff(close, prepend=np.nan)
    sgnstep = np.sign(step)
    pos = (sgnstep == 1).astype(np.int32)
    neg = (sgnstep == -1).astype(np.int32)
    ppos = np.concatenate(([0], np.cumsum(pos, dtype=np.int64)))
    pneg = np.concatenate(([0], np.cumsum(neg, dtype=np.int64)))
    body = np.abs(close - op)
    d5 = close - np.roll(close, 5)
    d5[:5] = np.nan
    cand = []
    for w in (w1, w2):
        d = close - np.roll(close, w)
        d[:w] = np.nan
        with np.errstate(divide="ignore", invalid="ignore"):
            late = np.abs(d5) / np.abs(d)
        p_count = np.zeros(n, dtype=np.int64)
        n_count = np.zeros(n, dtype=np.int64)
        valid = np.arange(w, n)
        p_count[valid] = ppos[valid + 1] - ppos[valid - w + 1]
        n_count[valid] = pneg[valid + 1] - pneg[valid - w + 1]
        dsign = np.sign(d)
        same = np.where(dsign > 0, p_count, np.where(dsign < 0, n_count, 0))
        ok = (
            (hours >= s0) & (hours <= s1) &
            (np.abs(d) >= disp_thr * PIP) &
            (body >= body_thr * PIP) &
            (late >= late_thr) &
            (same >= dc_thr)
        )
        for i in np.flatnonzero(ok):
            cand.append((int(i), 1 if d[i] < 0 else -1, "L80"))
    cand.sort(key=lambda z: z[0])
    out = []
    last = -10**18
    for i, direction, src in cand:
        if i - last > dedup and i + 1 < n:
            out.append((i, direction, src))
            last = i
    return out

def month_ranges(start: date, end: date):
    cur = start
    while cur < end:
        last_day = calendar.monthrange(cur.year, cur.month)[1]
        next_month = date(cur.year + (cur.month == 12), 1 if cur.month == 12 else cur.month + 1, 1)
        yield cur, min(next_month, end)
        cur = next_month

def download_side(price_type: str, outname: str):
    DATA.mkdir(parents=True, exist_ok=True)
    patch = ROOT / "dukascopy_fetch_patch.cjs"
    downloaded = []
    download_logs = []
    for chunk_start, chunk_end in month_ranges(START, END_EXCLUSIVE):
        stem = f"{outname}_{chunk_start:%Y%m}"
        path = DATA / f"{stem}.csv"
        path.unlink(missing_ok=True)
        cmd = [
            "npx", "--yes", "dukascopy-node",
            "-i", "eurusd", "-from", chunk_start.isoformat(), "-to", chunk_end.isoformat(),
            "-t", "m1", "-p", price_type, "-utc", "0", "-f", "csv", "-fl",
            "-dir", str(DATA), "-fn", stem,
            "-bs", "3", "-bp", "2000", "-r", "5", "-rp", "5000",
        ]
        env = os.environ.copy()
        if patch.is_file():
            env["NODE_OPTIONS"] = (env.get("NODE_OPTIONS", "") + f" --require={patch.resolve()}").strip()
        last_error = "no attempt"
        success = False
        # Short chunk requests are retried up to 3 times. Empty/invalid monthly data is fatal.
        for attempt in range(1, 4):
            path.unlink(missing_ok=True)
            try:
                proc = subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                    text=True, check=False, env=env, timeout=600
                )
                log = proc.stdout or ""
                last_error = f"exit={proc.returncode}; bytes={(path.stat().st_size if path.exists() else 0)}; log={log[-1800:]}"
                if proc.returncode == 0 and path.is_file() and path.stat().st_size > 20:
                    try:
                        preview = pd.read_csv(path, nrows=2)
                        if len(preview.columns) >= 5 and len(preview) > 0:
                            success = True
                            download_logs.append({
                                "side": price_type, "month": chunk_start.strftime("%Y-%m"),
                                "attempt": attempt, "bytes": path.stat().st_size
                            })
                            break
                    except Exception as exc:
                        last_error += f"; parse preview failed: {type(exc).__name__}: {exc}"
                if "Request returned an empty dataset" in log and attempt < 3:
                    last_error += "; empty dataset response retried"
            except Exception as exc:
                last_error = f"{type(exc).__name__}: {exc}"
            if attempt < 3:
                time.sleep(attempt * 3)
        if not success:
            raise RuntimeError(
                f"DOWNLOAD_FAILED side={price_type} month={chunk_start:%Y-%m}..{chunk_end.isoformat()} "
                f"after 3 tries: {last_error}"
            )
        downloaded.append(path)

    frames = []
    for path in downloaded:
        df = pd.read_csv(path)
        frames.append(df)
    combined = pd.concat(frames, ignore_index=True)
    final_path = DATA / f"{outname}.csv"
    combined.to_csv(final_path, index=False)
    return final_path, download_logs

def read_bars(path: Path):
    raw = pd.read_csv(path)
    raw.columns = [str(c).replace("\ufeff", "").strip().lower() for c in raw.columns]
    ts_col = next((c for c in ("timestamp", "datetime", "date") if c in raw.columns), None)
    if ts_col is None:
        raise ValueError(f"No timestamp/datetime column in {path}; columns={list(raw.columns)}")
    ts_raw = raw[ts_col].astype(str).str.strip()
    numeric = pd.to_numeric(ts_raw, errors="coerce")
    if numeric.notna().mean() > 0.95:
        med = float(numeric.abs().median())
        unit = "ms" if med >= 1e11 else ("s" if med >= 1e8 else None)
        if unit is None:
            raise ValueError(f"Unknown numeric timestamp scale in {path}; median={med}")
        idx = pd.to_datetime(numeric, unit=unit, utc=True, errors="coerce")
    else:
        idx = pd.to_datetime(ts_raw, utc=True, errors="coerce")
    req = ["open", "high", "low", "close"]
    missing = set(req) - set(raw.columns)
    if missing or idx.isna().any():
        raise ValueError(f"Missing OHLC columns {sorted(missing)} or invalid timestamps in {path}")
    bars = raw[req].apply(pd.to_numeric, errors="coerce")
    bars.columns = ["Open", "High", "Low", "Close"]
    bars.index = pd.DatetimeIndex(idx, name="timestamp_utc")
    bars = bars.replace([np.inf, -np.inf], np.nan).dropna().sort_index()
    dupes = int(bars.index.duplicated(keep="last").sum())
    bars = bars.loc[~bars.index.duplicated(keep="last")]
    valid = (
        (bars.High >= bars[["Open", "Close"]].max(axis=1)) &
        (bars.Low <= bars[["Open", "Close"]].min(axis=1)) &
        (bars.High >= bars.Low)
    )
    invalid = int((~valid).sum())
    bars = bars.loc[valid]
    if bars.empty:
        raise ValueError(f"No valid OHLC rows in {path}")
    diagnostics = {
        "rows": int(len(bars)),
        "duplicate_timestamps_removed": dupes,
        "invalid_ohlc_rows_removed": invalid,
        "start_utc": bars.index[0].isoformat(),
        "end_utc": bars.index[-1].isoformat(),
        "columns": list(raw.columns),
    }
    return bars, diagnostics

def pf(values):
    a = np.asarray(values, dtype=float)
    gross_profit = float(a[a > 0].sum())
    gross_loss = float(-a[a < 0].sum())
    if gross_loss == 0:
        return "INF" if gross_profit > 0 else None
    return gross_profit / gross_loss

def max_dd(values):
    a = np.asarray(values, dtype=float)
    if not len(a):
        return 0.0
    eq = np.cumsum(a)
    peaks = np.maximum.accumulate(np.r_[0.0, eq])
    return float(np.max(peaks[1:] - eq))

def metric_block(trades, extra_cost, elapsed_weeks):
    net = np.array([t["gross_pips"] - extra_cost for t in trades], dtype=float)
    wins = int(np.sum(net > 0))
    return {
        "trades": int(len(net)),
        "PF": pf(net),
        "net_pips": float(net.sum()) if len(net) else 0.0,
        "max_drawdown_pips": max_dd(net),
        "win_rate": float(wins / len(net)) if len(net) else None,
        "mean_net_pips_per_trade": float(net.mean()) if len(net) else None,
        "trades_per_week": float(len(net) / elapsed_weeks) if elapsed_weeks > 0 else None,
    }

def simulate(df, bid, ask, signals, corrected_timeout):
    n = len(df)
    idx = df.index
    bo, bh, bl = (bid[k].to_numpy(float) for k in ("Open", "High", "Low"))
    ao, ah, al = (ask[k].to_numpy(float) for k in ("Open", "High", "Low"))
    spread_open = (ask.Open.to_numpy(float) - bid.Open.to_numpy(float)) / PIP
    trades = []
    active_exit = -1
    spread_rejects = 0
    overlaps = 0
    censored = 0
    for si, direction, _src in signals:
        e = si + 1
        if e >= n:
            continue
        if not np.isfinite(spread_open[e]) or spread_open[e] < -1e-9 or spread_open[e] > MAX_SPREAD_PIPS + 1e-12:
            spread_rejects += 1
            continue
        if e <= active_exit:
            overlaps += 1
            continue
        entry = float(ask.Open.iat[e] if direction == 1 else bid.Open.iat[e])
        hard_stop = entry - direction * SL * PIP
        target = entry + direction * TP * PIP
        fav = entry
        trail_active = False
        stop = hard_stop
        scheduled = e + TIME_STOP_BARS
        if scheduled >= n:
            censored += 1
            active_exit = n
            continue
        last = scheduled - 1 if corrected_timeout else scheduled
        exit_i = None
        gross = None
        reason = None
        for j in range(e, last + 1):
            current_stop = stop if trail_active else hard_stop
            stop_hit = (bl[j] <= current_stop) if direction == 1 else (ah[j] >= current_stop)
            target_hit = (bh[j] >= target) if direction == 1 else (al[j] <= target)
            if stop_hit:
                exit_i = j
                gross = direction * (current_stop - entry) / PIP
                reason = "TRAIL_STOP" if trail_active else "STOP"
                break
            if target_hit:
                exit_i = j
                gross = TP
                reason = "TARGET"
                break
            if direction == 1:
                fav = max(fav, bh[j])
                favourable = (fav - entry) / PIP
                if favourable >= MFE_TRIGGER:
                    new_stop = entry + (favourable - TRAIL) * PIP
                    if new_stop > stop:
                        stop = new_stop
                    trail_active = True
            else:
                fav = min(fav, al[j])
                favourable = (entry - fav) / PIP
                if favourable >= MFE_TRIGGER:
                    new_stop = entry - (favourable - TRAIL) * PIP
                    if (not trail_active) or new_stop < stop:
                        stop = new_stop
                    trail_active = True
        if exit_i is None:
            exit_i = scheduled
            # Time-stop executes at the scheduled bar OPEN, before its high/low is observed.
            exit_price = float(bid.Open.iat[exit_i] if direction == 1 else ask.Open.iat[exit_i])
            gross = direction * (exit_price - entry) / PIP
            reason = "TIME_OPEN_CAUSAL" if corrected_timeout else "TIME_OPEN_LEGACY"
        trades.append({
            "signal_utc": idx[si].isoformat(),
            "entry_utc": idx[e].isoformat(),
            "exit_utc": idx[exit_i].isoformat(),
            "direction": "LONG" if direction == 1 else "SHORT",
            "entry_price": entry,
            "entry_spread_pips": float(spread_open[e]),
            "exit_reason": reason,
            "gross_pips": float(gross),
            "engine": "causal_time_stop" if corrected_timeout else "legacy",
        })
        active_exit = exit_i
    return trades, {
        "signals_filtered_by_spread_in_sim": spread_rejects,
        "overlap_skipped": overlaps,
        "end_of_data_censored": censored,
    }

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = {
        "status": "STARTED",
        "round": "R259",
        "method": "Locked R189/L80 rules replayed without parameter changes on Dukascopy EURUSD M1 BID/ASK 2016-2025; independent cross-feed replication, not exact reproduction of the unavailable HistData/spread inputs.",
        "window_utc": {"from_inclusive": START.isoformat(), "to_exclusive": END_EXCLUSIVE.isoformat()},
        "locked_parameters": {
            "displacement_pips": 15, "late_ratio_min": 0.8, "body_pips_min": 2,
            "directional_consistency_min": 7, "signal_hours_utc": "03..11 excluding 06 and 09",
            "dedup_bars": 14, "entry_spread_cap_pips": MAX_SPREAD_PIPS,
            "SL_pips": SL, "TP_pips": TP, "MFE_trigger_pips": MFE_TRIGGER,
            "trailing_distance_pips": TRAIL, "time_stop_bars": TIME_STOP_BARS,
            "extra_cost_stress_pips_per_trade": EXTRA_COST_STRESS,
        },
        "notes": [
            "Dukascopy is a different feed from the unavailable original 2016-2025 HistData and spread files; this is a cross-feed replication, not exact historical reproduction.",
            "The locked fixed GMT-5 signal clock is retained with no DST: eligible wall-clock hours 03..11, excluding 06 and 09 (corresponding to UTC hours 08..16 excluding 11 and 14).",
            "Empty individual daily buckets are allowed because weekends and market holidays can legitimately have no minute candles; non-empty data and coverage diagnostics are still checked.",
            "Extra costs are applied per closed trade on top of executable bid/ask prices.",
            "Legacy and causal exits are both reported; causal is the implementation that exits at the time-stop bar open before considering that bar's high/low.",
        ],
    }
    results_path = OUT / "r259_r189_history_results.json"
    try:
        bid_path, bid_logs = download_side("bid", "eurusd_bid")
        ask_path, ask_logs = download_side("ask", "eurusd_ask")
        bid, bid_diag = read_bars(bid_path)
        ask, ask_diag = read_bars(ask_path)
        common = bid.index.intersection(ask.index).sort_values()
        if len(common) < 10000:
            raise RuntimeError(f"Only {len(common)} common bid/ask M1 bars; refusing to test")
        bid = bid.loc[common]
        ask = ask.loc[common]
        df = bid.copy()
        spread_open = (ask.Open - bid.Open) / PIP
        if (spread_open < -1e-8).any():
            raise RuntimeError(f"Negative ask-bid open spread in {int((spread_open < -1e-8).sum())} rows")
        if not np.isfinite(spread_open.to_numpy()).all():
            raise RuntimeError("Missing/non-finite spread after bid/ask timestamp alignment")
        # Generate the canonical L80 signals first; preserve R189 order of hour & spread filters.
        all_signals = l80_fast(df, disp_thr=15, late_thr=0.8)
        eligible_signals = [
            (i, d, src) for i, d, src in all_signals
            if ((df.index[i].hour - 5) % 24) not in (6, 9) and i + 1 < len(df)
            and spread_open.iat[i + 1] <= MAX_SPREAD_PIPS + 1e-12
        ]
        legacy, legacy_diag = simulate(df, bid, ask, eligible_signals, corrected_timeout=False)
        causal, causal_diag = simulate(df, bid, ask, eligible_signals, corrected_timeout=True)
        start_ts, end_ts = df.index[0], df.index[-1]
        elapsed_weeks = max((end_ts - start_ts).total_seconds() / (7 * 24 * 3600), 1 / 7)
        report.update({
            "status": "COMPLETE",
            "data": {
                "bid_file_sha256": hashlib.sha256(bid_path.read_bytes()).hexdigest(),
                "ask_file_sha256": hashlib.sha256(ask_path.read_bytes()).hexdigest(),
                "bid_diagnostics": bid_diag, "ask_diagnostics": ask_diag,
                "common_bars": int(len(common)),
                "start_utc": start_ts.isoformat(), "end_utc": end_ts.isoformat(),
                "spread_min_pips": float(spread_open.min()),
                "spread_median_pips": float(spread_open.median()),
                "spread_p95_pips": float(spread_open.quantile(0.95)),
                "spread_max_pips": float(spread_open.max()),
                "signals_before_R189_hour/spread_filters": int(len(all_signals)),
                "eligible_signals": int(len(eligible_signals)),
                "calendar_weeks_in_sample": float(elapsed_weeks),
                "monthly_downloads_bid": bid_logs,
                "monthly_downloads_ask": ask_logs,
            },
            "legacy_engine": {
                "diagnostics": legacy_diag,
                "at_0_2_extra_cost": metric_block(legacy, 0.2, elapsed_weeks),
                "cost_stress": [{"extra_cost_pips": c, **metric_block(legacy, c, elapsed_weeks)} for c in EXTRA_COST_STRESS],
            },
            "causal_time_stop_engine": {
                "diagnostics": causal_diag,
                "at_0_2_extra_cost": metric_block(causal, 0.2, elapsed_weeks),
                "cost_stress": [{"extra_cost_pips": c, **metric_block(causal, c, elapsed_weeks)} for c in EXTRA_COST_STRESS],
            },
            "comparison_at_0_2_extra_cost": {
                "legacy": metric_block(legacy, 0.2, elapsed_weeks),
                "causal_time_stop": metric_block(causal, 0.2, elapsed_weeks),
            },
        })

        # Period-separated evaluation is attribution by entry time. A trade exiting at/after
        # the period boundary is excluded from that period to avoid cross-boundary leakage.
        period_windows = {
            "full_2016_2025": (pd.Timestamp("2016-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")),
            "discovery_2016_2020": (pd.Timestamp("2016-01-01", tz="UTC"), pd.Timestamp("2021-01-01", tz="UTC")),
            "validation_2021": (pd.Timestamp("2021-01-01", tz="UTC"), pd.Timestamp("2022-01-01", tz="UTC")),
            "forward_2022_2025": (pd.Timestamp("2022-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")),
            "reported_forward_2021_2025": (pd.Timestamp("2021-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")),
        }
        def phase_subset(trade_list, lo, hi):
            entered = [t for t in trade_list if lo <= pd.Timestamp(t["entry_utc"]) < hi]
            complete = [t for t in entered if pd.Timestamp(t["exit_utc"]) < hi]
            return entered, complete

        report["period_metrics"] = {}
        for period_name, (lo, hi) in period_windows.items():
            weeks = (hi - lo).total_seconds() / (7 * 24 * 3600)
            period_result = {"start_utc": lo.isoformat(), "end_exclusive_utc": hi.isoformat(),
                             "elapsed_weeks": weeks, "extra_cost_stress": {}}
            for engine_name, trade_list in (("legacy", legacy), ("causal_time_stop", causal)):
                entered, completed = phase_subset(trade_list, lo, hi)
                period_result.setdefault("engines", {})[engine_name] = {
                    "entries_attributed_to_period": len(entered),
                    "completed_inside_period": len(completed),
                    "excluded_cross_boundary_exits": len(entered) - len(completed),
                    "cost_stress": [
                        {"extra_cost_pips": c, **metric_block(completed, c, weeks)}
                        for c in EXTRA_COST_STRESS
                    ],
                }
            report["period_metrics"][period_name] = period_result

        def weekly_block_bootstrap(trade_list, extra_cost, lo, hi, block_weeks=4, reps=5000, seed=189):
            entered, completed = phase_subset(trade_list, lo, hi)
            n_weeks = int(np.ceil((hi - lo).total_seconds() / (7 * 24 * 3600)))
            weekly_net = np.zeros(n_weeks, dtype=float)
            weekly_n = np.zeros(n_weeks, dtype=int)
            for trade in completed:
                ts = pd.Timestamp(trade["entry_utc"])
                w = int((ts - lo).total_seconds() // (7 * 24 * 3600))
                if 0 <= w < n_weeks:
                    weekly_net[w] += float(trade["gross_pips"]) - extra_cost
                    weekly_n[w] += 1
            if n_weeks < block_weeks or len(completed) == 0:
                return {"trades": len(completed), "weeks": n_weeks, "error": "insufficient sample"}
            rng = np.random.default_rng(seed)
            block_count = int(np.ceil(n_weeks / block_weeks))
            means = np.empty(reps, dtype=float)
            starts = np.arange(n_weeks)
            for k in range(reps):
                pick = rng.integers(0, n_weeks, size=block_count)
                ix = np.concatenate([(s + np.arange(block_weeks)) % n_weeks for s in pick])[:n_weeks]
                means[k] = weekly_net[ix].mean()
            return {
                "trades": len(completed), "weeks": n_weeks, "block_weeks": block_weeks,
                "reps": reps, "seed": seed,
                "observed_mean_net_pips_per_week": float(weekly_net.mean()),
                "observed_net_pips": float(weekly_net.sum()),
                "observed_mean_net_pips_per_trade": float(np.mean([t["gross_pips"] - extra_cost for t in completed])),
                "probability_mean_weekly_net_positive": float(np.mean(means > 0)),
                "bootstrap_95pct_ci_mean_weekly_net_pips": [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))],
            }

        report["forward_2022_2025_weekly_block_bootstrap"] = {
            str(cost): weekly_block_bootstrap(
                causal, cost, period_windows["forward_2022_2025"][0],
                period_windows["forward_2022_2025"][1], block_weeks=4, reps=5000, seed=189
            )
            for cost in (0.2, 1.0, 2.0)
        }

        annual = []
        for year in sorted({pd.Timestamp(t["entry_utc"]).year for t in causal}):
            yy = [t for t in causal if pd.Timestamp(t["entry_utc"]).year == year]
            annual.append({"year": year, **metric_block(yy, 0.2, 52.0)})
        report["causal_time_stop_engine"]["annual_at_0_2_extra_cost"] = annual

        # Annual cohorts under higher cost stresses, with the same period-boundary rule.
        annual_stress = []
        for year in sorted({pd.Timestamp(t["entry_utc"]).year for t in causal}):
            y0 = pd.Timestamp(f"{year}-01-01", tz="UTC")
            y1 = pd.Timestamp(f"{year + 1}-01-01", tz="UTC")
            entered, completed = phase_subset(causal, y0, y1)
            weeks = (y1 - y0).total_seconds() / (7 * 24 * 3600)
            for cost in (0.2, 1.0, 2.0):
                annual_stress.append({
                    "year": year, "entries_attributed_to_year": len(entered),
                    "completed_inside_year": len(completed), "extra_cost_pips": cost,
                    **metric_block(completed, cost, weeks)
                })
        report["causal_time_stop_engine"]["annual_cost_stress"] = annual_stress
        monthly = []
        for month in sorted({pd.Timestamp(t["entry_utc"]).strftime("%Y-%m") for t in causal}):
            mm = [t for t in causal if pd.Timestamp(t["entry_utc"]).strftime("%Y-%m") == month]
            weeks = calendar.monthrange(int(month[:4]), int(month[5:7]))[1] / 7.0
            monthly.append({"month_utc": month, **metric_block(mm, 0.2, weeks)})
        report["causal_time_stop_engine"]["monthly_at_0_2_extra_cost"] = monthly

        # Binary decision for this locked cross-feed robustness test.
        fwd = report["period_metrics"]["forward_2022_2025"]["engines"]["causal_time_stop"]["cost_stress"]
        fwd_by_cost = {round(row["extra_cost_pips"], 4): row for row in fwd}
        fwd_plus1 = fwd_by_cost[1.0]
        fwd_plus2 = fwd_by_cost[2.0]
        annual_forward_plus1 = [
            row for row in annual_stress
            if 2022 <= row["year"] <= 2025 and row["extra_cost_pips"] == 1.0
            and row["trades"] >= 20
        ]
        bootstrap_plus1 = report["forward_2022_2025_weekly_block_bootstrap"]["1.0"]
        gate_results = {
            "forward_completed_trades_ge_100": fwd_plus1["trades"] >= 100,
            "forward_PF_ge_1.10_at_plus_1pip": isinstance(fwd_plus1["PF"], (int, float)) and fwd_plus1["PF"] >= 1.10,
            "forward_PF_ge_1.05_at_plus_2pip": isinstance(fwd_plus2["PF"], (int, float)) and fwd_plus2["PF"] >= 1.05,
            "every_forward_year_with_at_least_20_trades_PF_ge_1_at_plus_1pip": bool(annual_forward_plus1) and all(
                isinstance(row["PF"], (int, float)) and row["PF"] >= 1.0 for row in annual_forward_plus1
            ),
            "four_week_bootstrap_95pct_lower_weekly_net_gt_zero_at_plus_1pip":
                len(bootstrap_plus1.get("bootstrap_95pct_ci_mean_weekly_net_pips", [])) == 2
                and bootstrap_plus1["bootstrap_95pct_ci_mean_weekly_net_pips"][0] > 0,
        }
        report["acceptance_gates"] = {
            "rule": "All listed gates must pass; no retuning is permitted after forward results.",
            "gates": gate_results,
            "forward_PF_plus_1pip": fwd_plus1["PF"],
            "forward_PF_plus_2pip": fwd_plus2["PF"],
            "forward_trades": fwd_plus1["trades"],
            "annual_forward_cohorts_plus_1pip": annual_forward_plus1,
            "forward_weekly_bootstrap_plus_1pip": bootstrap_plus1,
        }
        report["verdict"] = "LULUS" if all(gate_results.values()) else "GAGAL"

        pd.DataFrame(legacy).to_csv(OUT / "r259_r189_history_legacy_trades.csv", index=False)
        pd.DataFrame(causal).to_csv(OUT / "r259_r189_history_causal_trades.csv", index=False)
    except Exception as exc:
        report.update({
            "status": "FAILED",
            "error": f"{type(exc).__name__}: {exc}",
        })
        results_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2, allow_nan=False), flush=True)
        return 1
    results_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, allow_nan=False), flush=True)
    return 0

if __name__ == "__main__":
    sys.exit(main())
