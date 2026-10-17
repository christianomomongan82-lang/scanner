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

## 3. Perubahan arah strategis — 2026-10-16

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

### R189 — GAGAL UNTUK PROMOSI; audit historis dan eksekusi

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


## Research continuation — R265 audit and R266 result (2026-10-16)

### R265 — USA500/USATECH relative-value mean reversion: FAILED / EXPLORATORY ONLY
- [Retrospective audit](research/R265_EXPLORATORY_AUDIT.md)
- [Machine-readable audit](research/R265_relative_value_audit.json)
- [Runner](research/r265_relative_value.py)
- [Ideal-entry ledger](research/ledgers/R265_trades_ideal.csv.gz)
- [Five-minute delayed ledger](research/ledgers/R265_trades_delay5.csv.gz)
- Forward 2022–2025 contains 41 trades only, below the 100-trade minimum. PF at +4 bps was 1.395 ideal and 1.313 delayed, but four-week block bootstrap 95% intervals crossed zero. No contemporaneous preregistration was found in the repo before audit, and the aggregate output included available data into 2026, so it is not clean OOS evidence. Treat as retrospective exploratory output only; do not tune or promote.

### R266 — U.S. index afternoon continuation after a strong morning: FAILED
- [Preregistration / locked hypothesis](research/R266_INTRADAY_DRIFT_PREREGISTRATION.md)
- [Final report](research/R266_INTRADAY_DRIFT_RESULTS.md)
- [Machine-readable results and gate ledger](research/R266_intraday_drift_results.json)
- [Local Python runner](research/r266_intraday_drift.py)
- [Ideal-entry trade ledger](research/ledgers/R266_trade_ledger_tiny_ideal.csv.gz)
- [Five-minute delayed trade ledger](research/ledgers/R266_trade_ledger_tiny_delay5.csv.gz)
- GitHub source inputs: R205 artifact BID-only M5 snapshots for USA500 and USATECH. Data hashes recorded in result JSON. Calculations executed locally; no backtest GitHub Actions workflow was run. 2026 outcomes were not inspected.
- At +4 bps, ideal discovery 2016–2020 PF 0.934 and net −1,213.5 bps; validation 2021 PF 0.557 and net −1,846.1 bps; forward 2022–2025 PF 1.145 and +2,343.1 bps over 725 trades. The +5-minute entry mode has the same 725 forward trades, PF 1.102 and +1,638.3 bps.
- Both entry modes failed because discovery and validation were negative, years 2023 and 2024 had negative PnL, and the 4-week block-bootstrap 95% weekly-PnL intervals included zero. Do not tune parameters and do not inspect 2026 to rescue the failed hypothesis.

### Status after R266
- **All currently evaluated strategies are GAGAL for funded approval.** R189 historical reproduction is GAGAL because the exact required history inputs are absent; funded-readiness is GAGAL on execution constraints; R260–R266 must not be treated as approved strategy candidates.
- Next experiment must be a structurally different, pre-registered hypothesis; keep the five-minute delay and cost sensitivity in the primary test. Run calculations in local Python, retrieve inputs only from GitHub, do not start GitHub Actions for backtesting, and record a binary verdict. If a pre-registered gate fails, stop that candidate without retuning.


### R267 — Last-hour momentum into next RTH open: EXPLORATORY PILOT FAILED
- [Retrospective pilot report](research/R267_LAST_HOUR_OVERNIGHT_PILOT.md)
- [Machine-readable summary](research/R267_last_hour_overnight_pilot.json)
- [Local replay runner](research/r267_last_hour_to_overnight.py)
- Important research-integrity caveat: this calculation was run before a contemporaneous preregistration was committed to GitHub. It is archived as an exploratory pilot only; do not call it preregistered and do not use it to promote a candidate.
- Rules: at 15:00 ET, follow the 14:00-open to 14:55-close M5 return in USA500/USATECH; enter 15:00 or 15:05 for latency stress; exit at the next complete RTH 09:30 ET open. BID-only inputs; modeled costs +2/+4/+6 bps are assumptions. Entry and exit dates were capped before 2026-01-01, and 2026 outcomes were not inspected.
- At +4 bps, ideal forward 2022–2025: 1,986 trades, PF 0.878, net −7,469.5 bps. Delayed forward: PF 0.857, net −8,762.0 bps. Four-week block-bootstrap 95% intervals for weekly net bps include zero (ideal −80.65 to +8.70; delayed −85.98 to +1.35). Discovery negative; most annual cohorts negative; both indices negative. Exploratory candidate FAILED.
- R267 compact trade ledgers are regenerable via the runner, but the published pilot summary does not include the verbose raw JSON output. The full locally produced JSON is not committed; use the compact summary for its approved interpretation.

### Research process priority after R267
- Do not immediately invent or optimize another signal just to make a new round number. A large family of prior range breakouts, reversals, momentum and relative-value ideas have already failed; repeated similar experiments add selection bias.
- Recommended next work item is an execution/reproducibility audit of existing R189 historical replay and signal/exit mechanics, plus explicit separation of verified facts versus feed-specific replication. It must not be described as a fresh preregistered performance test. No candidate is approved or funded-ready.


### R189/L80 — execution-delay audit (2026-10-16)
- [Execution-delay audit report](research/R189_EXECUTION_DELAY_AUDIT.md)
- [Machine-readable delay summary](research/R189_execution_delay_audit.json)
- This is a retrospective audit of an already-run Dukascopy M1 BID/ASK replay, not an exact reproduction of the original HistData results and not a fresh preregistered strategy test.
- Intrabar-aware stress results, forward 2021–2025: at +0.5 pip additional cost, PF declines from 1.284 at ideal fill to 1.071 after +5 minutes; at +1.0 pip, PF declines from 1.114 to 0.926 and net becomes −203 pips. The +5-minute bootstrap intervals include zero at both costs. This matters for phone/email execution latency.
- The delay-stress ledger checks spread at the actual delayed entry bar; M1 candles model gaps through stops/targets and stop-before-target ordering but cannot verify tick-level closing duration.
- R189 berstatus GAGAL untuk funded-readiness: pemetaan GMT-5 ke server/DST, biaya live, Quick Strike sub-30-detik, serta DLL/MLL tidak memenuhi gate bukti.
- No retuning or parameter selection from this audit. Keep R189 rules locked while verifying mapping and execution constraints.


### FundedNext eligibility and rule audit (official pages checked 2026-10-16)
- [Current Stellar 2-Step rule audit](research/FUNDEDNEXT_STELLAR2_RULE_AUDIT_20261016.md)
- Official page currently lists $6,000 Stellar 2-Step at approximately $59.99, targets 8% then 5%, DLL 5%, MLL 10%, five trading days per phase by default, and no phase time limit. A “No Minimum Trading Days” add-on is listed for $6k/$15k/$25k, but its cost must be checked at checkout; do not assume it is cheaper without the final price.
- Critical eligibility constraint: FundedNext's official age FAQ requires age 18+. Based on the registered birth date (2008-12-25), purchase/KYC must wait until 2026-12-25. Until then, research only.
- Official inactivity policy changed/clarified to **30 consecutive calendar days without a trade**, not 60.
- Quick Strike is not the share of trades; it is the share of total recorded profit generated by profitable trades closed within 30 seconds. 20% warning; 30% or above pauses challenge progression until the ratio drops below 30%.
- FundedNext official help center specifies seasonal server time GMT+2 / GMT+3. Actual login/platform mapping still has to be verified.
- R189 remains NOT FUNDED-READY because the +5-minute stress results weaken sharply and still lack live cost distribution, actual platform timezone/DST mapping and Quick Strike / DLL / MLL validation.


## 7. Putusan biner dan compounding — instruksi permanen 2026-10-16

