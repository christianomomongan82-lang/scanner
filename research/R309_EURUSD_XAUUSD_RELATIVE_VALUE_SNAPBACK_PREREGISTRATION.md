# R309 — EURUSD/XAUUSD Relative-Value Snapback (Preregistration)

**Status:** preregistered before R309 PnL calculation  
**Mechanism family:** FX_GOLD_RELATIVE_VALUE_REVERSION  
**Parent/related evidence:** R305/R306 (same-direction USD impulse transmission; failed), R251 (GBPUSD→EURUSD lead-lag; failed), R265/R287/R288 (US-index relative-value; not direct evidence for this FX/gold pair)  
**Mutation type:** new cross-asset relative-value mechanism; it trades the relative-return residual back toward its recent center, not same-direction impulse follow-through.

## Hypothesis
A large one-hour relative move between gold and EURUSD, measured against a rolling beta estimated only from prior paired returns, temporarily overshoots their short-horizon relationship and partially mean-reverts over the next two hours. The strategy is only eligible while the trailing beta is positive and paired data are continuous.

## Frozen rules
- Instrument inputs: paired Dukascopy EURUSD M1 BID/ASK aggregated into complete UTC M5 bars, plus Dukascopy XAUUSD M5 BID/ASK; exact timestamp joins only.
- Exclusive outcome cutoff: 2026-01-01 00:00 UTC. Do not score/open any 2026 XAU row.
- Feature history: 5,760 prior contiguous paired M5 returns (approximately 20 active trading days). Rolling beta is cov(r_EURUSD, r_XAUUSD)/var(r_EURUSD), using information only through the prior bar. Residual return is r_XAUUSD - beta * r_EURUSD.
- Signal statistic: sum of the latest 12 residual M5 returns (one hour), z-scored against the trailing 5,760 prior one-hour residual sums; current observation is excluded from mean/standard-deviation estimation.
- Entry: if z >= +2.0, short the residual (short XAUUSD, long EURUSD); if z <= -2.0, long the residual (long XAUUSD, short EURUSD). Require beta > 0. No entry while a position is open.
- Latency: signal M5 bar closes at its start timestamp +5 minutes. Primary entry is the first exact paired executable M5 open at signal timestamp +10 minutes (five additional minutes for manual reaction). If that exact timestamp/path is unavailable, skip the signal; do not forward-fill.
- Exit, evaluated at M5 closes and executed at the following exact M5 open: take profit when z returns through |z| <= 0.5; stop if z reaches or exceeds 3.5 in the adverse direction; maximum hold 24 M5 bars (2 hours). If stop/target are both crossed inside a bar, use the adverse stop. No overlapping positions. If required timestamps are missing during the holding path, exclude that event from PnL and report the count.
- Execution: all four legs use actual executable quote sides: long legs enter ASK/exit BID; short legs enter BID/exit ASK. No synthetic bars. Use entry-time beta frozen for the position.
- Extra cost stress beyond observed BID/ASK: baseline +$0.30/oz round-trip XAUUSD and +1.0 pip round-trip EURUSD; also score zero-extra-cost and +$0.50/oz / +2.0 pips. Fixed delay stress enters at signal timestamp +15 minutes (10 minutes after signal close), without changing other rules.
- Risk units: one R equals the residual move from signal z=2.0 to the stop at z=3.5, i.e. 1.5 times the prior one-hour residual standard deviation; apply the same calculation symmetrically for negative signals. Report costs and results in residual R. This is an economic screening metric, not a challenge-equivalent account-dollar replay.
- Discovery: 2017–2020. Validation/diagnostic: 2021–2025. The latter is program-contaminated by prior research and is not pristine OOS. Any 2016 values are feature burn-in only.
- No parameter grid, direction flip, threshold search, or post-result tuning is permitted under R309. R309 is closed after this registered screen.

## Binary gates
1. exact BID/ASK data audit passes; timestamps paired without synthetic fill;
2. at least 300 discovery and 500 validation trades;
3. net R > 0 and PF_R >= 1.05 in both discovery and validation at baseline costs;
4. net R > 0 in both periods at the stronger +$0.50/oz / +2-pip stress;
5. at least 3/4 discovery years and 4/5 validation years are positive at baseline cost;
6. weekly block-bootstrap validation 95% CI lower bound > 0, resampling calendar weeks in circular 4-week blocks and retaining zero-trade weeks;
7. delayed-entry stress at baseline costs remains net positive in both periods;
8. no integrity or execution-path defect and complete row-level reproducibility.

**Decision rule:** any failed required gate means **GAGAL**; do not run a FundedNext challenge replay. Only a fully passing candidate can proceed to common-account funded-path simulation. No conclusion from R309 can be called a FundedNext pass.
