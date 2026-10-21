# R314 — XAUUSD NY Clock-Time Drift Search — Preregistration

Registered: 2026-10-21. Status before computation: **LOCKED / R314 PnL not yet inspected**.

## Mechanism

Test whether a reproducible directional drift exists at a fixed New York clock time in XAUUSD. Potential sources include repeated liquidity-provider inventory cycles, settlement-related flows, or daily hedging; this is a hypothesis, not a claimed fact or guaranteed source of alpha. This family differs from R313 spread-dislocation reversal, R274 candle-impulse continuation, R298 range sweep/reclaim, R302 PM auction extension fade, and R305/R306 cross-asset directional filters.

## Data and split

Use the already checksum-verified XAUUSD M5 paired BID/ASK archive. Apply strict exclusive cutoff `2026-01-01T00:00:00Z` before any rolling feature, selection or trade outcomes. No 2026 price or PnL may be viewed. Discovery/selection: 2016–2020. Historical validation: 2021–2025 (not pristine project-wide OOS due prior exploration). Do not open the protected 2026 period unless every pre-2026 hard gate below passes.

## Frozen candidate grid

There are exactly 48 fixed New York local clock slots at 00:00, 00:30, …, 23:30 and two directions (LONG/SHORT): 96 candidates total. No weekday, month, volatility, trend or prior-return filters; no multi-slot composition. For each eligible New York calendar date, a candidate attempts at most one trade at its registered half-hour slot.

- Signal is purely the registered calendar slot, not a price-pattern trigger. Use the exact M5 bar open at slot time S, if present and active.
- Entry is the first paired active M5 bar open exactly at S+5 minutes. This is an explicit five-minute delay after the clock alert.
- Stop distance is the median BID true range over the prior 12 eligible active bars, excluding the bar at S. No forward fill or synthetic bars. Skip if the trailing range or delayed entry quote is unavailable.
- Initial stop distance is 1.00R. Target is 1.25R in the chosen fixed direction. Long enters at ASK open and exits on BID quotes; short enters at BID open and exits on ASK quotes. If stop and target both touch within one M5 bar, assume stop first. A gap through stop is filled at the worse opening executable quote; target fills no better than target level.
- Maximum holding period is 60 minutes. If the active quote stream has a gap before target/stop/time exit, flatten at the last observed executable close before the gap and mark `data_gap_time`; do not synthesize bars. One open trade per candidate at any time and at most one trade per NY date.
- Friction beyond the observed BID/ASK spread is deducted from PnL at $0.00, $0.10, $0.30 (primary) and $0.50 per ounce. `R = [direction × (exit executable price − entry executable price) − additional round-trip cost] / initial stop distance`.

## Candidate selection—discovery only

For all 96 candidates, compute discovery period (2016–2020) net R at +$0.30/oz and a Newey–West HAC mean test on weekly net R (four lags; include zero-trade weeks). Apply Holm step-down correction across the full 96 one-sided tests. The candidate carried forward is the candidate with the highest HAC t-statistic among those with at least 200 discovery trades and positive discovery net R at +$0.30/oz. If none meet those two preconditions, R314 stops at discovery with **GAGAL**. The best candidate's Holm-adjusted p-value is recorded; a value >=0.05 is a hard failure for advancing to a protected final test.

The single selected clock and direction are frozen before opening validation outputs. No other slot, opposite direction or variation can be promoted after seeing validation.

## Required outputs and hard gates

Commit a row-level discovery ledger for the full grid; selected-candidate validation ledger; all-cost results, 96-candidate selection table with unadjusted and Holm-adjusted p-values, year/period summaries, a full zero-inclusive weekly PnL series, exact raw-source manifest/checksums and a 10,000-replicate circular four-calendar-week bootstrap (seed 314) of the selected validation candidate.

To be eligible for the one reserved final test, all must pass:
1. Discovery has a selected candidate with >=200 trades, positive net R at +$0.30/oz, and Holm-adjusted one-sided p < 0.05.
2. Selected candidate validation has >=200 trades and positive net R at +$0.30/oz.
3. Validation PF_R >=1.05 at +$0.30/oz; at least 3 of five validation years are positive.
4. Validation four-week block-bootstrap 95% lower bound for mean weekly net R >0.
5. At +$0.50/oz, validation net R remains positive and PF_R >=0.90.
6. Quote-side execution, trade frequency, drawdown clustering and one-hour holding are compatible with phone execution, but cannot override the hard gates.

Any failed hard gate = **GAGAL**; do not promote the selected slot, switch direction, or test a neighboring time. A screen pass authorizes a separate execution-readiness review, not live trading or a claim of funded challenge success. Exact intended-account contract sizes, commissions, swaps, slippage and server reset timezone/DST remain execution gates.
