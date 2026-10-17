# R293 Preregistration — USA500 Overnight Carry With Closing Cross-Index Breadth

**Candidate ID:** `R293_USA500_OVERNIGHT_BREADTH_FILTER`  
**Status:** locked before candidate PnL calculation  
**Date:** 2026-10-17  
**Parent lineage:** R292 (overnight return segment) × R205/R276 (cross-index breadth as market-context information). This is a new context/holding-period crossover, not a retune of R292's close-to-open entry rule.

## Hypothesis

USA500's next-session overnight return may be more favorable when at least 75% of the quality-valid US equity-index CFDs finished the prior regular session in positive territory by the same late-session signal timestamp. The cross-index vote is a context filter for a single USA500 overnight exposure; it does not use price indicators, opening-range triggers, cross-sectional residual ranking, or any R292 threshold.

## Frozen data inputs and integrity

Use only cached R205 Dukascopy M5 BID archives:
- `usa500idxusd_m5.csv.gz` — artifact 11709864394 — SHA-256 `df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee`
- `usatechidxusd_m5.csv.gz` — artifact 11710370389 — SHA-256 `82b06c38f66cd1387097691baac1d45c9463b6540eea9dfe28a894d85e122f7c`
- `usa30idxusd_m5.csv.gz` — artifact 11710730507 — SHA-256 `8fcef9d76b31e99ae8d0175e769307ab13f930ae3ec2c17ef6baf0311ea1783a`
- `ussc2000idxusd_m5.csv.gz` — artifact 11710111254 — SHA-256 `c01c97d8705453d3fa3fd4ac1d386e9c1d72ab27e3b7d57d6cde53da9dfdf6f0`

- All timestamps are bar-open Unix milliseconds; convert to `America/New_York` using DST-aware conversion.
- A valid instrument-session must contain exactly the 78 five-minute bars starting 09:30 through 15:55 ET; timestamps must match the exact grid; OHLC must be valid and positive; reject duplicate timestamps, gaps, inconsistent OHLC, and any repeated-flat placeholder defined as O=H=L=C=the previous raw row's close. Do not synthesize or fill missing bars.
- Require a valid USA500 session and at least three valid instruments for the same date. If only three instruments are valid, the breadth condition requires all three to have positive close-to-open return. Do not backfill missing symbols or dates.
- Signal return for each valid index is `close(15:45 bar) / open(09:30 bar) - 1`. The 15:45 bar's close is known at 15:50 ET. The signal excludes later bars.
- Retain rejected-session counts/reasons, eligible-date coverage and source hashes in the replay outputs.

## Candidate rules (locked)

1. At the close of the 15:45 ET bar (15:50 ET confirmation), count valid indices with a positive session return `close(15:45) / open(09:30) - 1 > 0`.
2. Enter **long USA500 only** at the open of the 15:55 ET bar. This is T+10 from the signal bar's opening timestamp (five minutes for bar confirmation plus five minutes of phone execution delay). The intervening 15:50 bar must exist, but its OHLC must not be used to improve the entry.
3. Enter only when at least 75% of valid symbols are positive: for 3 valid symbols require 3/3; for 4 require at least 3/4. Otherwise stay flat. No shorts, no position stacking, no discretionary filters, stops, targets or scaling.
4. Exit at the open of the next quality-valid USA500 RTH session. The return therefore includes the final five minutes of the entry session through the next session open. Omit if the next eligible session is more than seven calendar days later. No synthetic rows are filled.
5. Matched parent: buy USA500 at the same 15:55 open and exit at the same next-session 09:30 open on every quality-valid date, independent of breadth. The parent is a same-timestamp baseline only and cannot be promoted under this test.
6. Gross return in bps is `(exit_bid / entry_bid - 1) * 10,000`. Deduct 1, 2 and 4 bps per round trip as cost sensitivities; 2 bps is primary. These are hypothetical costs, not observed spread/commission/slippage. Input is BID-only, so no executable ASK-side fill is inferred.
7. Do not model leverage, swaps, margin, overnight floating loss or challenge account equity at this screening stage; report these as limitations. No funded challenge replay unless all signal-screen gates pass.

## Locked periods and gates

- Discovery: entry dates 2017-01-01 through 2020-12-31.
- Validation: entry dates 2021-01-01 through 2021-12-31.
- Do not calculate any 2022+ strategy PnL unless every discovery and validation gate below passes. Even then, 2022–2025 are contaminated exploratory windows in this project, not pristine program-level OOS.
- Discovery at 2 bps must have: at least 200 trades; net total bps > 0; PF >= 1.05; at least 2 of 4 annual cohorts with positive net bps. Discovery PF at 4 bps must be >= 0.90.
- Validation at 2 bps must have: at least 75 trades; net total bps > 0; PF >= 1.05; four-week circular block-bootstrap 95% CI lower bound for mean weekly net bps strictly > 0 (5,000 resamples, seed 293, with zero-trade weeks included). Validation PF at 4 bps must be >= 0.90.
- For the weekly bootstrap, bucket validation net returns by **exit week**, include every Monday-start week in the 2021 validation window (including zero-trade weeks), and use circular four-week blocks.
- Any failed gate means **GAGAL**. No post-result changes to breadth threshold, instruments, time window, entry timing, direction, exit, costs or gates. No parameter rescue on these dates.
- Calculate and compare the matched parent under identical session eligibility, entry/exit and cost assumptions. Report it as a diagnostic, not as a second chance to choose direction after seeing results.

## Interpretation and promotion boundary

R293 is a single preregistered evolutionary crossover: R292's overnight segment plus the R205/R276 broad-breadth context, with a delayed pre-close entry. Historical periods have already been studied in related experiments, so even a screen pass would not establish independent OOS or funded readiness. A separate executable BID/ASK and slippage test plus a FundedNext rule-aware two-phase equity-path replay would still be mandatory.

## Required artifacts

Archive the local runner, compact JSON, final report, session-quality audit, candidate trade ledger and matched-parent ledger in this branch. Run in local Python/container only; do not create or dispatch a GitHub Actions backtest workflow.
