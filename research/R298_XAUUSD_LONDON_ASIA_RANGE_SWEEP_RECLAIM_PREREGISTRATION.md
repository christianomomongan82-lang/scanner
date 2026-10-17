# R298 — XAUUSD London Asia-Range Sweep-and-Reclaim Reversal (LOCKED PREREGISTRATION)

**Status before outcome calculation: PREREGISTERED / PNL NOT YET CALCULATED.**  
Date: 2026-10-17. Research branch: local-backtest/r189-dukascopy-history.

## One-sentence hypothesis
On XAUUSD, when the London morning first sweeps beyond the completed UTC 00:00–05:55 Asian range and the same M5 bar closes back inside that range, the failed breakout predicts reversion toward the Asian-range midpoint over the next four hours.

This is a new intraday range-rejection family, not a weekend reopening gap, cash-open breakout/retest, overnight carry, cross-index breadth, or intraday return-residual candidate. This is one locked candidate, not a parameter search.

## Registered data and cutoff
- Source: cached XAUUSD M5 BID and ASK archive, collection artifact 12031270051 / run 38859918137.
- BID SHA-256: b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575
- ASK SHA-256: b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9
- Data must pair one-to-one by timestamp; no duplicates; valid OHLC ordering; timestamps exactly M5-aligned.
- All signal, event and PnL calculations stop at 2025-12-31 23:55 UTC. Every row timestamped 2026-01-01 UTC or later is excluded before signal construction. No candidate PnL, selection, or diagnostic based on 2026 is permitted unless every historical gate below passes.
- Discovery: calendar years 2016–2020. Validation: calendar years 2021–2025. The validation years are research-contaminated, so even a pass is only eligibility for a separate untouched holdout, not final proof of alpha.

## Pre-outcome data-quality rules
- A BID bar is active if BID high > low or BID open != close; likewise for ASK. A tradable row must be active on both sides. Static quote snapshots are never used as executable candles.
- For each UTC date, the Asian range requires exactly 72 observed timestamps from 00:00 through 05:55 UTC and all 72 paired BID/ASK bars active. Otherwise that date is ineligible.
- Signal bars, delayed-entry bars, all bars in the trade path and the exact time-exit bar must have paired active BID/ASK data. Missing or static bars are audited and cause the affected event/trade to be skipped; no synthetic bars or late-fill substitution.
- High/low and close for signal detection use midpoint fields (BID+ASK)/2. Executions use the relevant side: long entry ASK and long exit BID; short entry BID and short exit ASK.
- For London session definitions, use the IANA Europe/London timezone, so 07:00–10:00 local follows daylight-saving changes correctly. The Asian range uses the same UTC calendar date. Only Monday–Friday London dates are considered.

## Frozen signal, entry, stop and target
1. Calculate the Asian range from the active midpoint bars starting 00:00–05:55 UTC: range high, range low, range width, and midpoint.
2. Search the London-local interval [07:00, 10:00) for the first qualifying M5 bar.
   - SHORT sweep-and-reclaim: midpoint high >= Asian high + 0.10 × Asian range width, while midpoint close is inside the Asian range (Asian low <= close <= Asian high).
   - LONG sweep-and-reclaim: midpoint low <= Asian low − 0.10 × Asian range width, while midpoint close is inside the Asian range.
   - If both directions qualify on the same bar, exclude that date as ambiguous. If both directions qualify on different bars, only the earliest is eligible; no second trade that date.
3. The signal is known only when the signal M5 bar closes. To model a five-minute manual response delay, execute at the exact open timestamp signal-bar-start + 10 minutes. If that precise timestamp is missing, not M5 aligned, or not a paired active row, skip the signal.
4. At entry, long entry is ASK open and short entry is BID open. The long stop is the signal bar BID low; the short stop is the signal bar ASK high. No adjustable stop buffer is permitted. The profit target is the Asian-range midpoint.
5. A trade is eligible only when the stop is on the adverse side of entry, the target is on the favorable side of entry, and planned reward/risk to the midpoint is at least 1.00. This is a fixed eligibility rule, not a tunable parameter.
6. Initial risk per ounce R$ is the absolute entry-to-stop price distance. At most one position is entered per UTC date and no overlap is allowed.
7. Starting from the entry M5 bar, use executable-side BID/ASK OHLC. Long stop triggers when BID low <= stop; long target triggers when BID high >= target. Short stop triggers when ASK high >= stop; short target triggers when ASK low <= target. If the same bar touches stop and target, stop wins conservatively. If the bar opens through the stop, fill at that adverse open; if it opens through the target, fill at the favorable open; otherwise fill at the level.
8. If neither level has triggered, close at the exact bar open four hours after entry. The exact exit row must be active on both sides; otherwise the trade is excluded before PnL scoring. There is no discretion, trailing stop, scale-out, or second signal.
9. Baseline realized trade R subtracts observed-side execution effects already embedded in BID/ASK fills. Add separate extra friction stresses of $0.00, $0.10, $0.30 and $0.50 per ounce round trip; at each stress, net R = (side-correct price PnL − extra cost per ounce) / initial price risk. These dollar-per-ounce stresses are modeled, not verified broker fees.

## Frozen evaluation and gates
Report event counts, data-quality skips, completed trades, win rate, gross/net R, PF_R, closed-trade max drawdown in R, exit type, long/short counts, holding time, annual cohorts, and performance at every locked friction level. Bootstrap weekly net R for validation on all 261 Monday-start weeks across 2021–2025, including zero-trade weeks; circular four-week moving blocks, 10,000 resamples, seed 298.

Candidate is **ELIGIBLE FOR A SEPARATE HOLDOUT ONLY if every hard gate passes**:
- Discovery (2016–2020) at +$0.30/oz: at least 75 completed trades, positive net R, PF_R >= 1.05, and at least 3 of 5 calendar years with positive net R.
- Discovery at +$0.50/oz: positive net R and PF_R >= 0.90.
- Validation (2021–2025) at +$0.30/oz: at least 100 completed trades, positive net R, PF_R >= 1.05, and at least 3 of 5 calendar years with positive net R.
- Validation four-week block-bootstrap 95% confidence interval lower bound for weekly net R must be strictly above zero.
- Validation at +$0.50/oz: positive net R and PF_R >= 0.90.
- No hard-gate averaging; one failed gate means the whole candidate is GAGAL. After a failure, do not change sweep threshold, session hours, target, stop, minimum reward/risk, delay, or holding period on these dates; do not reverse direction as a rescue. Do not open 2026 or run a funded-account replay after failure.

## Known limitations
The archive is historical CFD-style M5 BID/ASK and does not prove funded-broker fills, slippage, commissions, swaps, contract sizing, margin, or account-equity behavior. A candidate that passes this screen would still require broker-specific execution verification and a separate equity-aware FundedNext two-phase challenge replay. Passing point-estimate PF alone is insufficient.
