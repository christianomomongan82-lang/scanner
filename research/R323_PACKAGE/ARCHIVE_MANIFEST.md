# R323 archive status — V2 audit, 2026-10-22

**Official disposition: GAGAL — DATA/PROCESS for package closure.**  
**Underlying pre-outcome finding: GAGAL — DATA/SAMPLE. PnL was not calculated.**

The earlier line that this archive was "closed for reproducibility" is superseded by this V2 audit. Reports, config, eligibility audit and logs exist, but the project-wide V2 contract requires an exact runner committed as a normal repository file, all required artifacts/readbacks, and reconciled master ledger/family map/PROJECT_STATE. The runner was attached only as an Actions artifact, and no complete V2 card/preflight/closeout was read-back-verified for R323. Therefore R323 is not CLOSED and blocks further search until its missing archive elements are restored or explicitly dispositioned as unresolvable.

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
