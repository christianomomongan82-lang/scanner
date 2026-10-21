#!/usr/bin/env python3
"""Restore and verify the reconstructed R311 row-level eligibility/trade ledger.

Run from any directory:
  python research/ledgers/restore_r311_reconstructed_ledger.py --output-dir /tmp/r311-ledger

The checked-in .b64 fragments are GitHub-blob-SHA1 pinned individually. The
decoded gzip and uncompressed CSV are then SHA-256 pinned. This file restores
the reconstructed evidence ledger; it does not claim byte identity with an
unavailable original R311 output.
"""
from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
from pathlib import Path

PARTS = [
    ("R311_reconstructed_event_eligibility_and_trades.csv.gz.b64.part00", 12000, "ec929fedf3bf43e7c9a91edca8c168b8bbdf4168"),
    ("R311_reconstructed_event_eligibility_and_trades.csv.gz.b64.part01", 12000, "abcbcf755a4a6271785c8a79f057ff10d33f96ad"),
    ("R311_reconstructed_event_eligibility_and_trades.csv.gz.b64.part02", 12000, "e1010c771c2cc09a795531f83f3ff5d1f2c99d2c"),
    ("R311_reconstructed_event_eligibility_and_trades.csv.gz.b64.part03a0", 3000, "cde070b30338ecb7ea76209ad1f945fcf97367b0"),
    ("R311_reconstructed_event_eligibility_and_trades.csv.gz.b64.part03a1", 3000, "1e312351bf60c5df6de033450d12d3fd4a7d74bf"),
    ("R311_reconstructed_event_eligibility_and_trades.csv.gz.b64.part03b", 6000, "79b44e172323ead808ab2db6aaddbcc635440b64"),
    ("R311_reconstructed_event_eligibility_and_trades.csv.gz.b64.part04", 12000, "fc486efe11c7f022ebc4dccf6d3f3de049994ea7"),
    ("R311_reconstructed_event_eligibility_and_trades.csv.gz.b64.part05", 12000, "8890b794cdcc6206dfcebb785d3e89ea0fd2a270"),
    ("R311_reconstructed_event_eligibility_and_trades.csv.gz.b64.part06", 12000, "09788f14b8bf54556742063f9a61decbed12b280"),
    ("R311_reconstructed_event_eligibility_and_trades.csv.gz.b64.part07", 6184, "516fb026e09b33f8ec49841792f50a395dc6b961"),
]
EXPECTED_B64_LEN = 90184
EXPECTED_GZIP_SHA256 = "e6c4e60f82703f37d83e9f7078612577e046e7c4545f054eb7aef4148846dfa2"
EXPECTED_CSV_SHA256 = "bb98d010e2dfcabd6ea34908c1d167ce864f0d36f8ce5c7df0408f247055f5c8"
EXPECTED_CSV_BYTES = 449552
EXPECTED_DATA_ROWS = 2608


def git_blob_sha1(data: bytes) -> str:
    header = f"blob {len(data)}\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", type=Path, default=Path("."))
    args = parser.parse_args()
    here = Path(__file__).resolve().parent
    fragments: list[bytes] = []
    for name, expected_len, expected_sha in PARTS:
        payload = (here / name).read_bytes()
        actual_sha = git_blob_sha1(payload)
        if len(payload) != expected_len or actual_sha != expected_sha:
            raise SystemExit(
                f"FAIL {name}: bytes={len(payload)} sha={actual_sha}; "
                f"expected bytes={expected_len} sha={expected_sha}"
            )
        fragments.append(payload)
        print(f"OK {name} bytes={len(payload)} git_blob_sha1={actual_sha}")

    encoded = b"".join(fragments)
    if len(encoded) != EXPECTED_B64_LEN:
        raise SystemExit(f"FAIL base64 length {len(encoded)} != {EXPECTED_B64_LEN}")
    compressed = base64.b64decode(encoded, validate=True)
    gzip_sha = hashlib.sha256(compressed).hexdigest()
    if gzip_sha != EXPECTED_GZIP_SHA256:
        raise SystemExit(f"FAIL gzip SHA-256 {gzip_sha} != {EXPECTED_GZIP_SHA256}")
    csv_bytes = gzip.decompress(compressed)
    csv_sha = hashlib.sha256(csv_bytes).hexdigest()
    if len(csv_bytes) != EXPECTED_CSV_BYTES or csv_sha != EXPECTED_CSV_SHA256:
        raise SystemExit(
            f"FAIL CSV bytes={len(csv_bytes)} sha256={csv_sha}; "
            f"expected bytes={EXPECTED_CSV_BYTES} sha256={EXPECTED_CSV_SHA256}"
        )
    lines = csv_bytes.count(b"\n")
    if lines - 1 != EXPECTED_DATA_ROWS:
        raise SystemExit(f"FAIL row count {lines - 1} != {EXPECTED_DATA_ROWS}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    gz_path = args.output_dir / "R311_reconstructed_event_eligibility_and_trades.csv.gz"
    csv_path = args.output_dir / "R311_reconstructed_event_eligibility_and_trades.csv"
    gz_path.write_bytes(compressed)
    csv_path.write_bytes(csv_bytes)
    print("PASS: all fragments and combined ledger match pinned checksums.")
    print(f"gzip: {gz_path} bytes={len(compressed)} sha256={gzip_sha}")
    print(f"csv:  {csv_path} bytes={len(csv_bytes)} rows={lines - 1} sha256={csv_sha}")


if __name__ == "__main__":
    main()
