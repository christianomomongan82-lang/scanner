# Experiment Registration Card — Template v1

> Copy this file into a new immutable candidate preregistration before running any signal PnL. Do not edit a locked preregistration after results are seen. Corrections required for data/implementation must be timestamped in a separate amendment **before** rerunning affected outcomes.

## A. Identity and lineage

- Candidate ID:
- Date/time locked:
- Primary family ID:
- Secondary tags:
- Parent experiment IDs:
- Reusable component/block IDs:
- Candidate type: NEW_MECHANISM / STRUCTURAL_CROSSOVER / ABLATION / ROUTER / PORTFOLIO / EXECUTION_STRESS / DATA_VALIDITY
- Exact matched parent and no-filter baseline:
- Related closed candidates that must not be rescued:
- Hypothesis selection score (novelty, data readiness, phone feasibility, falsifiability, diversification, overlap penalty):
- Why this is not merely a symbol/threshold/timeframe variation of a closed hypothesis:

## B. Falsifiable hypothesis

**Claim:** [One sentence stating the conditional return behavior expected.]

**Market mechanism:** [Why the behavior might exist; distinguish economic explanation from chart description.]

**Expected edge condition:** [Exact event/context definition, measurable from data available at signal time.]

**Direction and trigger:** [Exact formula/logic; include feature lookback and when each input becomes available.]

**Falsification criteria:** [What observable outcome would refute the claim.]

**Known alternatives/confounds:** [Session effect, volatility regime, instrument correlation, survivorship, data artifacts, selection bias.]

## C. Immutable trade rules

- Instruments/universe and selection rule:
- Timeframe/session/calendar/timezone/DST:
- Signal conditions:
- Long/short direction:
- De-duplication / max trades per day:
- Entry quote/time:
- Baseline manual delay: five minutes **after signal close**, using the first valid observed executable quote thereafter.
- Delay stress:
- Stop:
- Target:
- Maximum holding/session exit:
- Open-gap fill:
- Same-bar SL/TP collision:
- Overlapping position / risk-cap skip:
- Size/risk rule (predeclared; same for parent and child):
- Any rule not fully specified above invalidates the preregistration.

## D. Data contract — must pass before PnL

- Source/feed and artifact ID:
- File paths, SHA-256 hashes, row counts:
- Date range requested / present / included:
- Quote sides available: BID / ASK / BID-only / other:
- Time coverage, missing/duplicate/invalid row counts:
- Closed-market/static/synthetic-row policy:
- Missing bars: leave missing; no silent forward-fill:
- Cross-instrument joins: exact timestamps only:
- Required event coverage and expected active-branch rate:
- Pre-outcome eligibility checks:
- Data risks that prevent promotion:
- Reproduction: runner + config + inputs + command committed? YES/NO

If any required timestamp, quote side, coverage or provenance requirement fails, verdict the specified research claim **GAGAL — DATA/IMPLEMENTATION**, and explicitly say this is not evidence that the economic idea itself has no edge.

## E. Frozen periods and contamination declaration

- Calibration-only period:
- Discovery period:
- Validation period:
- Forward diagnostic period:
- Protected final holdout (instrument × period):
- All periods already inspected in this family or adjacent families:
- Number of variants/candidates previously tried using any overlapping dates:
- Program-level contamination assessment:
- Rule for opening the protected holdout:
- Who/what can access holdout outcomes before the candidate is frozen:

Important: 2022–2025 is already contaminated at project level for many FX and index families. EURUSD 2026 has also been inspected by several rounds. XAUUSD 2026 is reserved in existing reports and may only be used once by a single frozen candidate after all predeclared gates pass. Do not call a repeatedly inspected period untouched OOS.

## F. Execution and cost model

- Primary execution model:
- Observed quote-side spread:
- Commission/fee source:
- Slippage source or stress:
- Swap/overnight costs:
- Primary incremental cost case:
- Cost-stress cases:
- Why these assumptions are executable for the intended account:
- Unverified provider/account items:

Default research stresses unless a pre-outcome rationale says otherwise:
- FX BID/ASK: +0 / +0.5 / +1 / +2 pips per round trip.
- XAUUSD BID/ASK: +$0 / +$0.10 / +$0.30 / +$0.50 per ounce per round trip.
- Index BID-only screen: +2 / +4 / +6 price bps per round trip. A BID-only index result is a research screen, not fully executable-side evidence.

