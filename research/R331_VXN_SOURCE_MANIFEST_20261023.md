# R331 VXN source manifest — 2026-10-23

**Purpose:** data provenance only. Raw VXN values are held in the local analysis environment and are not redistributed or committed to this public repository.

- Official source identified in the mirror README: https://cdn.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv
- Public mirror used to acquire the daily series: https://github.com/fuxui/vix-vxn/blob/main/data/history.json
- Mirror retrieval time recorded in JSON: 2026-10-23T00:27:11Z
- Mirror JSON SHA-256: 4c0603b692e69fd9b1aad3ae82ce2bdb0b875104e38d53c27991bf2202d1a11a
- VXN observations used locally: 750 daily rows, 2023-10-25 through 2026-10-21 inclusive, no duplicate dates or missing close values in the extracted window.
- Local derived CSV SHA-256 (file retained locally only): 23c48798bb9691d8f9d168ea8c1356e4f3acd0df739372f3f679d76ca200e448
- Local CSV columns: date,close. The raw daily values are not embedded in this manifest, the public R331 runner, or public result artifacts.

## Known limitation

The public mirror identifies the CBOE daily VXN history endpoint as its source, but this retrieval path is a third-party mirror rather than an authenticated point-in-time feed. The data is used only as a replication input for R331. The source CSV is historical and not FundedNext execution data. Any future discrepancy between the mirror and an official snapshot should be classified as a data-source issue; do not silently overwrite the local series after outcomes.