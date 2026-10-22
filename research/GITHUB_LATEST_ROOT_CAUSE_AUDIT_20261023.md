# Audit akar penyebab kegagalan eksperimen terbaru — GitHub
Tanggal: 2026-10-23
Cakupan yang benar-benar diperiksa: branch `local-backtest/market-response-model-v1-20261023`, ledger `MASTER_SEARCH_LEDGER_R251_R310.csv` (55 baris eksperimen), laporan R302–R310, process repair R311, integration/source audits R312, serta MRM V1/V2 dan closure-clean replay.
Sumber: hanya artefak yang saat ini ada di GitHub pada branch tersebut. ZIP pembanding pengguna bukan dasar temuan di bawah.

## Putusan eksekutif

**Akar masalah terbesar bukan satu bug dan bukan sekadar spread. Sampai bukti terbaru yang tersimpan di GitHub, kita belum menemukan edge yang positif setelah eksekusi realistis. Di saat yang sama, proses riset berkali-kali menambah eksperimen sebelum sistem evaluasi funded dan reproduksibilitas lengkap siap.** Kedua hal ini terjadi bersamaan.

- Tidak ada kandidat yang dipromosikan sebagai funded-ready.
- Kandidat terbaru yang menguji sinyal ekonomi, R302–R310, semuanya gagal atau berhenti pada gerbang data/sampel.
- MRM V1 dan V2 juga gagal; V1 awal terkontaminasi data pasar tutup, lalu tetap negatif setelah koreksi.
- R311/R312 adalah perbaikan infrastruktur, bukan bukti bahwa ada strategi yang lolos.
- Data 2017–2025 telah dipakai berulang kali oleh banyak eksperimen; hasil dari periode tersebut bukan lagi holdout program-level yang bersih.
- Reproduksibilitas GitHub belum tuntas untuk beberapa eksperimen karena runner dan ledger transaksi lengkap tidak tersimpan sebagai file repo biasa.

## 1. Bukti langsung dari eksperimen terbaru

### R302 — XAUUSD PM auction-window fade: GAGAL
- Discovery: 179 trade, PF_R 0.640, −32.96R pada biaya tambahan $0.30/oz.
- Validation: 208 trade, PF_R 0.730, −26.99R.
- Validation tetap −14.57R bahkan dengan biaya tambahan $0/oz; delay 15 menit memperburuk hasil.
- Diagnosis: arah/kondisi yang diuji tidak menghasilkan expectancy positif; bukan sekadar tambahan biaya.

### R303 — EURUSD spread-shock reversion: GAGAL
- Pada +1 pip tambahan: discovery 739 trade, PF_R 0.769, −93.41R; validation 66 trade, PF_R 0.777, −7.36R.
- Bahkan +0.5 pip tambahan membuat kedua periode negatif. Dengan biaya tambahan nol, hasil hanya sedikit positif; T+10 juga negatif.
- Validation cuma 66 trade, di bawah gate 100; audit pra-outcome hanya menemukan 76 event eligible sebelum overlap.
- Diagnosis: kandidat sangat cost-fragile, expectancy utama negatif, sampel validation kurang, dan artefak kode/ledger lengkap belum tersimpan di repo.

### R304 — FX local-session currency depreciation: GAGAL
- Pada +1 pip: discovery 2.059 trade, PF_R 0.926, −42.39R; validation 513 trade, PF_R 0.889, −15.56R.
- Tanpa biaya tambahan hanya marginal positif; +0.5 pip sudah membalik kedua periode menjadi negatif. Mirror arah juga negatif.
- Hanya 1 dari 4 tahun discovery yang positif.
- Diagnosis: efek akademik yang memotivasi hipotesis tidak berpindah menjadi edge yang dapat dieksekusi pada feed ini.

