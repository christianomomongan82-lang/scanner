# R329 compact eligibility ledger schema
The official file is `eligibility_skip_audit.csv.gz`. This schema keeps the full scheduled weekly pre-outcome audit while shrinking a repetitive file to make repository archiving/reconstruction reliable. Epoch fields are Unix seconds in UTC.

| Field | Meaning |
|---|---|
| `h` | Registered lookback horizon in eligible weekly observations: 13, 26, or 39 |
| `t` | Signal candle open timestamp (Tuesday 10:00 UTC); that candle close is known at 11:00 UTC |
| `en` | Registered entry proxy (Tuesday 12:00 UTC exact H1 open) |
| `ex` | Scheduled exit proxy, one week after `en`, at Tuesday 12:00 UTC |
| `p` | Period code: D=discovery, C=confirmation, G=diagnostic, X=outside registered periods |
| `ok` | 1=eligible portfolio rebalance; 0=not eligible |
| `why` | Skip reason code: X=outside period; S_TS=signal timestamp not common; S_INACTIVE=signal bar inactive in ≥1 pair; HIST=insufficient eligible lookback; E_TS=entry timestamp not common; X_TS=exit timestamp not common; E_INACTIVE=entry bar inactive in ≥1 pair; X_INACTIVE=exit bar inactive in ≥1 pair; FEATURE=invalid signal/volatility; FLAT=flat after USD cap/zero signal; OK=eligible |
| `n` | Number of active legs with nonzero target weight |
| `days` | Calendar days spanned by the eligible weekly-observation lookback; -1 when not available |
| `usd` | Absolute net USD-factor exposure divided by final gross weight; -1 when not available |
| `gross` | Final absolute portfolio weight after registered caps |

The data audit and test log remain separate. This is an eligibility/skip audit only. It does not include post-entry returns or compute PnL.
