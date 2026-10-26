# R333 — Preregistrasi Terkunci: IDX Small-Cap Daily

**Branch:** `research/r333-idx-smallcap-daily`  
**Parent:** none — new family `IDX_SMALLCAP_DAILY`  
**Status dokumen:** dikunci sebelum perhitungan PnL; penelitian dihentikan pada Gate Akuisisi Tahap 0.  
**Tanggal cutoff OOS yang diniatkan:** 2026-10-26, inklusif.  
**Tidak ada PF, win rate, expectancy, R, atau PnL yang dihitung untuk R333.**

## Hipotesis kausal

Saham kecil punya cakupan analis dan institusi lebih sedikit, jadi reaksi harga terhadap informasi lebih lambat dan bisa diukur dari raw price + volume. Ini bisa gagal, dan itu hasil valid.

Hipotesis ini hanya mekanisme yang diuji, bukan fakta yang diasumsikan sudah terbukti. OHLCV saja tidak mengidentifikasi berita/informasi secara langsung; jika strategi hanya mengukur momentum pasar umum, Gate beta wajib menolaknya.

## 0. Urutan data dan aturan STOP

Sumber tunggal yang dipilih a priori: **Yahoo Finance, seri saham berakhiran `.JK`, OHLCV harian via `yfinance` di Python/Colab**. Tidak ada fallback ke sumber data lain untuk R333.

Sumber dokumentasi:
- `yfinance.download`: https://ranaroussi.github.io/yfinance/reference/api/yfinance.download.html
- `yfinance.Ticker.history`: https://ranaroussi.github.io/yfinance/reference/yfinance.price_history.html
- IDX, jam/mekanisme, biaya pasar, short selling, settlement: https://www.idx.id/id/produk-layanan/jam-dan-mekanisme-perdagangan/
- KSEI settlement: https://www.ksei.co.id/en/service-support/service-type/settlement-of-securities-transactions-services
- Ajaib fee schedule (contoh broker yang spesifik): https://ajaib.co.id/biaya
- CGS International minimum age FAQ: https://www.cgsi.co.id/help/faq-opening-account?lang=ID
- Tick/fraksi dan satuan lot pada IDX: halaman mekanisme IDX di atas.
- Perubahan ARB efektif 20 Oktober 2026 (berlaku sampai 31 Desember 2026 menurut sumber media yang mengutip keputusan BEI): https://katadata.co.id/finansial/bursa/6ad6bb9113d26/bei-ubah-lagi-aturan-arb-saham-rp-14-bisa-turun-ke-rp-1

### Hasil fakta Tahap 0 yang berhasil diverifikasi

| Item | Fakta / status |
|---|---|
| Pustaka dan mode pengambilan | Dokumentasi `yfinance` mendukung data harian. Dokumentasinya menyebut `auto_adjust=True` sebagai default saat ini; parameter harus ditetapkan eksplisit. `actions=True` meminta data dividen dan stock split. |
| Pilihan OHLCV yang terkunci jika input lolos | Minta `auto_adjust=False`, `actions=True`, dan pertahankan nilai raw OHLCV beserta metadata corporate action; jangan bergantung pada default pustaka. |
| Periode pertama/terakhir yang benar-benar diunduh | **Tidak tersedia** — tidak ada cache yang berhasil diterima. |
| Jumlah baris aktual | **Tidak tersedia** — tidak boleh mengisi dari tebakan. |
| SHA-256 cache | **Tidak tersedia** — file data tidak pernah berhasil diunduh, jadi tidak ada checksum yang sah. |
| Delisted / survivorship | Yahoo Finance tidak memberi jaminan roster point-in-time yang lengkap untuk seluruh saham IDX yang aktif maupun delisted. Universe dari ticker aktif saja akan menimbulkan survivorship bias; tidak dapat dianggap layak untuk klaim alpha historis 2016–2026. |
| Split/dividen aktual pada cache | Tidak bisa diaudit tanpa cache. Konfigurasi yang diniatkan mengambil harga raw dan corporate actions; data harus tetap dianggap **data inadequate** karena corporate-action completeness dan sejarah saham beredar tidak terverifikasi. |
| Akuisisi 1 | Endpoint chart Yahoo Finance tidak dapat diakses dari lingkungan eksekusi ini; tidak ada byte OHLCV yang diterima. |
| Akuisisi 2 | Halaman histori Yahoo Finance mengembalikan HTTP 429 (Too Many Requests); tidak ada byte OHLCV yang diterima. |
| Keputusan data | **STOP.** Dua percobaan akuisisi pada sumber yang sama gagal. Tidak ada fallback, sumber kedua, proxy data, atau bypass. |

