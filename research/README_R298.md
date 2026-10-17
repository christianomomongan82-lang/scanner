# R298 Research Package

## Verdict
GAGAL. Do not tune/reverse the same signal against 2016–2025 and do not open 2026 for this candidate.

## Contents
- `R298_FINAL_REPORT.md`: human-readable outcomes and locked gate table.
- `R298_results_compact.json`: machine-readable metrics, data checks, and gate outcomes.
- `R298_trade_ledger.csv`: one row per completed trade.
- `R298_event_quality_audit.csv`: each first-reclaim event outcome or skip reason.
- `R298_asian_window_quality_audit.csv`: daily Asian-window activity/completeness checks.
- `R298_london_signal_audit.csv`: daily London session signal audit.
- `R298_annual_summary.csv`: annual metrics at all registered cost levels.
- `R298_validation_weekly_net_R.csv`: validation weekly net R series used for bootstrap.
- `r298_xauusd_london_sweep_reclaim.py`: local runner used for the result.
- `R298_PREREGISTRATION_LINK.md`: immutable pre-outcome specification in GitHub.

## Re-run
Run with Python, pandas and numpy available:

```bash
python r298_xauusd_london_sweep_reclaim.py --data-dir /path/to/r298data --out-dir ./R298_outputs
```

The two source archives are XAUUSD M5 BID/ASK gzipped CSV files. Input SHA-256 hashes must match the report. The runner fails if the hashes, timestamp pairing, timestamp uniqueness, M5 alignment, or OHLC ordering fail. It hard-excludes timestamps at/after 2026-01-01 UTC before any strategy event construction.

## Execution limitations
The source is historical XAUUSD BID/ASK quote data, not verified FundedNext account fills. There is no contract-size, commission, slippage, swap, margin, floating-equity, or two-phase challenge replay in this package.