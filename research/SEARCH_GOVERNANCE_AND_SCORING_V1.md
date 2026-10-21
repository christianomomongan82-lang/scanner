> **Superseded notice — 2026-10-21:** New experiments must follow [Search Process Improvement Protocol v2](SEARCH_PROCESS_IMPROVEMENT_PROTOCOL_V2.md) and [Experiment Registration Card Template v2](EXPERIMENT_REGISTRATION_CARD_TEMPLATE_V2.md). V2 is stricter and authoritative for preregistration timing, maximum grid size, reproducibility gates, complete artifact archiving and stopping search on a process regression. This v1 file is retained as historical governance, not the highest-priority contract.

# Search Governance and Scoring Contract v1

Effective: 2026-10-18  
Scope: audited experiments R251–R299; supplements existing `EVOLUTIONARY_METHOD_COMPOUNDING_20261016.md` and `PRIMARY_OBJECTIVE_FUNDED_TARGET_COMPLETION_20261016.md`.

## 1. The actual objective

The system is selected for the **probability of completing both funded phases before breaching risk rules, and the time-to-completion distribution**. The reference challenge currently documented by the project is $6,000, +8% Phase 1, then +5% Phase 2. Official rules, eligibility, platform time mapping and checkout terms must be verified again before any real purchase or live claim. Until eligibility, this project remains research-only.

PF is a diagnostic—not the search target. Do not select a strategy solely because it has the highest PF, highest trade frequency, highest historical return, or a lucky single-path target hit.

## 2. Current result from the ledger

- The audited ledger has **47 experiment records across R251–R299**, excluding R259 (recorded workflow incident, explicitly not an accepted backtest) and R267 (no independently verified research report surfaced in this audit).
- No candidate in this audited set is approved for funded use. R276 had a historical statistical screen pass but was explicitly not promoted because funded-rule replay and later diagnostic support were insufficient.
- The database shows breadth across FX momentum, reversals, sessions, range breakouts, cross-pair/cross-index relationships, index intraday/opening behavior, overnight carry, XAU price-action setups, and portfolio/router combinations. The main fault is not lack of named strategies: it is repeated exposure to similar assets/data/windows, uneven cost units, and failure to translate signal evidence into a consistent challenge-completion scorecard.
- The exact original R189 M1 history/ledger is not reproduced from the current repository. R189 OOS 2026 results and later Dukascopy replays are separate evidence and must never be presented as the original historical reproduction.

## 3. Family and lineage rules

Every experiment must have:
- a unique immutable ID;
- one primary mechanism-family ID and any secondary tags;
- parent experiment IDs, reusable block IDs, and matched-baseline ID;
- a one-sentence causal/economic hypothesis;
- explicit mutation/crossover and why previous evidence motivates it;
- a declaration of whether it is a new family, a structural mutation, an execution test, a data-quality test, an ablation, or a portfolio-composition test.

Changing symbol, threshold, timeframe, target, or session window alone does **not** automatically make a hypothesis independent. Shared signal logic, data source, price behavior and selection windows must be recorded. An experiment may compare several instruments as a predeclared universe but may not choose the winning instrument after viewing PnL unless that selection is inside a nested development split.

### Primary family taxonomy

| Family ID | Mechanism | Audited coverage | Search rule |
|---|---|---|---|
| FX_TREND_MOMENTUM | FX directional momentum, trend breakout, pullback continuation | R252, R256–R258, R262, R271 | Broadly explored; don't create another lookback/threshold-only child. A future test needs a distinct economic mechanism or an independently justified context interaction. |
| FX_REVERSION_SWEEP | FX shock fade, failed break, rolling extreme sweep/reclaim | R254–R255, R260, R269 | Exact tested variants are closed. Do not treat all reversal hypotheses as disproved, but require a mechanism distinct from changing extreme thresholds. |
| FX_SESSION_RANGE_ROUTER | FX Asian/London range breakout, session impulse, regime router | R253–R254, R257, R261, R269–R270 | Prioritize feature coverage/reachability tests before PnL; don't accept a router whose branch is unreachable or whose active module is already negative. |
| FX_CROSS_PAIR | Cross-pair lead-lag / consensus | R251 | The registered EUR/GBP catch-up hypothesis failed OOS and cost stress. A new cross-pair idea must be a different causal mechanism, not a window/threshold repair. |
| US_INDEX_CASH_OPEN | US-index opening-range breakout, gap fade, retest, breadth, same-day variants | R263–R264, R276–R280, R283–R286, R290 | **Saturated for near-duplicate screening.** Pause new cash-open ORB/gap/target/timing variants until a genuinely different source of edge is justified. |
| INDEX_CROSS_SECTIONAL | US index breadth, residual follow/fade, relative value, leader/follower and cross-session links | R265, R276–R280, R287–R288, R291, R299 | High overlap in instruments and data. Any next candidate needs a distinct market mechanism, exact timestamp pairing, and matched parent/child ablation. |
| US_INDEX_OVERNIGHT | Overnight carry and breadth-conditioned carry | R292–R295 | Close this registered family. Positive point estimates are not enough when bootstrap uncertainty, cost stress or floating drawdown fails. |
| US_INDEX_INTRADAY_DRIFT | Late-morning impulse, calendar effect, afternoon drift, overextension | R284–R286, R266 | Multiple time-window variants are already tested; don't relaunch the same directional drift family with new clock cutoffs. |
| XAU_PRICE_ACTION | Gold impulse/pullback, reopening gap, Asian sweep and two-module router | R272–R274, R297–R298 | Tested variants are closed. The reserved 2026 XAU segment may only be opened once for a preregistered final test after a single candidate clears predeclared historical/data gates. Do not use it to breed more variants. |
| PORTFOLIO_ROUTING | Integrating previously tested streams, regime routing, fixed-fractional replay | R268, R270, R272 | A combination of losing or unreachable modules is not evolutionary improvement. Compare standalone blocks, matched baseline, ablation and integrated stream with identical timestamps, costs and shared risk limits. |
| DATA_OR_EXECUTION_VALIDITY | Feed coverage, quote sides, exact delay, active market rows, reproducibility | R257, R259 incident, R281–R282, R296–R297, R265/R268 provenance caveats | This is a validity gate, not an alpha family. Failed data tests must not be reported as evidence of positive or negative alpha. |

