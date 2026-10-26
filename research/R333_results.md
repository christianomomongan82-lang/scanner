# R333 — Hasil dan Verdict

**VERDICT: `DATA_INADEQUATE` — alpha `NOT_TESTED`.**  
Smoke-test unduhan harga berhasil. Namun smoke test empat ticker bukan universe small-cap historis dan input belum lolos seluruh audit kelayakan. Tidak ada perhitungan sinyal, trade, PF, expectancy, R, t-stat atau PnL yang dijalankan.

- Branch riset: `research/r333-idx-smallcap-daily`
- Branch data: `data/r333-idx-daily-yahoo`
- Preregistrasi dan amandemen: [R333_LOCKED_PREREGISTRATION.md](R333_LOCKED_PREREGISTRATION.md)
- Collector Yahoo data-only: [r333_yahoo_source_only.py](r333_yahoo_source_only.py)
- Workflow Yahoo data-only: [.github/workflows/r333-yahoo-daily-source-only.yml](../.github/workflows/r333-yahoo-daily-source-only.yml)
- Governance: [SEARCH_GOVERNANCE_AND_SCORING_V1.md](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/market-response-model-v1-20261023/research/SEARCH_GOVERNANCE_AND_SCORING_V1.md)
- Hasil cache ada di [branch data](https://github.com/christianomomongan82-lang/scanner/tree/data/r333-idx-daily-yahoo).

## 1. Akuisisi Yahoo yang sah (GitHub Actions)

Workflow run [40306721616](https://github.com/christianomomongan82-lang/scanner/actions/runs/40306721616) dan [40307108809](https://github.com/christianomomongan82-lang/scanner/actions/runs/40307108809) berhasil mengunduh keempat ticker melalui Python + `yfinance==1.7.0`, lalu commit CSV dan manifest ke branch data. Run terbaru yang direkonsiliasi dengan manifest: **40307108809**, selesai 2026-10-26 10:24:41 UTC. Artefak dari Actions digunakan untuk membawa cache tersebut ke sandbox tanpa mengakses Yahoo dari sandbox. Hash ZIP artefak Actions: `144ee050d6507c0b335d46b3f2fbe8a25a8fd6c16070a30449a26b4dcd4c4415`.

Parameter: start `2010-01-01`, interval `1d`, `auto_adjust=False`, `actions=True`, end tidak ditentukan agar provider mengembalikan data terbaru. Versi yfinance dicatat di manifest. Run pertama [40306521287](https://github.com/christianomomongan82-lang/scanner/actions/runs/40306521287) adalah **kegagalan infrastruktur workflow sebelum akuisisi** karena cache pip meminta `requirements.txt/pyproject.toml`; bukan 429 dan bukan attempt pengambilan Yahoo. Setelah perbaikan, run berikutnya sukses pada attempt 1 untuk tiap ticker.

Manifest sumber: [latest.json](https://github.com/christianomomongan82-lang/scanner/blob/data/r333-idx-daily-yahoo/data/r333/manifests/latest.json).

| Ticker | Data rows | Tanggal pertama | Tanggal terakhir | File bytes | SHA-256 CSV | Invalid OHLC rows* | Corporate actions tercatat |
|---|---:|---|---|---:|---|---:|---|
| `^JKSE` | 4.131 | 2010-01-04 | 2026-10-26 | 446.298 | `08c46c6a8d59d831f03c4a9cecb2431fda831323db2e9cc3e5256139ccf45fd3` | 52 | 0 dividends, 0 splits |
| `BBCA.JK` | 4.131 | 2010-01-04 | 2026-10-26 | 300.992 | `16f85b162f544a12bfab96d149aaa7509c23a1fc241c5be2c978a6b8ad881890` | 0 | 35 dividend rows, 1 split |
| `BBRI.JK` | 4.131 | 2010-01-04 | 2026-10-26 | 425.609 | `f7e1aa2165a42f3c23e702cf19512e8d39b9084d9094b003cb8280533ae83b39` | 1 | 22 dividend rows, 2 splits |
| `TLKM.JK` | 4.131 | 2010-01-04 | 2026-10-26 | 303.002 | `bb1dcc8c3608a3b9b1b19c208f6a65ba4aeb222b41b0547afc83e6303cac1689` | 4 | 19 dividend rows, 1 split |

*Audit defined an invalid row as missing/non-numeric OHLC or OHLC geometry that violates `Low ≤ Open/Close ≤ High`. The 52 `^JKSE` rows are blank OHLC rows (not tradable bars, often non-trading dates); `BBRI.JK` has a geometry issue on 2016-04-20; `TLKM.JK` has three geometry issues (2012-06-27, 2012-06-29, 2016-04-20) plus one blank row (2019-06-19). There are 0 duplicate dates in all four files and no missing required column names. Do not fill blanks or repair broken OHLC silently; preserve and exclude invalid rows by a preregistered rule if the data eventually qualifies.

CSV columns: `Date, Open, High, Low, Close, Adj Close, Volume, Dividends, Stock Splits`. The raw-price request was `auto_adjust=False`, and `Adj Close` and action fields are preserved. Whether Yahoo's historical OHLC semantics fully represent pre-/post-split raw prices is not independently verified; presence of a split event field alone is not proof that all split handling is correct.

## 2. Universe / official IDX source acquisition

Sumber publik yang terverifikasi untuk membangun roster adalah halaman resmi IDX [Daftar Saham](https://block.idx.id/id/data-pasar/data-saham/) (table includes code/name/listing date/listed shares/board), [Ringkasan Saham](https://idx.co.id/id/data-pasar/ringkasan-perdagangan/ringkasan-saham/) (includes ticker, value, volume and listed shares), dan [Aktivitas Pencatatan](https://www.idx.co.id/id/perusahaan-tercatat/aktivitas-pencatatan) (tabs New Listing / Delisting / Relisting). Sumber web yang dibaca tidak membuktikan bahwa halaman roster kini mencakup seluruh delisted ticker sejak 2010 atau historical shares outstanding point-in-time. Karena itu, roster aktif saat ini tidak boleh langsung dianggap sebagai universe historis layak.

Workflow source-only resmi IDX sudah ditambahkan: [.github/workflows/r333-idx-metadata-source-only.yml](../.github/workflows/r333-idx-metadata-source-only.yml), collector [r333_idx_metadata_source_only.py](r333_idx_metadata_source_only.py). Run pertamanya, [40308051186](https://github.com/christianomomongan82-lang/scanner/actions/runs/40308051186), gagal karena SyntaxError di collector—itu kegagalan implementasi, bukan hasil dari sumber IDX. Script diperbaiki; run [40308193067](https://github.com/christianomomongan82-lang/scanner/actions/runs/40308193067) sedang dievaluasi dalam log saat laporan ini diperbarui. Belum ada roster yang dikunci, dan belum ada PnL. Hasil endpoint resmi dan status delisted coverage harus ditambahkan setelah run diperiksa.

**Aturan universe tidak berubah:** small-cap = percentile ke-30 kapitalisasi pasar cross-section IDX tiap rebalance bulanan, menggunakan shares outstanding yang diketahui pada tanggal tersebut; filter median nilai transaksi 60 sesi sebelumnya ≥ Rp500 juta/hari dan minimum 54/60 sesi valid; ticker ordering dan dedup korelasi di discovery mengikuti preregistrasi. Daftar universe final dan provenance harus di-commit sebelum PnL.

Jika saham delisted atau saham beredar point-in-time tidak dapat diverifikasi, status data historis tetap `DATA_INADEQUATE`; jika analisis deskriptif bersyarat akhirnya dijalankan terhadap survivor-only roster, seluruh hasil wajib dilabeli **`survivorship-biased`** dan tidak boleh dipromosikan sebagai bukti edge tanpa koreksi bias eksplisit dan terukur.

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
