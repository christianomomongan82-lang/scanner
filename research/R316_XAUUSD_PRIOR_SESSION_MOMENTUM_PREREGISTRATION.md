# R316 — XAUUSD Prior-NY-Session Momentum Continuation — Preregistration

Registered: 2026-10-21. Status before calculation: **LOCKED / PnL not yet inspected**.

## Distinct mechanism

Test whether a strong directional move during one completed New York cash-hours session predicts continuation after the next NY morning alert. This is conditional cross-session persistence, not unconditional clock-time bias (R314), a compressed range breakout (R315), a single-bar impulse (R274), sweep/reclaim (R298), auction extension fade (R302), or spread-shock fade (R313).

## Data and timing

Use paired Dukascopy XAUUSD M5 BID/ASK from the checksum-verified archive. Strict exclusive cutoff `2026-01-01T00:00:00Z` is applied before any feature/outcome calculation. Discovery uses New York dates 2016–2020; validation diagnostic split 2021–2025 is not pristine project-wide OOS due prior exploration. Protected 2026 outcomes stay closed.

For each New York calendar date D, define the completed prior session as the exact 09:30 M5 bar open through the close of the exact 16:55 M5 bar on D−1. Session return is midpoint close of the 16:55 bar minus midpoint open of the 09:30 bar (USD/oz). Require both timestamps to exist as valid paired active source rows; do not fill missing observations. Require absolute session return to be at least the median absolute return of the latest 20 fully completed prior NY sessions, including D−1. Direction is the sign of D−1 session return. Signal alert is at 09:30 New York time, when all prior-session data is already known; wait five minutes for manual execution and enter at the exact active 09:35 M5 open.

## Execution

- Only the first eligible signal/trade per New York date; one open position at a time.
- Initial stop distance is the median BID true range of the 24 prior eligible active M5 rows strictly before 09:30; no signal-day future bars are used to calculate the distance. Skip if unavailable or zero.
- Long entry at ASK open, long exit on BID; short entry at BID open, short exit on ASK. Stop = 1.00 × initial distance, target = 1.50 × initial distance.
- If stop and target are touched in the same bar, stop wins. If price gaps beyond stop, fill at the worse executable opening quote; never improve a target beyond its limit.
- Maximum hold: 120 minutes from entry. If the executable M5 timestamp sequence breaks before the trade exits, flatten at the last observed executable close and mark `data_gap_time`; do not fill/synthesize bars.
- Additional round-trip cost above observed BID/ASK: $0.00, $0.10, $0.30/oz (primary), $0.50/oz. `R = (direction × (exit executable − entry executable) − added cost) / initial stop distance`.

## Output and hard gates

Save every date's eligibility/skip reason, prior-session return/threshold, trade quote-side prices, stops/targets, exit timestamps/reasons, all four cost streams, year/period summaries, a zero-inclusive weekly series, source manifest/checksums and 10,000-replicate circular four-calendar-week bootstrap (seed 316) for validation net R at +$0.30/oz.

The candidate is a necessary screen-pass only if **all** hold:
1. At least 300 trades in discovery and in validation (frequency floor for a practical funded attempt).
2. Net R positive in both periods at +$0.30/oz.
3. Validation PF_R >=1.05 at +$0.30/oz.
4. At least 3 of 5 validation calendar years positive.
5. Validation weekly bootstrap lower 95% CI for mean net R >0.
6. At +$0.50/oz, validation net R remains positive and PF_R >=0.90.

If discovery has fewer than 300 trades or non-positive net R at +$0.30/oz, stop at discovery with **GAGAL** and do not calculate candidate-specific validation PnL. Any failed validation gate = **GAGAL**; no inverse-direction or parameter rescue after results. A historical pass triggers execution-readiness validation, not live trading/funded-pass claims; account contract size, fee/swap, spread/slippage, server reset timezone/DST remain separate gates.
