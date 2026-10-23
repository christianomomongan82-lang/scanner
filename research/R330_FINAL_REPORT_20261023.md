# R330 Final Report — Multi-asset weekly time-series momentum screen

**Date:** 2026-10-23 UTC
**Binary verdict: GAGAL — ECONOMIC SCREEN.** The frozen specification did not survive confirmation. It is closed and must not be rescued by changing lookback, direction, thresholds or universe on these same outcomes.

## Scope and execution integrity

- Universe: eight FundedNext-listed US stock CFDs (AAPL, AMZN, GOOG, MSFT, NVDA, TSLA, AMD, META) plus BTCUSD and ETHUSD.
- Data: daily underlying-market OHLC aggregates from Massive, 2024-10-23 through 2026-10-22. Stocks are split-adjusted underlying-market bars; crypto uses underlying spot traded-price bars. These are not FundedNext's exact CFD BID/ASK quotes.
- Frozen source runner SHA-256: 35e753efa87e0267652cf83eab8f053b19003c92bad997b44ce7ed2697040d90.
- All ten raw CSVs were retrieved from GitHub and their SHA-256 matched the input manifest. Row counts were eight × 501 stock rows and two × 730 crypto rows; zero duplicate labels or invalid OHLC rows were detected.
- The exact committed JavaScript screen core was executed twice against identical inputs. JSON outputs were byte-identical at SHA-256 646dc2d3ae4766ad149955bdb5c4b87511c45566167a9a8f32f77f80f5c1be39. This is a deterministic screen-runtime result, not the normal local-Python rerun. Python reproduction and exact CFD execution remain mandatory before any possible promotion.
- The ten-instrument universe was frozen by pre-outcome Amendment A after the connected data API rate-limited further requests. No symbols were substituted after inspecting outcomes.

## Primary-proxy results

| Metric | Discovery | Confirmation |
|---|---:|---:|
| Eligible weekly snapshots | 51 | 52 |
| Signal period | 2024-10-25 to 2025-10-10 | 2025-10-24 to 2026-10-16 |
| Compounded primary-net return | 82.83% | -37.41% |
| Compounded stress-net return | 77.52% | -39.86% |
| Mean primary-net return per week | 1.26% | -0.84% |
| Positive-week rate | 58.82% | 36.54% |
| Weekly-contribution profit factor | 2.606 | 0.516 |
| Maximum compounded drawdown | -11.82% | -39.23% |
| Annualized weekly Sharpe (descriptive) | 2.403 | -1.801 |
| 4-week block-bootstrap 95% CI for mean primary-net week | [0.38%, 2.08%] | [-1.66%, -0.02%] |

## Diagnosis

Discovery looked strong (+82.83% cumulative primary-proxy return), but confirmation lost 37.41% compounded, with a weekly profit factor of 0.516, maximum drawdown -39.23%, and a 4-week block-bootstrap 95% interval for the mean primary-net weekly return entirely below zero (-1.66% to -0.02%). The confirmation stress result was -39.86%. This is the exact discovery-to-confirmation reversal the search process was intended to detect.

In confirmation, all eight stock gross contributions were negative in this implementation; BTCUSD and ETHUSD were positive but not enough to offset the stock contributions and cost proxies. That attribution explains this frozen portfolio result; it is not permission to cherry-pick crypto or retune the same dates.

## What this does and does not establish

- It establishes that this **exact frozen R330 rule and ten-instrument portfolio failed the registered economic screen** on the source data and cost proxies.
- It does not establish that every trend strategy, every asset, or trading itself is impossible.
- The data covers only about one year of discovery and one year of confirmation. It is not multi-regime evidence.
- Actual FundedNext CFD bid/ask fills, five-minute alert-to-entry delay, symbol-specific swap/financing and intraday rule-equity paths were not modeled. Therefore this result is not a funded challenge replay and no day-179 pass probability is available.

## Decision

Close R330. Do not invert, change thresholds, drop the losing assets, or use the confirmation period to select a revised basket. The next candidate must be a materially different and externally motivated mechanism, registered before outcome calculation, with reliable execution data and a pre-outcome sample/target-feasibility argument. No challenge account should be started on this evidence.

## Artifacts

- Pre-registration: [R330_MULTI_ASSET_TIMESERIES_MOMENTUM_PREREGISTRATION_20261023.md](R330_MULTI_ASSET_TIMESERIES_MOMENTUM_PREREGISTRATION_20261023.md)
- Amendments: [A — frozen universe](R330_AMENDMENT_A_PREOUTCOME_UNIVERSE_DATA_LIMIT_20261023.md); [B — screen runtime](R330_AMENDMENT_B_SCREEN_EXECUTION_RUNTIME_20261023.md); [C — operational semantics](R330_AMENDMENT_C_OPERATIONAL_SEMANTICS_20261023.md)
- Raw data: [input manifest](R330_DATA/R330_INPUT_MANIFEST_20261023.md)
- Exact core: [r330_screen_core.js](R330_DATA/r330_screen_core.js)
- Full output, scorecard and row-level ledgers are stored alongside this report; hashes are listed in the output manifest.