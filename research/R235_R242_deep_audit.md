# R235–R242 deep audit

## Statistical decision

The acceptance rule for this deeper batch requires at least 30 forward closes, PF >=1.15 at both modeled 1 and 2 bps, PF >=1 at 1 bp in every annual cohort with >=5 trades, and Holm-adjusted one-sided bootstrap p <0.05 for positive expectancy across the eight registered hypotheses.

- **R236 / Japan 225** passes the numeric forward PF and annual-cohort sub-gates, but fails the inferential bar. Bootstrap mean net at 2 bps is +5.05 bps/trade, 95% interval [-4.90, +15.62], raw p=0.158, Holm-adjusted p=1.000. OOS is only 18 trades and PF@2 bps=0.154.
- **R238 / US Tech 100** forward PF@1/@2 bps=1.244/1.197, but 2023 annual PF@1 bps=0.958 and OOS PF@2 bps=0.418. Its bootstrap interval crosses zero.
- **R241 / France 40** forward PF@1/@2 bps=1.001/0.961; the expectancy turns negative at 2 bps and the annual gate fails.
- **R242 / US Small Cap 2000** has 2,449 forward trades, but PF@1/@2=1.074/1.034 and 2022 PF@1=0.892.
- R235, R237, R239 and R240 did not have any instrument meeting the discovery gate of >=100 closes and PF@2 bps >=1.00.

## Data and execution verification

- 10 H1 source files checked for duplicates, hourly grid, finite OHLC and valid candle relationships.
- 190/190 full-versus-truncated feature and signal comparisons passed.
- 88/88 unique ledger files passed; 75,308 trade rows were checked against raw source timestamps and opens. No assertion failed.
- Independent checks included signal-to-next-hour entry, source-price matches, active/non-flat signal/entry/exit bars, exact active-bar holding horizon, PnL arithmetic, 1/2/3/5 bps cost deductions, no duplicate symbol/signal trades, no same-symbol overlap and period boundaries.
- Cost PF surfaces, annual cohorts, directional split and 2022–2023 vs 2024–2025 stability tables are in separate CSVs.

## Unequal history

The common-history discovery window starts 2018-08-08 13:00 UTC, when the US Small Cap dataset becomes available. Re-ranking on that common window left R238, R241 and R242 unchanged, produced no eligible common-window asset for R236, and produced Australia 200 as a common-window eligible choice for R239 (which had no eligible primary-window choice). No forward/OOS reruns were performed; those alternate selections are not validated.

## Conclusion

No strategy passes the full statistical acceptance standard. Better-looking forward PF is not enough when annual stability, OOS diagnostics and multiplicity-adjusted inference disagree. BID-only data and modeled costs remain insufficient to claim real funded/live performance.