# R274 Pre-registration — XAUUSD M5 impulse follow-through

**Status: LOCKED before R274 signal/PnL calculation.** Date: 2026-10-16.

## Parent lineage and motivation

- New hypothesis family relative to failed R272/R273 fade/pullback-context routers: follow-through after a large, decisive single M5 price impulse, not a 12-hour trend-pullback router, failed-range fade, daily breakout or opening-range breakout.
- Inherited only execution/data controls: real matched Dukascopy BID/ASK; preserve missing bars; executable-side fills; T+10 minutes from signal-bar open (five minutes after signal close); same-day flattening at the 16:45 New York quote; stop-first intrabar handling and adverse stop-gap fills.
- Motivation: R189's minute-scale signal lost robustness with several-minute manual delay. R274 tests a slower M5 impulse horizon and a fixed holding/risk structure, without claiming the old signal block itself is proven. This is a new locked hypothesis, not a retune of R189, R272 or R273.

## Data, splits and causality

- Source: corrected raw-only Dukascopy XAUUSD M5 BID/ASK artifact `12031270051`; 2016-01-01 inclusive to 2026-10-16 exclusive UTC. Loader must validate source manifest, row counts, SHA-256 values, exact timestamp pairing and `include_synthetic_flat_bars=false`. Missing bars are never filled.
- Discovery: 2016–2020. Historical validation: 2021–2025 (program-level research-contaminated; only a screen, never standalone promotion-grade OOS). Candidate-specific 2026-01-01 through 2026-10-15 stays unopened unless every historical gate passes.
- For signal bar t, A is the median BID high-low range of the previous 144 completed M5 bars. The current signal bar is excluded from A. Context and signal bar must sit within complete five-minute history for the rolling A calculation; no missing bar is synthesized.
- Signal bar open must be on a weekday from 06:00 to 15:50 America/New_York.

## Locked trigger

At the close of signal bar t, define range = BID_high[t] - BID_low[t], body = abs(BID_close[t] - BID_open[t]). Require range >= 2.00*A, body >= 0.80*A, and body/range >= 0.65.

- LONG if BID_close[t] > BID_open[t] and (BID_high[t] - BID_close[t])/range <= 0.20.
- SHORT if BID_close[t] < BID_open[t] and (BID_close[t] - BID_low[t])/range <= 0.20.
- No ER filter, no trend indicator, no breakout filter, no second trigger, and no parameter sweep.

## Entry, stop, target and exits

- Signal bar timestamp is its open time T. Decision occurs at T+5; additional manual execution delay is five minutes, so entry is the open at T+10 (index t+2), only if both intervening exact five-minute intervals exist.
- LONG enters ASK; SHORT enters BID. LONG stop is signal bar BID low; SHORT stop is signal bar ASK high. Risk distance must be positive and between 0.50*A and 2.00*A. Fixed target is 1.50R from actual delayed entry.
- If delayed entry's executable quote has already crossed stop or target, skip the signal. Reject a missing entry interval, missing same-day cutoff, nonpositive reward, or invalid risk.
- Stop and target are monitored on BID OHLC for longs and ASK OHLC for shorts. Stop has priority if both are touched within a candle. A stop gap fills at the worse opening executable quote; target fills at target price when touched.
- One accepted trade per New York session day and no overlapping trades. Force-flat at the executable opening quote of 16:45 New York if present; never read the 16:45 candle's later high/low. If no exact 16:45 bar exists, use the last valid close at or before the cutoff. No overnight holding.
- Add round-trip cost sensitivity of $0.00, $0.10, $0.30 primary, and $0.50 per ounce beyond observed BID/ASK. No scaling, trailing stop, news filter or parameter search.

## Required outputs and locked gates

Report signal count, accepted trades, rejected-fill reasons, net R, PF, mean/median R, win rate, year/month results, exit mix, and four-week circular bootstrap of weekly net R with 10,000 replicates and seed `2742026`. Compare cost sensitivities on the same locked trade stream.

All historical gates must pass before 2026 is opened:

1. Discovery 2016–2020: at least 100 closed trades and net R > 0 at +$0.30/oz.
2. Discovery four-week block-bootstrap lower 95% bound for mean weekly net R > 0 at +$0.30/oz.
3. Validation 2021–2025: at least 200 closed trades and net R > 0 at +$0.30/oz.
4. Validation net R remains > 0 at +$0.50/oz.
5. At least 3 of 5 validation calendar years are positive at +$0.30/oz.

If any gate fails, **R274 = GAGAL** and do not inspect 2026 or change any threshold. If all pass, a separate run may read the reserved 2026 period once; passing the signal screen alone is not funded-ready and does not permit a challenge replay until verified costs and account rules are modelled.