# R317–R318 EURUSD M5 Clean-Quote Search — 2026-10-21

**Final decision: GAGAL. No strategy from this batch is approved for a funded challenge.**

This report supersedes the preliminary R317 table that was shown before the repeated-flat placeholder audit. Those preliminary numbers were generated before the data-cleaning defect was caught and must not be used.

## Source-data audit

Source archive: existing GitHub artifact `11959096102`, collected by run `38697080604`. ZIP SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.

The BID/ASK inputs each contained 4,415,493 timestamp rows. A strict row-level filter removed 696,795 synthetic repeated-flat placeholders (both sides' complete current OHLC equals their own previous close on a consecutive minute). Remaining M1 rows: 3,718,698. The paired feed was aggregated to 736,076 exact complete M5 bars; 7,882 gaps over five minutes were preserved as gaps, not filled. Signals requiring a contiguous lookback were rejected across gaps.

Execution model used actual BID/ASK sides, an entry at signal timestamp +10 minutes, an entry-spread ceiling of 0.8 pip, conservative stop-first same-bar handling, gap-aware exits, one accepted position at a time, and additional per-trade cost stress. This remains historical screening, not a verified broker emulator.

## R317 — momentum / London range families

A discovery-selected configuration was chosen using 2016–2020, including a 960-way exit-geometry sweep. Frozen specification: follow a six-M5-bar move when its magnitude is at least 5 times the trailing median M5 true range; New York 08:00–12:00; stop 1.5 times that prior median range; target 4R; maximum hold 36 M5 bars; one trade per New York date; spread cap 0.8 pip; entry delayed 10 minutes.

| Segment | Cost beyond observed BID/ASK | Trades | Net R | PF |
|---|---:|---:|---:|---:|
| Discovery 2016–2020 | 0.5 pip | 374 | +39.40R | 1.138 |
| Validation 2021–2025 | 0.0 pip | 397 | −3.862R | 0.987 |
| Validation 2021–2025 | 0.5 pip | 397 | −37.264R | 0.888 |
| Validation 2021–2025 | 1.0 pip | 397 | −70.666R | 0.803 |

*The 0.0-pip discovery figure was not retained as the primary discovery headline in the compact run output; treat it as unverified and do not rely on it. The primary discovery comparison is +39.40R at +0.5 pip.

At the primary +0.5-pip cost, only one of five validation years was positive. The four-week weekly block-bootstrap at this cost had mean −0.143R/week and 95% interval [−0.433R, +0.152R]. **R317 = GAGAL; the family is closed, with no tuning against validation.**

## R318 — additional raw-price auction / candle-shape search

The clean data were used to screen 972 configurations across four different rule families: wick-confirmed sweep/reclaim fades, close-confirmed range breakouts, large-range candles conditioned on close location, and prior displacement plus candle-close confirmation. The common first-pass exit was a stop 1.5 times the trailing median M5 true range, target 2R, 12-bar maximum hold, and +0.5 pip extra cost. Only 5 of 959 configurations with at least 100 completed discovery trades were net positive in 2016–2020; only 3 met PF ≥1.05. These are discovery results after a broad search and are subject to selection bias.

The five strongest discovery configurations were frozen and tested once against 2021–2025. Every one failed at +0.5 pip extra cost:

| Frozen rule ranked from discovery | Discovery trades | Discovery net R | Discovery PF | Validation trades | Validation net R | Validation PF |
|---|---:|---:|---:|---:|---:|---:|
| Large-range candle, 2× prior median TR, body ≥80%, close in top 10%; fade short, London–NY overlap | 262 | +15.93R | 1.106 | 265 | −24.05R | 0.855 |
| Prior 12-bar down-displacement ≥4× prior median TR, bullish signal candle closing in top 10%; long, London–NY overlap | 132 | +10.66R | 1.166 | 128 | −16.48R | 0.787 |
| Large-range candle, 2× prior median TR, body ≥60%, close in top 10%; fade short, London–NY overlap | 332 | +8.33R | 1.042 | 337 | −29.90R | 0.860 |
| Prior 6-bar down-displacement ≥4× prior median TR, bearish close in bottom 10%; short, New York session | 200 | +6.38R | 1.051 | 237 | −27.69R | 0.828 |
| Large-range candle, 2× prior median TR, body ≥40%, close in top 10%; fade short, London–NY overlap | 361 | +3.74R | 1.017 | 357 | −30.23R | 0.867 |

For the second-ranked rule, validation at zero additional cost was already −6.24R, PF 0.912. At +0.5 pip it was −16.48R, PF 0.787, max drawdown 24.85R, and only two of five years were positive (2022 and 2025). Weekly four-week bootstrap at +0.5 pip: mean −0.063R/week, 95% interval [−0.160R, +0.034R], and only 10.0% of bootstrap replicates had positive mean weekly R.

All five discovery-selected configurations therefore failed the frozen forward comparison. The period 2021–2025 has also been reused in earlier project research, so it is not a pristine, untouched OOS dataset; a future positive result would still need fresh forward evidence.

## Decision and next filter

- R317 = **GAGAL**.
- R318 = **GAGAL**.
- No risk increase or challenge-account simulation can turn negative expectancy into a reliable edge. These candidates must not be promoted or sized for a funded challenge.
- Keep the protected 2026 segment unopened for this search.
- The first-pass discovery grid and local row-level ledgers were generated in the working container. This report records the key results, but the full 972-row grid and every row-level ledger have not yet been committed and read-back-verified in GitHub; do not claim repository-complete reproducibility.

Input lineage and hashes above identify the exact source archive. The cleaned M5 snapshot was generated locally from that archive using the strict placeholder and contiguous-bar rules described above.