## G. Preregistered signal gates

Use the common scoring contract unless a justified amendment is committed **before PnL**.

| Gate | Predeclared minimum | Result |
|---|---|---|
| Data and executable-event integrity | All required checks pass | |
| Discovery trades | >=200 preferred/common screen; low-frequency exemption must specify longer independent horizon and still cannot pass without adequate evidence | |
| Validation trades | >=100 preferred; do not waive evidence solely because the point PF looks good | |
| Discovery expectancy | Net R > 0 at primary cost | |
| Validation expectancy | Net R > 0 at primary cost | |
| Discovery PF | >=1.05 at primary cost | |
| Validation PF | >=1.05 at primary cost | |
| Cost robustness | Net R > 0 and PF >=1.00 at registered stress | |
| Year stability | >=3 of 4 discovery years positive, or predeclared equivalent | |
| Bootstrap | 95% lower bound for validation mean weekly net R > 0 | |
| Delay feasibility | Positive/stable after the declared phone-delay stress | |
| Sample / feature coverage | No unreachable router branch or unexplained zero-trade period | |
| Reproducibility | Exact inputs, rules, runner, ledger and JSON saved on GitHub | |

These are initial historical research gates; they are not a promise of profitability or funded readiness. If a gate fails, the locked candidate is GAGAL. Do not change the rule and relabel it as the same experiment.

## H. Component, crossover and portfolio gates

Complete this section for any filter, router, crossover or combined stream:

- Parent A results on matched events:
- Parent B results on matched events:
- Child/integrated stream results:
- No-filter / naive baseline:
- Ablation removing each added block:
- Events added/removed and return profile of removed subset:
- Each router branch activation rate:
- Correlation and overlap of simultaneous/open positions:
- Incremental net R and opportunity frequency:
- Contribution to phase-pass probability and time-to-target:
- Does the child improve the objective without unacceptable breach/cost/delay deterioration? Exact predeclared test:

A combination of negative components is not assumed useful. A positive point estimate relative to a losing parent is not a positive edge. An unreachable module invalidates the claimed multi-module architecture.

## I. Challenge replay — only after signal gates pass

Use the actual current provider rules, verified before simulation.

- Initial/phase balance:
- Phase 1 target (+8% reference):
- Phase 2 target (+5% reference):
- Daily-loss definition and server-day reset:
- Static/relative maximum-loss definition:
- Intratrade floating equity:
- Minimum trading days and permitted add-ons:
- Quick Strike or holding-time constraints:
- Server timezone/DST:
- Commission/slippage/swaps:
- Fixed risk grid and shared portfolio cap:
- Compounding convention:
- Correlated/overlapping-position policy:
- Number of chronological/cluster-preserving paths:
- P(Phase 1 pass before breach):
- P(Phase 2 pass conditional on Phase 1):
- P(both phases complete):
- P(daily/max-loss breach):
- Median / 90th / 95th percentile time-to-target:
- Failure modes and confidence interval:
- What elements remain proxy-only:

Do not call a closed-equity-only or UTC-day proxy a provider-equivalent challenge replay. A challenge replay does not repair failed signal expectancy.

## J. Final immutable verdict

- **Binary verdict:** LULUS / GAGAL
- Failure subtype if GAGAL: DATA / IMPLEMENTATION / EXPECTANCY / COST / INSTABILITY / SAMPLE / LATENCY / PORTFOLIO_CONTRIBUTION / CHALLENGE_BREACH / REPRODUCIBILITY
- Gate-by-gate result table:
- Main evidence:
- What was learned:
- Reusable blocks (only if contribution is separately supported):
- Closed blocks that may not be tuned on the same sample:
- Artifacts committed: preregistration, data manifest, runner, config, event audit, trade ledger, results JSON, bootstrap series, report:
- Updated master ledger row:
- Updated project checkpoint link:

## K. Run integrity log

| Timestamp | Action | Input/output hash | Was candidate PnL visible? | Notes |
|---|---|---|---|---|
| | Preregistration committed | | NO | |
| | Data-only eligibility audit | | NO | |
| | First locked PnL run | | YES | |
| | Final report / binary verdict | | YES | |

No GitHub Actions backtest. Raw data may be acquired/stored on GitHub; signal generation, replay, statistics and verdict calculation run in local Python/container.
