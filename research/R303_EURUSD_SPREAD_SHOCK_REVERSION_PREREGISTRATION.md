# R303 — EURUSD Spread-Shock Reversion (LOCKED PREREGISTRATION)

**Lock timestamp:** 2026-10-19 UTC  
**Status at lock:** No candidate PnL has been calculated.  
**Binary rule:** LULUS or GAGAL; no threshold/direction/exit rescue after outcomes.

## A. Identity and lineage

- Candidate ID: R303
- Primary family: FX_MICROSTRUCTURE_SPREAD_SHOCK
- Secondary tags: EURUSD, paired BID/ASK, liquidity-stress/recovery, manual-delay execution.
- Candidate type: NEW_MECHANISM.
- Related closed work: R260 candle-shock fade; R300 London-fixing event fade; R281 EURUSD data-quality / execution work. They are context and matched diagnostics, not parents whose thresholds are being repaired.
- Matched diagnostic: identical qualifying signal events and execution rules but follow the preceding 5-minute midpoint move instead of fading it. This is diagnostic only; direction will not be selected after outcomes.
- Mechanism novelty score (0–3): 2. The primary trigger is a paired-quote spread shock and a predeclared restoration gate, not a change to a candle-size threshold or session cutoff in a prior strategy.
- Data readiness (0–3): 3; paired EURUSD M1 BID/ASK archive exists.
- Manual-delay feasibility (0–3): 2; T+5 base and T+10 stress, with no sub-minute dependency.
- Falsifiability (0–3): 3; explicit spread/return conditions and a single locked exit design.
- Diversification potential (0–3): 2; quote-state/microstructure behavior is distinct in mechanism, although the instrument and historical windows are contaminated.
- Penalties: overlap with previous FX reversal work = 1; historical/program contamination = 2. These scores choose a test, not a promotion.

## B. Falsifiable hypothesis

**Claim:** In active EURUSD trading hours, a large midpoint move that coincides with an abnormal observed BID/ASK spread widening will, conditional on the spread having returned to a normal range by the manual-compatible entry time, reverse more often/profitably over the next 30 minutes than it continues.

**Mechanism:** temporary quote/liquidity impairment can amplify a short-lived price displacement, while spread normalization provides a measurable proxy that trading conditions have recovered. This mechanism can be false: spread widening may instead accompany information arrival and continuation.

**Frozen signal:**
1. Input timestamps are UTC M1 bar-start times; each bar's close becomes known one minute later. All derived midpoints use (BID+ASK)/2; spread is ASK−BID. Only exact timestamp pairs are allowed.
2. Consider signal bars whose close times fall on Monday–Friday, 06:00–19:59 UTC. No feature or outcome may use any timestamp at or after 2026-01-01T00:00:00Z.
3. Require five uninterrupted, active M1 bars for the 5-minute move. Let (r_5 = midclose_t - midclose_{t-5m}).
4. Let baseline spread be the median spread-close of the preceding 60 active paired M1 bars, all within the prior 180 minutes; require at least 45 such rows. Do not include the current signal bar in that median.
5. Let the volatility threshold be the 90th percentile of absolute 5-minute midpoint returns from the prior 20 calendar days only, requiring at least 1,000 valid past 5-minute observations. Do not include the current return.
6. A signal occurs only when current spread-close is at least 2.0 × the prior median spread **and** (|r_5|) is at least that trailing 20-day 90th-percentile absolute return.
7. Primary direction fades (r_5): short when (r_5>0), long when (r_5<0). Zero returns do not trigger.

**Entry / latency:**
- Baseline entry quote is the first active paired M1 bar open at or after signal-bar close + 5 minutes (for a signal bar stamped t, earliest entry bar start is t+6 minutes).
- Enter only if its open spread is no more than 1.5 × the signal's pre-event baseline spread. Otherwise skip; do not wait for a later attractive quote. This makes spread recovery a pre-outcome executable condition.
- Delay stress repeats this exact eligibility test at signal close + 10 minutes (earliest bar start t+11 minutes). No outcome-driven substitution.
- Long enters at ASK open; short enters at BID open. At most one open position per instrument; signals while a position is open are recorded as skipped.

