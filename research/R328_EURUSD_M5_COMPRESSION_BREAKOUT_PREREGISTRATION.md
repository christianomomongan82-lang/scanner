# R328 — EURUSD M5 volatility-compression breakout (preregistered)

Status: **REGISTERED BEFORE R328 OUTCOME CALCULATION**.

This tests a rolling volatility-compression -> range-breakout structure. It is not the fixed six-hour Asian-range breakout in R325: the compression zone is rolling, must fall below a historical range percentile, and is defined from the immediately preceding 12 M5 bars.

## Locked data and cohorts
- Source: Dukascopy EURUSD M1 BID/ASK OHLC archive, 2016–2025.
- Exact BID/ASK timestamp join, valid OHLC, strictly increasing timestamps required. Do not fill-forward/interpolate gaps.
- Use complete, contiguous M5 candles built from exactly five consecutive M1 bars. Midpoint M5 high/low are the extrema of per-minute midpoint highs/lows, not averages of independently occurring BID/ASK extremes.
- 2016 is implementation/warm-up only; discovery 2017–2020; confirmation A 2021–2023; holdout B 2024–2025. The holdout is strategy-specific, not globally untouched across all project experiments.

## Frozen signal
1. Candidate M5 signal bars open from 06:00 through 09:50 UTC Monday–Friday. The M5 bar and the 72 complete M5 bars preceding it must be consecutive at five-minute intervals; otherwise no setup.
2. Define the compression zone from the 12 complete midpoint M5 bars immediately preceding the signal candle: compression high = maximum midpoint high, compression low = minimum midpoint low, height = high - low. Require positive height.
3. Compute 60 historical rolling 12-bar ranges from the previous 60 eligible contiguous M5 windows, all ending before the current 12-bar compression zone. The current compression height must be <= the 25th percentile (linear quantile) of those previous 60 ranges. No current or future range may enter its threshold.
4. LONG signal if the current M5 midpoint close is >= compression high + 0.05 × compression height. SHORT if close <= compression low - 0.05 × height. First qualifying signal per UTC day is the sole attempt; if that attempt becomes invalid, do not substitute a later setup.
5. Entry is at signal-bar-open +10 minutes (five-minute delay after the M5 close), no later than 10:00 UTC. Use ASK open for LONG and BID open for SHORT.
6. LONG stop is compression low - 0.2 pip; SHORT stop is compression high + 0.2 pip. Cancel if the executable stop is touched any time from signal-bar close through the five delay bars (M1 bars with timestamps signal +5 through +9 minutes). Reject nonpositive entry-to-stop risk. Stop remains fixed.
7. Target is 1.5R from actual entry, where R is entry-to-stop distance. Evaluate LONG exits against BID and SHORT exits against ASK. If stop and target touch in the same M1 bar, stop wins. Stop gaps fill at worse bar open; target fills at target without favorable gap improvement. Force close at the 11:59 UTC bar close using the executable side.
8. Eligible sample trades need contiguous M1 coverage from entry through the 11:59 close. No imputing missing data. One trade per UTC day and no overlapping trades.
9. Add fixed round-trip friction of 0.5, 1.0, and 2.0 pips beyond use of BID/ASK. Primary result is +0.5 pip. Report expectancy R, PF, drawdown R, win rate, exit reasons, annual cohorts and zero-inclusive weekly net R.

## Frozen sample gate (before outcomes)
- Discovery: >=350 eligible trades total and >=50 in each year 2017–2020.
- Confirmation A: >=250 total and >=50 in each year 2021–2023.
- Holdout B: >=150 total and >=35 in each year 2024–2025.
- An eligible trade must have the first valid signal, valid delayed entry/stop, no stop touch during delay, and a complete contiguous exit horizon. Sample counts must not calculate exits, PnL, R, PF, drawdown or bootstrap.
- Any sample failure stops the test and yields **FAIL — DATA/SAMPLE**.

## Frozen edge gates
Only if every sample gate passes:
- At +0.5 pip: net expectancy >0 and PF >=1.05 in discovery, confirmation A and holdout B.
- At +2 pips: net expectancy >0 and PF >=1.00 in all three cohorts.
- At +0.5 pip, at least 3/4 discovery years, 2/3 confirmation years and both holdout years must have positive net R; no discovery year may contribute >60% of total positive discovery annual net R.
- Circular four-week block bootstrap on weekly net R including zero-trade weeks, 10,000 resamples, seed 328. The lower bound of the two-sided 95% percentile interval for mean weekly net R must be >0 in both confirmation A and holdout B.
- Two clean independent runs must produce byte-identical normalized ledger and summary. Reproducibility/integrity failure: **FAIL — DATA/PROCESS**. Adequate sample but any edge/robustness failure: **FAIL — EDGE**. **PASS** requires every gate.

No tuning against confirmation or holdout results. Historical PASS is not a guarantee of future profitability or funded challenge readiness.
