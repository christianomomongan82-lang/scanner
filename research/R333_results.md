# R333 — Hasil dan Verdict

**VERDICT BINER: GAGAL — kelayakan/akuisisi data.**  
**Klasifikasi data: `data inadequate`.**  
**Ini bukan bukti `alpha gagal`, dan bukan hasil strategi tanpa edge. Tidak ada metrik edge yang dihitung.**

- Branch: `research/r333-idx-smallcap-daily`
- Parent: none; family baru `IDX_SMALLCAP_DAILY`
- Preregistrasi: [R333_LOCKED_PREREGISTRATION.md](R333_LOCKED_PREREGISTRATION.md)
- Prereg commit: `5ef12c40c1cd68e889c9632f08e19e1edab98065`
- Klarifikasi template R332: commit `e71f3845d1d0d5f47636f655d87dc7509b006b82`
- Batas penghentian: Tahap 0, akuisisi sumber tunggal Yahoo Finance setelah dua percobaan gagal.
- Perhitungan PF/PnL: **tidak dijalankan**.
- Runner backtest/ledger: **tidak dibuat/dijalankan** karena hard stop Tahap 0; membuat runner atau mencoba sumber lain akan melampaui aturan STOP yang dikunci.

## 1. Akuisisi sumber (dua percobaan, lalu STOP)