**Stops / exits:**
- Risk distance (D = max(|r_5|, 2 × entry_open_spread)), in price units.
- Initial stop is 1.0D against the position; target is 1.5D in favor.
- Maximum hold is 30 minutes. Require a complete contiguous 30-bar active paired M1 path before the event may be declared execution-eligible; missing bars are never synthesized.
- Long exits use BID; short exits use ASK. A stop has priority if stop and target are both touched in one minute. Opening gaps through a stop fill at that observed open; target fills at its target level. Time exit fills at the observed closing quote at the 30-minute cutoff.
- No trailing stop, partial close, or retuning.

## C. Data contract

- Source: Dukascopy EURUSD M1 BID/ASK archive downloaded from pre-existing GitHub Actions data artifact #11959096102; artifact was data acquisition only.
- Archive: `EURUSD_M1_BID_ASK_archive.zip`; expected SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- Exact raw source window: 2016-01-01 inclusive to 2026-01-01 exclusive. The exclusive 2026 cutoff must be applied before features, thresholds, event counts, or PnL.
- Quote sides: paired BID/ASK. Join by exact timestamp, never row index. Preserve missing rows; no forward-fill or synthetic bars.
- Data-only audit must report row counts, paired timestamp coverage, duplicates, invalid OHLC, negative spread, active/flat-bar handling, timestamp gaps and hashes. Active-bar policy must be fixed before signal PnL.
- Because the original Dukascopy collection used flat-filled data, exclude a minute only if BID and ASK are both O=H=L=C and both sides' four prices equal the preceding observed minute's closes with an exact 1-minute timestamp step. Report counts; do not remove a flat bar merely because its range is zero.
- Cost model uses observed executable BID/ASK fills plus incremental round-trip stress of +0 / +0.5 / +1 / +2 pips. Primary cost = +1 pip. These are sensitivity settings, not a verified broker-cost claim.

## D. Frozen periods and contamination

- Discovery: 2017-01-01 through 2020-12-31 UTC.
- Validation: 2021-01-01 through 2021-12-31 UTC.
- Do not calculate R303 candidate PnL for 2022 onward in this experiment. These FX periods are development-contaminated by prior project rounds and are not pristine program-level OOS; even a historical-screen pass is not funded-ready.
- Report the number of candidate variants tried on related periods: many prior FX candidates, explicitly including R260/R281/R300; this is why R303 cannot establish a clean OOS claim.
- 2016 is data warm-up/calibration only and is not scored.

## E. Locked tests and gates

- Primary hypothesis: fade-direction stream at +1 pip incremental round-trip cost, T+5 entry.
- Diagnostics: 0 / 0.5 / 2 pip costs; T+10 latency stress; matched follow-direction stream on identical event eligibility.
- Report event counts and skip reasons before outcomes; trade ledger, annual cohorts, net R, PF_R, mean/median R, drawdown, losing streak, holding time, trades/week, cost and delay sensitivity.
- Validation bootstrap: 5,000 circular four-calendar-week block resamples of 2021 weekly net R, seed 303; include all calendar weeks including zero-trade weeks.
- Gates: data/execution integrity; at least 200 discovery and 100 validation trades; net R > 0 and PF_R ≥ 1.05 in both periods at +1 pip; at the +2-pip stress net R > 0 and PF_R ≥ 1.00; at least 3/4 discovery years net positive; validation weekly bootstrap 95% lower bound > 0; T+10 stress net R > 0; no unexplained unreachable eligibility condition; all code/config/row-level output reproducible from exact input hash.
- Every gate is hard. Failure of sample, expectancy, cost, bootstrap, delay, or reproducibility means GAGAL for promotion. No challenge replay will be run if any historical gate fails.
- Even if every gate passes, this is only a contaminated historical screen; a separate independent/locked validation and account-equity-aware funded replay would still be mandatory.

## F. Required output artifacts

Commit the exact runner, data-integrity audit, pre-outcome eligibility/skip audit, all valid trade ledger, matched-follow ledger, cost/delay stream table, compact JSON, annual and period tables, validation weekly bootstrap JSON and input series, final report, index, and updated project checkpoint. GitHub Actions must not calculate strategy PnL; all backtest calculations run in the local Python/container session.

## G. Run-integrity log

| Timestamp | Action | Candidate PnL visible? | Result |
|---|---|---|---|
| 2026-10-19 UTC | Registration locked and committed | NO | Pending data-only audit |
