# R299 Data-Quality Amendment — Exact Timestamp-Key Alignment

**Committed before any R299 candidate PnL was calculated.** This amendment is narrowly limited to cross-instrument timestamp alignment; the hypothesis, Q95 threshold calibration, discovery/validation periods, entry delay, stop/target, holding period, cost schedule, bootstrap, and gates remain unchanged.

## Reason for amendment
The raw USA500 and USATECH M5 files do not contain identical complete timestamp sets. Timestamp-only audit found:
- USA500: 886,206 unique rows.
- USATECH: 886,039 unique rows.
- Exact shared timestamps: 886,031.
- USA500-only timestamps: 175.
- USATECH-only timestamps: 8.
Both streams are strictly increasing, unique, and M5-aligned. Most unmatched timestamps occur in earlier history. This audit examined timestamps only; no OHLC outcomes, signal PnL or performance statistics were calculated.

Requiring both raw arrays to have the exact same length and index order would discard/abort a valid lagged cross-instrument design for an irrelevant file-layout reason. Conversely, forward-filling, inventing bars, or pairing by row number would be invalid.

## Superseding data alignment rule
- Load each instrument as its own timestamp-indexed series; never join by row number.
- For a USATECH signal at timestamp T, its seven source bars T−30m through T must exist at their exact timestamps, be M5-contiguous and active.
- To trade the signal, USA500 must contain the exact signal timestamp T plus each exact timestamp needed for the six-bar risk window; all required rows must be M5-contiguous and active.
- USA500 entry at T+10m and time exit at T+40m must each exist as exact timestamps. Every intervening target bar must exist at its exact M5 timestamp and be active. Missing rows are logged as skips; there is no forward-fill, synthetic bar, shifted entry or delayed exit.
- Retain per-stream duplicate, chronological-order, M5-grid and OHLC validation. For data quality, report timestamp set intersection and per-stream unmatched counts, not a false pass/fail based on whole-array equality.
- The global time cutoff remains absolute: any source or target row at or after 2022-01-01T00:00:00Z is dropped before activity checks, threshold calibration, signal construction, or PnL calculation.

No signal-performance values were inspected before this amendment. If timestamp-key-aligned inputs still fail an exact event/trade-path requirement, skip the affected event and include the reason in the audit. No other specification parameter may change.
