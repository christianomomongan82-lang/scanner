# R285 Preregistration — US500 Turn-of-Month Intraday Seasonality

**Candidate ID:** `R285_US500_TURN_OF_MONTH_INTRADAY`  
**Status:** locked before outcome calculation.  
**Date:** 2026-10-17.

## Question and economic rationale

Test whether a pre-specified calendar window around month boundaries has a stronger same-day long drift in the US500 CFD proxy than ordinary sessions. Month-end portfolio rebalancing and recurring monthly allocations can create calendar-timed demand, but the classic turn-of-month effect may occur overnight rather than intraday; this test deliberately evaluates only the executable intraday expression and does not assume it exists.

This is a new calendar-seasonality mechanism, not a retuning or direction reversal of R283/R284. No price threshold is fitted and no signal is selected after observing trade returns.

## Input, calendar and quality rules

- Use only the already-cached GitHub R205 USA500 M5 BID-only snapshot, artifact `11709864394`, ZIP SHA-256 `21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac`.
- Convert epoch-millisecond bar-open timestamps to `America/New_York`, respecting DST.
- RTH = weekdays with 78 expected bar-open timestamps from 09:30 through 15:55 ET inclusive, every five minutes.
- A calendar-session candidate is any weekday with at least one observed timestamp in that RTH window. If a candidate date does not have exactly the 78 unique expected timestamps, has invalid OHLC, or contains a repeated-flat row (O=H=L=C=previous row close), reject its entire calendar month to avoid misclassifying first/last sessions because of a detected missing/placeholder session. No bars are synthesized. The repeated-flat rule is a conservative data-quality heuristic, not proof that every such row is synthetic.
- After session-quality checks, identify valid US500 trading sessions chronologically from the eligible calendar. A trade date qualifies if it is among the **first three** eligible RTH sessions of its calendar month or among the **last two** eligible RTH sessions of its calendar month. The union is de-duplicated. No month-specific or year-specific parameters are fitted.
- Evaluate 2017–2020 discovery and 2021 validation only initially. 2022–2025 PnL and 2026 outcomes must not be calculated or inspected unless every historical gate passes.

## Locked signal and execution

1. Direction is LONG only on qualifying calendar sessions; no price-based entry condition.
2. Entry at the 09:40 ET M5 bar open, ten minutes after the 09:30 cash-open bar begins. This models signal/decision readiness plus the user's five-minute manual phone execution delay; no earlier bar price may be used as the entry.
3. Exit at the 15:55 ET bar close. No overnight holdings, stop, target, pyramiding, or compounding in this signal-screen stage.
4. Return per trade is `(exit_close / entry_open - 1) × 10,000` basis points before cost. Subtract modeled round-trip notional costs of 1, 2 and 4 bp. Primary screen uses 2 bp. Because this archive is BID-only, these are assumed cost stresses—not measured spread, slippage, commission or verified FundedNext instrument costs.
5. Matched parent baseline: same entry and exit on every eligible US500 session, always LONG. Compare selected seasonality days versus this baseline on the same source and same costs. This baseline is diagnostic; it is not an additional candidate to tune.

## Binary gates

Primary cost = 2 bp round-trip.

- Discovery 2017–2020: at least 150 qualifying trades; PF >= 1.05; positive total net return; at least 3 of 4 annual cohorts have positive net return.
- Validation 2021: at least 45 qualifying trades; PF >= 1.00 and positive total net return.
- Cost stress: at 4 bp, PF >= 0.90 in both discovery and validation.
- If any gate fails, verdict is **GAGAL** and stop: do not calculate/inspect 2022–2025 or 2026 results, do not change the window, direction, times, costs or gates after seeing results, and do not run a funded challenge replay.
- If all gates pass, only then may 2022–2025 be opened as exploratory due prior project-level contamination; a screen pass still would not prove edge or funded readiness. An integrated two-phase equity-path replay requires verified executable costs, swaps, account loss rules and proper challenge logic.

## Required archive

Store the exact local replay engine, source ZIP hash/row coverage, quality exclusions, annual results, parent comparison, cost sensitivities, trade ledger, JSON metrics and binary verdict in the research branch. Backtest calculations must run locally, never as a GitHub Actions backtest workflow.
