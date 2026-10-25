# R330 — FINAL VERDICT: REJECT (aturan R191 di 10 indeks, pooled, tanpa seleksi)

Gagal: G5 (tahun forward terburuk) dan G8 (simulasi Stellar 2-Step). Semua gate lain lolos. Tidak ada tuning, varian, atau pembuangan indeks setelah hasil keluar. Sumber angka: research/R330_results.json (run Actions 40166799441, commit hasil 8cac744). Ringkasan ini ditulis ulang dari JSON, menggantikan teks lama 'Gate 1 PASS (preflight only)'.

## Gate
| Gate | Hasil |
|---|---|
| G1_CANONICAL_DETERMINISM_AND_BASELINE | PASS |
| G2_TRUNCATION_ALL_10 | PASS |
| G3_POOLED_FORWARD | PASS |
| G4_POOLED_DISCOVERY | PASS |
| G5_WORST_FORWARD_YEAR | FAIL |
| G6_NEIGHBORHOOD_N40_55_80 | PASS |
| G7_LEAVE_ONE_OUT | PASS |
| G8_STELLAR_2STEP_SIMULATION | FAIL |
| G9_CAUSALITY_IF_PF_GT_1_4 | PASS |

Pooled forward 2022-2025 @2bp: n=284, PF 1.301. Pooled discovery 2017-2021 @2bp: n=277, PF 1.508.

## Tahun forward (@2bp)
| Tahun | n | PF |
|---|---:|---:|
| 2022 | 77 | 0.561 |
| 2023 | 88 | 1.367 |
| 2024 | 66 | 1.963 |
| 2025 | 53 | 2.019 |

Ambang G5 = 0.80. Tahun terburuk gagal.

## Simulasi Stellar 2-Step (bootstrap kuartal)
| Risk/trade | Basket lolos % | Basket gagal % | R191-saja lolos % | R191-saja gagal % | Lolos gate |
|---|---:|---:|---:|---:|---|
| 0.5% | 50.7 | 21.48 | 28.0 | 5.75 | tidak |
| 1.0% | 46.17 | 29.33 | 54.52 | 28.57 | tidak |

## Pembacaan
Edge pooled tampak nyata dan kausal (G9: 1834 trade diaudit, 0 error), tapi basket tidak mengalahkan R191-saja untuk challenge: indeks jatuh bareng di 2022, risiko gagal naik di 0.5% dan pass-rate lebih rendah di 1.0%. Catatan: komisi/spread live, slippage, dan risiko floating intraday belum diverifikasi. R191 (usa500+usatech) tetap satu-satunya kandidat hidup. R330 ditutup.
