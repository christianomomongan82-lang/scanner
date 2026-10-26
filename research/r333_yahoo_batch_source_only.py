#!/usr/bin/env python3
"""R333 batched Yahoo daily acquisition only. No universe scoring, signals, PnL or PF."""
from __future__ import annotations

import csv
import hashlib
import io
import json
import logging
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import yfinance as yf

yf.config.debug.hide_exceptions = False
MAX_ATTEMPTS = 5
WAIT_SECONDS = [30, 120, 600, 600]
INTERVAL = "1d"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def slug(ticker: str) -> str:
    value = ticker.replace("^", "IDX_").replace(".", "_")
    value = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")
    return value or "ticker"


def flatten_columns(frame: pd.DataFrame) -> pd.DataFrame:
    if not isinstance(frame.columns, pd.MultiIndex):
        return frame
    known = {"Open", "High", "Low", "Close", "Adj Close", "Volume",
             "Dividends", "Stock Splits", "Capital Gains"}
    names = []
    for column in frame.columns.to_list():
        parts = [str(x) for x in (column if isinstance(column, tuple) else (column,))]
        matches = [p for p in parts if p in known]
        names.append(matches[0] if matches else "_".join(parts))
    out = frame.copy()
    out.columns = names
    return out


def quality(frame: pd.DataFrame, dates: list[str]) -> dict[str, Any]:
    cols = {str(c).strip().lower(): c for c in frame.columns}
    required = ["open", "high", "low", "close", "volume"]
    missing = [name for name in required if name not in cols]
    bad_ohlc = None
    bad_volume = None
    if not missing:
        op, hi, lo, cl = [pd.to_numeric(frame[cols[k]], errors="coerce")
                          for k in ("open", "high", "low", "close")]
        invalid = (op.isna() | hi.isna() | lo.isna() | cl.isna()
                   | (op < 0) | (hi < 0) | (lo < 0) | (cl < 0)
                   | (lo > hi) | (lo > op) | (lo > cl)
                   | (hi < op) | (hi < cl))
        bad_ohlc = int(invalid.sum())
        vol = pd.to_numeric(frame[cols["volume"]], errors="coerce")
        bad_volume = int((vol.isna() | (vol < 0)).sum())
    dividends = pd.to_numeric(frame[cols["dividends"]], errors="coerce").fillna(0) if "dividends" in cols else pd.Series(0, index=frame.index)
    splits = pd.to_numeric(frame[cols["stock splits"]], errors="coerce").fillna(0) if "stock splits" in cols else pd.Series(0, index=frame.index)
    return {
        "missing_required_fields": missing,
        "duplicate_date_rows": int(pd.Series(dates).duplicated(keep=False).sum()),
        "invalid_ohlc_rows": bad_ohlc,
        "invalid_volume_rows": bad_volume,
        "dividend_event_rows": int((dividends != 0).sum()),
        "stock_split_event_rows": int((splits != 0).sum()),
        "has_adj_close": "adj close" in cols,
        "raw_ohlc_requested": True,
        "invalid_rows_preserved": True,
    }


def output(key: str, value: str) -> None:
    output_file = os.environ.get("GITHUB_OUTPUT")
    if output_file:
        with open(output_file, "a", encoding="utf-8") as handle:
            handle.write(f"{key}={value}\n")
    print(f"R333_{key.upper()}={value}")


