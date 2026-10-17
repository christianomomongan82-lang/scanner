# R295 Preregistration — USA500 Own-Session Direction Confirmation on Positive Breadth

**Candidate ID:** `R295_BREADTH_PLUS_USA500_DIRECTION_CONFIRMATION`  
**Status:** locked before R295 candidate outcome calculation  
**Date:** 2026-10-17  
**Parent lineage:** R293 positive-tail breadth filter, using R294's matched event/price ledger as the inherited data-integrity and timestamp source. R294's side decomposition showed the symmetric negative-breadth short tail was materially harmful. R295 does not trade short and does not alter R293's breadth threshold or holding interval.

## Hypothesis

Positive broad-market breadth can still occur when USA500 itself is flat or down (for example, three of four indices rise while USA500 is the lone non-positive index). An overnight long exposure on a non-positive USA500 cash-session return lacks agreement from the actual traded instrument. Requiring USA500 itself to have a positive 09:30-open to 15:45-close return may avoid those dissonant long entries. This tests a new context/alignment component, not a retune of the 75% breadth threshold.

## Frozen inputs and inherited execution

Use the four previously cached R205 Dukascopy M5 BID archives with the registered checksums:
- USA500 artifact 11709864394, SHA-256 `df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee`
- USATECH artifact 11710370389, SHA-256 `82b06c38f66cd1387097691baac1d45c9463b6540eea9dfe28a894d85e122f7c`
- USA30 artifact 11710730507, SHA-256 `8fcef9d76b31e99ae8d0175e769307ab13f930ae3ec2c17ef6baf0311ea1783a`
- USSC2000 artifact 11710111254, SHA-256 `c01c97d8705453d3fa3fd4ac1d386e9c1d72ab27e3b7d57d6cde53da9dfdf6f0`

Session validity, timestamps, missing-bar rejection, repeated-flat rejection, and costs inherit the R293/R294 rules. No fabricated bars. Session returns are `close(15:45 bar)/open(09:30 bar)-1`. The 15:45 bar close becomes known at 15:50 ET. Enter USA500 at the 15:55 ET M5 bar open, exactly T+10 from the 15:45 bar-open timestamp. Exit at the next quality-valid USA500 09:30 RTH open; skip if the next eligible session is over seven calendar days later or crosses the frozen split boundary. No stop, target, leverage compounding, stacking or discretionary skips.

## Frozen child rule

1. Calculate positive breadth exactly as R293: at least 75% of all quality-valid index feeds on that date (minimum three valid feeds) must have a strictly positive 09:30-open to 15:45-close return.
2. Add one new required confirmation: USA500's own 09:30-open to 15:45-close return must be strictly positive.
3. If both conditions are true, buy USA500 at the 15:55 bar open; otherwise remain flat. No shorts.
4. Gross return in bp is `(next eligible 09:30 USA500 bid open / entry 15:55 USA500 bid open - 1) * 10,000`; deduct modeled 1, 2 and 4 bp per round trip. Use 2 bp as the primary cost.
5. The matched parent is the full R293 positive-breadth long-only stream without the USA500 own-direction filter, on the exact same eligible session dates, fills and costs. This is diagnostic, not a second promotion candidate.

## Frozen partitions and gates

- Discovery: entry dates 2017-01-01 through 2020-12-31.
- Validation: entry dates 2021-01-01 through 2021-12-31.
- Do not calculate R295 strategy PnL for 2022 or later unless every locked discovery and validation gate passes. Related periods 2017–2021 are already contaminated and cannot be described as pristine program-level OOS.
- Discovery at modeled 2 bp: at least 200 trades; net total bp > 0; PF >= 1.05; at least 2 of 4 annual cohorts positive. Discovery PF at modeled 4 bp >= 0.90.
- Validation at modeled 2 bp: at least 75 trades; net total bp > 0; PF >= 1.05; four-week circular block-bootstrap 95% CI lower bound for mean weekly net bp strictly > 0 (5,000 resamples, seed 295; include all 52 Monday-start weeks including zero-trade weeks). Validation PF at 4 bp >= 0.90.
- Bootstrap PnL is bucketed by exit week; sample circular four-week blocks.
- Any failed gate means **GAGAL**. Do not alter the breadth threshold, own-return confirmation, execution timing, exit, costs or time split after results. No same-period parameter rescue.

## Limitations and promotion boundary

All feeds are BID-only; modeled cost deductions do not establish executable bid/ask fills, slippage, commission, point value or swaps. No overnight floating loss, margin, FundedNext rule-aware two-phase equity path, completion probability or time-to-target is computed at this alpha-screen stage. Even if every historical gate passes, promotion requires a separate verified-cost and account-equity replay. If the screen fails, do not run a funded replay.

## Required artifacts

Store a local replay runner, compact JSON, final report, candidate and matched-parent ledgers, and session-quality/skipped-date audit. Run in local Python only; do not create or dispatch a GitHub Actions backtest workflow.
