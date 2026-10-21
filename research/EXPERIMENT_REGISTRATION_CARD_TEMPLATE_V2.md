# Experiment Registration Card — Template v2 (mandatory)

**Copy and fill this before any candidate PnL. Commit the completed card and JSON config to GitHub first.** V2 supersedes the older template where stricter.

## A. Immutable identity and lineage
- Experiment ID and UTC lock time:
- Family ID; novelty check against MASTER_SEARCH_LEDGER_R251_R320.csv and SEARCH_FAMILY_MAP:
- Parent/related/closed experiment IDs:
- Type: NEW_MECHANISM / STRUCTURAL_CROSSOVER / ABLATION / PORTFOLIO / EXECUTION / DATA_VALIDITY:
- Exact reason this is not just a symbol/threshold/timeframe/stop/target mutation:
- Preregistration commit SHA and UTC time (must precede first PnL computation):
- Source runner commit SHA:
- Candidate grid/config SHA-256:
- Expected artifacts and reproduction command:

## B. Falsifiable mechanism
- One-sentence conditional return claim:
- Economic/market mechanism (not just a chart pattern):
- Signal-time information available:
- Exact trigger/direction formulas:
- Falsifying outcomes:
- Known confounds and alternative explanations:
- Prior lessons incorporated from failed families:

## C. Search size and selection rule
- Number of registered configurations (default <=100):
- If >100, separate pre-outcome justification, nested selection design and multiple-testing correction:
- Ranking metric and tie-break, based only on the permitted discovery partition:
- Minimum discovery/validation sample sizes:
- Exact candidates to freeze for confirmation; no post-hoc expansion:
- Statistical/multiple-testing adjustment:

## D. Immutable trade/execution rules
- Instruments and selection rule:
- Timeframe, timestamp convention, timezone, DST, session/calendar:
- Signal formula and lookback:
- Entry exact quote/time; side-correct bid/ask fill:
- Delay measured from signal close; primary manual delay and delay stress:
- SL/TP; gap fill; same-bar ambiguity:
- Maximum hold and exit rule:
- Position overlap/correlation/risk cap:
- Spread ceiling, commission, swap, slippage and stress grid:
- Exact position sizing and maximum aggregate risk:
- Any unspecified rule blocks preregistration.

## E. Data provenance and eligibility
- Provider, artifact ID, member paths, source/cleaned-data SHA-256:
- Requested/available/included UTC date ranges and exclusive cutoffs:
- BID/ASK pairing rules and spread diagnostics:
- Duplicate/invalid/static/repeated-flat counts:
- Missing-gap policy (never synthesize bars):
- Exact bar completeness rule after resampling:
- Feature-lookback reset rule at gaps:
- Pre-outcome event/eligibility/skip audit plan:
- Period split with contamination declaration:
- Protected holdout and exact unlock conditions:

## F. Frozen economic gates
- Primary incremental friction and separate cost stresses:
- Discovery: minimum count, net R, PF, year stability:
- Confirmation/validation: minimum count, net R, PF:
- Bootstrap series, block length, repetitions and fixed seed:
- Cost robustness gate:
- Manual delay/holding-feasibility gate:
- Maximum drawdown / loss-streak gate:
- Every required gate is binary and frozen before outcomes.
- Overall verdict rule: any required gate fails => GAGAL.

## G. Data and implementation gates — no PnL until passed
- Exact source hash checked locally:
- Clean data hash and row-count report:
- No look-ahead test:
- Timestamp alignment/gap test:
- Executable side/fill test:
- Intrabar collision and gap-fill tests:
- Entry delay exact timestamp test:
- Determinism/seed test:
- Source runner committed/read-back-verified:
- Environment/library versions pinned:
- Local preflight test log and SHA-256:

## H. Required final package (all must be committed/read-back-verified)
- [ ] Immutable registration markdown + JSON/config.
- [ ] Source/input/data manifest and hashes.
- [ ] Runner source + dependencies/environment + local run command.
- [ ] Data-quality and event eligibility/skip ledger.
- [ ] Full grid and every candidate scorecard.
- [ ] Full chronological trade ledger for each frozen finalist.
- [ ] Zero-inclusive weekly net-R and annual/quarterly cohort data.
- [ ] Cost/delay stress and block-bootstrap results.
- [ ] Machine-readable result JSON + report + run log.
- [ ] SHA-256/size manifest for every output.
- [ ] Second-run byte-identical deterministic hash verification.
- [ ] Updated master ledger, family map and PROJECT_STATE.
- [ ] Read-back verification of all required paths.
- [ ] If economics pass: challenge-event path + real-account rule evidence + >=10,000 dependence-aware sequential paths.

If artifacts exceed ordinary file limits, store verified chunks and provide a restore script with a reconstructed-byte hash check. A list of hashes alone is insufficient.

## I. Challenge-readiness gate (only if economic gates pass)
- Current official firm rules and source URLs/verification date:
- Account size and actual contract value/lot sizing:
- Commission/swap/fee and platform-specific symbol specification:
- Server timezone, DST and daily reset:
- Floating equity, daily/max loss, forced cycle close and Quick Strike:
- Two-phase target mechanics and minimum trading days:
- Exact risk grid and aggregate exposure limit:
- Required output: both-phase completion probability, breach probabilities by type, P(funded by day 179), median/P90/P95 days-to-funded, drawdown/loss-streak tails and cost/delay sensitivity.

Do not estimate pass probability before this gate is executable. A historical single path is not a pass-probability estimate.

## J. Decision and learning record
- Final binary verdict LULUS/GAGAL:
- Failure class, if failed:
- First failed gate:
- What this result falsifies / does not falsify:
- Which family/block is now closed:
- Exact lesson added to family map:
- What process control improved from the previous run:
- What remains blocking the next experiment:
- Project-state commit SHA after closure:

Do not edit a registered card after observing outcomes. Corrections are amendments committed before rerun; failed hypotheses cannot be rescued on the same inspected periods.
