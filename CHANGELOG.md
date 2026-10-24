# Changelog

## 2026-10-24 — R330 Gate 1 entry-convention amendment

- Corrected Gate 1 to use canonical R191 entry: open of the next completed New York wall-clock H4 bar.
- The previous manual5m PF@1bp=1.491 is now diagnostic-only and is not counted as a canonical replication failure or used for any PASS/FAIL gate.
- Kept all R330 performance thresholds, discovery/forward/OOS criteria, neighborhood criteria, leave-one-out criteria and Stellar challenge simulation requirements unchanged.
- Added exact Gate 1 target comparisons for selection (n=78, PF@1bp=2.082), forward (n=70, PF@1bp=1.247, PF@2bp=1.241), and 2026 OOS (n=11, PF@2bp=1.954).
- The requested file R191_CANONICAL_index_trend_long.py is absent from the accessible repository snapshot. The available R192 ideal mode is the next-H4-open equivalent, but its stored R194-ledger results do not match the supplied references. Accordingly, status is GATE-MISMATCH (definisi konvensi entry), strategi belum dievaluasi; no pooled data, Gate 2, tuning, variant, or instrument removal was performed.


## 2026-10-24 — R330 canonical Gate 1 source correction

- Added the user-supplied `research/R191_CANONICAL_index_trend_long.py` to branch `research/r330-r191-pooled-ten-index`. Its H4 resample call, signal, 27-bar SL, RR=2 TP, and `sim` body are preserved; only a loader adapter reads the repository's `dl/<instrument>_m5.csv.gz` cache when the original XZ files are absent.
- Gate 1 now compares outputs from the canonical script to the locked selection/forward/OOS targets. R192 `ideal` and `manual5m` are diagnostic ledgers only.
- On Gate 1 mismatch, the runner exports `research/R330_G1_canonical_trades.csv`, `research/R330_G1_r192_ideal_trades.csv`, and `research/R330_G1_first_trade_mismatch.json`, then stops before Gate 2 and pooled criteria. No strategy tuning or instrument exclusion was introduced.
