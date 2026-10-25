#!/usr/bin/env python3
"""R331-A audit: compare unchanged scanner H1->H4 bars/signals with locked R191 M5->H4."""
from __future__ import annotations
import hashlib
import json
import os
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

# Reuse live scanner helpers exactly as committed; no scanner/state import side effects.
import scan
from research.R191_CANONICAL_index_trend_long import load as canonical_load
from research.r192_ger40 import parse_data

NY = "America/New_York"
CACHE_RUN_ID = 40166799441
CUTOFF = pd.Timestamp("2026-10-23T20:00:00Z")
START_NY = pd.Timestamp("2024-01-01 00:00:00", tz=NY)
INSTRUMENTS = ("usa500idxusd", "usatechidxusd")
EXPECTED_CACHE = {
    "usa500idxusd": {
        "sha256": "75d3c8dd64ba4647af7f5376ac219010dc2c65f46beb296f978257e770c90087",
        "bytes": 11805722,
    },
    "usatechidxusd": {
        "sha256": "b8f3b267e187669890f455486100133a29a78b5b5fcb4824c67d2b8f3acb8755",
        "bytes": 13248558,
    },
}
M5_DIR = ROOT / "dl" / "r330_m5"
TEMP_DIR = ROOT / "dl" / "r331a_m5_cut"
RESULT_JSON = ROOT / "research" / "R331A_results.json"
RESULT_MD = ROOT / "research" / "R331A_results.md"
CANONICAL_GIT_BLOB = "39935852a06730b87b50252ddc89c91b3cb6ee44"
SCAN_GIT_BLOB = "ed912fae254acc6d790e833f991a4d78db555e73"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def rounded_or_none(value, digits=8):
    if pd.isna(value):
        return None
    return round(float(value), digits)


def label_ny(index_value) -> str:
    return pd.Timestamp(index_value).tz_convert(NY).isoformat()


def enrich(h4: pd.DataFrame) -> pd.DataFrame:
    out = h4.copy()
    out["high_55"] = out["high"].shift(1).rolling(window=55, min_periods=55).max()
    out["close_minus_high55"] = out["close"] - out["high_55"]
    out["raw_signal"] = out["high_55"].notna() & (out["close"] > out["high_55"])
    return out


def eligible_detail_map(h4: pd.DataFrame, complete_mask) -> dict:
    details = {}
    utc_labels = pd.DatetimeIndex(h4.index).tz_convert("UTC")
    starts_ny = pd.DatetimeIndex(h4.index).tz_convert(NY)
    for i, (_, row) in enumerate(h4.iterrows()):
        ts_utc = utc_labels[i]
        if starts_ny[i] < START_NY or ts_utc > CUTOFF:
            continue
        eligible = bool(complete_mask[i])
        key = ts_utc.isoformat()
        details[key] = {
            "timestamp_ny": starts_ny[i].isoformat(),
            "eligible_completed_bar": eligible,
            "signal": (bool(row["raw_signal"]) if eligible else None),
            "close": rounded_or_none(row["close"]),
            "high_55_previous": rounded_or_none(row["high_55"]),
            "close_minus_high55": rounded_or_none(row["close_minus_high55"]),
        }
    return details


