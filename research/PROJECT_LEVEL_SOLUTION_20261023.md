# Project-Level Solution — Stop the Backtest Loop and Optimize Funded Completion

Date: 2026-10-23  
Type: **RESEARCH/DELIVERY SYSTEM FIX, NOT A STRATEGY PROPOSAL**  
Status: operating decision for the project; no new signal PnL is authorized by this document.

## Decision

The project should stop treating each numbered backtest as an independent attempt to find a winning chart pattern. It needs one controlled research-to-decision system whose final output is the probability of meeting the actual funded objective, not a sequence of increasingly attractive historical PnL figures.

No one can legitimately guarantee that every new test will produce better PnL. Requiring monotonic PnL creates a direct incentive to keep selecting, filtering and tuning against the same history. Research quality can be monotonic; financial outcomes cannot be promised to be monotonic. Literature on backtest overfitting and multiple testing supports that distinction:
- Bailey et al., *The Probability of Backtest Overfitting*: https://doi.org/10.21314/JCF.2016.322
- Bailey & López de Prado, *The Deflated Sharpe Ratio*: https://doi.org/10.3905/jpm.2014.40.5.094
- White, *A Reality Check for Data Snooping*: https://doi.org/10.1111/1468-0262.00152

## Root cause of the repeated loop

1. **The wrong progress unit:** numbered experiments and headline PF/PnL were being treated as progress toward passing. More experiments on already-inspected history do not imply a greater chance of success.
2. **Candidate research and package administration were coupled:** an old missing artifact could become a project-wide stop, leading to repeated audits rather than a final disposition. The canonical ledger and family map have now been reconciled through R328; truly unavailable historic artifacts are explicitly non-promotable exceptions rather than pretending their rows were recovered.
3. **There was no immutable end-to-end acceptance funnel:** data eligibility, signal economics, reproducibility and challenge-path outcomes must be separate gates. A test that fails its sample gate cannot be called a negative edge; an archive failure cannot be called a market result; a clean code test cannot approve a signal.
4. **The final objective was not the primary comparison metric:** a strategy with positive PF may still take too long or breach daily/static loss rules. The project's target is completion of both phases by day 179 without a breach.
5. **The evidence base is reused:** EURUSD 2017–2025 and US indices 2017–2026 have been inspected repeatedly. Those periods can support diagnosis but must not be mislabeled fresh independent validation. XAUUSD 2026 remains protected under the existing project rule.

## The solution: a bounded, one-way decision pipeline

### Gate 0 — Project integrity (historical debt is closed)

- Canonical [master ledger](MASTER_SEARCH_LEDGER_R251_R328.csv) and [family map](SEARCH_FAMILY_MAP_R251_R328.md) are the source of truth through R328.
- Only R259 (workflow incident) and R267 (no standalone source record surfaced) are absent from the experiment ledger; no metrics are invented.
- R317/R318/R326 package gaps and R319/R320 post-outcome registration are classified explicitly as historical non-promotable exceptions. They must not be reopened to tune failed ideas.
- The five old smoke-test issues #1/#2/#3/#5/#6 were dispositioned and closed.
- This closes the *historical reconciliation task*. It does not prove an edge exists.

### Gate 1 — Candidate-independent infrastructure verification (no signal PnL)

Verify once, using synthetic/known fixtures rather than candidate outcomes:
- exact quote-side handling and BID/ASK pairing;
- timestamp alignment, DST/session reset and gaps without fabricated bars;
- five-minute phone-execution delay and skipped entries;
- adverse gap fills and stop-first ambiguous bars;
- floating and closed equity, daily loss reset, static maximum-loss floor, commissions, swaps, phase targets, minimum trading days and cycle rules;
- deterministic ledger-to-challenge replay and reproducible report output.

The project already has a challenge engine and integration tests. They must be treated as infrastructure only; no strategy edge is inferred from passing these tests. Missing broker-specific contract size, commissions/swap and server reset assumptions must be itemized, sourced and sensitivity-tested before any funded-ready claim.

### Gate 2 — Freeze an experiment before outcomes

Before any PnL:
- define one falsifiable economic mechanism and prove it is not a relabelled closed family;
- document the number of attempted hypotheses, instruments and parameter combinations;
- lock raw-data hashes, sample construction, execution delay, quote sides, costs, splits, selection rule, statistical gates, runner, dependencies and output manifest;
- pass the V2 preflight from GitHub readback;
- stop before outcomes if the eligibility/sample gate fails.

A DATA/PROCESS failure repairs the exact package. A DATA/SAMPLE failure records ineligibility without inspecting PnL. An EDGE failure closes the hypothesis. None can be bypassed by starting another round number.

### Gate 3 — Evaluate research evidence, not just a winning backtest

Use a bounded development set to discover and prune, with explicit multiple-testing accounting. Promote nothing from repeated use of the same validation window. Require:
- realistic executable-side fills, spreads, extra slippage, commissions and swaps;
- net economics in discovery and independent confirmation;
- adequate sample, year/regime stability and a predeclared weekly inference test;
- deterministic rerun hashes and complete row-level archives;
- a genuinely untouched instrument-period window or future timestamp-locked evidence before making a high-confidence generalization claim.

Do not demand that every exploratory result be positive. Demand that the promotion criteria stay fixed and that no candidate advances after failing them.

### Gate 4 — Optimize the actual challenge result

Only a candidate that passes Gates 1–3 may be evaluated in the funded challenge engine. Use the actual chronological stream and floating equity; do not randomly shuffle away time dependence. Run dependence-aware sequential paths, with fixed risk and explicit costs, to report:
- probability of completing Phase 1 (+8%) and Phase 2 (+5%) before any daily/max-loss breach;
- probability of completing both phases by day 179;
- median/P90/P95 days-to-funded among successful paths;
- breach probabilities by rule, drawdown/loss-streak tails, concurrency, and cost/delay sensitivity.

The target is **P(both phases completed by day 179 without breach)**. PF, expectancy, trade count and annual results are diagnostics and prerequisite gates, not the project objective. Portfolio components can be combined only when a locked comparison demonstrates that the integrated system improves this target metric without violating risk constraints.

### Gate 5 — Forward fallback instead of endless historical recycling

If no historical candidate survives, stop breeding variants on the same historical windows. Continue with a timestamp-locked forward/paper process: record each signal and the first executable quote before its outcome, enforce the real phone delay, do not tune from the forward results, and review only at a fixed checkpoint with a preregistered minimum sample. If the edge does not validate, the correct conclusion is GAGAL/no edge found so far—not a forced pass claim.

## Operating rule going forward

Every project update must report exactly one of:
- **PROCESS PROGRESS:** a specific reproducibility, data, inference or challenge-engine defect was permanently fixed and verified;
- **EDGE EVIDENCE:** a frozen candidate passed/failed a stated economic gate;
- **FUNDED OBJECTIVE:** a complete challenge-path replay quantified completion and breach probabilities;
- **BLOCKED:** name the single gate that failed and the exact evidence needed to repair it.

Do not describe more experiments, more files, or a better discovery PnL as progress toward funded status unless the preregistered scorecard supports that claim. Do not open XAUUSD 2026 or change old failed families to make the next result look better.

## Current conclusion

The project-level solution is to end the open-ended audit loop, freeze process gates, use challenge completion as the final objective and use independent evidence rather than forcing rising PnL. The historical ledger/family-map reconciliation has been completed. No new strategy has been chosen or tested here, and **there is not yet a verified funded-ready system**. The next action is infrastructure verification and then a properly frozen research run; the system should never again present an archive/admin blocker as a reason to keep inventing another strategy round.
