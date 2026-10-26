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

## 3. Full-roster Yahoo acquisition — current Actions snapshot

Run [40321267682](https://github.com/christianomomongan82-lang/scanner/actions/runs/40321267682) menjalankan workflow data-only dari GitHub Actions. Job persiapan, validasi queue 962 ticker unik, dan syntax check kolektor berhasil. Semua CSV yang berhasil diperoleh disimpan ke branch data bersama hash/manifest per ticker; tidak ada PnL di Actions.

**Snapshot progres terakhir yang terverifikasi dari run dan batch manifest:**

| Metrik | Status |
|---|---:|
| Queue sumber listing IDX yang sedang dipakai untuk coverage | 962 ticker |
| Batch selesai penuh dengan semua ticker sukses | 52 / 97 |
| Batch berstatus INCOMPLETE (CSV parsial dan manifest tetap di-commit) | 28 |
| Batch masih berjalan | 3 |
| Batch masih antre | 14 |
| CSV ticker berhasil tersimpan | 767 |
| Total baris harian dalam CSV sukses/parsial yang tersimpan | 2.140.303 |
| Baris OHLC invalid menurut manifest awal per batch | 1.063 |
| Ticker yang tidak mendapatkan CSV Yahoo | 33 |
| Error HTTP 429 pada batch yang sudah selesai | 0 |

Snapshot ini bukan hasil akhir. Tiga puluh tiga ticker gagal pada tahap `Ticker.history` dengan exception `HTTPError: HTTP Error 404: ` (lihat tabel di bawah dan failure ledger). Setiap 404 diklasifikasikan non-transient oleh collector, dicatat pada manifest, lalu tidak di-retry. Tidak ada 429 yang terlihat pada manifest yang telah selesai saat snapshot ini, jadi jadwal 30/120/600/600 detik belum terpicu. Jika 429 muncul pada batch tersisa, collector menerapkan jadwal tersebut sampai maksimal lima attempt.

### Gagalnya ticker Yahoo — exact status dan log

| Batch | Ticker gagal | Tahap | Error yang disimpan |
|---:|---|---|---|
| 25 | TECH.JK, BTEL.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 38 | COWL.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 42 | GAMA.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 44 | GOLL.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 45 | HOME.JK, HOTL.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 46 | IIKP.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 50 | KBRI.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 51 | LCGP.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 52 | LMAS.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 53 | MAGP.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 54 | META.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 58 | OCAP.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 59 | PLAS.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 60 | POOL.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 62 | RIMO.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 63 | SCPI.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 64 | SIMA.JK, SKYB.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 65 | SMRU.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 66 | SRIL.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 67 | SUGI.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 70 | TRAM.JK, TRIL.JK, TRIO.JK | `Ticker.history` | `HTTPError: HTTP Error 404: `; TRIO also `possibly delisted; no timezone found` |
| 71 | UNIT.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 72 | WSKT.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 74 | MTRA.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 75 | ARMY.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 76 | MABA.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 78 | JSKY.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |
| 79 | TDPM.JK | `Ticker.history` | `HTTPError: HTTP Error 404: ` |

Manifest per-batch tetap sumber detail otoritatif, termasuk response code 404 dan log yfinance; daftar lengkap dan SHA Git tiap manifest tersimpan di [failure ledger JSON](https://github.com/christianomomongan82-lang/scanner/blob/data/r333-idx-daily-yahoo/data/r333/manifests/yahoo_batches/failure_ledger_run_40321267682.json).

Penting: sebagian ticker berasal dari roster IDX yang saat ini mencantumkan nama, jumlah saham, dan board, namun Yahoo tidak mengembalikan histori. Log `No data found, symbol may be delisted` hanya muncul untuk sebagian ticker (misalnya TECH.JK, BTEL.JK, TRIO.JK); itu **bukan** bukti resmi delisting dan dapat juga menunjukkan ticker Yahoo tidak tersedia atau mapping berbeda. Status delisting tetap harus diverifikasi dari sumber resmi.

Job batch gagal bukan karena commit: setiap batch di tabel ini menyimpan CSV bagi ticker yang sukses beserta manifest error ke data branch. Workflow sengaja memberi job conclusion `failure` supaya hasil parsial tidak disalahartikan sebagai semua ticker berhasil.

### Implikasi data dan next step

- Data roster tetap **survivorship-biased** sampai data delisting point-in-time tersedia.
- **1.063 baris OHLC invalid** dari 767 CSV sukses/parsial yang sudah selesai tetap dipertahankan; tak ada interpolasi, forward-fill, atau auto-repair.
- Tidak ada bukti bahwa 962 kode pada queue merupakan universe aktif lengkap; 33 Yahoo 404 menambah kebutuhan mencocokkan roster dengan catatan listing/delisting resmi.
- Setelah seluruh 97 batch selesai, tarik artefak Actions ke sandbox dan jalankan hanya audit integritas cache (`research/r333_audit_yahoo_dataset.py`), bukan backtest. Roster point-in-time, shares outstanding dan sektor historis belum diverifikasi, sehingga G1–G11 strategi tetap NOT_RUN dan PnL tetap dilarang.

## 3. Gate status dan metrik

| Item | Status | Alasan |
|---|---|---|
| Smoke acquisition Yahoo | **PASS** | 4/4 ticker didownload dan committed melalui Actions. |
| Cache determinism / SHA check | **PASS untuk smoke cache** | SHA manifest cocok dengan CSV di artefak yang ditarik dari Actions. Ini bukan pass untuk strategi. |
| OHLC quality | **FAIL untuk clean-input eligibility tanpa penanganan** | Ada 57 baris OHLC invalid/blank di empat file; tak boleh diisi/diperbaiki diam-diam. |
| Historical universe incl. delisted | **NOT VERIFIED** | Hanya smoke tickers, belum ada roster historis yang terkunci. |
| Shares outstanding/sector point-in-time | **NOT VERIFIED** | Sumber data point-in-time belum ada. |
| Split/dividend adjustment semantics | **NOT FULLY VERIFIED** | Raw request and actions stored, but underlying adjustment semantics and completeness need audit. |
| Strategy gates G1–G11 | **NOT_RUN** | Belum ada universe yang eligible; dilarang hitung PnL. |
| Edge verdict | **NOT_TESTED** | Tidak ada sinyal, trade, PnL atau PF yang dihitung. |

Angka performa yang diwajibkan—n trade, PF pada cost realistis/1,5×/2×, expectancy R, total R, t-stat, bootstrap CI, jumlah posisi simultan, annual breakdown, equal-weight baseline, IHSG baseline—semua `null/NOT_RUN`, bukan nol.

## 4. Biaya dan eksekusi live

Jangkar biaya publik broker yang sebelumnya dicatat adalah 0,1513% beli dan 0,2513% jual (Ajaib; bukan verifikasi akun pengguna). **Fee broker live, slippage, spread/antrean aktual, dan risiko eksekusi ARA/ARB belum diverifikasi pada akun nyata.** Seluruh riset ini simulasi sampai syarat usia, akun, data, dan eksekusi aktual terverifikasi.

## 5. Putusan terkini

**R333 = `DATA_INADEQUATE`; alpha = `NOT_TESTED`.** Unduhan smoke berhasil, tetapi empat ticker tidak membangun universe small-cap historis. Invalid bars belum diselesaikan, delisted and point-in-time shares/sector coverage belum terbukti, sehingga Stage 1–2/backtest tidak dijalankan. Tidak ada klaim “tidak ada edge” atau “ada edge”.
