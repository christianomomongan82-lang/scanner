# R282 — EURUSD weekend-reopening gap fade

**Verdict: INVALID TEST / DATA INADEQUATE — not evidence that gap-fading has or lacks alpha. No trades were evaluated.**

## What happened
The locked event detector found only three candidate long closures in nearly ten years, and all three failed the exact T+10-minute data-continuity requirement. The source collector used Dukascopy's `-fl` option; the archive's synthetic/flat-row removal is not merely a small cleaning step here. It has erased most of the opening-period observations required to identify Sunday reopening and execute a ten-minute delayed entry. As a result, this archive cannot validly test the preregistered weekly-reopening hypothesis.

## Data audit
- Input archive SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- Paired M1 rows after heuristic removal: 3,718,698.
- Detected >=36-hour gaps meeting the literal Friday-to-Sunday/Monday day-of-week rule: 3.
- Tradable signals after exact T+10 sequence requirement: 0.
- Closed trades: 0. PF, net pips and drawdown are **undefined**, not zero-edge metrics.
- Inspection of raw timestamps shows long closures often resume at Monday 00:00 UTC (e.g. 2017-12-29 21:59 to 2018-01-01 00:00) rather than retaining the Sunday reopen rows. This matches the known `-fl` source limitation.

## Decision
- Stop R282. Do not loosen the event rule or substitute Monday reopening for Sunday after observing this failure.
- Do not claim weekend-gap fading is disproven; the data cannot answer the question.
- No 2022–2025 strategy outcomes were calculated; no holdout was opened; no candidate was selected.
- A future retry requires an independently obtained, verified EURUSD BID/ASK M1 source that retains genuine weekend-reopen observations and supports exact delayed entry. The current archive is unsuitable.
- No GitHub Actions backtest workflow was created or dispatched.

## Artifacts
- Preregistration: `research/R282_EURUSD_WEEKEND_GAP_FADE_PREREGISTRATION.md`
- Runner/audit: `research/r282_eurusd_weekend_gap_fade.py`
- Results: `research/R282_results_compact.json`
- Event audit: `research/R282_event_audit.csv`
