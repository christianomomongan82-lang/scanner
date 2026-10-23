# R329 — Seven-pair FX time-series momentum portfolio

**Binary verdict: GAGAL — ECONOMIC SCREEN.** Selected horizon under the frozen discovery selection rule: **13 weeks**. No candidate clears the registered economics gates. No funded challenge replay was run.

## Primary-cost results

Costs are observed executable BID/ASK fills plus $10 round-trip commission per 100,000-base-unit lot, +1 pip slippage per round trip, and the registered adverse swap proxy of 2 pip-equivalents per seven-day holding period.

| Period | Active legs | Active weeks | Net R | PF_R | Bootstrap lower 95% (weekly R) |
|---|---:|---:|---:|---:|---:|
| Discovery 2017–2020 | 1,001 | 143 | -2.606 | 0.862 | -0.0513 |
| Confirmation 2021–2023 | 658 | 94 | -5.283 | 0.651 | -0.0720 |
| Diagnostic 2024–2025 | 371 | 53 | -3.135 | 0.593 | — |

The discovery-selected 13-week setup loses in both discovery and confirmation; the Holm-adjusted discovery p-value is 1.000. Its 26-week and 39-week alternatives also fail both periods. Under the more adverse +2-pip slippage / 4-pip weekly swap proxy, the 13-week results are -5.871 R (PF 0.720) in discovery and -7.643 R (PF 0.538) in confirmation.

## Root cause indicated by the result

The failure is not explained by incremental costs alone. Before extra commission, slippage and swap deductions (but still using executable BID/ASK entry and exit sides), the weighted signal stream was +1.811 R in discovery and **-2.093 R in confirmation**, then -1.155 R in the 2024–2025 diagnostic period. The directional relationship does not persist into confirmation.

The registered annual stability gate also fails: 2018 = -2.345 R, 2019 = -3.676 R, 2020 = +2.742 R; only one of those three complete discovery years is positive.

## Data and execution boundaries

All 14 raw H1 BID/ASK streams were hash-checked against the source manifest. Each has 78,361 rows; the seven-pair exact timestamp intersection also has 78,361 timestamps. The eligibility preflight found 468 common active Tuesday 10:00 UTC snapshots. All three horizons passed the pre-outcome sample gates.

This remains a historical development result, not independent project-level OOS. H1 bars provide a conservative one-hour bar-open entry proxy, not an actual five-minute executable quote. The adverse swap assumptions are proxies, not verified symbol-specific FundedNext swaps. Therefore no challenge replay, pass probability or funded-ready claim is justified.

## Reproducibility note

Two runs using the same local outcome runner produced byte-identical output files. A second source reconstruction matched result JSON, scorecard, annual cohorts, full grid and trade-ledger outputs; its only output difference was an unused `entry_date` column in `weekly_all_configs.csv.gz`. The executed local source hash is not byte-identical to the pinned GitHub runner blob. This source-identity caveat is recorded explicitly; R329 is not promotable and must not be retuned to rescue it.
