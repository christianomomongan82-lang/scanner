# R298 Data Manifest

## Input identity
- Instrument/timeframe: XAUUSD M5.
- Source archive: conversation artifact `xauusd_m5_bid_ask.zip`, collection artifact ID `12031270051`, collection run `38859918137`.
- Input files expected by the runner:
  - `xauusd_bid_M5_2016-2026.csv.gz`
  - `xauusd_ask_M5_2016-2026.csv.gz`
- Rows per side: 947,326. BID and ASK timestamps pair one-to-one.
- BID SHA-256: `b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575`.
- ASK SHA-256: `b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9`.
- R298 runner drops all timestamps at or after `2026-01-01T00:00:00Z` before candidate construction. It used 877,930 source rows and excluded 69,396 2026+ rows.

## Repository status
The R298 preregistration, runner, final report, compact JSON, annual summary, complete trade ledger, event-quality audit, London-signal audit, Asian-window audit, weekly-bootstrap input series and README are stored individually in this repository and linked from [R298_INDEX.md](R298_INDEX.md).

**Raw-data limitation:** the original source archive is approximately 20 MB and remains an external conversation artifact; it is not committed as a GitHub file in this sync. The source hashes above are the identity check the runner enforces. All *research outputs and code* are in GitHub, so you can inspect them there without downloading the ZIP bundle. To rerun from the exact same data, the two matching gzip CSVs still need to be supplied to the runner's `--data-dir`.

## Integrity requirements
Do not substitute a re-downloaded file unless its SHA-256 matches exactly. Do not remove static source rows by fabricating replacement candles. The runner validates timestamp equality, uniqueness, M5 alignment and OHLC ordering, and it rejects hash mismatch.
