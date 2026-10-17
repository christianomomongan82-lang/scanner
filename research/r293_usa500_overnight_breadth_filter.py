#!/usr/bin/env python3
"""R293 locked local replay: USA500 overnight carry filtered by prior-session US-index breadth."""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

TZ = "America/New_York"
COSTS = (1, 2, 4)
BOOTSTRAPS = 5000
SEED = 293
BLOCK_WEEKS = 4
WINDOW_START = "2017-01-01"
WINDOW_END = "2021-12-31"
HASHES = {
    "usa500idxusd": "df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee",
    "usatechidxusd": "82b06c38f66cd1387097691baac1d45c9463b6540eea9dfe28a894d85e122f7c",
    "usa30idxusd": "8fcef9d76b31e99ae8d0175e769307ab13f930ae3ec2c17ef6baf0311ea1783a",
    "ussc2000idxusd": "c01c97d8705453d3fa3fd4ac1d386e9c1d72ab27e3b7d57d6cde53da9dfdf6f0",
}

def profit_factor(x):
    a = np.asarray(x, dtype=float)
    gains = float(a[a > 0].sum())
    losses = float(-a[a < 0].sum())
    return gains / losses if losses > 0 else (float("inf") if gains > 0 else None)

def load_sessions(path: Path, symbol: str):
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != HASHES[symbol]:
        raise ValueError(f"{symbol} source SHA mismatch: {actual}")
    d = pd.read_csv(path, compression="gzip")
    if d.columns.tolist() != ["timestamp", "open", "high", "low", "close"]:
        raise ValueError(f"{symbol}: unexpected schema {d.columns.tolist()}")
    if d["timestamp"].duplicated().any():
        raise ValueError(f"{symbol}: duplicate raw timestamps")
    d = d.sort_values("timestamp", kind="stable").reset_index(drop=True)
    d["flat_placeholder"] = (
        (d["open"] == d["high"]) & (d["high"] == d["low"])
        & (d["low"] == d["close"]) & (d["close"] == d["close"].shift(1))
    )
    # Outcomes are locked to 2016–2021; the complete raw series is used only for checksums
    # and to determine whether a row repeats the previous raw close.
    end_utc_ms = int(pd.Timestamp("2022-01-02", tz="UTC").timestamp() * 1000)
    d = d[d["timestamp"] < end_utc_ms].copy()
    d["dt"] = pd.to_datetime(d["timestamp"], unit="ms", utc=True).dt.tz_convert(TZ)
    d["date"] = d["dt"].dt.strftime("%Y-%m-%d")
    d["minute"] = d["dt"].dt.hour * 60 + d["dt"].dt.minute
    cols = ["open", "high", "low", "close"]
    d["valid_ohlc"] = (
        d[cols].notna().all(axis=1) & (d[cols] > 0).all(axis=1)
        & (d["high"] >= d[["open", "close", "low"]].max(axis=1))
        & (d["low"] <= d[["open", "close", "high"]].min(axis=1))
    )
    rth = d[(d["dt"].dt.dayofweek < 5) & d["minute"].between(570, 955)].copy()
    sessions, audit = {}, []
    expected_minutes = np.arange(570, 956, 5, dtype=int)
    for day, g0 in rth.groupby("date", sort=True):
        g = g0.sort_values("timestamp").reset_index(drop=True)
        reasons = []
        if len(g) != 78:
            reasons.append("bar_count")
        elif not np.array_equal(g["minute"].to_numpy(dtype=int), expected_minutes):
            reasons.append("timestamp_sequence")
        if not g["valid_ohlc"].all():
            reasons.append("invalid_ohlc")
        if g["flat_placeholder"].any():
            reasons.append("repeated_flat_placeholder")
        ok = not reasons
        audit.append({
            "symbol": symbol, "date": day, "year": int(day[:4]), "bars": int(len(g)),
            "flat_count": int(g["flat_placeholder"].sum()),
            "invalid_ohlc_count": int((~g["valid_ohlc"]).sum()),
            "eligible": ok, "reason": "|".join(reasons),
        })
        if ok:
            sessions[day] = g
    meta = {
        "symbol": symbol, "sha256": actual, "rows_before_2022_01_02_utc": int(len(d)),
        "last_timestamp_ny": d["dt"].max().isoformat(),
        "rth_session_dates": int(len(rth["date"].unique())),
        "valid_sessions": int(len(sessions)),
    }
    return sessions, audit, meta

