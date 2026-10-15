# R189 Historical Dukascopy Replay — Results
Date: 2026-10-16  
**Verdict: NOT PASSED — not approved for the funded challenge or live manual execution.** This is a separate Dukascopy-feed replay, not an exact reproduction of the missing original HistData archive.

## Data and provenance

- GitHub data-only workflow: [run 38697080604](https://github.com/christianomomongan82-lang/scanner/actions/runs/38697080604), conclusion `success`.
- Raw artifact: `EURUSD-M1-Dukascopy-BID-ASK-2016-2025`, artifact ID `11959096102`, 67,719,731 bytes; expires 2027-01-13.
- Source: Dukascopy via the repository's existing `dukascopy-node` fetch method. The action downloaded raw quote data only; all signal/PnL calculations were run in local Python.
- BID and ASK each contain 4,415,493 rows, with identical timestamps from 2016-01-03 00:00 UTC through 2025-12-31 21:58 UTC. Zero duplicate timestamps and zero invalid OHLC rows after validation. SHA-256: BID `b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc`; ASK `52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b`.
- There are 538 gaps longer than one minute in the timestamp series; these include weekends and scheduled market closures and must not be interpreted as 538 unexplained data-loss incidents. All 240 month-side download requests completed without reported download errors.
- Entry-spread filter is 1.5 pips. Among eligible trades, median entry spread was 0.3 pip, 95th percentile 0.7 pip, maximum 1.1 pips. The all-timestamp spread distribution is inflated by weekend/holiday closed-market quotes, so those broad-series quantiles are not a realistic active-session spread estimate.

## Locked strategy tested

R189/L80; no parameter search or post-result tuning:
- Displacement 15 pips; lookbacks 11 and 12 M1 bars; late ratio >= 0.80; candle body >= 2 pips; directional consistency >= 7.
- Fixed GMT-5 session hours 03–11, excluding 06 and 09; deduplication 14 bars.
- Entry at the next M1 open: ASK for long, BID for short; entry spread <= 1.5 pips.
- SL 6 pips; TP 18 pips; MFE trigger 6 pips; zero-distance trailing stop; 60-bar time stop.
- Exit-side quotes are BID for long and ASK for short. Extra cost stress subtracts 0 / 0.2 / 0.5 / 0.8 / 1 / 2 pips per completed trade beyond observed BID/ASK prices.
- Main table below uses the execution-sensitivity replay: stop/target orders active at bar open are handled at the open if price has crossed them; ambiguous intrabar stop/target collisions are stop-first; a zero-distance trail that is reached and retraced before the bar closes exits in that bar. The original locked bar-activation variant gives essentially the same verdict.

## Main metrics — intrabar execution sensitivity variant

Metrics are in pips, with max drawdown calculated on the chronological trade-PnL curve; these are not funded-account dollar drawdowns.

| Segment | Extra cost | Trades | PF | Net pips | Max DD pips | Trades/week |
|---|---:|---:|---:|---:|---:|---:|
| 2016–2025 | 0.0 | 1,673 | 1.442 | 2,135.5 | 74.5 | 3.21 |
| 2016–2025 | 0.2 | 1,673 | 1.360 | 1,800.9 | 84.4 | 3.21 |
| 2016–2025 | 0.5 | 1,673 | 1.248 | 1,299.0 | 102.7 | 3.21 |
| 2016–2025 | 0.8 | 1,673 | 1.145 | 797.1 | 121.0 | 3.21 |
| 2016–2025 | 1.0 | 1,673 | 1.082 | 462.5 | 142.5 | 3.21 |
| 2016–2025 | 2.0 | 1,673 | 0.812 | -1,210.5 | 1,286.3 | 3.21 |
| Discovery 2016–2020 | 0.5 | 906 | 1.218 | 624.2 | 102.7 | 3.47 |
| Discovery 2016–2020 | 1.0 | 906 | 1.056 | 171.2 | 140.4 | 3.47 |
| Forward slice 2021–2025 | 0.5 | 767 | 1.284 | 674.8 | 93.8 | 2.94 |
| Forward slice 2021–2025 | 1.0 | 767 | 1.114 | 291.3 | 142.5 | 2.94 |
| Forward slice 2021–2025 | 2.0 | 767 | 0.838 | -475.7 | 586.8 | 2.94 |

## Forward annual stability at +1 pip extra cost

| Year | Trades | PF | Net pips |
|---|---:|---:|---:|
| 2021 | 68 | 1.121 | 27.0 |
| 2022 | 321 | 0.976 | -27.4 |
| 2023 | 145 | 1.058 | 29.4 |
| 2024 | 74 | 1.495 | 100.4 |
| 2025 | 159 | 1.330 | 161.9 |

Four-week circular block bootstrap on forward weekly net PnL at +1 pip: mean +1.116 pips/week; 94.72% of resampled means were positive, but the 95% interval was [-0.223, +2.489] pips/week and therefore includes zero.

## Execution feasibility

In the intrabar replay, median holding time is 2 minutes; 30.7% of trades exit within the same M1 minute as entry, 47.5% within one minute, and 79.1% within five minutes. This does not fit the current manual phone workflow where email receipt and order placement can take several minutes. Entry delay was not simulated, so real results for that workflow would likely be worse.

## Gate decision

**Fail / not approved for funded use.** The project robustness floor is PF 1.10: the full 2016–2025 result is only PF 1.082 at +1 pip, the discovery slice is 1.056, and the forward annual floor is 0.976 (2022). The forward bootstrap interval crosses zero. Costs of +2 pips/trade make the aggregate and forward results clearly negative. In addition, this M1 trade/management profile cannot be reproduced reliably by manual phone execution.

Keep the parameter set locked. Do not tune it based on this report. It is not declared a permanent proof of zero edge because this feed is not the original HistData feed, but it is **not a qualified strategy** for funded-challenge sizing or inclusion in an executable strategy portfolio. Broker-specific commissions, live slippage, order latency, provider daily/max loss behavior, and the Quick Strike constraint remain unverified.
