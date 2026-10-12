# Discovery-selection period sensitivity

**Exploratory only, not a new pass/forward validation.** The US Small Cap source begins 2018-08-08 while other instruments have longer history. Asset selection was rerun over the common 2018-08-08 to 2022-01-01 discovery interval using the same rules and 100-trade minimum. Because the primary forward/OOS results had already been inspected, the alternative forward/OOS figures are descriptive only and cannot promote any finalist.

| Strategy | Original selected | Common-span selected | Same? | Common discovery n | PF@2bps | Forward diagnostic PF@1 / PF@2 | OOS diagnostic PF@1 / PF@2 |
|---|---|---|---|---:|---:|---|---|
| R218 | US30 | US30 | Yes | 2075 | 0.948 | 0.872 / 0.826 | 0.959 / 0.900 |
| R219 | US Tech 100 | France 40 | No | 1218 | 0.956 | 0.952 / 0.894 | 0.842 / 0.787 |
| R220 | US Small Cap 2000 | US Small Cap 2000 | Yes | 125 | 1.535 | 0.802 / 0.774 | 1.149 / 1.113 |
| R221 | None | None | No | 26 max | 0.503 max | — | — |
| R222 | US30 | US30 | Yes | 2627 | 1.014 | 0.901 / 0.848 | 1.086 / 1.011 |
| R223 | US Tech 100 | Japan 225 | No | 282 | 0.854 | 1.019 / 0.969 | 1.481 / 1.426 |
| R224 | US Small Cap 2000 | US Small Cap 2000 | Yes | 492 | 1.181 | 0.988 / 0.954 | 1.327 / 1.272 |
| R225 | US30 | US Tech 100 | No | 517 | 0.971 | 0.928 / 0.899 | 0.985 / 0.943 |
| R226 | Japan 225 | FTSE 100 | No | 427 | 0.940 | 1.139 / 1.065 | 1.249 / 1.167 |

## Interpretation

Four of eight locked asset choices changed. The alternative forward/OOS data are post-hoc diagnostics, not a fresh validation; none meets the required forward PF >=1.15 at both modeled 1 and 2 bps. Main batch decisions remain unchanged.
