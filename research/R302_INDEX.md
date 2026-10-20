# R302 — Artifact Index

**Binary verdict: GAGAL.** No alpha block retained. No funded challenge replay was run. Protected XAUUSD 2026 remains unopened.

- [Locked preregistration](R302_XAUUSD_PM_AUCTION_EXTENSION_FADE_PREREGISTRATION.md)
- [Locked runner bootstrap](r302_xauusd_pm_auction_extension_fade.py) — expands to the checksum-locked implementation. A one-shot recovery replay was used to publish the missing rows after the original hashes were reproduced; that workflow has been removed.
- [Final report](R302_FINAL_REPORT.md)
- [Compact metrics and gate JSON](R302_results_compact.json)
- [Data-integrity audit](R302_data_audit.json)
- [Period and annual scorecard](R302_period_annual_summary.csv)
- [Validation weekly bootstrap result](R302_validation_weekly_bootstrap.json)
- [Data/ledger manifest and local-output hashes](R302_DATA_MANIFEST.md)
- [Ledger restoration notes and repository readback verification](R302_LEDGER_REASSEMBLY.md)
- [Primary-cost trade ledger — 387 rows](R302_primary_cost_trade_ledger.csv)
- [Pre-outcome eligibility audit — 2,336 rows](R302_preoutcome_eligibility_audit.csv)
- [All cost/delay streams and skip audit — 4,644 rows](R302_all_cost_delay_streams_and_skips.csv)
- [All valid trade variants — 4,638 rows](R302_all_valid_trade_ledger.csv)

All four detailed CSVs are committed in this branch, with pre-commit SHA-256 values matching the original manifest and post-push GitHub tree metadata confirming the files and exact byte sizes. See the restoration notes for the commit and verification record.

## Locked result

At $0.30/oz additional round-trip friction, discovery 2017–2020 produced 179 trades, −32.964R and PF_R 0.640. Validation 2021–2025 produced 208 trades, −26.991R and PF_R 0.730. The validation bootstrap mean was −0.10302R/week with a 95% interval [−0.18945, −0.01557]. Only 3 of 8 preregistered historical-screen gates passed.

The scheduled-clock proxy includes weekday timestamps whether or not the LBMA PM auction officially published that day; no official IBA non-publication calendar was applied. The protected 2026 test remains locked. The result is not FundedNext-ready.
