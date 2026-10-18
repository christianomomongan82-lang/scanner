# R301 — Data Manifest

- Provider: Dukascopy via dukascopy-node; pre-existing raw-data collection archives.
- XAUUSD archive artifact: GitHub Actions artifact #12031270051, collection run #38859918137.
- USA500 M5 archive artifact: GitHub Actions artifact #11709864394.
- Local archive ZIP SHA-256, XAUUSD: 2cde8338800fd7f4d5d4628512201c16757ef06bd90d51ffdc8ef9bea425ba1a
- Local archive ZIP SHA-256, USA500: 21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac
- XAU BID gzip member SHA-256: b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575
- XAU ASK gzip member SHA-256: b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9
- USA500 M5 BID gzip member SHA-256: df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee

## Cutoff and integrity

The exclusive cutoff is 2026-01-01T00:00:00Z and was applied before feature construction or outcome calculation. XAUUSD had 947,326 raw rows per side; 69,396 per side at/after cutoff were excluded, leaving 877,930 rows per side. USA500 had 886,206 raw rows; 67,605 rows at/after cutoff were excluded, leaving 818,601 rows. Source timestamps were strictly monotonic, with no duplicates and zero invalid OHLC rows before cutoff. XAU BID/ASK timestamp sets matched exactly; there were no negative open/close spreads.

USA500 was context-only, not a traded instrument. Of the New York weekday RTH sessions, 2,558 passed the strict 78-bar, five-minute-grid check and 33 incomplete sessions were omitted. No missing rows were filled, timestamps interpolated, or flat bars synthesized. Ordinary flat XAU bars were not automatically labeled closed because a flat observed M5 bar can be valid. Candidate events were restricted to New York cash-session timestamps.

Raw archives are not duplicated in Git because the files are large; the artifact IDs, member hashes, and local ZIP hashes are recorded above. The 2021–2025 validation interval is program-contaminated. The reserved XAUUSD 2026 interval remained unopened.