def main() -> int:
    data_root = Path(os.environ["R333_DATA_ROOT"]).resolve()
    request_path = Path(os.environ["R333_REQUEST_PATH"]).resolve()
    batch_index = int(os.environ["R333_BATCH_INDEX"])
    run_id = os.environ.get("GITHUB_RUN_ID", "local")
    run_attempt = os.environ.get("GITHUB_RUN_ATTEMPT", "1")

    request = json.loads(request_path.read_text(encoding="utf-8"))
    start_date = str(request.get("start_date", "2010-01-01"))
    interval = str(request.get("interval", "1d"))
    batch_size = int(request.get("batch_size", 10))
    if start_date < "2010-01-01":
        raise SystemExit("START_DATE_REJECTED: R333 acquisition may not start before 2010-01-01.")
    if interval != "1d":
        raise SystemExit(f"INTERVAL_REJECTED: locked request expects 1d, got {interval!r}.")
    if batch_size != 10:
        raise SystemExit(f"BATCH_SIZE_REJECTED: locked acquisition batch size must be 10, got {batch_size}.")

    queue_path = data_root / "data/r333/universe/yahoo_daily_acquisition_roster.csv"
    if not queue_path.exists():
        raise SystemExit(f"QUEUE_NOT_FOUND: {queue_path}")
    raw_queue = queue_path.read_bytes()
    with queue_path.open("r", newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    tickers = [row["yahoo_ticker"].strip() for row in rows if row.get("yahoo_ticker", "").strip()]
    expected = int(request.get("expected_ticker_count", len(tickers)))
    if len(tickers) != expected:
        raise SystemExit(f"QUEUE_COUNT_MISMATCH: expected={expected} actual={len(tickers)}")
    if len(set(tickers)) != len(tickers):
        raise SystemExit("QUEUE_DUPLICATE_TICKERS: duplicate Yahoo ticker symbols found.")
    all_batches = (len(tickers) + batch_size - 1) // batch_size
    if batch_index < 0 or batch_index >= all_batches:
        raise SystemExit(f"BATCH_INDEX_OUT_OF_RANGE: index={batch_index}, batch_count={all_batches}")
    batch = tickers[batch_index * batch_size:(batch_index + 1) * batch_size]

    queue_git_sha = subprocess.run(
        ["git", "hash-object", str(queue_path.relative_to(data_root))],
        cwd=data_root, check=True, capture_output=True, text=True
    ).stdout.strip()
    started = now()
    print(f"R333_BATCH_START run={run_id} attempt={run_attempt} batch={batch_index + 1}/{all_batches} tickers={len(batch)} start={start_date} interval={interval}")
    print(f"R333_QUEUE rows={len(tickers)} sha256={sha256_bytes(raw_queue)} git_blob_sha={queue_git_sha}")
    print("R333_MODE=DATA_ONLY; signals/PnL/PF are prohibited in this collector")

    ticker_results: list[dict[str, Any]] = []
    out_dir = data_root / "data/r333/yahoo_daily"
    for ticker in batch:
        result: dict[str, Any] = {
            "ticker": ticker,
            "status": "FAILED",
            "request": {
                "library": "yfinance", "method": "Ticker.history",
                "start": start_date, "end": None, "interval": interval,
                "auto_adjust": False, "actions": True, "repair": False,
                "keepna": True, "timeout_seconds": 30,
            },
            "attempts": [],
        }
        success: pd.DataFrame | None = None
        date_values: list[str] | None = None

        for attempt in range(1, MAX_ATTEMPTS + 1):
            began = now()
            logbuf = io.StringIO()
            handler = logging.StreamHandler(logbuf)
            logger = logging.getLogger("yfinance")
            old_level = logger.level
            logger.addHandler(handler)
            logger.setLevel(logging.DEBUG)
            stage = "Ticker.history"
            try:
                frame = yf.Ticker(ticker).history(
                    start=start_date, interval=interval, auto_adjust=False,
                    actions=True, prepost=False, repair=False, keepna=True, timeout=30
                )
                stage = "response-validation"
                if frame is None or frame.empty:
                    raise RuntimeError("EMPTY_DATAFRAME: yfinance returned no daily rows.")
                frame = flatten_columns(frame).sort_index()
                ix = pd.DatetimeIndex(frame.index)
                if ix.tz is not None:
                    dates = list(ix.tz_convert("Asia/Jakarta").strftime("%Y-%m-%d"))
                else:
                    dates = list(ix.strftime("%Y-%m-%d"))
                if len(dates) != len(frame) or not dates:
                    raise RuntimeError(f"DATE_ALIGNMENT_ERROR: dates={len(dates)} rows={len(frame)}")
                success = frame.copy()
                date_values = dates
                diagnostic = logbuf.getvalue()
                result["attempts"].append({
                    "attempt": attempt, "started_utc": began, "finished_utc": now(),
                    "stage": "success", "status": "OK", "error_type": None,
                    "error_message": None, "library_log_tail": diagnostic[-2500:],
                })
                print(f"ACQUISITION_OK ticker={ticker} attempt={attempt} rows={len(frame)} first={dates[0]} last={dates[-1]}")
                break
            except Exception as exc:
                diagnostic = logbuf.getvalue()
                msg = str(exc) or repr(exc)
                result["attempts"].append({
                    "attempt": attempt, "started_utc": began, "finished_utc": now(),
                    "stage": stage, "status": "ERROR", "error_type": type(exc).__name__,
                    "error_message": msg, "library_log_tail": diagnostic[-4000:],
                })
                print(f"ACQUISITION_ERROR ticker={ticker} attempt={attempt} stage={stage} error_type={type(exc).__name__} error={msg!r}")
                if diagnostic:
                    print(f"YFINANCE_LOG_TAIL ticker={ticker} attempt={attempt}: {diagnostic[-2000:]}")
            finally:
                logger.removeHandler(handler)
                logger.setLevel(old_level)
                handler.close()
            if attempt < MAX_ATTEMPTS:
                delay = WAIT_SECONDS[attempt - 1]
                print(f"RETRY_WAIT ticker={ticker} next_attempt={attempt + 1} wait_seconds={delay}")
                time.sleep(delay)

        if success is not None and date_values is not None:
            output_path = out_dir / f"{slug(ticker)}.csv"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_frame = success.copy().reset_index(drop=True)
            output_frame.insert(0, "Date", date_values)
            output_frame.to_csv(output_path, index=False, encoding="utf-8", lineterminator="\n")
            result.update({
                "status": "ACQUIRED_NEEDS_AUDIT",
                "csv_path": str(output_path.relative_to(data_root)),
                "row_count": int(len(output_frame)),
                "first_date": date_values[0],
                "last_date": date_values[-1],
                "bytes": int(output_path.stat().st_size),
                "sha256": sha256_file(output_path),
                "quality_summary": quality(success, date_values),
                "yfinance_version": getattr(yf, "__version__", "unknown"),
            })
        else:
            result.update({
                "status": "FAILED_AFTER_MAX_ATTEMPTS",
                "row_count": None, "first_date": None, "last_date": None,
                "bytes": None, "sha256": None,
                "failure_stage": result["attempts"][-1]["stage"] if result["attempts"] else "no-attempt",
            })
        ticker_results.append(result)

    overall = "ACQUISITION_COMPLETE" if all(x["status"] == "ACQUIRED_NEEDS_AUDIT" for x in ticker_results) else "INCOMPLETE"
    manifest = {
        "experiment": "R333",
        "purpose": "raw daily data acquisition and metadata only; no small-cap selection, signals, PnL, PF, or alpha verdict",
        "source": "Yahoo Finance via yfinance",
        "source_branch": "data/r333-idx-daily-yahoo",
        "run_id": str(run_id), "run_attempt": str(run_attempt),
        "batch_index_zero_based": batch_index, "batch_number_one_based": batch_index + 1,
        "batch_count": all_batches, "batch_size": batch_size,
        "started_utc": started, "finished_utc": now(),
        "library": "yfinance", "library_version": getattr(yf, "__version__", "unknown"),
        "python_version": sys.version,
        "parameters": {
            "start": start_date, "end": "API current end; omitted intentionally",
            "interval": interval, "auto_adjust": False, "actions": True,
            "repair": False, "keepna": True, "maximum_total_attempts_per_ticker": MAX_ATTEMPTS,
            "wait_seconds_between_failed_attempts": WAIT_SECONDS,
        },
        "queue": {
            "path": "data/r333/universe/yahoo_daily_acquisition_roster.csv",
            "row_count": len(tickers), "sha256": sha256_bytes(raw_queue),
            "git_blob_sha": queue_git_sha, "source_roster_git_blob_sha": request.get("source_roster_git_blob_sha"),
            "survivorship_label": "survivorship-biased",
            "is_smallcap_universe": False,
        },
        "tickers_requested": batch,
        "ticker_results": ticker_results,
        "overall_status": overall,
        "survivorship_warning": "Queue contains only current IDX listing roster. No verified delisted universe; this is survivorship-biased acquisition coverage only, not a historical small-cap universe or alpha test.",
    }
    manifest_dir = data_root / "data/r333/manifests/yahoo_batches"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / f"batch_{batch_index:03d}_run_{run_id}_attempt_{run_attempt}.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    output("overall_status", overall)
    output("batch_index", str(batch_index))
    output("batch_manifest_path", str(manifest_path.relative_to(data_root)))
    print(f"MANIFEST_WRITTEN path={manifest_path.relative_to(data_root)} status={overall}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
