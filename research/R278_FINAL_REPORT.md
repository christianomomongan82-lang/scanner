# R278 — Long-only synchronized cash-open breadth router

**Verdict: GAGAL.** The child is profitable in the repeatedly inspected 2022–2025 interval, but fails the locked discovery-cost robustness gate and is negative in diagnostic 2026.

## Locked test
Only upper opening-range breakouts are traded (lower/short signals ignored), and at least three of four U.S. index CFDs must produce their first upper breakout on the exact same completed M5 timestamp. Entry is exact T+10; stop is the opening-range low; fixed target 2R; force-flat at the exact 16:00 New York bar open. Same-day flat means no overnight exposure.

Data: Dukascopy M5 BID OHLC snapshots from R205 artifacts 11709864394 (USA500), 11710370389 (USATECH), 11710730507 (USA30), 11710111254 (USSC2000). USSC2000 begins 2018-08-08; synchronized events before common four-feed coverage are excluded. Data are BID-only and round-trip 1/2 price bps are modeled, not verified broker spreads or commissions. 2022–2025 is research-contaminated; 2026 is diagnostic and has also been repeatedly viewed in this project. No challenge path replay was run.

## Results
| Period | Trades | PF +1 bp | Net R +1 bp | PF +2 bp | Net R +2 bp |
|---|---:|---:|---:|---:|---:|
| Discovery 2017–2021 | 435 | 0.939 | −11.46 | 0.889 | −21.68 |
| Exploratory forward 2022–2025 | 508 | 1.403 | +69.10 | 1.346 | +60.74 |
| Diagnostic 2026 | 67 | 0.877 | −2.63 | 0.826 | −3.85 |

Forward annual cohorts at +1 bp: 2022 PF 1.582 (+31.45R), 2023 PF 1.527 (+23.07R), 2024 1.413 (+10.17R), 2025 1.089 (+4.39R). Bootstrap at +1 bp: mean 0.331R/week, 95% interval [0.053R, 0.612R] across 209 weeks, 10,000 circular four-week blocks.

## Decision
One locked gate fails: discovery PF after +2 bps is 0.889 rather than the required ≥1.00. Other forward gates pass, but the favorable and contaminated forward period cannot override this failure. The 2026 diagnostic is negative and only 67 trades. No funded challenge replay, no threshold repair, no promotion.
