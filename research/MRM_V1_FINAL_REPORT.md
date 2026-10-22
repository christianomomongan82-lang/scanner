> **SUPERSEDED:** This first-pass result included static market-closure placeholder rows in some feature and outcome windows. Use [the closure-clean corrected replay](MRM_V1_CLOSED_MARKET_CLEAN_REPLAY.md) and its machine-readable summary as the current V1 result. The initial metrics below are retained for audit history only.

# Market Response Model v1 — Final Report

**Verdict: GAGAL — no cost-surviving positive edge found. Do not promote to funded challenge.**  
Run date: 2026-10-23  
Repository branch: `local-backtest/market-response-model-v1-20261023`

## Hypothesis

Replace manually nominated chart patterns with one nonlinear model that directly estimates net executable trade outcome (pips) for both LONG and SHORT at each 30-minute decision point, using only information available at the signal time. A single fixed LightGBM regressor was fitted once; no hyperparameter search was performed.

## Data and execution contract

- Input: retained GitHub Actions artifact [11959096102](https://github.com/christianomomongan82-lang/scanner/actions/runs/38697080604), `EURUSD-M1-Dukascopy-BID-ASK-2016-2025`.
- 4,415,493 timestamp-matched BID/ASK M1 rows; range 2016-01-03 00:00 UTC through 2025-12-31 21:58 UTC.
- Compressed BID SHA-256: `b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc`.
- Compressed ASK SHA-256: `52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b`.
- 140,188 valid decision points after requiring 240 exact contiguous historical minutes, a five-minute delay after the completed signal bar, and a complete 120-minute forward path. 82 raw/context features; 92 model columns after side and signed-direction interactions.
- Decision cadence: every 30 minutes. Entry is five minutes after the signal bar closes. TP 15 pips, SL 10 pips, maximum holding 120 minutes.
- Long fills: entry Ask, exit Bid. Short fills: entry Bid, exit Ask. A candle touching both stop and target is resolved against the strategy (stop first). PnL includes observed BID/ASK spread and +0.5 pip extra round-turn friction; +1.0 pip total incremental friction is also reported.
- The extra friction is a stress assumption, not a verified live broker commission/slippage schedule. Barrier exits are booked at their nominal SL/TP level; gap-through fills and stop slippage beyond that level are not separately modeled.

## Frozen modeling protocol

- Train: 2016–2019 only.
- Validation / threshold lock: 2020–2021. Threshold used only model-score distribution, not PnL optimization: `max(0.5 pip, 75th percentile of max(LONG score, SHORT score))`. Resulting threshold = 0.5 pip.
- Forward diagnostic: 2022–2025, with model and threshold frozen.
- Important: 2020–2025 are **not pristine program-level holdouts** because those years were previously examined in this broader project. These are useful diagnostics, not independent final proof.
- LightGBM fixed settings: 350 trees, learning rate 0.035, 23 leaves, min child samples 800, L1 0.2, L2 8, row/column sampling 0.85, random seed 20261023.

## Results

### Prediction diagnostics (all decision-event labels overlap and are not independent trades)

| Cohort | Events | Spearman(score, realized net PnL) | Mean PnL of model-chosen side | Top prediction quartile mean PnL | Bottom quartile mean PnL |
|---|---:|---:|---:|---:|---:|
| Train, in-sample | 56,145 | 0.30123 | +0.763 pips | +5.067 pips | -2.907 pips |
| Validation 2020–2021 | 28,047 | 0.01991 | -1.204 pips | -0.707 pips | -2.553 pips |
| Forward diagnostic 2022–2025 | 55,996 | 0.05591 | -1.530 pips | -0.731 pips | -3.602 pips |

The in-sample ranking collapses out of sample. The highest-scored decile still loses on average: -0.681 pips in validation and -0.702 pips in the 2022–2025 diagnostic. The model does rank very poor predictions below less-poor predictions, but that is not the same as finding a profitable condition.

### One-position-at-a-time policy replay

| Period / policy | Trades | Net pips | Mean pips/trade | PF | Max closed-trade drawdown |
|---|---:|---:|---:|---:|---:|
| Validation: selective model, +0.5 pip extra friction | 964 | -399.810 | -0.415 | 0.923 | 691.607 pips |
| Validation: same score, +1.0 pip extra friction | 964 | -881.810 | -0.915 | 0.839 | 1,040.107 pips |
| Forward 2022–2025: selective model, +0.5 pip extra friction | 1,907 | -2,065.888 | -1.083 | 0.814 | 2,138.494 pips |
| Forward 2022–2025: same score, +1.0 pip extra friction | 1,907 | -3,019.388 | -1.583 | 0.741 | 3,042.994 pips |
| Forward 2022–2025: model direction with no filter | 18,483 | -28,125.059 | -1.522 | 0.712 | 28,128.548 pips |
| Forward 2022–2025: simple 60-minute momentum direction | 18,592 | -30,874.450 | -1.661 | 0.689 | 30,881.550 pips |

The selective model greatly reduces trade count and losses versus the unfiltered controls, but its selected trades remain negative after costs. Its four forward years all lose:

| Year | Trades | Net pips | PF |
|---|---:|---:|---:|
| 2022 | 682 | -890.599 | 0.792 |
| 2023 | 472 | -301.997 | 0.885 |
| 2024 | 406 | -540.899 | 0.748 |
| 2025 | 347 | -332.393 | 0.838 |

For the selective policy's 2022–2025 weekly net PnL, the four-week circular block-bootstrap 95% CI for mean weekly PnL is [-14.337, -5.575] pips/week; 0/3,000 resamples have a positive mean. At +1.0 pip incremental friction the CI is [-19.149, -9.956] pips/week.

## What we learned

1. This first model does not find a condition with positive net expectancy in the tested EURUSD space under the stated target, stop, 5-minute delay, and cost contract.
2. The first four gain-importance features are all spread-related (`spread_mean_15m`, `spread_mean_60m`, `spread_over_vol15`, `spread_now_pips`). The model's strongest repeatable behavior is partly avoiding costly spread states, not identifying a profitable directional response.
3. In-sample fit was much stronger than validation fit: classic overfitting / non-stationarity signature.
4. Do not tune this model against 2020–2025 or rescue it by changing its score threshold on the same years. Close this registered v1 run as **GAGAL**.

## Limits and final decision

- This is not a FundedNext two-phase equity-aware replay and does not estimate the probability of passing a challenge.
- Intrabar ordering is unknowable from M1 OHLC; stop-first is conservative but still approximate.
- Barrier fills are assumed to occur at the nominal TP/SL price; gap-through losses and live slippage beyond that price are not modeled and can make actual results worse.
- The cost stress does not claim to reproduce a particular broker's actual commissions, swaps, or live slippage.
- The retained EURUSD artifact ends in 2025. The protected XAUUSD 2026 outcome window was not opened.
- No candidate is promoted. The correct conclusion is narrow: **this Market Response Model v1 did not discover a funded-usable EURUSD edge**. That does not prove every possible trading edge is absent.
