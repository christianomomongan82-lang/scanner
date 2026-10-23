# R330 — Multi-asset time-series momentum screen (pre-registration)

**State:** REGISTERED / OUTCOME NOT CALCULATED  
**Registration date:** 2026-10-23 UTC  
**Claim type:** initial economic screen only; not funded-ready evidence  
**Parent/related families:** R258 (single-pair short-horizon FX momentum), R271 (single-market daily breakout), R329 (seven-pair FX-only multi-week time-series momentum).  
**Novelty claim:** same broad persistence mechanism, but this is a fixed, separately declared universe of FundedNext-tradable US stock CFDs and two major crypto CFDs. The purpose is to test whether cross-asset-class variation in equity and crypto price persistence provides an opportunity the earlier FX-only work could not measure. It is not treated as an independent confirmation of R329's economic mechanism.

## 1. Universe frozen before outcomes

Only current FundedNext Stellar tradables for which the connected data source returns a complete history over the declared window:

- Crypto CFDs: BTCUSD, ETHUSD.
- US stock CFDs: AAPL, AMZN, GOOG, MSFT, NVDA, TSLA, AMD, META, BABA, NFLX, INTC, NKE, KO.

SPCX is excluded from this two-year screen because it only recently began public trading and cannot meet the frozen two-year lookback/sample window. Forex, metals (including XAUUSD), and indices are excluded from R330 outcomes: the relevant FX/metal/index history in this project is already contaminated or explicitly protected, and the currently connected index data API reports that index history is not included in the available plan. Do not add instruments after seeing results.

Official FundedNext tradable assets / symbols and current commission page:
- https://fundednext.com/general-rules/cfds/symbols-and-conditions
- https://help.fundednext.com/en/articles/8224087-fundednext-tradable-assets-what-can-i-trade-on-fundednext-cfd-accounts

## 2. Data, date split, and limitations

- Source: Massive daily aggregate OHLC API, split-adjusted stocks (adjusted=true) and BTCUSD/ETHUSD spot trade aggregates; stock bar timestamps are ET-labelled aggregates and crypto bars UTC-labelled aggregates per source API documentation.
- Requested window: 2024-10-23 through 2026-10-22 inclusive.
- Discovery: 2024-10-23 through 2025-10-22.
- Confirmation: 2025-10-23 through 2026-10-22.
- No result is scored before the raw source rows, request parameters, full symbol universe, cleaning rules, and this registration are archived.
- The source is not FundedNext's own BID/ASK archive. Stock/crypto daily OHLC is derived from the underlying traded market, not the precise broker CFD execution quote. This screen cannot prove exact broker fills, actual five-minute execution, spread, swap, or challenge pass probability. A positive result may advance only to a quote/execution feasibility gate, not to funded promotion.
- The available data coverage is only about two years; one year per partition is insufficient for a claim of long-run robustness. Do not call the confirmation a pristine, multi-regime out-of-sample result.

## 3. Frozen signal and portfolio construction

No grid or parameter search is authorized in R330.

At each completed Friday-labelled daily bar, for every instrument with at least 21 prior complete observations:
1. Compute simple 20-observation momentum: mom20 = close[t] / close[t-20] - 1.
2. Compute daily close-to-close returns from observed consecutive bars only. Estimate trailing 20-observation volatility using the population standard deviation of those daily returns, then multiply by sqrt(20) to obtain a 20-observation volatility scale.
3. Define score = mom20 / vol20.
4. Set direction to +1 when score >= +1.0, -1 when score <= -1.0, otherwise 0 (flat).
5. At the weekly rebalance, weight active positions proportional to 1 / stdev20 and normalize so the sum of absolute notional weights is 1.0 NAV (100% gross exposure). No active position means cash. The universe/threshold/holding interval cannot be changed after outcomes.

For the initial daily-data screen only, measure forward return over seven calendar days from the signal bar close to the last available close in the following [t+6 days, t+7 days] window. A known market holiday can therefore use the prior active close; never fill a missing bar. Rebalance at weekly signal snapshots; calculate turnover from changes in weights, charging both closing/opening orders as actual absolute weight changes.

This forward close-to-close screen approximates signal persistence; it is not a fill-exact test. No intraday stop path or intraday PnL is inferred from daily bars.

## 4. Cost assumptions frozen before outcomes

FundedNext currently publishes Stellar 1-Step / 2-Step commissions of 0.004% per side for stocks and 0.04% per side for crypto. R330 uses those as commission inputs only, with a declared sensitivity for additional unobserved spread/slippage:

- Stocks: 0 bp per side (commission-only floor), +5 bp per side (primary proxy), +10 bp per side (stress).
- Crypto: 0 bp per side (commission-only floor), +15 bp per side (primary proxy), +30 bp per side (stress).

These additional spread/slippage figures are explicit sensitivity assumptions, not claims about FundedNext's actual instrument spreads. No symbol-specific swap deduction is included at this screening stage because it is not yet verified; consequently, a candidate cannot be promoted unless the exact symbol swap/financing costs are subsequently obtained and tested. The primary outcome is net of published commission and primary spread/slippage proxy; the full cost ladder must be reported.

## 5. Outcome rules fixed before calculation

Report discovery and confirmation separately:
- Eligible weekly snapshots and forward-return coverage.
- Gross portfolio return, commission-only return, primary-proxy net return, stress net return.
- Cumulative return, weekly mean/median, win-week rate, profit factor of positive versus negative weekly contributions, max drawdown, annualized weekly Sharpe as a descriptive statistic, turnover, and per-asset/asset-class contribution.
- A deterministic 4-week block bootstrap of weekly net returns with at least 10,000 resamples and a fixed recorded seed. Because the sample is short and regimes are not independent, this is a diagnostic interval, not proof of a known population distribution.
- No parameter tuning and no claims of statistical significance from the two-year screen alone.

### Binary R330 verdict

- GAGAL — ECONOMIC SCREEN: primary-proxy net return is not positive in confirmation, or confirmation's block-bootstrap lower 95% bound is not above zero. This closes the frozen R330 rule; no rescue parameter variants.
- GAGAL — DATA/PROCESS: the source archive, input hashes, exact runner, or result reproduction cannot be verified; do not treat it as a market-alpha conclusion.
- PASS — SCREEN ONLY: primary-proxy net confirmation is positive and lower 95% block-bootstrap bound is above zero, with positive discovery and stress-test survival. This is only permission to conduct a separate exact-feed execution/financing preflight; it is not funded-ready.
- GAGAL — TARGET FEASIBILITY: opportunity frequency or achievable account-path return cannot plausibly meet the day-179 target after rule-aware simulation.

No challenge account should be purchased or started based on an R330 screen result. The 8%/5% phase targets, 5% daily loss and 10% static max loss must later be tested with the exact chronological two-phase simulator and realistic broker execution terms.

## 6. Reproduction contract

- Archive each original API CSV response as immutable data files on the project branch.
- Record API endpoint, requested date range, stock adjustment flag, source timestamp conventions, row counts, min/max timestamps, and SHA-256 for every raw file.
- Save a complete exact Python runner, dependency versions, one-command invocation, normalized input manifest, full weekly portfolio ledger, per-asset signal/skip ledger, scorecard, block bootstrap, logs and SHA-256 output manifest.
- Run the exact archived runner twice from clean inputs and compare deterministic hashes before closing.
- Only then update the master ledger and PROJECT_STATE.md with the R330 result and its proper verdict class.

No PnL was calculated when this registration was written.
