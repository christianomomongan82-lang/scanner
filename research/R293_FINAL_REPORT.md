# R293 — USA500 Overnight Carry With Closing Cross-Index Breadth

**Verdict: GAGAL.** The locked validation bootstrap requirement failed; no later-period PnL or funded replay was run.

## Candidate results

| Metric | Discovery 2017–2020 | Validation 2021 |
|---|---:|---:|
| Trades | 442 | 119 |
| Gross total (bp) | 2204.41 | 487.78 |
| Net total at 2 bp (bp) | 1320.41 | 249.78 |
| Profit factor at 2 bp | 1.137 | 1.144 |
| Net total at 4 bp (bp) | 436.41 | 11.78 |
| Profit factor at 4 bp | 1.043 | 1.006 |
| Maximum closed-PnL drawdown (% fixed notional) | 24.54 | 4.20 |

## Matched unconditional parent (diagnostic only)

| Metric | Discovery 2017–2020 | Validation 2021 |
|---|---:|---:|
| Trades | 975 | 250 |
| Net total at 2 bp (bp) | 1533.09 | 459.12 |
| Profit factor at 2 bp | 1.070 | 1.109 |
| Net total at 4 bp (bp) | -416.91 | -40.88 |
| Profit factor at 4 bp | 0.982 | 0.991 |
| Maximum closed-PnL drawdown (% fixed notional) | 37.96 | 3.40 |

## Annual discovery decomposition at 2 bp

| Year | Candidate trades | Candidate PF | Candidate net bp | Parent trades | Parent PF | Parent net bp |
|---|---:|---:|---:|---:|---:|---:|
| 2017 | 92 | 1.085 | +72.78 | 241 | 1.192 | +431.42 |
| 2018 | 95 | 1.466 | +660.73 | 240 | 1.044 | +211.41 |
| 2019 | 129 | 1.032 | +81.10 | 248 | 1.224 | +947.69 |
| 2020 | 126 | 1.105 | +505.80 | 246 | 0.995 | -57.44 |

## Validation weekly bootstrap

- Candidate: mean 4.803 bp/week; 95% CI [-5.548, 14.232] using 5,000 circular resamples of four-week blocks and 52 weeks including zero-trade weeks.
- Parent: mean 8.829 bp/week; 95% CI [-5.639, 24.051].

## Locked gate results

| Gate | Result |
|---|---|
| discovery_min_200_trades | PASS |
| discovery_net_bp_2_positive | PASS |
| discovery_pf_2bp_ge_1_05 | PASS |
| discovery_at_least_2_of_4_years_positive | PASS |
| discovery_pf_4bp_ge_0_90 | PASS |
| validation_min_75_trades | PASS |
| validation_net_bp_2_positive | PASS |
| validation_pf_2bp_ge_1_05 | PASS |
| validation_bootstrap_ci_lower_gt_zero | FAIL |
| validation_pf_4bp_ge_0_90 | PASS |

## Interpretation

The breadth-filtered child improves PF at 2 bp versus the unconditional parent in both discovery (1.137 vs 1.070) and validation (1.144 vs 1.109), and reduces discovery closed-PnL drawdown from 37.96% to 24.54% of fixed notional. However, it trades less frequently and generates lower total net bp than the parent in both discovery and validation. Crucially, the locked 2021 four-week bootstrap CI crosses zero, so the strategy does not meet the statistical robustness gate.

**Disposition: GAGAL.** Do not retune the breadth threshold or entry/exit using the same periods. Keep only the research lesson that breadth filtering improved relative PF/drawdown in this historical sample; it is not evidence of a validated alpha block.

## Input integrity and limitations

- All four cached M5 BID archives passed their registered SHA-256 checks. The session audit covered 2016–2021; the candidate outcome ledger used entry dates 2017–2021 only.
- Modeled 1/2/4 bp round-trip costs do not verify real spread, ASK fills, slippage, commission, point value or swaps.
- No overnight floating loss, margin, FundedNext daily/max-loss equity-path, two-phase completion probability or time-to-target simulation was run because the validation gate failed.
- Historical 2017–2021 windows are already contaminated by related project experiments; even a historical screen pass would not be pristine program-level OOS.
- **No strategy PnL was calculated for 2022 or later.**
