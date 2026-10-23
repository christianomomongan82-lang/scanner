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

- AAPL: 9a4161adbd9a6889e5830226f63e1ac10536a961f4b6199587307ee40352b48d; rows=501
- AMZN: d2e677d502b87dffaec08b7e3036569f4c99401c0aba96be80ca1af4302ab17c; rows=501
- GOOG: 2aa1a097ed22b68689f46040de5aa55dd05c1b6635de87f97741311aa070da0d; rows=501
- MSFT: a5b30d15a82a915d659a84ba55382f3a82159eb6935a31967e2ba2bef94ca106; rows=501
- NVDA: 4b248ae1362e36739eacccd7786a9e956ce2319bfcb35e8890c2caa4642f736b; rows=501
- TSLA: 841aa8f2027acf744b73bbbea7cd1dac9227d50bdbc1294e208938489339d81c; rows=501
- AMD: f13e5ee41ccdcc4c4eec4e390aa3b90d12d8372be042a7cbc28b53524fb38801; rows=501
- META: b7c5b4f6ad8034c36b48ef59d8d5a6a5aa47292a350ef63365ae56795b6125d1; rows=501
- BTCUSD: 799fbcb438520cf2833172c9a985aaff9c4a080cfb48098c590e2ba6df8d76ef; rows=730
- ETHUSD: 38658f779569348f0aaddd0b1e5df39e65bd0326f7ffc99199521ce1a0fa57f5; rows=730

## Output hashes

- Full output JSON: 646dc2d3ae4766ad149955bdb5c4b87511c45566167a9a8f32f77f80f5c1be39
- Compact scorecard JSON: 768e971055747900ada71228ec19afed806caa8198fdefa54f787c8cd9a9d37f
- Weekly ledger CSV: 99f3a856e8314147e833315c74ccc9e591182e322db12faad1f1e0a35b50137b
- Asset-event ledger CSV: 5b35e68858828e0fa2c5707d0d71187f36619551462fa6d21596a4623f5d7a13
- Human report SHA-256: 3a7b9e37e4a434d209809600ec62b531a99b513afa277436b578e0a9ad7c1004

## Interpretation boundary

All results are underlying-market close-to-close screen returns on fixed weekly target weights, with declared commission and spread/slippage proxies. No exact FundedNext quote execution, symbol swap, five-minute fills, daily/max loss equity paths, or two-phase challenge pass distribution has been modeled.