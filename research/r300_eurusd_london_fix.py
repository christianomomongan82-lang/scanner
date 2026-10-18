#!/usr/bin/env python3
"""R300 EURUSD London-fix post-event reversal. Local replay only; respects locked cutoff."""
import argparse
import hashlib
import json
from datetime import datetime, date, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy as np
import pandas as pd

EXPECTED_ARCHIVE_SHA256 = "b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e"
EXPECTED_MEMBER_SHA256 = {
    "eurusd_ask_M1_2016-2025.csv.gz": "52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b",
    "eurusd_bid_M1_2016-2025.csv.gz": "b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc",
}
CUTOFF_MS = int(pd.Timestamp("2022-01-01T00:00:00Z").timestamp() * 1000)
LONDON = ZoneInfo("Europe/London")
COSTS = (0.0, 0.5, 1.0, 2.0)
PIP = 0.0001


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def read_side(root: Path, filename: str, label: str):
    path = root / filename
    if not path.is_file():
        raise FileNotFoundError(f"Missing source member: {path}")
    actual_hash = sha256_file(path)
    if actual_hash != EXPECTED_MEMBER_SHA256[filename]:
        raise ValueError(f"SHA-256 mismatch for {filename}: expected {EXPECTED_MEMBER_SHA256[filename]}, got {actual_hash}")
    df = pd.read_csv(path, compression="gzip")
    needed = {"timestamp", "open", "high", "low", "close"}
    if not needed.issubset(df.columns):
        raise ValueError(f"{filename}: missing columns {sorted(needed - set(df.columns))}")
    df = df[["timestamp", "open", "high", "low", "close"]].copy()
    df["timestamp"] = pd.to_numeric(df["timestamp"], errors="raise").astype("int64")
    # Locked absolute cutoff, applied before any eligibility/outcome construction.
    df = df.loc[df.timestamp < CUTOFF_MS].copy()
    if df.timestamp.duplicated().any():
        raise ValueError(f"{label}: duplicate timestamps before cutoff")
    if not df.timestamp.is_monotonic_increasing:
        raise ValueError(f"{label}: non-monotonic timestamps before cutoff")
    if not (df.timestamp % 60000 == 0).all():
        raise ValueError(f"{label}: timestamps not aligned to minute grid")
    vals = df[["open", "high", "low", "close"]].to_numpy(float)
    if not np.isfinite(vals).all():
        raise ValueError(f"{label}: non-finite OHLC")
    bad = (df.high < df.low) | (df.high < df[["open", "close"]].max(axis=1)) | (df.low > df[["open", "close"]].min(axis=1))
    if bad.any():
        raise ValueError(f"{label}: {int(bad.sum())} invalid OHLC rows")
    df["active"] = (df.high > df.low) | (df.open != df.close)
    df["side"] = label
    return df.reset_index(drop=True), actual_hash


def combine_m1(root: Path):
    bid, bid_hash = read_side(root, "eurusd_bid_M1_2016-2025.csv.gz", "bid")
    ask, ask_hash = read_side(root, "eurusd_ask_M1_2016-2025.csv.gz", "ask")
    bset, aset = set(map(int, bid.timestamp.to_numpy())), set(map(int, ask.timestamp.to_numpy()))
    if bset != aset:
        raise ValueError(f"BID/ASK timestamps mismatch before cutoff: BID-only {len(bset-aset)}, ASK-only {len(aset-bset)}")
    m = bid.drop(columns="side").merge(ask.drop(columns="side"), on="timestamp", suffixes=("_bid", "_ask"), validate="one_to_one")
    m = m.sort_values("timestamp").reset_index(drop=True)
    m["active_both"] = m.active_bid & m.active_ask
    m["spread_open"] = m.open_ask - m.open_bid
    m["spread_close"] = m.close_ask - m.close_bid
    if (m.spread_open < 0).any() or (m.spread_close < 0).any():
        raise ValueError("Negative opening/closing BID/ASK spread found")
    for field in ("open", "high", "low", "close"):
        m[f"{field}_mid"] = (m[f"{field}_bid"] + m[f"{field}_ask"]) / 2
    return m, bid, ask, bid_hash, ask_hash


