#!/usr/bin/env python3
"""R333 official IDX monthly delisting report sweep. Source acquisition only; no strategy calculations."""
from __future__ import annotations

import csv
import hashlib
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests

DATA_ROOT = Path(os.environ["R333_DATA_ROOT"]).resolve()
REQUEST_PATH = Path(os.environ["R333_REQUEST_PATH"]).resolve()
RUN_ID = str(os.environ.get("GITHUB_RUN_ID", "local"))
RUN_ATTEMPT = str(os.environ.get("GITHUB_RUN_ATTEMPT", "1"))
BASE_URL = "https://block.idx.id/primary/DigitalStatistic/GetApiDataPaginated"
OUT = DATA_ROOT / "data/r333/idx_metadata/delisted_monthly_sweep"
MANIFEST_DIR = DATA_ROOT / "data/r333/manifests"
RETRY_WAITS = [30, 120, 600, 600]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
    "Referer": "https://block.idx.id/id/data-pasar/laporan-statistik/digital-statistic/monthly/corporate-action-of-listed-companies/delisted-company",
}
OFFICIAL_HOST = "block.idx.id"


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def month_range(start: str, end: str) -> list[tuple[int, int]]:
    a = datetime.strptime(start, "%Y-%m")
    b = datetime.strptime(end, "%Y-%m")
    if a > b:
        raise SystemExit(f"INVALID_MONTH_RANGE: start={start} end={end}")
    out = []
    year, month = a.year, a.month
    while (year, month) <= (b.year, b.month):
        out.append((year, month))
        month += 1
        if month == 13:
            year += 1
            month = 1
    return out


def make_url(year: int, month: int, page: int, page_size: int) -> str:
    params = {
        "urlName": "LINK_DELISTING",
        "periodYear": year,
        "periodMonth": month,
        "periodType": "monthly",
        "isPrint": "False",
        "cumulative": "false",
        "pageSize": page_size,
        "pageNumber": page,
        "orderBy": "",
    }
    return BASE_URL + "?" + urlencode(params)


def fetch_page(session: requests.Session, year: int, month: int, page: int, page_size: int) -> dict[str, Any]:
    url = make_url(year, month, page, page_size)
    attempts: list[dict[str, Any]] = []
    for attempt in range(1, len(RETRY_WAITS) + 2):
        started = now()
        try:
            response = session.get(url, timeout=45, allow_redirects=True)
            record: dict[str, Any] = {
                "attempt": attempt, "started_utc": started, "finished_utc": now(),
                "http_status": response.status_code, "final_url": response.url,
                "content_type": response.headers.get("Content-Type", ""),
                "bytes": len(response.content),
                "error": None if response.status_code == 200 else f"HTTP {response.status_code}: {response.text[:500]}",
            }
            attempts.append(record)
            print(f"IDX_DELISTED_MONTH year={year} month={month:02d} page={page} attempt={attempt} http={response.status_code} bytes={len(response.content)}", flush=True)
            if response.status_code == 200:
                try:
                    payload = response.json()
                except Exception as exc:
                    record["json_error"] = f"{type(exc).__name__}: {exc}"
                    payload = None
                if not isinstance(payload, dict) or not isinstance(payload.get("data"), list) or not isinstance(payload.get("meta"), dict):
                    record["schema_error"] = "Expected JSON object with data:list and meta:object."
                else:
                    return {
                        "status": "FETCHED",
                        "url": url,
                        "requested_page": page,
                        "bytes": len(response.content),
                        "sha256": sha(response.content),
                        "content_type": record["content_type"],
                        "payload": payload,
                        "attempts": attempts,
                    }
            # Non-transient 403/404: record exact response and stop; don't hammer the official host.
            if response.status_code in (400, 401, 403, 404, 410):
                break
            if response.status_code == 429 or response.status_code >= 500:
                if attempt <= len(RETRY_WAITS):
                    delay = RETRY_WAITS[attempt - 1]
                    record["retry_wait_seconds"] = delay
                    print(f"IDX_DELISTED_RETRY year={year} month={month:02d} page={page} wait_seconds={delay}", flush=True)
                    time.sleep(delay)
                    continue
            break
        except Exception as exc:
            attempts.append({
                "attempt": attempt, "started_utc": started, "finished_utc": now(),
                "http_status": None, "error_type": type(exc).__name__, "error_message": str(exc),
            })
            print(f"IDX_DELISTED_ERROR year={year} month={month:02d} page={page} attempt={attempt} type={type(exc).__name__} error={str(exc)!r}", flush=True)
            if attempt <= len(RETRY_WAITS):
                delay = RETRY_WAITS[attempt - 1]
                attempts[-1]["retry_wait_seconds"] = delay
                time.sleep(delay)
    return {"status": "FAILED", "url": url, "requested_page": page, "attempts": attempts}


