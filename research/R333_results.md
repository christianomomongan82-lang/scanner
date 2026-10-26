# R333 — Hasil dan Verdict

**VERDICT: `DATA_INADEQUATE` — `alpha NOT_TESTED`.**

Data belum dinyatakan layak dan belum ada hasil performa strategi. Status ini bukan verdict alpha negatif: **tidak ada edge belum dapat disimpulkan** karena PnL/PF belum dihitung.

- Family: `IDX_SMALLCAP_DAILY`, keluarga baru; parent tidak ada.
- Branch riset: `research/r333-idx-smallcap-daily`.
- Preregistrasi terkunci: [R333_LOCKED_PREREGISTRATION.md](R333_LOCKED_PREREGISTRATION.md).
- Workflow akuisisi yang dibuat: [R333 Yahoo daily source-only](../../tree/main/.github/workflows/r333-yahoo-daily-source-only.yml).
- Branch data yang ditetapkan: [data/r333-idx-daily-yahoo](../../tree/data/r333-idx-daily-yahoo).
- Perhitungan PnL/PF: **belum dijalankan**. Tahap 1–2 baru boleh jalan sesudah audit data lolos.

## 1. Aturan akuisisi yang berlaku sekarang

Akuisisi dilakukan **hanya melalui GitHub Actions**, dengan Python + versi yfinance yang dipatok, interval harian, `auto_adjust=False`, `actions=True`, start 2010-01-01 sampai tanggal pengambilan data, lalu file CSV dan manifest di-commit ke branch data. Percobaan via tool browser pada jawaban sebelumnya bukan akuisisi sah dan tidak dihitung sebagai percobaan workflow.

Workflow menerapkan maksimal lima total attempt per ticker, dengan jeda bertahap 30 detik, 120 detik, 600 detik, dan 600 detik antara attempt yang gagal. Error per ticker dan per attempt ditulis ke manifest. Jika empat ticker tes kecil tidak lengkap, percobaan terjadwal di jam berbeda akan mengulang tes yang gagal; tidak ada fallback ke penyedia lain.

## 2. Status cache saat laporan ini diperbarui

| Ticker smoke test | Baris | Tanggal pertama | Tanggal terakhir | SHA-256 | Status |
|---|---:|---|---|---|---|
| `^JKSE` | Belum terverifikasi | Belum terverifikasi | Belum terverifikasi | Belum terverifikasi | Menunggu hasil Actions |
| `BBCA.JK` | Belum terverifikasi | Belum terverifikasi | Belum terverifikasi | Belum terverifikasi | Menunggu hasil Actions |
| `BBRI.JK` | Belum terverifikasi | Belum terverifikasi | Belum terverifikasi | Belum terverifikasi | Menunggu hasil Actions |
| `TLKM.JK` | Belum terverifikasi | Belum terverifikasi | Belum terverifikasi | Belum terverifikasi | Menunggu hasil Actions |

Nilai di atas sengaja tidak diisi sebelum CSV benar-benar di-commit dan diaudit. Setiap nilai akhir harus berasal dari manifest data yang menyimpan baris, tanggal, versi pustaka, parameter unduhan, error aktual, dan SHA-256 file yang di-commit.

## 3. Kelayakan data / survivorship

Data Yahoo harus diaudit untuk missing/duplicate rows, OHLC invalid, volume, tanggal perdagangan, split/dividen, dan rentang yang benar-benar tersedia. Pengaturan permintaan raw adalah `auto_adjust=False`; kolom `Adj Close`, `Dividends`, dan `Stock Splits` disimpan bila tersedia. Harga raw tidak boleh disamakan dengan adjusted price.

Yahoo Finance biasanya menyediakan sejarah ticker yang masih tersedia, dan tidak menjamin arsip lengkap semua saham IDX yang telah delisting. Sampai roster delisted/point-in-time bisa diverifikasi, setiap hasil harus diberi label **`survivorship-biased`**. Jika saham delisted tidak dapat diperoleh, tidak ada klaim edge historis yang boleh dipromosikan tanpa koreksi eksplisit terhadap survivorship bias. Universe kecil yang hanya diambil dari ticker aktif tidak cukup untuk mengklaim representasi small-cap IDX historis.

## 4. Universe dan hasil performa

Universe small-cap harus didapat dari sumber yang bisa diverifikasi, diurutkan/dedup sesuai preregistrasi, lalu **daftar final dan provenance-nya di-commit sebelum perhitungan PnL apa pun**. Setelah daftar itu dikunci, data harian diunduh lewat Actions yang sama dan di-commit ke branch data.

Baseline wajib tetap: equal-weight buy-and-hold basket dari universe yang sama dan IHSG. Long-only sudah dikunci a priori; tidak ada short. Tidak boleh mengulang keluarga strategi yang ditutup atau memilih/membuang ticker berdasarkan PnL.

Semua metrik edge—jumlah trade, PF pada biaya realistis/1,5×/2×, expectancy R, total R, t-stat, bootstrap CI, annual breakdown, maximum simultaneous positions, baseline matched basket dan IHSG—berstatus **`NOT_RUN`**. Tidak ada angka nol yang dipakai sebagai pengganti data tidak tersedia.

## 5. Verdict biner dan gate

- **Status R333 saat ini: `DATA_INADEQUATE`.**
- **Status alpha: `NOT_TESTED`.**
- Status Gate A (data eligibility): **`DATA_INADEQUATE` sampai cache dan provenance lolos audit**.
- G1–G11 performa/robustness: **`NOT_RUN`**, bukan gagal performa, karena belum ada backtest.
- Tidak ada runner strategi atau trade ledger yang boleh dieksekusi sebelum data gate lolos.

Kriteria dan alur kerja tetap di [preregistrasi](R333_LOCKED_PREREGISTRATION.md), termasuk batas likuiditas, definisi small cap, dedup korelasi, sinyal raw price + volume, exit RR 1:2, periode discovery/forward/OOS, matched baseline, biaya dan semua gate.

## 6. Biaya dan eksekusi live

Jangkar biaya publik yang sudah dicatat dari Ajaib adalah 0,1513% beli dan 0,2513% jual; itu bukan verifikasi biaya akun pengguna. **Fee broker live, slippage, spread/antrean aktual, dan risiko eksekusi ARA/ARB belum diverifikasi pada akun nyata.** Riset ini tetap simulasi sampai syarat usia, akun, data, serta eksekusi nyata terkonfirmasi.

## 7. Audit provenance dan sejarah perubahan verdict

- Verdict sebelumnya `GAGAL` dicabut pada 2026-10-26 karena browser probes bukan akuisisi data sah untuk alur R333.
- Verdict terkoreksi: **`DATA_INADEQUATE` (alpha `NOT_TESTED`)**.
- Governance dibaca dari [SEARCH_GOVERNANCE_AND_SCORING_V1.md](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/market-response-model-v1-20261023/research/SEARCH_GOVERNANCE_AND_SCORING_V1.md).
- Template R332 dibaca dari branch `research/r332-multi-asset-trend`.
