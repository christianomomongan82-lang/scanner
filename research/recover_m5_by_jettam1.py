#!/usr/bin/env python3
"""Recover a failed native M5 BID interval using Dukascopy's current official Jetta M1 BID API.

This is a last-resort data-acquisition fallback, never a strategy variant. Before it is
allowed to emit any M5 bars, it must match native M5 OHLC for the same instrument on
an existing overlapping cache day. Only five-minute groups containing all five M1
candles are emitted; partial groups are a hard error and are never synthesized.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
UTC = timezone.utc
OHLC = ["open", "high", "low", "close"]
TIME = "time"
VALIDATION_ATOL = 1e-8


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_manifest(path: Path) -> dict:
    if not path.is_file():
        return {"schema": 1, "recovered_intervals": []}
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(obj, dict):
            raise ValueError("manifest root is not an object")
        obj.setdefault("schema", 1)
        obj.setdefault("recovered_intervals", [])
        return obj
    except Exception as exc:
        raise RuntimeError(f"Cannot read existing recovery provenance file {path}: {exc}") from exc


def write_manifest(path: Path, obj: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    tmp.replace(path)


def as_utc_timestamp(text: str) -> pd.Timestamp:
    t = pd.Timestamp(text)
    if t.tzinfo is None:
        return t.tz_localize("UTC")
    return t.tz_convert("UTC")


def parse_native_m5(path: Path) -> pd.DataFrame:
    from research.r192_ger40 import parse_data
    df, _ = parse_data(path)  # CSV/timestamp adapter only; no R192 calculations are used.
    df = df[OHLC].copy()
    df.index = pd.DatetimeIndex(df.index).tz_convert("UTC")
    return df.sort_index()


def fetch_m1_day(code: str, day: str, client):
    from dukascopy_downloader.decode import decode_candles
    from dukascopy_downloader.timeframes import Chunk

    start = datetime.strptime(day, "%Y-%m-%d").replace(tzinfo=UTC)
    end = start + timedelta(days=1)
    chunk = Chunk("m1", start, end)
    path = chunk.url_path(code, "BID")
    frame = client.get_json(path, parse=lambda payload: decode_candles(payload, start, end))
    if frame is None or frame.empty:
        return pd.DataFrame(columns=[TIME, *OHLC, "volume"])
    frame = frame.copy()
    frame[TIME] = pd.to_datetime(frame[TIME], utc=True, errors="raise")
    frame = frame.sort_values(TIME).drop_duplicates(TIME, keep="last")
    return frame.loc[(frame[TIME] >= pd.Timestamp(start)) & (frame[TIME] < pd.Timestamp(end))]


def aggregate_complete_m5(m1: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    if m1.empty:
        return pd.DataFrame(columns=OHLC, index=pd.DatetimeIndex([], tz="UTC", name=TIME))
    source = m1.set_index(TIME).sort_index()
    source = source.loc[(source.index >= start) & (source.index < end)]
    if source.empty:
        return pd.DataFrame(columns=OHLC, index=pd.DatetimeIndex([], tz="UTC", name=TIME))
    grouped = source["open"].resample("5min", label="left", closed="left").count()
    partial = grouped[(grouped > 0) & (grouped < 5)]
    if len(partial):
        examples = [x.isoformat() for x in partial.index[:5]]
        raise RuntimeError(
            "Jetta M1 contains incomplete five-minute buckets; refusing to infer missing OHLC "
            f"or emit partial M5 bars. Example bins: {examples}"
        )
    out = source[OHLC].resample("5min", label="left", closed="left").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    )
    out = out.loc[grouped == 5].dropna(subset=["open"])
    out.index = pd.DatetimeIndex(out.index).tz_convert("UTC")
    out.index.name = TIME
    return out


def native_cache_candidates(inst: str) -> list[Path]:
    folder = Path("dl/chunks")
    annual = re.compile(rf"^{re.escape(inst)}_m5_\d{{4}}\.csv\.gz$")
    quarterly = re.compile(rf"^{re.escape(inst)}_m5q_\d{{4}}_Q[1-4]\.csv\.gz$")
    files = [
        p for p in folder.glob(f"{inst}_m5*.csv.gz")
        if annual.fullmatch(p.name) or quarterly.fullmatch(p.name)
    ]
    return sorted(files, key=lambda p: p.name, reverse=True)


def validation_candidates(native: pd.DataFrame) -> list[str]:
    counts = pd.Series(1, index=native.index).groupby(native.index.date).sum()
    days = sorted(str(day) for day, count in counts.items() if count >= 50 and day.weekday() < 5)
    if not days:
        return []
    positions = sorted(set([len(days) // 4, len(days) // 2, (3 * len(days)) // 4]))
    return [days[i] for i in positions if 0 <= i < len(days)]


def validate_m1_to_m5(inst: str, code: str, client, manifest: dict) -> dict:
    """Require exact OHLC equivalence on a day available in the native M5 cache."""
    previous = manifest.get("validation")
    if isinstance(previous, dict) and previous.get("status") == "PASS":
        sample = Path("dl/chunks") / str(previous.get("native_file", ""))
        if sample.is_file() and sha256_file(sample) == previous.get("native_sha256"):
            return previous

    failures = []
    for native_file in native_cache_candidates(inst):
        try:
            native = parse_native_m5(native_file)
        except Exception as exc:
            failures.append(f"{native_file.name}: cannot parse native M5 cache: {exc}")
            continue

        for day in validation_candidates(native):
            try:
                m1 = fetch_m1_day(code, day, client)
                start = pd.Timestamp(day, tz="UTC")
                end = start + pd.Timedelta(days=1)
                derived = aggregate_complete_m5(m1, start, end)
                day_mask = np.asarray(native.index.date == start.date())
                native_day = native.loc[day_mask]
                common = native_day.join(derived, how="inner", lsuffix="_native", rsuffix="_jetta")
                if len(common) < 50 or len(common) / max(1, len(native_day)) < 0.95:
                    failures.append(
                        f"{native_file.name} {day}: insufficient overlap "
                        f"{len(common)}/{len(native_day)} native bars"
                    )
                    continue

                equal = np.ones(len(common), dtype=bool)
                for col in OHLC:
                    equal &= np.isclose(
                        common[f"{col}_native"].to_numpy(float),
                        common[f"{col}_jetta"].to_numpy(float),
                        rtol=0.0,
                        atol=VALIDATION_ATOL,
                    )
                if not bool(equal.all()):
                    mismatches = int((~equal).sum())
                    failures.append(
                        f"{native_file.name} {day}: {mismatches}/{len(common)} overlapping OHLC rows differ"
                    )
                    continue

                return {
                    "status": "PASS",
                    "method": "same-instrument Dukascopy Jetta BID M1 aggregated to complete M5 bars",
                    "native_file": native_file.name,
                    "native_sha256": sha256_file(native_file),
                    "sample_day_utc": day,
                    "native_day_rows": int(len(native_day)),
                    "matched_rows": int(len(common)),
                    "matched_fraction": float(len(common) / max(1, len(native_day))),
                    "ohlc_mismatches": 0,
                    "absolute_tolerance": VALIDATION_ATOL,
                    "symbol_code": code,
                }
            except Exception as exc:
                failures.append(f"{native_file.name} {day}: Jetta comparison failed: {exc}")

    tail = "; ".join(failures[-8:])
    raise RuntimeError(
        "HARD STOP: M1-derived M5 equivalence could not be proven against native M5 for "
        f"{inst}; no fallback data will be used. Attempts: {tail}"
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--instrument", required=True)
    parser.add_argument("--start", required=True, help="UTC inclusive start, YYYY-MM-DD")
    parser.add_argument("--end", required=True, help="UTC exclusive end, YYYY-MM-DD")
    parser.add_argument("--output", required=True, help="raw CSV path to write (uncompressed)")
    args = parser.parse_args()

    inst = args.instrument.strip().lower()
    start = as_utc_timestamp(args.start)
    end = as_utc_timestamp(args.end)
    if end <= start:
        raise SystemExit(f"Invalid recovery interval: {start} to {end}")

    manifest_path = Path("dl") / f"{inst}_m5_recovery.json"
    manifest = read_manifest(manifest_path)

    from dukascopy_downloader.client import ApiError, DukascopyClient
    from dukascopy_downloader.instruments import Instruments

    client = DukascopyClient(rate_limit=1.0, max_retries=8, timeout=(10, 60), pool_size=2)
    try:
        instruments = Instruments(client, Path("dl/chunks/.jettam1-instrument-cache"))
        code = instruments.resolve(inst)
        validation = validate_m1_to_m5(inst, code, client, manifest)
        manifest["validation"] = validation

        minute_parts = []
        day = start.normalize()
        while day < end:
            date_text = day.strftime("%Y-%m-%d")
            try:
                minute = fetch_m1_day(code, date_text, client)
            except ApiError as exc:
                # A weekend with no source bars has no M5 candles to recover. Weekday
                # 404s and every other request failure stay a hard stop.
                if exc.status == 404 and day.dayofweek >= 5:
                    minute = pd.DataFrame(columns=[TIME, *OHLC, "volume"])
                    manifest.setdefault("empty_weekend_intervals", []).append(
                        {"date_utc": date_text, "reason": "Jetta M1 API returned HTTP 404 on weekend"}
                    )
                else:
                    raise
            minute_parts.append(minute)
            day += pd.Timedelta(days=1)

        if minute_parts:
            minute = pd.concat(minute_parts, ignore_index=True)
        else:
            minute = pd.DataFrame(columns=[TIME, *OHLC, "volume"])
        if not minute.empty:
            minute = minute.sort_values(TIME).drop_duplicates(TIME, keep="last")
        minute_bytes = minute.to_csv(index=False, lineterminator="\n").encode("utf-8")
        derived = aggregate_complete_m5(minute, start, end)

        # Source absence on a weekday is not treated as a successful recovery.
        if start.dayofweek < 5 and len(derived) < 20:
            raise RuntimeError(
                f"HARD STOP: only {len(derived)} complete M5 bars recovered for weekday interval "
                f"{start}..{end}; refusing incomplete data"
            )

        out_path = Path(args.output)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out = derived.reset_index().rename(columns={TIME: "timestamp"})
        if out.empty:
            out = pd.DataFrame(columns=["timestamp", *OHLC])
        else:
            out["timestamp"] = (pd.to_datetime(out["timestamp"], utc=True).astype("int64") // 1_000_000).astype("int64")
            out = out[["timestamp", *OHLC]]
        out.to_csv(out_path, index=False, lineterminator="\n")

        entry = {
            "start_utc": start.isoformat(),
            "end_utc": end.isoformat(),
            "source": "Dukascopy Jetta API M1 BID aggregated to M5 OHLC",
            "symbol_code": code,
            "m1_rows": int(len(minute)),
            "complete_m5_rows": int(len(derived)),
            "partial_m5_buckets_synthesized": 0,
            "minute_payload_sha256": sha256_bytes(minute_bytes),
            "output_csv_sha256": sha256_file(out_path),
            "equivalence_validation": validation,
        }
        intervals = manifest.setdefault("recovered_intervals", [])
        key = (entry["start_utc"], entry["end_utc"])
        intervals[:] = [
            old for old in intervals
            if (old.get("start_utc"), old.get("end_utc")) != key
        ]
        intervals.append(entry)
        manifest["last_updated_utc"] = datetime.now(UTC).isoformat()
        manifest["instrument"] = inst
        write_manifest(manifest_path, manifest)

        print(json.dumps({
            "status": "RECOVERED",
            "instrument": inst,
            "symbol_code": code,
            "start_utc": start.isoformat(),
            "end_utc": end.isoformat(),
            "m1_rows": len(minute),
            "complete_m5_rows": len(derived),
            "validation": validation,
            "output": str(out_path),
            "output_sha256": entry["output_csv_sha256"],
        }, indent=2))
        return 0
    finally:
        client.close()


if __name__ == "__main__":
    raise SystemExit(main())
