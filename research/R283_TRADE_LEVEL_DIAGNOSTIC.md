# R283 Trade-Level Diagnostic — Why the Gap Fade Failed

**Diagnosis status: completed from the 872-row local trade ledger. Strategy verdict remains GAGAL.**  
This is a post-result decomposition of the locked R283 trades, not a parameter search. No rules were changed and no 2022–2025 results were inspected.

## Core result

| Segment | Trades | PF before modeled cost | Gross net R | PF @ 2 bp | Net R @ 2 bp | Mean net R/trade |
|---|---:|---:|---:|---:|---:|---:|
| Discovery 2017–2020 | 709 | 0.795 | -61.750 | 0.748 | -77.900 | -0.110 |
| Validation 2021 | 163 | 0.638 | -30.520 | 0.599 | -34.830 | -0.214 |

The strategy is already negative before modeled costs. The 2-bp model removed a further 16.150R in discovery and 4.310R in validation, but it did not create the failure.

## Exit mechanics explain the losses

| Segment | Exit | Trades | Share | Gross R | Net R @ 2 bp | Mean net R |
|---|---|---:|---:|---:|---:|---:|
| Discovery | Target | 151 | 21.30% | +166.291 | +162.554 | +1.077 |
| Discovery | Target gap-open | 1 | 0.14% | +1.167 | +1.132 | +1.132 |
| Discovery | Stop | 237 | 33.43% | -237.000 | -242.630 | -1.024 |
| Discovery | Session close | 320 | 45.13% | +7.792 | +1.043 | +0.003 |
| Validation | Target | 35 | 21.47% | +39.490 | +38.600 | +1.103 |
| Validation | Stop | 71 | 43.56% | -71.000 | -72.950 | -1.027 |
| Validation | Stop gap-open | 1 | 0.61% | -1.001 | -1.020 | -1.020 |
| Validation | Session close | 56 | 34.36% | +1.992 | +0.539 | +0.010 |

**Discovery:** 152 target exits versus 237 stop exits. Among trades resolved by target or stop, only 39.07% reached target; given the observed average target win (~1.077R) and stop loss (~1.024R), the break-even target share is about 48.7%, before considering time exits. Session-close trades were almost flat after costs and did not compensate for the stop/target imbalance.

**Validation 2021:** 35 target exits versus 72 stop exits. Only 32.71% of target/stop-resolved trades reached target, versus a break-even share around 48.2%. The stop-exit share rose from 33.43% to 44.17%; the target-exit share stayed near 21.3–21.5%. This is the clearest deterioration across periods.

## Directional asymmetry

“LONG” means buying after a gap down to fade it; “SHORT” means shorting after a gap up to fade it.

| Segment | Direction | Trades | Net R @ 2 bp | PF | Positive trade % | Target exits % | Stop exits % |
|---|---|---:|---:|---:|---:|---:|---:|
| Discovery | LONG | 316 | -17.159 | 0.870 | 47.47% | 23.73% | 34.81% |
| Discovery | SHORT | 393 | -60.741 | 0.658 | 37.40% | 19.59% | 32.32% |
| Validation | LONG | 82 | -10.738 | 0.732 | 46.34% | 17.07% | 45.12% |
| Validation | SHORT | 81 | -24.092 | 0.486 | 32.10% | 25.93% | 43.21% |

Fading gap-ups (SHORT) was substantially weaker than fading gap-downs in both periods. Neither direction was profitable. This is a diagnostic finding, **not evidence that gap continuation has an edge**.

## Instrument and year consistency

At 2 bp, net R by instrument:
- Discovery: USA500 -27.731R; USATECH -26.869R; USA30 -13.916R; USSC2000 -9.383R.
- Validation 2021: USA500 -12.918R; USA30 -12.481R; USSC2000 -9.496R; USATECH +0.065R (effectively flat, not a meaningful pass).

Annual discovery net R was negative in every year: 2017 -0.832R (only 28 trades), 2018 -8.103R, 2019 -25.076R, and 2020 -43.889R. Validation 2021 was -34.830R.

A descriptive four-week block bootstrap on weekly aggregated net R at 2 bp (50,000 resamples; seed 283) gave mean weekly net R / 95% interval of -0.590 / [-1.152, -0.072] for discovery (132 weeks) and -0.941 / [-1.458, -0.433] for validation (37 weeks). This is a post-hoc diagnostic, not a preregistered gate; summing R across simultaneous instruments is not a funded-account exposure simulation.

## Decision and next use

1. **Close this exact R283 specification as GAGAL.** Do not tune its quantile, stop multiplier, entry time, or target after seeing results.
2. **Costs are secondary, not the root cause.** The gross strategy was negative before the modeled cost subtraction.
3. The key mechanism is inadequate target attainment relative to stop hits; this worsened in 2021. Gap-up fades were particularly weak.
4. Do not promote the inverse/continuation direction based on this decomposition alone. Any new hypothesis must have its own locked rules and must be treated as exploratory where prior family-level data have already been examined.
5. No funded-ready claim follows from this test. Broker BID/ASK execution costs, CFD specifications, and FundedNext equity-path replay remain unverified.

## Reproducibility limitation

The 872-row file `R283_trade_ledger.csv` and exact runner `r283_cash_open_gap_fade.py` were present in the current local analysis workspace and used for these figures, but **the full row-level ledger and runner have not yet been committed to this GitHub branch**. The aggregate diagnostic tables and this report are archived; repository-only reproduction remains incomplete until those source artifacts are added. The cached input ZIP hashes and the R283 preregistration/report/results remain in the repository.
