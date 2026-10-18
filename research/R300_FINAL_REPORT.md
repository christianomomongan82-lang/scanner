# R300 — EURUSD London 4pm Fix Post-Event Reversal

**Binary verdict: GAGAL.** The candidate was preregistered and its runner committed before any R300 PnL was calculated. All rules stayed frozen. The 2022+ period was excluded before signal/outcome construction and was not scored.

## Locked hypothesis

Fade the EURUSD midpoint return from the M5 close at 15:40 to the M5 close at 15:55 London time. After waiting until 16:05 London (ten minutes after the signal close so the 16:00 fixing window has finished), enter with executable-side BID/ASK quotes. Use the mean midpoint range of the six M5 bars starting 15:25–15:50 as 1R, a 1R stop and 1R target, and a maximum exit at the 16:35 bar open. One position per London weekday. The matched direction diagnostic follows the same pre-fix return on the same events and timestamps. Cost stresses are extra 0/0.5/1/2 pips per round trip beyond observed BID/ASK execution.

The hypothesis was motivated by published research on unusual price/volatility behavior near the WMR London 4pm fix and evidence consistent with short-lived price pressure/negative serial correlation. That literature is motivation for the test, not evidence that this Dukascopy feed contains a tradeable edge:
- “Did the reform fix the London fix problem?” (2018): https://www.sciencedirect.com/science/article/pii/S0261560617302024
- “The WMR Fix and its Impact on Currency Markets” (2017): https://www.norges-bank.no/contentassets/619c8b75e1ed4ba691e8ad6a006855e6/39-panagiotou---the-wmr-fix-and-its-impact-on-currency-markets-.pdf?v=11122017105711
- FCA Occasional Paper 46, “Fixing the Fix?”: https://www.fca.org.uk/publications/occasional-papers/occasional-paper-no-46-fixing-fix-assessing-effectiveness-4pm-fix

## Data and execution audit

- Source archive: Dukascopy EURUSD M1 BID/ASK artifact **11959096102**, collection run **38697080604**; ZIP SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- Exact source-member hashes are recorded in the preregistration and data manifest. Before the UTC cutoff, 2,650,553 rows per side matched one-to-one, with unique, increasing M1 timestamps and no invalid OHLC rows or negative open/close spreads.
- M5 aggregation retained only complete five-row, contiguous, active M1 blocks; 422,289 valid active M5 bars remained.
- Pre-outcome eligibility audit: 1,283 eligible weekday event dates across 2017–2021; two had exactly zero pre-fix return and were skipped, yielding 1,281 matched fade and follow trades.
- At the exact 16:05 London entry time, observed spread median was 0.30 pip, p95 0.40 pip, maximum 0.80 pip.
- No missing bars were filled. Exact timestamps and Europe/London DST rules were used. Longs enter ASK and exit BID; shorts enter BID and exit ASK. Stops take priority on same-bar stop/target collisions. The 16:35 time cap is filled at the open without inspecting that bar's high/low.

## Primary fade results

| Period | Extra cost | Trades | Net R | PF_R | Win rate | Max closed-trade DD |
|---|---:|---:|---:|---:|---:|---:|
| Discovery 2017–2020 | 0 pip | 1,024 | -68.03R | 0.863 | 46.48% | 75.31R |
| Discovery 2017–2020 | 0.5 pip | 1,024 | -162.52R | 0.704 | 45.70% | 168.44R |
| Discovery 2017–2020 | 1 pip | 1,024 | -257.01R | 0.573 | 45.02% | 261.56R |
| Discovery 2017–2020 | 2 pips | 1,024 | -445.99R | 0.370 | 43.36% | 447.80R |
| Validation 2021 | 0 pip | 257 | -11.17R | 0.904 | 47.47% | 16.64R |
| Validation 2021 | 0.5 pip | 257 | -35.57R | 0.726 | 47.08% | 37.97R |
| Validation 2021 | 1 pip | 257 | -59.98R | 0.580 | 45.53% | 60.91R |
| Validation 2021 | 2 pips | 257 | -108.80R | 0.362 | 41.25% | 109.61R |

The registered candidate is already negative at zero *additional* cost after the observed BID/ASK spread has been accounted for. At the primary +1 pip stress, all four discovery years are negative: 2017 −76.65R, 2018 −67.00R, 2019 −73.66R, and 2020 −39.70R. Validation 2021 is −59.98R.

## Matched follow-direction diagnostic

This control uses the same event dates, execution times, risk geometry, exits and cost grid, but follows the sign of the pre-fix return instead of fading it. It also loses in aggregate:

| Period | Extra cost | Trades | Net R | PF_R |
|---|---:|---:|---:|---:|
| Discovery 2017–2020 | 0 pip | 1,024 | -39.20R | 0.919 |
| Discovery 2017–2020 | 1 pip | 1,024 | -228.18R | 0.607 |
| Discovery 2017–2020 | 2 pips | 1,024 | -417.16R | 0.389 |
| Validation 2021 | 0 pip | 257 | -15.56R | 0.870 |
| Validation 2021 | 1 pip | 257 | -64.37R | 0.560 |
| Validation 2021 | 2 pips | 257 | -113.19R | 0.351 |

Although following lost less than fading in some discovery comparisons, neither side supplies positive after-spread expectancy. This does not justify selecting the follow direction post hoc.

## Robustness and gate outcomes

The validation weekly bootstrap uses all 52 Monday-start weeks of 2021, including zero-trade weeks, circular blocks of four weeks, 10,000 resamples, seed 300. At the registered +1 pip cost, mean weekly net was **−1.1535R**, with 95% interval **[−1.5884R, −0.6723R]**; the entire interval is negative.

Only **4 of 14** registered gates passed: data integrity, discovery trade count, validation trade count, and exact active entry/exit timestamps. Expectancy, PF, annual stability, +2-pip stress, and the positive-bootstrap-bound gates failed.

## Decision and evolutionary disposition

**R300 = GAGAL; close the rule.** Do not tune the time window, impulse threshold, stop/target or holding period, and do not flip the direction as a rescue on these dates. Reuse only the engineering controls (exact BID/ASK timestamp joins, no synthetic candles, Europe/London DST mapping, side-correct fills, fixed phone-delay mapping, and active-path audit); retain neither trading direction as a proven alpha block.

Limitations: this is a historical signal screen, not a provider-equivalent funded challenge replay. The 2017–2021 EURUSD data are programme-contaminated, and actual provider commission, slippage, financing and FundedNext floating-equity/DLL/MLL path behavior remain unverified. No 2022–2025 PnL was calculated. A future candidate must use a genuinely different economic mechanism and still pass a fresh prospective/independent test before any funded-readiness claim.