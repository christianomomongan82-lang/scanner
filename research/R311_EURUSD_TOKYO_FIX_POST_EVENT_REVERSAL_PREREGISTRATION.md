# R311 — EURUSD Tokyo Fix Post-Event Reversal — Locked Preregistration

**Registration status: LOCKED BEFORE PnL.** No R311 outcome PnL has been calculated at registration time.

## A. Identity and lineage

- Candidate ID: R311
- Primary family ID: `FX_TOKYO_FIX_EVENT_REVERSAL`
- Secondary tags: `INSTITUTIONAL_FIXING_FLOW`; `SHORT_HORIZON_MEAN_REVERSION`; `PHONE_DELAY`; `BID_ASK_EXECUTION`
- Candidate type: `NEW_MECHANISM` (new institutional event: Tokyo 09:55 fixing; not a clock-only mutation of a generic intraday strategy).
- Parent/context only: R300 London 16:00 fix post-event reversal. R300 is a different benchmark, market-participant setting and fixing convention. It is not an alpha component and its thresholds/outcomes will not be reused for tuning.
- Stop list: exact R300 London rule; R303 spread-shock reversion; R304 fixed-local-hours; R307 intraday-of-week; R308 weekend carry (data-ineligible); R309–R310 cross-asset residual; and the previously closed FX trend/reversal/session variants. Do not change event clock, return horizon, direction, risk unit or hold period to rescue R311 on the same sample.
- Hypothesis selection rationale: economic event flow is institutionally defined and distinct from technical-price thresholds; source quotes and local timestamps exist; one possible trade per weekday offers adequate screen frequency; fixed post-event execution is plausible with phone delay. Published effect evidence is from market data unlike this broker feed, therefore it is only motivation, not evidence of a tradable edge here.

## B. Falsifiable hypothesis

**Claim:** On valid EURUSD weekdays, the sign of the 15-minute midpoint return ending at 09:55 Asia/Tokyo time predicts an opposite-direction EURUSD move after the Tokyo fixing, from a five-minute delayed 10:00 entry to a maximum 10:30 exit, after observed BID/ASK execution and registered extra costs.

**Mechanism:** Tokyo's 09:55 FX fixing serves transactions between Japanese banks and their customers. Fix-related demand can concentrate orders around a common timestamp and create temporary price pressure; a reversal after the event is a falsifiable possibility, not an assumed result.

**Public rationale (available before scoring):**
- Ito & Yamada, NBER Working Paper 21518, *Was the Forex Fixing Fixed?* describes the Tokyo 09:55 JST fixing and distinguishes it institutionally from the London fix: https://www.nber.org/papers/w21518
- Ito & Hashimoto, *Intraday seasonality in activities of the foreign exchange markets*, documents intraday patterns in EUR/USD and USD/JPY firm quotes: https://www.nber.org/papers/w12413
- Research with inter-dealer quotes finds that thinness can contribute to negative quote-return autocorrelation, but the sample is narrow and not necessarily executable for this feed: https://www.sciencedirect.com/science/article/pii/S0261-5606(96)00044-7

**Falsification:** R311 is GAGAL if any required data/coverage gate fails, or if discovery/validation cost-adjusted expectancy, annual stability, bootstrap, delay or cost robustness fails. A failure refutes this registered rule on these data; it does not prove all fixing-related effects impossible. The matched follow-direction stream is diagnostic only and cannot replace the primary fade on the same sample.

**Known confounds:** The Dukascopy quote feed is not the inter-dealer fixing source; timestamps are M1 OHLC rather than ticks; fixing demand can be two-sided; fixing practices and participants may change over time; the Tokyo event window can overlap other news; program-level FX dates are contaminated by earlier research; BID/ASK broker spreads and slippage can erase a gross effect.

## C. Frozen rules

