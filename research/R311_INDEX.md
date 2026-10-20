# R311 — Artifact Index

**Binary verdict: GAGAL.** The preregistered Tokyo-fixing fade is closed; no alpha block retained and no funded challenge replay was run.

- [Locked preregistration](R311_EURUSD_TOKYO_FIX_POST_EVENT_REVERSAL_PREREGISTRATION.md)
- [Local runner bootstrap with source and serialization hashes](r311_eurusd_tokyo_fix.py)
- [Implementation amendment 01 — timestamp-grid correction before PnL](R311_IMPLEMENTATION_AMENDMENT_01.md)
- [Implementation amendment 02 — JSON serialization-only correction](R311_IMPLEMENTATION_AMENDMENT_02.md)
- [Final report](R311_FINAL_REPORT.md)
- [Compact metrics and gate JSON](R311_RESULTS_COMPACT.json)
- [Data / output manifest and explicit repository-gate status](R311_DATA_MANIFEST.md)
- [Master experiment registry through R311](MASTER_SEARCH_LEDGER_R251_R311.csv)
- [Search-family map through R311](SEARCH_FAMILY_MAP_R251_R311.md)
- [Component-block library through R311](COMPONENT_BLOCK_LIBRARY_R251_R311.md)

## Core result

At +1 pip additional round-trip friction, discovery 2017–2020: 750 trades, -360.843R, PF_R 0.3445. Validation 2021: 143 trades, -73.799R, PF_R 0.3161. Both periods are negative even with zero added cost, and the validation weekly bootstrap 95% interval is entirely below zero.

The full local ledger and audits are checksum-identified in the manifest, but the row-level output files are not yet committed/read-back verified on this branch. The repository-artifact gate remains false. 2022–2025 PnL was not calculated; this screen is not pristine OOS and is not funded-ready.
