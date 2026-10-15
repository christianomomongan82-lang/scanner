# R261 — London-window impulse continuation (local-only)

**Status before execution:** preregistered; no results inspected at registration time  
**Execution contract:** Python backtest runs in the ChatGPT/container session. GitHub is only the data source and repository for the preregistration, runner, results, and ledger. Do not create or dispatch GitHub Actions to run this experiment.

## Hypothesis

After a comparatively large net price impulse from 05:00 through 08:00 Europe/London local time (using the completed H1 bars starting at 05:00, 06:00, and 07:00), EURUSD may continue in the same direction after the 08:00 London-local entry. This is an independent session-timing hypothesis, not a retune of R251–R260.

## Fixed rules

- Instrument: EURUSD, side-specific Dukascopy H1 BID and ASK OHLC.
- Data source: the already-retained GitHub Actions artifact named R258-multihorizon-momentum-audit (artifact ID 11916174401, repository christianomomongan82-lang/scanner), specifically dl/r251_fx/eurusd_bid_H1.csv and eurusd_ask_H1.csv.
- Build entry times from timezone-aware Europe/London local timestamps so DST changes are handled with the actual London clock, not a fixed UTC approximation.
- Signal window: require valid paired quote bars at local 05:00, 06:00, and 07:00 on the same local trading date. Signal impulse = BID close of the 07:00 bar minus BID open of the 05:00 bar.
- Threshold: absolute impulse at or above the 75th percentile of valid training-window impulse magnitudes, calculated solely from 2017-01-01 through 2020-12-31 UTC. Freeze that value for every later period.
- Direction: follow the sign of the impulse. Long entry uses ASK open at local 08:00; short entry uses BID open at local 08:00.
- Stop: long stop is the minimum BID low of the three signal bars; short stop is the maximum ASK high of the three signal bars. Reject non-positive risk or risk below 0.5 pip.
- Target: 1.5R from the executable-side entry.
- Time exit: if neither stop nor target has been hit, exit at the executable-side open of local 16:00 on that same London date. No holding overnight.
- No overlapping positions; at most one entry per local date. Each valid signal has a unique entry time and positions are closed by 16:00.
- Intrabar collision policy: check stop before target where both are touched in the same H1 candle. Model stop gaps at the executable-side bar open if it is already beyond the stop. Never interpolate or fill missing bars; if required bars or an exit quote are missing, skip the setup. Do not fabricate candles.
- Quote execution: enter/exit longs using ASK to enter and BID to exit; enter/exit shorts using BID to enter and ASK to exit. Report observed spread diagnostics. Stress results by subtracting extra costs of 0, 0.5, 1.0, and 2.0 pips per completed trade beyond observed quote-side execution.
- No optimization after looking at validation, forward, or OOS results.

## Periods

- Discovery / threshold fit: 2017-01-01 to 2020-12-31 UTC.
- Validation: 2021 calendar year.
- Forward: 2022–2025, with separate annual reporting for each year.
- OOS: 2026-01-01 through the last timestamp available in both quote feeds.

## Binary gates

At the +1 pip extra-cost stress level, a candidate can be labelled **PASS FOR FURTHER RESEARCH** only if all are true:
1. At least 100 closed trades in discovery and at least 50 in validation, forward, and OOS.
2. PF >= 1.10 in discovery, validation, forward aggregate, and OOS.
3. Every forward year (2022, 2023, 2024, 2025) has positive net pips and PF >= 1.00.
4. A circular 4-week block bootstrap over weekly forward net pips has a 95% confidence interval whose lower bound is above zero.
5. No data-integrity or execution-model gate fails.

Otherwise the binary verdict is **FAIL**. Passing these gates is not a funded-ready claim; broker commissions, live slippage, and funded-provider rules must still be separately verified.

## Required report

Record source artifact ID, file hashes, quote coverage/duplicates/invalid OHLC, spread quantiles, missing hourly points, fitted threshold, signal/trade counts, skips, exits by reason, PF/net/win rate/frequency at each cost level for every period, forward annual stats, bootstrap output, binary verdict, and any limitations. Save the machine results and full trade ledger alongside the runner.