- Instrument/feed: EURUSD paired Dukascopy M1 BID and ASK OHLC.
- Timestamp join: exact timestamp key only; no row-number pairing, forward fill or synthetic bars.
- Active row: for each side, active iff `high > low` or `open != close`. A derived M5 bar is eligible only when it consists of five exact, contiguous, active M1 rows, aligned to the M5 boundary, on both quote sides.
- Clock: IANA `Asia/Tokyo` local time, including historical timezone rules. Event date is Monday–Friday Tokyo local date. No future holiday information or externally selected day list.
- Signal: on the M5 bar starting 09:50 Tokyo, whose close is known at 09:55, calculate midpoint-close return from the M5 bar starting 09:35 to the bar starting 09:50: `r = close_mid(09:50) / close_mid(09:35) - 1`. Both bars and every required source bar must be exact, active and contiguous.
- Direction: primary FADE. If r > 0, SHORT; if r < 0, LONG; if r == 0, skip. No percentile/magnitude threshold, no regime filter, no weekday filter, no post-hoc parameter selection. One primary event per Tokyo-local date.
- Entry: exact M5 open at 10:00 Tokyo time, five minutes after the signal close. LONG at ASK open; SHORT at BID open. Do not substitute a later bar.
- Risk distance R: arithmetic mean of the six complete midpoint M5 ranges (midpoint high minus midpoint low) on bars starting 09:25, 09:30, 09:35, 09:40, 09:45 and 09:50 Tokyo. R must be finite and positive.
- Spread eligibility: entry spread = ASK open − BID open at 10:00. A candidate event is eligible only if `R >= 3 * entry_spread` and entry spread <= 2.0 pips. Reasons for every rejected event are retained before outcomes.
- Barrier/holding: fixed 1R stop and 1R target. Maximum hold = 30 minutes from entry, time exit at the exact 10:30 M5 open. Monitor bars starting 10:00, 10:05, 10:10, 10:15, 10:20, 10:25. No overnight positions, scaling, trailing or re-entry.
- Executable sides: LONG stop/target check and exits use BID OHLC; SHORT stop/target check and exits use ASK OHLC. A bar opening through a stop/target fills at that adverse/favorable open; if stop and target are both touched in one bar, stop-first. Otherwise execute the first barrier reached. A missing/inactive/noncontiguous required source/path bar makes the date ineligible before outcome calculation.
- Matched follow control: same timestamps, same risk/entry/exit rules, but LONG after positive pre-fix return and SHORT after negative return. Diagnostic only.
- No concurrent positions: fixed 30-minute holding and one event per Tokyo date means no intended overlap. If timestamps nonetheless overlap, skip the later entry and record reason.

## D. Data and integrity contract

- Source archive: existing GitHub data-only artifact #11959096102; acquisition run #38697080604.
- Archive SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- BID gzip SHA-256: `b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc`.
- ASK gzip SHA-256: `52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b`.
- Source dates: 2016-01-03 through 2025-12-31 UTC, subject to observed feed rows.
- Cutoff: drop timestamps >= 2022-01-01T00:00:00Z before feature construction or PnL; no R311 outcomes for 2022–2025.
- Before PnL, verify member hashes, row count, unique and monotonic minute timestamps, BID/ASK timestamp-set equality, valid OHLC, nonnegative spreads, active/static rows, exact complete M5 formation, exact local event/entry/path timestamps, and event skip reasons/counts by year.
- Data limitation: repeated static/closed-market feed rows are not evidence of executable quotes and must not be treated as tradable bars.
- Reproduction: save runner, preregistration, event eligibility audit, trade ledger, scorecards, compact metrics and final binary verdict to the active research branch. Backtest computation runs in local Python, not GitHub Actions.

## E. Locked periods and contamination

- 2016: time-zone, source and event-coverage sanity only; no R311 PnL.
- Discovery: 2017–2020.
- Validation screen: 2021.
- 2022–2025: no R311 PnL will be calculated. If the historical gate passes, this candidate still needs separately approved prospective/new data before promotion; this screen is not pristine program-level OOS.
- Program-level status: 2017–2021 FX data are contaminated by previous experiments. Results cannot be called untouched OOS or funded-ready.

## F. Frozen execution cost grid

- Observed BID/ASK spread is already represented by the executable side-specific entry/exit prices; do not subtract it twice.
- Subtract additional round-trip EURUSD friction of +0 / +0.5 / +1 / +2 pips from price PnL; one pip = 0.0001.
- Primary case: +1 pip per round trip.
- Primary entry delay: five minutes after the signal close. Delay stress: entry at exact 10:05 Tokyo M5 open, with same signal and 30-minute maximum holding from actual entry; require a complete path and do not shift a missing entry forward.
- No swap due to same-session exit. Broker commission/slippage assumptions are represented through the extra-pip sensitivity only; this is not a claim about a FundedNext account's exact costs.

## G. Preregistered screen gates

All gates are conjunctive for historical-screen promotion:

1. Data and event/path integrity fully pass; no synthetic or inactive quote used.
2. >=200 completed discovery trades and >=100 completed validation trades at primary cost; also publish eligible/skip coverage so trade count cannot hide a reachability defect.
3. At +1 pip, net R > 0 and PF_R >= 1.05 in both discovery and 2021 validation.
4. At least 3 of the 4 discovery calendar years have positive net R at +1 pip.
5. Validation weekly net-R 95% circular 4-week block-bootstrap CI lower bound > 0 (10,000 resamples, seed 311, zero-trade calendar weeks included).
6. Validation net R > 0 and PF_R >= 1.00 at +2 pips.
7. Validation net R > 0 under T+10 entry delay at +1 pip.
8. Matched-control and event-subgroup diagnostics are reported; the primary rule is not replaced by the better-looking direction after seeing outcomes.
9. Exact inputs, runner, data/event audit, trade ledger and metrics are committed/readable in GitHub.

Failure of any required gate means **GAGAL** and closes this exact R311 candidate. No R312 parameter mutation may be chosen on R311 validation outcomes.
