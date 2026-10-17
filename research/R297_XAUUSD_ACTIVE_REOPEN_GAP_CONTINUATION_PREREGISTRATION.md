# R297 Preregistration — XAUUSD True Active Weekend-Reopening Gap Continuation

**Candidate ID:** `R297_XAUUSD_ACTIVE_REOPEN_GAP_CONTINUATION`  
**Status:** locked before any R297 candidate PnL calculation  
**Date:** 2026-10-17  
**Lineage:** data-integrity correction to the invalid R296 attempt, not an outcome-driven signal change. R296 used the first Sunday timestamp at 00:00 UTC, which the raw quote inspection identified as a static closed-market quote block; it therefore did not represent an executable market reopening. R296 performance figures must be treated as **invalid test output**, not evidence for or against gap continuation. R297 changes the event timestamp definition only to the first genuinely active bar after the weekend closure; gap direction, 2× combined-spread eligibility threshold, T+10 entry, 1R stop/target, 4-hour time exit, costs, and direction are otherwise inherited unchanged.

## Hypothesis

A weekend reopening gap in XAUUSD may continue in the direction of repricing after the first genuinely active five-minute bar, rather than immediately reverting. Only continuation is tested. Do not test the opposite fade direction as a post-result rescue.

## Source integrity

Use only the raw-only Dukascopy artifact 12031270051 (data collection run 38859918137):
- BID SHA-256 `b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575`, 947,326 rows.
- ASK SHA-256 `b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9`, 947,326 rows.
- Exact BID/ASK timestamps must match. No timestamps are synthesized or interpolated.
- The archived manifest requested synthetic flat bars disabled, but raw-data inspection found long Sunday blocks with BID and ASK OHLC all equal at the same static quote before the active weekly reopening. The manifest flag alone is not accepted as proof that each individual row is tradable.

## True-active-bar and weekend-gap definition

1. Restrict all outcome calculations to event timestamps before 2026-01-01. Do not read or calculate strategy outcomes for 2026 unless every discovery/validation gate passes.
2. Treat source timestamps as UTC M5 bar-open times. An **active bar** is one where at least one of BID or ASK has `high > low` or `open != close`. A closed/static row where both sides have `open = high = low = close` is not executable and cannot define a signal or entry.
3. On the sequence of active bars only, a weekend event exists when a current active bar opens Sunday UTC, the preceding active bar opens Friday UTC, and their time difference is between 18 and 60 hours. The rows between them must all be static bars (both sides OHLC equal within each row); if any non-static intermediate bars occur, reject the event as ambiguous/ineligible.
4. Gap reference `G` is mid(Sunday first active bar open) minus mid(Friday last active bar close). Calculate spread values using those same actual Friday-active closing quotes and Sunday-active opening quotes.
5. Both selected bars must have valid positive internally consistent OHLC on both sides, BID/ASK timestamps must match exactly, ASK open/close must not be below BID open/close, and all event/entry/exit quotes must pass validity checks.
6. Keep only gaps satisfying `abs(G) > 2 * (Friday active-close spread + Sunday active-open spread)`. This coefficient is frozen; do not change it after examining any candidate outcome.
7. Signal bar is the first active Sunday M5 bar. Its close is known at T+5. Enter at the exact active-data M5 bar open at T+10 (five-minute signal confirmation plus five-minute phone execution latency). If the exact timestamp is missing, not active, or either quote is invalid, skip the event. No later-bar replacement.
8. Direction is gap continuation only: LONG if G > 0, SHORT if G < 0.
9. Initial distance `D = abs(G)` USD/oz. LONG enters at ASK open, stop = entry − D, target = entry + D; check both against BID OHLC. SHORT enters at BID open, stop = entry + D, target = entry − D; check both against ASK OHLC. Start exit checks at the entry bar. Stop priority applies if both stop and target are touched in one M5 bar. Stops that gap through fill at the worse executable open; targets that gap through fill at executable open; otherwise fill a stop/target at its level when hit.
10. If neither stop nor target hits, force-flat at the exact active quote bar open T+4 hours from the Sunday first-active bar timestamp. Do not inspect that exit bar's later OHLC. Require complete exact M5 timestamps throughout the entry-to-exit holding path; if any are missing/inactive, reject the event rather than fill a later bar. At most one trade per weekly reopening.
11. Net R = executable-side PnL per ounce less added round-trip cost, divided by D. Report costs $0.00, $0.10, $0.30 and $0.50/oz; primary cost +$0.30/oz beyond actual historical BID/ASK. This does not verify broker/funded commission or slippage. Report exits, long/short, annual cohorts, net R/PF_R, drawdown R, and a four-week weekly-net-R bootstrap.
12. No leverage compounding, stop/target optimization, trailing, news filter, or parameter sweeps.

## Frozen partitions and gates

- Discovery: event dates 2016-01-01 through 2020-12-31.
- Validation: event dates 2021-01-01 through 2025-12-31; this window has prior XAU strategy research exposure and is not pristine program-level OOS.
- Reserved final diagnostic: 2026-01-01 through 2026-10-15, sealed unless every prior gate passes.
- At +$0.30/oz, discovery requires at least 75 trades, net R > 0, PF_R ≥ 1.05, and at least 3 of 5 yearly cohorts with positive net R. At +$0.50/oz, discovery net R must remain positive and PF_R ≥ 0.90.
- At +$0.30/oz, validation requires at least 100 trades, net R > 0, PF_R ≥ 1.05, at least 3 of 5 yearly cohorts with positive net R, and the lower bound of the 95% CI for mean weekly net R strictly above zero. Use 10,000 circular resamples, block length four consecutive Monday-start weeks, seed 297; include every week from 2021-01-04 through 2025-12-29, including zero-trade weeks. Bucket trades by the Monday of their actual exit week.
- At +$0.50/oz, validation net R must remain positive and PF_R ≥ 0.90.
- Any failed gate gives **GAGAL**. Do not open 2026, change the threshold/entry/direction/stop/target/exit/cost, or rerun a gap-fade variant on the same dates.

## Promotion boundary

This is only a historical signal screen. Even a full screen pass would require a one-time 2026 diagnostic and then a separate FundedNext two-phase challenge replay with validated CFD contract sizing, exact spreads/commission/swaps, realistic slippage, floating intraday and overnight PnL, server-day reset, +8%/+5% targets, 5% daily loss, 10% static maximum loss, minimum trading days and Quick Strike rule handling. No funded-ready claim may follow from a signal-screen PASS alone.

## Archival requirements

Save a local runner, the active-row/session-quality audit, qualifying/skipped event audit, trade ledger, annual summary, weekly bootstrap, compact JSON, report and binary decision to the research branch. Local Python only; no GitHub Actions backtest workflow.
