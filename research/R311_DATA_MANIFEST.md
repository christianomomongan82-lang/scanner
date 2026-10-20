# R311 — Data and Output Manifest

## Source
- Provider/source: Dukascopy EURUSD M1 paired BID/ASK; existing GitHub data-only artifact #11959096102, collection run #38697080604.
- Archive ZIP SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- BID member SHA-256: `b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc`.
- ASK member SHA-256: `52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b`.
- Cutoff: exclude timestamps >= `2022-01-01T00:00:00Z` before any R311 feature, event or outcome construction. No PnL calculated for 2022–2025.
- Paired M1 rows after cutoff: 2,650,553 per side; 2,202,782 rows had both quote sides active; 447,771 were static/inactive on at least one side. Exact active aggregation produced 422,289 valid M5 bars.
- Discovery 2017–2020; validation screen 2021. The FX programme has prior exposure to these dates; they are not pristine OOS.

## Original local output checksums

| Output | Bytes | SHA-256 |
|---|---:|---|
| `R311_trade_ledger.csv` | 1,172,967 | `7d35b79d69ef76d19a93dd8e5730d5c7f4ba96dcb8a0b78b61140c64baf754d7` |
| `R311_event_eligibility_audit.csv` | 320,632 | `e993bbdbc9ebe7339fab1464c92521a667469a237d0021678a486fa7700f6f77` |
| `R311_simulation_skip_audit.csv` | 60,429 | `86345fd11dabd9d065276f596fdc65e9754b7dd0d8330c7a95fc633a0dd02f8e` |
| `R311_annual_summary.csv` | 8,078 | `638df80cc2aa87b4adecf559351cf74db2b58abda2f48111856a74e80bf24593` |
| `R311_validation_weekly_net_R.csv` | 1,583 | `5d2ee1e1fdd78ba7df8ea43a85f3671407f9294126ab8cf33fecd9171965e76c` |
| `R311_data_audit.json` | 31,304 | `1e802d1c74902708acc5f2593843608725070a0fc5a9356c1f781af6d5ae29f1` |
| `R311_preoutcome_data_audit.json` | 24,236 | `0de0e8d295a9c1ea115aa2f6636ef6579034b512eb2bcea059754fd58985bac1` |

## Full output storage status — repository gate currently FAILS

The original local run outputs are identified by the SHA-256 values above, and the exact original source ZIP and BID/ASK members are in the existing GitHub data artifact. However, the six files `R311_trade_ledger.csv`, `R311_event_eligibility_audit.csv`, `R311_simulation_skip_audit.csv`, `R311_annual_summary.csv`, `R311_validation_weekly_net_R.csv` and `R311_data_audit.json` are **local run artifacts, not yet stored as row-level outputs in the active GitHub tree**. The pre-outcome audit JSON also remains identified by its local hash. Do not describe R311 as repository-self-contained until their compressed copies or original files are committed and read back.
The checked-in compact result therefore correctly sets `repository_artifacts_committed_and_readback_verified=false`. This is a reproducibility/storage status, separate from the negative strategy evidence. The candidate remains GAGAL regardless.

## Outcome summary
At +1 pip extra round-trip friction: discovery 750 trades / -360.843R / PF_R 0.3445; validation 143 / -73.799R / PF_R 0.3161. The validation weekly bootstrap 95% CI is [-1.8635R, -0.9933R]. R311 is **GAGAL**. No 2022+ PnL was calculated.
