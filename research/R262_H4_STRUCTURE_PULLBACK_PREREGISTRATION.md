# R262 H4 Structural Pullback Continuation — Preregistration

Date locked: 2026-10-16  
Status before run: preregistered; results not yet viewed.  
Execution boundary: raw data from the existing Dukascopy BID/ASK artifact; all signal/PnL calculations in local Python only. No GitHub Actions backtest.

## Question

Can a slower, price-structure trend-pullback rule produce an edge that survives forward data, extra cost, and a few minutes of manual entry latency better than R189's M1 setup?

This is a single candidate test, not a parameter sweep. A failed result will be closed without tuning.

## Data and bars

- Input: the stored Dukascopy EURUSD M1 BID/ASK data, 2016-01-01 through 2025-12-31.
- For Sunday, remove closed-market flat placeholders before the first non-flat BID M1 candle of that Sunday. Retain weekdays and Sunday candles from that first active quote onward; do not synthesize bars. Exclude empty/flat H4 bars from structural indexing. Keep actual timestamp gaps.
- Aggregate UTC-aligned H4 OHLC on each quote side separately. Signals use completed BID H4 bars; entries and exits use correct quote sides.
- Historical partitions are fixed: discovery 2016–2020, validation 2021, forward 2022–2025. There is no 2026 data in this 2016–2025 artifact; 2026 OOS is required before any final promotion if the candidate passes the historical screen.

## Locked signal

At the close of active H4 bar i, compare two non-overlapping five-bar segments:

- Older segment: bars i-9 through i-5.
- Recent segment: bars i-4 through i.

Long setup:
1. Recent segment maximum High is strictly above the older segment maximum High.
2. Recent segment minimum Low is strictly above the older segment minimum Low.
3. The last two closes show a two-bar pullback: Close[i] < Close[i-1] < Close[i-2].

Short setup is the exact mirror:
1. Recent segment maximum High is strictly below the older segment maximum High.
2. Recent segment minimum Low is strictly below the older segment minimum Low.
3. The last two closes rise: Close[i] > Close[i-1] > Close[i-2].

- Signal decision uses only completed bars.
- Suppress a new same-direction or opposite-direction signal if a retained signal occurred within the prior 4 active H4 bars; retain the earliest eligible candidate in each 4-bar cluster.
- One position at a time; ignore signals whose entry time falls before or at the existing trade's exit.

## Execution and risk geometry

- Baseline entry: next active H4 bucket's first available M1 open. Long enters at ASK; short at BID.
- Latency audit: compare 0, +1, +3, and +5 minutes after the ideal entry time using actual M1 quote opens at those timestamps. Do not assume fill at the H4 open if the latency-shifted time has no corresponding quote.
- Entry spread cap: 1.5 pips measured at actual fill time.
- Stop: long at the lowest BID Low across the last 3 completed signal H4 bars; short at the highest BID High across those bars. A stop not on the risk side of the entry is rejected.
- Target: 1.5 times the initial entry-to-stop distance.
- No trailing stop and no scaling/partial exit.
- Management runs on subsequent M1 BID/ASK OHLC to avoid using H4-bar extremes that may have occurred before a delayed fill. Stop/target crossed at bar open fill at that open; if both SL and TP are touched inside one M1 bar, use stop-first.
- Time stop: first available active-market M1 open at or after 48 elapsed hours from entry. Never exit using Sunday closed-market placeholder bars.
- Additional cost stress beyond quote-side BID/ASK: 0, 0.5, 1, and 2 pips per completed trade.

## Metrics and gates

Report trade count, PF, net pips, win rate, maximum trade-equity drawdown in pips, median holding time, yearly cohort results, entry spreads, gap/skip/overlap counters, and latency sensitivity. Use a four-week circular moving-block bootstrap (5,000 reps) on forward weekly net PnL at +1 pip extra cost.

Primary screen: at least 100 trades in forward 2022–2025, forward PF >= 1.10 at +1 pip, and a 95% bootstrap confidence interval for mean weekly net PnL that excludes zero on the positive side. Annual stability is a diagnostic; flag any year with >=30 trades and PF < 0.90 at +1 pip. For execution fit, report whether +5-minute latency retains PF >=1.10 at +0.5 pip extra cost and whether annual results remain stable.

No parameter changes after seeing any discovery, validation, forward, or latency result. If the locked candidate fails, mark R262 failed and move to a distinct hypothesis instead of rescuing it.

## Limitations

This is a Dukascopy same-feed study, not a reproduction of the absent original HistData archive. M1 OHLC does not reveal tick-exact intrabar sequencing. Live broker commission, actual live slippage, swap, funded-provider daily/max loss mechanics, and Quick Strike are not established by this study.
