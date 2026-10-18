# R300 — Artifact Index

**Verdict: GAGAL.** This is a closed historical signal test, not a funded-ready strategy.

- [Locked preregistration](R300_EURUSD_LONDON_FIX_POST_EVENT_REVERSAL_PREREGISTRATION.md)
- [Data manifest](R300_DATA_MANIFEST.md)
- [Pre-outcome integrity metrics](R300_preoutcome_data_audit.json)
- [Full pre-outcome eligible/ineligible date audit (gzip CSV)](R300_preoutcome_event_eligibility_audit.csv.gz)
- [Exact local replay runner](r300_eurusd_london_fix.py)
- [Final report](R300_FINAL_REPORT.md)
- [Compact result metrics](R300_results_compact.json)
- [Annual summary](R300_annual_summary.csv)
- [Validation weekly bootstrap input](R300_validation_weekly_net_R.csv)
- Full trade ledger and event/skip audit are available as generated session artifacts: [trade ledger CSV](sandbox:/mnt/data/r300_results/R300_trade_ledger_fade_and_follow.csv) · [event audit CSV](sandbox:/mnt/data/r300_results/R300_event_audit.csv)

## Summary

Primary fade: 1,024 discovery trades, −257.01R/PF 0.573 at +1 extra pip; 257 validation trades, −59.98R/PF 0.580. Validation weekly bootstrap 95% CI: [−1.5884R, −0.6723R]. Four of 14 gates passed, so the locked binary verdict is GAGAL. The matched follow-direction stream was also net negative. No 2022+ R300 PnL was calculated.