### R305/R306 — EURUSD ke XAUUSD common-USD transmission: keduanya GAGAL
- R305 pada biaya utama: discovery −6.974R (12.338 trade; PF_R 0.340), validation −4.486R (14.201 trade; PF_R 0.536).
- R306: discovery −2.059R (3.322 trade; PF_R 0.304), validation −1.399R (4.004 trade; PF_R 0.497).
- Keduanya juga negatif ketika biaya tambahan ditetapkan nol; bootstrap validation sepenuhnya negatif.
- Diagnosis: hubungan arah yang diuji salah/tidak ada dalam bentuk yang dibekukan. Filter underreaction memperkecil sampel tetapi tidak menghasilkan edge. Ini bukan kegagalan yang bisa diperbaiki hanya dengan slippage lebih murah.

### R307/R308 — weekday drift / weekend carry: GAGAL dengan dua alasan berbeda
- R307: 1.028 trade discovery dan 1.281 validation/diagnostic; pada +1 pip hasil −74.49R / PF_R 0.755 dan −53.46R / PF_R 0.854. Keduanya negatif bahkan pada biaya tambahan nol; bootstrap validation CI seluruhnya di bawah nol.
- R308: hanya dua gap aktif Friday-to-Monday yang memenuhi definisi di seluruh 2017–2025, bukan 150 trade validation yang disyaratkan. Tidak ada PnL yang dihitung.
- Diagnosis: R307 gagal secara ekonomi; R308 gagal karena data/event coverage dan sampel, sehingga R308 tidak membuktikan weekend carry mustahil maupun menguntungkan.

### R309/R310 — EURUSD/XAUUSD relative-value snapback: keduanya GAGAL
- R309 pada biaya utama: discovery 3.576 trade, −991.56R, PF_R 0.338; validation/diagnostic 3.665 trade, −644.44R, PF_R 0.512.
- R310 memperbaiki geometri exit agar TP/SL memakai pergerakan residual pasca-entry yang nyata, bukan sekadar z-score rolling yang menormalisasi saat kejutan menua. Hasilnya relatif lebih baik, tetapi tetap negatif: discovery 3.003 trade, −804.58R, PF_R 0.553; validation/diagnostic 3.125 trade, −544.15R, PF_R 0.681.
- Keduanya negatif di semua sembilan tahun yang diskor dan juga negatif dengan biaya tambahan nol.
- Diagnosis: exit R309 punya kelemahan konseptual, tetapi memperbaiki exit saja tidak menciptakan edge. R310 adalah bukti langsung bahwa koreksi engineering dapat memperbaiki angka tanpa mengubah kandidat menjadi profitable.

### MRM V1/V2 — machine learning: GAGAL
- V1 awal memasukkan static/flat market-closure candles ke lookback fitur dan jalur label karena hanya memeriksa kesinambungan timestamp. Itu bug data-preparation nyata.
- Setelah closure-clean replay, ranking model runtuh: Spearman train +0.262, validation −0.038, forward −0.015. Policy forward 2022–2025: 1.751 trade, −1.795,7 pip, PF 0.821. Menghapus tambahan biaya 0,5 pip masih −920,2 pip dan PF 0.903 dengan spread BID/ASK tetap dihitung.
- V2 membuang fitur spread untuk menguji prediksi harga kotor, tetapi korelasi skor juga negatif pada validation dan forward; selected stream forward −4.039 pip/PF 0.841 pada biaya utama.
- V2 punya cacat tambahan: midpoint high/low dibuat dengan merata-ratakan BID dan ASK extrema yang belum tentu terjadi pada saat yang sama; maka label high/low tersebut bukan midpoint ekstrem yang benar-benar teramati.
- Diagnosis: V1 mempunyai bug data awal dan tetap gagal setelah koreksi. V2 bukan validasi independen yang bersih; hasilnya juga gagal, dengan cacat label yang membatasi interpretasi. Jangan memakai angka V1 awal sebagai bukti edge.

## 2. Temuan lintas eksperimen: penyebab sistemik

