# R333 Yahoo Cache Audit — Actions run 40321267682

**Verdict:** `DATA_INADEQUATE`  
**Alpha verdict:** `NOT_TESTED`  
**Scope:** raw-cache provenance / integrity / OHLC quality only. No signals, trade simulation, PnL, PF, expectancy, R or alpha calculations.

## 1. Source and artifact provenance

- GitHub Actions run: https://github.com/christianomomongan82-lang/scanner/actions/runs/40321267682
- Workflow purpose: Yahoo 1d OHLCV data collection only, not a backtest.
- Data source: Yahoo Finance queried by GitHub Actions runner via `yfinance==1.7.0`; Python 3.12.15.
- Parameters: start 2010-01-01, end omitted/current provider end, interval 1d, `auto_adjust=False`, `actions=True`, `repair=False`, `keepna=True`.
- Artifact ID: `12649374154`
- Artifact name: `R333-Yahoo-current-listings-batches-40321267682`
- Downloaded artifact ZIP SHA-256: `96306cc81c0b7fc18fc4ff436fda422c14844371950945d3136a9bc14e83aa51`
- Archive contains 97 per-batch manifests, the 962-row acquisition queue, queue README, batch CSVs and failure ledger.
- The artifact was transferred from GitHub into the sandbox. **The sandbox did not access Yahoo.**

## 2. Final batch and ticker counts

| Item | Audited result |
|---|---:|
| Queue rows / unique Yahoo ticker symbols | 962 / 962 |
| Batch manifests | 97 |
| Batches fully successful | 63 |
| Batches incomplete (one or more Yahoo 404s; partial successful CSVs preserved) | 34 |
| Ticker requests successful | 921 |
| Ticker requests failed | 41 |
| CSV files in combined artifact | 922 |
| Rows across the 921 queue-ticker CSVs | 2,399,444 |
| Invalid OHLC rows (recomputed from CSVs) | 1,124 |
| CSVs with zero invalid OHLC rows | 462 |
| CSVs with one or more invalid/blank OHLC rows | 459 |
| Duplicate date rows across acquired ticker CSVs | 0 |
| CSV data files whose SHA-256 matches manifest | 921 / 921 |
| CSV whose byte length matches manifest | 921 / 921 |
| CSV row count and first/last date match manifest | 921 / 921 |
| Missing required fields or invalid/unordered dates | 0 integrity failures |
| HTTP 429 recorded in completed ticker manifests | 0 |
| Strategy PnL / PF computed | **No** |

The 922nd CSV is the separately acquired `^JKSE` smoke baseline file (`IDX_JKSE.csv`); it is not one of the 962 stock symbols in the current-listing acquisition queue.

For the 921 downloaded queue tickers, all file-integrity checks passed: recomputed SHA-256, bytes, row count, first/last dates, date ordering, zero duplicate dates and required-field presence all match their per-batch manifest. This is a cache integrity result only. It does not mean every OHLC row is valid, or that the source has complete historical listing coverage.

## 3. Raw OHLC quality is not clean

There are 1,124 rows that fail basic OHLC geometry/field validity checks across the 921 acquired ticker CSVs. Those rows were **preserved, not fixed, dropped, forward-filled or interpolated**. A full per-ticker invalid-row count and hash remains in each batch manifest.

Yahoo daily data in this collector contains raw OHLC, Adj Close, Volume, Dividends and Stock Splits. Asking for `auto_adjust=False` preserves raw OHLC in the request, but the semantics/completeness of all historical adjustments and corporate actions are not independently established. Yahoo daily OHLCV also does not provide observed executable bid/ask quotes or order-queue data.

## 4. Exact Yahoo failures

The 41 ticker requests that failed did so at the `Ticker.history` stage, with last recorded error `HTTPError: HTTP Error 404: ` (TRIO has the more specific message `$TRIO.JK: possibly delisted; no timezone found`).

```text
TECH.JK
BTEL.JK
COWL.JK
GAMA.JK
GOLL.JK
HOME.JK
HOTL.JK
IIKP.JK
KBRI.JK
LCGP.JK
LMAS.JK
MAGP.JK
META.JK
OCAP.JK
PLAS.JK
POOL.JK
RIMO.JK
SCPI.JK
SIMA.JK
SKYB.JK
SMRU.JK
SRIL.JK
SUGI.JK
TRAM.JK
TRIL.JK
TRIO.JK
UNIT.JK
WSKT.JK
MTRA.JK
ARMY.JK
MABA.JK
JSKY.JK
TDPM.JK
NUSA.JK
HKMU.JK
DUCK.JK
CPRI.JK
POSA.JK
ENVY.JK
PURE.JK
CBMF.JK
```

These are Yahoo symbol/data-availability failures, not official proof that each company is delisted. The 34 incomplete jobs are expected to conclude failure because one or more tickers failed, while any successful CSVs in the same batch and the exact error manifest are committed. The final archive was uploaded successfully.

No HTTP 429 was recorded in the completed batch manifests, so the 30/120/600/600-second retry schedule was not triggered. Because 404 is classified as non-transient in the collector, those ticker requests stopped on their first attempt. No source fallback was used.

## 5. Survivorship and universe gate

The queue is frozen in deterministic order from the *current* IDX listing snapshot and is labelled `survivorship-biased`. The collector produced histories for 921 names on that list, but this does **not** create a valid historical IDX universe. Official delisting records were not successfully acquired; historical point-in-time shares outstanding and sector classifications are also unverified. It is not permissible to apply today's listed-shares figure retroactively to historical market capitalization.

The original small-cap rule remains unchanged: bottom 30th percentile of IDX market capitalization at each monthly rebalance using point-in-time shares, plus the registered 60-session liquidity filter. This universe is **NOT FROZEN**. The daily price cache cannot yet be used for R333 strategy PnL.

## 6. Decision

**R333 remains `DATA_INADEQUATE`; alpha is `NOT_TESTED`.** Raw-cache integrity passed for the 921 successful stock CSVs, but OHLC quality has 1,124 invalid rows and, more importantly, delisted listing membership / point-in-time shares / sectors are not verified. Every output from the current-roster dataset must be marked **`survivorship-biased`**. Do not claim edge or no edge and do not calculate strategy PnL until the historical universe gate is legitimately resolved.

Broker live fees, slippage, observed spread/queue, and ARA/ARB execution fills have not been verified in a real account. This research remains simulation-only.
