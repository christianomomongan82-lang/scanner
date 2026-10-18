# R301 — XAUUSD Safe-Haven Delayed Hedge Response — Locked Preregistration

**Locked:** 2026-10-19 07:28 Asia/Makassar  
**Candidate:** R301_XAUUSD_SAFE_HAVEN_DELAYED_HEDGE_RESPONSE  
**Primary family:** XAU_CROSS_ASSET_SAFE_HAVEN_DELAY  
**Type:** NEW_MECHANISM  
**Related tests:** R272–R274 and R297–R298 (XAU trade engine/data lessons); R299 (cross-asset lead-lag is a caution, not a signal parent).  
**Matched baseline:** first qualifying extreme USA500 downside shock per New York cash session, without requiring gold underreaction.  
**No-filter diagnostic:** same gold entry/exit engine with all eligible USA500 downside-shock events, plus unconditional gold long entries at the same clock slots as a time-of-day sanity check.  
**Frozen data boundary:** feature timestamps before 2026-01-01T00:00:00Z only. XAUUSD 2026 remains protected and will not be opened in this candidate unless every pre-2026 gate passes; if not, it stays unopened.

## A. Falsifiable hypothesis

**Claim:** After an extreme rolling 30-minute downside move in USA500 during the New York regular session, XAUUSD has positive delayed long-side expectancy when gold itself has not risen during that same shock window.

**Mechanism:** A sharp broad-equity selloff can generate safe-haven hedging/allocation demand, but gold does not always respond synchronously with equities. The proposed edge is the conditional delay: equity downside shock plus non-positive gold return over the same 30 minutes. This is not a claim that every equity drop makes gold rise. A contemporaneous gold response, joint forced liquidation, dollar strength, event-day confounding, and the previously tested cross-index lead-lag family's broader limitations are alternatives.

**Why this is not a rescue of R299 or prior XAU tests:** It trades only XAUUSD and uses USA500 solely to define a downside risk-off event. The key interaction is delayed safe-haven response after *gold underreaction*, not USA500/USATECH price catch-up, XAU impulse continuation, a gold-only Asian sweep, or a reopening gap. No prior thresholds, directions, or trades are inherited.

## B. Frozen data, periods, and signal

- **Sources:** local raw archives from Dukascopy via dukascopy-node. XAUUSD M5 has paired BID/ASK; USA500 M5 is BID-only and is used only for signal context, not as a traded instrument.
- **XAU BID gzip SHA-256:** `b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575`.
- **XAU ASK gzip SHA-256:** `b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9`.
- **USA500 M5 BID gzip SHA-256:** `df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee`.
- **Discovery:** 2017–2020. **Validation:** 2021–2025. Earlier 2016 is used only for warmup/calibration. Program-level contamination is acknowledged: these periods and related instruments have been inspected in adjacent research; this is not pristine program-level OOS.
- **Protected:** all XAUUSD timestamps >= 2026-01-01T00:00:00Z are excluded before feature construction or outcome calculation.
- Convert timestamps to America/New_York with DST handled by the timezone database. Eligible feature endpoints are 10:00–15:00 ET on USA500 regular cash-session weekdays. Keep only actual, contiguous 5-minute bars; no resampling, ffill, invented bars or cross-instrument timestamp interpolation.
- At each eligible 5-minute endpoint, compute trailing 30-minute simple returns (current completed bar close divided by close six 5-minute bars earlier minus one) for USA500 BID close and XAUUSD BID close. All seven timestamps for each window must be exact, contiguous 5-minute observations; XAU BID/ASK timestamp keys must match exactly.
- **Equity shock:** USA500 trailing 30-minute return is at or below the 5th percentile of all valid USA500 trailing 30-minute returns from the prior 60 complete New York RTH sessions only. Threshold is expanding/trailing causal: current session and future values are never used. Require at least 40 prior complete sessions; otherwise the signal is ineligible.
- **Gold underreaction:** XAUUSD trailing 30-minute BID return <= 0 at the same exact endpoint.
- **Candidate trigger:** first eligible bar each NY session where both conditions are true. Maximum one entry per NY session; no second signal after a trade exits that session.
- **Matched parent:** first eligible extreme-USA500 downside shock per NY session, without the XAU return filter, using the same gold execution and exit rules. It is diagnostic; it cannot substitute for candidate gates.
- **No short-side mirror, no parameter sweep, no clock/quantile/holding-period retune, and no 2026 search.**