### A. Edge sinyal negatif adalah penyebab dominan pada kandidat terbaru
R305–R310 dan R302 negatif bahkan dengan biaya tambahan nol setelah spread quote aktual; R307 juga negatif pada nol biaya tambahan; MRM V1 tetap negatif ketika tambahan 0,5 pip dihapus. Jadi kesimpulan “semua gagal hanya karena spread” tidak sesuai bukti. Pada kandidat tertentu spread/slippage adalah pembunuh tambahan, tetapi pada banyak kandidat expectancy dasarnya sudah negatif.

### B. Biaya tetap membuat kandidat tipis menjadi tidak dapat diperdagangkan
R303 dan R304 tampak hampir impas pada biaya tambahan nol, lalu negatif pada +0,5 pip. R251 juga berubah negatif dengan tambahan hanya +0,5 pip. Sebagian indeks memakai BID-only M5 dan biaya basis-point yang dimodelkan, bukan spread/commission fill yang benar-benar teramati. Karena itu beberapa angka biaya bukan biaya broker terverifikasi.

### C. Pemilihan berulang mengotori periode validasi
Banyak eksperimen memakai discovery 2017–2020 dan validation 2021; batch lain menggunakan 2021–2025 yang sudah berulang kali ditinjau. Dengan banyak keluarga diuji pada data yang sama, satu hasil validation positif bukan bukti independen lagi. Ini memperbesar risiko selection bias pada tingkat program meskipun satu eksperimen tertentu dikunci sebelum PnL.

### D. Cacat data/implementasi memang nyata, tetapi bukan penjelasan universal
- R296 salah menganggap static Sunday quote sebagai reopening aktif; invalid dan diganti R297.
- R257 punya masalah eligibility/coverage; R281 memperbaiki engine, tetapi fixed grid tetap kalah pada discovery dan validation sampelnya kurang.
- R282/R308 tidak mempunyai event reopening yang cukup pada data/definisi terdaftar; ini masalah data/sampel, bukan bukti ekonomi.
- MRM V1 closure contamination dan MRM V2 midpoint-extrema approximation adalah cacat yang spesifik pada keluarga itu.
- Karena itu, sebagian hasil lama memang invalid; sebagian lainnya merupakan tes valid yang kalah. Dua kelas ini tidak boleh disatukan.

### E. Sistem pencarian tidak mengukur tujuan funded sejak awal
R311 memperbaiki simulator equity-path dan lulus 8/8 tes sintetis; R312 menambahkan adapter BID/ASK dan smoke tests. Namun itu belum membuat satu kandidat funded-ready. Replay R312 menggunakan R298 yang sudah gagal hanya sebagai tes integrasi: pada risk 0,5%, satu path melanggar max loss di Phase 1 setelah 26 trade ditutup; pada 1% juga melanggar max loss, dan 1,5% melanggar daily loss. Itu bukan probabilitas pass, dan tidak boleh dipakai untuk menyatakan bahwa strategi apa pun telah diuji funded secara lengkap.

### F. Reproduksibilitas artefak belum konsisten
- R302 mencatat ledger trade, eligibility audit, dan audit seluruh biaya/delay sebagai file lokal yang belum dipindahkan ke repo.
- R303 menyatakan exact runner dan row-level ledger belum diarsipkan.
- R304 dan R305/R306 juga menyatakan row-level outputs/runner belum lengkap di repo.
- R309/R310 sama: full runner dan row-level trade ledgers belum tersimpan sebagai file biasa.
- R312 berhasil mencocokkan metrik agregat R298 dengan report, tetapi hash/isi ledger rekonstruksi tidak sama baris demi baris dengan CSV repo yang ada.
Artinya laporan ringkas cukup untuk mencatat verdict saat ini, tetapi belum semua hasil dapat dibangun ulang secara independen hanya dari isi repo.

## 3. Apa yang sebenarnya salah dalam cara kerja proyek?

