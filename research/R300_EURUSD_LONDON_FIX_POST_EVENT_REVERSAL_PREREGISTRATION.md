# R300 — EURUSD London 4pm Fix Post-Event Reversal — Locked Preregistration

**Locked:** 2026-10-18 UTC. **Candidate type:** NEW_MECHANISM. **Status before scoring:** registered, no R300 signal PnL calculated.

## A. Identity and lineage

- Candidate ID: R300
- Primary family ID: FX_LONDON_FIX_EVENT_REVERSAL
- Secondary tags: FIXING_WINDOW; SHORT_HORIZON_MEAN_REVERSION; PHONE_DELAY; BID_ASK_EXECUTION
- Parent candidates for stop-list / context only: R260 (general H1 shock fade), R269 (London Asia-range sweep/reclaim), R275 (phone-delay stress), R270 (session router). None is reused as an alpha component.
- Closed candidates not to rescue: R255, R260, R269, R270, R275, R282; the exact registered rules stay closed.
- Exact matched directional control: same R300 events, timestamps, sizing, stop/target, costs, and risk geometry, but follow rather than fade the pre-fix return. This is a diagnostic ablation; it cannot be promoted post hoc on the same periods.
- Why structurally new: R300 is tied to the institutional 16:00 London benchmark fixing window and the short-lived post-fix price-impact/reversal mechanism, not a generic H1 candle fade, Asia/London opening-range sweep, or a lead-lag between separate instruments. The R300 rule is set before outcome calculation. Literature reports unusual price/volatility behavior around the WMR fix and negative serial correlation around the fix, particularly at month-end; those results motivate a falsifiable hypothesis, not an assumption that this feed has a tradeable edge.
- Hypothesis selection score (0–5, qualitative): novelty 4; data readiness 5; phone feasibility 3 (wait until fix window is complete, then enter with ten-minute post-close delay); falsifiability 5; potential diversification 3; overlap penalty 2. Overall priority: medium, research-only.

## B. Falsifiable hypothesis

**Claim:** On valid EURUSD trading weekdays, the direction of the 15-minute midpoint return ending at 15:55 London time predicts an opposite-direction EURUSD move from a delayed 16:05 entry to a maximum 16:35 London exit, after quote-side fills and registered costs.

**Mechanism:** Institutional benchmark orders are concentrated around the WMR 16:00 London fix. Research has documented unusual fix-window price dynamics and evidence consistent with temporary order imbalance / negative serial correlation. The test only asks whether fading the pre-fix move after the fixing window finishes survives this data feed's bid/ask and latency costs.

**Public rationale, available before scoring:**
- Boehmer? No author attribution is required for the code; use the cited studies below rather than inferring a price edge from the title alone.
- “Did the reform fix the London fix problem?” *Journal of International Money and Finance* (2018): https://www.sciencedirect.com/science/article/pii/S0261560617302024
- “The WMR Fix and its Impact on Currency Markets” (2017): https://www.norges-bank.no/contentassets/619c8b75e1ed4ba691e8ad6a006855e6/39-panagiotou---the-wmr-fix-and-its-impact-on-currency-markets-.pdf?v=11122017105711
- FCA Occasional Paper 46, “Fixing the Fix?” (first published 2018, update history visible on page): https://www.fca.org.uk/publications/occasional-papers/occasional-paper-no-46-fixing-fix-assessing-effectiveness-4pm-fix

**Falsification:** GAGAL if any core gate below fails. Negative fade expectancy or no bootstrap support refutes the registered trade rule in these historical partitions. It does not prove all fix-related mechanisms are impossible.

**Confounds:** Published research may use inter-dealer transaction/quote data unlike Dukascopy CFD-like bars; 2015 changed the fixing window; DST must be handled in Europe/London local time; EURUSD FX windows have prior project contamination; fixed clock event may overlap other US-market announcements; M1 OHLC cannot resolve exact tick ordering; historical broker execution costs are not verified.

## C. Immutable trade rules

