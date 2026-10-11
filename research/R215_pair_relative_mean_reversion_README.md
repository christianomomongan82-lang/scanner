# R215 — relative-return divergence mean reversion

R215 registered an intraday US-index pair mean-reversion hypothesis using only raw M5 BID OHLC. This branch preserves the discovery-stage mirror, results report, candidate ledger summary, source integrity checks, and metadata. The exact local engine and all three full discovery trade ledgers are in the conversation's R215 local execution bundle.

## Run the discovery stage

Install Python 3.10+, NumPy and pandas. Extract the four raw M5 CSVs from the preserved scanner R205 Actions artifacts and pass their directory:

`python research/r215_pair_relative_mean_reversion.py --data-dir /path/to/r205_snapshot --out-dir /path/to/r215-results`

The code uses exact timestamp inner joins, does not interpolate or forward-fill flat bars, and checks feature prefix equivalence. The locked eligibility rule is at least 30 closed discovery trades and PF >= 1.00 at modeled 2 bps. If no pair qualifies, it stops without evaluating forward/OOS or tuning thresholds.

The data stream is BID-only. Costs are modeled, not verified live broker/prop costs; this is not trading-ready validation.