1. Kita terus menghasilkan hipotesis baru meskipun audit proses sudah meminta jeda sampai ledger, scoring contract, dan funded replay tersambung.
2. Kita menilai banyak eksperimen lewat PF/expectancy historis, tetapi tidak konsisten menyelesaikan path ekuitas dua fase yang memasukkan floating loss, DLL/MLL, biaya aktual, timezone, delay manual, dan batas waktu proyek.
3. Kita punya campuran unit hasil (pip, R, basis point, USD/oz) dan kualitas data (paired BID/ASK versus BID-only). Ini menghalangi peringkat lintas kandidat yang adil tanpa normalisasi ke account-path yang sama.
4. Kita mengulang pengujian pada periode yang sama, sehingga “validation” per eksperimen bukan holdout independen tingkat program.
5. Kita tidak selalu mengarsipkan runner dan ledger lengkap; akibatnya hasil tidak selalu dapat direproduksi dari GitHub saja.
6. Perbaikan engineering kadang hanya memperbaiki atau mengoreksi angka, tetapi tidak membuat expectancy positif. R310 dan MRM V1 corrected replay adalah contoh nyata.

## 4. Putusan audit

- **TERBUKTI — ekonomi/sinyal:** kandidat R302–R310 dan MRM V1/V2 yang diuji tidak menunjukkan edge positif yang tahan pada gate masing-masing.
- **TERBUKTI — proses:** pencarian strategi berlangsung sebelum jalur funded-readiness dan reproduksibilitas lengkap terhubung; periode sejarah telah terkontaminasi oleh pengujian berulang.
- **TERBUKTI — data/implementasi:** setidaknya R296, R257, R282/R308, MRM V1 dan label MRM V2 memiliki masalah kualitas/coverage yang spesifik; tidak semua eksperimen dapat diperlakukan sebagai tes ekonomi valid.
- **TERBUKTI — biaya:** sejumlah kandidat marginal runtuh dengan sedikit biaya tambahan; banyak kandidat lain sudah negatif tanpa biaya tambahan ekstra.
- **BELUM TERBUKTI:** bahwa seluruh ide trading mustahil menghasilkan edge; atau bahwa R189 pasti valid/invalid pada semua feed.
- **STATUS PROYEK:** NO-GO untuk funded. Belum ada kandidat yang lolos semua gerbang dan belum ada estimasi pass-probability yang sah untuk strategi kandidat.

## 5. Langkah korektif yang mengikuti bukti, bukan ide strategi baru

1. Pertahankan semua verdict gagal; jangan retune keluarga yang sudah ditutup pada periode yang sama.
2. Jangan jalankan strategi baru sebelum satu kandidat terpilih dapat direproduksi end-to-end dari data GitHub hingga trade ledger dan chronological equity path.
3. Selesaikan perbedaan baris-per-baris pada ledger R298/R312 dan simpan runner/ledger lengkap untuk hasil yang masih dijadikan referensi.
4. Satukan semua hasil pada satu kontrak scoring account-level; semua kandidat harus dinilai dengan aturan funded, biaya, delay, risiko floating, dan horizon waktu yang sama.
5. Jangan membuka XAUUSD 2026 yang diproteksi untuk memilih parameter. Gunakan hanya satu kali untuk kandidat yang telah dikunci dan lolos seluruh gate sejarah.
6. Baru setelah data/engine/ledger cocok dan kandidat menunjukkan expectancy positif setelah biaya, jalankan minimal 10.000 jalur challenge dua fase. Tes sintetis atau satu jalur tidak boleh disebut probabilitas lolos.

