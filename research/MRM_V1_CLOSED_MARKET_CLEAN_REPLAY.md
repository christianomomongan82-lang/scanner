# MRM V1 — Closure-Clean Corrected Replay

**Final verdict: GAGAL. The closure-data defect was real, but correcting it did not make the model profitable.**  
Run: 2026-10-23, local Python execution.  
This report supersedes the original MRM V1 aggregate results in `MRM_V1_FINAL_REPORT.md`, which included static market-closure rows in feature/label windows.

## Root-cause investigation

The raw EURUSD M1 BID/ASK archive contains candle rows with `open=high=low=close` on both sides during market closures, especially Sunday before the weekly market open. Timestamp continuity alone was an invalid test of market activity: those placeholder minutes are timestamped sequentially, so a test of adjacent timestamp deltas accepted them.

Independent audit of the retained input:
- Rows: 4,415,493, BID/ASK timestamps matched.
- 713,969 rows have flat OHLC on both BID and ASK.
- 696,795 rows have flat OHLC on both sides and repeat the previous minute's BID and ASK closes.
- A conservative run detector flags 682,472 rows as part of flat-BID/ASK runs lasting at least 30 minutes.
- The uncorrected candidate builder produced 140,188 decision points. 22,793 points were excluded by the closure-clean rule (16.25%).
- In the original event diagnostics, 17.66% of timestamps had >5% closure placeholders within the 4-hour feature lookback, and 27.22% had at least one closure placeholder in the subsequent 120-minute outcome path.

The original run was therefore not clean. This is an engineering/data-preparation error, and it should have been prevented by a common activity-aware preprocessing function rather than a timestamp-only continuity check.

## Corrected method

- The same fixed V1 LightGBM model and features; no hyperparameter search or post-result tuning.
- Train 2016–2019; validation 2020–2021; forward diagnostic 2022–2025.
- Each event is retained only if its complete lookback from row `i-240` through decision row `i` and its entire entry-to-time-stop path contain no row inside any BID/ASK flat-candle run of at least 30 minutes.
- The same entry delay (5 minutes after the completed signal candle), TP 15 pip, SL 10 pip, maximum holding 120 minutes, stop-first tie handling, observed BID/ASK executable sides, and +0.5 pip additional round-turn friction were retained.
- The 30-minute flat-run rule is a conservative activity heuristic. It removes obvious static closure artifacts but is not a substitute for a broker session calendar or tick data.
- The 2020–2025 periods are still not pristine program-level holdouts because this project has examined them in earlier research.

## Corrected results

### Prediction diagnostics

| Cohort | Events | Spearman: predicted score vs realized net PnL | Mean realized PnL of model-chosen side | Top prediction quartile mean PnL |
|---|---:|---:|---:|---:|
| Train, in-sample | 47,037 | +0.26224 | +1.619 pip | +5.535 pip |
| Validation 2020–2021 | 23,550 | -0.03842 | -0.829 pip | -0.955 pip |
| Forward diagnostic 2022–2025 | 46,808 | -0.01466 | -0.873 pip | -0.817 pip |

The in-sample relationship disappears out of sample and reverses slightly. Even the highest-scored quartile is negative on validation and forward data. That is direct evidence that this fitted model is not ranking actionable outcomes reliably.

### One-position-at-a-time policy

| Forward policy, 2022–2025 | Trades | Net pips | Mean pips/trade | PF |
|---|---:|---:|---:|---:|
| Model score-filtered, observed BID/ASK plus +0.5 pip incremental cost | 1,751 | -1,795.690 | -1.026 | 0.821 |
| Same selected trades, removing the extra +0.5 pip stress (observed BID/ASK remains) | 1,751 | -920.190 | -0.526 | 0.903 |
| Model direction, without its score filter, at +0.5 pip incremental cost | 16,011 | -12,418.654 | -0.776 | 0.846 |
| Simple trailing 60-minute momentum, +0.5 pip incremental cost | 16,143 | -17,159.098 | -1.063 | 0.795 |

Removing the arbitrary extra 0.5 pip cost does not turn the selected policy profitable: it still loses 920.2 pips with the observed BID/ASK costs retained. So the result is not explained by the extra-cost stress alone.

The score filter is also a bad selection rule in this test: selected trades lose more per trade than the unfiltered model-direction stream. That means the model's score threshold does not isolate a profitable subset, even though the model direction fares somewhat better than the simple momentum baseline.

Every forward year is negative for the selected policy:
- 2022: 566 trades, -418.596 pip, PF 0.877.
- 2023: 467 trades, -534.097 pip, PF 0.801.
- 2024: 380 trades, -427.897 pip, PF 0.784.
- 2025: 338 trades, -415.098 pip, PF 0.789.

The four-week circular weekly-net bootstrap 95% interval for mean weekly PnL is [-13.277, -4.140] pip/week; zero of 3,000 bootstrap means are positive.

## Why it failed after the correction

This isolates three different issues instead of conflating them:

1. **The original V1 run had a real data-preparation bug.** Static market-closure candles entered the lookback and some future trade labels. The old V1 aggregate figures should not be used as a clean estimate.
2. **The closure-clean model still does not generalize.** Train rank correlation is +0.262, but validation is -0.038 and forward is -0.015. The top score quartile remains negative. This is consistent with overfitting and/or non-stationarity, not a stable conditional edge.
3. **The selected trade stream has negative expectancy even without the extra 0.5 pip stress.** Observed BID/ASK costs still leave a negative result. Costs make the failure worse, but do not explain all of it.

The model does not qualify for funded use. Do not retune its score threshold on these periods.

## Additional caution about MRM V2

V2 also used the same raw archive before closure cleaning, so its training/evaluation sets share this contamination defect. In addition, it constructed a "midpoint" candle high/low by averaging separately observed BID and ASK highs/lows. Since those highs/lows may occur at different moments inside the minute, that is not an observed synchronized midpoint high/low. The V2 outcome remains evidence that its tested policy failed, but V2 should not be treated as an independent or definitive test of gross directional predictability.

## Evidence and code

- Corrected local runner: [`market_response_v1_closed_market_clean.py`](market_response_v1_closed_market_clean.py)
- Corrected machine-readable results: [`MRM_V1_CLOSED_MARKET_CLEAN_SUMMARY.json`](MRM_V1_CLOSED_MARKET_CLEAN_SUMMARY.json)
- Original initial report (superseded): [`MRM_V1_FINAL_REPORT.md`](MRM_V1_FINAL_REPORT.md)
- Input data artifact: [GitHub Actions artifact 11959096102](https://github.com/christianomomongan82-lang/scanner/actions/runs/38697080604)

## Bottom line

**MRM V1 failed for two distinct reasons: the original data pipeline admitted static market-closure rows, and after removing those rows the model still did not find an out-of-sample profitable condition.** The first is our engineering mistake. The second is the economic/modeling result for this specific feature set, target/stop/horizon, execution delay, and EURUSD dataset. Neither implies that all possible trading edges are impossible.