def evaluate_instrument(inst: str) -> dict:
    cache_file = M5_DIR / f"{inst}_m5.csv.gz"
    if not cache_file.is_file():
        raise FileNotFoundError(f"R330 M5 artifact missing: {cache_file}")
    actual_bytes = cache_file.stat().st_size
    actual_sha = sha256_file(cache_file)
    expect = EXPECTED_CACHE[inst]
    if actual_bytes != expect["bytes"] or actual_sha != expect["sha256"]:
        raise RuntimeError(
            f"R330 cache identity mismatch for {inst}: bytes={actual_bytes}, sha256={actual_sha}; "
            f"expected bytes={expect['bytes']}, sha256={expect['sha256']}"
        )

    # Validate original R330 cache, then clip a working copy at the locked cutoff.
    m5_full, m5_duplicates = parse_data(cache_file)
    m5_utc = m5_full.index.tz_convert("UTC")
    m5_cut = m5_full.loc[m5_utc <= CUTOFF].copy()
    if m5_cut.empty:
        raise RuntimeError(f"No M5 rows at/before locked cutoff for {inst}")
    TEMP_DIR.mkdir(parents=True, exist_ok=True)
    m5_cut_file = TEMP_DIR / f"{inst}_m5.csv.gz"
    export = m5_cut[["open", "high", "low", "close"]].reset_index(drop=True)
    export.insert(0, "timestamp", m5_cut.index.tz_convert("UTC").astype(str).to_numpy())
    export.to_csv(m5_cut_file, index=False, compression="gzip")

    # scan.fetch_h1() stays unchanged. A temporary in-memory historical position anchor
    # extends its normal recent-45-day lookback to 2023-12-13 for 55-bar warm-up.
    # This does not read or write state.json; the first evaluated NY label is 2024-01-01.
    h1 = scan.fetch_h1(inst, {"position": {"entry_time_utc": "2023-12-15T00:00:00Z"}})
    h1_rows_downloaded = int(len(h1))
    h1 = h1.loc[h1.index.tz_convert("UTC") <= CUTOFF].copy()
    if h1.empty:
        raise RuntimeError(f"H1 download has no rows at/before cutoff for {inst}")
    h4_a_raw = scan.to_h4(h1)  # unchanged scanner implementation
    h4_b_raw = canonical_load(str(TEMP_DIR), inst)  # unchanged R191 canonical M5 resample
    if h4_a_raw.empty or h4_b_raw.empty:
        raise RuntimeError(f"Empty H4 series for {inst}: H1-derived={len(h4_a_raw)}, M5-derived={len(h4_b_raw)}")

    h4_a = enrich(h4_a_raw)
    h4_b = enrich(h4_b_raw)

    a_close_utc = pd.to_datetime(h4_a["bar_close_utc"], utc=True)
    a_complete = (a_close_utc <= CUTOFF).to_numpy(dtype=bool)
    # The canonical pandas 4h resample has fixed 4-elapsed-hour bins.
    b_close_utc = pd.DatetimeIndex(h4_b.index).tz_convert("UTC") + pd.Timedelta(hours=4)
    b_complete = (b_close_utc <= CUTOFF)

    a_idx_ny = pd.DatetimeIndex(h4_a.index).tz_convert(NY)
    b_idx_ny = pd.DatetimeIndex(h4_b.index).tz_convert(NY)
    a_eval = (a_idx_ny >= START_NY) & a_complete
    b_eval = (b_idx_ny >= START_NY) & b_complete

    a_cmp = h4_a.loc[a_eval, ["open", "high", "low", "close"]].copy()
    b_cmp = h4_b.loc[b_eval, ["open", "high", "low", "close"]].copy()
    a_cmp.index = pd.DatetimeIndex(a_cmp.index).tz_convert("UTC")
    b_cmp.index = pd.DatetimeIndex(b_cmp.index).tz_convert("UTC")
    a_labels, b_labels = set(a_cmp.index), set(b_cmp.index)
    shared = sorted(a_labels & b_labels)
    a_only = sorted(a_labels - b_labels)
    b_only = sorted(b_labels - a_labels)

    per_col = {}
    all_diffs = []
    for col in ("open", "high", "low", "close"):
        if shared:
            diffs = (a_cmp.loc[shared, col] - b_cmp.loc[shared, col]).abs()
            maximum = float(diffs.max())
            gt_half = int((diffs > 0.5).sum())
            all_diffs.extend(diffs.astype(float).tolist())
        else:
            maximum = None
            gt_half = 0
        per_col[col] = {
            "bars_abs_diff_gt_0_5": gt_half,
            "max_abs_diff_points": None if maximum is None else round(maximum, 8),
        }

    detail_a = eligible_detail_map(h4_a, a_complete)
    detail_b = eligible_detail_map(h4_b, b_complete)
    signal_a = {key for key, rec in detail_a.items() if rec["eligible_completed_bar"] and rec["signal"] is True}
    signal_b = {key for key, rec in detail_b.items() if rec["eligible_completed_bar"] and rec["signal"] is True}
    mismatch_keys = sorted(signal_a ^ signal_b, key=lambda key: pd.Timestamp(key))
    union_signals = signal_a | signal_b

    mismatches = []
    for key in mismatch_keys:
        da, db = detail_a.get(key), detail_b.get(key)
        present = da or db
        mismatches.append({
            "timestamp_utc": key,
            "timestamp_ny": present["timestamp_ny"] if present else None,
            "A_H1_to_H4": da,
            "B_M5_canonical": db,
        })

    return {
        "instrument": inst,
        "m5_cache": {
            "artifact_run_id": CACHE_RUN_ID,
            "file": cache_file.name,
            "bytes": actual_bytes,
            "sha256": actual_sha,
            "source_rows_after_parse": int(len(m5_full)),
            "duplicates_removed_by_parser": int(m5_duplicates),
            "source_last_timestamp_utc": m5_full.index[-1].tz_convert("UTC").isoformat(),
            "rows_at_or_before_cutoff": int(len(m5_cut)),
            "last_timestamp_used_utc": m5_cut.index[-1].tz_convert("UTC").isoformat(),
            "cutoff_utc": CUTOFF.isoformat(),
        },
        "h1_source": {
            "downloaded_rows_before_cutoff": h1_rows_downloaded,
            "rows_at_or_before_cutoff": int(len(h1)),
            "first_timestamp_utc_used": h1.index[0].tz_convert("UTC").isoformat(),
            "last_timestamp_utc_used": h1.index[-1].tz_convert("UTC").isoformat(),
            "warmup_start_ny": label_ny(h4_a.index[0]),
        },
        "h4_bars": {
            "A_H1_to_H4_completed_in_period": int(len(a_cmp)),
            "B_M5_canonical_completed_in_period": int(len(b_cmp)),
            "same_timestamp_labels_compared": int(len(shared)),
            "labels_only_in_A": int(len(a_only)),
            "labels_only_in_B": int(len(b_only)),
            "labels_only_in_A_first_10_ny": [label_ny(x) for x in a_only[:10]],
            "labels_only_in_B_first_10_ny": [label_ny(x) for x in b_only[:10]],
            "ohlc_diagnostics_on_same_timestamp_labels_only": {
                "common_labels": int(len(shared)),
                "columns": per_col,
                "max_abs_ohlc_diff_points_overall": None if not all_diffs else round(max(all_diffs), 8),
            },
        },
        "signals": {
            "A_signal_count": int(len(signal_a)),
            "B_signal_count": int(len(signal_b)),
            "mismatch_bar_count_symmetric_difference": int(len(mismatch_keys)),
            "union_of_signal_labels": int(len(union_signals)),
            "mismatch_pct_of_union_signals": (
                0.0 if not union_signals else round(100.0 * len(mismatch_keys) / len(union_signals), 6)
            ),
            "mismatch_pct_of_combined_signal_counts": (
                0.0 if not (len(signal_a) + len(signal_b))
                else round(100.0 * len(mismatch_keys) / (len(signal_a) + len(signal_b)), 6)
            ),
            "signal_sets_identical": len(mismatch_keys) == 0,
            "mismatch_bars": mismatches,
        },
    }


