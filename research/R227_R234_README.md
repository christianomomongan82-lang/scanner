# R227–R234 batch archive

This branch stores the R227–R234 batch summary and audit. The downloadable ZIP has the exact local Python engine, independent audit runner, all instrument discovery trade ledgers, selected forward/OOS ledgers, source hashes, annual cohorts, cost sensitivity, direction splits, bootstrap, and selection sensitivity.

- 8 hypotheses × 10 H1 index CFD datasets.
- 6 discovery-eligible candidates advanced to forward/OOS; R231 failed the minimum 100-trade discovery sample and R232 failed discovery PF.
- No candidate passed the forward acceptance gates.
- Data are raw BID H1 OHLC. Flat candles are skipped rather than forward-filled; entries use next exact H1 open.
- Audit: 180/180 causality-prefix checks, 92/92 unique ledger CSVs, 1,380/1,380 per-ledger checks, 60,074 trade rows inspected.
- Costs are modeled 0/1/2/3/5 bps and are not verified live broker/prop execution costs.

The local ZIP is the canonical copy of the full runner. This GitHub branch is an audit/results mirror, not the main branch.
