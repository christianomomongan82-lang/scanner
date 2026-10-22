# Market Response Model research index

Branch: `local-backtest/market-response-model-v1-20261023`  
Date: 2026-10-23

## Final decisions

- **MRM V1: GAGAL.** A net-PnL model learned in-sample but its score ranking collapsed out of sample; 1,907 forward-diagnostic selected trades lost 2,065.888 pips at +0.5 pip incremental friction, PF 0.8138.
- **MRM V2: GAGAL.** Separating gross midpoint response from spread cost did not uncover direction alpha; 4,415 forward-diagnostic selected trades lost 4,039.285 pips at +0.5 pip incremental friction, PF 0.8410.
- Neither candidate is funded-ready. 2020–2025 results are not pristine program-level OOS. The protected XAUUSD 2026 window remains unscored.

## Files

- [V1 final report](MRM_V1_FINAL_REPORT.md)
- [V1 machine-readable summary](MRM_V1_summary.json)
- [V1 local runner](market_response_v1.py)
- [V1 top feature importance](MRM_V1_feature_importance_top20.csv)
- [V2 preregistration](MRM_V2_COST_ALPHA_DECOMPOSITION_PREREGISTRATION.md)
- [V2 final report](MRM_V2_FINAL_REPORT.md)
- [V2 machine-readable summary](MRM_V2_summary.json)
- [V2 local runner](market_response_v2.py)
- [V2 top feature importance](MRM_V2_feature_importance_top20.csv)

## Interpretation

V1's feature importance indicated spread states dominated the model, so V2 removed spread from the predictor and applied a spread gate based on training data only. V2 still had slightly negative out-of-sample gross-response rank correlation and negative executable expectancy. This is direct evidence that this model class, feature representation and tested EURUSD setup did not find a usable edge. It is not evidence that all trading edges are impossible. Do not tune the two registered candidates on the same windows. A next step should change the information source or conditional mechanism, rather than repeatedly altering these models.
