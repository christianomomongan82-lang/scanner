# R284 Preregistration — US Index Late-Morning Impulse Continuation

**Status: locked before calculating strategy outcomes.** Candidate ID: `R284_LATE_MORNING_CROSS_SECTIONAL_CONTINUATION`. Date: 2026-10-17.

## Parent evidence and intended mutation

- Research parents/context: R276–R280 US cash-open breakout/breadth family and R283 cash-open gap fade. None is promoted. R283 was negative before costs; its post-mortem does **not** justify simply reversing its gap-fade direction.
- Inherited blocks are only implementation controls: retain bar timestamps and gaps, conservative executable-delay assumptions, stop-first intrabar ambiguity, and a single-position cap to avoid pretending four highly correlated US indexes are four independent funded opportunities.
- New signal block: continuation of a directional move measured strictly from 10:00 to 12:00 ET, then traded from 12:05 to 15:55 ET. This avoids the cash-open gap and opening-range events tested in R276–R283.
- Child mutation: take the day's strongest normalized late-morning impulse only when it is above its per-index discovery-period 75th percentile. Matched parent has the same selected instrument and execution but no magnitude gate. This is a controlled filter ablation, not a parameter grid.

## Hypothesis

A sufficiently large directional return from 10:00 to 12:00 ET reflects information diffusion or a trend-day state that persists through the afternoon. A cross-sectional selector takes at most one position per New York session, selecting the available index with the greatest `abs(10:00 open to 11:55 close return) / index-specific Q75`. The child trades only if this score is at least 1.0 and follows the sign of the late-morning return. The matched parent takes the same highest-scoring index every eligible day, regardless of score.

This is an unconfirmed hypothesis, not an assumed edge.

## Input and eligibility

- Inputs: cached GitHub Actions artifacts from R205: `USA500` artifact 11709864394, `USATECH` 11710370389, `USA30` 11710730507, `USSC2000` 11710111254. M5 BID-only OHLC snapshots. No BID/ASK pair is available in these snapshots.
- Source ZIP SHA-256 values, extracted CSV hashes, row counts, timestamp coverage and session coverage must be recorded in the report/JSON.
- Convert UTC epoch-millisecond bar-open timestamps to `America/New_York`, including DST.
- Reject duplicate timestamps and invalid OHLC. A `flat candidate` is a row with O=H=L=C that repeats the prior row's close; it is treated as a synthetic-flat possibility, not proven to be synthetic. Reject the instrument-session if such a row occurs in the 10:00–15:55 ET test window.
- An instrument-session is eligible only when every 5-minute bar-open timestamp from 10:00 through 15:55 ET exists exactly once (72 bars) and OHLC values are valid. Do not synthesize missing bars. Require at least three eligible index sessions on a date before the cross-sectional ranking is formed. USA Small Cap data starts later than the other three indexes; it joins only when genuinely available.
- Strategy outcome calculations are staged: first calculate 2017–2020 discovery and 2021 validation only. Do not calculate any 2022–2026 PnL unless the preregistered historical gates pass. The 2022–2025 period is already contaminated by other project rounds and is exploratory only; index 2026 is not a promotion-grade holdout.

## Locked signal and execution

1. For each eligible instrument-session, signal return is `close[11:55 ET] / open[10:00 ET] - 1`; the signal candle closes at 12:00 ET. Signal direction is the sign of this return.
2. For each instrument, estimate Q75 of the absolute signal return using eligible sessions in 2017–2020 only. No threshold is fit on 2021 or later.
3. On a date with at least three eligible instruments, rank available instruments by `abs(signal_return) / that_instrument_Q75`; tie-break by instrument symbol. Parent always selects the highest score. Child selects that same instrument only when its score is >= 1.0. One trade maximum across the whole index universe per date.
4. Entry is the 12:05 ET bar open, exactly T+10 minutes from the signal candle's 11:55 open: T+5 candle close plus the fixed 5-minute manual phone delay. Require exact 12:00 and 12:05 bars. No trade may use any high/low from the intervening 12:00 bar to improve the entry.
5. Stop distance is the high-low range across the 24 bars opening 10:00–11:55 ET. Long stop/target are entry minus 1.0 range and entry plus 1.5 ranges; short levels are mirrored. If range is nonpositive, skip.
6. Monitor M5 bars beginning with 12:05 through the 15:50 bar. If an opening quote gaps through a stop, fill at that adverse open; a target gap fills at the target (no price improvement). If stop and target are both touched inside one bar, stop first. At the 15:55 ET bar open, force-flat at its open and do not inspect that bar's high/low.
7. Use direction-signed BID-price movement with a modeled round-trip notional cost of 1, 2 and 4 bp. The primary screen uses 2 bp. These are cost stresses, **not** observed spreads, commissions or verified FundedNext charges. BID-only data prevents a true executable BID/ASK replay.
8. The stop-distance-based R denominator is fixed from the entry-time setup range. R is a diagnostic, not a funded-account replay. Do not claim portfolio target-completion or funded readiness from the signal screen alone.

## Locked gates

Primary cost: 2 bp round trip.

- Discovery 2017–2020: at least 200 child trades, PF >= 1.05, positive total net R, and at least 2 of 4 annual cohorts positive.
- Validation 2021: at least 50 child trades, PF >= 1.00 and positive total net R.
- Cost stress: at 4 bp, PF must be >= 0.90 in both discovery and validation.
- If any discovery/validation gate fails, stop. Do not inspect 2022–2026 trade outcomes and do not tune the threshold, time window, stop, target, cost or selection rule.
- If all historical gates pass, 2022–2025 may be scored as an **exploratory** diagnostic only: at least 100 trades, PF >=1.05 at 2 bp, at least 3/4 annual cohorts positive, and a positive lower 95% CI from a 4-week circular block bootstrap of weekly net R. Even if it passes, no promotion is permitted without genuinely independent OOS evidence, verified execution costs and a rule-aware equity-path two-phase funded-challenge simulation.

## Required output

Store the runner, hashes/provenance, source-quality report, threshold values, parent and child results, annual breakdown, cost stresses, trade ledger (where calculation occurs), bootstrap settings when eligible, failure category and binary verdict in GitHub. No GitHub Actions backtest workflow may be created or dispatched.