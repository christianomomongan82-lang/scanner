# R302 — XAUUSD PM Benchmark Pre-Auction Extension Fade — Final Report

**Binary verdict: GAGAL.** The candidate is closed if any registered gate fails. The protected 2026 interval remains unopened.

## Primary result at +$0.30/oz additional cost

| Metric | Discovery 2017–2020 | Validation 2021–2025 |
|---|---:|---:|
| Trades | 179 | 208 |
| Net R | -32.9645 | -26.9914 |
| PF_R | 0.6398 | 0.7299 |
| Mean R/trade | -0.1842 | -0.1298 |
| Max closed-R DD | 34.8025 | 31.1873 |
| Positive years | 0/4 | 1/5 |

Validation weekly net-R bootstrap (262 calendar weeks including zero-trade weeks; circular four-week blocks; 10,000 resamples; seed 302): mean -0.10302R/week; 95% CI [-0.18945, -0.01557].

## Cost and execution sensitivity

- Validation at $0.00/oz added cost: 208 trades, -14.5730R, PF_R 0.8434.
- Validation at $0.50/oz added cost: 208 trades, -35.2704R, PF_R 0.6628.
- Validation with T+15-minute entry delay and $0.30/oz: 207 trades, -32.9171R, PF_R 0.6736.
- Matched continuation-direction control at $0.30/oz: discovery -50.8976R; validation -27.3964R.

## Registered gate outcomes

| Gate | Result |
|---|---|
| Data integrity | PASS |
| Minimum trade counts in both periods | PASS |
| Positive net R and PF_R >= 1.05 in both periods at $0.30/oz | FAIL |
| At least 3 of 5 validation years positive | FAIL |
| Validation weekly-bootstrap lower bound > 0 | FAIL |
| Validation net R positive at $0.50/oz cost | FAIL |
| Validation net R positive with T+15 delay at $0.30/oz | FAIL |
| Execution-path integrity | PASS |

**3 of 8 registered historical-screen gates pass.** The official IBA non-publication calendar was not applied, so the protected 2026 test remains locked even if this historical screen passes.

## Data integrity / scope

- Source: XAUUSD M5 BID/ASK, Dukascopy via existing GitHub raw-data artifact #12031270051. Actual source-member hashes are checked by the runner against the manifest.
- Exclusive cutoff 2026-01-01 UTC was applied before features and outcomes. No 2026 rows entered threshold history, event signals, trade PnL or summaries.
- Paired timestamps were joined exactly. Missing grid cells were not filled or synthesized; entries with incomplete required timestamp paths were excluded before outcome calculation.
- The official LBMA Gold Price PM auction is scheduled to start at 15:00 London time ([LBMA source](https://www.lbma.org.uk/prices-and-data/lbma-precious-metal-prices)); the dataset does not contain the historical non-publication calendar. The result is therefore a scheduled-clock proxy, not an auction-day-only estimate.
- 2021–2025 has been used by prior experiments and is program-contaminated, not pristine OOS. No FundedNext-ready claim is made. No challenge replay is reported as equivalent to the official floating-equity/DLL/MLL path.

## Exact artifacts

See [R302 index](R302_INDEX.md), [data manifest](R302_DATA_MANIFEST.md), and [ledger restoration notes](R302_LEDGER_REASSEMBLY.md). This report does not claim that the historical screen is a pristine OOS result or that the candidate can pass a funded challenge.