Dua kegagalan akses di atas membuktikan bahwa akuisisi tidak berhasil di sesi ini; itu **tidak** membuktikan Yahoo selalu gagal di Colab. Namun syarat Tahap 0 mengharuskan data aktual yang dapat disimpan dan diaudit, bukan dugaan bahwa unduhan mungkin berhasil di lingkungan lain. Tidak ada data yang akan disimulasikan atau direkayasa untuk melanjutkan tahap ini.

### Biaya dan mekanika pasar yang sudah diverifikasi (bukan konfirmasi akun live)

- Contoh biaya total Ajaib untuk transaksi saham yang dipublikasikan: beli **0,1513%** dan jual **0,2513%**; masing-masing mencakup biaya broker, levy yang tercantum, PPN biaya broker dan PPh final jual. Ini adalah jangkar biaya publik spesifik broker, bukan biaya yang telah diverifikasi pada akun pengguna.
- IDX menyebut biaya transaksi bursa (di luar komisi Anggota Bursa): **0,0433% beli** dan **0,1433% jual** pada tabel pasar reguler; komisi broker nasabah belum termasuk.
- Pasar reguler diselesaikan **T+2**.
- Satuan perdagangan pasar reguler/tunai: **1 lot = 100 saham**. Minimum rupiah order bukan angka tetap; secara nominal bergantung pada harga saham dan dibulatkan ke lot penuh.
- Halaman IDX yang kini dipublikasikan menyebut fraksi harga saat ini di kelompok harga: di bawah Rp200 = Rp1; Rp200–di bawah Rp500 = Rp2; Rp500–di bawah Rp2.000 = Rp5; Rp2.000–di bawah Rp5.000 = Rp10; Rp5.000 ke atas = Rp25. Aturan perlu dipetakan per tanggal untuk periode historis; jangan terapkan tabel terkini ke seluruh 2016–2026.
- Per 20 Oktober 2026, ketentuan ARB untuk saham papan utama/pengembangan/ekonomi baru berubah lagi untuk periode 20 Oktober–31 Desember 2026; saham Rp11–Rp14 mempunyai ARB nominal Rp1, saham Rp15–Rp200 ARB 7%, >Rp200–Rp5.000 ARB 7%, dan >Rp5.000 ARB 7%; ARA tetap berbeda menurut kelompok harga. Papan Akselerasi dan Pemantauan Khusus memiliki perlakuan tersendiri. Karena perubahan aturan terjadi, simulasi harus memakai kalender aturan historis dan tetap mencatat risiko antrean/limit-up/limit-down.
- Short selling **tidak dipakai** dalam hipotesis R333 (long-only dikunci a priori). Short selling IDX mensyaratkan rekening khusus, efek yang masuk daftar short-selling, serta Anggota Bursa berlisensi; karena itu tidak realistis untuk menganggap semua small-cap bisa di-short.
- Syarat umur adalah spesifik broker. Contoh CGS International yang dipublikasikan menyebut minimum **17 tahun dan sudah memiliki KTP**. Ini bukan verifikasi bahwa seluruh broker memakai syarat yang sama, atau bahwa akun pengguna sudah memenuhi seluruh syarat live.

### Model biaya yang terkunci jika data suatu saat dinyatakan layak dalam eksperimen independen baru

Satuan pelaporan adalah basis points (bps) dari notional entry; semua laporan memakai satuan yang sama. Jangkar broker dasar yang direncanakan: fee beli 15,13 bps dan fee jual 25,13 bps dari notional masing-masing transaksi. Biaya round trip dinyatakan sebagai:
`cost_bps_entry = 15.13 + 25.13 × (exit_price / entry_price)`.

