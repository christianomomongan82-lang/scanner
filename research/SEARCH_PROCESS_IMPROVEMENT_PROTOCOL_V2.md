# Search Process Improvement Protocol v2 — Hard Gates, No Process Regression

Effective: 2026-10-21  
Status: AUTHORITATIVE for all new experiments, superseding v1 wherever this document is stricter.  
Execution location: local Python/container. GitHub is the source of truth and archive, not the backtest compute engine.

## 1. Non-negotiable principle

**Research quality must be monotonic; strategy returns are allowed to vary.** No one can guarantee that the next strategy will perform better than the last one. The process can and must get more reliable each round: fewer data defects, zero unregistered parameter changes, zero unexplained rerun differences, complete artifacts, and fewer repeated/near-duplicate hypotheses.

A lower PnL is not a process regression if the experiment was correctly designed and falsified a hypothesis. A higher PnL is not progress if it came from contaminated selection, a data bug, missing execution costs, or an irreproducible run.

## 2. State-machine control

An experiment must move through these states in order. A state cannot be skipped.

1. **PROPOSED** — mechanism, family, novelty, and reason for running it are written. No candidate PnL may be inspected.
2. **REGISTERED** — immutable preregistration, exact configuration/grid, selection rule, period split, costs, manual latency, falsification criteria and required outputs are committed to GitHub. Record the commit SHA and UTC commit time. If a source/data correction is required, append a dated amendment before rerunning outcome code.
3. **DATA-PASS** — input hashes match; timestamp coverage, duplicates, invalid OHLC, static/placeholder rows, gaps, side alignment, timezone/DST, and event eligibility have been audited without selecting on PnL. The filtered-data construction and its hash are recorded.
4. **RUNNABLE** — the exact runner, dependency lock/environment, and one local run command are committed and read-back-verified. Smoke tests confirm no look-ahead, no fabricated bars, exact quote-side fills, exact-delay eligibility and adverse-first collision rules.
5. **EXECUTED** — the registered run has completed locally; run log, seed, source hash and every screened configuration are saved. No parameter adjustment is allowed after outcomes are seen.
6. **REPRODUCED** — a second clean run produces identical full grid, scorecard, selected-candidate trades, eligibility/skip audit, annual/cohort and weekly series hashes. Compressed outputs use deterministic metadata (for gzip, fixed mtime); timestamps/runtime fields are excluded from equality comparisons only if explicitly identified as nondeterministic.
7. **CLOSED** — reports, machine results, artefacts, checksums, binary verdict, failure class, master ledger and PROJECT_STATE have been committed and read back from GitHub. The package clearly states whether validation is contaminated and whether the research claim is reproducible.
8. **CHALLENGE-REPLAY** — permitted only after the candidate passes the registered cost, stability, sample, inference and execution-feasibility gates. Then and only then run the chronological account-level path and sequential two-phase Monte Carlo.

If any gate fails, the run stops at that gate. A stopped/invalid run is recorded as **GAGAL — DATA/PROCESS** for the registered claim, not misrepresented as evidence for or against market alpha. Fix the failure with a versioned amendment and rerun the same locked experiment; do not begin another strategy search to avoid fixing it.

## 3. Mandatory pre-outcome lock

Before any signal PnL is computed, commit all of the following:

- Unique experiment ID; primary family; parent IDs; related closed candidates; explicit novelty check against the master ledger and family map.
- One falsifiable economic/mechanical hypothesis, direction and event eligibility.
- Exact symbols, quote sides, timezones/DST, event times, signal timestamp convention, entry delay, stops, targets, hold limit, one-position/overlap rules and gap handling.
- Exact data artifact/member hashes and row-quality rules; UTC period boundaries; contamination declaration.
- Complete candidate grid and ranking/selection formula, or a single locked configuration. No silent grid expansion.
- A maximum number of configurations. Default maximum: **100 per registered experiment**. More than 100 requires a separate, pre-outcome justification plus a nested selection plan and multiple-testing treatment; it is not permitted merely to brute-force more thresholds.
- Primary costs plus stress cases, fixed risk assumptions, annual/quarterly and weekly inference plan, bootstrap seed, minimum sample and every binary gate.
- A declaration of how the candidate fits at least a five-minute manual-entry delay. M1 strategies whose typical holding period is shorter than the real reaction delay are rejected as execution-infeasible.
- Required outputs and intended challenge replay conditions if signal gates pass.

**A GitHub commit made after the PnL calculation does not count as preregistration.** Such a run can be archived as exploratory diagnostics, but cannot be called preregistered or promoted from its own reported validation result.

## 4. Data, simulator and output contract

### Before PnL