### Family-level stop rule

The cash-open index variants are exhausted as a near-duplicate search area. The exact FX variants listed above remain closed. New search effort should target a **mechanism not yet adequately represented**, and the reason for choosing it must be written before computing candidate PnL. The point is not to give an untested family a free pass; it must pass the same validation contract.

## 4. Data and execution contract

Before calculating strategy PnL:
1. Record data provider/source, symbol mapping, requested and actual timestamp range, timezone and DST convention, quote side (BID/ASK), file hash, row counts, duplicate/invalid checks, missing-bar policy and synthetic/closed-market-row policy.
2. Verify event coverage and execution eligibility without using outcome PnL. Any router branch must have attainable conditions under the fitted threshold; report branch activation rates and skipped-signal reasons.
3. Preserve missing bars. Do not forward-fill or synthesize tradable OHLC. Use exact timestamps for cross-instrument joins; never pair rows by row number.
4. Entry occurs at the **first valid observed executable quote after the declared manual reaction delay**, not a convenient substituted bar. For M5 signals, baseline execution is five minutes after the signal bar has closed (typically signal-bar timestamp +10 minutes). For other timeframes, measure delay from the actual signal close, not by hard-coded timestamp arithmetic.
5. Use ASK to enter long / exit short and BID to exit long / enter short when quote-side data exist. If only BID exists, identify the backtest as a cost-sensitivity screen, not a fully executable replay.
6. Define same-bar stop/target collision, gap-through-stop fill, stop validity, maximum hold, session end, overlapping positions and position-skip rules before outcome calculation.
7. Record whether the run is fully reproducible from committed code + exact data + parameter file + ledger. Missing input ledgers/data is a reproducibility failure even if a summary report exists.

### Cost convention

Costs must be asset-specific at the quote level and expressed in a common risk-normalized outcome after fills:
- FX with paired quote sides: observed BID/ASK execution plus predeclared extra-cost stresses (default report grid: +0, +0.5, +1, +2 pips per round trip).
- XAUUSD with paired quote sides: observed BID/ASK execution plus +$0, +$0.10, +$0.30, +$0.50 per ounce per round trip.
- Index CFD BID-only history: report explicitly labeled modeled notional-basis-point stresses (default grid +2/+4/+6 bp). Such results cannot establish actual spread-adjusted promotion without a verified executable-side/cost source.
- Do not compare raw pips, raw basis points, dollars-per-ounce, PF, or R values as though the quantities are interchangeable. Within a candidate, all relevant output must include net R/trade; then use the same portfolio-risk and account-equity engine for cross-candidate comparisons.
- Any future broker/funded cost settings must be verified before a candidate can be called funded-ready; these stress grids are research conventions, not claims about live costs.

## 5. Chronological integrity

### Already exposed or contaminated at project level
- **US equity-index families:** 2017–2021 was used repeatedly, and 2022–2026 has been inspected by several exploratory/diagnostic rounds. Those years are development diagnostics, not a pristine global holdout.
- **EURUSD FX:** 2021, 2022–2025 and much of 2026 have been inspected in several FX rounds. Do not label these as untouched program-level OOS.
- **XAUUSD:** many 2016–2025 variants have been tested, but the reports for R272/R297/R298 say 2026 outcome PnL remained unopened. A final 2026 XAU test may be reserved only if the proposed candidate is frozen before any 2026 outcome is computed and only one designated candidate is tested on this period. This is a protected, limited holdout—not another development period.
- **Cross-market/cross-index:** has program-level exposure from multiple related experiments; same historical window is not independent simply because the second symbol differs.

If a family has no genuinely independent historical window, report historical metrics as development evidence only. Use a locked forward/paper period or a one-time protected instrument-period holdout for promotion evidence. Do not reuse that period to breed descendants.

## 6. Standard decision gates

