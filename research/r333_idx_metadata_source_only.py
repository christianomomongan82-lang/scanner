#!/usr/bin/env python3
"""R333 official IDX listing metadata acquisition only; no signals or PnL."""
from __future__ import annotations
import hashlib, json, os, sys, time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
import requests

DATA_ROOT = Path(os.environ["R333_DATA_ROOT"]).resolve()
RUN_ID = os.getenv("GITHUB_RUN_ID", "local")
RUN_ATTEMPT = os.getenv("GITHUB_RUN_ATTEMPT", "1")
OUT = DATA_ROOT / "data" / "r333" / "idx_metadata"
MANIFEST = DATA_ROOT / "data" / "r333" / "manifests"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
    "Referer": "https://www.idx.co.id/id/data-pasar/data-saham/daftar-saham",
}
SOURCES = [
    ("listed_securities_primary", "https://www.idx.co.id/primary/StockData/GetSecuritiesStock?code=&sector=&board=&start=0&length=2000", "json"),
    ("listed_securities_umbraco", "https://www.idx.co.id/umbraco/Surface/StockData/GetSecuritiesStock?code=&sector=&board=&start=0&length=2000", "json"),
    ("listed_securities_block", "https://block.idx.id/primary/StockData/GetSecuritiesStock?code=&sector=&board=&start=0&length=2000", "json"),
    ("listing_activity_page", "https://www.idx.co.id/id/perusahaan-tercatat/aktivitas-pencatatan", "html"),
    ("listing_activity_block_page", "https://block.idx.id/id/perusahaan-tercatat/aktivitas-pencatatan", "html"),
    ("stock_list_page", "https://block.idx.id/id/data-pasar/data-saham/daftar-saham/", "html"),
]

def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")

def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()

def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

def find_record_arrays(obj: Any) -> list[dict]:
    found: list[dict] = []
    def walk(item: Any) -> None:
        if isinstance(item, dict):
            keys = {str(k).lower() for k in item}
            score = sum(k in keys for k in ("stockcode", "code", "securitycode", "listingdate", "listedshares", "shares", "listingboard", "board"))
            if score >= 2:
                found.append(item)
            for child in item.values():
                walk(child)
        elif isinstance(item, list):
            for child in item:
                walk(child)
    walk(obj)
    return found

def has_stock_codes(obj: Any) -> bool:
    if isinstance(obj, list):
        if obj and all(isinstance(item, dict) for item in obj[:10]):
            keys = {str(k).lower() for item in obj[:10] for k in item.keys()}
            return bool(keys & {"stockcode", "code", "securitycode"}) and bool(keys & {"listingdate", "listedshares", "shares"})
        return any(has_stock_codes(item) for item in obj)
    if isinstance(obj, dict):
        return any(has_stock_codes(value) for value in obj.values())
    return False

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    MANIFEST.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update(HEADERS)
    results: list[dict[str, Any]] = []
    valid_listing = None

    for name, url, kind in SOURCES:
        entry: dict[str, Any] = {
            "name": name, "url": url, "kind": kind,
            "attempts": [], "status": "FAILED", "started_utc": now()
        }
        for attempt in range(1, 4):
            started = now()
            try:
                response = session.get(url, timeout=35, allow_redirects=True)
                body = response.content
                content_type = response.headers.get("Content-Type", "")
                record = {
                    "attempt": attempt, "started_utc": started, "finished_utc": now(),
                    "http_status": response.status_code, "final_url": response.url,
                    "content_type": content_type, "bytes": len(body),
                    "error": None if response.status_code == 200 else f"HTTP {response.status_code}: {response.text[:500]}"
                }
                entry["attempts"].append(record)
                print(f"IDX_SOURCE name={name} attempt={attempt} status={response.status_code} bytes={len(body)} content_type={content_type}")

                if response.status_code == 200 and len(body) > 100:
                    suffix = ".json" if kind == "json" else ".html"
                    raw_path = OUT / f"{name}{suffix}"
                    raw_path.write_bytes(body)
                    entry.update({
                        "status": "FETCHED", "saved_path": str(raw_path.relative_to(DATA_ROOT)),
                        "bytes": len(body), "sha256": sha(body),
                        "content_type": content_type, "final_url": response.url
                    })
                    if kind == "json":
                        try:
                            parsed = response.json()
                            parsed_path = OUT / f"{name}_parsed.json"
                            write_json(parsed_path, parsed)
                            entry["parsed_path"] = str(parsed_path.relative_to(DATA_ROOT))
                            entry["parsed_sha256"] = sha(parsed_path.read_bytes())
                            entry["candidate_record_objects"] = len(find_record_arrays(parsed))
                            if name.startswith("listed_securities") and has_stock_codes(parsed) and valid_listing is None:
                                valid_listing = {
                                    "source": name, "path": str(parsed_path.relative_to(DATA_ROOT)), "url": url,
                                    "candidate_records": len(find_record_arrays(parsed))
                                }
                        except Exception as parse_error:
                            entry["json_parse_error"] = f"{type(parse_error).__name__}: {parse_error}"
                    break
                entry["status"] = "FAILED"
            except Exception as exc:
                entry["attempts"].append({
                    "attempt": attempt, "started_utc": started, "finished_utc": now(),
                    "http_status": None, "error_type": type(exc).__name__, "error_message": str(exc)
                })
                print(f"IDX_SOURCE_ERROR name={name} attempt={attempt} error_type={type(exc).__name__} error={str(exc)!r}")

            if attempt < 3:
                delay = (10, 30)[attempt - 1]
                print(f"IDX_SOURCE_RETRY name={name} wait_seconds={delay}")
                time.sleep(delay)
        entry["finished_utc"] = now()
        results.append(entry)

    overall = "ROSTER_JSON_FOUND" if valid_listing else "IDX_SOURCE_NOT_VERIFIED"
    manifest = {
        "experiment": "R333",
        "purpose": "official IDX listing/delisting metadata acquisition only; no signals/PnL",
        "run_id": RUN_ID, "run_attempt": RUN_ATTEMPT,
        "started_utc": results[0]["started_utc"] if results else now(),
        "finished_utc": now(), "official_domains_only": True,
        "overall_status": overall, "sources": results, "selected_roster": valid_listing,
        "limitations": [
            "Current listing metadata alone is not a historical point-in-time universe.",
            "A current roster does not prove complete delisted coverage or historical shares outstanding.",
            "If delisted names or point-in-time shares/sectors cannot be established, mark any result survivorship-biased/data-inadequate and make no edge claim without an explicit defensible correction."
        ]
    }
    write_json(MANIFEST / "idx-metadata-latest.json", manifest)
    write_json(MANIFEST / f"idx_metadata_run_{RUN_ID}_attempt_{RUN_ATTEMPT}.json", manifest)
    print(f"IDX_METADATA_STATUS={overall}")
    with open(os.getenv("GITHUB_OUTPUT", "/dev/null"), "a", encoding="utf-8") as output:
        output.write(f"roster_status={overall}\n")
    return 0 if valid_listing else 1

if __name__ == "__main__":
    raise SystemExit(main())
