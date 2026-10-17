# R298 — XAUUSD London Asian-Range Sweep-and-Reclaim Reversal

**Verdict: GAGAL.** This candidate was preregistered before PnL calculation. All rows dated 2026-01-01 UTC or later were excluded before signal construction.

## Registered method
Build the Asian midpoint range from 00:00–05:55 UTC only when all 72 BID/ASK bars are active; during 07:00–10:00 Europe/London, take the first M5 sweep beyond 0.10×range that closes back inside; execute at signal timestamp +10 minutes; stop at the signal bar's executable-side extreme; target the Asian midpoint; minimum planned reward/risk 1.00; four-hour maximum hold; stop-first when stop and target touch in the same bar. Costs include paired BID/ASK sides plus added stress of $0/$0.10/$0.30/$0.50 per ounce round trip. No parameter rescue was permitted.

## Data-quality audit
- Source: XAUUSD M5 BID/ASK archive 12031270051 / collection run 38859918137.
- Registered hashes passed: BID b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575; ASK b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9.
- Paired source rows per side: 947,326; used through 2025-12-31: 877,930; excluded 2026+: 69,396.
- Paired-active bars before cutoff: 708,724; eligible full Asian-window dates: 2,553 of 3,109 audited dates.
- First-reclaim candidates: 894; completed trades: 598. Signal skips: 261 failed minimum RR, 23 stop no longer on the adverse side at entry, 12 midpoint target not favorable. No 2026 PnL was calculated.

## Results
Net trade R and PF_R after the additional per-ounce cost stress:

| Period | Added cost | Trades | Net R | PF_R | Win rate | Max closed DD (R) |
|---|---:|---:|---:|---:|---:|---:|
| Discovery 2016–2020 | $0.00/oz | 313 | -132.434 | 0.515 | 23.3% | 137.615 |
| Discovery 2016–2020 | $0.10/oz | 313 | -183.587 | 0.422 | 23.3% | 187.928 |
| Discovery 2016–2020 | $0.30/oz | 313 | -285.893 | 0.297 | 23.0% | 288.555 |
| Discovery 2016–2020 | $0.50/oz | 313 | -388.198 | 0.218 | 22.4% | 389.480 |
| Validation 2021–2025 | $0.00/oz | 285 | -100.768 | 0.575 | 20.7% | 102.748 |
| Validation 2021–2025 | $0.10/oz | 285 | -126.823 | 0.511 | 20.7% | 128.780 |
| Validation 2021–2025 | $0.30/oz | 285 | -178.933 | 0.409 | 20.7% | 180.844 |
| Validation 2021–2025 | $0.50/oz | 285 | -231.044 | 0.333 | 20.7% | 232.908 |

At +$0.30/oz all five discovery annual cohorts and all five validation annual cohorts were negative. Validation's 10,000-resample circular four-week weekly-net-R bootstrap (seed 298; 261 Monday-start weeks including zero-trade weeks) had mean -0.68557R/week and 95% CI [-0.89792, -0.47209]R/week, entirely below zero.

## Locked hard gates

| Gate | Result |
|---|---|
| Discovery at least 75 trades | PASS |
| Discovery positive net R at +$0.30/oz | FAIL |
| Discovery PF_R ≥ 1.05 | FAIL |
| Discovery at least 3/5 positive years | FAIL |
| Discovery positive net R and PF_R ≥ 0.90 at +$0.50/oz | FAIL |
| Validation at least 100 trades | PASS |
| Validation positive net R and PF_R ≥ 1.05 at +$0.30/oz | FAIL |
| Validation at least 3/5 positive years | FAIL |
| Validation bootstrap lower 95% bound > 0 | FAIL |
| Validation positive net R and PF_R ≥ 0.90 at +$0.50/oz | FAIL |

**Disposition: GAGAL.** The strategy loses even with zero extra friction; this is not a marginal spread sensitivity. Do not alter the sweep threshold, sessions, target, stop, delay, RR gate, or holding time on these dates. Do not reverse direction as a rescue. No alpha block is promoted, no 2026 PnL is opened, and no funded challenge replay is run.

## Limitations
2021–2025 is research-contaminated and not pristine program-level OOS. Historical BID/ASK quotes do not verify actual FundedNext fills, contract value, commission, slippage, swaps, margin or floating-account equity/DLL/MLL behavior. Even a candidate passing these historical screens would still need separate untouched-holdout and funded-account replay.

Artifacts: locked [preregistration](R298_XAUUSD_LONDON_ASIA_RANGE_SWEEP_RECLAIM_PREREGISTRATION.md); local trade ledger, event-quality audit, annual summary, weekly bootstrap series and runner are included in the research bundle.
