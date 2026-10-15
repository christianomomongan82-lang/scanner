# Objective Correction — Funded Target Completion Comes First

Date: 2026-10-16  
**This is the latest authoritative objective and supersedes any earlier wording that made PF improvement the primary objective.**

## Actual objective

The goal is to pass the smallest viable funded challenge as quickly as is realistically achievable, then pass its second phase and reach funded status. For the current FundedNext Stellar 2-Step reference configuration, the research target is +8% in Phase 1 followed by +5% in Phase 2, while staying inside the applicable daily-loss and maximum-loss rules. Do not buy a challenge or run KYC before age eligibility; the known eligibility date is 2026-12-25.

The objective is **not** to maximize PF, maximize trade frequency, or find one unusually strong setup. PF is a diagnostic statistic—one example of why the current single-setup “needle in a haystack” approach is insufficient. It is not the project's end goal.

## What “compound” means in this project

Build an integrated system by combining and coordinating multiple compatible sources of opportunity: setups, contextual conditions, independent strategies, and different time windows. The intent is to create enough qualified opportunities and a favorable sequence of outcomes to reach the funded target, without relying on one rare setup or one market regime.

A useful compound system may improve its challenge-pass profile through several mechanisms:
- a component can provide opportunities when another component is inactive;
- context/routing can activate different setups in different market conditions;
- one module may filter weak conditions for another;
- independent streams can diversify loss sequences and reduce time spent waiting for valid opportunities;
- shared position/risk control prevents simultaneous or correlated positions from breaking challenge limits.

Combining is not blind union: every component's effect on the full target-completion distribution must be measured. A component that adds PF but slows target completion, or adds trade count while increasing breach probability, may not help. A component with modest standalone PF can still be useful as a diversifier only if its net economics and effect on the challenge outcome are demonstrated.

## Primary optimization target and scorecard

Optimize the portfolio/system for:
1. Probability of reaching the phase target **before** breaching daily/max loss.
2. Distribution of time to target among successful paths (median and upper quantiles, in trading days).
3. Overall probability of completing both phases, including the reset/restart rules actually specified by the firm.
4. Breach probability and worst loss streak / drawdown distribution.
5. Frequency of valid opportunities under the five-minute manual-execution delay.
6. Robustness to realistic costs, spread, slippage, delayed entry and correlation between modules.

PF, net expectancy, win rate, R distribution, trade frequency, annual metrics and bootstrap results remain useful explanatory diagnostics, not the single objective. PF >= 1.10 must not be treated as a standalone goal or proof that a system reaches the challenge target well. Conversely, a system must not be promoted merely because a high-risk lottery occasionally hits the target: its breach probability and distribution across repeated simulations must be reported.

## Required challenge replay

For every candidate system:
- Simulate the actual sequential phase targets (+8%, then +5% for the current reference case) from the relevant phase balances.
- Use the exact daily-loss and maximum-loss definitions, server-time reset, time zone/DST and any minimum-trading-day/inactivity rules that apply; use evidence for those rules rather than guessed approximations.
- Model entry delay and executable BID/ASK sides, commissions/fees and slippage stress.
- Track floating as well as closed equity when data permit. A closed-equity-only replay must not be called challenge-equivalent.
- Use trade order and cross-module overlap from timestamps. No artificial shuffling that breaks time dependence unless clearly labeled as a supplementary bootstrap.
- Report target-hit probability, loss-rule breach probability, time-to-target quantiles, trades/days to target, failure modes, and uncertainty across block-bootstrap or resampled path tests. Make the resampling method preserve clustering/dependence as far as the data allow.
- Compare at least the component streams, a matched baseline, and the integrated system with identical assumptions. Explain which combination actually reduces time-to-target or increases pass probability.
- Fixed-fractional capital compounding is the position sizing mechanism inside this simulation, not the optimization goal itself. Risk per trade and portfolio caps must be fixed before the replay.

## Research governance

- Result status stays binary: **LULUS** or **GAGAL**. Missing required data/implementation verification means the tested claim is GAGAL.
- Do not tune old failed candidates on already-inspected validation/forward outcomes.
- The 2022–2025 period has been inspected across many rounds and is no longer a clean untouched holdout for promotion. Use it for diagnosis/development; an independent locked window or genuinely future evidence is required for a high-confidence LULUS promotion.
- Don't run GitHub Actions for backtests. Retrieve raw data from GitHub, compute locally in Python, save preregistration, code, input hashes, ledgers, metrics, reports and verdict to GitHub.
- Before age eligibility, research is simulation-only. Do not recommend purchasing the challenge now.

## Correct interpretation in one sentence

**Combine and coordinate strategies to maximize realistic probability of passing the actual funded targets quickly without violating loss limits; measure PF as one diagnostic, not as the target.**
