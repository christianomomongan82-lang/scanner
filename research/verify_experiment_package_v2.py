#!/usr/bin/env python3
"""Fail-closed preflight/closeout validator for Proyek backtest experiment packages."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
PREOUTCOME_REQUIRED_FILES = {
    "registration.md", "registration.json", "runner.py", "config.json",
    "environment.txt", "run.sh", "data_manifest.json", "data_audit.json",
    "eligibility_skip_audit.csv.gz", "preflight_test_log.txt",
}
CLOSEOUT_REQUIRED_FILES = PREOUTCOME_REQUIRED_FILES | {
    "full_grid.csv.gz", "scorecard.csv", "finalist_trade_ledger.csv.gz",
    "annual_cohort.csv", "weekly_net_r.csv", "results.json", "report.md",
    "run.log", "output_sha256_manifest.json", "rerun_hash_check.json",
}
REGISTRATION_FIELDS = (
    "experiment_id", "family_id", "hypothesis", "registered_at_utc",
    "registration_commit_sha", "registration_commit_utc", "runner_commit_sha",
    "candidate_count", "selection_rule", "discovery_period_utc",
    "confirmation_period_utc", "cost_model", "manual_delay_minutes",
    "falsification_gates", "holdout_status", "data_source_sha256",
    "output_contract_version",
)

class GateError(Exception):
    pass

def parse_utc(value: Any, label: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise GateError(f"{label}: missing UTC timestamp")
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(text)
    except ValueError as exc:
        raise GateError(f"{label}: invalid ISO-8601 timestamp {value!r}") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise GateError(f"{label}: timestamp must include UTC offset")
    return dt.astimezone(timezone.utc)

def load_json(path: Path) -> dict[str, Any]:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise GateError(f"Cannot read JSON {path.name}: {exc}") from exc
    if not isinstance(obj, dict):
        raise GateError(f"{path.name} must contain a JSON object")
    return obj

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def validate_registration(package: Path, phase: str) -> tuple[dict[str, Any], list[str]]:
    issues: list[str] = []
    reg_path = package / "registration.json"
    if not reg_path.is_file():
        raise GateError("Missing registration.json")
    reg = load_json(reg_path)
    for key in REGISTRATION_FIELDS:
        if key not in reg or reg[key] in (None, "", [], {}):
            issues.append(f"registration.json: required field {key!r} is missing/empty")
    try:
        registered = parse_utc(reg.get("registered_at_utc"), "registered_at_utc")
        committed = parse_utc(reg.get("registration_commit_utc"), "registration_commit_utc")
        if committed < registered:
            issues.append("registration_commit_utc predates registered_at_utc")
        if reg.get("first_outcome_compute_at_utc"):
            first_pnl = parse_utc(reg["first_outcome_compute_at_utc"], "first_outcome_compute_at_utc")
            if committed >= first_pnl:
                issues.append("PREREGISTRATION VIOLATION: registration commit is not before first outcome compute")
            if phase == "preflight":
                issues.append("preflight cannot be passed after first_outcome_compute_at_utc is populated")
    except GateError as exc:
        issues.append(str(exc))
    for key in ("registration_commit_sha", "runner_commit_sha"):
        value = reg.get(key)
        if not isinstance(value, str) or len(value) < 7 or not re.fullmatch(r"[0-9a-fA-F]+", value):
            issues.append(f"{key} must be a Git commit SHA")
    data_hash = reg.get("data_source_sha256")
    if not isinstance(data_hash, str) or not SHA256_RE.fullmatch(data_hash):
        issues.append("data_source_sha256 must be a lowercase 64-character SHA-256")
    candidate_count = reg.get("candidate_count")
    if not isinstance(candidate_count, int) or candidate_count < 1:
        issues.append("candidate_count must be a positive integer")
    elif candidate_count > 100:
        justification = reg.get("large_grid_justification")
        nested = reg.get("nested_selection_plan")
        correction = reg.get("multiple_testing_correction")
        if not all(isinstance(x, str) and x.strip() for x in (justification, nested, correction)):
            issues.append("candidate_count >100 requires large_grid_justification, nested_selection_plan and multiple_testing_correction")
    if str(reg.get("holdout_status", "")).upper() not in {"CLOSED", "LOCKED", "UNOPENED"}:
        issues.append("holdout_status must be CLOSED/LOCKED/UNOPENED before the registered gates pass")
    for key in ("selection_rule", "discovery_period_utc", "confirmation_period_utc", "cost_model", "falsification_gates", "output_contract_version"):
        if key not in reg or reg[key] in (None, "", [], {}):
            issues.append(f"registration.json: {key} must be explicitly defined")
    return reg, issues

def read_manifest(package: Path) -> tuple[set[str], list[str]]:
    issues: list[str] = []
    manifest_path = package / "output_sha256_manifest.json"
    if not manifest_path.is_file():
        return set(), ["Missing output_sha256_manifest.json"]
    manifest = load_json(manifest_path)
    entries = manifest.get("files")
    if not isinstance(entries, list):
        return set(), ["output_sha256_manifest.json must contain a files array"]
    listed: set[str] = set()
    for item in entries:
        if not isinstance(item, dict):
            issues.append("manifest entry must be a JSON object")
            continue
        rel = item.get("path")
        digest = item.get("sha256")
        size = item.get("size_bytes")
        if not isinstance(rel, str) or not rel or Path(rel).is_absolute() or ".." in Path(rel).parts:
            issues.append(f"Unsafe/invalid manifest path: {rel!r}")
            continue
        if rel in listed:
            issues.append(f"Duplicate manifest path: {rel}")
            continue
        listed.add(rel)
        if not isinstance(digest, str) or not SHA256_RE.fullmatch(digest):
            issues.append(f"{rel}: invalid SHA-256 in manifest")
            continue
        path = package / rel
        if not path.is_file():
            issues.append(f"{rel}: file in manifest is absent")
            continue
        actual_size = path.stat().st_size
        if size != actual_size:
            issues.append(f"{rel}: size mismatch (manifest={size}, actual={actual_size})")
        actual_hash = sha256_file(path)
        if actual_hash != digest:
            issues.append(f"{rel}: SHA-256 mismatch (manifest={digest}, actual={actual_hash})")
    return listed, issues

def run_gate(package: Path, phase: str) -> dict[str, Any]:
    package = package.resolve()
    if not package.is_dir():
        raise GateError(f"Package directory does not exist: {package}")
    reg, issues = validate_registration(package, phase)
    required = PREOUTCOME_REQUIRED_FILES if phase == "preflight" else CLOSEOUT_REQUIRED_FILES
    for name in sorted(required):
        if not (package / name).is_file():
            issues.append(f"Missing required file: {name}")
    if phase == "closeout":
        early_stop = False
        result_for_closeout = {}
        result_path = package / "results.json"
        if result_path.is_file():
            try:
                result_for_closeout = load_json(result_path)
                early_stop = (
                    str(result_for_closeout.get("verdict", "")).upper() == "GAGAL"
                    and result_for_closeout.get("outcomes_computed") is False
                    and result_for_closeout.get("first_failed_gate") in {
                        "data_gate", "sample_gate", "minimum_sample_gate", "v2_preflight"
                    }
                )
            except GateError as exc:
                issues.append(str(exc))
        if not reg.get("first_outcome_compute_at_utc") and not early_stop:
            issues.append("closeout requires first_outcome_compute_at_utc unless the registered run stopped before outcomes at a named data/sample/preflight gate")
        if early_stop and reg.get("first_outcome_compute_at_utc"):
            issues.append("pre-outcome GAGAL package must leave first_outcome_compute_at_utc empty")
        listed, manifest_issues = read_manifest(package)
        issues.extend(manifest_issues)
        missing_manifest_entries = sorted((CLOSEOUT_REQUIRED_FILES - {"output_sha256_manifest.json"}) - listed)
        if missing_manifest_entries:
            issues.append("Manifest omits required artifact(s): " + ", ".join(missing_manifest_entries))
        if (package / "results.json").is_file():
            try:
                result = load_json(package / "results.json")
                if str(result.get("verdict", "")).upper() not in {"LULUS", "GAGAL"}:
                    issues.append("results.json verdict must be exactly LULUS or GAGAL")
                if not result.get("first_failed_gate") and str(result.get("verdict", "")).upper() == "GAGAL":
                    issues.append("GAGAL result must name first_failed_gate")
                if result.get("outcomes_computed") is False:
                    if str(result.get("verdict", "")).upper() != "GAGAL":
                        issues.append("pre-outcome stop must have verdict GAGAL")
                    if result.get("first_failed_gate") not in {"data_gate", "sample_gate", "minimum_sample_gate", "v2_preflight"}:
                        issues.append("pre-outcome stop must name the first data/sample/preflight gate")
                    if reg.get("first_outcome_compute_at_utc"):
                        issues.append("pre-outcome stop must not claim a PnL outcome computation time")
            except GateError as exc:
                issues.append(str(exc))
        if (package / "rerun_hash_check.json").is_file():
            try:
                rerun = load_json(package / "rerun_hash_check.json")
                if rerun.get("runs_compared", 0) < 2:
                    issues.append("rerun_hash_check.json must compare at least two runs")
                if rerun.get("mismatches") != []:
                    issues.append("rerun_hash_check.json mismatches must be an empty array")
            except GateError as exc:
                issues.append(str(exc))
    return {
        "package": str(package),
        "phase": phase,
        "experiment_id": reg.get("experiment_id"),
        "status": "PASS" if not issues else "BLOCKED",
        "issues": issues,
        "checks": {"required_files": len(required), "sha256_manifest_checked": phase == "closeout"},
    }

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase", choices=("preflight", "closeout"))
    parser.add_argument("package", type=Path)
    args = parser.parse_args()
    try:
        result = run_gate(args.package, args.phase)
    except GateError as exc:
        result = {"package": str(args.package), "phase": args.phase, "status": "BLOCKED", "issues": [str(exc)]}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 2

if __name__ == "__main__":
    raise SystemExit(main())
