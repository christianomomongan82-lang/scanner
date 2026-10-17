# R292 — USA500 Overnight-Only Long Carry
**Status:** preregistered before calculating candidate returns  
**Hypothesis family:** overnight/intraday return decomposition; not a breakout or intraday directional trigger

## Frozen hypothesis
The long-only USA500 equity-index drift may be concentrated in the interval from the end of the U.S. regular session to the next regular-session open. Test the overnight segment as a standalone exposure, not a prediction rule.

## Input and eligibility
- One instrument only: `usa500idxusd_m5.csv.gz`, cached R205 artifact previously ID 11709864394, SHA-256 `df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee`.
- Use `America/New_York` exchange-local timezone and exact M5 bars starting 09:30 through 15:55 (78 bars/session).
- Reject incomplete/incorrect timestamp sequences, invalid OHLC, duplicate timestamps and repeated-flat placeholders (OHLC all equal and close repeats previous row). Do not fill missing bars.
- Eligible dates: 2017-01-01 through 2021-12-31. No results past 2021 may be calculated unless every gate below passes.

## Entry / exit
- Buy the eligible session's final 15:55 M5 bar close (proxy for 16:00 New York) using a long-only constant-notional exposure.
- Exit at the 09:30 open of the next eligible USA500 RTH session.
- No intraday stop, take-profit, direction filter, volatility filter, weekday filter, or discretionary skip; this is a pure baseline for overnight-segment drift.
- Long overnight holding includes weekends and exchange holidays if the next eligible session is the next available cash session. No same-day return is added.
- Net simple return in basis points = (next-session RTH open / prior session final close − 1) × 10,000 − modeled round-trip cost. Costs 1, 2 and 4 bp are sensitivities, not verified FundedNext charges or spread.
- This first-stage alpha screen does not infer executable BID/ASK fills from BID-only OHLC. It also does not establish margin, swap charges, funding rules, floating drawdown or funded challenge pass odds.

## Locked periods and binary gates
- Discovery: 2017–2020. Validation: 2021. Historical windows are project-contaminated and not pristine unseen data.
- At modeled 2 bp, discovery requires at least 500 overnight trades, aggregate net basis points > 0, PF of net basis-point outcomes ≥ 1.05, and at least three of four annual net returns positive.
- Cost robustness requires discovery PF at modeled 4 bp ≥ 0.90.
- Validation requires at least 100 trades, net bp > 0, PF ≥ 1.05 at modeled 2 bp, 4-week circular block bootstrap (5,000 resamples, seed 292) of weekly net bp with 95% CI lower bound strictly > 0, and PF ≥ 0.90 at 4 bp.
- Any failed gate = **GAGAL**. Do not tune the holding interval, session times, direction, instrument, cost or filters after seeing 2017–2021 results. No second pass over the same period.
- Only if every gate passes may 2022–2026 be examined, labeled exploratory due project contamination. A historical pass still requires a separate execution, swap, overnight floating equity, DLL/MLL, and funded-challenge equity-path replay.