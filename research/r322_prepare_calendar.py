#!/usr/bin/env python3
"""Data-only R322 calendar filter. This script never computes trading signals or PnL."""
from __future__ import annotations
import argparse, csv, hashlib, json
from datetime import datetime, timezone
from pathlib import Path

SOURCE_URL = "https://huggingface.co/datasets/Ehsanrs2/Forex_Factory_Calendar/resolve/main/forex_factory_cache.csv"
EXPECTED_SHA256 = "f4e92bca4168cfe6e4598d3d2a69ac933dfd6c7c94550e056498a418e3efaf5e"
START = datetime(2016, 1, 1, tzinfo=timezone.utc)
END = datetime(2025, 4, 8, tzinfo=timezone.utc)  # exclusive
OUT_FIELDS = ["DateTime", "Currency", "Impact", "Event", "source_row_index"]

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def parse_datetime(value: str):
    v = (value or "").strip()
    if not v:
        return None
    try:
        d = datetime.fromisoformat(v.replace("Z", "+00:00"))
    except ValueError:
        return None
    if d.tzinfo is None:
        return None
    return d.astimezone(timezone.utc)

def norm_row(row):
    return {(k or "").replace("\ufeff", "").strip().lower(): (v or "").strip()
            for k, v in row.items() if k is not None}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    if not args.input.is_file():
        raise FileNotFoundError(args.input)
    source_hash = sha256_file(args.input)
    if source_hash != EXPECTED_SHA256:
        raise SystemExit(f"FAIL_CLOSED: source SHA-256 mismatch: {source_hash}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    out_csv = args.output_dir / "R322_USD_HIGH_IMPACT_CALENDAR.csv"
    source_rows = selected = invalid_timestamp = outside_window = 0
    min_dt = max_dt = None
    impacts_seen = set()
    with args.input.open("r", encoding="utf-8-sig", newline="") as src, out_csv.open("w", encoding="utf-8", newline="") as dst:
        reader = csv.DictReader(src)
        if not reader.fieldnames:
            raise SystemExit("FAIL_CLOSED: source CSV has no header")
        header_set = {h.replace("\ufeff", "").strip().lower() for h in reader.fieldnames if h}
        required = {"datetime", "currency", "impact", "event"}
        if not required.issubset(header_set):
            raise SystemExit(f"FAIL_CLOSED: missing required columns; found {sorted(header_set)}")
        writer = csv.DictWriter(dst, fieldnames=OUT_FIELDS, lineterminator="\n")
        writer.writeheader()
        for i, raw in enumerate(reader, start=2):
            source_rows += 1
            row = norm_row(raw)
            currency = row.get("currency", "").upper()
            impact_raw = row.get("impact", "").strip()
            impact = impact_raw.lower()
            is_high = impact in {"high", "high impact", "high impact expected", "3", "3.0"}
            if currency != "USD" or not is_high:
                continue
            dt = parse_datetime(row.get("datetime", ""))
            if dt is None:
                invalid_timestamp += 1
                # Keep malformed high-impact USD row so local preflight can decide and record.
                writer.writerow({"DateTime": row.get("datetime", ""), "Currency": currency,
                                 "Impact": impact_raw, "Event": row.get("event", ""),
                                 "source_row_index": i})
                selected += 1
                impacts_seen.add(impact_raw)
                continue
            if not (START <= dt < END):
                outside_window += 1
                continue
            writer.writerow({"DateTime": row.get("datetime", ""), "Currency": currency,
                             "Impact": impact_raw, "Event": row.get("event", ""),
                             "source_row_index": i})
            selected += 1
            impacts_seen.add(impact_raw)
            if min_dt is None or dt < min_dt:
                min_dt = dt
            if max_dt is None or dt > max_dt:
                max_dt = dt

    manifest = {
        "type": "data-only; no signals or PnL calculated",
        "source_url": SOURCE_URL,
        "source_sha256_verified": source_hash,
        "source_bytes": args.input.stat().st_size,
        "source_data_rows": source_rows,
        "currency_filter": "USD",
        "impact_filter": ["High", "High Impact Expected", "numeric 3"],
        "retained_usd_high_rows": selected,
        "invalid_timezone_or_timestamp_rows_retained_for_audit": invalid_timestamp,
        "valid_rows_outside_locked_study_window_omitted": outside_window,
        "locked_window_start_utc_inclusive": START.isoformat(),
        "locked_window_end_utc_exclusive": END.isoformat(),
        "valid_retained_timestamp_min_utc": min_dt.isoformat() if min_dt else None,
        "valid_retained_timestamp_max_utc": max_dt.isoformat() if max_dt else None,
        "impact_values_retained": sorted(impacts_seen),
        "filtered_csv": out_csv.name,
        "filtered_csv_bytes": out_csv.stat().st_size,
        "filtered_csv_sha256": sha256_file(out_csv),
        "note": "Actual, forecast, previous and revised values are intentionally not exported. Calendar rows are external schedule metadata, not a claim that the market received unrevised point-in-time data."
    }
    (args.output_dir / "R322_CALENDAR_SOURCE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
