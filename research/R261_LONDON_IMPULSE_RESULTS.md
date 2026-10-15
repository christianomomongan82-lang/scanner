# R261 — Official local backtest result

**Binary verdict: FAIL. Reject this setup; do not tune it using forward/OOS results.**

## Setup tested

EURUSD continuation after the completed 05:00–08:00 Europe/London H1 impulse. At the 08:00 London open, enter in the impulse direction if its absolute magnitude is at or above the 75th percentile fitted exclusively on complete Monday–Friday windows from 2017–2020. Stop is the three-bar window extreme on the correct executable side, target 1.5R, and time exit at 16:00 London on the same day. No overnight holds. London-local timestamps use the IANA Europe/London timezone, so daylight-saving changes are handled.

Quote execution uses ASK to enter longs and BID to exit longs; BID to enter shorts and ASK to exit shorts. A stop is checked before a target on same-bar conflicts; stop gaps execute at the observed executable-side open. Missing/incomplete bars were not filled or interpolated.

## Source and data quality

- Downloaded from existing GitHub artifact **R258-multihorizon-momentum-audit**, artifact ID **11916174401**, in christianomomongan82-lang/scanner. The backtest itself ran in the ChatGPT/container Python session, not GitHub Actions.
- Data: EURUSD H1 BID and ASK OHLC, 2017-01-01 00:00 UTC through 2026-10-13 23:00 UTC.
- BID: 85,170 rows; zero duplicate timestamps and zero invalid OHLC rows. SHA256: 68d667ef6e84d4357207da86dc0ffd18453bbfa91837d0dd1349ac82bb6c47bf
- ASK: 85,170 rows; zero duplicate timestamps and zero invalid OHLC rows. SHA256: 8b9d3660213fae55bf0066c42fd093badc4a8092ddb2a0ca1672bbac5bcc7b91
- Complete hourly grid: 85,752 points; 582 missing/incomplete points left missing. No negative opening spreads.
- Observed opening spread: median 0.4 pip; p95 7.4 pips; p99 8.9 pips; maximum 23.1 pips. These data include wider-than-normal observations; no independent live spread/commission/slippage claim is made.
- Flat placeholder quotes were observed while FX was closed on weekends. The first diagnostic pass was discarded because it included closed-market weekend dates in the threshold sample. The official run excludes Saturday/Sunday London-local dates and fits the unchanged 75th-percentile rule on eligible weekdays only. See the preregistration addendum; no results from the discarded pass are used here.
- Fitted threshold: **14.5 pips** absolute 05:00–08:00 London-local impulse.
- 2,552 complete weekday London windows across all periods, including 1,044 training windows; 612 windows triggered the threshold and became trades. Exit reasons: 275 stops, 178 targets, 159 time exits. No tiny-risk or overlap skips; missing/incomplete holding windows were skipped.

## Period results

PF and net pips after the listed *additional* cost per completed trade, on top of the observed BID/ASK quote-side execution:

| Period | Trades | PF, +0 pip | Net, +0 pip | PF, +0.5 pip | Net, +0.5 pip | PF, +1 pip | Net, +1 pip | PF, +2 pip | Net, +2 pip | Trades/week |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Discovery 2017–2020 | 262 | 1.009 | +32.7 | 0.973 | −98.3 | 0.938 | −229.3 | 0.873 | −491.3 | 1.26 |
| Validation 2021 | 59 | 1.717 | +370.4 | 1.644 | +340.9 | 1.574 | +311.4 | 1.444 | +252.4 | 1.13 |
| Forward 2022–2025 | 249 | 1.054 | +189.2 | 1.018 | +64.7 | **0.984** | **−59.8** | 0.918 | −308.8 | 1.19 |
| OOS 2026 through 13 Oct | 42 | 1.312 | +137.4 | 1.258 | +116.4 | 1.206 | +95.4 | 1.111 | +53.4 | 1.03 |

## Forward annual check at +1 pip extra cost

| Year | Trades | PF | Net pips |
|---|---:|---:|---:|
| 2022 | 99 | 0.727 | −500.8 |
| 2023 | 46 | 1.245 | +125.8 |
| 2024 | 33 | 1.266 | +92.1 |
| 2025 | 71 | 1.238 | +223.1 |

The strategy was strongly negative in 2022. The aggregate forward PF also falls below 1 after +1 pip stress, even though 2023–2025 are positive.

## Uncertainty and binary gates

A circular 4-week block bootstrap over 2022–2025 weekly net pips after +1 pip (5,000 replications, seed 261) gives:
- Observed mean weekly net: **−0.286 pip/week**
- Bootstrap probability of positive mean: **45.38%**
- 95% interval for mean weekly net: **[−5.02, +4.38] pip/week**

Failed gates:
- Discovery PF >= 1.10: **FAIL** (0.938)
- Forward aggregate PF >= 1.10: **FAIL** (0.984)
- OOS minimum 50 trades: **FAIL** (42)
- All four forward years positive with annual PF >= 1.00: **FAIL** (2022 PF 0.727, net −500.8 pips)
- Forward bootstrap 95% interval lower bound above zero: **FAIL**
  
Validation PF and OOS PF at +1 pip pass their numeric threshold, but they do not offset the discovery/forward failures and OOS sample shortage.

## Decision

**FAIL. Close R261 without parameter tuning.** The isolated strong validation and 2026 OOS results do not establish a robust edge when discovery and forward performance fail. Frequency is only about 1.0–1.3 trades/week, so it is not a high-frequency route to a funded target.

This test is not a reproduction of R189: the stored source is H1, while R189 requires M1. The result also does not model independently verified broker commissions, manual-entry delay, live slippage, or funded-provider DLL/MLL mechanics. No funded-challenge pass probability should be inferred.

## Files

- Preregistration: research/R261_london_impulse_preregistration.md
- Local runner: research/r261_london_impulse.py
- Machine-readable results: research/R261_london_impulse_results.json
- Annual table: research/R261_london_impulse_annual.csv
- Full ledger: research/R261_london_impulse_trades.csv.gz (gzip-compressed CSV)
