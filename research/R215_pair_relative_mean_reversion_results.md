# R215 — US-index relative-return divergence mean reversion

**Decision: REJECT — no discovery-eligible pair.**

## Locked hypothesis

- For each completed M5 BID candle, compute 60-minute raw relative log return and z-score it over the trailing 144 M5 observations. No indicators or forward-filling.
- Entry only on a crossing of |z| from below 2.0 to at least 2.0; fade relative outperformance. Exit at <=0.25 z reversion, >=3.5 z divergence stop, or 12 elapsed hours. Entries at next M5 open; exits after a completed-close trigger at the next paired active open.
- Three pair candidates only: US500 vs Tech100, US500 vs US30, US500 vs US Small Cap 2000. Costs modeled at 1 and 2 bp round-trip per leg on equal-weighted pair exposure.
- Locked discovery eligibility: >=30 closed trades and PF@2bp >=1.00; if eligible select fewest discovery trades, tie-break higher PF@2bp. Since none qualifies, forward/OOS were not run and no replacement was selected.
- Periods: discovery 2017–2021; forward 2022–2025; OOS 2026 through common snapshot cutoff.

## Discovery results

| Pair | Closed | PF @1 bp | PF @2 bp | Eligible |
|---|---:|---:|---:|---|
| US500 vs US Tech 100 | 2700 | 0.622 | 0.427 | NO |
| US500 vs US30 | 2920 | 0.508 | 0.261 | NO |
| US500 vs US Small Cap 2000 | 2654 | 0.932 | 0.726 | NO |

## Audit

- Source integrity checks: PASS.
- Causal truncation-prefix checks: PASS.
- Automated checks: 4/4 passed.
- Forward/OOS intentionally not run because the pre-registered discovery gate failed. This is a rejection, not a request to tune thresholds.
- The data is BID-only; costs are stress assumptions, not verified broker/prop costs. No live/funded-readiness conclusion is supported.
