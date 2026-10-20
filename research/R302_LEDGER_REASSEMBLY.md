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


## Exact local replay verified — 2026-10-20

The committed compressed bootstrap was rehydrated locally. After applying its registered gate-key normalization, the expanded runner SHA-256 was exactly `646d2c552ab5855af6bbaa0e683ecc34cc707230cadea1e3e02bcada2fee8bdc`. The runner completed locally against the already-downloaded, hash-verified BID/ASK gzip members (26.53 seconds; no strategy calculation ran in GitHub Actions).

All four previously missing row-level CSV outputs were reproduced byte-for-byte against the original local-output SHA-256 values in the manifest:

| Output | Data rows (header excluded) | Bytes | SHA-256 |
|---|---:|---:|---|
| `R302_primary_cost_trade_ledger.csv` | 387 | 126,330 | `43d31c21186e679e3e463e092ddbd40cca5a20382c3632d52b5b639314394903` |
| `R302_preoutcome_eligibility_audit.csv` | 2,336 | 288,734 | `d66a6762f3a59e282078fdf69dd1646d5ad2a930bc6cd92562cd4eb871f3a3a3` |
| `R302_all_cost_delay_streams_and_skips.csv` | 4,644 | 1,537,582 | `3dcb874f70c64c3704b311aea4753f2dba9655c8f985f5ab0d7cff370999e683` |
| `R302_all_valid_trade_ledger.csv` | 4,638 | 1,527,805 | `d0b2138af8096157e0343fda60d19760b9e7bd34615ce924850f245cbf42d910` |

The regenerated data audit, annual/period summary, weekly bootstrap input/result, compact results and original-run report also match their manifest SHA-256 values. The current committed human-readable report is a later edited version and was not overwritten.

**Strategy status is unchanged: GAGAL.** Discovery remains 179 trades / −32.9644576459R / PF_R 0.6397595; validation remains 208 trades / −26.9914313008R / PF_R 0.7298631; 3 of 8 gates pass. Protected 2026 remains unopened.

**Repository storage is not yet complete:** the exact detailed CSVs now reproduce locally, but the four row-level CSVs still need to be transferred into the active branch. Do not confuse successful reproducibility with successful GitHub storage. No result after the exclusive 2026-01-01 cutoff was calculated.
