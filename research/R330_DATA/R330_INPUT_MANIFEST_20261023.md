# R330 raw input manifest — 2026-10-23

This manifest records the exact raw CSV response saved from Massive's daily aggregate OHLC endpoint. Dates in this manifest refer to bar-start timestamps as returned by the API; US-stock daily aggregates are ET-labelled and are displayed here in their equivalent UTC timestamps, while crypto bars are UTC.

**Endpoint pattern:** /v2/aggs/ticker/{ticker}/range/1/day/2024-10-23/2026-10-22  
**Request parameters:** adjusted=true; sort=asc; limit=50000.  
**Window:** 2024-10-23 through 2026-10-22 inclusive.  
**Input data only:** no R330 PnL was calculated during collection or manifest preparation.

| Instrument | FundedNext class | Raw file | Rows | First timestamp UTC | Last timestamp UTC | SHA-256 |
|---|---|---|---:|---|---|---|
| AAPL | US stock CFD | raw/AAPL_daily_20241023_20261022.csv | 501 | 2024-10-23T04:00:00Z | 2026-10-22T04:00:00Z | 9a4161adbd9a6889e5830226f63e1ac10536a961f4b6199587307ee40352b48d |
| AMZN | US stock CFD | raw/AMZN_daily_20241023_20261022.csv | 501 | 2024-10-23T04:00:00Z | 2026-10-22T04:00:00Z | d2e677d502b87dffaec08b7e3036569f4c99401c0aba96be80ca1af4302ab17c |
| GOOG | US stock CFD | raw/GOOG_daily_20241023_20261022.csv | 501 | 2024-10-23T04:00:00Z | 2026-10-22T04:00:00Z | 2aa1a097ed22b68689f46040de5aa55dd05c1b6635de87f97741311aa070da0d |
| MSFT | US stock CFD | raw/MSFT_daily_20241023_20261022.csv | 501 | 2024-10-23T04:00:00Z | 2026-10-22T04:00:00Z | a5b30d15a82a915d659a84ba55382f3a82159eb6935a31967e2ba2bef94ca106 |
| NVDA | US stock CFD | raw/NVDA_daily_20241023_20261022.csv | 501 | 2024-10-23T04:00:00Z | 2026-10-22T04:00:00Z | 4b248ae1362e36739eacccd7786a9e956ce2319bfcb35e8890c2caa4642f736b |
| TSLA | US stock CFD | raw/TSLA_daily_20241023_20261022.csv | 501 | 2024-10-23T04:00:00Z | 2026-10-22T04:00:00Z | 841aa8f2027acf744b73bbbea7cd1dac9227d50bdbc1294e208938489339d81c |
| AMD | US stock CFD | raw/AMD_daily_20241023_20261022.csv | 501 | 2024-10-23T04:00:00Z | 2026-10-22T04:00:00Z | f13e5ee41ccdcc4c4eec4e390aa3b90d12d8372be042a7cbc28b53524fb38801 |
| META | US stock CFD | raw/META_daily_20241023_20261022.csv | 501 | 2024-10-23T04:00:00Z | 2026-10-22T04:00:00Z | b7c5b4f6ad8034c36b48ef59d8d5a6a5aa47292a350ef63365ae56795b6125d1 |
| BTCUSD | Crypto CFD | raw/BTCUSD_daily_20241023_20261022.csv | 730 | 2024-10-23T00:00:00Z | 2026-10-22T00:00:00Z | 799fbcb438520cf2833172c9a985aaff9c4a080cfb48098c590e2ba6df8d76ef |
| ETHUSD | Crypto CFD | raw/ETHUSD_daily_20241023_20261022.csv | 730 | 2024-10-23T00:00:00Z | 2026-10-22T00:00:00Z | 38658f779569348f0aaddd0b1e5df39e65bd0326f7ffc99199521ce1a0fa57f5 |

## Source/API limitations

- Stock rows are split-adjusted underlying-market aggregates, not FundedNext's actual CFD BID/ASK quote history.
- Crypto rows are underlying spot traded-price aggregates, not FundedNext's actual CFD BID/ASK quote history.
- This dataset can test whether the registered price-persistence signal is worth further investigation. It cannot by itself determine live broker fills, symbol spreads, swap, account-rule breaches or day-179 pass probability.
- Additional spread/slippage costs are sensitivity assumptions specified in the pre-registration; exact symbol-specific spreads and financing must be sourced before any candidate may be promoted.
