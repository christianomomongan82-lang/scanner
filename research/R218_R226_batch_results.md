# Batch R218–R226: nine raw-price H1 strategy hypotheses

**Decision: no strategy passed the forward acceptance gate.** These nine hypotheses were evaluated together. Instrument selection for each family was locked on discovery data only; forward and OOS data were not used to choose candidates.

## Results

| Hypothesis | Locked instrument | Discovery n | Discovery PF @2 bps | Forward n | Forward PF @1 bp | Forward PF @2 bps | OOS n | OOS PF @1 bp | OOS PF @2 bps | Decision |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| R218 | US30 | 2,543 | 0.942 | 2,165 | 0.872 | 0.826 | 443 | 0.959 | 0.900 | REJECT |
| R219 | US Tech 100 | 2,703 | 0.931 | 2,442 | 1.048 | 0.986 | 501 | 0.677 | 0.636 | REJECT |
| R220 | US Small Cap 2000 | 125 | 1.535 | 146 | 0.802 | 0.774 | 31 | 1.149 | 1.113 | REJECT |
| R221 | None | 26 max | 0.503 max PF | — | — | — | — | — | — | Discovery sample failure |
| R222 | US30 | 2,627 | 1.014 | 2,943 | 0.901 | 0.848 | 568 | 1.086 | 1.011 | REJECT |
| R223 | US Tech 100 | 452 | 0.856 | 355 | 0.938 | 0.907 | 78 | 1.052 | 1.008 | REJECT |
| R224 | US Small Cap 2000 | 492 | 1.181 | 567 | 0.988 | 0.954 | 101 | 1.327 | 1.272 | REJECT |
| R225 | US30 | 375 | 0.973 | 284 | 0.913 | 0.879 | 52 | 0.785 | 0.736 | REJECT |
| R226 | Japan 225 | 632 | 0.966 | 642 | 1.069 | 1.004 | 197 | 0.973 | 0.928 | REJECT |

## Registered hypotheses

- **R218:** Three-hour return momentum continuation, current candle agrees with direction; hold 4 hours.
- **R219:** H1 long-wick rejection; wick occupies at least 60% of range and close confirms rejection; hold 3 hours.
- **R220:** Established 8-hour trend, two-bar pullback, then reversal candle closes through prior H1 extreme; hold 4 hours.
- **R221:** Fade a >=0.35% displacement from the prior 24-hour range midpoint when the current candle turns toward the midpoint; hold 6 hours.
- **R222:** Cross-market breadth: at least 7 of 10 indices have valid 4-hour returns exceeding +/-0.10% in the same direction; trade aligned assets; hold 4 hours.
- **R223:** Engulfing reversal conditioned on a >=0.40% prior 4-hour move; hold 4 hours.
- **R224:** Fade a >=0.40% 4-hour return outlier relative to the synchronized cross-index median when the current H1 candle turns against the shock; hold 4 hours.
- **R225:** Fade a >=0.60% 4-hour move when the current H1 candle turns against it; hold 4 hours.
- **R226:** Reverse after three consecutive H1 candle bodies in one direction when the 3-hour move is >=0.30% and the current candle reverses; hold 3 hours.

## Selection and pass rules

For each hypothesis, the instrument with the highest discovery PF at modeled 2 bps was selected among those with at least 100 discovery closes; trade count breaks ties. This selection rule is discovery-only. R221 did not reach 100 trades on any instrument and was not advanced to forward/OOS.

Forward acceptance requires >=30 closed trades, PF >=1.15 at both modeled 1 and 2 bps, and PF >=1.00 at 1 bp for every qualifying annual cohort with >=5 trades. **None passed.**

## Audit

- Ten H1 input files passed timestamp, hourly-grid, OHLC relationship, and finiteness checks.
- 90/90 strategy-instrument causal-prefix comparisons passed.
- Independent audit verified 106 ledger CSVs with zero failures and inspected 102,860 trade rows. This includes all per-symbol discovery ledgers and the selected forward/OOS ledgers.
- Actual entry and exit opens were checked against raw source files; costs, time order, position overlap, and period boundaries were independently checked.
- Cost stress surface: 0, 1, 2, 3 and 5 bps per trade.
- Weekly-block bootstrap: 2,000 circular resamples per selected strategy-period-cost cell, using 4-week blocks. Confidence intervals are diagnostic, not a guarantee of future performance.
- Test register: 100/100 checks passed.

Data are BID-only. Costs are modeled, not verified broker/funded spread, commission, financing or slippage. No contract multipliers or funded drawdown rules are simulated. A discovery-winning instrument still has multiple-testing bias; independent forward results remain decisive. No strategy is live/funded-ready.

## Common-history discovery-selection sensitivity — exploratory

The US Small Cap 2000 source begins 2018-08-08, while other instruments have earlier history. To control for unequal discovery periods, a sensitivity pass repeated the asset selection over the common 2018-08-08 to 2022-01-01 window using the same minimum sample and PF@2 bps ranking. This sensitivity was run after the primary forward/OOS results had been inspected; its alternate forward/OOS statistics are diagnostics only, not a fresh validation.

| Strategy | Original asset | Common-window choice | Changed? | Common discovery trades | PF @2 bps | Alt forward PF @1/@2 | Alt OOS PF @1/@2 |
|---|---|---|---|---:|---:|---|---|
| R218 | US30 | US30 | No | 2075 | 0.948 | 0.872 / 0.826 | 0.959 / 0.900 |
| R219 | US Tech 100 | France 40 | Yes | 1218 | 0.956 | 0.952 / 0.894 | 0.842 / 0.787 |
| R220 | US Small Cap | US Small Cap | No | 125 | 1.535 | 0.802 / 0.774 | 1.149 / 1.113 |
| R221 | None | None | — | 26 max | 0.503 max | — | — |
| R222 | US30 | US30 | No | 2627 | 1.014 | 0.901 / 0.848 | 1.086 / 1.011 |
| R223 | US Tech 100 | Japan 225 | Yes | 282 | 0.854 | 1.019 / 0.969 | 1.481 / 1.426 |
| R224 | US Small Cap | US Small Cap | No | 492 | 1.181 | 0.988 / 0.954 | 1.327 / 1.272 |
| R225 | US30 | US Tech 100 | Yes | 517 | 0.971 | 0.928 / 0.899 | 0.985 / 0.943 |
| R226 | Japan 225 | FTSE 100 | Yes | 427 | 0.940 | 1.139 / 1.065 | 1.249 / 1.167 |

Four of eight locked asset choices changed. Even among these post-hoc choices none meets the forward PF>=1.15 gate at both 1 and 2 bps. High OOS PF for R223/R226 cannot override the failed primary forward protocol; all primary decisions remain REJECT.
