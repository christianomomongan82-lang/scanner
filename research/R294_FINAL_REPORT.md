# R294 — USA500 Two-Sided Extreme-Breadth Overnight Direction

**Verdict: GAGAL**

All rules were preregistered before candidate outcomes were calculated. No 2022+ candidate PnL was calculated.

## Candidate vs controls at modeled 2 bp

| Metric | Discovery 2017–2020 | Validation 2021 |
|---|---:|---:|
| Candidate trades | 786 | 216 |
| Long trades | 442 | 119 |
| Short trades | 344 | 97 |
| Net bp @2bp | -137.72 | -448.43 |
| PF @2bp | 0.993 | 0.891 |
| Net bp @4bp | -1709.72 | -880.43 |
| PF @4bp | 0.918 | 0.797 |
| Max closed-PnL DD (% fixed notional) | 29.36 | 9.31 |

## Matched controls at 2 bp

| Series | Period | Trades | Net bp | PF |
|---|---|---:|---:|---:|
| R293 positive-tail long-only | discovery | 442 | +1320.41 | 1.137 |
| Unconditional long | discovery | 975 | +1533.09 | 1.070 |
| R293 positive-tail long-only | validation | 119 | +249.78 | 1.144 |
| Unconditional long | validation | 250 | +459.12 | 1.109 |

## Annual discovery cohorts @ 2 bp

| Year | Trades | Long | Short | Net bp | PF |
|---|---:|---:|---:|---:|---:|
| 2017 | 152 | 92 | 60 | -327.49 | 0.813 |
| 2018 | 186 | 95 | 91 | +609.19 | 1.167 |
| 2019 | 227 | 129 | 98 | -1249.12 | 0.755 |
| 2020 | 221 | 126 | 95 | +829.70 | 1.087 |

## Validation weekly bootstrap

- Mean: -8.6236 bp/week; 95% CI [-26.0117, 7.1954] over 52 weeks (including zeros), 5,000 circular 4-week block resamples.

## Locked gates

| Gate | Result |
|---|---|
| discovery_min_200_trades | PASS |
| discovery_net_bp_2_positive | FAIL |
| discovery_pf_2bp_ge_1_05 | FAIL |
| discovery_at_least_2_of_4_years_positive | PASS |
| discovery_pf_4bp_ge_0_90 | PASS |
| validation_min_75_trades | PASS |
| validation_net_bp_2_positive | FAIL |
| validation_pf_2bp_ge_1_05 | FAIL |
| validation_bootstrap_ci_lower_gt_zero | FAIL |
| validation_pf_4bp_ge_0_90 | FAIL |

## Interpretation and limitations

- Adding the negative-breadth short tail increased event coverage but destroyed net expectancy: it lost in discovery and validation at 2 bp.
- R293 positive-tail long-only remained stronger than R294 and the unconditional long parent on PF in both partitions.
- BID-only inputs cannot verify short ASK-side entry/exit; 1/2/4 bp are modeled cost sensitivities.
- No live spread, slippage, commission, swap, margin, overnight floating loss, or funded challenge equity path was modeled.
- 2017–2021 is research-contaminated, and no strategy PnL from 2022 onward was calculated.
