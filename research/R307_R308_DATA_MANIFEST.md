# R307/R308 — Data and Output Manifest

## Data
- Existing GitHub EURUSD M1 BID/ASK artifact #11959096102 / acquisition run #38697080604.
- ZIP SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- 4,415,493 paired rows per side before cutoff; 696,795 registered repeat-flat rows removed; 3,718,698 active M1 timestamps and 736,076 complete active M5 bars; 7,882 M5 timestamp gaps greater than five minutes preserved.
- Protected cutoff: exclude timestamps >= 2026-01-01T00:00:00Z before feature/event/outcome construction.

## Local runner and outputs

| Output | SHA-256 | Bytes |
|---|---|---:|
| Local runner `r307_r308_batch.py` | `b8fb7728adf1d08028ff0486cf5d810025531ee15f7dfdf81ed8c8316af94a11` | 23,908 |
| Pre-outcome audit JSON | `fc5d973e77c88d62e65b035e742a281af3ab7178c36d4ae931c346192dbb93d2` | 1,308 |
| Full pre-outcome event/skip CSV | `9a8c7f0512f5b76565287ddbac22d44f784b647844903a85686cefbdf05ef348` | 210,615 |
| R307 08:05 full trade ledger | `6726ce5bbf8eff01f5ce4c9476e7139d03a798d43d57a9ae4624d6c5dadfcb4a` | 499,860 |
| R307 08:10 delay-stress ledger | `8e0878cc3937a6a31b852d38a52204627350f415c997c5d1b65a0e2b351e335d` | 502,155 |
| Combined cost/delay scorecard | `fc3fcc4018b2fb622b30570753759df8a494ab7cdebcf59594fdc71f7a03b74a` | 2,602 |
| Annual summary | local hash recorded in session output | — |
| Validation weekly input 08:05 | `aa750ec45cdac43b8e84c5e4c8d9e7a6af775ace221e4ae3b77df741053bc0d6` | 7,975 |
| Validation weekly input 08:10 | `95d27332e4de58a6aee13ffe12911e96ab69812556030fc98096bf3003949b74` | 7,985 |

The full runner and row-level CSVs are local session artifacts, not yet verified as decoded GitHub files. Aggregate outputs and this manifest are stored in GitHub, but repository-only end-to-end reproduction therefore remains a failed gate. R308 produced no PnL/ledger because its pre-outcome data/sample gate failed.
