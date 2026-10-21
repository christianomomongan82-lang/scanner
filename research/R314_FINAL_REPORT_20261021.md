# R314 final report — XAUUSD NY clock-time directional drift

**Verdict: GAGAL at discovery.** No validation candidate was selected or run. The protected 2026 outcomes were not scored.

## What was tested

The preregistered test evaluated 96 fixed candidates: 48 half-hour New York clock slots × LONG/SHORT. For each slot, enter at the next paired active M5 quote exactly five minutes after the slot open, with fixed stop = the trailing median BID true range over the previous 12 bars, target = 1.25R, quote-side execution, stop-first if barriers share a bar, a 60-minute maximum hold, one active trade at a time and no more than one per NY date. The primary cost screen deducted an extra $0.30/oz beyond observed BID/ASK. Selection used the 2016–2020 discovery years; all thresholds were locked in [the preregistration](R314_XAUUSD_CLOCK_TIME_DRIFT_SEARCH_PREREGISTRATION.md).

## Discovery results (2016–2020)

| Metric | Result |
|---|---:|
| Registered candidates | 96 |
| Candidates with completed trades | 92 |
| Candidates meeting prerequisite (>=200 trades and positive net R at +$0.30/oz) | **0** |
| Candidates with positive net R at +$0.30/oz | **0** |
| Aggregate trade rows across candidate streams | 118,036 |
| Best active candidate (least-negative net R and best t-statistic): 10:00 NY LONG | |
| Trades | 1,290 |
| Net R at +$0.30/oz | **−605.866R** |
| PF_R | **0.427** |
| Win rate | 35.35% |
| Mean weekly net R | −2.321R |
| HAC t-statistic on weekly R (4 lags) | −11.19 |
| One-sided p for positive mean | 1.0 |
| Holm-adjusted p | 1.0 |

Every one of the 92 active candidate streams lost after the primary added-cost assumption. The four remaining candidates had zero completed trades because their registered slot lacked a valid stop/entry quote series. The best observed candidate was still strongly negative; no multiple-testing adjustment can turn a failed eligibility gate into a candidate.

The 118,036 trade count is the **sum across mutually overlapping counterfactual candidate streams**, not a portfolio simulation or a single strategy's trade count.

## Data and audit details

- Source archive SHA-256: `2cde8338800fd7f4d5d4628512201c16757ef06bd90d51ffdc8ef9bea425ba1a`.
- Paired raw BID and ASK files each had 877,930 rows before the strict pre-2026 / phase split. Discovery calculation used 439,073 phase rows, 354,177 active paired M5 rows after validity/static-bar filtering.
- Discovery quote window used: 2016-01-03 23:00 UTC through 2020-12-31 21:55 UTC. Missing/static bars were not synthesized.
- Compressed full event/trade ledger generated locally: 8,707,973 bytes, SHA-256 `0be5a087f8d2dc6611330fa4f41cacddf83a5f77e737d853f055726c3befdf37`.
- 96-candidate result table SHA-256: `95469a7098064afa63a91a6ada43d90a63d5f03e8e51b5ee8df3c48c67873243`.
- Result JSON SHA-256: `5d5b99d86b33388bc384d9d8b019bfe804144159b702c966511b547146087c86`.
- The raw source data's protected 2026 outcomes remained excluded. This is a discovery failure; no 2021–2025 candidate-validation PnL was calculated.

## Conclusion

The hypothesis that a fixed NY clock-time directional drift by itself can provide the required edge is rejected on the registered discovery sample. Do not invert direction, choose a neighboring slot, or rescue this family with weekday/trend filters after seeing the results. R314 is **GAGAL**, not a funded strategy.
