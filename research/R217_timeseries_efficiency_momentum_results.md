# R217 — Time-series momentum with directional-efficiency filter

**Decision: REJECT_FORWARD_GATE_FAILED.**

## Locked rules

- At completed H1 bars whose closes align with 00:00, 04:00, 08:00, 12:00, 16:00, or 20:00 UTC, calculate the raw close-to-close return over the preceding 24 H1 intervals.
- Directional efficiency = absolute 24-hour log price move divided by the sum of absolute H1 log moves over the same 24 intervals.
- Signal only when 24-hour absolute return >= 0.25% and directional efficiency >= 0.35. Trade in the sign of the 24-hour return.
- Enter at the next exact H1 open. Schedule exit four hours later; if that source bar is flat, delay until the first later non-flat source open. Flat signal and entry bars do not create a trade. No stop or target.
- Costs: modeled 1 and 2 bps round trip, not verified broker/prop costs.
- Discovery selection among ten indices: >=100 closed trades and PF@2bps >=1.00; choose highest discovery PF@2bps, tie-break by more trades. Forward/OOS only for that locked winner.

## Discovery candidates

| Instrument | Trades | PF @1 bp | PF @2 bps | Eligible |
|---|---:|---:|---:|---|
| Japan 225 | 2084 | 1.1235 | 1.0579 | YES |
| FTSE 100 | 1679 | 1.1197 | 1.0509 | YES |
| Germany 40 / DAX | 1871 | 1.0848 | 1.0267 | YES |
| US30 | 1973 | 1.0865 | 1.0175 | YES |
| US Tech 100 | 2226 | 1.0664 | 1.0066 | YES |
| Australia 200 | 1563 | 1.0628 | 0.9918 | NO |
| US Small Cap 2000 | 1418 | 1.0279 | 0.9815 | NO |
| EU50 | 1518 | 1.0308 | 0.9797 | NO |
| US500 / S&P 500 | 1966 | 1.0349 | 0.9651 | NO |
| France 40 | 1579 | 0.9876 | 0.9378 | NO |

## Locked selection: Japan 225

| Period | Trades | PF @1 bp | PF @2 bps | Mean net @1 bp | Mean net @2 bps |
|---|---:|---:|---:|---:|---:|
| Discovery 2017–2021 | 2084 | 1.1235 | 1.0579 | +1.9394 bps | +0.9394 bps |
| Forward 2022–2025 | 1611 | 0.9488 | 0.8966 | -0.9290 bps | -1.9290 bps |
| OOS 2026 | 327 | 0.9409 | 0.9046 | -1.5492 bps | -2.5492 bps |

### Forward annual cohorts

| Year | Trades | PF @1 bp | PF @2 bps |
|---:|---:|---:|---:|
| 2022 | 399 | 0.7806 | 0.7371 |
| 2023 | 431 | 0.9947 | 0.9294 |
| 2024 | 385 | 0.9854 | 0.9339 |
| 2025 | 396 | 1.0496 | 0.9982 |

## Audit and limitations

- All 15 tests in the exact local execution run passed, including full-vs-truncated prefix checks for all ten instruments.
- Ten H1 files validated for duplicate timestamps, hourly grid, finite OHLC, and valid candle relationships. Exact source SHA-256 fingerprints are stored in the local bundle.
- BID-only history; modeled costs only. ASK spread, actual broker/funded commissions, slippage, financing, and contract sizing are not verified.
- Selecting among ten instruments carries multiple-testing risk. This does not establish live/funded readiness.
