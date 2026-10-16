# R272 — XAUUSD M5 dual-module router

**Putusan biner: GAGAL.** Dijalankan lokal memakai data Dukascopy M5 BID/ASK yang manifest-nya membuktikan synthetic flat bars dinonaktifkan. Hanya data sampai 2025-12-31 masuk ke perhitungan. Holdout 2026 tetap tidak dibuka.

## Data audit

- Data-only run: [38859918137](https://github.com/christianomomongan82-lang/scanner/actions/runs/38859918137); artifact ID `12031270051` (raw data only, not a backtest).
- BID and ASK each contain 947,326 rows; all timestamps match one-to-one. SHA-256 gzip BID: `b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575`; ASK: `b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9`.
- Synthetic flat bars disabled; 0 duplicate timestamps; 0 negative open spreads; 572 gaps over five minutes preserved, not filled. Median observed opening spread $0.358/oz; p95 $1.117/oz.
- Signal/PnL calculations used 877,930 paired quote rows before 2026-01-01 only. The raw file ends 2026-10-15 23:55 UTC; reserved 2026 quotes were not loaded into the calculation.

## Results at primary +$0.30/oz incremental cost

| Stream | Period | Trades | Net R | PF | Mean R/trade | Win rate |
|---|---|---:|---:|---:|---:|---:|
| Module A | 2016–2020 | 0 | 0.00 | n/a | n/a | n/a |
| Module A | 2021–2025 | 0 | 0.00 | n/a | n/a | n/a |
| Module B / router | 2016–2020 | 944 | -437.47 | 0.525 | -0.463 | 23.94% |
| Module B / router | 2021–2025 | 957 | -401.22 | 0.548 | -0.419 | 21.84% |
| Raw union | 2016–2020 | 1,073 | -452.70 | 0.564 | -0.422 | 24.60% |
| Raw union | 2021–2025 | 1,094 | -439.37 | 0.564 | -0.402 | 22.21% |

Even with $0.00/oz extra cost, Module B/router was negative: -174.83 R in discovery and -227.38 R in validation. At +$0.50/oz it was -612.56 R and -517.11 R respectively. Four-week circular block bootstrap, 10,000 resamples at +$0.30/oz: discovery weekly mean -1.676 R, 95% CI [-2.081, -1.256]; validation weekly mean -1.537 R, 95% CI [-1.951, -1.115]. Both intervals are wholly negative.

## Component diagnosis for the evolutionary search

- **Module A structural incompatibility:** its six-bar continuation trigger fired 972 times, but maximum 12-hour ER among these triggers was 0.3249; none met the router's locked ER >= 0.45 gate. It therefore produced no trades. Lowering the threshold after seeing this result would be post-result tuning and is prohibited.
- **Module B failed as an edge:** the balanced failed-excursion fade lost before extra cost and remained strongly negative on discovery and validation. Do not carry the exact fade trigger forward as an evidence-backed edge.
- **Router versus raw union:** router retained 957/1,094 = 87.5% of validation trades and was less negative by 38.15 R than raw union. This is only a relative improvement; both streams lose materially, so the router fails its absolute gates.
- **Execution rejections:** 341 candidates failed RR >= 1, 229 had invalid stop distances, 77 delayed entries had already crossed stop/target and 50 had invalid targets. These secondary issues do not explain away negative expectancy.

## Preregistered historical gates

| Gate | Result | Evidence |
|---|---|---|
| Router discovery >= 100 trades and positive net R | **FAIL** | 944 trades; -437.47 R |
| Router validation >= 200 trades and positive net R | **FAIL** | 957 trades; -401.22 R |
| Module A >= 50 trades and positive R in each segment | **FAIL** | zero trades in both |
| Module B >= 50 trades and positive R in each segment | **FAIL** | enough trades, negative R in both |
| Validation router positive at +$0.50/oz | **FAIL** | -517.11 R |
| Router outperforms raw union in validation and keeps >=60% of its count | PASS | -401.22 R vs -439.37 R; keeps 87.5% |

## Decision and continuation

**R272 = GAGAL.** Do not open 2026, do not tune R272, and do not run its funded challenge replay. Reuse the diagnosis—not the failed signal: regime filters can make a module structurally unreachable, and a higher-trade-count combination does not repair negative expectancy. The next evolutionary child must be separately locked and should test a materially justified replacement for the context/router logic. The local run generated development-only trade ledgers; this GitHub verdict artifact is a compact summary, not a claim that every full row-level ledger has been uploaded.

## Code and test provenance

- Locked specification: [R272 preregistration](R272_XAUUSD_DUAL_MODULE_PREREGISTRATION.md)
- Runner in repository: [r272_xauusd_dual_module.py](r272_xauusd_dual_module.py)
- Engine smoke tests: [test_r272_xauusd_dual_module.py](test_r272_xauusd_dual_module.py)
- Local mirrored runner smoke checks passed for T+10-minute entry, target fill, exact 16:45 cutoff gap handling and rejecting a broken intervening bar. The calculations were executed in local Python; GitHub Actions was only used to collect raw data.