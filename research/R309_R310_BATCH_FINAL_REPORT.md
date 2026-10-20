# R309/R310 — EURUSD–XAUUSD Relative-Value Batch Final Report

**Binary verdict: R309 = GAGAL; R310 = GAGAL.** Neither strategy qualifies for a FundedNext challenge replay. This batch does not meet the user's objective of completing both phases in fewer than 180 calendar days; no pass probability is claimed.

## What was tested

- **R309:** Fade an extreme one-hour residual return between XAUUSD and EURUSD, with a rolling beta fitted only from prior paired returns. The exit used a rolling residual-return z-score.
- **R310:** Evolutionary child of R309. It retains the same signal, beta, data, entry, costs, and delays but corrects the exit geometry: take-profit/stop are triggered by the *actual post-entry residual price change*, not by the one-hour rolling z-score reverting as the original shock ages out of the window.
- Exact BID/ASK sides are used for both instruments. The beta is frozen at signal time. A primary entry is at the exact paired M5 open ten minutes after the signal bar's start timestamp (five minutes to the signal close plus five minutes for manual reaction). The stress entry is at +15 minutes. No overlap and no synthetic bars.
- Discovery: 2017–2020. Validation/diagnostic: 2021–2025; this period is already contaminated by prior project research, so it is not pristine OOS. The XAUUSD 2026 outcome window was not opened.

## Source-data audit

The final runner matches the registered EURUSD repeated-flat-placeholder filter and source manifest:
- EURUSD paired raw rows per side: 4,415,493.
- Repeated flat placeholders removed: **696,795**; active paired minute timestamps: **3,718,698**.
- Complete active EURUSD M5 bars: **736,076**.
- Paired XAUUSD M5 rows through the cutoff: **877,930**.
- Exact common EURUSD/XAUUSD M5 timestamps: **732,199**.
- Duplicate timestamps, invalid OHLC checks and negative opening/closing spreads: **zero** on both feeds.
- All data timestamped at or after 2026-01-01 UTC was excluded from feature construction and scoring.

The first R309 runner version removed every flat candle rather than only repeated flat placeholders. Its metrics were voided and not used. The corrected run above reproduces the source-manifest counts. The feature coverage amendment and pipeline correction are recorded separately in the repository.

## Primary result

Baseline costs are observed BID/ASK fills plus incremental round-trip cost of $0.30/oz for XAUUSD and 1 pip for EURUSD. “Zero extra” still includes the observed BID/ASK spread. Stress adds $0.50/oz for XAUUSD and 2 pips for EURUSD.

| Candidate | Period | Trades | Zero-extra net R / PF | Baseline net R / PF | Stress net R / PF | T+15 baseline net R / PF |
|---|---|---:|---:|---:|---:|---:|
| R309 | Discovery 2017–2020 | 3,576 | -453.35 / 0.612 | -991.56 / 0.338 | -1,388.72 / 0.220 | -945.78 / 0.311 |
| R309 | Diagnostic 2021–2025 | 3,665 | -327.01 / 0.715 | -644.44 / 0.512 | -890.87 / 0.395 | -594.18 / 0.497 |
| R310 | Discovery 2017–2020 | 3,003 | -351.75 / 0.773 | -804.58 / 0.553 | -1,138.77 / 0.431 | -754.70 / 0.559 |
| R310 | Diagnostic 2021–2025 | 3,125 | -274.27 / 0.825 | -544.15 / 0.681 | -753.64 / 0.586 | -538.87 / 0.672 |

Every annual baseline-cost result was negative for both candidates: R309 was negative in all nine scored years (2017–2025), and R310 was also negative in all nine. R310 reduced the loss relative to R309, but it did not uncover positive expectancy—even at zero *additional* costs.

## Validation uncertainty

Four-calendar-week circular block bootstrap over 261 Monday-start weeks, retaining zero-trade weeks; 10,000 resamples, seed 309.

- **R309:** mean -2.469 R/week; 95% CI **[-2.939, -2.005]**; 0% of bootstrap means positive.
- **R310:** mean -2.085 R/week; 95% CI **[-2.578, -1.604]**; 0% of bootstrap means positive.

The confidence intervals are wholly negative. This is not a marginal cost-sensitivity miss.

## Frozen gate score

| Gate | R309 | R310 |
|---|---|---|
| Data integrity / timestamp alignment | PASS | PASS |
| Minimum trade counts | PASS | PASS |
| Positive net R and PF floor in both periods at baseline costs | FAIL | FAIL |
| Positive net R in both periods at stronger cost stress | FAIL | FAIL |
| Annual stability (3/4 discovery and 4/5 validation years positive) | FAIL | FAIL |
| Validation weekly bootstrap lower bound above zero | FAIL | FAIL |
| Positive result after delayed entry | FAIL | FAIL |
| Complete repository-only reproduction | FAIL — row-level ledgers and exact runner are not yet ordinary files in the branch | FAIL — same |

**Each: 2/8 gates passed → GAGAL.** No challenge-path simulation was run, correctly, because both candidates failed their strategy-level expectancy gates. A challenge simulator cannot turn a negative edge into a credible pass plan.

## Evolutionary lesson and next action

R310 is the useful evolutionary result: replacing the rolling-z exit with a real post-entry price-move exit improved the statistics, but both discovery and validation stayed strongly negative even before incremental costs. Therefore close this exact relative-value snapback family; do not flip the direction or tune the z threshold, beta lookback, target, stop, or hold period on these already inspected years.

The remaining actual blocker is **not** “find a more attractive PF.” There is still no cost-surviving edge candidate to pass into the common account-level simulator, and the branch lacks complete row-level reproduction artifacts. Next search must start from a distinct economic mechanism and must commit its runner/row-level outputs before it can be treated as a fully auditable experiment. No candidate is funded-ready.
