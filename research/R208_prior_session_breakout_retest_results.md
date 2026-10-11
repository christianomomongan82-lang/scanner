# R208 — Prior US Cash-Session Breakout and Held Retest

**Verdict: REJECT IN DISCOVERY; no eligible candidate.** Workflow: https://github.com/christianomomongan82-lang/scanner/actions/runs/38161697576

## Locked hypothesis

Use the prior valid regular US cash session (09:30–16:00 New York time) high and low. A valid reference session requires at least 70 M5 bars, an observed 15:55 bar, and at least 60 non-flat bars. In the next session, take the first M5 close beyond the prior session high/low. Within 60 minutes of that trigger close, require a later non-flat M5 candle to touch the broken level intrabar and close back in breakout direction. Enter at the next non-flat M5 open. Stop is the retest candle low for longs or high for shorts; target is 2R. Only the first breakout level per instrument/session day is considered.

The strategy uses raw M5 OHLC and America/New_York session times. No indicators or parameter grid.

## Execution and validation

- Universe: USA 500, USA 100 Tech, USA 30 and US Small Cap 2000.
- Source: Dukascopy M5 BID OHLC.
- Modeled round-trip costs: 1 and 2 price basis points relative to entry, not verified broker costs.
- Discovery: entries 2017–2021; forward: 2022–2025; OOS cutoff: 2026-10-09 20:15 UTC.
- Snapshot validation, Python compilation and DST conversion tests passed.

## Results

| Instrument | Discovery closes | Discovery PF @ 1bp | Discovery PF @ 2bp | Forward closes | Forward PF @ 1bp | Forward PF @ 2bp | Worst eligible forward cohort PF @ 1bp | OOS closes | OOS PF @ 1bp | OOS PF @ 2bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| USA 500 / S&P 500 | 522 | 0.3965 | 0.2381 | 455 | 0.7381 | 0.5904 | 0.6606 | 98 | 0.7037 | 0.5705 |
| USA 100 Tech / Nasdaq 100 | 545 | 0.6545 | 0.5339 | 452 | 0.7190 | 0.6125 | 0.5096 | 96 | 1.0688 | 0.9173 |
| USA 30 / Dow Jones | 515 | 0.6917 | 0.5239 | 454 | 0.6630 | 0.5324 | 0.5658 | 85 | 0.4103 | 0.3409 |
| US Small Cap 2000 | 376 | 0.8805 | 0.7130 | 462 | 0.8645 | 0.7525 | 0.6994 | 88 | 0.7487 | 0.6393 |

## Selection guardrail and verdict

The preregistered discovery eligibility gate required at least 50 discovery closes and PF >= 1.00 at 2 bps. **No instrument qualified**, so there is no forward-selected candidate. Forward metrics are shown for diagnostics only and are not used to select a replacement.

All four instruments failed the discovery PF gate and showed weak forward PFs. The prior-session breakout-retest setup is rejected with no parameter tweaking. BID-only execution remains a screening proxy, particularly for shorts; this is not evidence of live/funded readiness.

The `R208-prior-session-retest-audit` Actions artifact contains `meta.json`, instrument ledger, annual cohorts, all trades and session diagnostics.
