# R294 Preregistration — Two-Sided Extreme-Breadth Overnight Direction

**Candidate ID:** `R294_USA500_TWO_SIDED_BREADTH_OVERNIGHT`  
**Status:** locked before candidate outcomes are calculated  
**Date:** 2026-10-17  
**Parent lineage:** R293 (positive breadth as overnight context) × R292 (fixed USA500 overnight holding interval). This is a direction-mapping crossover, not a threshold/exit retune of R293.

## Hypothesis

R293's positive-tail filter increased historical profit factor and reduced discovery closed-PnL drawdown versus the same-time unconditional long parent, but cut trade count and aggregate net return. A distinct hypothesis is that *extreme breadth in either direction* may indicate overnight directional persistence: buy USA500 after an extreme positive close and sell short after an extreme negative close. This test restores a symmetric short tail without changing the long-side threshold, signal timestamp, entry, exit or costs.

## Frozen data and quality rules

Use only the previously cached R205 Dukascopy M5 BID archives:
- USA500: artifact 11709864394; SHA-256 `df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee`
- USATECH: artifact 11710370389; SHA-256 `82b06c38f66cd1387097691baac1d45c9463b6540eea9dfe28a894d85e122f7c`
- USA30: artifact 11710730507; SHA-256 `8fcef9d76b31e99ae8d0175e769307ab13f930ae3ec2c17ef6baf0311ea1783a`
- USSC2000: artifact 11710111254; SHA-256 `c01c97d8705453d3fa3fd4ac1d386e9c1d72ab27e3b7d57d6cde53da9dfdf6f0`

- Convert bar-open Unix-millisecond timestamps to `America/New_York`.
- A valid RTH session must have exactly the 78 five-minute bars starting 09:30–15:55 ET, valid positive OHLC and exact timestamps; reject duplicates, missing bars, invalid OHLC and repeated-flat placeholders (O=H=L=C=previous raw row close). Do not synthesize missing bars.
- Require a valid USA500 session and at least three valid index feeds for that date. Breadth is calculated only from those valid feeds. Do not fill missing index returns.
- The 15:45 bar close is the confirmed signal, available at 15:50 ET. Use return `close(15:45)/open(09:30)-1` for every quality-valid index.
- Use entry at the open of the USA500 15:55 ET bar, exactly T+10 minutes from the 15:45 signal bar's opening timestamp (five-minute bar confirmation plus the user's five-minute phone-execution delay). The intervening 15:50 bar must exist; do not use its high/low/close to improve the fill.
- Exit at the next quality-valid USA500 RTH session's 09:30 open. Skip the signal if the next eligible session is over seven calendar days later. No trade stacking or discretionary skip.

## Frozen direction rule

Let `p` be the fraction of valid feeds with positive 09:30-open to 15:45-close return.

- If `p >= 0.75`, enter long USA500.
- Else if `p <= 0.25`, enter short USA500.
- Else, remain flat.
- These symmetric inequalities are fixed. For three valid feeds, all-positive triggers long and none-positive triggers short. For four feeds, at least 3 positive triggers long and at most 1 positive triggers short.
- Do not add any volatility, weekday, instrument, trend, gap, stop or target filters. Do not change the direction map after results.

Gross directional return in bp is `side * (exit_bid / entry_bid - 1) * 10,000`, where side is +1 for long and -1 for short. Deduct modeled 1, 2 and 4 bp round-trip costs. The primary cost is 2 bp; 1/2/4 bp are sensitivities, not observed executable costs. The BID-only series cannot establish actual short ASK-side exit fills, live spread, commission or slippage; this remains a material limitation.

## Matched diagnostics

Report both:
1. R294 symmetric-tail child (frozen long/short rule).
2. R293 positive-tail long-only rule at the same timestamps.
3. Unconditional USA500 long at the same timestamps.

All share the same valid-session date set, entry/exit prices, skip conditions and cost schedule. Parents are diagnostics; the locked child is judged only against the preregistered absolute gates, not selected after comparing later-period results.

## Locked periods and binary gates

- Discovery: entry dates 2017-01-01 to 2020-12-31.
- Validation: entry dates 2021-01-01 to 2021-12-31.
- Do not calculate any 2022+ strategy PnL unless every discovery and validation gate below passes. 2017–2021 has prior-project contamination and is not a pristine program-level holdout.
- Discovery at 2 bp: at least 200 trades; net total bp > 0; PF >= 1.05; at least 2 of 4 annual net-bp cohorts positive. Discovery PF at 4 bp >= 0.90.
- Validation at 2 bp: at least 75 trades; net total bp > 0; PF >= 1.05; four-week circular block bootstrap 95% CI lower bound for mean weekly net bp strictly > 0 (5,000 resamples; seed 294; include all Monday-start weeks, including zero-trade weeks). Validation PF at 4 bp >= 0.90.
- Bootstrap weekly net is bucketed by **exit week**; include all Monday-start weeks in calendar year 2021 and sample circular four-week blocks.
- Any failed gate means **GAGAL**. No post-result change to threshold, direction, entry/exit, costs, or period split, and no rescue on the same windows.
- Calculate no post-2021 signal PnL if any gate fails. No FundedNext challenge replay is allowed when the signal screen fails.

## Promotion boundary and artifacts

Even a historical screen pass is not funded-ready. Before any challenge claim, the method requires verified bid/ask execution, CFD point value, realistic spread/slippage/commission/swap, overnight floating equity, server-day daily-loss reset, static maximum loss, target sequence, minimum trading days, Quick Strike and a two-phase equity-aware challenge replay. Store runner, source/quality audit, trade ledgers, result JSON, annual breakdown and binary report in this repository branch. Run locally in Python only; do not create or dispatch a GitHub Actions backtest workflow.
