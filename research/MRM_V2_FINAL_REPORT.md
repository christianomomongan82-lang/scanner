# Market Response Model v2 — Gross Alpha / Execution Cost Decomposition

**Verdict: GAGAL. No positive executable edge found. Not funded-ready.**  
Run date: 2026-10-23  
Branch: `local-backtest/market-response-model-v1-20261023`

## What changed from V1

V1's top four gain-importance features all measured spread. V2 therefore predicts gross midpoint TP/SL/time-stop outcome using price/context features only; all eight spread-derived features are removed. Spread is handled separately by a pre-locked execution gate. This was a new decomposition test, preregistered at [MRM_V2_COST_ALPHA_DECOMPOSITION_PREREGISTRATION.md](MRM_V2_COST_ALPHA_DECOMPOSITION_PREREGISTRATION.md), not a score-threshold retune of V1.

## Locked design

- Input: retained GitHub Actions artifact 11959096102, EURUSD Dukascopy BID/ASK M1 from 2016–2025; 4,415,493 matched timestamps.
- 140,188 valid decision timestamps; 74 price/context columns plus direction and 39 signed interactions.
- Decision every 30 minutes; wait 5 minutes after signal candle closes before entry. One position at a time.
- Model target: gross midpoint outcome with TP 15 pip, SL 10 pip, time stop 120 minutes; stop-first when both barrier prices touch in the same M1 candle.
- One fixed LightGBM regressor; train 2016–2019; no parameter search.
- Score cutoff is max(1 gross pip, 75th percentile of max directional score over 2020–2021): resulting cutoff 1.0 gross pip. Validation PnL was not used to select this cutoff.
- Spread gate is the 90th percentile of training-sample next-entry spread: 2.0003 pip. Spread gate and model stayed frozen for validation and forward diagnostics.
- Economic result uses executable bid/ask quote sides and +0.5 pip incremental round-turn friction; +1.0 pip incremental cost is a stress. These are fixed cost assumptions, not broker-verified live costs.
- Train 2016–2019; validation 2020–2021; forward diagnostic 2022–2025. **2020–2025 are not pristine program-level holdouts** because this wider project has already examined these years.

## Prediction diagnostics

| Cohort | Decision events | Spearman: score vs gross outcome | Spearman: score vs net executable outcome | Mean gross outcome, selected side | Mean executable outcome, selected side |
|---|---:|---:|---:|---:|---:|
| Train, in-sample | 56,145 | +0.24409 | +0.26194 | +1.9915 pip | +0.6846 pip |
| Validation 2020–2021 | 28,047 | -0.03739 | -0.01201 | +0.0760 pip | -1.2173 pip |
| Forward diagnostic 2022–2025 | 55,996 | -0.03842 | -0.00332 | +0.0571 pip | -1.5262 pip |

Validation top prediction quartile still produced a mean gross result of -0.0791 pip and net result of -0.9054 pip. Forward top quartile was slightly positive gross (+0.1361 pip), but negative net (-0.8398 pip). The model loses its ranking power out of sample.

## One-position-at-a-time replay

| Cohort / policy | Trades | Net pip | Mean pip/trade | PF | Max closed-trade DD |
|---|---:|---:|---:|---:|---:|
| Validation: selected, +0.5 pip incremental cost | 2,020 | -1,722.402 | -0.8527 | 0.8484 | 1,980.001 |
| Validation: selected, +1.0 pip incremental cost | 2,020 | -2,732.402 | -1.3527 | 0.7717 | 2,895.701 |
| Validation: model direction + spread gate, no score filter | 8,046 | -6,661.826 | -0.8280 | 0.8275 | 6,827.835 |
| Validation: 60-minute momentum + same spread gate | 8,033 | -6,678.118 | -0.8313 | 0.8272 | 6,867.914 |
| Forward 2022–2025: selected, +0.5 pip incremental cost | 4,415 | -4,039.285 | -0.9149 | 0.8410 | 4,123.780 |
| Forward 2022–2025: selected, +1.0 pip incremental cost | 4,415 | -6,246.785 | -1.4149 | 0.7663 | 6,299.985 |
| Forward: model direction + spread gate, no score filter | 16,553 | -15,413.206 | -0.9311 | 0.8162 | 15,532.405 |
| Forward: 60-minute momentum + same spread gate | 16,660 | -17,326.488 | -1.0400 | 0.7976 | 17,377.487 |

Every forward year was negative for the selected policy:

| Year | Trades | Net pip | PF |
|---|---:|---:|---:|
| 2022 | 1,744 | -1,739.398 | 0.8345 |
| 2023 | 959 | -722.004 | 0.8650 |
| 2024 | 575 | -554.693 | 0.8206 |
| 2025 | 1,137 | -1,023.190 | 0.8415 |

The four-week circular bootstrap 95% CI for mean weekly net PnL on the selected forward stream is [-26.0202, -12.8708] pip/week; none of 3,000 bootstrap means was positive. At +1.0 pip extra friction, the interval is [-37.1981, -22.8816].

## Interpretation

V2 answers the diagnostic question negatively: removing spread features did not uncover a useful directional relationship. Gross midpoint prediction ranking was slightly negative in validation and forward data; actual trade streams lost after executable spread and incremental cost. The model direction barely outperformed a simple momentum direction under a matched spread gate, and both streams were negative.

**Do not tune V2 using the same years, reverse its direction, or vary the score threshold against these results. Close this registered version as GAGAL.** The finding is narrow: this model, feature set, instrument, TP/SL/horizon, and 5-minute delayed-entry setup did not reveal a net positive EURUSD edge. It does not prove every possible trading edge is absent.

## Execution and inference limitations

- The PnL score assumes fills at nominal SL/TP barrier prices. Gap-through fills and slippage beyond stop levels are not modeled.
- M1 OHLC can't identify the true intrabar path; when both barriers touch, stop-first is assumed.
- Incremental cost is a stress assumption and not a verified FundedNext/broker spread, commission, swap, or slippage model.
- Overlapping event-level diagnostic labels are correlated and are not independent trades; the one-position-at-a-time stream is the more relevant but still approximate policy replay.
- Not a two-phase, equity-aware FundedNext challenge simulator. It does not calculate probability of completing a funded challenge.
- The protected XAUUSD 2026 window was not opened.