| Percobaan | Endpoint Yahoo Finance | Hasil aktual | Byte data / cache |
|---|---|---|---|
| 1 | [Yahoo chart endpoint BBCA.JK](https://query1.finance.yahoo.com/v8/finance/chart/BBCA.JK?range=max&interval=1d) | Tool browser mengembalikan “URL is not accessible”; tidak menerima payload harga. | Tidak ada |
| 2 | [Yahoo history BBCA.JK](https://finance.yahoo.com/quote/BBCA.JK/history) | HTTP **429 Too Many Requests** dari akses halaman. | Tidak ada |

Ini adalah dua kegagalan akses dari lingkungan eksekusi saat ini. Ini **tidak** membuktikan Yahoo selalu gagal di Google Colab. Tetapi R333 mensyaratkan cache data aktual yang dapat diperiksa—bukan asumsi bahwa unduhan akan berhasil di lingkungan berbeda. Sesuai preregistrasi, berhenti di sini: tidak ada percobaan ketiga, fallback, penggantian sumber, atau bypass.

## 2. Audit fakta data

| Wajib dicatat | Temuan |
|---|---|
| Tahun pertama dan terakhir pada data aktual | **Tidak tersedia** — dataset tidak berhasil diunduh. |
| Jumlah baris | **Tidak tersedia** — bukan nol; jumlahnya tidak diketahui karena tidak ada file. |
| SHA-256 cache | **Tidak tersedia** — tak ada cache yang byte-nya dapat di-hash. |
| Cache mentah/versioned di repo | Tidak ada, karena akuisisi gagal. |
| Raw vs adjusted untuk split/dividen | Dokumentasi `yfinance.download` menyatakan `auto_adjust=True` sebagai default; konfigurasi preregistrasi memaksa `auto_adjust=False` dan meminta `actions=True`. Karena payload aktual tidak ada, kelengkapan/semantik seri aktual belum dapat diaudit. |
| Kelengkapan saham delisted | Tidak dapat dibuktikan. Menggunakan roster ticker aktif saat ini akan menimbulkan survivorship bias. |
| Shares outstanding historis point-in-time | Tidak diverifikasi dari input yang tersedia; definisi small-cap historis dengan kapitalisasi pasar tidak bisa dipastikan. |
| Corporate actions & sektor point-in-time | Tidak dapat diverifikasi. |
| Spread bid-ask | Yahoo daily OHLCV tidak memberi bid/ask aktual dalam data yang diambil; tidak ada spread teramati yang bisa disimpan. |
| Keputusan | **`data inadequate`**. Tidak ada kesimpulan performa strategi. |

**Mengapa data belum cukup untuk klaim edge:** bahkan bila OHLCV satu ticker tersedia, syarat R333 membutuhkan roster listing historis termasuk delisted, shares outstanding point-in-time untuk klasifikasi kapitalisasi, sektor point-in-time untuk Gate G7, serta penanganan corporate action dan spread/eksekusi. Unsur tersebut belum terbukti tersedia lengkap dari sumber tunggal yang dipilih. Karena hard stop akuisisi sudah terjadi, kekurangan tersebut tidak dicoba diatasi dengan provider lain.

## 3. Fakta pasar/broker yang berhasil diverifikasi

1. **Biaya contoh broker, bukan biaya live akun pengguna:** Ajaib mempublikasikan biaya total saham **0,1513% beli** dan **0,2513% jual**; tabelnya menyebut komponen broker, levy, PPN biaya broker, dan PPh final jual. IDX menerbitkan levy pasar reguler 0,0433% beli dan 0,1433% jual, di luar komisi Anggota Bursa. Sumber: [Ajaib biaya](https://ajaib.co.id/biaya), [IDX mekanisme dan biaya](https://www.idx.id/id/produk-layanan/jam-dan-mekanisme-perdagangan/).
2. **Settlement:** pasar reguler diselesaikan T+2. Sumber: [IDX](https://www.idx.id/id/produk-layanan/jam-dan-mekanisme-perdagangan/), [KSEI](https://www.ksei.co.id/en/service-support/service-type/settlement-of-securities-transactions-services).
3. **Minimum lot:** pasar reguler/tunai diperdagangkan dalam round lot **100 saham (1 lot)**; nilai rupiah minimum bergantung harga dan lot yang dapat dibeli. Sumber: [IDX mekanisme perdagangan](https://www.idx.id/id/produk-layanan/jam-dan-mekanisme-perdagangan/).
4. **Fraksi harga:** halaman IDX yang diakses untuk aturan berjalan menampilkan Rp1 untuk harga di bawah Rp200; Rp2 untuk Rp200–di bawah Rp500; Rp5 untuk Rp500–di bawah Rp2.000; Rp10 untuk Rp2.000–di bawah Rp5.000; Rp25 mulai Rp5.000. Ini adalah tabel aturan yang berjalan saat akses, bukan tabel yang boleh dipaksakan ke seluruh sejarah 2016–2026.
5. **ARA/ARB:** ada amandemen yang berlaku 20 Oktober–31 Desember 2026 untuk saham di papan utama/pengembangan/ekonomi baru, termasuk ARB 7% pada sebagian besar rentang dan batas nominal Rp1 untuk rentang harga Rp11–Rp14; papan Akselerasi/Pemantauan Khusus berbeda. Sumber yang mengutip keputusan BEI: [Katadata](https://katadata.co.id/finansial/bursa/6ad6bb9113d26/bei-ubah-lagi-aturan-arb-saham-rp-14-bisa-turun-ke-rp-1). Data harian OHLCV saja tidak mengungkap urutan antrean maupun jaminan fill pada ARA/ARB.
6. **Short selling:** R333 sejak awal dikunci long-only. Halaman IDX menyatakan short selling memerlukan rekening efek khusus, instrumen yang memenuhi daftar short-selling, dan Anggota Bursa berlisensi; halaman tersebut juga menyebut jaminan awal sesuai ketentuan 50% nilai transaksi atau Rp50 juta sesuai persyaratan Anggota Bursa. Karena ketersediaan saham pinjaman tidak universal—terutama untuk small cap—R333 tidak mengasumsikan short dapat dilakukan. Sumber: [IDX aturan dan mekanisme](https://www.idx.id/id/produk-layanan/jam-dan-mekanisme-perdagangan/).
7. **Usia:** persyaratan tergantung broker. Contoh CGS International mempublikasikan minimum 17 tahun dan sudah memiliki KTP: [FAQ CGS International](https://www.cgsi.co.id/help/faq-opening-account?lang=ID). Ini tidak memverifikasi syarat semua broker atau persetujuan rekening tertentu.
8. **Keterbatasan live wajib dicatat:** **fee broker live, slippage, spread/antrean, dan risiko ARA/ARB belum diverifikasi pada akun nyata.** Hasil riset, jika kelak data layak, tetap simulasi sampai kelayakan umur, akun, dan eksekusi nyata terkonfirmasi.

## 4. Status gate dan metrik

Semua gate performa berstatus **GAGAL untuk klaim kelayakan eksperimen** karena Tahap 0 berhenti sebelum bisa menguji bukti wajib. Kata “GAGAL” di bagian ini tidak berarti strategi sudah terbukti memiliki expectancy negatif.

| Gate | Verdict | Alasan |
|---|---|---|
| Data Tahap 0 | **GAGAL** | Dua percobaan akuisisi gagal; tidak ada cache. |
| G1 Determinisme | **GAGAL** | Tidak ada cache/runner yang dapat dijalankan dua kali. |
| G2 Truncation | **GAGAL** | Tidak ada baris data untuk menguji prefix/truncation. |
| G3 Forward n/PF pada 1,5× biaya | **GAGAL** | Tidak ada trade atau PF yang dihitung. |
| G4 Discovery PF pada biaya realistis | **GAGAL** | Tidak ada trade atau PF yang dihitung. |
| G5 Stabilitas tahunan | **GAGAL** | Tidak ada breakdown tahunan; data tidak ada. |
| G6 Neighbor robustness | **GAGAL** | Tidak ada pengujian parameter. |
| G7 Leave-one-sector-out | **GAGAL** | Sektor point-in-time dan hasil tidak tersedia. |
| G8 Bootstrap blok | **GAGAL** | Tidak ada return per trade yang bisa di-bootstrap. |
| G9 Beta check | **GAGAL** | Matched buy-and-hold basket dan strategi tidak dapat dihitung. |
| G10 Audit jika PF > 1,4 | **GAGAL / tidak terpicu** | PF sama sekali tidak dihitung; tidak ada klaim PF tinggi. |
| G11 Likuiditas, spread, ARA/ARB | **GAGAL** | Tidak ada cache dan tidak ada spread aktual/eksekusi yang bisa diverifikasi. |

Metrik wajib—n trade, PF pada biaya 1×/1,5×/2×, expectancy R, total R, t-stat, bootstrap CI, maximum simultaneous positions, drawdown, baseline basket dan IHSG—semua **N/A karena tidak dihitung**, bukan nol dan bukan hasil buruk. Tidak ada trade ledger. Tidak ada klaim determinisme atau reproducibility.

## 5. Putusan akhir

**R333 = GAGAL karena kelayakan data/akuisisi. Kategori: `data inadequate`.**

- Tidak boleh menyimpulkan “tidak ada edge” untuk hipotesisnya, sebab strategi tidak diuji.
- Tidak boleh menyimpulkan ada edge, sebab tidak ada return, biaya aktual, baseline, atau cache.
- Tidak dilakukan retuning, varian, pembersihan saham berdasarkan PnL, atau penggantian sumber.
- Checkpoint proyek diperbarui untuk mempertahankan putusan biner dan menghindari pengulangan percobaan yang sama tanpa bukti baru.
