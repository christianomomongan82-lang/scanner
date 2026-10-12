# R235–R242 batch archive

This branch stores results and the deep audit for eight registered H1 price-action hypotheses. The downloadable local ZIP contains all 80 discovery ledgers, selected forward/OOS ledgers, exact batch engine, final auditor, source SHA-256 fingerprints, 190 causality checks, 88 ledger audit results, cost stress at 0/1/2/3/5 bps, annual cohorts, bootstrap, direction/half-period diagnostics, common-history selection sensitivity, and cumulative R218–R242 summary.

## Reproduce

Python 3.10+ with NumPy and pandas. Extract the ten H1 source CSVs from the retained R205 snapshot artifacts to a directory, then run:

1. python engine/r235_r242_batch.py --data-dir /path/to/r205_snapshot --out-dir /path/to/results --bootstrap 2000
2. Set R235_OUT_DIR=/path/to/results and R235_DATA_DIR=/path/to/r205_snapshot, then run python engine/r235_finalize.py

Discovery spans 2017–2021, forward spans 2022–2025, and OOS spans 2026 through the common source cutoff. Instrument selection is discovery-only, with >=100 trades and PF>=1.00 at modeled 2 bps. Final acceptance also requires forward PF>=1.15 at 1 and 2 bps, annual cohort stability, and Holm-adjusted positive-expectancy bootstrap p<0.05.

No strategy passed. Four hypotheses failed discovery; the other four failed forward or inferential gates. Inputs are BID-only and costs are modeled; this does not establish live/funded readiness.