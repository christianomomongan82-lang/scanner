# R334 — FX Market Eligibility Audit (preregistered)

**Date locked:** 2026-11-03  
**Status:** PRE-DATA / NO ALPHA TEST / NO STRATEGY PNL  
**Branch:** `research/r334-fx-market-eligibility`  
**Parent:** `research/r333-idx-smallcap-daily`  
**Purpose:** decide whether USDHUF is a sufficiently distinct and realistically tradable research market to justify a later, separately preregistered hypothesis.

## 1. Research question

Does USDHUF offer a materially different and still researchable market microstructure from the project's repeatedly explored EURUSD baseline, while remaining feasible under FundedNext CFD execution costs?

This is a **market eligibility and characterization audit only**. It does not test a trading strategy, does not estimate alpha, and must not be described as evidence that USDHUF is easier to profit from or less efficiently priced.

## 2. Fixed instrument universe

No symbol may be added, dropped, or reordered after inspecting price metrics.

| Order | Role | Dukascopy ID | Reason |
|---:|---|---|---|
| 1 | Primary candidate | `usdhuf` | FundedNext CFD symbol; HUF market is less prominent in public pair-level turnover statistics; dedicated HUF microstructure literature exists |
| 2 | Secondary candidate | `eurnok` | FundedNext CFD symbol; a directly reported low-turnover cross in BIS preliminary 2025 pair table |
| 3 | Liquid emerging-market comparator | `usdzar` | FundedNext CFD symbol; compare a more actively reported EME pair |
| 4 | Major-market baseline | `eurusd` | Benchmark for quote cost, volatility, activity and data quality |

FundedNext's public CFD tradable-assets article dated 2026-04-09 lists USDHUF, EURNOK and USDZAR among symbols available to Stellar CFD accounts. Account-specific availability must still be checked in the actual terminal using Market Watch > Show All before any tradeability claim.

## 3. Data source and locked acquisition scope

- Provider: Dukascopy historical bid/ask candles, accessed only through the project's established `dukascopy-node` acquisition method.
- Downloader version: `dukascopy-node 1.50.0` (fixed for provenance).
- Timeframe: M5.
- Price sides: separate BID and ASK files for every symbol.
- Common start: 2007-03-13 00:00:00 UTC (the latest earliest-start among these four symbols).
- End: 2026-10-31 23:59:59 UTC, subject to the provider's available completed candles.
- No fallback provider, no fabricated bars, no forward-fill, no row-number joins.
- Preserve all missing intervals and record expected-market-hours assumptions.
- Each file must record exact start/end timestamps, row count, bytes, SHA-256, source symbol, side, timeframe and downloader version.

Published Dukascopy instrument pages currently report M5 history from 2007-03-13 for USDHUF, 2004-10-25 for EURNOK, 2003-08-03 for USDZAR and 2003-05-04 for EURUSD. These catalog dates are not accepted as proof that the downloaded caches have complete coverage; actual manifest checks are mandatory.

## 4. Data integrity checks

For each symbol and side:

1. Monotonic timestamps; no duplicate timestamps.
2. OHLC validity: high >= max(open, close), low <= min(open, close), high >= low; all prices finite and positive.
3. BID and ASK timestamps paired exactly before spread calculations.
4. No negative or zero-invalid opening/closing spreads; all anomalous values retained in a separate exception report rather than silently corrected.
5. Report missing M5 bars by month and UTC hour after excluding scheduled FX market closures; do not classify weekend closure as missing data.
6. Do not infer volume from Dukascopy candle volume as centralized market-wide FX turnover.

Any input mismatch or missing required side blocks the corresponding spread analysis. No synthetic replacement is permitted.

## 5. Locked descriptive metrics

Calculate the following on the common observed BID/ASK timestamps. No strategy signals or trade outcomes are permitted in R334.

### Quote-cost burden
- Opening and closing spread: ASK minus BID, retaining price units and converting to pips with explicit instrument pip conventions.
- Median, p75, p90, p95, p99 and maximum spread, overall and by UTC hour/day-of-week.
- Spread-to-range ratios against the same bar's BID range and rolling 1-hour/4-hour realized range. State clearly that M5 OHLC spreads are sampled candle quotes, not tick-level executable spread history.
- Compare each candidate's spread burden to EURUSD; do not compare raw pips across instruments without normalization.

### Market activity and volatility
- M5 observed-bar counts and missing-bar distribution.
- 1-hour and daily realized volatility distributions (median, p75, p90, p95, p99).
- Absolute return tails, gap frequency, and volatility clustering.
- Intraday activity/volatility profile by UTC hour; any local-time profile must state the timezone and DST treatment.
- Rolling correlations to EURUSD using exact timestamps only; report sample coverage alongside every correlation.

