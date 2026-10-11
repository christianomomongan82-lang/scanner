# R212 — H4 Inside-Bar Mother-Range Breakout

**Final verdict: REJECT.**  
Workflow run: https://github.com/christianomomongan82-lang/scanner/actions/runs/38163175338  
Audit artifact: `R212-h4-inside-bar-breakout-audit` (90-day retention).

## Locked rule

Using complete UTC-anchored H4 bars built from exactly four consecutive H1 BID bars, identify an inside bar whose high is below the previous (mother) H4 bar high and whose low is above the mother bar low. A long signal occurs on the first close above the mother bar high within the next 1–3 completed H4 bars after the inside bar. Entry is the first non-flat M5 BID open at least five minutes after signal close and before the next H4 bar closes. Stop is the inside bar low; target is 2R. Only one position per instrument.

This is a raw-price hypothesis; no standard indicators and no parameter grid were used. H4 aggregation boundaries are 00/04/08/12/16/20 UTC. Incomplete bins with missing H1 source bars are skipped, not synthesized.

## Validation and assumptions

- All ten H1/M5 source snapshot pairs validated.
- H4 UTC aggregation and incomplete-bin exclusion passed.
- Prefix-causality gate passed for every completed H4 decision on each asset (23,096–23,371 checks; Small Cap starts later and had 17,764 checks).
- Modeled round-trip costs are 1 and 2 price basis points relative to entry; these are not measured broker spread, commissions or live slippage.
- Discovery: entries 2017–2021; forward: 2022–2025; OOS cutoff: 2026-10-09 20:00 UTC.

## Result ledger

| Instrument | Discovery closes | Discovery PF @ 1bp | Discovery PF @ 2bp | Forward closes | Forward PF @ 1bp | Forward PF @ 2bp | Worst forward cohort PF @ 1bp | OOS closes | OOS PF @ 1bp | OOS PF @ 2bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| EU Stocks 50 | 385 | 0.9347 | 0.8793 | 311 | 0.9707 | 0.9136 | 0.9156 | 48 | 0.6293 | 0.5954 |
| France 40 / CAC 40 | 368 | 0.9948 | 0.9298 | 312 | 0.8413 | 0.7965 | 0.7235 | 60 | 0.6882 | 0.6121 |
| Germany 40 / DAX | 346 | 0.9475 | 0.9060 | 187 | 1.1747 | 1.1378 | 0.7453 | 45 | 0.7808 | 0.7548 |
| USA 100 Tech / Nasdaq 100 | 342 | 1.0992 | 1.0143 | 198 | 1.1575 | 1.1230 | 0.6773 | 48 | 0.9881 | 0.9655 |
| USA 30 / Dow Jones | 307 | 1.2433 | 1.1387 | 195 | 1.0164 | 0.9708 | 0.6439 | 35 | 0.8806 | 0.8463 |
| FTSE 100 | 300 | 0.8629 | 0.8129 | 227 | 0.9664 | 0.9289 | 0.6584 | 34 | 1.5215 | 1.4662 |
| USA 500 / S&P 500 | 289 | 1.1397 | 1.0642 | 156 | 1.1055 | 1.0651 | 0.7984 | 50 | 1.0459 | 1.0085 |
| Japan 200+ | 278 | 1.1557 | 1.1092 | 217 | 1.2792 | 1.2500 | 0.9746 | 45 | 0.8720 | 0.8597 |
| Australia 200 | 269 | 0.9485 | 0.9063 | 199 | 0.9022 | 0.8750 | 0.7392 | 42 | 0.5256 | 0.5064 |
| US Small Cap 2000 | 194 | 1.0322 | 1.0045 | 234 | 0.8049 | 0.7835 | 0.6696 | 42 | 0.5333 | 0.5214 |

Worst cohort is the lowest forward 2022–2025 entry-year PF at 1 bp among cohorts with at least five closed trades.

## Locked selection and verdict

Discovery-only eligibility required at least 30 closed discovery trades and PF >= 1.00 at 2 bps. Eligible instruments were USA 100 Tech, USA 30, Japan 200+, USA 500 and US Small Cap 2000. Selection prioritized the highest number of discovery closes, then discovery PF at 2 bps as tie-breaker. This selects **USA 100 Tech / Nasdaq 100** (342 discovery closes, PF 1.0143 at 2 bps).

Forward: 198 closes, PF **1.1575 at 1 bp** and **1.1230 at 2 bps**; worst eligible forward entry-year cohort PF was **0.6773**. It fails the 2-bps forward PF requirement (>=1.15) and worst-cohort requirement (>=1.00). OOS 2026 PF was 0.9881 at 1 bp and 0.9655 at 2 bps.

**Conclusion: reject the inside-bar breakout rule as tested.** Do not replace the selected candidate with Japan 200+ or another asset based on forward results. These are bid-only screening simulations; actual bid/ask execution, broker commissions and live slippage remain unverified. No funded/live readiness is established.
