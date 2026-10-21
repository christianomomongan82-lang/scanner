# R312 reproducibility follow-up — 2026-10-21

**Scope:** repository-state correction and an independent local replay of the already-closed R311 rule. This is not a new strategy candidate. No protected 2026 XAUUSD outcomes were opened, and no GitHub Actions backtest was run.

## R302 ledger state correction

The older R312 stop note's wording that R302's detailed ledgers were absent is superseded by the R302 restoration completed on 2026-10-20. The active research branch now contains all four R302 row-level CSVs. Restoration commit: [cd42a9a4c5092ff34705d17580706b6a2ac8628f](https://github.com/christianomomongan82-lang/scanner/commit/cd42a9a4c5092ff34705d17580706b6a2ac8628f). The restoration note records the row counts, byte sizes, and checksums. R302 itself remains **GAGAL**.

## R311 input and local replay verification

- Raw input artifact #11959096102, downloaded and checksum-verified locally: ZIP SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- BID gzip SHA-256: `b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc`.
- ASK gzip SHA-256: `52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b`.
- The exclusive `2022-01-01T00:00:00Z` cutoff was applied before feature/outcome construction. Each quote side has 2,650,553 rows before cutoff; the exact BID/ASK timestamp sets match. Removing 447,771 rows that are static/inactive on at least one side leaves 2,202,782 active paired M1 timestamps and 422,289 fully observed active M5 bars. Missing bars were not synthesized.
- Local environment: pandas 2.2.3, NumPy 2.3.5. A reconstruction from the locked R311 specification independently reproduced the registered aggregate results exactly to the reported precision.

## Reproduced R311 results

| Stream | Trades | Net R | PF_R |
|---|---:|---:|---:|
| T+5, +1 pip, discovery 2017–2020 | 750 | -360.8429858455 | 0.3444750654 |
| T+5, +1 pip, validation 2021 | 143 | -73.7993088584 | 0.3160645243 |
| T+5, zero extra cost, discovery 2017–2020 | 750 | -75.9813920562 | 0.8041793604 |
| T+5, zero extra cost, validation 2021 | 143 | -13.5841268720 | 0.8183728067 |
| T+5, +2 pips, validation 2021 | 143 | -134.0144908447 | 0.0800607045 |
| T+10 delay, +1 pip, discovery 2017–2020 | 746 | -340.7206992944 | 0.3627296204 |
| T+10 delay, +1 pip, validation 2021 | 143 | -75.2450501069 | 0.3253780863 |

Validation circular four-week bootstrap, 52 calendar weeks including zero-trade weeks, 10,000 resamples, seed 311: mean **-1.4192174780R/week**, 95% interval **[-1.8635392239, -0.9933272762]**. This independently reproduces the committed R311 report.

**Binary strategy verdict remains GAGAL.** The validation result is negative even with zero additional cost, both cost stress and entry-delay stress are negative, and the full bootstrap interval is below zero. R311 must not be inverted, tuned, traded, or promoted to funded replay.

## Exact status—not overstated

Local reconstructed outputs and their SHA-256 values were generated under `/mnt/data/r311_reconstruction/` during this session:
- `R311_reconstructed_event_eligibility_and_trades.csv`: 449,552 bytes; SHA-256 `bb98d010e2dfcabd6ea34908c1d167ce864f0d36f8ce5c7df0408f247055f5c8`.
- `R311_reconstructed_cost_streams.csv`: 1,869,395 bytes; SHA-256 `55ad50973ab38ce0991decd33e80905f66fa3861352c37bdf93122155705fab2`.
- `R311_reconstructed_validation_weekly_net_R.csv`: 1,574 bytes; SHA-256 `ae6894121e31167ad46b0599141ec3eebb27624108d7b3bf5e1a2e8b179dd786`.
- `R311_reconstruction_summary.json`: 2,576 bytes; SHA-256 `6728dac272bec4a50754f8de45319ad296c0682cce7f1af5830004bd3b1f23b6`.

These are independently reconstructed outputs, not byte-for-byte copies of the missing original local outputs; row-by-row comparison against an original R311 trade ledger is not possible until that reference ledger is restored. Thus **aggregate reproduction passes; repository storage / exact row-level identity remains an open gate**. Do not describe R311 as fully repository-self-contained, and do not claim it passed a funded challenge.

## Resume gate

The common funded challenge simulator and paired BID/ASK source adapter pass their committed synthetic/integration tests (35 total in CI run [39412962243](https://github.com/christianomomongan82-lang/scanner/actions/runs/39412962243)); this validates infrastructure only. No strategy currently qualifies for funded-path Monte Carlo. Before resuming new signal search, archive the exact R311 row-level outputs (or formally supersede them with a committed, tested reconstruction), verify the actual intended account's symbol contract sizes, commissions/swaps, and server reset timezone/DST, and keep the protected XAUUSD 2026 sample closed until every pre-2026 gate is cleared.


## Ledger payload persisted — 2026-10-21

The reconstructed 2,608-row eligibility/event ledger is now stored in GitHub as ten base64 payload fragments under `research/ledgers/`. Every fragment's byte count and Git blob SHA-1 was checked against the corresponding local source slice, including the corrected chunk boundaries. The expected assembled base64 length (90,184 chars), gzip hash (67,636 bytes; SHA-256 `e6c4e60f82703f37d83e9f7078612577e046e7c4545f054eb7aef4148846dfa2`) and CSV hash (449,552 bytes; SHA-256 `bb98d010e2dfcabd6ea34908c1d167ce864f0d36f8ce5c7df0408f247055f5c8`) are pinned in the restoration script. See [ledger storage manifest](ledgers/R311_RECONSTRUCTED_LEDGER_STORAGE_MANIFEST.md) and [restore script](ledgers/restore_r311_reconstructed_ledger.py).

**Status correction:** the gate that reconstructed R311 outputs were not committed is closed. The still-unresolved distinction is narrower: the original local output file is unavailable, so exact row-by-row identity against that old file cannot be checked. The committed reconstruction has verifiable provenance and a reproducible restore path. R311 remains **GAGAL** and provides no funded edge.