def write_report(result: dict) -> None:
    RESULT_JSON.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# R331-A — audit scanner H1→H4 vs canonical M5→H4",
        "",
        f"**Verdict: {result.get('status', 'INCOMPLETE')}**",
        "",
        f"- R330 cache run: {CACHE_RUN_ID}; cutoff: {CUTOFF.isoformat()}.",
        "- Evaluation labels: NY timestamp >= 2024-01-01 00:00; completed H4 bars only.",
        "- Signal rule unchanged: close > max(high of previous 55 H4 bars); no position simulation, tuning, or rule changes.",
        "- A uses scan.fetch_h1() and scan.to_h4() imported unchanged from scan.py; an in-memory historical position anchor extends H1 download for warm-up without touching state.json.",
        "- B uses the unchanged R191 canonical script copied from R330 and the exact R330 M5 cache, clipped only at the locked cutoff before canonical resampling.",
        "- OHLC differences are computed only on identical UTC instants / NY labels present and completed in both series; label-only bars are counted separately.",
        "",
    ]
    if result.get("status") == "INCOMPLETE":
        lines += [f"**Error:** {result.get('error', 'unknown')}", ""]
        RESULT_MD.write_text("\n".join(lines), encoding="utf-8")
        return
    lines += [
        "## Ringkasan",
        "",
        "| Instrumen | H4 A | H4 B | Label sama dibandingkan | Hanya A | Hanya B | Sinyal A | Sinyal B | Mismatch | Mismatch / union |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for inst in INSTRUMENTS:
        r = result["instruments"][inst]
        h, s = r["h4_bars"], r["signals"]
        lines.append(
            f"| {inst} | {h['A_H1_to_H4_completed_in_period']} | {h['B_M5_canonical_completed_in_period']} | "
            f"{h['same_timestamp_labels_compared']} | {h['labels_only_in_A']} | {h['labels_only_in_B']} | "
            f"{s['A_signal_count']} | {s['B_signal_count']} | {s['mismatch_bar_count_symmetric_difference']} | "
            f"{s['mismatch_pct_of_union_signals']:.3f}% |"
        )
    lines += ["", "## Diagnostik OHLC pada label yang sama", "",
              "| Instrumen | Kolom | Bar dengan |Δ| > 0.5 poin | Maks. |", "|---|---|---:|---:|"]
    for inst in INSTRUMENTS:
        cols = result["instruments"][inst]["h4_bars"]["ohlc_diagnostics_on_same_timestamp_labels_only"]["columns"]
        for col in ("open", "high", "low", "close"):
            d = cols[col]
            mx = "NA" if d["max_abs_diff_points"] is None else f"{d['max_abs_diff_points']:.6f}"
            lines.append(f"| {inst} | {col.upper()} | {d['bars_abs_diff_gt_0_5']} | {mx} |")
    for inst in INSTRUMENTS:
        signals = result["instruments"][inst]["signals"]
        lines += ["", f"## Daftar bar sinyal mismatch — {inst}", ""]
        if not signals["mismatch_bars"]:
            lines.append("Tidak ada mismatch.")
            continue
        lines += [
            "| Label NY (offset disertakan) | Sinyal A | Close−high55 A | Sinyal B | Close−high55 B |",
            "|---|---:|---:|---:|---:|",
        ]
        for row in signals["mismatch_bars"]:
            da, db = row["A_H1_to_H4"], row["B_M5_canonical"]
            sa = "NA" if da is None or da["signal"] is None else ("true" if da["signal"] else "false")
            sb = "NA" if db is None or db["signal"] is None else ("true" if db["signal"] else "false")
            va = "NA" if da is None or da["close_minus_high55"] is None else f"{da['close_minus_high55']:+.6f}"
            vb = "NA" if db is None or db["close_minus_high55"] is None else f"{db['close_minus_high55']:+.6f}"
            lines.append(f"| {row['timestamp_ny']} | {sa} | {va} | {sb} | {vb} |")
    lines += ["", "## Kriteria", "",
              "PASS hanya bila himpunan label sinyal A dan B identik untuk kedua instrumen (0 mismatch).",
              f"Hasil audit: **{result['status']}**.", ""]
    RESULT_MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    try:
        results = {inst: evaluate_instrument(inst) for inst in INSTRUMENTS}
        status = "PASS" if all(r["signals"]["signal_sets_identical"] for r in results.values()) else "FAIL"
        report = {
            "experiment": "R331-A",
            "status": status,
            "cache_artifact_run_id": CACHE_RUN_ID,
            "cache_cutoff_utc": CUTOFF.isoformat(),
            "evaluation_start_label_ny": START_NY.isoformat(),
            "signal_rule": "close > max(high of previous 55 H4 bars)",
            "acceptance_criteria": "PASS iff signal-label sets are identical for both instruments and mismatch count is zero.",
            "scanner_source": {"path": "scan.py", "source_git_blob_sha": SCAN_GIT_BLOB,
                               "to_h4": "imported unchanged", "fetch_h1": "imported unchanged"},
            "canonical_source": {"path": "research/R191_CANONICAL_index_trend_long.py",
                                 "source_r330_git_blob_sha": CANONICAL_GIT_BLOB,
                                 "load": "imported unchanged"},
            "instruments": results,
        }
        write_report(report)
        return 0 if status == "PASS" else 1
    except Exception as exc:
        report = {
            "experiment": "R331-A",
            "status": "INCOMPLETE",
            "cache_artifact_run_id": CACHE_RUN_ID,
            "cache_cutoff_utc": CUTOFF.isoformat(),
            "evaluation_start_label_ny": START_NY.isoformat(),
            "error": f"{type(exc).__name__}: {exc}",
            "note": "No PASS/FAIL verdict is assigned without completing both instrument audits.",
        }
        write_report(report)
        print(f"R331-A INCOMPLETE: {report['error']}", file=sys.stderr, flush=True)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
