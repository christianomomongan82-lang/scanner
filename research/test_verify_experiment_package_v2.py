from __future__ import annotations
import gzip
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from verify_experiment_package_v2 import run_gate, PREOUTCOME_REQUIRED_FILES, CLOSEOUT_REQUIRED_FILES

BASE = {
 "experiment_id":"TEST001", "family_id":"TEST_FAMILY", "hypothesis":"One falsifiable claim",
 "registered_at_utc":"2026-10-21T00:00:00Z", "registration_commit_sha":"abcdef1234567",
 "registration_commit_utc":"2026-10-21T00:01:00Z", "runner_commit_sha":"abcdef9876543",
 "candidate_count":1, "selection_rule":"single frozen rule", "discovery_period_utc":"2016-01-01/2019-01-01",
 "confirmation_period_utc":"2019-01-01/2021-01-01", "cost_model":"paired bid ask + stress",
 "manual_delay_minutes":5, "falsification_gates":["net_R_positive"], "holdout_status":"CLOSED",
 "data_source_sha256":"a"*64, "output_contract_version":"v2", "first_outcome_compute_at_utc":None
}

def build_package(root: Path, phase: str):
    for name in (PREOUTCOME_REQUIRED_FILES if phase == "preflight" else CLOSEOUT_REQUIRED_FILES):
        p=root/name;p.parent.mkdir(parents=True,exist_ok=True)
        if name.endswith(".gz"):
            with p.open("wb") as raw:
                with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as f: f.write(b"timestamp,value\n2026-01-01,0\n")
        elif name.endswith(".json"):
            p.write_text("{}",encoding="utf-8")
        else: p.write_text("artifact\n",encoding="utf-8")
    (root/"registration.json").write_text(json.dumps(BASE),encoding="utf-8")
    (root/"registration.md").write_text("Locked test",encoding="utf-8")
    if phase == "closeout":
        reg=json.loads((root/"registration.json").read_text());reg["first_outcome_compute_at_utc"]="2026-10-21T00:02:00Z"
        (root/"registration.json").write_text(json.dumps(reg),encoding="utf-8")
        (root/"results.json").write_text(json.dumps({"verdict":"GAGAL","first_failed_gate":"discovery_net_R"}),encoding="utf-8")
        (root/"rerun_hash_check.json").write_text(json.dumps({"runs_compared":2,"mismatches":[]}),encoding="utf-8")
        manifest=[]
        for name in sorted(CLOSEOUT_REQUIRED_FILES-{"output_sha256_manifest.json"}):
            p=root/name;manifest.append({"path":name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"size_bytes":p.stat().st_size})
        (root/"output_sha256_manifest.json").write_text(json.dumps({"files":manifest}),encoding="utf-8")

class GateTests(unittest.TestCase):
    def test_preflight_minimum_valid(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);build_package(root,"preflight")
            self.assertEqual(run_gate(root,"preflight")["status"],"PASS")
    def test_grid_over_100_requires_plan(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);build_package(root,"preflight")
            reg=json.loads((root/"registration.json").read_text());reg["candidate_count"]=972
            (root/"registration.json").write_text(json.dumps(reg))
            result=run_gate(root,"preflight")
            self.assertEqual(result["status"],"BLOCKED")
            self.assertTrue(any(">100" in x for x in result["issues"]))
    def test_post_result_card_cannot_pass_preflight(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);build_package(root,"preflight")
            reg=json.loads((root/"registration.json").read_text());reg["first_outcome_compute_at_utc"]="2026-10-21T00:00:30Z"
            (root/"registration.json").write_text(json.dumps(reg))
            self.assertEqual(run_gate(root,"preflight")["status"],"BLOCKED")
    def test_closeout_manifest_passes(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);build_package(root,"closeout")
            self.assertEqual(run_gate(root,"closeout")["status"],"PASS")
    def test_closeout_detects_hash_mismatch(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);build_package(root,"closeout")
            (root/"runner.py").write_text("changed\n")
            result=run_gate(root,"closeout")
            self.assertEqual(result["status"],"BLOCKED")
            self.assertTrue(any("SHA-256 mismatch" in x for x in result["issues"]))

    def test_closeout_allows_registered_sample_gate_failure_before_pnl(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);build_package(root,"closeout")
            reg=json.loads((root/"registration.json").read_text())
            reg["first_outcome_compute_at_utc"]=None
            (root/"registration.json").write_text(json.dumps(reg),encoding="utf-8")
            (root/"results.json").write_text(json.dumps({
                "verdict":"GAGAL","first_failed_gate":"minimum_sample_gate",
                "outcomes_computed":False,
                "reason":"sample gate failed before any PnL was calculated"
            }),encoding="utf-8")
            manifest=[]
            for name in sorted(CLOSEOUT_REQUIRED_FILES-{"output_sha256_manifest.json"}):
                p=root/name
                manifest.append({"path":name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"size_bytes":p.stat().st_size})
            (root/"output_sha256_manifest.json").write_text(json.dumps({"files":manifest}),encoding="utf-8")
            result=run_gate(root,"closeout")
            self.assertEqual(result["status"],"PASS",result["issues"])

    def test_closeout_requires_two_identical_runs(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);build_package(root,"closeout")
            (root/"rerun_hash_check.json").write_text(json.dumps({"runs_compared":1,"mismatches":["x"]}))
            manifest=[]
            for name in sorted(CLOSEOUT_REQUIRED_FILES-{"output_sha256_manifest.json"}):
                p=root/name;manifest.append({"path":name,"sha256":hashlib.sha256(p.read_bytes()).hexdigest(),"size_bytes":p.stat().st_size})
            (root/"output_sha256_manifest.json").write_text(json.dumps({"files":manifest}))
            result=run_gate(root,"closeout")
            self.assertEqual(result["status"],"BLOCKED")
            self.assertTrue(any("at least two runs" in x for x in result["issues"]))

if __name__ == "__main__": unittest.main(verbosity=2)