## C. Frozen execution and outcome model

- Signal is known only at the endpoint after its M5 bar has closed.
- **Primary delay:** enter at the first paired, active XAU quote bar open at or after 5 minutes following signal close (nominal timestamp signal endpoint + 5 minutes); maximum quote wait 10 additional minutes, otherwise record a skip. Long entry uses ASK open.
- **Delay stress:** first paired active quote at or after 10 minutes following signal close, with the same maximum 10-minute quote wait.
- Gold bars must be active/valid during the US cash-session event: exclude repeated static closed-market quote rows and any bar with invalid OHLC; never fill missing timestamps. Every feature bar used to trigger the event must belong to a contiguous active path.
- Stop distance is 1.0 × ATR(12) of XAUUSD M5 true range, using only the 12 completed active bars strictly before signal close. Freeze this distance at signal time. Long stop = ASK entry − ATR; target = ASK entry + ATR (1R:1R). Reject non-positive/missing ATR.
- After entry, evaluate each paired M5 bar's BID high/low. If stop and target are both touched within the same bar, count the stop first (pessimistic). Otherwise exit at first stop or target; if neither occurs, exit on the first active paired bar open at/after 60 minutes from actual entry. No overnight carry is intended. If the required path is missing, close at the first next active bid open and flag the trade as a data-path exception; any exception triggers a validity review, not silent omission.
- Report net outcome in R after subtracting round-trip incremental cost per ounce from price PnL and dividing by the frozen ATR risk distance. Primary cost is +$0.30/oz beyond observed BID/ASK execution; sensitivity grid is +$0.00, +$0.10, +$0.30, +$0.50/oz per round trip. These are stress assumptions, not verified FundedNext broker fees or slippage.
- One position maximum at a time, one entry maximum per NY session. No compounding, no simultaneous second trade, no discretionary skips. This historical screen is not a funded-account equity/DLL/MLL replay.

## D. Locked acceptance gates

Apply to the candidate at +$0.30/oz unless a row states otherwise. All listed gates must pass for an economic screen pass; passing the screen still does not mean funded-ready.

1. All required source hashes, timestamp pairing, active bar, continuity, quote-side, timezone, and pre-outcome eligibility checks pass.
2. At least 200 discovery and 100 validation completed candidate trades.
3. Discovery and validation net R are both > 0, and PF_R >= 1.05 in both at primary cost.
4. At +$0.50/oz, net R remains > 0 and PF_R >= 1.00 in both discovery and validation.
5. At least 3 of 4 discovery calendar years have positive net R at primary cost.
6. Validation weekly net-R circular moving-block bootstrap uses all Monday-start weeks (including zero-trade weeks), 4-week blocks, 10,000 resamples, seed 301; the 95% lower bound for mean weekly net R must be > 0.
7. Delayed entry stress remains net positive in both partitions and does not reverse the candidate's conclusion.
8. Every gate result, annual score, matched-parent comparison, and skip/feature-coverage count is reported. A failed gate means binary verdict **GAGAL**; no retuning or holdout opening to rescue this candidate.

## E. Limitations registered before scoring

- USA500 context is BID-only, not an executable trade leg; exact matched timestamp keys are required.
- The XAU source uses provider quote history, not guaranteed FundedNext live spreads/fills. Account-specific commissions, slippage, server-time mapping, swap, margin, and floating equity-path rule enforcement remain unverified.
- The 2021–2025 validation interval is program-contaminated; only XAUUSD 2026 is reserved as the limited next-period holdout.
- Positive fixed-risk R statistics are necessary screening evidence, not proof of passing either challenge phase. Do not claim a funded-ready result absent a separate equity-aware two-phase replay under verified current rules.

**Lock rule:** this file is immutable after signal outcome calculation. Any correction to execution or data handling must be recorded as a new dated amendment before re-running outcomes; it does not permit a rule change under R301.
