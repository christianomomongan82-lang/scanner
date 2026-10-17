# R287 Preregistration — Intraday Cross-Index Residual Reversion

**Candidate ID:** `R287_US_INDEX_INTRADAY_RESIDUAL_REVERSION`  
**Status:** locked before outcome calculation.  
**Date:** 2026-10-17.

## Lineage and hypothesis

This is a controlled, same-session evolution of the exploratory R265 relative-value idea, which was underpowered at the daily-pair holding horizon, not a rescue of R265's thresholds or old results. It also differs from the cash-open R276–R280 family: no opening gap, opening range or Nasdaq follower trigger is used.

When correlated US equity indices show unusually different returns over the late-morning window, the most divergent index may partially revert relative to the cross-index median by the end of the same RTH session. The matched parent takes the same event on the same instrument and timestamps but follows the residual instead of fading it. This isolates direction as the key hypothesis contrast.

## Input and session data

- Use the already cached GitHub R205 M5 BID-only data for USA500 (artifact `11709864394`), USATECH (`11710370389`), USA30 (`11710730507`) and USSC2000 (`11710111254`). Data files are under `/mnt/data/r284data`; archive SHA values are the ones previously recorded for R205/R283. Do not call external data providers.
- Convert bar-open epoch-millisecond timestamps to `America/New_York`, including DST.
- A valid session must contain exactly one valid bar for every 5-minute timestamp 09:30 through 15:55 ET (78 bars), positive consistent OHLC and no repeated-flat candidate (O=H=L=C=previous raw row close) anywhere in RTH. A fully flat placeholder-only date is not an active session. Missing bars are not fabricated.
- A date is eligible for cross-section only if at least three instruments have a quality-valid RTH session and exact signal/entry timestamps. Rank only the valid instruments for that date. Keep missing/ineligible symbols out; do not backfill or extend the time window.
- Retain the source archive/input hashes, eligible counts, skipped dates and common timestamp coverage in the report.

## Frozen signal and execution

1. For each eligible instrument-session, calculate late-morning return `r_i = close(12:55 ET) / open(10:00 ET) - 1`. The 12:55 bar is the signal candle; its close becomes known at 13:00 ET.
2. Calculate the cross-sectional median return for the same date from the three or four quality-valid instruments. Each instrument residual is `e_i = r_i - median(r)`.
3. For each instrument, fit a threshold equal to the 75th percentile of `abs(e_i)` from eligible discovery dates in 2017–2020 only. The same-day cross-sectional median is included in the residual calculation, but all fit dates are restricted to discovery.
4. On dates with at least three valid instruments, rank symbols by `abs(e_i) / Q75_i`; tie-break by symbol. Select at most one index per date: the symbol with the highest normalized absolute residual.
5. If the winning normalized residual is below 1.0, no trade. Otherwise the candidate fades the residual (short if residual positive, long if negative). The matched parent takes the exact same winning instrument and event but follows the residual direction. Both use the exact same eligible event dates.
6. Entry is the 13:05 ET bar open, i.e. T+10 from signal-bar open at 12:55 (five-minute candle confirmation + five-minute manual phone execution delay). The entry bar timestamp and intervening 13:00 timestamp must be exact. Do not use the 13:00 bar high/low to improve entry.
7. Force-flat at the 15:55 ET bar open. Do not inspect that bar's later high/low or close to determine the fill. No stop, target, scaling, overnight exposure, stacking or compounding in this initial signal screen.
8. Gross trade return is direction-signed BID price movement from 13:05 open to 15:55 open in basis points. Subtract modeled 1, 2 and 4 bp round-trip notional costs. The primary cost is 2 bp. These are stresses, not observed spreads/commissions/slippage; feeds are BID-only.

## Locked partitions and gates

- Discovery: trade entry dates in 2017–2020.
- Validation: trade entry dates in 2021.
- 2022–2025 is program-contaminated and is not a clean promotion OOS. Do not calculate its PnL unless every historical gate passes; if opened later it is exploratory only. Do not inspect 2026 outcomes for this candidate.
- At 2 bp, discovery must have at least 200 trades, PF >= 1.05, positive net bps and at least 2 of 4 annual cohorts positive.
- At 2 bp, validation must have at least 50 trades, PF >= 1.00 and positive net bps.
- Cost stress: PF >= 0.90 at 4 bp in both discovery and validation.
- Report both the candidate and matched directional parent under identical event, instrument, timestamp and cost assumptions. Direction contrast does not allow the parent to become a promotion candidate without its own separate hypothesis/gates.
- Any failed discovery or validation gate yields **GAGAL**. Do not change percentile, entry time, direction, lookback, session window, cost schedule or gates after outcomes. Do not run a funded challenge replay if the signal screen fails.

## Known limitations

The R205 inputs are BID-only and previously used. Modeled basis-point costs do not verify live CFD point values, actual spread, commissions, slippage or swap. Even a historical-screen pass would not be funded-ready without independent OOS and a separate account-equity replay using verified provider rules.

## Required archive

Store source/quality audit, fitted thresholds, runner, event/trade ledger for candidate and parent, annual/cost metrics and final binary verdict in the active research branch. Calculation must run locally in Python; no GitHub Actions backtest workflow may be created or dispatched.
