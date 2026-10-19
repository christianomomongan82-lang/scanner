# R304 — Data and Output Manifest

## Source
- Repo / branch: christianomomongan82-lang/scanner / local-backtest/r189-dukascopy-history.
- Data-only artifact: 11959096102; collection run 38697080604. No backtest ran in GitHub Actions.
- ZIP SHA-256: b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e.
- BID SHA-256: b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc.
- ASK SHA-256: 52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b.
- Raw rows per side 4,415,493; repeated flat rows removed 696,795; active rows 3,718,698; gaps >1 minute 12,018.
- Scored periods only 2017–2021. No R304 PnL after 2021.

## Local output hashes
| File | SHA-256 | Bytes |
|---|---|---:|
| r304_preoutcome_audit.py | 9f5852d543902c5937c08368f2922d7dfe5475527d741fb5e5380ff272a97c22 | 12,271 |
| R304_data_audit_preoutcome.json | 521f77aaa2bbe4eef6cd1a277abeb1ef4c904e4848295a9f53a7cfab40d17979 | 5,198 |
| R304_preoutcome_event_eligibility.csv | fb1f2a8bed616bd0ac457b08dd89113b6729c2857e3c3b26ab90a4c080520b42 | 1,315,753 |
| r304_backtest.py | b865986a26f2322f6074907a1529cacf8b205ea8ff5ea6fd9bccab40d9b5459a | 17,129 |
| R304_results_compact.json | 90f2facbd11fcbaebc27bead0afd4321708b7b2073856d126d5b5328ae41c9ab | 43,131 |
| R304_trade_ledger_2017_2021.csv | a1f25a7fa5809047a39029cef481a02aa088e5210c536e2d2584a3e3378e5b34 | 961,137 |
| R304_mirror_direction_control_2017_2021.csv | c55aabc9e403e6acc62c1f59d58238e1a7a6dd41d2c782d5b658f5d58ed4e219 | 961,745 |
| R304_period_annual_summary.csv | 01ca47dc1b54bae597aa2ce81304ef8fad0ffc0e07d1a0ebc62b6b8385bcd317 | 6,626 |
| R304_validation_weekly_net_R.csv | ff4d4588799541db716c8585ed6bfad9fe3e72eab5db38edbce7f281db9b39b7 | 1,216 |
| R304_validation_weekly_bootstrap.json | 36a2c8c8b883079aed1c882ce93cb2d812da563a51c7b718a1e5ba092457a522 | 313 |
| R304_FINAL_REPORT.md | c9e29d1c21fa059890205252bc4ca512a649d0756de4fdf9dcc4c95fa913d5b5 | 8,491 (detailed local report) |

## Reproducibility
The compact GitHub scorecard/report are normalized archival summaries, not byte-for-byte copies of the richer local result JSON and row-level ledgers. The local runner and full ledgers have not been verified as committed regular files in the active branch. Therefore repository-only reproduction remains a failed gate. The report does not claim otherwise.