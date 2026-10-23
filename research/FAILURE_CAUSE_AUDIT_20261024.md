# Failure-cause audit — backtest program (2026-10-24)

**Purpose:** diagnose repeated failures and define the next research decision. This is an audit of existing evidence, not a new strategy experiment. No new price/PnL results are claimed here.

## Executive conclusion

The strongest explanation is **lack of a persistent, cost-surviving predictive edge in the tested hypotheses**, compounded by **discovery overfit and regime instability**. Data and code defects are a genuine secondary cause: they invalidate some early outputs and waste research cycles, but do not explain the majority of negative results because many corrected, well-sampled tests remain negative before incremental friction.

No candidate is currently demonstrated to be ready for a FundedNext two-phase challenge replay. A high win-rate, PF, or discovery return is not enough; the required evidence is a frozen event stream that survives confirmation, executable-side cost/delay, and a realistic chronological challenge-path simulation.

## Ranked root causes

Confidence labels below are qualitative evidence weights, not estimated Bayesian probabilities.

### 1. Missing cost-surviving edge in the tested signal families — VERY HIGH

Several unrelated rules are negative even before adding incremental costs, with enough events to reject those exact specifications:

- **R321 causal EURUSD price-state audit:** all 28 feature/horizon comparisons were negative at +1 pip and PF below 1. The best, with 48,879 events, was still negative at zero extra friction (mean −0.2568 pip/event; PF 0.934).
- **R255 rolling-extreme sweep/reclaim:** 2,824 forward trades at PF 0.786 and 563 later-period trades at PF 0.671; all four forward years were negative.
- **R258 multi-horizon FX momentum:** 944 forward trades, PF 0.785, net −3,848.4 pips at +1 pip; all four forward years negative.
- **R305/R306 cross-asset EURUSD-to-gold transmission:** thousands of events, strongly negative even with zero additional friction.
- **R315 XAU compression breakout:** 1,280 completed discovery trades, −1,102.961R even at zero additional friction.
- **R331 VXN-banded Nasdaq reversion:** 93 discovery / 33 confirmation trades and negative gross return in both splits before added costs; PF 0.752 / 0.665.
- **R330 weekly multi-asset momentum:** discovery +82.83% compounded at its primary proxy cost reversed to −37.41% in confirmation.

Interpretation: increasing risk, adding more trades, or reducing a small cost assumption cannot repair these exact negative streams. This is the most important cause, and it rules out treating risk-sizing as the missing edge.

### 2. Selection bias and non-stationarity / regime reversal — VERY HIGH

- **R319:** 11 of 972 configurations passed discovery selection; 0/11 survived confirmation or diagnostic-forward evaluation. The selected configuration changed from +17.038R / PF 1.208 in discovery to −25.860R / PF 0.555 in confirmation.
- **R330:** discovery's +82.83% was followed by −37.41% confirmation; the confirmation bootstrap interval for mean weekly net return was wholly negative (−1.66% to approximately −0.02%).
- **R320:** the selected channel-breakout configuration was +4.918R / PF 1.059 in discovery and −5.173R / PF 0.917 in confirmation.
- A substantial part of 2021–2025 and the US index history has been looked at repeatedly across families. It is development/contaminated diagnostic history, not a clean project-wide final holdout.

Interpretation: seemingly strong discovery results frequently represent noise, selection after many tries, or an effect that does not persist. Reusing the same confirmation period to breed variants would make this problem worse.

### 3. Research-process and code/data defects — HIGH, but not the principal economic cause

Verified incidents include:

- **R331:** the first run called the pandas Index.has_duplicates property as if it were a function; a separate date-object vs ISO-string key mismatch then silently skipped valid sessions. Both were fixed before the accepted rerun; the zero-trade first run must be discarded.
- **R257:** the original compression-breakout grid had a coverage/eligibility defect that caused zero validation trades. Its corrected follow-up R281 still failed its locked discovery and validation-sample gates.
- **R270/R272:** a context/efficiency gate made one router module unreachable in the tested data, so the intended two-module design was not actually tested as imagined.
- Some earlier records lacked exact runner / row-ledger packages or full repository read-back verification; Protocol V2 correctly treats those as a process/archive gate, not positive evidence.

