# R243–R250 deep audit

## Independent audit results
- Raw source: 10/10 H1 OHLC files valid; zero duplicate timestamps, off-grid timestamps, malformed OHLC, or non-finite prices.
- Causal prefix checks: 190/190 passed. This includes per-instrument signal/feature recomputation on truncated history and separate full-versus-prefix verification of the cross-index signal.
- Independent trade ledgers: 90/90 passed, comprising 119,234 trade rows.
- Row-level checks include exact source signal timestamp, regenerated signal direction, exact next-H1 entry timestamp, active entry bar, source entry price, correct observed-active-bar exit horizon, source exit timestamp and price, gross PnL formula, modeled cost deductions, period boundaries, side/direction, duplicate signals and non-overlapping positions.
- Failed assertions: 0.

## Discovery-only selection stability
A separate equal-span discovery sensitivity starts at 2018-08-08 13:00 UTC. Candidate selections were stable for R246 (EU50), R248 (Germany 40), R249 (US Small Cap 2000), and R250 (Japan 225). R247 changed from Germany 40 to France 40. R243–R245 still had no eligible asset. This sensitivity did not select assets from forward or OOS performance and did not trigger extra forward tuning.

## Decisions
R243–R245 did not meet the discovery gate on any asset. R246–R250 passed discovery instrument eligibility but failed the locked forward/inferential acceptance gate. Holm-adjusted positive-expectancy p-values were 1.000 for all eight hypotheses.

## Limitations
Raw source is BID-only H1 OHLC. Costs remain modeled. Actual broker/prop-firm spread, commission, financing, slippage, exact contract sizing, platform-timezone mapping, and funded DLL/MLL implementation were not independently verified.