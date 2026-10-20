# R311 — Artifact Index

**Binary verdict: GAGAL.** The preregistered Tokyo-fixing fade is closed; no alpha block retained and no funded challenge replay was run.

- [Locked preregistration](R311_EURUSD_TOKYO_FIX_POST_EVENT_REVERSAL_PREREGISTRATION.md)
- [Local runner bootstrap with source and serialization hashes](r311_eurusd_tokyo_fix.py)
- [Implementation amendment 01 — timestamp-grid correction before PnL](R311_IMPLEMENTATION_AMENDMENT_01.md)
- [Implementation amendment 02 — JSON serialization-only correction](R311_IMPLEMENTATION_AMENDMENT_02.md)
- [Final report](R311_FINAL_REPORT.md)
- [Compact metrics and gate JSON](R311_RESULTS_COMPACT.json)
- [Data / output manifest](R311_DATA_MANIFEST.md)

## Core result

At +1 pip additional round-trip friction, discovery 2017–2020: 750 trades, -360.843R, PF_R 0.3445. Validation 2021: 143 trades, -73.799R, PF_R 0.3161. Both periods are negative even with zero added cost, and the validation weekly bootstrap 95% interval is entirely below zero.

The four year-partitions of eligibility/score data and three execution streams are retained as compressed CSV artifacts. Full row-level artifacts are indexed in the data manifest. 2022–2025 PnL was not calculated; this historical screen is not pristine OOS and is not funded-ready.
