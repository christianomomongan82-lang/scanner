# R319–R320 archive and restoration manifest

Repo branch: local-backtest/r189-dukascopy-history
Raw data artifact: run 38697080604, artifact 11959096102; archive SHA-256 b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e. The source artifact must be fetched as /mnt/data/eurusd_raw_source.zip before executing the restored runners.

Restore command (Linux/macOS/Git Bash with base64 and gzip): sh research/archive/restore_r319_r320_runners.sh

R319 runner is gzip-compressed then base64-encoded across research/archive/R319_runner_source_b64.part01 through part08. Original gzip size 8,547 bytes, gzip SHA-256 fddbddc87da9e768e3373f244174d65bf51067e1611ece4ad9e48343125bdf96; decompressed Python source SHA-256 99d6125a8c61f4a2681350b473531a608c24987d57fe58bd748f8ffb2247317f. Each of its eight base64 part files was read back from GitHub and its SHA-256 matched the source-derived part hash before publication.

R320 runner is gzip-compressed then base64-encoded across research/archive/R320_runner_source_b64_small.part01 through part08. Original gzip size 4,002 bytes, gzip SHA-256 92b5e6ffe91baf2912b072aba7fbd2fa2e011240e4352d265176067cd9ba78f2; decompressed Python source SHA-256 0e3ba8c147b1ec3b1759c84e60f806c06316dc5bfe83187a4f30340cfb83753d. It imports the R319 loader/simulator from /tmp/r319_pullback_research.py. The archived R320 file corrects two comments that incorrectly said 486 configs; executable logic still screened 162 configurations.

Runner environment used: Python 3.13.5, pandas 2.2.3, NumPy 2.3.5, Numba 0.65.1. Run R319 first; then run R320. R319 outputs to /tmp/r319_outputs and R320 to /tmp/r320_outputs. The scripts generate the full grid, selected-candidate trade ledger and compact JSON. The compact JSON archives in this folder are concise recorded summaries rather than raw byte copies of the original runner output.

The results were exploratory and committed after the calculation, not as an independent pre-outcome preregistration. 2019–2025 are project-contaminated; the protected 2026 sample remained unopened. No strategy passed.