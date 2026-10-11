# R216 — UTC cross-sectional daily momentum rotation

The branch holds the exact discovery/forward/OOS source ledger summaries and a runnable engine matching the local bundle.

## Run

Install Python 3.10+, NumPy, and pandas. Preserve/extract the four M5 CSVs from the existing scanner R205 Actions snapshots, then run:

\`python research/r216_cross_sectional_daily_momentum.py --data-dir /path/to/r205_snapshot --out-dir /path/to/r216-results\`

The strategy ranks four US indices by raw 24-hour close-to-close return at 15:55 UTC, enters long the strongest and short the weakest at the following 16:00 UTC open, and closes both legs 24 hours later. Flat endpoints invalidate the scheduled trade. It does not interpolate or forward-fill.

**Decision: REJECT_FORWARD_GATE_FAILED.** The source is BID-only and 1/2 bps are modeled cost stresses, not verified broker/prop costs. Common four-index history starts 2018-08-08 because of US Small Cap data coverage. The full 503/605/119 trade ledgers and automated audit are also included in the local execution ZIP.
