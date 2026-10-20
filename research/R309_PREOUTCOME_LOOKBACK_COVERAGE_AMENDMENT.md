# R309 — Pre-Outcome Amendment: Rolling Lookback Coverage

**Committed before any R309 trade PnL was calculated.**

## Issue found
The first runner build interpreted “5,760 prior contiguous paired M5 returns” as requiring every timestamp in the entire 5,760-bar feature lookback to be five minutes apart. That creates no valid signal features across real market closures/weekends, so the feature-coverage audit returned zero valid z-score rows. No trade PnL, candidate metrics, or optimization was used from that implementation.

## Locked correction
- The lookback is the trailing 5,760 exact timestamp-joined paired M5 rows, not 5,760 wall-clock-contiguous bars.
- Return observations that bridge an observed timestamp gap greater than five minutes remain missing; no synthetic bar or cross-gap return is created.
- The rolling beta and z-score reference statistics require at least 4,608 valid observations (80% of the 5,760-row window). Missing observations are not forward-filled.
- The one-hour residual signal still requires 12 valid consecutive M5 residual returns.
- The actual trade entry timestamp and all forward monitoring/exit timestamps retain the preregistered exact-continuity rules; an entry or holding path that cannot be observed at the declared timing is excluded and counted.
- All price, direction, cost, delay, stop/target/time-exit, risk-unit, period and binary acceptance gates in the original R309 preregistration remain unchanged.
- The 2026 outcome window remains closed. Discovery remains 2017–2020 and 2021–2025 remains contaminated validation/diagnostic.

## Audit status
The literal implementation's zero-feature result is classified as **DATA/IMPLEMENTATION COVERAGE**, not evidence for or against the trading hypothesis. The amendment was committed before re-running the corrected feature builder and before scoring any R309 trade outcome. No threshold or rule was changed in response to strategy PnL.
