# R304 — FX Local-Session Currency Depreciation (LOCKED PREREGISTRATION)

**Lock status: preregistration committed before R304 signal/PnL calculation.** Candidate ID R304. Binary verdict: LULUS/GAGAL; no outcome-driven direction changes or session-window tuning.

## A. Identity and lineage

- Primary family: `FX_LOCAL_HOURS_ORDER_FLOW`.
- Type: NEW_MECHANISM / two-module calendar-time portfolio.
- Instrument: EURUSD only; paired Dukascopy M1 BID/ASK.
- Not a descendant or parameter rescue of R300 London-fix reversal, R303 spread-shock fade, R260 shock fade, prior range/breakout, or momentum rules. Previous session candidates used range/impulse triggers; this candidate tests a published unconditional local-trading-hours return effect with fixed directional signs, not a price-triggered entry.
- Evidence motivating the falsifiable hypothesis: Breedon & Ranaldo, “Intraday Patterns in FX Returns and Order Flow” (Journal of Money, Credit and Banking, 2013), reports currencies tended to depreciate during their local trading hours, with patterns related to order flow. This is external motivation only, not evidence that a retail EURUSD feed retains a tradeable edge: https://onlinelibrary.wiley.com/doi/10.1111/jmcb.12032
- Hypothesis selection: novelty = distinct from range/impulse sessions; data readiness = paired M1 available; manual execution = 5-minute delay; coverage must be established before PnL; all directions/time windows fixed below.

## B. Falsifiable hypothesis

**Claim:** EURUSD has a cost-surviving directional intraday bias consistent with local-currency depreciation: short EURUSD during the early European-local window and long EURUSD during the early US-local window, using only fixed clock events and a five-minute execution delay.

**Economic rationale:** if EUR tends to depreciate during European-local trading hours, EURUSD should fall; if USD tends to depreciate during US-local hours, EURUSD should rise. Because EUR and US windows do not overlap under the definitions below, the two modules can be evaluated separately and as one ordered system. The result may fail because currency-specific effects do not transfer cleanly to EURUSD, overlap in global order flow offsets the direction, or spreads/costs erase the effect.

### Immutable modules

**Module E — EUR local hours**
- Use `Europe/London` IANA timezone and historical DST.
- Eligible calendar days: Monday–Friday London-local.
- Session start: 08:00 London time; planned entry: 08:05; planned time exit: 12:00.
- Direction: SHORT EURUSD every eligible day.
- Signal is the fixed session clock, not any price movement or threshold.

**Module U — USD local hours**
- Use `America/New_York` IANA timezone and historical DST.
- Eligible calendar days: Monday–Friday New-York-local.
- Session start: 08:00 New York time; planned entry: 08:05; planned time exit: 12:00 New York time.
- Direction: LONG EURUSD every eligible day.
- Signal is the fixed session clock, not any price movement or threshold.

The 08:05 local entry is the declared five-minute reaction delay from the 08:00 session start. Enter at the first active paired M1 open at or after 08:05, but no later than 08:10 local. If no active quote exists in that window, skip and log the reason. Do not use a later favorable quote. Exit at the exact 12:00 local M1 open; if that required quote or any stop-monitoring path is unavailable, skip the event before PnL calculation. No overnight holding, no overlapping positions, no second entry per module/day.

## C. Risk and execution rules

- Build the midpoint from exact paired BID/ASK OHLC; join only by timestamp keys.
- For each module and each local calendar day, calculate the previous 20 eligible full-session midpoint ranges (`max(mid_high) - min(mid_low)`) strictly before the current date. Require at least 15 valid historical sessions. Initial risk distance `D` is their median. No current-day high/low contributes to D.
- Stop distance = 1.0D, with no profit target. This is a calendar-window drift test, not a fixed target scalp; if the stop is not hit, close at the exact 12:00 local bar open.
- LONG: enter at ASK open; check stop on BID low/open and exit at BID. SHORT: enter at BID open; check stop on ASK high/open and exit at ASK.
- Stop-gap handling: if the executable open is already through the stop, fill at that open; otherwise fill at the stop level when first touched. No trailing, scale-in/out, direction flip, or intraday re-entry.
- Require exact active timestamps for the entry, stop-monitoring path, and time exit. Do not forward-fill or synthesize tradable bars. If any required minute is absent/inactive after the registered data filter, mark the event ineligible before outcomes; report coverage loss by module/year.
- Module E's time exit occurs before Module U's planned entry even during UK/US DST mismatch weeks. If the actual event path overlaps, skip the later entry rather than allow concurrent positions.
- One position maximum at any time across both modules; if a previous trade remains open, log and skip the next event.
- Cost grid: observed executable BID/ASK fills plus incremental round-trip costs of +0, +0.5, +1, and +2 pips. Primary cost = +1 pip. These are stress assumptions, not a claim about FundedNext's final live cost schedule.

