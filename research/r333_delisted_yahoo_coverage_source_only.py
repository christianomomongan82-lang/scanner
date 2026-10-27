#!/usr/bin/env python3
"""R333 delisted-issuer Yahoo historical price availability audit only. Never computes strategy PnL."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import logging
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

MAX_ATTEMPTS = 5
WAIT_SECONDS = [30, 120, 600, 600]
RETRY_TOKENS = (
    "429", "too many requests", "rate limit", "ratelimit",
    "timed out", "timeout", "connection reset", "connection aborted",
    "temporarily unavailable", "http 500", "http 502", "http 503", "http 504",
    "curl: (",
)


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_date(value: str, field: str) -> pd.Timestamp:
    date = pd.to_datetime(value, dayfirst=True, format="mixed", errors="coerce")
    if pd.isna(date):
        raise SystemExit(f"INVALID_EVENT_DATE: field={field!r} value={value!r}")
    return pd.Timestamp(date).normalize()


def safe_slug(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_") or "ticker"


def flatten_columns(frame: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(frame.columns, pd.MultiIndex):
        return frame
    known = {"Open", "High", "Low", "Close", "Adj Close", "Volume", "Dividends", "Stock Splits", "Capital Gains"}
    out = frame.copy()
    columns = []
    for col in frame.columns.to_list():
        parts = [str(x) for x in (col if isinstance(col, tuple) else (col,))]
        found = [x for x in parts if x in known]
        columns.append(found[0] if found else "_".join(parts))
    out.columns = columns
    return out


def valid_ohlc(frame: pd.DataFrame) -> pd.Series:
    col = {str(x).strip().lower(): x for x in frame.columns}
    required = ("open", "high", "low", "close")
    if any(x not in col for x in required):
        return pd.Series(False, index=frame.index)
    op, hi, lo, cl = [pd.to_numeric(frame[col[x]], errors="coerce") for x in required]
    return (
        op.notna() & hi.notna() & lo.notna() & cl.notna()
        & (op >= 0) & (hi >= 0) & (lo >= 0) & (cl >= 0)
        & (lo <= hi) & (lo <= op) & (lo <= cl)
        & (hi >= op) & (hi >= cl)
    )


def output(key: str, value: str) -> None:
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as handle:
            handle.write(f"{key}={value}\n")
    print(f"R333_{key.upper()}={value}", flush=True)


def main() -> int:
    data_root = Path(os.environ["R333_DATA_ROOT"]).resolve()
    request_path = Path(os.environ["R333_REQUEST_PATH"]).resolve()
    request = json.loads(request_path.read_text(encoding="utf-8"))
    if request.get("data_only") is not True or request.get("pnl_calculation") is not False:
        raise SystemExit("REQUEST_POLICY_REJECTED: only Yahoo historical price availability checks are permitted.")
    if request.get("source") != "Yahoo Finance via yfinance":
        raise SystemExit("SOURCE_POLICY_REJECTED: expected Yahoo Finance via yfinance.")

    event_path = data_root / str(request["events_csv_path"])
    if not event_path.exists():
        raise SystemExit(f"DELISTED_EVENTS_CSV_NOT_FOUND: {event_path}")
    event_bytes = event_path.read_bytes()
    event_sha = sha(event_bytes)
    expected_event_sha = str(request["events_csv_sha256"])
    if event_sha != expected_event_sha:
        raise SystemExit(f"EVENT_CSV_SHA256_MISMATCH: expected={expected_event_sha} actual={event_sha}")

    with event_path.open("r", newline="", encoding="utf-8-sig") as handle:
        events = list(csv.DictReader(handle))
    if len(events) != int(request["expected_event_rows"]):
        raise SystemExit(f"EVENT_ROW_COUNT_MISMATCH: expected={request['expected_event_rows']} actual={len(events)}")
    codes = [str(x.get("code", "")).strip() for x in events]
    if any(not x for x in codes) or len(set(codes)) != len(codes):
        raise SystemExit(f"EVENT_CODE_INTEGRITY_FAILURE: rows={len(codes)} unique={len(set(codes))}")
    if len(events) != 65:
        raise SystemExit(f"LOCKED_R333_EXPECTATION_FAILURE: expected 65 events, got {len(events)}")

    run_id = str(os.environ.get("GITHUB_RUN_ID", "local"))
    run_attempt = str(os.environ.get("GITHUB_RUN_ATTEMPT", "1"))
    start_date = str(request.get("history_start_date", "1970-01-01"))
    near_days = int(request.get("near_delisting_calendar_days", 30))
    if near_days != 30:
        raise SystemExit(f"NEAR_WINDOW_POLICY_REJECTED: expected 30 calendar days, got {near_days}")

    out_dir = data_root / "data/r333/yahoo_delisted_daily"
    out_dir.mkdir(parents=True, exist_ok=True)
    started = now()
    results: list[dict[str, Any]] = []
    logger = logging.getLogger("yfinance")
    prev_level = logger.level
    logger.setLevel(logging.DEBUG)

    for idx, event in enumerate(events, start=1):
        code = str(event["code"]).strip()
        ticker = str(request.get("ticker_suffix", ".JK"))
        ticker = code + ticker
        listing_date = parse_date(str(event.get("ListingDate", "")), "ListingDate")
        delisting_date = parse_date(str(event.get("DeListingDate", "")), "DeListingDate")
        record: dict[str, Any] = {
            "code": code,
            "ticker": ticker,
            "issuer_name": str(event.get("issuerName", "")),
            "listing_date": listing_date.strftime("%Y-%m-%d"),
            "reported_delisting_date": delisting_date.strftime("%Y-%m-%d"),
            "report_month": str(event.get("_report_month", "")),
            "request": {
                "method": "yf.Ticker(ticker).history",
                "start": start_date,
                "end": "provider current end; omitted",
                "interval": "1d",
                "auto_adjust": False,
                "actions": True,
                "repair": False,
                "keepna": True,
            },
            "attempts": [],
            "history_status": "UNTESTED",
            "has_any_history": False,
            "history_rows": 0,
            "first_bar_date": None,
            "last_bar_date": None,
            "valid_ohlc_rows": 0,
            "invalid_or_blank_ohlc_rows": None,
            "last_valid_bar_on_or_before_delisting": None,
            "gap_calendar_days_to_delisting": None,
            "has_valid_bar_within_30_calendar_days": False,
            "csv_path": None,
            "csv_bytes": None,
            "csv_sha256": None,
            "final_error": None,
        }

        frame_success: pd.DataFrame | None = None
        date_strings: list[str] | None = None
        attempt = 0
        while attempt < MAX_ATTEMPTS:
            attempt += 1
            began = now()
            logbuf = io.StringIO()
            handler = logging.StreamHandler(logbuf)
            logger.addHandler(handler)
            old_handler_levels = handler.level
            handler.setLevel(logging.DEBUG)
            stage = "Ticker.history"
            try:
                frame = yf.Ticker(ticker).history(
                    start=start_date,
                    interval="1d",
                    auto_adjust=False,
                    actions=True,
                    repair=False,
                    keepna=True,
                    timeout=30,
                )
                diag = logbuf.getvalue()
                if frame is None or frame.empty:
                    lower = diag.lower()
                    code_404 = ("404" in lower) or ("possibly delisted" in lower) or ("no timezone found" in lower)
                    status = "HTTP_404_OR_YAHOO_UNAVAILABLE" if code_404 else "EMPTY_HISTORY"
                    record["attempts"].append({
                        "attempt": attempt, "started_utc": began, "finished_utc": now(),
                        "stage": stage, "status": status,
                        "error_type": "EmptyHistory",
                        "error_message": (diag.strip()[-4000:] or "yfinance returned an empty DataFrame without an explicit exception"),
                        "http_404_evidence_in_yfinance_log": code_404,
                    })
                    record["history_status"] = status
                    record["final_error"] = record["attempts"][-1]["error_message"]
                    print(f"YAHOO_DELISTED_EMPTY code={code} ticker={ticker} attempt={attempt} status={status} log={record['final_error']!r}", flush=True)
                    break

                frame = flatten_columns(frame).sort_index()
                ix = pd.DatetimeIndex(frame.index)
                if ix.tz is not None:
                    date_strings = list(ix.tz_convert("Asia/Jakarta").strftime("%Y-%m-%d"))
                else:
                    date_strings = list(ix.strftime("%Y-%m-%d"))
                if len(date_strings) != len(frame) or not date_strings:
                    raise RuntimeError(f"DATE_ALIGNMENT_ERROR: dates={len(date_strings)} rows={len(frame)}")
                frame_success = frame.copy()
                record["attempts"].append({
                    "attempt": attempt, "started_utc": began, "finished_utc": now(),
                    "stage": "success", "status": "OK", "error_type": None,
                    "error_message": None, "library_log_tail": diag[-2000:],
                })
                record["history_status"] = "AVAILABLE"
                print(f"YAHOO_DELISTED_AVAILABLE code={code} ticker={ticker} attempt={attempt} rows={len(frame)} first={date_strings[0]} last={date_strings[-1]}", flush=True)
                break
            except Exception as exc:
                diag = logbuf.getvalue()
                msg = str(exc) or repr(exc)
                err = (msg + "\n" + diag).lower()
                is_404 = ("404" in err) or ("possibly delisted" in err) or ("no timezone found" in err)
                retryable = any(token in err for token in RETRY_TOKENS)
                record["attempts"].append({
                    "attempt": attempt, "started_utc": began, "finished_utc": now(),
                    "stage": stage, "status": "ERROR",
                    "error_type": type(exc).__name__,
                    "error_message": msg,
                    "http_404_evidence_in_error_or_log": is_404,
                    "retryable_by_policy": retryable,
                    "library_log_tail": diag[-4000:],
                })
                record["final_error"] = msg
                record["history_status"] = "HTTP_404" if is_404 else "ERROR"
                print(f"YAHOO_DELISTED_ERROR code={code} ticker={ticker} attempt={attempt} type={type(exc).__name__} error={msg!r} log={diag[-1200:]!r}", flush=True)
                if is_404 or not retryable or attempt >= MAX_ATTEMPTS:
                    break
            finally:
                logger.removeHandler(handler)
                handler.close()

            delay = WAIT_SECONDS[attempt - 1]
            record["attempts"][-1]["retry_wait_seconds"] = delay
            print(f"YAHOO_DELISTED_RETRY code={code} next_attempt={attempt+1} wait_seconds={delay}", flush=True)
            time.sleep(delay)

        if frame_success is not None and date_strings is not None:
            output_frame = frame_success.copy().reset_index(drop=True)
            output_frame.insert(0, "Date", date_strings)
            csv_path = out_dir / f"{safe_slug(code)}_JK.csv"
            output_frame.to_csv(csv_path, index=False, encoding="utf-8", lineterminator="\n")
            valid_mask = valid_ohlc(frame_success)
            # Align the mask by positional rows to the Date values.
            valid_dates = [date_strings[pos] for pos, valid in enumerate(valid_mask.to_list()) if bool(valid)]
            on_or_before = [d for d in valid_dates if d <= delisting_date.strftime("%Y-%m-%d")]
            last_valid = max(on_or_before) if on_or_before else None
            gap = (delisting_date - pd.Timestamp(last_valid)).days if last_valid else None
            all_dates = sorted(date_strings)
            invalid_count = int((~valid_mask).sum())
            record.update({
                "history_status": "AVAILABLE",
                "has_any_history": bool(len(output_frame)),
                "history_rows": int(len(output_frame)),
                "first_bar_date": all_dates[0],
                "last_bar_date": all_dates[-1],
                "valid_ohlc_rows": int(valid_mask.sum()),
                "invalid_or_blank_ohlc_rows": invalid_count,
                "last_valid_bar_on_or_before_delisting": last_valid,
                "gap_calendar_days_to_delisting": int(gap) if gap is not None else None,
                "has_valid_bar_within_30_calendar_days": bool(gap is not None and 0 <= gap <= near_days),
                "csv_path": str(csv_path.relative_to(data_root)),
                "csv_bytes": int(csv_path.stat().st_size),
                "csv_sha256": sha_file(csv_path),
                "final_error": None,
            })
            if not record["has_valid_bar_within_30_calendar_days"]:
                record["history_status"] = "AVAILABLE_BUT_NO_VALID_BAR_WITHIN_30D_OF_DELISTING"
            print(f"YAHOO_DELISTED_COVERAGE code={code} any_history=1 rows={record['history_rows']} range={record['first_bar_date']}..{record['last_bar_date']} last_valid_before_delist={last_valid} gap_days={gap} near30={int(record['has_valid_bar_within_30_calendar_days'])} invalid={invalid_count}", flush=True)

        results.append(record)
        print(f"YAHOO_DELISTED_PROGRESS={idx}/{len(events)}", flush=True)
        time.sleep(0.15)

    logger.setLevel(prev_level)

    available = [x for x in results if x["has_any_history"]]
    explicit_404 = [x for x in results if x["history_status"] == "HTTP_404" or x["history_status"] == "HTTP_404_OR_YAHOO_UNAVAILABLE"]
    empty_or_error = [x for x in results if not x["has_any_history"] and x not in explicit_404]
    near = [x for x in results if x["has_valid_bar_within_30_calendar_days"]]
    near_pct = 100.0 * len(near) / len(events) if events else 0.0
    available_pct = 100.0 * len(available) / len(events) if events else 0.0

    summary_path = out_dir / "delisted_yahoo_coverage_2010-01_to_2026-10.csv"
    fields = [
        "code", "ticker", "issuer_name", "listing_date", "reported_delisting_date", "report_month",
        "history_status", "has_any_history", "history_rows", "first_bar_date", "last_bar_date",
        "valid_ohlc_rows", "invalid_or_blank_ohlc_rows", "last_valid_bar_on_or_before_delisting",
        "gap_calendar_days_to_delisting", "has_valid_bar_within_30_calendar_days",
        "csv_path", "csv_bytes", "csv_sha256", "final_error",
    ]
    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n", extrasaction="ignore")
        writer.writeheader()
        for item in results:
            row = {k: item.get(k) for k in fields}
            row["has_any_history"] = int(bool(row["has_any_history"]))
            row["has_valid_bar_within_30_calendar_days"] = int(bool(row["has_valid_bar_within_30_calendar_days"]))
            writer.writerow(row)

    manifest = {
        "experiment": "R333",
        "purpose": "Yahoo historical daily bar availability for 65 officially reported delisted IDX issuers; source audit only, no strategy calculations",
        "data_only": True,
        "pnl_calculation": False,
        "run_id": run_id,
        "run_attempt": run_attempt,
        "started_utc": started,
        "finished_utc": now(),
        "source": "Yahoo Finance via yfinance in GitHub Actions",
        "yfinance_version": getattr(yf, "__version__", "unknown"),
        "python_version": sys.version,
        "events_csv": {
            "path": str(event_path.relative_to(data_root)),
            "rows": len(events),
            "sha256": event_sha,
            "expected_sha256": expected_event_sha,
        },
        "request": {
            "history_start_date": start_date,
            "end": "provider current end, omitted",
            "interval": "1d",
            "auto_adjust": False,
            "actions": True,
            "repair": False,
            "keepna": True,
            "near_delisting_definition": f"at least one valid OHLC daily bar on or before DeListingDate, with the last valid pre-delisting bar no more than {near_days} calendar days earlier",
            "retry_waits_seconds": WAIT_SECONDS,
            "max_attempts_per_ticker": MAX_ATTEMPTS,
            "source_only": True,
        },
        "counts": {
            "delisted_event_rows_tested": len(events),
            "unique_codes_tested": len(set(codes)),
            "nonempty_yahoo_history": len(available),
            "nonempty_history_percent_of_65": round(available_pct, 4),
            "explicit_http_404_or_yfinance_404_evidence": len(explicit_404),
            "empty_history_or_other_error_without_explicit_404": len(empty_or_error),
            "valid_bar_within_30_calendar_days_of_delisting": len(near),
            "valid_bar_within_30_calendar_days_percent_of_65": round(near_pct, 4),
            "valid_bar_within_30_calendar_days_percent_of_nonempty_histories": round(100.0 * len(near) / len(available), 4) if available else 0.0,
            "bars_within_10_calendar_days_of_delisting": sum(1 for x in results if x["gap_calendar_days_to_delisting"] is not None and 0 <= x["gap_calendar_days_to_delisting"] <= 10),
            "with_any_valid_ohlc_row": sum(1 for x in results if x["valid_ohlc_rows"] and x["valid_ohlc_rows"] > 0),
            "csvs_saved_for_nonempty_history": len(available),
            "range_min_first_bar_date": min((x["first_bar_date"] for x in available if x["first_bar_date"]), default=None),
            "range_max_last_bar_date": max((x["last_bar_date"] for x in available if x["last_bar_date"]), default=None),
            "total_history_rows": sum(x["history_rows"] for x in available),
            "total_invalid_or_blank_ohlc_rows": sum(x["invalid_or_blank_ohlc_rows"] or 0 for x in available),
        },
        "records": results,
        "outputs": {
            "summary_csv": str(summary_path.relative_to(data_root)),
            "summary_csv_sha256": sha_file(summary_path),
            "summary_csv_bytes": summary_path.stat().st_size,
            "raw_nonempty_ticker_csv_directory": str(out_dir.relative_to(data_root)),
        },
        "limitations": [
            "Yahoo HTTP 404 or empty history is not independent proof that IDX delisted the issuer.",
            "Historical bar availability in this Yahoo cache does not validate corporate action adjustments or executable prices.",
            "Near-delisting coverage is measured as the last valid OHLC bar on or before the official reported DeListingDate being within 30 calendar days.",
            "No backtest, signal, PnL, PF, return, or alpha computation is performed.",
        ],
    }
    manifest_path = data_root / "data/r333/manifests/yahoo-delisted-coverage-latest.json"
    immutable_path = data_root / "data/r333/manifests" / f"yahoo_delisted_coverage_run_{run_id}_attempt_{run_attempt}.json"
    for path in (manifest_path, immutable_path):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output("overall_status", "COMPLETE" if len(results) == len(events) else "INCOMPLETE")
    output("records", str(len(results)))
    output("history_available", str(len(available)))
    output("http_404", str(len(explicit_404)))
    output("near_30d", str(len(near)))
    output("near_30d_pct", f"{near_pct:.4f}")
    output("summary_path", str(summary_path.relative_to(data_root)))
    output("manifest_path", str(manifest_path.relative_to(data_root)))
    print(f"R333_DELISTED_YAHOO_SUMMARY total={len(results)} available={len(available)} explicit_404={len(explicit_404)} empty_or_other={len(empty_or_error)} near30={len(near)} near30_pct={near_pct:.4f} range_min_first={manifest['counts']['range_min_first_bar_date']} range_max_last={manifest['counts']['range_max_last_bar_date']}", flush=True)
    return 0 if len(results) == len(events) else 1


if __name__ == "__main__":
    raise SystemExit(main())
