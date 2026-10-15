# R269 — London Asian-range sweep/reclaim reversal

Date: 2026-10-16
**Purpose:** one pre-registered, slower intraday EURUSD hypothesis designed for a five-minute manual execution delay. This is not an R189 retune and will not be combined with other strategies unless it passes its own locked gate.

## Data and execution
- Raw inputs: GitHub Actions artifact `EURUSD-M1-Dukascopy-BID-ASK-2016-2025`, artifact ID 11959096102, EURUSD M1 BID/ASK, UTC timestamps, 2016-01-01 inclusive through 2026-01-01 exclusive. Data-only collection job; all signal/PnL calculations run locally.
- Feed provenance is Dukascopy. Results are not claimed as broker-specific history.
- Convert UTC timestamps to `Europe/London` for session grouping and DST. Do not synthesize missing bars. Align only timestamps common to BID and ASK.
- Fixed splits: discovery 2016–2020, validation 2021, forward 2022–2025. No 2026 bars/outcomes may be used.
- Entry is delayed: signal bar timestamp is its open; its close is only known at the next minute. Entry is at the open timestamp exactly six minutes after the signal-bar timestamp (five minutes after the close becomes known). If that exact timestamp is absent, skip the trade. Use ASK for long entries and BID for shorts.
- Entry spread cap: 1.5 pips, measured at delayed entry. Use BID for long exits and ASK for short exits.

## Locked signal and trade rules
1. Per London calendar day, calculate the Asian range from all available BID bars whose London-local wall-clock time is 00:00–07:59: high = maximum High; low = minimum Low. Do not trade if either range edge is missing or the range is non-positive.
2. Look for signals during 08:00–11:59 London local time, weekdays only.
3. Long signal: BID Low of a bar is at least 2.0 pips below the Asian low and BID Close finishes strictly above the Asian low (sweep below and close back inside).
4. Short signal: BID High is at least 2.0 pips above the Asian high and BID Close finishes strictly below the Asian high (sweep above and close back inside).
5. Only the first qualifying signal per day is eligible. If both long and short conditions occur on the same signal bar, discard that day as ambiguous. No re-entry that day.
6. Place the entry at the delayed executable quote. Stop is one pip beyond the signal-bar extreme: long stop = signal Low − 1 pip; short stop = signal High + 1 pip. Target is the midpoint of the precomputed Asian range.
7. Before placing the delayed entry, invalidate the setup if the executable-side stop or target was touched after the signal bar and before the delayed entry open. Also skip if the delayed entry open is at/beyond the stop or leaves reward/risk below 1.00. Compute reward/risk using the actual delayed entry side and executable stop/target side. No rounding of prices beyond source precision.
8. Maximum holding period: 240 elapsed minutes from delayed entry. At each post-entry bar, if stop and target are both touched, stop-first. If opening price has crossed the stop, exit at the worse opening quote; target exits are filled at the target level. If neither target nor stop is hit by the first bar open at/after the four-hour limit, exit at that open quote. No trailing stop.
9. No position sizing changes feed back into the signal stream; one position per day. For the separate compound diagnostic, size each trade at 0.25% of current realized equity divided by initial stop risk (R multiple), starting at $6,000.

## Cost, metrics and precommitted gates
- Primary incremental cost is +1.0 pip per completed trade beyond observed BID/ASK prices. Also report +0, +0.5, and +2.0 pips.
- Report data coverage/quality, spread, skipped/missing entry timestamps, signal counts, skip reasons, exit reasons, R distribution, PF in R after cost, net R, pips, win rate, trade frequency, maximum drawdown and per-year results. Include a forward weekly PnL four-week circular block bootstrap with 10,000 resamples and fixed seed 2692026.
- **Economic screen LULUS requires every condition:** (a) at +1 pip both discovery and validation net R > 0 and PF >= 1.10; (b) forward 2022–2025 has >=100 closed trades, net R > 0 and PF >= 1.10 at +1 pip; (c) at least 3 of 4 forward years have net R > 0 and PF > 1.00 at +1 pip; (d) bootstrap 95% CI lower bound of average weekly net R is > 0; (e) forward PF at +2 pips >= 1.00 and net R > 0; (f) the 0.25%-risk fixed-fractional forward curve does not cross the static $5,400 10%-loss floor from a $6,000 starting balance using realized PnL.
- Any failed gate = **GAGAL**; no threshold adjustment, parameter sweep, or post-result rescue. If a gate fails because a mandatory input/metric cannot be reconstructed, the experiment verdict is also GAGAL.
- A pass would only mean the locked historical economic screen passed on this Dukascopy feed. Funded-readiness would remain a separate test requiring verified live costs, exact platform/server-time mapping, floating equity/DLL and other applicable firm constraints.

## Reproducibility
Store the local runner, machine-readable result JSON, report, annual/segment metrics, and compressed trade ledger in this branch. Record SHA-256 for raw ZIP and extracted BID/ASK files. Do not create or dispatch a backtest GitHub Actions workflow.