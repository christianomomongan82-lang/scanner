# Proyek Backtest — Checkpoint Utama

**Terakhir diperbarui:** 2026-10-16  
**Status proyek:** SEMUA KANDIDAT YANG DIUJI BERSTATUS GAGAL; TIDAK ADA YANG LULUS.  
**Repositori sumber utama:** https://github.com/christianomomongan82-lang/scanner  
**Branch riset aktif saat checkpoint ini:** [local-backtest/r189-dukascopy-history](https://github.com/christianomomongan82-lang/scanner/tree/local-backtest/r189-dukascopy-history)

Dokumen ini adalah titik lanjut permanen. Percakapan baru yang menerima instruksi “lanjut” harus membaca dokumen ini terlebih dahulu, lalu memeriksa artefak riset terbaru di branch aktif dan memperbarui checkpoint setelah ada hasil penting. Jangan meminta pengguna membuat prompt khusus atau mengunggah ulang data yang sudah ada di GitHub.

## 1. Protokol penyimpanan dan kelanjutan

- GitHub adalah sumber kebenaran untuk keputusan, kode, konfigurasi, data hasil, laporan, ledger transaksi, dan metadata eksperimen mulai sekarang.
- Jangan membuat file unduhan terpisah untuk pengguna. Simpan hasil langsung ke repositori; file baru hanya dibuat di GitHub sebagai bagian dari pekerjaan riset.
- Setiap backtest harus punya skrip, parameter yang dikunci, sumber/periode data, aturan eksekusi, hasil mesin yang dapat dibaca, laporan final, dan ledger jika ada transaksi.
- Jika data mentah atau artefak tidak tersimpan/versioned di repo, jangan mengklaim hasilnya sepenuhnya dapat direproduksi. Catat celahnya, checksum, dan lokasi artefak yang benar-benar tersedia.
- Setelah setiap eksperimen, simpan putusan biner **LULUS** atau **GAGAL** beserta alasan dan tautan artefak. Dilarang mengubah parameter setelah melihat hasil forward/OOS lalu melaporkan hasil yang diubah sebagai tes terkunci.
- Jika koneksi GitHub tidak tersedia di obrolan baru, jelaskan hambatannya; jangan berpura-pura mengetahui perubahan terbaru.
- Branch `main` menyimpan checkpoint ini. Branch riset aktif yang disebutkan di atas menyimpan artefak R251–R258. Jangan menganggap semua berkas di branch riset sudah berada di `main`.

## 2. Tujuan proyek

Mencari strategi forex yang mempunyai edge terukur dan dapat dieksekusi secara realistis, lalu menggunakan kombinasi strategi yang terbukti untuk meluluskan challenge funded secepat mungkin tanpa merusak akun. Setelah lolos, tujuan lanjutannya adalah pendapatan yang realistis dari akun simulasi $6.000.

Jangan mengembalikan target lama “2× UMK” atau asumsi lama FundedNext Futures tanpa konfirmasi baru. Simulasi Stellar 2-Step yang pernah dipakai (target 8% lalu 5%, DLL 5%, MLL 10%) hanyalah parameter historis dan tidak merupakan verifikasi aturan live yang lengkap. Jangan menyarankan membeli challenge sebagai langkah sekarang.

Preferensi strategi: gunakan price action/statistik mentah; indikator klasik EMA/RSI/MACD/Bollinger tidak dipakai kecuali pengguna mengubah batasan. PF minimal 1,10 pernah dipakai sebagai ambang diagnostik historis, bukan tujuan akhir. Tujuan utamanya adalah probabilitas dan kecepatan mencapai target challenge di bawah batas risiko; lihat bagian 'Latest authoritative objective' di bawah.

## 3. Perubahan arah strategis — 2026-10-15

**Keputusan terbaru: jangan memaksa satu strategi untuk sekaligus memenuhi semua kebutuhan** (expectancy tinggi, banyak sinyal, drawdown kecil, tahan di beragam kondisi, dan cepat lulus challenge).

Gunakan arsitektur modular, tetapi tidak harus menjalankan beberapa strategi sekaligus:

1. **Strategi A — kualitas edge.** Cari dan validasi edge positif yang tahan pada data di luar sampel. Frekuensi boleh rendah jika edge-nya nyata.
2. **Strategi B — edge pelengkap.** Dicari terpisah bila A kurang sering memberi sinyal. B harus punya alasan/edge independen; jangan sekadar menggandakan eksposur atau mengubah parameter A untuk menambah frekuensi.
3. **Satu pengendali risiko akun.** Mengendalikan risiko gabungan, posisi yang berkorelasi, daily loss limit, dan maximum loss limit. Ini tidak menciptakan edge; fungsinya membatasi kerusakan.

**Aturan kombinasi:** uji A dan B sendiri-sendiri terlebih dahulu. Hanya setelah masing-masing punya bukti memadai, gabungkan urutan sinyal mereka berdasarkan timestamp dan simulasi pada modal serta batas funded yang sama. Bandingkan expectancy, distribusi hasil, frekuensi, drawdown, overlap/korelasi, peluang melanggar aturan, dan waktu mencapai target. Kombinasi ditolak bila hanya menambah jumlah trade tetapi memperburuk expectancy atau risiko. Tidak wajib mempertahankan B jika tidak membantu.

## 4. Eksperimen terbaru dan putusannya

### R258 — GAGAL

- [Laporan putusan](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R258_FINAL_VERDICT.md)
- [Hasil JSON](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R258_multihorizon_momentum_results.json)
- [Ledger trade](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R258_multihorizon_momentum_trades.csv)
- [GitHub Actions run](https://github.com/christianomomongan82-lang/scanner/actions/runs/38610064013)

Aturan terkunci: momentum absolut 24 jam melewati persentil ke-65 yang dihitung hanya dari 2017–2020 dan searah dengan momentum 120 jam; entry pada open H1 berikutnya; stop = 0,5 × rentang high-low 24 jam setidaknya; TP = 2R; maksimal holding 24 jam; eksekusi menggunakan sisi BID/ASK yang sesuai. Missing hourly bars tidak diisi dengan bar sintetis.

Data Dukascopy EURUSD H1 BID/ASK 2017-01-01 sampai 2026-10-13. Ada 85.170 timestamp quote bersama; 0 timestamp duplikat, 0 OHLC invalid, 0 spread open negatif. Sebanyak 582 titik jam hilang/tidak lengkap tetap dibiarkan hilang. Engine mencatat 2.065 trade tertutup.

| Periode | Trade | PF quote teramati | PF +1 pip biaya tambahan | Net +1 pip |
|---|---:|---:|---:|---:|
| Discovery 2017–2020 | 820 | 1,040 | 0,977 | −306,3 pip |
| Validation 2021 | 166 | 0,973 | 0,900 | −222,6 pip |
| Forward 2022–2025 | 944 | 0,832 | 0,785 | −3.848,4 pip |
| OOS 2026 sampai 13 Okt | 135 | 0,954 | 0,889 | −224,9 pip |

Semua tahun forward 2022–2025 negatif setelah biaya tambahan 1 pip. Bootstrap pada forward memperkirakan probabilitas mean positif sekitar 0,3% dengan interval 95% sekitar −6,97 sampai −1,24 pip/trade. Semua gate utama gagal; **jangan retune R258 berdasarkan hasil forward/OOS**.

Replay challenge yang ada masih disederhanakan dengan proxy PnL harian tertutup, bukan mesin funded live-equivalent: risk 0,25%, 0,5%, dan 0,75% gagal Phase 1; risk 1% sempat menyentuh target Phase 1 lalu melanggar MLL pada Phase 2. Jangan mengutip replay tersebut sebagai probabilitas live yang presisi.

### R251–R257 — GAGAL

Semua jalur eksperimen R251–R257 yang tercatat di branch aktif harus diperlakukan sebagai gagal, bukan calon strategi untuk dihidupkan dengan tuning setelah melihat data. Mulai audit dari laporan/hasil masing-masing:

- [R251 verdict](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R251_FINAL_VERDICT.md)
- [R252 verdict](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R252_FINAL_VERDICT.md)
- [R253 verdict](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R253_FINAL_VERDICT.md)
- [R254 verdict](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R254_FINAL_VERDICT.md)
- [R255 verdict](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R255_FINAL_VERDICT.md)
- [R256 verdict](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R256_FINAL_VERDICT.md)
- [R257 machine-readable results](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R257_compression_breakout_results.json)

Jangan berasumsi penyebab kegagalannya sama. Ekstrak bukti per eksperimen untuk membuat taksonomi kegagalan kumulatif setidak memilih jalur strategi berikutnya.

### R189 — prioritas audit, tidak FINAL

- [GitHub Actions run OOS 2026](https://github.com/christianomomongan82-lang/scanner/actions/runs/38439056132)
- [Hasil OOS 2026](https://github.com/christianomomongan82-lang/scanner/blob/r189-oos-2026-test/research/r189_oos_2026_results.json)

Pemeriksaan independen EURUSD M1 2026-01-01 sampai 2026-10-12: 55 trade, PF 1,484 setelah biaya tambahan 0,2 pip, net +78,1 pip, mean +1,42 pip/trade, max drawdown 24,8 pip, sekitar 1,35 trade/minggu (~5,9/bulan). Ini terlihat menjanjikan, tetapi ukuran sampel masih kecil dan frekuensinya rendah. Cost stress PF: biaya tambahan 0 pip = 1,571; +0,5 pip = 1,365; +0,8 pip = 1,255; +1 pip = 1,187; +2 pip = 0,900.

Pengaturan terkunci yang diuji: displacement 15 pip, late ratio ≥0,8, body ≥2 pip, directional consistency ≥7 dalam tiap window 11/12 bar, sesi 03:00–11:59 fixed GMT−5 dengan jam 06 dan 09 dikecualikan, dedup 14 bar, ceiling spread entry 1,5 pip, SL 6 pip, TP 18 pip, MFE trigger 6 pip, trailing distance 0, time stop 60 menit. Biaya mencakup BID/ASK aktual +0,2 pip tambahan.

Metrik sejarah R189 yang pernah dikutip (2016–2025: 1.840 trade, PF 1,328; forward 2021–2025: PF 1,358) **tidak direproduksi secara independen** dan tidak boleh digabungkan begitu saja dengan validasi OOS 2026. Jangan menetapkan R189 LULUS setidak reproduksi historis dan audit implementasi selesai.

## 5. Celah yang tidak selesai

- Reproduksi penuh hasil historis R189 masih tidak selesai.
- Komisi broker/funded aktual, slippage live, pemetaan timezone platform, urutan intrabar saat SL/TP tersentuh di candle sama, serta aturan DLL/MLL yang benar-benar berlaku tidak seluruhnya diverifikasi.
- Challenge replay R258 tidak setara dengan engine funded yang sebenarnya.
- Penyimpanan data mentah/periode historis harus memiliki asal-usul, timestamp, sisi BID/ASK, checksum dan versi yang jelas; jangan mengandalkan data yang hanya pernah terunggah di percakapan.

## 6. Langkah berikutnya — status diperbarui 2026-10-15 (lokal, bukan Actions)

### Aturan kerja yang harus diikuti
- **Backtest harus dieksekusi di sesi ChatGPT/container lokal. Jangan dispatch GitHub Actions untuk menghitung backtest.**
- GitHub tetap menjadi sumber input dan penyimpanan riset: ambil dataset/artefak GitHub ke lingkungan lokal, jalankan engine di sini, lalu simpan kode, konfigurasi, hasil, gate, dan putusan ke repo.
- Jangan mengklaim uji lokal atas data H1 sebagai hasil R189 yang memerlukan M1.

### Peta kegagalan R251–R258 selesai
- [Peta kegagalan kumulatif R251–R258](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R251_R258_failure_taxonomy.md)
- Semua delapan jalur berakhir gagal. Pada mayoritas metode, frekuensi bukan masalah inti; expectancy tidak bertahan setelah biaya dan/atau tidak stabil pada forward tahunan. R257 menghasilkan nol trade valid pada periode validasi. Jangan retune konfigurasi lama memakai hasil forward/OOS.

### R260 — backtest lokal shock reversal: GAGAL
- [Preregistrasi R260](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r260-hourly-shock-reversal/research/R260_local_shock_reversal_preregistration.md)
- [Laporan hasil lokal](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r260-hourly-shock-reversal/research/R260_LOCAL_SHOCK_REVERSAL_RESULTS.md)
- [Runner lokal Python](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r260-hourly-shock-reversal/research/r260_local_shock_reversal.py)
- [Hasil JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r260-hourly-shock-reversal/research/R260_local_shock_reversal_results.json)
- Dijalankan di container lokal sesi ini memakai EURUSD H1 BID/ASK dari GitHub Actions artifact 11916174401; 85.170 quote bersama, 582 jam hilang/tidak lengkap tidak diisi, nol spread open negatif. Threshold abs candle body 90th percentile dari 2017–2020 = 12,9 pip; fade candle besar; SL di ekstrem candle, TP 1R, maksimum holding 6 jam.
- 7.961 trade selesai. Forward 2022–2025 menghasilkan PF 0,438 setelah +1 pip, net -8.654,5 pip, 17,41 trade/minggu. Semua tahun forward negatif; bootstrap 4-minggu pada net mingguan memberi CI 95% [-49,24, -34,51] pip/minggu. PF OOS 2026 setelah +1 pip 0,450. **GAGAL—hipotesis ditutup, tidak dituning.**

### R189 — hambatan data tidak terselesaikan
- Laporan historis R189 masih tidak bisa direproduksi: GitHub repo/artefak yang tersedia tidak memiliki arsip EURUSD M1 2016–2025 asli, file spread aslinya, atau ledger historisnya. Artefak EURUSD H1 yang tersedia tidak kompatibel untuk menguji ulang aturan R189 M1.
- OOS 2026 R189 tetap bukti terpisah, bukan pengganti data historis tersebut.
- Jangan jalankan backtest R189 atas H1 atau menyebut data eksternal baru sebagai “data dari GitHub”. Cari artefak/data M1 yang benar-benar tersimpan di GitHub terlebih dahulu. Jika tidak ada, tandai reproduksi sebagai blocked sampai input tersedia.

### Insiden R259 — workflow tak sengaja dibuat dan dijalankan
- Run [38623417685](https://github.com/christianomomongan82-lang/scanner/actions/runs/38623417685) sempat selesai setelah gue keliru mengirim eksperimen ke GitHub Actions. File workflow pemicu sudah dihapus dari branch `r259-r189-dukascopy-history` agar tidak membuat trigger berikutnya.
- Jangan menganggap output R259 sebagai hasil riset resmi; ia tidak mengikuti metode eksekusi yang disepakati (local backtest memakai data dari GitHub). Insiden ini dicatat untuk transparansi, bukan sebagai eksperimen yang diterima.
- Mulai sekarang tidak membuat workflow GitHub Actions untuk backtesting.

### Langkah berikutnya
1. Pertahankan R260 sebagai GAGAL; jangan ubah threshold/SL/TP untuk menyelamatkannya.
2. Cari di GitHub artefak yang benar-benar menyimpan EURUSD M1 historis yang cocok untuk R189; jika tidak tersedia, lanjutkan riset lokal pada hipotesis baru dengan dataset H1 GitHub yang tersedia, preregistrasikan dulu, dan simpan verdict biner.
3. Tetap pisahkan kualitas edge, frekuensi, dan kontrol risiko. Tidak ada strategi final yang lulus dan tidak ada strategi yang terbukti funded-ready.

**Kesimpulan status:** tidak ada strategi final yang lulus. R258 dan R260 GAGAL. Reproduksi historis R189 berstatus GAGAL karena data M1 asli tidak ditemukan; funded-readiness R189 berstatus GAGAL akibat batasan eksekusi. Eksekusi backtest selanjutnya dilakukan di sini; GitHub hanya sumber data/artefak dan penyimpanan.

## Koreksi permanen alur data — 2026-10-15

- Saat data yang dibutuhkan tidak tersedia secara lokal, **cari dan unduh sendiri dari file/artefak GitHub yang sudah ada** setidak meminta apa pun kepada pengguna.
- Dalam workflow backtest proyek ini, GitHub adalah satu-satunya sumber dataset/artefak yang dipakai secara default. **Jangan beralih ke Massive atau API penyedia data lain** tanpa izin eksplisit pengguna.
- GitHub bukan tempat menghitung backtest. Tarik data GitHub ke container/sesi ini dan jalankan perhitungan Python secara lokal di sini. Jangan membuat atau men-dispatch GitHub Actions untuk backtest.
- Jangan menunggu pengguna memerintah langkah pengambilan data yang sudah menjadi bagian normal pekerjaan. Jika data yang dibutuhkan tidak ada di GitHub, laporkan spesifik file/periode apa yang tidak ditemukan dan lanjutkan dengan dataset GitHub yang cocok yang benar-benar tersedia; jangan menggantinya diam-diam dengan timeframe atau feed yang tidak kompatibel.

### R261 — London-window impulse continuation: GAGAL (local run, 2026-10-15)

- [Preregistration and data-eligibility audit](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r261-london-impulse/research/R261_london_impulse_preregistration.md)
- [Final result report](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r261-london-impulse/research/R261_LONDON_IMPULSE_RESULTS.md)
- [Local runner](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r261-london-impulse/research/r261_london_impulse.py)
- [Machine-readable result](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r261-london-impulse/research/R261_london_impulse_results.json)
- [Annual forward table](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r261-london-impulse/research/R261_london_impulse_annual.csv)

Setup: EURUSD H1 London-local 05:00–08:00 impulse continuation, abs impulse threshold 14.5 pips (75th percentile fit on eligible weekdays in 2017–2020), 08:00 entry, stop at 3-bar range extreme, target 1.5R, same-day exit at 16:00 London. Data downloaded from the already-retained GitHub artifact 11916174401 and backtested in the local ChatGPT/container session. A first diagnostic pass that counted flat weekend placeholder quote bars was discarded; the official run excludes London-local weekends and recalculates the locked quantile on Monday–Friday windows. No GitHub Actions backtest was started for R261.

- 612 total trades from 2,552 complete weekday windows, about 1.0–1.3 trades/week depending period.
- Discovery 2017–2020 (262 trades): PF 0.938 and net −229.3 pips after +1 pip extra cost.
- Validation 2021 (59 trades): PF 1.574, net +311.4 pips at +1 pip.
- Forward 2022–2025 (249 trades): PF 0.984, net −59.8 pips at +1 pip.
- OOS 2026 through 13 Oct (42 trades): PF 1.206, net +95.35 pips at +1 pip, but below the minimum 50 OOS trades gate.
- Forward annual at +1 pip: 2022 PF 0.727 / −500.75 pips; 2023 PF 1.245 / +125.8; 2024 PF 1.266 / +92.05; 2025 PF 1.238 / +223.1.
- 4-week circular block bootstrap of 2022–2025 weekly net at +1 pip: probability of positive mean 45.38%; 95% interval for mean weekly net [−5.02, +4.38] pips.
- **Verdict: GAGAL.** Discovery and aggregate forward PF fail required gates, 2022 is deeply negative, OOS has insufficient trades, and bootstrap lower bound is below zero. Do not tune using forward/OOS results.
- This is not an R189 reproduction because input is H1, not required M1. It also does not validate live commissions, slippage, or funded constraints. R189 historical M1 remains blocked until its original M1 history/spread input is actually located in GitHub.

### Correction to data-missing procedure — 2026-10-15

A missing stored file must trigger data acquisition, not an immediate BLOCKED conclusion. If the required series is absent from existing files/artifacts:
1. Reuse the existing proven source/download method (for EURUSD M1, the repo already uses Dukascopy's dukascopy-node with the checked-in dukascopy_fetch_patch.cjs header patch).
2. Run a data-only collection job if direct download from this session is not available. It may fetch raw quotes and package them in a GitHub artifact, but it must not calculate signals, PnL, backtest metrics, or a verdict.
3. Retrieve the data artifact into the local ChatGPT/container session and run Python backtests here.
4. Keep feed provenance explicit. Fresh Dukascopy history is not identical to the missing original HistData M1/spread archive; it allows a separate same-feed historical replay, not a claim that the old HistData figures have been exactly reproduced.
5. Never call a market-data provider's analysis/backtest endpoints. Do not use Massive for this workflow. GitHub stores/serves data and research files; the test engine runs locally.

A data-only EURUSD M1 BID/ASK download for 2016-01-01 through 2025-12-31 has now been added in branch data/eurusd-m1-2016-2025. Run 38697080604 (https://github.com/christianomomongan82-lang/scanner/actions/runs/38697080604) is the acquisition step only—not a backtest. After it finishes, inspect/download its raw data artifact and run the locked local replay.


## R189 historical Dukascopy replay — checkpoint 2026-10-16

### Acquisition complete
- Data-only workflow [run 38697080604](https://github.com/christianomomongan82-lang/scanner/actions/runs/38697080604) succeeded. It downloaded raw EURUSD M1 BID/ASK 2016-01 through 2025-12; no signal or PnL calculation ran in Actions.
- Raw artifact: `EURUSD-M1-Dukascopy-BID-ASK-2016-2025`, ID `11959096102`, about 67.7 MB, currently expires 2027-01-13.
- Both files contain 4,415,493 rows and matching timestamps; zero duplicate and zero invalid OHLC rows detected. SHA-256 BID `b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc`; ASK `52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b`.
- This is **Dukascopy**, not the missing original HistData M1/spread data. Results must not be described as an exact R189 reproduction.

### Local replay result
- The locked R189/L80 historical replay and an additional intrabar-zero-trail execution sensitivity pass were executed locally in Python. Strategy thresholds were not optimized or changed.
- Result report: [R189 historical replay](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R189_DUKASCOPY_HISTORY_RESULTS.md).
- Machine-readable summary: [summary JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R189_Dukascopy_2016_2025_summary.json).
- Execution-sensitivity runner: [r189_execution_sensitivity.py](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/r189_execution_sensitivity.py).
- Intrabar sensitivity variant: all 2016–2025 = 1,673 trades, PF 1.248 at +0.5 pip extra cost and PF 1.082 at +1 pip. Discovery 2016–2020 PF 1.056 at +1 pip. Forward slice 2021–2025 = 767 trades, PF 1.284 at +0.5 and 1.114 at +1 pip. Forward annual PF at +1 pip includes 2022 = 0.976 and 2023 = 1.058. Four-week block bootstrap at +1 pip: probability of positive mean 94.72%, but its 95% interval for mean weekly PnL crosses zero: [-0.223, +2.489] pips.
- Holding time is incompatible with the current phone/manual workflow: median 2 minutes; 30.7% of exits are in the same M1 minute, 47.5% within one minute and 79.1% within five minutes. Manual alert/order latency was not modelled.
- **Verdict: NOT PASSED / not approved for the funded challenge.** It fails the project PF 1.10 robustness floor in the full sample at +1 pip (PF 1.082), in discovery (1.056), and in the weakest forward year (0.976). Bootstrap uncertainty includes zero; +2 pip stress is negative. Do not tune parameters to rescue it. It remains an unapproved research result, not a validated portfolio component or funded-ready strategy.
- Broker-specific commission, live slippage, manual execution delay, FundedNext DLL/MLL behavior and Quick Strike remain unverified.
- Note: the data artifact is an Actions artifact and expires on 2027-01-13. Save or reacquire it before then if the raw data is needed beyond that date.

### Current operating rule (reaffirmed)
Raw data collection may use GitHub Actions. All signals, PnL, robustness metrics and verdicts must run in local ChatGPT/container Python. GitHub is source/artifact storage, never the backtest compute engine. Do not use Massive. If a stored series is absent, proactively acquire raw data through the established source method and retain explicit feed provenance.


### R189 manual execution latency audit — 2026-10-16

- Local replay uses the official intrabar-aware execution model and unchanged R189/L80 signal parameters. No tuning was performed. The delay audit is stored here: [report](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R189_MANUAL_EXECUTION_DELAY_AUDIT.md) and [machine-readable JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R189_manual_execution_delay_audit.json).
- Delay means additional minutes after the ideal next-M1-open fill: +1/+3/+5 minutes (approximately 2/4/6 minutes from signal-bar close). Forward 2021–2025 with +0.5 pip extra cost: PF 1.284 at ideal fill, 1.225 at +1 minute, 1.212 at +3 minutes, and 1.071 at +5 minutes. With +1 pip extra cost: PF 1.114, 1.062, 1.048, and 0.926 respectively; the +5-minute result has net −203.0 pips.
- The PF 1.10 annual robustness floor is already breached in 2023 at only +1 minute delay (PF 0.973 at +0.5 pip extra cost); at +5 minutes three forward years fail the floor. At +1 pip extra cost, all latency settings have a weekly-bootstrap 95% interval crossing zero.
- **Verdict remains NOT PASSED for the user's several-minute manual-phone execution. Do not optimize R189 to fix the latency result.** Next research should use a separate candidate with a longer decision/holding horizon compatible with manual execution, and must pass its own forward/OOS and cost gates before portfolio combination.


### R262 — H4 structural pullback continuation: FAILED (local test, 2026-10-16)

- Preregistration: [R262 locked hypothesis](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R262_H4_STRUCTURE_PULLBACK_PREREGISTRATION.md)
- Report: [R262 results and decision](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R262_H4_STRUCTURE_PULLBACK_RESULTS.md)
- Machine-readable verdict: [R262 results JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R262_h4_structure_pullback_results.json)
- The candidate compared two non-overlapping five-active-H4-bar segments. Recent HH+HL or LH+LL structure plus two consecutive countertrend closes; swing stop from the last 3 completed H4 candles; target 1.5R; 48-hour time stop. Raw Dukascopy EURUSD M1 BID/ASK was used to build UTC H4 candles and simulate quote-side M1 execution. No parameter sweep or tuning.
- Data checks: 4,415,493 matched minute rows, 666,490 Sunday closed-market placeholder rows removed, 16,090 active H4 bars; 2,268 raw pattern candidates, 1,358 after 4-bar deduplication.
- Ideal entry: discovery 2016–2020 = 646 trades, PF 1.134 before extra cost but PF 0.979 at +1 pip; validation 2021 = 132 trades, PF 0.819 before extra cost; forward 2022–2025 = 503 trades, PF 0.815 before extra cost, 0.760 at +0.5 pip and 0.710 at +1 pip, with net -1,225.5 pips at +1 pip. All four forward years were negative at +1 pip (2022 PF 0.805; 2023 0.728; 2024 0.673; 2025 0.623).
- Four-week weekly-PnL bootstrap at +1 pip: mean -5.86 pips/week, 0.06% of 5,000 resamples positive, 95% interval [-9.24, -2.60] pips/week. The interval is wholly negative. Delayed-fill tests at +1/+3/+5 minutes remain negative.
- **Verdict: FAILED.** Do not run 2026 OOS because the historical forward gate failed; do not tune this setup. A different hypothesis is required. The code/results calculation was performed locally; GitHub Actions was not used for backtesting.


### R263 — U.S. cash-open opening-range breakout: FAILED (local test, 2026-10-16)

- Preregistration: [R263 locked rules](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R263_US_CASH_OPEN_ORB_PREREGISTRATION.md)
- Results: [R263 full report](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R263_US_CASH_OPEN_ORB_RESULTS.md)
- Machine-readable summary: [R263 JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R263_US_cash_open_ORB_results.json)
- Strategy: 09:30–10:00 New York opening range; first confirmed M5 close breakout 10:00–12:00; opposite range boundary stop; target 1.5R; close by 16:00 New York; one trade per index/day. USA500 and USATECH tested with same locked parameters. No tuning.
- Source is the already-retained GitHub BID-only M5 snapshot (USA500 886,206 rows; USATECH 886,039, to 2026-10-09). Since there is no ASK stream in these files, +2/+4/+6 basis-point transaction costs are fixed sensitivity assumptions, not measured execution costs. Metrics are return basis points per equal-notional trade and not FundedNext account drawdown percentages. All results were calculated in local Python; no GitHub Actions backtest ran.
- Ideal entry forward 2022–2025: 1,925 combined trades; PF 1.049 at +2 bps, 0.974 at +4 bps, 0.904 at +6 bps. At +4 bps net is -1,372 bps. USA500 PF 0.969 and USATECH 0.977 at +4 bps.
- Discovery 2016–2020 combined PF 0.885 at +2 bps and 0.811 at +4 bps; validation 2021 combined PF 0.911 at +2 and 0.831 at +4. Both fail before OOS.
- Five-minute entry delay forward combined: PF 1.065 at +2 bps, 0.988 at +4, 0.916 at +6. At +4 bps the forward bootstrap 95% intervals include zero both ideal [-35.79, +23.70] and delayed [-30.25, +25.08] bps/week. Annual PF at +4 bps is 1.105 (2022), 1.020 (2023), 0.854 (2024), 0.836 (2025).
- **Verdict: FAILED.** Primary +4 bps PF gate, per-index gate, discovery/validation gates, positive bootstrap-confidence gate, and latency gate fail. Per preregistration, do not inspect 2026 OOS and do not tune this setup.

Current active conclusion after R189, R262 and R263: no strategy is approved/funded-ready. The next candidate must be a materially different pre-registered hypothesis compatible with several-minute manual latency; keep testing costs and time delay from the outset.

### R264 — U.S. cash-open gap-fade to prior close: FAILED (local test, 2026-10-16)

- Preregistration: [R264 rules](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R264_US_CASH_OPEN_GAP_FADE_PREREGISTRATION.md)
- Report: [R264 results](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R264_US_CASH_OPEN_GAP_FADE_RESULTS.md)
- JSON: [R264 machine-readable results](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R264_US_cash_open_gap_fade_results.json)
- Strategy: >=25 bps opening gap; first M5 candle reverses relative to gap; enter at 09:35 ET or +5-min delayed 09:40; stop at opening candle extreme; target previous RTH close; require reward/risk >=1; no overnight; USA500 and USATECH, one trade per instrument/day.
- Historical data was from existing GitHub-stored BID-only M5 index artifacts, with signals/PnL locally calculated in Python. No ASK series is available, so +2/+4/+6 bps per trade are assumed cost sensitivities, not observed quoted costs.
- Ideal entry: discovery 2016–2020 combined 638 trades, PF 0.807 at +2 bps and 0.707 at +4; validation 2021 119 trades, PF 0.909 at +2 and 0.787 at +4; forward 2022–2025 533 trades, PF 1.075 at +2 and 0.953 at +4 (net -433.6 bps at +4).
- +5-min entry delay forward: 443 trades, combined PF 0.975 at +2, 0.863 at +4 and 0.769 at +6. Bootstrap 95% CI of weekly net returns at +4 crosses zero for ideal [-13.63, +10.25] bps/week and delayed [-16.21, +7.22]. Annual PF at +4 for ideal entry: 2022 1.156, 2023 0.932, 2024 0.809, 2025 0.786.
- **Verdict: FAILED.** Do not tune parameters and do not inspect 2026 OOS because the pre-registered gates did not pass.

Research sequence so far: R189 (M1, unfit for manual execution), R262 (H4 structural pullback, failed), R263 (US cash-open ORB, failed), R264 (US opening-gap fade, failed). None is approved for the funded challenge.

## 7. Putusan biner dan compounding — instruksi permanen (2026-10-16)

**Kebijakan wajib:** [RESEARCH_POLICY_BINARY_COMPOUNDING.md](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/RESEARCH_POLICY_BINARY_COMPOUNDING.md)

- Status setiap kandidat/percobaan hanya **LULUS** atau **GAGAL**. Tidak ada status pending atau kandidat yang dibiarkan tanpa keputusan. Jika data wajib atau eksekusi tidak bisa diverifikasi, percobaan untuk klaim itu GAGAL dengan alasan dan celah yang spesifik.
- Jangan terus mencari satu strategi tunggal. Uji arsitektur portofolio modular, interaksi sinyal, korelasi/overlap, shared risk controller, serta compounding fixed-fractional dengan ukuran posisi dihitung dari ekuitas terbaru.
- Menggabungkan strategi yang gagal tidak otomatis menciptakan edge. Setiap komposit harus mengunci komponen, bobot/risk budget, urutan sinyal, biaya, delay, aturan skip dan gate sebelum hitungan. Komposit yang dipilih setelah hasil komponen terlihat adalah diagnostik retrospektif; tidak dapat dipromosikan dari periode yang sama.
- **R268 — GAGAL:** [preregistration](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R268_COMPOUND_PORTFOLIO_PREREGISTRATION.md) · [report](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R268_COMPOUND_PORTFOLIO_RESULTS.md) · [JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R268_compound_portfolio_results.json) · [local runner](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/r268_compound_portfolio.py).
- R268 menggabungkan R262 EURUSD dan R263 USA500/USATECH memakai ledger delay 5 menit, biaya ekstra +1 pip FX dan +4 bps indeks, risiko 0,25% ekuitas per trade, dan batas risiko terbuka 1%.
- Forward 2022–2025: 2.399 trade, PF net R 0,823; compounding dari $6.000 berakhir pada $3.374,61 (−43,76%) dengan closed-equity drawdown 44,60%. Bootstrap mingguan 95% CI adalah −0,315% hingga −0,102%. Batas loss statis $5.400 pertama kali ditembus pada 2023-05-26 04:06 UTC; challenge replay akan gagal pada titik itu. Floating equity/DLL tidak direkonstruksi secara tick-by-tick.
- R268 bukan calon strategi LULUS; statusnya GAGAL dan komponen R262/R263 tetap ditutup. Jangan retune keduanya. Berikutnya hanya eksperimen baru dengan hipotesis dan/atau struktur risiko berbeda yang dipreregistrasikan, seluruh hitungan dijalankan lokal dan hasil disimpan ke GitHub.


- **R268 reproducibility status: GAGAL.** The local combined calculation used R262/R263 delayed trade-ledger CSVs that are not present as repository files; result JSON, report, and runner are saved, but this exact run is not self-contained from GitHub alone. Its local input hashes are documented in the report/JSON. Do not claim otherwise.


## R269 — London Asian-range sweep/reclaim — GAGAL (2026-10-16)

Active branch record: [full R269 checkpoint and research artifacts](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/PROJECT_STATE.md).

- [Preregristration](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R269_LONDON_ASIAN_SWEEP_PREREGISTRATION.md) · [runner](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/r269_london_asian_sweep.py) · [results](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R269_LONDON_ASIAN_SWEEP_RESULTS.md) · [compact JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R269_results_compact.json).
- EURUSD M1 BID/ASK from the raw-only GitHub artifact 11959096102 (run 38697080604); calculations were run locally. Feed: Dukascopy, 2016–2025. This is not exact reproduction of original HistData.
- At +1 pip extra cost: discovery PF 0.758/−73.48R (340 trades), 2021 validation PF 0.632/−19.31R (49), forward 2022–2025 PF 0.657/−78.91R (242). Forward four-week block bootstrap 95% CI for mean weekly net R: [−0.661, −0.078].
- Fixed fractional 0.25% per trade from $6,000 ended at $4,912.24 (−18.13%); realized-equity path crossed the $5,400 static floor on 2024-09-13 09:27 UTC. This is not tick-level funded replay.
- **Verdict GAGAL**. Candidate is closed; do not tune it on these dates. Continue from the active branch's failure taxonomy and use pre-registered, structurally justified tests rather than repeated lookalike parameter variations.


## R260–R269 family diagnosis

- [Failure taxonomy](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R260_R269_FAILURE_TAXONOMY.md).
- No candidate in R260–R269 passed all promotion gates. Frequency was not the core bottleneck across the family; negative expectancy, unstable periods and execution stress repeatedly failed.
- 2022–2025 has been inspected across multiple strategy families, so it must not be treated as an untouched final holdout for a new candidate. Next hypotheses must be structurally distinct, justified by a clear economic mechanism, pre-registered, and compatible with the five-minute execution delay.


## Correction: Compounding means strategy/edge composition first (2026-10-16)

- **Primary objective:** compose compatible setups, conditions and strategy modules into an integrated trade stream that improves risk-normalized PF and net expectancy compared with each component and a matched no-filter baseline. Do not interpret “compound compound” as only increasing position size with equity or as blindly unioning weak strategies.
- [Detailed correction and workflow](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/COMPOUNDING_OBJECTIVE_CORRECTION_20261016.md).
- R268 was a negative portfolio diagnostic from adding previously failed streams plus fixed-fractional sizing, not a successful strategy-compounding result. R269 returned to a standalone candidate and also missed the intended priority.
- Capital compounding is downstream: once an integrated stream has qualified, use fixed-fractional sizing to test dollar growth and funded-account survival. Position sizing alone does not create edge.
- Future composites must show incremental PF/expectancy, sample size, yearly stability, bootstrap, costs and the five-minute latency stress, and be frozen before independent validation. The repeatedly inspected 2022–2025 period is not a clean untouched holdout.


## Latest authoritative objective — funded target completion (2026-10-16)

**The project's objective is to reach the actual funded-challenge targets as quickly as realistically possible while controlling the probability of daily/max-loss breach. PF is a diagnostic only, not the objective.** This supersedes earlier wording that made PF >=1.10 or PF improvement a primary target.

- [Authoritative objective, simulator requirements, and scorecard](research/PRIMARY_OBJECTIVE_FUNDED_TARGET_COMPLETION_20261016.md).
- [Corrected binary/compounding policy](research/RESEARCH_POLICY_BINARY_COMPOUNDING.md).
- The current reference challenge is the $6k Stellar 2-Step model: +8% Phase 1 then +5% Phase 2, with applicable loss limits and provider rules. Research remains simulation-only until age eligibility.
- “Compound” means assembling and coordinating multiple compatible opportunities/contexts/strategy streams so the combined system can reach targets with a stronger probability/time profile; it does not mean merely raising lot size with equity or blindly unioning failing strategies.
- Primary scorecard: probability of hitting each phase target before loss-rule breach, probability of completing both phases, median/upper-quantile time to target, risk/breach probability, opportunity frequency under 5-minute execution delay, cost robustness and inter-module overlap/correlation.
- PF, expectancy, win rate, frequency and drawdown remain diagnostics that explain why a portfolio succeeds/fails. Do not select the system solely for highest PF. Do not promote a high-risk lottery on the basis of occasional target hits; quantify repeated-path success and breach distributions.
- Fixed-fractional capital compounding is part of the challenge path simulation after the integrated opportunity stream is defined; it is not the project's end goal.



## Latest research update — R270 GAGAL (2026-10-16)

Active research branch: [local-backtest/r189-dukascopy-history](https://github.com/christianomomongan82-lang/scanner/tree/local-backtest/r189-dukascopy-history). R270 preregistration, results report, compact JSON and full checkpoint are on that branch:
- [R270 preregistration](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R270_SESSION_REGIME_ROUTER_PREREGISTRATION.md)
- [R270 result report](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R270_SESSION_REGIME_ROUTER_RESULTS.md)
- [R270 compact JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R270_results_compact.json)

R270 used EURUSD M1 BID/ASK from raw-only GitHub artifact 11959096102 (Dukascopy, 2016–2025; SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`) and was calculated locally, not in GitHub Actions. Module A produced zero trades (observed max Asia ER 0.2101 against a locked minimum 0.30), so the router collapsed to Module B. At +1 pip extra cost, B/router generated 290 discovery trades PF 0.712/-65.97R, 68 validation trades PF 0.639/-20.16R, and 219 forward diagnostic trades PF 0.628/-63.50R; every forward year was negative. Four-week bootstrap mean was -0.304R/week (95% CI [-0.484, -0.115]). Challenge-path proxy did not improve the two-phase completion profile without higher breach risk. **R270 = GAGAL; no retuning.** 2022–2025 is not an untouched holdout, 2026 is absent, and the official funded engine is not fully verified. Full local row-level ledger/runner had not yet been committed at this checkpoint update; do not claim GitHub-only reproducibility until stored.


## Latest research update — R271 daily 20-session breakout — GAGAL (2026-10-16)

Active research branch: [local-backtest/r189-dukascopy-history](https://github.com/christianomomongan82-lang/scanner/tree/local-backtest/r189-dukascopy-history).

- [Preregistration](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R271_DAILY_TREND_BREAKOUT_PREREGISTRATION.md)
- [Result report](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R271_DAILY_TREND_BREAKOUT_RESULTS.md)
- [Local runner](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/r271_daily_trend_breakout.py)
- [Compact results JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R271_results_compact.json)
- [Timestamped compact trade ledger](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R271_trade_ledger_compact.csv)
- [Full active-branch checkpoint](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/PROJECT_STATE.md)

R271 was preregistered before calculation and tested locally on EURUSD M1 Dukascopy BID/ASK from raw-data artifact 11959096102 (run 38697080604; ZIP SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`). No GitHub Actions backtest was run. The locked daily 20-session close-confirmed breakout produced 126 closed trades. At +1 pip extra cost, discovery 2016–2020 was 57 trades / PF 0.811 / −4.949R, validation 2021 was 14 / PF 0.769 / −1.437R, and diagnostic forward 2022–2025 was 55 / PF 0.808 / −4.265R. The forward stream was negative even with zero additional cost (−3.892R); the 4-week bootstrap CI crossed zero; only 1 of 4 forward years was positive. All preregistered gates failed. The low 2021 trade count also failed the minimum sample gate. **R271 = GAGAL; no parameter rescue and no challenge replay was run because the underlying stream was net-negative.** Historical 2022–2025 is contaminated and the input archive has no 2026+, so it cannot be treated as fresh promotion-grade OOS evidence.

Next research must remain structurally distinct, registered before outcome calculation, and focused on the probability/time profile of completing both funded targets without breach. PF is diagnostic only; higher risk cannot compensate for negative expectancy. If the local runner or full raw-data archive is not available in a future runtime, retrieve the referenced GitHub artifacts/source first and do not claim self-contained reproduction solely from the rounded compact trade ledger.


## Funded-readiness gate and official rules — 2026-10-16

- [Current official Stellar 2-Step rule matrix](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/FUNDEDNEXT_STELLAR2_RULES_VERIFIED_20261016.md)
- [Mandatory funded-readiness promotion gate](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/FUNDED_READINESS_GATE_20261016.md)
- [Full active-branch checkpoint](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/PROJECT_STATE.md)

Official rule details verified on 2026-10-16: Stellar 2-Step targets +8% then +5%; DLL 5%, static MLL 10%, five separate trading days per phase, no time limit, Quick Strike strictly below 30%; daily loss must include current-day closed P&L plus all open floating P&L, charges, commissions and swaps; the server clock uses seasonal GMT+2/GMT+3. FundedNext's current public help center requires age 18+. Future promotion to funded-ready must use a rule-aware replay, not the older simplified challenge proxies. R270 and R271 remain GAGAL; no tuning or promotion based on repeatedly inspected 2022–2025.


## R272 — Gold dual-module test / corrected data acquisition (2026-10-16)

**Strategy verdict: not calculated yet.** Do not infer LULUS or GAGAL from downloader state. No R272 signal/PnL/backtest results have been calculated or inspected in this continuation.

- Locked hypothesis: XAUUSD M5, 12-hour trend-pullback continuation (A) routed in persistent regimes and failed-excursion reversal (B) routed in balanced regimes; five-minute manual execution delay after the signal candle closes; side-correct BID/ASK fills; force-flat by 16:45 New York; primary added cost $0.30/oz; preregistered historical and one-time 2026 gates.
- [Preregistration and its pre-result timing amendment](research/R272_XAUUSD_DUAL_MODULE_PREREGISTRATION.md)
- [Local-only runner](research/r272_xauusd_dual_module.py)
- [Verified FundedNext Stellar 2-Step rule matrix](research/FUNDEDNEXT_STELLAR2_RULES_VERIFIED_20261016.md) · [funded-readiness gate](research/FUNDED_READINESS_GATE_20261016.md)
- **Runner corrected before results:** since Dukascopy timestamps are bar-open times, a decision at signal-bar close T+5m plus a five-minute execution delay requires entry at T+10m (index t+2), not the next bar open at T+5m. The runner now enforces both five-minute intervals, records realized delay, and corrects exact 16:45 cutoff gap fills. Empty-month metrics also have a stable JSON-safe schema.
- Local syntax and synthetic functional checks pass: expected entry delay = 5 minutes after signal close; normal target fill, target/stop gap at the 16:45 cutoff, and rejection of a broken intervening bar were verified. This is engine testing only, not strategy performance evidence.
- Data integrity issue found before backtest: the January probe artifact [run 38857759446](https://github.com/christianomomongan82-lang/scanner/actions/runs/38857759446) reports Include flats: true. That setting may create flat bars across closed sessions, violating the preregistered no-synthetic-bars rule. Do not use that probe or the original full acquisition [run 38857936371](https://github.com/christianomomongan82-lang/scanner/actions/runs/38857936371) as valid input.
- The data-only collector has been corrected to omit the -fl flag and record include_synthetic_flat_bars: false; the workflow concurrency group was separated so a corrected raw-data run can start. Corrected data-only run: [38859918137](https://github.com/christianomomongan82-lang/scanner/actions/runs/38859918137) (queued at checkpoint time). It may download/package raw BID/ASK only; no feature, signal, PnL or backtest calculations in Actions.
- Raw-data branch: [data/r272-xauusd-m5-2016-2026](https://github.com/christianomomongan82-lang/scanner/tree/data/r272-xauusd-m5-2016-2026). Data must pass local timestamp/side integrity checks before any results are accepted.
- Only calculate discovery 2016–2020 and historical validation 2021–2025 first. Do not open the 2026-01-01 to 2026-10-15 holdout unless every locked historical gate passes. Funded-ready is a separate decision requiring the equity-aware two-phase rule replay; a positive signal screen is not sufficient.
