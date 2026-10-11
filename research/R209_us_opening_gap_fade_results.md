# R209 — US Regular-Session Opening-Gap Fade to Prior Close

**Final verdict: REJECT — no discovery-eligible candidate.**  
Corrected workflow run: https://github.com/christianomomongan82-lang/scanner/actions/runs/38162134502

> Audit note: run 38161910510 is superseded. Its date comparison used a string against a date object, which prematurely terminated exits and produced meaningless all-zero PFs. The corrected run converts each trade's New York session date to a `date` object before comparing it with the M5 timestamp dates. Only the corrected run below is used for this verdict.

## Locked hypothesis

For each valid regular US cash session (09:30–16:00 New York time), use the previous valid session's final 15:55 M5 bar close (the close at 16:00 ET). A trade is considered if the next session's 09:30 M5 open gaps away from that prior close and the first 5-minute candle closes against the gap direction. Enter at the next non-flat M5 open after the first candle closes. Stop at the 09:30 candle extreme (high for a short, low for a long); target the prior valid session close. Require reward/risk >= 2 at entry. If neither stop nor target hits, close the position at 16:00 ET. One candidate per index per NY session date.

Valid RTH sessions require at least 70 M5 bars, an observed 15:55 bar, and at least 60 non-flat bars. Session time is America/New_York including DST. This is raw OHLC; no standard indicators or parameter grid.

## Execution and assumptions

- Instruments: USA 500, USA 100 Tech, USA 30 and US Small Cap 2000.
- Source: Dukascopy M5 BID OHLC.
- Modeled round-trip costs: 1 and 2 price basis points relative to entry. They are stress assumptions, not measured broker spread, commissions or live slippage.
- Discovery: entries 2017–2021, outcomes closed before 2022-01-01.
- Forward: entries 2022–2025, outcomes closed before 2026-01-01.
- OOS: entries from 2026 to common cutoff 2026-10-09 20:15 UTC.
- Source snapshots, compile check and DST boundary check passed.
- Corrected exit audit: 2,041 trades had distinct stop/target/end-of-day outcomes; 1,569 stopped out, 393 reached target, 75 closed at end-of-day, 3 stopped at gap-open. One trade remained open at the end of available data. Exit timestamps are M5 bar timestamps, so a stop/target touched in the entry bar can share the entry bar's timestamp; this does not mean the bar path before entry was observed.

## Result ledger

PF values below include the modeled cost shown in the column. “Worst cohort” is the lowest 2022–2025 entry-year PF at 1 bp among cohorts with at least five closed trades.

| Instrument | Discovery closes | Discovery PF @ 1bp | Discovery PF @ 2bp | Forward closes | Forward PF @ 1bp | Forward PF @ 2bp | Worst cohort PF @ 1bp | OOS closes | OOS PF @ 1bp | OOS PF @ 2bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| USA 500 / S&P 500 | 316 | 0.4639 | 0.2920 | 245 | 0.9916 | 0.8782 | 0.9507 | 35 | 0.5770 | 0.5059 |
| USA 100 Tech / Nasdaq 100 | 257 | 1.0341 | 0.9295 | 202 | 0.9962 | 0.9223 | 0.5202 | 45 | 1.0554 | 0.9582 |
| USA 30 / Dow Jones | 283 | 0.8081 | 0.7049 | 151 | 0.7453 | 0.6715 | 0.4664 | 35 | 0.7082 | 0.6462 |
| US Small Cap 2000 | 133 | 0.6956 | 0.6428 | 143 | 1.3548 | 1.2635 | 0.9363 | 28 | 2.4428 | 2.2884 |

## Selection and verdict

Selection was locked to discovery only: at least 50 discovery closes and PF >= 1.00 at 2 bps; among eligible candidates choose the highest discovery trade count, then PF at 2 bps. **No instrument qualified.** Nasdaq 100 was close at 1 bp, but discovery PF fell to 0.9295 at the required 2 bps. US Small Cap had higher forward PF, but discovery PF was only 0.6428 at 2 bps and it cannot be selected after looking at forward results.

The setup is rejected without parameter tweaking or forward-based replacement. The high OOS PF for Small Cap has only 28 closes and does not override the discovery failure. BID-only modeling is a screening proxy, especially for shorts; no funded/live readiness claim is warranted.

The `R209-opening-gap-audit` artifact on the corrected workflow contains `meta.json`, full trades, annual cohorts, instrument ledger and session diagnostics. Artifact retention: 90 days.
