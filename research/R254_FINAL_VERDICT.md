# R254 — Final Binary Verdict

**Verdict: GAGAL.** The failed Asian-range breakout/reclaim fade did not produce an edge that survived forward testing and execution costs.

Workflow: https://github.com/christianomomongan82-lang/scanner/actions/runs/38522868392

## Preregistered rule
- Completed UTC Asian range from H1 bars opening 00:00–05:00.
- First require a close inside the range, then an H1 close beyond the upper/lower range by the registered excursion fraction (0% or 5%), followed by the next H1 close back inside the range.
- Fade the failure: short after a failed upside break; long after a failed downside break.
- Stop: extreme across the breakout and reclaim candles; target alternatives 1R, 1.5R and 2R.
- Entry at the next exact H1 open; one attempt per day/candidate; liquidate at 16:00 UTC if stop/target did not hit.
- Executable BID/ASK quote-side OHLC is used; stop-first for same-bar stop/target collisions, plus 0/0.5/1/2-pip additional cost stress.
- The chosen configuration was **EXCUR0.05_RR1.0**, ranked on 2021 validation only.

## Data quality
EURUSD BID and ASK H1 each contain 85,170 rows from 2017-01-01 to 2026-10-13. Duplicate timestamps, invalid OHLC, off-hour timestamps and negative open spreads were zero. No bars were synthesized. The 1,008 skipped calendar days had zero-width/invalid Asian ranges, not corrupted BID/ASK data.

## Results

| Period | Trades | PF, observed BID/ASK only | PF +0.5 pip | PF +1 pip | PF +2 pips |
|---|---:|---:|---:|---:|---:|
| Discovery 2017–2020 | 220 | 0.978 | 0.917 | 0.859 | 0.753 |
| Validation 2021 | 70 | 1.188 | 1.107 | 1.030 | 0.892 |
| Forward 2022–2025 | 214 | 0.944 | 0.890 | 0.838 | 0.744 |
| OOS 2026 through Oct 13 | 39 | 0.667 | 0.618 | 0.573 | 0.490 |

At +1 extra pip, forward net was **-316.4 pips** (mean -1.48 pips/trade) at only **1.03 trades/week**. OOS lost **-144 pips** with PF 0.573 at +1. The 4-week block bootstrap on forward +1-pip returns estimated 14.5% probability of positive mean with 95% interval [-4.023, +1.163] pips/trade.

## Acceptance gates

| Gate | Outcome |
|---|---|
| Validation ≥50 trades | PASS — 70 |
| Validation PF ≥1.05 at +1 pip | **FAIL — 1.030** |
| Discovery ≥100 trades | PASS — 220 |
| Discovery PF ≥1.00 at +1 pip | **FAIL — 0.859** |
| Forward ≥100 trades | PASS — 214 |
| Forward PF ≥1.10 at +1 pip | **FAIL — 0.838** |
| Forward PF ≥1.05 at +2 pips | **FAIL — 0.744** |
| Forward frequency ≥2 trades/week | **FAIL — 1.03** |
| All qualifying forward years PF ≥1 at +1 pip | **FAIL** |
| Bootstrap supports positive expectancy at 95% | **FAIL — 14.5%, CI crosses zero** |
| OOS ≥30 trades | PASS — 39 |
| OOS PF ≥1 at +1 pip | **FAIL — 0.573** |

**Final status: GAGAL.** The 2021 validation result did not replicate in discovery, forward, or 2026 OOS. Do not tune these six variants using the failed forward/OOS periods.
