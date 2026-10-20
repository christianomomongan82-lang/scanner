# R310 — Entry-to-Exit EURUSD/XAUUSD Residual Snapback

**Status:** preregistered before R310 trade PnL  
**Family:** FX_GOLD_RELATIVE_VALUE_REVERSION  
**Parent:** R309 (GAGAL; 3,576 discovery and 3,665 diagnostic validation trades at baseline costs, both strongly negative under the registered trailing-z exit)  
**Mutation:** structural exit correction only. R309's signal feature and direction are retained unchanged; exits now measure actual post-entry pair price change rather than waiting for a rolling one-hour return z-score to fall back inside a band.

## R309 diagnosis motivating this child
A trailing one-hour residual-return z-score can move back toward zero because the original shock rolls out of the one-hour calculation window, even if the pair position has not earned a favorable post-entry return. R310 therefore defines profit/loss barriers on the post-entry residual price change with a beta frozen at the signal. R309 remains closed; its parameters are not tuned or re-opened.

## Frozen rules
- Inputs, paired timestamp join, data filter, rolling beta, 12-bar one-hour residual feature, trailing 5,760-row z-score history (minimum 4,608 valid observations), beta-positive eligibility, cutoff, entry delay, and signal thresholds are exactly as in R309.
- Signal: z >= +2.0 -> short residual (short gold, long EURUSD); z <= -2.0 -> long residual (long gold, short EURUSD).
- Primary entry: exact paired executable M5 open at signal timestamp +10 minutes (signal bar closes +5 minutes, then 5-minute manual reaction). T+15-minute entry is the fixed delay stress.
- Entry-time beta and the prior one-hour residual standard deviation are frozen for the trade.
- Exit state is the actual pair's cumulative log-price move since entry, calculated at M5 closes as side * [log(XAU mid close / XAU mid open at entry) - beta_entry * log(EURUSD mid close / EURUSD mid open at entry)].
- Take profit when this post-entry residual move reaches +1.5 * the signal-time one-hour residual standard deviation; stop when it reaches -1.5 * that standard deviation. This is a fixed +1R/-1R barrier, evaluated on M5 closes and executed at the next exact paired M5 open. Otherwise exit at the next open after 24 M5 bars (two hours). No overlapping positions. Require exact contiguous paired timestamps throughout the declared maximum holding path; missing paths are excluded and counted, never synthesized.
- Execution uses executable sides for each leg: long legs enter ASK and exit BID; short legs enter BID and exit ASK. Positions: residual-long = long gold + short EURUSD; residual-short = short gold + long EURUSD. All PnL uses the signal-time beta.
- Costs beyond observed BID/ASK: baseline +$0.30/oz XAUUSD and +1.0 pip EURUSD round trip; stress +$0.50/oz and +2.0 pips; zero-extra-cost diagnostic also recorded. Fixed delay stress is +15 minutes from the signal bar timestamp.
- Risk unit is 1R = 1.5 * signal-time one-hour residual SD. Results are residual-R economic screening, not account-dollar funded challenge replay.
- Discovery 2017–2020; contaminated validation/diagnostic 2021–2025. 2016 is feature burn-in only; no 2026 outcomes are scored.

## Binary gates
1. source/filter/timestamp integrity passes, no synthetic bars;
2. at least 300 discovery and 500 validation trades;
3. baseline-cost net R > 0 and PF_R >= 1.05 in both discovery and validation;
4. net R remains positive in both periods under +$0.50/oz and +2-pip stress;
5. at least 3/4 discovery years and 4/5 validation years positive at baseline costs;
6. validation weekly circular four-week block-bootstrap 95% CI lower bound > 0, including zero-trade weeks;
7. T+15 delayed-entry stress stays net positive in both periods;
8. executable-side path integrity and row-level result archive recorded.

Any failed gate means **GAGAL** and closes R310. No threshold/holding-period sweep or direction flip is permitted. Only a full pass may proceed to a separately validated, floating-equity-aware two-phase funded challenge simulation.
