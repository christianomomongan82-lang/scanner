# R304 — FX Local-Session Currency Depreciation

**Binary verdict: GAGAL.** The registered method is closed. No PnL after 2021 was calculated, and no FundedNext challenge replay was run because the strategy-level gates failed.

## Frozen hypothesis

R304 tests the published intraday currency-depreciation pattern during local trading hours (Breedon & Ranaldo, 2013, “Intraday Patterns in FX Returns and Order Flow”: https://onlinelibrary.wiley.com/doi/10.1111/jmcb.12032). The paper motivated a falsifiable test; it did not establish a tradeable edge for this feed.

- Module E: SHORT EURUSD from the first active paired M1 quote at/after 08:05 and no later than 08:10 Europe/London, until the exact 12:00 local exit.
- Module U: LONG EURUSD under the same entry/exit rules in America/New_York local time.
- Risk distance: median of the last 20 prior **complete 240-minute sessions** (minimum 15); stop at 1R, no take-profit; stop hit or exit at 12:00 local.
- Long entries use ASK and exits/stops use BID; short entries use BID and exits/stops use ASK. Stop gaps fill at the adverse open. Missing bars are never synthesized.
- Cost grid is additional round-trip friction beyond observed BID/ASK: 0, 0.5, 1 and 2 pips. Primary cost: +1 pip.
- Discovery: 2017–2020; validation: 2021. 2022–2025 candidate PnL and all 2026 outcomes remain unopened.

## Data and pre-outcome eligibility

Source: existing GitHub data-only artifact 11959096102, acquisition run 38697080604. ZIP SHA-256: b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e. BID SHA-256: b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc. ASK SHA-256: 52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b.

There were 4,415,493 rows per side, exact timestamp pairing, zero duplicate timestamps, invalid OHLC rows or negative open/close spreads. The registered repeated-flat filter removed 696,795 rows, leaving 3,718,698 active paired timestamps; 12,018 gaps longer than one minute were preserved. The pre-outcome audit found 2,572 eligible module-events for 2017–2021: 2,059 discovery and 513 validation. Eligibility required an observed entry in the fixed window, an exact 12:00 local exit quote, at least 15 prior full sessions for the risk estimate and a completely contiguous stop-monitoring path.

## Primary results

All metrics below use the preregistered directions and executable BID/ASK fills. R means initial-stop risk units.

| Period | Added cost | Trades | Net R | PF_R | Net pips | Max closed-R DD |
|---|---:|---:|---:|---:|---:|---:|
| Discovery 2017–2020 | 0 pip | 2,059 | +18.058 | 1.034 | +966.8 | 35.53R |
| Discovery 2017–2020 | 0.5 pip | 2,059 | -12.166 | 0.978 | -62.7 | 52.84R |
| Discovery 2017–2020 | **1 pip** | 2,059 | **-42.390** | **0.926** | **-1,092.2** | **77.96R** |
| Discovery 2017–2020 | 2 pips | 2,059 | -102.837 | 0.829 | -3,151.2 | 128.39R |
| Validation 2021 | 0 pip | 513 | +1.110 | 1.008 | +57.2 | 9.18R |
| Validation 2021 | 0.5 pip | 513 | -7.225 | 0.947 | -199.3 | 13.61R |
| Validation 2021 | **1 pip** | 513 | **-15.560** | **0.889** | **-455.8** | **20.34R** |
| Validation 2021 | 2 pips | 513 | -32.231 | 0.784 | -968.8 | 35.34R |

The zero-extra-cost point estimates are only marginally positive and turn negative at +0.5 pip extra friction. Both discovery and validation lose at the registered +1 pip cost.

### Module and annual diagnosis at +1 pip

| Stream/year | Net R | PF_R |
|---|---:|---:|
| Module E, 2017–2021 | -27.116 | 0.922 |
| Module U, 2017–2021 | -30.834 | 0.915 |
| 2017 combined | +25.560 | 1.214 |
| 2018 combined | -20.315 | 0.865 |
| 2019 combined | -33.206 | 0.785 |
| 2020 combined | -14.430 | 0.901 |
| 2021 combined | -15.560 | 0.889 |

Only 1 of 4 discovery years is positive at +1 pip. Neither module supplies a positive combined-period block.

### Fixed-direction mirror control

The preregistered direction-mirror diagnostic used the same event timestamps and risk geometry, but reversed each module’s direction. It is not an alternate candidate and cannot replace the primary strategy after the outcomes are seen.

| Period | Mirror net R at 0 pip | PF_R | Mirror net R at +1 pip | PF_R |
|---|---:|---:|---:|---:|
| Discovery 2017–2020 | -65.611 | 0.887 | -126.059 | 0.795 |
| Validation 2021 | -11.055 | 0.920 | -27.726 | 0.812 |

Both direction streams fail after observed bid/ask fills; changing direction does not rescue this registered idea.

## Validation uncertainty and gates

Validation weekly bootstrap: 53 Monday-start calendar weeks intersecting 2021, including zero-trade weeks; circular 4-week blocks; 10,000 resamples; seed 304. At +1 pip, mean weekly net was **-0.29359R**, 95% interval **[-0.64112R, +0.06233R]**, and only 5.35% of bootstrap means were positive.

| Gate | Result |
|---|---|
| Discovery minimum trade count | PASS — 2,059 |
| Discovery net R > 0 and PF_R ≥ 1.05 at +1 pip | FAIL — -42.390R, PF 0.926 |
| Discovery +2 pip cost stress | FAIL — -102.837R, PF 0.829 |
| Validation minimum trade count | PASS — 513 |
| Validation net R > 0 and PF_R ≥ 1.05 at +1 pip | FAIL — -15.560R, PF 0.889 |
| Validation +2 pip cost stress | FAIL — -32.231R, PF 0.784 |
| Module E positive over 2017–2021 | FAIL — -27.116R |
| Module U positive over 2017–2021 | FAIL — -30.834R |
| At least 3/4 discovery years positive | FAIL — 1/4 |
| Validation bootstrap lower bound > 0 | FAIL — lower bound -0.64112R |
| Repository-only reproducibility | FAIL — row-level ledgers were generated locally but not verified as committed repository files |

Only 2 of 11 candidate/data gates passed: minimum sample in discovery and validation. The challenge replay was **not run** because the locked strategy screen failed; therefore there is no valid estimate that this method could pass both FundedNext phases in under 180 days.

## Verdict and research disposition

**R304 = GAGAL. Close the exact rule. Do not retune the hours, direction, range estimator or stop on the same periods.** Do not score 2022–2025 or any 2026 outcomes to rescue it. The result rejects this registered fixed-clock design, not every possible intraday FX mechanism. No alpha block is retained and no funded-ready claim is made.

The governing objective remains: realistically maximize the probability of passing the $6,000 reference Stellar 2-Step challenge (+8%, then +5%) before any daily/max-loss breach and in **less than 180 calendar days**. Profit factor remains a diagnostic, not the target.

For reproducibility limitations and local-output checksums, see R304_DATA_MANIFEST.md. The locked preregistration, full-session range amendment and pre-outcome audit are linked from R304_INDEX.md.