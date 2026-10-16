# Funded-Ready Promotion Gate — effective 2026-10-16

**Primary objective:** maximize realistic probability of completing both funded challenge phases quickly without daily-loss or maximum-loss violation. PF is a diagnostic, not the target.

## Current verdict

No strategy is currently funded-ready. R270 and R271 remain GAGAL. Their parameters must not be changed to rescue their recorded samples. The 2022–2025 window has been inspected repeatedly, and is exploratory/diagnostic only—not an untouched final holdout.

## Required evidence gates before a candidate can be marked LULUS

### Gate 1 — Data integrity and provenance
- Raw input file/artifact, market feed, timeframe, quote side, time bounds, checksum, duplicate/missing-bar audit and timezone handling are recorded.
- No fabricated bars, look-ahead, or mixing incompatible price sides.
- Store the pre-registration, exact runner, full chronological trade ledger, compact results, tests, report and input metadata on the research branch.
- All calculations run locally in the ChatGPT/container environment. GitHub stores code and data/results; do not use GitHub Actions to calculate a backtest.

### Gate 2 — Locked strategy and practical execution
- Rules are frozen before validation: signals, side, exact entry timestamp, SL/TP, time exit, overlap, and invalid/skip rules.
- Entry pricing begins after the actual intended five-minute manual delay, not ideal entry with an optional delay test afterward.
- Costs include observed BID/ASK plus documented broker/funded commissions, swaps and fees, with incremental slippage stress. Unknown account-specific costs must be labelled unknown, not silently set to zero.
- Profitable positions closed within 30 seconds must not push Quick Strike to 30%; the safe design target is zero such trades.

### Gate 3 — Independent evidence
- Discovery and validation are kept separate; all thresholds are locked on discovery only.
- The repeatedly inspected 2022–2025 period cannot serve as a promotion holdout.
- A promotion test must use a genuinely untouched instrument/feed window or a post-lock forward collection. Do not pick the one asset or date slice that looked best after browsing results.
- Require a meaningful trade sample across distinct market periods. A positive total PF or one good year alone is never enough.
- The locked stream must have positive net expectancy after costs, positive annual/period stability and bootstrap evidence that is inconsistent with a negative edge. A small-sample or interval-crossing-zero result is GAGAL for promotion.

### Gate 4 — Verified Challenge engine
Use current official rules from `FUNDEDNEXT_STELLAR2_RULES_VERIFIED_20261016.md`, not the historical proxy:
- Phase 1 +8%, Phase 2 +5%, each calculated on closed P&L from the phase's starting balance.
- 5% daily loss; 10% static maximum loss, with balance/equity and floating losses observed.
- Daily server reset with seasonal GMT+2/GMT+3 handling.
- Daily-loss calculation includes current-day closed P&L + current floating P&L, commissions, swaps and fees; floating positions persist across daily reset.
- At least five separate calendar trading days per phase.
- Quick Strike below 30% by profitable P&L attribution for positions closed in less than 30 seconds.
- The two phases are simulated sequentially, with the firm's actual phase transition timing and a fresh phase balance.
- Include intratrade equity paths and stop-gap/slippage stress. A closed-trade-only replay is not Challenge-equivalent.
- Test a predeclared risk grid; do not pick a high-risk configuration merely because a few paths hit the target.

### Gate 5 — Internal readiness scorecard
These are project safety criteria, not FundedNext rules:
- For the locked out-of-sample trade stream, positive net expectancy after the declared cost/slippage stress and no single-year dependency.
- At least 10,000 dependence-preserving challenge path simulations, with the resampling method and seed recorded.
- Target: at least 70% estimated probability of passing both phases before any loss-rule breach, at least 90% of simulated paths respecting the loss limits until target or explicit fail, median time to finish both phases no longer than 90 trading days and 90th percentile no longer than 180 trading days. Report uncertainty, not just point estimates.
- Results must remain acceptable under a predeclared higher-cost/slippage stress and one lower-risk configuration; a lottery-like risk setting cannot be promoted.
- Minimum-day and Quick Strike constraints must be satisfied in the replay.
- Report target-hit probability, breach probability, pass-both-phase probability, time-to-target quantiles, P&L, drawdown, cost and latency sensitivities, failure reasons, and input hashes.

If any mandatory gate is missing or fails, verdict is GAGAL for funded readiness. A candidate can still be retained as research knowledge, but it must not be described as ready or guaranteed to pass.

## Workflow for future rounds

1. Audit previously tested streams and data available in GitHub before inventing another near-duplicate.
2. Choose a distinct, economically motivated composite/setup with a clear mechanism compatible with five-minute latency.
3. Commit the pre-registration before calculating validation/forward outcomes.
4. Run the exact local backtest, create full trade ledger and all cost/delay/annual/bootstrap diagnostics.
5. If and only if the locked stream clears Gate 3, run the verified two-phase challenge replay.
6. Commit report and update `PROJECT_STATE.md` with the binary verdict, limitations and links.
7. Never redefine 'ready' after seeing results, and never purchase or start KYC before legal age eligibility.

## Age / enrollment constraint

FundedNext's current public help page states that traders must be at least 18. The current research can continue as simulation, but account purchase, KYC and funded enrollment must wait until age eligibility.
