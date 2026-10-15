# R189 historical same-feed replay: Dukascopy EURUSD M1 2016–2025

## Status and purpose
Preregistered before observing historical test output. This is an independent historical replay of the locked R189/L80 strategy on a newly acquired Dukascopy feed. It is NOT an exact reproduction of previously reported HistData/spread results because the original HistData files are not present.

## Execution boundary
- The raw-data collection job may run in GitHub Actions, but that job downloads and packages raw BID/ASK M1 quotes only.
- Signal generation, trade simulation, PnL calculations, bootstrap, gates, and verdict are run by Python in the local ChatGPT/container session.
- GitHub is used as input/artifact storage and source-code/results archive, never as the backtest compute engine.
- Do not use Massive. Do not modify the strategy parameters after observing results.

## Source and input
- Feed: Dukascopy via the same dukascopy-node downloader already used in this repository.
- Instrument/timeframe: EURUSD M1 BID and ASK.
- Window: 2016-01-01 00:00 UTC inclusive through 2026-01-01 00:00 UTC exclusive.
- Required artifact files: eurusd_bid_M1_2016-2025.csv.gz and eurusd_ask_M1_2016-2025.csv.gz, plus manifest/checksums.
- Keep unmatched quotes, duplicate timestamps, invalid OHLC, missing minutes, and spread diagnostics visible. Align only timestamps present in both quote streams; never create synthetic candles. Any invalid quote rows or duplicate timestamps are diagnosed and removed by the documented data reader.

## Locked R189/L80 strategy parameters
- Displacement threshold: 15 pips.
- Directional consistency minimum: 7.
- Late ratio minimum: 0.80.
- Candle body minimum: 2 pips.
- Lookback windows: 11 and 12 M1 bars.
- Signal session mapped to the legacy fixed GMT-5 wall clock (no DST): hours 03–11, excluding hours 06 and 09.
- Deduplicate signals by at least 14 bars.
- Entry: next M1 bar open, using ASK for long entry and BID for short entry.
- Maximum entry spread: 1.5 pips.
- Initial SL: 6 pips; TP: 18 pips.
- When favourable excursion reaches 6 pips, activate a zero-distance trailing stop under the existing R189 simulator behavior.
- Time stop: 60 M1 bars.
- Exit-side quotes: BID for long exits, ASK for short exits.
- Intrabar ambiguity policy: preserve the locked simulator's conservative stop-before-target ordering; report causal time-stop semantics (exit at scheduled bar open before checking that bar's later high/low). A legacy version may be included only as a diagnostic comparison, not substituted for the causal result.
- Extra-cost stresses: 0, 0.2, 0.5, 0.8, 1.0, and 2.0 pips/trade beyond observed BID/ASK execution.

## Required reporting
- Data coverage, timestamps, row counts, duplicates, invalid OHLC, side alignment, missing minutes, spread distribution, checksums, and downloaded source provenance.
- Signals before and after hour/spread filters; skipped-overlap/censored trades and exit reasons.
- All-period 2016–2025 results, split 2016–2020 and 2021–2025, and year-by-year results.
- PF, net pips, max drawdown, win rate, and trade frequency at every preregistered extra-cost level. Include forward 2021–2025 weekly block bootstrap after +1 pip.
- Compare the resulting Dukascopy feed with the formerly reported R189 figures but do not present it as an exact reproduction of the missing HistData feed.
- No parameter search/tuning.

## Interpretation
A favorable result on a separate feed does not rescue the absent original data or verify funded readiness. Live broker commission, slippage, manual entry delay, and provider-specific DLL/MLL mechanics remain separate verification items.
