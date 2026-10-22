# R327 — sample-gate report

**Verdict: FAIL — DATA/SAMPLE. Profitability was not computed.**

Registered hypothesis: EURUSD overnight directional stretch fade, using the previous weekday's 18:00 UTC to current weekday's 05:59 UTC move, a 20-valid-session rolling median threshold, contrarian direction, entry at 06:05 UTC, overnight-extreme stop, 1.5R target and force close at 11:59 UTC.

Registration commit: e9034bf5983aa3c9b8fde2331777be3a2b731477  
Input SHA-256: b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e

| Cohort | Candidates before delay filters | Eligible trades | Required |
|---|---:|---:|---:|
| Discovery 2017–2020 | 395 | 342 | 500 |
| Confirmation A 2021–2023 | 311 | 272 | 300 |
| Holdout B 2024–2025 | 208 | 187 | 200 |

Annual eligible counts were 2017: 90; 2018: 80; 2019: 84; 2020: 88; 2021: 89; 2022: 93; 2023: 90; 2024: 95; 2025: 92. Per-year floors passed, but all three cohort-level totals failed. Therefore the test stopped before outcome calculation. It must not be rescued by lowering the threshold after seeing these sample counts.
