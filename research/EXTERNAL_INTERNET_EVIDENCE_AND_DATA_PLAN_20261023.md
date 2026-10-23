# External Internet Evidence for the <6-Month Funded Challenge Objective

Date: 2026-10-23
Repository branch: `local-backtest/r189-dukascopy-history`

## Decision objective

Find a strategy/process that can pass FundedNext Stellar 2-Step Phase 1 (+8%) and Phase 2 (+5%) within 179 days, without violating the 5% daily or 10% static maximum loss limits, and that can be executed manually from MT5 on a phone with a realistic alert-to-entry delay. A result that only looks profitable in discovery is not a pass.

## External evidence checked on the internet

1. **Official FundedNext Stellar 2-Step page**  
   https://fundednext.com/api-docs/cfds/stellar-2-step  
   States 8% then 5% targets, 5% daily loss, 10% static maximum loss, minimum 5 trading days per phase, no official time limit, and shows a $6K account offer. The project's 179-day deadline is our own acceptance criterion, not a FundedNext rule. Price/promotional code can change and must be checked again before purchase.

2. **Official FundedNext trading objectives / general rules**  
   https://fundednext.com/static/general-rules/cfds/trading-objectives  
   Daily loss includes realized and unrealized P&L, swap, and commission; resets at 00:00 server time. Maximum loss is static from initial balance. Inactivity rule: 60 consecutive days without a trade can deactivate a CFD account. These details must be implemented in the challenge simulator rather than approximated.

3. **HistData.com free historical FX data FAQ**  
   https://www.histdata.com/f-a-q/  
   Provides downloadable CSV historical FX data including M1 and tick data. Its FAQ says bar OHLC is based on Bid prices and explicitly provides no warranty/certification. Therefore it is a possible independent EURUSD price-path cross-check, not an authoritative source for executable Ask, spread, or broker fills. Do not combine it with Dukascopy as if the quotes were interchangeable.

4. **Hsu, Taylor & Wang (2016), “Technical trading: Is it still beating the foreign exchange market?”**  
   https://www.sciencedirect.com/science/article/pii/S0022199616300472  
   Large study across 30 currencies and over 21,000 rules with data-snooping controls and out-of-sample analysis. It found profitability/predictability in some periods, with substantial time variation. This supports testing conditional, time-varying effects rather than assuming a universal rule.

5. **Zarrabi, Snaith & Coakley (2017), “FX technical trading rules can be profitable sometimes!”**  
   https://repository.essex.ac.uk/18805/  
   Examined 7,650 rules with false-discovery controls and transaction costs. Out-of-sample profitable rules appeared over short periods but were not consistently profitable over the full sample. Implication: repeated selection of top discovery results is not sufficient; require frozen confirmation and robustness.

6. **Lim (2026), “Testing Common Forex Trading Strategies: A Null Result” (preprint/empirical note)**  
   https://papers.ssrn.com/sol3/Delivery.cfm/6871118.pdf?abstractid=6871118&mirid=1  
   Reports no tradeable edge from the tested intraday FX prediction and daily momentum/carry approaches after costs and multiple-testing corrections. This is a recent preprint, not a universal proof that all strategies fail; it is a warning against assuming generic FX momentum or ML features create edge.

## How internet data and literature change the research protocol

- Add an **independent-data validation lane** for EURUSD using HistData M1 Bid OHLC, if it can be retrieved and quality-checked. Use it to test signal/path stability only. Rebuild costs from a separate, documented spread model; HistData Bid candles alone cannot validate exact Bid/Ask execution.
- Continue using Dukascopy Bid/Ask data where both sides are available, but independently verify symbol/time coverage, gaps, timestamps, price scales, and bar construction.
- Search public empirical literature for a specific mechanism and pre-register the hypothesis before measuring its P&L. Literature is a hypothesis source, not evidence that the exact implementation is profitable now.
- Preserve a genuinely untouched confirmation period; log every attempted family/configuration and account for multiple testing.
- Rank candidates by **probability of completing both phases by day 179 under realistic execution**, with rule breaches as hard failures. Do not rank by discovery PF or return alone.
- Run funded-rule replay only after exact fills/costs/timezone/DST and daily-reset handling have been tested. Include manual execution delay and adverse slippage.
- Stop or redesign a family when independent confirmation fails; do not keep tweaking it against the same holdout.

## What this internet check does and does not establish

It confirms authoritative rule details and identifies an independent free FX-data source plus relevant empirical studies. It does **not** establish that a new strategy has an edge or that the challenge has been passed. No candidate is promoted to funded-ready by this note alone.
