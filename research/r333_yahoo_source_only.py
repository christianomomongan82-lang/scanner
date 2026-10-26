#!/usr/bin/env python3
"""R333 Yahoo Finance daily source acquisition ONLY; no signal/PnL calculations."""
from __future__ import annotations

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

SMOKE_TICKERS = ["^JKSE", "BBCA.JK", "BBRI.JK", "TLKM.JK"]
WAIT_SECONDS = [30, 120, 600, 600]  # delays after failures on attempts 1..4
MAX_ATTEMPTS = 5
MAX_TICKERS_PER_RUN = 10
INTERVAL = "1d"
DEFAULT_START = "2010-01-01"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def slug(ticker: str) -> str:
    value = ticker.replace("^", "IDX_").replace(".", "_")
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")
    return value or "ticker"


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_output_status(value: str) -> None:
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(f"overall_status={value}\n")
    print(f"R333_OVERALL_STATUS={value}")


def flat_columns(frame: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(frame.columns, pd.MultiIndex):
        return frame
    known = {
        "Open", "High", "Low", "Close", "Adj Close", "Volume",
        "Dividends", "Stock Splits", "Capital Gains",
    }
    renamed = []
    for col in frame.columns.to_list():
        pieces = [str(x) for x in (col if isinstance(col, tuple) else (col,))]
        matches = [x for x in pieces if x in known]
        renamed.append(matches[0] if matches else "_".join(pieces))
    frame = frame.copy()
    frame.columns = renamed
    return frame


def quality_summary(frame: pd.DataFrame, date_strings: list[str]) -> dict[str, Any]:
    cols = {str(c).strip().lower(): c for c in frame.columns}
    ohlc_names = ["open", "high", "low", "close"]
    missing_fields = [c for c in ohlc_names + ["volume"] if c not in cols]
    bad_ohlc_rows = None
    bad_volume_rows = None
    if not missing_fields:
        op = pd.to_numeric(frame[cols["open"]], errors="coerce")
        hi = pd.to_numeric(frame[cols["high"]], errors="coerce")
        lo = pd.to_numeric(frame[cols["low"]], errors="coerce")
        cl = pd.to_numeric(frame[cols["close"]], errors="coerce")
        bad = (
            op.isna() | hi.isna() | lo.isna() | cl.isna()
            | (op < 0) | (hi < 0) | (lo < 0) | (cl < 0)
            | (lo > hi) | (lo > op) | (lo > cl)
            | (hi < op) | (hi < cl)
        )
        bad_ohlc_rows = int(bad.sum())
        vol = pd.to_numeric(frame[cols["volume"]], errors="coerce")
        bad_volume_rows = int((vol.isna() | (vol < 0)).sum())
    dividend_col = cols.get("dividends")
    split_col = cols.get("stock splits")
    dividends = pd.to_numeric(frame[dividend_col], errors="coerce").fillna(0) if dividend_col else pd.Series(0, index=frame.index)
    splits = pd.to_numeric(frame[split_col], errors="coerce").fillna(0) if split_col else pd.Series(0, index=frame.index)
    return {
        "missing_required_fields": missing_fields,
        "duplicate_date_rows": int(pd.Series(date_strings).duplicated(keep=False).sum()),
        "ohlc_invalid_rows": bad_ohlc_rows,
        "volume_invalid_rows": bad_volume_rows,
        "dividend_event_rows": int((dividends != 0).sum()),
        "stock_split_event_rows": int((splits != 0).sum()),
        "has_adj_close": "adj close" in cols,
        "raw_ohlc_requested": True,
    }


def latest_manifest_path(root: Path) -> Path:
    return root / "data" / "r333" / "manifests" / "latest.json"


def choose_tickers(root: Path, event_name: str, input_tickers: str) -> tuple[list[str], str, bool]:
    manifests = root / "data" / "r333" / "manifests"
    latest = read_json(latest_manifest_path(root))
    smoke = read_json(manifests / "smoke-test.json")

    if event_name == "schedule":
        if latest and latest.get("overall_status") == "INCOMPLETE":
            prior = latest.get("tickers_requested") or []
            if prior:
                return prior, latest.get("batch_label", "scheduled-retry"), False
        if smoke and smoke.get("overall_status") == "ACQUISITION_COMPLETE":
            print("Scheduled retry skipped: initial four-ticker acquisition is already complete and there is no newer incomplete batch.")
            return [], "scheduled-skip-after-complete", True
        return SMOKE_TICKERS, "smoke-test-scheduled-retry", False

    if input_tickers.strip():
        tickers = [x.strip() for x in input_tickers.split(",") if x.strip()]
    else:
        tickers = SMOKE_TICKERS
    unique = list(dict.fromkeys(tickers))
    if unique == SMOKE_TICKERS:
        label = "smoke-test"
    elif event_name == "push":
        label = "smoke-test"
    else:
        label = "manual-batch"
    return unique, label, False


def main() -> int:
    data_root = Path(os.environ["R333_DATA_ROOT"]).resolve()
    event_name = os.environ.get("R333_EVENT_NAME", "unknown")
    input_tickers = os.environ.get("R333_TICKERS", "")
    start_date = os.environ.get("R333_START_DATE", DEFAULT_START)
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")
    manifest_dir = data_root / "data" / "r333" / "manifests"
    data_dir = data_root / "data" / "r333" / "yahoo_daily"

    if start_date != DEFAULT_START:
        # Allow later registered batches to set an earlier/later start, but never request before 2010.
        if start_date < DEFAULT_START:
            raise SystemExit("START_DATE_REJECTED: R333 source-only acquisition may not start before 2010-01-01.")

    tickers, batch_label, skipped = choose_tickers(data_root, event_name, input_tickers)
    if skipped:
        write_output_status("SKIPPED")
        return 0
    if not tickers:
        write_output_status("INCOMPLETE")
        raise SystemExit("NO_TICKERS: no ticker was specified.")
    if len(tickers) > MAX_TICKERS_PER_RUN:
        raise SystemExit(f"BATCH_TOO_LARGE: maximum {MAX_TICKERS_PER_RUN} tickers per workflow run to respect the retry budget.")

    started = utc_now()
    print(f"R333 source-only acquisition run={run_id} attempt={run_attempt} started_utc={started}")
    print(f"yfinance_version={getattr(yf, '__version__', 'unknown')} interval={INTERVAL} start={start_date} auto_adjust=False actions=True")
    print(f"tickers={','.join(tickers)} batch_label={batch_label}")

    ticker_results: list[dict[str, Any]] = []
    for ticker in tickers:
        ticker_result: dict[str, Any] = {
            "ticker": ticker,
            "status": "FAILED",
            "request": {
                "library": "yfinance",
                "method": "Ticker.history",
                "start": start_date,
                "end": None,
                "interval": INTERVAL,
                "auto_adjust": False,
                "actions": True,
                "repair": False,
                "keepna": True,
            },
            "attempts": [],
        }
        success_frame: pd.DataFrame | None = None
        success_dates: list[str] | None = None
        for attempt in range(1, MAX_ATTEMPTS + 1):
            began = utc_now()
            log_buffer = io.StringIO()
            handler = logging.StreamHandler(log_buffer)
            yf_logger = logging.getLogger("yfinance")
            original_level = yf_logger.level
            yf_logger.addHandler(handler)
            yf_logger.setLevel(logging.DEBUG)
            stage = "Ticker.history"
            try:
                frame = yf.Ticker(ticker).history(
                    start=start_date,
                    interval=INTERVAL,
                    auto_adjust=False,
                    actions=True,
                    prepost=False,
                    repair=False,
                    keepna=True,
                    timeout=30,
                    raise_errors=True,
                )
                stage = "response-validation"
                if frame is None or frame.empty:
                    raise RuntimeError("EMPTY_DATAFRAME: yfinance returned no daily rows for this ticker/date range.")
                frame = flat_columns(frame).sort_index()
                idx = pd.DatetimeIndex(frame.index)
                if idx.tz is not None:
                    date_strings = list(idx.tz_convert("Asia/Jakarta").strftime("%Y-%m-%d"))
                else:
                    date_strings = list(idx.strftime("%Y-%m-%d"))
                if len(date_strings) != len(frame):
                    raise RuntimeError("DATE_ALIGNMENT_ERROR: date index and dataframe row counts differ.")
                if not date_strings:
                    raise RuntimeError("EMPTY_DATE_INDEX: no usable date values in response.")
                success_frame = frame.copy()
                success_dates = date_strings
                diag = log_buffer.getvalue()
                ticker_result["attempts"].append({
                    "attempt": attempt,
                    "started_utc": began,
                    "finished_utc": utc_now(),
                    "stage": "success",
                    "status": "OK",
                    "error_type": None,
                    "error_message": None,
                    "library_log_tail": diag[-3000:] if diag else "",
                })
                print(f"ACQUISITION_OK ticker={ticker} attempt={attempt} rows={len(frame)} first={date_strings[0]} last={date_strings[-1]}")
                break
            except Exception as exc:  # capture the actual Yahoo/yfinance failure stage and text
                diag = log_buffer.getvalue()
                error_message = str(exc) or repr(exc)
                attempt_record = {
                    "attempt": attempt,
                    "started_utc": began,
                    "finished_utc": utc_now(),
                    "stage": stage,
                    "status": "ERROR",
                    "error_type": type(exc).__name__,
                    "error_message": error_message,
                    "library_log_tail": diag[-5000:] if diag else "",
                }
                ticker_result["attempts"].append(attempt_record)
                print(f"ACQUISITION_ERROR ticker={ticker} attempt={attempt} stage={stage} error_type={type(exc).__name__} error={error_message!r}")
                if diag:
                    print(f"YFINANCE_LOG_TAIL ticker={ticker} attempt={attempt}: {diag[-3000:]}")
            finally:
                yf_logger.removeHandler(handler)
                yf_logger.setLevel(original_level)
                handler.close()
            if attempt < MAX_ATTEMPTS:
                delay = WAIT_SECONDS[attempt - 1]
                print(f"RETRY_WAIT ticker={ticker} next_attempt={attempt + 1} wait_seconds={delay}")
                time.sleep(delay)

        if success_frame is not None and success_dates is not None:
            slugged = slug(ticker)
            output_path = data_dir / f"{slugged}.csv"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_frame = success_frame.copy().reset_index(drop=True)
            output_frame.insert(0, "Date", success_dates)
            output_frame.to_csv(output_path, index=False, encoding="utf-8", lineterminator="\n")
            ticker_result.update({
                "status": "ACQUIRED_NEEDS_AUDIT",
                "csv_path": str(output_path.relative_to(data_root)),
                "row_count": int(len(output_frame)),
                "first_date": success_dates[0],
                "last_date": success_dates[-1],
                "sha256": sha256_file(output_path),
                "bytes": int(output_path.stat().st_size),
                "quality_summary": quality_summary(success_frame, success_dates),
                "yfinance_version": getattr(yf, "__version__", "unknown"),
            })
        else:
            ticker_result.update({
                "status": "FAILED_AFTER_MAX_ATTEMPTS",
                "row_count": None,
                "first_date": None,
                "last_date": None,
                "sha256": None,
                "failure_stage": ticker_result["attempts"][-1]["stage"] if ticker_result["attempts"] else "no-attempt",
            })
        ticker_results.append(ticker_result)

    overall = "ACQUISITION_COMPLETE" if all(x["status"] == "ACQUIRED_NEEDS_AUDIT" for x in ticker_results) else "INCOMPLETE"
    ended = utc_now()
    manifest = {
        "experiment": "R333",
        "purpose": "data acquisition and source/data-quality metadata only; no strategy signals, PnL, PF, or verdict calculation",
        "source": "Yahoo Finance via yfinance",
        "run_id": str(run_id),
        "run_attempt": str(run_attempt),
        "event_name": event_name,
        "batch_label": batch_label,
        "started_utc": started,
        "finished_utc": ended,
        "library": "yfinance",
        "library_version": getattr(yf, "__version__", "unknown"),
        "python_version": sys.version,
        "parameters": {
            "tickers_requested": tickers,
            "start": start_date,
            "end": "API current end; omitted intentionally",
            "interval": INTERVAL,
            "auto_adjust": False,
            "actions": True,
            "maximum_total_attempts_per_ticker": MAX_ATTEMPTS,
            "wait_seconds_between_failed_attempts": WAIT_SECONDS,
            "retry_policy": "up to five total attempts per ticker; waits 30s, 120s, 600s, 600s",
        },
        "overall_status": overall,
        "ticker_results": ticker_results,
        "survivorship_warning": "Yahoo history does not by itself prove complete historical coverage of delisted IDX equities; no alpha claim or data-eligibility pass follows from acquisition success alone.",
    }
    manifest_dir.mkdir(parents=True, exist_ok=True)
    write_json(latest_manifest_path(data_root), manifest)
    write_json(manifest_dir / f"run_{run_id}_attempt_{run_attempt}.json", manifest)
    if batch_label.startswith("smoke-test"):
        write_json(manifest_dir / "smoke-test.json", manifest)

    output_status = "COMPLETE" if overall == "ACQUISITION_COMPLETE" else "INCOMPLETE"
    write_output_status(output_status)
    print(f"MANIFEST_WRITTEN path=data/r333/manifests/latest.json status={overall}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
