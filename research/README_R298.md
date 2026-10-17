# R298 Research — Repository Guide

## Verdict
**GAGAL.** Do not tune or reverse the same signal against 2016–2025, and do not open 2026 for this candidate.

## Browse the results in GitHub
Open [R298_INDEX.md](R298_INDEX.md). It links to the preregistration, final report, machine-readable metrics, annual summary, complete trade ledger, all quality audits, weekly-bootstrap series and the exact runner source. You do not need to download a ZIP to read any of those outputs.

## Runner
The source file is [r298_xauusd_london_sweep_reclaim.py](r298_xauusd_london_sweep_reclaim.py). Run with Python, pandas and NumPy available:

```bash
python r298_xauusd_london_sweep_reclaim.py --data-dir /path/to/r298data --out-dir ./R298_outputs
```

The two inputs expected under `--data-dir` are `xauusd_bid_M5_2016-2026.csv.gz` and `xauusd_ask_M5_2016-2026.csv.gz`. The runner enforces the registered SHA-256 hashes, timestamp pairing, uniqueness, M5 alignment and OHLC ordering. It hard-excludes timestamps at/after 2026-01-01 UTC before candidate construction.

## Source-data availability
The raw paired source ZIP is about 20 MB and is not committed to this repository; see [R298_DATA_MANIFEST.md](R298_DATA_MANIFEST.md) for its original artifact identity, file names and exact hashes. Thus all **research outputs and code** can be inspected in GitHub without download, but an exact rerun still requires those two matching source CSVs.

## Execution limitations
Historical BID/ASK quote replay does not verify actual FundedNext fills, point/contract value, commission, slippage, swaps, margin, floating equity or the two-phase challenge path. No funded equity replay was performed.
