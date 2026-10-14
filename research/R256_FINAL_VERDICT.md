# R256 — Final Binary Verdict

**Verdict: GAGAL.** The EURUSD H4 rolling-breakout strategy failed the locked forward, stability, inference, and OOS acceptance gates.

Workflow: https://github.com/christianomomongan82-lang/scanner/actions/runs/38523813115

## Frozen strategy
- Build UTC-anchored H4 candles only from four consecutive, exact H1 BID/ASK bars; missing bars are never filled.
- Long when completed H4 BID close exceeds the highest BID high of the previous 12/24/48 H4 bars; short when completed H4 ASK close falls below the lowest ASK low of the previous range.
- Candidate stop windows are 6/12/24 H4 bars, including the completed signal bar; target is fixed at 2R.
- Entry at the exact H1 open that coincides with H4 close. Actual H1 BID/ASK OHLC is used for stop/target execution, stop-first on same-bar collisions, with a maximum 48-hour hold.
- Add-on execution cost stress: 0 / 0.5 / 1 / 2 pips.
- One configuration was selected by 2021 validation only: **L12_S24_RR2.0** (12 H4 breakout lookback, 24 H4 stop window, 2R target).

## Data audit
EURUSD BID and ASK H1 streams each contain 85,170 rows from 2017-01-01 through 2026-10-13. Both streams had zero duplicate timestamps, invalid OHLC rows, off-hour timestamps or invalid ASK-vs-BID open spreads. The H4 builder created 21,278 complete bins from four exact H1 candles; 160 incomplete bins were skipped. No missing H1 candles were synthesized.

## Results for the selected configuration

| Period | Trades | PF, observed BID/ASK only | PF +0.5 pip | PF +1 pip | PF +2 pips |
|---|---:|---:|---:|---:|---:|
| Discovery 2017–2020 | 374 | 1.070 | 1.046 | 1.022 | 0.976 |
| Validation 2021 | 114 | 0.893 | 0.868 | 0.845 | 0.800 |
| Forward 2022–2025 | 339 | 0.891 | 0.870 | 0.850 | 0.812 |
| OOS 2026 through Oct 13 | 81 | 0.848 | 0.825 | 0.803 | 0.761 |

At +1 additional pip, forward net was **-1,183.7 pips**, mean expectancy **-3.49 pips/trade**, with 1.62 trades/week. OOS lost **-326.4 pips** with PF 0.803 at +1 pip. Positive aggregate discovery results did not persist into validation, forward, or OOS.

### Forward annual cohorts at +1 extra pip
- 2022: 62 trades, PF 1.020
- 2023: 93 trades, PF 0.638
- 2024: 98 trades, PF 0.675
- 2025: 86 trades, PF 1.136

Two of four forward years lost materially. The 4-week block bootstrap estimated **12.05% probability of positive forward mean**, with 95% interval **[-8.897, +2.115] pips/trade**; this does not establish positive expectancy.

## Acceptance gates

| Gate | Outcome |
|---|---|
| Validation ≥15 trades | PASS — 114 |
| Validation PF ≥1.05 at +1 pip | **FAIL — 0.845** |
| Discovery ≥30 trades | PASS — 374 |
| Discovery PF ≥1.00 at +1 pip | PASS — 1.022 |
| Forward ≥80 trades | PASS — 339 |
| Forward PF ≥1.10 at +1 pip | **FAIL — 0.850** |
| Forward PF ≥1.05 at +2 pips | **FAIL — 0.812** |
| Forward frequency ≥1 trade/week | PASS — 1.62 |
| Every qualifying forward year PF ≥1 at +1 pip | **FAIL — 2023 and 2024 below 1** |
| Bootstrap supports positive expectancy at 95% | **FAIL — probability 12.05%, CI crosses zero** |
| OOS ≥20 trades | PASS — 81 |
| OOS PF ≥1 at +1 pip | **FAIL — 0.803** |

**Final status: GAGAL.** The 12-H4 breakout / 24-H4 stop window had a modest discovery edge that disappeared afterwards. Do not retune these nine combinations using the failed forward/OOS results.
