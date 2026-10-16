# R276 — Synchronized US cash-open breadth router

**Historical screen: PASS. Funded-promotion decision: GAGAL / NOT PROMOTED.**

## Locked test
Parent experiments R205/R206 were crossed: first opening-range breakouts across the four US index CFDs, with a child trade allowed only when at least 3 of 4 indices broke their ranges in the same direction at the exact same completed M5 timestamp. Entries use exact T+10-minute execution (M5 bar-open timestamp + five minutes to signal close + five-minute manual delay). Stop at opposite opening-range edge; fixed 2R target; one position per asset; modeled round-trip costs of 1/2 price bps. No thresholds were retuned.

Data: Dukascopy M5 BID OHLC snapshots from R205 artifacts 11709864394 (USA500), 11710370389 (USATECH), 11710730507 (USA30), 11710111254 (USSC2000). USSC2000 begins 2018-08-08; synchronized events before common four-feed coverage are excluded. Data are BID-only and round-trip 1/2 price bps are modeled, not verified broker spreads or commissions. 2022–2025 is research-contaminated; 2026 is diagnostic and has also been repeatedly viewed in this project. No challenge path replay was run.

## Child results
| Period | Trades | PF +1 bp | Net R +1 bp | PF +2 bp | Net R +2 bp |
|---|---:|---:|---:|---:|---:|
| Discovery 2017–2021 | 767 | 1.173 | +84.94 | 1.138 | +69.12 |
| Exploratory forward 2022–2025 | 828 | 1.289 | +147.06 | 1.257 | +132.85 |
| Diagnostic 2026 | 102 | 0.748 | −19.38 | 0.729 | −21.21 |

Four-week weekly-net-R bootstrap on 2022–2025 at +1 bp: mean 0.704R/week; 95% interval [0.166R, 1.269R] (10,000 circular four-week blocks). The child improved mean R per trade over the matched T+10 parent, but its aggregate forward net R (+147.06R) was below the parent (+176.09R) because it traded less often.

## Why not promoted
All locked historical statistical gates passed. However, the candidate also requires a risk-aware challenge-target comparison before promotion; no full two-phase equity-path replay was run. Further, 2026 diagnostic performance turned negative. The child holds too long for the intended funded workflow: median 17.83h, p95 124.63h, maximum 1,439.33h (~60 days). Overnight swap, true BID/ASK/spread and floating daily-loss effects are not modeled. Therefore this is **not a funded-ready strategy** and must not be labeled LULUS for challenge use.

## Evolutionary lesson
The synchronized breadth router improves per-trade expectancy and historical net drawdown versus the matched parent but discards many trades and has a negative later diagnostic. Do not turn a contaminated forward pass into promotion evidence. The next child tested the same signal family with a mandatory same-day flat.
