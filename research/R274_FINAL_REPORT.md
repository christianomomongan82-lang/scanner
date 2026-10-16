# R274 — XAUUSD M5 impulse follow-through

**Verdict: GAGAL.** This locked setup tested decisive M5 candles after range expansion. It was profitable neither on discovery nor historical validation, including the quote-observed baseline with no incremental cost. The reserved 2026 segment remains unopened.

## Locked setup

Signal after a completed M5 candle with range >= 2A, body >= 0.8A, body/range >= 0.65, and close in the last 20% of the candle in the same direction as the body. A is median BID high-low range over the prior 144 completed M5 bars. Enter executable side at T+10m after signal bar open; stop at signal candle extreme; fixed target 1.5R; only one accepted trade per NY date; flat at 16:45 New York. No ER, breakout, trailing or news filters. Cost sensitivities +$0/$0.10/$0.30 primary/$0.50 per oz beyond observed BID/ASK. Specification committed before calculation: [pre-registration](R274_XAUUSD_M5_IMPULSE_FOLLOWTHROUGH_PREREGISTRATION.md).

## Data audit

- Source: raw-only Dukascopy XAUUSD M5 BID/ASK artifact [12031270051](https://github.com/christianomomongan82-lang/scanner/actions/runs/38859918137). 947,326 rows per side; exact paired timestamps; no negative spreads; synthetic flat bars disabled; 572 gaps >5m preserved.
- Historical rows calculated before 2026-01-01 UTC: 877,930. The feature/signal pipeline did not evaluate the 2026 holdout.

## Outcomes at +$0.30/oz extra cost

| Segment | Trades | Net R | PF | Mean R/trade | Win rate |
|---|---:|---:|---:|---:|---:|
| Discovery 2016–2020 | 974 | -655.94 | 0.324 | -0.673 | 27.72% |
| Validation 2021–2025 | 997 | -430.65 | 0.483 | -0.432 | 30.79% |

Even with zero extra cost, net R was -295.44 discovery and -228.98 validation. At +$0.50/oz it was -896.28 and -565.09. Four-week circular weekly-net-R bootstrap (10,000 reps, seed 2742026): discovery mean -2.513R/week, CI95 [-2.884, -2.136]; validation mean -1.650R/week, CI95 [-1.906, -1.389]. All five validation years were negative: 2021 -97.28R, 2022 -80.20R, 2023 -95.93R, 2024 -84.98R, 2025 -72.26R.

## Locked gates

| Gate | Result |
|---|---|
| Discovery >=100 trades and positive net R | **FAIL** — 974 trades, -655.94R |
| Discovery weekly bootstrap lower 95% bound >0 | **FAIL** — -2.136R/week |
| Validation >=200 trades and positive net R | **FAIL** — 997 trades, -430.65R |
| Validation positive at +$0.50/oz | **FAIL** — -565.09R |
| At least 3/5 validation years positive | **FAIL** — 0/5 |

## Decision

**R274 = GAGAL.** Do not open 2026 or change this locked hypothesis. This rejects the specific impulse-follow-through setup and shows that high trade frequency does not compensate for poor outcomes. It is not promoted to challenge simulation.

## Reproducibility

The local calculation used the optimized local mirror of the quote-side execution controls on the verified historical-only raw slice. The committed runner imports the stored R272 quote/execution engine to reproduce the locked R274 trigger. The row-level ledger was generated locally but is not uploaded in this commit.