def session_return(g):
    # M5 bars are bar-open stamped; 15:45 bar closes at 15:50 ET.
    return float(g.iloc[75]["close"] / g.iloc[0]["open"] - 1.0)

def build_ledgers(all_sessions):
    usa = all_sessions["usa500idxusd"]
    usa_dates = sorted(usa)
    rows, parent_rows, skipped = [], [], []
    for i, day in enumerate(usa_dates[:-1]):
        if not (WINDOW_START <= day <= WINDOW_END):
            continue
        nxt = usa_dates[i + 1]
        if (pd.Timestamp(nxt) - pd.Timestamp(day)).days > 7:
            skipped.append({"date": day, "next_usa500_session": nxt, "reason": "gap_over_7_calendar_days"})
            continue
        split = "DISCOVERY" if day <= "2020-12-31" else "VALIDATION"
        bound = "2020-12-31" if split == "DISCOVERY" else "2021-12-31"
        if nxt > bound:
            skipped.append({"date": day, "next_usa500_session": nxt, "reason": "partition_boundary"})
            continue
        eligible = {s: all_sessions[s][day] for s in all_sessions if day in all_sessions[s]}
        if "usa500idxusd" not in eligible or len(eligible) < 3:
            skipped.append({"date": day, "next_usa500_session": nxt, "reason": "fewer_than_three_valid_indices"})
            continue
        entry = float(usa[day].iloc[77]["open"])
        exitp = float(usa[nxt].iloc[0]["open"])
        if not np.isfinite(entry) or not np.isfinite(exitp) or entry <= 0 or exitp <= 0:
            skipped.append({"date": day, "next_usa500_session": nxt, "reason": "invalid_entry_exit"})
            continue
        positives = sum(session_return(g) > 0 for g in eligible.values())
        breadth_n = len(eligible)
        gross_bp = (exitp / entry - 1.0) * 10000.0
        take = positives / breadth_n >= 0.75
        common = {
            "entry_date": day, "exit_date": nxt, "year": int(day[:4]), "split": split,
            "entry_timestamp_ny": usa[day].iloc[77]["dt"].isoformat(),
            "exit_timestamp_ny": usa[nxt].iloc[0]["dt"].isoformat(),
            "entry_bid_open_1555": entry, "exit_bid_open_0930": exitp,
            "breadth_positive": int(positives), "breadth_valid_n": int(breadth_n),
            "breadth_fraction": float(positives / breadth_n), "gross_bp": float(gross_bp),
        }
        if take:
            cand = dict(common, take_trade=True)
            for c in COSTS:
                cand[f"net_bp_{c}"] = float(gross_bp - c)
            rows.append(cand)
        par = dict(common, take_trade=True)
        for c in COSTS:
            par[f"net_bp_{c}"] = float(gross_bp - c)
        parent_rows.append(par)
    return pd.DataFrame(rows), pd.DataFrame(parent_rows), pd.DataFrame(skipped)

def summarize(frame):
    out = {"trades": int(len(frame))}
    for c in COSTS:
        arr = frame[f"net_bp_{c}"].to_numpy(float) if len(frame) else np.array([], dtype=float)
        out[f"net_bp_{c}"] = float(arr.sum()) if len(arr) else 0.0
        out[f"pf_{c}bp"] = profit_factor(arr) if len(arr) else None
    if len(frame):
        a = frame["net_bp_2"].to_numpy(float)
        cum = np.r_[0.0, np.cumsum(a)] / 100.0
        dd = cum - np.maximum.accumulate(cum)
        out["gross_bp"] = float(frame["gross_bp"].sum())
        out["win_rate_2bp_pct"] = float((a > 0).mean() * 100.0)
        out["mean_net_bp_2"] = float(a.mean())
        out["max_closed_pnl_drawdown_pct_fixed_notional_2bp"] = float(-min(0.0, float(dd.min())))
    else:
        out.update({"gross_bp": 0.0, "win_rate_2bp_pct": None, "mean_net_bp_2": None,
                    "max_closed_pnl_drawdown_pct_fixed_notional_2bp": 0.0})
    return out

