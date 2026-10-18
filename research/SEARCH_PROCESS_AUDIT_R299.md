# Search-Process Audit — R276–R299
Date: 2026-10-18
Branch: `local-backtest/r189-dukascopy-history`

## Executive verdict

**The search was diversified across multiple hypotheses; it was not simply one strategy being forced to work. The weak point is how the search is organized and how evidence is compared.** The audited reports show several genuinely different mechanisms, but also clusters of closely related variants built on the same US index M5 data and the same repeatedly examined historical periods. A few tests produced relative improvement without establishing positive edge. Several promising-looking results failed robustness, cost, or later-period checks.

No audited candidate is currently established as funded-ready. This is not a claim that no edge exists anywhere; it is a claim that the available evidence does not yet justify promotion.

## 1. Coverage map

| Research family | Reports reviewed | What was actually tested | Audit finding |
|---|---|---|---|
| US cash-open breakout / breadth / execution timing | R276–R280, R283–R286, R290 | Synchronized multi-index breakout, long-only breadth, Nasdaq lead-lag, gap fade, late-morning impulse, turn-of-month, three-session overextension, breakout retest | A real family of variants was explored, including meaningful structural changes. Most fail discovery or robustness gates. R276 passed a historical screen but was not promoted because funded-equity replay was absent, later diagnostic performance was negative, and holding time could be excessive. |
| Cross-index residual / cross-market lead-lag | R287–R288, R291, R299 | Fade/follow index residuals; US cash-session lead to German session; USATECH impulse predicting USA500 follow-through | Several different hypotheses, but many rely on shared equity-index directional behavior and the same BID-only index archives. R287 fade was strongly negative; following the residual was better relative to fading but was not itself robust. R291 and R299 were negative after costs. |
| Overnight US500 carry / breadth filter | R292–R295 | Unconditional overnight long, positive-tail breadth filter, bearish mirror, own-session confirmation | This is one experiment family with useful matched comparisons. R293 improved PF and drawdown relative to its parent, but produced lower total net return and failed the validation bootstrap. R294's bearish mirror damaged results. R295 removed only five discovery trades and zero validation trades, demonstrating a redundant filter rather than a new source of edge. |
| European cash-open gap continuation | R289 | Follow unusual gaps in DEUIDXEUR, FRAIDXEUR, EUSIDXEUR | One of the stronger historical point estimates, but the validation weekly-bootstrap interval crossed zero. A report also notes positive validation R alongside negative net notional return; the normalization needs reconciliation before any ranking or portfolio use. Not promoted. |
| EURUSD intraday compression / weekend reopening | R281–R282; execution-delay stress R275 | H1 compression-release breakout; Sunday reopening gap fade; phone-delay effect on an older EURUSD setup | R281 discovery was materially negative and validation trade counts were too low. R282 is an invalid/inadequate-data test, not evidence for or against gap-fade alpha. R275 shows the specified phone delay worsened its tested parent; it does not establish a new signal family. |
| XAUUSD momentum, impulse, reopening gap, and London reversal | R273–R274, R297–R298 | Aligned pullback continuation, decisive-candle impulse follow-through, weekend-gap continuation, Asian-range sweep/reclaim | These are distinct price-action hypotheses, not merely one parameter sweep. The tested versions were negative or too weak. R297 had only 24 discovery and 28 validation trades, poor discovery PF, and fragile validation. R298 was strongly negative in both periods, including with no added cost. |
| Data-inadequate test | R282; earlier invalid reopening observations corrected in R297 | EURUSD weekend-gap detection and XAU reopening event time | A critical distinction: invalid data tests must not be counted as failed alpha tests. R282 found zero tradable events because the collection method removed required reopening data. R296's static Sunday quote issue was corrected in R297; only R297 is valid evidence for that specified XAU setup. |

## 2. What the numbers show

- **A relative improvement is not necessarily a tradable edge.** R293's breadth filter improved PF versus the unconditional parent at modeled 2 bp, but total net bps fell and the bootstrap lower bound crossed zero. R295's extra confirmation was nearly redundant and even discarded a profitable subset in discovery.
- **There are results with positive point estimates, but too much uncertainty or instability.** R289's validation bootstrap includes zero. R292 has positive discovery/validation point estimates at 2 bp but its weekly bootstrap includes zero, discovery drawdown reached 38.57% of fixed notional, and discovery PF falls to about 1.00 at 4 bp.
- **A favorable later window cannot repair broad earlier losses.** R278–R280 and R284 show positive results in 2022–2025 for some variants, but the reports explicitly classify that period as previously inspected/contaminated at program level; their discovery gates fail and 2026 diagnostic behavior is poor.
- **The XAU failures are not all one repeated setup.** R273, R274, R297 and R298 test different mechanisms. Their results provide evidence against those exact registered versions, not proof that every possible XAU edge is absent.
- **Trade count alone is not the obstacle.** Some candidates have hundreds of trades and still show negative expectancy after costs (for example R298 and R299). More signals do not repair a negative conditional expectation.

## 3. The main process failures

