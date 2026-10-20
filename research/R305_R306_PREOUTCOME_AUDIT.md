# R305/R306 — Pre-outcome audit (locked batch)

**Audit was generated before calculating any trade outcome.** No PnL, win-rate, PF, expectancy or target completion metric was inspected for either candidate at the time this audit was saved.

## Input integrity

- EURUSD M1 paired BID/ASK archive: 4,415,493 rows/side before the registered 2026 cutoff, exactly paired, 0 invalid OHLC, 0 negative open/close spreads. The R304-compatible repeat-flat filter removed 696,795 rows; 3,718,698 active M1 rows remain, from which 736,076 complete contiguous M5 bars were built.
- XAUUSD M5 paired BID/ASK archive: 877,930 rows/side before the 2026 cutoff, exactly paired, 0 duplicate/nonincreasing timestamps, 0 invalid OHLC, 0 negative open/close spreads.
- Exact timestamp keys only. EURUSD M5 and XAU M5 had 732,199 shared signal timestamps. Missing rows were not forward-filled; no synthetic candles were created.
- Data artifacts are existing GitHub raw-data artifacts: EURUSD #11959096102 / XAUUSD #12031270051. Their exact member hashes and source windows are in the locked registrations.
- Hard cutoff timestamp >= 2026-01-01 UTC was applied before features and signal event construction. 2026 XAU outcomes remain unopened.

## Registered-signal and execution-path audit

| Candidate | 2017–2020 candidate events | T+10 baseline execution-eligible | T+15 stress path-eligible | 2021–2025 candidate events | T+10 baseline execution-eligible | T+15 stress path-eligible |
|---|---:|---:|---:|---:|---:|---:|
| R305 common-USD transmission continuation | 16,270 | 16,196 | 16,191 | 18,973 | 18,928 | 18,926 |
| R306 EURUSD shock + XAU underreaction catch-up | 3,834 | 3,796 | 3,795 | 4,529 | 4,515 | 4,516 |

Event counts are pre-outcome eligibility only, not completed trades and not evidence of edge. Eligibility requires exact delayed-entry timestamp, a contiguous 13-bar prior true-range path, and a complete contiguous 60-minute exit/stop path.

## Audit reproducibility note

- Full local event eligibility CSV: SHA-256 `8774054abfe66f03eba9d991e54272f13aa4bcbfdff10b9e36d855255e7d6ff5`, 6,835,903 bytes.
- Local two-mode runner: `/mnt/data/r305_batch.py`.
- The row-level audit CSV is currently retained as a local session artifact and is **not** represented as committed row-level GitHub data in this summary. Repository-only reproducibility will remain a failed gate unless that row-level file and exact runner are committed and verified.
