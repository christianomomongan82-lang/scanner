# R300 Data Manifest — Pre-Outcome

- Candidate: R300 EURUSD London 4pm fix post-event reversal
- Status at audit: data-only gate passed; **no R300 signal PnL has been calculated yet**
- Source provider: Dukascopy via the previously collected data-only workflow
- Artifact ID: 11959096102; collection run: 38697080604
- Original archive SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`
- Exact members:
  - BID `eurusd_bid_M1_2016-2025.csv.gz`: `b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc`
  - ASK `eurusd_ask_M1_2016-2025.csv.gz`: `52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b`
- Exclusive outcome cutoff: 2022-01-01 00:00 UTC, applied before event/outcome construction.

## Pre-outcome integrity results

| Check | Result |
|---|---:|
| BID M1 rows before cutoff | 2,650,553 |
| ASK M1 rows before cutoff | 2,650,553 |
| Paired rows | 2,650,553 |
| BID/ASK timestamp sets | Exact match |
| Duplicate/non-monotonic rows | 0 |
| Invalid OHLC rows | 0 |
| Negative open/close spreads | 0 |
| Active on both sides | 2,202,782 |
| Static or one-side-inactive | 447,771 |
| Valid complete active M5 bars | 422,289 |
| Eligible 16:05 London event dates, 2017–2021 | 1,283 |

The eligible entry quote spread is median 0.30 pip, 95th percentile 0.40 pip, maximum 0.80 pip. This is quote-quality evidence only; no direction, return or PnL outcome was examined in this audit.

## Required handling

- The original ZIP is retained as external artifact 11959096102; repository stores its provenance/checksums, not a duplicate of all raw quote data.
- Build M5 only from five exact consecutive active M1 rows with matched BID/ASK timestamps. Never forward-fill or create bars.
- Joins are exact timestamp-key joins; use Europe/London IANA timezone/DST conversion.
- M1 bid/ask OHLC archives contain static quote rows outside active periods; M5 aggregation only keeps five-row blocks with all rows active on both sides.
- 2022+ observations are not scored under R300. The 2017–2021 FX sample is contaminated at programme level and cannot certify a funded-ready edge.
- See [locked preregistration](R300_EURUSD_LONDON_FIX_POST_EVENT_REVERSAL_PREREGISTRATION.md), [runner](r300_eurusd_london_fix.py), and [pre-outcome JSON audit](R300_preoutcome_data_audit.json).
