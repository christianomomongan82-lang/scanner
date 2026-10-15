# R269 — London Asian-range sweep/reclaim reversal

**Verdict: GAGAL.** The pre-registered economic gates failed. No retuning was performed after the result.

- [Preregistration](R269_LONDON_ASIAN_SWEEP_PREREGISTRATION.md)
- [Local runner](r269_london_asian_sweep.py)
- [Machine-readable result](R269_results_compact.json)
- [Raw-data artifact acquisition run](https://github.com/christianomomongan82-lang/scanner/actions/runs/38697080604)
- Data-only artifact ID: 11959096102, EURUSD M1 BID/ASK, 2016-01-03 through 2025-12-31. The action downloaded raw data only. Signal generation, fill simulation, costs, bootstrap and compounding ran locally in Python.

## Result that matters

| Period | Trades | PF in R at +1 pip | Net R | Net pips |
|---|---:|---:|---:|---:|
| Discovery 2016–2020 | 340 | 0.758 | −73.48 | −409.80 |
| Validation 2021 | 49 | 0.632 | −19.31 | −78.70 |
| Forward 2022–2025 | 242 | 0.657 | −78.91 | −347.35 |

The forward result was already negative **before** adding the extra one-pip stress: at +0 pip cost, PF was 0.891 and net −19.90R. At +2 pips, forward PF dropped to 0.505 and net was −137.93R.

All four forward calendar years lost after +1 pip: 2022 −8.58R (PF 0.894), 2023 −13.92R (PF 0.779), 2024 −31.94R (PF 0.121), and 2025 −24.47R (PF 0.511).

The four-week circular block bootstrap of 209 forward weeks at +1 pip estimated mean weekly net −0.378R; its 95% interval was [−0.661R, −0.078R]. Only 0.89% of sampled means were positive.

## Fixed-fractional illustration

Starting from $6,000, risking 0.25% of current realized equity per trade at +1 pip cost ended at **$4,912.24 (−18.13%)**, with a closed-equity peak-to-trough drawdown of 19.07%. The static $5,400 floor was first crossed on **2024-09-13 09:27 UTC** at $5,393.30 (trade 567). This uses closed equity, not floating intratrade equity; that limitation makes this only a research diagnostic, not a precise funded-account replay.

## Data quality and provenance

BID and ASK each contained 4,415,493 unique rows; common timestamps were 4,415,493. There were zero unmatched timestamps, duplicate rows, invalid OHLC rows, or negative BID/ASK open spreads. The aligned series ran from 2016-01-03 00:00 UTC through 2025-12-31 21:58 UTC. The 538 gaps longer than one minute are dominated by weekends/market closures; no synthetic bars were created. ZIP SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. BID SHA-256: `b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc`. ASK SHA-256: `52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b`.

## Interpretation

This candidate fails the discovery, validation, forward expectancy, annual stability, bootstrap, +2 pip stress and compounding-floor gates. The hypothesis is closed as **GAGAL**; do not change the sweep threshold, entry window, stop, target, or time stop on these same dates to try to rescue it. The result also does not prove the original HistData R189 history because the available archive is a separate Dukascopy feed. Funded readiness remains a separate claim requiring real execution-cost, server-time, latency, floating drawdown, DLL/MLL and provider-rule checks.
