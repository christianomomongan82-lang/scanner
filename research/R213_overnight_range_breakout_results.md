# R213 — US Overnight-Range First Breakout

**Verdict: REJECT.** One raw-price hypothesis was registered and tested on the downloaded R205 M5 snapshot. No standard indicators or parameter grid were used. This calculation ran in the local Python environment; no new GitHub Actions backtest was launched.

## Preregistered rule

- Universe: USA 500, USA 100 Tech, USA 30, US Small Cap 2000.
- Overnight range: non-flat M5 BID candles opening 00:00–09:25 America/New_York. Require the complete 114-slot five-minute timestamp grid and at least 60 non-flat bars.
- Cash session: require the full 78-slot grid from 09:30 to 15:55 ET, at least 60 non-flat bars, and an executable non-flat 15:55 bar open for scheduled liquidation.
- Signal: first non-flat M5 close from 09:30 to 15:50 ET outside the overnight range; above range is long, below range is short. One attempt per symbol/date.
- Entry: next non-flat M5 open after the completed signal candle and before 15:55 ET.
- Stop: signal candle low for long, high for short. Target: 2R.
- Execution: BID M5 OHLC, stop before target when both are touched, stop-gap fill at open, skip flat bars. Any remaining position exits at the scheduled 15:55 M5 open without observing that candle's later high/low.
- Stress costs: round-trip price cost = entry × 1 or 2 / 10,000. These are not verified real execution costs.
- Frozen discovery selection: at least 50 closed discovery trades and PF ≥1.00 at 2 bps; then highest discovery trade count, then PF at 2 bps. Forward is calculated only for the discovery-selected instrument.
- Discovery: 2017–2021; forward: 2022–2025; OOS through the common cutoff 2026-10-09 20:15 UTC.

## Data validation

All four source series are BID-only M5 OHLC. Timestamps were aligned to five-minute boundaries, ordered, finite and unique; no duplicates or off-grid times were found. Source flat candles were not forward-filled and were excluded from overnight extrema, entry/signal detection and intrabar exit checks.

| Instrument | Bars | Duplicate timestamps | Off-grid timestamps | Flat bars |
|---|---:|---:|---:|---:|
| USA 500 | 886,206 | 0 | 0 | 207,186 |
| USA 100 Tech | 886,039 | 0 | 0 | 206,491 |
| USA 30 | 886,038 | 0 | 0 | 206,175 |
| US Small Cap 2000 | 699,134 | 0 | 0 | 170,238 |

## Discovery selection only

| Instrument | Closed trades | PF @ 1 bp | PF @ 2 bps | Status |
|---|---:|---:|---:|---|
| USA 500 | 1,177 | 0.8584 | 0.7302 | Ineligible |
| USA 100 Tech | 1,179 | 0.9642 | 0.8722 | Ineligible |
| USA 30 | 1,170 | 0.9108 | 0.7864 | Ineligible |
| US Small Cap 2000 | 656 | 1.1511 | 1.0736 | Selected by discovery eligibility |

Only US Small Cap 2000 passed the discovery gate and was locked before computing forward metrics.

## Locked candidate — forward 2022–2025

| Cost | Closed trades | PF |
|---|---:|---:|
| 1 bp | 942 | 0.8172 |
| 2 bps | 942 | 0.7653 |

### Forward entry-year cohorts

| Year | Closed trades | PF @ 1 bp | PF @ 2 bps |
|---|---:|---:|---:|
| 2022 | 245 | 0.9338 | 0.8869 |
| 2023 | 244 | 0.8597 | 0.8055 |
| 2024 | 223 | 0.7853 | 0.7301 |
| 2025 | 230 | 0.6902 | 0.6405 |

All forward years have at least five trades, and all fail the minimum annual cohort PF of 1.00 at 1 bp.

## OOS 2026

| Cost | Closed trades | PF |
|---|---:|---:|
| 1 bp | 181 | 1.0414 |
| 2 bps | 181 | 0.9680 |

OOS does not override the locked forward failure.

## Causal and execution audit

- Every candidate-capable five-minute prefix was checked for first breakout signal stability.
- Every emitted signal/stop was recomputed on a dataset truncated at the signal bar; no later data were needed.
- Discovery prefix checks: USA 500 95,865; USA 100 Tech 95,711; USA 30 95,865; US Small Cap 2000 53,130. The full selected run checked 144,452 prefixes.
- Entry preceding signal-bar close: 0 violations. Exit preceding entry: 0 violations. Duplicate symbol/session-date trades: 0.
- Execution/timezone unit tests: 9/9 passed, including long/short stop-first collisions, stop-gap at open, scheduled exit without use of future candle range, DST session grids, and transaction invariants.

## Locked gates

| Gate | Result |
|---|---|
| At least 30 forward closes | PASS — 942 |
| PF ≥1.15 at 1 bp | FAIL — 0.8172 |
| PF ≥1.15 at 2 bps | FAIL — 0.7653 |
| Each forward year with ≥5 trades has PF ≥1.00 at 1 bp | FAIL — worst year 0.6902 |
| PF >1.40 extra audit hold | Not triggered |
| Final verdict | **REJECT** |

The script and machine-readable ledgers are in this branch. Full trade-by-trade R213 output and the complete R205 audit comparison are in the local execution bundle delivered with this report. Costs are hypothetical; actual bid/ask execution, commission, financing and live slippage remain unverified. This does not establish funded/live readiness.