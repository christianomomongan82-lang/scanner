# R324 — EURUSD Asia-range sweep rejection (preregistered)

Status: **REGISTERED BEFORE OUTCOME CALCULATION**. This test is a new mechanism: intraday stop-run/sweep and close-back-inside rejection of the Asian range. It is not the R321 EURUSD cross-pair relation screen, R322 news impulse, R323 cross-sectional strength, or R206 US-index opening-range breakout.

## Question
After price sweeps one edge of the 00:00–05:59 UTC EURUSD range and closes back inside it during 06:00–09:54 UTC, is fading the sweep profitable with executable BID/ASK prices when entry is delayed five minutes?

## Locked data and splits
- Source: archived Dukascopy EURUSD M1 BID and ASK OHLC, 2016–2025.
- Require exact BID/ASK timestamp joins. No forward fill/interpolation. Record duplicates, invalid OHLC, timestamp gaps, and missing session minutes before computing outcomes.
- Setup discovery: entry dates 2017–2020.
- Confirmation: entry dates 2021–2023.
- Diagnostic only, not used for passing: entry dates 2024–2025.
- 2016 is excluded as a warm-up/implementation audit year.

## Frozen signal and execution
1. Trade Monday–Friday UTC dates only. Require all 360 M1 bars from 00:00 through 05:59 UTC. Otherwise skip the date.
2. Build the Asian range using midpoint OHLC = (BID OHLC + ASK OHLC)/2: high of all Asian bars and low of all Asian bars. Range must be positive.
3. From 06:00 to 09:54 UTC, find the first sweep episode. The first side touched outside its edge starts that episode. Track that side's extreme until an M1 bar closes back inside the relevant range edge. If both edges are breached before a clean rejection, mark the date ambiguous and skip it.
4. The rejection is eligible only if the tracked extreme overshoots the relevant Asian range edge by at least 0.10 × Asian-range height. A high-edge sweep closing back below the range high is a SHORT; a low-edge sweep closing back above the range low is a LONG. If the first episode re-enters without meeting the threshold, skip that date (no second attempt).
5. Signal candle timestamp is its bar-open time. Entry is at the first M1 open at or after signal-bar close + five minutes; in regular contiguous data this is the bar with timestamp signal_time + 6 minutes. Entry must be no later than 10:00 UTC. If the intended stop is breached during the delay, invalidate the setup. One attempt per UTC date.
6. Use executable sides: LONG enters at ASK open and exits against BID; SHORT enters at BID open and exits against ASK. Stop for LONG is signal episode's minimum BID low minus 0.2 pip; stop for SHORT is its maximum ASK high plus 0.2 pip. The fixed stop is known at the signal close and is not moved during the delay. Reject nonpositive/invalid entry-to-stop risk.
7. Target is 1.5R from actual entry price, where 1R is initial entry-to-stop distance in executable price units. For LONG, stop trigger is BID low <= stop and target trigger is BID high >= target. For SHORT, stop trigger is ASK high >= stop and target trigger is ASK low <= target. If stop and target appear in the same M1 bar, stop wins. Stop gaps fill at the worse bar open; targets fill at target price, without favorable gap improvement.
8. Force-close any open trade at 11:59 UTC bar close using executable side. If the necessary bars do not exist, log and exclude the trade outcome without imputing prices; also separately report such exclusions. Never use bars after the close.
9. Measure PnL with extra fixed round-trip friction of 0.5, 1.0 and 2.0 pips in addition to use of executable BID/ASK. Primary metric is at +0.5 pip; +1 and +2 are stress cases. Use 1 pip = 0.0001. Compute net expectancy in R, profit factor, trade count, drawdown in R, year cohorts, and weekly net R including zero-trade weeks.

## Frozen pass/fail gates
A trading-edge PASS requires every gate below; otherwise the outcome is FAIL with the earliest failure class clearly identified.
- DATA gate: exact timestamp pairing, no duplicate timestamps, valid OHLC, documented gaps and no fill-forward; two independent runs of the same locked code produce byte-identical normalized trade ledger and summary.
- SAMPLE gate: at least 400 closed trades in discovery (2017–2020) and at least 250 in confirmation (2021–2023), at least 50 closed trades per discovery year, and at least 50 per confirmation year.
- Primary +0.5-pip cost: net expectancy > 0 and PF >= 1.05 in both discovery and confirmation.
- +2-pip cost stress: net expectancy > 0 and PF >= 1.00 in both discovery and confirmation.
- Year robustness: at least 3/4 discovery years and 2/3 confirmation years have positive net R at +0.5 pip; no single discovery year contributes more than 60% of total positive discovery net R.
- Statistical confirmation: 20-trading-day block bootstrap, 10,000 resamples with fixed seed 324, on confirmation weekly net R including zero weeks; lower bound of the two-sided 95% percentile interval for mean weekly net R must be > 0.
- Report 2024–2025 as diagnostic only. It cannot repair a failed confirmation.
- No parameter variants, stop/target sweeps, time-window search or threshold optimization are allowed in this preregistered test. Any future variant must be a new registration and a new untouched confirmation period.

## Interpretation
If SAMPLE fails, stop before computing profitability and label **FAIL — DATA/SAMPLE**. If DATA fails, label **FAIL — DATA/PROCESS**. If sample/data gates pass but any edge/statistical gate fails, label **FAIL — EDGE**. Only all gates passing merits **PASS**; this is historical research, not proof of future profitability.
