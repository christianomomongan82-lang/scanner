# R189/L80 — Execution Delay Audit (Retrospective, No Tuning)

Audit date: 2026-10-16  
Source calculation: local Python replay produced 2026-10-15 using the saved Dukascopy BID/ASK M1 history.  
**Decision: execution robustness is not established; not funded-ready.**

This is an audit of an already-run R189 replay, not a fresh preregistered performance test and not an exact reproduction of the original HistData run. Rules and parameters were not changed.

## Signal and execution tested

- Locked L80 signal rules; signal hours use a fixed GMT-5 offset, not DST-aware New York time: 03–11 inclusive, excluding 06 and 09.
- Entry at the next M1 open after signal bar; long enters ASK and short enters BID. Additional delay offsets are applied after that ideal fill: 0 / 1 / 3 / 5 minutes. The +5-minute case is approximately six minutes after the signal bar's timestamp/start, i.e. five minutes later than the ideal fill.
- Fixed stop 6 pips, target 18 pips, trailing-to-breakeven activation at +6 pips, time exit at scheduled 60th bar open. BID exits for long positions and ASK exits for shorts.
- Intrabar-aware stress model explicitly checks gaps through the stop/target at bar opens and conservatively checks stop before target when both are touched inside one M1 bar.
- Period reported here is 2021–2025 (not the 2022–2025 period used by the index experiments). Costs below are additional cost layered on top of observed BID/ASK entry/exit pricing.

## Forward 2021–2025 results

| Additional cost | Delay after ideal fill | Trades | PF | Net pips | Max drawdown pips |
|---:|---:|---:|---:|---:|---:|
| 0.5 pip | 0 min | 767 | 1.284 | +674.8 | 93.8 |
| 0.5 pip | 1 min | 768 | 1.225 | +544.1 | 121.7 |
| 0.5 pip | 3 min | 769 | 1.212 | +509.6 | 171.1 |
| 0.5 pip | 5 min | 769 | 1.071 | +181.5 | 92.0 |
| 1.0 pip | 0 min | 767 | 1.114 | +291.3 | 142.5 |
| 1.0 pip | 1 min | 768 | 1.062 | +160.1 | 198.8 |
| 1.0 pip | 3 min | 769 | 1.048 | +125.1 | 286.8 |
| 1.0 pip | 5 min | 769 | 0.926 | -203.0 | 364.8 |

The number of trades varies with delay because the spread cap is checked at the actual delayed entry bar. The stress model had 27, 32, 34 and 28 gap-through fills at delay 0, 1, 3 and 5 minutes, respectively; overlap-skipped trades were zero. The M1 OHLC source cannot reconstruct tick-level execution times.

## Inference at +5-minute delay

Four-week circular block bootstrap over all 261 calendar weeks in 2021–2025, including weeks without trades, 5,000 replications:

| Additional cost | Mean net pips/week | Bootstrap means positive | 95% interval pips/week |
|---:|---:|---:|---:|
| 0.5 pip | +0.695 | 88.76% | [-0.444, +1.849] |
| 1.0 pip | -0.778 | 8.38% | [-1.997, +0.348] |

Both intervals include zero. At +1 pip and five-minute delay, point-estimate expectancy is negative and PF falls below 1.00. At +0.5 pip, the point estimate remains positive but PF is only 1.071 and bootstrap inference is inconclusive. Thus the edge is too execution-sensitive to call verified for manual phone execution.

## Verification boundaries

- Historical Dukascopy BID/ASK feed differs from the missing original HistData/spread files; this is cross-feed replication, not exact R189 reproduction.
- Fixed extra costs are sensitivity assumptions; a verified live broker/prop-firm fill-cost distribution is unavailable.
- Signal-hour rules use fixed GMT-5 and may map differently around daylight-saving changes than the funded platform.
- M1 OHLC cannot establish exact trade-close duration, so Quick Strike's sub-30-second closing restriction is not verified.
- Funded provider's current timezone mapping, DLL/MLL implementation and account-level risk replay remain unverified.

**Status remains: no strategy approved and no funded-ready strategy.** Do not retune R189 from these stress results. Next work should focus on timestamp/platform mapping and exact execution-rule verification, not another performance-optimized variant.
