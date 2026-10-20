# R311 — EURUSD Tokyo Fix Post-Event Reversal — Final Report

**Binary verdict: GAGAL.** The preregistered Tokyo 09:55-fixing fade does not show a tradable edge in this historical screen. No direction flip or parameter rescue is permitted on the same sample.

## Main results

| Metric | Discovery 2017–2020 | Validation screen 2021 |
|---|---:|---:|
| Primary T+5 trades | 750 | 143 |
| Net R, +1 pip incremental round-trip cost | -360.8430R | -73.7993R |
| PF_R, +1 pip | 0.3445 | 0.3161 |
| Net R, zero extra cost | -75.9814R | -13.5841R |
| PF_R, zero extra cost | 0.8042 | 0.8184 |
| Net R, +2 pip cost | -645.7046R | -134.0145R |
| PF_R, +2 pip cost | 0.1199 | 0.0801 |
| Positive discovery years at +1 pip | 0 of 4 | — |

Validation weekly net R at +1 pip: mean -1.4192R/week; circular four-week block bootstrap 95% interval [-1.8635R, -0.9933R] across 52 calendar weeks (10,000 resamples, seed 311). The full interval is negative.

The delayed T+10 fade control is also negative at +1 pip: discovery 746 trades / -340.7207R / PF_R 0.3627; validation 143 trades / -75.2451R / PF_R 0.3254. The preregistered same-event follow-direction diagnostic is also negative even at zero extra cost: discovery -139.6179R; validation -23.5589R.

## Decision

The candidate passed the basic data-integrity and minimum-sample gates only. It failed the expectancy/PF gates in both periods, annual-stability gate, cost-stress gate, bootstrap gate and delayed-entry gate. The result remains GAGAL even before considering programme-level contamination. It is not funded-ready and must not be used to trade a challenge.

## Data / execution integrity

- Existing EURUSD M1 BID/ASK Dukascopy source artifact #11959096102; raw ZIP SHA-256 and member hashes are recorded in the manifest.
- Exclusive cutoff: 2022-01-01T00:00:00Z, applied before feature/outcome construction. **No R311 PnL at or after 2022 was calculated.**
- 2,650,553 paired M1 rows per side before cutoff; zero duplicate/non-monotonic timestamps, invalid OHLC rows or negative opening/closing spreads. 2,202,782 rows have both quote sides active; 447,771 are static/inactive on at least one side. Only exact active M1 blocks were aggregated to M5.
- Screen windows: discovery 2017–2020 and validation 2021. Earlier programme FX research reused these years, so this is not pristine OOS.
- Signals use a 15-minute midpoint return ending at 09:55 Tokyo. Entries use observed executable ASK for longs and BID for shorts at T+5, stop/target checks use the executable exit side, 1R stop/target, max 30-minute hold, and +0/+0.5/+1/+2 pip added-cost sensitivities. All outcomes are on exact timestamp paths; no synthetic rows or future fills.

## Reproducibility and stored artifacts

See [R311 index](R311_INDEX.md), [data/output manifest](R311_DATA_MANIFEST.md), [locked preregistration](R311_EURUSD_TOKYO_FIX_POST_EVENT_REVERSAL_PREREGISTRATION.md), [master experiment registry](MASTER_SEARCH_LEDGER_R251_R311.csv), and [family map](SEARCH_FAMILY_MAP_R251_R311.md).

The locked runner, preregistration, compact results and human-readable report are committed in GitHub. The exact run also created the full local trade ledger, pre-outcome eligibility audit, runtime skip audit, annual scorecard, weekly validation input and full data audit; their original byte sizes and SHA-256 values are recorded in the manifest. **The full row-level result files are not yet committed/read-back verified in the GitHub tree**, so the repository-artifact reproducibility gate is explicitly false. This gap does not affect the failed economic verdict and does not authorize changing the R311 rule.

R311 is closed. Do not invert its direction, move the event clock, alter return horizon, or re-optimize stop/target on these dates. Under the existing R312 search governance, do not launch another signal hypothesis until the reproducible real-data funded-path pipeline and required artifact storage are complete.
