#!/usr/bin/env python3
"""Raw XAUUSD M5 BID/ASK acquisition only. No signals, PnL or backtest logic."""
from __future__ import annotations
import csv, gzip, hashlib, json, os, subprocess, time
from datetime import date, datetime, timezone
from pathlib import Path

START = date(2016, 1, 1)
END_EXCLUSIVE = date(2026, 10, 16)  # newest complete UTC day available at collection start
ROOT = Path(".")
DATA = ROOT / "dl" / "xauusd_m5_2016_2026"
OUT = ROOT / "data_exports" / "xauusd_m5_2016_2026"
PATCH = ROOT / "dukascopy_fetch_patch.cjs"
CLI = os.environ.get("DUKASCOPY_NODE_VERSION", "1.50.0")


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
    last_error = "no attempt"
    cmd = [
        "npx", "--yes", f"dukascopy-node@{CLI}",
        "-i", "xauusd", "-from", month_start.isoformat(), "-to", month_end.isoformat(),
        "-t", "m5", "-p", side, "-utc", "0", "-f", "csv", "-fl",
        "-dir", str(DATA), "-fn", stem, "-bs", "5", "-bp", "2000", "-r", "5", "-rp", "5000",
    ]
    env = os.environ.copy()
    if PATCH.is_file():
        prior = env.get("NODE_OPTIONS", "").strip()
        env["NODE_OPTIONS"] = (prior + f" --require={PATCH.resolve()}").strip()
    for attempt in range(1, 4):
        path.unlink(missing_ok=True)
        try:
            proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                  text=True, check=False, env=env, timeout=900)
            log = proc.stdout or ""
            size = path.stat().st_size if path.exists() else 0
            last_error = f"exit={proc.returncode}, bytes={size}, log={log[-1600:]}"
            if proc.returncode == 0 and path.is_file() and size > 20:
                with path.open("r", encoding="utf-8-sig", newline="") as f:
                    reader = csv.reader(f)
                    header, sample = next(reader, None), next(reader, None)
                    if header and sample and len(header) >= 5 and len(sample) >= 5:
                        print(f"OK side={side} month={month_start:%Y-%m} rows_file_bytes={size} attempt={attempt}", flush=True)
                        return path
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
        if attempt < 3:
            time.sleep(4 * attempt)
    raise RuntimeError(f"DOWNLOAD_FAILED side={side} month={month_start:%Y-%m}: {last_error}")


def parse_timestamp(value: str):
    s = str(value).strip()
    try:
        n = float(s)
        if abs(n) >= 1e11:  # epoch milliseconds
            return datetime.fromtimestamp(n / 1000, tz=timezone.utc)
        if abs(n) >= 1e9:   # epoch seconds
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


def combine_and_compress(side: str, files: list[Path]):
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / f"xauusd_{side}_M5_2016-2026.csv.gz"
    header = None
    ti = 0
    row_count = bad_ts = duplicates = 0
    min_ts = max_ts = None
    seen = set()
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
                month_key = path.stem[-6:]
                year, month = int(month_key[:4]), int(month_key[4:])
                lo = datetime(year, month, 1, tzinfo=timezone.utc)
                next_month = date(year + (month == 12), 1 if month == 12 else month + 1, 1)
                hi = datetime(next_month.year, next_month.month, next_month.day, tzinfo=timezone.utc)
                for row in reader:
                    if not row or len(row) < len(header):
                        continue
                    dt = parse_timestamp(row[ti])
                    if dt is None:
                        bad_ts += 1
                        continue
                    if dt < lo or dt >= hi:
                        continue
                    key = dt.isoformat()
                    if key in seen:
                        duplicates += 1
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
    return {
        "file": final.name, "bytes": final.stat().st_size,
        "sha256_gzip_file": hashlib.sha256(final.read_bytes()).hexdigest(),
        "rows": row_count, "duplicate_timestamps_removed": duplicates,
        "unparseable_timestamps_skipped": bad_ts,
        "start_utc": min_ts.isoformat() if min_ts else None,
        "end_utc": max_ts.isoformat() if max_ts else None
    }


def main():
    monthly = []
    downloaded = {"bid": [], "ask": []}
    for side in ("bid", "ask"):
        for start, end in month_ranges(START, END_EXCLUSIVE):
            downloaded[side].append(download_month(side, start, end))
            monthly.append({"side": side, "month": start.strftime("%Y-%m")})
    manifest = {
        "status": "RAW_DATA_COLLECTION_ONLY",
        "task": "XAUUSD M5 BID/ASK raw market-data acquisition; no features, signals, PnL, simulation or backtest",
        "source_feed": "Dukascopy through dukascopy-node",
        "instrument": "XAUUSD",
        "timeframe": "M5",
        "requested_window_utc": {"start_inclusive": START.isoformat(), "end_exclusive": END_EXCLUSIVE.isoformat()},
        "downloader_version": CLI,
        "monthly_requests": len(monthly),
        "outputs": {
            side: combine_and_compress(side, paths)
            for side, paths in downloaded.items()
        },
        "important_scope_note": "The 2026 data will be held back by the local analysis workflow until the strategy rule set and acceptance gates are committed. GitHub Actions here only downloads and archives raw data."
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"status": manifest["status"], "monthly_requests": manifest["monthly_requests"],
                      "outputs": manifest["outputs"], "manifest": str(OUT / "manifest.json")}, indent=2), flush=True)


if __name__ == "__main__":
    main()