def bootstrap_validation(frame):
    weeks = {d.strftime("%Y-%m-%d"): 0.0
             for d in pd.date_range("2021-01-04", "2021-12-27", freq="W-MON")}
    for _, r in frame.iterrows():
        dt = pd.Timestamp(r["exit_date"])
        key = (dt - pd.Timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
        if key in weeks:
            weeks[key] += float(r["net_bp_2"])
    vals = np.array(list(weeks.values()), dtype=float)
    rng = np.random.default_rng(SEED)
    means = np.empty(BOOTSTRAPS, dtype=float)
    n = len(vals)
    for b in range(BOOTSTRAPS):
        idx = []
        while len(idx) < n:
            start = int(rng.integers(0, n))
            idx.extend(((start + np.arange(BLOCK_WEEKS)) % n).tolist())
        means[b] = vals[np.asarray(idx[:n], dtype=int)].mean()
    ci = np.quantile(means, [0.025, 0.975])
    return {
        "weeks_total_including_zero_trade_weeks": int(n),
        "weeks_with_trades": int((vals != 0).sum()),
        "mean_weekly_net_bp_2": float(vals.mean()),
        "ci95_low": float(ci[0]), "ci95_high": float(ci[1]),
        "resamples": BOOTSTRAPS, "block_length_weeks": BLOCK_WEEKS, "seed": SEED,
        "weekly_net_bp": {k: float(v) for k, v in weeks.items()},
    }

def period_summary(candidate, parent):
    output = {}
    for split, lo, hi in [
        ("discovery", "2017-01-01", "2020-12-31"),
        ("validation", "2021-01-01", "2021-12-31"),
    ]:
        c = candidate[candidate["entry_date"].between(lo, hi)].copy()
        p = parent[parent["entry_date"].between(lo, hi)].copy()
        annual = {}
        if split == "discovery":
            for y in range(2017, 2021):
                annual[str(y)] = summarize(c[c.year == y])
        output[split] = {"candidate": summarize(c), "matched_unconditional_parent": summarize(p),
                         "candidate_yearly": annual}
        if split == "validation":
            output[split]["candidate_weekly_bootstrap"] = bootstrap_validation(c)
            output[split]["parent_weekly_bootstrap"] = bootstrap_validation(p)
    return output

def main():
    import argparse
    from concurrent.futures import ThreadPoolExecutor
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", type=Path, required=True)
    ap.add_argument("--out-dir", type=Path, default=Path("R293_outputs"))
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    symbols = list(HASHES)
    def load_one(symbol):
        return symbol, load_sessions(args.data_dir / f"{symbol}_m5.csv.gz", symbol)
    with ThreadPoolExecutor(max_workers=2) as pool:
        loaded = list(pool.map(load_one, symbols))
    all_sessions, audits, metas = {}, [], []
    for symbol, (sessions, audit, meta) in loaded:
        all_sessions[symbol] = sessions
        audits.extend(audit)
        metas.append(meta)
    candidate, parent, skipped = build_ledgers(all_sessions)
    period = period_summary(candidate, parent)
    ann_rows = []
    for year in range(2017, 2021):
        for label, df in [("candidate", candidate), ("matched_parent", parent)]:
            ann_rows.append({"year": year, "series": label, **summarize(df[df.year == year])})
    pd.DataFrame(audits).to_csv(args.out_dir / "R293_session_quality_audit.csv", index=False)
    candidate.to_csv(args.out_dir / "R293_candidate_trade_ledger.csv", index=False)
    parent.to_csv(args.out_dir / "R293_matched_parent_ledger.csv", index=False)
    skipped.to_csv(args.out_dir / "R293_skipped_dates.csv", index=False)
    pd.DataFrame(ann_rows).to_csv(args.out_dir / "R293_annual_summary.csv", index=False)
    d, v = period["discovery"]["candidate"], period["validation"]["candidate"]
    annual = period["discovery"]["candidate_yearly"]
    boot = period["validation"]["candidate_weekly_bootstrap"]
    gates = {
        "discovery_min_200_trades": d["trades"] >= 200,
        "discovery_net_bp_2_positive": d["net_bp_2"] > 0,
        "discovery_pf_2bp_ge_1_05": d["pf_2bp"] is not None and d["pf_2bp"] >= 1.05,
        "discovery_at_least_2_of_4_years_positive": sum(annual[y]["net_bp_2"] > 0 for y in annual) >= 2,
        "discovery_pf_4bp_ge_0_90": d["pf_4bp"] is not None and d["pf_4bp"] >= 0.90,
        "validation_min_75_trades": v["trades"] >= 75,
        "validation_net_bp_2_positive": v["net_bp_2"] > 0,
        "validation_pf_2bp_ge_1_05": v["pf_2bp"] is not None and v["pf_2bp"] >= 1.05,
        "validation_bootstrap_ci_lower_gt_zero": boot["ci95_low"] > 0,
        "validation_pf_4bp_ge_0_90": v["pf_4bp"] is not None and v["pf_4bp"] >= 0.90,
    }
    result = {
        "candidate_id": "R293_USA500_OVERNIGHT_BREADTH_FILTER",
        "verdict": "LULUS_HISTORICAL_SCREEN_ONLY" if all(gates.values()) else "GAGAL",
        "inputs": metas,
        "data_quality": {
            "audited_instrument_sessions": int(len(audits)),
            "eligible_sessions_by_symbol": {m["symbol"]: m["valid_sessions"] for m in metas},
            "skipped_candidate_event_dates": int(len(skipped)),
            "skips_by_reason": skipped["reason"].value_counts().to_dict() if len(skipped) else {},
        },
        "locked_windows": {"discovery": "2017-01-01/2020-12-31", "validation": "2021-01-01/2021-12-31",
                           "no_strategy_pnl_calculated_2022_plus": True},
        "results": period,
        "gates": {k: {"pass": bool(v)} for k, v in gates.items()},
        "limitations": [
            "All inputs are cached M5 BID-only; 1/2/4 bp are modeled cost sensitivities, not verified executable costs.",
            "No ask-side spread, slippage, swap, margin, overnight floating equity or funded account-path was modeled.",
            "2017-2021 windows are contaminated; this is not pristine independent OOS.",
            "No strategy PnL was calculated for 2022 or later."
        ]
    }
    (args.out_dir / "R293_results_compact.json").write_text(json.dumps(result, indent=2, allow_nan=False))
    lines = ["# R293 — USA500 Overnight Carry With Closing Cross-Index Breadth",
             f"\n**Verdict: {result['verdict']}**\n", "## Candidate results\n",
             "| Metric | Discovery 2017–2020 | Validation 2021 |", "|---|---:|---:|"]
    for key, label in [("trades", "Trades"), ("gross_bp", "Gross total bp"), ("net_bp_2", "Net bp at 2bp"),
                       ("pf_2bp", "PF at 2bp"), ("net_bp_4", "Net bp at 4bp"), ("pf_4bp", "PF at 4bp"),
                       ("max_closed_pnl_drawdown_pct_fixed_notional_2bp", "Max closed PnL drawdown (% fixed notional)")]:
        lines.append(f"| {label} | {period['discovery']['candidate'].get(key)} | {period['validation']['candidate'].get(key)} |")
    lines += ["\n## Matched unconditional parent (diagnostic only)\n",
              "| Metric | Discovery 2017–2020 | Validation 2021 |", "|---|---:|---:|"]
    for key, label in [("trades", "Trades"), ("net_bp_2", "Net bp at 2bp"), ("pf_2bp", "PF at 2bp"),
                       ("net_bp_4", "Net bp at 4bp"), ("pf_4bp", "PF at 4bp")]:
        lines.append(f"| {label} | {period['discovery']['matched_unconditional_parent'].get(key)} | {period['validation']['matched_unconditional_parent'].get(key)} |")
    lines += ["\n## Validation bootstrap\n",
              f"- Candidate: {boot['mean_weekly_net_bp_2']:.4f} bp/week; 95% CI [{boot['ci95_low']:.4f}, {boot['ci95_high']:.4f}].",
              "\n## Locked gates\n", "| Gate | Result |", "|---|---|"]
    for k, v0 in gates.items():
        lines.append(f"| {k} | {'PASS' if v0 else 'FAIL'} |")
    lines += ["\n## Limitations\n",
              "- Four feeds are M5 BID-only; modeled costs are not executable quotes.",
              "- No overnight floating loss, swap or FundedNext DLL/MLL equity-path replay was run.",
              "- Historical validation is contaminated and cannot establish pristine OOS.",
              "- No candidate PnL was calculated for 2022 or later; do not tune this failed hypothesis on the same dates."]
    (args.out_dir / "R293_FINAL_REPORT.md").write_text("\n".join(lines) + "\n")

if __name__ == "__main__":
    main()