- Status hasil hanya **LULUS** atau **GAGAL**. Tidak ada kategori pending, status nonbiner, atau kandidat yang dibiarkan tanpa putusan. Bila suatu klaim gagal karena data/implementasi/bukti tidak tersedia, percobaan untuk klaim itu dicatat GAGAL dengan alasan spesifik.
- [Kebijakan riset biner, portofolio modular, dan compounding](research/RESEARCH_POLICY_BINARY_COMPOUNDING.md).
- Jangan terus berburu satu strategi tunggal. Riset harus mencakup strategi modular, portfolio replay, korelasi/overlap, shared risk controller dan compounding fractional-risk berdasarkan ekuitas terbaru. Namun, menggabungkan strategi gagal tidak otomatis menciptakan edge; hasil komposit wajib diuji sebagai satu sistem.
- Compounding dan challenge replay harus menunjukkan trade R, equity curve dalam dolar, daily/max loss, serta peringatan bahwa closed-equity saja tidak menangkap floating DD. Risiko per entry dan cap portfolio dikunci sebelum kalkulasi.
- **R268 — GAGAL:** [preregistration](research/R268_COMPOUND_PORTFOLIO_PREREGISTRATION.md) · [report](research/R268_COMPOUND_PORTFOLIO_RESULTS.md) · [JSON](research/R268_compound_portfolio_results.json) · [runner](research/r268_compound_portfolio.py).
- R268 menggabungkan R262 EURUSD dan R263 indeks memakai ledger delay 5 menit, biaya tambahan +1 pip FX dan +4 bps indeks, risiko 0,25% ekuitas per trade, batas open risk 1%. Forward 2022–2025: 2.399 trade, PF net R 0,823, equity referensi $6.000 menjadi $3.374,61 (−43,76%), closed-equity DD 44,60%. Batas MLL nominal $5.400 pertama kali dilewati di 2023-05-26 04:06 UTC; simulasi akan gagal pada titik itu. Ini diagnostik retrospektif, bukan estimasi peluang lulus funded.
- R268 membuktikan bahwa gabungan dua modul ini **GAGAL**; jangan retune komponen lama untuk menyelamatkannya. Untuk kandidat baru, praregistrasikan aturan dan gate, lalu uji komposit serta compounding lokal. Hasil yang tidak memenuhi satu gate pun = GAGAL.


- **R268 reproducibility status: GAGAL.** The local combined calculation used R262/R263 delayed trade-ledger CSVs that are not present as repository files; result JSON, report, and runner are saved, but this exact run is not self-contained from GitHub alone. Its local input hashes are documented in the report/JSON. Do not claim otherwise.


## R269 — London Asian-range sweep/reclaim reversal — GAGAL (2026-10-16)