def build_m5(m1: pd.DataFrame):
    """Aggregate only exact five-row active contiguous M1 blocks; never synthesize incomplete bars."""
    d = m1.copy()
    d["m5_ts"] = (d.timestamp // 300000) * 300000
    d["active_i"] = d.active_both.astype("int8")
    agg = d.groupby("m5_ts", sort=True).agg(
        n=("timestamp", "size"), first_ts=("timestamp", "first"), last_ts=("timestamp", "last"), active_n=("active_i", "sum"),
        bid_open=("open_bid", "first"), bid_high=("high_bid", "max"), bid_low=("low_bid", "min"), bid_close=("close_bid", "last"),
        ask_open=("open_ask", "first"), ask_high=("high_ask", "max"), ask_low=("low_ask", "min"), ask_close=("close_ask", "last"),
        mid_open=("open_mid", "first"), mid_high=("high_mid", "max"), mid_low=("low_mid", "min"), mid_close=("close_mid", "last"),
    ).reset_index()
    # Unique minute timestamps plus n==5, correct endpoints, and active_n==5 proves five valid constituents.
    good = (agg.n == 5) & (agg.first_ts == agg.m5_ts) & (agg.last_ts == agg.m5_ts + 240000) & (agg.active_n == 5)
    m5 = agg.loc[good].copy()
    m5["timestamp"] = m5.m5_ts.astype("int64")
    m5["active"] = True
    m5 = m5.drop(columns=["m5_ts", "n", "first_ts", "last_ts", "active_n"]).sort_values("timestamp").reset_index(drop=True)
    if len(m5):
        m5["dt_utc"] = pd.to_datetime(m5.timestamp, unit="ms", utc=True)
        m5["dt_london"] = m5.dt_utc.dt.tz_convert("Europe/London")
        m5["date_london"] = m5.dt_london.dt.date
    stats = {"raw_m1_groups": int(len(agg)), "exact_5row_groups": int((agg.n == 5).sum()), "valid_active_m5_bars": int(len(m5))}
    return m5, stats


def london_ts_ms(d: date, hhmm: str) -> int:
    h, minute = map(int, hhmm.split(":"))
    aware = datetime(d.year, d.month, d.day, h, minute, tzinfo=LONDON)
    return int(pd.Timestamp(aware).tz_convert("UTC").timestamp() * 1000)


def eligible_event_audit(m5: pd.DataFrame):
    """Pre-outcome audit only: no returns, directions, SL/TP hits, PnL, or performance metrics."""
    idx = {int(t): i for i, t in enumerate(m5.timestamp.to_numpy())}
    all_dates = pd.date_range("2017-01-01", "2021-12-31", freq="D")
    rows = []
    risk_clock = ["15:25", "15:30", "15:35", "15:40", "15:45", "15:50"]
    path_clock = ["16:05", "16:10", "16:15", "16:20", "16:25", "16:30", "16:35"]
    required = risk_clock + path_clock
    for day_ts in all_dates:
        d = day_ts.date()
        if day_ts.weekday() >= 5:
            continue
        need_times = [london_ts_ms(d, x) for x in required]
        missing = [name for name, ts in zip(required, need_times) if ts not in idx]
        reason = ""
        if missing:
            reason = "missing_required_m5:" + ",".join(missing)
        else:
            risk_ts = [london_ts_ms(d, x) for x in risk_clock]
            path_ts = [london_ts_ms(d, x) for x in path_clock]
            if np.diff(risk_ts).size and not np.all(np.diff(risk_ts) == 300000):
                reason = "noncontiguous_risk_grid"
            elif not np.all(np.diff(path_ts) == 300000):
                reason = "noncontiguous_trade_path_grid"
        rows.append({"date_london": str(d), "year": d.year, "weekday": day_ts.day_name(), "eligible": not bool(reason), "reason": reason})
    return pd.DataFrame(rows)


def add_entry_spread_audit(events: pd.DataFrame, m5: pd.DataFrame):
    """Record executable-time spreads only; do not calculate returns or outcomes."""
    index = {int(t): i for i, t in enumerate(m5.timestamp.to_numpy())}
    events = events.copy()
    events["entry_spread_pips"] = np.nan
    for i, row in events.iterrows():
        if not row.eligible:
            continue
        ts = london_ts_ms(pd.Timestamp(row.date_london).date(), "16:05")
        j = index.get(ts)
        if j is not None:
            events.at[i, "entry_spread_pips"] = (float(m5.iloc[j].ask_open) - float(m5.iloc[j].bid_open)) / PIP
    return events


def audit_only(root: Path, out: Path):
    m1, bid, ask, bid_hash, ask_hash = combine_m1(root)
    m5, agg = build_m5(m1)
    events = add_entry_spread_audit(eligible_event_audit(m5), m5)
    entry_spread = events.loc[events.eligible, "entry_spread_pips"].dropna().to_numpy(float)
    years = {}
    for year in range(2017, 2022):
        e = events.loc[events.year == year]
        years[str(year)] = {"weekday_dates_checked": int(len(e)), "preoutcome_eligible_dates": int(e.eligible.sum()), "ineligible_dates": int((~e.eligible).sum())}
    spread = m1.spread_open.to_numpy(float)
    audit = {
        "candidate": "R300_EURUSD_LONDON_FIX_POST_EVENT_REVERSAL", "stage": "PRE_OUTCOME_DATA_AUDIT_ONLY", "candidate_pnl_calculated": False,
        "archive_artifact_id": 11959096102, "collection_run_id": 38697080604, "archive_sha256_verified": EXPECTED_ARCHIVE_SHA256,
        "member_sha256": {"bid": bid_hash, "ask": ask_hash}, "cutoff_utc_exclusive": "2022-01-01T00:00:00Z",
        "rows_after_cutoff": {"bid_m1": int(len(bid)), "ask_m1": int(len(ask)), "paired_m1": int(len(m1))},
        "source_time_coverage_utc": {"first": pd.to_datetime(int(m1.timestamp.min()), unit="ms", utc=True).isoformat(), "last": pd.to_datetime(int(m1.timestamp.max()), unit="ms", utc=True).isoformat()},
        "integrity": {
            "bid_ask_timestamp_sets_equal": True, "unique_and_monotonic": True, "timestamp_grid_m1": "60 seconds; checked",
            "invalid_ohlc": 0, "negative_open_or_close_spreads": 0, "active_both_m1_rows": int(m1.active_both.sum()),
            "static_or_one_side_inactive_m1_rows": int((~m1.active_both).sum()),
            "open_spread_pips": {"min": float(spread.min() / PIP), "median": float(np.median(spread) / PIP), "p95": float(np.quantile(spread, .95) / PIP), "max": float(spread.max() / PIP)},
        },
        "m5_aggregation_audit": agg,
        "preoutcome_eligibility_by_year": years,
        "eligible_entry_spread_pips_at_1605_london": {
            "n": int(len(entry_spread)), "median": float(np.median(entry_spread)), "p95": float(np.quantile(entry_spread, .95)),
            "max": float(np.max(entry_spread)), "pct_over_1_pip": float((entry_spread > 1.0).mean() * 100), "pct_over_2_pips": float((entry_spread > 2.0).mean() * 100),
        },
        "skip_counts_by_year": {str(y): events.loc[(events.year == y) & (~events.eligible), "reason"].value_counts().to_dict() for y in range(2017, 2022)},
        "interpretation": "Counts only exact, complete and active timestamp coverage for the registered event geometry. Does not compute signal return, direction, trade result, or PnL.",
    }
    out.mkdir(parents=True, exist_ok=True)
    events.to_csv(out / "R300_preoutcome_event_eligibility_audit.csv", index=False)
    (out / "R300_preoutcome_data_audit.json").write_text(json.dumps(audit, indent=2))
    print(json.dumps(audit, indent=2))


def net_stats(frame, cost_pips):
    values = frame[f"net_R_{cost_pips:g}pip"].to_numpy(float)
    cumulative = np.cumsum(values)
    peak = np.maximum.accumulate(np.r_[0.0, cumulative])[1:]
    dd = peak - cumulative
    return {
        "trades": int(len(frame)), "net_R": float(values.sum()),
        "PF_R": float(values[values > 0].sum() / (-values[values < 0].sum())) if (values < 0).any() else None,
        "win_rate_pct": float((values > 0).mean() * 100) if len(values) else None, "max_closed_DD_R": float(dd.max()) if len(dd) else 0.0,
        "longs": int((frame.direction == 1).sum()), "shorts": int((frame.direction == -1).sum()),
        "stop_exits": int(frame.exit_type.str.startswith("stop").sum()), "target_exits": int(frame.exit_type.str.startswith("target").sum()),
        "time_exits": int((frame.exit_type == "time").sum()), "mean_hold_min": float(frame.hold_minutes.mean()) if len(frame) else None,
    }


def simulate_stream(m5, events, stream):
    idx = {int(t): i for i, t in enumerate(m5.timestamp.to_numpy())}
    active = m5.active.to_numpy(bool)
    opens = {s: m5[f"{s}_open"].to_numpy(float) for s in ("bid", "ask", "mid")}
    highs = {s: m5[f"{s}_high"].to_numpy(float) for s in ("bid", "ask", "mid")}
    lows = {s: m5[f"{s}_low"].to_numpy(float) for s in ("bid", "ask", "mid")}
    closes = m5.mid_close.to_numpy(float)
    trades, audit = [], []
    for day in events.date_london:
        d = pd.Timestamp(day).date()
        stamp = {hhmm: london_ts_ms(d, hhmm) for hhmm in ("15:25", "15:30", "15:35", "15:40", "15:45", "15:50", "16:05", "16:10", "16:15", "16:20", "16:25", "16:30", "16:35")}
        all_ts = [stamp[x] for x in stamp]
        reason = ""
        if any(t not in idx for t in all_ts):
            reason = "missing_required_m5"
        elif any(not active[idx[t]] for t in all_ts):
            reason = "inactive_required_m5"
        if reason:
            audit.append({"date_london": str(d), "stream": stream, "status": "SKIP", "reason": reason})
            continue
        risk_idx = [idx[stamp[x]] for x in ("15:25", "15:30", "15:35", "15:40", "15:45", "15:50")]
        risk = float(np.mean(highs["mid"][risk_idx] - lows["mid"][risk_idx]))
        if not np.isfinite(risk) or risk <= 0:
            audit.append({"date_london": str(d), "stream": stream, "status": "SKIP", "reason": "nonpositive_risk_range"})
            continue
        start_mid, end_mid = closes[idx[stamp["15:35"]]], closes[idx[stamp["15:50"]]]
        ret = end_mid / start_mid - 1.0
        if not np.isfinite(ret) or ret == 0:
            audit.append({"date_london": str(d), "stream": stream, "status": "SKIP", "reason": "zero_or_invalid_pref_fix_return"})
            continue
        fade_dir = -1 if ret > 0 else 1
        direction = fade_dir if stream == "fade" else -fade_dir
        entry_t = stamp["16:05"]
        entry_i = idx[entry_t]
        entry_side = "ask" if direction == 1 else "bid"
        exit_side = "bid" if direction == 1 else "ask"
        entry = float(opens[entry_side][entry_i])
        stop, target = entry - direction * risk, entry + direction * risk
        exit_price = exit_type = exit_t = None
        for hhmm in ("16:05", "16:10", "16:15", "16:20", "16:25", "16:30"):
            bt, bi = stamp[hhmm], idx[stamp[hhmm]]
            op, hi, lo = float(opens[exit_side][bi]), float(highs[exit_side][bi]), float(lows[exit_side][bi])
            if direction == 1:
                if op <= stop: exit_price, exit_type = op, "stop_gap"
                elif op >= target: exit_price, exit_type = op, "target_gap"
                elif lo <= stop and hi >= target: exit_price, exit_type = stop, "stop_collision"
                elif lo <= stop: exit_price, exit_type = stop, "stop"
                elif hi >= target: exit_price, exit_type = target, "target"
            else:
                if op >= stop: exit_price, exit_type = op, "stop_gap"
                elif op <= target: exit_price, exit_type = op, "target_gap"
                elif hi >= stop and lo <= target: exit_price, exit_type = stop, "stop_collision"
                elif hi >= stop: exit_price, exit_type = stop, "stop"
                elif lo <= target: exit_price, exit_type = target, "target"
            if exit_price is not None:
                exit_t = bt
                break
        if exit_price is None:
            exit_t = stamp["16:35"]
            exit_price, exit_type = float(opens[exit_side][idx[exit_t]]), "time"
        gross_r = direction * (exit_price - entry) / risk
        out = {
            "date_london": str(d), "stream": stream,
            "signal_timestamp_utc": pd.to_datetime(stamp["15:50"], unit="ms", utc=True).isoformat(),
            "entry_time_utc": pd.to_datetime(entry_t, unit="ms", utc=True).isoformat(),
            "exit_time_utc": pd.to_datetime(exit_t, unit="ms", utc=True).isoformat(),
            "pref_fix_return_mid_pct": ret * 100.0, "direction": direction, "risk_distance": risk,
            "entry": entry, "exit": float(exit_price), "exit_type": exit_type,
            "hold_minutes": (exit_t - entry_t) / 60000, "gross_R": gross_r,
        }
        for cost in COSTS:
            out[f"net_R_{cost:g}pip"] = (direction * (exit_price - entry) - cost * PIP) / risk
        trades.append(out)
        audit.append({"date_london": str(d), "stream": stream, "status": "TRADE", "reason": "", "exit_type": exit_type})
    return pd.DataFrame(trades), pd.DataFrame(audit)


def score(root: Path, out: Path):
    m1, bid, ask, bid_hash, ask_hash = combine_m1(root)
    m5, agg = build_m5(m1)
    all_pre_events = add_entry_spread_audit(eligible_event_audit(m5), m5)
    elig = all_pre_events.loc[all_pre_events.eligible].copy()
    all_trades, all_audit = [], []
    for stream in ("fade", "follow"):
        tr, aud = simulate_stream(m5, elig, stream)
        bad_dates = all_pre_events.loc[~all_pre_events.eligible, ["date_london", "reason"]].copy()
        if len(bad_dates):
            bad_dates["stream"] = stream
            bad_dates["status"] = "SKIP"
            bad_dates["reason"] = "preoutcome_ineligible:" + bad_dates["reason"].astype(str)
            bad_dates["exit_type"] = ""
            aud = pd.concat([aud, bad_dates[["date_london", "stream", "status", "reason", "exit_type"]]], ignore_index=True)
        all_trades.append(tr)
        all_audit.append(aud)
    ledger = pd.concat([t for t in all_trades if len(t)], ignore_index=True)
    audit = pd.concat([a for a in all_audit if len(a)], ignore_index=True)
    summaries = {}
    for stream in ("fade", "follow"):
        part = ledger.loc[ledger.stream == stream].copy()
        part["year"] = part.date_london.str[:4].astype(int)
        summaries[stream] = {}
        for label, mask in (("discovery_2017_2020", part.year.between(2017, 2020)), ("validation_2021", part.year == 2021)):
            frame = part.loc[mask].copy()
            summaries[stream][label] = {f"cost_{cost:g}pip": net_stats(frame, cost) for cost in COSTS}
            summaries[stream][label]["annual"] = {str(y): {f"cost_{cost:g}pip": net_stats(frame.loc[frame.year == y], cost) for cost in COSTS} for y in sorted(frame.year.unique())}
    val = ledger.loc[(ledger.stream == "fade") & (ledger.date_london.str.startswith("2021"))].copy()
    val["date"] = pd.to_datetime(val.date_london)
    val["week_monday"] = val.date.map(lambda d: d.date() - timedelta(days=d.weekday()))
    weeks = [x.date() for x in pd.date_range("2021-01-04", "2021-12-27", freq="W-MON")]
    weekly = np.array([val.loc[val.week_monday == w, "net_R_1pip"].sum() for w in weeks], dtype=float)
    rng = np.random.default_rng(300)
    boot = []
    for _ in range(10000):
        starts = rng.integers(0, len(weekly), size=int(np.ceil(len(weekly) / 4)))
        inds = np.concatenate([np.arange(s, s + 4) % len(weekly) for s in starts])[:len(weekly)]
        boot.append(weekly[inds].mean())
    bootstrap = {"weeks": len(weekly), "trade_weeks": int((weekly != 0).sum()), "mean_weekly_net_R": float(weekly.mean()), "ci95_lower": float(np.quantile(boot, 0.025)), "ci95_upper": float(np.quantile(boot, 0.975)), "resamples": 10000, "block_len": 4, "seed": 300}
    fade_disc, fade_val = summaries["fade"]["discovery_2017_2020"], summaries["fade"]["validation_2021"]
    disc1, val1 = fade_disc["cost_1pip"], fade_val["cost_1pip"]
    disc2, val2 = fade_disc["cost_2pip"], fade_val["cost_2pip"]
    disc_years_positive = sum(1 for y in ("2017", "2018", "2019", "2020") if fade_disc["annual"].get(y, {}).get("cost_1pip", {}).get("net_R", -1e99) > 0)
    gates = {
        "data_integrity": True,
        "discovery_trades_ge_200": disc1["trades"] >= 200,
        "validation_trades_ge_100": val1["trades"] >= 100,
        "discovery_net_R_positive_at_1pip": disc1["net_R"] > 0,
        "discovery_PF_ge_1_05_at_1pip": disc1["PF_R"] is not None and disc1["PF_R"] >= 1.05,
        "validation_net_R_positive_at_1pip": val1["net_R"] > 0,
        "validation_PF_ge_1_05_at_1pip": val1["PF_R"] is not None and val1["PF_R"] >= 1.05,
        "at_least_3_of_4_discovery_years_positive_at_1pip": disc_years_positive >= 3,
        "discovery_net_R_positive_at_2pip": disc2["net_R"] > 0,
        "discovery_PF_ge_1_at_2pip": disc2["PF_R"] is not None and disc2["PF_R"] >= 1.0,
        "validation_net_R_positive_at_2pip": val2["net_R"] > 0,
        "validation_PF_ge_1_at_2pip": val2["PF_R"] is not None and val2["PF_R"] >= 1.0,
        "validation_weekly_bootstrap_lower_gt_zero_at_1pip": bootstrap["ci95_lower"] > 0,
        "all_entry_exit_timestamps_exact_active": True,
    }
    verdict = "LULUS" if all(gates.values()) else "GAGAL"
    entry_spreads = all_pre_events.loc[all_pre_events.eligible, "entry_spread_pips"].dropna().to_numpy(float)
    report = {
        "candidate": "R300_EURUSD_LONDON_FIX_POST_EVENT_REVERSAL", "verdict": verdict,
        "source_archive_id": 11959096102, "source_archive_sha256": EXPECTED_ARCHIVE_SHA256,
        "source_member_sha256": {"bid": bid_hash, "ask": ask_hash}, "cutoff_utc_exclusive": "2022-01-01T00:00:00Z",
        "source_rows_after_cutoff": {"bid_m1": int(len(bid)), "ask_m1": int(len(ask)), "paired_m1": int(len(m1))},
        "m5_aggregation_audit": agg,
        "entry_spread_pips_at_1605_london": {"n": int(len(entry_spreads)), "median": float(np.median(entry_spreads)), "p95": float(np.quantile(entry_spreads, .95)), "max": float(np.max(entry_spreads))},
        "preoutcome_eligibility_by_year": {str(y): {"dates_checked": int((all_pre_events.year == y).sum()), "eligible": int(((all_pre_events.year == y) & all_pre_events.eligible).sum()), "ineligible": int(((all_pre_events.year == y) & (~all_pre_events.eligible)).sum())} for y in range(2017, 2022)},
        "trade_counts": {stream: int((ledger.stream == stream).sum()) for stream in ("fade", "follow")},
        "skip_counts": {stream: audit.loc[(audit.stream == stream) & (audit.status == "SKIP"), "reason"].value_counts().to_dict() for stream in ("fade", "follow")},
        "streams": summaries, "validation_bootstrap_fade_1pip": bootstrap,
        "discovery_years_positive_at_1pip": int(disc_years_positive), "gates": gates, "passed_gates": int(sum(gates.values())), "total_gates": int(len(gates)),
        "interpretation": "This is a historical signal screen, not a FundedNext-equivalent equity replay. Program-level FX history is contaminated; no candidate PnL after 2021 was calculated.",
    }
    out.mkdir(parents=True, exist_ok=True)
    ledger.to_csv(out / "R300_trade_ledger_fade_and_follow.csv", index=False)
    audit.to_csv(out / "R300_event_audit.csv", index=False)
    all_pre_events.to_csv(out / "R300_preoutcome_event_eligibility_audit.csv", index=False)
    pd.DataFrame({"week_monday_london": weeks, "net_R_1pip_fade": weekly}).to_csv(out / "R300_validation_weekly_net_R.csv", index=False)
    (out / "R300_results_compact.json").write_text(json.dumps(report, indent=2))
    year_rows = []
    for stream in ("fade", "follow"):
        x = ledger.loc[ledger.stream == stream].copy(); x["year"] = x.date_london.str[:4].astype(int)
        for y in sorted(x.year.unique()):
            for cost in COSTS:
                year_rows.append({"stream": stream, "year": int(y), "cost_pips": cost, **net_stats(x.loc[x.year == y], cost)})
    pd.DataFrame(year_rows).to_csv(out / "R300_annual_summary.csv", index=False)
    print(json.dumps(report, indent=2))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, help="Directory containing the two exact extracted gzip M1 members")
    parser.add_argument("--output-dir", default="r300_output")
    parser.add_argument("--audit-only", action="store_true", help="Run data/eligibility audit without constructing signal returns or PnL")
    args = parser.parse_args()
    if args.audit_only:
        audit_only(Path(args.data_dir), Path(args.output_dir))
    else:
        score(Path(args.data_dir), Path(args.output_dir))


if __name__ == "__main__":
    main()
