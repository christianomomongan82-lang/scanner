#!/usr/bin/env python3
"""RAW-DATA-ONLY R331 acquisition. No features, events, signals, PnL, or backtest."""
from __future__ import annotations
import csv, gzip, hashlib, json, os, subprocess, time
from datetime import date, datetime, timezone
from pathlib import Path
import pandas as pd

START = date(2023, 10, 23)
END_EXCLUSIVE = date(2026, 10, 23)
ROOT = Path(".")
DATA = ROOT / "dl" / "r331_usatech_m1"
OUT = ROOT / "data_exports" / "r331_usatech_m1"
PATCH = ROOT / "dukascopy_fetch_patch.cjs"
CLI = os.environ.get("DUKASCOPY_NODE_VERSION", "1.50.0")
SYMBOL = "usatechidxusd"


def month_ranges(start: date, end: date):
    cur = start
    while cur < end:
        next_month = date(cur.year + (cur.month == 12), 1 if cur.month == 12 else cur.month + 1, 1)
        yield cur, min(next_month, end)
        cur = next_month


def parse_timestamp(value: str):
    s = str(value).strip()
    try:
        n = float(s)
        if abs(n) >= 1e11:
            return datetime.fromtimestamp(n / 1000, tz=timezone.utc)
        if abs(n) >= 1e9:
            return datetime.fromtimestamp(n, tz=timezone.utc)
    except Exception:
        pass
    try:
        s = s.replace("Z", "+00:00")
        dt = datetime.fromisoformat(s)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except Exception:
        return None


def download_month(side: str, month_start: date, month_end: date):
    DATA.mkdir(parents=True, exist_ok=True)
    stem = f"{side}_{month_start:%Y%m}"
    path = DATA / f"{stem}.csv"
    cmd = [
        "npx", "--yes", f"dukascopy-node@{CLI}",
        "-i", SYMBOL, "-from", month_start.isoformat(), "-to", month_end.isoformat(),
        "-t", "m1", "-p", side, "-utc", "0", "-f", "csv",
        "-dir", str(DATA), "-fn", stem, "-bs", "5", "-bp", "2000", "-r", "5", "-rp", "5000",
    ]
    env = os.environ.copy()
    if PATCH.is_file():
        prior = env.get("NODE_OPTIONS", "").strip()
        env["NODE_OPTIONS"] = (prior + f" --require={PATCH.resolve()}").strip()
    last_error = "no attempt"
    for attempt in range(1, 4):
        path.unlink(missing_ok=True)
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  text=True, check=False, env=env, timeout=900)
            log = proc.stdout or ""
            size = path.stat().st_size if path.exists() else 0
            last_error = f"exit={proc.returncode}; bytes={size}; log={log[-1200:]}"
            if proc.returncode == 0 and path.is_file() and size > 20:
                with path.open("r", encoding="utf-8-sig", newline="") as fin:
                    reader = csv.reader(fin)
                    header, sample = next(reader, None), next(reader, None)
                    if header and sample and len(header) >= 5 and len(sample) >= 5:
                        print(f"OK side={side} month={month_start:%Y-%m} bytes={size} attempt={attempt}", flush=True)
                        return path
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        if attempt < 3:
            time.sleep(attempt * 4)
    raise RuntimeError(f"DOWNLOAD_FAILED side={side} month={month_start:%Y-%m}: {last_error}")


