# R255 — Final Binary Verdict

**Verdict: GAGAL.** EURUSD rolling-extreme sweep-and-reclaim reversal failed profitability, annual stability, cost and OOS requirements.

Workflow: https://github.com/christianomomongan82-lang/scanner/actions/runs/38523381180

## Preregistered rule
- Lookbacks: 12, 24 and 48 prior H1 bars; targets: 1R, 1.5R and 2R.
- Long: current BID low sweeps at least 2% of prior-window range below the prior BID low, then the candle closes back above the prior low and within the prior range.
- Short: current ASK high sweeps at least 2% of prior-window range above the prior ASK high, then the candle closes back below the prior high and within the prior ASK range.
- Entry: next exact H1 open. Stop: signal candle's executable-side sweep extreme. Exit at stop/target or after 8 elapsed hours. One position at a time; missing-hour sequences are rejected, not filled.
- Actual BID/ASK quotes are used for execution, then cost stress of 0/0.5/1/2 additional pips is applied.
- Candidate chosen using 2021 validation PF at +1 pip was **L12_RR1.5**.

## Data quality
EURUSD BID and ASK each contain 85,170 hourly rows from 2017-01-01 to 2026-10-13. Duplicate timestamps, invalid OHLC and off-hour timestamps were all zero. Forty hourly gaps were retained; no missing candles were synthesized.

## Results for selected configuration

| Period | Trades | PF, observed BID/ASK only | PF +0.5 pip | PF +1 pip | PF +2 pips |
|---|---:|---:|---:|---:|---:|
| Discovery 2017–2020 | 2,812 | 0.958 | 0.878 | 0.806 | 0.680 |
| Validation 2021 | 703 | 0.841 | 0.758 | 0.684 | 0.559 |
| Forward 2022–2025 | 2,824 | 0.929 | 0.854 | 0.786 | 0.668 |
| OOS 2026 through Oct 13 | 563 | 0.816 | 0.740 | 0.671 | 0.553 |

At +1 extra pip, forward net was **-4,049.1 pips** and mean expectancy **-1.434 pips/trade**, despite 13.53 trades/week. OOS net was -1,124.8 pips and PF 0.671 at +1. The four-week block bootstrap estimated **0% probability of positive forward mean**, with a 95% interval of **[-2.004, -0.840] pips/trade**.

Forward annual PF at +1 pip: 2022 0.829, 2023 0.671, 2024 0.782, 2025 0.850. All four years failed the annual consistency gate.

## Acceptance gates

| Gate | Outcome |
|---|---|
| Validation ≥50 trades | PASS — 703 |
| Validation PF ≥1.05 at +1 pip | **FAIL — 0.684** |
| Discovery ≥100 trades | PASS — 2,812 |
| Discovery PF ≥1.00 at +1 pip | **FAIL — 0.806** |
| Forward ≥100 trades | PASS — 2,824 |
| Forward PF ≥1.10 at +1 pip | **FAIL — 0.786** |
| Forward PF ≥1.05 at +2 pips | **FAIL — 0.668** |
| Forward frequency ≥2 trades/week | PASS — 13.53 |
| Every qualifying forward year PF ≥1 at +1 pip | **FAIL — all four years below 1** |
| Bootstrap supports positive expectancy at 95% | **FAIL — 0%, CI entirely below zero** |
| OOS ≥30 trades | PASS — 563 |
| OOS PF ≥1 at +1 pip | **FAIL — 0.671** |

**Final status: GAGAL.** The method produced frequent trades but negative expectancy across validation, forward and OOS periods. Do not retune these nine configurations against the failed later periods.
