# R207 — Failed US Opening-Range Breakout Fade

**Verdict: REJECT IN DISCOVERY; no eligible candidate.** Workflow: https://github.com/christianomomongan82-lang/scanner/actions/runs/38161422461

## Locked hypothesis

Use the six M5 bars opening 09:30–09:55 New York time to define the 30-minute opening range. Find the first non-flat M5 close after 10:00 ET that closes beyond the range. If a later non-flat M5 close returns inside the range within 60 minutes, fade the initial breakout at the next non-flat M5 open. The stop is the most adverse high/low from the initial breakout bar through the failure-confirmation close, and the target is 2R. One first breakout is considered per instrument/session day; only one position at a time per instrument.

No standard indicators or parameter grid were used. Session conversion uses America/New_York and passed the DST boundary test.

## Execution and costs

- Four instruments: USA 500, USA 100 Tech, USA 30, US Small Cap 2000.
- Source: Dukascopy M5 BID OHLC.
- Entry/exit screen: non-flat M5 candles; SL before TP; gap through stop fills at open; no time stop.
- Modeled round-trip cost: 1 and 2 price basis points. These are not verified broker spread, commission, or live slippage.
- Discovery: 2017–2021; forward: 2022–2025; common OOS cutoff: 2026-10-09 20:15 UTC.
- All four snapshots, Python compilation and DST check passed.

## Results

| Instrument | Discovery closes | Discovery PF @ 1bp | Discovery PF @ 2bp | Forward closes | Forward PF @ 1bp | Forward PF @ 2bp | Worst eligible forward cohort PF @ 1bp | OOS closes | OOS PF @ 1bp | OOS PF @ 2bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| USA 500 / S&P 500 | 871 | 0.6232 | 0.4254 | 670 | 0.8209 | 0.7292 | 0.6534 | 133 | 0.8114 | 0.7169 |
| USA 100 Tech / Nasdaq 100 | 867 | 0.9849 | 0.8881 | 691 | 0.9161 | 0.8458 | 0.8022 | 123 | 1.0500 | 0.9654 |
| USA 30 / Dow Jones | 870 | 0.7362 | 0.6372 | 677 | 0.9055 | 0.8058 | 0.7077 | 127 | 0.9010 | 0.8090 |
| US Small Cap 2000 | 582 | 0.8557 | 0.7887 | 684 | 0.9060 | 0.8465 | 0.6870 | 125 | 0.7714 | 0.7157 |

## Selection guardrail and verdict

The preregistered discovery eligibility gate required at least 50 discovery closes and PF >= 1.00 at 2 bps. **No instrument qualified**, so there is no forward-selected candidate. Forward metrics are shown for diagnostics only and must not be used to pick a replacement.

All four instruments failed the discovery gate, and none met the forward PF gate. The failed-breakout fade is rejected without further parameter tweaking. Bid-only execution is a screening proxy, especially for shorts; no claim of live/funded readiness is justified.

The `R207-failed-orb-audit` Actions artifact contains `meta.json`, per-instrument ledger, annual cohorts, all simulated trades and session diagnostics.
