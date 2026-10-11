# R214 local execution package

This experiment was executed in local Python using the downloaded R205 H1/M5 snapshot. No new GitHub Actions backtest was launched.

The exact engine and full 343-row selected trade ledger are provided in the downloadable local execution bundle. This repository branch contains the locked report, discovery-only selection ledger, forward/OOS ledgers, cohorts, data-validation summary and ten-test result.

Inputs are the ten H1/M5 CSV pairs from the R205 snapshot, with `timestamp,open,high,low,close` columns and Unix-millisecond UTC timestamps. The engine uses NumPy, pandas and Numba for local sequential execution.

Costs of 1 and 2 price basis points are modeled stress assumptions on BID-only OHLC, not actual broker/prop execution costs. The verdict is research-only: **REJECT**.