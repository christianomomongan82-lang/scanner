# R292 — USA500 Overnight-Only Long Carry

**Verdict: GAGAL.** Frozen hypothesis: long USA500 at the final RTH bar close (16:00 proxy) and exit at the next eligible RTH open; one constant-notional overnight segment; no stop or target.

## Results

| Metric | Discovery 2017–2020 | Validation 2021 |
|---|---:|---:|
| Trades | 978 | 250 |
| Gross PF (bp outcomes) | 1.193 | 1.328 |
| Gross total bp | 3951.48 | 1242.22 |
| PF after modeled 2 bp | 1.094 | 1.186 |
| Net bp after modeled 2 bp | 1995.48 | 742.22 |
| PF after modeled 4 bp | 1.002 | 1.058 |
| Cumulative PnL as % of fixed notional after 2 bp | 19.95% | 7.42% |

Validation four-week circular block bootstrap: weekly mean 14.00 bp; 95% CI [-2.24, 30.11] bp/week. Because the lower bound crosses zero, the preregistered robustness gate fails.

## Annual discovery decomposition at 2 bp

| Year | Trades | PF | Net bp | PF at 4 bp |
|---|---:|---:|---:|---:|
| 2017 | 241 | 1.248 | 544.49 | 1.026 |
| 2018 | 243 | 1.084 | 401.62 | 0.983 |
| 2019 | 248 | 1.187 | 759.02 | 1.061 |
| 2020 | 246 | 1.028 | 290.35 | 0.981 |

Closed-trade drawdown relative to fixed notional reaches 38.57% in discovery at 2 bp, concentrated in 2020. This is a serious risk warning even before any funded loss-limit replay.

## Locked gates

- PASS — discovery_min_500_trades
- PASS — discovery_net_bp_2_positive
- PASS — discovery_pf_2bp_ge_1_05
- PASS — at_least_3_of_4_discovery_years_positive
- PASS — discovery_pf_4bp_ge_0_90
- PASS — validation_min_100_trades
- PASS — validation_net_bp_2_positive
- PASS — validation_pf_2bp_ge_1_05
- FAIL — validation_bootstrap_ci_lower_gt_zero
- PASS — validation_pf_4bp_ge_0_90

No post-2021 outcomes were calculated after the locked gates. This is a historical signal screen only: the source is BID-only M5, modeled costs are not observed execution costs, overnight floating drawdown and swaps were not modeled, and no FundedNext daily/max-loss equity-path replay was performed. Positive discovery and validation point estimates do not override the failed bootstrap gate. Do not retune this rule on the same periods.

Preregistration: [R292_USA500_OVERNIGHT_CARRY_PREREGISTRATION.md](R292_USA500_OVERNIGHT_CARRY_PREREGISTRATION.md)