- Compare the source file hashes to the registered manifest. Check exact paired BID/ASK timestamp sets; duplicates; invalid OHLC; spread sign; repeated-flat placeholders/static quotes; missing minutes; and completeness of every resampled bar.
- Apply the exclusive time cutoff before feature, signal, entry and outcome construction.
- Preserve missing times. Do not forward-fill OHLC, manufacture a tradable bar, pair instruments by row number, or silently substitute a nearest timestamp.
- Produce a complete eligibility/event/skip audit even when the hypothesis has zero eligible events.
- For FX/XAU with paired quote data, buy at ASK and sell at BID; use the opposite side for short entry/exit. Record additional costs separately from observed spread. Gaps through stops must fill adversely; ambiguous SL/TP bars resolve against the strategy.
- Verify all feature windows use only information available at signal time; reset or reject lookbacks across gaps according to the registered rule.

### Archive must contain (or run is NOT CLOSED)

1. Immutable preregistration markdown and machine-readable configuration.
2. Input manifest with artifact IDs, member names, date range, data cleaning rules and SHA-256 values.
3. Exact runner source, source checksum, Python/library versions and one documented local command.
4. Data-quality report and complete eligibility/skip/event audit.
5. Complete candidate grid and scorecard, including rejected configurations and the selection rank.
6. Full chronological trade ledger for every frozen finalist, with entry/exit timestamp, executable price sides, stop/target, reason, cost components and realized outcome.
7. Weekly net-R series with zero-trade weeks preserved, annual/cohort results and bootstrap outputs.
8. Machine-readable result JSON, human-readable final report and run log.
9. SHA-256 manifest for every output; after commit, read every required path back from GitHub and compare hashes/sizes.
10. Updated master ledger and PROJECT_STATE entry with direct file links and binary verdict.

A hash list without the required row-level files or deterministic regeneration path is not complete archival. If repo/file-size restrictions block storage, split files into verified chunks, document reconstruction, and verify reconstructed byte hashes. If neither storage nor reconstruction can be verified, stop and mark archive gate failed. **Do not carry an open ledger gap into the next search.**

## 5. Frozen-period and multiple-testing policy

- A period previously used to pick a strategy or rank a large grid is development data, not independent validation.
- EURUSD 2021–2026 and US index 2017–2026 have been repeatedly inspected. Treat them as contaminated diagnostics, not fresh independent evidence.
- 2021–2025 has been reused across multiple cross-family experiments; do not label it a pristine project-level OOS set.
- The reserved XAUUSD 2026 period remains closed unless a single candidate first passes all pre-2026 gates and its test is registered and frozen. Do not open 2026 to choose, tune, or rank candidates.
- Discovery candidates chosen after a broad grid are subject to selection bias. Report total configurations tested, count passing discovery, and out-of-period performance of every frozen finalist. Apply a predeclared multiple-testing correction or explain why it is not applicable.
- Once a family fails its registered mechanism on confirmation/forward evidence, close that family. No post-hoc direction flip, session shift, threshold/stop/target rescue, or cherry-picking years. A materially different hypothesis requires independent causal justification and its own new registration—not a new round label.

Because the project-wide historical windows are contaminated, a historical pass alone cannot establish a high-confidence new edge. Promotion evidence requires an independently held-out instrument-period/window or future timestamp-locked forward evidence.

## 6. Fixed economic gates

Unless a stricter mechanism-specific threshold is registered before outcomes, require all applicable checks:

- At least 200 discovery trades and 100 validation trades for a standard screen. Lower-frequency events may be described as hypotheses, but cannot pass the evidence gate without a justified longer independent horizon and adequate inferential power.
- Positive net R and PF >= 1.05 at registered primary cost in both discovery and validation.
- Positive net R and PF >= 1.00 under the registered execution-cost stress; never excuse a negative expectancy by increasing risk.
- Positive results in at least 3 of 4 discovery years (or equivalent predeclared duration rule), without one outlier year dominating total return.
- Validation weekly block-bootstrap 95% lower bound for mean net R > 0. The series includes zero-trade weeks; block length and seed are frozen before outcomes.
- Realistic five-minute manual-delay stress, side-correct fills, holding-time feasibility, and no invalid signal/branch reachability.
- Report mean/median R, PF, net R, max DD in R, losing streak, trade frequency, holding time, skip reasons, year/quarter cohorts and cost/delay sensitivity.

These are research gates, not a funded guarantee. A candidate that fails one required gate is **GAGAL**. PF alone is never the objective.

## 7. Challenge target comes after edge validation

Only candidates that pass the preceding gates proceed to account-level replay. Use the actual provider rule definitions, exact symbol contract value, commission/swap, spread/slippage, timezone/DST/day reset, floating equity, minimum trading days, forced-close/time-cycle and Quick Strike restrictions. Unknown rules must be explicitly marked unknown, not guessed.