Stress level mengalikan semua biaya transaksi variabel dalam rumus tersebut dengan **1,5× dan 2×**. OHLCV Yahoo tidak menyediakan spread bid-ask yang dapat diamati; spread nyata tidak boleh diklaim sudah terukur. Jika hanya bisa digunakan proxy satu fraksi harga per sisi, proxy itu wajib diberi label *proxy*, tidak boleh dianggap spread aktual dan tidak akan cukup untuk lolos G11 tanpa bukti tambahan. Untuk R333 ini tak ada biaya yang benar-benar diterapkan karena STOP terjadi sebelum backtest.

## 1. Universe, urutan, dan pencegahan survivorship

Aturan berikut terkunci sebagai desain awal, namun **belum dieksekusi** dan belum boleh dianggap menghasilkan universe layak:

1. Universe konseptual adalah seluruh saham biasa yang tercatat di IDX pada setiap tanggal historis, termasuk efek yang kemudian delisted; keluarkan ETF, rights, waran, obligasi, dan instrumen non-common-equity.
2. Definisi small-cap adalah kapitalisasi pasar yang berada pada atau di bawah persentil ke-30 cross-section IDX pada tiap tanggal rebalance bulanan, memakai harga penutupan dan **jumlah saham beredar yang diketahui pada tanggal tersebut** (point-in-time). Dilarang memakai shares outstanding terkini secara retroaktif.
3. Filter likuiditas: median nilai transaksi harian `close × volume` selama 60 sesi bursa lengkap sebelumnya minimal **Rp500 juta/hari**; minimal 54 dari 60 sesi memiliki data valid dan volume positif. Hanya informasi yang tersedia hingga akhir sesi sebelumnya yang boleh memengaruhi kelayakan.
4. Rebalance universe bulanan dengan aturan yang sama; snapshot konstituen dibentuk sebelum return bulan berikutnya diproses. Saham tidak boleh dikeluarkan karena PnL buruk. Delisting wajib dikelola dengan aturan terminal return/exit yang terdokumentasi; data hilang tidak boleh diperlakukan sebagai exit di harga yang menguntungkan.
5. Urutan tetap dedup: urutkan kandidat berdasarkan median nilai transaksi 60 sesi, tertinggi dahulu; jika seri, ticker ascending. Korelasi memakai return harian discovery 2016–2020 saja dan hanya data yang tersedia pada periode discovery. Jika `abs(correlation) > 0.70` terhadap salah satu saham yang lebih dahulu diterima, kandidat berikutnya dilewati. Korelasi tidak dihitung dengan informasi forward/OOS. Syarat minimum 500 pasangan return valid; jika tidak terpenuhi, kandidat tidak dapat lolos pemeriksaan data.
6. **Data gate:** jika roster saham delisted, jumlah saham beredar point-in-time, sektor point-in-time, corporate actions, atau nilai transaksi historis tidak dapat diverifikasi dari sumber Yahoo yang sama, hasilnya `data inadequate` dan R333 berhenti. Dilarang mengganti data dengan feed lain untuk menyelamatkan eksperimen ini.

## 2. Satu aturan sinyal terkunci (tidak ada pencarian parameter)

Aturan berikut didaftarkan untuk dokumentasi lengkap, tetapi **tidak dijalankan** karena STOP Tahap 0. Ini bukan strategi yang sudah diuji.

- Long-only; satu posisi aktif maksimal per saham.
- Pada close hari `i`, trigger hanya jika semua syarat berikut benar:
  1. raw close-to-close return hari `i` berada di antara **+0,50% dan +3,00%**;
  2. `(close_i - low_i) / (high_i - low_i) ≥ 0.80` (close di bagian atas range); jika range nol, tidak ada sinyal;
  3. volume hari `i` ≥ **2,0 × median volume 20 sesi sebelumnya**, dengan hari `i` dikecualikan;
  4. `close_i ≤ max(high_{i-20}, …, high_{i-1})`: bukan breakout high 20 sesi, supaya tes bukan pengulangan breakout konvensional;
  5. saham lolos universe dan likuiditas hanya berdasarkan data yang telah diketahui saat itu.
