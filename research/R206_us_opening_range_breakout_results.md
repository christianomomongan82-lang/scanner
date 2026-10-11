# R206 — US Cash-Session 30-Minute Opening-Range Breakout

**Verdict: REJECT.** Workflow: https://github.com/christianomomongan82-lang/scanner/actions/runs/38161054155

## Locked hypothesis

On each New York session date, define the opening range from the six M5 bars opening at 09:30, 09:35, 09:40, 09:45, 09:50 and 09:55 ET. Require all six bars and at least four non-flat observations. After 10:00 ET, take only the first M5 close beyond the range high or low, with entry at the next non-flat M5 open. Stop at the opposite opening-range edge and target 2R. One attempt per instrument per session date; only one position at a time per instrument. Exit uses BID M5 OHLC, stop-first handling, gaps through stops at the open, and no time stop.

Session conversion uses `America/New_York`, including daylight saving time. No standard indicators are used.

## Execution and validation

- Universe: USA 500, USA 100 Tech, USA 30 and US Small Cap 2000.
- Source: Dukascopy M5 BID OHLC.
- Modeled round-trip costs: 1 and 2 price basis points relative to entry; these are stress assumptions, not measured spread/commission/slippage.
- Discovery: entries 2017–2021, with exits before 2022-01-01.
- Forward: entries 2022–2025, with exits before 2026-01-01.
- Common OOS cutoff: 2026-10-09 20:15 UTC.
- Python compilation, DST boundary checks, and all four source snapshot validations passed.
- Costs are modeled on BID-only bars. This is a screening proxy, especially for shorts; it is not actual bid/ask execution.

## Instrument ledger

| Instrument | Discovery closes | Discovery PF @ 1bp | Discovery PF @ 2bp | Forward closes | Forward PF @ 1bp | Forward PF @ 2bp | Worst eligible forward entry-year PF @ 1bp | OOS closes | OOS PF @ 1bp | OOS PF @ 2bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| USA 500 / S&P 500 | 935 | 1.0289 | 0.9829 | 713 | 1.2130 | 1.1659 | 1.0574 | 144 | 0.8585 | 0.8246 |
| USA 100 Tech / Nasdaq 100 | 794 | 1.0714 | 1.0413 | 630 | 1.1746 | 1.1467 | 1.0714 | 117 | 1.0124 | 0.9908 |
| USA 30 / Dow Jones | 850 | 0.9563 | 0.9184 | 601 | 0.9011 | 0.8721 | 0.8129 | 114 | 0.8931 | 0.8664 |
| US Small Cap 2000 | 485 | 1.0846 | 1.0636 | 571 | 1.0592 | 1.0403 | 0.9389 | 112 | 0.7999 | 0.7827 |

## Locked selection and verdict

Selection used discovery results only: among instruments with at least 50 closed discovery trades and PF >= 1.00 at 2 bps, choose the highest number of discovery closes, then PF at 2 bps as tie-break. This selected **USA 100 Tech / Nasdaq 100** (794 closes; discovery PF 1.0413 at 2 bps).

Forward result: **630 closed trades**, PF **1.1746 at 1 bp** and **1.1467 at 2 bps**. The worst eligible forward entry-year cohort PF at 1 bp was **1.0714**. OOS 2026 had 117 closes, PF 1.0124 at 1 bp and 0.9908 at 2 bps.

The candidate fails the locked forward PF >= 1.15 gate at 2 bps (1.1467) and OOS performance is weak. Verdict is **REJECT**, even though trade frequency is high and other forward metrics are close. No other index is substituted based on forward outcomes.

No funded/live readiness claim is justified. Actual bid/ask execution, broker commissions and live slippage remain unverified. The GitHub Actions artifact `R206-opening-range-audit` contains `meta.json`, full instrument ledger, annual entry cohorts, all trades and opening-range session diagnostics.
