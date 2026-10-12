# R218–R226 extended audit

- Independent per-ledger audit: **106/106 passed**, zero failed; 102,860 trade rows inspected.
- Signal causal-prefix checks: 90/90 passed.
- Full test register: 100/100 passed.
- Transaction cost sensitivity tested at 0, 1, 2, 3 and 5 bps per trade.
- Moving block bootstrap: 2,000 draws per selected strategy-period-cost cell, using circular 4-week blocks, estimating the 95% interval for mean net bps per trade.

## Forward expectancy at modeled 2 bps

| Strategy | Mean net bps/trade | 95% block-bootstrap interval | Bootstrap P(mean > 0) |
|---|---:|---:|---:|
| R218 | -3.469 | -5.304 to -1.761 | 0.000 |
| R219 | -0.237 | -2.269 to 1.701 | 0.398 |
| R220 | -7.426 | -20.857 to 5.188 | 0.137 |
| R222 | -2.730 | -4.102 to -1.306 | 0.000 |
| R223 | -2.921 | -12.498 to 6.815 | 0.300 |
| R224 | -1.346 | -7.126 to 4.299 | 0.309 |
| R225 | -3.368 | -12.424 to 6.754 | 0.253 |
| R226 | +0.065 | -2.964 to 3.220 | 0.502 |

R218 and R222 had block-bootstrap intervals fully below zero at modeled 2 bps. R226 is near breakeven, but its interval is wide and it does not meet the required PF gate. R220 showed the strongest discovery PF, then fell below PF 0.80 in forward; its discovery result is highly regime-sensitive. R224 rebounded in OOS, but forward PF was below 1 at both costs and every forward annual cohort failed the annual PF gate. OOS does not override forward rejection.

## Annual cohort stability at 1 bp

| Strategy | Weakest forward year | Trades | PF @1 bp | All annual cohorts PF >=1? |
|---|---:|---:|---:|---|
| R218 | 2023 | 454 | 0.720 | No |
| R219 | 2023 | 582 | 0.989 | No |
| R220 | 2023 | 28 | 0.245 | No |
| R222 | 2023 | 707 | 0.706 | No |
| R223 | 2024 | 57 | 0.531 | No |
| R224 | 2024 | 142 | 0.877 | No |
| R225 | 2022 | 128 | 0.830 | No |
| R226 | 2023 | 152 | 0.907 | No |

R221's maximum discovery sample was 26 trades, below the registered 100-trade minimum, so no forward/OOS candidate was selected.

## Execution and data boundary

The engine calculates signals using closed raw H1 candles; entry is the next exact hourly open. No flat bars are synthesized or forward-filled. Time exits use the first observed non-flat open at or after the scheduled horizon, and closed trades must exit inside their assessment period. BID-only data and modeled costs are insufficient to claim funded/live readiness.

## Common-history selection sensitivity — post-hoc only

The shared-history interval is 2018-08-08 to 2022-01-01, matching the latest-starting index source. Selection changed four of eight assets (R219 to France 40, R223 to Japan 225, R225 to US Tech 100, R226 to FTSE 100). This analysis happened after the main forward/OOS data had already been reviewed, so the alternate forward/OOS readings are descriptive and cannot be considered confirmation. None of these alternative assets reaches PF 1.15 at both modeled cost levels in forward. The main batch verdicts are unchanged.

The exact CSV and explanatory note are stored as R218_R226_equal_span_selection_sensitivity.csv and R218_R226_equal_span_selection_sensitivity.md.
