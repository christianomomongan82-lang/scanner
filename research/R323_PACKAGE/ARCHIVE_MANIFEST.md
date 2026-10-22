# R323 archive closeout

Archive review date: 2026-10-22 UTC.

## Verified in the repository
- Preregistration: `research/R323_FX_CURRENCY_STRENGTH_PREREGISTRATION.md`
- Terminal report: `research/R323_PACKAGE/report.md`
- Result JSON: `research/R323_PACKAGE/results.json`
- Data/config/environment/run files, validator log, rerun-hash check, scorecards and annual cohort files under `research/R323_PACKAGE/`
- Eligibility/skip audit archive: `research/R323_PACKAGE/eligibility_skip_audit.csv.gz.b64`
- Reproducible code artifact attached to GitHub Actions run 39721131341; artifact ID 12400854388, name `R323-local-compute-code`.
- Data-only workflow run: https://github.com/christianomomongan82-lang/scanner/actions/runs/39719343805

## Deliberately not generated
- `full_grid.csv.gz.b64`: no parameter grid was run; R323 was a single preregistered configuration.
- `finalist_trade_ledger.csv.gz.b64`: no outcome/PnL ledger was generated because the frozen sample gate failed before profitability calculation.
- PnL, PF, drawdown and bootstrap are explicitly recorded as not calculated in the terminal report/results JSON. Creating those files now would falsely imply computations that never occurred.

## Final status
**Archive closed for reproducibility and honest outcome accounting. R323 = FAIL — DATA/SAMPLE.** The data acquisition, audit, preregistration, code, deterministic rerun check, validator and terminal sample-gate report are preserved. No claim of a trading edge is made.
