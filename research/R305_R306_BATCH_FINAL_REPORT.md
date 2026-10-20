# R305/R306 — Cross-Asset USD-Factor Batch: Final Report

**Batch verdict: both candidates GAGAL.** Both hypotheses were preregistered before PnL calculation and tested locally on paired Dukascopy quotes. The XAUUSD 2026 outcome window was not opened. No FundedNext challenge replay was run because both candidates failed the strategy-level gates.

## What was tested

- **R305 — USD-factor impulse transmission:** an unusually large 30-minute EURUSD midpoint move predicts same-direction XAUUSD movement after a phone-compatible delay; positive EURUSD return triggers a gold long, negative return a gold short.
- **R306 — USD-factor shock with gold underreaction:** the same registered EURUSD shock, but only when XAUUSD's own preceding 30-minute move is at or below its causal rolling median; trade the expected same-direction catch-up.
- Both use exact EURUSD/XAU timestamp alignment, executable BID/ASK fills, entry five minutes after signal close, one position at a time, prior-only 1.5× median true-range stop distance, 1R stop, 1.5R target, 60-minute maximum hold, stop-first barrier collision, and added friction stresses of $0/$0.30/$0.50 per ounce.
- Discovery: 2017–2020. Validation/diagnostic: 2021–2025, which is not pristine program-level OOS. No outcomes at or after 2026-01-01 UTC were calculated.

## Data integrity

EURUSD had 4,415,493 rows per side before cutoff, exact BID/ASK pairing, no invalid OHLC, and no negative open/close spreads. The registered repeated-flat filter removed 696,795 minutes, leaving 3,718,698 active M1 rows and 736,076 complete contiguous M5 bars.

XAUUSD had 877,930 paired M5 rows per side before cutoff; no duplicate/nonincreasing timestamps, invalid OHLC, or negative open/close spreads. Exactly 732,199 EURUSD/XAUUSD M5 timestamps were shared. Missing rows were left missing and no bars were synthesized. The protected 2026 cutoff was applied before feature and outcome construction.

## Primary execution (T+10 entry; +$0.30/oz added friction)

| Candidate | Period | Trades | Net R | PF_R | Win rate | Max closed-R drawdown |
|---|---|---:|---:|---:|---:|---:|
| R305 | Discovery 2017–2020 | 12,338 | -6,974.05 | 0.340 | 28.65% | 6,977.66R |
| R305 | Validation 2021–2025 | 14,201 | -4,486.27 | 0.536 | 34.42% | 4,495.62R |
| R306 | Discovery 2017–2020 | 3,322 | -2,058.60 | 0.304 | 27.97% | 2,061.20R |
| R306 | Validation 2021–2025 | 4,004 | -1,398.50 | 0.497 | 33.57% | 1,402.31R |

These are accumulated risk units (R), not account dollars. The large negative totals reflect thousands of trades with negative expectancy; they are not a funded-account replay.

## Cost and annual stress

Both candidates were negative in both periods even at $0 additional friction after observed BID/ASK fills. At +$0.50/oz, losses worsened:

| Candidate | Period | Net R at $0 added cost | PF_R | Net R at +$0.50/oz | PF_R |
|---|---|---:|---:|---:|---:|
| R305 | Discovery | -3,466.78 | 0.568 | -9,312.24 | 0.244 |
| R305 | Validation | -2,493.51 | 0.701 | -5,814.77 | 0.450 |
| R306 | Discovery | -1,027.46 | 0.532 | -2,746.03 | 0.212 |
| R306 | Validation | -801.65 | 0.662 | -1,796.41 | 0.412 |

At the fixed +$0.30/oz cost, zero of four discovery years were positive for either candidate and all five validation years were negative for both. T+15-minute entry delay did not repair the results: R305 validation -4,393.50R / PF_R 0.540; R306 validation -1,322.39R / PF_R 0.522.

## Validation uncertainty

A circular four-calendar-week block bootstrap was run over all 261 Monday-start validation weeks, including weeks with no trades; 10,000 resamples per candidate.

- **R305:** mean -17.1888R/week; 95% CI [-18.7661, -15.5937]R; bootstrap share of positive mean = 0%.
- **R306:** mean -5.3583R/week; 95% CI [-5.9689, -4.7170]R; bootstrap share of positive mean = 0%.

The confidence intervals are wholly negative. This is not merely a marginal PF or cost-sensitivity issue: the registered directional relationships failed even before extra costs were added.

## Verdict and next move

Each candidate passed only its two minimum-sample gates. Both failed primary expectancy/PF, +$0.50/oz stress, annual stability, the positive-bootstrap-bound gate, T+15 delay stress, and repository-only reproducibility. Each is **GAGAL (2/8 gates)**. No alpha block is retained; neither candidate proceeds to challenge replay. We make no claim that either could pass both phases in under 180 days.

Do not tune the return threshold, session, stop/target, direction, or holding period on these same years. The common-USD transmission and underreaction-catch-up ideas both failed strongly. The next search must change the underlying mechanism, not merely flip direction or alter a threshold.

## Reproducibility limitation

The locked preregistrations and pre-outcome audit summary are committed to the repository. The exact local batch runner and detailed CSV ledgers are identified by hashes in `R305_R306_DATA_MANIFEST.md`, but are not yet committed as row-level files in the active branch. Therefore repository-only reproducibility is explicitly **failed**; this report does not claim full independent reproduction from GitHub alone.
