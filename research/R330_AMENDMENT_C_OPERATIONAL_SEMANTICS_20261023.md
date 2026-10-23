# R330 Amendment C — operational semantics frozen before outcomes

**Date:** 2026-10-23 UTC. Committed before R330 PnL.
**Purpose:** remove ambiguous implementation choices from the existing fixed R330 signal. No signal threshold, universe, target, or ranking rule is changed.

## Time labelling and weekly snapshots

- For US stocks, convert each returned bar timestamp to its America/New_York calendar date. For crypto, use its UTC calendar date. Keep original timestamps unchanged in the source ledger.
- A signal snapshot is labelled Friday, using the most recent complete available bar whose date label is on or before that Friday. Do not use any future bar. A stock-market holiday may therefore use the previous active daily close; do not fabricate a missing bar.
- Rebalance once each Friday snapshot. Use the latest close at that snapshot for the signal.
- The forward exit close is the latest observed bar whose asset-local date label lies in the inclusive interval [signal date + 6 calendar days, signal date + 7 calendar days]. If no close exists in that interval for an instrument with nonzero target weight, fail the data gate instead of filling or substituting a bar.

## Partition boundaries and no leakage across split

- Discovery signal snapshots are eligible only when the signal date is on/after 2024-10-23 and the selected forward-exit label is on/before 2025-10-22.
- Confirmation signal snapshots are eligible only when the signal date is on/after 2025-10-23 and the selected forward-exit label is on/before 2026-10-22.
- Consequently, the last weekly snapshot whose complete forward window sits inside discovery is 2025-10-10; the next scored confirmation snapshot begins 2025-10-24. The one-week boundary embargo prevents a forward-return window from crossing partitions.
- Treat the two partitions as independent tests: reset the prior target weights to zero at the start of each partition and charge entry turnover there. Lookback prices from before a partition may be used to compute causal features, but no discovery PnL or weights carry into confirmation.

## Portfolio-return and cost arithmetic

- Compute 20-observation momentum from the current signal close divided by the close 20 observed bars earlier, minus one. Compute 20 close-to-close returns from adjacent observed rows only; never forward-fill missing rows. Use population standard deviation of those returns times sqrt(20) for the volatility scale.
- The score is momentum divided by that volatility scale; long if score >= +1.0, short if score <= -1.0, otherwise flat. Weight active positions in proportion to inverse daily-return standard deviation; normalize sum of absolute target weights to one (100% gross notional exposure).
- Each weekly gross portfolio return is the sum of target weight times each instrument's forward close-to-close return. This is an additive one-period return on notional, not a leverage or margin simulation.
- Turnover is the sum over instruments of absolute target-weight changes from the previous weekly target. At the start of each partition, previous weights are zero. Charge commissions and spread/slippage proxies on this turnover, applying the relevant per-side rate to the notional traded.
- Commission per side: stocks 0.004% (=0.00004 of notional); crypto 0.04% (=0.0004). Additional per-side spread/slippage proxies: stocks 0 / 5 / 10 bp and crypto 0 / 15 / 30 bp for floor / primary / stress. These are assumptions, not confirmed FundedNext spreads.
- Primary net weekly return = gross return − commission cost − primary extra-cost proxy. Stress net = gross return − commission cost − stress extra-cost proxy. Apply all costs once per unit of traded notional as defined by turnover.

## Summary statistics and bootstrap

- Compound each partition's weekly net returns as equity[t] = equity[t−1] × (1 + net return[t]); report cumulative return and peak-to-trough maximum drawdown on that equity path.
- Profit factor is sum of positive weekly net returns divided by the absolute sum of negative weekly net returns; report null if there are no negative weeks. Weekly win rate counts net return > 0. Annualized weekly Sharpe is sqrt(52) × mean weekly return / population standard deviation of weekly returns, descriptive only.
- Bootstrap the mean primary-proxy weekly net return by a circular moving-block bootstrap: 10,000 resamples, each of the same length as the partition; block length four weeks; concatenate consecutive circular blocks and truncate to the original length. RNG is xorshift32 seeded with integer 33020261023 coerced to unsigned 32-bit. Report the 2.5th and 97.5th percentiles using sorted empirical order statistics.
- Preserve every eligible snapshot including weeks with zero portfolio exposure. Do not select parameters from the output or revise these mechanics after looking at PnL.

## Verdict clarification

PASS — SCREEN ONLY requires both discovery and confirmation primary net cumulative returns > 0; confirmation's block-bootstrap lower 95% bound for mean primary weekly net return > 0; and confirmation stress net cumulative return > 0. It remains only a screen. Otherwise apply the previously registered economic or data/process verdict as appropriate.

Daily OHLC underlying-market data still cannot validate precise broker quotes, five-minute execution delay, or symbol-specific financing/swap. No candidate can be promoted without a separate exact-feed preflight and chronological two-phase challenge replay.