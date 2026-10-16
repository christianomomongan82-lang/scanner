# Riset Trading — Putusan Biner, Portofolio Gabungan, dan Compounding

Effective: 2026-10-16

## 1. Status eksperimen harus biner

Setiap kandidat, eksperimen, audit eligibility, atau verifikasi implementasi hanya memiliki satu status akhir: **LULUS** atau **GAGAL**.

- Gunakan LULUS hanya jika seluruh gate yang ditulis sebelum pengujian terpenuhi.
- Jika data, execution mapping, biaya, atau bukti wajib gagal diverifikasi, status percobaan tersebut adalah GAGAL untuk klaim yang sedang diuji. Jangan menaruh kandidat dalam status pending/menunggu/“belum lolos”.
- Gagal pada satu tahap tidak berarti pengetahuan eksperimen dihapus. Simpan alasan kegagalan, input, kode, checksum, ledger, dan laporan sehingga bisa dipakai untuk mencegah pengulangan atau mendesain hipotesis independen.
- Ganti status GAGAL menjadi LULUS hanya melalui pengujian baru yang memiliki bukti baru dan gate yang dipreregistrasikan; jangan mengganti label eksperimen lama setelah melihat hasil.

## 2. Strategi tunggal bukan satu-satunya unit riset

Bangun portofolio modular:
1. Uji modul strategi sebagai stream sinyal/transaksi mandiri.
2. Uji gabungan dengan bobot, urutan sinyal, overlap, korelasi, biaya dan aturan skip yang sudah dikunci.
3. Gabungan tidak otomatis lebih baik. Mencampur beberapa strategi yang expectancy-nya negatif umumnya hanya menggabungkan kerugian; komponen yang gagal tidak boleh diselamatkan dengan menala parameter setelah forward/OOS dilihat.
4. Komposit yang dipilih setelah hasil komponen telah dilihat wajib dicatat sebagai diagnostik retrospektif. Hasil yang tampak baik tetap GAGAL untuk promosi menggunakan periode yang sama; diperlukan periode independen yang belum dipakai untuk memilih komposit.

## 3. Compounding dan pengendali risiko

- Ukuran posisi harus dihitung dari ekuitas terbaru menggunakan fractional risk yang ditetapkan sebelum test.
- PnL dalam dolar dihitung dengan ukuran posisi yang ditetapkan pada saat entry; perubahan ekuitas dari trade tertutup menentukan ukuran entry berikutnya.
- Semua modul berbagi satu risk controller: maximum aggregate open risk, daily loss, maximum loss, korelasi instrumen, waktu reset server dan aturan firm.
- Risk controller dapat membatasi kerusakan tetapi tidak menciptakan edge.
- Laporan wajib memisahkan expectancy trade dalam R dari hasil dolar yang sudah di-compound, serta menyebut drawdown realized-only jika floating equity tidak tersedia.
- Challenge replay baru boleh disebut LULUS jika batas loss, target, waktu trading minimum, Quick Strike, session/server-time, biaya riil yang relevan dan mekanisme entry/exit yang berlaku sudah dimodelkan dengan bukti memadai. Selain itu, hasil challenge adalah GAGAL.

## 4. R268 — hasil penerapan

- [Preregistration](R268_COMPOUND_PORTFOLIO_PREREGISTRATION.md)
- [Result](R268_COMPOUND_PORTFOLIO_RESULTS.md)
- [Machine-readable output](R268_compound_portfolio_results.json)
- [Local Python runner](r268_compound_portfolio.py)
- R262 + R263 dengan risiko 0,25% per entry, batas risiko terbuka 1%, biaya tambahan +1 pip FX dan +4 bps indeks, delay 5 menit: **GAGAL**.
- Forward 2022–2025 berakhir di $3.374,61 dari referensi $6.000 (−43,76%), PF dalam R 0,823, drawdown closed-equity 44,60%, bootstrap CI mingguan −0,315% hingga −0,102%.
- Batas MLL nominal $5.400 pertama kali ditembus pada 2023-05-26 04:06 UTC berdasarkan closed equity. Ini bukan challenge-pass estimate karena floating equity/DLL tidak direkonstruksi secara tick-by-tick.

