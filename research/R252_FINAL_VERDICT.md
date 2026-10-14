# R252 — Final Binary Verdict

**Verdict: GAGAL.** The locked EURUSD H1 tail-threshold momentum/reversal experiment failed.

Run: https://github.com/christianomomongan82-lang/scanner/actions/runs/38521990341

## Preregistered procedure
- Six configurations: momentum-following or reversal at 3-, 6-, or 12-hour lookbacks.
- Signal only when the absolute lookback return first crosses above the 90th percentile of absolute returns fitted on 2017–2020. No threshold is fitted on validation/forward/OOS.
- One candidate is selected by validation-year 2021 PF after +1 additional pip cost (minimum 50 validation trades; tie-break mean expectancy then trade count).
- Entry: next exact H1 open after the completed signal candle; exit: exactly four elapsed hours later.
- Longs enter EURUSD ASK and exit BID; shorts enter BID and exit ASK. Added cost stress is charged on top of observed quote-side costs.

## Data audit
EURUSD BID and ASK H1 sources each contain 85,170 rows from 2017-01-01 through 2026-10-13. There were zero duplicate timestamps, zero invalid OHLC rows, and zero off-hour timestamps. Forty missing-hour gaps were preserved; the script did not fill missing bars. The common BID/ASK overlap contains 85,170 rows.

## Selection and results
The 2021 validation rule selected **L12_MOMENTUM** (12-hour lookback, follow direction of return). Its validation performance at +1 additional pip was PF 1.179 across 126 trades. That validation success did not carry forward.

| Period | Trades | PF, observed BID/ASK only | PF +0.5 pip | PF +1 pip | PF +2 pips |
|---|---:|---:|---:|---:|---:|
| Discovery 2017–2020 | 749 | 0.829 | 0.778 | 0.730 | 0.645 |
| Validation 2021 | 126 | 1.411 | 1.289 | 1.179 | 0.992 |
| Forward 2022–2025 | 888 | 0.725 | 0.687 | 0.652 | 0.586 |
| OOS 2026 through Oct 13 | 92 | 0.835 | 0.787 | 0.742 | 0.661 |

Forward net at +1 pip was **-3,537.3 pips**, average **-3.98 pips/trade**, with 4.25 trades/week. OOS at +1 pip was **-230.8 pips** and PF 0.742. The method produced plenty of trades; frequency was not the cause of failure.

Forward annual PF at +1 pip: 2022 0.584, 2023 0.789, 2024 0.472, 2025 0.803. All four forward years failed the annual PF >=1.00 gate.

The circular four-week block bootstrap for forward trades at +1 pip returned **P(mean > 0) = 0.000**, with 95% interval **[-5.612, -2.382] pips/trade**.

## Locked acceptance gates

| Gate | Result |
|---|---|
| Validation at least 50 trades | PASS — 126 |
| Validation PF >= 1.05 at +1 pip | PASS — 1.179 |
| Discovery at least 100 trades | PASS — 749 |
| Discovery PF >= 1.00 at +1 pip | **FAIL — 0.730** |
| Forward at least 100 trades | PASS — 888 |
| Forward PF >= 1.10 at +1 pip | **FAIL — 0.652** |
| Forward PF >= 1.05 at +2 pips | **FAIL — 0.586** |
| Forward frequency >= 2 trades/week | PASS — 4.25 |
| Each forward year with >=20 trades has PF >=1 at +1 pip | **FAIL — all four years below 1** |
| Four-week bootstrap supports positive expectancy at 95% | **FAIL — probability 0%, CI below zero** |
| OOS at least 30 trades | PASS — 92 |
| OOS PF >= 1.00 at +1 pip | **FAIL — 0.742** |

**Final status: GAGAL.** The 2021 validation winner was a regime-specific result; it lost money in discovery, forward, and OOS even before the +1-pip stress. Do not tune these six configurations based on the failed forward/OOS results.
