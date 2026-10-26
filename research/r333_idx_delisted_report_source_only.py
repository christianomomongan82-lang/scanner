#!/usr/bin/env python3
"""R333 official IDX delisted-report route probe only; no universe selection or PnL."""
from __future__ import annotations

import hashlib
import json
import os
import re
import time
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import requests

ROOT = Path(os.environ["R333_DATA_ROOT"]).resolve()
RUN_ID = str(os.environ.get("GITHUB_RUN_ID", "local"))
RUN_ATTEMPT = str(os.environ.get("GITHUB_RUN_ATTEMPT", "1"))
REQUEST_PATH = Path(os.environ["R333_REQUEST_PATH"]).resolve()
OUT = ROOT / "data/r333/idx_metadata/delisted_report_probe"
MANIFESTS = ROOT / "data/r333/manifests"
WAITS = [10, 30]
MAX_ATTEMPTS = 3
HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "text/html,application/javascript,application/json,application/pdf,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*",
    "Accept-Language": "id-ID,id;q=0.9,en;q=0.8",
    "Referer": "https://block.idx.id/id/perusahaan-tercatat/aktivitas-pencatatan",
}
OFFICIAL_HOSTS = {"block.idx.id", "www.idx.co.id", "idx.co.id"}
FILE_EXTS = (".csv", ".xls", ".xlsx", ".pdf", ".zip", ".json")


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def slug(text: str) -> str:
    text = re.sub(r"[^A-Za-z0-9._-]+", "_", text).strip("._-")
    return text[:120] or "resource"


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[dict[str, str]] = []
        self.scripts: list[str] = []
        self.page_text: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        if tag.lower() == "a" and a.get("href"):
            self.links.append({"href": str(a["href"]), "text": ""})
        if tag.lower() == "script" and a.get("src"):
            self.scripts.append(str(a["src"]))

    def handle_data(self, data: str) -> None:
        if data.strip():
            self.page_text.append(data.strip())


def load_request() -> dict[str, Any]:
    req = json.loads(REQUEST_PATH.read_text(encoding="utf-8"))
    if req.get("data_only") is not True or req.get("pnl_calculation") is not False:
        raise SystemExit("REQUEST_POLICY_REJECTED: this job only fetches official IDX public sources.")
    for resource in req.get("sources", []):
        if not isinstance(resource, dict) or not resource.get("url"):
            raise SystemExit(f"INVALID_SOURCE_ENTRY: expected object with url, got {resource!r}")
        url = str(resource["url"])
        host = (urlparse(url).hostname or "").lower()
        if host not in OFFICIAL_HOSTS:
            raise SystemExit(f"NON_OFFICIAL_SOURCE_REJECTED: host={host} url={url}")
    return req


def official_url(url: str, base: str) -> str | None:
    absolute = urljoin(base, url)
    parsed = urlparse(absolute)
    if parsed.scheme not in ("http", "https") or (parsed.hostname or "").lower() not in OFFICIAL_HOSTS:
        return None
    return absolute