- Instrument: EURUSD only.
- Source timeframe: one-minute Dukascopy BID and ASK OHLC; construct a derived M5 bar only when all five exact M1 bars exist, are minute-contiguous, active, and timestamp-aligned on both sides. No synthetic/fill candles.
- Time zone: Europe/London with historical timezone/DST rules applied using IANA zone data.
- Eligible dates: Monday–Friday London-local dates with every required M5 source, entry and path bar present and active. No holiday list or future information. One attempted trade per eligible date.
- Signal bar: M5 bar starting 15:50 London time. Its close is known at 15:55.
- Pre-fix return: midpoint close of the 15:50 bar divided by midpoint close of the 15:35 bar, minus one. Midpoint close = (BID close + ASK close)/2. Both bars and all required interval bars must be valid; otherwise mark the date skipped.
- Signal direction: if the registered 15-minute return is positive, primary candidate SHORT; if negative, primary candidate LONG. If exactly zero, skip. No percentile threshold or magnitude filter.
- Entry: wait until 16:05 London time, exactly ten minutes after signal close. This is deliberately later than the standard five-minute manual reaction delay so the WMR fixing window has completed; no backdating to the fix midpoint.
- Executable entry: LONG at ASK open; SHORT at BID open at the exact 16:05 M5 timestamp.
- Risk unit: arithmetic mean of the six completed midpoint M5 ranges (midpoint high minus midpoint low) for bars starting 15:25, 15:30, 15:35, 15:40, 15:45 and 15:50. Must be finite and positive.
- Stop and target: fixed 1.0R stop and 1.0R target from entry. LONG stop/target = entry −/+ R; SHORT stop/target = entry +/− R. No trailing, scaling, re-entry or stop/target tuning.
- Exit horizon: first stop or target reached in M5 bars starting 16:05, 16:10, 16:15, 16:20, 16:25 or 16:30; otherwise exit at the exact 16:35 bar open. No overnight positions.
- Executable exit side: LONG exits and stop/target checks use BID OHLC; SHORT exits and stop/target checks use ASK OHLC.
- Gap/collision convention: if the executable open has gapped through stop or target, fill at that open; if stop and target both touched inside the same M5 candle, stop-first; otherwise fill at the first touched level. A required missing, inactive or noncontiguous path timestamp skips the entire trade; never substitute a later price.
- Position overlap: one position maximum because the holding window is fixed; if a prior trade has not closed by the next eligible signal, skip that date (the registered close horizon should usually prevent overlap).
- Matched follow-direction control: same signal dates, but LONG on positive pre-fix return and SHORT on negative; identical risk distance, entry time, exits and cost grid. This is diagnostic only; a post-hoc winner cannot replace the primary fade candidate on the same sample.

## D. Data contract

- Provider/source: Dukascopy through the already-collected data-only GitHub artifact; no new market-data source.
- Artifact ID 11959096102; collection run 38697080604; archive ZIP SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- Exact extracted members and SHA-256:
  - `eurusd_ask_M1_2016-2025.csv.gz`: `52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b`
  - `eurusd_bid_M1_2016-2025.csv.gz`: `b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc`
- Archive time range requested: 2016-01-01 through 2025-12-31 UTC; do not score any row at/after 2022-01-01 UTC. The cutoff is applied before building features/signals/outcomes.
- Quote sides: paired BID/ASK.
- Before outcome calculation, report member hashes, unique/monotonic minute timestamps, paired timestamp equality, minute grid/alignment, valid OHLC, observed spread sanity, active-vs-static rows, full five-minute aggregation eligibility, each required event timestamp, skip reasons, and coverage by year.
- Join BID/ASK by exact timestamp keys. No forward-fill, no synthetic OHLC, no row-number pairing.
- The historical validation year 2021 and older FX dates have prior use in this research programme. This is only a historical screen, not pristine program-level OOS and not a claim of funded readiness.

## E. Frozen periods

