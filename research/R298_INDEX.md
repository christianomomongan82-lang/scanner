# R298 — Artifact Index

**Verdict: GAGAL.** Complete candidate results and audit files are stored individually in this repository. You do not need to download the research ZIP to inspect the result.

## Start here
- [Final report](R298_FINAL_REPORT.md) — locked test, results, gates and disposition.
- [Preregistration](R298_XAUUSD_LONDON_ASIA_RANGE_SWEEP_RECLAIM_PREREGISTRATION.md) — hypothesis and thresholds frozen before PnL calculation.
- [Compact results JSON](R298_results_compact.json) — machine-readable outcome and gate status.
- [Annual summary](R298_annual_summary.csv) — year-by-year scores.
- [Reproduction notes](README_R298.md) — data, script and interpretation notes.
- [Preregi­stration pointer](R298_PREREGISTRATION_LINK.md).

## Full detail
- [Trade ledger](R298_trade_ledger.csv) — all completed trades with executable-side outcomes.
- [London signal audit](R298_london_signal_audit.csv) — detected signals and eligibility disposition.
- [Event-quality audit](R298_event_quality_audit.csv) — event exclusions and data-quality checks.
- [Asian-window quality audit](R298_asian_window_quality_audit.csv) — range-window completeness and active-bar checks.
- [Validation weekly net R](R298_validation_weekly_net_R.csv) — weekly series used by the validation bootstrap.
- [Runner](r298_xauusd_london_sweep_reclaim.py) — local replay implementation.

## Locked outcome
At +$0.30/oz extra cost: discovery (2016–2020) = 313 trades, −285.893R, PF_R 0.297; validation (2021–2025) = 285 trades, −178.933R, PF_R 0.409. Both remained negative with zero added cost, and the validation weekly bootstrap 95% CI was entirely below zero. Do not tune this family on the same periods; no 2026 candidate PnL was calculated and no alpha was promoted.