### A. No clean program-level holdout remains in the audited research
Many tests reuse discovery 2017–2020 and validation 2021. Other experiments use 2016–2020 versus 2021–2025, while multiple index studies have already inspected 2022–2025 and/or 2026 as exploratory or diagnostic data. Even when a single test is preregistered properly, repeated strategy selection after seeing neighboring experiments makes those same later years no longer pristine at the overall-program level.

**Effect:** the individual test's locked gates are useful, but their nominal confidence levels do not fully account for how many related hypotheses have already been tried on the same market history.

### B. Cost and outcome units are not standardized
The reports mix R-based outcomes, basis points of index notional, pips, and dollar-per-ounce cost stresses. Several equity-index tests use BID-only M5 snapshots with modeled 1/2/4 bp deductions; gold tests use paired BID/ASK with additional $/oz stress; FX uses pips and quote-side execution. Those are useful within a study, but they cannot be ranked as if one unit meant the same economic risk across studies.

R289 explicitly reports positive validation net R alongside negative net notional return. That may arise from different normalizations, but it must be reconciled rather than ignored.

**Effect:** it is hard to answer the actual cross-candidate question: which method contributes the most realistic chance of passing the challenge per calendar month, after realistic costs and account rules?

### C. Edge tests are separated from the user's funded objective
The reports usually stop after a statistical gate fails, so they correctly avoid promoting weak signals. However, even R276—which passed its historical screen—was not replayed through the full two-phase challenge equity path. Daily loss, static max loss, floating equity, clustered exposure, contract sizing, swaps, and time-to-target have not been consistently compared across candidates.

**Effect:** we have been screening signal statistics, not yet measuring the ultimate product we need: probability and time to reach +8%, survive the loss limits, then reach +5%.

### D. Related hypotheses sometimes look more independent than they are
R276–R280 and R283–R286 are numerous experiments, but many still draw from US equity-index cash-session behavior, the same M5 feeds, similar entry delays, and shared annual partitions. R292–R295 are explicitly one overnight-carry family. R287–R291 and R299 also draw on cross-index or cross-session relationships.

That is not wrong by itself. The issue is that **the experiment ledger needs to tag shared mechanisms and data**, so ten variations from one family do not create the illusion of ten independent sources of edge.

### E. Data quality and execution realism still limit promotion
A number of reports flag BID-only inputs, heuristic flat-row filtering, modeled rather than broker-verified costs, and no tick-level resolution of stop/target ordering. R282 is an outright data-inadequate test. Positive results under these limitations require more validation, not promotion.

## 4. What the search has learned

1. **Do not keep tuning the already-closed candidates** R273–R275, R277–R295, R297–R299 just to turn a failed report green. Their registered hypotheses remain closed.
2. **Do not count R282 as evidence against the gap-fade mechanism**, because the required events were missing in its data source.
3. **Retain implementation lessons, not failed alpha blocks:** exact timestamps, no forward-fill, pre-outcome data amendments, matched-parent ablations, cost stress, and blocked weekly bootstrap.
4. **The next experiment should be chosen for mechanism novelty, execution feasibility, and information gain**—not just because another parameter variation is easy to run.
5. **Any future candidate must be evaluated in one common economic unit and eventually pass an equity-aware challenge replay.** Better PF alone is insufficient; the final ranking must prioritize probability of reaching the target without breaching daily or maximum loss, and time-to-target.

## 5. Audit decision and next step

**Decision: pause new candidate generation until the experiment ledger and common scoring contract are in place.** This is not a pause in the whole project; it is a stop against launching another loosely comparable strategy test.

The next research-generation step should be:

1. Create a compact master ledger of every accessible R-series report with fields for mechanism family, parent, instruments/data source, in-sample/validation periods already viewed, execution assumptions, cost unit, trade count, net outcome, uncertainty, hard-gate result, and whether funded-path replay exists.
2. Mark all already-viewed dates as contaminated for program selection; do not describe 2022–2026 as a pristine holdout in a new study.
3. Standardize costs and per-trade risk for the instruments actually eligible on the intended funded account. Separate strategy screening from final challenge simulation, but make the latter mandatory before a candidate is called ready.
4. Only then select a genuinely under-covered mechanism—or deliberately stop if the evidence says the existing data cannot test it correctly.

## Evidence links

- [R276 — breadth router, historical screen pass but not promoted](R276_FINAL_REPORT.md)
- [R278 — long-only breadth router](R278_FINAL_REPORT.md)
- [R280 — Nasdaq-led breakout follow-through](R280_FINAL_REPORT.md)
- [R281 — EURUSD H1 compression-release](R281_FINAL_REPORT.md)
- [R282 — invalid EURUSD weekend-gap data](R282_FINAL_REPORT.md)
- [R289 — European cash-open gap continuation](R289_FINAL_REPORT.md)
- [R292 — US500 overnight carry](R292_FINAL_REPORT.md)
- [R293 — breadth-filtered carry](R293_FINAL_REPORT.md)
- [R295 — redundant own-session filter](R295_FINAL_REPORT.md)
- [R297 — corrected XAU reopening-gap continuation](R297_FINAL_REPORT.md)
- [R298 — XAU London sweep-and-reclaim](R298_FINAL_REPORT.md)
- [R299 — USATECH leads USA500](R299_FINAL_REPORT.md)
