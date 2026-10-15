# R189 Manual-Execution Latency Audit — 2021–2025 Forward Data

Date: 2026-10-16  
**Verdict: NOT PASSED for the current manual phone workflow.** This is an execution-feasibility audit of the already-locked R189/L80 setup. No signal parameter was changed or optimized.

## Method

- Used the same intrabar-aware simulator as the official R189 historical Dukascopy replay: BID/ASK entry and exit sides, open-gap stop fills, stop-first handling when SL/TP collide within an M1 bar, and the existing zero-distance trailing rule.
- The ideal reference entry is the next M1 open after the signal. Latency stress shifts fill by another 1, 3, or 5 M1 bars. Relative to the signal-bar close, that means approximate fills 2, 4, or 6 minutes later.
- Costs of +0.5 and +1.0 pips/trade are additional to the observed BID/ASK execution already reflected in the simulation.
- Forward period: 2021-01-01 through 2025-12-31. Four-week circular moving-block bootstrap, 5,000 repetitions.

This is a deterministic candle-open latency stress, not a tick-perfect reconstruction of a human's actual order placement. It cannot model the exact path between an email alert and the actual fill.

## Forward results

| Additional delay after ideal fill | Extra cost | Trades | PF | Net pips | Max DD (pips) | Bootstrap P(mean weekly PnL > 0) | 95% CI for mean weekly net (pips) |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0 min | +0.5 | 767 | 1.284 | +674.8 | 93.8 | 100.00% | [+1.19, +4.02] |
| 1 min | +0.5 | 768 | 1.225 | +544.1 | 121.7 | 99.36% | [+0.40, +3.79] |
| 3 min | +0.5 | 769 | 1.212 | +509.6 | 171.1 | 99.02% | [+0.29, +3.65] |
| 5 min | +0.5 | 769 | 1.071 | +181.5 | 92.0 | 88.76% | [-0.44, +1.85] |
| 0 min | +1.0 | 767 | 1.114 | +291.3 | 142.5 | 94.22% | [-0.25, +2.50] |
| 1 min | +1.0 | 768 | 1.062 | +160.1 | 198.8 | 78.26% | [-0.99, +2.18] |
| 3 min | +1.0 | 769 | 1.048 | +125.1 | 286.8 | 72.16% | [-1.22, +2.10] |
| 5 min | +1.0 | 769 | 0.926 | -203.0 | 364.8 | 8.38% | [-2.00, +0.35] |

## Annual stability at +0.5 pip extra cost

| Year | Ideal entry | +1 min delay | +3 min delay | +5 min delay |
|---:|---:|---:|---:|---:|
| 2021 | 1.293 | 2.177 | 1.812 | 1.717 |
| 2022 | 1.126 | 1.119 | 1.112 | 1.038 |
| 2023 | 1.218 | 0.973 | 1.038 | 0.949 |
| 2024 | 1.729 | 1.390 | 1.179 | 1.123 |
| 2025 | 1.531 | 1.364 | 1.431 | 1.028 |

## Decision

The project robustness floor is PF 1.10. Ideal next-bar entry at +0.5 pip clears that floor in every forward year, but just one additional M1 bar of delay pulls 2023 below it. With five extra bars of latency, aggregate forward PF is only 1.071 at +0.5 pip and 0.926 at +1 pip, and the bootstrap interval includes zero. At +1 pip, even the zero-delay baseline has PF only 1.114 overall and its confidence interval crosses zero.

The observed R189 trade management is also too fast for reliable manual-phone execution: the official replay reported median holding time of 2 minutes; 30.7% of exits occur in the entry minute and 79.1% within five minutes. These results do not prove the signal has zero edge in every possible automated environment, but they do disqualify it for this user's current several-minute manual entry workflow.

**Final status stays NOT PASSED. Do not tune R189 to recover the results.** The next research step should be a separate candidate whose decision horizon and management are compatible with real manual latency; it must earn its own forward/OOS evidence before we combine it with any other strategy. This is still a Dukascopy feed replay, not an exact reproduction of the missing original HistData archive.