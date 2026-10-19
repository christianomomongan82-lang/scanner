# R302 — Ledger Reassembly / Reproducibility Notes

## Exact local output artifacts

The complete local execution produced the following byte-exact files, with SHA-256 values recorded in [R302 data manifest](R302_DATA_MANIFEST.md):

- `R302_primary_cost_trade_ledger.csv`: all primary-cost ($0.30/oz), baseline-delay candidate trade rows; 126,330 bytes, 388 CSV lines including header.
- `R302_preoutcome_eligibility_audit.csv`: per-event pre-outcome screening/skip audit; 288,734 bytes, 2,337 CSV lines including header.
- `R302_all_cost_delay_streams_and_skips.csv`: all variants across registered cost/delay sensitivities plus skip rows; 1,537,582 bytes, 4,645 CSV lines including header.
- `R302_all_valid_trade_ledger.csv`: all valid trades across registered sensitivity streams; approximately 1.5 MB, 4,639 CSV lines including header.

The compact JSON and summary/bootstrap artifacts are committed in GitHub. The weekly validation input `R302_validation_weekly_net_R.csv` is committed exactly as a 262-calendar-week series, preserving zero-trade weeks.

## Important status

The three large detailed CSV files listed above (primary ledger, pre-outcome event audit, and all-cost/delay audit) have not yet been transferred as row-level GitHub files. They are present in the local run output and have a documented SHA-256 digest. Do not describe repository-only reconstruction as complete. The runner bootstrap and data manifest preserve the exact strategy rules, raw archive provenance and integrity checks, while the compact result is sufficient for the binary verdict but not a substitute for those large row-level artifacts.

If the source-member archive is available locally again, rerun the saved R302 bootstrap locally and compare each output file against the hashes in [R302_DATA_MANIFEST.md](R302_DATA_MANIFEST.md). Do not calculate any 2026 outcomes or reopen the protected interval to salvage this failed candidate.
