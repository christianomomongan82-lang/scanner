# R277 — Same-day-flat synchronized cash-open breadth router

**Verdict: GAGAL.** The structural change removes overnight holding, but fails three preregistered gates.

## Locked test
The same 3-of-4 synchronized, same-direction first opening-range breakout on USA500, USATECH, USA30 and USSC2000. Entry T+10, stop at opposite opening-range edge, 2R target, forced liquidation at the exact 16:00 New York M5 bar **open** if neither stop nor target triggered earlier. The 16:00 bar's high/low are not read. Missing exact close timestamps are skipped.

Data: Dukascopy M5 BID OHLC snapshots from R205 artifacts 11709864394 (USA500), 11710370389 (USATECH), 11710730507 (USA30), 11710111254 (USSC2000). USSC2000 begins 2018-08-08; synchronized events before common four-feed coverage are excluded. Data are BID-only and round-trip 1/2 price bps are modeled, not verified broker spreads or commissions. 2022–2025 is research-contaminated; 2026 is diagnostic and has also been repeatedly viewed in this project. No challenge path replay was run.

## Child results
| Period | Trades | PF +1 bp | Net R +1 bp | PF +2 bp | Net R +2 bp |
|---|---:|---:|---:|---:|---:|
| Discovery 2017–2021 | 842 | 1.035 | +13.08 | 0.989 | −4.39 |
| Exploratory forward 2022–2025 | 969 | 1.187 | +71.25 | 1.139 | +54.23 |
| Diagnostic 2026 | 121 | 0.916 | −3.73 | 0.872 | −5.84 |

Forward annual cohorts at +1 bp: 2022 PF 1.352 (+45.17R); 2023 1.305 (+23.61R); 2024 **0.794 (−18.36R)**; 2025 1.240 (+20.83R). Weekly-net-R bootstrap at +1 bp: mean 0.341R/week, 95% interval [−0.116R, 0.793R], 10,000 circular four-week blocks.

## Locked gate failures
1. Discovery PF at +2 bp is 0.989 (<1.00).
2. The 2024 annual cohort is negative at +1 bp (PF 0.794).
3. The bootstrap interval's lower bound is below zero.

## Evolutionary lesson
The same-day flat fixes R276's excessive duration, but the broad long/short router still fails discovery robustness and annual inference. No challenge replay and no tuning. The negative 2026 diagnostic and BID-only modeled-cost limitations further argue against promotion.
