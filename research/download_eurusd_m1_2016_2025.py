#!/usr/bin/env python3
"""Download and archive EURUSD M1 BID/ASK from Dukascopy. DATA ACQUISITION ONLY.
No indicators, signals, PnL, simulation, or backtest calculations are performed here.
"""
from __future__ import annotations
import calendar
import csv
import gzip
import hashlib
import json
import os
import subprocess
import time
from datetime import date
from pathlib import Path

START = date(2016, 1, 1)
END_EXCLUSIVE = date(2026, 1, 1)
ROOT = Path(".")
DATA = ROOT / "dl" / "eurusd_m1_2016_2025"
OUT = ROOT / "data_exports" / "eurusd_m1_2016_2025"
PATCH = ROOT / "dukascopy_fetch_patch.cjs"


def month_ranges(start: date, end: date):
    cur = start
    while cur < end:
        next_month = date(cur.year + (cur.month == 12), 1 if cur.month == 12 else cur.month + 1, 1)
        yield cur, min(next_month, end)
        cur = next_month


def download_month(side: str, month_start: date, month_end: date):
    DATA.mkdir(parents=True, exist_ok=True)
    stem = f"{side}_{month_start:%Y%m}"
    path = DATA / f"{stem}.csv"
    logs = []
    cmd = [
        "npx", "--yes", "dukascopy-node",
        "-i", "eurusd", "-from", month_start.isoformat(), "-to", month_end.isoformat(),
        "-t", "m1", "-p", side, "-utc", "0", "-f", "csv", "-fl",
        "-dir", str(DATA), "-fn", stem, "-bs", "3", "-bp", "2000", "-r", "5", "-rp", "5000",
    ]
    env = os.environ.copy()
    if PATCH.is_file():
        env["NODE_OPTIONS"] = (env.get("NODE_OPTIONS", "") + f" --require={PATCH.resolve()}").strip()
    last_error = "no attempt"
    for attempt in range(1, 4):
        path.unlink(missing_ok=True)
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  text=True, check=False, env=env, timeout=900)
            log = proc.stdout or ""
            size = path.stat().st_size if path.exists() else 0
            last_error = f"exit={proc.returncode}, bytes={size}, log={log[-2000:]}"
            if proc.returncode == 0 and path.is_file() and size > 20:
                with path.open("r", encoding="utf-8-sig", newline="") as f:
                    reader = csv.reader(f)
                    header = next(reader, None)
                    sample = next(reader, None)
                    if header and sample and len(header) >= 5 and len(sample) >= 5:
                        logs.append({"side": side, "month": month_start.strftime("%Y-%m"),
                                     "attempt": attempt, "bytes": size})
                        print(f"OK {side} {month_start:%Y-%m} bytes={size} attempt={attempt}", flush=True)
                        return path, logs
            if "Request returned an empty dataset" in log:
                last_error += "; empty response"
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        if attempt < 3:
            time.sleep(attempt * 4)
    raise RuntimeError(f"DOWNLOAD_FAILED side={side} month={month_start:%Y-%m} after 3 tries: {last_error}")


def detect_timestamp(value: str):
    s = str(value).strip()
    try:
        n = float(s)
        # Dukascopy CSV timestamps may be epoch milliseconds or seconds.
        import datetime
        unit = 0.001 if abs(n) >= 1e11 else 1.0
        return datetime.datetime.fromtimestamp(n * unit, tz=datetime.timezone.utc)
    except Exception:
        import datetime
        s = s.replace("Z", "+00:00")
        try:
            dt = datetime.datetime.fromisoformat(s)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=datetime.timezone.utc)
            return dt.astimezone(datetime.timezone.utc)
        except Exception:
            return None


