# R321 — Causal price-relationship audit (immutable preregistration)

**Status: REGISTERED BEFORE OUTCOME CALCULATION.** This is a small hypothesis audit, not a funded strategy and not a license to inspect protected 2026 data.

## A. Identity and lineage
- Experiment: R321; family: causal sequential price-state prediction.
- Type: NEW_MECHANISM / predictive-relationship audit (not a stop/target sweep).
- Related closed work reviewed: R317/R318 (candle/price-shape screens failed forward); R319 (H1 displacement plus M15 pullback failed confirmation/diagnostic); R320 (H4 channel breakout failed); R303 (spread shock failed); R304/R307 (clock/weekday effects failed); R309/R310 (cross-asset residual snapback failed).
- Novelty: compare simple return direction baselines against a compact, causal state-encoding set that tests whether path efficiency, acceleration, and directional persistence contain predictive information beyond a raw return threshold. No parameter rescue of those closed families.
- Data window already inspected by the overall project; therefore this is exploratory/falsification evidence, **not pristine independent validation**. R321 cannot certify funded readiness from these dates.
- Protected holdout: all data timestamped 2026-01-01 UTC and later remains unopened and excluded.

## B. Falsifiable claim
The primary claim is that causal path-state scores—return acceleration, path-efficiency-weighted return, lag-1 return persistence, and volatility-conditioned recent return—predict the sign and magnitude of EURUSD's *executable* forward move beyond plain 15/30/60-minute returns, after a five-minute manual-compatible delay and realistic costs.

This claim fails if the state scores have no positive post-cost directional return, do not beat the simple-return baselines, reverse sign across chronological cohorts, or show apparent significance that disappears under block inference/multiple-test adjustment. Finding a statistically measurable relationship is not enough if the executable post-cost move is negative.

## C. Locked universe, data and chronology
- Instrument: EURUSD only; Dukascopy raw paired BID/ASK M1 source archive SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- Members: `eurusd_bid_M1_2016-2025.csv.gz` and `eurusd_ask_M1_2016-2025.csv.gz`; timestamps interpreted as UTC epoch milliseconds.
- First perform source integrity, paired timestamp, repeated-flat placeholder, OHLC validity, spread sign, duplicate and gap audit. Apply the existing joint repeated-flat placeholder rule (remove a minute only when both BID and ASK OHLC are identical to the previous paired minute); document exact counts and hash the cleaned rows.
- Resample only exact contiguous five-minute groups containing all five paired M1 timestamps. Do not fill gaps or use incomplete bars. Reset every rolling feature after any missing M5 bar; no rolling window may bridge a gap.
- MID OHLC is the component-wise average of BID and ASK OHLC. Fill calculations nevertheless use true BID/ASK.
- Discovery: 2016-01-01 through 2018-12-31 UTC.
- Confirmation: 2019-01-01 through 2020-12-31 UTC.
- Diagnostic: 2021-01-01 through 2025-12-31 UTC. This range is program-contaminated and can falsify but cannot establish independent out-of-sample readiness.
- 2026 onward: excluded, protected.