Use chronological event paths and a shared risk controller for simultaneous/correlated exposure. Run at least 10,000 dependence-aware sequential paths after those assumptions are verified. Report:
- probability of completing Phase 1 and Phase 2 without any loss-rule breach;
- probability of reaching funded status by project day 179 (a project objective, not a firm rule);
- breach type/probability, median and 90th/95th percentile time to funding;
- worst drawdown/loss streak, sensitivity to costs/delay and uncertainty intervals.

Do not run a challenge replay for a strategy with failed expectancy gates. Do not report single-path success as pass probability. Do not call a candidate funded-ready until the actual-account contract and the required replay pass.

## 8. Monotonic process scorecard

At every close-out, add measured values to the cumulative scorecard. Required operating targets are invariants:

| Process measure | Required value |
|---|---:|
| Pre-outcome registrations committed before outcome compute | 100% |
| Candidate configurations matching registered grid exactly | 100% |
| Source-data hashes verified before features/PnL | 100% |
| Required runner/config/audit/grid/finalist ledger committed and read-back-verified | 100% |
| Independent clean reruns with identical deterministic output hashes | 100% |
| Unexplained differences or undocumented substitutions | 0 |
| Unclosed ledger/archive gates before next hypothesis | 0 |
| Protected holdouts opened before pre-gates pass | 0 |
| Closed-family tuning on previously inspected outcomes | 0 |
| Candidate promotion without cost/stability/manual-delay gates | 0 |
| Strategy pass-probability claims based solely on one historical path | 0 |

If any measured invariant regresses, the next signal search is **blocked** until the defect is corrected. A failed edge search with all process invariants passing is still research progress because it eliminates a hypothesis reliably. Record lessons once in the family map so descendants do not repeat the same mistake.

## 9. Current baseline and explicit corrective action

- R317/R318: a repeated-flat placeholder defect was found after initial outcome runs. Their corrected outcome report exists, but the full original runner and all row-level output were not recovered during the later audit. They remain archive-incomplete and cannot be retroactively described as end-to-end reproducible.
- R319/R320: their source was archived after calculation, so these runs were not formally preregistered before PnL. Source/data identity, deterministic outputs and repeat-run hashes were checked; the full ledgers regenerate but were not retained as standalone row-level repository files. This is an improvement in computational reproducibility, but still does not meet the new full archive/pre-registration invariant.
- Therefore the last rounds are **not a perfect process baseline**. V2 is adopted specifically to prevent the same deficiencies from being repeated. No further signal PnL search begins until the next experiment package passes this gate before and after execution.
- The 35 integration/synthetic tests on the challenge adapter validate infrastructure only; they do not validate alpha. Actual account contract/fees/swaps/server reset details remain separate requirements for funded promotion.

## 10. Close-out checklist

Before calling any run DONE, answer YES to each:
- [ ] Was its preregistration read back from GitHub and committed before the first outcome compute?
- [ ] Do source data, cleaned data and every executable assumption match their recorded hashes/rules?
- [ ] Are all configs and selection logic exactly the locked ones?
- [ ] Does the second run produce identical deterministic outputs?
- [ ] Are the complete required audit/grid/finalist ledgers and all scores committed and read-back-verified?
- [ ] Is the binary result and failure class reconciled against every gate?
- [ ] Is the master ledger and PROJECT_STATE updated and read back?
- [ ] Is every open issue either fixed or explicitly blocking next search?
If any answer is NO, the run is not fully complete and no next signal search may launch.

Final rule: **Never sacrifice process integrity to produce a better-looking strategy result.**


## 11. Run the gate validator, not just the checklist

The reference validator is `research/verify_experiment_package_v2.py`; its regression tests are `research/test_verify_experiment_package_v2.py`. It fails closed if mandatory preregistration fields or pre-outcome files are absent, a candidate grid exceeds 100 without a documented nested-selection/statistical plan, the registration is after the first outcome timestamp, the final output manifest omits files or hashes/sizes differ, the final verdict is not binary, or rerun comparisons are missing/non-identical.

Run the test suite locally before adopting a validator revision:

```sh
python -m unittest -v research/test_verify_experiment_package_v2.py
```

For a candidate package directory, run both stages explicitly:

```sh
python research/verify_experiment_package_v2.py preflight path/to/experiment_package
python research/verify_experiment_package_v2.py closeout path/to/experiment_package
```

A `BLOCKED` response is a hard stop, not a warning. The validator supplements rather than replaces human review of GitHub commit order, data semantics, hidden leakage and the economic hypothesis. The current local reference suite passed 6/6 tests on 2026-10-21; this is process-tool testing, not evidence for a market edge.
