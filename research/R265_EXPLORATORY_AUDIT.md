# R265 Relative-Value Mean Reversion — Retrospective Audit

Date archived: 2026-10-16  
**Research status: exploratory / not promotion-eligible. Verdict: FAILED.**

This R265 output was present locally but a contemporaneous preregistration was not found in the GitHub branch at the time of this audit. Its specification can be recovered from the saved runner, but the timing of the lock cannot be independently proven. Additionally, the aggregate output includes all available dates through 2026-10-09, so the aggregate whole-sample metrics cannot be used as clean out-of-sample evidence. The specific 2022–2025 forward split is reported separately below; no 2026 result is used for promotion.

## Hypothesis and method

Test whether the relative log-price ratio of USATECH to USA500 mean-reverts after a 60-session z-score reaches ±2. Enter the two-index equal-notional pair at the next common RTH session open; exit after z-score returns to zero, reaches adverse ±3, or reaches a maximum of 10 sessions. A 5-minute delayed entry uses the 09:35 ET open. Costs of +2/+4/+6 bps per pair trade are assumed sensitivities; only BID prices are available.

## Forward 2022–2025 results

| Entry mode | Trades | PF +2 bps | PF +4 bps | Net bps +4 | Bootstrap 95% CI (bps/week) at +4 |
|---|---:|---:|---:|---:|---|
| 09:30 ideal | 41 | 1.496 | 1.395 | +399.9 | [-2.64, +6.66] |
| 09:35 delay | 41 | 1.404 | 1.313 | +332.4 | [-3.14, +6.43] |

## Verdict

The forward sample contains only 41 closed trades in 2022–2025, below the pre-existing minimum research threshold of 100 trades. Both four-week block-bootstrap confidence intervals include zero. The 60-session relative-value idea therefore fails the evidence/frequency gate; no tuning is permitted.

At +4 bps, the whole-file aggregate was negative for ideal and delayed modes, but the saved output’s aggregate runs through the entire available date range (including 2026) and is not an authorized OOS statistic. Do not use it for promotion decisions.

## Limitations

- BID-only index history; no ASK-side quotes or observed spread.
- Fixed costs are scenarios, not verified execution costs.
- Not a funded-account simulation; DLL/MLL, actual costs and Quick Strike remain unverified.
- This archive documents an exploratory run, not proof of a preregistered experiment.
