# R251–R258 — Cumulative Failure Taxonomy

**Status: completed evidence map; all eight paths are closed as failures.** This is descriptive synthesis only. It does not retune, promote, or rank a replacement strategy using forward/OOS outcomes.

## Evidence matrix

All quoted cost-adjusted PF values use the experiment's *additional* execution-cost stress of +1 pip on top of observed BID/ASK where available.

| Round | Family / hypothesis | Forward result | 2026 OOS result | Frequency / principal failure |
|---|---|---:|---:|---|
| R251 | Cross-pair consensus / EURUSD lag catch-up | PF 0.927; 1,499 trades | PF 0.716; 281 trades | 7.18 trades/week forward; turns negative with only +0.5 pip extra cost. Too cost-sensitive, OOS negative. |
| R252 | H1 tail-threshold momentum vs reversal | PF 0.652; 888 trades | PF 0.742; 92 trades | 4.25 trades/week forward; 2021 validation winner did not generalize. |
| R253 | Asian-range close breakout | PF 1.021; 813 trades | PF 1.177; 157 trades | 3.90 trades/week forward; discovery/validation and annual-stability gates failed, bootstrap did not establish positive expectancy. Positive OOS alone cannot rescue it. |
| R254 | Asian-range failed-break fade | PF 0.838; 214 trades | PF 0.573; 39 trades | 1.03 trades/week forward; both expectancy and frequency gates failed. |
| R255 | Rolling-extreme sweep-and-reclaim reversal | PF 0.786; 2,824 trades | PF 0.671; 563 trades | 13.53 trades/week forward; high frequency with materially negative expectancy across all four forward years. |
| R256 | H4 rolling breakout | PF 0.850; 339 trades | PF 0.803; 81 trades | 1.62 trades/week forward; validation, forward, annual-consistency, inference, and OOS gates failed. |
| R257 | H1 range-compression breakout | No candidate qualified for validation | No candidate selected or tested | Zero validation trades for all eight preregistered configurations because compression/breakout grids were invalid across most bars; no edge was established. |
| R258 | H1 24h/120h aligned momentum | PF 0.785; 944 trades | PF 0.889; 135 trades | 4.52 trades/week forward; all forward years negative after +1 pip stress; bootstrap estimated 0.3% probability of positive forward mean. |

## What the failure pattern says

1. **Frequency was usually not the binding constraint.** R251, R252, R253, R255, and R258 generated multiple trades per week yet failed profitability or robustness. Increasing frequency by itself is not a research objective.
2. **Small gross edges are fragile to execution costs.** R251 became negative with +0.5 pip additional cost; R253 failed its forward robustness gates; R258's forward PF was already 0.832 before the +1 pip stress and 0.785 after it. Observed BID/ASK spread is not a verified substitute for broker commissions or live slippage.
3. **Validation-period winners often failed later.** R252 was selected on 2021 validation yet performed poorly during 2022–2025 and 2026. R253's positive 2026 OOS does not compensate for failed discovery/validation and annual-stability gates.
4. **The families tested so far do not nominate a ready replacement.** Trend/momentum, cross-pair lag, range breakout, failed-break fade, and sweep/reclaim all failed their predeclared acceptance gates. R257 produced no eligible validation sample at all.
5. **Do not re-tune these exact rules against their failed forward/OOS intervals.** Any new hypothesis must have a distinct rationale, preregistered conditions and gates, actual quote-side execution, cost stress, period-separated results, and a binary verdict.

## Implication for the next work item

Prioritize R189's reproducibility gap before inventing another FX signal. Its prior 2016–2025/2021–2025 aggregate is not independently verified because the exact HistData M1 archive, spread file, and chronological trade ledger were absent from the repository. The independent 2026 Dukascopy BID/ASK test is useful evidence but not a reproduction of those missing inputs. A separate locked cross-feed replay may test whether the *same R189 rules* exhibit similar behavior on Dukascopy 2016–2025; label that honestly as a cross-feed replication, not as exact reproduction. R189 also remains unsuitable for a demonstrated funded pass until sub-30-second Quick Strike compliance and the applicable funded execution/risk rules can be verified.
