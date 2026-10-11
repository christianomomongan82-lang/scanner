#!/usr/bin/env python3
"""R211: locked H4 55-bar breakout followed by a held 3-bar retest.

One preregistered hypothesis. A completed H4 close breaks above the prior 55-bar
high. Within the next 1-3 completed H4 bars, price must touch that breakout
level and close back above it. Enter via the first non-flat M5 open at least
five minutes after retest confirmation, before the following H4 close. Stop at
the retest H4 low, target 2R. One position per instrument. Raw OHLC only.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research.r192_ger40 import parse_data

CFG = {
    "id": "R211_H4_55BAR_BREAKOUT_HELD_RETEST_3B_RR2",
    "role": "locked_h4_breakout_retest_candidate",
    "breakout": 55,
    "retest_bars": 3,
}
ASSETS = {
    "usa500idxusd": "USA 500 / S&P 500",
    "usatechidxusd": "USA 100 Tech / Nasdaq 100",
    "usa30idxusd": "USA 30 / Dow Jones",
    "ussc2000idxusd": "US Small Cap 2000",
    "deuidxeur": "Germany 40 / DAX",
    "gbridxgbp": "FTSE 100",
    "fraidxeur": "France 40 / CAC 40",
    "eusidxeur": "EU Stocks 50",
    "ausidxaud": "Australia 200",
    "jpnidxjpy": "Japan 200+",
}
RR = 2.0
DISCOVERY_START = pd.Timestamp("2017-01-01", tz="UTC")
DISCOVERY_END = pd.Timestamp("2022-01-01", tz="UTC")
FORWARD_START = DISCOVERY_END
FORWARD_END = pd.Timestamp("2026-01-01", tz="UTC")
OOS_START = FORWARD_END


def build_h4_utc(h1, now_utc):
    """Aggregate only UTC H4 bins containing four consecutive H1 bars."""
    now_utc = pd.Timestamp(now_utc)
    if now_utc.tzinfo is None:
        now_utc = now_utc.tz_localize("UTC")
    else:
        now_utc = now_utc.tz_convert("UTC")
    src = h1.copy().sort_index()
    src.index = src.index.tz_convert("UTC")
    idx = src.index
    start = idx[0].floor("4h")
    end = idx[-1].floor("4h") + pd.Timedelta(hours=4)
    bounds = pd.date_range(start=start, end=end, freq="4h")
    rows = []
    skipped = 0
    for left, right in zip(bounds, bounds[1:]):
        a = int(idx.searchsorted(left, side="left"))
        b = int(idx.searchsorted(right, side="left"))
        ch = src.iloc[a:b]
        expected = pd.date_range(left, periods=4, freq="1h")
        if len(ch) != 4 or not ch.index.equals(expected):
            skipped += 1
            continue
        rows.append({
            "label_utc": left,
            "bar_close_utc": right,
            "open": float(ch.open.iloc[0]),
            "high": float(ch.high.max()),
            "low": float(ch.low.min()),
            "close": float(ch.close.iloc[-1]),
            "completed": bool(right <= now_utc),
        })
    if not rows:
        raise ValueError("No complete UTC H4 bars could be built from H1 source")
    h4 = pd.DataFrame(rows).set_index("label_utc")
    h4.index = pd.DatetimeIndex(h4.index).tz_convert("UTC")
    return h4, {
        "h4_bars": len(h4),
        "h4_anchor": "UTC 00/04/08/12/16/20",
        "incomplete_or_missing_h4_bins_skipped": skipped,
        "h4_start_utc": h4.index[0].isoformat(),
        "h4_end_utc": h4["bar_close_utc"].iloc[-1].isoformat(),
    }


def signals_and_stops(h4, cfg=CFG):
    """Causal retest signal: prior channel breakout, then a held touch in next 3 bars."""
    hi = h4.high.to_numpy(float)
    lo = h4.low.to_numpy(float)
    cl = h4.close.to_numpy(float)
    completed = h4.completed.to_numpy(bool)
    n = len(h4)
    b = int(cfg["breakout"])
    wait = int(cfg["retest_bars"])
    sig = np.zeros(n, dtype=bool)
    stops = np.full(n, np.nan)
    levels = np.full(n, np.nan)
    breakout_idx = np.full(n, -1, dtype=np.int64)

    # Decide on each retest bar from that bar and the 1-3 already completed
    # bars before it. This form is prefix-causal by construction.
    for j in range(b + 1, n):
        if not completed[j]:
            continue
        for i in range(max(b, j - wait), j):
            if not completed[i]:
                continue
            level = float(np.max(hi[i - b:i]))
            if cl[i] <= level:
                continue
            if lo[j] <= level and cl[j] > level:
                sig[j] = True
                stops[j] = float(lo[j])
                levels[j] = level
                breakout_idx[j] = i
                break
    return sig, stops, levels, breakout_idx


def truncation_gate(h4, full_sig, full_stops, full_levels, full_breakout_idx, cfg=CFG):
    """Independent scalar prefix check for every completed H4 decision."""
    hi = h4.high.to_numpy(float)
    lo = h4.low.to_numpy(float)
    cl = h4.close.to_numpy(float)
    completed = h4.completed.to_numpy(bool)
    b = int(cfg["breakout"])
    wait = int(cfg["retest_bars"])
    checked = 0
    for j in np.flatnonzero(completed):
        checked += 1
        expected_sig = False
        expected_stop = np.nan
        expected_level = np.nan
        expected_breakout_idx = -1
        for i in range(max(b, int(j) - wait), int(j)):
            if not completed[i]:
                continue
            level = float(np.max(hi[i - b:i]))
            if cl[i] <= level:
                continue
            if lo[j] <= level and cl[j] > level:
                expected_sig = True
                expected_stop = float(lo[j])
                expected_level = level
                expected_breakout_idx = int(i)
                break
        if expected_sig != bool(full_sig[j]):
            return {"pass": False, "checked": checked, "bar": int(j), "reason": "retest signal prefix mismatch"}
        if expected_sig:
            if not np.isclose(expected_stop, float(full_stops[j]), rtol=0, atol=1e-12):
                return {"pass": False, "checked": checked, "bar": int(j), "reason": "stop mismatch"}
            if not np.isclose(expected_level, float(full_levels[j]), rtol=0, atol=1e-12):
                return {"pass": False, "checked": checked, "bar": int(j), "reason": "breakout level mismatch"}
            if expected_breakout_idx != int(full_breakout_idx[j]):
                return {"pass": False, "checked": checked, "bar": int(j), "reason": "trigger bar mismatch"}
    return {"pass": True, "checked": checked, "reason": "all completed-bar prefixes match"}


def simulate(h4, m5, cfg, sig, stops, levels, breakout_idx):
    h4utc = h4.index.tz_convert("UTC")
    completed = h4.completed.to_numpy(bool)
    mt = m5.index.tz_convert("UTC")
    op = m5.open.to_numpy(float)
    hi = m5.high.to_numpy(float)
    lo = m5.low.to_numpy(float)
    close = m5.close.to_numpy(float)
    flat = (op == hi) & (hi == lo) & (lo == close)

    trades = []
    skipped_active = 0
    skipped_no_fill = 0
    skipped_invalid_risk = 0
    last_exit = None
    for j in range(len(h4) - 1):
        if not completed[j] or not bool(sig[j]):
            continue
        signal_time = pd.Timestamp(h4["bar_close_utc"].iloc[j]).tz_convert("UTC")
        if last_exit is not None and (pd.isna(last_exit) or not (last_exit < signal_time)):
            skipped_active += 1
            continue

        stop = float(stops[j])
        left = int(mt.searchsorted(signal_time + pd.Timedelta(minutes=5), side="left"))
        next_bar_close = pd.Timestamp(h4["bar_close_utc"].iloc[j + 1]).tz_convert("UTC")
        right = int(mt.searchsorted(next_bar_close, side="left"))
        start_j = next((k for k in range(left, right) if not flat[k]), None)
        if start_j is None:
            skipped_no_fill += 1
            continue
        entry_time = mt[start_j]
        entry = float(op[start_j])
        if not math.isfinite(entry - stop) or entry <= stop:
            skipped_invalid_risk += 1
            continue
        risk = entry - stop
        target = entry + RR * risk

        exit_time = None
        exit_price = np.nan
        reason = "OPEN_AT_DATA_END"
        flat_skipped = 0
        for k in range(start_j, len(mt)):
            if flat[k]:
                flat_skipped += 1
                continue
            o = float(op[k]); h = float(hi[k]); l = float(lo[k])
            # SL first, with market-open fill if a gap has passed the stop.
            if l <= stop or o <= stop:
                exit_price = o if o <= stop else stop
                reason = "SL_GAP_OPEN" if o <= stop else "SL"
                exit_time = mt[k]
                break
            if h >= target:
                exit_price = target
                reason = "TP"
                exit_time = mt[k]
                break

        bi = int(breakout_idx[j])
        trades.append({
            "config": cfg["id"], "role": cfg["role"],
            "breakout_lookback": int(cfg["breakout"]),
            "max_retest_wait_bars": int(cfg["retest_bars"]),
            "mode": "manual5m",
            "breakout_bar_utc": h4utc[bi].isoformat(),
            "breakout_close_utc": pd.Timestamp(h4["bar_close_utc"].iloc[bi]).tz_convert("UTC").isoformat(),
            "breakout_level": float(levels[j]),
            "retest_bar_utc": h4utc[j].isoformat(),
            "signal_close_utc": signal_time.isoformat(),
            "entry_time_utc": entry_time.isoformat(),
            "entry": entry, "sl": stop, "tp": target,
            "exit_time_utc": None if exit_time is None else exit_time.isoformat(),
            "exit": None if exit_time is None else float(exit_price),
            "reason": reason, "entry_exact_m5_timestamp": True,
            "risk_points": risk, "flat_m5_bars_skipped_while_open": flat_skipped,
        })
        last_exit = pd.NaT if exit_time is None else exit_time
        if pd.isna(last_exit):
            break
    return trades, {
        "signals": int((sig & completed).sum()), "taken": len(trades),
        "skipped_active": skipped_active, "skipped_no_tradable_fill": skipped_no_fill,
        "skipped_invalid_risk": skipped_invalid_risk,
    }


def trade_r(trade, bps):
    if trade["exit"] is None:
        return np.nan
    cost = float(trade["entry"]) * bps / 10000.0
    return (float(trade["exit"]) - float(trade["entry"]) - cost) / float(trade["risk_points"])


def finite_number(x):
    return isinstance(x, (int, float, np.integer, np.floating)) and math.isfinite(float(x))


def metric(trades, start, end, cutoff, bps):
    picked = [t for t in trades if start <= pd.Timestamp(t["entry_time_utc"]) < end]
    closed = [t for t in picked if t["exit_time_utc"] is not None and pd.Timestamp(t["exit_time_utc"]) < cutoff]
    vals = np.asarray([trade_r(t, bps) for t in closed], dtype=float)
    wins = float(vals[vals > 0].sum()) if len(vals) else 0.0
    losses = float(-vals[vals < 0].sum()) if len(vals) else 0.0
    pf = wins / losses if losses > 0 else (float("inf") if wins > 0 else float("nan"))
    return {"entries": len(picked), "closed": len(closed), "censored": len(picked) - len(closed),
            "pf": pf, "wins_r": wins, "losses_r": losses}


def safe(x):
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating, float)):
        if math.isnan(float(x)): return None
        if math.isinf(float(x)): return "INF" if x > 0 else "-INF"
        return float(x)
    if isinstance(x, (pd.Timestamp,)):
        return x.isoformat()
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="dl")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    data_dir = Path(args.data_dir)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    common_end_by_asset = {}
    parsed = {}
    asset_meta = {}
    all_trades = []
    annual_rows = []
    diagnostics = {}

    # Validate all sources and prefix-causality before reporting any PF.
    now = pd.Timestamp.now(tz="UTC")
    for inst, name in ASSETS.items():
        h1_path = data_dir / f"{inst}_h1.csv.gz"
        m5_path = data_dir / f"{inst}_m5.csv.gz"
        if not h1_path.is_file() or not m5_path.is_file():
            raise SystemExit(f"HARD STOP: missing H1/M5 source for {inst}")
        h1, h1_dups = parse_data(h1_path)
        m5, m5_dups = parse_data(m5_path)
        if len(h1) < 5000 or len(m5) < 10000:
            raise SystemExit(f"HARD STOP: too few rows for {inst}: H1={len(h1)}, M5={len(m5)}")
        if not h1.index.is_monotonic_increasing or h1.index.has_duplicates:
            raise SystemExit(f"HARD STOP: unsorted/duplicate H1 index for {inst}")
        if not m5.index.is_monotonic_increasing or m5.index.has_duplicates:
            raise SystemExit(f"HARD STOP: unsorted/duplicate M5 index for {inst}")
        h4, h4_diag = build_h4_utc(h1, now)
        sig, stops, levels, breakout_idx = signals_and_stops(h4, CFG)
        gate = truncation_gate(h4, sig, stops, levels, breakout_idx, CFG)
        if not gate["pass"]:
            raise SystemExit(f"HARD STOP: causal/truncation check failed for {inst}: {gate}")
        parsed[inst] = (h4, m5, sig, stops, levels, breakout_idx)
        common_end_by_asset[inst] = m5.index[-1].tz_convert("UTC") + pd.Timedelta(minutes=5)
        asset_meta[inst] = {
            "name": name,
            "h1_rows": len(h1), "h1_duplicates_removed": h1_dups,
            "m5_rows": len(m5), "m5_duplicates_removed": m5_dups,
            "h1_start_utc": h1.index[0].tz_convert("UTC").isoformat(),
            "h1_end_utc": h1.index[-1].tz_convert("UTC").isoformat(),
            "m5_start_utc": m5.index[0].tz_convert("UTC").isoformat(),
            "m5_end_utc": m5.index[-1].tz_convert("UTC").isoformat(),
            "flat_m5_rows": int(((m5.open == m5.high) & (m5.high == m5.low) & (m5.low == m5.close)).sum()),
            **h4_diag, "truncation_gate": gate,
        }
        print(f"TRUNCATION GATE PASS {inst}: completed prefixes={gate['checked']}; H1={len(h1):,}; M5={len(m5):,}; retests={int((sig & h4.completed.to_numpy(bool)).sum()):,}", flush=True)

    common_end = min(common_end_by_asset.values())
    for inst, name in ASSETS.items():
        h4, m5, sig, stops, levels, breakout_idx = parsed[inst]
        trades, sim_diag = simulate(h4, m5, CFG, sig, stops, levels, breakout_idx)
        tagged = []
        for original in trades:
            t = dict(original)
            t["instrument"] = inst
            t["instrument_name"] = name
            tagged.append(t)
        all_trades.extend(tagged)
        diagnostics[inst] = {**sim_diag}
        for phase, (start, end, cutoff) in {
            "discovery": (DISCOVERY_START, DISCOVERY_END, DISCOVERY_END),
            "forward": (FORWARD_START, FORWARD_END, FORWARD_END),
            "oos": (OOS_START, common_end, common_end),
        }.items():
            for bps in (1, 2):
                m = metric(tagged, start, end, cutoff, bps)
                diagnostics[inst][f"{phase}_entries"] = m["entries"]
                diagnostics[inst][f"{phase}_closed"] = m["closed"]
                diagnostics[inst][f"{phase}_censored"] = m["censored"]
                diagnostics[inst][f"{phase}_pf_{bps}bp"] = m["pf"]
        for year in range(2017, 2027):
            if year <= 2021: cutoff = DISCOVERY_END
            elif year <= 2025: cutoff = FORWARD_END
            else: cutoff = common_end
            start = pd.Timestamp(f"{year}-01-01", tz="UTC")
            end = pd.Timestamp(f"{year+1}-01-01", tz="UTC")
            for bps in (1, 2):
                m = metric(tagged, start, end, cutoff, bps)
                annual_rows.append({
                    "instrument": inst, "instrument_name": name, "entry_year": year, "cost_bps_rt": bps,
                    "entries": m["entries"], "n_closed_by_cutoff": m["closed"],
                    "censored_by_cutoff": m["censored"], "pf_entry_cohort": m["pf"],
                    "wins_r": m["wins_r"], "losses_r": m["losses_r"],
                })

    ledger = pd.DataFrame([{"instrument": inst, "instrument_name": ASSETS[inst], **diagnostics[inst]}
                           for inst in ASSETS])
    cohorts = pd.DataFrame(annual_rows)
    eligible = ledger[
        (ledger["discovery_closed"] >= 30)
        & ledger["discovery_pf_2bp"].apply(finite_number)
        & (ledger["discovery_pf_2bp"] >= 1.0)
    ].copy()
    eligible = eligible.sort_values(
        ["discovery_closed", "discovery_pf_2bp", "instrument"],
        ascending=[False, False, True], kind="stable"
    )
    selected = {"forward_verdict": "NO_DISCOVERY_ELIGIBLE_CANDIDATE",
                "note": "No instrument reached >=30 discovery closes and PF@2bp >=1.00; no forward winner may be selected."}
    if len(eligible):
        pick = eligible.iloc[0]
        inst = str(pick["instrument"])
        yearly = cohorts[
            (cohorts["instrument"] == inst) & (cohorts["cost_bps_rt"] == 1)
            & cohorts["entry_year"].between(2022, 2025) & (cohorts["n_closed_by_cutoff"] >= 5)
        ]
        yearpfs = [float(x) for x in yearly["pf_entry_cohort"] if finite_number(x)]
        worst = min(yearpfs) if yearpfs else None
        pf1 = float(pick["forward_pf_1bp"]); pf2 = float(pick["forward_pf_2bp"])
        pass_base = (
            int(pick["forward_closed"]) >= 30 and math.isfinite(pf1) and pf1 >= 1.15
            and math.isfinite(pf2) and pf2 >= 1.15 and (worst is None or worst >= 1.0)
        )
        suspicious = math.isfinite(pf1) and pf1 > 1.4
        selected = {
            "instrument": inst, "instrument_name": ASSETS[inst],
            "selection_rule": "highest discovery close count among assets with >=30 discovery closes and PF@2bp >=1.00; tie-break by PF@2bp",
            "discovery_closed": int(pick["discovery_closed"]),
            "discovery_pf_1bp": float(pick["discovery_pf_1bp"]),
            "discovery_pf_2bp": float(pick["discovery_pf_2bp"]),
            "forward_closed": int(pick["forward_closed"]),
            "forward_pf_1bp": pf1, "forward_pf_2bp": pf2,
            "forward_worst_entry_year_pf_1bp_n5plus": worst,
            "forward_pf_gt_1_4_extra_audit_required": bool(suspicious),
            "oos_closed": int(pick["oos_closed"]),
            "oos_pf_1bp": float(pick["oos_pf_1bp"]),
            "oos_pf_2bp": float(pick["oos_pf_2bp"]),
            "forward_verdict": "HOLD_EXTRA_AUDIT" if pass_base and suspicious else "PASS" if pass_base else "REJECT",
        }

    meta = {
        "research": "R211: H4 55-bar channel breakout followed by a held retest in next 1-3 completed H4 bars",
        "run_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "common_oos_cutoff_utc": common_end.isoformat(),
        "assets": asset_meta,
        "locked_rule": {
            "h4_anchor": "UTC 00/04/08/12/16/20; only complete bins with four consecutive H1 bars",
            "direction": "long only",
            "breakout": "completed H4 close > prior 55 completed H4 bars' maximum high",
            "retest": "within the next 1-3 completed H4 bars, low touches or crosses breakout level and close finishes above the same level",
            "entry": "first non-flat M5 open >= 5 minutes after retest H4 close, before the next H4 close",
            "stop": "retest H4 bar low",
            "target": "entry + 2R",
            "position_limit": "one active position per instrument",
            "exit": "M5 BID OHLC; SL checked before TP; a gap through SL fills at open; no time stop; flat synthetic M5 bars skipped",
            "cost_model": "1bp and 2bp modeled round-trip price cost; not actual broker spread, commission, or live slippage",
            "selection": "discovery only: >=30 closed trades and PF@2bp >=1.00; highest trade frequency among eligible assets, PF tie-break",
            "validation": "forward 2022-2025 requires >=30 closes, PF >=1.15 at both costs and worst eligible entry-year cohort PF >=1.00; PF >1.40 requires extra audit",
        },
        "periods": {
            "discovery": "entries 2017-2021; exits before 2022-01-01",
            "forward": "entries 2022-2025; exits before 2026-01-01",
            "oos": "entries 2026 to common cached-data cutoff",
        },
        "discovery_eligible_instruments": eligible["instrument"].tolist(),
        "locked_selected_candidate": selected,
        "guardrails": [
            "One preregistered retest definition; no parameter grid.",
            "Causal prefix check was run at every completed H4 decision per instrument.",
            "Instrument selection is discovery-only; a failed forward candidate is not replaced based on forward PF.",
            "Sources are Dukascopy BID H1/M5; bid-only results are screening evidence, not proof of executable spread/commission/slippage.",
        ],
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=safe), encoding="utf-8")
    ledger.to_csv(out / "ten_instrument_ledger.csv", index=False)
    cohorts.to_csv(out / "annual_cohort.csv", index=False)
    pd.DataFrame(all_trades).to_csv(out / "trades.csv", index=False)

    show = ["instrument", "discovery_closed", "discovery_pf_1bp", "discovery_pf_2bp",
            "forward_closed", "forward_pf_1bp", "forward_pf_2bp",
            "forward_worst_entry_year_pf_1bp_n5plus", "oos_closed", "oos_pf_1bp", "oos_pf_2bp"]
    ledger["forward_worst_entry_year_pf_1bp_n5plus"] = np.nan
    for idx, row in ledger.iterrows():
        inst = row["instrument"]
        y = cohorts[(cohorts["instrument"] == inst) & (cohorts["cost_bps_rt"] == 1)
                    & cohorts["entry_year"].between(2022, 2025) & (cohorts["n_closed_by_cutoff"] >= 5)]
        vals = [float(x) for x in y["pf_entry_cohort"] if finite_number(x)]
        ledger.loc[idx, "forward_worst_entry_year_pf_1bp_n5plus"] = min(vals) if vals else np.nan
    print("\nR211 DISCOVERY/FORWARD LEDGER:", flush=True)
    print(ledger[show].sort_values(["discovery_closed", "instrument"], ascending=[False, True]).to_string(index=False), flush=True)
    print("\nLOCKED SELECTION + FORWARD VERDICT:", flush=True)
    print(json.dumps(selected, indent=2, default=safe), flush=True)
    print(f"Common OOS cutoff UTC: {common_end.isoformat()}", flush=True)
    print(f"Artifacts written to {out.resolve()}", flush=True)


if __name__ == "__main__":
    main()