Every registered experiment receives a binary final verdict **LULUS** or **GAGAL** under the project rules. Use failure subtypes for diagnosis (data/implementation, negative expectancy, low sample, cost-sensitive, unstable, execution-infeasible, portfolio contribution negative, challenge-rule breach). A test with invalid or missing required data is GAGAL for the specified research claim, but must be explicitly labeled “data/implementation failure—not evidence that the market edge is absent.”

### Gate A — data eligibility (before PnL)
- All data-quality checks pass and event/branch coverage is measured.
- No invalid timestamp alignment, synthetic tradable bars, missing required entry/exit quotes, look-ahead, or unregistered substitution.
- Exact runner, parameter config and data hashes are committed or the test fails reproducibility.
- If this gate fails, do not interpret PF or declare economic evidence.

### Gate B — signal economics (on frozen partitions)
Use the predeclared primary cost and a separately registered cost-stress case. Default historical research screen:
- At least 100 completed trades in discovery and 50 in validation for an initial screen; fewer trades may be recorded as a low-frequency hypothesis but **cannot pass the evidence gate** without a justified longer independent sample.
- Net R > 0 and PF >= 1.05 at primary cost in both discovery and validation.
- Net R remains > 0 and PF >= 1.00 at the registered stress cost; for BID-only index screens, stressed PF alone does not fix the missing executable-side evidence.
- Positive results in at least 3/4 discovery years (or the equivalent predeclared share if the period length differs). A single outlier year must be called out.
- Validation weekly block-bootstrap 95% lower confidence bound for mean net R must be >0. If event count or the number of nonzero weeks is too low for meaningful inference, classify the candidate GAGAL for promotion due insufficient evidence.
- Report PF, net R, mean/median R, trade count/frequency, holding distribution, drawdown in R, losing streak, yearly/quarterly cohorts, skip audit and cost sensitivity. A gate cannot be waived after seeing results.

These gates are an **initial research screen**, not a guarantee of profitability or sufficient proof by themselves. They are stricter/consistent defaults replacing the previous habit of changing sample-count and cost gates from one experiment to another. Any change must be registered before the next candidate is run, with a rationale that does not reference the candidate's outcome.

### Gate C — contribution to the system
For any router, filter, crossover, or portfolio child:
- Compare parents, each component, child, no-filter/naive baseline, and ablation on identical eligible timestamps and costs.
- Report branch reachability, signals removed/added, retained trade count, overlap/correlation, net R, expectancy, loss clustering and contribution to both phase pass odds/time.
- An added block must improve the predefined portfolio objective or offer a measurable diversification benefit without causing unacceptable deterioration in cost robustness, trade opportunity or breach probability.
- “Better PF than parent” does not pass if both parent and child are negative; a filter that removes near-zero events is redundant unless its contribution appears in out-of-sample results.

### Gate D — two-phase challenge replay (only after A–C)
Use the confirmed provider rule implementation and chronological combined event stream, never isolated trades or only a daily closed-equity proxy:
- Model target sequence (+8% then +5% for the current reference case), daily loss, static maximum loss, minimum trading days, reset rules/timezone/DST, activity/inactivity and any duration-based constraint that applies.
- Track open and closed equity, simultaneous positions, risk stacking and correlated exposure. A closed-only equity replay cannot certify daily/max loss survival.
- Use actual platform execution time mapping, BID/ASK or verified spread approximation, commissions, slippage, swaps and manual delay; declare every unverified item.
- Predeclare a risk grid and portfolio cap. Score target completion probability, both-phase completion probability, loss-rule breach probability, median and 90th/95th percentile time-to-target, longest losing sequence and cost/delay robustness across repeated chronological/block-bootstrap paths.
- Select on a risk-aware Pareto frontier, not a single PF or a high-risk lottery. Report target-hit odds alongside breach odds.
- Only a passed challenge replay can be labeled funded-ready. This is distinct from a historical signal-screen pass.

## 7. Candidate ranking before each new test

Score the **proposed hypothesis before calculating its PnL** on a 0–3 scale for each:
- Mechanism novelty relative to closed families;
- Data/executable-side readiness;
- Suitability for five-minute manual execution;
- Ability to test a falsifiable statement without a broad parameter sweep;
- Potential to complement existing behavior rather than duplicate it.

Subtract 0–3 for overlap with already-tested mechanisms and for dependence on contaminated periods. Scores document the choice; they must never replace the hard gates or justify keeping a bad result. The candidate with the highest score is not automatically accepted—its preregistration must state the hypothesis and an exact binary gate.

## 8. Required saved artifacts for every next-generation candidate

1. Immutable preregistration and configuration.
2. Input manifest, hashes, time coverage and data-quality audit.
3. Exact local runner, environment/library versions and run command.
4. Signal/branch-eligibility audit before outcomes.
5. Full chronological trade ledger and skip/rejection audit.
6. Machine-readable result JSON, annual/cohort tables, cost/delay stress, block-bootstrap series and gate table.
7. Parent-child and ablation comparison when relevant.
8. Result report with binary verdict and explicit limits.
9. Update to the master ledger and family map.
10. Update to the project checkpoint.

Do not dispatch GitHub Actions to calculate backtests. Use GitHub as source storage and report versioning; execute calculations in the local Python/container session.
