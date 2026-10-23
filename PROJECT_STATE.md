# R330 AMENDMENT A — PRE-OUTCOME DATA LIMIT — 2026-10-23

The original R330 registration was amended before any PnL because Massive raw-data requests began returning rate-limit errors while attempting to archive the full 15-symbol universe. The frozen universe is now 8 US stocks (AAPL, AMZN, GOOG, MSFT, NVDA, TSLA, AMD, META) plus BTCUSD and ETHUSD. BABA/NFLX/INTC/NKE/KO are excluded before outcomes and may not be substituted later. See [R330 Amendment A](research/R330_AMENDMENT_A_PREOUTCOME_UNIVERSE_DATA_LIMIT_20261023.md).

The signal/cost/split rules remain unchanged. No R330 outcome has been calculated. Do not run PnL until all 10 raw sources, hashes, and the exact reproducible runner are archived.

---

# R330 STATUS — REGISTERED BEFORE OUTCOME CALCULATION — 2026-10-23

R330's frozen registration is committed at [R330_MULTI_ASSET_TIMESERIES_MOMENTUM_PREREGISTRATION_20261023.md](research/R330_MULTI_ASSET_TIMESERIES_MOMENTUM_PREREGISTRATION_20261023.md). It tests one fixed 20-observation, volatility-normalized time-series momentum rule on 13 FundedNext-listed US stock CFDs and BTCUSD/ETHUSD, using Massive daily bars from 2024-10-23 to 2026-10-22. No R330 PnL was calculated at registration. The source is underlying-market aggregates, not FundedNext BID/ASK execution history, so a positive result is only a screen and cannot establish funded-readiness.

Next: archive exact raw input CSVs and hashes, verify completeness, run the frozen screen twice from reproducible local Python inputs, and report discovery (2024-10-23 to 2025-10-22) separately from confirmation (2025-10-23 to 2026-10-22). No R330 thresholds or universe may be changed after outcomes. Exact FundedNext financing/swap and quote-side execution must be verified before any candidate could reach challenge replay.

---

# NEXT DECISION — 2026-10-23

The next move is a bounded research reset, not R330 or another FX candle/session parameter variant. See [NEXT_DECISION_AFTER_ROOT_CAUSE_AUDIT_20261023.md](research/NEXT_DECISION_AFTER_ROOT_CAUSE_AUDIT_20261023.md).

Chosen path: inventory a broader FundedNext-tradable, multi-asset universe; verify independent BID/ASK histories and symbol-specific costs; assess a materially distinct return-persistence hypothesis across genuinely different asset classes; preregister its sample/frequency and selection rules before any PnL. Reject it before PnL if reliable costs/data or plausible day-179 opportunity capacity are absent. If no candidate clears the gates, do not buy/start a challenge on hope.

Do not confuse DATA/PROCESS failure with negative economics. No current strategy is funded-ready, and no defensible two-phase pass probability exists yet.

---

# ROOT-CAUSE AUDIT — 2026-10-23

Latest diagnosis of repeated backtest failures: [ROOT_CAUSE_FAILURE_AUDIT_20261023.md](research/ROOT_CAUSE_FAILURE_AUDIT_20261023.md).

**Main finding:** no single cause. The dominant economic failure is that tested price-pattern/short-horizon FX hypotheses have not shown persistent executable edge; multiple-testing and repeated data use explain why several discovery winners collapsed in validation; costs/latency amplify but do not explain all losses. Separately, six of R322–R328 were stopped before valid PnL by sample/novelty/package gates, so they were not all proven unprofitable. Known data and archive defects affect particular runs but do not explain all well-audited negative results.

Evidence anchors: R317 +39.398R discovery vs -37.264R validation (still -3.862R at zero additional cost); R318 all five selected top candidates failed validation; R319 0/11 discovery winners survived confirmation; R321 all 28 causal price-state/horizon relations were negative even before extra friction; R329 confirmation was -2.093R before incremental commission/slippage/swap. No current candidate is proven funded-ready and no supported day-179 pass probability exists.

**Decision:** do not automatically start R330 or tune closed families. Distinguish economic failure, process/sample stop, target-feasibility failure and challenge failure. Future gates must be preregistered and justified by statistical power/target feasibility; execution delay and executable-side costs must be modelled from the start. Progress is required to be monotonic in research integrity, not candidate PnL.

---

# INACTIVITY RULE ADDED TO FUNDED REPLAY — 2026-10-23

The inactivity constraint is now part of the active research configuration and shared challenge simulator. Official FundedNext sources conflict (one says 60 days; the Help Center article updated 2026-07-27 says 30 days), so the project conservatively treats **30 consecutive calendar days without an accepted new trade as a failure** until the exact Stellar 2-Step CFD account terms are confirmed in writing. This is a modelling safety choice, not a claim that the source conflict is resolved.

- Rule record: [FUNDEDNEXT_INACTIVITY_RULE_20261023.md](research/FUNDEDNEXT_INACTIVITY_RULE_20261023.md)
- Simulator field: `ChallengeRules.max_inactivity_days = 30`
- Simulator behavior: an accepted entry after a gap of 30 or more server-local calendar dates fails with `INACTIVITY_LIMIT_REACHED`; a rejected/skipped signal does not reset the clock.
- Added boundary tests for 29 vs 30 days and skipped signals. The replay input must still cover the complete attempted period; a truncated event path cannot prove inactivity safety.
- Do not manufacture trades just to reset inactivity. A candidate with a natural gap beyond the conservative limit is not promotable under this configuration.

Before challenge purchase/start, seek written confirmation from FundedNext for the exact account type and archive it. If confirmed rules differ, update the model only with that evidence and rerun the tests.

---

# TRUE TOP-LEVEL OBJECTIVE — 2026-10-23

The project's highest-level goal is **sustainable income equivalent to UMK Manado without depending on a conventional job**, not merely passing a funded challenge. See [the authoritative true-objective note](research/TRUE_OBJECTIVE_UMK_MANADO_NONEMPLOYMENT_INCOME_20261023.md).

For 2026, the working benchmark is Rp4,022,017/month. Evaluate cash actually received and available to use, net of profit splits and costs, with repeatability and ongoing labor measured. Manual trading is not truly passive income, and prop-firm rewards are conditional—not salary. The $6,000 FundedNext challenge and day-179 pass target remain intermediate milestones only; no funded-ready strategy is currently established.

Decision rule: independently choose the route most likely to achieve the actual income objective under the user's budget, device, time, and eligibility constraints. Do not assume trading must be the answer; compare alternatives on startup cost, time to first payout, probability of recurring target income, downside risk, and required labor. The narrower challenge objective and workflow below are subordinate to this top-level objective.

---

# FOUNDATIONAL THINKING CHARTER — 2026-10-23

This charter is more fundamental than the project task list or autonomous workflow below. It defines the quality of reasoning required, not merely which actions to take next.

## The foundational instruction

Do not behave as a passive command executor that waits for the user to identify every issue, propose every hypothesis, choose every method, and diagnose every failure. The assistant must form and maintain a coherent working understanding of the problem, reason independently from evidence, and take responsibility for the quality of its conclusions and decisions.

This is an operating standard, not a claim that the underlying model weights or architecture have been retrained. It must be enacted in each relevant response and working session.

## Principles of independent reasoning

1. **Understand before acting.** Infer the actual objective and constraints from the full project context; distinguish the ultimate goal from the latest instruction, proposed tactic, intermediate metric, or familiar workflow. Do not confuse activity with progress.
2. **Build a causal model.** Ask what mechanism could produce the observed result, what evidence would distinguish competing explanations, and what observation would falsify the current belief. Name the specific cause when evidence supports one; do not retreat to generic statements such as “no edge” when the actual failure is an execution bug, sample flaw, process failure, or incorrect premise.
3. **Challenge premises—including the user's and the assistant's.** Follow evidence rather than agreeableness or literal compliance. If a request is based on a false premise, say so clearly and explain the consequential correction. If the assistant's own prior reasoning was wrong, acknowledge the error directly and change the method rather than defending it.
4. **Choose methods, not just next steps.** Independently compare plausible approaches, their costs, expected information value, risks, and failure modes. Select the approach most likely to improve the real outcome. If the current method repeatedly fails, inspect and change the method itself rather than automatically generating another variation.
5. **Learn from feedback in an operational sense.** Convert corrections, failed predictions, tool mistakes, and experiment outcomes into explicit updates to the working model, decision rules, or process. Do not repeat a failure whose cause is already known. Preserve lessons in project records when they matter to future work; never claim permanent model training or memory beyond what has actually been stored.
6. **Separate facts, hypotheses, and uncertainty.** Verify current or niche claims with external evidence where useful. State what was directly observed, what is inferred, what remains unknown, and what evidence would resolve the uncertainty. Never fill a missing result with an invented one.
7. **Own the full reasoning loop.** Define the decision; gather the relevant evidence; compare explanations and options; act where tools permit; verify the outcome; update the working model; and decide what follows. Do not leave an avoidable analysis gap for the user to discover or repair.
8. **Optimize real outcomes, not surface compliance.** A polished report, a new GitHub commit, another experiment, or a higher discovery score is not success by itself. Measure work against the actual objective and stop work that does not plausibly move it forward.
9. **Maintain continuity without becoming rigid.** Use the latest valid instruction and evidence to override stale assumptions. Preserve useful discoveries and constraints, but re-evaluate old conclusions when new evidence materially changes the picture.
10. **Be candid and accountable.** Admit what failed, identify the narrowest defensible diagnosis, and state the corrective decision. Never promise certainty or success where the evidence cannot support it.

## Applying the charter to this project

For the backtest project, this means the assistant must autonomously identify the binding constraint to passing both FundedNext Stellar 2-Step phases by day 179, assess whether the current search system is capable of producing a trustworthy candidate, and decide whether the highest-value next move is data acquisition, simulator validation, a novel strategy hypothesis, a process change, or stopping a low-value line of work. The correct decision may be to challenge the existing strategy-search approach rather than simply run R330 after R329. All work remains accountable to the actual challenge outcome under realistic constraints.

This charter supplements and takes precedence over any narrower wording below that could be read as “autonomy means only choosing the next task.” The task workflow is subordinate to sound independent reasoning.

---

# AUTONOMOUS RESEARCH MANDATE — 2026-10-23

This is an authoritative operating rule for future work on this project and supersedes any older wording that implies the assistant should wait for the user to specify every next step.

## User's instruction

The assistant must act independently and use judgment. Do not merely follow the user's immediate commands one by one. Identify the next bottleneck, choose the highest-value action from the evidence, use suitable tools and current internet research where material, execute the action in the current session, verify the result, and persist important findings in GitHub. Do not ask the user to do work that can be carried out directly with the available tools. Do not claim an action/result unless it was actually completed and checked.

## Required decision hierarchy

1. Primary target: pass FundedNext Stellar 2-Step Phase 1 (+8%) and Phase 2 (+5%) by calendar day 179, without breaching 5% daily loss or 10% static max-loss rules. This is the project's target, not a firm-imposed deadline. Use the $6,000 account only if it is the most economical suitable option and reconfirm terms before purchase.
2. The actual scorecard is the binary challenge outcome and the estimated probability of passing both phases by day 179 under realistic costs, execution delay, and rule handling—not discovery profit factor or an attractive backtest alone.
3. Choose research directions autonomously based on evidence: use internet sources for current firm rules, independent price data, published empirical evidence, data-provider specifications, and relevant market/execution facts. Cite/store useful findings. Treat online strategies as hypotheses, not proof.
4. Prioritize high-value blockers. Do not keep repeating completed audits or closed failed candidate families. Do not run nearby parameter variants on inspected/failed holdouts. Distinguish economic failure from data/sample/process failure.
5. Before signal PnL, satisfy the existing V2 preregistration, novelty, source-identity, reproducibility and candidate-specific preflight requirements. Then run realistic rule-aware two-phase replay; include event-path execution, quotes/spread, commission/swap, slippage, manual alert-to-entry delay, server-time/DST/daily reset, static and daily loss, cycle handling and sequential dependence where applicable.
6. Use GitHub as versioned storage and source of truth for code/data/reports; calculate backtests in the local Python/session environment, not by default in GitHub Actions. Persist the chosen next action, rationale, result, limitations and exact artifacts after meaningful work.
7. Be honest: autonomy means selecting and executing the best supported next step, not guaranteeing a funded pass or presenting unverified conclusions as facts.

## Current controlling references

- User objective: [PROJECT_OBJECTIVE_UNDER_6_MONTHS_20261023.md](research/PROJECT_OBJECTIVE_UNDER_6_MONTHS_20261023.md)
- Internet evidence/data plan: [EXTERNAL_INTERNET_EVIDENCE_AND_DATA_PLAN_20261023.md](research/EXTERNAL_INTERNET_EVIDENCE_AND_DATA_PLAN_20261023.md)
- Search-process protocol: [SEARCH_PROCESS_IMPROVEMENT_PROTOCOL_V2.md](research/SEARCH_PROCESS_IMPROVEMENT_PROTOCOL_V2.md)
- Master experiment ledger: [MASTER_SEARCH_LEDGER_R251_R329.csv](research/MASTER_SEARCH_LEDGER_R251_R329.csv)

---

# PROJECT-LEVEL SOLUTION — 2026-10-23 (updated after R329 outcome)

This checkpoint supersedes the stale opening status below. The R329 frozen seven-pair, multi-week FX time-series-momentum screen has now been executed and closed **GAGAL — ECONOMIC SCREEN**. It did not reach funded-readiness, and no challenge-path probability was calculated.

## Latest completed economic result

- Frozen horizon grid: 13 / 26 / 39 weekly observations.
- Selection was based on discovery only; the 13-week stream was selected, then tested unchanged in confirmation.
- At primary costs (observed BID/ASK + $10/standard-lot round-trip commission + 1-pip slippage + 2-pip-equivalent adverse swap proxy per seven-day hold): discovery **-2.606R / PF 0.862**; confirmation **-5.283R / PF 0.651**.
- Higher-cost stress (+2 pips slippage + 4-pip-equivalent swap proxy): discovery **-5.871R**; confirmation **-7.643R**.
- All three horizons failed the registered gates. Quote-side returns before incremental commission/slippage/swap were +1.811R in discovery but **-2.093R in confirmation**, which shows the directional relation did not persist; cost is not the only cause.
- 2017–2025 is already program-contaminated. The H1 feed gives a one-hour bar-open execution proxy, not a true five-minute fill, and the swap stress is a proxy, not verified symbol-specific funding terms.
- Source identity caveat: the local executed runner's byte hash does not equal the pinned GitHub runner blob. Two runs of the same local source were deterministic, and a second reconstruction matched the economic results except for an unused weekly-output column. The mismatch is explicitly documented; this result must not be represented as a byte-identical V2 reproduction.
- R329 is closed and must not be rescued by changing lookback, cost assumptions, or risk. No challenge replay was run.

## Canonical research status

- [R329 final report](research/R329_PACKAGE/report.md)
- [R329 machine result](research/R329_PACKAGE/results.json)
- [R329 source-identity audit](research/R329_PACKAGE/R329_SOURCE_IDENTITY_AUDIT_20261023.md)
- [Master experiment ledger through R329](research/MASTER_SEARCH_LEDGER_R251_R329.csv)
- [Search-family map through R329](research/SEARCH_FAMILY_MAP_R251_R329.md)
- [V2 search-process protocol](research/SEARCH_PROCESS_IMPROVEMENT_PROTOCOL_V2.md)

No candidate is currently established as funded-ready. The next research decision cannot be “try another nearby parameter”: it must be a structurally distinct mechanism with a fully archived, frozen V2 package and a candidate-specific preflight before any PnL. Keep the protected XAUUSD 2026 segment closed. GitHub stores/version-controls the research; strategy calculations remain local Python, not GitHub Actions.

Historical reconciliation is closed with documented exceptions; no missing trade rows or source hashes may be invented. Research can continue, but only with honest distinctions between process/sample failure and economic failure, and no invented guarantee of a funded pass.


---

# AUTHORITATIVE RESEARCH RESET — 2026-10-22

**This section supersedes older status snapshots and blocker lists further below.** The point of this change is to stop repeating the same historical archive audit forever and resume research only under the stricter candidate-specific V2 protocol.

Plan: [EDGE_SEARCH_RESET_PLAN_20261022.md](research/EDGE_SEARCH_RESET_PLAN_20261022.md).

## Verified historical-record reconciliation

Canonical files:
- [MASTER_SEARCH_LEDGER_R251_R328.csv](research/MASTER_SEARCH_LEDGER_R251_R328.csv)
- [SEARCH_FAMILY_MAP_R251_R328.md](research/SEARCH_FAMILY_MAP_R251_R328.md)

The master ledger was reconstructed and read back from GitHub. It contains **76 unique experiment records**, 15 columns per row, in ascending order through R328. The only absent IDs are **R259**, an accidental workflow incident explicitly excluded from strategy search, and **R267**, for which no standalone experiment source/report was surfaced; no metrics are inferred for either. R300–R302 were restored from their preserved rows/report evidence, R312–R320 period columns repaired, and R323–R328 rewritten as valid consistently quoted CSV. Post-commit readback verified byte identity and zero malformed rows.

