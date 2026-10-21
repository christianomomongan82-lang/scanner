# R319–R320 archive, restoration and output verification manifest

Repo branch: local-backtest/r189-dukascopy-history.
Raw data artifact: run 38697080604, artifact 11959096102; archive SHA-256 b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e. Artifact bytes 67,719,731. Raw side row count 4,415,493 BID and 4,415,493 ASK; clean rows 3,718,698 after removing 696,795 joint repeated-flat placeholders. Exact complete bars M5 736,076, M15 240,883, H1 57,191 and H4 12,348; never fabricate missing bars.

## Rebuild runners
From repository root (Linux/macOS/Git Bash): `sh research/archive/restore_r319_r320_runners.sh`. It reconstructs the archived runner source from the individually verified base64 pieces and applies a source patch that fixes nondeterministic gzip headers. The restored, patched source hashes must be:
- R319 Python source SHA-256: `6acc5bf9e6f317ff50c22c5db8c1a9cfe9bf8e21af792ad207a34c63797f0e6a`
- R320 Python source SHA-256: `df20cfaf25176e9c2022983c72d3809026b4a512c98fdd6f20557b92f3fb2f7c`
Original gzip source hashes before the deterministic compression patch: R319 `fddbddc87da9e768e3373f244174d65bf51067e1611ece4ad9e48343125bdf96` (8,547 bytes); R320 `92b5e6ffe91baf2912b072aba7fbd2fa2e011240e4352d265176067cd9ba78f2` (4,002 bytes). R320 imports the R319 loader/simulator, so restore and run R319 first. Runtime environment: Python 3.13.5, pandas 2.2.3, NumPy 2.3.5, Numba 0.65.1. Source archive inputs need to be available as `/mnt/data/eurusd_raw_source.zip`.

## Rerun-verified output hashes
R319 (972 configurations):
- Full grid CSV: 2,143,327 bytes; SHA-256 `541cdb6771d1b6f0d202a6db3fee5dd83b781c90db7efb2fc0de1d2bf2a5be70`
- Config scorecard CSV: 214,224 bytes; SHA-256 `4e8c2cbda0c96200a30f99225d54ff20a94371818adec921557e345015805c9e`
- Top candidates JSON: 70,895 bytes; SHA-256 `0a1d24cbcd4831717375c698d4420ea8bffcc6abfa846dc75b79c7328e97e00c`
- Discovery trade ledger gzip: 77,939 bytes; SHA-256 `6679d295655488b75010ca2daefce6bc0c4841f384b3cb1df3e5e31492ae7dbb`
- Confirmation ledger gzip: 28,277 bytes; SHA-256 `716d2ae8eebde6cd626d55d858085e0f92058d95900a1be7c79720c7356e7b28`
- Diagnostic ledger gzip: 123,946 bytes; SHA-256 `4a1279355aa3f4bbf319d24861ad325e0cf5ffa2c885663bc7b555e4a69f5f80`

R320 (162 configurations):
- Full grid CSV: 364,269 bytes; SHA-256 `00d256ce4291303ee48068ec1f04a9ee794c4240662f627b16e0d606e2335b5e`
- Config scorecard CSV: 38,760 bytes; SHA-256 `54b15f4d05c02a27ff9473c4a951e15745a352f8b75b1f15f825fd7bf5f3bc3a`
- Top candidates JSON: 5,024 bytes; SHA-256 `bcd2c2ede9e42ba14565c580fd70723f41252328799be7e1703247aa114909b4`
- Discovery ledger gzip: 10,508 bytes; SHA-256 `02271a484d001e04f813c293caf18d5e0a95b3da094ba5812030f7ede7bde2bc`
- Confirmation ledger gzip: 7,632 bytes; SHA-256 `a42d9ee56ddeab84102a3b2b81aee40fdda9876e7dd1625c4d9beb17634228af`
- Diagnostic ledger gzip: 15,048 bytes; SHA-256 `17315f304d34690c66fec8e8d7f84d3e442773fb46d2c38f69ba79bd05919f0d`

Both runners were re-executed twice in this session. Complete-grid, scorecard, top-candidate, and deterministically gzipped trade-ledger hashes were identical across reruns. The runner's compact JSON includes measured runtime and is therefore intentionally not hash-pinned byte-for-byte; the checked-in compact decision summaries omit runtime. Detailed outputs are regenerable rather than individually stored as repository files. This is reproducible generation, not static storage of every row-level output.

R319 and R320 full result/decision: `research/R319_R320_EDGE_SEARCH_REPORT_20261021.md`, `research/archive/R319_RESULTS_COMPACT.json`, `research/archive/R320_RESULTS_COMPACT.json`.

Important limits: these were exploratory searches; reports/specification were committed after results, not formally registered in GitHub before computation. 2019–2025 are project-contaminated and not pristine OOS. 2026 remained closed. Previous R317/R318 historical runner/full ledgers were not recovered in this work; don't claim those older rounds have been retroactively made reproducible.
