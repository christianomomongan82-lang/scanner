# R288 — Cross-Index Residual Follow-Through (pre-registration)

Date locked: 2026-10-17 (before calculating any 2022–2026 PnL).

## Lineage and purpose
- Parent diagnostic: R287 cross-index residual fade. R287 failed; its matched opposite-direction diagnostic was materially better on the same 2017–2021 events. That direction choice was observed after outcomes, so the historical R287 sample is disqualified for promotion of this child.
- Child ID: R288_US_INDEX_INTRADAY_RESIDUAL_FOLLOW.
- Inherited blocks: synchronized four-index panel, same-date cross-sectional median residual, one event at most per New York session, per-symbol residual Q75 fitted on 2017–2020, strict cash-session data quality, entry after five-minute manual delay, exit at 15:55 ET bar open, modeled transaction-cost stress.
- Single mutation: follow the signed residual instead of fading it. Do not alter threshold, universe, signal window, event ranking, times, or cost model after seeing child results.

## Data and provenance
- Source: cached GitHub Actions raw M5 BID-only R205 artifacts, run 38160487617:
  - USA500 artifact 11709864394, archive SHA-256 21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac.
  - USATECH artifact 11710370389, archive SHA-256 91c7d44b0487e98eeea021712528910475e626bf433220a007629f3005fc66ad.
  - USA30 artifact 11710730507, archive SHA-256 53a54804f0584c69d52f41af08534e00effea66e7cc31872ae0438e7907e0fe6.
  - USSC2000 artifact 11710111254, archive SHA-256 52216f5623a974dfaa0fb19e3cb28e2b2db589f1c07cef5cc8e5e2b383638872.
- Source is M5 BID-only. Cost stresses 1/2/4 bp round trip are modeled assumptions, not observed CFD spread/slippage. Repeated-flat bar removal is a conservative heuristic, not verified tick-level data integrity.
- Thresholds are fit only on eligible 2017–2020 dates. R287's 2017–2021 results are not used to fit thresholds or evaluate this child.
- 2022–2025 is project-contaminated exploratory evidence, not an untouched program-level holdout. 2026 is a later chronological check but is not claimed pristine at the program level.

## Locked rules
1. Convert timestamps to America/New_York; eligible cash-session dates must contain exactly the expected 78 M5 bars from 09:30 through 15:55 ET, valid OHLC, no duplicate timestamps, and no repeated-flat candidate bars.
2. Require at least three eligible index symbols on a date. For each symbol, calculate signal return from the 10:00 ET bar open to the 12:55 ET bar close; residual = that return minus the same-date median return across eligible symbols.
3. Fit each symbol's Q75 absolute residual on eligible 2017–2020 rows only. Normalize each symbol's absolute residual by its frozen Q75.
4. Select the eligible symbol with the highest normalized score per date, with alphabetical symbol as deterministic tie-breaker. Skip if score < 1 or residual = 0.
5. Direction follows the sign of residual. Entry is the 13:05 ET bar open (five minutes after the 13:00 ET signal-close decision), exit is the 15:55 ET bar open. One position at a time; no compounding or funded replay in this signal test.
6. Gross return is the directional percent change between entry and exit converted to basis points. Subtract fixed 1, 2, and 4 bp round-trip cost stresses; do not claim these equal provider costs.

## Locked scorecard and binary gates
Report candidate and matched fade-parent on identical events for 2022–2025 by year and 2026 through the latest valid timestamp in the source. Calculate trade count, net bp, PF, mean/median bp, max closed-trade drawdown in bp, win rate, monthly/weekly aggregate series, and four-week circular block-bootstrap CI for mean weekly net bp.
- 2022–2025 gates: at 2 bp, at least 300 trades, net > 0, PF >= 1.05, and at least 3 of 4 calendar years positive; at 4 bp, PF >= 0.90; four-week block-bootstrap 95% CI lower bound for mean weekly net bp must be > 0.
- 2026 gates: at least 50 trades, 2 bp net > 0 and PF >= 1.00, and 4 bp net > 0.
- Binary R288 verdict is LULUS only if every listed gate passes. Any failed gate = GAGAL and no threshold/time/direction rescue on these data.
- Even if R288 passes its historical gates, it is not funded-ready: BID-only prices, assumed costs, uncertain CFD contract conversion, no verified account-equity DLL/MLL path, and contaminated program-level periods require further independent validation before any funded challenge replay.

## Integrity and limits
- No GitHub Actions backtest is used; calculations run locally in Python.
- The result, exact runner, per-trade ledger, annual tables, weekly bootstrap output, and checkpoint are to be archived after the locked computation.
- This pre-registration is immutable. Correcting an implementation/data-quality defect requires a dated amendment committed before re-running the affected calculation, not a post-result rule change.
