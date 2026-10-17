# R291 — U.S. Cash-Session Lead → German Index Follow-Through
**Verdict: GAGAL.** No signal block retained.

The hypothesis was that a large S&P 500 cash-session move would predict follow-through in the next German session. This was preregistered before scoring, with PnL locked to 2017–2021 unless all historical gates passed.

## Results

| Period | Trades | Gross PF_R | Gross net R | PF_R @1bp | Net R @1bp | PF_R @2bp | Net R @2bp | PF_R @4bp | Net R @4bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Discovery 2017–2020 | 246 | 0.769 | −36.653R | 0.574 | −85.537R | 0.451 | −134.421R | 0.302 | −232.189R |
| Validation 2021 | 74 | 1.228 | +8.547R | 0.332 | −82.566R | 0.178 | −173.679R | 0.082 | −355.905R |

The frozen Q75 absolute USA500 cash-session return threshold was **0.673764%**, fitted on 979 eligible sessions in 2017–2020. All four discovery calendar years were negative at modeled 2 bp costs:

| Year | Trades | PF_R @2bp | Net R @2bp |
|---|---:|---:|---:|
| 2017 | 11 | 0.245 | −11.778R |
| 2018 | 74 | 0.518 | −32.295R |
| 2019 | 48 | 0.334 | −42.472R |
| 2020 | 113 | 0.514 | −47.876R |

The 2021 weekly-net-R four-week circular bootstrap (5,000 resamples, seed 291) had mean −3.277R/week and 95% CI **[−9.525, +0.040]R/week**. The lower bound does not exceed zero.

## Why it failed

- Discovery expectancy was negative even **before modeled costs**: PF_R 0.769 and net −36.653R.
- Every preregistered PF/expectancy/stability/cost gate failed; only minimum trade counts passed.
- The stop definition allows extremely narrow risk distances. One 2021 trade had a 0.02-point stop distance; under the frozen 1 bp cost assumption alone, its cost equaled about 75.6R. That reveals the rule is not realistically tradable as specified. This is a post-result diagnosis, **not** permission to add a stop-distance filter and re-test the same windows.

No 2022–2026 candidate PnL was calculated. Do not tune this candidate or inherit it into a portfolio.

## Inputs and limits

- USA500 M5 BID-only SHA-256: `df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee` (cached R205 artifact ID 11709864394).
- DEUIDXEUR M5 BID-only SHA-256: `7ad37cb19545eef6111b928a97322c06c9f2478030a0c4282669542262303af4`.
- Modeled 1/2/4 bp costs are sensitivity assumptions, not verified FundedNext spreads, slippage, fees, or swaps.
- Both directions use BID-side proxy fills; five-minute OHLC cannot certify tick-level stop/target sequence. Flat-placeholder filtering is heuristic.
- 2021 has been viewed in other project experiments and is not a pristine program-level holdout.
- Even a historical pass would require actual quote-side execution modeling and full funded-equity, daily-loss, maximum-loss, and challenge-duration replay.

Preregistration: [R291_TRANSATLANTIC_LEAD_LAG_PREREGISTRATION.md](R291_TRANSATLANTIC_LEAD_LAG_PREREGISTRATION.md)