- Sinyal hanya sah setelah bar `i` selesai; entry yang direncanakan pada open hari bursa `i+1`. Dilarang mengisi entry di close `i`.
- Entry dibatalkan jika open berikutnya ≤ low hari sinyal atau stop tidak berada di bawah entry; tidak melakukan pembelian retroaktif.
- Initial stop = low hari sinyal. Target = entry + **2 × (entry − stop)**. Tidak ada trailing stop.
- Gap menembus stop: fill pada open sesi yang melampaui stop, bukan pada level stop.
- Jika stop dan target tersentuh di hari yang sama dan OHLC harian tidak menentukan urutan: **stop menang**.
- Time-stop: keluar pada close setelah **10 sesi perdagangan lengkap** jika stop/target belum menyentuh lebih dulu.
- Tidak ada piramida, averaging down, leverage, atau short.

### Sizing dan kelayakan eksekusi

- Risiko awal nominal per posisi = **0,5% ekuitas** berdasarkan jarak entry-stop, dengan maksimum gross exposure 20% ekuitas per saham.
- Batasi nilai posisi pada nilai yang lebih kecil dari (a) batas sizing berdasarkan stop, (b) 20% ekuitas, (c) 1% median nilai transaksi harian 60 sesi sebelumnya, dan (d) 1% volume hari sebelumnya pada harga entry.
- Bulatkan ke bawah ke lot 100 saham. Jika tidak cukup untuk membeli satu lot, tidak ada order. Tidak ada saham yang dipilih/dibuang berdasarkan hasil trade.
- Laporkan simulasi modal Rp1 juta dan Rp10 juta sebagai cek kapasitas; kapasitas realistis tidak boleh disimpulkan dari omzet tanpa spread, antrean, dan batas auto-rejection.
- Yahoo OHLCV tidak merekam spread/antrean order. Jika input yang sama tidak dapat memberi bukti untuk biaya spread yang layak atau eksekusi pada limit-up/down, Gate G11 gagal; jangan menyebut hasil siap diperdagangkan live.

## 3. Periode dan baseline yang terkunci

- Discovery: **2016-01-01 sampai 2020-12-31**.
- Forward: **2021-01-01 sampai 2025-12-31**.
- OOS satu kali: **2026-01-01 sampai 2026-10-26**, inklusif, cutoff tunggal.
- Krisis 2020 tetap ada di tabel discovery; 2022 tetap ada dalam forward. Semua tahun kalender wajib dirinci. Tidak retune setelah melihat forward/OOS.
- Baseline 1: equal-weight buy-and-hold basket dari konstituen point-in-time yang sama, dengan rebalance bulanan memakai aturan universe yang sama, tanpa filter sinyal. Biaya transaksi yang relevan diterapkan.
- Baseline 2: IHSG (`^JKSE`) untuk return pasar. IHSG price index tidak boleh disebut total return tanpa bukti dividend reinvestment.
- Gate beta: strategi harus mengungguli baseline basket bersih setelah biaya dan menghasilkan intercept/alpha beta-adjusted positif; jika hasilnya dijelaskan oleh eksposur pasar small-cap dan tidak ada excess return versus matched basket, reject. Baseline harus memakai timestamp dan periode observasi yang sama.

## 4. Gate biner

Satu gate gagal berarti putusan strategi untuk klaim tersebut adalah **GAGAL**. STOP karena input tidak layak dicatat sebagai `data inadequate`, bukan bukti bahwa hipotesis alpha sendiri terbukti salah.

