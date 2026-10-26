#!/usr/bin/env python3
"""R333 raw Yahoo cache audit only. This script never calculates signals, trades, PnL or PF."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def locate_data_root(root: Path) -> Path:
    candidates = [root, root / "data-repo", root / "data"]
    for candidate in candidates:
        if (candidate / "data/r333/universe/yahoo_daily_acquisition_roster.csv").exists():
            return candidate
        if (candidate / "r333/universe/yahoo_daily_acquisition_roster.csv").exists():
            # An artifact may flatten the data/r333 prefix.
            return candidate.parent if candidate.name == "r333" else candidate
    raise FileNotFoundError(
        "Could not find data/r333/universe/yahoo_daily_acquisition_roster.csv under "
        + str(root)
    )


def invalid_ohlc_count(df: pd.DataFrame) -> int:
    cols = {str(c).strip().lower(): c for c in df.columns}
    required = ["open", "high", "low", "close"]
    if any(k not in cols for k in required):
        return len(df)
    o, h, l, c = [pd.to_numeric(df[cols[k]], errors="coerce") for k in required]
    bad = (
        o.isna() | h.isna() | l.isna() | c.isna()
        | (o < 0) | (h < 0) | (l < 0) | (c < 0)
        | (l > h) | (l > o) | (l > c)
        | (h < o) | (h < c)
    )
    return int(bad.sum())


def inspect_csv(path: Path, expected: dict[str, Any]) -> dict[str, Any]:
    raw_sha = sha256(path)
    df = pd.read_csv(path)
    datecol = next((c for c in df.columns if str(c).strip().lower() == "date"), None)
    if datecol is None:
        dates = pd.Series(pd.NaT, index=df.index)
    else:
        dates = pd.to_datetime(df[datecol], errors="coerce")
    duplicates = int(dates.duplicated(keep=False).sum())
    date_ordered = bool(dates.notna().all() and dates.is_monotonic_increasing)
    invalid = invalid_ohlc_count(df)
    fields = {str(c).strip().lower() for c in df.columns}
    required = {"date", "open", "high", "low", "close", "volume"}
    missing = sorted(required - fields)
    result = {
        "path": str(path),
        "rows_actual": int(len(df)),
        "rows_manifest": expected.get("row_count"),
        "row_count_matches": expected.get("row_count") == int(len(df)),
        "first_date_actual": None if dates.isna().all() else str(dates.min().date()),
        "first_date_manifest": expected.get("first_date"),
        "last_date_actual": None if dates.isna().all() else str(dates.max().date()),
        "last_date_manifest": expected.get("last_date"),
        "date_ordered": date_ordered,
        "bad_date_rows": int(dates.isna().sum()),
        "duplicate_date_rows": duplicates,
        "missing_required_fields": missing,
        "invalid_ohlc_rows_actual": invalid,
        "invalid_ohlc_rows_manifest": (expected.get("quality_summary") or {}).get("invalid_ohlc_rows"),
        "sha256_actual": raw_sha,
        "sha256_manifest": expected.get("sha256"),
        "sha256_matches": raw_sha == expected.get("sha256"),
        "dividend_event_rows": int((pd.to_numeric(df["Dividends"], errors="coerce").fillna(0) != 0).sum()) if "Dividends" in df else None,
        "split_event_rows": int((pd.to_numeric(df["Stock Splits"], errors="coerce").fillna(0) != 0).sum()) if "Stock Splits" in df else None,
    }
    result["file_integrity_pass"] = bool(
        result["row_count_matches"] and result["sha256_matches"]
        and not missing and date_ordered and duplicates == 0
        and result["bad_date_rows"] == 0
        and result["first_date_actual"] == result["first_date_manifest"]
        and result["last_date_actual"] == result["last_date_manifest"]
    )
    # Invalid OHLC is recorded as a separate quality failure, never silently repaired.
    result["ohlc_clean"] = invalid == 0
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, help="Extracted Actions artifact or data branch checkout root")
    parser.add_argument("--output", required=True, help="Output JSON path for the data-only audit")
    args = parser.parse_args()
    root = locate_data_root(Path(args.root).resolve())
    queue_path = root / "data/r333/universe/yahoo_daily_acquisition_roster.csv"
    batch_dir = root / "data/r333/manifests/yahoo_batches"
    csv_dir = root / "data/r333/yahoo_daily"
    if not queue_path.exists() or not batch_dir.exists():
        raise FileNotFoundError(f"Missing queue or manifest directory under {root}")

    with queue_path.open("r", newline="", encoding="utf-8-sig") as f:
        queue = list(csv.DictReader(f))
    queue_tickers = [row["yahoo_ticker"].strip() for row in queue if row.get("yahoo_ticker", "").strip()]
    queue_unique = len(set(queue_tickers)) == len(queue_tickers)

    batch_manifests = sorted(batch_dir.glob("batch_*.json"))
    ticker_records: dict[str, dict[str, Any]] = {}
    run_summaries = []
    duplicate_manifest_tickers = []
    for path in batch_manifests:
        manifest = json.loads(path.read_text(encoding="utf-8"))
        batch_results = manifest.get("ticker_results", [])
        succeeded = 0
        failed = 0
        for item in batch_results:
            ticker = item.get("ticker")
            if not ticker:
                continue
            if ticker in ticker_records:
                duplicate_manifest_tickers.append(ticker)
            # Most recent file ordering is not outcome-based; if duplicate acquisitions exist,
            # preserve every duplicate as a hard audit warning instead of choosing by PnL.
            ticker_records[ticker] = {
                **item,
                "manifest_path": str(path.relative_to(root)),
                "run_id": manifest.get("run_id"),
                "batch_index": manifest.get("batch_index_zero_based"),
                "overall_status": manifest.get("overall_status"),
            }
            if item.get("status") == "ACQUIRED_NEEDS_AUDIT":
                succeeded += 1
            else:
                failed += 1
        run_summaries.append({
            "manifest_path": str(path.relative_to(root)),
            "run_id": manifest.get("run_id"),
            "batch_index": manifest.get("batch_index_zero_based"),
            "overall_status": manifest.get("overall_status"),
            "requested": len(batch_results),
            "succeeded": succeeded,
            "failed": failed,
        })

    ticker_audits = []
    failed_tickers = []
    for ticker in queue_tickers:
        record = ticker_records.get(ticker)
        if record is None:
            failed_tickers.append({"ticker": ticker, "status": "NO_BATCH_MANIFEST"})
            continue
        if record.get("status") != "ACQUIRED_NEEDS_AUDIT":
            failed_tickers.append({
                "ticker": ticker, "status": record.get("status"),
                "failure_stage": record.get("failure_stage"),
                "attempts": record.get("attempts"),
            })
            continue
        csv_path = root / str(record.get("csv_path", ""))
        if not csv_path.exists():
            failed_tickers.append({
                "ticker": ticker, "status": "CSV_MISSING",
                "manifest_path": record.get("manifest_path"),
                "expected_path": record.get("csv_path"),
            })
            continue
        audit = inspect_csv(csv_path, record)
        audit["ticker"] = ticker
        audit["manifest_path"] = record.get("manifest_path")
        ticker_audits.append(audit)
        if not audit["file_integrity_pass"]:
            failed_tickers.append({
                "ticker": ticker,
                "status": "FILE_INTEGRITY_FAILURE",
                "audit": audit,
            })

    first_smoke = root / "data/r333/yahoo_daily/IDX_JKSE.csv"
    extra_baseline = None
    if first_smoke.exists():
        extra_baseline = {"ticker": "^JKSE", "path": str(first_smoke.relative_to(root)), "sha256": sha256(first_smoke), "role": "IHSG baseline; not part of IDX listing ticker queue"}

    invalid_rows = sum(x["invalid_ohlc_rows_actual"] for x in ticker_audits)
    file_integrity_failures = [x["ticker"] for x in ticker_audits if not x["file_integrity_pass"]]
    ohlc_dirty_tickers = [x["ticker"] for x in ticker_audits if not x["ohlc_clean"]]
    missing_tickers = sorted(set(queue_tickers) - set(ticker_records))
    output = {
        "experiment": "R333",
        "purpose": "cache integrity and raw OHLCV eligibility audit only; no signals, PnL, PF, alpha or universe ranking",
        "created_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "data_root": str(root),
        "verdict": "DATA_INADEQUATE",
        "alpha_verdict": "NOT_TESTED",
        "survivorship_label": "survivorship-biased",
        "queue": {
            "path": str(queue_path.relative_to(root)),
            "rows": len(queue_tickers),
            "unique_tickers": len(set(queue_tickers)),
            "duplicates": not queue_unique,
            "locked_expected_count": 962,
        },
        "batch_manifests": {
            "count": len(batch_manifests),
            "summary": run_summaries,
            "ticker_records": len(ticker_records),
            "duplicate_tickers_across_manifests": sorted(set(duplicate_manifest_tickers)),
        },
        "acquisition": {
            "queue_tickers_with_successful_csv_audit": len(ticker_audits),
            "missing_tickers": missing_tickers,
            "failed_tickers": failed_tickers,
            "file_integrity_failures": file_integrity_failures,
            "invalid_ohlc_rows_total": invalid_rows,
            "tickers_with_invalid_ohlc": ohlc_dirty_tickers,
            "files_with_clean_OHLC": sum(1 for x in ticker_audits if x["ohlc_clean"]),
            "rows_in_verified_csvs": sum(x["rows_actual"] for x in ticker_audits),
        },
        "files": ticker_audits,
        "additional_baseline": extra_baseline,
        "eligibility": {
            "raw_cache_integrity_pass": bool(
                len(ticker_audits) == len(queue_tickers)
                and not missing_tickers and not failed_tickers
                and not file_integrity_failures and queue_unique
            ),
            "OHLC_quality_pass": invalid_rows == 0,
            "delisted_history_verified": False,
            "point_in_time_shares_verified": False,
            "point_in_time_sectors_verified": False,
            "bid_ask_spread_observed": False,
            "historical_smallcap_universe_pass": False,
            "strategy_pnl_allowed": False,
        },
        "prohibited_claims": [
            "Do not call a survivor-only subset an unbiased IDX historical universe.",
            "Do not claim edge or no edge; alpha is NOT_TESTED.",
            "Do not run any PnL or strategy gates from this data-audit script.",
        ],
        "limitations": [
            "Only current IDX listing tickers are in the queue; no delisted ticker roster has been verified.",
            "Current listed shares and sectors are not historical point-in-time values.",
            "Yahoo daily OHLCV does not contain observed bid/ask spread or queue fill data.",
            "Broker live fee, slippage, spread/queue and ARA/ARB execution remain unverified in a real account.",
        ],
    }
    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "verdict": output["verdict"],
        "alpha_verdict": output["alpha_verdict"],
        "queue_tickers": len(queue_tickers),
        "verified_csvs": len(ticker_audits),
        "missing_or_failed": len(missing_tickers) + len(failed_tickers),
        "rows_verified": output["acquisition"]["rows_in_verified_csvs"],
        "invalid_ohlc_rows": invalid_rows,
        "raw_cache_integrity_pass": output["eligibility"]["raw_cache_integrity_pass"],
        "historical_smallcap_universe_pass": False,
        "pnl_calculated": False,
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