## Artefak utama yang menjadi dasar
- [MRM V1 closure-clean replay](MRM_V1_CLOSED_MARKET_CLEAN_REPLAY.md)
- [MRM V2 final report](MRM_V2_FINAL_REPORT.md)
- [R302 final report](R302_FINAL_REPORT.md) dan [ledger reassembly](R302_LEDGER_REASSEMBLY.md)
- [R303 final report](R303_FINAL_REPORT.md)
- [R304 final report](R304_FINAL_REPORT.md)
- [R305/R306 batch report](R305_R306_BATCH_FINAL_REPORT.md)
- [R307/R308 batch report](R307_R308_BATCH_FINAL_REPORT.md)
- [R309/R310 batch report](R309_R310_BATCH_FINAL_REPORT.md)
- [R311 process repair](R311_PROCESS_REPAIR.md)
- [R312 stop/unblock protocol](R312_STOP_AND_UNBLOCK_20261020.md), [ledger replay audit](R312_LEDGER_REPLAY_AUDIT.json), [source audit](R312_XAU_SOURCE_AUDIT.json)
- [R251–R310 master ledger](MASTER_SEARCH_LEDGER_R251_R310.csv)


## 6. Process contradiction found in the newest chronology

R312 dated 2026-10-20 explicitly orders a pause on all new strategy backtests until the reproducible real-data adapter, full event path, and challenge replay are complete. The MRM V1/V2 signal experiments were nevertheless run on 2026-10-23, before the report documents those gates as complete. The MRM reports themselves confirm that the candidate still was not fully repository-reproducible and no FundedNext challenge path was run.

This is a direct process-control failure: the project identified the correct stop condition, but did not enforce it. The MRM findings remain valid evidence against those tested models, but running more signal research before closing the R312 prerequisites added more negative results without solving the stated blocker. The next step must follow the pause criteria rather than open another signal family.


## 7. Local recheck of the remaining legacy R189 candidate — 2026-10-23

The raw GitHub Actions artifact `EURUSD-M1-Dukascopy-BID-ASK-2016-2025` (artifact ID `11959096102`) was retrieved into the current local session and checked against the hashes in the committed R189 report.

| Input | Rechecked value | Result |
|---|---|---|
| BID rows | 4,415,493 | Match saved audit |
| ASK rows | 4,415,493 | Match saved audit |
| BID SHA-256 | `b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc` | Match |
| ASK SHA-256 | `52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b` | Match |
| Intrabar replay trades | 1,673 | Match saved report |
| Full-period PF / net pips at +1 pip | 1.082 / +462.5 | Match saved report |
| 2021–2025 PF / net pips at +0.5 pip | 1.284 / +674.8 | Match saved report |
| 2021–2025 PF / net pips at +1 pip | 1.114 / +291.3 | Match saved report |

The independent local replay used the committed strategy and execution function logic. It reproduced the headline metrics to rounding precision. It was assembled as a local verification script from the fetched source logic rather than invoking the checked-in Python file byte-for-byte; treat this as a successful logic-level replay, not a cryptographically identical build invocation.

### Manual latency decision

The local latency replay also matched the saved R189 sensitivity results:

| Additional delay after ideal next-bar fill | Extra cost beyond observed BID/ASK | Forward PF | Forward net pips | 95% weekly-bootstrap CI |
|---:|---:|---:|---:|---:|
| 1 minute | +0.5 pip | 1.225 | +544.1 | [+0.404, +3.794] |
| 3 minutes | +0.5 pip | 1.212 | +509.6 | [+0.287, +3.646] |
| 5 minutes | +0.5 pip | 1.071 | +181.5 | [-0.444, +1.849] |
| 5 minutes | +1.0 pip | 0.926 | -203.0 | [-1.997, +0.348] |

**Updated decision: R189 is reproducible at the headline-metric level but remains NOT PASSED for the user's several-minute manual-phone execution.** At a five-minute extra delay, the +0.5-pip case falls below the project's PF 1.10 floor and its weekly interval includes zero; at +1 pip the point estimate is loss-making. This confirms an execution-horizon mismatch, not a data-checksum problem.

This does not change the project-wide verdict: no current candidate has demonstrated all historical, execution, account-path, challenge-rule, and pass-probability gates. Do not retune R189 on these reused dates.
