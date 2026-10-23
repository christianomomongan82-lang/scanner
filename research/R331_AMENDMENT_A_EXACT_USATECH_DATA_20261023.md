# R331 Amendment A — exact-target index feed replaces unentitled QQQ proxy

**Committed before any R331 event return/PnL was calculated.**

## Reason for amendment

The registered initial screen specified QQQ 5-minute aggregate bars as an underlying-market proxy. Massive returned NOT_ENTITLED for the QQQ intraday-bars endpoint under the connected plan. Daily bars cannot evaluate a 30-minute exit, so the proxy route is stopped; no price/PnL results were calculated from it.

The replacement input is Dukascopy USATECHIDXUSD M1 BID/ASK history, aggregated locally into five-minute bars, plus prior-session daily VXN close from the CBOE series. USATECHIDXUSD is the project’s target Nasdaq-100 CFD-style index symbol and is more relevant to the funded objective than QQQ, though this is still Dukascopy feed data, not the actual FundedNext platform's quote stream. Actual platform spread/slippage/financing must still be verified before promotion.

## Frozen data and rules after Amendment A

- Instrument: USATECHIDXUSD M1 BID and ASK, from Dukascopy through dukascopy-node 1.50.0; no synthetic flat bars, no forward-fill.
- Requested window: 2023-10-25 through 2026-10-22 inclusive for index quotes; paired quote bars only.
- VXN: CBOE daily close with available coverage 2023-10-25 through 2026-10-21. Use prior completed VXN close only. CBOE raw values are a local research input and must not be committed or republished in this public repo; record source URL, date coverage, and SHA-256 only.
- Discovery: 2023-10-25 through 2025-03-31.
- Confirmation: 2025-04-01 through 2026-10-21.
- Signal band formula, extreme-volatility regime, first-breach rule, 5-minute manual delay, 30-minute exit, one trade per session, cost ladder, binary decision rules, and all sample gates remain exactly as in the original R331 pre-registration. Only the market-price source changes from QQQ to the target CFD-style index feed.
- This remains a replication window overlapping the published preprint's 2023–2026 OOS range; it is not pristine unseen market history.

## Data retrieval plan

Because no compatible intraday index file is present in the active branch and the connected stock-intraday subscription is not entitled, a dedicated GitHub Actions job is permitted strictly for *raw data acquisition and archival*. It must not compute features, signals, event returns, PnL or strategy verdicts. The analysis and all backtest calculations remain local to the ChatGPT/container session.

## Promotion boundary

A screen pass is only permission to run a separate exact FundedNext feed/contract-cost preflight and a rule-aware two-phase challenge replay. It is not a funded-ready verdict or evidence of a day-179 pass probability.

No R331 price/event/PnL result was calculated when this amendment was written.