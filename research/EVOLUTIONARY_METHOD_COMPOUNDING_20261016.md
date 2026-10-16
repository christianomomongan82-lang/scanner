# Evolutionary Method Compounding — authoritative research workflow

Date: 2026-10-16

## User intent

“Compounding” means compounding the **method-discovery process**, like evolution. Every experiment should inherit useful information from all prior experiments. The research process should improve the next generation of methods rather than repeatedly inventing isolated strategies from scratch.

This is distinct from:
- capital/equity compounding (position sizing);
- blindly combining all old strategies;
- changing the parameters of a failed strategy until historical results look good;
- optimizing only PF when the actual objective is funded-target completion probability and time.

## The evolutionary loop

1. **Maintain a reusable building-block library.** Decompose every tested method into components: market/context state, setup trigger, direction, entry timing, stop/target/exit logic, session/instrument, execution assumptions, and risk policy. Keep an exact definition, provenance, sample eligibility, and evidence for each block.
2. **Keep failures informative.** A full candidate can fail even when one component may be useful. Store why it failed (negative expectancy, insufficient trade frequency, regime dependence, late fill, cost sensitivity, instability, data invalidity, or breach risk). A failed combination does not automatically condemn every block inside it; use controlled ablations to identify which parts add or destroy value. Do not rehabilitate the exact locked failed candidate by retuning on its test window.
3. **Generate the next generation using explicit mutations and crossovers.** Combine evidence-backed blocks, change one economically motivated structural choice at a time, or create a new block when the previous evidence supports it. Examples: A's contextual filter + B's entry trigger; B's setup with C's exit logic; a context-dependent router; or removing a block shown to destroy results. Each child records its parent experiment IDs, inherited components, mutation/crossover, rationale, and a new immutable hypothesis ID.
4. **Evaluate on matched event streams.** Use identical source data, timestamps, executable sides, latency, and cost assumptions. Compare parents, child, each component, ablation, and simple/no-filter baseline. Report trade count/coverage alongside target-completion probability, time to target, risk-rule breach, net expectancy, PF, drawdown and stability. A child is useful only if it improves the project's actual funded-target scorecard without turning into a high-risk lottery or collapsing usable opportunities.
5. **Select a diverse population, not one lucky winner.** Retain candidates that are non-dominated across completion probability, median/upper-quantile time-to-target, breach probability, cost/delay robustness, and opportunity count. Keep structurally different parents when they contribute distinct regimes. Do not select solely by in-sample PF or net profit.
6. **Protect against evolutionary overfitting.** The development window may generate and prune generations, but repeated generations on the same validation period leak information. Use nested chronological walk-forward selection, freeze all components and thresholds before each evaluation, record how many candidates were tried, and use a genuinely untouched final instrument-period holdout only once after the historical screening gates pass. 2022–2025 has already been examined in this project and is not a pristine holdout. Do not repeatedly inspect or recycle the final 2026 XAUUSD screen to breed later candidates.
7. **Promote a system, not a promising chart.** Only after a frozen integrated trade stream survives independent OOS and costs may it go through an equity-aware two-phase challenge replay. That replay must model the real target sequence, daily and maximum loss, open floating P&L, fees/swaps, server-day reset, minimum trading days, Quick Strike, execution delay and sizing. This stage evaluates funded readiness; it must not be used to invent or tune edge.

## Required candidate registry

For every generation save:
- unique candidate ID, parent IDs, hypothesis and component/block IDs;
- mutation/crossover rationale and what observation motivated it;
- immutable rules, data source/checksums, cost and latency assumptions;
- component, ablation, baseline and integrated-system results on the same event stream;
- development / validation / OOS boundaries, number of tried candidates, and whether a period has been inspected;
- binary LULUS/GAGAL verdict for that locked candidate and precise failure category;
- what was learned, what blocks can be reused, and what must not be repeated.

## Candidate selection objective

The primary objective remains maximizing the realistic probability of completing both funded targets as quickly as possible before a rule breach. Rank using a risk-aware scorecard / Pareto frontier, not a PF threshold in isolation. PF and expectancy are diagnostic evidence, not the target itself. Position-size compounding is evaluated only downstream on the evolving combined method.

Never promise that evolution guarantees a profitable method. It accelerates systematic learning by reusing evidence and avoiding repeated dead ends; if all children fail their gates, record GAGAL and change the underlying hypothesis family rather than falsifying or loosening the gates after seeing outcomes.

## Current project correction

R270/R271 and the other failed candidates remain locked GAGAL; preserve them and reuse only components whose contribution is independently diagnosed. R272 is currently a preregistered XAUUSD dual-module candidate intended to test one combination, but it is **not yet a full evolutionary-search implementation**. Complete its data-integrity-safe locked test without opening 2026 early; then use the results plus the reusable component ledger to construct and test the next generation. Do not call a single combined setup “compounding” merely because it has two modules.
