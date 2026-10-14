# R253 — Final Binary Verdict

**Verdict: GAGAL.** EURUSD UTC Asian-range close breakout does not meet the locked acceptance gates.

Workflow: https://github.com/christianomomongan82-lang/scanner/actions/runs/38522660810

## Rule and evaluation
- Asian range: completed BID highs/lows of H1 bars opening 00:00–05:00 UTC.
- Signal: first completed H1 close between 06:00 and 10:00 UTC outside the range plus a fixed buffer fraction (0% or 5% of range).
- Entry: following exact H1 open.
- Initial stop: opposite edge of the range; target alternatives were 1R, 1.5R and 2R.
- One attempt per day per candidate. Stop is checked before target when both are touched within the same hourly bar; stop gaps fill at observed bar open. If neither level is hit, close at the 16:00 UTC open.
- Entry/exit use EURUSD actual BID/ASK H1 quote-side prices. Costs are stressed at 0, 0.5, 1 and 2 extra pips per trade.
- Six predeclared variants were ranked only on calendar 2021 validation. The selected variant was BUF0.00_RR1.5.

## Data/execution checks
BID and ASK each provide 85,170 H1 rows from 2017-01-01 through 2026-10-13. Duplicate timestamps, invalid OHLC rows, off-hour timestamps, non-finite aligned opens and negative BID/ASK open spreads: all zero. No bars were synthesized. Twenty calendar dates were skipped for incomplete hourly grids. Zero-width / invalid Asian ranges were counted as range-quality skips, not quote-data errors.

## Selected variant metrics

| Period | Trades | PF, observed BID/ASK only | PF +0.5 pip | PF +1 pip | PF +2 pips |
|---|---:|---:|---:|---:|---:|
| Discovery 2017–2020 | 863 | 0.879 | 0.841 | 0.805 | 0.737 |
| Validation 2021 | 236 | 1.110 | 1.057 | 1.006 | 0.912 |
| Forward 2022–2025 | 813 | 1.107 | 1.063 | 1.021 | 0.942 |
| OOS 2026 through Oct 13 | 157 | 1.310 | 1.242 | 1.177 | 1.058 |

At +1 extra pip the forward result is +206.75 pips over 813 trades, but PF is only 1.021 and mean expectancy 0.254 pip/trade. This does not reach the preregistered forward PF requirement of 1.10. Performance also weakens materially under +2 pips (PF 0.942). OOS is positive but cannot override discovery and forward failures.

Forward annual PF at +1 pip: 2022 1.090, 2023 1.059, 2024 0.908, 2025 0.994. The 4-week block bootstrap at +1 pip gives P(mean>0)=0.5995 and 95% interval [-1.707, +2.194] pips/trade, which does not support positive expectancy at the required confidence.

## Acceptance gates

| Gate | Outcome |
|---|---|
| Validation ≥50 trades | PASS — 236 |
| Validation PF ≥1.05 at +1 pip | **FAIL — 1.006** |
| Discovery ≥100 trades | PASS — 863 |
| Discovery PF ≥1.00 at +1 pip | **FAIL — 0.805** |
| Forward ≥100 trades | PASS — 813 |
| Forward PF ≥1.10 at +1 pip | **FAIL — 1.021** |
| Forward PF ≥1.05 at +2 pips | **FAIL — 0.942** |
| Forward frequency ≥2 trades/week | PASS — 3.90 |
| Every qualifying forward annual cohort PF ≥1 at +1 pip | **FAIL** |
| Four-week bootstrap supports positive expectancy at 95% | **FAIL** |
| OOS ≥30 trades | PASS — 157 |
| OOS PF ≥1.00 at +1 pip | PASS — 1.177 |

**Final status: GAGAL.** The positive 2026 OOS is not enough to establish robust edge because the discovery, validation, forward-cost, annual-cohort and inferential gates failed. Do not retune these six variants using the failed forward/OOS results.
