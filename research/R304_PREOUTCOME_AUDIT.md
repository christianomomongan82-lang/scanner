# R304 — Pre-outcome eligibility audit

**Status:** completed before calculating any R304 trade outcome. No PnL, win rate, expectancy, PF or net-R values were calculated in this audit.

## Source integrity

- Raw GitHub artifact: #11959096102, acquisition run #38697080604, Dukascopy EURUSD M1 BID/ASK.
- ZIP SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- BID member SHA-256: `b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc`.
- ASK member SHA-256: `52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b`.
- 4,415,493 rows per side; timestamps paired exactly; no duplicates, invalid OHLC rows, or negative open/close spreads.
- Registered repeated-flat filter removes 696,795 rows; 3,718,698 active paired timestamps remain. There are 12,018 gaps greater than one minute across the full archive; gaps remain missing and no synthetic tradable bars are created.

## Eligibility before outcome calculation

| Module | Window / direction | 2017 | 2018 | 2019 | 2020 | 2021 |
|---|---|---:|---:|---:|---:|---:|
| E | 08:00–12:00 Europe/London, SHORT | 256 | 258 | 257 | 257 | 256 |
| U | 08:00–12:00 America/New_York, LONG | 258 | 258 | 256 | 259 | 257 |

Entry is the first active quote at/after 08:05 local and no later than 08:10; exit must have an exact active 12:00 local quote. Stop-monitoring path must be contiguous in the retained active M1 series; no path gaps are accepted. The prior-session median range requires at least 15 prior eligible ranges; per the pre-outcome amendment, only sessions with exactly 240 active minute timestamps (08:00–11:59) may enter the range-history estimator. See [full-session range-history amendment](R304_DQ1_FULL_SESSION_RANGE_AMENDMENT.md). Median session coverage was 100% in every module/year shown.

**Eligible total across discovery 2017–2020 and validation 2021: 2,572 module-events** (1,284 Module E; 1,288 Module U). These are eligible scheduled events before outcome calculation, not trades with known profitability.

The local audit ledger is identified by SHA-256 `fb1f2a8bed616bd0ac457b08dd89113b6729c2857e3c3b26ab90a4c080520b42`; the local runner SHA-256 is `9f5852d543902c5937c08368f2922d7dfe5475527d741fb5e5380ff272a97c22`. The runner records the filter, timestamp logic, event eligibility and all skip reasons. The exact raw data is the identified GitHub artifact, not a new data source. The full row-level audit CSV remains identified locally rather than committed as a decoded file in this branch. No outcomes after 2021 are calculated unless all locked discovery/validation gates pass.
