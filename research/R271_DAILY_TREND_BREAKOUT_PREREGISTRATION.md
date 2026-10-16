# R271 — Daily 20-session breakout continuation

Date: 2026-10-16  
Status before run: preregistered; no signal/PnL results inspected for this candidate.

## Hypothesis
Medium-horizon directional persistence after a confirmed close beyond a prior multi-session extreme may survive several-minute manual execution delay better than the previously tested intraday setups. This is a distinct daily-horizon trend-following hypothesis—not a rescue of R257, R261, R263, or R269. No parameter sweep is authorized.

## Data and provenance
- Instrument: EURUSD, Dukascopy M1 BID and ASK.
- Source artifact: GitHub raw-only artifact 11959096102 from run 38697080604; requested window 2016-01-01 through 2025-12-31 UTC.
- Archive SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- Calculations must run locally, never in GitHub Actions. Use timestamps present in both sides; no synthetic minute bars. Drop known closed-market flat Sunday placeholder rows consistently; preserve quote sides.
- Build FX sessions in America/New_York time, session day running 17:00 local to 16:59 local on the next calendar day, with DST handled by timezone conversion.
- Windows: discovery 2016–2020, validation 2021, exploratory diagnostic 2022–2025. The latter and earlier years have substantial research-selection contamination; none is treated as a clean final holdout. Input ends 2025, so no 2026+ evidence exists in this archive.

## Locked entry logic
1. For each completed FX session, calculate its BID high/low/close and true range. ATR20 is the arithmetic mean of the prior 20 completed session true ranges only; current signal session is excluded from ATR calculation.
2. Define the rolling 20-session breakout levels from the 20 sessions completed before the signal session, excluding the current session.
3. LONG signal only when the current session BID close is strictly above the prior-20-session BID high. SHORT signal only when current session BID close is strictly below the prior-20-session BID low. No additional trend, volatility, weekday, or news filter.
4. Entry at the first exact M1 quote timestamp corresponding to 17:05 America/New_York after the signal session closes at 16:59. If this quote is unavailable, skip; do not delay further. Long enters at ASK open; short enters at BID open. Reject if a position is already open at signal time or the initial stop is invalid.
5. Initial stop distance = 2.0 × prior ATR20. LONG stop = entry − distance; SHORT stop = entry + distance. Take-profit = 2.0R from entry (4 × ATR20). Only one active position; no pyramiding; ignore signals while a trade is open.
6. Monitor M1 executable exit side: long exits use BID OHLC; shorts use ASK OHLC. Stop has priority if stop and target are both touched in one minute. Stop gaps fill at the worse opening quote; target fills at the target price when touched. At a 10th subsequent valid FX session close, exit at the first available executable quote at/after the session close. No synthetic bars.
7. Primary incremental transaction-cost stress is +1.0 pip per round trip beyond observed BID/ASK; also report +0, +0.5, and +2.0 pip sensitivities. Apply incremental cost to trade PnL, not signal prices. Entry delay is built into the rule (no ideal-entry substitute in the primary result).

## Locked comparisons and metrics
- Compare long, short, and combined trade streams using net R, profit factor as a diagnostic, mean/median R, win rate, count, annual outcomes, and weekly net-R block bootstrap (4-week circular blocks; 10,000 replicates; fixed seed 2712026).
- Report signal counts and skipped signals; compare costs at 0, +0.5, +1 and +2 pips.
- For a secondary reference-only challenge path diagnostic, test 0.25%, 0.50%, 0.75%, and 1.00% fixed-fractional risk per trade on sequential trades with +8% then +5% phase targets and the historical $5,400 static-floor / 5% UTC-day-loss proxy only if the base trade stream is net positive. These rules are not an official FundedNext-equivalent engine; do not describe proxy odds as live odds.

## Binary gates
The exploratory historical screen can only be called LULUS if all hold at +1 pip: (a) discovery and 2021 validation net R are positive with at least 50 trades in each segment; (b) 2022–2025 net R is positive in at least 3 of 4 years and positive in aggregate; (c) the 2022–2025 4-week bootstrap 95% interval lower bound of mean weekly net R is above zero; (d) +2-pip incremental-cost forward net R remains positive; and (e) five-minute delay is inherent in the primary trade stream. Otherwise GAGAL; no retuning.

Even if the exploratory screen passes, this data archive does not support promotion to a funded-ready strategy because all available periods have been repeatedly inspected in the broader research program, 2022–2025 is explicitly contaminated, 2026+ is absent, and official live funded mechanics/costs remain incompletely verified. A later promotion requires a frozen, independent post-lock sample and a verified challenge engine.
