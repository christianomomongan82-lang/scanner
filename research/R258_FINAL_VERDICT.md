# R258 — Final Binary Verdict

**Verdict: GAGAL.** Locked EURUSD 24h/120h aligned momentum failed discovery/validation, forward, annual stability, OOS, inference and challenge-replay gates.

Run: https://github.com/christianomomongan82-lang/scanner/actions/runs/38610064013  
Machine-readable results: https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R258_multihorizon_momentum_results.json  
Chronological ledger: https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R258_multihorizon_momentum_trades.csv

## Locked rule

At a completed H1 close, require:
- Absolute 24-hour return at or above the 65th percentile fitted only on 2017–2020.
- The 24-hour return direction agrees with the 120-hour return direction.
- Entry at the next exact H1 open. Long trades use ASK entry/BID exit; shorts use BID entry/ASK exit.
- Stop distance = half the high-low range of the previous 24 completed hourly bars; target = 2R; time exit after 24 hours at the next observed open on or after the horizon.
- One position at a time. Missing hourly bars are not synthesized; stops/targets are evaluated only on observed quote bars, with stop gaps filled at the observed executable open.
- Evaluate extra-cost stresses of 0, 0.5, 1 and 2 pips on top of the observed quote-side spread.

## Data and execution audit

EURUSD H1 BID/ASK from Dukascopy, 2017-01-01 through 2026-10-13. There were 85,170 exact common quote timestamps, zero duplicate timestamps, zero invalid OHLC rows, and zero negative open spreads. The 582 missing/incomplete hourly grid points were preserved rather than filled.

The corrected final engine emitted 2,065 closed trades (787 ordinary stops, 1 stop-gap exit, 246 targets, and 1,031 time exits). No parameter changes were made after inspecting forward/OOS performance.

## Performance

| Period | Trades | PF, observed BID/ASK | PF +0.5 pip | PF +1 pip | PF +2 pips | Net pips +1 pip |
|---|---:|---:|---:|---:|---:|---:|
| Discovery 2017–2020 | 820 | 1.040 | 1.008 | 0.977 | 0.919 | -306.3 |
| Validation 2021 | 166 | 0.973 | 0.936 | 0.900 | 0.832 | -222.6 |
| Forward 2022–2025 | 944 | 0.832 | 0.808 | 0.785 | 0.741 | -3,848.4 |
| OOS 2026 to Oct 13 | 135 | 0.954 | 0.921 | 0.889 | 0.829 | -224.9 |

Forward frequency was 4.52 trades/week and OOS frequency 3.30 trades/week. Trade count was adequate; profitability was not.

### Forward annual stability at +1 additional pip

| Year | Trades | PF | Net pips |
|---|---:|---:|---:|
| 2022 | 314 | 0.713 | -2,164.3 |
| 2023 | 227 | 0.819 | -691.2 |
| 2024 | 189 | 0.700 | -876.2 |
| 2025 | 214 | 0.968 | -116.8 |

All four forward years were negative after the +1-pip stress. A circular four-week block bootstrap estimated only **0.3% probability of positive forward mean**, with a 95% interval of **-6.97 to -1.24 pips/trade**.

## Challenge replay

Using 2026 OOS sequence and +1 additional pip:
- 0.25% risk/trade: failed to reach Phase 1; ending balance $5,895.
- 0.50%: failed Phase 1; ending balance $5,786.71.
- 0.75%: failed Phase 1; ending balance $5,675.38.
- 1.00%: briefly reached Phase 1 on 2026-01-27, then breached the static maximum-loss level in Phase 2, finishing at $5,349.19.

No tested risk setting passed both phases.

## Acceptance result

Failed gates:
- Discovery PF at +1 pip >= 1.00: observed 0.977.
- Validation PF at +1 pip >= 1.00: observed 0.900.
- Forward PF at +1 pip >= 1.10: observed 0.785.
- Forward PF at +2 pips >= 1.05: observed 0.741.
- Every qualifying forward annual cohort PF >= 1.00: all four failed.
- 4-week bootstrap supports positive expectancy at 95%: failed; estimated probability 0.3%, confidence interval entirely below zero.
- OOS PF at +1 pip >= 1.00: observed 0.889.
- Both challenge phases passed in OOS replay: failed.

**Final status: GAGAL.** This exact R258 rule is closed and must not be retuned using its failed forward/OOS outcomes.
