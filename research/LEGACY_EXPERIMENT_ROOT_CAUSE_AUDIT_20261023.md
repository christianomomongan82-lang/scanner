# Audit akar penyebab kegagalan eksperimen backtest lama
Tanggal audit: 2026-10-23
Sumber utama: `File gabungan.zip` (167 artefak: skrip, laporan, JSON, CSV, knowledge archive).
Status dokumen: AUDIT AWAL BERBASIS ARSIP; bukan klaim bahwa setiap artefak telah dijalankan ulang. Arsip tidak menyertakan raw M1/tick lengkap untuk mereproduksi semua eksperimen secara independen.

## Putusan sementara yang didukung bukti
Kegagalan proyek bukan disebabkan satu faktor tunggal. Ada setidaknya empat kelompok masalah berbeda, dan beberapa eksperimen lama memang menghasilkan angka yang tidak boleh dipercaya sebagai bukti edge:

1. **Look-ahead / sinyal memakai data masa depan — terbukti pada keluarga tertentu.**
   - Arsip `BACA_DULU_ALASAN_INVALID.md.txt` menyatakan R133, R137, B20, dan B21 awalnya terdampak struktur konfirmasi yang overlap dengan sesi impuls.
   - Bukti R137: sinyal sebelum sesi selesai memiliki PF 1.838; setelah sesi selesai PF 0.884; versi fully-causal PF 0.830. Jadi PF bagus awal pada keluarga session-impulse/recovery bukan edge yang bisa dieksekusi. Keluarga ini ditutup; angka B20/B21 awal tidak boleh diperlakukan sebagai strategi siap pakai.
   - Ini penyebab konkret untuk keluarga tersebut, bukan penjelasan otomatis bagi semua eksperimen.

2. **Biaya eksekusi terlalu optimistis — terbukti pada L80 + H1-R1.**
   - `CHECKPOINT_2026-09-21_SPREAD_NYATA.md` di knowledge archive: kandidat L80+H1-R1 yang terlihat bagus dengan biaya flat gagal floor pada bid/ask nyata, bahkan dengan markup tambahan 0.
   - Penyebab terukur: H1-R1 banyak entry tepat sesudah rollover; spread entry rata-rata sekitar 3.5 pip (256 dari 323 entry). Komponen H1 yang tampak +2.99 pip/trade pada model bid-only menjadi sekitar -0.96 pip/trade, PF 0.679, pada replay bid/ask.
   - L80 sendiri juga tidak lolos floor tahunan pada spread nyata: PF 1.296 pada markup 0 tetapi worst-year PF 0.954; dengan markup 0.2 worst-year 0.902. Jadi masalah bukan sekadar tambahan markup kecil.

3. **Bug engine / timestamp / eksekusi — beberapa kejadian terdokumentasi.**
   - Arsip mencatat paket GPT adaptive-exit lama mempunyai loader CSV yang gagal dan double bar-shift pada entry L80. Shift dua bar mengubah hasil win/loss meski jumlah trade sama.
   - Riwayat rekonstruksi H1 16–18 versus 17–19 menghasilkan jumlah trade berbeda; versi lama yang tidak sama dengan canonical kemudian disupersede/dibuang.
   - R169 awal memiliki masalah indexing/audit dan secara eksplisit tidak boleh dipakai sebagai bukti promosi.
   - Audit 2026-10-23 atas MRM V1 menemukan flat/closed-market candles masuk ke feature/label windows. Setelah titik-titik yang terkena closure dibuang, forward PF tetap 0.821 dan hasil tetap negatif. Artinya bug tersebut nyata, tetapi memperbaikinya tidak menciptakan edge.

4. **Selection bias, regime-overfit, dan hasil yang tidak tahan waktu — pola luas, tetapi berbeda dari look-ahead.**
   - Knowledge archive mencatat GA/evolutionary search pada M1/M5/M30 overfit ke 2024–2025 atau threshold-fragile.
   - Banyak keluarga lain gagal di periode lain: displacement-reversal menunjukkan regime split 2020/2021; ORB, continuation-after-displacement, gap, D1, multi-feature scorer, conditional-state mining, dan berbagai exit/filter mutation tidak melewati floor konsistensi.
   - Contoh arsip: generic multi-feature scorer terbaik hanya PF sekitar 1.039 dengan worst-year 0.656; conditional-state mining terbaik PF 1.179 tetapi worst-year 1.079; beberapa D1 candidate memiliki PF agregat di atas 1.2 namun worst-year di bawah 1.
   - Ini menunjukkan banyak pola lokal yang tampak menguntungkan tidak bertahan lintas tahun. Tidak cukup bukti untuk menyebut semuanya overfit dengan mekanisme yang sama.

