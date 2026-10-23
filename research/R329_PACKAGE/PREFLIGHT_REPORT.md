# R329 candidate-specific pre-outcome gate

**Verdict: PREFLIGHT PASS. No PnL has been calculated by this gate.**

Source: fourteen native H1 BID/ASK streams across EURUSD, GBPUSD, AUDUSD, NZDUSD, USDCHF, USDCAD and USDJPY. Source artifact 12400822266, acquired by data-only workflow 39719343805. Composite SHA-256: `2db7c7d88b2f31965ff956dd5e017ce7f0b76a4ac1792dca4896833b884e85e0`.

All fourteen streams match their pinned hashes and byte counts. Each stream contains 78,361 rows; BID/ASK timestamps are exact per pair and the seven-way common intersection has 78,361 timestamps. Duplicate, misaligned, invalid OHLC, non-finite OHLC, and negative opening/closing spread counts are all zero. The shared active Tuesday 10:00 UTC signal calendar has 468 snapshots. Missing timestamps remain missing; static/flat rows are retained in raw inputs but are not eligible to signal, enter, or exit.

| Horizon | Discovery legs / dates | Confirmation legs / dates | Gate |
|---|---:|---:|---|
| 13 weeks | 1,001 / 143 | 658 / 94 | PASS |
| 26 weeks | 896 / 128 | 644 / 92 | PASS |
| 39 weeks | 840 / 120 | 644 / 92 | PASS |
| Minimum | 200 / 100 | 100 / 70 | — |

The locked runner and all three candidate gates passed. This authorizes the separate frozen economic screen; it does not establish that the signal has positive expectancy. R329's economic runner rechecks input hashes and refuses to calculate PnL unless this archived summary explicitly records all candidate sample gates as passed and `outcomes_computed=false`.

2026 data remain excluded. XAUUSD 2026 remains unopened.
