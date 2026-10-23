# R330 output manifest — 2026-10-23

**Verdict:** GAGAL — ECONOMIC SCREEN

## Source identity

- Branch: local-backtest/r189-dukascopy-history
- Core: research/R330_DATA/r330_screen_core.js
- Core SHA-256: 35e753efa87e0267652cf83eab8f053b19003c92bad997b44ce7ed2697040d90
- Full serialized output SHA-256: 646dc2d3ae4766ad149955bdb5c4b87511c45566167a9a8f32f77f80f5c1be39
- Repeat-run test: PASS; two JSON serializations identical.
- Runtime: deterministic ECMAScript V8 tool runtime, as registered in Amendment B. Not local Python; no GitHub Actions compute was used.

## Raw input hashes (all matched)

NaN
NaN
NaN
NaN
NaN
NaN
NaN
NaN
NaN
NaN

## Output hashes

- Full output JSON: 646dc2d3ae4766ad149955bdb5c4b87511c45566167a9a8f32f77f80f5c1be39
- Compact scorecard JSON: 768e971055747900ada71228ec19afed806caa8198fdefa54f787c8cd9a9d37f
- Weekly ledger CSV: 99f3a856e8314147e833315c74ccc9e591182e322db12faad1f1e0a35b50137b
- Asset-event ledger CSV: 5b35e68858828e0fa2c5707d0d71187f36619551462fa6d21596a4623f5d7a13
- Human report SHA-256: 3a7b9e37e4a434d209809600ec62b531a99b513afa277436b578e0a9ad7c1004

## Interpretation boundary

All results are underlying-market close-to-close screen returns on fixed weekly target weights, with declared commission and spread/slippage proxies. No exact FundedNext quote execution, symbol swap, five-minute fills, daily/max loss equity paths, or two-phase challenge pass distribution has been modeled.