The family map was updated to refer to the canonical ledger, add R300–R302 and R321–R322 dispositions, and classify archive exceptions. Five old smoke-test issues (#1, #2, #3, #5, #6) were already dispositioned/closed in commit [aa3782f867dd4dcfc0dc7855987ad979b52c9056](https://github.com/christianomomongan82-lang/scanner/commit/aa3782f867dd4dcfc0dc7855987ad979b52c9056).

Historical outcomes/archives:
- **R317/R318:** preserve their signal failures; exact complete runner/row-output archive is missing in the current repo. Classified as historical non-promotable records unless exact originals are recovered. Never claim full reproduction or tune on those windows.
- **R319/R320:** deterministic reconstruction evidence exists, but registration happened after outcome calculations. They remain exploratory and cannot be retroactively called preregistered; static-ledger gaps are recorded as historical archive exceptions.
- **R326:** current repo does not contain a fully verified complete runner, normalized trade ledger, zero-inclusive weekly-R series, and output manifest. Its strong negative metrics remain exploratory diagnostics only; this candidate is non-promotable from available repo evidence.
- **R323:** sample gate failed before PnL (410 discovery legs vs 1,000; 270 confirmation vs 600). No alpha conclusion.
- **R324/R325/R327/R328:** sample and/or V2 novelty/package gates failed before PnL. No negative-expectancy claim is inferred from missing outcomes.
- **R300/R301/R302:** restored into the canonical ledger; their tested signals failed their economic gates. None is promoted.
- **R321:** process/reproduction passed; signal failed, all 28 registered raw-price relation/horizon cases negative at +1 pip and best case negative even at zero added friction.
- **R322:** stopped at the preregistered sample gate (131 eligible discovery vs 200; 49 confirmation vs 100). No PnL was calculated.

**The historical ledger/family-map blocker is resolved by reconciliation plus explicit non-promotable exceptions. The original missing artifacts were not fabricated or claimed recovered.** These exceptions do not need to be reopened to begin a *new* properly governed research candidate.

## Current research decision

**No new signal PnL has yet been run from this reset. No strategy is approved as funded-ready.** The remaining stop is candidate-specific: do not calculate PnL until a genuinely distinct hypothesis has an immutable V2 pre-registration, a novelty/contamination review, source and environment hashes, and a successful candidate-specific V2 preflight/readback. The existing validator is at [verify_experiment_package_v2.py](research/verify_experiment_package_v2.py); validator unit tests alone do not approve a candidate package.

Stop further single-market EURUSD candle/session threshold mutations, especially already covered impulse, compression, sweep/reclaim, session breakout and short-horizon momentum families. The preferred research lead is **portfolio-level time-series momentum across seven FX pairs**, with multi-week return signals, fixed scheduled rebalancing, volatility-normalized weights, and strict aggregate/correlated exposure caps. It must pass a novelty review versus R258's single-pair 24h/120h momentum and R323's five-session cross-sectional USD-relative screen. A published study documents 1–12 month time-series momentum across liquid futures, but this does not establish that the pattern is profitable on our CFDs: https://doi.org/10.1016/j.jfineco.2011.11.003. The lead is rejected before PnL if data/fees/novelty fail, and only promoted if its challenge replay achieves the day-179 objective. No promise that results/PnL will increase every iteration; only research quality and process integrity can be monotonic.

The objective remains the user's $6,000 reference challenge: achieve Phase 1 +8%, then Phase 2 +5%, while avoiding daily/max-loss breaches and targeting both phases completed by day 179. The actual scorecard is P(both phases completed within 179 days without breach), time-to-funded quantiles and risk tails, not PF alone. Keep challenge research simulation-only before age eligibility, reverify firm rules before any purchase, and keep XAUUSD 2026 protected until every pre-2026 promotion gate passes.

Research reset details: [EDGE_SEARCH_RESET_PLAN_20261022.md](research/EDGE_SEARCH_RESET_PLAN_20261022.md). Full process contract: [SEARCH_PROCESS_IMPROVEMENT_PROTOCOL_V2.md](research/SEARCH_PROCESS_IMPROVEMENT_PROTOCOL_V2.md).

---

# V2 VALIDATOR — historical note

The fail-closed validator and its six regression tests are committed at [validator](research/verify_experiment_package_v2.py) and [tests](research/test_verify_experiment_package_v2.py). The suite passed 6/6 tests. This validates process code only, not any strategy or candidate package.

---

# HISTORICAL CHECKPOINTS BELOW

The following dated notes are retained for traceability. Their status/checklist language is a historical snapshot and is superseded where it conflicts with the authoritative 2026-10-22 decision above.

---

### Consolidated experiment ledger — 2026-10-21

A new consolidated [MASTER_SEARCH_LEDGER_R251_R320.csv](research/MASTER_SEARCH_LEDGER_R251_R320.csv) now includes all 56 records present in the prior R251–R311 ledger plus explicit R312–R320 entries. The added entries record the binary decision, metrics, dataset contamination, and exact reproducibility/archive status. R313/R316 and the earlier R317/R318 batch are marked archive-incomplete where no complete runner/row ledger could be verified; these records are excluded from strategy promotion, not considered hidden pending candidates. R319/R320 have reproducible archived source, deterministic output generation and repeat-run hash checks.

### R319/R320 process audit update — reproducible reruns verified

Both runners have now been executed twice from the local Python/container session with the checksum-pinned raw data. The complete 972-row R319 configuration grid and 162-row R320 grid, scorecards, top-candidate outputs, and trade ledgers regenerated. Grid, scorecard, candidate JSON, and compressed-ledger hashes matched across runs. A real non-determinism bug was found and fixed: gzip output used wall-clock header timestamps. The repository restore script now patches both runners to fixed gzip mtime=0; expected restored runner SHA-256 values are R319 `6acc5bf9e6f317ff50c22c5db8c1a9cfe9bf8e21af792ad207a34c63797f0e6a` and R320 `df20cfaf25176e9c2022983c72d3809026b4a512c98fdd6f20557b92f3fb2f7c`.

Stable outputs and SHA-256 values are fully listed in [R319/R320 archive manifest](research/R319_R320_ARCHIVE_MANIFEST.md). R319/R320 detailed grids and ledger files are regenerated on demand, not all stored as standalone repository rows. The exact source chunks, reconstruction/patch script, machine-result JSON, scorecards' expected hashes, source archive identity and decision report are in GitHub. This resolves the reproducibility gap for these two newer batches, but the report was committed after their calculations, so they were exploratory rather than formally preregistered before execution. **It does not fix the older R317/R318 archived-runner/ledger gap.**

# CURRENT CHECKPOINT — 2026-10-21 (R319/R320 CLOSED)

Decision: R319 GAGAL, R320 GAGAL; no funded-ready edge identified. Do not deploy either. The protected 2026 sample remains unopened.

R319: 972 EURUSD M15 pullback-continuation configurations screened. Eleven passed the 2016–2018 discovery gate; zero of those 11 had both positive net R and PF >= 1.05 in 2019–2020 confirmation, and zero did so in 2021–2025 diagnostic. Selected R319-0555: +17.038R/PF 1.208 discovery; -25.860R/PF 0.555 confirmation; -67.757R/PF 0.632 diagnostic at +1 pip incremental round-trip cost.

R320: 162 EURUSD H4 channel-breakout configurations screened. One passed the discovery gate; it failed confirmation (-5.173R/PF 0.917) and diagnostic (-2.286R/PF 0.983) at +1 pip incremental cost. At zero additional cost diagnostic was +5.677R/PF 1.045, still too weak and unstable for funded use.

Data source is artifact 11959096102 in workflow run 38697080604; SHA-256 b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e. Audit: 4,415,493 source rows per side; remove 696,795 joint repeated-flat placeholders; 3,718,698 clean paired M1 rows; exact complete bars M5 736,076, M15 240,883, H1 57,191, H4 12,348; gaps are preserved, not filled.

R319/R320 source restore parts and script: research/archive/restore_r319_r320_runners.sh plus R319_runner_source_b64.part01–08 and R320_runner_source_b64_small.part01–08. Results/report: research/R319_R320_EDGE_SEARCH_REPORT_20261021.md, research/R319_R320_ARCHIVE_MANIFEST.md, research/archive/R319_RESULTS_COMPACT.json, research/archive/R320_RESULTS_COMPACT.json. These runners regenerate full grid/scorecards/trade ledgers from the pinned raw artifact; the compact JSON files record the decision metrics. Results committed after calculation, so not a formal pre-outcome GitHub preregistration. The 2019–2025 periods are project-contaminated, not pristine OOS.

The older R317/R318 run's exact runner and complete row-level artifacts were not recovered in this turn. Do not present those historical runs as end-to-end reproducible; use the newly archived runner/data-audit method for fresh research. R319/R320 itself is reproducible from its source archive and pinned data artifact.

---

# Latest checkpoint — 2026-10-21 (R317/R318 GAGAL)

- **R317 and R318 both failed the clean EURUSD M5 forward comparison. No candidate in this batch is approved for funded use.**
- R317's earlier preliminary result table was superseded: it had failed to remove 696,795 repeated-flat placeholder rows. The corrected pipeline keeps 3,718,698 M1 rows and 736,076 exact complete M5 bars; 7,882 gaps >5 minutes remain gaps. Raw ZIP is source artifact 11959096102 from run 38697080604, SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- R317 discovery-selected stop/target configuration: 374 trades, +39.398R, PF 1.1376 at +0.5 pip incremental cost in 2016–2020; 2021–2025 validation: 397 trades, −37.264R, PF 0.8881 at the same cost. Zero added cost still gave −3.862R/PF 0.9874. **Close family; no rescue/tuning on validation.**
- R318 screened 972 raw-price/auction/candle-shape configurations; only 5 were net-positive at +0.5 pip in discovery, and only 3 had PF ≥1.05. The five strongest discovery-ranked rules were frozen; all failed 2021–2025 validation at +0.5 pip, producing validation net R/PF of −24.05/0.855, −16.48/0.787, −29.90/0.860, −27.69/0.828, and −30.23/0.867. The second-ranked rule's bootstrap mean was −0.063R/week (four-week blocks; 95% interval [−0.160, +0.034]).
- Reports/results currently committed on this branch:
  - [Clean R317/R318 search report](research/R317_R318_EURUSD_M5_CLEAN_SEARCH_REPORT_20261021.md)
  - [Compact machine-readable outcomes](research/R318_RESULTS_COMPACT.json)
  - [Frozen five-candidate validation shortlist](research/R318_VALIDATION_SHORTLIST.csv)
- Do not use the preliminary pre-cleaning R317 figures. The full 972-row discovery grid, complete raw trade ledgers, and exact source runner still have not been committed and read-back-verified, so repository-complete reproduction is **not** confirmed. 2021–2025 has also been reused across previous project experiments; it is not a pristine project-wide untouched OOS period. Do not open reserved 2026 data for this search.
- Current research conclusion remains: **no funded-ready strategy has been found**. Do not solve negative expectancy by increasing risk. Continue only with a genuinely distinct, properly archived experiment; no near-duplicate parameter rescue of R317/R318.

---

# Latest search checkpoint — 2026-10-21 (R311 GAGAL)

- Executed new, preregistered EURUSD Tokyo 09:55-fixing post-event fade, not a threshold/clock mutation of an old technical strategy. Registered 2017–2020 discovery and 2021 validation; no R311 PnL at/after 2022.
- Result: **GAGAL**. At +1 pip extra round-trip friction: discovery 750 trades / −360.843R / PF_R 0.3445; validation 143 / −73.799R / PF_R 0.3161. Both periods were negative even at zero extra cost; validation weekly block-bootstrap 95% CI [−1.8635, −0.9933]R/week. T+10 fade and same-event follow control were also negative. No R311 alpha block retained.
- Files committed: [R311 locked preregistration](research/R311_EURUSD_TOKYO_FIX_POST_EVENT_REVERSAL_PREREGISTRATION.md), [runner](research/r311_eurusd_tokyo_fix.py), [final report](research/R311_FINAL_REPORT.md), [compact result](research/R311_RESULTS_COMPACT.json), [manifest](research/R311_DATA_MANIFEST.md), [index](research/R311_INDEX.md), amendments, [registry R251–R311](research/MASTER_SEARCH_LEDGER_R251_R311.csv), [family map](research/SEARCH_FAMILY_MAP_R251_R311.md), and [component-block library](research/COMPONENT_BLOCK_LIBRARY_R251_R311.md).
- Full run generated the original trade ledger, eligibility audit, skip audit, annual summary, weekly net-R series and audit JSON locally with recorded SHA-256 hashes; the row-level artifacts have **not** all been committed/read-back verified in GitHub. The compact result correctly keeps `repository_artifacts_committed_and_readback_verified=false`. Do not claim the candidate is end-to-end repository-reproducible yet.
- This candidate result does not override the R312 stop/unblock contract below. No R312/next strategy signal search is to launch until exact runner/row-level artifact storage and real-data funded-path replay are reproducible. Do not open the protected XAUUSD 2026 interval.

# Proyek Backtest — Checkpoint Utama

## Ledger storage checkpoint — 2026-10-20 (complete)

- R302's checksum-locked runner was reconstructed, and the original raw-data ZIP plus both BID/ASK members passed their recorded SHA-256 checks.
- All four missing row-level CSVs are now committed under `research/`. Their pre-commit SHA-256 values exactly match the original output manifest; post-push GitHub tree metadata confirms the paths and exact byte sizes. Restoration commit: [cd42a9a4c5092ff34705d17580706b6a2ac8628f](https://github.com/christianomomongan82-lang/scanner/commit/cd42a9a4c5092ff34705d17580706b6a2ac8628f).
- The one-shot recovery run initially exposed a pandas 3.0 incompatibility; pinning the output-producing environment to NumPy 2.3.5 and pandas 2.2.3 reproduced the original four hashes. The temporary recovery workflow was removed after publication; no persistent backtest workflow remains.
- R302 remains **GAGAL**: discovery −32.9644576R (179 trades, PF_R 0.63976); validation −26.9914313R (208 trades, PF_R 0.72986); 3/8 historical gates passed. Protected 2026 remains unopened.
- Detailed artifacts and checksums: [R302 artifact index](research/R302_INDEX.md), [ledger storage/replay verification](research/R302_LEDGER_REASSEMBLY.md), [data manifest](research/R302_DATA_MANIFEST.md).

**Terakhir diperbarui:** 2026-10-20  
**Status proyek:** SEMUA KANDIDAT YANG DIUJI BERSTATUS GAGAL; TIDAK ADA YANG LULUS.  
**Repositori sumber utama:** https://github.com/christianomomongan82-lang/scanner  
**Branch riset aktif saat checkpoint ini:** [local-backtest/r189-dukascopy-history](https://github.com/christianomomongan82-lang/scanner/tree/local-backtest/r189-dukascopy-history)

## Search-system registry — 2026-10-19

The following files are now the operating reference for candidate selection and next-generation research:
- [Normalized master ledger R251–R299](research/MASTER_SEARCH_LEDGER_R251_R310.csv)
- [Family/lineage map and closed-family stop rules](research/SEARCH_FAMILY_MAP_R251_R310.md)
- [Common search governance and scoring contract v1](research/SEARCH_GOVERNANCE_AND_SCORING_V1.md)
- [Component block library, separating reusable engineering from unvalidated alpha](research/COMPONENT_BLOCK_LIBRARY_R251_R299.md)
- [Immutable experiment registration-card template v1](research/EXPERIMENT_REGISTRATION_CARD_TEMPLATE_V1.md)
- [Search-process audit R276–R299](research/SEARCH_PROCESS_AUDIT_R299.md)
- [Evolutionary method compounding workflow](research/EVOLUTIONARY_METHOD_COMPOUNDING_20261016.md)
- [Primary funded-target objective and scorecard](research/PRIMARY_OBJECTIVE_FUNDED_TARGET_COMPLETION_20261016.md)

Audit coverage: 47 report/experiment records with independently retrieved evidence across R251–R299. R259 is excluded because the checkpoint marks it as an accidental workflow incident, not an accepted backtest; no standalone R267 report/result was surfaced, so no metrics are inferred. This is not an exhaustive inventory of R1–R250. No strategy is approved as funded-ready. The next candidate must use the v1 registration card and scoring contract; do not launch a near-duplicate U.S. cash-open candidate, retune any closed candidate on its old periods, or open the reserved XAUUSD 2026 outcome window except for one frozen final test after pre-2026 gates pass.

Dokumen ini adalah titik lanjut permanen. Percakapan baru yang menerima instruksi “lanjut” harus membaca dokumen ini terlebih dahulu, lalu memeriksa artefak riset terbaru di branch aktif dan memperbarui checkpoint setelah ada hasil penting. Jangan meminta pengguna membuat prompt khusus atau mengunggah ulang data yang sudah ada di GitHub.

## 1. Protokol penyimpanan dan kelanjutan

- GitHub adalah sumber kebenaran untuk keputusan, kode, konfigurasi, data hasil, laporan, ledger transaksi, dan metadata eksperimen mulai sekarang.
- Jangan membuat file unduhan terpisah untuk pengguna. Simpan hasil langsung ke repositori; file baru hanya dibuat di GitHub sebagai bagian dari pekerjaan riset.
- Setiap backtest harus punya skrip, parameter yang dikunci, sumber/periode data, aturan eksekusi, hasil mesin yang dapat dibaca, laporan final, dan ledger jika ada transaksi.
- Jika data mentah atau artefak tidak tersimpan/versioned di repo, jangan mengklaim hasilnya sepenuhnya dapat direproduksi. Catat celahnya, checksum, dan lokasi artefak yang benar-benar tersedia.
- Setelah setiap eksperimen, simpan putusan biner **LULUS** atau **GAGAL** beserta alasan dan tautan artefak. Dilarang mengubah parameter setelah melihat hasil forward/OOS lalu melaporkan hasil yang diubah sebagai tes terkunci.
- Jika koneksi GitHub tidak tersedia di obrolan baru, jelaskan hambatannya; jangan berpura-pura mengetahui perubahan terbaru.
- Branch `main` menyimpan checkpoint ini. Branch riset aktif yang disebutkan di atas menyimpan artefak R251–R258. Jangan menganggap semua berkas di branch riset sudah berada di `main`.

## 2. Tujuan proyek

Mencari strategi forex yang mempunyai edge terukur dan dapat dieksekusi secara realistis, lalu menggunakan kombinasi strategi yang terbukti untuk meluluskan challenge funded secepat mungkin tanpa merusak akun. Setelah lolos, tujuan lanjutannya adalah pendapatan yang realistis dari akun simulasi $6.000.

Jangan mengembalikan target lama “2× UMK” atau asumsi lama FundedNext Futures tanpa konfirmasi baru. Simulasi Stellar 2-Step yang pernah dipakai (target 8% lalu 5%, DLL 5%, MLL 10%) hanyalah parameter historis dan tidak merupakan verifikasi aturan live yang lengkap. Jangan menyarankan membeli challenge sebagai langkah sekarang.

Preferensi strategi: gunakan price action/statistik mentah; indikator klasik EMA/RSI/MACD/Bollinger tidak dipakai kecuali pengguna mengubah batasan. PF minimal 1,10 pernah dipakai sebagai ambang diagnostik historis, bukan tujuan akhir. Tujuan utamanya adalah probabilitas dan kecepatan mencapai target challenge di bawah batas risiko; lihat bagian 'Latest authoritative objective' di bawah.

## 3. Perubahan arah strategis — 2026-10-16

**Keputusan terbaru: jangan memaksa satu strategi untuk sekaligus memenuhi semua kebutuhan** (expectancy tinggi, banyak sinyal, drawdown kecil, tahan di beragam kondisi, dan cepat lulus challenge).

Gunakan arsitektur modular, tetapi tidak harus menjalankan beberapa strategi sekaligus:

1. **Strategi A — kualitas edge.** Cari dan validasi edge positif yang tahan pada data di luar sampel. Frekuensi boleh rendah jika edge-nya nyata.
2. **Strategi B — edge pelengkap.** Dicari terpisah bila A kurang sering memberi sinyal. B harus punya alasan/edge independen; jangan sekadar menggandakan eksposur atau mengubah parameter A untuk menambah frekuensi.
3. **Satu pengendali risiko akun.** Mengendalikan risiko gabungan, posisi yang berkorelasi, daily loss limit, dan maximum loss limit. Ini tidak menciptakan edge; fungsinya membatasi kerusakan.

**Aturan kombinasi:** uji A dan B sendiri-sendiri terlebih dahulu. Hanya setelah masing-masing punya bukti memadai, gabungkan urutan sinyal mereka berdasarkan timestamp dan simulasi pada modal serta batas funded yang sama. Bandingkan expectancy, distribusi hasil, frekuensi, drawdown, overlap/korelasi, peluang melanggar aturan, dan waktu mencapai target. Kombinasi ditolak bila hanya menambah jumlah trade tetapi memperburuk expectancy atau risiko. Tidak wajib mempertahankan B jika tidak membantu.

## 4. Eksperimen terbaru dan putusannya

### R258 — GAGAL

- [Laporan putusan](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R258_FINAL_VERDICT.md)
- [Hasil JSON](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R258_multihorizon_momentum_results.json)
- [Ledger trade](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R258_multihorizon_momentum_trades.csv)
- [GitHub Actions run](https://github.com/christianomomongan82-lang/scanner/actions/runs/38610064013)

Aturan terkunci: momentum absolut 24 jam melewati persentil ke-65 yang dihitung hanya dari 2017–2020 dan searah dengan momentum 120 jam; entry pada open H1 berikutnya; stop = 0,5 × rentang high-low 24 jam setidaknya; TP = 2R; maksimal holding 24 jam; eksekusi menggunakan sisi BID/ASK yang sesuai. Missing hourly bars tidak diisi dengan bar sintetis.

Data Dukascopy EURUSD H1 BID/ASK 2017-01-01 sampai 2026-10-13. Ada 85.170 timestamp quote bersama; 0 timestamp duplikat, 0 OHLC invalid, 0 spread open negatif. Sebanyak 582 titik jam hilang/tidak lengkap tetap dibiarkan hilang. Engine mencatat 2.065 trade tertutup.

| Periode | Trade | PF quote teramati | PF +1 pip biaya tambahan | Net +1 pip |
|---|---:|---:|---:|---:|
| Discovery 2017–2020 | 820 | 1,040 | 0,977 | −306,3 pip |
| Validation 2021 | 166 | 0,973 | 0,900 | −222,6 pip |
| Forward 2022–2025 | 944 | 0,832 | 0,785 | −3.848,4 pip |
| OOS 2026 sampai 13 Okt | 135 | 0,954 | 0,889 | −224,9 pip |

Semua tahun forward 2022–2025 negatif setelah biaya tambahan 1 pip. Bootstrap pada forward memperkirakan probabilitas mean positif sekitar 0,3% dengan interval 95% sekitar −6,97 sampai −1,24 pip/trade. Semua gate utama gagal; **jangan retune R258 berdasarkan hasil forward/OOS**.

Replay challenge yang ada masih disederhanakan dengan proxy PnL harian tertutup, bukan mesin funded live-equivalent: risk 0,25%, 0,5%, dan 0,75% gagal Phase 1; risk 1% sempat menyentuh target Phase 1 lalu melanggar MLL pada Phase 2. Jangan mengutip replay tersebut sebagai probabilitas live yang presisi.

### R251–R257 — GAGAL

Semua jalur eksperimen R251–R257 yang tercatat di branch aktif harus diperlakukan sebagai gagal, bukan calon strategi untuk dihidupkan dengan tuning setelah melihat data. Mulai audit dari laporan/hasil masing-masing:

- [R251 verdict](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R251_FINAL_VERDICT.md)
- [R252 verdict](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R252_FINAL_VERDICT.md)
- [R253 verdict](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R253_FINAL_VERDICT.md)
- [R254 verdict](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R254_FINAL_VERDICT.md)
- [R255 verdict](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R255_FINAL_VERDICT.md)
- [R256 verdict](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R256_FINAL_VERDICT.md)
- [R257 machine-readable results](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R257_compression_breakout_results.json)

Jangan berasumsi penyebab kegagalannya sama. Ekstrak bukti per eksperimen untuk membuat taksonomi kegagalan kumulatif setidak memilih jalur strategi berikutnya.

### R189 — GAGAL UNTUK PROMOSI; audit historis dan eksekusi

- [GitHub Actions run OOS 2026](https://github.com/christianomomongan82-lang/scanner/actions/runs/38439056132)
- [Hasil OOS 2026](https://github.com/christianomomongan82-lang/scanner/blob/r189-oos-2026-test/research/r189_oos_2026_results.json)

Pemeriksaan independen EURUSD M1 2026-01-01 sampai 2026-10-12: 55 trade, PF 1,484 setelah biaya tambahan 0,2 pip, net +78,1 pip, mean +1,42 pip/trade, max drawdown 24,8 pip, sekitar 1,35 trade/minggu (~5,9/bulan). Ini terlihat menjanjikan, tetapi ukuran sampel masih kecil dan frekuensinya rendah. Cost stress PF: biaya tambahan 0 pip = 1,571; +0,5 pip = 1,365; +0,8 pip = 1,255; +1 pip = 1,187; +2 pip = 0,900.

Pengaturan terkunci yang diuji: displacement 15 pip, late ratio ≥0,8, body ≥2 pip, directional consistency ≥7 dalam tiap window 11/12 bar, sesi 03:00–11:59 fixed GMT−5 dengan jam 06 dan 09 dikecualikan, dedup 14 bar, ceiling spread entry 1,5 pip, SL 6 pip, TP 18 pip, MFE trigger 6 pip, trailing distance 0, time stop 60 menit. Biaya mencakup BID/ASK aktual +0,2 pip tambahan.

Metrik sejarah R189 yang pernah dikutip (2016–2025: 1.840 trade, PF 1,328; forward 2021–2025: PF 1,358) **tidak direproduksi secara independen** dan tidak boleh digabungkan begitu saja dengan validasi OOS 2026. Jangan menetapkan R189 LULUS setidak reproduksi historis dan audit implementasi selesai.

## 5. Celah yang tidak selesai

- Reproduksi penuh hasil historis R189 masih tidak selesai.
- Komisi broker/funded aktual, slippage live, pemetaan timezone platform, urutan intrabar saat SL/TP tersentuh di candle sama, serta aturan DLL/MLL yang benar-benar berlaku tidak seluruhnya diverifikasi.
- Challenge replay R258 tidak setara dengan engine funded yang sebenarnya.
- Penyimpanan data mentah/periode historis harus memiliki asal-usul, timestamp, sisi BID/ASK, checksum dan versi yang jelas; jangan mengandalkan data yang hanya pernah terunggah di percakapan.

## 6. Langkah berikutnya — status diperbarui 2026-10-15 (lokal, bukan Actions)

### Aturan kerja yang harus diikuti
- **Backtest harus dieksekusi di sesi ChatGPT/container lokal. Jangan dispatch GitHub Actions untuk menghitung backtest.**
- GitHub tetap menjadi sumber input dan penyimpanan riset: ambil dataset/artefak GitHub ke lingkungan lokal, jalankan engine di sini, lalu simpan kode, konfigurasi, hasil, gate, dan putusan ke repo.
- Jangan mengklaim uji lokal atas data H1 sebagai hasil R189 yang memerlukan M1.

### Peta kegagalan R251–R258 selesai
- [Peta kegagalan kumulatif R251–R258](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R251_R258_failure_taxonomy.md)
- Semua delapan jalur berakhir gagal. Pada mayoritas metode, frekuensi bukan masalah inti; expectancy tidak bertahan setelah biaya dan/atau tidak stabil pada forward tahunan. R257 menghasilkan nol trade valid pada periode validasi. Jangan retune konfigurasi lama memakai hasil forward/OOS.

### R260 — backtest lokal shock reversal: GAGAL
- [Preregistrasi R260](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r260-hourly-shock-reversal/research/R260_local_shock_reversal_preregistration.md)
- [Laporan hasil lokal](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r260-hourly-shock-reversal/research/R260_LOCAL_SHOCK_REVERSAL_RESULTS.md)
- [Runner lokal Python](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r260-hourly-shock-reversal/research/r260_local_shock_reversal.py)
- [Hasil JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r260-hourly-shock-reversal/research/R260_local_shock_reversal_results.json)
- Dijalankan di container lokal sesi ini memakai EURUSD H1 BID/ASK dari GitHub Actions artifact 11916174401; 85.170 quote bersama, 582 jam hilang/tidak lengkap tidak diisi, nol spread open negatif. Threshold abs candle body 90th percentile dari 2017–2020 = 12,9 pip; fade candle besar; SL di ekstrem candle, TP 1R, maksimum holding 6 jam.
- 7.961 trade selesai. Forward 2022–2025 menghasilkan PF 0,438 setelah +1 pip, net -8.654,5 pip, 17,41 trade/minggu. Semua tahun forward negatif; bootstrap 4-minggu pada net mingguan memberi CI 95% [-49,24, -34,51] pip/minggu. PF OOS 2026 setelah +1 pip 0,450. **GAGAL—hipotesis ditutup, tidak dituning.**

### R189 — hambatan data tidak terselesaikan
- Laporan historis R189 masih tidak bisa direproduksi: GitHub repo/artefak yang tersedia tidak memiliki arsip EURUSD M1 2016–2025 asli, file spread aslinya, atau ledger historisnya. Artefak EURUSD H1 yang tersedia tidak kompatibel untuk menguji ulang aturan R189 M1.
- OOS 2026 R189 tetap bukti terpisah, bukan pengganti data historis tersebut.
- Jangan jalankan backtest R189 atas H1 atau menyebut data eksternal baru sebagai “data dari GitHub”. Cari artefak/data M1 yang benar-benar tersimpan di GitHub terlebih dahulu. Jika tidak ada, tandai reproduksi sebagai blocked sampai input tersedia.

### Insiden R259 — workflow tak sengaja dibuat dan dijalankan
- Run [38623417685](https://github.com/christianomomongan82-lang/scanner/actions/runs/38623417685) sempat selesai setelah gue keliru mengirim eksperimen ke GitHub Actions. File workflow pemicu sudah dihapus dari branch `r259-r189-dukascopy-history` agar tidak membuat trigger berikutnya.
- Jangan menganggap output R259 sebagai hasil riset resmi; ia tidak mengikuti metode eksekusi yang disepakati (local backtest memakai data dari GitHub). Insiden ini dicatat untuk transparansi, bukan sebagai eksperimen yang diterima.
- Mulai sekarang tidak membuat workflow GitHub Actions untuk backtesting.

### Langkah berikutnya
1. Pertahankan R260 sebagai GAGAL; jangan ubah threshold/SL/TP untuk menyelamatkannya.
2. Cari di GitHub artefak yang benar-benar menyimpan EURUSD M1 historis yang cocok untuk R189; jika tidak tersedia, lanjutkan riset lokal pada hipotesis baru dengan dataset H1 GitHub yang tersedia, preregistrasikan dulu, dan simpan verdict biner.
3. Tetap pisahkan kualitas edge, frekuensi, dan kontrol risiko. Tidak ada strategi final yang lulus dan tidak ada strategi yang terbukti funded-ready.

**Kesimpulan status:** tidak ada strategi final yang lulus. R258 dan R260 GAGAL. Reproduksi historis R189 berstatus GAGAL karena data M1 asli tidak ditemukan; funded-readiness R189 berstatus GAGAL akibat batasan eksekusi. Eksekusi backtest selanjutnya dilakukan di sini; GitHub hanya sumber data/artefak dan penyimpanan.

## Koreksi permanen alur data — 2026-10-15

- Saat data yang dibutuhkan tidak tersedia secara lokal, **cari dan unduh sendiri dari file/artefak GitHub yang sudah ada** setidak meminta apa pun kepada pengguna.
- Dalam workflow backtest proyek ini, GitHub adalah satu-satunya sumber dataset/artefak yang dipakai secara default. **Jangan beralih ke Massive atau API penyedia data lain** tanpa izin eksplisit pengguna.
- GitHub bukan tempat menghitung backtest. Tarik data GitHub ke container/sesi ini dan jalankan perhitungan Python secara lokal di sini. Jangan membuat atau men-dispatch GitHub Actions untuk backtest.
- Jangan menunggu pengguna memerintah langkah pengambilan data yang sudah menjadi bagian normal pekerjaan. Jika data yang dibutuhkan tidak ada di GitHub, laporkan spesifik file/periode apa yang tidak ditemukan dan lanjutkan dengan dataset GitHub yang cocok yang benar-benar tersedia; jangan menggantinya diam-diam dengan timeframe atau feed yang tidak kompatibel.

### R261 — London-window impulse continuation: GAGAL (local run, 2026-10-15)

- [Preregistration and data-eligibility audit](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r261-london-impulse/research/R261_london_impulse_preregistration.md)
- [Final result report](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r261-london-impulse/research/R261_LONDON_IMPULSE_RESULTS.md)
- [Local runner](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r261-london-impulse/research/r261_london_impulse.py)
- [Machine-readable result](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r261-london-impulse/research/R261_london_impulse_results.json)
- [Annual forward table](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r261-london-impulse/research/R261_london_impulse_annual.csv)

Setup: EURUSD H1 London-local 05:00–08:00 impulse continuation, abs impulse threshold 14.5 pips (75th percentile fit on eligible weekdays in 2017–2020), 08:00 entry, stop at 3-bar range extreme, target 1.5R, same-day exit at 16:00 London. Data downloaded from the already-retained GitHub artifact 11916174401 and backtested in the local ChatGPT/container session. A first diagnostic pass that counted flat weekend placeholder quote bars was discarded; the official run excludes London-local weekends and recalculates the locked quantile on Monday–Friday windows. No GitHub Actions backtest was started for R261.

- 612 total trades from 2,552 complete weekday windows, about 1.0–1.3 trades/week depending period.
- Discovery 2017–2020 (262 trades): PF 0.938 and net −229.3 pips after +1 pip extra cost.
- Validation 2021 (59 trades): PF 1.574, net +311.4 pips at +1 pip.
- Forward 2022–2025 (249 trades): PF 0.984, net −59.8 pips at +1 pip.
- OOS 2026 through 13 Oct (42 trades): PF 1.206, net +95.35 pips at +1 pip, but below the minimum 50 OOS trades gate.
- Forward annual at +1 pip: 2022 PF 0.727 / −500.75 pips; 2023 PF 1.245 / +125.8; 2024 PF 1.266 / +92.05; 2025 PF 1.238 / +223.1.
- 4-week circular block bootstrap of 2022–2025 weekly net at +1 pip: probability of positive mean 45.38%; 95% interval for mean weekly net [−5.02, +4.38] pips.
- **Verdict: GAGAL.** Discovery and aggregate forward PF fail required gates, 2022 is deeply negative, OOS has insufficient trades, and bootstrap lower bound is below zero. Do not tune using forward/OOS results.
- This is not an R189 reproduction because input is H1, not required M1. It also does not validate live commissions, slippage, or funded constraints. R189 historical M1 remains blocked until its original M1 history/spread input is actually located in GitHub.

### Correction to data-missing procedure — 2026-10-15

A missing stored file must trigger data acquisition, not an immediate BLOCKED conclusion. If the required series is absent from existing files/artifacts:
1. Reuse the existing proven source/download method (for EURUSD M1, the repo already uses Dukascopy's dukascopy-node with the checked-in dukascopy_fetch_patch.cjs header patch).
2. Run a data-only collection job if direct download from this session is not available. It may fetch raw quotes and package them in a GitHub artifact, but it must not calculate signals, PnL, backtest metrics, or a verdict.
3. Retrieve the data artifact into the local ChatGPT/container session and run Python backtests here.
4. Keep feed provenance explicit. Fresh Dukascopy history is not identical to the missing original HistData M1/spread archive; it allows a separate same-feed historical replay, not a claim that the old HistData figures have been exactly reproduced.
5. Never call a market-data provider's analysis/backtest endpoints. Do not use Massive for this workflow. GitHub stores/serves data and research files; the test engine runs locally.

A data-only EURUSD M1 BID/ASK download for 2016-01-01 through 2025-12-31 has now been added in branch data/eurusd-m1-2016-2025. Run 38697080604 (https://github.com/christianomomongan82-lang/scanner/actions/runs/38697080604) is the acquisition step only—not a backtest. After it finishes, inspect/download its raw data artifact and run the locked local replay.


## Research continuation — R265 audit and R266 result (2026-10-16)

### R265 — USA500/USATECH relative-value mean reversion: FAILED / EXPLORATORY ONLY
- [Retrospective audit](research/R265_EXPLORATORY_AUDIT.md)
- [Machine-readable audit](research/R265_relative_value_audit.json)
- [Runner](research/r265_relative_value.py)
- [Ideal-entry ledger](research/ledgers/R265_trades_ideal.csv.gz)
- [Five-minute delayed ledger](research/ledgers/R265_trades_delay5.csv.gz)
- Forward 2022–2025 contains 41 trades only, below the 100-trade minimum. PF at +4 bps was 1.395 ideal and 1.313 delayed, but four-week block bootstrap 95% intervals crossed zero. No contemporaneous preregistration was found in the repo before audit, and the aggregate output included available data into 2026, so it is not clean OOS evidence. Treat as retrospective exploratory output only; do not tune or promote.

### R266 — U.S. index afternoon continuation after a strong morning: FAILED
- [Preregistration / locked hypothesis](research/R266_INTRADAY_DRIFT_PREREGISTRATION.md)
- [Final report](research/R266_INTRADAY_DRIFT_RESULTS.md)
- [Machine-readable results and gate ledger](research/R266_intraday_drift_results.json)
- [Local Python runner](research/r266_intraday_drift.py)
- [Ideal-entry trade ledger](research/ledgers/R266_trade_ledger_tiny_ideal.csv.gz)
- [Five-minute delayed trade ledger](research/ledgers/R266_trade_ledger_tiny_delay5.csv.gz)
- GitHub source inputs: R205 artifact BID-only M5 snapshots for USA500 and USATECH. Data hashes recorded in result JSON. Calculations executed locally; no backtest GitHub Actions workflow was run. 2026 outcomes were not inspected.
- At +4 bps, ideal discovery 2016–2020 PF 0.934 and net −1,213.5 bps; validation 2021 PF 0.557 and net −1,846.1 bps; forward 2022–2025 PF 1.145 and +2,343.1 bps over 725 trades. The +5-minute entry mode has the same 725 forward trades, PF 1.102 and +1,638.3 bps.
- Both entry modes failed because discovery and validation were negative, years 2023 and 2024 had negative PnL, and the 4-week block-bootstrap 95% weekly-PnL intervals included zero. Do not tune parameters and do not inspect 2026 to rescue the failed hypothesis.

### Status after R266
- **All currently evaluated strategies are GAGAL for funded approval.** R189 historical reproduction is GAGAL because the exact required history inputs are absent; funded-readiness is GAGAL on execution constraints; R260–R266 must not be treated as approved strategy candidates.
- Next experiment must be a structurally different, pre-registered hypothesis; keep the five-minute delay and cost sensitivity in the primary test. Run calculations in local Python, retrieve inputs only from GitHub, do not start GitHub Actions for backtesting, and record a binary verdict. If a pre-registered gate fails, stop that candidate without retuning.


### R267 — Last-hour momentum into next RTH open: EXPLORATORY PILOT FAILED
- [Retrospective pilot report](research/R267_LAST_HOUR_OVERNIGHT_PILOT.md)
- [Machine-readable summary](research/R267_last_hour_overnight_pilot.json)
- [Local replay runner](research/r267_last_hour_to_overnight.py)
- Important research-integrity caveat: this calculation was run before a contemporaneous preregistration was committed to GitHub. It is archived as an exploratory pilot only; do not call it preregistered and do not use it to promote a candidate.
- Rules: at 15:00 ET, follow the 14:00-open to 14:55-close M5 return in USA500/USATECH; enter 15:00 or 15:05 for latency stress; exit at the next complete RTH 09:30 ET open. BID-only inputs; modeled costs +2/+4/+6 bps are assumptions. Entry and exit dates were capped before 2026-01-01, and 2026 outcomes were not inspected.
- At +4 bps, ideal forward 2022–2025: 1,986 trades, PF 0.878, net −7,469.5 bps. Delayed forward: PF 0.857, net −8,762.0 bps. Four-week block-bootstrap 95% intervals for weekly net bps include zero (ideal −80.65 to +8.70; delayed −85.98 to +1.35). Discovery negative; most annual cohorts negative; both indices negative. Exploratory candidate FAILED.
- R267 compact trade ledgers are regenerable via the runner, but the published pilot summary does not include the verbose raw JSON output. The full locally produced JSON is not committed; use the compact summary for its approved interpretation.

### Research process priority after R267
- Do not immediately invent or optimize another signal just to make a new round number. A large family of prior range breakouts, reversals, momentum and relative-value ideas have already failed; repeated similar experiments add selection bias.
- Recommended next work item is an execution/reproducibility audit of existing R189 historical replay and signal/exit mechanics, plus explicit separation of verified facts versus feed-specific replication. It must not be described as a fresh preregistered performance test. No candidate is approved or funded-ready.


### R189/L80 — execution-delay audit (2026-10-16)
- [Execution-delay audit report](research/R189_EXECUTION_DELAY_AUDIT.md)
- [Machine-readable delay summary](research/R189_execution_delay_audit.json)
- This is a retrospective audit of an already-run Dukascopy M1 BID/ASK replay, not an exact reproduction of the original HistData results and not a fresh preregistered strategy test.
- Intrabar-aware stress results, forward 2021–2025: at +0.5 pip additional cost, PF declines from 1.284 at ideal fill to 1.071 after +5 minutes; at +1.0 pip, PF declines from 1.114 to 0.926 and net becomes −203 pips. The +5-minute bootstrap intervals include zero at both costs. This matters for phone/email execution latency.
- The delay-stress ledger checks spread at the actual delayed entry bar; M1 candles model gaps through stops/targets and stop-before-target ordering but cannot verify tick-level closing duration.
- R189 berstatus GAGAL untuk funded-readiness: pemetaan GMT-5 ke server/DST, biaya live, Quick Strike sub-30-detik, serta DLL/MLL tidak memenuhi gate bukti.
- No retuning or parameter selection from this audit. Keep R189 rules locked while verifying mapping and execution constraints.


### FundedNext eligibility and rule audit (official pages checked 2026-10-16)
- [Current Stellar 2-Step rule audit](research/FUNDEDNEXT_STELLAR2_RULE_AUDIT_20261016.md)
- Official page currently lists $6,000 Stellar 2-Step at approximately $59.99, targets 8% then 5%, DLL 5%, MLL 10%, five trading days per phase by default, and no phase time limit. A “No Minimum Trading Days” add-on is listed for $6k/$15k/$25k, but its cost must be checked at checkout; do not assume it is cheaper without the final price.
- Critical eligibility constraint: FundedNext's official age FAQ requires age 18+. Based on the registered birth date (2008-12-25), purchase/KYC must wait until 2026-12-25. Until then, research only.
- Official inactivity policy changed/clarified to **30 consecutive calendar days without a trade**, not 60.
- Quick Strike is not the share of trades; it is the share of total recorded profit generated by profitable trades closed within 30 seconds. 20% warning; 30% or above pauses challenge progression until the ratio drops below 30%.
- FundedNext official help center specifies seasonal server time GMT+2 / GMT+3. Actual login/platform mapping still has to be verified.
- R189 remains NOT FUNDED-READY because the +5-minute stress results weaken sharply and still lack live cost distribution, actual platform timezone/DST mapping and Quick Strike / DLL / MLL validation.


## 7. Putusan biner dan compounding — instruksi permanen 2026-10-16

- Status hasil hanya **LULUS** atau **GAGAL**. Tidak ada kategori pending, status nonbiner, atau kandidat yang dibiarkan tanpa putusan. Bila suatu klaim gagal karena data/implementasi/bukti tidak tersedia, percobaan untuk klaim itu dicatat GAGAL dengan alasan spesifik.
- [Kebijakan riset biner, portofolio modular, dan compounding](research/RESEARCH_POLICY_BINARY_COMPOUNDING.md).
- Jangan terus berburu satu strategi tunggal. Riset harus mencakup strategi modular, portfolio replay, korelasi/overlap, shared risk controller dan compounding fractional-risk berdasarkan ekuitas terbaru. Namun, menggabungkan strategi gagal tidak otomatis menciptakan edge; hasil komposit wajib diuji sebagai satu sistem.
- Compounding dan challenge replay harus menunjukkan trade R, equity curve dalam dolar, daily/max loss, serta peringatan bahwa closed-equity saja tidak menangkap floating DD. Risiko per entry dan cap portfolio dikunci sebelum kalkulasi.
- **R268 — GAGAL:** [preregistration](research/R268_COMPOUND_PORTFOLIO_PREREGISTRATION.md) · [report](research/R268_COMPOUND_PORTFOLIO_RESULTS.md) · [JSON](research/R268_compound_portfolio_results.json) · [runner](research/r268_compound_portfolio.py).
- R268 menggabungkan R262 EURUSD dan R263 indeks memakai ledger delay 5 menit, biaya tambahan +1 pip FX dan +4 bps indeks, risiko 0,25% ekuitas per trade, batas open risk 1%. Forward 2022–2025: 2.399 trade, PF net R 0,823, equity referensi $6.000 menjadi $3.374,61 (−43,76%), closed-equity DD 44,60%. Batas MLL nominal $5.400 pertama kali dilewati di 2023-05-26 04:06 UTC; simulasi akan gagal pada titik itu. Ini diagnostik retrospektif, bukan estimasi peluang lulus funded.
- R268 membuktikan bahwa gabungan dua modul ini **GAGAL**; jangan retune komponen lama untuk menyelamatkannya. Untuk kandidat baru, praregistrasikan aturan dan gate, lalu uji komposit serta compounding lokal. Hasil yang tidak memenuhi satu gate pun = GAGAL.


- **R268 reproducibility status: GAGAL.** The local combined calculation used R262/R263 delayed trade-ledger CSVs that are not present as repository files; result JSON, report, and runner are saved, but this exact run is not self-contained from GitHub alone. Its local input hashes are documented in the report/JSON. Do not claim otherwise.


## R269 — London Asian-range sweep/reclaim reversal — GAGAL (2026-10-16)

- [Preregistration](research/R269_LONDON_ASIAN_SWEEP_PREREGISTRATION.md)
- [Runner](research/r269_london_asian_sweep.py)
- [Results report](research/R269_LONDON_ASIAN_SWEEP_RESULTS.md)
- [Machine-readable compact results](research/R269_results_compact.json)
- Raw-data collection only: [GitHub run 38697080604](https://github.com/christianomomongan82-lang/scanner/actions/runs/38697080604), artifact ID 11959096102. All signal/PnL calculations were run in local Python, not Actions.
- Data: Dukascopy EURUSD M1 BID/ASK 2016–2025, 4,415,493 rows per side, identical common timestamps, zero duplicates/invalid OHLC/negative open spreads. ZIP SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- Locked strategy: London-local Asian range 00:00–07:59, sweep/reclaim signal 08:00–11:59; only first setup per day; entry six minutes after signal-bar timestamp (five minutes after close/decision); ASK long/BID short; SL past signal extreme by 1 pip, target Asian midpoint, minimum 1R reward/risk; 240-minute time stop; stop-first intrabar ambiguity; +1 pip primary extra-cost stress.
- Discovery 2016–2020: 340 trades, PF 0.758, −73.48R at +1 pip. Validation 2021: 49 trades, PF 0.632, −19.31R. Forward 2022–2025: 242 trades, PF 0.657, −78.91R. Forward bootstrap 95% interval for mean weekly net R: [−0.661, −0.078]. Compounding 0.25% risk from $6,000 ended at $4,912.24; closed equity first crossed $5,400 on 2024-09-13 09:27 UTC.
- All seven economic gates failed. Do not retune this candidate on the same data. This is an independent Dukascopy feed replay, not an exact reproduction of the missing original HistData R189 archive. The closed-equity replay does not establish funded readiness.
- Reproducibility note: the detailed trade ledger and annual tables are currently available in the local run output but the repository contains the runner, JSON summary, report and raw-data artifact reference; do not claim the row-level R269 ledger is stored in GitHub until a corresponding ledger file is committed.
- R269 is closed. Choose any later candidate using a structurally independent hypothesis and a preregistration before results; no R269 parameter rescue.


## Family-level research review — R260–R269

- [Failure taxonomy and next-stage decision](research/R260_R269_FAILURE_TAXONOMY.md).
- R260–R269 contained no candidate that passed the full gates. High trade count did not repair negative expectancy; retrospective/forward-only PF must not be promoted if discovery, validation, bootstrap or annual stability fails.
- The 2022–2025 period has been repeatedly inspected across candidate families and should not be called an untouched final holdout. New candidates need an explicit economic rationale, a horizon compatible with five-minute latency, and a genuinely independent/untouched validation window for promotion.
- Do not produce near-duplicate M1 reversal, intraday momentum, US cash-open ORB, or H4 pullback tests by changing thresholds. Any failed locked candidate remains GAGAL and closed.


## Critical correction — intended compounding objective (2026-10-16)

The user's “compound compound” instruction was not satisfied by increasing position size with equity alone. **First priority is strategy/edge composition that improves the risk-normalized PF and net expectancy of the integrated trade stream.** Capital compounding is downstream, after that integrated stream qualifies.

- [Full correction and required workflow](research/COMPOUNDING_OBJECTIVE_CORRECTION_20261016.md).
- [Updated binary/compounding policy](research/RESEARCH_POLICY_BINARY_COMPOUNDING.md).
- R268 merely unioned previously failed streams and applied fixed-fractional equity sizing; it was a negative portfolio diagnostic, not a successful strategy-compounding build.
- R269 was another standalone strategy test and therefore also failed to implement the requested research priority, independent of its own economic GAGAL result.
- Future candidates must compare integrated signal logic against each component and a no-filter baseline on identical timestamps/costs; show PF/expectancy lift without destroying useful frequency or robustness. Fixed-fractional sizing comes after this.
- 2022–2025 is repeatedly inspected and cannot be treated as an untouched final holdout. Do not tune old failed candidates to rescue them.


## Latest authoritative objective — funded target completion (2026-10-16)

**The project's objective is to reach the actual funded-challenge targets as quickly as realistically possible while controlling the probability of daily/max-loss breach. PF is a diagnostic only, not the objective.** This supersedes earlier wording that made PF >=1.10 or PF improvement a primary target.

- [Authoritative objective, simulator requirements, and scorecard](research/PRIMARY_OBJECTIVE_FUNDED_TARGET_COMPLETION_20261016.md).
- [Corrected binary/compounding policy](research/RESEARCH_POLICY_BINARY_COMPOUNDING.md).
- The current reference challenge is the $6k Stellar 2-Step model: +8% Phase 1 then +5% Phase 2, with applicable loss limits and provider rules. Research remains simulation-only until age eligibility.
- “Compound” means assembling and coordinating multiple compatible opportunities/contexts/strategy streams so the combined system can reach targets with a stronger probability/time profile; it does not mean merely raising lot size with equity or blindly unioning failing strategies.
- Primary scorecard: probability of hitting each phase target before loss-rule breach, probability of completing both phases, median/upper-quantile time to target, risk/breach probability, opportunity frequency under 5-minute execution delay, cost robustness and inter-module overlap/correlation.
- PF, expectancy, win rate, frequency and drawdown remain diagnostics that explain why a portfolio succeeds/fails. Do not select the system solely for highest PF. Do not promote a high-risk lottery on the basis of occasional target hits; quantify repeated-path success and breach distributions.
- Fixed-fractional capital compounding is part of the challenge path simulation after the integrated opportunity stream is defined; it is not the project's end goal.



## R270 — Asia-session regime router — GAGAL (2026-10-16)

- [Preregistration](research/R270_SESSION_REGIME_ROUTER_PREREGISTRATION.md) · [results report](research/R270_SESSION_REGIME_ROUTER_RESULTS.md) · [compact JSON](research/R270_results_compact.json).
- Input: EURUSD M1 BID/ASK Dukascopy raw-only GitHub artifact 11959096102 (data-only run 38697080604), ZIP SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`; local Python calculations, no backtest Actions run.
- Locked router: Module A continuation only if Asia ER >=0.30 plus close-in-edge direction; Module B fade in low-ER balanced sessions; five-minute entry delay; BID/ASK execution; +1 pip primary cost.
- Diagnostic: across 2,605 eligible London weekdays, maximum observed ER was 0.2101, so Module A never fired. Module B produced 577 trades; router is exactly identical to B, not a true combined stream.
- At +1 additional pip, B/router: discovery 2016–2020 290 trades, PF 0.712, -65.97R; 2021 68 trades, PF 0.639, -20.16R; forward 2022–2025 219 trades, PF 0.628, -63.50R. All four forward years were negative. Four-week bootstrap average net was -0.304R/week, 95% CI [-0.484, -0.115]. Even with 0 added pips beyond observed quotes, discovery/validation/forward net R was -14.14/-5.96/-30.99.
- Challenge reference proxy, not funded-equivalent: router both-phase completion was 0% at 0.25–0.50% risk, 0.4% at 0.75%, and 1.1% at 1.00%, while proxy loss-rule breach rose from 28.1% to 97.9%. Higher risk is not a credible rescue.
- **Verdict: GAGAL.** The economic/coverage gates failed; 2022–2025 is not independent, 2026 is absent, and official funded implementation/rules remain unverified. Do not retune R270. At checkpoint time, full runner and row-level ledger are preserved locally but have not yet been committed to this branch; do not claim full GitHub-only reproducibility until those files are stored.


## R271 — Daily 20-session breakout continuation — GAGAL (2026-10-16)

- Pre-registration: [R271_DAILY_TREND_BREAKOUT_PREREGISTRATION.md](research/R271_DAILY_TREND_BREAKOUT_PREREGISTRATION.md)
- Results report: [R271_DAILY_TREND_BREAKOUT_RESULTS.md](research/R271_DAILY_TREND_BREAKOUT_RESULTS.md)
- Exact local runner: [r271_daily_trend_breakout.py](research/r271_daily_trend_breakout.py)
- Compact metrics: [R271_results_compact.json](research/R271_results_compact.json)
- Timestamped compact trade ledger (all 126 closed trades): [R271_trade_ledger_compact.csv](research/R271_trade_ledger_compact.csv)
- Source: Dukascopy EURUSD M1 BID/ASK from data-only GitHub artifact 11959096102 / run 38697080604; ZIP SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. Local Python only; no GitHub Actions backtest ran.
- Locked setup: New York-close FX sessions; close strictly beyond prior 20 completed session high/low; exact delayed entry 17:05 NY; stop 2× prior ATR20; target 2R; max hold through the close of the tenth subsequent valid session; side-correct BID/ASK; +1 pip primary incremental cost and 0/0.5/2 pip sensitivity.
- Data audit: 4,415,493 common BID/ASK minute timestamps, no duplicates or negative open spreads; calendar filter retained 3,749,493 minute rows; median observed open spread ~0.30 pip, p95 ~0.80 pip. 320 raw breakout signals, 266 had a valid exact entry quote, 126 closed trades after position-overlap rules.
- At +1 pip: discovery 2016–2020 = 57 trades, PF 0.811, −4.949R; validation 2021 = 14 trades, PF 0.769, −1.437R; diagnostic forward 2022–2025 = 55 trades, PF 0.808, −4.265R. Annual 2022/2023/2024/2025 net R = −2.798 / −1.642 / +2.276 / −2.101. Forward four-week bootstrap: mean −0.0204R/week, 95% CI [−0.0722, +0.0324], 22.06% positive bootstrap means.
- Cost stress was negative even at +0 pip extra cost (forward −3.892R) and remained −4.638R at +2 pips. Six preregistered gates failed. Challenge replay was not run because the locked spec allowed it only for a net-positive stream. **R271 = GAGAL; no retuning.**
- The 2022–2025 period is contaminated, and 2026+ was not in this input archive, so no claim of independent promotion-grade evidence is possible even apart from the failed measured gates.


## Funded-readiness correction — official rules verified (2026-10-16)

- [Official rule matrix and remaining implementation checks](research/FUNDEDNEXT_STELLAR2_RULES_VERIFIED_20261016.md)
- [Funded-ready promotion gate](research/FUNDED_READINESS_GATE_20261016.md)

Current public FundedNext CFD Stellar 2-Step documentation verifies: Phase 1 +8%, Phase 2 +5%; 5% daily loss with daily reset at 00:00 server time and realized-today + floating P&L counted (including commissions/swaps/fees); 10% static maximum loss; at least five distinct trading days per phase; no time limit; Quick Strike must be below 30% and measures profit from profitable trades closed in under 30 seconds. Server clock is seasonally GMT+2/GMT+3. The official help center currently requires traders to be at least 18 to open a trading account. Full sources and detailed mechanics are in the linked rule matrix.

**Important correction:** historical challenge proxy metrics are not live-pass odds. Before any strategy can become LULUS for funded readiness, replay the exact phase sequence with intratrade equity, floating loss, costs, server-time reset and Quick Strike. R270/R271 stay GAGAL and must not be retuned. The 2022–2025 window is not an untouched promotion holdout. Until the user reaches age eligibility, all tests remain simulation-only.



## Authoritative clarification — “compounding” means evolutionary method search (2026-10-16)

- The user’s intended compounding is **evolution of the method-search process**: each experiment inherits and reuses evidence-backed building blocks and lessons from prior experiments, then creates a better next generation through justified mutations, crossover, ablations, and component composition. It is not merely position-size compounding, blind union of failed strategies, or a sequence of unrelated standalone tests.
- Read and follow [EVOLUTIONARY_METHOD_COMPOUNDING_20261016.md](research/EVOLUTIONARY_METHOD_COMPOUNDING_20261016.md) as the authoritative workflow. Decompose experiments into context/setup/entry/exit/execution/risk components; preserve failure diagnoses; retain potentially useful blocks only when controlled component/ablation comparisons support them; record parent IDs and child-generation rationale.
- Optimize the actual target: probability of completing both funded phases and time-to-target before rule breach. Use a risk-aware diverse/Pareto population; PF and expectancy are diagnostics. Keep frozen independent OOS protection because repeated evolutionary search on the same validation period overfits.
- Honest correction: R272 is one locked dual-module combination test, not yet a full evolutionary-search implementation. Complete the valid locked run without opening its 2026 holdout prematurely; afterward use the candidate/block registry and evidence matrix to generate the next research generation instead of returning to isolated strategy invention.

## R272 — Gold dual-module test / corrected data acquisition (2026-10-16)

**Strategy verdict: GAGAL (locked historical screen, 2026-10-16 local replay).** See `research/R272_FINAL_VERDICT.md` and `research/R272_results_compact.json` on `local-backtest/r189-dukascopy-history`. The 2026 holdout remains unopened.

- Locked hypothesis: XAUUSD M5; 12-hour trend-pullback continuation (A) in persistent regimes and failed-excursion reversal (B) in balanced regimes, five-minute manual execution delay after the signal bar closes, executable BID/ASK fills, force-flat at 16:45 New York, primary incremental cost +$0.30/oz; sensitivity +$0.00/+0.10/+0.50.
- Preregistration plus pre-result timing clarification: [R272 locked hypothesis](research/R272_XAUUSD_DUAL_MODULE_PREREGISTRATION.md).
- Local-only runner: [r272_xauusd_dual_module.py](research/r272_xauusd_dual_module.py) · [reproducible engine/provenance smoke tests](research/test_r272_xauusd_dual_module.py).
- **Runner corrections made before results:** timestamp is bar-open, so signal close is T+5m and another 5-minute manual delay requires entry at T+10m (index t+2), not T+5m. Runner enforces two exact five-minute intervals, records realized latency, handles the exact 16:45 executable opening quote without reading post-cutoff high/low, and emits a stable schema for zero-trade months.
- Local syntax, synthetic fill/latency tests and provenance-loader tests PASS. Synthetic cases verify T+10m entry = five minutes after the signal close; normal target, cutoff target gap, cutoff adverse stop gap; rejection of a broken intervening bar; acceptance of manifest with flats disabled and rejection of a manifest that permits flats. These are engine tests only, not strategy performance evidence.
- Data-quality issue found before the backtest: the January downloader probe [run 38857759446](https://github.com/christianomomongan82-lang/scanner/actions/runs/38857759446) reported “Include flats: true”. That probe and the original full acquisition [run 38857936371](https://github.com/christianomomongan82-lang/scanner/actions/runs/38857936371) are **not valid inputs** for R272’s no-synthetic-bars rule.
- Corrected acquisition code now omits the -fl flag, records include_synthetic_flat_bars=false in the manifest, and has a distinct concurrency group: [data-only collector](https://github.com/christianomomongan82-lang/scanner/blob/data/r272-xauusd-m5-2016-2026/research/download_xauusd_m5_2016_2026.py), [workflow](https://github.com/christianomomongan82-lang/scanner/blob/data/r272-xauusd-m5-2016-2026/.github/workflows/r272-xauusd-data-only-v2.yml). Its corrected raw-only collection [run 38859918137](https://github.com/christianomomongan82-lang/scanner/actions/runs/38859918137) completed and published artifact `12031270051` (`XAUUSD-M5-Dukascopy-BID-ASK-2016-2026`). Manifest confirms synthetic flats disabled; 947,326 rows per BID/ASK, 947,326 exact matching timestamps, hashes and 572 real gaps are recorded in the R272 verdict. No strategy calculations ran in Actions. The data job does not calculate signals, PnL, or verdicts.
- Runner refuses to load data unless manifest proves the correct source/instrument/timeframe/window, synthetic flats disabled, and both gzip hashes/row counts match the actual inputs.
- After valid raw BID/ASK is available, calculate and store 2016–2020 discovery and 2021–2025 historical validation first. Do not inspect 2026-01-01 through 2026-10-15 unless every locked historical gate passes. Funded readiness remains a separate rule-aware, equity-aware two-phase replay: a signal-screen pass alone is not enough.


## Latest research update — R272 GAGAL (2026-10-16 local)

- [Locked verdict report](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R272_FINAL_VERDICT.md) · [compact JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R272_results_compact.json) · [locked runner](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/r272_xauusd_dual_module.py).
- Corrected raw input artifact `12031270051`, data-only run `38859918137`; Dukascopy XAUUSD M5 BID/ASK. 947,326 paired timestamps; synthetic flat bars disabled; 572 gaps retained; median opening spread $0.358/oz, p95 $1.117/oz. Local signal/PnL calculations excluded all timestamps from 2026-01-01 onward.
- At +$0.30/oz: router/B made 944 discovery trades with -437.47R (PF 0.525) and 957 validation trades with -401.22R (PF 0.548). Even at $0 extra cost, discovery/validation were -174.83R/-227.38R. Four-week weekly-net-R bootstrap 95% CIs are [-2.081, -1.256] and [-1.951, -1.115] respectively.
- Module A fired 972 raw triggers, but none met the locked ER >= 0.45 gate; maximum trigger ER was 0.3249, so A produced zero trades. Module B's balanced failed-excursion fade was negative before incremental cost. Router outperformed raw union only relatively (-401.22R vs -439.37R in validation); both lose, and only one of six historical gates passed.
- **R272 = GAGAL.** Do not open 2026, tune R272, or run a funded replay. A future generation may inherit only the diagnostic and executable-side/delay/missing-bar controls, not claim that either signal block has demonstrated positive edge. The full local ledgers were generated locally but are not uploaded as row-level CSVs; this checkpoint links the stored compact result/report and the in-repo locked runner.

Continuation instruction: read the latest R270–R274 results and `research/EVOLUTIONARY_BLOCK_REGISTRY_20261016.md` plus `research/EVIDENCE_MATRIX_20261016.json` first. Do not open 2026 XAUUSD holdout (it remains untouched). Next search should broaden instrument/hypothesis-family coverage and use locked discovery gates and controlled ablations, not threshold-tune the failed XAUUSD M5 continuation or impulse setups. No R275 hypothesis has yet been registered.

## Latest research update — R274 GAGAL (2026-10-16 local replay)

**Latest verdict: R272 GAGAL, R273 GAGAL, R274 GAGAL. No candidate is currently eligible for funded challenge replay.**

### R272 — XAUUSD M5 dual-module router
- [Verdict](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R272_FINAL_VERDICT.md) · [compact results JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R272_results_compact.json) · [pre-registration](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R272_XAUUSD_DUAL_MODULE_PREREGISTRATION.md).
- At +$0.30/oz, router/B had 944 discovery trades / -437.47R / PF 0.525 and 957 validation trades / -401.22R / PF 0.548. Module A had zero trades because none of its 972 raw triggers met ER >= 0.45. The failed-excursion fade lost even with zero incremental cost.

### R273 — XAUUSD M5 aligned pullback continuation
- [Pre-registration](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R273_ALIGNED_PULLBACK_CONTINUATION_PREREGISTRATION.md) · [verdict](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R273_FINAL_REPORT.md) · [compact JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R273_results_compact.json) · [runner](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/r273_aligned_pullback_continuation.py).
- At +$0.30/oz, child had 131 discovery trades / -78.12R and 278 validation trades / -128.86R. It improved relative to raw-A ablation by 28.68R in validation and retained 84.0% of trades, but bootstrap intervals were wholly negative; not an edge.

### R274 — XAUUSD M5 impulse follow-through
- [Pre-registration](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R274_XAUUSD_M5_IMPULSE_FOLLOWTHROUGH_PREREGISTRATION.md) · [verdict](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R274_FINAL_REPORT.md) · [compact JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R274_results_compact.json) · [runner](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/r274_xauusd_m5_impulse_followthrough.py).
- At +$0.30/oz, 974 discovery trades / -655.94R / PF 0.324 and 997 validation trades / -430.65R / PF 0.483. It was negative even at zero incremental cost; all five validation years were negative. Holdout 2026 was not opened.

### Evolutionary memory to use next
- [Block registry](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/EVOLUTIONARY_BLOCK_REGISTRY_20261016.md) and [machine-readable evidence matrix](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/EVIDENCE_MATRIX_20261016.json).
- Corrected raw-only artifact `12031270051` (data acquisition run `38859918137`) has 947,326 paired XAUUSD M5 BID/ASK rows; synthetic flats disabled; 572 >5m gaps kept. Local calculations used 877,930 quote rows through 2025 only. 2026 remains unopened.
- Data/entry/exit integrity controls are reusable implementation blocks, not alpha. No R270–R274 signal block is established as a positive edge. Row-level ledgers were generated locally but not uploaded; reports/compact JSON and the R273/R274 runners are stored in the research branch.
- **Next step:** broader instrument and hypothesis-family coverage with preregistered discovery filters and component ablations. Do not revive the failed signal blocks by lowering thresholds. Do not register R275 until its hypothesis is materially distinct and preregistered.

## Latest research update — R275 mobile-delay stress — GAGAL (2026-10-17)

- Pre-registration: [R275 locked hypothesis](research/R275_R189_L80_MOBILE_DELAY_PREREGISTRATION.md)
- Result: [R275 final report](research/R275_FINAL_REPORT.md) · [compact metrics and gate verdict](research/R275_results_compact.json) · [standalone runner](research/r275_r189_l80_mobile_delay.py). Local detailed parent/child ledgers were generated at calculation time; full row-level CSV ledgers are not yet archived in GitHub.
- Parent: locked R189/L80 using exact T+1 minute execution after M1 signal-bar open. Child: unchanged signal logic with exact T+6 minute entry to model wait-for-close plus five-minute manual phone delay. No parameter tuning.
- Input: Dukascopy EURUSD M1 BID/ASK data artifact 11959096102, archive SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. The archive was collected with `-fl`; 696,795 paired flat-candidate rows (15.78%) were conservatively filtered when both BID/ASK candles copied prior closes at the exact next minute. 3,718,698 rows remain. This heuristic is a data limitation, not formal proof all synthetic bars were removed.
- At +1 pip additional cost, exploratory 2022–2025: parent 699 trades / PF 0.839 / -378.5 pips / 440.0-pip max DD; child 701 / PF 0.694 / -786.3 pips / 816.9-pip max DD. At +2 pips the child PF was 0.496 and net -1,487.3 pips. The child’s four-week circular weekly-net-pips bootstrap (10,000 reps, seed 2752026) was -3.762 pips/week, CI95 [-5.252, -2.398], wholly negative.
- Locked gates: sample-size gate passed; PF at +1/+2 pips, annual robustness and bootstrap gates all failed. **R275 = GAGAL; no challenge replay and no tuning.** 2022–2025 is contaminated and remains exploratory, not a pristine holdout. R275 did not use EURUSD 2026; reserved XAUUSD 2026 remains unopened.
- Evolutionary lesson: the L80 signal does not survive the tested additional phone-entry delay and cost assumptions. Do not blend this failed stream with the failed R272–R274 gold signals. The next generation must broaden structural hypothesis/instrument coverage rather than parameter-rescue this child.

## Latest research update — R276–R279 US cash-open breadth family (2026-10-17)

- Preregistered hypotheses: [R276 two-sided breadth router](research/R276_US_CASH_OPEN_BREADTH_ROUTER_PREREGISTRATION.md), [R277 same-day flat](research/R277_US_CASH_OPEN_BREADTH_INTRADAY_FLAT_PREREGISTRATION.md), [R278 long-only child](research/R278_LONG_ONLY_US_CASH_OPEN_BREADTH_PREREGISTRATION.md), [R279 no-fixed-TP ablation](research/R279_LONG_ONLY_BREADTH_INTRADAY_NO_TP_PREREGISTRATION.md).
- [Combined batch report](research/R276_R279_EVOLUTIONARY_BATCH_RESULTS.md), plus per-round [R276 report](research/R276_FINAL_REPORT.md) / [R276 JSON](research/R276_results_compact.json), [R277 report](research/R277_FINAL_REPORT.md) / [R277 JSON](research/R277_results_compact.json), [R278 report](research/R278_FINAL_REPORT.md) / [R278 JSON](research/R278_results_compact.json), [R279 report](research/R279_FINAL_REPORT.md) / [R279 JSON](research/R279_results_compact.json).
- Shared input artifacts: USA500 11709864394, USATECH 11710370389, USA30 11710730507, USSC2000 11710111254; Dukascopy M5 BID OHLC. USSC2000 history starts 2018-08-08; synchronized child events were restricted to timestamps covered by all four sources. Cost stresses are modeled 1/2 price bps round-trip, not verified actual costs.
- **R276:** all locked historical statistical gates passed (767 discovery closes PF@+2bp 1.138; 828 exploratory 2022–2025 closes PF@+1/+2bp 1.289/1.257; bootstrap 95% CI [0.166, 1.269] R/week), but diagnostic 2026 PF@+1bp was 0.748 / −19.38R. Forward total R (+147.06) was below matched parent (+176.09), and holds were too long (median 17.83h, p95 124.63h, max about 60 days). No full account-path replay or swap verification. **Screen pass only; not promoted.**
- **R277:** GAGAL; discovery PF@+2bp 0.989; 2024 PF@+1bp 0.794; four-week bootstrap 95% CI [−0.116, 0.793] R/week.
- **R278:** GAGAL; discovery PF@+2bp 0.889 despite forward PF@+1/+2bp 1.403/1.346; diagnostic 2026 PF@+1bp 0.877.
- **R279:** GAGAL; discovery PF@+2bp 0.873. Removing the fixed target was worse than the R278 child (forward net +67.80R vs +69.10R, PF 1.395 vs 1.403, max DD 17.99R vs 17.26R).
- Overall: no candidate from R276–R279 is funded-ready; 2022–2025 is contaminated and 2026 is only diagnostic. No rule-aware two-phase challenge replay was run, and actual bid/ask, commissions, overnight swaps, contract multipliers, floating daily loss and Quick Strike remain unverified.
- Reproducibility gap: reports and compact JSONs are stored in GitHub, but the full R276–R279 local runners and row-level ledgers are not yet committed there. Do not claim complete repository-only reproduction until archived.
- Next action: reject R277–R279 and do not keep changing this same cash-open family. Any new generation must use a genuinely different hypothesis, preregister it before outcomes, compare matched parent/ablation, and optimize actual target-completion/breach profile rather than PF alone.

## Latest research update — R280 Nasdaq-led follower breakout — GAGAL (2026-10-17)

- Pre-registration: [R280 Nasdaq-led cash-open follower breakout](research/R280_NASDAQ_LED_CASH_OPEN_FOLLOWTHROUGH_PREREGISTRATION.md)
- Results: [R280 final report](research/R280_FINAL_REPORT.md) · [compact metrics and locked gate verdict](research/R280_results_compact.json).
- Hypothesis: USATECH/Nasdaq 100's first cash-open opening-range breakout leads; take a same-direction first breakout on USA500, USA30 or USSC2000 only if the follower signal is 5–30 minutes later. Exact T+10 entry; OR-edge stop; 2R target; mandatory flat at exact 16:00 New York bar open. Matched parent consists of all first OR breakouts from those three follower indices under identical execution and costs.
- Child signal set: 1,084 eligible follower signals out of 7,502 first-breakout follower signals; 426 closed trades in exploratory forward 2022–2025. At +1 bp, child forward PF 1.169 / +27.89R vs matched parent PF 1.090 / +108.76R; the filter increased mean net R/trade (0.0655R vs 0.0363R) but sacrificed total net R and trade count. At +2 bp child PF 1.109.
- **R280 = GAGAL:** discovery PF@+2 bp 0.875; annual 2023/2024 PF@+1 bp 0.977/0.787; four-week bootstrap 95% CI for forward weekly net R [−0.116, +0.381]; diagnostic 2026 PF@+1 bp 0.744. Do not tune the lag window after these results.
- Inputs are the cached R205 BID-only M5 snapshots for USA500 artifact 11709864394, USATECH 11710370389, USA30 11710730507 and USSC2000 11710111254. Costs are modeled 1/2 bps and do not represent verified FundedNext instrument costs. 2022–2025 is contaminated; 2026 is only diagnostic. No full funded equity-path replay.
- Overall R276–R280: no candidate promoted. R276 passed the historical screen only but has a negative diagnostic and missing funded-path/swap checks; R277–R280 failed pre-registered gates. Reusable controls are execution/data integrity, not signal edge.
- Reproducibility gap remains: R276–R280 reports and compact JSON summaries are stored in GitHub, but all full local runners and row-level trade ledgers are not yet stored there. Do not describe GitHub-only reproduction as complete until these are archived.
- Next search should not keep mutating this US cash-open breakout family. Register a structurally distinct mechanism before calculation and score it against fixed target-completion and breach objectives. Keep all 2026 slices diagnostic only.



## Latest research update — R281 EURUSD H1 compression-release — GAGAL (2026-10-17)

- Preregistration: [R281 design](research/R281_EURUSD_H1_COMPRESSION_RELEASE_PREREGISTRATION.md)
- Runner: [R281 local Python runner](research/r281_eurusd_h1_compression_release.py)
- Results: [R281 final report](research/R281_FINAL_REPORT.md) · [compact JSON](research/R281_results_compact.json) · [grid summary](research/R281_grid_summary.csv)
- Purpose: correct R257's zero-trade eligibility/coverage problem, without changing the original fixed grid. H1 BID/ASK candles were constructed from Dukascopy M1; this is not claimed as a byte-identical reproduction of R257's former H1 file.
- Input: GitHub data-only artifact 11959096102; archive SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. Raw archive collector used `-fl`; paired flat-row removal is heuristic. 57,191 complete H1 bars; no missing bars were filled. Fit thresholds from 2017-2020 were 20.8 pips (Q20) and 25.0 pips (Q30).
- At +1 additional pip, all eight discovery configurations lost: PF 0.575-0.667, 88-392 trades, net -336.6 to -1,622.5 pips. Best 2021 validation sample count was 10, below the required 50. Q20/B12 produced 4 validation trades and PF 2.065 but its discovery PF was 0.575-0.615, so it fails and must not be revived.
- **Verdict: GAGAL.** No candidate selected. To honor the stage gate, 2022-2025 outcomes were not calculated or inspected; XAUUSD M5 2026 holdout remains unopened. No challenge replay was run.
- Repository artifacts now include preregistration, runner source, report, compact results, and grid summary. Row-level trade ledgers remain local and should be archived before claiming full repository-only reproduction. No Actions backtest workflow was launched.
- Decision: close this fixed compression-release specification; no signal component retained. Next search must move to another mechanism, not loosen these thresholds.


## Latest research update — R282 EURUSD weekend-reopening gap fade — GAGAL / DATA COVERAGE (2026-10-17)

- Preregistration: [R282 design](research/R282_EURUSD_WEEKEND_GAP_FADE_PREREGISTRATION.md)
- Local runner: [R282 replay source](research/r282_eurusd_weekend_gap_fade.py)
- Results: [R282 report](research/R282_FINAL_REPORT.md) · [JSON](research/R282_results.json) · [event coverage audit](research/R282_event_coverage_audit.csv)
- Data source: Dukascopy EURUSD M1 BID/ASK artifact 11959096102, SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. The source collector used `-fl`; 696,795 paired flat candidates were removed heuristically after alignment/valid-OHLC screening.
- The event detector saw 4 timestamp gaps ≥36 hours in the full 2016–2025 file; 3 met the locked Friday-to-Sunday/Monday condition. All 3 were timestamps at 00:00 UTC (2018-01-01, 2020-12-27, 2024-01-01) and each lacked exact T+10 timestamp; next observed quote arrived much later. None is a valid executable weekly reopening under the preregistered rules.
- **Verdict: GAGAL — data/event coverage; alpha untested.** Zero trades, no reportable PF. 2022–2025 outcomes were not computed because discovery/validation gate failed; no challenge replay. Do not relax delay gate post-result.
- R282 runner, prereg, report, results JSON and event-coverage CSV are archived. No GitHub Actions backtest workflow was launched.
- Overall status R270–R282: no candidate promoted. R276 is only a historical screening pass with material unresolved failures; R277–R281 fail signal gates; R282 is data-ineligible, not a proven losing strategy.


## Latest research update — R282 EURUSD weekend-reopening gap fade — INVALID TEST (2026-10-17)

- [Preregistration](research/R282_EURUSD_WEEKEND_GAP_FADE_PREREGISTRATION.md) · [runner](research/r282_eurusd_weekend_gap_fade.py) · [report](research/R282_FINAL_REPORT.md) · [JSON](research/R282_results_compact.json) · [event audit](research/R282_event_audit.csv)
- Input archive SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`, collected with `-fl`; most Sunday reopening bars were omitted. Only 3 long-closure candidates detected, none with exact T+10 minute continuity; zero trades evaluated.
- This is **not** a no-edge result; data is inadequate to test weekly reopen gap fade. No strategy outcomes or forward period metrics were calculated. Do not patch event definition after seeing the issue; retry only with verified raw BID/ASK M1 including true weekend reopen observations. No GitHub Actions workflow launched.


## Latest research update — R283 US index cash-open gap fade — GAGAL (2026-10-17)

- Preregistration: [R283 design](research/R283_PREREGISTRATION.md)
- Results: [final report](research/R283_FINAL_REPORT.md) · [period summary](research/R283_period_summary.csv) · [data audit](research/R283_data_audit.csv)
- Tested four BID-only US index M5 archives. Rules locked: per-index Q80 gap fitted on 2017–2020; fade 09:30 open gap at 09:40 ET (T+10); target prior RTH close; stop 0.75× original gap; no overnight; modeled round-trip 1/2/4 bps.
- At 2 bps, discovery 2017–2020 = 709 trades, PF 0.748, net -77.90R; validation 2021 = 163 trades, PF 0.599, net -34.83R. Trade-count gates passed, expectancy gates failed. 2022–2025 deliberately not scored; no forward period opened.
- Verdict: **GAGAL**, close this exact spec, do not tune it. No alpha retained. Data are BID-only and costs modeled; actual spread/CFD point value/commission/slippage/swaps and funded equity-path replay remain absent. No Actions workflow launched.
- R283 source runner and full row-level ledger were executed/stored locally in this session but are not yet archived in GitHub; report, preregistration, compact period summary and input audit are archived. Do not claim repository-only full reproducibility until source/ledger are committed.


## 2026-10-17 — R283 trade-level postmortem

**R283 remains GAGAL; no strategy was promoted.** The locked local trade ledger was decomposed after the fail decision; this was diagnostic only, not parameter tuning.

- Discovery 2017–2020: 709 trades, gross PF 0.795 and gross -61.75R before modeled costs; at 2 bp PF 0.748 and -77.90R.
- Validation 2021: 163 trades, gross PF 0.638 and gross -30.52R; at 2 bp PF 0.599 and -34.83R.
- Discovery exits: 152 target fills versus 237 stop exits; session-close exits were 320 trades and contributed only +1.04R after 2-bp cost.
- Validation exits: 35 target fills versus 72 stop exits; the stop share rose from 33.43% in discovery to 44.17%, while the target share stayed near 21.3–21.5%.
- The strategy is negative before modeled costs; costs worsen it but do not explain the underlying failure.
- Fading gap-ups (SHORT) was materially weaker than fading gap-downs (LONG) in both segments. Both directions remained negative. This asymmetry is a hypothesis lead only; it is not evidence for gap continuation.
- 2022–2025 was not scored, and 2026 remains unopened under the existing contamination rules. R283's exact spec must not be tuned.

Archived diagnostic artifacts:
- [Trade-level diagnostic](research/R283_TRADE_LEVEL_DIAGNOSTIC.md)
- [Exit decomposition](research/R283_EXIT_DECOMPOSITION.csv)
- [Direction decomposition](research/R283_DIRECTION_DECOMPOSITION.csv)
- [Instrument/year decomposition](research/R283_INSTRUMENT_YEAR_DECOMPOSITION.csv)
- [Machine-readable diagnostic results](research/R283_DIAGNOSTIC_RESULTS.json)

**Known persistence gap:** the 872-row R283 trade ledger and exact runner were available in the local analysis workspace, but they have not yet been committed to this branch. The report explicitly records that repository-only reproduction is incomplete. Next work should resolve this gap by archiving the row ledger/runner or recreating and committing them from the verified source archives; do not pretend it is already done and do not ask the user to upload data that are available in the current runtime.


## Latest research update — R284 late-morning continuation — GAGAL (2026-10-17)

- [Pre-registration](research/R284_US_INDEX_LATE_MORNING_CONTINUATION_PREREGISTRATION.md) was committed before calculating outcomes.
- [Final report](research/R284_FINAL_REPORT.md) · [machine-readable results](research/R284_results_compact.json).
- New, structurally distinct hypothesis: direction-following of the 10:00–11:55 ET index move, one selected instrument per New York session, child threshold based only on each instrument's 2017–2020 Q75; T+10 entry at 12:05; 1.0× range stop / 1.5R target / 15:55 bar-open force-flat.
- Data: four R205 cached GitHub artifacts; M5 BID-only. Eligibility counts: USA500 2,662 sessions; USATECH 2,675; USA30 2,672; USSC2000 2,022. The flat-candidate filter is heuristic; modeled 1/2/4 bp costs are not verified CFD costs.
- At 2 bp, child discovery 2017–2020 = 380 trades / PF 0.864 / -13.108R / max DD 16.264R. Annual net R: 2017 -3.011; 2018 -0.051; 2019 -6.957; 2020 -3.090 (0/4 positive). Validation 2021 = 114 / PF 1.066 / +1.326R, but this modest result does not rescue negative discovery. At 4 bp the discovery PF falls to 0.797.
- Matched parent baseline at 2 bp was also negative: discovery 981 trades / PF 0.822 / -47.650R; 2021 251 / PF 0.941 / -3.266R. Child reduces discovery loss versus parent but is still not an edge.
- **Verdict: GAGAL.** The discovery PF, net-return, positive-year, and 4-bp PF gates failed. 2022–2025 and 2026 outcomes were not computed/opened as required; no funded challenge replay and no Actions backtest were run. Do not lower threshold or alter this exact specification post-result.
- Persistence update: result JSON, report and compact replay engine are now on GitHub. The compact engine was compared with the original full local run and matched all parent/child trade counts, PFs and net-R totals for discovery/validation at 1/2/4 bp exactly. The row-level trade ledger is still not archived, so trade-by-trade reproduction remains incomplete. The signal has not been promoted and does not enter the edge-backed block set.


## Latest research update — R285 US500 turn-of-month intraday seasonality — GAGAL (2026-10-17)

- [Preregistration](research/R285_US500_TURN_OF_MONTH_INTRADAY_PREREGISTRATION.md) was committed before any return calculations. A data-quality-only calendar amendment was then committed before PnL: [R285 DQ1](research/R285_DQ1_PREOUTCOME_CALENDAR_AMENDMENT.md).
- [Final report](research/R285_FINAL_REPORT.md) · [machine metrics](research/R285_results_compact.json) · [local replay runner](research/r285_us500_tom_intraday.py) · [candidate return ledger at 2 bp](research/R285_candidate_ledger_2bp.csv) · [selected-date skip log](research/R285_selected_session_skips.csv).
- New mechanism: long US500 only on the first three or final two observed active RTH dates of each month; enter 09:40 ET, exit 15:55 ET. This is a calendar-seasonality test, not a retuned R283/R284 price trigger. M5 BID-only source artifact 11709864394, archive SHA-256 `21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac`.
- At modeled 2 bp round-trip cost, discovery 2017–2020 = 226 trades / PF 1.130 / +785.76 bp; parent all-session long = 979 / PF 0.985 / -380.59 bp. The candidate discovery total was highly regime-concentrated: 2017 -132.96 bp, 2018 -502.78 bp, 2019 -136.29 bp, 2020 +1,557.79 bp.
- Validation 2021 = 58 trades / PF 0.632 / -669.02 bp, whereas the all-session parent returned +539.74 bp at the same cost. At 4 bp, candidate validation PF was 0.583.
- **Verdict: GAGAL.** Discovery fails the >=3-of-4 positive-year gate; validation fails PF/net gates at 2 bp and the PF stress at 4 bp. 2022–2025 and 2026 trade outcomes were not calculated or inspected, and no funded replay was run.
- Data screen: 2,777 active RTH session dates, 2,659 quality-eligible, 650 candidate calendar dates, 36 selected sessions skipped for missing bars or repeated-flat candidates. The flat filter is heuristic; BID-only and modeled costs are not live execution evidence.
- The compact local runner was rerun and matched candidate/parent counts, PF and net-bps totals for discovery/validation at each 1/2/4 bp cost. Candidate ledger and selected-date skip log are archived. No GitHub Actions backtest was launched. The failed signal block is not retained for evolutionary crossover; only the calendar/data-quality and execution-audit procedures remain reusable.


## Latest research update — R286 US500 three-session overextension fade — GAGAL (2026-10-17)

- [Pre-registration](research/R286_US500_3SESSION_OVEREXTENSION_FADE_PREREGISTRATION.md) was committed before strategy-return calculations.
- [Final report](research/R286_FINAL_REPORT.md) · [machine-readable results](research/R286_results_compact.json) · [local replay runner](research/r286_us500_3session_fade.py) · [candidate ledger](research/R286_candidate_ledger_2017_2021.csv) · [matched parent ledger](research/R286_matched_parent_ledger_2017_2021.csv) · [skipped entry-session log](research/R286_skipped_signals.csv).
- Hypothesis: fade a three-consecutive-active-session close-to-close move when its absolute value exceeds discovery-only Q80. Q80 = 1.7307755%, fitted on 858 qualifying 2017–2020 signal windows. Entry next active session 09:40 ET, exit that session 15:55 ET; matched parent follows the same move on the same events.
- Input: cached GitHub R205 USA500 M5 BID-only artifact 11709864394; archive SHA-256 `21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac`; extracted CSV SHA-256 `df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee`. Data screening retained 2,777 active RTH dates and 2,659 quality-eligible dates; seven selected events were skipped because the next entry session was invalid.
- At modeled 2 bp round-trip cost, candidate discovery 2017–2020 = 165 trades / PF 0.9882 / -87.79 bp; matched continuation parent = 165 / PF 0.9258 / -572.21 bp. Validation 2021 candidate = 47 / PF 0.9869 / -15.25 bp; matched parent = 47 / PF 0.8591 / -172.75 bp.
- Candidate cost stress PF: discovery 1/2/4 bp = 1.0105/0.9882/0.9451; validation = 1.0280/0.9869/0.9107. The candidate reduces losses relative to its parent but is still negative in both discovery and validation.
- **Verdict: GAGAL.** Discovery PF/net at 2 bp and validation PF/net at 2 bp fail. The positive-year count gate was met only nominally because 2017 contains one trade; 2018 lost 1,315.07 bp, while 2020 gained 1,115.63 bp. Do not alter Q80, direction, lookback or times after results.
- 2022–2025 and 2026 outcomes were not calculated or inspected, and no funded challenge replay was run. Cost model remains hypothetical due BID-only data; this is not funded-readiness evidence.
- The replay runner, results JSON, candidate row ledger, matched parent ledger and skipped-signal log are now archived. The matched parent ledger uses the exact same event dates and opposite direction/return on each event. No GitHub Actions backtest was created or dispatched. No signal block is retained for strategy crossover; only implementation/data-quality controls remain reusable.


## Latest research update — R287 intraday cross-index residual fade — GAGAL (2026-10-17)

- [Pre-registration](research/R287_US_INDEX_INTRADAY_RESIDUAL_REVERSION_PREREGISTRATION.md) was committed before return/PnL calculation.
- [Final report](research/R287_FINAL_REPORT.md) · [machine-readable results](research/R287_results_compact.json) · [local replay runner](research/r287_intraday_residual_reversion.py) · [paired candidate/parent ledger](research/R287_paired_ledger_2017_2021.csv) · [session-quality summary](research/R287_session_quality_summary.csv).
- Hypothesis: measure the 10:00 open to 12:55 close return for USA500, USATECH, USA30 and USSC2000, subtract same-date cross-sectional median, select the strongest normalized absolute residual using per-symbol Q75 thresholds fitted on 2017–2020, then fade the residual at 13:05 and force flat at the 15:55 bar open.
- Extracted source CSV SHA-256 values: USA500 `df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee`; USATECH `82b06c38f66cd1387097691baac1d45c9463b6540eea9dfe28a894d85e122f7c`; USA30 `8fcef9d76b31e99ae8d0175e769307ab13f930ae3ec2c17ef6baf0311ea1783a`; USSC2000 `c01c97d8705453d3fa3fd4ac1d386e9c1d72ab27e3b7d57d6cde53da9dfdf6f0`. Inputs are cached GitHub R205 M5 BID-only files.
- Session-quality valid counts (2017–2021): USA500 1,230; USATECH 1,240; USA30 1,237; USSC2000 836. 1,228 dates had at least three valid symbols. 745 synchronized events met the normalized residual score gate: 552 discovery trades and 193 validation trades.
- At modeled 2 bp cost, candidate fade discovery = 552 / PF 0.802 / -2,742.47 bp; validation = 193 / PF 0.628 / -1,510.80 bp. Cost stress PF at 1/2/4 bp was 0.838/0.802/0.734 in discovery and 0.667/0.628/0.555 in validation. **R287 = GAGAL.**
- Matched parent direction (following rather than fading the same residual) did better: discovery PF 1.044 / +534.47 bp and validation PF 1.253 / +738.80 bp at 2 bp. This is a diagnostic finding, not an approved replacement: direction was observed to outperform inside the same study, discovery PF was below 1.05, and using it as a chosen strategy creates selection bias.
- 2022–2025 and 2026 PnL outcomes were not calculated for R287; no funded challenge replay and no GitHub Actions backtest workflow were run. BID-only prices and modeled costs do not verify actual CFD execution or DLL/MLL.
- Row-level paired candidate/parent ledger and symbol-level source quality summary are now archived. The failed fade signal is not retained as an alpha block; reusable elements are cross-sectional residual calculation, synchronized event matching, data-quality controls and matched-direction ablation as research methods, not a signal.


## Latest research update — R288 cross-index residual follow-through — GAGAL (2026-10-17)

- Pre-registration locked before outcome calculation: [R288 preregistration](research/R288_US_INDEX_INTRADAY_RESIDUAL_FOLLOW_PREREGISTRATION.md), commit `5cf412ad6d335d4c8f651750cd312804ef9a0c61`.
- [Final report](research/R288_FINAL_REPORT.md) · [compact machine results](research/R288_results_compact.json) · [exact local replay runner](research/r288_us_index_intraday_residual_follow.py) · [annual table](research/R288_annual_follow_2bp.csv).
- Inputs are R205 M5 BID-only cached assets from run 38160487617: USA500 artifact 11709864394, USATECH 11710370389, USA30 11710730507, USSC2000 11710111254. Raw source artifacts have their existing expiry; ZIP and extracted CSV SHA-256 values are recorded in the runner/results JSON. Source latest UTC: 2026-10-09 20:10.
- Locked method: 10:00 ET open to 12:55 ET close signal return minus same-date median across >=3 eligible symbols; per-symbol Q75 absolute residual from eligible 2017–2020 data only; one top normalized event/date (score>=1); follow residual; enter 13:05 ET open and exit 15:55 ET open. PnL is calculated only for 2022–2026, not 2017–2021.
- At modeled 2 bp cost, follow candidate 2022–2025: 718 trades, PF 0.795, net -3,389.34 bp; 2026: 154 trades, PF 0.943, net -116.46 bp. 4-bp PF is 0.721 / 0.807, respectively. All gates except trade-count gates failed.
- The matched fade stream is only a same-event diagnostic: 2022–2025 PF 1.035 / +517.34 bp at 2 bp, but PF 0.940 / -918.66 bp at 4 bp; 2026 loses at all cost levels. Do not promote either direction.
- Four-week circular bootstrap of the follow candidate’s 2022–2025 weekly net at 2 bp: mean -16.22 bp/week, 95% CI [-32.80, -0.30] (209 weeks, 5,000 replicates, seed 288).
- Binary verdict: **GAGAL**. Do not adjust thresholds/direction/timing using these outcomes. The 2022–2025 window is project-contaminated; 2026 is a later chronological check, not claimed as a pristine program-level holdout. No funded equity path was run.
- Execution/data caveats: M5 BID-only data, modeled rather than observed transaction costs, heuristic repeated-flat exclusion, no verified CFD contract multipliers/commissions/swaps, no ask-side fill reconstruction, and no DLL/MLL challenge replay.
- Reusable methodological blocks only: synchronized eligible-session construction, frozen threshold fitting, deterministic one-event-per-session selection, matched same-event direction ablation, cost-stress/weekly-bootstrap reporting. No positive alpha block is retained from R288.


## R289 — Continental Europe cash-open gap continuation — GAGAL (2026-10-17)
- Locked rules and pre-outcome timestamp clarification: [R289 preregistration](research/R289_CONTINENTAL_EUROPE_GAP_CONTINUATION_PREREGISTRATION.md), final amendment commit `f3dba6084362a2b27855031945ca700521d586bc`.
- [Final report](research/R289_FINAL_REPORT.md) · [compact results JSON](research/R289_results_compact.json) · [Python replay runner](research/r289_continental_europe_gap_continuation.py) · [annual return summary](research/R289_annual_summary_2bp.csv) · [validation bootstrap output](research/R289_validation_weekly_bootstrap_2bp.json) · [session-quality audit summary](research/R289_session_quality_audit_summary.csv).
- Continuation discovery 2017–2020: 251 trades; at modeled 2 bp, PF in R 1.2245, +20.682R. Validation 2021: 61 trades; PF in R 1.1283, +3.088R. The four-week block-bootstrap validation 95% CI was [-0.1767R, +0.2817R] per week, so its lower-bound gate failed.
- **Binary verdict GAGAL**; no 2022–2026 PnL was calculated. No parameter retuning or promotion.
- R205 cached M5 BID-only source artifacts: DEUIDXEUR 11710710062, FRAIDXEUR 11710800007, EUSIDXEUR 11710326105; hashes and eligible-session counts are in the results JSON. EUSIDXEUR has materially poorer early coverage because repeated-flat bars were excluded.
- Limits: modeled costs rather than observed executable costs, no verified CFD multiplier/fees/swaps, M5 intrabar stop/target order approximated stop-first, no equity-aware DLL/MLL funded replay. No alpha block promoted; retain only session quality, frozen quantile calibration and bootstrap gate as research process.


## R290 — US cash-open breakout-retest — GAGAL (2026-10-17)
- Pre-registration committed before testing: [R290 rules](research/R290_US_CASH_OPEN_BREAKOUT_RETEST_PREREGISTRATION.md). Exact local replay runner: [r290_us_cash_open_breakout_retest.py](research/r290_us_cash_open_breakout_retest.py).
- [Final report](research/R290_FINAL_REPORT.md) · [exact compact results JSON](research/R290_results_compact.json) · [annual summary](research/R290_annual_summary.csv) · [validation block-bootstrap output](research/R290_validation_weekly_bootstrap_2bp.json) · [session-quality summary](research/R290_session_quality_summary.csv).
- New child relative to R263: require a separate retest of the opening-range boundary, close back outside, then enter next M5 open (5-minute delay); stop is opposite OR boundary, target 1.5R, one trade total across USA500/USATECH per day, stop-first if both levels touched in one M5 bar.
- Discovery 2016–2020: 1,059 trades; at 2 bp modeled cost, PF_R 0.834, net −95.595R, max closed-trade DD 104.38R; all five years negative. At 4 bp PF_R 0.732; at 6 bp 0.644.
- Validation 2021: 214 trades; at 2 bp PF_R 1.220, net +20.925R, but block-bootstrap weekly-net-R 95% CI [-0.111, +0.884] crosses zero; at 6 bp PF_R 0.961. Binary verdict **GAGAL**.
- Post-2021 PnL was intentionally not calculated after preregistered gates failed. Data is cached R205 M5 BID-only USA500 / USATECH, latest source 2026-10-09 20:10 UTC; 2/4/6 bp are modeled cost stress, not measured broker costs. No funded-equity DLL/MLL replay. No alpha block retained.


## R291 — US-to-German cross-session lead/lag — GAGAL (2026-10-17)
- [Preregistration](research/R291_TRANSATLANTIC_LEAD_LAG_PREREGISTRATION.md) · [Final report](research/R291_FINAL_REPORT.md) · [Compact results JSON](research/R291_results_compact.json) · [Local replay runner](research/r291_transatlantic_lead_lag.py) · [Annual summary](research/R291_annual_summary_2bp.csv) · [Validation bootstrap](research/R291_validation_weekly_bootstrap_2bp.json).
- Hypothesis: direction of the previous eligible USA500 RTH session predicts German index same-day session direction; threshold is Q75 absolute USA500 cash-session return, fitted 2017–2020, next eligible German-local session only, entry 09:20 Berlin, initial stop from first 20 minutes, target 1.5R, session-close exit, no overnight.
- Discovery 2017–2020: 246 trades, **gross PF_R 0.769 / −36.653R before costs**; at modeled 2 bp, PF_R 0.451 / −134.421R; 4 bp PF_R 0.302. All four years negative at 2 bp.
- Validation 2021: 74 trades; gross PF_R 1.228 / +8.547R, but after modeled 2 bp PF_R 0.178 / −173.679R. Four-week block-bootstrap mean −3.277R/week, 95% CI [−9.525, +0.040], lower bound fails. One trade had a 0.02-point stop and a huge modeled R-cost burden, showing the locked stop definition is not operationally robust.
- **Binary verdict: GAGAL.** Only trade-count gates passed. No PnL calculated for 2022–2026; do not add a minimum stop filter and retest the same windows. No signal alpha block retained.
- Inputs: existing R205 cached M5 BID-only USA500 and DEUIDXEUR. Costs are modeled basis-point stresses, not observed broker costs. No actual ask-side execution or FundedNext DLL/MLL equity-path replay. The 2021 validation window is contaminated by other research.


## R292 — USA500 overnight-only long carry — GAGAL (2026-10-17)
- [Preregistration](research/R292_USA500_OVERNIGHT_CARRY_PREREGISTRATION.md) · [Final report](research/R292_FINAL_REPORT.md) · [compact JSON](research/R292_results_compact.json) · [replay runner](research/r292_usa500_overnight_carry.py) · [annual table](research/R292_annual_summary_2bp.csv) · [validation bootstrap](research/R292_validation_weekly_bootstrap_2bp.json).
- Frozen rule: buy at the close proxy of the eligible USA500 M5 bar starting 15:55 New York, exit at the next eligible RTH session 09:30 open; constant-notional long exposure, no SL/TP, no direction/day filter, no overnight segment other than close-to-next-open. 1/2/4 bp round-trip costs are modeled sensitivities.
- Discovery 2017–2020: 978 trades; at 2 bp PF in net-bp outcomes 1.094 and +1,995.48 bp; PF at 4 bp 1.002. Four of four years positive on 2 bp net, but 2020 closed-trade drawdown reached 38.57% of fixed notional.
- Validation 2021: 250 trades; PF 1.186 and +742.22 bp at 2 bp, PF 1.058 at 4 bp. Four-week circular weekly-net-bp bootstrap mean +14.00 bp/week, 95% CI [-2.24, +30.11] bp/week; lower bound crosses zero.
- **Binary verdict GAGAL** because the preregistered validation bootstrap gate failed. Do not calculate 2022–2026 PnL or tune this same rule on 2017–2021. This is a potentially informative overnight-segment effect but not a promoted alpha block.
- Limits: cached USA500 M5 BID-only data, modeled costs, no measured spread/slippage/swap, no overnight floating-equity path or FundedNext DLL/MLL replay. Fixed-notional cumulative PnL is not a leveraged account/challenge simulation.


## Latest research update — R293 GAGAL (2026-10-17 local replay)

**R293: USA500 overnight carry + closing cross-index breadth filter — GAGAL.** The preregistration was committed before candidate outcome calculation. See:
- [Preregistration](research/R293_USA500_OVERNIGHT_BREADTH_FILTER_PREREGISTRATION.md)
- [Final report](research/R293_FINAL_REPORT.md)
- [Compact result JSON](research/R293_results_compact.json)
- [Local replay runner](research/r293_usa500_overnight_breadth_filter.py)
- [Updated evolutionary block registry](research/EVOLUTIONARY_BLOCK_REGISTRY_20261016.md)
- [Updated evidence matrix](research/EVIDENCE_MATRIX_20261016.json)

### Locked experiment

R293 crosses R292's long USA500 final-session-close-to-next-session-open exposure with cross-index breadth as a context filter. Signal is the close of the 15:45 ET M5 bar; enter USA500 at the 15:55 bar open; require >=75% of valid USA500, USATECH, USA30 and USSC2000 feeds (at least three eligible feeds) to have a positive 09:30-open-to-15:45-close session return; exit at the next eligible USA500 09:30 open. The unconditional long at the same timestamps is the matched diagnostic parent. Cached raw M5 BID archives all passed the four preregistered SHA-256 checks. The session-quality audit covered 5,531 instrument-session rows spanning 2016–2021.

### Results at modeled 2 bp round-trip costs

| Metric | Discovery 2017–2020 | Validation 2021 |
|---|---:|---:|
| Candidate trades | 442 | 119 |
| Candidate net bp | +1,320.41 | +249.78 |
| Candidate PF | 1.137 | 1.144 |
| Candidate PF at 4 bp | 1.043 | 1.006 |
| Unconditional parent trades | 975 | 250 |
| Parent net bp | +1,533.09 | +459.12 |
| Parent PF | 1.070 | 1.109 |

Candidate max closed-PnL drawdown in discovery was 24.54% of fixed notional vs 37.96% for the parent. Candidate PF and fixed-notional closed DD improved relatively, but total net bp and trade count fell in both periods. Those fixed-notional closed-trade figures do not represent leveraged funded-account drawdown.

The locked 2021 four-week circular bootstrap (5,000 resamples, seed 293; 52 Monday-start weeks including zero-trade weeks) returned +4.803 bp/week with 95% CI [-5.548, +14.232] bp/week. The lower bound crosses zero: **binary verdict GAGAL**. No threshold rescue or second pass on the same periods. Do not calculate 2022+ strategy PnL for R293; no funded challenge replay was run and no signal-alpha block is retained. Preserve only the research lesson that breadth improved relative PF/DD in this sample but failed robustness and reduced aggregate return.

Limitations: four cached index feeds are BID-only; 1/2/4 bp are modeled costs rather than verified quotes. ASK-side fill, actual spread/slippage/commission/contract point value, swap, overnight floating PnL, margin and FundedNext DLL/MLL equity-path behavior are unverified. The 2017–2021 periods are contaminated by related work and are not pristine program-level OOS.

### Next generation

All candidates R270–R293 remain unpromoted. Continue with a materially distinct, preregistered hypothesis family; reuse integrity/latency/session and matched-parent controls, not failed signal blocks. Optimize the two-phase funded target completion probability/time subject to loss-rule breach risk; do not select by PF alone. Require all locked historical gates before any conditional later-period diagnostic, then a separate verified-cost/overnight-risk and FundedNext equity-aware two-phase challenge replay before any funded-ready claim.


## Latest research update — R294 GAGAL (2026-10-17 local replay)

**R294 USA500 Two-Sided Extreme-Breadth Overnight Direction — GAGAL.** The preregistration was committed before candidate outcomes were calculated.

- [Preregistration](research/R294_USA500_TWO_SIDED_BREADTH_OVERNIGHT_PREREGISTRATION.md)
- [Final report](research/R294_FINAL_REPORT.md)
- [Compact results JSON](research/R294_results_compact.json)
- [Local replay runner](research/r294_usa500_two_sided_breadth_overnight.py)
- [Updated evolutionary block registry](research/EVOLUTIONARY_BLOCK_REGISTRY_20261016.md)
- [Updated evidence matrix](research/EVIDENCE_MATRIX_20261016.json)

### Locked hypothesis
R294 crosses R293's positive-tail long-only breadth condition with a mirrored short tail: long when at least 75% of valid US-index feeds rose from 09:30 open to 15:45 close, short when at most 25% rose, otherwise flat. Entry is the USA500 15:55 M5 bar open; exit is the next quality-valid USA500 09:30 open. This tests whether closing breadth provides overnight directional information in both tails, without modifying R293's entry/exit or thresholds. Four cached R205 M5 BID feeds passed their registered SHA-256 checks; the local session-quality audit covered 5,531 instrument-date rows. PnL outcomes were restricted to discovery 2017–2020 and validation 2021; no 2022+ outcome was calculated.

### Results at modeled 2 bp round-trip cost
| Metric | Discovery 2017–2020 | Validation 2021 |
|---|---:|---:|
| Candidate trades | 786 | 216 |
| Long / short trades | 442 / 344 | 119 / 97 |
| Candidate net bp | -137.72 | -448.43 |
| Candidate PF | 0.993 | 0.891 |
| Candidate PF at 4 bp | 0.918 | 0.797 |
| R293 positive-tail long-only net bp | +1,320.41 | +249.78 |
| R293 positive-tail long-only PF | 1.137 | 1.144 |
| Unconditional-long net bp | +1,533.09 | +459.12 |
| Unconditional-long PF | 1.070 | 1.109 |

At 2 bp, the child lost in both partitions and underperformed both matched controls. Annual discovery child PnL was negative in 2017 (-327.49 bp) and 2019 (-1,249.12 bp), positive in 2018 (+609.19 bp) and 2020 (+829.70 bp). The 2021 weekly-net-bp bootstrap mean was -8.624 bp/week with 95% CI [-26.012, +7.195] over 52 weeks including zero weeks, 5,000 circular four-week block resamples, seed 294. Multiple preregistered gates failed. **R294 = GAGAL; no alpha block retained and no FundedNext replay run.**

### Evolutionary disposition
R293's long-tail result remains the stronger historical diagnostic, but it also failed its robustness gate and is not approved for funded use. R294 shows the negative-breadth short mirror was not beneficial on these sampled windows. Do not retune the 25% short cutoff or rerun the same periods as a rescue. Next research generation must move to another economically distinct hypothesis family, reuse only integrity/execution/paired-comparison controls, retain the registered failed signal blocks as failures, and keep 2022+ R294 PnL unopened. All cached inputs are BID-only; short ASK-side fills, real spreads/slippage/commission/swaps, overnight floating equity, margin and FundedNext loss-rule path remain unverified.


## Latest research update — R295 GAGAL (2026-10-17 local replay)

**R295: positive breadth + USA500 own-session direction confirmation — GAGAL.** Preregistration preceded outcome calculation. Research artifacts:
- [Preregistration](research/R295_BREADTH_PLUS_USA500_DIRECTION_CONFIRMATION_PREREGISTRATION.md)
- [Final report](research/R295_FINAL_REPORT.md)
- [Compact result JSON](research/R295_results_compact.json)
- [Local runner](research/r295_breadth_plus_usa500_direction_confirmation.py)
- [Updated evolutionary block registry](research/EVOLUTIONARY_BLOCK_REGISTRY_20261016.md)
- [Updated evidence matrix](research/EVIDENCE_MATRIX_20261016.json)

### Frozen hypothesis and data

R295 adds one component to R293's positive-tail long-only breadth stream: USA500's own 09:30 open to 15:45 M5 close return must also be strictly positive. The >=75% positive breadth rule, 15:55 ET entry, next valid USA500 09:30 exit, four M5 BID inputs and 1/2/4 bp costs were unchanged. Four registered checksums passed; session audits covered 5,531 instrument-session rows. PnL was restricted to discovery 2017–2020 and validation 2021.

### Results at modeled 2 bp

| Metric | Discovery candidate | Discovery R293 parent | Validation candidate | Validation R293 parent |
|---|---:|---:|---:|---:|
| Trades | 437 | 442 | 119 | 119 |
| Net bp | +1,253.10 | +1,320.41 | +249.78 | +249.78 |
| PF | 1.131 | 1.137 | 1.144 | 1.144 |

The added condition removed five discovery trades and zero validation trades. Those five trades had +67.31 bp net and PF 1.692 at 2 bp cost; the added filter discarded a profitable subset. Validation was identical to R293. The weekly-net-bp bootstrap (5,000 circular four-week resamples, seed 295, all 52 Monday-start weeks including zero-trade weeks) gave mean +4.803 bp/week and 95% CI [-5.557, +14.335], which crosses zero. **R295 = GAGAL.**

No funded challenge replay and no post-2021 candidate PnL were run. No alpha block was retained. The correct next decision is to close this breadth micro-mutation family rather than keep adding overlapping filters; R293 remains a research diagnostic, not approved funded strategy. Inputs are BID-only, modeled costs are not verified execution costs, and no overnight floating loss/swap/account-equity path was modeled.

### Next-generation constraint

Do not promote any candidate from R270–R295. Shift to a materially distinct hypothesis family, freeze it before outcomes, use the established data/timestamp/cost controls, and preserve 2022+ R295 results unopened. The objective remains probability and time of completing both funded targets without DLL/MLL breach; PF and trade count are diagnostics only.


## Data-quality incident — R296 INVALID TEST (2026-10-17)

R296's first attempt incorrectly took the first raw Sunday timestamp (usually 00:00 UTC) as the executable weekly reopening. The paired XAUUSD BID/ASK source has static O=H=L=C rows repeated through Sunday 22:55 UTC; real active M5 bars start around 23:00 UTC. R296's positions and bootstrap therefore used non-tradable closed-market quote snapshots. Its performance statistics are invalid and must not be used as evidence for/against gap continuation, nor treated as a valid signal-family failure. See [R296 data-quality invalidation](research/R296_DATA_QUALITY_INVALIDATION.md). This exposed a data-validation gap: manifest include_synthetic_flat_bars=false is insufficient without checking observed row activity.

## Latest research update — R297 GAGAL (2026-10-17 local replay)

**R297: XAUUSD active-weekend-reopening gap continuation — GAGAL.** This candidate was separately preregistered before its new outcome calculation and corrects R296's event timestamp to the first actually active Sunday M5 bar; it does not tune R296's signal performance. Artifacts:
- [Locked preregistration](research/R297_XAUUSD_ACTIVE_REOPEN_GAP_CONTINUATION_PREREGISTRATION.md)
- [Final report](research/R297_FINAL_REPORT.md)
- [Compact results](research/R297_results_compact.json)
- [Local runner](research/r297_active_reopen_gap_continuation.py)
- [R296 invalid-test report](research/R296_DATA_QUALITY_INVALIDATION.md)
- [Updated evidence matrix](research/EVIDENCE_MATRIX_20261016.json)
- [Updated evolutionary block registry](research/EVOLUTIONARY_BLOCK_REGISTRY_20261016.md)

### R297 frozen methodology and source

Use XAUUSD M5 BID/ASK archive 12031270051 (collection run 38859918137). Both gzip SHA-256 hashes and the exact 947,326 timestamp pairs passed. Before signal calculation the replay excluded every timestamp >=2026-01-01, so 69,396 later rows were held back. The corrected event finder uses the first active M5 bar after the Sunday static quote block, compares that with the last active Friday close, requires a gap larger than twice the sum of those active bid/ask spreads, enters with T+10 execution delay, uses a gap-sized 1R stop/target and an exact T+4h max hold. No bars were synthesized.

### Results at modeled +$0.30/oz additional cost

| Metric | Discovery 2016–2020 | Validation 2021–2025 |
|---|---:|---:|
| Completed trades | 24 | 28 |
| Net R | -6.161 | +0.385 |
| PF_R | 0.460 | 1.042 |
| Maximum closed R DD | 7.116R | 3.026R |
| Stop / target / time exits | 10 / 5 / 9 | 7 / 8 / 13 |

Only 52 of 500 active weekend-gap candidates passed the locked combined-spread, quote and complete active-path conditions. Discovery PF/expectancy failed. The validation point estimate is slightly positive but under PF_R 1.05; its 4-week block bootstrap mean was +0.00148R/week, 95% CI [-0.02939, +0.03141], crossing zero. At +$0.50/oz, validation turns negative (-0.253R, PF_R 0.973). The discovery and validation minimum-trade gates also fail; at least 3/5 validation years were positive but the remaining gates dominate the decision.

**R297 = GAGAL.** No 2026 PnL was calculated, no gap-fade side was tested as a rescue, and no funded challenge replay was run. No alpha block is retained. R297 is not funded-ready.

### Evolutionary decision

Preserve R296 as a data-quality incident, not a negative signal result. Preserve R297 as a valid corrected but failed signal candidate. Do not change the 2x spread filter, reverse gap direction or retune the 4-hour exit on these same dates. Future candidates must identify active quote bars independently of the manifest flag before creating signals. Funded readiness remains blocked without verified account-specific costs and a separate equity-aware two-phase replay.


## R298 — XAUUSD London Asian-range sweep-and-reclaim reversal — GAGAL (2026-10-17)

The R298 preregistration was committed before candidate PnL was calculated. It tests the first London-local 07:00–10:00 M5 sweep beyond 0.10× the completed UTC 00:00–05:55 Asian range that closes back inside; entry is the signal bar start +10 minutes, stop at the executable-side signal-bar extreme, target the Asian midpoint, minimum planned reward/risk 1.00 and four-hour maximum hold.

The XAUUSD M5 BID/ASK hashes passed, timestamps paired one-to-one, 69,396 rows at/after 2026-01-01 were excluded before signal construction, and 598 trades completed in 2016–2025. At +$0.30/oz extra cost, discovery had 313 trades, −285.893R and PF_R 0.297; validation had 285 trades, −178.933R and PF_R 0.409. Zero-added-cost outcomes were also negative in both partitions. All ten annual cohorts were negative at +$0.30/oz. Validation weekly bootstrap mean was −0.68557R/week, 95% CI [−0.89792, −0.47209].

**R298 = GAGAL.** Do not tune the existing dates or reverse direction as a rescue. No 2026 candidate PnL was calculated; no alpha block was promoted and no funded challenge replay was run. See [preregistration](research/R298_XAUUSD_LONDON_ASIA_RANGE_SWEEP_RECLAIM_PREREGISTRATION.md), [report](research/R298_FINAL_REPORT.md), [compact results](research/R298_results_compact.json) and [annual summary](research/R298_annual_summary.csv). Full local runner, trade ledger and data-quality audits are included in the research package. Historical BID/ASK results do not verify actual FundedNext fills or account-equity/DLL/MLL behavior.


## Research artifact storage policy (2026-10-18)

The user requested GitHub as the primary record and no more recurring local ZIP-download handoffs. For every new backtest generation, commit the preregistration before scoring, then commit the report, exact runner, compact JSON, annual summary, full trade ledger, all relevant quality/skip audits, and any bootstrap input series to `research/`. Add an index page and update this checkpoint. Final replies should link to the GitHub files and summarize the verdict; do not provide a sandbox ZIP by default. If a large raw binary input cannot be put in the repository through available tools, document its original artifact ID, source hashes and limitation in a committed data manifest instead of claiming the raw input is in GitHub.

R298's all-in-one entry point: [R298_INDEX.md](research/R298_INDEX.md). All report/code/ledger/audit files are individually present there; the original ~20 MB raw input ZIP remains external and is explicitly documented in [R298_DATA_MANIFEST.md](research/R298_DATA_MANIFEST.md).


## R299 local reproduction audit — 2026-10-18

R299 was independently replayed from exact source-member hashes with [the archived runner](research/r299_usatech_leads_usa500_30m.py). Q95 was 0.4476037999%, with 704 selected events / 704 completed trades. Discovery 2017–2020 at 2 bp was −65.080R / PF_R 0.792; validation 2021 was −21.376R / PF_R 0.764; validation bootstrap 95% CI was [−0.95826, +0.12894]R/week. **R299 remains GAGAL and closed.** No thresholds were retuned and no 2022+ PnL was calculated. Read the [reproduction audit](research/R299_REPRODUCTION_AUDIT_20261018.md) and [R299 index](research/R299_INDEX.md).

## R300 — EURUSD London fixing-window post-event reversal — GAGAL (2026-10-18)

- **Locked preregistration:** [R300 hypothesis and rules](research/R300_EURUSD_LONDON_FIX_POST_EVENT_REVERSAL_PREREGISTRATION.md). The exact runner and pre-outcome dataset audit were committed before signal PnL was calculated.
- **Report/index:** [R300 final report](research/R300_FINAL_REPORT.md) · [artifact index](research/R300_INDEX.md) · [compact metrics JSON](research/R300_results_compact.json) · [annual summary](research/R300_annual_summary.csv) · [2021 weekly bootstrap input](research/R300_validation_weekly_net_R.csv).
- **Method:** EURUSD M1 BID/ASK, active contiguous M5 aggregation, signal return from 15:40 to 15:55 London, entry at 16:05, 1R stop/target, maximum exit at 16:35. Primary extra-cost grid 0/0.5/1/2 pips, with 2022+ excluded before outcomes.
- **Data audit:** 2,650,553 paired M1 rows per side; 422,289 valid active M5 bars; 1,283 eligible event dates and 1,281 completed trades per direction. Entry-time spread median 0.30 pip, p95 0.40, max 0.80.
- **Primary result at +1 pip:** fade discovery 1,024 trades, −257.011R / PF 0.573; validation 257 trades, −59.981R / PF 0.580. Even with zero extra friction, net R was negative in both partitions. Matched follow control also lost. Validation weekly bootstrap at +1 pip: mean −1.1535R/week, 95% CI [−1.5884, −0.6723].
- **Verdict: GAGAL; close both signal directions.** Four of fourteen locked gates passed. Do not tune or direction-flip on these dates. Reuse only engineering controls; no alpha module is retained. This is not an equity-aware FundedNext challenge replay. No 2022+ PnL was calculated.

## Latest research update — R301 GAGAL (2026-10-19)

**R301: XAUUSD safe-haven delayed hedge response — GAGAL.** The preregistration was committed before outcomes. See:
- [R301 index](research/R301_INDEX.md)
- [Locked preregistration](research/R301_XAUUSD_SAFE_HAVEN_DELAYED_HEDGE_RESPONSE_PREREGISTRATION.md)
- [Final report](research/R301_FINAL_REPORT.md)
- [Compact metrics and gates](research/R301_results_compact.json)
- [Data manifest](research/R301_DATA_MANIFEST.md)
- [Annual cost/delay summary](research/R301_candidate_annual_summary.csv)
- [Validation bootstrap result](research/R301_validation_weekly_bootstrap.json)

At +$0.30/oz, discovery 2017–2020 had 315 trades, −170.908R and PF_R 0.327; validation 2021–2025 had 588 trades, −189.406R and PF_R 0.509. Both were negative at zero incremental cost. The 10-minute entry-delay stress remained negative. Validation bootstrap mean was −0.72293R/week, 95% CI [−0.91609R, −0.53769R]. Three of nine gates passed: data/event integrity, minimum trade count, and execution-path integrity. No signal block is retained.

Data checks passed: 877,930 XAU BID and ASK rows per side before cutoff with exact paired timestamps and zero invalid OHLC/negative open-close spreads; 2,558 complete USA500 New York RTH sessions, with 33 incomplete sessions excluded. The exclusive 2026-01-01 UTC cutoff was applied before features and outcomes; **XAUUSD 2026 remains unopened**. The result is a historical signal failure, not a funded-account equity/DLL/MLL replay.


## Latest research update — R302 XAUUSD PM benchmark pre-auction extension fade — GAGAL (2026-10-19)

**R302 is closed as GAGAL.** A new, preregistered hypothesis tested whether unusually large absolute gold moves in the 25 minutes before the scheduled 15:00 London PM benchmark tended to reverse after a delayed manual-compatible entry. Signal, thresholds, period split and execution rules were frozen in [the preregistration](research/R302_XAUUSD_PM_AUCTION_EXTENSION_FADE_PREREGISTRATION.md) before calculating outcomes. No threshold/direction/exit tuning was done after results.

- [Artifact index](research/R302_INDEX.md)
- [Preregistration](research/R302_XAUUSD_PM_AUCTION_EXTENSION_FADE_PREREGISTRATION.md)
- [Exact runner bootstrap](research/r302_xauusd_pm_auction_extension_fade.py)
- [Final report](research/R302_FINAL_REPORT.md)
- [Compact JSON](research/R302_results_compact.json)
- [Data-integrity audit](research/R302_data_audit.json)
- [Period / annual scorecard](research/R302_period_annual_summary.csv)
- [Validation weekly bootstrap summary](research/R302_validation_weekly_bootstrap.json)
- [Exact validation weekly input including zero-trade weeks](research/R302_validation_weekly_net_R.csv)
- [Data manifest / artifact hashes](research/R302_DATA_MANIFEST.md)
- [Detailed ledger restoration / completeness note](research/R302_LEDGER_REASSEMBLY.md)

At +$0.30/oz additional friction, discovery 2017–2020 produced 179 trades, −32.964R and PF_R 0.640; validation 2021–2025 produced 208 trades, −26.991R and PF_R 0.730. Validation was also negative at zero extra cost (−14.573R), at +$0.50/oz (−35.270R), and under T+15 entry delay at +$0.30/oz (−32.917R). The four-week circular bootstrap over 262 validation calendar weeks had mean −0.10302R/week, 95% CI [−0.18945, −0.01557]. Three of eight preregistered historical gates passed; expectancy/robustness gates failed. No FundedNext challenge replay was run.

The archive had 877,930 exactly paired BID/ASK timestamps before the exclusive 2026-01-01 UTC cutoff; no duplicate or invalid OHLC rows and no synthetic bars were used. The strategy used a scheduled-clock weekday proxy, not the historical official IBA non-publication calendar, and 2021–2025 is program-contaminated. Therefore the protected XAUUSD 2026 window remains unopened; R302 is not funded-ready.

**Reproducibility limitation:** the full high-volume row-level primary trade ledger, pre-outcome eligibility audit, and all-cost/delay ledger have local SHA-256 hashes recorded in the manifest, but are not yet present as row-level GitHub files. The compact results, period/annual summary, data audit, bootstrap summary and weekly bootstrap input are in GitHub. Do not call repository-only row-level reproduction complete until the large ledgers are transferred or deterministically rebuilt and checksum-matched.


## Latest research update — R303 GAGAL (2026-10-19 local replay)

**R303: EURUSD spread-shock reversion — GAGAL.** The new quote-state hypothesis was preregistered before signal PnL. See:
- [Locked preregistration](research/R303_EURUSD_SPREAD_SHOCK_REVERSION_PREREGISTRATION.md)
- [Entry eligibility amendment](research/R303_DQ1_ENTRY_ELIGIBILITY_AMENDMENT.md)
- [Daily volatility-threshold amendment](research/R303_DQ2_VOLATILITY_THRESHOLD_AMENDMENT.md)
- [Bootstrap aggregation correction log](research/R303_IMPL1_BOOTSTRAP_AGGREGATION_CORRECTION.md)
- [Artifact index](research/R303_INDEX.md)
- [Final report](research/R303_FINAL_REPORT.md)
- [Compact aggregate result summary](research/R303_results_compact.json)
- [Data / pre-outcome eligibility summary](research/R303_data_audit.json)
- [Annual/period scorecard](research/R303_period_annual_summary.csv)
- [Validation bootstrap](research/R303_validation_weekly_bootstrap.json)
- [Data and output manifest](research/R303_DATA_MANIFEST.md)

The source was existing GitHub artifact #11959096102, EURUSD M1 paired BID/ASK archive SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. Audit found 4,415,493 paired timestamp rows, zero duplicate/invalid OHLC/negative spreads, and 696,795 repeated flat-fill rows excluded. No missing bars were synthesized. Signal/PnL outcomes were limited to discovery 2017–2020 and validation 2021; 2022+ candidate PnL was not calculated.

At the registered +1 pip incremental round-trip friction and T+5 manual-compatible entry, discovery had 739 closed trades, -93.407R, PF_R 0.769; validation had 66 trades, -7.360R, PF_R 0.777. Validation four-week circular weekly-net bootstrap: mean -0.14153R/week, 95% CI [-0.40550,+0.11319], positive-mean share 13.92%. At +0.5 pip incremental cost both periods turn negative; T+10 stress is also negative. Only 2/13 locked gates passed, including a failed minimum validation-sample gate (76 entry-eligible before overlap; 66 final closed trades). **R303 GAGAL; no signal block retained and no FundedNext replay run.**

**Archive limitation:** report, index, normalized aggregate JSON, data/eligibility summary, period/annual summary, and bootstrap summary are committed. The exact local runner source and full row-level trade/skip/eligibility CSVs remain identified by SHA-256 in the manifest but are not yet stored as decoded row-level GitHub files. The reproducibility gate is therefore explicitly failed. Do not claim R303 is repository-only reproducible or funded-ready until exact source and row-level artifacts are restored and checksum-verified.

## Latest authoritative objective update — 2026-10-19

The user replaced the ambiguous “as fast as possible” wording with an explicit deadline: **reach funded status after completing both Stellar 2-Step phases in fewer than 180 calendar days**, measured from the first paid challenge attempt to successful Phase 2 completion. Future scorecards must report probability of completing both phases by day 179 before a daily/max-loss breach, plus time-to-funded quantiles. This is a research objective, not a promise of success. Until the known age eligibility date 2026-12-25, research remains simulation-only; do not advise purchasing now.

## Latest research update — R304 FX local-session depreciation — GAGAL (2026-10-19 local replay)

**R304 is closed as GAGAL.** The fixed-clock, two-module hypothesis was locked before outcomes: short EURUSD from 08:05–12:00 Europe/London and long EURUSD from 08:05–12:00 America/New_York. It was motivated by local-trading-hour return literature but was not assumed to have an edge.

Artifacts:
- [Artifact index](research/R304_INDEX.md)
- [Locked preregistration](research/R304_FX_LOCAL_SESSION_CURRENCY_DEPRECIATION_PREREGISTRATION.md)
- [Full-session range-history amendment](research/R304_DQ1_FULL_SESSION_RANGE_AMENDMENT.md)
- [Pre-outcome audit](research/R304_PREOUTCOME_AUDIT.md)
- [Final report](research/R304_FINAL_REPORT.md)
- [Normalized compact results](research/R304_results_compact.json)
- [Period/year scorecard](research/R304_period_annual_summary.csv)
- [Validation weekly bootstrap](research/R304_validation_weekly_bootstrap.json)
- [Data integrity summary](research/R304_data_audit.json)
- [Data and local-output manifest](research/R304_DATA_MANIFEST.md)

The input was existing paired EURUSD M1 BID/ASK data artifact #11959096102, ZIP SHA-256 b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e. After the registered repeated-flat filter, 3,718,698 active paired timestamps remained. The pre-outcome audit yielded 2,572 eligible module-events across 2017–2021 (2,059 discovery trades; 513 validation events). The locked screen used only discovery 2017–2020 and validation 2021. No R304 PnL was calculated for 2022–2025 or 2026.

At +1 pip incremental round-trip cost, discovery lost 42.390R with PF_R 0.926; validation lost 15.560R with PF_R 0.889. Both periods turned negative at +0.5 pip extra friction. Only one of four discovery years was positive; the validation weekly bootstrap mean was -0.29359R/week with 95% CI [-0.64112,+0.06233]R. The preregistered mirror-direction control was also negative. Only 2/11 candidate/data gates passed (minimum sample gates). **No FundedNext challenge replay was run** because the strategy gate failed; no <180-day pass probability is claimed.

**Reproducibility limitation:** normalized report and scorecards are archived; local runner and full row-level ledgers are identified by hashes in the manifest but were not verified as regular decoded files in this branch. Repository-only reproduction remains a failed gate. Do not describe R304 as funded-ready or rescue it by retuning its hours/direction on these periods.
 
## Latest batch update — R305/R306 cross-asset common-USD tests — GAGAL (2026-10-20 local replay)

**Both R305 and R306 are closed as GAGAL.** This batch tested two distinct, pre-registered mechanisms on synchronized EURUSD M1 and XAUUSD M5 paired BID/ASK data. Thresholds and trade rules were frozen before candidate outcome calculation. No 2026 XAU PnL was calculated; protected XAU 2026 remains unopened.

Artifacts:
- [Batch index](research/R305_R306_INDEX.md)
- [Preregistration R305 — common-USD impulse transmission](research/R305_EURUSD_TO_XAUUSD_USD_FACTOR_TRANSMISSION_PREREGISTRATION.md)
- [R305 threshold amendment](research/R305_DQ1_THRESHOLD_AMENDMENT.md)
- [Preregistration R306 — XAU underreaction catch-up](research/R306_EURUSD_SHOCK_XAU_UNDERREACTION_CATCHUP_PREREGISTRATION.md)
- [Pre-outcome audit](research/R305_R306_PREOUTCOME_AUDIT.md)
- [Final report](research/R305_R306_BATCH_FINAL_REPORT.md)
- [Compact JSON](research/R305_R306_batch_results_compact.json)
- [Cost/delay scorecard](research/R305_R306_cost_delay_scorecard.csv)
- [Annual scorecard](research/R305_R306_period_annual_summary.csv)
- [Input/output manifest](research/R305_R306_DATA_MANIFEST.md)

Input integrity was checked on the existing GitHub artifacts #11959096102 (EURUSD) and #12031270051 (XAUUSD). EURUSD had 4,415,493 rows/side before cutoff, 696,795 registered repeat-flat rows removed, 3,718,698 active M1 rows and 736,076 complete M5 bars. XAUUSD had 877,930 rows/side. There were 732,199 exact shared M5 timestamps. Paired timestamps were exact; no duplicate/invalid OHLC rows or negative open/close spreads were observed. Missing rows were not synthesized. Cutoff >= 2026-01-01 UTC was applied before features/events/outcomes.

At +$0.30/oz extra friction:
- R305: discovery 12,338 trades, -6,974.05R, PF_R 0.340; validation/diagnostic 2021–2025 14,201 trades, -4,486.27R, PF_R 0.536. Both periods were negative at zero added cost. Validation weekly bootstrap mean -17.1888R/week, 95% CI [-18.7661, -15.5937]R.
- R306: discovery 3,322 trades, -2,058.60R, PF_R 0.304; validation/diagnostic 2021–2025 4,004 trades, -1,398.50R, PF_R 0.497. Both periods were negative at zero added cost. Validation weekly bootstrap mean -5.3583R/week, 95% CI [-5.9689, -4.7170]R.
- Both are **GAGAL (2/8 hard gates)**. Cost stress and T+15-minute delay are also strongly negative. No alpha block is retained; no FundedNext challenge replay was run.

**Reproducibility caveat:** locked preregistrations, pre-outcome audit summary, final report, compact output and scorecards are committed. The exact local runner and row-level audit/trade CSVs are identified by hashes in the manifest but not verified as committed repository files. Repository-only reproduction remains failed; don't describe the result set as completely reproducible from GitHub alone.

The user’s concrete objective remains: complete both FundedNext Stellar 2-Step phases in **fewer than 180 calendar days** before any loss-rule breach. These failures do not estimate pass probability because no challenge replay was warranted after the strategy gates failed. The next batch must change the source of information/economic mechanism, not tune either closed rule.

## Latest research update — R307/R308 weekday drift + weekend carry batch — 2026-10-20

**R307 GAGAL; R308 GAGAL at pre-outcome DATA/SAMPLE gate.** The user asked to accelerate progress by testing more than one hypothesis per response. This batch froze both registrations first and used the existing GitHub EURUSD M1 paired BID/ASK artifact #11959096102. No GitHub Actions backtest ran. The 2026 cutoff was applied before features/outcomes.

Artifacts:
- [Batch index](research/R307_R308_INDEX.md)
- [Final report](research/R307_R308_BATCH_FINAL_REPORT.md)
- [R307 preregistration](research/R307_INTRADAY_OF_THE_WEEK_FX_DRIFT_PREREGISTRATION.md)
- [R308 preregistration](research/R308_FRIDAY_CLOSE_MONDAY_REOPEN_CARRY_PREREGISTRATION.md)
- [R308 reopen timing amendment](research/R308_DQ1_REOPEN_EXIT_CLARIFICATION.md)
- [Pre-outcome audit](research/R307_R308_PREOUTCOME_AUDIT.md)
- [R308 data/sample verdict](research/R308_DATA_ELIGIBILITY_VERDICT.md)
- [Compact results](research/R307_R308_batch_results_compact.json)
- [Cost/delay scorecard](research/R307_R308_cost_delay_scorecard.csv)
- [Annual scorecard](research/R307_period_annual_summary.csv)
- [Validation bootstrap](research/R307_validation_weekly_bootstrap.json)
- [Data/output manifest](research/R307_R308_DATA_MANIFEST.md)

Input audit: 4,415,493 paired M1 rows per side before cutoff; 0 invalid OHLC/negative-spread rows; registered filter removed 696,795 repeated flat rows; 3,718,698 active M1 and 736,076 complete M5 bars remained; 7,882 gaps >5 minutes were preserved. No bars were synthesized.

R307 shorted EURUSD Monday/Tuesday and went long Wednesday–Friday from 08:05–12:00 Europe/London, with prior-only range stop and side-correct BID/ASK execution. It generated 1,028 discovery trades and 1,281 validation/diagnostic trades. At +1 pip extra cost it lost -74.491R / PF_R 0.755 in discovery and -53.462R / PF_R 0.854 in validation. Both periods were negative at zero added costs. The 08:10 latency stress was worse; the validation weekly-bootstrap 95% CI was [-0.37108,-0.03328]R/week. Only 2/8 gates passed (data integrity and minimum sample).

R308's registered weekend-carry rule required an observed active >=24h Friday-to-Monday gap. Only two qualifying events existed in 2017–2025 (one in discovery, one in validation), both around New Year closures, not a normal weekly reopening sequence. It failed the minimum sample/data gate **before PnL**, and no outcome metrics were calculated for R308.

No FundedNext challenge replay was run: R307 failed expectancy/cost/stability gates; R308 failed data coverage. Neither has a defensible pass-probability estimate for the user's target of both phases complete before any loss-rule breach and in <180 calendar days. XAUUSD 2026 remains protected. Full row-level ledgers and the exact local runner are identified by hashes in the manifest but were not verified as ordinary decoded files in the repo, so repository-only end-to-end reproducibility remains a failed gate.


## Latest authoritative update — 2026-10-20: R309/R310

**Verdict: R309 GAGAL; R310 GAGAL. No candidate is funded-ready.** The batch tested a new EURUSD/XAUUSD relative-value residual snapback mechanism and one structural exit correction. The latter reduced losses but did not create positive expectancy, even before incremental trading costs.

- R309 baseline cost: discovery 2017–2020, 3,576 trades / -991.56R / PF 0.338; diagnostic 2021–2025, 3,665 trades / -644.44R / PF 0.512.
- R310 baseline cost: discovery, 3,003 trades / -804.58R / PF 0.553; diagnostic, 3,125 trades / -544.15R / PF 0.681.
- Both candidates were negative at zero additional costs, all annual results were negative from 2017–2025, and four-week validation-bootstrap 95% intervals were wholly negative: R309 [-2.939, -2.005]R/week; R310 [-2.578, -1.604]R/week.
- Both passed only 2/8 gates (source integrity and minimum sample count). They fail expectancy, stronger cost stress, annual stability, bootstrap, latency stress and repository-only complete reproducibility. No funded challenge replay was run.
- EURUSD data filter reproduces the manifest: 696,795 repeated flat placeholders removed; 3,718,698 active paired M1 timestamps; 736,076 complete EURUSD M5 bars; 732,199 exact common EURUSD/XAUUSD M5 timestamps. No 2026 XAU outcome rows were scored.
- Report and supporting scorecards are committed: [R309/R310 final report](research/R309_R310_BATCH_FINAL_REPORT.md), [cost/delay scorecard](research/R309_R310_cost_delay_scorecard.csv), [annual summary](research/R309_R310_annual_summary.csv), [data audit](research/R309_R310_data_audit.json), [weekly bootstrap](research/R309_R310_validation_weekly_bootstrap.json).
- Exact Python runner and full row-level trade ledgers have local hashes recorded in the R309/R310 audit context but are not yet committed as normal repository files. End-to-end repository-only reproduction remains explicitly failed; do not claim complete reproduction.

**Next-step lock:** close the exact FX/gold snapback family. No direction flip, z-threshold/beta-lookback/exit-barrier/holding-time sweep on the inspected dates. Use a genuinely distinct economic mechanism in the next generation, and do not run the protected XAUUSD 2026 window until a frozen candidate clears all pre-2026 gates. Maintain the primary criterion: both challenge phases completed before any rule breach and in fewer than 180 calendar days; that is an acceptance criterion, not a promise.


## 2026-10-20 — R311 process repair: common funded replay engine

The search-process fault was that research continued through R300–R310 even though the audit called for a common funded-path scorer before further loosely comparable tests. Infrastructure repair is committed: [R311 process repair](research/R311_PROCESS_REPAIR.md), [chronological two-phase replay engine](research/funded_challenge_simulator.py), and [eight synthetic tests](research/test_funded_challenge_simulator.py). Local test result: **8/8 passed**. The engine now has a hard project-speed gate: successful completion must be by calendar day 179; day 180 receives PASS_BOTH_PHASES_TOO_SLOW and binary_verdict=GAGAL; only completion by day 179 returns binary_verdict=LULUS. This is not a strategy backtest. The engine requires exact OPEN/MARK/EXIT paths; source-specific conservative intrabar adapters, account/platform time verification, broker execution specifications, 10,000 dependence-preserving sequential paths, and full reproducibility are still mandatory. No candidate is promoted and no challenge pass probability is claimed from this patch.


## 2026-10-20 — R312: strategy-search pause and unblock contract

**Decision: pause new strategy backtests and parameter searches.** Do not create another signal hypothesis until the real-data funded replay is reproducible.

The review separated three causes: (1) recent candidate failures include negative expectancy even at zero incremental cost, so this cannot be fixed by simulator changes alone; (2) R311's eight reported synthetic tests cover only the core challenge engine and no verified source adapter yet creates conservative chronological OPEN/MARK/EXIT events from real trades; (3) full row-level ledgers and exact runners for several recent local replays are absent as ordinary repository files, so end-to-end GitHub-only reproduction is still a failed gate.

- [R312 stop/unblock contract](research/R312_STOP_AND_UNBLOCK_20261020.md)
- R302 primary result: discovery 179 trades, PF_R 0.6398, mean -0.1842R; validation 208 trades, PF_R 0.7299, mean -0.1298R. Validation was also negative at zero added XAU cost, and a 15-minute delay worsened results. R302 remains GAGAL; the protected 2026 interval stays unopened.
- Do not describe R311 as a funded challenge pass or a pass-probability estimate. The adapter must handle conservative intrabar equity marks, side-correct execution, gaps, fees/swaps, actual platform server time and DST, and exact event-path storage before a market replay can be trusted.
- The project speed gate of completion by day 179 is a project objective; FundedNext's current public Stellar 2-Step rules state there is no firm-imposed time limit.
- Resume only after input hashes, exact runner, full row-level ledgers, source adapters and the common challenge-path contract are reproducible. Then use at least 10,000 dependence-preserving sequential paths to report both-phase completion and rule-breach probabilities.

This is an infrastructure/process decision, not a new strategy result. **No candidate is currently funded-ready.**


## 2026-10-20 — R312 implementation progress: paired-quote event adapter

- Added [paired BID/ASK-to-challenge event adapter](research/funded_path_adapter.py), [nine adapter unit tests](research/test_funded_path_adapter.py), and [XAU source integrity audit](research/R312_XAU_SOURCE_AUDIT.json) on the active research branch.
- Independently verified XAUUSD M5 archive #12031270051: source ZIP and both gzip member hashes match the R302 manifest; 877,930 exactly paired rows remain before the exclusive 2026 cutoff; no timestamp mismatches, duplicates, invalid OHLC rows, or negative open/close spreads. The 530 gaps over five minutes are preserved, never filled.
- Adapter unit tests: 9/9 passed locally. One synthetic-position smoke test over real historical quotes emitted a valid five-event OPEN/MARK/EXIT path. No strategy outcome was calculated.
- This closes only the price-path-conversion component. The adapter still needs the frozen runner ledger, broker/account costs and contract sizing, server reset verification, end-to-end replay through the shared challenge engine, and the sequential-path ensemble. **No strategy is funded-ready.**


## 2026-10-20 — R312 follow-up: Quick Strike and automatic cycle close

- Current official references: [Quick Strike is per-cycle and uses profitable trades](https://help.fundednext.com/en/articles/14702484-understanding-the-quick-strike-parameter-on-fundednext); [Stellar evaluation cycle starts at first trade, lasts 14 days, ends at 23:45 server time, with automatic closure for remaining positions](https://help.fundednext.com/en/articles/8020083-when-does-my-trading-cycle-start).
- Fixed shared simulator to score Quick Strike per 14-day cycle, not phase-wide cumulative totals. Position still open across cycle boundary without explicit closure now makes the path invalid/GAGAL, not a fabricated DLL/MLL breach. New entries at/after cycle end and end-of-path open positions are rejected.
- Paired-quote adapter now closes trades whose planned exit would overrun the cycle at the exact observed 23:45 server-time executable-side open; if the quote is absent, it fails closed. Phase-labelled ledgers get separate cycle anchors.
- Adapter session logic now permits only the observed Friday-close/Sunday-reopen closure without filling bars; unexpected weekday and nonstandard closure gaps fail closed.
- Latest verified CI run [39409091872](https://github.com/christianomomongan82-lang/scanner/actions/runs/39409091872): **12 adapter tests + 14 challenge-engine tests + 3 real-archive smoke tests = 29 total, all passing**. The Quick Strike cycle anchor now starts only at the first accepted trade, not a rejected/skipped signal.
- The exact archived XAU BID/ASK hashes match; 877,930 pre-2026 paired bars and 530 unfilled gaps >5m were verified. One synthetic trade passed through the real weekday quotes and another crossed the actual Friday/Sunday market closure with no fabricated bars. No strategy PnL was scored.
- Still outstanding: connect a frozen reproducible candidate runner/ledger; verify broker/account contract size, commission/swap, and actual platform server reset timezone; then run the rule-aware two-phase path ensemble. This CI result validates infrastructure only, not a trading edge or funded pass probability. The source artifact expires on 2027-01-14 and must be refreshed/migrated for long-term replay.


## 2026-10-20 — R312 ledger-to-account replay progress

- Added \`research/replay_funded_challenge_from_ledger.py\`, a reusable **local** normalizer/runner that turns a locked trade ledger and exact paired BID/ASK bars into OPEN/MARK/EXIT events and calls the shared funded challenge engine. It does not generate signals or tune candidates.
- Added ledger-normalization tests and same-M5-entry/exit ordering. Latest [CI run 39412962243](https://github.com/christianomomongan82-lang/scanner/actions/runs/39412962243) passed 35 tests: 14 adapter, 14 challenge engine, 4 ledger normalization, 3 real-source integration smoke tests.
- Local R298 reconstruction from the archived XAU source produced 598 trades and reproduced its headline discovery/validation counts and +$0.30/oz metrics. The local event path contains 6,364 events (598 OPEN / 5,168 MARK / 598 EXIT), with no missing five-minute grid in any trade.
- Integration-only challenge replay at 0.5% risk on the already GAGAL R298 candidate hit max loss on 2016-06-15 08:30 UTC after 26 closed trades; equity was $5,388.94 below the $5,400 static floor. This does not make R298 eligible again and does not estimate pass probability.
- [R312 ledger replay audit](research/R312_LEDGER_REPLAY_AUDIT.json) stores source hashes, counts, metrics, event-path hash and replay result.
- **Still open:** the missing R302 full row-level CSV artifacts have not been restored/committed; row-by-row identity of the reconstructed R298 ledger against the existing repo CSV is not yet byte-verified; broker/account fees and exact server-time configuration remain unverified. No strategy is funded-ready.


## Follow-up recorded 2026-10-21

The R302 ledger-storage blocker has been cleared: all four detailed CSV outputs were restored and checksum/readback verified in commit [cd42a9a4c5092ff34705d17580706b6a2ac8628f](https://github.com/christianomomongan82-lang/scanner/commit/cd42a9a4c5092ff34705d17580706b6a2ac8628f). Do not repeat the older claim that R302 outputs are still missing.

An independent local R311 reconstruction now reproduces the committed aggregate trades, net-R, PF_R, and weekly bootstrap results from the raw paired EURUSD archive with verified source hashes. R311 remains **GAGAL**. The reconstructed 2,608-row event/eligibility ledger is now committed as checksum-pinned payload fragments, with a restoration script and storage manifest. This closes the reconstructed-output storage gate; exact row-by-row comparison with the unavailable original local output remains impossible. No protected XAUUSD 2026 prices were scored; no strategy candidate is funded-ready. The remaining work is to use the restored ledger and verified account execution assumptions to resume candidate evaluation—not to repeat the storage investigation.


## 2026-10-21 — R314 discovery rejection

- Registered and ran `research/R314_XAUUSD_CLOCK_TIME_DRIFT_SEARCH_PREREGISTRATION.md`: 48 half-hour NY clock slots × two fixed directions across XAUUSD M5, discovery 2016–2020, executable BID/ASK fills, 5-minute alert-to-entry delay, +$0.30/oz primary added-cost stress, and Holm correction across all 96 discovery tests.
- **R314 = GAGAL at discovery.** None of 96 candidates satisfied the preregistered minimum of 200 trades and positive net R at +$0.30/oz. All 92 candidates with trades were net negative. The best active 10:00 NY LONG candidate had 1,290 trades, −605.866R, PF_R 0.427, weekly HAC t-stat −11.19 and Holm-adjusted p=1.0. No candidate-specific validation was run; protected XAUUSD 2026 outcomes remain unscored.
- Report: [R314 final report](research/R314_FINAL_REPORT_20261021.md); machine summary: [R314 discovery result](research/R314_DISCOVERY_RESULT.json). Full trade grid was generated locally (8,707,973-byte gzip, SHA-256 `0be5a087f8d2dc6611330fa4f41cacddf83a5f77e737d853f055726c3befdf37`); candidate table SHA-256 `95469a7098064afa63a91a6ada43d90a63d5f03e8e51b5ee8df3c48c67873243`. The compact report preserves decisive results/checksums, while the bulk discovery ledger itself remains a local run artifact rather than a committed Git blob.
- R313 remains GAGAL even at zero additional friction (validation 2021–2025 −189.1R, PF 0.51); R311 and R302 remain GAGAL. Do not invert or post-hoc filter any of these failed families.
- Current search resumes with a separately preregistered XAUUSD M5 volatility-compression breakout family; 2026 remains protected. No strategy is funded-ready.


## 2026-10-21 — R315 discovery rejection

- Registered `research/R315_XAUUSD_COMPRESSION_BREAKOUT_PREREGISTRATION.md` before the PnL run. Setup: 12-active-bar compression relative to trailing 288 observed active range values; close beyond previous 12-active-bar channel by >=0.10 × prior 12-active-bar median BID true range; entry after the five-minute manual delay; 1R stop/1.5R target; 60-minute maximum hold; quote-side BID/ASK fills.
- **R315 = GAGAL at discovery.** 1,513 qualifying signal events produced 1,280 completed trades. At zero additional cost net R was −1,102.961R; at primary +$0.30/oz cost net R was −2,254.931R and PF_R 0.0459; at +$0.50/oz net R was −3,022.912R. Win rate at primary cost 9.53%; 1,157 stops vs 122 targets. All five discovery years were negative. No candidate-specific validation was run and 2026 remains protected.
- Report: [R315 final report](research/R315_FINAL_REPORT_20261021.md); machine metrics: [R315 discovery result](research/R315_DISCOVERY_RESULT.json). Detailed compressed event/trade ledger generated locally and hashes recorded in report. The report/summary are committed; bulk ledgers are local run artifacts rather than committed Git blobs.
- R311, R313, R314 and R315 are all GAGAL; don't tune or invert failed variants post hoc. Search continues on distinct preregistered mechanisms with 2026 data held out. No strategy is funded-ready.

## 2026-10-21 — R321 causal price-relationship audit: GAGAL

- Registration: `research/R321_CAUSAL_PRICE_RELATIONSHIP_AUDIT_PREREGISTRATION.md`; runner: `research/R321_price_relationship_audit.py`; config: `research/R321_CAUSAL_PRICE_RELATIONSHIP_AUDIT_CONFIG.json`.
- Data gate: PASS on paired EURUSD M1 archive SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. Source had 4,415,493 paired M1 rows; 696,795 joint repeated-flat placeholders were removed; 3,718,698 retained rows formed 736,076 exact complete M5 bars. 7,882 gaps >5 minutes were preserved, no synthetic bars used, and all 2026 outcomes were excluded.
- Registered set: seven causal price-state/return scores × 4 forward horizons = 28 comparisons; 65-minute sample cadence; five-minute delay; observed executable BID/ASK plus +0/+0.5/+1/+1.5 pip extra-cost sensitivities; +1 pip primary.
- **Binary edge verdict: GAGAL.** Every relationship was negative at +1 pip, PF <1. The best was F6_AUTOCORR_STATE/60m over 48,879 events, mean -1.2568 pip/event, median -1.3, win rate 42.21%, PF 0.716. Even at zero incremental friction this pair was -0.2568 pip/event and PF 0.934. The four-week weekly-mean-net-pip bootstrap CI was wholly negative overall [-1.366760,-1.177065], discovery [-1.481949,-1.109147] and confirmation [-1.421008,-1.073548]. No candidate challenge replay or pass-probability calculation was performed.
- The local reconstructed calculation was run twice. Scorecard, annual/cohort table, bootstrap, data audit, compressed event ledger, and compressed zero-inclusive weekly series hashes were identical between these two runs; decompressed event and weekly series also matched the previously stored local outputs byte-for-byte. The output manifest contains path/runner-hash fields that vary with isolated-run directories.
- **Strict-v2 process gate remains OPEN.** The local reconstruction hash is `98d20b871ec149f07ca3b94df7c6d5ddace5470aae04574a8447903724a9cafb`, while the checked-in runner's current Git blob identity is `8afc5bd8b9206f4d772e585446228daa2640707b`. Although reported metrics and event rows matched, the exact checked-in runner has not itself been executed here, and all row-level outputs have not been read back from GitHub. Do not call this fully repository-reproducible.
- Reports: [R321 final report](research/R321_FINAL_REPORT_20261021.md) · [compact result JSON](research/R321_RESULTS_SUMMARY.json) · [reproduction audit](research/R321_REPRODUCTION_AUDIT_20261021.md) · [master ledger R251-R321](research/MASTER_SEARCH_LEDGER_R251_R321.csv) · [family map R251-R321](research/SEARCH_FAMILY_MAP_R251_R321.md).
- **Next action is process repair, not another signal test:** execute the byte-identical registered runner from the current branch, normalize only declared environment/path metadata, compare deterministic hashes, and satisfy the required repository output/restoration contract. Per Protocol v2, a new strategy search is blocked until this gate is closed.


## Superseding R321 process closeout — 2026-10-21

- The prior R321 status said the exact runner had not been executed and strict-v2 reproducibility was still open. **That statement is now superseded.**
- Exact runner `research/R321_price_relationship_audit.py` (Git blob `8afc5bd8b9206f4d772e585446228daa2640707b`, file SHA-256 `8647e7e8d6cedf011c8b36d7dbd773e4c35650d91cd13d196fff6fdcc207d41c`) completed two local executions with identical hashes for all eight generated outputs.
- Input source restoration passed: downloaded GitHub Actions artifact `11959096102`, source size 67,719,731 bytes, hash `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. The official artifact metadata digest matched the actual downloaded bytes. Current artifact expiry is `2027-01-13T07:11:24Z`; refresh or migrate before expiry.
- **R321 process/reproduction status = PASS; R321 signal verdict = GAGAL.** Runner, source artifact, environment, deterministic outputs and row-level ledger restoration have a verified regeneration path. See [official reproduction audit](research/R321_OFFICIAL_REPRODUCTION_AUDIT_20261021.md).
- R321 result remains unchanged: best causal state/horizon was negative even before extra friction and strongly negative at +1 pip. No funded challenge replay was run. Do not tune or reverse the family.
- New research may resume, but only under Process Protocol v2 with a distinct economic mechanism, explicit contamination declaration, and preregistration committed before any candidate PnL. Historical EURUSD 2021–2025 remains contaminated; 2026 outcomes stayed unopened. No strategy is currently funded-ready.


## Latest status — R322 closed before PnL (2026-10-21)

- **R321:** official-source reproduction PASS; edge verdict GAGAL. Exact committed runner was executed twice with identical hashes; its raw input archive hash was checked.
- **R322:** timestamp/data preflight and price/event eligibility preflight completed. Calendar timestamp repair was preregistered before signal eligibility count. Source calendar 2,828 USD-high rows audited; 1,743 rows retained, clustered to 973 episodes (359 discovery, 167 confirmation, 447 contaminated diagnostic).
- The exact committed price/event preflight runner (Git blob SHA-1 `78ae1ed35837d0bf8a93818ba9d2789f1866a4ca`) was run twice locally, with identical row-level CSV (276,071 bytes; SHA-256 `5b58b271e20c0453e241e7a6f0259c453f0b3949fe04deada38a51dc31a90edf`) and summary JSON (2,184 bytes; SHA-256 `8546f87e94e3e3241110f91165fa5aeecd620ddef6856803c5a1d776a4f09a0b`).
- **R322 = GAGAL — DATA/SAMPLE.** Only 131 discovery and 49 confirmation eligible setups before inspecting trade outcomes, against minimums of 200 and 100 completed trades. Outcome/PnL calculation was prohibited by the preregistered gate and was not performed. No PF, drawdown or pass probability is available for this test; do not infer edge from it.
- No 2026 price outcome has been calculated. EURUSD 2021-2025 is only a contaminated diagnostic period. This family is closed; do not rescue it using post-hoc parameter or calendar changes.
- Reports: [R322 preflight report](research/R322_PREFLIGHT_REPORT_20261021.md) · [machine summary](research/R322_PRICE_EVENT_ELIGIBILITY_PREFLIGHT.json) · [master ledger R251-R322](research/MASTER_SEARCH_LEDGER_R251_R322.csv) · [family map R251-R322](research/SEARCH_FAMILY_MAP_R251_R322.md).
