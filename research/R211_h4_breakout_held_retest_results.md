# R211 — H4 55-Bar Breakout Followed by a Held Retest

**Final verdict: REJECT.**  
Workflow run: https://github.com/christianomomongan82-lang/scanner/actions/runs/38162790430  
Audit artifact: `R211-h4-breakout-retest-audit` (90-day retention).

## Locked rule

A completed H4 close must break above the maximum high of the previous 55 completed H4 bars. Within the next 1–3 completed H4 bars, price must touch or cross that breakout level and close back above it. Enter the first non-flat M5 BID bar at least five minutes after the retest H4 bar closes, before the following H4 bar closes. Stop at the retest H4 low; target is 2R. One active position per instrument.

H4 candles are built from exactly four consecutive H1 BID bars using UTC 00/04/08/12/16/20 boundaries; incomplete bins are skipped. No indicators or parameter grid were used.

## Data and execution checks

- Ten indices; H1/M5 snapshots validated.
- Prefix-causality/truncation check passed for all completed H4 decision points on every instrument (23,096–23,371 checks per asset; Small Cap starts later with 17,764).
- UTC H4 aggregation and incomplete-bin exclusion test passed.
- 2,771 trades were emitted: 1,708 SL, 950 TP and 113 gap-through-stop exits. No end-of-day exit or same-timestamp entry/exit anomaly.
- Costs are modeled at 1 and 2 price bps round-trip. They are not measured broker spread, commissions or live slippage.
- Discovery 2017–2021; forward 2022–2025; common OOS cutoff 2026-10-09 20:00 UTC.

## Full instrument ledger

| Instrument | Discovery closes | Discovery PF @ 1bp | Discovery PF @ 2bp | Forward closes | Forward PF @ 1bp | Forward PF @ 2bp | Worst forward cohort PF @ 1bp | OOS closes | OOS PF @ 1bp | OOS PF @ 2bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| USA 500 / S&P 500 | 190 | 0.9040 | 0.8286 | 122 | 0.9550 | 0.8483 | 0.5997 | 19 | 1.3245 | 1.2108 |
| USA 100 Tech / Nasdaq 100 | 188 | 0.9381 | 0.8630 | 119 | 0.7719 | 0.7161 | 0.3448 | 23 | 0.2069 | 0.1135 |
| USA 30 / Dow Jones | 165 | 0.6988 | 0.4869 | 114 | 0.9388 | 0.8205 | 0.6291 | 10 | 0.4480 | 0.4232 |
| Australia 200 | 149 | 1.0043 | 0.9214 | 118 | 0.8448 | 0.7887 | 0.5802 | 14 | 0.2828 | 0.2612 |
| Japan 200+ | 143 | 0.7454 | 0.6862 | 120 | 1.0547 | 0.9479 | 0.5145 | 18 | 0.6034 | 0.5861 |
| Germany 40 / DAX | 123 | 1.0549 | 0.9726 | 127 | 1.1658 | 1.0520 | 0.7567 | 16 | 1.1531 | 1.1089 |
| FTSE 100 | 116 | 1.1200 | 1.0339 | 118 | 0.8197 | 0.7591 | 0.4102 | 22 | 0.9848 | 0.9140 |
| EU Stocks 50 | 93 | 0.1279 | 0.0675 | 81 | 1.0165 | 0.9424 | 0.4867 | 11 | 0.6015 | 0.5642 |
| France 40 / CAC 40 | 93 | 1.0542 | 0.9582 | 72 | 0.7530 | 0.7152 | 0.6680 | 9 | 0.9626 | 0.7190 |
| US Small Cap 2000 | 91 | 1.4842 | 1.4047 | 93 | 0.6916 | 0.6512 | 0.4826 | 15 | 1.2677 | 1.2063 |

The worst cohort is the lowest 2022–2025 entry-year PF at 1 bp among years with at least five closed trades.

## Locked selection and verdict

Discovery-only eligibility required at least 30 closed trades and PF >= 1.00 at 2 bps. The eligible instruments were FTSE 100 and US Small Cap 2000. Selection favored the highest discovery trade count, with PF@2bps as tie-breaker, so **FTSE 100** was selected (116 discovery closes, PF 1.0339 at 2 bps).

Forward: 118 closes, PF **0.8197 at 1 bp** and **0.7591 at 2 bps**; worst eligible forward entry-year cohort PF was **0.4102**. This decisively fails the locked PF, cohort and consistency gates. US Small Cap is not substituted based on forward results; its forward PF is also poor.

**Conclusion: reject this H4 breakout-retest rule as tested.** No claim of live/funded readiness is justified; bid-only costs remain modeled rather than verified executable costs.