## 5. Cara menjalankan riset selanjutnya

- Riset/backtest dijalankan dalam Python lokal pada sesi, bukan GitHub Actions.
- GitHub menjadi sumber input dan penyimpanan kode, preregistrasi, ledger, hasil JSON, laporan, dan checkpoint.
- Tidak ada strategi yang dipilih hanya berdasarkan total PF. Gate harus mencakup net expectancy setelah biaya, stabilitas lintas periode/tahun, bootstrap, trade count, drawdown, delay, korelasi dan challenge rule compliance.
- Jika R189, R262, R263, R266 atau R267 digunakan lagi sebagai komponen, jangan mengubah aturan lama. Setiap portfolio test baru harus menjelaskan apakah independen atau retrospektif dan menetapkan putusan biner.


## 6. Correct interpretation of compounding — 2026-10-16

**Primary objective: strategy/edge compounding before capital compounding.** The user's request to “compound compound” must not be reduced to fixed-fractional position sizing or a blind union of previously failed trade streams.

- Build an integrated signal/entry system by testing conditional filters, compatible setups and complementary modules. Measure whether the integrated trade stream has a genuinely stronger **risk-normalized PF and net expectancy**, while retaining sufficient sample size and robustness, versus its components and a comparable baseline.
- Do not call a union of several losing strategies “compounding” and expect PF to rise. R268 was only a loss diagnostic of adding previously failed streams, not a successful implementation of the intended objective. R269 returned to a single standalone setup, also missing that priority.
- Capital compounding comes **after** edge construction: fixed-fractional sizing computes position size from the latest equity and tests dollar growth / funded-rule survival. This changes the distribution of dollar outcomes; it does not by itself create entry/exit edge.
- Every composite must lock its logic before validation and show incremental PF, expectancy, trades, annual stability, bootstrap and five-minute latency/cost stress. The 2022–2025 window has been inspected too many times to serve as an untouched promotion holdout.
- Full correction and workflow: [COMPOUNDING_OBJECTIVE_CORRECTION_20261016.md](COMPOUNDING_OBJECTIVE_CORRECTION_20261016.md).


## 7. Primary objective correction — funded target completion (2026-10-16)

The latest authoritative objective is [PRIMARY_OBJECTIVE_FUNDED_TARGET_COMPLETION_20261016.md](PRIMARY_OBJECTIVE_FUNDED_TARGET_COMPLETION_20261016.md). It supersedes any earlier language that made PF or “better PF” the primary objective.

- The target is to complete the actual funded challenge as quickly as realistically possible, chiefly measured by probability of hitting phase targets before daily/max loss breach and by the time-to-target distribution.
- For the current reference configuration: +8% Phase 1, then +5% Phase 2, with the firm's actual loss limits/rules modeled. Research only before age eligibility.
- “Compound” means coordinate/combine multiple usable opportunities, conditions and strategy modules into an integrated system that helps reach these targets—not only fixed-fractional account sizing and not a blind union of losing streams.
- PF is only one diagnostic. Trade frequency, expected R, win/loss clustering, time-to-target, pass/fail odds, latency, costs, cross-module overlap and loss-rule breaches all matter to the objective.
- Capital compounding and the shared risk controller are simulated after the integrated opportunity stream is defined. They are not substitutes for optimizing target completion.

## 7. Evolutionary method compounding — explicit operating rule

“Compounding” means compounding method discovery over generations. Every candidate must carry parent IDs, reusable component IDs, and the reason for each crossover/mutation. Preserve diagnostics from failed candidates and use controlled ablations to distinguish failed combinations from potentially useful components. Compare offspring with parents and no-filter/component baselines on matched timestamp/cost/delay streams. Maintain a diverse risk-aware Pareto set for funded target completion probability, time-to-target and breach probability. Repeated search on already inspected validation data creates selection bias; a true final holdout is opened once, after locked historical gates. See [EVOLUTIONARY_METHOD_COMPOUNDING_20261016.md](EVOLUTIONARY_METHOD_COMPOUNDING_20261016.md). R272 is a single combination test, not yet a full evolutionary-search system.
