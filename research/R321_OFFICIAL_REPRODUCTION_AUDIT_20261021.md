# R321 official-source reproduction audit — 2026-10-21

## Final process status
- Exact runner reproduction: **PASS**.
- Deterministic clean rerun: **PASS** (two official-source executions, all output hashes identical).
- Source restoration from GitHub: **PASS**.
- R321 signal/edge verdict: **GAGAL**.
- Funded challenge replay: **NOT RUN**, because the edge gates failed.
- Full raw row-level output is reproducible from the archived input and committed runner; it need not be promoted as an alpha result.

This note supersedes the earlier open-gate conclusion in [R321_REPRODUCTION_AUDIT_20261021.md](R321_REPRODUCTION_AUDIT_20261021.md), which was written before the exact checked-in runner had been executed.

## Input source verified
- GitHub Actions data-only artifact: **11959096102**, `EURUSD-M1-Dukascopy-BID-ASK-2016-2025`.
- Acquisition workflow run: **38697080604** on branch `data/eurusd-m1-2016-2025`, head commit `2de5c97a2e261e361f23d00e4599aa748693b474`.
- Artifact state checked: not expired; listed expiry **2027-01-13 07:11:24 UTC**.
- Artifact ZIP size: **67,719,731 bytes**.
- GitHub artifact digest and locally downloaded bytes both match SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- The exact ZIP members used by the runner are `eurusd_bid_M1_2016-2025.csv.gz` and `eurusd_ask_M1_2016-2025.csv.gz`.

## Runner verified
- Exact committed file: `research/R321_price_relationship_audit.py`.
- Runner-changing commit: `25d8c2ac93b62f728fe68041a6b4804777077a8e`.
- Git blob SHA-1: `8afc5bd8b9206f4d772e585446228daa2640707b`.
- File SHA-256: `8647e7e8d6cedf011c8b36d7dbd773e4c35650d91cd13d196fff6fdcc207d41c`.
- Execution environment: Python 3.13.5, pandas 2.2.3, NumPy 2.3.5, SciPy 1.17.0.
- Local command: `python /mnt/data/R321_price_relationship_audit.py`, with the artifact ZIP placed at the hard-coded source path `/mnt/data/eurusd_raw_source.zip`.

## Two exact-source runs
Both clean executions used the same byte-identical runner and input ZIP, and every generated file hash matched between run 1 and run 2. The manifest itself also matched.

| Output | Bytes | SHA-256 |
|---|---:|---|
| `R321_ANNUAL_COHORT_SCORECARD.csv` | 28,298 | `004fbd9f7006a015ca25cf0eb4405b2cbbea04aef66ec5169901891f77b91a83` |
| `R321_BLOCK_BOOTSTRAP.csv` | 6,685 | `111e018dc17ade409cb06031ed77551cc43825bdc06d27bbd551a1b654dfec4c` |
| `R321_DATA_AUDIT.json` | 1,637 | `b3c7203e0593e2e270f61ef94341adcaebd687d7a1b9287fd97e9ba0aa1ce311` |
| `R321_ENVIRONMENT.json` | 307 | `8278c00d57433905231dcfb75439dfddb3d63b09fd2e4f32785292b67f315fcf` |
| `R321_OUTPUT_MANIFEST.json` | 1,086 | `3ba8afa4fea21ee640481437835b48161d1fbe8138f34467747033128e466987` |
| `R321_PREDICTION_EVENT_LEDGER.csv.gz` | 8,190,426 | `35b4796557a109f14148861b300286c4b86a90ec2817a82b1714c4855773580b` |
| `R321_SCORECARD_ALL_COSTS.csv` | 16,087 | `8457cd9a572384636b43555c6047c56f9edc1fcb6d901c0ba010f05a5099c054` |
| `R321_WEEKLY_NET_PIPS_ZERO_INCLUSIVE.csv.gz` | 210,236 | `5644983332996e648f350299fbbc67a186ac8addb2778642e046b7d17c31e3e8` |

The regenerated ledger is 56,633 rows × 70 columns. Decompressed ledger SHA-256: `5ad36685453b7537c4ed331e566309a7a53dfbc6f9a1ee4b8dfd98dc02144d4e`. The decompressed zero-inclusive weekly file SHA-256 is `9ab0046862cb68e0413dc4af70b467688e1510dcc19a25a7e8c53b59f906ba06`.

## Data and signal findings (unchanged)
- 4,415,493 paired M1 rows; 696,795 joint repeated-flat placeholders removed; 3,718,698 retained paired M1 rows; 736,076 exact complete M5 bars; 7,882 gaps over five minutes retained without fabricated bars.
- All 28 registered feature/horizon pairs had negative mean executable net pips and PF below 1 at the primary +1 pip incremental-cost case.
- Best zero-incremental-cost result: F6 autocorrelation-state / 60 minutes, 48,879 events, mean −0.2568035 pip/event, PF 0.93383.
- Same pair at +1 pip incremental cost: mean −1.2568035 pips/event, median −1.3, win rate 42.21%, PF 0.71612. Four-week block-bootstrap 95% intervals were below zero in the pooled, discovery and confirmation partitions.
- 2026 price outcomes remained excluded. No FundedNext account-path replay or pass-probability estimate was run.

## Restoration rule
Re-download artifact **11959096102**, verify the ZIP digest above, place it at `/mnt/data/eurusd_raw_source.zip`, run the exact committed runner with Python 3.13.5 / pandas 2.2.3 / NumPy 2.3.5 / SciPy 1.17.0, then compare all outputs against the manifest hashes above. Refresh or migrate the raw artifact before its current expiry on 2027-01-13.

**Disposition:** R321 is reproducible but still **GAGAL as a trading hypothesis**. The process gate for deterministic regeneration is now closed. A new strategy experiment may begin only with a distinct economic mechanism and a preregistration committed before outcome calculation; no parameter/sign rescue of R321 is permitted. Historical 2021–2025 results remain contaminated diagnostics, and 2026 remains protected.