- Data/clock sanity only: 2016; no R300 PnL scored in 2016.
- Discovery: 2017–2020.
- Validation screen: 2021.
- 2022–2025: protected from R300 outcome calculation; no PnL will be calculated if any registered core gate fails.
- Program-level contamination: substantial. Many FX tests have reused 2017–2021; if all gates pass, promotion requires new prospective/paper evidence, not a claim that these dates are untouched.
- Candidate count: this exact R300 rule is the only primary fade variant. The matched follow stream is a preregistered direction diagnostic, not a candidate-selection escape hatch.

## F. Execution and cost model

- Base execution uses the observed side-specific BID/ASK OHLC. Do not add back observed spread.
- Additional round-trip cost grid: +0, +0.5, +1.0, +2.0 pips; one EURUSD pip = 0.0001. The primary case is +1.0 extra pip per round trip.
- At each cost c, net trade R = [direction_sign × (exit − entry) − c × 0.0001] / risk_distance.
- Intra-session only; no swap. Actual challenge account commission, slippage, financing, contract sizing and order execution are not verified. Add-on pips are sensitivity assumptions, not claims about FundedNext's actual fees.
- All costs are deducted identically in R and matched follow-direction control.
- Five-minute OHLC cannot exactly resolve intrabar touch order; use the registered conservative stop-first collision rule.

## G. Frozen historical screen gates

All primary candidate gates are conjunctive. If any fails, R300 is GAGAL and 2022+ PnL remains unopened.

1. Integrity: hashes, timestamp matching, M1/M5 eligibility, BID/ASK execution-side and cutoff checks all pass.
2. Sample size: at least 200 completed trades in 2017–2020 and at least 100 in 2021.
3. At +1 pip additional cost, both discovery and validation must have net R > 0 and PF_R >= 1.05.
4. Annual stability: at least 3 of four discovery years positive net R at +1 pip.
5. Cost stress: at +2 pips, both discovery and validation net R > 0 and PF_R >= 1.00.
6. Validation bootstrap: aggregate net R by all 52 Monday-start weeks of calendar 2021 in Europe/London, including zero-trade weeks; circular blocks of four weeks; 10,000 resamples, RNG seed 300. The 95% lower bound for mean weekly net R at +1 pip must be strictly greater than zero.
7. Delay/executable path: all entry/exit times are exact observed active timestamps. Since the signal purposely waits until 16:05, do not test a faster entry as a rescue.
8. Direction diagnostic: report matched follow-direction performance at all costs and the removed/changed direction subset. This does not override failed primary-candidate gates.
9. Binary verdict: LULUS/GAGAL only. LULUS at this screen stage is not equivalent to funded-ready; actual costs and an equity-aware two-phase challenge replay remain mandatory.

## H. Required artifacts

Commit exact runner, data manifest, full signal/skip audit, completed-trade ledger for fade and matched follow streams, annual summaries, validation weekly bootstrap series, compact JSON, final gate-by-gate report, an index, and ledger/checkpoint updates. Do not create/dispatch a GitHub Actions backtest. Calculations are local Python only.

## I. Funded promotion guardrail

Even if the historical gates passed, this would remain research-only until independently validated on future/prospective data and replayed with verified account costs, actual floating equity, daily loss/reset timezone, static max loss, sequential +8% then +5% targets, minimum trading days, and any applicable provider constraints. Do not recommend challenge purchase or make a funded-ready claim based on a signal screen.

## J. Expected result handling

- Any failure stays GAGAL; no parameter or directional rescue on the same dates.
- Preserve data/implementation failures separately from economic failures.
- If the fade loses while the matched follow stream looks better, record that fact, but do not promote the follow stream from this selected sample.
- Next research should learn from this family result and change mechanism if the primary candidate fails.

## K. Run integrity log

| Stage | Artifact / action | PnL visible? |
|---|---|---|
| 1 | Preregistration committed to active branch | NO |
| 2 | Pre-outcome data/coverage audit | NO |
| 3 | First locked outcome run | YES |
| 4 | Final report / ledger update | YES |
