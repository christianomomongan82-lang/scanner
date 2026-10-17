# R298 — Artifact Index

**Verdict: GAGAL.** The reports, code, trade ledger and audits are individual GitHub files. No ZIP download is needed to inspect results.

## Start here
- [Final report](R298_FINAL_REPORT.md) — results, gates and decision.
- [Preregistration](R298_XAUUSD_LONDON_ASIA_RANGE_SWEEP_RECLAIM_PREREGISTRATION.md) — frozen hypothesis and rules.
- [Compact results JSON](R298_results_compact.json) — machine-readable metrics and gate statuses.
- [Annual summary](R298_annual_summary.csv) — annual scores at all cost levels.
- [Runner source](r298_xauusd_london_sweep_reclaim.py) — exact replay implementation used.
- [Data manifest](R298_DATA_MANIFEST.md) — source hashes and availability caveat.
- [Reproduction notes](README_R298.md) — command and requirements.

## Full detail
- [Trade ledger](R298_trade_ledger.csv) — completed trades and executable-side outcomes.
- [Event-quality audit](R298_event_quality_audit.csv) — each event disposition and skip reason.
- [London signal audit](R298_london_signal_audit.csv) — detected first-reclaim signals.
- [Asian-window audit](R298_asian_window_quality_audit.csv) — range completeness and active-quote checks.
- [Validation weekly net-R series](R298_validation_weekly_net_R.csv) — input series for the validation bootstrap.
- [Preregistration pointer](R298_PREREGISTRATION_LINK.md).

## Locked outcome
At +$0.30/oz extra cost: discovery (2016–2020) = 313 trades, −285.893R, PF_R 0.297; validation (2021–2025) = 285 trades, −178.933R, PF_R 0.409. Both remained negative with zero added cost, and the validation weekly bootstrap 95% CI was entirely below zero. Do not tune this family on the same periods; no 2026 candidate PnL was calculated and no alpha was promoted.
