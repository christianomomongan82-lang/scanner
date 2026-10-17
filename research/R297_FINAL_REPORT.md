# R297 — XAUUSD Active Weekend-Reopening Gap Continuation

**Verdict: GAGAL.** The corrected test used the first genuinely active M5 bar at weekend reopening; the earlier R296 outputs were invalid and are not signal evidence.

## Results at modeled additional cost of $0.30/oz

| Metric | Discovery 2016–2020 | Validation 2021–2025 |
|---|---:|---:|
| Closed trades | 24 | 28 |
| Net R | -6.161 | +0.385 |
| PF_R | 0.460 | 1.042 |
| Win rate after cost | 33.3% | 53.6% |
| Maximum closed R drawdown | 7.116R | 3.026R |
| Stop exits | 10 | 7 |
| Target exits | 5 | 8 |
| Four-hour time exits | 9 | 13 |

Validation's point estimate is slightly positive, but it is too weak to pass the locked gate. The lower 95% bound of the four-week weekly-net-R bootstrap crosses zero, the 100-trade validation minimum fails, and the strategy turns negative at the +$0.50/oz cost stress.

## Cost sensitivity

| Cost stress | Discovery net R / PF_R | Validation net R / PF_R |
|---|---:|---:|
| $0.00/oz extra | -5.078 / 0.526 | +1.343 / 1.153 |
| $0.10/oz extra | -5.439 / 0.503 | +1.024 / 1.115 |
| $0.30/oz extra | -6.161 / 0.460 | +0.385 / 1.042 |
| $0.50/oz extra | -6.883 / 0.420 | -0.253 / 0.973 |

## Annual cohorts at +$0.30/oz

| Year | Trades | Net R | PF_R |
|---|---:|---:|---:|
| 2016 | 4 | +0.862 | 1.823 |
| 2017 | 4 | -1.287 | 0.058 |
| 2018 | 2 | -0.242 | 0.784 |
| 2019 | 6 | -0.246 | 0.846 |
| 2020 | 8 | -5.250 | 0.163 |
| 2021 | 2 | -0.597 | 0.439 |
| 2022 | 5 | +0.635 | 1.851 |
| 2023 | 6 | +1.885 | 2.285 |
| 2024 | 4 | -3.026 | 0.025 |
| 2025 | 11 | +1.487 | 1.528 |

## Data-eligibility audit

- 500 active weekend-reopening gaps were identified in 2016–2025.
- 52 passed the locked quote-validity, complete-path and friction rules; all 52 completed simulation without late-fill substitution.
- 448 event candidates were rejected, overwhelmingly because the reopening gap did not exceed twice the combined Friday-close and Sunday-active-open spreads.
- The raw XAUUSD manifest said synthetic flat bars were disabled, but Sunday 00:00 UTC rows were static closed-market quote snapshots through 22:55 UTC; genuine active bars began around 23:00 UTC. R296 mistakenly used the static snapshot. Its PnL is **invalid**, not a failed alpha result. R297 fixes this event-time/data-eligibility defect and keeps the economic hypothesis and trading parameters locked.

## Validation bootstrap

At +$0.30/oz, the mean weekly net result was +0.00148R/week with 95% CI **[-0.02939, +0.03141]R/week** across 261 Monday-start weeks, including zero-trade weeks (10,000 circular four-week block resamples, seed 297). The interval crosses zero.

## Locked gates

| Gate | Result |
|---|---|
| Discovery at least 75 trades | FAIL |
| Discovery positive net R at $0.30/oz | FAIL |
| Discovery PF_R ≥ 1.05 | FAIL |
| Discovery at least 3 of 5 years positive | FAIL |
| Discovery net positive at $0.50/oz | FAIL |
| Discovery PF_R ≥ 0.90 at $0.50/oz | FAIL |
| Validation at least 100 trades | FAIL |
| Validation positive net R at $0.30/oz | PASS |
| Validation PF_R ≥ 1.05 | FAIL |
| Validation at least 3 of 5 years positive | PASS |
| Validation bootstrap 95% CI lower bound > 0 | FAIL |
| Validation net positive at $0.50/oz | FAIL |
| Validation PF_R ≥ 0.90 at $0.50/oz | PASS |

**Disposition: GAGAL.** Do not inspect 2026, change the friction threshold/holding rules, or test gap-fade as a rescue on the same dates. The corrected active-reopening continuation idea showed poor discovery economics and insufficient sample size/robustness; it is not eligible for funded challenge replay.

## Limitations

- Historical BID/ASK quotes are not guaranteed funded-account fills.
- Added costs are stress assumptions; broker-specific spread, slippage, commission, swap and contract specifications remain unverified.
- 2021–2025 has prior XAU research exposure and is not pristine program-level out-of-sample data.
- No strategy outcome PnL after 2025-12-31 was calculated; the 2026 segment remains unopened.
- No FundedNext two-phase equity-aware challenge replay was run.
