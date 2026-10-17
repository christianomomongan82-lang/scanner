# R296 Preregistration — XAUUSD Weekend-Reopening Gap Continuation

**Candidate ID:** `R296_XAUUSD_WEEKEND_GAP_CONTINUATION`  
**Status:** locked before any candidate outcome/PnL calculation  
**Date:** 2026-10-17  
**Hypothesis family:** weekly closure / reopening price discovery, not an intraday indicator, cross-index breadth, opening-range breakout, or overnight carry rule.

## Economic hypothesis

A large weekend reopening gap in gold may reflect repricing of news and hedging demand accumulated while the market was closed. If that information is not fully absorbed by the first 10 minutes of resumed trading, price may continue in the gap direction rather than immediately fill it. This candidate tests only the continuation direction. The EURUSD weekend-gap fade experiment R282 was **data-ineligible and evaluated zero trades**, so it does not provide evidence for or against continuation on XAUUSD. Do not test the opposite direction as a post-result rescue if this locked continuation hypothesis fails.

## Frozen source and data integrity

Use only the already-collected Dukascopy XAUUSD M5 BID/ASK source from raw-only artifact `12031270051`, collected on the data-only run `38859918137`.

- BID archive SHA-256: `b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575`, 947,326 rows.
- ASK archive SHA-256: `b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9`, 947,326 rows.
- Manifest records synthetic-flat bars disabled, no duplicate timestamps, exact paired BID/ASK timestamp coverage, and gaps left unfilled.
- Refuse calculation unless the actual gzip hashes, row counts and exact paired timestamp equality match the manifest. Do not fill any missing timestamps or use another source.
- Reserve all timestamps from 2026-01-01 onward. **Do not read/calculate 2026 candidate outcomes unless every preregistered discovery and validation gate below passes.** If opened, 2026 is a one-time final diagnostic for this candidate, not a tuning window.
- Dates through 2025 have been seen in other XAU research; this is a family-specific historical screen but not pristine program-level OOS.

## Weekend-event definition

1. Treat source timestamps as M5 bar-open time. Sort raw bars chronologically and convert to UTC.
2. An event exists only where the current bar opens Sunday UTC and the immediately previous raw bar opens Friday UTC, with the exact raw timestamp gap in the predeclared 18 to 60 hours. Keep one event per reopening timestamp. Exclude all other gaps, including midweek missing-data interruptions.
3. Require a valid Friday previous bar and valid Sunday first-open BID/ASK quotes (all OHLC finite and positive, each side OHLC internally consistent, ASK open >= BID open, and exact BID/ASK timestamp alignment). No synthetic quote rows or interpolated prices.
4. Weekend gap reference uses quote midpoints: `G = mid(Sunday first bar open) - mid(Friday previous bar close)`.
5. A gap is eligible only when `abs(G) > 2 * (Friday closing spread + Sunday opening spread)`. This is a locked friction screen, not a threshold fitted to outcomes. Do not fit a quantile, change the coefficient, reverse direction or add discretionary exceptions after seeing results.
6. Signal time is the close of the first Sunday M5 bar (bar opens at T, known at T+5). Enter at the exact next required execution bar open at T+10, representing bar confirmation plus five-minute phone/alert execution delay. If the T+5 or T+10 timestamp is missing on either side, or entry quote is invalid, skip the event. Never substitute a later bar.
7. Direction is continuation: LONG if G > 0; SHORT if G < 0. Direction is locked by the original weekend gap, not by movement after reopening.
8. Let the initial risk distance `D = abs(G)` in USD/oz. Use a symmetric 1R stop and 1R target around the actual entry fill: LONG stop = entry ASK - D and target = entry ASK + D; SHORT stop = entry BID + D and target = entry BID - D. Long stops/targets are triggered/fill-checked against BID OHLC; short stops/targets against ASK OHLC.
9. Begin checking exits at the entry bar. A stop has priority if stop and target both touch in one M5 bar. If the opening quote gaps past a stop, fill at that worse open. If an opening quote gaps beyond target, fill at that executable open; otherwise target fills at its level when touched. If neither level is hit, force-flat at the exact open of the bar starting four hours after the first Sunday bar opens (T+4h); skip the event if that exact timestamp or required executable quote is absent. No overnight position beyond this fixed 4-hour window after reopening.
10. Trade net R equals direction-signed executable price PnL minus added round-trip cost, divided by D. Model additional costs of $0.00, $0.10, $0.30 and $0.50 per ounce; primary screening cost is +$0.30/oz beyond observed BID/ASK. For shorts, use BID entry and ASK exits. Report gross and net PnL, R, PF_R, win rate, max drawdown in R, holding time, stop/target/time-exit mix, cost sensitivity and annual cohorts.
11. One trade maximum per weekend event. No stacking, compounding, trailing stop, target optimization, news filter, or parameter grid. No position is opened if gap/entry already invalidates the 1R order logic.

## Locked chronological partitions and binary promotion gates

- **Discovery:** reopening events 2016-01-01 through 2020-12-31.
- **Validation:** reopening events 2021-01-01 through 2025-12-31. This is exploratory relative to the whole program because XAU data has been used in other strategy studies.
- **2026 final diagnostic:** 2026-01-01 through 2026-10-15, still sealed unless all historical gates pass.
- At +$0.30/oz extra cost, discovery must have: at least 100 closed trades; net R > 0; PF_R >= 1.05; at least 3 of 5 annual cohorts with positive net R. At +$0.50/oz discovery net R must remain positive and PF_R >= 0.90.
- At +$0.30/oz validation must have: at least 200 closed trades; net R > 0; PF_R >= 1.05; at least 3 of 5 annual cohorts with positive net R; four-week circular block-bootstrap 95% CI lower bound for mean weekly net R strictly > 0 (10,000 resamples, seed 296, using all Monday-start weeks including zero-trade weeks). At +$0.50/oz validation net R must remain positive and PF_R >= 0.90.
- Bucket weekly net R by exit-week Monday. Include each Monday-start week in validation from 2021-01-04 through 2025-12-29, including weeks with no trades; bootstrap circular blocks of four consecutive weeks.
- Any failed discovery or validation gate means **GAGAL**: do not inspect any 2026 strategy outcome, do not adjust the $0.30 friction screen, D/stop/target, direction, entry delay or time exit, and do not test the opposite (gap-fade) side on the same windows.
- A full historical screen pass permits only the one-time 2026 diagnostic; it does not itself make the strategy funded-ready.

## Promotion boundary

All data have BID/ASK but that does not certify FundedNext's contract sizing or actual account-specific commission, spread, slippage, swap, margin or server-day treatment. Even if this strategy passes all signal gates, the project still requires a separate account-equity replay implementing the actual two-phase +8%/+5% targets, 5% daily loss (including floating PnL and charges), 10% static max loss, server reset, minimum trading days, and realistic execution before it can be called funded-ready.

## Required archived outputs

Store the local runner, exact input hashes, data-quality audit, skipped event ledger, candidate trade ledger, per-year summaries, compact JSON, weekly bootstrap result, final report and binary verdict. All calculations run in local Python only. No GitHub Actions backtest workflow may be created or dispatched.
