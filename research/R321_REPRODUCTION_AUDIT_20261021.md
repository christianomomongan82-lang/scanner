# R321 rerun and closeout audit — 2026-10-21

## Locked claim verdict: GAGAL
The registered causal price-state prediction claim fails. This is an edge-family failure, not proof that all market prediction is impossible. Do not reverse direction, tune thresholds, or promote a neighbouring variant on the same inspected history.

## Two-run deterministic comparison
The same locally reconstructed runner logic was executed twice against the exact registered raw archive (source ZIP SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`) with isolated output directories. The following hashes matched exactly between runs:

| Output | SHA-256 | Result |
|---|---|---|
| Scorecard, all registered costs | `8457cd9a572384636b43555c6047c56f9edc1fcb6d901c0ba010f05a5099c054` | identical |
| Annual/cohort scorecard | `004fbd9f7006a015ca25cf0eb4405b2cbbea04aef66ec5169901891f77b91a83` | identical |
| Four-week block bootstrap | `111e018dc17ade409cb06031ed77551cc43825bdc06d27bbd551a1b654dfec4c` | identical |
| Data audit | `b3c7203e0593e2e270f61ef94341adcaebd687d7a1b9287fd97e9ba0aa1ce311` | identical |
| Compressed 56,633 × 70 event ledger | `35b4796557a109f14148861b300286c4b86a90ec2817a82b1714c4855773580b` | identical |
| Compressed zero-inclusive weekly series | `5644983332996e648f350299fbbc67a186ac8addb2778642e046b7d17c31e3e8` | identical |

The decompressed event-ledger CSV hash is `5ad36685453b7537c4ed331e566309a7a53dfbc6f9a1ee4b8dfd98dc02144d4e`, and the decompressed weekly-series CSV hash is `9ab0046862cb68e0413dc4af70b467688e1510dcc19a25a7e8c53b59f906ba06`. Both match the earlier local result payload byte-for-byte after decompression. The output manifest itself contains run-specific environment fields (output path and runner-file hash), so its hash is not expected to match across these isolated paths.

## Results reconfirmed
- Data: 4,415,493 paired raw M1 rows; 696,795 placeholders removed; 3,718,698 retained paired M1 rows; 736,076 exact complete M5 bars; 7,882 gaps >5 minutes preserved without synthetic fills.
- All 28 registered feature/horizon relationships have negative average executable net pips at the +1 pip primary incremental-cost case; none has positive mean or PF above 1. At zero incremental friction, even the best remains negative: F6_AUTOCORR_STATE / 60 minutes, 48,879 events, mean -0.2568 pip/event, PF 0.934.
- At +1 pip, that same best relative result is -1.2568 pips/event, median -1.3, win rate 42.21%, PF 0.716.
- Its four-week bootstrap 95% CI for weekly mean net pips: overall [-1.366760, -1.177065]; discovery [-1.481949, -1.109147]; confirmation [-1.421008, -1.073548]. All are below zero.
- Protected 2026 outcomes were not scored. No challenge replay or pass-probability estimate was run.

## Remaining strict-v2 gate
This is **not** a byte-for-byte execution of the runner currently stored at `research/R321_price_relationship_audit.py`. The local reconstruction's SHA-256 is `98d20b871ec149f07ca3b94df7c6d5ddace5470aae04574a8447903724a9cafb`; the current Git blob identity for the checked-in runner is `8afc5bd8b9206f4d772e585446228daa2640707b`. Aggregate scorecards and event/weekly series reproduce, but exact-source execution and full repository readback of all row-level outputs have **not** passed. Do not call R321 fully repository-reproducible, and do not start a new signal family until this strict-v2 process gate is closed.

## Required repair before next strategy search
Execute the exact checked-in runner from the registered source, compare its deterministic outputs against the listed row/aggregate hashes, and ensure every required output either exists and is read-back verified in the branch or has a verified restoration process. Then update this audit and run the v2 closeout validator. This repair is process work, not parameter tuning, and must not access the protected 2026 outcome window.
