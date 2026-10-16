# R271 — Daily 20-session breakout continuation: GAGAL

Date: 2026-10-16  
**Final verdict: GAGAL. Close this locked candidate; do not retune it on these periods.**

## What was tested

The pre-registration was committed before running the calculation: R271_DAILY_TREND_BREAKOUT_PREREGISTRATION.md. This is a medium-horizon daily breakout hypothesis, not a modification of R270. It requires a completed New York-close FX session to close beyond the previous 20 sessions' high/low, enters at the exact 17:05 New York quote, uses a stop of 2 × prior ATR20 and a target of 2R, and exits on stop/target or the close of the tenth subsequent valid session. The signal has no discretionary filters; overlap signals are skipped. Exits use the executable side (BID for long, ASK for short), with stop priority inside a minute and extra round-trip cost stress of 0, 0.5, 1 and 2 pips.

## Input and data audit

- Feed: Dukascopy through dukascopy-node; EURUSD M1 BID/ASK; UTC data collection window 2016-01-01 through 2025-12-31.
- Raw archive SHA-256: b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e.
- 4,415,493 rows on BID and ASK each; zero duplicate timestamps on either side; 4,415,493 common timestamps.
- FX-calendar filter retained 3,749,493 rows and excluded 666,000 weekend/closed-hour rows. No synthetic minute bars were created; zero negative opening spreads were detected. Median observed opening spread was about 0.30 pip, p95 about 0.80 pip.
- 2,607 New York-close session buckets; 10 lacked an exact 16:59 close bar. There were 320 raw close-breakout signals, 266 with a valid exact 17:05 entry quote, and 126 closed trades after overlap rules. Signals were skipped because of missing entry quote (53), missing 16:59 close (1), or because a position was already open at the signal close (140 among otherwise eligible signals). The trade ledger includes each accepted trade and its exit.
- All calculations ran in the local Python/container session. No GitHub Actions backtest was run. The data source archive is referenced by hash; the code, trade ledger and result JSON are stored with this report.

## Results at +1 pip additional cost

| Period | Trades | PF (diagnostic) | Net R | Mean R/trade |
|---|---:|---:|---:|---:|
| Discovery 2016–2020 | 57 | 0.811 | −4.949 | −0.0868 |
| Validation 2021 | 14 | 0.769 | −1.437 | −0.1026 |
| Diagnostic forward 2022–2025 | 55 | 0.808 | −4.265 | −0.0775 |

The validation sample is only 14 trades, far below the preregistered minimum of 50. Forward results are also negative in aggregate. By year at +1 pip: 2022 = 14 trades, PF 0.602, −2.798R; 2023 = 14, PF 0.628, −1.642R; 2024 = 14, PF 1.489, +2.276R; 2025 = 13, PF 0.654, −2.101R. Only one of the four diagnostic-forward years was positive.

The four-week circular block bootstrap on the 209 calendar weeks from 2022–2025 (10,000 repetitions, seed 2712026) estimated mean weekly net return of −0.0204R, with 95% interval [−0.0722R, +0.0324R]. The interval crosses zero; only 22.06% of resampled means were positive.

## Cost sensitivity

| Extra cost | Discovery net R | 2021 net R | 2022–2025 net R |
|---:|---:|---:|---:|
| 0 pip | −4.552 | −1.322 | −3.892 |
| 0.5 pip | −4.751 | −1.379 | −4.079 |
| 1 pip | −4.949 | −1.437 | −4.265 |
| 2 pips | −5.346 | −1.552 | −4.638 |

The stream is already negative with no additional cost beyond observed BID/ASK, so transaction cost is not the primary explanation. It is negative across discovery, validation and forward aggregate. Exit types were 70 time exits, 46 stop hits, 9 targets and 1 stop-gap fill. Trade frequency is also low for reaching the challenge target quickly (about 11–12 closed trades per year in the period aggregates).

## Preregistered gates and verdict

All six historical-screen gates failed: discovery was not positive; validation was not positive and had fewer than 50 trades; forward aggregate was negative; only one of four forward years was positive; the block-bootstrap lower bound was negative; and forward net R remained negative at +2 pip cost. No challenge-path simulation was run because the preregistered rule only allowed it if the base stream was positive. Simulating more risk on a negative stream would not create an edge and would obscure the research conclusion.

**Conclusion:** R271 is GAGAL. Do not rescue it by shortening the breakout window, changing ATR multiples or picking the one positive year after seeing results. The failed claim is this exact daily breakout specification; it does not mathematically disprove every medium-term trend-following method. The broader project still has no funded-ready strategy. This archive ends in 2025, and 2022–2025 is contaminated by prior research; it cannot establish promotion-grade out-of-sample performance even if a future exploratory screen looks strong.

## Artifacts

- Pre-registration: R271_DAILY_TREND_BREAKOUT_PREREGISTRATION.md
- Local runner: r271_daily_trend_breakout.py
- Machine-readable summary: R271_results_compact.json
- Trade ledger: R271_trade_ledger.csv