## Masalah spesifik R189/R190
- R189 dilaporkan: 1,840 trade full sample; PF 1.328 pada biaya historis +0.2 pip; forward 2021–2025 PF 1.358, worst-year PF 1.185, 869 trade, 3.34 trade/minggu. Namun laporan yang sama masih menyebut broker/funded commission, live timezone mapping, dan intraday running-loss belum diverifikasi.
- Knowledge archive sebelumnya menyatakan keluarga L80+H1-R1 gagal ketika memakai bid/ask tick/spread nyata. Karena itu R189 tidak boleh langsung dianggap aman hanya karena report canonical lulus checksum dengan biaya per-trade sederhana.
- Replay BID/ASK independen yang dibahas pada audit sesi 2026-10-23 memberi hasil yang lebih lemah dan frekuensi berbeda. Angka ini belum bisa dipakai sebagai rekonsiliasi final sampai raw data, timestamp mapping, signal timestamps, entry prices, exit path, spread treatment, dan trade log dibandingkan satu per satu.
- R190 menurunkan PF forward dari 1.358 ke 1.304 dan worst-year PF dari 1.185 ke 1.132; mekanisme tambahan tidak memperbaiki baseline pada hasil laporan. Maka R190 bukan jawaban atas masalah R189.

## Kenapa proyek terlihat lebih baik sebelum metode berubah?
Sebagian hasil lama memang lebih baik secara angka, tetapi arsip menunjukkan ada dua kelas hasil yang tercampur:
- hasil yang kuat pada engine/cost model tertentu, namun belum lolos eksekusi bid/ask nyata atau provenance;
- hasil yang kemudian terbukti invalid akibat look-ahead atau bug implementasi.
Karena itu, membandingkan angka PF lama dengan hasil baru tanpa menyamakan data, sesi waktu, biaya, dan engine akan menyesatkan. Namun juga salah jika semua hasil lama dianggap buruk: R189/L80 memang layak diaudit sebagai baseline historis, bukan diterima mentah-mentah atau dibuang tanpa rekonsiliasi.

## Akar masalah operasional pada proses riset
1. Beberapa kali promosi dilakukan sebelum seluruh verifikasi biaya nyata dan funded risk selesai.
2. Ada inkonsistensi antara label status seperti PROMOTE/VERIFIED dan catatan BELUM DIVERIFIKASI.
3. Ada hasil yang berasal dari rekonstruksi, bukan kode/data canonical; beberapa versi kode mempunyai bug.
4. Terlalu banyak mutasi keluarga strategi yang sudah menunjukkan kegagalan stabilitas, sehingga pencarian melebar sebelum baseline yang unggul direkonsiliasi sampai trade-level.
5. PF agregat terlalu sering menjadi headline, padahal keputusan harus didasarkan pada data/eksekusi yang valid, worst-year, frekuensi, biaya nyata, dan risiko intraday funded.

## Status audit
- **TERBUKTI:** look-ahead pada keluarga session-impulse/recovery; biaya rollover merusak komponen H1-R1; beberapa bug engine/indexing/bar-shift; MRM closed-candle contamination.
- **KUAT DIDUKUNG:** selection/regime overfit pada banyak keluarga; baseline bid-only/flat-cost melebihkan daya guna strategi L80+H1-R1.
- **BELUM DIREKONSILIASI:** selisih detail R189 canonical versus replay bid/ask independen; perlu pencocokan trade-by-trade pada raw data dan timestamp convention yang sama.
- **BELUM BOLEH DISIMPULKAN:** bahwa tidak ada edge yang mungkin ditemukan; bahwa semua eksperimen lama invalid; atau bahwa R189 pasti akan lolos challenge.

## Langkah audit berikutnya (bukan pencarian strategi baru)
1. Bangun ledger seluruh keluarga/ronde: lineage, data, timestamp/timezone, engine hash, biaya, status causal, periode seleksi/forward, alasan reject.
2. Rekonsiliasi R189 trade-by-trade terhadap data bid/ask asli; cari titik pertama ketika sinyal, entry, exit, spread, atau net P/L berbeda.
3. Tandai setiap hasil dengan salah satu status: REPRODUCIBLE, INVALID, NON-REPRODUCIBLE, atau VALID-BUT-FAILED.
4. Baru setelah ledger dan R189 discrepancy selesai, putuskan apakah ada baseline yang layak diuji lanjut. Jangan mulai strategi baru sebelum ini selesai.
