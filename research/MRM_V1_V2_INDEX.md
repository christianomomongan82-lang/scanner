# Market Response Model research index

Branch: `local-backtest/market-response-model-v1-20261023`  
Date: 2026-10-23

## Current authoritative result

- **Closure-clean MRM V1: GAGAL.** This is the current authority after finding and correcting a data-preparation defect.
- Raw EURUSD M1 contained 696,795 flat BID/ASK rows repeating previous quotes; the corrected filter excluded 22,793 decision points whose lookback or future trade path touched >=30-minute flat-candle runs.
- After correction, forward 2022–2025 selected policy = 1,751 trades, -1,795.690 pip with +0.5 pip incremental friction, PF 0.821. Removing that extra 0.5 pip still leaves -920.190 pip after observed BID/ASK friction, PF 0.903. All four forward years are negative.
- The original V1 result is superseded. V2 shares the closure-data defect and uses an approximated midpoint-barrier label; its gross-alpha diagnostics are not definitive.
- Neither model is funded-ready. The 2020–2025 dates are not pristine program-level holdouts. The protected XAUUSD 2026 window remains unopened.

## Files

- [Closure-clean corrected replay report](MRM_V1_CLOSED_MARKET_CLEAN_REPLAY.md)
- [Closure-clean machine summary](MRM_V1_CLOSED_MARKET_CLEAN_SUMMARY.json)
- [Closure-clean runner](market_response_v1_closed_market_clean.py)
- [Original V1 report — superseded](MRM_V1_FINAL_REPORT.md)
- [V2 report — contaminated input / midpoint-label caution](MRM_V2_FINAL_REPORT.md)
- [V2 preregistration](MRM_V2_COST_ALPHA_DECOMPOSITION_PREREGISTRATION.md)
- [V2 runner](market_response_v2.py)

## Root-cause conclusion

The recent experiment had a concrete engineering error: sequential timestamps were treated as sufficient evidence of active market data. The closure-clean rerun still failed, so that defect is not the complete explanation. After correction, the model's ranking ability remains positive in-sample but slightly negative out of sample, the score-selected policy loses money, and even removing the extra 0.5 pip cost assumption does not make it profitable.

The next project-wide audit should determine which earlier tests consumed the same static-placeholder archive without an equivalent activity filter. Do not assume all earlier failures had this cause; audit each family's actual source and preprocessing. Keep the corrected V1 locked as GAGAL and do not retune its threshold on these dates.
