# R259 — Locked R189/L80 cross-feed replication plan

**Status before run: PREREGISTERED; no result inspected.**  
**Branch:** `r259-r189-dukascopy-history`

## Question

Does the exact locked R189/L80 signal and execution logic show comparable historical behavior on Dukascopy EURUSD M1 BID/ASK data for 2016–2025?

This is **not** an exact reproduction of the original report. The repository does not contain the original `EURUSD_M1_2016-2025.xz`, `spread_2016-2025.csv.xz`, or 2016–2025 chronological ledger. A matching result on a different feed cannot prove that the old reported ledger is correct.

## Frozen rules

Reuse the R189 OOS signal-generation and execution code without changing strategy parameters:

- Displacement threshold: 15 pips.
- Rolling windows: 11 and 12 observed M1 closes.
- Candle body minimum: 2 pips.
- Late-move ratio minimum: 0.80.
- Directional consistency: at least 7 same-direction steps.
- Fixed GMT-5 wall clock with no DST: hours 03:00–11:59 eligible, excluding hours 06 and 09.
- Deduplicate signals within 14 bars.
- Entry at the next observed M1 open; reject if entry spread exceeds 1.5 pips.
- SL 6 pips; TP 18 pips; when favourable excursion reaches 6 pips, zero-distance trailing logic activates.
- Time exit after 60 bars. Report both legacy timing and the causal implementation (exit at the scheduled bar open without checking that bar's future high/low).
- Use actual executable quote sides: long ASK entry/BID exits; short BID entry/ASK exits.
- No parameter search or replacement of the selected rules after observing results.

## Data and attribution

- Fresh Dukascopy EURUSD M1 BID/ASK, 2016-01-01 through 2025-12-31 UTC.
- Validate timestamps, duplicate rows, OHLC geometry, common BID/ASK timestamps, negative spreads, spread distribution, file SHA-256 checksums, and monthly download success.
- Additional cost stress on top of observed quote-side execution: 0, 0.2, 0.5, 0.8, 1.0, and 2.0 pips per closed trade.
- Report separate periods: discovery 2016–2020, validation 2021, forward 2022–2025, the old report's broad 2021–2025 interval, and full 2016–2025.
- Periods are attributed by entry timestamp. Trades exiting at/after a period boundary are excluded from that period. The recent 2026 OOS test remains a separate sample.

## Acceptance gates for this cross-feed check

The historical forward period (2022–2025) must have at least 100 completed trades, PF ≥1.10 after +1 additional pip, PF ≥1.05 after +2 pips, and no forward entry-year with at least 20 trades may have PF <1.00 after +1 pip. In addition, the four-week circular block bootstrap of weekly net pips at +1 pip must have a 95% interval whose lower bound is above zero. Report validation 2021 and 2026 OOS as separate diagnostics; do not use either to retune the parameters.

Failure of any required gate means **GAGAL for the cross-feed robustness check**. Passing these gates would still not be an exact reproduction or a funded-readiness claim: the original inputs are missing, live commission/slippage need verification, and sub-30-second Quick Strike compliance cannot be established from M1 OHLC timestamps.

## Outputs

- `research/r259_r189_history_results.json`: machine-readable metrics, phase cuts, stress results, annual cohorts, hashes, download diagnostics, and final binary verdict.
- `research/r259_r189_history_legacy_trades.csv`
- `research/r259_r189_history_causal_trades.csv`

Raw downloaded files remain ephemeral in the Actions runner and are not claimed to be versioned in GitHub. The saved hashes and fixed download procedure support reruns, but do not archive the full raw quotes.
