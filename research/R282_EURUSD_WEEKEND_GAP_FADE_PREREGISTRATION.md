# R282 — EURUSD weekend-reopening gap fade
**Status before calculation: PRE-REGISTERED; strategy outcomes not calculated.**

## Hypothesis
After the FX market reopens following the weekend, some gaps away from the prior Friday close may partially revert. The mechanism tested is the weekly reopening gap itself, not intraday candle impulse, ordinary high/low sweeps, H1 compression, or cash-open breakout. This is a standalone candidate; no failed strategy block is combined with it.

## Data and provenance
- Input: Dukascopy EURUSD M1 BID/ASK archive collected through dukascopy-node, GitHub data-only artifact 11959096102.
- Archive SHA-256 must equal `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- Requested source window: 2016-01-01 inclusive to 2026-01-01 exclusive. All signal and outcome calculations are restricted to 2017-01-01 through 2025-12-31. No 2026 data are used.
- Apply the same paired synthetic-flat candidate filter used in R275/R281: both BID and ASK candles are flat, each open equals its own previous close, and timestamps are exactly one minute apart. This source was collected with `-fl`; the filter remains heuristic and cannot prove that all synthetic observations were removed. Preserve gaps; do not fill missing minutes.
- Require unique paired timestamps, valid OHLC and nonnegative opening spreads.

## Locked event definition
1. A weekly-reopening event is the first paired M1 timestamp (t) after a gap of at least 36 hours whose prior observed timestamp falls on Friday UTC and whose current timestamp falls on Sunday or Monday UTC. There is at most one event per weekend. Do not infer events from ordinary short intraday data gaps.
2. The opening gap in pips is current M1 mid-open ((BID_{open}+ASK_{open})/2) minus the previous observed Friday M1 mid-close ((BID_{close}+ASK_{close})/2). Positive gap means fade short; negative gap means fade long. Zero gap is ignored. No minimum gap-size threshold is added; economic viability is judged after observed spread and cost stress.
3. Entry delay is exactly 10 minutes after the first reopening M1 timestamp. Entry is allowed only if every M1 timestamp from (t) through (t+10) minutes is present sequentially and (t+10m) exists exactly.
4. Use executable sides: short enters BID open and exits on ASK; long enters ASK open and exits on BID. Short target is the previous Friday ASK close; long target is previous Friday BID close. Skip the event if the relevant target is no longer profitable at the delayed entry (gap has already filled or reversed).
5. Stop is fixed from the opening 10-minute range: for a short, maximum ASK high during minutes (t) through (t+9m), plus 0.5 times the absolute opening gap; for a long, minimum BID low during those minutes, minus 0.5 times the absolute opening gap. Do not change the 0.5 multiplier.
6. Monitor stops/targets using executable BID/ASK OHLC. Process opening gaps first with fill at the executable open. If both stop and target are touched in the same M1 bar, assume stop first. No trailing stop, partial exit, or second entry.
7. Timeout: 48 calendar hours after entry; exit at the first observed paired M1 open at or after that timestamp. If the archive ends before that point and neither barrier hit, mark the trade censored and exclude it from closed-trade metrics. One open position maximum; skip overlapping events.
8. Subtract additional costs of 0.5, 1.0, and 2.0 pips per completed round trip on top of actual BID/ASK execution. A zero-extra-cost view may be reported for diagnosis but is not a promotion gate.

## Locked periods
- Discovery: entries and exits within 2017-01-01 through 2020-12-31.
- Validation: entries and exits within 2021-01-01 through 2021-12-31.
- Exploratory forward screen: entries and exits within 2022-01-01 through 2025-12-31. This period is contaminated by prior research and is not clean program-level OOS.
- Trades crossing a reporting-period boundary are excluded from that period.

## Gates
Do not change any rule after seeing outcomes.
1. Discovery must have at least 100 closed trades and PF >= 1.00 at +1 pip extra cost.
2. Validation must have at least 30 closed trades, PF >= 1.10 at +1 pip and positive net pips; PF >= 1.00 at +2 pips.
3. Only if all discovery/validation gates pass, calculate 2022-2025 exploratory metrics. Forward screen requires at least 100 closed trades; PF >= 1.10 at +1 pip; PF >= 1.05 at +2 pips; every year with at least 10 trades must have PF >= 1.00 at +1 pip; and a 4-week circular bootstrap (10,000 replicates, seed 2822026) of weekly net pips at +1 pip must have a 95% CI lower bound above zero.
4. Any failed gate is a binary **GAGAL**. A screen pass is not funded-ready. A separate rule-aware challenge-equity-path replay and verified FundedNext costs, swaps, contract multipliers, and Quick Strike requirements are required before promotion.

## Required artifacts
Commit runner source, data audit, locked metrics JSON, grid/period summary, trade ledger and verdict to the active research branch. Do not create or dispatch a GitHub Actions backtest workflow. Do not use results from 2022-2025 to rescue a failed candidate.