def fetch_one(session: requests.Session, name: str, url: str) -> dict[str, Any]:
    result: dict[str, Any] = {
        "name": name, "requested_url": url, "status": "FAILED",
        "attempts": [], "started_utc": now(),
    }
    response: requests.Response | None = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        started = now()
        try:
            current = session.get(url, timeout=60, allow_redirects=True)
            rec = {
                "attempt": attempt, "started_utc": started, "finished_utc": now(),
                "http_status": current.status_code, "final_url": current.url,
                "content_type": current.headers.get("Content-Type", ""),
                "bytes": len(current.content),
                "error": None if current.status_code == 200 else f"HTTP {current.status_code}: {current.text[:500]}",
            }
            result["attempts"].append(rec)
            print(f"IDX_REPORT_SOURCE name={name} attempt={attempt} http={current.status_code} bytes={len(current.content)} content_type={rec['content_type']}")
            if current.status_code == 200 and len(current.content) > 50:
                response = current
                result.update({
                    "status": "FETCHED", "final_url": current.url,
                    "content_type": rec["content_type"], "bytes": len(current.content),
                    "sha256": sha(current.content),
                })
                break
        except Exception as exc:
            rec = {
                "attempt": attempt, "started_utc": started, "finished_utc": now(),
                "http_status": None, "error_type": type(exc).__name__, "error_message": str(exc),
            }
            result["attempts"].append(rec)
            print(f"IDX_REPORT_SOURCE_ERROR name={name} attempt={attempt} type={type(exc).__name__} error={str(exc)!r}")
        if attempt < MAX_ATTEMPTS:
            delay = WAITS[attempt - 1]
            result["attempts"][-1]["retry_wait_seconds"] = delay
            print(f"IDX_REPORT_RETRY name={name} wait_seconds={delay}")
            time.sleep(delay)

    if response is not None:
        content_type = response.headers.get("Content-Type", "").lower()
        path = urlparse(response.url).path
        suffix = Path(path).suffix.lower()
        if not suffix:
            if "javascript" in content_type or name.endswith("_chunk"):
                suffix = ".js"
            elif "json" in content_type:
                suffix = ".json"
            else:
                suffix = ".html"
        saved = OUT / f"{slug(name)}{suffix}"
        saved.parent.mkdir(parents=True, exist_ok=True)
        saved.write_bytes(response.content)
        result["saved_path"] = str(saved.relative_to(ROOT))
        result["finished_utc"] = now()
        body = response.content
        if "html" in content_type or suffix in (".html", ".htm"):
            decoded = response.text
            parser = LinkParser()
            parser.feed(decoded)
            result["script_srcs"] = sorted(set(parser.scripts))
            links = []
            for item in parser.links:
                normalized = official_url(item["href"], response.url)
                text = item.get("text", "").strip()
                if normalized:
                    links.append({"url": normalized, "text": text})
            result["html_links"] = links[:500]
            result["candidate_file_links"] = [
                x for x in links
                if urlparse(x["url"]).path.lower().endswith(FILE_EXTS)
                or re.search(r"delist|unduh|download|report|laporan|listing.activity", x["url"] + " " + x["text"], re.I)
            ][:250]
            result["visible_text_sample"] = " ".join(parser.page_text)[:3000]
        elif "javascript" in content_type or suffix == ".js":
            decoded = response.text
            patterns = [
                r"GetDelisting", r"data-table", r"delisted-company", r"delisted-stock",
                r"\.xlsx", r"\.xls(?:[?\"'])", r"\.csv", r"\.pdf",
                r"/(?:primary|api|umbraco)/[^\"'\s]{1,260}",
                r"https?://[^\"'\s]{1,500}",
            ]
            hits = []
            for pattern in patterns:
                try:
                    for match in list(re.finditer(pattern, decoded, flags=re.I))[:100]:
                        start, end = match.span()
                        hits.append({"pattern": pattern, "index": start, "snippet": decoded[max(0, start-220):min(len(decoded), end+420)]})
                except re.error:
                    continue
            # Stable unique hits, sorted by position for the saved manifest.
            seen = set()
            unique = []
            for item in sorted(hits, key=lambda x: x["index"]):
                key = (item["index"], item["snippet"])
                if key not in seen:
                    unique.append(item)
                    seen.add(key)
            result["route_and_download_hits"] = unique[:300]
            result["contains_getdelisting"] = "GetDelisting" in decoded
        result["bytes"] = len(body)
        result["sha256"] = sha(body)
    else:
        result["finished_utc"] = now()
        result["final_error"] = result["attempts"][-1] if result["attempts"] else None
    return result


def main() -> int:
    req = load_request()
    OUT.mkdir(parents=True, exist_ok=True)
    MANIFESTS.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    session.headers.update(HEADERS)
    started = now()
    results = []
    for resource in req["sources"]:
        results.append(fetch_one(session, resource["name"], resource["url"]))

    # Discover exact official script URLs from the fetched HTML pages and collect them
    # only if they were explicitly referenced by a fetched official page.
    discovered = []
    for item in results:
        if item.get("status") != "FETCHED" or "html_links" not in item:
            continue
        base = item.get("final_url") or item["requested_url"]
        for src in item.get("script_srcs", []):
            url = official_url(src, base)
            if url:
                discovered.append(url)
    discovered = sorted(set(discovered))
    manifest = {
        "experiment": "R333",
        "purpose": "official IDX delisted-report page and frontend chunk investigation only; no strategy calculations",
        "run_id": RUN_ID, "run_attempt": RUN_ATTEMPT,
        "started_utc": started, "finished_utc": now(),
        "data_only": True, "pnl_calculation": False,
        "sources": results,
        "discovered_official_script_urls": discovered,
        "delisted_records_acquired": False,
        "survivorship_label": "survivorship-biased",
        "interpretation": "HTML/JS route evidence is not a delisted record set. If no actual official delisted rows or file is obtained, the historical universe remains ineligible and alpha remains NOT_TESTED.",
    }
    latest = MANIFESTS / "idx-delisted-report-probe-latest.json"
    immutable = MANIFESTS / f"idx_delisted_report_probe_run_{RUN_ID}_attempt_{RUN_ATTEMPT}.json"
    latest.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    immutable.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    ok = sum(1 for x in results if x.get("status") == "FETCHED")
    print(f"IDX_DELISTED_REPORT_PROBE status={ok}/{len(results)} resources fetched; DELISTED_RECORDS_ACQUIRED=false")
    print(f"IDX_DELISTED_REPORT_MANIFEST={latest.relative_to(ROOT)}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