- **G1 Determinisme:** dua run identik dari cache dan konfigurasi yang sama; semua metrik sama sampai 3 desimal.
- **G2 Truncation/no look-ahead:** sinyal dan stop dihitung ulang hanya dari data terpotong sampai bar `i`; sama persis dengan hitungan versi penuh. Gagal berarti stop sebelum melihat PF.
- **G3 Forward:** pooled forward `n ≥ 150` dan PF ≥ **1.15** pada biaya **1,5×**.
- **G4 Discovery:** pooled PF ≥ **1.00** pada biaya realistis.
- **G5 Year stability:** setiap tahun forward terburuk PF ≥ **0.80**; tampilkan semua tahun, termasuk 2020 dan 2022 dalam periode yang sesuai.
- **G6 Neighborhood:** uji tetangga yang sudah dikunci untuk setiap parameter kunci: volume multiple 1,5×/2,0×/2,5×; batas bawah return 0,25%/0,50%/0,75%; batas atas return 2,5%/3,0%/4,0%; close-location 0,70/0,80/0,90; RR 1,5/2,0/2,5; time-stop 7/10/13 sesi. Semua kombinasi tetangga yang dipreregistrasi wajib pooled forward PF ≥ **1.00**; ini uji ketahanan, bukan izin memilih konfigurasi baru.
- **G7 Leave-one-sector-out:** buang satu sektor setiap kali berdasarkan klasifikasi point-in-time; PF ≥ **1.05** pada setiap iterasi. Jika sektor point-in-time tidak tersedia, data gate gagal.
- **G8 Bootstrap:** 10.000 circular moving-block bootstrap resampling blok 4 minggu atas forward, random seed **333**; batas bawah interval kepercayaan 95% mean R per trade harus **> 0**.
- **G9 Beta/baseline:** excess return net terhadap matched equal-weight basket harus positif dan alpha beta-adjusted tidak boleh dijelaskan hanya oleh IHSG/small-cap beta.
- **G10 PF tinggi:** bila PF > **1.40** selepas biaya, hentikan promosi dan wajibkan audit kausalitas independen sebelum klaim edge. PF tinggi sendiri tidak meloloskan strategi.
- **G11 Likuiditas/eksekusi:** ukuran posisi Rp1 juta dan Rp10 juta memenuhi batas partisipasi di atas; spread bid-ask benar-benar dimodelkan dengan data yang dapat dipertanggungjawabkan; limit-up/down, gap, lot, tick size dan biaya konsisten. Broker fee live, slippage, dan risiko ARA/ARB tetap memerlukan verifikasi akun nyata.

### Metrik wajib kalau pengujian suatu saat berstatus eligible

Laporan harus memuat breakdown semua tahun dan periode: n trade, PF pada biaya dasar/1,5×/2×, expectancy R per trade, total R, t-statistic, bootstrap CI, maximum simultaneous positions, maximum exposure, equity drawdown, baseline buy-and-hold basket, IHSG, sektor, biaya, spread proxy/aktual, jumlah sinyal yang ditolak karena lot, ARA/ARB, dan missing/corporate-action bars. Semua metrik harus menyebut jumlah observasi dan definisi; nol trade tidak boleh direkayasa menjadi PF.

## 5. Larangan dan disiplin

- Tidak memakai EMA, RSI, MACD, Bollinger, atau indikator turunan.
- Tidak mengulang keluarga breakout harian konvensional; aturan R333 didesain sebagai high-volume near-high non-breakout, tetapi status keluarga baru tetap mensyaratkan review registry sebelum eksperimen lain.
- Tidak sweep, tuning, menghapus saham setelah PnL, atau menyelamatkan strategi setelah satu gate gagal.
- Tidak memandang kenaikan PF relatif sebagai edge. Edge harus positif absolut setelah biaya dan melampaui baseline.
- Jangan mengklaim reproducible tanpa raw data, manifest, checksum, versi sumber dan runner yang disimpan.
- Tidak membuat klaim funded-ready. R333 adalah simulasi riset; perdagangan live tetap tunduk pada syarat umur broker, ketersediaan akun, mekanika bursa dan kemampuan eksekusi aktual.

## 6. Catatan audit sebelum hasil

Dokumen `R332_LOCKED_PREREGISTRATION.md` tidak ditemukan di `main`, tetapi template aktual berhasil ditemukan pada branch `research/r332-multi-asset-trend`; susunan R333 mengikuti disiplin template itu (lock sebelum hasil, sumber/cache dan checksum, fixed order/dedup, hard gates, laporan lengkap, binary verdict). File `SEARCH_GOVERNANCE_AND_SCORING_V1` tidak ditemukan pada `main` maupun pada branch template yang diperiksa; tidak ada klaim bahwa isinya telah dibaca. Kebijakan `RESEARCH_POLICY_BINARY_COMPOUNDING.md` ditemukan pada branch `local-backtest/r189-dukascopy-history` dan diterapkan: putusan biner, sumber dan ketidakpastian eksplisit, serta larangan menyebut data tidak layak sebagai bukti alpha gagal. R333 secara eksplisit mencatat keterbatasan akses ini.

**Preregistrasi ini dicatat tanpa menghitung PF.** Karena dua akses akuisisi Yahoo gagal dan histori point-in-time/delisted/shares-outstanding tidak dapat diverifikasi, tidak ada perhitungan strategi yang diizinkan pada R333 ini.