def combine_and_compress(side: str, files: list[Path]):
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / f"eurusd_{side}_M1_2016-2025.csv.gz"
    header = None
    row_count = 0
    bad_ts = 0
    min_ts = None
    max_ts = None
    seen = set()
    duplicate_count = 0
    with gzip.open(final, "wt", encoding="utf-8", newline="", compresslevel=6) as gout:
        writer = None
        for path in files:
            with path.open("r", encoding="utf-8-sig", newline="") as fin:
                reader = csv.reader(fin)
                this_header = next(reader, None)
                if not this_header:
                    continue
                if header is None:
                    header = this_header
                    writer = csv.writer(gout, lineterminator="\n")
                    writer.writerow(header)
                    lower = [x.strip().lower() for x in header]
                    ti = next((lower.index(k) for k in ("timestamp", "datetime", "date") if k in lower), 0)
                elif [x.strip().lower() for x in this_header] != [x.strip().lower() for x in header]:
                    raise RuntimeError(f"CSV header mismatch in {path}: {this_header} != {header}")
                for row in reader:
                    if not row or len(row) < len(header):
                        continue
                    dt = detect_timestamp(row[ti])
                    if dt is None:
                        bad_ts += 1
                        continue
                    # Enforce the labelled month interval to avoid boundary duplicates from inclusive APIs.
                    month_key = path.stem[-6:]
                    year, month = int(month_key[:4]), int(month_key[4:])
                    lo = dt.replace(year=year, month=month, day=1, hour=0, minute=0, second=0, microsecond=0)
                    next_month = date(year + (month == 12), 1 if month == 12 else month + 1, 1)
                    hi = __import__("datetime").datetime(next_month.year, next_month.month, next_month.day,
                            tzinfo=__import__("datetime").timezone.utc)
                    import datetime
                    lo = datetime.datetime(year, month, 1, tzinfo=datetime.timezone.utc)
                    if dt < lo or dt >= hi:
                        continue
                    key = dt.isoformat()
                    if key in seen:
                        duplicate_count += 1
                        continue
                    seen.add(key)
                    writer.writerow(row[:len(header)])
                    row_count += 1
                    if min_ts is None or dt < min_ts:
                        min_ts = dt
                    if max_ts is None or dt > max_ts:
                        max_ts = dt
    if row_count == 0:
        raise RuntimeError(f"No valid timestamps emitted for {side}")
    digest = hashlib.sha256(final.read_bytes()).hexdigest()
    return {"file": final.name, "bytes": final.stat().st_size, "rows": row_count,
            "duplicate_timestamps_removed_while_combining": duplicate_count,
            "unparseable_timestamps_skipped": bad_ts,
            "start_utc": min_ts.isoformat() if min_ts else None, "end_utc": max_ts.isoformat() if max_ts else None,
            "sha256_gzip_file": digest}


def main():
    all_downloads = {"bid": [], "ask": []}
    monthly_log = []
    for side in ("bid", "ask"):
        for start, end in month_ranges(START, END_EXCLUSIVE):
            path, logs = download_month(side, start, end)
            all_downloads[side].append(path)
            monthly_log.extend(logs)
    manifest = {
        "status": "DATA_DOWNLOAD_COMPLETE",
        "task": "raw EURUSD M1 BID/ASK market data collection only; no backtest performed in this job",
        "source_feed": "Dukascopy through dukascopy-node",
        "instrument": "EURUSD",
        "timeframe": "M1",
        "requested_window_utc": {"start_inclusive": START.isoformat(), "end_exclusive": END_EXCLUSIVE.isoformat()},
        "monthly_requests": len(monthly_log),
        "downloads": monthly_log,
        "outputs": {side: combine_and_compress(side, paths) for side, paths in all_downloads.items()},
        "important_scope_note": "This is a new historical BID/ASK feed for local testing; it is not represented as the missing original HistData/spread archive used in prior R189 summary figures.",
    }
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "monthly_requests": manifest["monthly_requests"],
                      "outputs": manifest["outputs"], "manifest": str(OUT / "manifest.json")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
