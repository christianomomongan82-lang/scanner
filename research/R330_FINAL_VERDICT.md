# R330 STATUS — GATE-MISMATCH (definisi konvensi entry), strategi belum dievaluasi

## Amandemen Gate 1

Gate 1 harus memakai entry canonical: open bar H4 berikutnya. PF manual5m sebesar 1.491 sebelumnya **bukan** bukti replikasi canonical gagal dan tidak dipakai untuk pass/fail. Manual5m hanya diagnostik.

File bernama R191_CANONICAL_index_trend_long.py tidak ditemukan dalam tree repository atau file Project yang tersedia. Karena itu angka interim di bawah berasal dari ledger tersimpan R194, difilter ke USA500+USATECH mode ideal pada helper R192 (entry open bar H4 berikutnya). Ini adalah pemeriksaan canonical-equivalent, bukan klaim bahwa file bernama tersebut sudah dijalankan. Window selection juga belum bisa dibandingkan dengan definisi asli script; yang tersedia adalah discovery R192: entry 2017-01-01 sampai sebelum 2022-01-01.

## Gate 1 — canonical-equivalent observed vs target

| Phase | Entries | Closed n | Censored | PF@1bp | PF@2bp | PF@3bp | Target n | Target PF@1bp | Target PF@2bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Selection / available discovery 2017–2021 | 89 | 87 | 2 | 1.851 | 1.838 | 1.824 | 78 | 2.082 | — |
| Forward 2022–2025 | 77 | 75 | 2 | 1.325 | 1.318 | 1.311 | 70 | 1.247 | 1.241 |
| OOS 2026 through archived common cutoff | 12 | 10 | 2 | 1.989 | 1.978 | 1.966 | 11 | — | 1.954 |

PF uses the R192 helper's risk-normalized net-R convention: round-trip cost = entry × bps / 10,000; PF = summed positive net R / absolute summed negative net R. Source is the existing R194 audit artifact, run 38133085545 / artifact 11700178416, common cutoff 2026-10-09 20:00 UTC.

## Manual5m comparison — diagnostic only, never used for pass/fail

| Phase | Entries | Closed n | Censored | PF@1bp | PF@2bp | PF@3bp |
|---|---:|---:|---:|---:|---:|---:|
| Selection / available discovery 2017–2021 | 92 | 90 | 2 | 1.660 | 1.648 | 1.636 |
| Forward 2022–2025 | 72 | 70 | 2 | 1.491 | 1.483 | 1.475 |
| OOS 2026 through archived common cutoff | 13 | 11 | 2 | 1.657 | 1.648 | 1.639 |

## Decision and stop point

**GATE-MISMATCH (definisi konvensi entry), strategi belum dievaluasi.** The available canonical-equivalent stream does not reproduce the supplied targets (especially forward n/PF and 2026 OOS n/PF). Under the hard-stop rule, Gate 2, pooled performance, worst year, neighborhoods, leave-one-out, correlation/overlap and challenge simulation were not run. No tuning, instrument removal, or replacement variant was attempted.

Causality remains unverified from the archived ledger because the artifact lacks raw OHLC paths. The revised R330 runner now uses next-H4-open entry for the primary candidate, keeps manual5m diagnostic-only, and triggers an OHLC path audit whenever any Gate 1 PF exceeds 1.4 if the fresh canonical preflight can be reproduced.
