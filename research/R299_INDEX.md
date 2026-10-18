# R299 — Artifact Index

**Binary verdict: GAGAL.** The candidate is closed; no parameter rescue.

- [Pre-registration](R299_USATECH_LEADS_USA500_30M_PREREGISTRATION.md) — locked hypothesis, data cutoff, execution, modeled costs, and pass/fail gates.
- [Final report](R299_FINAL_REPORT.md) — discovery/validation metrics and gate outcomes.
- [Reproduction audit](R299_REPRODUCTION_AUDIT_20261018.md) — source hashes, replay match, and command.
- [Exact replay runner](r299_usatech_leads_usa500_30m.py) — deterministic local Python runner; checks both extracted member SHA-256 values.
- [Original machine-readable results](R299_results_compact.json).
- [Timestamp-alignment amendment](R299_DATA_QUALITY_AMENDMENT.md).
- [Annual summary](R299_annual_summary.csv).

Source archives were workflow artifacts #11709864394 (USA500) and #11710370389 (USATECH). The runner reads their exact extracted M5 gzip members, excludes timestamps from 2022-01-01 UTC onward before scoring, and generates the full trade ledger, event/skip audit, weekly net-R series, annual summary, and metrics JSON. No 2022+ strategy PnL is calculated.