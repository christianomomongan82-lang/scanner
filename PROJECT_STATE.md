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

Preferensi strategi: gunakan price action/statistik mentah; indikator klasik EMA/RSI/MACD/Bollinger tidak dipakai kecuali pengguna mengubah batasan. Ambang target yang pernah ditetapkan adalah PF minimal 1,10 pada kondisi stress terburuk yang diwajibkan; gate lengkap harus ditulis setidak setiap eksperimen.

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

