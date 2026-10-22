# R327 — EURUSD overnight directional stretch fade (preregistered)

Status: **REGISTERED BEFORE R327 OUTCOME CALCULATION**.

This is a pre-London contrarian session-overextension hypothesis. It is distinct from R324 sweep/re-entry, R325 Asia-range breakout, R326 single-candle M5 continuation, R322 scheduled-news continuation, and R323 cross-sectional currency strength. No parameter variants or sweeps are permitted.

## Data and fixed cohorts
- Source: Dukascopy EURUSD M1 BID/ASK OHLC archive, 2016–2025.
- Exact timestamp joins required. No fill-forward or interpolation. Document duplicates, invalid OHLC and timestamp gaps.
- Warm-up and implementation audit: 2016, not scored.
- Discovery: 2017–2020.
- Confirmation A: 2021–2023.
- Diagnostic/holdout B: 2024–2025 for this registered hypothesis. Note that these calendar years have appeared in prior unrelated strategy experiments, so this is strategy-specific holdout evidence, not a global untouched portfolio holdout.

## Frozen session signal
1. Evaluate Tuesday through Friday UTC only. For current date D, define the overnight session as 18:00 UTC on D-1 through 05:59 UTC on D, inclusive (720 one-minute bars). It must contain exactly 720 consecutive, valid bars. Otherwise mark the session incomplete and skip it. This date restriction avoids any weekend bars.
2. Calculate the overnight signed midpoint move in pips as midpoint close of the 05:59 bar minus midpoint open of the prior-day 18:00 bar, where midpoint price is the average of BID and ASK prices.
3. Construct the threshold from the median absolute signed moves of the previous 20 valid complete overnight sessions, excluding the current session. Require all 20 prior values and a strictly positive median. Signal only when the absolute current move is greater than or equal to 1.0 times that median. Positive overnight move means SHORT (fade); negative means LONG (fade). No second attempt that date.
4. The signal is known at 06:00 UTC. Entry is the first M1 open at 06:05 UTC (five-minute manual delay). Use ASK open for LONG, BID open for SHORT. Require all delay bars 06:00–06:04 to exist consecutively.
5. For LONG, initial stop is minimum BID low across the 720-bar overnight session minus 0.2 pip. For SHORT, initial stop is maximum ASK high across that session plus 0.2 pip. If this stop is touched at any time in 06:00–06:04, cancel the setup. Reject nonpositive entry-to-stop risk; do not move the stop.
6. Target is fixed at 1.5R from actual entry, where 1R is actual entry-to-stop distance in executable price units. Evaluate LONG exits against BID and SHORT exits against ASK. When stop and target are both touched in one M1 bar, stop wins. A stop gapped through fills at the worse open; target fills at target price without favorable gap improvement. If neither level hits, force-close at 11:59 UTC bar close using the executable side.
7. A valid sample trade must have a contiguous M1 horizon from entry at 06:05 through the 11:59 close. No imputed bars. One trade maximum per eligible UTC date, no overlapping positions.
8. Apply additional fixed round-trip friction of 0.5, 1.0 and 2.0 pips beyond BID/ASK execution. Primary case is +0.5 pip. Report expectancy in R, PF, trade count, max drawdown R, win rate, exit reasons, annual cohorts and weekly net R including zero-trade weeks.

## Frozen sample gate — checked before outcome calculation
- Discovery: at least 500 eligible trades total and at least 75 per year in each of 2017–2020.
- Confirmation A: at least 300 total and at least 75 per year in each of 2021–2023.
- Holdout B: at least 200 total and at least 50 per year in each of 2024–2025.
- A candidate counts only with complete overnight session, a valid signal and entry/stop, no stop touch during the delay, and full contiguous entry-to-force-close coverage. Sample counting must not inspect outcome-bar highs/lows to determine target/stop outcomes and must not compute PnL/R/PF/drawdown/bootstrap.
- If any threshold fails, stop before outcome calculation and report **FAIL — DATA/SAMPLE**.

## Frozen edge and robustness gates
Only after all sample gates pass:
- With +0.5 pip extra friction, net expectancy must be >0 and PF >=1.05 in discovery, confirmation A and holdout B.
- With +2 pips extra friction, net expectancy must be >0 and PF >=1.00 in all three cohorts.
- At +0.5 pip, at least 3/4 discovery years, 2/3 confirmation years and both holdout years must have positive net R. No discovery year may supply more than 60% of summed positive discovery annual net R.
- Circular four-week block bootstrap of weekly net R including zero-trade weeks, 10,000 resamples, seed 327. The lower end of each two-sided 95% percentile interval for mean weekly net R must be >0 separately in confirmation A and holdout B.
- Two independent clean runs must return byte-identical normalized trade ledger and summary. Data integrity or reproducibility failure is **FAIL — DATA/PROCESS**. Adequate sample but any edge/robustness failure is **FAIL — EDGE**. **PASS** requires every frozen gate.

No result from this registered test may be used to tune its own parameters. Historical success does not establish future profitability or funded-challenge readiness.
