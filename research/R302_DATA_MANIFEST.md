# R302 — Data Manifest

## Source

- Source: Dukascopy XAUUSD M5 BID/ASK from pre-existing raw-data collection artifact #12031270051, workflow run #38859918137. The Actions run was data acquisition only; R302 signal and PnL calculations ran locally in Python.
- ZIP SHA-256: `2cde8338800fd7f4d5d4628512201c16757ef06bd90d51ffdc8ef9bea425ba1a`
- BID gzip member SHA-256: `b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575`
- ASK gzip member SHA-256: `b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9`
- Exact pre-2026 source range: 2016-01-03 00:00 UTC through 2025-12-31 21:55 UTC. Exclusive cutoff: `2026-01-01T00:00:00Z`, applied before any feature/signal/PnL calculations.
- Raw rows: 947,326 per side; before cutoff: 877,930 per side. BID/ASK timestamps paired exactly; 0 duplicate timestamps, 0 invalid OHLC rows, 0 negative open/close spreads. Missing time-grid cells were not synthesized.
- Session source: local `Europe/London` timezone conversion with DST. The strategy used a scheduled-clock weekday proxy; the historical official IBA auction non-publication calendar was not applied. This is an explicit limitation and independently blocks opening the reserved 2026 test.

## Output checksums (original local CSV/JSON bytes)

| File | SHA-256 | Size |
|---|---|---:|
| `R302_FINAL_REPORT.md` | `c4cdc7456cb29c4cc1c23f7a2c2b5db944f0ec0aaf67f9855e0b7f18cc448b82` | 3,516 B |
| `R302_all_cost_delay_streams_and_skips.csv` | `3dcb874f70c64c3704b311aea4753f2dba9655c8f985f5ab0d7cff370999e683` | 1,537,582 B |
| `R302_all_valid_trade_ledger.csv` | `d0b2138af8096157e0343fda60d19760b9e7bd34615ce924850f245cbf42d910` | ~1.5 MB |
| `R302_data_audit.json` | `44b0af48201cc3e3b4b1822d72afa2e53634b23e3daa47f1de2a229b9e48e47b` | 1,531 B |
| `R302_period_annual_summary.csv` | `22660c3d492bc150b5f83c1e9bb1f094a50f49a2906bbb04ab889667d4b62bfe` | 24,912 B |
| `R302_preoutcome_eligibility_audit.csv` | `d66a6762f3a59e282078fdf69dd1646d5ad2a930bc6cd92562cd4eb871f3a3a3` | 288,734 B |
| `R302_primary_cost_trade_ledger.csv` | `43d31c21186e679e3e463e092ddbd40cca5a20382c3632d52b5b639314394903` | 126,330 B |
| `R302_results_compact.json` | `74d42af3a74c409c4c80e5a63ea9a2a812c003810a13cd84e38aaeb9e3bb1dc7` | 7,202 B |
| `R302_validation_weekly_bootstrap.json` | `c591f8a47f2bf06f77328ef4b47572e4f716a181c4c42f944530295ae4510098` | 19,950 B |
| `R302_validation_weekly_net_R.csv` | `bab94673497feb2fb9009bf997ae412346cb3ec1e0c0a2e9b43036ab38440056` | 6,224 B |

## Repository completeness limitation

Compact results, report, core data-integrity statistics, period/annual summary, weekly bootstrap summary and the 262-week bootstrap input CSV are committed in this branch. The original multi-configuration trade/skip ledger and full pre-outcome event audit were generated and checksummed in the local execution environment but are **not yet stored as row-level files in GitHub**. Their checksums above are supplied for integrity, not as a claim that the repo is fully self-contained. Repository-only reproduction of every row is therefore incomplete until these larger ledgers are transferred into GitHub or the raw data archive is reacquired and the runner is rerun.


## Exact output replay check — 2026-10-20

The locked local runner was rerun against source members whose BID/ASK SHA-256 matched the values above. Its expanded implementation SHA-256 matched the pinned value `646d2c552ab5855af6bbaa0e683ecc34cc707230cadea1e3e02bcada2fee8bdc`. The four detailed CSVs listed in the missing-row-artifact section were regenerated locally and their exact byte sizes and SHA-256 values match the original output manifest; counts are 387 primary trades, 2,336 eligibility-audit rows, 4,644 all-variant/skip rows, and 4,638 valid variant rows. The local runner completed in 26.53 seconds.

This confirms reproducibility, not repository completeness: the four CSVs remain absent from the active GitHub tree until their bytes are transferred. See [ledger reassembly notes](R302_LEDGER_REASSEMBLY.md). The candidate remains GAGAL and protected 2026 remains unopened.
