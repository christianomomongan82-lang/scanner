# R311 reconstructed ledger payload manifest — 2026-10-21

## Scope and verdict

This is a **reconstructed evidence ledger** for the pre-registered R311 EURUSD Tokyo-fix post-event-reversal experiment. It replaces the missing *local reconstructed-file storage* gate, but it is **not claimed to be byte-identical to an unavailable original R311 row output**. Strategy verdict: **GAGAL**.

## Restore and verify

From repository root:

```bash
python research/ledgers/restore_r311_reconstructed_ledger.py --output-dir /tmp/r311-ledger
```

The script checks each payload fragment's exact byte length and Git blob SHA-1, concatenates them in the declared order, verifies the combined base64 length, validates the decoded gzip SHA-256, decompresses the CSV, and verifies the CSV SHA-256, byte count, and data-row count.

| Output | Size | SHA-256 |
|---|---:|---|
| `R311_reconstructed_event_eligibility_and_trades.csv.gz` | 67,636 bytes | `e6c4e60f82703f37d83e9f7078612577e046e7c4545f054eb7aef4148846dfa2` |
| `R311_reconstructed_event_eligibility_and_trades.csv` | 449,552 bytes | `bb98d010e2dfcabd6ea34908c1d167ce864f0d36f8ce5c7df0408f247055f5c8` |

CSV contains **2,608 data rows** (plus header): eligibility/skip decisions and reconstructed event trade records across 2017–2021. This is the compact reconstruction ledger, not the separately generated 1.87 MB cost-sensitivity stream file.

## Source and result note

Raw paired EURUSD archive ZIP SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. Data cutoff was exclusive at `2022-01-01T00:00:00Z`; later price outcomes remain excluded. Full reproduction metrics and caveats are in [R312 reproducibility follow-up](../R312_REPRODUCIBILITY_FOLLOWUP_20261021.md).

The registered result stays **GAGAL**: validation at T+5 was negative with +1 pip additional cost and remained negative even when that additional cost was set to zero. Storage repair is not a strategy promotion.
