# R214 local execution package

This experiment was executed in local Python using the downloaded R205 H1/M5 snapshot. No new GitHub Actions backtest was launched.

- Engine: [r214_three_bar_impulse_reversal.py](./r214_three_bar_impulse_reversal.py)
- Results and locked verdict: [R214 results report](./R214_three_bar_impulse_reversal_results.md)
- Source/coverage validation: [validation CSV](./R214_three_bar_impulse_reversal_source_validation.csv)
- Discovery selection, forward ledger, annual cohorts and OOS ledger are adjacent in this research folder.
- The full 343-record selected trade ledger, independent test details and exact run outputs are included in the downloadable local execution bundle delivered in the conversation.

## Inputs and requirements

Use the ten H1/M5 CSV pairs from the R205 snapshot with timestamp, open, high, low, close columns and Unix-millisecond UTC timestamps. The engine requires Python 3.11+ with NumPy, pandas and Numba; Numba accelerates the sequential M5 execution scan.

Run command:
python -m pip install numpy pandas numba
python research/r214_three_bar_impulse_reversal.py --data-dir /path/to/r205_snapshot --out ./results/r214

Costs of 1 and 2 price basis points are modeled round-trip stress assumptions on BID-only OHLC, not actual broker/prop spreads, commissions, financing or live slippage. Final verdict: **REJECT**; research-only, not a live/funded readiness claim.
