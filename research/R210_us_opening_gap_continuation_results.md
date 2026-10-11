# R210 — US Regular-Session Opening-Gap Continuation

**Final verdict: REJECT — no discovery-eligible candidate.**  
Corrected workflow run: https://github.com/christianomomongan82-lang/scanner/actions/runs/38162495892

## Locked hypothesis

For each valid regular US cash session (09:30–16:00 New York time), compare its 09:30 M5 open with the previous valid session's final 15:55 M5 close (the close at 16:00 ET). If there is an opening gap and the first 5-minute candle closes in the same direction as that gap, enter at the next non-flat M5 open. Stop at the first candle's low for longs or high for shorts. Target is 2R from entry-to-stop risk. If neither stop nor target hits, close at 16:00 ET. One candidate per instrument per session day.

Valid RTH sessions require at least 70 M5 bars, an observed 15:55 bar, and at least 60 non-flat bars. Session time is America/New_York including DST. Raw OHLC only; no indicators or parameter grid.

## Execution and assumptions

- Instruments: USA 500, USA 100 Tech, USA 30 and US Small Cap 2000.
- Source: Dukascopy M5 BID OHLC.
- Modeled round-trip cost: 1 and 2 price basis points relative to entry. These are stress assumptions, not measured broker spread, commissions or live slippage.
- Discovery: entries 2017–2021, outcomes closed before 2022-01-01.
- Forward: entries 2022–2025, outcomes closed before 2026-01-01.
- OOS: entries in 2026 to common cutoff 2026-10-09 20:15 UTC.
- Snapshot validation, Python compilation and session DST boundary check passed.
- Corrected exit audit: 4,897 trades produced 3,158 stop-loss exits, 1,583 target exits, 153 end-of-day exits and 3 gap-through-stop exits. No mass zero-PF or same-price instant-exit anomaly was observed.

## Result ledger

| Instrument | Discovery closes | Discovery PF @ 1bp | Discovery PF @ 2bp | Forward closes | Forward PF @ 1bp | Forward PF @ 2bp | Worst cohort PF @ 1bp | OOS closes | OOS PF @ 1bp | OOS PF @ 2bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| USA 500 / S&P 500 | 593 | 0.8895 | 0.7573 | 474 | 0.8196 | 0.7178 | 0.5880 | 105 | 0.7960 | 0.6860 |
| USA 100 Tech / Nasdaq 100 | 589 | 1.0551 | 0.9593 | 469 | 0.9567 | 0.8833 | 0.7822 | 87 | 0.8384 | 0.7768 |
| USA 30 / Dow Jones | 602 | 0.9798 | 0.8443 | 481 | 0.7989 | 0.7206 | 0.6569 | 91 | 0.9712 | 0.8776 |
| US Small Cap 2000 | 431 | 0.9295 | 0.8617 | 505 | 0.8864 | 0.8277 | 0.6234 | 95 | 0.8935 | 0.8271 |

“Worst cohort” is the lowest 2022–2025 entry-year PF at 1 bp among cohorts with at least five closed trades.

## Selection and verdict

Selection was frozen on discovery only: at least 50 discovery closes and PF >= 1.00 at 2 bps, then choose the highest discovery trade count and use PF@2bps as tie-breaker. **No instrument qualified.** Nasdaq 100's discovery PF was 0.9593 at 2 bps; the others were lower. All instruments also failed the forward PF gate.

The opening-gap continuation setup is rejected without parameter tweaking or forward-based replacement. BID-only execution is a screening proxy, especially for shorts; this is not evidence of live/funded readiness.

The `R210-opening-gap-continuation-audit` artifact contains `meta.json`, instrument ledger, annual cohorts, all trades and session diagnostics. Retention: 90 days.
