# R301 — Artifact Index

**Binary verdict: GAGAL.** The safe-haven delayed-response candidate is closed. XAUUSD 2026 was not scored.

- [Locked preregistration](R301_XAUUSD_SAFE_HAVEN_DELAYED_HEDGE_RESPONSE_PREREGISTRATION.md)
- [Final report](R301_FINAL_REPORT.md)
- [Compact results and gate JSON](R301_results_compact.json)
- [Candidate annual summary, primary cost](R301_candidate_annual_summary.csv)
- [Gate summary](R301_gate_summary.csv)
- [Validation weekly bootstrap result](R301_validation_weekly_bootstrap.json)
- [Pre-outcome data audit](R301_preoutcome_data_audit.json)
- [Data manifest](R301_DATA_MANIFEST.md)
- [Session eligibility summary](R301_session_eligibility_summary.csv.gz)
- [Exact replay runner (compressed Python source)](r301_xau_safe_haven_delayed_response.py.gz)
- [Candidate primary-cost trade ledger (compressed CSV)](R301_candidate_trade_ledger_primary_cost030.csv.gz)
- [Validation bootstrap input series (compressed CSV)](R301_validation_weekly_net_R.csv.gz)

The full 38,480-row all-cost/all-delay/all-stream trade ledger and 4.8 MB pre-outcome timestamp eligibility audit remain as session artifacts because they are too large for the repository contents API payload. They are available in the current ChatGPT session output package.

## Locked result

At +$0.30/oz, discovery (2017–2020) has 315 trades, −170.908R and PF_R 0.327; validation (2021–2025) has 588 trades, −189.406R and PF_R 0.509. Both partitions are negative at zero added cost. Validation bootstrap mean is −0.72293R/week, 95% CI [−0.91609R, −0.53769R]. Two of nine gates passed. No 2026 outcome was calculated.
