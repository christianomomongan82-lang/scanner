#!/usr/bin/env python3
"""R322 pre-outcome calendar timestamp repair. No prices, signal PnL, or returns are read."""
from __future__ import annotations
import argparse, csv, hashlib, json, zipfile
from collections import Counter
from datetime import datetime, date, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
SOURCE_ZIP_SHA = "a781338fdd1c4ff3660a070e260c395fd3b959581408a70c005b8b9216139e0f"
CSV_SHA = "6fb6481fa4b8cb83b67461d20db757689bf77df2818122fa2a32a2d148e59ebd"
EXPECTED_INPUT = "R322_USD_HIGH_IMPACT_CALENDAR.csv"
STUDY_START = date(2016, 1, 1)
STUDY_END_EXCLUSIVE = date(2025, 4, 8)
SOURCE_TZ_NOTE = "Source timestamp offsets represent Asia/Tehran; local source date is retained for midnight placeholders."

def sha_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def event_clock(name: str):
    n = " ".join(name.casefold().replace("non farm", "non-farm").split())
    # Explicit exclusion prevents ADP from being mistaken for the BLS Employment Situation report.
    if "adp" in n or "minutes" in n or "economic projections" in n or "speak" in n or "testif" in n:
        return None, "OUTSIDE_REGISTERED_EVENT_ALLOWLIST"
    if "fomc press conference" in n:
        return time(14, 30), "FOMC_PRESS_CONFERENCE"
    if "federal funds rate" in n or "fomc statement" in n:
        return time(14, 0), "FOMC_1400"
    if "ism manufacturing pmi" in n or "ism services pmi" in n or "ism non-manufacturing pmi" in n or "jolts job openings" in n:
        return time(10, 0), "SCHEDULE_1000"
    if any(s in n for s in (
        "employment situation", "non-farm employment change", "non-farm payroll",
        "nonfarm payroll", "unemployment rate", "average hourly earnings",
        "employment cost index", "jolts job openings", "cpi", "ppi",
        "pce price index", "personal income", "personal spending", "personal outlays",
        "retail sales", "durable goods", "gdp", "unemployment claims",
        "initial jobless claims", "jobless claims"
    )):
        return time(8, 30), "SCHEDULE_0830"
    return None, "OUTSIDE_REGISTERED_EVENT_ALLOWLIST"

def parse_aware(raw: str):
    try:
        dt = datetime.fromisoformat((raw or "").strip().replace("Z", "+00:00"))
        if dt.tzinfo is None:
            return None
        return dt
    except (ValueError, TypeError):
        return None