Interpretation: these faults can invalidate a test, suppress trade counts, and create false confidence if not caught. They cannot be used to dismiss the negative results from the many other correctly executed, sufficiently populated screens. The response is fail-closed preflight, explicit eligibility/sample audits, and exact-runner reproduction—not to assume every failure is a coding bug.

### 4. Event rarity / sample-size mismatch — HIGH for event strategies; not the general explanation

- **R322:** only 131 discovery and 49 confirmation eligible news-cascade setups before outcome scoring, below its frozen 200/100 thresholds; PnL was correctly not calculated.
- **R308:** only two qualifying genuine long-gap events existed under the frozen definition.
- **R323–R328:** several pre-outcome gates failed because eligible legs/trades were below the predeclared floors or required V2 packages were incomplete.
- **R331:** confirmation had 33 primary trades against a 50-event minimum.

But many high-frequency tests also failed badly (e.g. R255, R258, R305/R306, R315, R321). So simply lowering entry thresholds to create more trades would repeat an established failure mode.

### 5. Execution friction, latency, and mismatch to the funded platform — MEDIUM as a cause of marginal failures; HIGH as a promotion blocker

The user needs a manual phone workflow and several-minute delay. Signal screens that use ideal entries, daily-close bars, bid-only prices, or underlying-market OHLC are not proof of executable CFD returns. R331 correctly used side-specific Dukascopy BID/ASK with delayed entry, yet its gross result was already negative. Thus execution is a major realism/promotion issue but not the sole cause of the broad failure pattern.

The challenge path itself is also not the same as ordinary strategy expectancy: Phase 1 target +8%, Phase 2 +5%, daily loss 5%, static maximum loss 10%, with floating P&L/fees included in daily-loss calculation. A candidate must be replayed chronologically against those constraints; no honest pass probability follows from PF alone.

## What the evidence does not say

- It does **not** prove every strategy or the funded objective is impossible.
- It does show that already-tested candle/clock/range/momentum/reversion specifications should not be rescued by threshold changes, direction flips, or re-ranking the same inspected data.
- A screen with too few events is **inconclusive about expectancy**, but still a failed candidate for the project's current evidence/promotion gate.
- A reproducible runner is necessary, not sufficient; a perfectly reproducible losing strategy remains a losing strategy.

## Decision and next research protocol

1. **Close the exact failed families.** Do not tune the listed failures on the dates used to reject them.
2. **Do not start another broad OHLC indicator/threshold sweep.** The evidence says the bottleneck is not a shortage of ideas or trade frequency; it is a lack of durable conditional advantage and excessive selection on reused history.
3. **Move the next generation toward an independent information mechanism**, not merely transformed candle features. Candidate leads must have an economic reason to persist after a 5–10-minute manual delay (for example, slower post-event drift or a verified cross-market information delay—not the first seconds/minutes of an announcement). The literature is a source of hypotheses, not evidence of current edge.
4. **Pre-outcome feasibility gate first:** confirm point-in-time source availability, historical coverage, instrument mapping, timestamps, executable-side data, and enough eligible events across predeclared discovery/confirmation splits. If sample count or data entitlement fails, stop before PnL.
5. **Only then preregister and calculate locally.** Use exact BID/ASK fills, preserve gaps, model delayed entry and extra slippage, record every eligible and skipped event, deterministic reruns, and repository-readable source/ledger/manifest. Do not use GitHub Actions to calculate backtests.
6. **Separate economic qualification from challenge qualification.** Require positive cost-stressed evidence on confirmation before using the untouched window; only then run the shared two-phase chronological replay with funded-rule equity marks, broker terms, server reset/DST, minimum trading days, open floating P&L, swaps/commissions, and dependence-preserving path resampling.
7. **Protect untouched data.** Repeatedly viewed 2021–2025 and US-index periods remain contaminated. Do not open the protected XAUUSD 2026 window to breed variants or pick among candidates.

## Binary program status on 2026-10-24

**No candidate has demonstrated a FundedNext pass.** The latest R331 is **GAGAL** at screen stage; it is neither a funded replay nor a pass-probability result. The correct next action is a source-and-sample feasibility review for a genuinely new information family before any additional strategy PnL—not another parameter mutation of an established losing family.
