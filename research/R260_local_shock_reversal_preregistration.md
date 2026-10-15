# R260 — Single-Hour Shock-Reversal Test (LOCAL EXECUTION ONLY)

**Status: preregistered before R260 performance calculation.**  
**Execution requirement:** run the Python engine inside the current ChatGPT/container session. Do not dispatch or create a GitHub Actions backtest workflow.  
**Input provenance:** GitHub Actions artifact 11916174401, `R258-multihorizon-momentum-audit.zip`, specifically its EURUSD H1 BID and ASK CSV snapshots. The artifact is downloaded into the session for local execution.  
**Feed window:** 2017-01-01 through the available 2026 OOS end. This is H1 data, not R189's M1 data.

## Hypothesis

After an unusually large completed one-hour candle, EURUSD tends to reverse part of that single-bar shock over the next several hours. This is not a rolling multi-hour momentum signal, a rolling-extreme sweep/reclaim, or an Asian-session breakout.

## Frozen rule

- Signal features use completed H1 candles only.
- Fit the shock threshold once: the 90th percentile of absolute EURUSD BID candle body size in pips, calculated solely from valid bars dated 2017-01-01 through 2020-12-31 UTC.
- A bearish signal candle meeting or exceeding this fixed threshold produces a LONG signal; a bullish signal meeting or exceeding the threshold produces a SHORT signal.
- Enter at the next exact H1 open, if both BID and ASK OHLC are available there.
- Long execution: ASK entry, BID stop/target/time exit. Initial stop is the signal candle's BID low; target is 1R above entry, where R is entry-to-stop distance.
- Short execution: BID entry, ASK stop/target/time exit. Initial stop is the signal candle's ASK high; target is 1R below entry.
- Skip trades whose entry is already beyond the protective stop, whose risk distance is non-positive or below 0.5 pip, or whose entry/required quote bars are incomplete.
- Hold for at most six elapsed hours. Stop/target are checked on observed H1 quote bars; when both touch within the same bar, stop takes precedence. A stop gap fills at the executable open. If the time-exit hour is missing, use the first later observed quote at or after the six-hour horizon; never synthesize missing OHLC bars.
- One position at a time. A signal is skipped when its entry would overlap an already-open position.
- Compute PF/net/expectancy using actual BID-entry/ASK-entry and executable exit-side quotes, then stress an extra 0, 0.5, 1.0, and 2.0 pips per closed trade. This additional cost is a stress assumption, not a verified live fee/slippage measurement.
- No parameter grid and no tuning after results. Fixed holding horizon 6h and target 1R.

## Periods

- Discovery/training: 2017–2020.
- Validation: 2021.
- Forward: 2022–2025.
- OOS diagnostic: 2026 through the final timestamp available in the downloaded snapshot.

Period statistics use trades whose entry time is within the period and whose exit occurs before the period boundary. Annual forward cohorts use the same rule.

## Binary acceptance gates

All are required:
1. At least 50 completed validation trades.
2. Validation PF >= 1.05 after +1 pip.
3. Discovery PF >= 1.00 after +1 pip.
4. At least 150 completed forward trades.
5. Forward PF >= 1.10 after +1 pip.
6. Forward PF >= 1.05 after +2 pips.
7. Forward frequency >= 2 completed trades per week.
8. Every forward entry-year with >=20 completed trades has PF >= 1.00 after +1 pip.
9. Circular four-week block bootstrap on forward weekly net pips after +1 pip has a 95% confidence interval with lower bound > 0.
10. At least 30 completed OOS trades and OOS PF >= 1.00 after +1 pip.

If any gate fails, verdict is **GAGAL**. The data has been reused in previous research rounds and this new idea was conceived after earlier results were known; therefore, even a pass is only a candidate edge, not proof of untouched global OOS or funded readiness.

## Outputs to preserve on this branch

- `research/r260_local_shock_reversal_results.json`
- `research/r260_local_shock_reversal_trades.csv`
- `research/r260_local_shock_reversal_annual.csv`
- `research/r260_local_shock_reversal.py` (local runner; it reads the cached artifact and does not download data or trigger Actions)

The complete raw data is sourced from the GitHub artifact listed above; the result must include file checksums and data-quality diagnostics.