def main() -> int:
    request = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
    if request.get("data_only") is not True or request.get("pnl_calculation") is not False:
        raise SystemExit("REQUEST_POLICY_REJECTED: only source acquisition is permitted.")
    if request.get("source_host") != OFFICIAL_HOST:
        raise SystemExit(f"OFFICIAL_HOST_REJECTED: expected {OFFICIAL_HOST}.")
    start_month = str(request.get("start_month", "2010-01"))
    end_month = str(request.get("end_month", "2026-10"))
    page_size = int(request.get("page_size", 2000))
    if page_size != 2000:
        raise SystemExit(f"PAGE_SIZE_REJECTED: locked page size is 2000, got {page_size}.")
    months = month_range(start_month, end_month)
    if len(months) != int(request.get("expected_month_count", len(months))):
        raise SystemExit(f"MONTH_COUNT_MISMATCH: expected={request.get('expected_month_count')} actual={len(months)}")

    OUT.mkdir(parents=True, exist_ok=True)
    MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update(HEADERS)
    started = now()
    results: list[dict[str, Any]] = []
    all_records: list[dict[str, Any]] = []
    for n, (year, month) in enumerate(months, start=1):
        first = fetch_page(session, year, month, 1, page_size)
        month_result: dict[str, Any] = {
            "month": f"{year:04d}-{month:02d}",
            "request_url": first["url"],
            "status": first["status"],
            "pages": [],
            "records_count": 0,
            "expected_total_items": None,
            "row_count_matches_total_items": False,
            "schema_errors": [],
        }
        if first["status"] != "FETCHED":
            month_result["attempts"] = first["attempts"]
            results.append(month_result)
            print(f"IDX_DELISTED_MONTH_FAILED month={month_result['month']} details={json.dumps(first['attempts'],ensure_ascii=False)}", flush=True)
            continue

        payload = first["payload"]
        meta = payload["meta"]
        try:
            total_items = int(meta["totalItems"])
            returned_page_size = int(meta["pageSize"])
            current_page = int(meta["pageNumber"])
        except (KeyError, TypeError, ValueError) as exc:
            total_items = -1
            returned_page_size = 0
            current_page = 0
            month_result["schema_errors"].append(f"META_PARSE_ERROR: {type(exc).__name__}: {exc}")
        month_result["expected_total_items"] = total_items
        month_result["returned_page_size"] = returned_page_size
        month_result["returned_page_number"] = current_page
        month_result["pages"].append({
            "page": 1, "url": first["url"], "bytes": first["bytes"],
            "sha256": first["sha256"], "row_count": len(payload["data"]),
            "total_items": total_items, "status": "FETCHED",
            "attempts": first["attempts"],
        })
        # Preserve original provider payload byte-for-byte as a JSON value, plus source URL and checksum.
        raw_path = OUT / f"{year:04d}-{month:02d}.json"
        write_json(raw_path, {
            "source_url": first["url"],
            "fetched_utc": now(),
            "source_response_sha256": first["sha256"],
            "source_response_bytes": first["bytes"],
            "payload": payload,
        })
        month_result["raw_saved_path"] = str(raw_path.relative_to(DATA_ROOT))
        month_records = list(payload["data"])

        if total_items < 0 or returned_page_size <= 0 or current_page != 1:
            month_result["status"] = "SCHEMA_INVALID"
            month_result["schema_errors"].append("Missing/invalid pagination metadata.")
        else:
            page_count = (total_items + page_size - 1) // page_size
            for page in range(2, page_count + 1):
                later = fetch_page(session, year, month, page, page_size)
                if later["status"] != "FETCHED":
                    month_result["status"] = "PAGINATION_INCOMPLETE"
                    month_result["pages"].append({
                        "page": page, "url": later["url"], "status": "FAILED",
                        "attempts": later["attempts"],
                    })
                    break
                later_payload = later["payload"]
                later_meta = later_payload["meta"]
                if int(later_meta.get("totalItems", -1)) != total_items or int(later_meta.get("pageNumber", -1)) != page:
                    month_result["status"] = "PAGINATION_INCONSISTENT"
                    month_result["schema_errors"].append(f"Pagination metadata mismatch on page {page}.")
                month_records = list(later_payload["data"])
                month_records.extend(month_records)
                month_result["pages"].append({
                    "page": page, "url": later["url"], "bytes": later["bytes"],
                    "sha256": later["sha256"], "row_count": len(later_payload["data"]),
                    "total_items": total_items, "status": "FETCHED",
                    "attempts": later["attempts"],
                })
                page_path = OUT / f"{year:04d}-{month:02d}_page_{page}.json"
                write_json(page_path, {
                    "source_url": later["url"], "fetched_utc": now(),
                    "source_response_sha256": later["sha256"], "source_response_bytes": later["bytes"],
                    "payload": later_payload,
                })
            if month_result["status"] == "FETCHED" and len(month_records) != total_items:
                month_result["status"] = "ROW_COUNT_MISMATCH"
                month_result["schema_errors"].append(f"Expected {total_items} rows from meta.totalItems; collected {len(month_records)}.")
        # Regardless of any error, preserve rows received to facilitate diagnostic audit.
        month_result["records_count"] = len(month_records)
        month_result["row_count_matches_total_items"] = (total_items >= 0 and len(month_records) == total_items and month_result["status"] == "FETCHED")
        month_result["finished_utc"] = now()
        if month_result["row_count_matches_total_items"]:
            for row in month_records:
                if not isinstance(row, dict):
                    month_result["schema_errors"].append(f"NON_OBJECT_ROW: {row!r}")
                    month_result["status"] = "SCHEMA_INVALID"
                    continue
                required = ["code", "issuerName", "ListingDate", "DeListingDate"]
                missing = [key for key in required if not row.get(key)]
                if missing:
                    month_result["schema_errors"].append(f"ROW_MISSING_FIELDS code={row.get('code')} missing={missing}")
                    month_result["status"] = "SCHEMA_INVALID"
                row_copy = dict(row)
                row_copy["_report_month"] = f"{year:04d}-{month:02d}"
                all_records.append(row_copy)
        results.append(month_result)
        print(f"IDX_DELISTED_MONTH_RESULT month={month_result['month']} status={month_result['status']} rows={month_result['records_count']} expected={month_result['expected_total_items']} ({n}/{len(months)})", flush=True)
        time.sleep(0.15)

    successes = [r for r in results if r["status"] == "FETCHED" and r["row_count_matches_total_items"] and not r["schema_errors"]]
    failures = [r for r in results if r not in successes]
    # Stable de-duplication by reported code, listing date, delisting date, issuer name.
    seen: set[tuple[str, str, str, str]] = set()
    dedup_records: list[dict[str, Any]] = []
    for row in all_records:
        key = (str(row.get("code", "")), str(row.get("ListingDate", "")), str(row.get("DeListingDate", "")), str(row.get("issuerName", "")))
        if key not in seen:
            seen.add(key)
            dedup_records.append(row)
    dedup_records.sort(key=lambda row: (str(row.get("DeListingDate", "")), str(row.get("code", "")), str(row.get("_report_month", ""))))

    csv_path = OUT / "delisted_events_2010-01_to_2026-10.csv"
    columns = ["_report_month", "code", "issuerName", "ListingDate", "LastDate", "DeListingDate", "ListedShares", "MCap", "RegPrice"]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
        writer.writeheader()
        writer.writerows(dedup_records)
    monthly_path = OUT / "monthly_coverage_audit.csv"
    with monthly_path.open("w", newline="", encoding="utf-8") as handle:
        fields = ["month", "status", "expected_total_items", "records_count", "row_count_matches_total_items", "pages_count", "schema_errors"]
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        for result in results:
            writer.writerow({
                "month": result["month"], "status": result["status"],
                "expected_total_items": result["expected_total_items"],
                "records_count": result["records_count"],
                "row_count_matches_total_items": result["row_count_matches_total_items"],
                "pages_count": len(result["pages"]),
                "schema_errors": " | ".join(result["schema_errors"]),
            })

    overall = "COMPLETE" if len(results) == len(months) and not failures and all(r["row_count_matches_total_items"] for r in results) else "INCOMPLETE"
    manifest = {
        "experiment": "R333",
        "purpose": "official IDX monthly delisted-company report sweep only; no strategy calculations",
        "data_only": True, "pnl_calculation": False,
        "source_host": OFFICIAL_HOST,
        "endpoint_template": BASE_URL + "?urlName=LINK_DELISTING&periodYear={year}&periodMonth={month}&periodType=monthly&isPrint=False&cumulative=false&pageSize=2000&pageNumber={page}&orderBy=",
        "run_id": RUN_ID, "run_attempt": RUN_ATTEMPT,
        "started_utc": started, "finished_utc": now(),
        "python_version": sys.version,
        "request": {
            "start_month": start_month, "end_month": end_month, "month_count": len(months),
            "page_size": page_size, "retry_waits_seconds": RETRY_WAITS,
            "non_transient_http": "400/401/403/404/410 are recorded and not hammered; no fallback hosts",
        },
        "overall_status": overall,
        "months_total": len(months),
        "months_success": len(successes),
        "months_failed_or_inconsistent": len(failures),
        "raw_rows_collected_before_deduplication": len(all_records),
        "deduplicated_event_rows": len(dedup_records),
        "unique_ticker_codes": len({str(row.get("code", "")) for row in dedup_records if row.get("code")}),
        "monthly_manifest": results,
        "outputs": {
            "monthly_directory": "data/r333/idx_metadata/delisted_monthly_sweep/",
            "event_csv": str(csv_path.relative_to(DATA_ROOT)),
            "event_csv_sha256": sha(csv_path.read_bytes()),
            "event_csv_rows_including_header": sum(1 for _ in csv_path.open("r", encoding="utf-8")) ,
            "monthly_coverage_csv": str(monthly_path.relative_to(DATA_ROOT)),
            "monthly_coverage_csv_sha256": sha(monthly_path.read_bytes()),
            "monthly_coverage_rows_including_header": sum(1 for _ in monthly_path.open("r", encoding="utf-8")),
        },
        "limitations": [
            "This sweep covers report months from 2010-01 to 2026-10 only; it does not establish coverage before 2010.",
            "Completeness conclusion is conditional on every report month being fetched and internal meta.totalItems/pagination checks passing.",
            "Official report data completeness is not an independent audit of Yahoo OHLCV, point-in-time shares, point-in-time sector, corporate actions or delisting price/exit treatment.",
            "No strategy signals, PnL, PF, returns, or alpha verdict were computed."
        ],
    }
    latest = MANIFEST_DIR / "idx-delisted-monthly-sweep-latest.json"
    immutable = MANIFEST_DIR / f"idx_delisted_monthly_sweep_run_{RUN_ID}_attempt_{RUN_ATTEMPT}.json"
    write_json(latest, manifest)
    write_json(immutable, manifest)
    print(f"R333_DELISTED_SWEEP_STATUS={overall}")
    print(f"R333_DELISTED_SWEEP_MONTHS={len(months)} SUCCESS={len(successes)} FAIL={len(failures)} ROWS={len(dedup_records)}", flush=True)
    return 0 if overall == "COMPLETE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
