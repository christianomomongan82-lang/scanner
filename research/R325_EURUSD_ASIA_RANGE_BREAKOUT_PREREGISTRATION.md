# R325 — EURUSD Asian-range breakout continuation (preregistered)

Status: **REGISTERED BEFORE R325 OUTCOME CALCULATION**. This is a continuation hypothesis, directionally distinct from R324's fade-after-rejection rule. R324 produced a sample-gate failure and no PnL; no R324 profitability numbers exist to inform this test.

## Question
When EURUSD closes decisively outside its 00:00–05:59 UTC Asian range during the 06:00–09:54 UTC European-start window, does delayed continuation reach 1.5R before a midpoint-of-range stop, using executable BID/ASK prices?

## Locked dataset and cohorts
- Input: archived Dukascopy EURUSD M1 BID/ASK OHLC, 2016–2025. Input SHA-256 will be recorded before testing.
- Join BID and ASK on exact timestamp; reject duplicates, invalid OHLC or unmatched times. Do not forward-fill or interpolate. Audit intraday gaps.
- Warm-up/implementation audit: 2016 (not scored).
- Discovery: entry dates 2017–2020.
- Confirmation A: entry dates 2021–2023.
- Final holdout B: entry dates 2024–2025. Neither confirmation cohort may be used to select parameters.
- Require a full 360 bars from 00:00 through 05:59 UTC; otherwise skip the date.

## Frozen strategy
1. On each Monday–Friday UTC date, compute Asian range high/low from midpoint OHLC = (BID OHLC + ASK OHLC)/2 over 00:00–05:59 UTC. Range must be strictly positive.
2. Scan bars timestamped 06:00–09:54 UTC. Signal on the **first M1 close** beyond Asian high + 0.05 × range height (LONG), or beyond Asian low − 0.05 × range height (SHORT). Use the first direction only; if one bar touches both external thresholds, skip the date as ambiguous. Do not require indicator confirmation.
3. Enter at the first M1 open at or after signal-bar close + five minutes; with contiguous bars this is signal timestamp + six minutes. Entry must be no later than 10:00 UTC. Use ASK open for LONG and BID open for SHORT.
4. Cancel before entry if any M1 close in the delay returns to/through the breakout edge back inside the Asian range; also cancel if stop level is touched during the delay. Do not move the planned stop.
5. Stop is the Asian range midpoint. LONG stop trigger is BID low <= midpoint; SHORT stop trigger is ASK high >= midpoint. Reject invalid/nonpositive entry-to-stop risk (entry must be on the correct side of midpoint). Target is 1.5R from the actual entry using initial executable entry-to-stop distance.
6. Exits use executable sides. For a LONG, evaluate BID; for a SHORT, evaluate ASK. If stop and target are hit in the same M1 candle, stop wins. Stops gapped through fill at the worse bar open. Targets fill at the target price (no favorable gap improvement). Force-close at the 11:59 UTC bar close. If that close/horizon is missing, log and exclude the outcome; never impute or fill-forward.
7. Costs are the observed BID/ASK execution spread plus fixed additional round-trip friction of 0.5, 1.0, or 2.0 pips. Primary metric is +0.5 pip; +1 and +2 pips are stress tests. One trade maximum per UTC date. No overlapping positions.
8. Report net expectancy in R, profit factor, trade count, max drawdown in R, win rate, exit reason, annual cohorts, and all-week net R with zero-trade weeks included.

## Sample gate (must be checked before calculating any PnL)
- Discovery >=600 eligible trades total and >=100 in each year 2017–2020.
- Confirmation A >=400 eligible trades total and >=100 in each year 2021–2023.
- Final holdout B >=250 eligible trades total and >=100 in each year 2024–2025.
- A trade is sample-eligible only after a valid entry exists and the full exit horizon through 11:59 UTC is present. This count phase must not calculate exit outcomes, PnL, R, PF, drawdown or bootstrap.
- If any sample threshold fails, stop and report **FAIL — DATA/SAMPLE**; do not calculate profitability.

## Edge gates (evaluated only after every sample gate passes)
- At +0.5 pip extra cost: net expectancy >0 and PF >=1.05 in discovery, confirmation A, and final holdout B.
- At +2 pips extra cost: net expectancy >0 and PF >=1.00 in all three cohorts.
- Annual robustness: at least 3/4 discovery years, 2/3 confirmation-A years and both final-holdout years have positive net R at +0.5 pip.
- No single discovery year may contribute more than 60% of summed positive annual discovery net R.
- Statistical evidence: a circular 4-week block bootstrap (roughly 20 trading days), 10,000 resamples, seed 325, on weekly net R including zero-trade weeks. The lower bound of the two-sided 95% percentile interval for mean weekly net R must be above zero separately in confirmation A and final holdout B.
- Data/reproducibility gate: two independent clean processes must produce byte-identical normalized ledgers and summaries. No fill-forward, no parameter sweep, no tuning on either confirmation cohort.
- **PASS** requires every gate. Any failed sample gate is **FAIL — DATA/SAMPLE**; any failed edge/statistical gate after adequate sample is **FAIL — EDGE**; broken integrity/reproducibility is **FAIL — DATA/PROCESS**.

No claim about future profitability follows from a historical PASS; funded-trading execution, broker slippage and challenge rules require separate validation.