### Market differentiation
- Report whether USDHUF's volatility, tail behavior, spread burden and intraday profile differ materially from the baseline and comparators.
- Do not select the best-looking symbol from these metrics and then call it independent validation. This is a screening comparison only.

## 6. Economic and market-structure context — motivation, not alpha evidence

The Hungarian central bank's published research on EURHUF found that customer order-flow effects were nonlinear and varied with volatility regimes. Another MNB study found that foreign customer order flow was informative about EURHUF movements while domestic customers contributed liquidity, but a realistic forecasting exercise did not outperform a random-walk benchmark.

These results motivate studying state-dependence in the HUF market. They do **not** establish the same effect in USDHUF, and Dukascopy bid/ask OHLC does not contain the signed customer order-flow data used by those papers. R334 must not claim to test or reproduce an order-flow edge.

The BIS survey's currency-pair collection reports 47 selected pairs; pairs not separately listed are grouped into “other” and “residual”. USDHUF is not published as an individually measured pair. Do not invent or infer an exact USDHUF turnover number from the residual. Currency-level HUF turnover and EURHUF pair turnover are context only, not USDHUF pair volume.

## 7. FundedNext execution feasibility

The public FundedNext rules specify a fixed forex commission for Stellar 2-Step accounts, while spreads remain variable and symbol-specific. The public symbol page displays fields for bid, ask and spread but the values are dynamically rendered and were not independently captured in this audit.

Therefore:
- Dukascopy spread statistics are historical source-feed characteristics, not FundedNext execution costs.
- FundedNext USDHUF spread, swap long/short, contract size, tick size/value, trading hours and any symbol-specific restrictions must be captured from the actual FundedNext trading terminal before funded-tradability can pass.
- If exact costs cannot be verified, funded-readiness is **GAGAL for the claim being tested**; do not substitute generic/assumed spreads.
- No funded challenge purchase or live-trading recommendation is part of R334.

## 8. Scope boundaries and verdict policy

- R334 is not an alpha test. No PF, win rate, expectancy, strategy trade count, or challenge-pass estimate will be produced.
- R334's market-data eligibility result will be one of: **PASS** (inputs and descriptive audit complete) or **GAGAL** (required data/quotes fail integrity or availability).
- A PASS means only that a later strategy hypothesis may be registered; it does not mean USDHUF is profitable, uncrowded, or funded-ready.
- Any future alpha hypothesis receives a new immutable experiment ID and its own preregistration before outcome calculation.
- All numerical calculations must run locally in the ChatGPT/container session. GitHub Actions, if needed, may perform data acquisition only and must not calculate metrics, signals, PnL or verdicts.
- Store raw-data manifests and acquisition artifacts in the designated data branch; store the local runner, result JSON, diagnostic CSVs and report in this research branch.

## 9. Sources checked before lock

- FundedNext CFD tradable assets (2026-04-09): https://help.fundednext.com/en/articles/8224087-fundednext-tradable-assets-what-can-i-trade-on-fundednext-cfd-accounts
- FundedNext symbol specifications: https://fundednext.com/symbols
- FundedNext general CFD rules: https://fundednext.com/forex-trading-rules
- Dukascopy-node USDHUF: https://www.dukascopy-node.app/instrument/usdhuf
- Dukascopy-node EURNOK: https://www.dukascopy-node.app/instrument/eurnok
- Dukascopy-node USDZAR: https://www.dukascopy-node.app/instrument/usdzar
- Dukascopy-node EURUSD: https://www.dukascopy-node.app/instrument/eurusd
- BIS 2025 Triennial Survey results and pair-aggregation methodology: https://www.bis.org/publications/triennial-central-bank-survey-foreign-exchange-and-over-the-counter-otc-derivatives-markets-2025
- MNB, Foreign Exchange Market handbook (spot-market description): https://www.mnb.hu/letoltes/mnb-oktatasi-fuzetek-7-devizapiac-eng-0309.pdf
- MNB Working Paper 2010/10, nonlinear order-flow relationship in EURHUF: https://www.mnb.hu/en/publications/studies-publications-statistics/working-papers-1-1/wp-2010-10-yuliya-lovcha-alejandro-perez-laborda-is-exchange-rate-customer-order-flow-relationship-linear-evidence-from-the-hungarian-fx-market

**Lock statement:** Instrument universe, source, date window, timeframe, sides, data-quality checks and descriptive metrics are fixed before R334 price-result calculations. No strategy PnL has been inspected or calculated for this screen.
