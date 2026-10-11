# R214 — H4 Three-Bar Impulse Exhaustion and Structure Reversal

**Final verdict: REJECT.** One preregistered raw-price hypothesis was executed in local Python. No new GitHub Actions backtest was launched. Forward performance failed both locked PF gates and annual-cohort consistency.

## Locked hypothesis

- Build UTC-anchored H4 candles only from exactly four consecutive H1 BID bars. Incomplete bins are skipped; no missing data are synthesized or forward-filled.
- **Long:** the three immediately preceding H4 candles are bearish with strictly descending closes; the current completed H4 candle is bullish and closes above the preceding candle high.
- **Short:** the three immediately preceding H4 candles are bullish with strictly ascending closes; the current completed H4 candle is bearish and closes below the preceding candle low.
- Entry: first non-flat M5 BID open at or after signal close +5 minutes, and strictly before the scheduled next H4 boundary. Stop is the signal H4 low (long) or high (short); target is 2R.
- One live position per instrument. M5 exits check SL before TP, stop gaps fill at available bar open, flat synthetic M5 bars cannot trigger execution, and unresolved trades are censored at the data cutoff.
- Costs are modeled as round-trip entry price × 1 or 2 / 10,000. They are stress-cost proxies, not verified broker spread, commissions, financing, or slippage.

## Source data and causal validation

- Source snapshots: ten indices, 20 H1/M5 BID-only files, **9,145,088 total rows**.
- Timestamp parse errors: 0; duplicate timestamps: 0; off-grid timestamps: 0; invalid OHLC relationships/non-finite rows: 0.
- Flat candles were counted and retained in source. Synthetic flat M5 bars were excluded from entry/exit execution; no forward-fill was used.
- All ten causal/truncation gates passed: **227,462 completed H4 prefixes checked**. Signals and signal-bar stops were independently recomputed using only the available prefix.
- Vectorized UTC H4 aggregation matched a scalar reference on a 1,500-H1-bar differential test (374 accepted bins, 14 skipped).
- Independent local execution, data and causality tests: **10/10 PASS**.
- Data source is the R205 artifact snapshot: https://github.com/christianomomongan82-lang/scanner/actions/runs/38160487617

## Discovery selection — frozen before forward

Eligibility was locked to at least 30 closed discovery trades and PF ≥ 1.00 at 2 bps. Among eligible indices, select the fewest discovery closes, then the higher PF at 2 bps as tie-break. Forward metrics for other indices were not used for replacement.

| Instrument | Discovery closes | PF @ 1 bp | PF @ 2 bps | Eligible? |
|---|---:|---:|---:|---|
| USA 500 / S&P 500 | 148 | 1.1003 | 1.0550 | Yes |
| USA 100 Tech / Nasdaq 100 | 150 | 0.8548 | 0.8265 | No |
| USA 30 / Dow Jones | 167 | 0.9917 | 0.9497 | No |
| US Small Cap 2000 | 126 | 0.9698 | 0.9448 | No |
| Germany 40 / DAX | 143 | 1.2371 | 1.1944 | Yes |
| FTSE 100 | 149 | 1.1870 | 1.1436 | Yes |
| France 40 / CAC 40 | 16 | 0.7560 | 0.7312 | No |
| EU Stocks 50 | 11 | 2.1463 | 2.0488 | No — fewer than 30 trades |
| Australia 200 | 180 | 1.0931 | 1.0497 | Yes |
| Japan 200+ | 172 | 1.0553 | 1.0124 | Yes |

The discovery-only rule selected **Germany 40 / DAX**: 143 closed trades, PF 1.2371 at 1 bp and 1.1944 at 2 bps.

## Locked forward result — 2022–2025

| Cost model | Closed trades | Profit factor | Required PF | Result |
|---|---:|---:|---:|---|
| 1 bp | 171 | 0.8479 | 1.15 | **FAIL** |
| 2 bps | 171 | 0.8144 | 1.15 | **FAIL** |

| Entry year | Closed trades | PF @ 1 bp | PF @ 2 bps | Annual gate at 1 bp |
|---|---:|---:|---:|---|
| 2022 | 43 | 0.4455 | 0.4355 | **FAIL** |
| 2023 | 48 | 1.1579 | 1.1177 | PASS |
| 2024 | 34 | 0.6800 | 0.6462 | **FAIL** |
| 2025 | 46 | 1.1481 | 1.0921 | PASS |

The worst qualifying annual entry cohort PF at 1 bp was **0.4455**. Forward trade count passed, but both PF gates and the annual-cohort gate failed.

## Additional OOS — 2026

Common OOS cutoff: **2026-10-09 20:00 UTC**.

| Cost model | Entries | Closed | Censored | PF |
|---|---:|---:|---:|---:|
| 1 bp | 29 | 28 | 1 | 0.6138 |
| 2 bps | 29 | 28 | 1 | 0.5954 |

OOS is diagnostic only and cannot overturn the locked forward rejection; its closed sample is below 30.

## Execution audit and limitations

- The full selected history contains 343 trade records: 342 closed (218 SL, 116 TP, 8 gap-through-stop) and one still open/censored at data end.
- Zero emitted entries occurred at or before signal close; zero closed exits occurred at or before entry; there were zero duplicate instrument/signal-bar trades.
- Source prices are BID-only. Shorts are not simulated with an observed ASK stream. Broker/prop spread, commission, financing and live slippage remain unverified.
- No live or funded profitability claim follows from this backtest.

## Decision

**REJECT.** The discovery-selected DAX candidate has sufficient forward trade count but PF of only 0.8479 / 0.8144 under the two cost assumptions, with the 2022 and 2024 cohorts failing. No parameter tweak or forward-based replacement was attempted.

The branch contains the report, discovery and forward ledgers, OOS table, source validation, metadata and execution tests. The full 343-row selected trade ledger and exact script are also available in the local execution bundle delivered in this conversation.