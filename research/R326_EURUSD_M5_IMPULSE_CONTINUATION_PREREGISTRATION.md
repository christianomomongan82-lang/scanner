# R326 — EURUSD M5 raw-price impulse continuation (preregistered)

Status: **REGISTERED BEFORE R326 OUTCOME CALCULATION**. This is a different mechanism from the prior Asia-range sweep/rejection, Asian-range breakout, news impulse and cross-sectional currency strength tests: continuation after a high-body M5 candle that closes near its directional extreme. No standard indicator is used.

## Hypothesis and data
- Source: raw Dukascopy EURUSD M1 BID/ASK OHLC, 2016–2025; construct M5 bars in UTC.
- Exact BID/ASK M1 timestamp join is mandatory. No fill-forward or interpolation.
- Discovery entries: 2017–2020.
- Confirmation A: 2021–2023.
- Final holdout B: 2024–2025.
- 2016 is implementation/warm-up only. No cohort may be reused to tune R326 parameters.

## Locked signal
1. Create M5 candles from exactly five consecutive M1 bars at timestamps minute 00–04, 05–09, etc. Aggregate BID and ASK separately: first open, maximum high, minimum low, last close. Exclude any incomplete M5 candle.
2. Midpoint OHLC = (BID OHLC + ASK OHLC)/2. For each M5 candidate candle, compare its absolute body `abs(close-open)` with the median absolute body of the previous 20 complete M5 candles. Require body >= 1.5 × that median. Require median > 0 and a nonzero candle range.
3. The candle must close in its directional outer quintile: bullish close location (close-low)/(high-low) >= 0.80, or bearish <= 0.20. Direction is long for bullish, short for bearish. The first qualifying candle per Monday–Friday UTC date with bar-open time 06:00–09:50 UTC is the sole attempt. A later qualifying candle is not substituted if the first attempt is invalid.
4. Signal candle close occurs five minutes after its bar-open timestamp. Entry is the M1 open at signal-bar-open + 10 minutes (five-minute delay after close). Entry must be available and no later than 10:00 UTC. Long enters at ASK open; short enters at BID open.
5. Stop for a long is the signal M5 candle's minimum BID low minus 0.2 pip; stop for a short is its maximum ASK high plus 0.2 pip. Cancel if that executable stop is touched any time between signal close and entry open. Also reject nonpositive/invalid entry-to-stop risk. Stop is fixed at signal close; do not update it.
6. Target is 1.5R from actual entry, where R is initial executable entry-to-stop distance. Evaluate exits using BID for longs and ASK for shorts. If stop and target are both touched in one minute, stop wins; gap-through stop fills at the worse open; target fills at target, without favorable gap improvement. Force close at the 11:59 UTC M1 close. The full minute-by-minute outcome horizon must be available and contiguous; otherwise exclude and log it.
7. One attempt per UTC date, no overlapping positions. Add extra round-trip friction of 0.5, 1.0 and 2.0 pips beyond BID/ASK execution. Primary metric is +0.5 pip. Report net expectancy R, PF, drawdown R, win rate, annual cohorts and weekly net R including zero-trade weeks.

## Sample gate — check before any outcome/PnL calculation
- Discovery: >=600 eligible closed-trade candidates in total and >=100 in each year 2017–2020.
- Confirmation A: >=400 total and >=100 in each year 2021–2023.
- Final holdout B: >=250 total and >=100 in each year 2024–2025.
- Sample-eligible means the first qualifying setup has a valid entry/stop after the delay and complete contiguous M1 coverage through the 11:59 exit horizon. Counting eligible setups must not inspect exit-price highs/lows, decide stop/target outcomes, or calculate PnL, R, PF or drawdown.
- If any threshold fails, stop and report **FAIL — DATA/SAMPLE** without calculating profitability.

## Frozen edge gates
Only after every sample threshold passes:
- At +0.5 pip: net expectancy >0 and PF >=1.05 in discovery, confirmation A, and holdout B.
- At +2 pips: net expectancy >0 and PF >=1.00 in all three cohorts.
- Positive net R at +0.5 pip in at least 3/4 discovery years, 2/3 confirmation-A years, and both holdout years.
- No discovery year may contribute more than 60% of summed positive annual discovery net R.
- Circular four-week block bootstrap, 10,000 resamples, seed 326, on each confirmation cohort's weekly net R including zero-trade weeks. Two-sided 95% percentile lower bounds for mean weekly net R must be >0 separately for confirmation A and holdout B.
- Data integrity and reproducibility require two independent clean runs with byte-identical normalized trade ledger and summary. No tuning, parameter grid, or use of confirmation outcomes for parameter selection.

**PASS** requires every gate. Sample failures are **FAIL — DATA/SAMPLE**; outcome/statistical failures after adequate sample are **FAIL — EDGE**; integrity or reproducibility failures are **FAIL — DATA/PROCESS**. A historical pass is not a guarantee of live/funded performance.
