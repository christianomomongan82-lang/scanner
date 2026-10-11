#!/usr/bin/env python3
"""R205: test cross-index breadth confirmation for the locked H4 breakout.

Preregistered single hypothesis: allow the locked long-only 55-bar breakout only
when at least 4 of at least 8 indices have a simultaneous breakout at the same
completed UTC H4 close. Stops, 2R target, execution and validation gates are locked.
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
from research.r192_ger40 import (
    parse_data, signals_and_stops, truncation_gate, simulate,
    metric, annual_rows, annual_cohort_rows, safe, PERIODS,
)

CFG = {"id": "R205_BREADTH4OF10_UTC_H4_55_27", "role": "locked_breadth_confirmation_candidate",
       "breakout": 55, "stop_bars": 27}
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



def build_h4_utc(h1, now_utc):
    """Aggregate complete UTC H4 bins from four consecutive H1 BID bars.

    Unlike the historical New York-clock grouping, this uses 00/04/08/12/16/20
    UTC boundaries on every instrument. Missing source H1 bars are not filled:
    any H4 bin without the exact four hourly timestamps is skipped.
    """
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
    diag = {
        "h4_bars": len(h4),
        "h4_anchor": "UTC 00/04/08/12/16/20",
        "incomplete_or_missing_h4_bins_skipped": skipped,
        "h4_start_utc": h4.index[0].isoformat(),
        "h4_end_utc": h4["bar_close_utc"].iloc[-1].isoformat(),
    }
    return h4, diag


def phase_metrics(trades, observed_end):
    spans = {
        "history_2016_2025": (pd.Timestamp("2016-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")),
        "discovery_2017_2021": PERIODS["discovery"],
        "forward_2022_2025": PERIODS["forward"],
        "oos_2026_to_data_end": (PERIODS["oos2026"][0], observed_end),
    }
    out = {}
    for phase, (start, end) in spans.items():
        for bps in (1, 2):
            m = metric(trades, start, end, bps)
            out[f"{phase}_entries"] = m["entries"]
            out[f"{phase}_closed"] = m["n"]
            out[f"{phase}_censored"] = m["censored"]
            out[f"{phase}_pf_{bps}bp"] = m["pf"]
    return out



def simulate_filtered(h4, m5, cfg, filtered_sig, stops, mode, breadth_map):
    """R191-compatible execution using an externally breadth-filtered signal array."""
    sig = np.asarray(filtered_sig, dtype=np.int8)
    stops = np.asarray(stops, dtype=float)
    h4utc = h4.index.tz_convert("UTC")
    completed = h4["completed"].to_numpy(bool)
    mt = m5.index.tz_convert("UTC")
    op = m5.open.to_numpy(float); hi = m5.high.to_numpy(float); lo = m5.low.to_numpy(float)
    close = m5.close.to_numpy(float)
    flat = (op == hi) & (hi == lo) & (lo == close)
    trades = []
    skipped_active = 0
    skipped_no_fill = 0
    skipped_invalid_risk = 0
    last_exit = None
    for i in range(len(h4) - 1):
        if not completed[i] or not sig[i]:
            continue
        signal_time = pd.Timestamp(h4["bar_close_utc"].iloc[i]).tz_convert("UTC")
        if last_exit is not None and (pd.isna(last_exit) or not (last_exit < signal_time)):
            skipped_active += 1
            continue
        stop = float(stops[i])
        if mode == "ideal":
            entry_time = h4utc[i + 1]
            entry = float(h4.open.iloc[i + 1])
            start_j = int(mt.searchsorted(entry_time, side="left"))
            exact = bool(start_j < len(mt) and mt[start_j] == entry_time)
            if start_j >= len(mt):
                skipped_invalid_risk += 1
                continue
        else:
            left = int(mt.searchsorted(signal_time + pd.Timedelta(minutes=5), side="left"))
            next_close = pd.Timestamp(h4["bar_close_utc"].iloc[i + 1]).tz_convert("UTC")
            right = int(mt.searchsorted(next_close, side="left"))
            start_j = next((j for j in range(left, right) if not flat[j]), None)
            if start_j is None:
                skipped_no_fill += 1
                continue
            entry_time = mt[start_j]
            entry = float(op[start_j])
            exact = True
        if start_j is None or start_j >= len(mt) or entry <= stop or not math.isfinite(entry - stop):
            skipped_invalid_risk += 1
            continue
        risk = entry - stop
        target = entry + RR * risk
        exit_time = None
        exit_price = np.nan
        reason = "OPEN_AT_DATA_END"
        flat_skipped = 0
        for j in range(start_j, len(mt)):
            if flat[j]:
                flat_skipped += 1
                continue
            o = float(op[j]); hh = float(hi[j]); ll = float(lo[j])
            if ll <= stop or o <= stop:
                exit_price = o if o <= stop else stop
                reason = "SL_GAP_OPEN" if o <= stop else "SL"
                exit_time = mt[j]
                break
            if hh >= target:
                exit_price = target
                reason = "TP"
                exit_time = mt[j]
                break
        valid_n, breadth_n = breadth_map.get(signal_time, (0, 0))
        trades.append({
            "config": cfg["id"], "role": cfg["role"], "breakout": cfg["breakout"],
            "stop_bars": cfg["stop_bars"], "breadth_min_breakouts": 4,
            "breadth_min_valid_indices": 8, "breadth_valid_indices": valid_n,
            "simultaneous_breakouts": breadth_n, "mode": mode,
            "signal_bar_utc": h4utc[i].isoformat(), "signal_close_utc": signal_time.isoformat(),
            "entry_time_utc": entry_time.isoformat(), "entry": entry, "sl": stop, "tp": target,
            "exit_time_utc": None if exit_time is None else exit_time.isoformat(),
            "exit": None if exit_time is None else float(exit_price), "reason": reason,
            "entry_exact_m5_timestamp": exact, "risk_points": risk,
            "flat_m5_bars_skipped_while_open": flat_skipped,
        })
        last_exit = pd.NaT if exit_time is None else exit_time
        if pd.isna(last_exit):
            break
    return trades, {
        "signals": int((sig & completed).sum()), "taken": len(trades),
        "skipped_active": skipped_active, "skipped_no_tradable_fill": skipped_no_fill,
        "skipped_invalid_risk": skipped_invalid_risk,
    }


def finite_number(x):
    return isinstance(x, (int, float, np.integer, np.floating)) and math.isfinite(float(x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="dl")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    data_dir, out = Path(args.data_dir), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    reports, annual, cohorts, all_trades = [], [], [], []
    trade_sets, meta_assets, gates = {}, {}, {}
    parsed, observed_ends = {}, {}
    base_sigs, base_stops = {}, {}

    # Parse and pass causal/truncation checks for every asset before showing any PF.
    for inst, name in ASSETS.items():
        h1_path = data_dir / f"{inst}_h1.csv.gz"
        m5_path = data_dir / f"{inst}_m5.csv.gz"
        if not h1_path.is_file() or not m5_path.is_file():
            raise SystemExit(f"HARD STOP: missing cached source data for {inst}: {h1_path}, {m5_path}")
        h1, h1_dups = parse_data(h1_path)
        m5, m5_dups = parse_data(m5_path)
        now = pd.Timestamp.now(tz="UTC")
        h4, diag = build_h4_utc(h1, now)
        if len(h4) < 100:
            raise SystemExit(f"HARD STOP: only {len(h4)} H4 bars for {inst}")
        sig, stops = signals_and_stops(h4, CFG)
        base_sigs[inst], base_stops[inst] = sig, stops
        gate = truncation_gate(h4, CFG, sig, stops)
        gates[inst] = gate
        if not gate["pass"]:
            raise SystemExit(f"HARD STOP: truncation gate failed for {inst}: {gate}")
        flat_m5 = int(((m5.open == m5.high) & (m5.high == m5.low) & (m5.low == m5.close)).sum())
        meta_assets[inst] = {
            "name": name, "h1_rows": len(h1), "h1_duplicates_removed": h1_dups,
            "m5_rows": len(m5), "m5_duplicates_removed": m5_dups,
            "h1_start_utc": h1.index[0].tz_convert("UTC").isoformat(),
            "h1_end_utc": h1.index[-1].tz_convert("UTC").isoformat(),
            "m5_start_utc": m5.index[0].tz_convert("UTC").isoformat(),
            "m5_end_utc": m5.index[-1].tz_convert("UTC").isoformat(),
            "m5_flat_rows": flat_m5, **diag,
        }
        parsed[inst] = (h4, m5)
        observed_ends[inst] = m5.index[-1].tz_convert("UTC") + pd.Timedelta(minutes=5)
        print(f"TRUNCATION GATE PASS {inst}: prefixes={gate['checked']}; H1={len(h1):,}; M5={len(m5):,}", flush=True)


    # Build a causal cross-index breadth map at each exact completed UTC H4 close.
    # Each state only uses that index's own completed bar and its trailing 55-bar channel.
    state_map = {}
    for inst, (h4, _m5) in parsed.items():
        sig = base_sigs[inst]
        for i in range(len(h4)):
            if not bool(h4["completed"].iloc[i]):
                continue
            t = pd.Timestamp(h4["bar_close_utc"].iloc[i]).tz_convert("UTC")
            state_map.setdefault(t, []).append((inst, bool(sig[i] != 0)))
    breadth_map = {
        t: (len(states), sum(1 for _inst, is_breakout in states if is_breakout))
        for t, states in state_map.items()
    }
    filtered_sigs = {}
    breadth_gate_failures = []
    for inst, (h4, _m5) in parsed.items():
        raw = base_sigs[inst]
        filtered = np.zeros(len(h4), dtype=np.int8)
        for i in range(len(h4)):
            if not bool(h4["completed"].iloc[i]) or int(raw[i]) == 0:
                continue
            t = pd.Timestamp(h4["bar_close_utc"].iloc[i]).tz_convert("UTC")
            valid_n, breakouts_n = breadth_map.get(t, (0, 0))
            if valid_n >= 8 and breakouts_n >= 4:
                filtered[i] = 1
            else:
                if filtered[i] != 0:
                    breadth_gate_failures.append((inst, t.isoformat()))
        filtered_sigs[inst] = filtered
    if breadth_gate_failures:
        raise SystemExit(f"HARD STOP: cross-index breadth gate failed: {breadth_gate_failures[:5]}")
    print(
        "BREADTH RULE PASS: each permitted signal has >=4 simultaneous breakouts "
        "among >=8 available indices at the same completed UTC H4 close.",
        flush=True,
    )

    common_end = min(observed_ends.values())
    for inst, name in ASSETS.items():
        h4, m5 = parsed[inst]
        observed_end = min(observed_ends[inst], common_end)
        for mode in ("ideal", "manual5m"):
            trades, sim_diag = simulate_filtered(h4, m5, CFG, filtered_sigs[inst], base_stops[inst], mode, breadth_map)
            tagged = []
            for original in trades:
                t = dict(original)
                t["instrument"] = inst
                t["instrument_name"] = name
                tagged.append(t)
            all_trades.extend(tagged)
            trade_sets[(inst, mode)] = tagged
            row = {
                "instrument": inst, "instrument_name": name, "mode": mode,
                "breakout": CFG["breakout"], "stop_bars": CFG["stop_bars"],
                "signals": sim_diag["signals"], "taken": sim_diag["taken"],
                "skipped_active": sim_diag["skipped_active"],
                "skipped_no_tradable_fill": sim_diag["skipped_no_tradable_fill"],
                "skipped_invalid_risk": sim_diag["skipped_invalid_risk"],
            }
            row.update(phase_metrics(tagged, observed_end))
            reports.append(row)
            annual.extend([{**r, "instrument": inst, "instrument_name": name}
                           for r in annual_rows(tagged, CFG, mode, observed_end)])
            cohorts.extend([{**r, "instrument": inst, "instrument_name": name}
                            for r in annual_cohort_rows(tagged, CFG, mode, observed_end)])

    ledger = pd.DataFrame(reports)
    manual = ledger[ledger["mode"] == "manual5m"].copy()
    # The instrument selection is frozen on discovery only, never on forward PF.
    eligible = manual[
        (manual["discovery_2017_2021_closed"] >= 10)
        & (manual["discovery_2017_2021_pf_2bp"].apply(finite_number))
        & (manual["discovery_2017_2021_pf_2bp"] >= 1.0)
    ].copy()
    eligible = eligible.sort_values(
        ["discovery_2017_2021_closed", "discovery_2017_2021_pf_2bp", "instrument"],
        ascending=[True, False, True], kind="stable")
    selected = None
    if len(eligible):
        selected = eligible.iloc[0].to_dict()
        fwd_coh = pd.DataFrame(cohorts)
        fwd_coh = fwd_coh[
            (fwd_coh["instrument"] == selected["instrument"])
            & (fwd_coh["mode"] == "manual5m")
            & (fwd_coh["cost_bps_rt"] == 1)
            & (fwd_coh["entry_year"].between(2022, 2025))
            & (fwd_coh["n_closed_by_cutoff"] >= 5)
        ]
        cohort_pfs = [float(x) for x in fwd_coh["pf_entry_cohort"] if finite_number(x)]
        worst = min(cohort_pfs) if cohort_pfs else None
        pf1, pf2 = selected["forward_2022_2025_pf_1bp"], selected["forward_2022_2025_pf_2bp"]
        suspicious = finite_number(pf1) and float(pf1) > 1.4
        normal_pass = (
            int(selected["forward_2022_2025_closed"]) >= 30
            and finite_number(pf1) and float(pf1) >= 1.15
            and finite_number(pf2) and float(pf2) >= 1.15
            and (worst is None or worst >= 1.0)
        )
        verdict = ("HOLD_EXTRA_AUDIT" if normal_pass and suspicious
                   else "PASS" if normal_pass
                   else "REJECT")
        selected = {
            "selection_method": "lowest number of closed manual5m trades in 2017-2021 among assets with >=10 discovery closes and discovery PF >=1.00 at 2bp",
            "instrument": selected["instrument"],
            "instrument_name": selected["instrument_name"],
            "discovery_closed": int(selected["discovery_2017_2021_closed"]),
            "discovery_pf_1bp": selected["discovery_2017_2021_pf_1bp"],
            "discovery_pf_2bp": selected["discovery_2017_2021_pf_2bp"],
            "forward_closed": int(selected["forward_2022_2025_closed"]),
            "forward_pf_1bp": pf1, "forward_pf_2bp": pf2,
            "forward_worst_entry_year_pf_1bp_n5plus": worst,
            "forward_pf_gt_1_4_extra_audit_required": bool(suspicious),
            "forward_verdict": verdict,
        }

    # Write all machine-readable results, including a ledger so every asset is visible.
    meta = {
        "research": "R205: one preregistered cross-index breadth filter on the locked UTC-H4 55/27 breakout",
        "run_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "snapshot_note": "All results use the same cached Dukascopy BID H1/M5 snapshot. Re-runs reuse that snapshot instead of redownloading; change the cache schema version deliberately to refresh.",
        "locked_rule": {
            "h4_anchor": "UTC 00/04/08/12/16/20; retain only bins with four consecutive H1 source bars",
            "direction": "long only",
            "signal": "H4 close > maximum high of prior 55 completed H4 bars, AND at least 4 of at least 8 available indices have a simultaneous 55-bar breakout at the same completed UTC H4 close",
            "breadth_gate": "at least 4 simultaneous breakout signals among at least 8 valid indices at the same completed UTC H4 close; each index state uses only trailing 55 completed H4 bars",
            "stop": "lowest low over signal bar and preceding 26 bars (27 inclusive)",
            "target": "entry + 2R",
            "entry_modes": {
                "ideal": "open of next H4 bar (comparison only)",
                "manual5m": "first non-flat M5 bar at or after signal close + 5 minutes, before the next UTC H4 close",
            },
            "exit": "M5 BID OHLC; SL checked before TP; gap through SL fills at open; no time stop",
            "cost_model": "1bp and 2bp modeled round-trip price cost; not a measured broker spread, commission, or live slippage",
        },
        "periods": {
            "history": "entries 2016-2025; exits before 2026-01-01",
            "discovery": "entries 2017-2021; outcomes closed before 2022-01-01",
            "forward": "entries 2022-2025; outcomes closed before 2026-01-01",
            "oos": "entries 2026 through common cached data cutoff",
        },
        "common_oos_cutoff_utc": common_end.isoformat(),
        "assets": meta_assets,
        "truncation_gates": gates,
        "discovery_eligible_assets": eligible["instrument"].tolist(),
        "selected_lowest_frequency_candidate": selected,
        "selection_guardrails": [
            "The only new hypothesis is a fixed cross-index breadth filter: >=4 breakouts among >=8 available indices. No threshold sweep was performed.",
            "Instrument selection uses discovery frequency and discovery PF only.",
            "Forward metrics are a one-time confirmation; if the selected instrument fails, do not swap to another instrument using forward results.",
            "This is a research shortlist, not evidence of live profitability.",
            "H1/M5 sources are Dukascopy BID. Flat source bars are retained for signal aggregation; synthetic flat M5 bars are skipped for manual execution.",
        ],
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=safe), encoding="utf-8")
    ledger.to_csv(out / "ten_instrument_ledger.csv", index=False)
    pd.DataFrame(annual).to_csv(out / "annual.csv", index=False)
    pd.DataFrame(cohorts).to_csv(out / "annual_cohort.csv", index=False)
    pd.DataFrame(all_trades).to_csv(out / "trades.csv", index=False)

    show = [
        "instrument", "discovery_2017_2021_closed", "discovery_2017_2021_pf_1bp",
        "discovery_2017_2021_pf_2bp", "forward_2022_2025_closed",
        "forward_2022_2025_pf_1bp", "forward_2022_2025_pf_2bp",
        "oos_2026_to_data_end_closed", "oos_2026_to_data_end_pf_1bp",
        "oos_2026_to_data_end_pf_2bp", "signals", "taken",
    ]
    ranking = manual.sort_values(["discovery_2017_2021_closed", "instrument"], kind="stable")
    print("\nR205 RANKING: manual5m sorted by discovery closed-trade count (cost 1bp/2bp):", flush=True)
    print(ranking[show].to_string(index=False), flush=True)
    print("\nDISCOVERY-ELIGIBLE ASSETS (ranked by fewest discovery trades):", flush=True)
    print(eligible[["instrument", "discovery_2017_2021_closed",
                    "discovery_2017_2021_pf_1bp", "discovery_2017_2021_pf_2bp"]].to_string(index=False), flush=True)
    print("\nLOCKED SELECTION + FORWARD VERDICT:", flush=True)
    print(json.dumps(selected, indent=2, default=safe), flush=True)
    print(f"\nCommon cached-data OOS cutoff UTC: {common_end.isoformat()}", flush=True)
    print(f"Artifacts written to {out.resolve()}", flush=True)


if __name__ == "__main__":
    main()
