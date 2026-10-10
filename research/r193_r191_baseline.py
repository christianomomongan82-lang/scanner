#!/usr/bin/env python3
"""R193: revalidate the locked R191 breakout baseline on USA500 and USATECH."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import numpy as np
import pandas as pd
import sys

# Direct script execution puts research/ rather than the repository root on sys.path.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from research.r192_ger40 import (
    parse_data, build_h4, signals_and_stops, truncation_gate, simulate,
    metric, annual_rows, annual_cohort_rows, safe, PERIODS,
)

CFG = {"id": "R191_BASE_55_27", "role": "locked_baseline", "breakout": 55, "stop_bars": 27}
ASSETS = {
    "usa500idxusd": "USA500/S&P 500",
    "usatechidxusd": "USATECH/Nasdaq 100",
}
RR = 2.0

def phase_metrics(trades, observed_end):
    out = {}
    spans = {
        "history_2016_2025": (pd.Timestamp("2016-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")),
        "discovery_2017_2021": PERIODS["discovery"],
        "forward_2022_2025": PERIODS["forward"],
        "oos_2026_to_data_end": (PERIODS["oos2026"][0], observed_end),
    }
    for phase, (start, end) in spans.items():
        for bps in (1, 2):
            m = metric(trades, start, end, bps)
            out[f"{phase}_entries"] = m["entries"]
            out[f"{phase}_closed"] = m["n"]
            out[f"{phase}_censored"] = m["censored"]
            out[f"{phase}_pf_{bps}bp"] = m["pf"]
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="dl")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    data_dir, out = Path(args.data_dir), Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    reports, trade_sets, annual, cohorts, all_trades, asset_meta = [], {}, [], [], [], {}
    gates = {}
    parsed = {}
    for inst, name in ASSETS.items():
        h1_path = data_dir / f"{inst}_h1.csv"
        m5_path = data_dir / f"{inst}_m5.csv"
        h1, h1_dups = parse_data(h1_path)
        m5, m5_dups = parse_data(m5_path)
        now = pd.Timestamp.now(tz="UTC")
        h4, diag = build_h4(h1, now)
        sig, stops = signals_and_stops(h4, CFG)
        gate = truncation_gate(h4, CFG, sig, stops)
        gates[inst] = gate
        if not gate["pass"]:
            raise SystemExit(f"HARD STOP: truncation gate failed for {inst}: {gate}")
        flat_m5 = int(((m5.open == m5.high) & (m5.high == m5.low) & (m5.low == m5.close)).sum())
        asset_meta[inst] = {
            "name": name, "h1_rows": len(h1), "h1_duplicates_removed": h1_dups,
            "m5_rows": len(m5), "m5_duplicates_removed": m5_dups,
            "h1_start_utc": h1.index[0].tz_convert("UTC").isoformat(),
            "h1_end_utc": h1.index[-1].tz_convert("UTC").isoformat(),
            "m5_start_utc": m5.index[0].tz_convert("UTC").isoformat(),
            "m5_end_utc": m5.index[-1].tz_convert("UTC").isoformat(),
            "m5_flat_rows": flat_m5, **diag,
        }
        parsed[inst] = (h4, m5)
        print(f"TRUNCATION GATE PASS {inst}: checked {gate['checked']} completed H4 prefixes.", flush=True)

    # Use a common observation cutoff so the two index OOS samples are comparable.
    observed_ends = {
        inst: m5.index[-1].tz_convert("UTC") + pd.Timedelta(minutes=5)
        for inst, (_, m5) in parsed.items()
    }
    common_end = min(observed_ends.values())
    config_frame = pd.DataFrame([CFG])
    for inst, name in ASSETS.items():
        h4, m5 = parsed[inst]
        inst_trades = []
        for mode in ("ideal", "manual5m"):
            trades, sim_diag = simulate(h4, m5, CFG, mode)
            for t in trades:
                t["instrument"] = inst
                t["instrument_name"] = name
                inst_trades.append(t)
            end = min(observed_ends[inst], common_end)
            row = {"instrument": inst, "instrument_name": name, "mode": mode,
                   "breakout": CFG["breakout"], "stop_bars": CFG["stop_bars"],
                   "signals": sim_diag["signals"], "taken": sim_diag["taken"],
                   "skipped_active": sim_diag["skipped_active"],
                   "skipped_no_tradable_fill": sim_diag["skipped_no_tradable_fill"],
                   "skipped_invalid_risk": sim_diag["skipped_invalid_risk"]}
            row.update(phase_metrics(trades, end))
            reports.append(row)
            annual.extend([{**r, "instrument": inst, "instrument_name": name}
                           for r in annual_rows(trades, CFG, mode, end)])
            cohorts.extend([{**r, "instrument": inst, "instrument_name": name}
                            for r in annual_cohort_rows(trades, CFG, mode, end)])
            trade_sets[(inst, mode)] = [t for t in trades]
        all_trades.extend(inst_trades)

    # Combined portfolio is the union of each instrument's independently simulated,
    # single-open-position-per-instrument stream. Trade returns are risk-normalized in R.
    for mode in ("ideal", "manual5m"):
        combined = []
        for inst in ASSETS:
            combined.extend(trade_sets[(inst, mode)])
        row = {"instrument": "COMBINED", "instrument_name": "USA500 + USATECH", "mode": mode,
               "breakout": CFG["breakout"], "stop_bars": CFG["stop_bars"]}
        row.update(phase_metrics(combined, common_end))
        reports.append(row)
        annual.extend([{**r, "instrument": "COMBINED", "instrument_name": "USA500 + USATECH"}
                       for r in annual_rows(combined, CFG, mode, common_end)])
        cohorts.extend([{**r, "instrument": "COMBINED", "instrument_name": "USA500 + USATECH"}
                        for r in annual_cohort_rows(combined, CFG, mode, common_end)])

    meta = {
        "research": "R193: R191 baseline revalidation only; no parameter search",
        "commit_purpose": "Verify corrected New York wall-clock H4 construction across USA500 and USATECH",
        "run_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "locked_rule": {"breakout": "H4 close > maximum high of prior 55 completed H4 bars",
                        "stop": "lowest low over the signal bar and preceding 26 bars (27 inclusive)",
                        "target": "entry + 2R", "direction": "long only",
                        "entry_modes": {"ideal": "open of next H4 bar",
                                        "manual5m": "first non-flat M5 bar at or after signal close + 5 minutes, before the next actual NY wall-clock H4 close"},
                        "exit": "M5 BID OHLC, SL checked before TP, gap through SL fills at open; no time stop",
                        "cost_model": "1bp and 2bp round-trip, cost price = entry * bps / 10000"},
        "periods": {"history": "2016-01-01 <= entry < 2026-01-01; exits before 2026-01-01",
                    "discovery": "entries 2017-2021; outcomes closed before 2022-01-01",
                    "forward": "entries 2022-2025; outcomes closed before 2026-01-01",
                    "oos": "entries in 2026, outcomes only through common data cutoff"},
        "common_oos_cutoff_utc": common_end.isoformat(),
        "assets": asset_meta, "truncation_gates": gates,
        "assumptions": ["H1 signal data and M5 entry/exit data are Dukascopy BID.",
                        "Existing flat H1/H4 bars are retained; no forward-fill.",
                        "Synthetic flat M5 rows are skipped for manual entry/exit.",
                        "Instrument positions are simulated independently; combined metrics pool completed risk-normalized R outcomes.",
                        "Modeled bps cost is not a substitute for measured live slippage or broker-specific fees."],
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=safe), encoding="utf-8")
    pd.DataFrame(reports).to_csv(out / "baseline_ledger.csv", index=False)
    pd.DataFrame(annual).to_csv(out / "annual.csv", index=False)
    pd.DataFrame(cohorts).to_csv(out / "annual_cohort.csv", index=False)
    pd.DataFrame(all_trades).to_csv(out / "trades.csv", index=False)

    ledger = pd.DataFrame(reports)
    show_cols = ["instrument", "mode", "history_2016_2025_closed", "history_2016_2025_pf_1bp",
                 "history_2016_2025_pf_2bp", "discovery_2017_2021_closed",
                 "discovery_2017_2021_pf_1bp", "discovery_2017_2021_pf_2bp",
                 "forward_2022_2025_closed", "forward_2022_2025_pf_1bp",
                 "forward_2022_2025_pf_2bp", "oos_2026_to_data_end_closed",
                 "oos_2026_to_data_end_pf_1bp", "oos_2026_to_data_end_pf_2bp"]
    print("\nR193 BASELINE LEDGER (1bp/2bp modeled round-trip cost):", flush=True)
    print(ledger[show_cols].to_string(index=False), flush=True)
    print("\nForward entry-year cohorts, manual5m, cost 1bp:", flush=True)
    coh = pd.DataFrame(cohorts)
    print(coh[(coh["mode"] == "manual5m") & (coh["cost_bps_rt"] == 1) &
              (coh["entry_year"].between(2022, 2025))][
        ["instrument", "entry_year", "entries", "n_closed_by_cutoff",
         "censored_by_cutoff", "pf_entry_cohort"]].to_string(index=False), flush=True)
    print(f"Artifacts written to {out.resolve()}", flush=True)

if __name__ == "__main__":
    main()
