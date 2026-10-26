# R333 — Hasil dan Verdict

**VERDICT: `DATA_INADEQUATE` — alpha `NOT_TESTED`.**  
Smoke-test unduhan harga berhasil. Namun smoke test empat ticker bukan universe small-cap historis dan input belum lolos seluruh audit kelayakan. Tidak ada perhitungan sinyal, trade, PF, expectancy, R, t-stat atau PnL yang dijalankan.

- Branch riset: `research/r333-idx-smallcap-daily`
- Branch data: `data/r333-idx-daily-yahoo`
- Preregistrasi terkunci: [R333_LOCKED_PREREGISTRATION.md](R333_LOCKED_PREREGISTRATION.md) · [amendment akuisisi](R333_DATA_AMENDMENT_20261026.md) · [audit roster/delisting](R333_IDX_METADATA_AUDIT_20261026.md)
- Collector Yahoo data-only: [r333_yahoo_source_only.py](r333_yahoo_source_only.py)
- Workflow Yahoo data-only: [.github/workflows/r333-yahoo-daily-source-only.yml](../.github/workflows/r333-yahoo-daily-source-only.yml)
- Governance: [SEARCH_GOVERNANCE_AND_SCORING_V1.md](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/market-response-model-v1-20261023/research/SEARCH_GOVERNANCE_AND_SCORING_V1.md)
- Hasil cache ada di [branch data](https://github.com/christianomomongan82-lang/scanner/tree/data/r333-idx-daily-yahoo).

## 1. Akuisisi Yahoo yang sah — GitHub Actions only

Run terbaru yang diaudit: [40309094513](https://github.com/christianomomongan82-lang/scanner/actions/runs/40309094513). Status Actions **SUCCESS**. Akuisisi dijalankan dari runner GitHub, bukan dari sandbox: Python 3.12.15, yfinance 1.7.0, start 2010-01-01, interval 1d, end omitted (API current end), auto_adjust=False, actions=True, repair=False, keepna=True. Keempat ticker sukses pada attempt pertama; tidak ada error Yahoo pada run ini. Data dan manifest sudah di-commit ke branch data.

- Manifest: [latest.json](https://github.com/christianomomongan82-lang/scanner/blob/data/r333-idx-daily-yahoo/data/r333/manifests/latest.json), Git blob SHA a05692486f1da2062947c170555996f1be15965c.
- Actions artifact [12642749466](https://github.com/christianomomongan82-lang/scanner/actions/runs/40309094513/artifacts/12642749466), ZIP SHA-256 6c33aaeecffe60442dc5d37ec25dcec578e1ee8b1cddc8f48021a14b8534c49f. Artefak diimpor ke sandbox hanya untuk audit dan checksum; sandbox tidak mengakses Yahoo.
- Run [40306521287](https://github.com/christianomomongan82-lang/scanner/actions/runs/40306521287) sebelumnya gagal di setup workflow sebelum akuisisi Yahoo karena cache pip meminta requirements.txt/pyproject.toml. Itu kesalahan infrastruktur, bukan Yahoo 429. Setelah perbaikan, run data-only berhasil.

Semua file mencakup 4.131 baris tanggal dari 2010-01-04 sampai 2026-10-26. Hash SHA-256 di bawah diverifikasi ulang terhadap CSV pada artefak run 40309094513.

| Ticker | CSV | Rows | First–last | Bytes | SHA-256 | Invalid OHLC | Dividends / splits |
|---|---|---:|---|---:|---|---:|---|
| ^JKSE | IDX_JKSE.csv | 4.131 | 2010-01-04–2026-10-26 | 446.287 | 9d404c0248b346dfe5ea75545d4c054597ab73061777527e9f208a487ba3b203 | 52 | 0 / 0 |
| BBCA.JK | BBCA_JK.csv | 4.131 | 2010-01-04–2026-10-26 | 301.116 | 68e873bb42470e68324a175a4298a8b93a2d0dc74c17963fcdf3a7256a2992cd | 0 | 35 / 1 |
| BBRI.JK | BBRI_JK.csv | 4.131 | 2010-01-04–2026-10-26 | 425.536 | 28f50503e1495241421e8e8cf9bd7a4b0ef09277f514c884d1167a12cde03902 | 1 | 22 / 2 |
| TLKM.JK | TLKM_JK.csv | 4.131 | 2010-01-04–2026-10-26 | 303.037 | 83cccf3388f14dc71a562c586a8bffda184effbdc8298301d3ac66b533d549f9 | 4 | 19 / 1 |

Quality audit: zero duplicate dates and no missing date/column names across all four CSVs. ^JKSE has 52 blank OHLC rows with Volume=0; these are preserved and not treated as tradable bars. BBRI.JK has a geometry violation on 2016-04-20 (Low > Open). TLKM.JK has geometry violations on 2012-06-27, 2012-06-29 and 2016-04-20, plus one blank OHLC row on 2019-06-19. Total invalid/blank OHLC rows = 57. Do not fill, interpolate or repair any without an explicitly registered rule.

CSV fields: Date, Open, High, Low, Close, Adj Close, Volume, Dividends, Stock Splits. Raw OHLC was requested explicitly and corporate-action fields were retained, but historical split/adjustment semantics and completeness are not independently established. This smoke set only validates the acquisition route; it is not the small-cap universe and does not pass the final data eligibility gate.

## 2. Universe and latest IDX delisting audit

### Current active roster found

Official IDX source-only run [40309248358](https://github.com/christianomomongan82-lang/scanner/actions/runs/40309248358) returned an active-listed securities JSON from the block subdomain. Source response: HTTP 200, 131,862 bytes, SHA-256 92114ed2700e7b723b9d538de77009ac09561cff423fdda2c105088df066f6e9. Parsed JSON SHA-256 db85c01ded27208bad3610d5dc1f3931dd3033bad1b03c84d4f6b53726896e82. The source reported 962 rows and 962 unique codes, which are committed as data/r333/universe/current_idx_listed_roster.csv (Git blob SHA 943c4aba24ef097fd59d0781669321dd38d5f704).

This roster gives current code, name, listing date, currently listed shares and board. It does **not** prove historical monthly constituents, historic shares outstanding or historical sector membership. It is not the frozen small-cap universe.

### Delisting records not acquired — exact errors

The metadata workflow's overall conclusion was ROSTER_JSON_FOUND, not full delisting success. The manifest's selected_delistings field is null. The following source attempts failed:

1. Primary IDX endpoint, [manifest](https://github.com/christianomomongan82-lang/scanner/blob/data/r333-idx-daily-yahoo/data/r333/manifests/idx-metadata-latest.json): `https://www.idx.co.id/primary/ListingActivity/GetDelisting?start=0&length=2000` — 3 attempts, HTTP 403 Cloudflare. Last error begins: `HTTP 403: <!DOCTYPE html><html lang="en-US"><head><title>Just a moment...</title><meta http-equiv="Content-Type" ...`; last body 5,979 bytes, content type text/html.
2. Block host endpoint: `https://block.idx.id/primary/ListingActivity/GetDelisting?start=0&length=2000` — 3 attempts, HTTP 404, 147 bytes. Exact body:
    HTTP 404: {"Message":"No HTTP resource was found that matches the request URI 'http://localhost:8000/api/ListingActivity/GetDelisting?length=2000&start=0'."}
3. Primary listing activity page: `https://www.idx.co.id/id/perusahaan-tercatat/aktivitas-pencatatan` — 3 attempts, HTTP 403 Cloudflare; last body 5,888 bytes.
4. Block listing activity page: `https://block.idx.id/id/perusahaan-tercatat/aktivitas-pencatatan` — HTTP 200, 146,471 bytes, SHA-256 bef90e211f4ac562334267ba0054740010b786bda55dd48980073c0cd703223d. It loads the page but provides no delisted data table by itself.

### Frontend scan

Run [40309624911](https://github.com/christianomomongan82-lang/scanner/actions/runs/40309624911) successfully downloaded 15/15 official IDX JavaScript assets. It found the page code's data route string `/primary/ListingActivity/GetDelisting` and public monthly/quarterly delisted-company report routes. The strings are only endpoint-discovery evidence: no response of delisted records was fetched, so they do not remove the survivorship gap.

### Current universe and survivor bias

- Current active listing snapshot: 962 unique codes.
- Delisted history records successfully acquired: **0** (this does not mean IDX has no delisted companies).
- Point-in-time historical shares outstanding and sectors: **not verified**.
- Therefore, a queue of these tickers for daily price acquisition is **survivorship-biased** and is only an acquisition/coverage roster, not a selected small-cap universe.
- Keep the original small-cap definition: monthly cross-sectional bottom 30% market cap using point-in-time shares, plus the locked 60-session liquidity filter. Do not use the latest shares-outstanding field retroactively, do not choose names using PnL, and do not calculate strategy PnL until a defensible universe gate passes.
- The deterministic source-acquisition queue is committed at [yahoo_daily_acquisition_roster.csv](https://github.com/christianomomongan82-lang/scanner/blob/data/r333-idx-daily-yahoo/data/r333/universe/yahoo_daily_acquisition_roster.csv), with its contract in [YAHOO_ACQUISITION_QUEUE_README.md](https://github.com/christianomomongan82-lang/scanner/blob/data/r333-idx-daily-yahoo/data/r333/universe/YAHOO_ACQUISITION_QUEUE_README.md). It freezes all 962 current ticker codes in source order, with no PnL-dependent filtering. This is **only** a survivorship-biased acquisition queue, not a small-cap universe. The Actions-only batch collector is [r333_yahoo_batch_source_only.py](r333_yahoo_batch_source_only.py); the 97-batch matrix workflow is [.github/workflows/r333-yahoo-full-roster-source-only.yml](../.github/workflows/r333-yahoo-full-roster-source-only.yml). The workflow will be launched by committing its batch request. Each batch has at most 10 tickers and keeps its own immutable manifest; failures after 5 attempts retain exact ticker/stage/error diagnostics. Even if all current-symbol histories download, original R333 remains DATA_INADEQUATE until historical delisting membership and point-in-time shares/sectors are defensible.

## 3. Full-roster Yahoo acquisition — final run and sandbox audit

Final matrix run: [40321267682](https://github.com/christianomomongan82-lang/scanner/actions/runs/40321267682), with conclusion `failure` by design because 34 batches had one or more non-transient 404 ticker failures. The archive job still succeeded and uploaded artifact `12649374154`. No strategy computation ran on Actions.

- Artifact: `R333-Yahoo-current-listings-batches-40321267682`, 29,062,170 bytes according to Actions.
- Artifact ZIP SHA-256 computed in the sandbox: `96306cc81c0b7fc18fc4ff436fda422c14844371950945d3136a9bc14e83aa51`.
- Sandbox audit report: [R333_YAHOO_CACHE_AUDIT_40321267682.md](R333_YAHOO_CACHE_AUDIT_40321267682.md) and [machine-readable JSON](R333_yahoo_cache_audit_40321267682.json).
- The archive was extracted in the sandbox. The sandbox did not query Yahoo; it checked only the bytes obtained from the GitHub Actions artifact.

### Acquisition and file integrity

| Metric | Final audit |
|---|---:|
| Frozen current-listing acquisition queue | 962 unique tickers |
| Per-batch manifests / batches | 97 / 97 |
| Fully successful batches | 63 |
| Incomplete batches | 34 |
| Successful queue ticker CSVs | 921 |
| Failed queue ticker requests | 41 |
| CSV files in artifact | 922 (includes extra smoke cache `^JKSE`) |
| Rows over 921 stock CSVs | 2,399,444 |
| Invalid OHLC rows (recomputed) | 1,124 |
| Files with clean OHLC | 462 |
| Files with at least one invalid OHLC row | 459 |
| SHA-256 identical to manifest | 921/921 |
| Byte length / row count / first-last date matches | 921/921 |
| Duplicate date rows / required-field errors / date-order failures | 0 / 0 / 0 |
| HTTP 429 observed | 0 |
| Strategy PnL/PF | **NOT RUN** |

The 921 acquired stock CSVs pass byte/row/date/hash integrity checks, but **their raw OHLC quality is not clean**: 1,124 rows fail basic OHLC field/geometry checks. Nothing was repaired, removed or interpolated. Raw OHLC, Adj Close, Volume, Dividends and Stock Splits were preserved. Split/dividend adjustment completeness is not independently proven and Yahoo daily OHLCV does not provide observed executable bid/ask / queue fill data.

### Exact failures

All 41 unavailable ticker requests failed at stage `Ticker.history`, with the last recorded error `HTTPError: HTTP Error 404: `. The special TRIO message was `$TRIO.JK: possibly delisted; no timezone found`.

```text
TECH.JK, BTEL.JK, COWL.JK, GAMA.JK, GOLL.JK, HOME.JK, HOTL.JK, IIKP.JK,
KBRI.JK, LCGP.JK, LMAS.JK, MAGP.JK, META.JK, OCAP.JK, PLAS.JK, POOL.JK,
RIMO.JK, SCPI.JK, SIMA.JK, SKYB.JK, SMRU.JK, SRIL.JK, SUGI.JK, TRAM.JK,
TRIL.JK, TRIO.JK, UNIT.JK, WSKT.JK, MTRA.JK, ARMY.JK, MABA.JK, JSKY.JK,
TDPM.JK, NUSA.JK, HKMU.JK, DUCK.JK, CPRI.JK, POSA.JK, ENVY.JK, PURE.JK,
CBMF.JK
```

Per-ticker exact logs and manifest hashes are in the [failure ledger](https://github.com/christianomomongan82-lang/scanner/blob/data/r333-idx-daily-yahoo/data/r333/manifests/yahoo_batches/failure_ledger_run_40321267682.json). The 34 incomplete batch jobs still committed their other successful CSVs plus manifests; the workflow conclusion is a visible partial-collection failure, not a commit failure. The retry schedule 30/120/600/600 seconds was not used because no HTTP 429/rate-limit/transient error was recorded. The collector treated the HTTP 404 responses as non-transient and stopped after one request. **Yahoo 404 is not official proof of IDX delisting.**

### Survivorship warning and universe

The queue was derived from the current IDX roster and is **`survivorship-biased`**. It has no successfully acquired official delisted records; shares outstanding and sector assignments point-in-time remain unverified. The Yahoo ticker history coverage does not fix those omissions and may be incomplete for names that are still present in the current roster.

The registered small-cap universe remains **NOT FROZEN**: monthly bottom 30th percentile of market capitalization using point-in-time shares, with the pre-registered 60-session liquidity filter and discovery correlation de-duplication. Today's shares outstanding must not be used retroactively. The current-roster queue is for acquisition coverage only, not candidate selection, not a historical universe, and not an input to strategy PnL.

## 3. Gate status dan metrik

| Gate / data prerequisite | Status | Alasan |
|---|---|---|
| Yahoo acquisition path via Actions | **PASS with 41 ticker failures** | 921 ticker CSVs retrieved; 41 404 failures recorded; no fallback. |
| Cache integrity | **PASS for 921 acquired CSVs** | SHA, bytes, rows, date range and order match manifest; zero duplicate dates. |
| Raw OHLC quality | **FAIL for clean-input eligibility** | 1,124 invalid/blank OHLC rows preserved in 459 files. |
| Historical delisted membership | **NOT VERIFIED** | No official delisted records acquired; Yahoo 404 does not verify delisting. |
| Point-in-time shares outstanding / sectors | **NOT VERIFIED** | Current listing metadata is not a historical monthly snapshot. |
| Corporate-action adjustment semantics | **NOT FULLY VERIFIED** | Raw OHLC and corporate-action fields exist; completeness/adjustment semantics remain unaudited. |
| Observable spread and executable fills | **NOT AVAILABLE / UNVERIFIED** | Yahoo daily OHLCV has no observed bid/ask or queue. |
| Final small-cap universe | **NOT FROZEN** | Preregistered point-in-time market-cap and liquidity filters cannot yet be safely applied. |
| G1–G11 strategy gates | **NOT_RUN** | Prerequisite data/universe gate not passed; no signal or PnL run. |
| Alpha verdict | **NOT_TESTED** | No strategy trade, PnL or PF calculated. |

Mandatory performance metrics—trade count, PF at 1×/1.5×/2× costs, expectancy R, total R, t-stat, bootstrap CI, max concurrent positions, annual breakdown, equal-weight matched basket and IHSG baseline—remain `null/NOT_RUN`, not zero. Do not infer “no edge” or “edge exists” from an eligibility failure.

## 4. Biaya dan eksekusi live

Jangkar biaya publik broker yang sebelumnya dicatat adalah 0,1513% beli dan 0,2513% jual (Ajaib; bukan verifikasi akun pengguna). **Fee broker live, slippage, spread/antrean aktual, dan risiko eksekusi ARA/ARB belum diverifikasi pada akun nyata.** Seluruh riset ini simulasi sampai syarat usia, akun, data, dan eksekusi aktual terverifikasi.

## 5. Putusan terkini

**R333 = `DATA_INADEQUATE`; alpha = `NOT_TESTED`.** Unduhan smoke berhasil, tetapi empat ticker tidak membangun universe small-cap historis. Invalid bars belum diselesaikan, delisted and point-in-time shares/sector coverage belum terbukti, sehingga Stage 1–2/backtest tidak dijalankan. Tidak ada klaim “tidak ada edge” atau “ada edge”.
