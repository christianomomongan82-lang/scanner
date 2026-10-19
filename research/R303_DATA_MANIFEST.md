# R303 — Data and Output Manifest

## Source data
- Acquired from existing GitHub data artifact #11959096102 (workflow run #385? data archive was already present; no backtest workflow was run).
- Archive: `EURUSD_M1_BID_ASK_archive.zip`
- Archive SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- Gzip member SHA-256, BID: `b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc`; ASK: `52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b`.
- Rows per side: 4,415,493; paired timestamp rows: 4,415,493. Source range 2016-01-03 00:00 UTC to 2025-12-31 21:58 UTC.
- Data quality: zero duplicate timestamps, zero invalid OHLC rows, zero negative spread. Repeated flat-fill filter removed 696,795 rows. Active rows: 3,718,698. 538 time gaps > 1 minute were preserved, not synthesized.
- Features/outcomes only through 2021-12-31 UTC. No candidate PnL was calculated for 2022 or later.

## Local corrected output hashes
These SHA-256 checksums identify the actual local run outputs; hashes do not imply the underlying row-level files are stored here.

| Output | SHA-256 |
|---|---|
| corrected runner raw source | `cbfeafcd474acac8f11e7f286518114d422efdc030bae067cf072504e6aac8f9` |
| runner gzip | `3f4635838fc18c9be8304ff2cb48bd3f1876d2e359bccd26f502dea50c6e3fb5` |
| compact local results | `1af7ebf76e5b80095eb75580cbdb0dc9a5cc71ed7d40069e9bb9ed168ad39868` |
| final report local output | `80f982637488f395dbbf5ad1430cc099ddd0629a1cd206a9a0e0ee95bc581c64` |
| data audit | `ca449d1db55f731228ac1075fcef3e135701dd88d8ffb3e57dff175fb445bb1d` |
| period / annual table | `e8201d5e77c97cd4b8fa26c23302834e92063a22d3deb6e77f45b83bd7aada30` |
| pre-outcome event audit CSV | `78f3839b65b8df139ece8c84bc03db676168a67f4c4474e47abaf835fc6f5257` |
| pre-outcome summary JSON | `e952059af2bb77ded3491151687f64694d9817c23aa10e1a122f94b8d0d39361` |
| weekly bootstrap JSON | `6d4a53f151b7458290c773af98b03f727ae4df78f68186d07b00394317810ad8` |
| weekly net-R CSV | `cf2da009de182ef69ae7f0495638189b5d31988581e3e9daaba8e42cec762f61` |
| T+5 fade gross trade ledger | `08fdb3a78eb60b060330937fa7007470db36e57ee6468e7b98d0e02a085cec86` |
| T+5 fade skip audit | `56b302ed5c674a0dc19722141827aeacb34503c3b27bebc50e2df33d0fcee7c1` |
| T+10 fade gross trade ledger | `6ae0315ddc7bda23ad41ddcbac11a9b5c89872ff72270c483bef92694782c3de` |
| T+10 fade skip audit | `ec179f1d1fc0cedf552d34225696ac08bf0133ba532b533883d56e616353f922` |
| T+5 follow gross trade ledger | `1e04050e333a5bb2c1964c73b9e498c46daf4582a862519eed668c2118038559` |
| T+5 follow skip audit | `1d01dde33f69e92f8a8286c5a40c77b5869d7aa013465aa83304e88eef06c273` |

## Repository-level reproducibility

The corrected local run completed. `R303_results_compact.json` and `R303_data_audit.json` in the repository are normalized archival summaries built from its aggregates; they are not byte-for-byte copies of the larger local output JSON files whose hashes appear above. The raw local files remain identified by their local hashes. At this checkpoint, the full runner and row-level ledgers have **not** yet been stored as regular decoded files in this branch; the repository-only reproducibility gate remains failed. Do not describe R303 as fully independently reproducible until the exact runner and all required row-level outputs are attached/committed and verified.
