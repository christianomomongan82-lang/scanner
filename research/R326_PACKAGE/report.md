# R326 — EURUSD M5 raw-price impulse continuation

**Official V2 disposition: GAGAL — DATA/PROCESS (NOT CLOSED).**  
**Outcome metrics below are exploratory diagnostics only, not a formally accepted EDGE closeout.**

The signal outcomes were computed before the repository's V2 preflight and novelty review were completed. The exact runner, full trade ledger and weekly net-R rows are not yet committed/read-back-verified as a complete V2 package. Therefore the overall experiment cannot be called CLOSED, even though the observed price outcome is strongly negative. The data below is retained transparently as diagnostic evidence; it must not be used to claim the V2 process gates passed or to justify a new parameter variation.


This test passed every frozen sample-size gate, so outcome metrics were calculated. It fails the edge gates in discovery, confirmation and final holdout. Do not use for a funded challenge; do not tune against these same confirmation/holdout dates.

## Reproducibility and data
- Preregistration: research/R326_EURUSD_M5_IMPULSE_CONTINUATION_PREREGISTRATION.md
- Preregistration commit: 4c2dddf2ff17e8a5273c875ee84bdfd6b9af15ea
- Source archive SHA-256: b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e
- BID/ASK rows: 4,415,493 / 4,415,493; exact timestamp pairing passed, zero duplicate timestamps and zero invalid OHLC rows.
- Complete M5 candles: 883,086. Source has 538 gaps over one minute, 528 gaps over one hour, and a maximum gap of 3,001 minutes. No gaps were imputed; candidate trades required contiguous delay and exit coverage.
- Python 3.13.5; NumPy 2.3.5; pandas 2.2.3.
- Runner SHA-256: 4a761fede599e39cd9316fcad9e8c2dbe848c9bbd6bbb236eb949b3c99246398
- Normalized trade ledger SHA-256: ee34a03a720cb980cd363f312a1690deb472b8a58e9d5b69673c89437ddc5d92
- Two independent clean processes returned byte-identical ledger, JSON summary, report, and annual scorecard. Hash comparison is in reproducibility_check.json.

## Sample gate
| Cohort | Eligible trades | Gate |
|---|---:|---|
| Discovery 2017–2020 | 928 | PASS (>=600; each year >=100) |
| Confirmation A 2021–2023 | 710 | PASS (>=400; each year >=100) |
| Final holdout B 2024–2025 | 479 | PASS (>=250; each year >=100) |

## Results, executable BID/ASK fills plus fixed extra round-trip friction
| Cohort | Extra cost (pips) | Trades | Net expectancy (R/trade) | PF | Max drawdown (R) | Win rate |
|---|---:|---:|---:|---:|---:|---:|
| Discovery | 0.5 | 928 | -0.25005 | 0.6595 | 235.539 | 0.361 |
| Discovery | 1.0 | 928 | -0.40086 | 0.5174 | 373.732 | 0.361 |
| Discovery | 2.0 | 928 | -0.70247 | 0.3217 | 653.031 | 0.334 |
| Confirmation A | 0.5 | 710 | -0.20902 | 0.7085 | 154.852 | 0.373 |
| Confirmation A | 1.0 | 710 | -0.34814 | 0.5694 | 250.583 | 0.370 |
| Confirmation A | 2.0 | 710 | -0.62636 | 0.3717 | 445.661 | 0.366 |
| Holdout B | 0.5 | 479 | -0.26382 | 0.6442 | 128.313 | 0.355 |
| Holdout B | 1.0 | 479 | -0.41459 | 0.5062 | 199.971 | 0.351 |
| Holdout B | 2.0 | 479 | -0.71612 | 0.3153 | 343.287 | 0.332 |

Even before extra fixed friction, gross expectancy is negative in each cohort: discovery -0.09924R, confirmation A -0.06991R, and holdout B -0.11306R per trade.

## Annual net results at +0.5 pip extra cost
| Year | Cohort | Trades | Expectancy (R/trade) | PF | Net total (R) |
|---:|---|---:|---:|---:|---:|
| 2017 | Discovery | 224 | -0.22897 | 0.6814 | -51.290 |
| 2018 | Discovery | 235 | -0.17315 | 0.7501 | -40.689 |
| 2019 | Discovery | 238 | -0.28869 | 0.6224 | -68.707 |
| 2020 | Discovery | 231 | -0.30891 | 0.5939 | -71.359 |
| 2021 | Confirmation A | 234 | -0.29612 | 0.6147 | -69.292 |
| 2022 | Confirmation A | 237 | -0.25839 | 0.6489 | -61.239 |
| 2023 | Confirmation A | 239 | -0.07480 | 0.8845 | -17.876 |
| 2024 | Holdout B | 237 | -0.34614 | 0.5577 | -82.036 |
| 2025 | Holdout B | 242 | -0.18321 | 0.7387 | -44.336 |

All nine annual cohorts are negative. Neither the primary-cost nor the +2-pip stress requirements passed in any cohort.

## Bootstrap and frozen verdict gates
- Confirmation A, zero-inclusive weekly net R: 156 weeks; mean -0.95132R/week; circular 4-week block bootstrap, 10,000 resamples, seed 326; 95% interval [-1.36662, -0.56633].
- Holdout B, zero-inclusive weekly net R: 105 weeks; mean -1.20354R/week; same bootstrap design/seed; 95% interval [-1.59833, -0.80282].
- Positive annual net-R years: 0/4 discovery, 0/3 confirmation A, 0/2 holdout B.
- Verdict: **FAIL — EDGE**. This is not a sample-size failure; it is a repeatedly negative historical outcome under the locked executable-price rules.