## D. Data contract

- Source: Dukascopy EURUSD M1 BID/ASK, data-only GitHub artifact #11959096102 from collection run #38697080604.
- ZIP SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- BID gzip SHA-256: `b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc`.
- ASK gzip SHA-256: `52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b`.
- Source timestamp range requested: 2016-01-01 inclusive to 2026-01-01 exclusive. No row >= 2026-01-01 UTC is eligible.
- Remove a minute only when both BID and ASK OHLC are flat, each side's open equals its preceding observed close, and its timestamp is exactly one minute after that prior observed row. Do not remove a flat candle unless all these conditions hold. Preserve gaps; never fill missing bars.
- Before PnL, audit ZIP/member hashes, row counts, paired timestamps, duplicates, monotonicity, invalid OHLC, negative spreads, the precise repeated-flat filter count, active timestamps/gaps, session event dates, required path coverage, and skip reasons by module/year. Eligibility audit is frozen before scoring.

## E. Frozen periods and gates

- 2016: warm-up only for data checks/trailing ranges.
- Discovery: 2017–2020.
- Validation: 2021.
- Do not calculate 2022–2025 R304 outcomes unless every core discovery and validation gate passes; any later use is explicitly program-contaminated diagnostic, not pristine OOS.
- 2022–2025 is already inspected across related FX work. This candidate cannot claim untouched program-level OOS. 2026 is excluded entirely.

All core gates are conjunctive:
1. Data integrity and executable-event path pass; no synthetic bars or timestamp lookahead.
2. At least 200 completed trades in combined discovery and 100 in combined validation.
3. At +1 pip incremental cost, combined-system net R > 0 and PF_R >= 1.05 in both discovery and validation.
4. Both modules must have positive combined-period net R at +1 pip; no post-hoc dropping of a losing module. Their relative contribution and the union/ordered portfolio are reported.
5. At +2 pip cost, combined net R > 0 and PF_R >= 1.00 in both scored periods.
6. At least 3 of 4 discovery years have positive combined net R at +1 pip.
7. Validation weekly net-R circular four-week bootstrap (10,000 resamples, seed 304; all calendar weeks including zero-trade weeks) has a 95% confidence interval lower bound > 0.
8. Fixed-direction controls are reported only as diagnostics; the preregistered direction cannot be reversed after observing PnL.
9. The exact code, input hashes, pre-outcome eligibility audit, row-level trade ledger, bootstrap input/result, reports and compact metrics must be reproducible from the active GitHub branch.

If any gate fails, verdict R304 **GAGAL** and do not tune its clock, direction, range estimator, stop distance or exit on the same periods. If all gates pass, calculate the predeclared 2022–2025 diagnostic and then run a separate account-equity-aware challenge replay. Challenge replay risk grid: 0.25%, 0.50%, and 0.75% of current phase equity per 1R, portfolio open-risk cap 1.0%, and maximum 1.0% nominal risk for each session event; track intratrade floating PnL, target sequencing (+8%, then +5%), daily/max loss, actual server-day reset/time mapping, minimum trading days, fees/slippage and time to funded status. The objective is maximize `P(both phases pass before any loss-rule breach and within 179 calendar days)`, not PF in isolation. Report median/90th/95th percentile time to target and P(pass within 179 days); no proxy replay may be called provider-equivalent unless all rules/costs are verified.

## F. Required final verdict artifacts

Save the local runner, immutable preregistration, pre-outcome eligibility/data audit, complete all-cost trade ledger, period/year summary, weekly bootstrap input/result, compact JSON, final report, and an updated checkpoint/ledger. No GitHub Actions backtest may run. Market-data collection, if needed in a future task, must remain data-only.