def combine_and_compress(side: str, files: list[Path]):
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / f"usatechidxusd_{side}_M1_20231023_20261022.csv.gz"
    header = None
    seen = set()
    duplicates = bad_timestamps = invalid_ohlc = rows_written = 0
    min_ts = max_ts = None
    columns = {}
    with gzip.open(final, "wt", encoding="utf-8", newline="", compresslevel=6) as gout:
        writer = None
        for path in files:
            with path.open("r", encoding="utf-8-sig", newline="") as fin:
                reader = csv.reader(fin)
                this_header = next(reader, None)
                if not this_header:
                    continue
                norm = [x.strip().lower().replace("\ufeff", "") for x in this_header]
                if header is None:
                    header = this_header
                    writer = csv.writer(gout, lineterminator="\n")
                    writer.writerow(header)
                    columns = {x: norm.index(x) for x in norm}
                    ts_i = next((columns[k] for k in ("timestamp", "datetime", "date") if k in columns), None)
                    if ts_i is None:
                        raise RuntimeError(f"No timestamp column in {path}: {this_header}")
                    for k in ("open", "high", "low", "close"):
                        if k not in columns:
                            raise RuntimeError(f"Missing {k} column in {path}: {this_header}")
                    oi, hi, li, ci = (columns[k] for k in ("open", "high", "low", "close"))
                elif norm != [x.strip().lower().replace("\ufeff", "") for x in header]:
                    raise RuntimeError(f"CSV header mismatch: {path}")
                month_key = path.stem[-6:]
                year, month = int(month_key[:4]), int(month_key[4:])
                lo = datetime(year, month, 1, tzinfo=timezone.utc)
                next_month = date(year + (month == 12), 1 if month == 12 else month + 1, 1)
                month_hi = datetime(next_month.year, next_month.month, next_month.day, tzinfo=timezone.utc)
                for row in reader:
                    if not row or len(row) < len(header):
                        continue
                    dt = parse_timestamp(row[ts_i])
                    if dt is None:
                        bad_timestamps += 1
                        continue
                    if dt < lo or dt >= month_hi or dt.date() < START or dt.date() >= END_EXCLUSIVE:
                        continue
                    key = dt.isoformat()
                    if key in seen:
                        duplicates += 1
                        continue
                    try:
                        op, high, low, close = float(row[oi]), float(row[hi]), float(row[li]), float(row[ci])
                    except Exception:
                        invalid_ohlc += 1
                        continue
                    if not all(pd.notna(x) and abs(x) < float("inf") for x in (op, high, low, close)) or high < max(op, low, close) or low > min(op, high, close):
                        invalid_ohlc += 1
                        continue
                    seen.add(key)
                    writer.writerow(row[:len(header)])
                    rows_written += 1
                    if min_ts is None or dt < min_ts:
                        min_ts = dt
                    if max_ts is None or dt > max_ts:
                        max_ts = dt
    if not rows_written:
        raise RuntimeError(f"No valid rows for {side}")
    return {
        "file": final.name, "bytes": final.stat().st_size,
        "sha256_gzip_file": hashlib.sha256(final.read_bytes()).hexdigest(),
        "rows": rows_written, "duplicate_timestamps_removed": duplicates,
        "unparseable_timestamps_skipped": bad_timestamps, "invalid_ohlc_skipped": invalid_ohlc,
        "start_utc": min_ts.isoformat(), "end_utc": max_ts.isoformat(),
    }


def main():
    monthly = {side: [] for side in ("bid", "ask")}
    for side in ("bid", "ask"):
        for start, end in month_ranges(START, END_EXCLUSIVE):
            monthly[side].append(download_month(side, start, end))
    outputs = {side: combine_and_compress(side, paths) for side, paths in monthly.items()}
    manifest = {
        "status": "RAW_DATA_COLLECTION_ONLY",
        "task": "USATECHIDXUSD M1 BID/ASK acquisition for R331; no signals, event labels, features, PnL or backtest",
        "source_feed": "Dukascopy via dukascopy-node",
        "instrument": SYMBOL, "timeframe": "M1", "downloader_version": CLI,
        "requested_window_utc": {"start_inclusive": START.isoformat(), "end_exclusive": END_EXCLUSIVE.isoformat()},
        "synthetic_flat_bars": False, "missing_quote_policy": "retain real gaps; never forward-fill or synthesize flat candles",
        "monthly_download_requests": len(monthly["bid"]) + len(monthly["ask"]),
        "outputs": outputs,
        "important_limitation": "Dukascopy source feed is not exact FundedNext platform quotes; its spread/cost is not claimed as live broker spread."
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
