# Proyek Backtest — Checkpoint Utama

**Terakhir diperbarui:** 2026-10-15  
**Status proyek:** BELUM ADA STRATEGI FINAL YANG LULUS  
**Repositori sumber utama:** https://github.com/christianomomongan82-lang/scanner  
**Branch riset aktif saat checkpoint ini:** [r251-fx-cross-pair-lead-lag](https://github.com/christianomomongan82-lang/scanner/tree/r251-fx-cross-pair-lead-lag)

Dokumen ini adalah titik lanjut permanen. Percakapan baru yang menerima instruksi “lanjut” harus membaca dokumen ini terlebih dahulu, lalu memeriksa artefak riset terbaru di branch aktif dan memperbarui checkpoint setelah ada hasil penting. Jangan meminta pengguna membuat prompt khusus atau mengunggah ulang data yang sudah ada di GitHub.

## 1. Protokol penyimpanan dan kelanjutan

- GitHub adalah sumber kebenaran untuk keputusan, kode, konfigurasi, data hasil, laporan, ledger transaksi, dan metadata eksperimen mulai sekarang.
- Jangan membuat file unduhan terpisah untuk pengguna. Simpan hasil langsung ke repositori; file baru hanya dibuat di GitHub sebagai bagian dari pekerjaan riset.
- Setiap backtest harus punya skrip, parameter yang dikunci, sumber/periode data, aturan eksekusi, hasil mesin yang dapat dibaca, laporan final, dan ledger jika ada transaksi.
- Jika data mentah atau artefak belum tersimpan/versioned di repo, jangan mengklaim hasilnya sepenuhnya dapat direproduksi. Catat celahnya, checksum, dan lokasi artefak yang benar-benar tersedia.
- Setelah setiap eksperimen, simpan putusan biner **LULUS** atau **GAGAL** beserta alasan dan tautan artefak. Dilarang mengubah parameter setelah melihat hasil forward/OOS lalu melaporkan hasil yang diubah sebagai tes terkunci.
- Jika koneksi GitHub tidak tersedia di obrolan baru, jelaskan hambatannya; jangan berpura-pura mengetahui perubahan terbaru.
- Branch `main` menyimpan checkpoint ini. Branch riset aktif yang disebutkan di atas menyimpan artefak R251–R258. Jangan menganggap semua berkas di branch riset sudah berada di `main`.

## 2. Tujuan proyek

Mencari strategi forex yang mempunyai edge terukur dan dapat dieksekusi secara realistis, lalu menggunakan kombinasi strategi yang terbukti untuk meluluskan challenge funded secepat mungkin tanpa merusak akun. Setelah lolos, tujuan lanjutannya adalah pendapatan yang realistis dari akun simulasi $6.000.

Jangan mengembalikan target lama “2× UMK” atau asumsi lama FundedNext Futures tanpa konfirmasi baru. Simulasi Stellar 2-Step yang pernah dipakai (target 8% lalu 5%, DLL 5%, MLL 10%) hanyalah parameter historis dan belum merupakan verifikasi aturan live yang lengkap. Jangan menyarankan membeli challenge sebagai langkah sekarang.

Preferensi strategi: gunakan price action/statistik mentah; indikator klasik EMA/RSI/MACD/Bollinger tidak dipakai kecuali pengguna mengubah batasan. Ambang target yang pernah ditetapkan adalah PF minimal 1,10 pada kondisi stress terburuk yang diwajibkan; gate lengkap harus ditulis sebelum setiap eksperimen.

## 3. Perubahan arah strategis — 2026-10-15

**Keputusan terbaru: jangan memaksa satu strategi untuk sekaligus memenuhi semua kebutuhan** (expectancy tinggi, banyak sinyal, drawdown kecil, tahan di beragam kondisi, dan cepat lulus challenge).

Gunakan arsitektur modular, tetapi belum harus menjalankan beberapa strategi sekaligus:

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

Aturan terkunci: momentum absolut 24 jam melewati persentil ke-65 yang dihitung hanya dari 2017–2020 dan searah dengan momentum 120 jam; entry pada open H1 berikutnya; stop = 0,5 × rentang high-low 24 jam sebelumnya; TP = 2R; maksimal holding 24 jam; eksekusi menggunakan sisi BID/ASK yang sesuai. Missing hourly bars tidak diisi dengan bar sintetis.

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

Jangan berasumsi penyebab kegagalannya sama. Ekstrak bukti per eksperimen untuk membuat taksonomi kegagalan kumulatif sebelum memilih jalur strategi berikutnya.

### R189 — prioritas audit, BELUM FINAL

- [GitHub Actions run OOS 2026](https://github.com/christianomomongan82-lang/scanner/actions/runs/38439056132)
- [Hasil OOS 2026](https://github.com/christianomomongan82-lang/scanner/blob/r189-oos-2026-test/research/r189_oos_2026_results.json)

Pemeriksaan independen EURUSD M1 2026-01-01 sampai 2026-10-12: 55 trade, PF 1,484 setelah biaya tambahan 0,2 pip, net +78,1 pip, mean +1,42 pip/trade, max drawdown 24,8 pip, sekitar 1,35 trade/minggu (~5,9/bulan). Ini terlihat menjanjikan, tetapi ukuran sampel masih kecil dan frekuensinya rendah. Cost stress PF: biaya tambahan 0 pip = 1,571; +0,5 pip = 1,365; +0,8 pip = 1,255; +1 pip = 1,187; +2 pip = 0,900.

Pengaturan terkunci yang diuji: displacement 15 pip, late ratio ≥0,8, body ≥2 pip, directional consistency ≥7 dalam tiap window 11/12 bar, sesi 03:00–11:59 fixed GMT−5 dengan jam 06 dan 09 dikecualikan, dedup 14 bar, ceiling spread entry 1,5 pip, SL 6 pip, TP 18 pip, MFE trigger 6 pip, trailing distance 0, time stop 60 menit. Biaya mencakup BID/ASK aktual +0,2 pip tambahan.

Metrik sejarah R189 yang pernah dikutip (2016–2025: 1.840 trade, PF 1,328; forward 2021–2025: PF 1,358) **belum direproduksi secara independen** dan tidak boleh digabungkan begitu saja dengan validasi OOS 2026. Jangan menetapkan R189 LULUS sebelum reproduksi historis dan audit implementasi selesai.

## 5. Celah yang belum selesai

- Reproduksi penuh hasil historis R189 masih belum selesai.
- Komisi broker/funded aktual, slippage live, pemetaan timezone platform, urutan intrabar saat SL/TP tersentuh di candle sama, serta aturan DLL/MLL yang benar-benar berlaku belum seluruhnya diverifikasi.
- Challenge replay R258 belum setara dengan engine funded yang sebenarnya.
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

### R189 — hambatan data belum terselesaikan
- Laporan historis R189 masih belum bisa direproduksi: GitHub repo/artefak yang tersedia belum memiliki arsip EURUSD M1 2016–2025 asli, file spread aslinya, atau ledger historisnya. Artefak EURUSD H1 yang tersedia tidak kompatibel untuk menguji ulang aturan R189 M1.
- OOS 2026 R189 tetap bukti terpisah, bukan pengganti data historis tersebut.
- Jangan jalankan backtest R189 atas H1 atau menyebut data eksternal baru sebagai “data dari GitHub”. Cari artefak/data M1 yang benar-benar tersimpan di GitHub terlebih dahulu. Jika tidak ada, tandai reproduksi sebagai blocked sampai input tersedia.

### Insiden R259 — workflow tak sengaja dibuat dan dijalankan
- Run [38623417685](https://github.com/christianomomongan82-lang/scanner/actions/runs/38623417685) sempat selesai setelah gue keliru mengirim eksperimen ke GitHub Actions. File workflow pemicu sudah dihapus dari branch `r259-r189-dukascopy-history` agar tidak membuat trigger berikutnya.
- Jangan menganggap output R259 sebagai hasil riset resmi; ia tidak mengikuti metode eksekusi yang disepakati (local backtest memakai data dari GitHub). Insiden ini dicatat untuk transparansi, bukan sebagai eksperimen yang diterima.
- Mulai sekarang tidak membuat workflow GitHub Actions untuk backtesting.

### Langkah berikutnya
1. Pertahankan R260 sebagai GAGAL; jangan ubah threshold/SL/TP untuk menyelamatkannya.
2. Cari di GitHub artefak yang benar-benar menyimpan EURUSD M1 historis yang cocok untuk R189; jika tidak tersedia, lanjutkan riset lokal pada hipotesis baru dengan dataset H1 GitHub yang tersedia, preregistrasikan dulu, dan simpan verdict biner.
3. Tetap pisahkan kualitas edge, frekuensi, dan kontrol risiko. Tidak ada strategi final yang lulus dan belum ada strategi yang terbukti funded-ready.

**Kesimpulan status:** belum ada strategi final yang lulus. R258 dan R260 GAGAL. R189 tetap belum terverifikasi untuk periode historis karena data M1 asli belum ditemukan. Eksekusi backtest selanjutnya dilakukan di sini; GitHub hanya sumber data/artefak dan penyimpanan.

## Koreksi permanen alur data — 2026-10-15

- Saat data yang dibutuhkan belum tersedia secara lokal, **cari dan unduh sendiri dari file/artefak GitHub yang sudah ada** sebelum meminta apa pun kepada pengguna.
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
