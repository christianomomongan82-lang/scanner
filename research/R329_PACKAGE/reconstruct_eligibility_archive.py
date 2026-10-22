#!/usr/bin/env python3
"""Reconstruct and SHA-256 verify the deterministic R329 pre-outcome eligibility archive."""
from __future__ import annotations
import argparse, base64, hashlib, json
from pathlib import Path

def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()

def main() -> int:
    p=argparse.ArgumentParser()
    p.add_argument("--chunk-dir",type=Path,default=Path(__file__).resolve().parent/"archive_chunks")
    p.add_argument("--output",type=Path,default=Path(__file__).resolve().parent/"eligibility_skip_audit.csv.gz")
    a=p.parse_args()
    manifest=json.loads((a.chunk_dir/"reconstruction_manifest.json").read_text(encoding="utf-8"))
    parts=[]
    for entry in manifest["parts"]:
        text=(a.chunk_dir/Path(entry["path"]).name).read_text(encoding="ascii")
        if len(text)!=entry["chars"]: raise SystemExit(f"length mismatch: {entry['path']}")
        if sha(text.encode("ascii"))!=entry["sha256"]: raise SystemExit(f"chunk SHA256 mismatch: {entry['path']}")
        parts.append(text)
    encoded="".join(parts)
    if len(encoded)!=manifest["base64_chars"]: raise SystemExit("concatenated base64 length mismatch")
    raw=base64.b64decode(encoded,validate=True)
    if len(raw)!=manifest["reconstructed_bytes"]: raise SystemExit("reconstructed byte count mismatch")
    if sha(raw)!=manifest["reconstructed_sha256"]: raise SystemExit("reconstructed gzip SHA256 mismatch")
    a.output.write_bytes(raw)
    print(json.dumps({"status":"PASS","output":str(a.output),"bytes":len(raw),"sha256":sha(raw),"chunks":len(parts),"outcomes_computed":False,"pnl_computed":False},sort_keys=True,indent=2))
    return 0
if __name__=="__main__": raise SystemExit(main())