def main():
    ap = argparse.ArgumentParser()
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--input-zip", type=Path)
    src.add_argument("--input-csv", type=Path)
    ap.add_argument("--output-dir", required=True, type=Path)
    args = ap.parse_args()
    zip_sha = None
    if args.input_zip:
        raw_zip = args.input_zip.read_bytes()
        zip_sha = sha_bytes(raw_zip)
        if zip_sha != SOURCE_ZIP_SHA:
            raise SystemExit(f"FAIL_CLOSED input ZIP hash mismatch: {zip_sha}")
        with zipfile.ZipFile(args.input_zip) as z:
            if EXPECTED_INPUT not in z.namelist():
                raise SystemExit("FAIL_CLOSED filtered calendar CSV missing from archive")
            raw_csv = z.read(EXPECTED_INPUT)
    else:
        raw_csv = args.input_csv.read_bytes()
    csv_sha = sha_bytes(raw_csv)
    if csv_sha != CSV_SHA:
        raise SystemExit(f"FAIL_CLOSED calendar subset hash mismatch: {csv_sha}")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    reader = csv.DictReader(raw_csv.decode("utf-8-sig").splitlines())
    required = {"DateTime", "Currency", "Impact", "Event", "source_row_index"}
    if not required.issubset(set(reader.fieldnames or [])):
        raise SystemExit("FAIL_CLOSED unexpected calendar CSV schema")
    audits, eligible = [], []
    counters = Counter()
    for row in reader:
        original = row["DateTime"].strip()
        name = row["Event"].strip()
        source_date_text = original[:10]
        reason = ""
        corrected = ""
        mapping = ""
        method = ""
        dt = parse_aware(original)
        try:
            source_date = date.fromisoformat(source_date_text)
        except ValueError:
            source_date = None
        clock, mapping = event_clock(name)
        if row["Currency"].strip().upper() != "USD" or row["Impact"].strip().casefold() not in {
            "high", "high impact", "high impact expected", "3", "3.0"
        }:
            reason = "NOT_USD_HIGH_IMPACT"
        elif clock is None:
            reason = mapping
        elif source_date is None or not (STUDY_START <= source_date < STUDY_END_EXCLUSIVE):
            reason = "SOURCE_DATE_OUTSIDE_LOCKED_WINDOW_OR_INVALID"
        elif dt is None:
            reason = "INVALID_OR_NAIVE_ORIGINAL_TIMESTAMP"
        elif dt.timetz().replace(tzinfo=None) == time(0, 0):
            # Timestamp's time part is a placeholder; retain the original local calendar date.
            mapped_local = datetime.combine(source_date, clock, tzinfo=NY)
            corrected = mapped_local.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
            method = "MIDNIGHT_CLOCK_REPLACED_BY_LOCKED_RELEASE_SCHEDULE"
        else:
            utc_dt = dt.astimezone(timezone.utc)
            eastern = utc_dt.astimezone(NY)
            if eastern.date() != source_date:
                reason = "NONMIDNIGHT_TIMESTAMP_EASTERN_DATE_MISMATCH"
            else:
                expected = datetime.combine(source_date, clock, tzinfo=NY)
                delta_min = abs((eastern - expected).total_seconds()) / 60.0
                if delta_min > 15:
                    reason = "NONMIDNIGHT_TIMESTAMP_CONFLICTS_WITH_LOCKED_RELEASE_SCHEDULE"
                else:
                    corrected = utc_dt.isoformat().replace("+00:00", "Z")
                    method = "ORIGINAL_OFFSET_TIMESTAMP_VALIDATED_AGAINST_LOCKED_RELEASE_SCHEDULE"
        if corrected and not reason:
            episode_row = {
                "source_row_index": row["source_row_index"],
                "source_date_local": source_date_text,
                "original_timestamp": original,
                "event_time_utc": corrected,
                "event_name": name,
                "event_clock_et": clock.strftime("%H:%M"),
                "mapping_key": mapping,
                "timestamp_method": method,
            }
            eligible.append(episode_row)
            counters["accepted_allowlisted_rows"] += 1
            counters[method] += 1
        else:
            counters[reason] += 1
        audits.append({
            "source_row_index": row["source_row_index"],
            "source_date_local": source_date_text,
            "original_timestamp": original,
            "currency": row["Currency"],
            "impact": row["Impact"],
            "event_name": name,
            "locked_event_clock_et": clock.strftime("%H:%M") if clock else "",
            "mapping_key": mapping or "",
            "timestamp_method": method,
            "corrected_event_time_utc": corrected,
            "decision": "KEEP" if corrected and not reason else "EXCLUDE",
            "reason": reason,
        })
    eligible.sort(key=lambda x: (x["event_time_utc"], int(x["source_row_index"])))
    episodes = []
    for e in eligible:
        ep_time = datetime.fromisoformat(e["event_time_utc"].replace("Z", "+00:00"))
        if not episodes:
            episodes.append({"episode_time_utc": e["event_time_utc"], "events": [e]})
            continue
        first = datetime.fromisoformat(episodes[-1]["episode_time_utc"].replace("Z", "+00:00"))
        if ep_time - first <= timedelta(minutes=40):
            episodes[-1]["events"].append(e)
        else:
            episodes.append({"episode_time_utc": e["event_time_utc"], "events": [e]})
    event_fields = ["episode_time_utc", "episode_event_count", "source_row_indices", "event_names", "event_schedule_keys"]
    episode_rows = []
    for ep in episodes:
        episode_rows.append({
            "episode_time_utc": ep["episode_time_utc"],
            "episode_event_count": len(ep["events"]),
            "source_row_indices": "|".join(e["source_row_index"] for e in ep["events"]),
            "event_names": " | ".join(e["event_name"] for e in ep["events"]),
            "event_schedule_keys": "|".join(e["mapping_key"] for e in ep["events"]),
        })
    def write_csv(path: Path, fields, rows):
        with path.open("w", encoding="utf-8", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
            w.writeheader()
            w.writerows(rows)
    audit_path = args.output_dir / "R322_TIMESTAMP_CORRECTION_AUDIT.csv"
    event_path = args.output_dir / "R322_CORRECTED_CALENDAR_EVENTS.csv"
    episode_path = args.output_dir / "R322_CORRECTED_EVENT_EPISODES.csv"
    write_csv(audit_path, list(audits[0].keys()) if audits else [], audits)
    write_csv(event_path, list(eligible[0].keys()) if eligible else [], eligible)
    write_csv(episode_path, event_fields, episode_rows)
    period_counts = Counter()
    for ep in episodes:
        d = datetime.fromisoformat(ep["episode_time_utc"].replace("Z", "+00:00")).date()
        if date(2016,1,1) <= d < date(2019,1,1): period_counts["discovery_2016_2018"] += 1
        elif date(2019,1,1) <= d < date(2021,1,1): period_counts["confirmation_2019_2020"] += 1
        elif date(2021,1,1) <= d < date(2025,4,8): period_counts["diagnostic_2021_2025-04-07"] += 1
        else: period_counts["outside_period_after_correction"] += 1
    manifest = {
        "purpose": "timestamp/coverage preflight only; no prices, signals, returns, PnL, or trade outcomes read",
        "locked_preregistration_amendment": "Amendment A, R322_NEWS_CASCADE_PREREGISTRATION.md",
        "input_mode": "verified_filtered_calendar_csv" if args.input_csv else "verified_calendar_artifact_zip",
        "source_zip_sha256_verified": zip_sha,
        "source_calendar_csv_sha256_verified": csv_sha,
        "source_calendar_rows_audited": len(audits),
        "allowlisted_timestamp_valid_rows": len(eligible),
        "corrected_event_episodes_40m": len(episodes),
        "episode_counts_by_locked_period": dict(period_counts),
        "decisions": dict(counters),
        "source_timezone_note": SOURCE_TZ_NOTE,
        "official_schedule_references": {
            "BLS_Employment_Situation": "https://www.bls.gov/schedule/news_release/empsit.htm",
            "BLS_CPI": "https://www.bls.gov/schedule/news_release/cpi.htm",
            "BLS_selected_releases": "https://www.bls.gov/schedule/2025/",
            "BEA": "https://www.bea.gov/news/schedule/",
            "Census_Retail": "https://www.census.gov/retail/release_schedule.html",
            "ISM": "https://www.ismworld.org/supply-management-news-and-reports/reports/ism-pmi-reports/",
        },
        "outputs": {
            p.name: {"bytes": p.stat().st_size, "sha256": sha_bytes(p.read_bytes())}
            for p in (audit_path, event_path, episode_path)
        },
        "warning": "This is still calendar-data preflight only. A separate locked price/event alignment preflight must pass before any PnL calculation."
    }
    manifest_path = args.output_dir / "R322_TIMESTAMP_PREFLIGHT_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
