# R264 U.S. Cash-Open Gap-Fade to Prior Close — Preregistration

Date locked: 2026-10-16
Status: locked before calculation. This is a mean-reversion hypothesis, distinct from R263's opening-range breakout.

## Question
After a sufficiently large U.S. cash-session opening gap, does a first M5 candle that closes against the gap predict a move back toward the prior RTH close? Does it retain expectancy with +5-minute execution delay and fixed costs?

## Data
- Use existing GitHub-stored USA500 and USATECH BID-only M5 snapshots from /mnt/data/r205_index_data/.
- Data runs 2016-01 through 2026-10-09, but fixed evaluation partitions are discovery 2016–2020, validation 2021, forward 2022–2025.
- Session date and times use America/New_York, including DST. No ASK-side bars exist in this artifact; all transaction costs are fixed sensitivity assumptions, not measured quoted spreads.

## Locked rules
1. Find each session's opening M5 bar starting at 09:30 ET and the previous available U.S. RTH session's 15:55 ET bar close (the 16:00 close). The gap is (today's 09:30 open / prior RTH close - 1) * 10,000 in bps.
2. Require an absolute opening gap of at least 25 bps.
3. Confirmation is the first M5 candle of the session: for a positive gap, it must close below its open; for a negative gap, it must close above its open. No other confirmation or indicator.
4. Positive gap plus bearish first candle: enter short. Negative gap plus bullish first candle: enter long.
5. Ideal entry is the 09:35 ET M5 open. Latency sensitivity enters at the exact 09:40 ET M5 open (+5 minutes after ideal fill). Missing timestamps are skipped, never substituted.
6. Stop is the first M5 candle's high for shorts and low for longs. Target is the previous RTH close, i.e., the gap-fill price.
7. At the actual fill, require the target to be ahead in the trade direction and reward/risk >= 1.0. If delayed fill no longer meets this criterion, reject the trade.
8. Use BID M5 OHLC for management, with open-gap fills at the open and stop-first handling if stop and target are touched inside the same bar. Start checking price path only on the actual entry bar. One trade max per instrument/session day.
9. No overnight holding. Exit unresolved trade at the close of the 15:55 ET bar.
10. Cost stresses: subtract 2, 4, or 6 bps per trade from gross entry-notional return. +4 bps is the primary gate. These are assumptions because the stored dataset is BID-only.

## Fixed gates
- Discovery 2016–2020; validation 2021; forward 2022–2025.
- Evaluate USA500 and USATECH individually and combined with equal notional per trade.
- Primary gate at +4 bps: combined forward PF >=1.10, at least 100 combined trades, each instrument forward PF >=1.00, and four-week circular moving-block bootstrap 95% CI of mean forward weekly net bps excludes zero positively.
- Manual-latency gate: combined forward PF >=1.10 at +4 bps with +5-minute entry delay and each index PF >0.95.
- If gates fail, close the candidate without tuning and do not inspect 2026 OOS. If gates pass, run 2026 OOS on the same locked rules once.
- Report data quality, no-quote-side limitation, splits, cost and delay sensitivity, annual forward stability, holding-time statistics and bootstrap.

## Execution boundary
Data is sourced from existing GitHub artifacts. Signals/PnL/metrics/verdict are calculated locally in Python only. No GitHub Actions backtest. Do not change thresholds or stops after observing results.

## Promotion limits
This BID-only screen cannot validate live spread, broker commission/slippage, actual alert-to-order delay, provider DLL/MLL implementation, or Quick Strike. Passing the screen would still not mean funded-ready.