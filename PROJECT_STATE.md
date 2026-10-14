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

## 6. Langkah berikutnya — jangan mulai R259 secara acak

1. Audit R251–R258 satu per satu dan bangun **peta kegagalan kumulatif**: hipotesis, sumber edge yang diuji, frekuensi, expectancy setelah biaya, forward/OOS, stabilitas tahunan, dan alasan gagal.
2. Reproduksi hasil historis R189 atau jelaskan tepatnya bagian mana yang belum bisa direproduksi; pertahankan hasil OOS 2026 sebagai bukti terpisah.
3. Berdasarkan bukti itu, pilih strategi A yang punya kualitas edge terbaik dan keluarga strategi B yang benar-benar berbeda untuk menutup kelemahan frekuensi bila diperlukan.
4. Preregistrasikan hipotesis dan semua gate sebelum run berikutnya. Simpan semua artefak ke GitHub dan berikan verdict biner LULUS/GAGAL.

**Kesimpulan status saat ini:** belum ada strategi final yang lulus. R258 resmi GAGAL. R189 punya sinyal OOS 2026 yang perlu direproduksi lebih lanjut, bukan dianggap sudah final. Arah baru adalah strategi modular dengan satu pengendali risiko, bukan satu metode yang dipaksa memenuhi semuanya.
