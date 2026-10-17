#!/usr/bin/env python3
"""R298 locked XAUUSD London Asian-range sweep-and-reclaim replay.
Only scores data through 2025-12-31 UTC; uses paired BID/ASK OHLC and strict active-bar checks.
"""
from __future__ import annotations
import argparse, gzip, hashlib, json, math
from pathlib import Path
from datetime import timedelta
import numpy as np
import pandas as pd

BID_SHA = "b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575"
ASK_SHA = "b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9"
CUTOFF = pd.Timestamp("2026-01-01T00:00:00Z")
COSTS = [0.00, 0.10, 0.30, 0.50]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def pf_r(vals):
    vals = np.asarray(vals, dtype=float)
    wins = vals[vals > 0].sum()
    losses = -vals[vals < 0].sum()
    if losses <= 0:
        return None if wins <= 0 else "INF"
    return float(wins / losses)


def max_closed_dd(vals):
    vals = np.asarray(vals, dtype=float)
    if len(vals) == 0:
        return 0.0
    eq = np.cumsum(vals)
    peaks = np.maximum.accumulate(np.r_[0.0, eq])[1:]
    return float(np.max(peaks - eq))


def metric_pack(rows, cost):
    if not rows:
        return {"trades": 0, "net_R": 0.0, "gross_price_PnL_per_oz": 0.0, "PF_R": None,
                "win_rate_pct": None, "max_closed_DD_R": 0.0, "longs": 0, "shorts": 0,
                "stop_exits": 0, "target_exits": 0, "time_exits": 0, "mean_hold_min": None}
    net = np.array([(r["raw_price_pnl_per_oz"] - cost) / r["initial_risk_per_oz"] for r in rows], dtype=float)
    raw = np.array([r["raw_price_pnl_per_oz"] for r in rows], dtype=float)
    holds = np.array([r["hold_minutes"] for r in rows], dtype=float)
    return {
        "trades": int(len(rows)), "net_R": float(net.sum()),
        "gross_price_PnL_per_oz": float(raw.sum()), "PF_R": pf_r(net),
        "win_rate_pct": float(100 * np.mean(net > 0)), "max_closed_DD_R": max_closed_dd(net),
        "longs": int(sum(r["direction"] == "LONG" for r in rows)),
        "shorts": int(sum(r["direction"] == "SHORT" for r in rows)),
        "stop_exits": int(sum(r["exit_type"] == "STOP" for r in rows)),
        "target_exits": int(sum(r["exit_type"] == "TARGET" for r in rows)),
        "time_exits": int(sum(r["exit_type"] == "TIME" for r in rows)),
        "mean_hold_min": float(holds.mean()) if len(holds) else None,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="/mnt/data/r298data")
    ap.add_argument("--out-dir", default="/mnt/data/R298_outputs")
    args = ap.parse_args()
    data_dir, out_dir = Path(args.data_dir), Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    bid_path = data_dir / "xauusd_bid_M5_2016-2026.csv.gz"
    ask_path = data_dir / "xauusd_ask_M5_2016-2026.csv.gz"
    hashes = {"bid_sha256": sha256(bid_path), "ask_sha256": sha256(ask_path)}
    if hashes["bid_sha256"] != BID_SHA or hashes["ask_sha256"] != ASK_SHA:
        raise ValueError(f"Input SHA256 mismatch: {hashes}")

    bid_all = pd.read_csv(bid_path, compression="gzip")
    ask_all = pd.read_csv(ask_path, compression="gzip")
    if len(bid_all) != len(ask_all) or not np.array_equal(bid_all.timestamp.to_numpy(), ask_all.timestamp.to_numpy()):
        raise ValueError("BID/ASK timestamp pairing failed")
    if bid_all.timestamp.duplicated().any() or ask_all.timestamp.duplicated().any():
        raise ValueError("Duplicate timestamps")
    if not np.array_equal(bid_all.timestamp.to_numpy() % 300000, np.zeros(len(bid_all), dtype=np.int64)):
        raise ValueError("Timestamp not M5 aligned")
    for label, df in [("BID", bid_all), ("ASK", ask_all)]:
        if ((df.high < df.low) | (df.high < df[["open", "close"]].max(axis=1)) |
            (df.low > df[["open", "close"]].min(axis=1))).any():
            raise ValueError(f"Invalid OHLC ordering in {label}")
    all_rows = len(bid_all)
    ts_all = pd.to_datetime(bid_all.timestamp, unit="ms", utc=True)
    before = ts_all < CUTOFF
    excluded_2026_rows = int((~before).sum())
    # Critical: discard 2026 before active detection, session construction or any outcome calculation.
    bid = bid_all.loc[before].reset_index(drop=True)
    ask = ask_all.loc[before].reset_index(drop=True)
    ts = pd.DatetimeIndex(ts_all[before].reset_index(drop=True))
    n = len(bid)

    b_active = (bid.high.to_numpy() > bid.low.to_numpy()) | (bid.open.to_numpy() != bid.close.to_numpy())
    a_active = (ask.high.to_numpy() > ask.low.to_numpy()) | (ask.open.to_numpy() != ask.close.to_numpy())
    paired_active = b_active & a_active
    paired_either_active = b_active | a_active
    b_o, b_h, b_l, b_c = (bid[k].to_numpy(float) for k in ["open", "high", "low", "close"])
    a_o, a_h, a_l, a_c = (ask[k].to_numpy(float) for k in ["open", "high", "low", "close"])
    mid_h, mid_l, mid_c = (b_h + a_h) / 2, (b_l + a_l) / 2, (b_c + a_c) / 2
    # Timestamp-to-index map supports exact-delay entry and exact time exits only.
    ts_ns = ts.asi8
    idx_by_ns = {int(v): i for i, v in enumerate(ts_ns)}
    five_ns = int(pd.Timedelta(minutes=5).value)

    utc_dates = np.array([x.date() for x in ts])
    utc_min = np.array([x.hour * 60 + x.minute for x in ts])
    london = ts.tz_convert("Europe/London")
    lon_dates = np.array([x.date() for x in london])
    lon_min = np.array([x.hour * 60 + x.minute for x in london])
    lon_weekday = np.array([x.weekday() < 5 for x in london])

    # Build contiguous UTC-date index groups once (the archive is timestamp-sorted).
    # This avoids repeatedly scanning the full ~878k-row array per day.
    change_points = np.r_[0, np.flatnonzero(utc_dates[1:] != utc_dates[:-1]) + 1, len(utc_dates)]
    utc_groups = {utc_dates[a]: np.arange(a, b, dtype=np.int64) for a, b in zip(change_points[:-1], change_points[1:])}

    # Pre-outcome quality: complete 72-row UTC Asian window and all paired-active.
    asia_by_date = {}
    asia_audit = []
    for d in sorted(utc_groups):
        day_ix = utc_groups[d]
        ix = day_ix[utc_min[day_ix] < 360]
        if len(ix) == 0:
            continue
        expected = np.arange(0, 360, 5, dtype=int)
        exact_times = np.array_equal(utc_min[ix], expected) if len(ix) == 72 else False
        active_count = int(paired_active[ix].sum())
        ok = bool(len(ix) == 72 and exact_times and active_count == 72)
        asia_audit.append({"utc_date": str(d), "observed_rows_00_0555": int(len(ix)),
                           "paired_active_rows": active_count, "complete_exact_grid": bool(exact_times),
                           "eligible_asia_range": ok})
        if ok:
            asia_by_date[d] = {"high": float(np.max(mid_h[ix])), "low": float(np.min(mid_l[ix])),
                               "mid": float((np.max(mid_h[ix]) + np.min(mid_l[ix])) / 2),
                               "width": float(np.max(mid_h[ix]) - np.min(mid_l[ix]))}

    # First eligible reclaim per date. Ambiguous both-direction bars exclude the whole date if first event.
    london_signal_audit = []
    first_events = {}
    ambiguous_dates = set()
    dates_with_asia = set(asia_by_date.keys())
    london_date_candidates = sorted(set(lon_dates[(lon_min >= 420) & (lon_min < 600) & lon_weekday]))
    for d in london_date_candidates:
        if d not in asia_by_date:
            continue
        rg = asia_by_date[d]
        if rg["width"] <= 0:
            continue
        day_ix = utc_groups.get(d, np.empty(0, dtype=np.int64))
        ix = day_ix[(lon_dates[day_ix] == d) & (lon_min[day_ix] >= 420) & (lon_min[day_ix] < 600) & lon_weekday[day_ix]]
        first = None
        amb = False
        for i in ix:
            if not paired_active[i]:
                continue
            close_inside = rg["low"] <= mid_c[i] <= rg["high"]
            short_signal = bool(close_inside and mid_h[i] >= rg["high"] + 0.10 * rg["width"])
            long_signal = bool(close_inside and mid_l[i] <= rg["low"] - 0.10 * rg["width"])
            if short_signal and long_signal:
                amb = True
                break
            if short_signal or long_signal:
                first = (int(i), "SHORT" if short_signal else "LONG")
                break
        if amb:
            ambiguous_dates.add(d)
            london_signal_audit.append({"utc_date": str(d), "status": "AMBIGUOUS_BOTH_DIRECTIONS", "signal_timestamp_utc": "", "direction": ""})
        elif first:
            i, direction = first
            first_events[d] = (i, direction)
            london_signal_audit.append({"utc_date": str(d), "status": "FIRST_RECLAIM_FOUND", "signal_timestamp_utc": ts[i].isoformat(), "direction": direction})
        else:
            london_signal_audit.append({"utc_date": str(d), "status": "NO_RECLAIM", "signal_timestamp_utc": "", "direction": ""})

    completed = []
    event_quality = []
    skip_counts = {}
    def skip(d, i, direction, reason, entry_ts=None, risk=None, rr=None):
        skip_counts[reason] = skip_counts.get(reason, 0) + 1
        event_quality.append({"signal_date_utc": str(d), "signal_timestamp_utc": ts[i].isoformat(),
                              "direction": direction, "status": "SKIPPED", "reason": reason,
                              "entry_timestamp_utc": entry_ts.isoformat() if entry_ts is not None else "",
                              "initial_risk_per_oz": risk, "planned_reward_risk": rr})

    for d, (si, direction) in sorted(first_events.items(), key=lambda kv: ts[kv[1][0]]):
        signal_ns = int(ts_ns[si])
        entry_ns = signal_ns + int(pd.Timedelta(minutes=10).value)
        exit_ns = entry_ns + int(pd.Timedelta(hours=4).value)
        ei = idx_by_ns.get(entry_ns)
        xi = idx_by_ns.get(exit_ns)
        entry_time = pd.Timestamp(entry_ns, tz="UTC")
        if ei is None:
            skip(d, si, direction, "entry_timestamp_missing", entry_time); continue
        if not paired_active[ei]:
            skip(d, si, direction, "entry_quote_static_or_one_sided", entry_time); continue
        if xi is None:
            skip(d, si, direction, "time_exit_timestamp_missing", entry_time); continue
        if not paired_active[xi]:
            skip(d, si, direction, "exact_time_exit_quote_static_or_one_sided", entry_time); continue
        # No artificial fill shift: if the feed has a missing timestamp before the cap, this event is unusable.
        if ts_ns[xi] - ts_ns[ei] != 48 * five_ns:
            skip(d, si, direction, "time_exit_not_exactly_4h", entry_time); continue

        rg = asia_by_date[d]
        target = float(rg["mid"])
        entry = float(a_o[ei] if direction == "LONG" else b_o[ei])
        stop = float(b_l[si] if direction == "LONG" else a_h[si])
        if direction == "LONG":
            risk = entry - stop
            reward = target - entry
        else:
            risk = stop - entry
            reward = entry - target
        if not (risk > 0):
            skip(d, si, direction, "stop_not_adverse_of_entry", entry_time, float(risk), None); continue
        if not (reward > 0):
            skip(d, si, direction, "midpoint_target_not_favorable", entry_time, float(risk), float(reward / risk)); continue
        rr = reward / risk
        if rr < 1.0:
            skip(d, si, direction, "planned_reward_risk_below_1", entry_time, float(risk), float(rr)); continue

        exit_idx = None
        exit_type = None
        exit_price = None
        exit_ts = None
        path_fail = None
        prev_ns = None
        for j in range(ei, xi + 1):
            if not paired_active[j]:
                path_fail = "trade_path_static_or_one_sided_quote"
                break
            if prev_ns is not None and ts_ns[j] - prev_ns != five_ns:
                path_fail = "trade_path_missing_m5_timestamp"
                break
            prev_ns = int(ts_ns[j])
            if direction == "LONG":
                op, hi, lo = float(b_o[j]), float(b_h[j]), float(b_l[j])
                if op <= stop:
                    exit_idx, exit_type, exit_price = j, "STOP", op
                elif op >= target:
                    exit_idx, exit_type, exit_price = j, "TARGET", op
                elif j == xi:
                    exit_idx, exit_type, exit_price = j, "TIME", op
                else:
                    hit_stop, hit_target = (lo <= stop), (hi >= target)
                    if hit_stop:
                        exit_idx, exit_type, exit_price = j, "STOP", float(stop)
                    elif hit_target:
                        exit_idx, exit_type, exit_price = j, "TARGET", float(target)
            else:
                op, hi, lo = float(a_o[j]), float(a_h[j]), float(a_l[j])
                if op >= stop:
                    exit_idx, exit_type, exit_price = j, "STOP", op
                elif op <= target:
                    exit_idx, exit_type, exit_price = j, "TARGET", op
                elif j == xi:
                    exit_idx, exit_type, exit_price = j, "TIME", op
                else:
                    hit_stop, hit_target = (hi >= stop), (lo <= target)
                    if hit_stop:
                        exit_idx, exit_type, exit_price = j, "STOP", float(stop)
                    elif hit_target:
                        exit_idx, exit_type, exit_price = j, "TARGET", float(target)
            if exit_idx is not None:
                exit_ts = ts[exit_idx]
                break
        if path_fail:
            skip(d, si, direction, path_fail, entry_time, float(risk), float(rr)); continue
        if exit_idx is None or exit_type is None or exit_price is None:
            skip(d, si, direction, "simulation_no_exit", entry_time, float(risk), float(rr)); continue
        raw_pnl = float(exit_price - entry) if direction == "LONG" else float(entry - exit_price)
        row = {
            "signal_date_utc": str(d), "signal_timestamp_utc": ts[si].isoformat(), "direction": direction,
            "entry_timestamp_utc": ts[ei].isoformat(), "exit_timestamp_utc": exit_ts.isoformat(),
            "entry_price_executable_side": entry, "stop_price_executable_side": stop,
            "target_price_midpoint": target, "planned_reward_risk": float(rr),
            "initial_risk_per_oz": float(risk), "exit_price_executable_side": float(exit_price),
            "exit_type": exit_type, "raw_price_pnl_per_oz": raw_pnl,
            "hold_minutes": float((exit_ts - ts[ei]).total_seconds() / 60),
            "entry_year": int(ts[ei].year), "entry_week_start_monday": str((ts[ei].date() - timedelta(days=ts[ei].weekday()))),
            "signal_mid_close": float(mid_c[si]), "asia_range_high_mid": float(rg["high"]),
            "asia_range_low_mid": float(rg["low"]), "asia_range_width_mid": float(rg["width"]),
        }
        completed.append(row)
        event_quality.append({"signal_date_utc": str(d), "signal_timestamp_utc": ts[si].isoformat(),
                              "direction": direction, "status": "COMPLETED", "reason": exit_type,
                              "entry_timestamp_utc": ts[ei].isoformat(), "initial_risk_per_oz": float(risk),
                              "planned_reward_risk": float(rr)})

    # Compute period outcomes without viewing any 2026 rows.
    trade_df = pd.DataFrame(completed)
    quality_df = pd.DataFrame(event_quality)
    annual = []
    summary = {"r298": "XAUUSD_LONDON_ASIA_RANGE_SWEEP_RECLAIM", "data_hashes": hashes,
               "data_quality": {"rows_source_each_side": all_rows, "rows_used_before_cutoff": n,
                                "rows_excluded_2026_and_later_before_signal_build": excluded_2026_rows,
                                "first_used_timestamp_utc": ts[0].isoformat(), "last_used_timestamp_utc": ts[-1].isoformat(),
                                "bid_active_before_cutoff": int(b_active.sum()), "ask_active_before_cutoff": int(a_active.sum()),
                                "paired_active_before_cutoff": int(paired_active.sum()),
                                "paired_either_active_before_cutoff": int(paired_either_active.sum()),
                                "asia_range_days_eligible": int(len(asia_by_date)),
                                "asia_window_dates_audited": int(len(asia_audit)),
                                "london_weekday_dates_audited": int(len(london_date_candidates)),
               "london_weekday_dates_with_eligible_asia_range": int(sum(1 for d in london_date_candidates if d in asia_by_date)),
                                "ambiguous_same_bar_dates": int(len(ambiguous_dates)),
                                "first_reclaim_events": int(len(first_events)),
                                "completed_trades": int(len(completed)),
                                "skip_counts": skip_counts},
               "parameters_locked": {"asia_utc_window": "00:00-05:55 inclusive; all 72 paired-active bars",
                                     "london_local_window": "[07:00,10:00) Europe/London",
                                     "sweep_threshold": "0.10 x Asian range width", "signal": "first M5 sweep and close back inside",
                                     "entry_delay": "signal bar start + 10 minutes", "stop": "signal BID low for LONG / ASK high for SHORT",
                                     "target": "Asian midpoint", "min_planned_reward_risk": 1.0,
                                     "max_holding": "4 hours from entry", "same_bar_stop_target_priority": "STOP",
                                     "extra_costs_usd_per_oz_round_trip": COSTS,
                                     "discovery": "2016-2020", "validation": "2021-2025", "2026_pnl_calculated": False}}

    for period, y0, y1 in [("discovery_2016_2020", 2016, 2020), ("validation_2021_2025", 2021, 2025)]:
        rows = [r for r in completed if y0 <= r["entry_year"] <= y1]
        summary.setdefault("periods", {})[period] = {f"cost_{cost:.2f}": metric_pack(rows, cost) for cost in COSTS}
        for year in range(y0, y1 + 1):
            yr = [r for r in rows if r["entry_year"] == year]
            for cost in COSTS:
                m = metric_pack(yr, cost)
                annual.append({"period": period, "year": year, "extra_cost_usd_per_oz": cost, **m})
    # Bootstrap validation weekly net-R series; use 261 Monday starts 2021-01-04 through 2025-12-29 incl. zeros.
    val_rows = [r for r in completed if 2021 <= r["entry_year"] <= 2025]
    weeks = [pd.Timestamp("2021-01-04") + pd.Timedelta(days=7*k) for k in range(261)]
    week_lookup = {w.strftime("%Y-%m-%d"): k for k, w in enumerate(weeks)}
    weekly = np.zeros(261, dtype=float)
    unmatched_val_week = 0
    for r in val_rows:
        w = r["entry_week_start_monday"]
        # Ignore no event on a week preceding the first Monday; count if this edge case occurs.
        if w not in week_lookup:
            unmatched_val_week += 1
            continue
        weekly[week_lookup[w]] += (r["raw_price_pnl_per_oz"] - 0.30) / r["initial_risk_per_oz"]
    rng = np.random.default_rng(298)
    reps = 10000
    boot_means = np.empty(reps, dtype=float)
    starts_max = len(weekly) - 1
    blocks_needed = math.ceil(len(weekly) / 4)
    for b in range(reps):
        chunks = []
        while sum(len(x) for x in chunks) < len(weekly):
            s = int(rng.integers(0, starts_max + 1))
            chunks.append(np.array([weekly[(s + j) % len(weekly)] for j in range(4)], dtype=float))
        sample = np.concatenate(chunks)[:len(weekly)]
        boot_means[b] = sample.mean()
    bootstrap = {"weeks": int(len(weekly)), "trade_weeks": int(np.count_nonzero(weekly)),
                 "mean_weekly_net_R": float(weekly.mean()), "ci95_lower": float(np.quantile(boot_means, 0.025)),
                 "ci95_upper": float(np.quantile(boot_means, 0.975)), "resamples": reps,
                 "circular_block_length_weeks": 4, "seed": 298, "unmatched_validation_trades_before_first_monday": unmatched_val_week}
    summary["validation_weekly_bootstrap_cost_0.30"] = bootstrap

    def get(period, cost):
        return summary["periods"][period][f"cost_{cost:.2f}"]
    disc30, disc50 = get("discovery_2016_2020", .30), get("discovery_2016_2020", .50)
    val30, val50 = get("validation_2021_2025", .30), get("validation_2021_2025", .50)
    disc_years = [x for x in annual if x["period"] == "discovery_2016_2020" and x["extra_cost_usd_per_oz"] == .30]
    val_years = [x for x in annual if x["period"] == "validation_2021_2025" and x["extra_cost_usd_per_oz"] == .30]
    gates = {
        "discovery_min_75_trades": disc30["trades"] >= 75,
        "discovery_positive_net_R_at_0.30": disc30["net_R"] > 0,
        "discovery_PF_R_at_least_1.05": isinstance(disc30["PF_R"], (int, float)) and disc30["PF_R"] >= 1.05,
        "discovery_at_least_3_of_5_positive_years": sum(x["net_R"] > 0 for x in disc_years) >= 3,
        "discovery_positive_net_R_at_0.50": disc50["net_R"] > 0,
        "discovery_PF_R_at_least_0.90_at_0.50": isinstance(disc50["PF_R"], (int, float)) and disc50["PF_R"] >= .90,
        "validation_min_100_trades": val30["trades"] >= 100,
        "validation_positive_net_R_at_0.30": val30["net_R"] > 0,
        "validation_PF_R_at_least_1.05": isinstance(val30["PF_R"], (int, float)) and val30["PF_R"] >= 1.05,
        "validation_at_least_3_of_5_positive_years": sum(x["net_R"] > 0 for x in val_years) >= 3,
        "validation_bootstrap_CI_lower_strictly_positive": bootstrap["ci95_lower"] > 0,
        "validation_positive_net_R_at_0.50": val50["net_R"] > 0,
        "validation_PF_R_at_least_0.90_at_0.50": isinstance(val50["PF_R"], (int, float)) and val50["PF_R"] >= .90,
    }
    summary["gates"] = gates
    summary["verdict"] = "ELIGIBLE_FOR_SEPARATE_HOLDOUT_ONLY" if all(gates.values()) else "GAGAL"
    summary["promotion_decision"] = "No 2026 PnL calculated; no funded replay. Do not tune or reverse this candidate on the same dates." if summary["verdict"] == "GAGAL" else "Historical gates pass only; 2026 untouched holdout and broker-specific funded replay still required."

    (out_dir / "R298_results_compact.json").write_text(json.dumps(summary, indent=2, allow_nan=False), encoding="utf-8")
    if len(trade_df):
        trade_df.to_csv(out_dir / "R298_trade_ledger.csv", index=False)
    else:
        pd.DataFrame(columns=["signal_date_utc", "direction", "entry_timestamp_utc", "exit_timestamp_utc"]).to_csv(out_dir / "R298_trade_ledger.csv", index=False)
    quality_df.to_csv(out_dir / "R298_event_quality_audit.csv", index=False)
    pd.DataFrame(asia_audit).to_csv(out_dir / "R298_asian_window_quality_audit.csv", index=False)
    pd.DataFrame(london_signal_audit).to_csv(out_dir / "R298_london_signal_audit.csv", index=False)
    pd.DataFrame(annual).to_csv(out_dir / "R298_annual_summary.csv", index=False)
    pd.DataFrame([{"week_start_monday": w.strftime("%Y-%m-%d"), "net_R_cost_0.30": float(weekly[i])} for i, w in enumerate(weeks)]).to_csv(out_dir / "R298_validation_weekly_net_R.csv", index=False)

    report = []
    report += ["# R298 — XAUUSD London Asian-Range Sweep-and-Reclaim Reversal", "", f"**Verdict: {summary['verdict']}**", "",
               "The run uses only the registered 2016–2025 history. All 2026+ rows were excluded before candidate signal construction. The setup, entry, stop, target, reward/risk gate, friction schedule and pass/fail criteria were committed before PnL was calculated.", "",
               "## Data-quality audit", "",
               f"- Matched BID/ASK rows in source: {all_rows:,} per side; used through 2025-12-31: {n:,}; excluded 2026+: {excluded_2026_rows:,}.",
               f"- Registered source hashes verified: BID `{hashes['bid_sha256']}`, ASK `{hashes['ask_sha256']}`.",
               f"- BID / ASK / paired-active bars before cutoff: {int(b_active.sum()):,} / {int(a_active.sum()):,} / {int(paired_active.sum()):,}.",
               f"- Complete eligible Asian-range dates: {len(asia_by_date):,} of {len(asia_audit):,} dates with any rows in the UTC 00:00–05:55 window.",
               f"- London weekday dates audited: {len(london_date_candidates):,}; those with a complete eligible Asian range: {sum(1 for d in london_date_candidates if d in asia_by_date):,}; first-reclaim signals: {len(first_events):,}; ambiguous first bars: {len(ambiguous_dates):,}; completed trades: {len(completed):,}.",
               f"- Trade skips: `{json.dumps(skip_counts, sort_keys=True)}`.", "",
               "## Core results", "",
               "All R results below subtract observed-side BID/ASK execution and the stated additional per-ounce cost stress. `PF_R` is profit factor calculated on net trade R at that cost.", "",
               "| Period | Extra cost | Trades | Net R | PF_R | Win % | Max closed DD (R) | Long / short | Stop / target / time |", "|---|---:|---:|---:|---:|---:|---:|---:|---:|"]
    for period_label, period_key in [("Discovery 2016–2020", "discovery_2016_2020"), ("Validation 2021–2025", "validation_2021_2025")]:
        for cost in COSTS:
            m = get(period_key, cost)
            pf = m["PF_R"] if m["PF_R"] is not None else "—"
            if isinstance(pf, float): pf = f"{pf:.3f}"
            report.append(f"| {period_label} | ${cost:.2f}/oz | {m['trades']} | {m['net_R']:+.3f} | {pf} | {m['win_rate_pct'] if m['win_rate_pct'] is not None else 0:.1f}% | {m['max_closed_DD_R']:.3f} | {m['longs']} / {m['shorts']} | {m['stop_exits']} / {m['target_exits']} / {m['time_exits']} |")
    report += ["", "## Annual cohorts at +$0.30/oz", "", "| Year | Period | Trades | Net R | PF_R |", "|---:|---|---:|---:|---:|"]
    for x in annual:
        if x["extra_cost_usd_per_oz"] != .30: continue
        pf = x["PF_R"] if x["PF_R"] is not None else "—"
        if isinstance(pf, float): pf = f"{pf:.3f}"
        report.append(f"| {x['year']} | {x['period'].replace('_',' ')} | {x['trades']} | {x['net_R']:+.3f} | {pf} |")
    report += ["", "## Validation weekly bootstrap at +$0.30/oz", "",
               f"- Weeks: {bootstrap['weeks']} (all Monday-start weeks from 2021-01-04 to 2025-12-29, including zero-trade weeks); trade weeks: {bootstrap['trade_weeks']}; mean weekly net R: {bootstrap['mean_weekly_net_R']:+.5f}.",
               f"- 95% circular four-week block-bootstrap CI: [{bootstrap['ci95_lower']:+.5f}, {bootstrap['ci95_upper']:+.5f}] R/week; {bootstrap['resamples']:,} resamples; seed {bootstrap['seed']}.", "",
               "## Locked gates", "", "| Gate | Outcome |", "|---|---|"]
    for name, passed in gates.items():
        report.append(f"| {name.replace('_',' ')} | {'PASS' if passed else 'FAIL'} |")
    report += ["", "## Disposition", "", summary["promotion_decision"], "",
               "A failed screen is not an invitation to tune the same sample. Even if every historic gate had passed, this would remain only eligible for a separate holdout; it would not be a funded-ready strategy.", "",
               "## Limitations", "",
               "- 2021–2025 is research-contaminated and cannot serve as a pristine program-level out-of-sample period.",
               "- Historical BID/ASK quote replay does not verify actual FundedNext broker fills, point/contract value, commission, slippage, swaps, margin or live account equity/DLL/MLL behavior.",
               "- No 2026 PnL or FundedNext two-phase account-equity replay was run.", ""]
    (out_dir / "R298_FINAL_REPORT.md").write_text("\n".join(report), encoding="utf-8")
    print(json.dumps({"verdict": summary["verdict"], "data_quality": summary["data_quality"],
                      "periods": summary["periods"], "bootstrap": bootstrap, "gates": gates,
                      "annual_at_030": [x for x in annual if x["extra_cost_usd_per_oz"] == .30]}, indent=2))

if __name__ == "__main__":
    main()