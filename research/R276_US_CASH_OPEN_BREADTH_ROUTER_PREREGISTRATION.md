# R276 — Synchronized US cash-open breakout with breadth router and phone delay

**Status: PREREGISTERED before calculation.**  
**Parents:** R206 US cash-session 30-minute opening-range breakout and R205 cross-index breadth confirmation. This is a pre-registered structural crossover, not a retune of the failed parent thresholds.

## Economic hypothesis
A cash-open breakout may be more reliable when the same-direction breakout is broad across U.S. indices, rather than isolated to a single index. The child only accepts a synchronized first-breakout event when at least three of four index CFDs break their own opening range in the same direction on the same completed M5 bar. Because the user executes from a phone, the model requires an additional five minutes after the signal candle closes.

## Locked universe, rule and execution
- Universe: USA500/S&P 500, USATECH/Nasdaq 100, USA30/Dow Jones, USSC2000/US Small Cap 2000.
- Data: the existing cached Dukascopy M5 BID OHLC snapshots published with R205 (source artifact IDs and hashes will be logged by the runner); these are BID-only screening inputs, not true bid/ask execution.
- For each New York trading date, build the opening range from exact M5 bars opening 09:30, 09:35, 09:40, 09:45, 09:50 and 09:55 America/New_York. Require all six timestamps, at least four non-flat bars, and a positive range.
- A parent signal is the first completed M5 candle after 10:00 ET whose close is strictly above the opening-range high (long) or strictly below the opening-range low (short). At most one first signal per index per date.
- Child eligibility: at least 3 of the 4 indices must have their first opening-range breakout on the exact same M5 timestamp and in the same direction. Trade only the participating index signals from that synchronized event; no replacement of a non-participating signal by later same-day signals.
- Timestamps label bar-open. With five-minute candle completion plus five additional minutes of manual latency, child and delayed parent entry must be the exact T+10 minute open. Missing exact timestamps or flat entry bars are skipped; no nearest-bar substitution.
- Stop: opposite edge of that index's opening range. Target: 2R from executable-proxy entry to stop. Stop-first on same-bar ambiguity; opening gaps through stops exit at the worse opening quote; no same-index overlap and one accepted signal per instrument/date. No fixed time exit.
- Costs: subtract 1 and 2 price basis points of entry notional per round trip. This is a transparent modeled stress on BID-only bars, not verified broker charges or real spread/slippage. Convert gross and net outcomes to R based on initial stop distance.
- Run three matched streams: parent ideal T+5 entry for diagnosis only, parent phone-delay T+10, and child breadth-router T+10. Use the same bar data, stop/target and costs.

## Periods and gates
- Discovery: 2017-01-01 through 2021-12-31.
- Historical forward screen: 2022-01-01 through 2025-12-31, with trades crossing the boundary excluded. This period has extensive prior project exposure and is exploratory, not a clean program-level holdout.
- 2026 through common source end is diagnostic only; the same period has been examined elsewhere and cannot establish untouched OOS.
- Record trade count and net R/PF at 1 and 2 bps, instrument and annual cohorts, risk-normalized drawdown, four-week circular bootstrap of weekly net R at 1 bp, skipped delayed entries, and overlap counts.
- Promotion gates for this child: >=100 discovery and >=100 exploratory-forward closes; discovery PF >=1.00 at 2 bps; forward PF >=1.10 at 1 bp and >=1.05 at 2 bps; every forward year with >=5 trades PF >=1.00 at 1 bp; weekly four-week block-bootstrap 95% lower bound for forward mean weekly net R >0. The child must also improve forward expectancy and challenge-target proxy relative to the T+10 parent without increasing loss-rule breach.
- Do not select a replacement by forward or 2026 results. No parameter tuning after outcomes. If any primary gate fails, verdict is GAGAL and no funded-readiness promotion is allowed.

## Output
Store the runner, compact JSON, trade ledger and readable verdict in the active research branch. Data acquisition and calculations run locally; no new GitHub Actions backtest workflow is required.
