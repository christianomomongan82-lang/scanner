# R305 — EURUSD-to-XAUUSD Common-USD-Factor Transmission (LOCKED PREREGISTRATION)

**Locked before any R305 candidate outcomes are calculated.** This is an independent cross-asset hypothesis, not a retune of the closed local-session, fixing, spread-shock, generic FX shock-fade, or XAU safe-haven-shock rules.

## Hypothesis

A large, unusual EURUSD midpoint move may proxy a common USD-factor shock. If EURUSD rises, the USD is weakening against EUR and XAUUSD may rise too; if EURUSD falls, USD strength may pressure gold. Thus this candidate follows the direction of an unusually large EURUSD move in XAUUSD after a phone-compatible delay.

This mechanism can be false because EUR-specific news can dominate the USD component, gold's drivers differ from FX, the relation may already be absorbed at the delayed entry, or bid/ask costs may erase it. This preregistration tests that claim; it does not assume the edge exists.

## Locked signals and execution

- **Inputs:** paired Dukascopy EURUSD M1 BID/ASK and XAUUSD M5 BID/ASK. Apply exact timestamp joins only. No row-number matching, forward-fill or synthetic tradable bars.
- **Protected interval:** exclude all outcomes at timestamps >= 2026-01-01 00:00:00 UTC before features, thresholds or trades are formed. 2026 XAU remains protected.
- **EURUSD feature:** use midpoint closes. At each XAU M5 signal bar start timestamp t, define the 30-minute EURUSD return as midpoint close at t minus the midpoint close at t-30 minutes, using the most recent complete EURUSD M1 bars aggregated to M5 only when all timestamps are present. Its close is known at t+5 minutes.
- **Causal threshold:** use the 85th percentile of absolute 30-minute EURUSD midpoint returns from the prior 20 calendar days, requiring at least 1,000 complete historical observations. Only timestamps strictly earlier than the current signal close are permitted.
- **Signal event:** absolute current 30-minute EURUSD return >= its trailing threshold, and the preceding five-minute EURUSD return was below that same threshold. This first-cross condition prevents duplicate signals during one continuous move. At most one event per XAU M5 timestamp.
- **Direction:** fixed continuation/same sign. Positive EURUSD return => LONG XAUUSD; negative EURUSD return => SHORT XAUUSD. No sign flip or instrument-selection rescue.
- **Manual-compatible entry:** signal bar close is t+5 minutes; enter at the first exact active paired XAU M5 bar whose start is >= t+10 minutes (five minutes after the signal close). Require it to be the exact t+10 timestamp; otherwise record the signal as ineligible. Long enters ASK open; short enters BID open.
- **Risk distance:** 1.5 × median XAU BID true range of the prior 12 complete contiguous M5 bars, all ending before entry. The prior median must be positive.
- **Exit geometry:** stop = 1.0R; target = 1.5R; maximum hold = 60 minutes (12 XAU M5 bars after entry). Long stop/target are tested on BID; short stop/target on ASK. If opening gap passes a stop, fill at adverse open. If stop and target are touched in the same bar, stop-first. If no barrier occurs, time-exit at executable close of the twelfth bar. Missing active bars skip the event before outcome calculation; no fill substitution.
- **Overlap:** only one open XAU position at a time. Signals while a position is open are logged as skipped; after position closure, a new first-cross signal may be accepted.
- **Costs:** observed BID/ASK execution plus added round-trip friction $0.00, $0.30 and $0.50 per oz. Primary cost is +$0.30/oz. These stress levels are not a claim about final live broker costs.
- **Matched diagnostic:** same event times, risk levels, holding and costs, but trade the opposite direction (fade). The mirror stream is diagnostic only, never an alternate winner chosen post hoc.

## Data and provenance

- EURUSD archive artifact #11959096102, data-only acquisition run #38697080604. ZIP SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. BID gzip SHA-256: `b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc`; ASK gzip SHA-256: `52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b`.
- XAUUSD archive artifact #12031270051, data-only collection run #38859918137. ZIP SHA-256: `2cde8338800fd7f4d5d4628512201c16757ef06bd90d51ffdc8ef9bea425ba1a`. BID gzip SHA-256: `b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575`; ASK gzip SHA-256: `b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9`.
- Audit exact timestamps, paired BID/ASK, duplicates, invalid OHLC, negative spreads, missing bars, repeat-flat filter, usable synchronized event count and event skip reasons before computing outcomes.

## Period split and hard gates

- Warmup/calibration: 2016 only.
- Discovery: 2017–2020.
- Validation/diagnostic: 2021–2025. This period is already programme-contaminated and cannot count as pristine OOS; 2026 remains locked.
- Core promotion gates are conjunctive:
  1. Data/feature/execution-path integrity passes and no synthetic tradable bars are used.
  2. At least 100 trades in discovery and 150 in validation.
  3. At +$0.30/oz, net R > 0 and PF_R >= 1.05 in both discovery and validation.
  4. At +$0.50/oz, net R > 0 and PF_R >= 1.00 in both scored periods.
  5. At least 3 of 4 discovery years positive at +$0.30/oz.
  6. Validation circular 4-calendar-week block bootstrap, 10,000 replications, seed 305, all calendar weeks including zero-trade weeks, has a 95% CI lower bound > 0 for mean weekly net R.
  7. Same-direction continuation stream remains positive under T+15-minute entry delay at +$0.30/oz.
  8. Complete runner, exact config, row-level trade ledger, all skip reasons, weekly input, metrics, and report are reproducible from repository artifacts.
- If a gate fails: verdict **GAGAL**, do not calculate candidate PnL for 2026 and do not tune this candidate's threshold, direction, risk distance or exits on the same data.
- Only if all core gates pass may a separate, provider-rule-verified challenge replay be run, with the objective (P(	ext{both phases pass before any loss-rule breach and by day 179})), not PF. Report time-to-funded quantiles and challenge breach probability; do not call a proxy replay provider-equivalent if server-day reset, fees, floating equity, slippage or swaps remain unverified.

## Required artifacts

Save data audit, pre-outcome eligibility audit, runner, primary and mirror trade ledgers, period/year scorecard, cost/delay scorecard, validation weekly bootstrap input/result, compact JSON, final report, and checkpoint/ledger. All signal and PnL computation must run locally in Python. GitHub Actions must not be used to compute a backtest.
