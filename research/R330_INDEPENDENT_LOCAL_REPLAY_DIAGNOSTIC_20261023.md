# R330 — Independent local replay diagnostic (2026-10-23)

**Diagnostic verdict: GAGAL — ECONOMIC SCREEN. This file is not the official V2 closeout.** The registered calculation logic from `research/R330_PACKAGE/outcome_runner.py` was independently re-executed against the exact hash-verified data source. The local execution was not byte-for-byte invocation of the committed runner, so the results are not recorded as an official R330 closeout and must be reconciled against the pinned runner before program promotion.

## Source and pre-outcome checks

- Source: 7 paired Dukascopy H1 FX pairs, 14 native BID/ASK files, 2017-01-01 through 2025-12-31.
- Each of the 14 files matched the name, byte count, and SHA-256 in the archived raw manifest.
- Every stream had 78,361 rows; timestamps were unique, increasing, and aligned to H1. BID and ASK timestamps matched exactly within every pair. All seven pairs shared 78,361 timestamps.
- No invalid OHLC rows, negative opening/closing spreads, or duplicate timestamps were detected.
- Active common Tuesday 10:00 UTC snapshots: 468.
- Pre-outcome sample gate passed for every registered horizon: H13 had 768 discovery / 620 confirmation eligible legs; H26 had 716 / 620; H39 had 664 / 620. All had at least 100 discovery dates and 70 confirmation dates.

## Primary-cost economic screen

Costs: observed executable BID/ASK sides, assumed $10 round-trip standard-lot commission, +1 pip adverse slippage, and a deliberately adverse 2-pip-equivalent swap proxy per seven-day holding period. Swap is a proxy, not a verified FundedNext symbol-specific charge. Risk normalization follows the committed registered score formula.

| Horizon | Discovery net R / PF | Confirmation net R / PF | 2024–25 diagnostic net R / PF |
|---|---:|---:|---:|
| 13 weeks | -13.998 / 0.647 | -5.845 / 0.803 | -9.256 / 0.537 |
| 26 weeks | -13.025 / 0.641 | -6.286 / 0.790 | -7.746 / 0.618 |
| 39 weeks | -11.401 / 0.685 | -7.232 / 0.770 | -3.040 / 0.848 |

Discovery-only selection therefore chooses 39 weeks, the least bad discovery candidate. It still fails: net R and PF are negative/under 1 in discovery, confirmation, and diagnostic. With +2 pips slippage and 4-pip-equivalent swap per week, selected H39 falls to -16.768 R / PF 0.575 in discovery and -11.826 R / PF 0.652 in confirmation.

The 10,000-replicate four-week circular block bootstrap with seed 329 produced lower 95% bounds for mean weekly R of:
- H13: discovery -0.1154; confirmation -0.0974.
- H26: discovery -0.1044; confirmation -0.0978.
- H39: discovery -0.1048; confirmation -0.0986.

All Holm-adjusted discovery p-values were 1.000. The selected H39 registered stability gate also failed: among complete discovery years 2018–2020, only 2020 was positive; 2018 was -8.954 R and 2019 was -3.060 R.

## Interpretation

The tested cross-sectional multi-week currency-momentum rule does not show a tradable positive expectancy under the registered execution-cost model. Failure is not explained only by the extra slippage: with extra slippage set to zero but commission and swap proxy retained, every horizon remained negative in discovery and confirmation.

No challenge replay was run. H1 data cannot demonstrate exact five-minute fills, symbol-specific swaps are unverified, the historic periods are contaminated by earlier program research, and the exact committed-runner archive closeout is still outstanding. Do not retune the three registered horizons or call this candidate funded-ready.

## Audit boundary

The calculation logic was reconstructed from the committed runner specification and applied to the exact source files whose 14 checksums passed. Because the executed source file is not byte-identical to the GitHub-pinned runner, this is explicitly a transparent independent diagnostic rather than a formal V2-closed R330 result. It is nevertheless clear negative evidence for the registered economics hypothesis and a reason not to promote or further tune this exact rule.
