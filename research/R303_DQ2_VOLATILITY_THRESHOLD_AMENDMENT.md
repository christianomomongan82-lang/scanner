# R303 DQ2 — Trailing volatility threshold implementation

**Timestamp:** 2026-10-19 UTC, before the event eligibility audit and before candidate PnL.
**Amends:** `R303_EURUSD_SPREAD_SHOCK_REVERSION_PREREGISTRATION.md`

To make the rolling Q90 deterministic and computationally reproducible without using the signal day itself, calculate the 90th percentile of absolute valid 5-minute midpoint returns from the exact 20 calendar days immediately preceding each UTC day's 00:00 boundary, requiring at least 1,000 observations. Freeze that threshold for the whole UTC day. No return from the current UTC day contributes to its threshold. All other preregistered rules remain unchanged.