## D. Fixed sampling and execution mapping
- Sample signals only on a fixed 65-minute UTC cadence, anchored at 2016-01-01 00:00 UTC, choosing the completed M5 bar whose close time exactly matches each cadence time. This makes the longest, 60-minute outcome windows non-overlapping (the next sample is at the previous maximum-horizon exit time).
- Every feature uses information available no later than the signal bar close.
- Entry is the exact observed M5 open five minutes after signal close (equivalently the M5 bar starting ten minutes after the signal bar's timestamp). The signal-to-entry wait is explicit; missing entry/open/exit timestamps invalidate that event and are counted by reason.
- Direction for the execution score is sign(feature score): long enters at ASK open and exits at BID close; short enters at BID open and exits at ASK close. No target/stop optimization, no overlapping positions.
- Horizons from entry: 5, 15, 30 and 60 minutes; exit at the corresponding observed M5 close. Stop/target collisions are not applicable to this fixed-horizon forecast audit.
- Cost levels are +0, +0.5, +1.0 and +1.5 pips incremental round-trip friction, in addition to observed BID/ASK spread. Primary is +1.0 pip. Pips use 0.0001 EURUSD.
- These are prediction events, not account-sized trades. No funded pass probability or risk sizing is estimated.

## E. Frozen feature set (7 scores × 4 horizons = 28 tests)
At completed signal bar k, let r_i = log(MID close_i / MID close_{i-1}), with bars indexed backward from k. All return calculations use only uninterrupted valid M5 bars.

1. **F1_RET15:** sum of r over last 3 bars.
2. **F2_RET30:** sum of r over last 6 bars.
3. **F3_RET60:** sum of r over last 12 bars.
4. **F4_ACCEL15:** sum of r over the latest 3 bars minus the sum over the immediately preceding 3 bars.
5. **F5_EFFICIENCY60:** sum of r over last 12 bars divided by sum(abs(r)) over those same 12 bars; score is zero if denominator is zero.
6. **F6_AUTOCORR_STATE:** sign(sum of last 12 r) multiplied by lag-1 Pearson autocorrelation of those 12 returns. If variance is zero or the sum is zero, score is zero.
7. **F7_VOL_CONDITIONED_RET15:** F1_RET15 multiplied by the ratio of realized standard deviation of the latest 3 returns to the trailing median of all available 3-return realized standard deviations over the preceding 48 bars. Require at least 24 valid trailing comparisons; otherwise ineligible.

Target horizons from the delayed entry: 5/15/30/60 minutes. No additional features, thresholds, clock filters, symbols, directions or horizons may be added after seeing outcomes.

## F. Metrics and selection rules
- For every score×horizon, report sample count, Spearman rank correlation between score and midpoint forward return, the top-minus-bottom score-decile midpoint-return spread, sign(score) directional executable mean net pips at all four cost levels, median net pips, positive-event share, gross win/loss PF where defined, annual and chronological-cohort results.
- Use UTC-week clustered inference with a four-week moving-block bootstrap, 2,000 replications, fixed seed 3212026. Preserve zero-event weeks in weekly series. Use a family-wise Bonferroni threshold of 0.05/28 for the primary 28 relationships; report raw and adjusted p-values. Do not use IID trade-level standard errors.
- At least 300 valid non-overlapping prediction events per period/cohort are required for a cohort result to be interpreted; otherwise that gate fails.
- A candidate relationship is only provisionally interesting if primary-cost mean net pips are positive in discovery and confirmation and in at least four of five diagnostic calendar years; its four-week block-bootstrap 95% interval is above zero in discovery and confirmation; the top-minus-bottom decile spread is positive in all three cohorts; and the state score improves mean net pips over the best of F1–F3 on the same horizon in both discovery and confirmation. Diagnostic history remains contaminated, so even a pass only warrants a newly preregistered challenge-readiness evaluation, not deployment.
- The family is falsified for funded-search purposes if no state score meets these gates. Do not tune the failing score or reuse these periods to select a nearby variant.

## G. Required outputs and reproduction
- Exact script + pinned environment, source archive identity, cleaned-data audit and hashes.
- Full 28-row scorecard at all registered cost levels; all eligible prediction events with feature scores, exact entry/exit timestamps, BID/ASK prices, skip reasons and costed outcomes; annual/cohort scorecards; weekly series; block-bootstrap results; family-wise adjustment; result JSON; report; SHA-256 manifest.
- Execute twice in a clean local Python/container session; all stable output hashes must match exactly. Store and read back all required repository files before closing.
- Local execution only; GitHub is the data/source-of-truth archive, not the compute engine.

## H. Binary decision
- No relationship is funded-ready from this audit. Its only possible positive decision is: **GAGAL to falsify the registered research claim / proceed to a separate preregistered, challenge-aware strategy evaluation**. Otherwise verdict is **GAGAL — no cost-surviving predictive relationship**. A result with missing gates/artifacts is GAGAL — DATA/PROCESS, never a soft pass.
- Registration is committed before the first outcome calculation. Any needed correction must be an append-only dated amendment committed before rerunning outcomes.


## Pre-outcome implementation lock — 2026-10-21 UTC

Before any outcome calculation, the implementation was committed and read back:
- Runner path: `research/R321_price_relationship_audit.py`
- Runner commit: `57d1427177cc1cd95829154ff13cbad2fdd25106`
- Runner Git blob SHA-1: `1192419baf92f4795ce75c886e67095d1495c7b9`
- Configuration path: `research/R321_CAUSAL_PRICE_RELATIONSHIP_AUDIT_CONFIG.json`; config commit `111d0ed2bf7eee7e4941fd2cdedbe72dc50ca50e`
- Initial card commit: `67a8de40dafed467cddf00ab52ddbc1a85ee37ca`
- Implementation clarification: F7's 48 trailing 3-return volatility estimates require an uninterrupted history of 50 M5 bars so no nested volatility window can reach across a missing-bar gap. This is a stricter data-validity condition, not a new signal parameter.
- No R321 signal-outcome metrics had been calculated when this amendment was committed.


## Pre-outcome data-gate amendment — 2026-10-21 UTC

The first **data-only** preflight stopped before feature-to-outcome calculations: the initial implementation retained 3,726,929 M1 rows and 742,194 complete M5 bars, inconsistent with the already registered source-cleaning baseline. The cause was a new timestamp-continuity condition added to repeated-flat removal. That condition was not part of the project's canonical cleaning rule.

Before any outcome metric was computed, the runner was corrected to drop the current row whenever all eight BID/ASK OHLC values exactly equal the preceding source row, regardless of the timestamp gap. This does not fill gaps; it only removes the existing joint repeated-flat placeholder pattern. The prior sentence in section C that conditioned removal on a 60,000 ms timestamp difference is superseded by this amendment.

Updated runner:
- Commit: `0d2fc3c037d5084879b8d9a5b51f56465efa3f08`
- Git blob SHA-1: `0778287acd50ed38243fdc2b202de8ad3c9ebe16`

No R321 feature-outcome correlation, directional return, costed return, or candidate score was calculated before this amendment. The only inspected numbers from the stopped attempt were source-cleaning and complete-bar counts.


## Pre-outcome filter-definition clarification — 2026-10-21 UTC

A second data-only audit compared alternative repeated-flat definitions against the established baseline count; no features or forward outcomes were computed. The canonical 696,795-row count is matched by the following exact predicate: remove the current row only when all four current BID OHLC values equal the preceding source row's BID close **and** all four current ASK OHLC values equal the preceding source row's ASK close. This predicate is independent of timestamp continuity. The previous two implementations (matching each current OHLC to the respective previous OHLC columns, and matching all current OHLC to themselves) are rejected and were never used to calculate outcomes.

Updated runner identity:
- Commit: `fbc46d8e604445d73619e7ceb34b5667cf017623`
- Git blob SHA-1: `7c68218694f75f8e1f8532b23ee1e9c8a54f76f0`

The registered repeated-flat rule is now the predicate above. Reproducible M1/M5 count and hash gates must pass before any return/relationship metrics are calculated.
