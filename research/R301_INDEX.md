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
- Session eligibility summary: generated in the current ChatGPT run as a local audit artifact; it is not committed in this GitHub branch.
- Exact replay runner: available as a session artifact at `/mnt/data/r301_xau_safe_haven_delayed_response.py`; it is not committed in this GitHub branch.
- Candidate primary-cost trade ledger: generated locally; the compact 903-trade score-period ledger is available at `/mnt/data/r301_results/R301_candidate_trade_ledger_compact.csv`, but it is not committed in this GitHub branch.
- Validation weekly bootstrap input series: available locally at `/mnt/data/r301_results/R301_validation_weekly_net_R.csv.gz`; it is not committed in this GitHub branch. The bootstrap result itself is in the JSON above.

The full 38,480-row all-cost/all-delay/all-stream trade ledger and 4.8 MB pre-outcome timestamp eligibility audit remain as session artifacts because the repository writes available in this run did not safely commit binary payloads. They are available in the current ChatGPT session output package. The text report, preregistration, compact JSON, annual summary, gate summary, data manifest, family map, master ledger and project checkpoint are committed to this branch.

## Locked result

At +$0.30/oz, discovery (2017–2020) has 315 trades, −170.908R and PF_R 0.327; validation (2021–2025) has 588 trades, −189.406R and PF_R 0.509. Both partitions are negative at zero added cost. Validation bootstrap mean is −0.72293R/week, 95% CI [−0.91609R, −0.53769R]. Three of nine gates passed. No 2026 outcome was calculated.