- [Preregistration](research/R269_LONDON_ASIAN_SWEEP_PREREGISTRATION.md)
- [Runner](research/r269_london_asian_sweep.py)
- [Results report](research/R269_LONDON_ASIAN_SWEEP_RESULTS.md)
- [Machine-readable compact results](research/R269_results_compact.json)
- Raw-data collection only: [GitHub run 38697080604](https://github.com/christianomomongan82-lang/scanner/actions/runs/38697080604), artifact ID 11959096102. All signal/PnL calculations were run in local Python, not Actions.
- Data: Dukascopy EURUSD M1 BID/ASK 2016–2025, 4,415,493 rows per side, identical common timestamps, zero duplicates/invalid OHLC/negative open spreads. ZIP SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- Locked strategy: London-local Asian range 00:00–07:59, sweep/reclaim signal 08:00–11:59; only first setup per day; entry six minutes after signal-bar timestamp (five minutes after close/decision); ASK long/BID short; SL past signal extreme by 1 pip, target Asian midpoint, minimum 1R reward/risk; 240-minute time stop; stop-first intrabar ambiguity; +1 pip primary extra-cost stress.
- Discovery 2016–2020: 340 trades, PF 0.758, −73.48R at +1 pip. Validation 2021: 49 trades, PF 0.632, −19.31R. Forward 2022–2025: 242 trades, PF 0.657, −78.91R. Forward bootstrap 95% interval for mean weekly net R: [−0.661, −0.078]. Compounding 0.25% risk from $6,000 ended at $4,912.24; closed equity first crossed $5,400 on 2024-09-13 09:27 UTC.
- All seven economic gates failed. Do not retune this candidate on the same data. This is an independent Dukascopy feed replay, not an exact reproduction of the missing original HistData R189 archive. The closed-equity replay does not establish funded readiness.
- Reproducibility note: the detailed trade ledger and annual tables are currently available in the local run output but the repository contains the runner, JSON summary, report and raw-data artifact reference; do not claim the row-level R269 ledger is stored in GitHub until a corresponding ledger file is committed.
- R269 is closed. Choose any later candidate using a structurally independent hypothesis and a preregistration before results; no R269 parameter rescue.


## Family-level research review — R260–R269

- [Failure taxonomy and next-stage decision](research/R260_R269_FAILURE_TAXONOMY.md).
- R260–R269 contained no candidate that passed the full gates. High trade count did not repair negative expectancy; retrospective/forward-only PF must not be promoted if discovery, validation, bootstrap or annual stability fails.
- The 2022–2025 period has been repeatedly inspected across candidate families and should not be called an untouched final holdout. New candidates need an explicit economic rationale, a horizon compatible with five-minute latency, and a genuinely independent/untouched validation window for promotion.
- Do not produce near-duplicate M1 reversal, intraday momentum, US cash-open ORB, or H4 pullback tests by changing thresholds. Any failed locked candidate remains GAGAL and closed.


## Critical correction — intended compounding objective (2026-10-16)

The user's “compound compound” instruction was not satisfied by increasing position size with equity alone. **First priority is strategy/edge composition that improves the risk-normalized PF and net expectancy of the integrated trade stream.** Capital compounding is downstream, after that integrated stream qualifies.

- [Full correction and required workflow](research/COMPOUNDING_OBJECTIVE_CORRECTION_20261016.md).
- [Updated binary/compounding policy](research/RESEARCH_POLICY_BINARY_COMPOUNDING.md).
- R268 merely unioned previously failed streams and applied fixed-fractional equity sizing; it was a negative portfolio diagnostic, not a successful strategy-compounding build.
- R269 was another standalone strategy test and therefore also failed to implement the requested research priority, independent of its own economic GAGAL result.
- Future candidates must compare integrated signal logic against each component and a no-filter baseline on identical timestamps/costs; show PF/expectancy lift without destroying useful frequency or robustness. Fixed-fractional sizing comes after this.
- 2022–2025 is repeatedly inspected and cannot be treated as an untouched final holdout. Do not tune old failed candidates to rescue them.


## Latest authoritative objective — funded target completion (2026-10-16)

**The project's objective is to reach the actual funded-challenge targets as quickly as realistically possible while controlling the probability of daily/max-loss breach. PF is a diagnostic only, not the objective.** This supersedes earlier wording that made PF >=1.10 or PF improvement a primary target.

- [Authoritative objective, simulator requirements, and scorecard](research/PRIMARY_OBJECTIVE_FUNDED_TARGET_COMPLETION_20261016.md).
- [Corrected binary/compounding policy](research/RESEARCH_POLICY_BINARY_COMPOUNDING.md).
- The current reference challenge is the $6k Stellar 2-Step model: +8% Phase 1 then +5% Phase 2, with applicable loss limits and provider rules. Research remains simulation-only until age eligibility.
- “Compound” means assembling and coordinating multiple compatible opportunities/contexts/strategy streams so the combined system can reach targets with a stronger probability/time profile; it does not mean merely raising lot size with equity or blindly unioning failing strategies.
- Primary scorecard: probability of hitting each phase target before loss-rule breach, probability of completing both phases, median/upper-quantile time to target, risk/breach probability, opportunity frequency under 5-minute execution delay, cost robustness and inter-module overlap/correlation.
- PF, expectancy, win rate, frequency and drawdown remain diagnostics that explain why a portfolio succeeds/fails. Do not select the system solely for highest PF. Do not promote a high-risk lottery on the basis of occasional target hits; quantify repeated-path success and breach distributions.
- Fixed-fractional capital compounding is part of the challenge path simulation after the integrated opportunity stream is defined; it is not the project's end goal.



## R270 — Asia-session regime router — GAGAL (2026-10-16)

- [Preregistration](research/R270_SESSION_REGIME_ROUTER_PREREGISTRATION.md) · [results report](research/R270_SESSION_REGIME_ROUTER_RESULTS.md) · [compact JSON](research/R270_results_compact.json).
- Input: EURUSD M1 BID/ASK Dukascopy raw-only GitHub artifact 11959096102 (data-only run 38697080604), ZIP SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`; local Python calculations, no backtest Actions run.
- Locked router: Module A continuation only if Asia ER >=0.30 plus close-in-edge direction; Module B fade in low-ER balanced sessions; five-minute entry delay; BID/ASK execution; +1 pip primary cost.
- Diagnostic: across 2,605 eligible London weekdays, maximum observed ER was 0.2101, so Module A never fired. Module B produced 577 trades; router is exactly identical to B, not a true combined stream.
- At +1 additional pip, B/router: discovery 2016–2020 290 trades, PF 0.712, -65.97R; 2021 68 trades, PF 0.639, -20.16R; forward 2022–2025 219 trades, PF 0.628, -63.50R. All four forward years were negative. Four-week bootstrap average net was -0.304R/week, 95% CI [-0.484, -0.115]. Even with 0 added pips beyond observed quotes, discovery/validation/forward net R was -14.14/-5.96/-30.99.
- Challenge reference proxy, not funded-equivalent: router both-phase completion was 0% at 0.25–0.50% risk, 0.4% at 0.75%, and 1.1% at 1.00%, while proxy loss-rule breach rose from 28.1% to 97.9%. Higher risk is not a credible rescue.
- **Verdict: GAGAL.** The economic/coverage gates failed; 2022–2025 is not independent, 2026 is absent, and official funded implementation/rules remain unverified. Do not retune R270. At checkpoint time, full runner and row-level ledger are preserved locally but have not yet been committed to this branch; do not claim full GitHub-only reproducibility until those files are stored.


## R271 — Daily 20-session breakout continuation — GAGAL (2026-10-16)

- Pre-registration: [R271_DAILY_TREND_BREAKOUT_PREREGISTRATION.md](research/R271_DAILY_TREND_BREAKOUT_PREREGISTRATION.md)
- Results report: [R271_DAILY_TREND_BREAKOUT_RESULTS.md](research/R271_DAILY_TREND_BREAKOUT_RESULTS.md)
- Exact local runner: [r271_daily_trend_breakout.py](research/r271_daily_trend_breakout.py)
- Compact metrics: [R271_results_compact.json](research/R271_results_compact.json)
- Timestamped compact trade ledger (all 126 closed trades): [R271_trade_ledger_compact.csv](research/R271_trade_ledger_compact.csv)
- Source: Dukascopy EURUSD M1 BID/ASK from data-only GitHub artifact 11959096102 / run 38697080604; ZIP SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. Local Python only; no GitHub Actions backtest ran.
- Locked setup: New York-close FX sessions; close strictly beyond prior 20 completed session high/low; exact delayed entry 17:05 NY; stop 2× prior ATR20; target 2R; max hold through the close of the tenth subsequent valid session; side-correct BID/ASK; +1 pip primary incremental cost and 0/0.5/2 pip sensitivity.
- Data audit: 4,415,493 common BID/ASK minute timestamps, no duplicates or negative open spreads; calendar filter retained 3,749,493 minute rows; median observed open spread ~0.30 pip, p95 ~0.80 pip. 320 raw breakout signals, 266 had a valid exact entry quote, 126 closed trades after position-overlap rules.
- At +1 pip: discovery 2016–2020 = 57 trades, PF 0.811, −4.949R; validation 2021 = 14 trades, PF 0.769, −1.437R; diagnostic forward 2022–2025 = 55 trades, PF 0.808, −4.265R. Annual 2022/2023/2024/2025 net R = −2.798 / −1.642 / +2.276 / −2.101. Forward four-week bootstrap: mean −0.0204R/week, 95% CI [−0.0722, +0.0324], 22.06% positive bootstrap means.
- Cost stress was negative even at +0 pip extra cost (forward −3.892R) and remained −4.638R at +2 pips. Six preregistered gates failed. Challenge replay was not run because the locked spec allowed it only for a net-positive stream. **R271 = GAGAL; no retuning.**
- The 2022–2025 period is contaminated, and 2026+ was not in this input archive, so no claim of independent promotion-grade evidence is possible even apart from the failed measured gates.


## Funded-readiness correction — official rules verified (2026-10-16)

- [Official rule matrix and remaining implementation checks](research/FUNDEDNEXT_STELLAR2_RULES_VERIFIED_20261016.md)
- [Funded-ready promotion gate](research/FUNDED_READINESS_GATE_20261016.md)

Current public FundedNext CFD Stellar 2-Step documentation verifies: Phase 1 +8%, Phase 2 +5%; 5% daily loss with daily reset at 00:00 server time and realized-today + floating P&L counted (including commissions/swaps/fees); 10% static maximum loss; at least five distinct trading days per phase; no time limit; Quick Strike must be below 30% and measures profit from profitable trades closed in under 30 seconds. Server clock is seasonally GMT+2/GMT+3. The official help center currently requires traders to be at least 18 to open a trading account. Full sources and detailed mechanics are in the linked rule matrix.

**Important correction:** historical challenge proxy metrics are not live-pass odds. Before any strategy can become LULUS for funded readiness, replay the exact phase sequence with intratrade equity, floating loss, costs, server-time reset and Quick Strike. R270/R271 stay GAGAL and must not be retuned. The 2022–2025 window is not an untouched promotion holdout. Until the user reaches age eligibility, all tests remain simulation-only.



## Authoritative clarification — “compounding” means evolutionary method search (2026-10-16)

- The user’s intended compounding is **evolution of the method-search process**: each experiment inherits and reuses evidence-backed building blocks and lessons from prior experiments, then creates a better next generation through justified mutations, crossover, ablations, and component composition. It is not merely position-size compounding, blind union of failed strategies, or a sequence of unrelated standalone tests.
- Read and follow [EVOLUTIONARY_METHOD_COMPOUNDING_20261016.md](research/EVOLUTIONARY_METHOD_COMPOUNDING_20261016.md) as the authoritative workflow. Decompose experiments into context/setup/entry/exit/execution/risk components; preserve failure diagnoses; retain potentially useful blocks only when controlled component/ablation comparisons support them; record parent IDs and child-generation rationale.
- Optimize the actual target: probability of completing both funded phases and time-to-target before rule breach. Use a risk-aware diverse/Pareto population; PF and expectancy are diagnostics. Keep frozen independent OOS protection because repeated evolutionary search on the same validation period overfits.
- Honest correction: R272 is one locked dual-module combination test, not yet a full evolutionary-search implementation. Complete the valid locked run without opening its 2026 holdout prematurely; afterward use the candidate/block registry and evidence matrix to generate the next research generation instead of returning to isolated strategy invention.

## R272 — Gold dual-module test / corrected data acquisition (2026-10-16)

**Strategy verdict: GAGAL (locked historical screen, 2026-10-16 local replay).** See `research/R272_FINAL_VERDICT.md` and `research/R272_results_compact.json` on `local-backtest/r189-dukascopy-history`. The 2026 holdout remains unopened.

- Locked hypothesis: XAUUSD M5; 12-hour trend-pullback continuation (A) in persistent regimes and failed-excursion reversal (B) in balanced regimes, five-minute manual execution delay after the signal bar closes, executable BID/ASK fills, force-flat at 16:45 New York, primary incremental cost +$0.30/oz; sensitivity +$0.00/+0.10/+0.50.
- Preregistration plus pre-result timing clarification: [R272 locked hypothesis](research/R272_XAUUSD_DUAL_MODULE_PREREGISTRATION.md).
- Local-only runner: [r272_xauusd_dual_module.py](research/r272_xauusd_dual_module.py) · [reproducible engine/provenance smoke tests](research/test_r272_xauusd_dual_module.py).
- **Runner corrections made before results:** timestamp is bar-open, so signal close is T+5m and another 5-minute manual delay requires entry at T+10m (index t+2), not T+5m. Runner enforces two exact five-minute intervals, records realized latency, handles the exact 16:45 executable opening quote without reading post-cutoff high/low, and emits a stable schema for zero-trade months.
- Local syntax, synthetic fill/latency tests and provenance-loader tests PASS. Synthetic cases verify T+10m entry = five minutes after the signal close; normal target, cutoff target gap, cutoff adverse stop gap; rejection of a broken intervening bar; acceptance of manifest with flats disabled and rejection of a manifest that permits flats. These are engine tests only, not strategy performance evidence.
- Data-quality issue found before the backtest: the January downloader probe [run 38857759446](https://github.com/christianomomongan82-lang/scanner/actions/runs/38857759446) reported “Include flats: true”. That probe and the original full acquisition [run 38857936371](https://github.com/christianomomongan82-lang/scanner/actions/runs/38857936371) are **not valid inputs** for R272’s no-synthetic-bars rule.
- Corrected acquisition code now omits the -fl flag, records include_synthetic_flat_bars=false in the manifest, and has a distinct concurrency group: [data-only collector](https://github.com/christianomomongan82-lang/scanner/blob/data/r272-xauusd-m5-2016-2026/research/download_xauusd_m5_2016_2026.py), [workflow](https://github.com/christianomomongan82-lang/scanner/blob/data/r272-xauusd-m5-2016-2026/.github/workflows/r272-xauusd-data-only-v2.yml). Its corrected raw-only collection [run 38859918137](https://github.com/christianomomongan82-lang/scanner/actions/runs/38859918137) completed and published artifact `12031270051` (`XAUUSD-M5-Dukascopy-BID-ASK-2016-2026`). Manifest confirms synthetic flats disabled; 947,326 rows per BID/ASK, 947,326 exact matching timestamps, hashes and 572 real gaps are recorded in the R272 verdict. No strategy calculations ran in Actions. The data job does not calculate signals, PnL, or verdicts.
- Runner refuses to load data unless manifest proves the correct source/instrument/timeframe/window, synthetic flats disabled, and both gzip hashes/row counts match the actual inputs.
- After valid raw BID/ASK is available, calculate and store 2016–2020 discovery and 2021–2025 historical validation first. Do not inspect 2026-01-01 through 2026-10-15 unless every locked historical gate passes. Funded readiness remains a separate rule-aware, equity-aware two-phase replay: a signal-screen pass alone is not enough.


## Latest research update — R272 GAGAL (2026-10-16 local)

- [Locked verdict report](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R272_FINAL_VERDICT.md) · [compact JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R272_results_compact.json) · [locked runner](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/r272_xauusd_dual_module.py).
- Corrected raw input artifact `12031270051`, data-only run `38859918137`; Dukascopy XAUUSD M5 BID/ASK. 947,326 paired timestamps; synthetic flat bars disabled; 572 gaps retained; median opening spread $0.358/oz, p95 $1.117/oz. Local signal/PnL calculations excluded all timestamps from 2026-01-01 onward.
- At +$0.30/oz: router/B made 944 discovery trades with -437.47R (PF 0.525) and 957 validation trades with -401.22R (PF 0.548). Even at $0 extra cost, discovery/validation were -174.83R/-227.38R. Four-week weekly-net-R bootstrap 95% CIs are [-2.081, -1.256] and [-1.951, -1.115] respectively.
- Module A fired 972 raw triggers, but none met the locked ER >= 0.45 gate; maximum trigger ER was 0.3249, so A produced zero trades. Module B's balanced failed-excursion fade was negative before incremental cost. Router outperformed raw union only relatively (-401.22R vs -439.37R in validation); both lose, and only one of six historical gates passed.
- **R272 = GAGAL.** Do not open 2026, tune R272, or run a funded replay. A future generation may inherit only the diagnostic and executable-side/delay/missing-bar controls, not claim that either signal block has demonstrated positive edge. The full local ledgers were generated locally but are not uploaded as row-level CSVs; this checkpoint links the stored compact result/report and the in-repo locked runner.

Continuation instruction: read the latest R270–R274 results and `research/EVOLUTIONARY_BLOCK_REGISTRY_20261016.md` plus `research/EVIDENCE_MATRIX_20261016.json` first. Do not open 2026 XAUUSD holdout (it remains untouched). Next search should broaden instrument/hypothesis-family coverage and use locked discovery gates and controlled ablations, not threshold-tune the failed XAUUSD M5 continuation or impulse setups. No R275 hypothesis has yet been registered.

## Latest research update — R274 GAGAL (2026-10-16 local replay)

**Latest verdict: R272 GAGAL, R273 GAGAL, R274 GAGAL. No candidate is currently eligible for funded challenge replay.**

### R272 — XAUUSD M5 dual-module router
- [Verdict](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R272_FINAL_VERDICT.md) · [compact results JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R272_results_compact.json) · [pre-registration](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R272_XAUUSD_DUAL_MODULE_PREREGISTRATION.md).
- At +$0.30/oz, router/B had 944 discovery trades / -437.47R / PF 0.525 and 957 validation trades / -401.22R / PF 0.548. Module A had zero trades because none of its 972 raw triggers met ER >= 0.45. The failed-excursion fade lost even with zero incremental cost.

### R273 — XAUUSD M5 aligned pullback continuation
- [Pre-registration](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R273_ALIGNED_PULLBACK_CONTINUATION_PREREGISTRATION.md) · [verdict](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R273_FINAL_REPORT.md) · [compact JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R273_results_compact.json) · [runner](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/r273_aligned_pullback_continuation.py).
- At +$0.30/oz, child had 131 discovery trades / -78.12R and 278 validation trades / -128.86R. It improved relative to raw-A ablation by 28.68R in validation and retained 84.0% of trades, but bootstrap intervals were wholly negative; not an edge.

### R274 — XAUUSD M5 impulse follow-through
- [Pre-registration](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R274_XAUUSD_M5_IMPULSE_FOLLOWTHROUGH_PREREGISTRATION.md) · [verdict](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R274_FINAL_REPORT.md) · [compact JSON](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R274_results_compact.json) · [runner](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/r274_xauusd_m5_impulse_followthrough.py).
- At +$0.30/oz, 974 discovery trades / -655.94R / PF 0.324 and 997 validation trades / -430.65R / PF 0.483. It was negative even at zero incremental cost; all five validation years were negative. Holdout 2026 was not opened.

### Evolutionary memory to use next
- [Block registry](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/EVOLUTIONARY_BLOCK_REGISTRY_20261016.md) and [machine-readable evidence matrix](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/EVIDENCE_MATRIX_20261016.json).
- Corrected raw-only artifact `12031270051` (data acquisition run `38859918137`) has 947,326 paired XAUUSD M5 BID/ASK rows; synthetic flats disabled; 572 >5m gaps kept. Local calculations used 877,930 quote rows through 2025 only. 2026 remains unopened.
- Data/entry/exit integrity controls are reusable implementation blocks, not alpha. No R270–R274 signal block is established as a positive edge. Row-level ledgers were generated locally but not uploaded; reports/compact JSON and the R273/R274 runners are stored in the research branch.
- **Next step:** broader instrument and hypothesis-family coverage with preregistered discovery filters and component ablations. Do not revive the failed signal blocks by lowering thresholds. Do not register R275 until its hypothesis is materially distinct and preregistered.

## Latest research update — R275 mobile-delay stress — GAGAL (2026-10-17)

- Pre-registration: [R275 locked hypothesis](research/R275_R189_L80_MOBILE_DELAY_PREREGISTRATION.md)
- Result: [R275 final report](research/R275_FINAL_REPORT.md) · [compact metrics and gate verdict](research/R275_results_compact.json) · [standalone runner](research/r275_r189_l80_mobile_delay.py). Local detailed parent/child ledgers were generated at calculation time; full row-level CSV ledgers are not yet archived in GitHub.
- Parent: locked R189/L80 using exact T+1 minute execution after M1 signal-bar open. Child: unchanged signal logic with exact T+6 minute entry to model wait-for-close plus five-minute manual phone delay. No parameter tuning.
- Input: Dukascopy EURUSD M1 BID/ASK data artifact 11959096102, archive SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. The archive was collected with `-fl`; 696,795 paired flat-candidate rows (15.78%) were conservatively filtered when both BID/ASK candles copied prior closes at the exact next minute. 3,718,698 rows remain. This heuristic is a data limitation, not formal proof all synthetic bars were removed.
- At +1 pip additional cost, exploratory 2022–2025: parent 699 trades / PF 0.839 / -378.5 pips / 440.0-pip max DD; child 701 / PF 0.694 / -786.3 pips / 816.9-pip max DD. At +2 pips the child PF was 0.496 and net -1,487.3 pips. The child’s four-week circular weekly-net-pips bootstrap (10,000 reps, seed 2752026) was -3.762 pips/week, CI95 [-5.252, -2.398], wholly negative.
- Locked gates: sample-size gate passed; PF at +1/+2 pips, annual robustness and bootstrap gates all failed. **R275 = GAGAL; no challenge replay and no tuning.** 2022–2025 is contaminated and remains exploratory, not a pristine holdout. R275 did not use EURUSD 2026; reserved XAUUSD 2026 remains unopened.
- Evolutionary lesson: the L80 signal does not survive the tested additional phone-entry delay and cost assumptions. Do not blend this failed stream with the failed R272–R274 gold signals. The next generation must broaden structural hypothesis/instrument coverage rather than parameter-rescue this child.

## Latest research update — R276–R279 US cash-open breadth family (2026-10-17)

- Preregistered hypotheses: [R276 two-sided breadth router](research/R276_US_CASH_OPEN_BREADTH_ROUTER_PREREGISTRATION.md), [R277 same-day flat](research/R277_US_CASH_OPEN_BREADTH_INTRADAY_FLAT_PREREGISTRATION.md), [R278 long-only child](research/R278_LONG_ONLY_US_CASH_OPEN_BREADTH_PREREGISTRATION.md), [R279 no-fixed-TP ablation](research/R279_LONG_ONLY_BREADTH_INTRADAY_NO_TP_PREREGISTRATION.md).
- [Combined batch report](research/R276_R279_EVOLUTIONARY_BATCH_RESULTS.md), plus per-round [R276 report](research/R276_FINAL_REPORT.md) / [R276 JSON](research/R276_results_compact.json), [R277 report](research/R277_FINAL_REPORT.md) / [R277 JSON](research/R277_results_compact.json), [R278 report](research/R278_FINAL_REPORT.md) / [R278 JSON](research/R278_results_compact.json), [R279 report](research/R279_FINAL_REPORT.md) / [R279 JSON](research/R279_results_compact.json).
- Shared input artifacts: USA500 11709864394, USATECH 11710370389, USA30 11710730507, USSC2000 11710111254; Dukascopy M5 BID OHLC. USSC2000 history starts 2018-08-08; synchronized child events were restricted to timestamps covered by all four sources. Cost stresses are modeled 1/2 price bps round-trip, not verified actual costs.
- **R276:** all locked historical statistical gates passed (767 discovery closes PF@+2bp 1.138; 828 exploratory 2022–2025 closes PF@+1/+2bp 1.289/1.257; bootstrap 95% CI [0.166, 1.269] R/week), but diagnostic 2026 PF@+1bp was 0.748 / −19.38R. Forward total R (+147.06) was below matched parent (+176.09), and holds were too long (median 17.83h, p95 124.63h, max about 60 days). No full account-path replay or swap verification. **Screen pass only; not promoted.**
- **R277:** GAGAL; discovery PF@+2bp 0.989; 2024 PF@+1bp 0.794; four-week bootstrap 95% CI [−0.116, 0.793] R/week.
- **R278:** GAGAL; discovery PF@+2bp 0.889 despite forward PF@+1/+2bp 1.403/1.346; diagnostic 2026 PF@+1bp 0.877.
- **R279:** GAGAL; discovery PF@+2bp 0.873. Removing the fixed target was worse than the R278 child (forward net +67.80R vs +69.10R, PF 1.395 vs 1.403, max DD 17.99R vs 17.26R).
- Overall: no candidate from R276–R279 is funded-ready; 2022–2025 is contaminated and 2026 is only diagnostic. No rule-aware two-phase challenge replay was run, and actual bid/ask, commissions, overnight swaps, contract multipliers, floating daily loss and Quick Strike remain unverified.
- Reproducibility gap: reports and compact JSONs are stored in GitHub, but the full R276–R279 local runners and row-level ledgers are not yet committed there. Do not claim complete repository-only reproduction until archived.
- Next action: reject R277–R279 and do not keep changing this same cash-open family. Any new generation must use a genuinely different hypothesis, preregister it before outcomes, compare matched parent/ablation, and optimize actual target-completion/breach profile rather than PF alone.

## Latest research update — R280 Nasdaq-led follower breakout — GAGAL (2026-10-17)

- Pre-registration: [R280 Nasdaq-led cash-open follower breakout](research/R280_NASDAQ_LED_CASH_OPEN_FOLLOWTHROUGH_PREREGISTRATION.md)
- Results: [R280 final report](research/R280_FINAL_REPORT.md) · [compact metrics and locked gate verdict](research/R280_results_compact.json).
- Hypothesis: USATECH/Nasdaq 100's first cash-open opening-range breakout leads; take a same-direction first breakout on USA500, USA30 or USSC2000 only if the follower signal is 5–30 minutes later. Exact T+10 entry; OR-edge stop; 2R target; mandatory flat at exact 16:00 New York bar open. Matched parent consists of all first OR breakouts from those three follower indices under identical execution and costs.
- Child signal set: 1,084 eligible follower signals out of 7,502 first-breakout follower signals; 426 closed trades in exploratory forward 2022–2025. At +1 bp, child forward PF 1.169 / +27.89R vs matched parent PF 1.090 / +108.76R; the filter increased mean net R/trade (0.0655R vs 0.0363R) but sacrificed total net R and trade count. At +2 bp child PF 1.109.
- **R280 = GAGAL:** discovery PF@+2 bp 0.875; annual 2023/2024 PF@+1 bp 0.977/0.787; four-week bootstrap 95% CI for forward weekly net R [−0.116, +0.381]; diagnostic 2026 PF@+1 bp 0.744. Do not tune the lag window after these results.
- Inputs are the cached R205 BID-only M5 snapshots for USA500 artifact 11709864394, USATECH 11710370389, USA30 11710730507 and USSC2000 11710111254. Costs are modeled 1/2 bps and do not represent verified FundedNext instrument costs. 2022–2025 is contaminated; 2026 is only diagnostic. No full funded equity-path replay.
- Overall R276–R280: no candidate promoted. R276 passed the historical screen only but has a negative diagnostic and missing funded-path/swap checks; R277–R280 failed pre-registered gates. Reusable controls are execution/data integrity, not signal edge.
- Reproducibility gap remains: R276–R280 reports and compact JSON summaries are stored in GitHub, but all full local runners and row-level trade ledgers are not yet stored there. Do not describe GitHub-only reproduction as complete until these are archived.
- Next search should not keep mutating this US cash-open breakout family. Register a structurally distinct mechanism before calculation and score it against fixed target-completion and breach objectives. Keep all 2026 slices diagnostic only.



## Latest research update — R281 EURUSD H1 compression-release — GAGAL (2026-10-17)

- Preregistration: [R281 design](research/R281_EURUSD_H1_COMPRESSION_RELEASE_PREREGISTRATION.md)
- Runner: [R281 local Python runner](research/r281_eurusd_h1_compression_release.py)
- Results: [R281 final report](research/R281_FINAL_REPORT.md) · [compact JSON](research/R281_results_compact.json) · [grid summary](research/R281_grid_summary.csv)
- Purpose: correct R257's zero-trade eligibility/coverage problem, without changing the original fixed grid. H1 BID/ASK candles were constructed from Dukascopy M1; this is not claimed as a byte-identical reproduction of R257's former H1 file.
- Input: GitHub data-only artifact 11959096102; archive SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. Raw archive collector used `-fl`; paired flat-row removal is heuristic. 57,191 complete H1 bars; no missing bars were filled. Fit thresholds from 2017-2020 were 20.8 pips (Q20) and 25.0 pips (Q30).
- At +1 additional pip, all eight discovery configurations lost: PF 0.575-0.667, 88-392 trades, net -336.6 to -1,622.5 pips. Best 2021 validation sample count was 10, below the required 50. Q20/B12 produced 4 validation trades and PF 2.065 but its discovery PF was 0.575-0.615, so it fails and must not be revived.
- **Verdict: GAGAL.** No candidate selected. To honor the stage gate, 2022-2025 outcomes were not calculated or inspected; XAUUSD M5 2026 holdout remains unopened. No challenge replay was run.
- Repository artifacts now include preregistration, runner source, report, compact results, and grid summary. Row-level trade ledgers remain local and should be archived before claiming full repository-only reproduction. No Actions backtest workflow was launched.
- Decision: close this fixed compression-release specification; no signal component retained. Next search must move to another mechanism, not loosen these thresholds.


## Latest research update — R282 EURUSD weekend-reopening gap fade — GAGAL / DATA COVERAGE (2026-10-17)

- Preregistration: [R282 design](research/R282_EURUSD_WEEKEND_GAP_FADE_PREREGISTRATION.md)
- Local runner: [R282 replay source](research/r282_eurusd_weekend_gap_fade.py)
- Results: [R282 report](research/R282_FINAL_REPORT.md) · [JSON](research/R282_results.json) · [event coverage audit](research/R282_event_coverage_audit.csv)
- Data source: Dukascopy EURUSD M1 BID/ASK artifact 11959096102, SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. The source collector used `-fl`; 696,795 paired flat candidates were removed heuristically after alignment/valid-OHLC screening.
- The event detector saw 4 timestamp gaps ≥36 hours in the full 2016–2025 file; 3 met the locked Friday-to-Sunday/Monday condition. All 3 were timestamps at 00:00 UTC (2018-01-01, 2020-12-27, 2024-01-01) and each lacked exact T+10 timestamp; next observed quote arrived much later. None is a valid executable weekly reopening under the preregistered rules.
- **Verdict: GAGAL — data/event coverage; alpha untested.** Zero trades, no reportable PF. 2022–2025 outcomes were not computed because discovery/validation gate failed; no challenge replay. Do not relax delay gate post-result.
- R282 runner, prereg, report, results JSON and event-coverage CSV are archived. No GitHub Actions backtest workflow was launched.
- Overall status R270–R282: no candidate promoted. R276 is only a historical screening pass with material unresolved failures; R277–R281 fail signal gates; R282 is data-ineligible, not a proven losing strategy.


## Latest research update — R282 EURUSD weekend-reopening gap fade — INVALID TEST (2026-10-17)

- [Preregistration](research/R282_EURUSD_WEEKEND_GAP_FADE_PREREGISTRATION.md) · [runner](research/r282_eurusd_weekend_gap_fade.py) · [report](research/R282_FINAL_REPORT.md) · [JSON](research/R282_results_compact.json) · [event audit](research/R282_event_audit.csv)
- Input archive SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`, collected with `-fl`; most Sunday reopening bars were omitted. Only 3 long-closure candidates detected, none with exact T+10 minute continuity; zero trades evaluated.
- This is **not** a no-edge result; data is inadequate to test weekly reopen gap fade. No strategy outcomes or forward period metrics were calculated. Do not patch event definition after seeing the issue; retry only with verified raw BID/ASK M1 including true weekend reopen observations. No GitHub Actions workflow launched.


## Latest research update — R283 US index cash-open gap fade — GAGAL (2026-10-17)

- Preregistration: [R283 design](research/R283_PREREGISTRATION.md)
- Results: [final report](research/R283_FINAL_REPORT.md) · [period summary](research/R283_period_summary.csv) · [data audit](research/R283_data_audit.csv)
- Tested four BID-only US index M5 archives. Rules locked: per-index Q80 gap fitted on 2017–2020; fade 09:30 open gap at 09:40 ET (T+10); target prior RTH close; stop 0.75× original gap; no overnight; modeled round-trip 1/2/4 bps.
- At 2 bps, discovery 2017–2020 = 709 trades, PF 0.748, net -77.90R; validation 2021 = 163 trades, PF 0.599, net -34.83R. Trade-count gates passed, expectancy gates failed. 2022–2025 deliberately not scored; no forward period opened.
- Verdict: **GAGAL**, close this exact spec, do not tune it. No alpha retained. Data are BID-only and costs modeled; actual spread/CFD point value/commission/slippage/swaps and funded equity-path replay remain absent. No Actions workflow launched.
- R283 source runner and full row-level ledger were executed/stored locally in this session but are not yet archived in GitHub; report, preregistration, compact period summary and input audit are archived. Do not claim repository-only full reproducibility until source/ledger are committed.


## 2026-10-17 — R283 trade-level postmortem

**R283 remains GAGAL; no strategy was promoted.** The locked local trade ledger was decomposed after the fail decision; this was diagnostic only, not parameter tuning.

- Discovery 2017–2020: 709 trades, gross PF 0.795 and gross -61.75R before modeled costs; at 2 bp PF 0.748 and -77.90R.
- Validation 2021: 163 trades, gross PF 0.638 and gross -30.52R; at 2 bp PF 0.599 and -34.83R.
- Discovery exits: 152 target fills versus 237 stop exits; session-close exits were 320 trades and contributed only +1.04R after 2-bp cost.
- Validation exits: 35 target fills versus 72 stop exits; the stop share rose from 33.43% in discovery to 44.17%, while the target share stayed near 21.3–21.5%.
- The strategy is negative before modeled costs; costs worsen it but do not explain the underlying failure.
- Fading gap-ups (SHORT) was materially weaker than fading gap-downs (LONG) in both segments. Both directions remained negative. This asymmetry is a hypothesis lead only; it is not evidence for gap continuation.
- 2022–2025 was not scored, and 2026 remains unopened under the existing contamination rules. R283's exact spec must not be tuned.

Archived diagnostic artifacts:
- [Trade-level diagnostic](research/R283_TRADE_LEVEL_DIAGNOSTIC.md)
- [Exit decomposition](research/R283_EXIT_DECOMPOSITION.csv)
- [Direction decomposition](research/R283_DIRECTION_DECOMPOSITION.csv)
- [Instrument/year decomposition](research/R283_INSTRUMENT_YEAR_DECOMPOSITION.csv)
- [Machine-readable diagnostic results](research/R283_DIAGNOSTIC_RESULTS.json)

**Known persistence gap:** the 872-row R283 trade ledger and exact runner were available in the local analysis workspace, but they have not yet been committed to this branch. The report explicitly records that repository-only reproduction is incomplete. Next work should resolve this gap by archiving the row ledger/runner or recreating and committing them from the verified source archives; do not pretend it is already done and do not ask the user to upload data that are available in the current runtime.


## Latest research update — R284 late-morning continuation — GAGAL (2026-10-17)

- [Pre-registration](research/R284_US_INDEX_LATE_MORNING_CONTINUATION_PREREGISTRATION.md) was committed before calculating outcomes.
- [Final report](research/R284_FINAL_REPORT.md) · [machine-readable results](research/R284_results_compact.json).
- New, structurally distinct hypothesis: direction-following of the 10:00–11:55 ET index move, one selected instrument per New York session, child threshold based only on each instrument's 2017–2020 Q75; T+10 entry at 12:05; 1.0× range stop / 1.5R target / 15:55 bar-open force-flat.
- Data: four R205 cached GitHub artifacts; M5 BID-only. Eligibility counts: USA500 2,662 sessions; USATECH 2,675; USA30 2,672; USSC2000 2,022. The flat-candidate filter is heuristic; modeled 1/2/4 bp costs are not verified CFD costs.
- At 2 bp, child discovery 2017–2020 = 380 trades / PF 0.864 / -13.108R / max DD 16.264R. Annual net R: 2017 -3.011; 2018 -0.051; 2019 -6.957; 2020 -3.090 (0/4 positive). Validation 2021 = 114 / PF 1.066 / +1.326R, but this modest result does not rescue negative discovery. At 4 bp the discovery PF falls to 0.797.
- Matched parent baseline at 2 bp was also negative: discovery 981 trades / PF 0.822 / -47.650R; 2021 251 / PF 0.941 / -3.266R. Child reduces discovery loss versus parent but is still not an edge.
- **Verdict: GAGAL.** The discovery PF, net-return, positive-year, and 4-bp PF gates failed. 2022–2025 and 2026 outcomes were not computed/opened as required; no funded challenge replay and no Actions backtest were run. Do not lower threshold or alter this exact specification post-result.
- Persistence update: result JSON, report and compact replay engine are now on GitHub. The compact engine was compared with the original full local run and matched all parent/child trade counts, PFs and net-R totals for discovery/validation at 1/2/4 bp exactly. The row-level trade ledger is still not archived, so trade-by-trade reproduction remains incomplete. The signal has not been promoted and does not enter the edge-backed block set.


## Latest research update — R285 US500 turn-of-month intraday seasonality — GAGAL (2026-10-17)

- [Preregistration](research/R285_US500_TURN_OF_MONTH_INTRADAY_PREREGISTRATION.md) was committed before any return calculations. A data-quality-only calendar amendment was then committed before PnL: [R285 DQ1](research/R285_DQ1_PREOUTCOME_CALENDAR_AMENDMENT.md).
- [Final report](research/R285_FINAL_REPORT.md) · [machine metrics](research/R285_results_compact.json) · [local replay runner](research/r285_us500_tom_intraday.py) · [candidate return ledger at 2 bp](research/R285_candidate_ledger_2bp.csv) · [selected-date skip log](research/R285_selected_session_skips.csv).
- New mechanism: long US500 only on the first three or final two observed active RTH dates of each month; enter 09:40 ET, exit 15:55 ET. This is a calendar-seasonality test, not a retuned R283/R284 price trigger. M5 BID-only source artifact 11709864394, archive SHA-256 `21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac`.
- At modeled 2 bp round-trip cost, discovery 2017–2020 = 226 trades / PF 1.130 / +785.76 bp; parent all-session long = 979 / PF 0.985 / -380.59 bp. The candidate discovery total was highly regime-concentrated: 2017 -132.96 bp, 2018 -502.78 bp, 2019 -136.29 bp, 2020 +1,557.79 bp.
- Validation 2021 = 58 trades / PF 0.632 / -669.02 bp, whereas the all-session parent returned +539.74 bp at the same cost. At 4 bp, candidate validation PF was 0.583.
- **Verdict: GAGAL.** Discovery fails the >=3-of-4 positive-year gate; validation fails PF/net gates at 2 bp and the PF stress at 4 bp. 2022–2025 and 2026 trade outcomes were not calculated or inspected, and no funded replay was run.
- Data screen: 2,777 active RTH session dates, 2,659 quality-eligible, 650 candidate calendar dates, 36 selected sessions skipped for missing bars or repeated-flat candidates. The flat filter is heuristic; BID-only and modeled costs are not live execution evidence.
- The compact local runner was rerun and matched candidate/parent counts, PF and net-bps totals for discovery/validation at each 1/2/4 bp cost. Candidate ledger and selected-date skip log are archived. No GitHub Actions backtest was launched. The failed signal block is not retained for evolutionary crossover; only the calendar/data-quality and execution-audit procedures remain reusable.


## Latest research update — R286 US500 three-session overextension fade — GAGAL (2026-10-17)

- [Pre-registration](research/R286_US500_3SESSION_OVEREXTENSION_FADE_PREREGISTRATION.md) was committed before strategy-return calculations.
- [Final report](research/R286_FINAL_REPORT.md) · [machine-readable results](research/R286_results_compact.json) · [local replay runner](research/r286_us500_3session_fade.py) · [candidate ledger](research/R286_candidate_ledger_2017_2021.csv) · [matched parent ledger](research/R286_matched_parent_ledger_2017_2021.csv) · [skipped entry-session log](research/R286_skipped_signals.csv).
- Hypothesis: fade a three-consecutive-active-session close-to-close move when its absolute value exceeds discovery-only Q80. Q80 = 1.7307755%, fitted on 858 qualifying 2017–2020 signal windows. Entry next active session 09:40 ET, exit that session 15:55 ET; matched parent follows the same move on the same events.
- Input: cached GitHub R205 USA500 M5 BID-only artifact 11709864394; archive SHA-256 `21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac`; extracted CSV SHA-256 `df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee`. Data screening retained 2,777 active RTH dates and 2,659 quality-eligible dates; seven selected events were skipped because the next entry session was invalid.
- At modeled 2 bp round-trip cost, candidate discovery 2017–2020 = 165 trades / PF 0.9882 / -87.79 bp; matched continuation parent = 165 / PF 0.9258 / -572.21 bp. Validation 2021 candidate = 47 / PF 0.9869 / -15.25 bp; matched parent = 47 / PF 0.8591 / -172.75 bp.
- Candidate cost stress PF: discovery 1/2/4 bp = 1.0105/0.9882/0.9451; validation = 1.0280/0.9869/0.9107. The candidate reduces losses relative to its parent but is still negative in both discovery and validation.
- **Verdict: GAGAL.** Discovery PF/net at 2 bp and validation PF/net at 2 bp fail. The positive-year count gate was met only nominally because 2017 contains one trade; 2018 lost 1,315.07 bp, while 2020 gained 1,115.63 bp. Do not alter Q80, direction, lookback or times after results.
- 2022–2025 and 2026 outcomes were not calculated or inspected, and no funded challenge replay was run. Cost model remains hypothetical due BID-only data; this is not funded-readiness evidence.
- The replay runner, results JSON, candidate row ledger, matched parent ledger and skipped-signal log are now archived. The matched parent ledger uses the exact same event dates and opposite direction/return on each event. No GitHub Actions backtest was created or dispatched. No signal block is retained for strategy crossover; only implementation/data-quality controls remain reusable.


## Latest research update — R287 intraday cross-index residual fade — GAGAL (2026-10-17)

- [Pre-registration](research/R287_US_INDEX_INTRADAY_RESIDUAL_REVERSION_PREREGISTRATION.md) was committed before return/PnL calculation.
- [Final report](research/R287_FINAL_REPORT.md) · [machine-readable results](research/R287_results_compact.json) · [local replay runner](research/r287_intraday_residual_reversion.py) · [paired candidate/parent ledger](research/R287_paired_ledger_2017_2021.csv) · [session-quality summary](research/R287_session_quality_summary.csv).
- Hypothesis: measure the 10:00 open to 12:55 close return for USA500, USATECH, USA30 and USSC2000, subtract same-date cross-sectional median, select the strongest normalized absolute residual using per-symbol Q75 thresholds fitted on 2017–2020, then fade the residual at 13:05 and force flat at the 15:55 bar open.
- Extracted source CSV SHA-256 values: USA500 `df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee`; USATECH `82b06c38f66cd1387097691baac1d45c9463b6540eea9dfe28a894d85e122f7c`; USA30 `8fcef9d76b31e99ae8d0175e769307ab13f930ae3ec2c17ef6baf0311ea1783a`; USSC2000 `c01c97d8705453d3fa3fd4ac1d386e9c1d72ab27e3b7d57d6cde53da9dfdf6f0`. Inputs are cached GitHub R205 M5 BID-only files.
- Session-quality valid counts (2017–2021): USA500 1,230; USATECH 1,240; USA30 1,237; USSC2000 836. 1,228 dates had at least three valid symbols. 745 synchronized events met the normalized residual score gate: 552 discovery trades and 193 validation trades.
- At modeled 2 bp cost, candidate fade discovery = 552 / PF 0.802 / -2,742.47 bp; validation = 193 / PF 0.628 / -1,510.80 bp. Cost stress PF at 1/2/4 bp was 0.838/0.802/0.734 in discovery and 0.667/0.628/0.555 in validation. **R287 = GAGAL.**
- Matched parent direction (following rather than fading the same residual) did better: discovery PF 1.044 / +534.47 bp and validation PF 1.253 / +738.80 bp at 2 bp. This is a diagnostic finding, not an approved replacement: direction was observed to outperform inside the same study, discovery PF was below 1.05, and using it as a chosen strategy creates selection bias.
- 2022–2025 and 2026 PnL outcomes were not calculated for R287; no funded challenge replay and no GitHub Actions backtest workflow were run. BID-only prices and modeled costs do not verify actual CFD execution or DLL/MLL.
- Row-level paired candidate/parent ledger and symbol-level source quality summary are now archived. The failed fade signal is not retained as an alpha block; reusable elements are cross-sectional residual calculation, synchronized event matching, data-quality controls and matched-direction ablation as research methods, not a signal.


## Latest research update — R288 cross-index residual follow-through — GAGAL (2026-10-17)

- Pre-registration locked before outcome calculation: [R288 preregistration](research/R288_US_INDEX_INTRADAY_RESIDUAL_FOLLOW_PREREGISTRATION.md), commit `5cf412ad6d335d4c8f651750cd312804ef9a0c61`.
- [Final report](research/R288_FINAL_REPORT.md) · [compact machine results](research/R288_results_compact.json) · [exact local replay runner](research/r288_us_index_intraday_residual_follow.py) · [annual table](research/R288_annual_follow_2bp.csv).
- Inputs are R205 M5 BID-only cached assets from run 38160487617: USA500 artifact 11709864394, USATECH 11710370389, USA30 11710730507, USSC2000 11710111254. Raw source artifacts have their existing expiry; ZIP and extracted CSV SHA-256 values are recorded in the runner/results JSON. Source latest UTC: 2026-10-09 20:10.
- Locked method: 10:00 ET open to 12:55 ET close signal return minus same-date median across >=3 eligible symbols; per-symbol Q75 absolute residual from eligible 2017–2020 data only; one top normalized event/date (score>=1); follow residual; enter 13:05 ET open and exit 15:55 ET open. PnL is calculated only for 2022–2026, not 2017–2021.
- At modeled 2 bp cost, follow candidate 2022–2025: 718 trades, PF 0.795, net -3,389.34 bp; 2026: 154 trades, PF 0.943, net -116.46 bp. 4-bp PF is 0.721 / 0.807, respectively. All gates except trade-count gates failed.
- The matched fade stream is only a same-event diagnostic: 2022–2025 PF 1.035 / +517.34 bp at 2 bp, but PF 0.940 / -918.66 bp at 4 bp; 2026 loses at all cost levels. Do not promote either direction.
- Four-week circular bootstrap of the follow candidate’s 2022–2025 weekly net at 2 bp: mean -16.22 bp/week, 95% CI [-32.80, -0.30] (209 weeks, 5,000 replicates, seed 288).
- Binary verdict: **GAGAL**. Do not adjust thresholds/direction/timing using these outcomes. The 2022–2025 window is project-contaminated; 2026 is a later chronological check, not claimed as a pristine program-level holdout. No funded equity path was run.
- Execution/data caveats: M5 BID-only data, modeled rather than observed transaction costs, heuristic repeated-flat exclusion, no verified CFD contract multipliers/commissions/swaps, no ask-side fill reconstruction, and no DLL/MLL challenge replay.
- Reusable methodological blocks only: synchronized eligible-session construction, frozen threshold fitting, deterministic one-event-per-session selection, matched same-event direction ablation, cost-stress/weekly-bootstrap reporting. No positive alpha block is retained from R288.


## R289 — Continental Europe cash-open gap continuation — GAGAL (2026-10-17)
- Locked rules and pre-outcome timestamp clarification: [R289 preregistration](research/R289_CONTINENTAL_EUROPE_GAP_CONTINUATION_PREREGISTRATION.md), final amendment commit `f3dba6084362a2b27855031945ca700521d586bc`.
- [Final report](research/R289_FINAL_REPORT.md) · [compact results JSON](research/R289_results_compact.json) · [Python replay runner](research/r289_continental_europe_gap_continuation.py) · [annual return summary](research/R289_annual_summary_2bp.csv) · [validation bootstrap output](research/R289_validation_weekly_bootstrap_2bp.json) · [session-quality audit summary](research/R289_session_quality_audit_summary.csv).
- Continuation discovery 2017–2020: 251 trades; at modeled 2 bp, PF in R 1.2245, +20.682R. Validation 2021: 61 trades; PF in R 1.1283, +3.088R. The four-week block-bootstrap validation 95% CI was [-0.1767R, +0.2817R] per week, so its lower-bound gate failed.
- **Binary verdict GAGAL**; no 2022–2026 PnL was calculated. No parameter retuning or promotion.
- R205 cached M5 BID-only source artifacts: DEUIDXEUR 11710710062, FRAIDXEUR 11710800007, EUSIDXEUR 11710326105; hashes and eligible-session counts are in the results JSON. EUSIDXEUR has materially poorer early coverage because repeated-flat bars were excluded.
- Limits: modeled costs rather than observed executable costs, no verified CFD multiplier/fees/swaps, M5 intrabar stop/target order approximated stop-first, no equity-aware DLL/MLL funded replay. No alpha block promoted; retain only session quality, frozen quantile calibration and bootstrap gate as research process.
