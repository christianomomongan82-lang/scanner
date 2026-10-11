#!/usr/bin/env python3
"""R204: test UTC-anchored H4 bars for the locked R191 signal across ten indices.

This is a single bar-construction robustness test, not a parameter sweep. Signal,
stop, target, entry, costs, selection, and validation gates remain locked from R204.
Only complete UTC H4 bins made of four consecutive source H1 bars are retained.
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

CFG = {"id": "R204_UTC_H4_BASE_55_27", "role": "locked_baseline_utc_h4",
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

    common_end = min(observed_ends.values())
    for inst, name in ASSETS.items():
        h4, m5 = parsed[inst]
        observed_end = min(observed_ends[inst], common_end)
        for mode in ("ideal", "manual5m"):
            trades, sim_diag = simulate(h4, m5, CFG, mode)
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
        "research": "R204: locked R191 baseline across ten indices; no parameter optimization",
        "run_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "snapshot_note": "All results use the same cached Dukascopy BID H1/M5 snapshot. Re-runs reuse that snapshot instead of redownloading; change the cache schema version deliberately to refresh.",
        "locked_rule": {
            "h4_anchor": "UTC 00/04/08/12/16/20; retain only bins with four consecutive H1 source bars",
            "direction": "long only",
            "signal": "H4 close > maximum high of prior 55 completed H4 bars",
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
    print("\nR204 RANKING: manual5m sorted by discovery closed-trade count (cost 1bp/2bp):", flush=True)
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
