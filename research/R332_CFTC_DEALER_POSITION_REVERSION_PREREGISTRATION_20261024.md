# R332 — CFTC dealer-position shock and four-week FX reversion (pre-registration)

**Date:** 2026-10-24 UTC  
**Status:** REGISTERED BEFORE PRICE-OUTCOME CALCULATION. No R332 return/PnL has been calculated.  
**Claim boundary:** initial falsification screen only; not a funded-ready strategy or a pass-probability estimate.

## Why this is a new mechanism

Prior project failures repeatedly cover candle geometry, price-only momentum/breakout, session-clock effects, failed-break reversals, FX/gold residuals, and short-horizon price-state predictors. R332 instead tests a published intermediary-demand mechanism using publicly released CFTC Traders in Financial Futures (TFF) Dealer/Intermediary positions. The economic claim is that dealer inventory changes absorb currency-selling demand; the currency depreciates around that demand shock and subsequently appreciates modestly. This is an externally motivated hypothesis, not proof that the effect survives modern CFD costs or the project's manual execution delay.

Primary literature: Mai Dao, Pierre-Olivier Gourinchas, and Oleg Itskhoki, “Breaking Parity: Equilibrium Exchange Rates and Currency Premia,” IMF Working Paper 2025/153 (2025-08-01). The paper's empirical horizon is monthly/longer; this screen fixes a 28-calendar-day holding period because the actual project objective has a sub-180-day time constraint. A negative result will close this specific fast-horizon implementation, not claim that the paper's longer-horizon mechanism is universally false.

## Data and causal availability

- Positions: public CFTC TFF Futures-Only data mirrored in the pinned Hugging Face dataset ZipLime/commitments-of-traders, dataset revision 917febb, files data/pit/part-00000.parquet, data/markets/part-00000.parquet, and data/releases/part-00000.parquet. Dataset license is Apache-2.0; source says data are from Tuesday's position snapshot and must be timed to actual publication, not backdated to Tuesday.
- The source's point-in-time table supplies event/report dates, knowledge/publication dates, market mapping, Dealer/Intermediary net positions and open interest. Its README warns that some release times are derived conservatively, corrections to prior weeks cannot all be reconstructed, and some rows are marked non-reconciling. The raw inputs, source commit, schemas, all release flags, and file hashes must be preserved. Any schema/date/mapping deficiency is a DATA/PROCESS failure, never silently repaired.
- Prices: the repository's hash-manifested paired native Dukascopy H1 BID/ASK source for AUDUSD, EURUSD, GBPUSD, NZDUSD, USDCAD, USDCHF and USDJPY, 2017-01-01 through 2025-12-31. These are not guaranteed to equal the FundedNext platform feed.
- Universe is fixed to these seven pairs and their matching CME currency futures only. Map market names/contracts from the frozen source market catalogue, before joining any outcomes. If any currency lacks a unique valid contract mapping, stop the screen rather than substitute a market.
- Use only reports whose dataset knowledge_date is at or before the evaluated timestamp. Keep release_source, release_estimated, knowledge_lag_days, change_reconciles and original event_date; preserve the latest-source revisions as disclosed. No Tuesday-to-Friday look-ahead, no synthetic release time from report date, no same-week backdating.
- Because price years 2021–2025 have appeared in other project research, they are not a pristine project-level holdout. The information source is new to this experiment, but any later screen pass remains historical screening evidence only.

## Frozen signal construction

1. For each of the seven currency futures, order its TFF Dealer/Intermediary rows by actual knowledge_date. For each calendar month, select the latest report that was actually published during that month. Compare month-selected observations; never group by Tuesday event_date as if it were known then.
2. Dealer net = reported Dealer/Intermediary long minus short. Define the published position ratio as dealer net divided by the trailing 12-selected-month mean open interest (the denominator is calculated using information available by that release). Define the signal as the first difference of this ratio versus the preceding month-selected report.
3. If the ratio change is strictly positive, the currency is long against USD for the next four weeks; if strictly negative, it is short against USD. There is no discovery-selected threshold, no parameter grid, no direction flip, and no post-hoc exclusion of currencies. This sign convention follows the paper's interpretation that dealer inventory absorbs the opposite side of client demand; verify formula orientation against the paper and source schema before calculating any price return. A zero change is no-trade.
4. Orientation is fixed: LONG currency versus USD means long AUDUSD/EURUSD/GBPUSD/NZDUSD and short USDCAD/USDCHF/USDJPY; SHORT currency versus USD is the reverse.
5. Signal becomes actionable only at the dataset's actual knowledge_date. Entry is the first exact observed H1 bar open at or after knowledge_date + 5 minutes. This is a conservative H1 execution proxy: it can be later than five minutes and must never be described as an exact five-minute fill. For a long, enter ASK and exit BID; for a short, enter BID and exit ASK.
6. Exit is the first observed H1 bar open at or after exactly 28 calendar days after entry. If an exact price bar cannot be found after a valid, contiguous observed market reopening, skip and report the event with a reason; never forward-fill. Report the actual entry/exit timestamps and realized delay/hold duration.
7. One signal per pair per calendar month; no duplicate entries from several weekly reports. Each signal contributes to the registered equal-notional event screen; cross-pair overlap is clustered by calendar month for inference.

## Frozen cost ladder

- Native, side-correct BID/ASK entry and exit already includes the observed source spread.
- Apply the published FundedNext FX commission ($5 per side per standard lot) converted to a fraction of the actual base-notional market value at entry. Check the applicable official terms before any promotion; do not assume the commission page is an immutable contract.
- Primary friction: +1 pip round-trip adverse slippage and a deliberately adverse 2-pip-equivalent swap proxy per 7 calendar days held.
- Stress friction: +2 pips round-trip adverse slippage and 4 pips-equivalent swap proxy per 7 calendar days.
- Extra slippage and swap are incremental beyond observed source BID/ASK sides. Report gross, source-spread-inclusive, commission-only, primary-net and stress-net outcomes separately. The swap values are proxies, not verified per-symbol FundedNext swap rates.

## Frozen partitions and acceptance gate

- Discovery: 2017-01-01 to 2020-12-31.
- Confirmation: 2021-01-01 to 2023-12-31.
- Diagnostic only: 2024-01-01 to 2025-12-31.
- Minimum eligible completed events: 200 discovery and 100 confirmation after timestamp, mapping and bar checks. Stop before PnL if either fails.
- Primary costs and H1 delayed entries must produce positive cumulative net bps and positive mean net bps in both discovery and confirmation.
- Confirmation must have a four-month circular moving-block-bootstrap 95% lower bound above zero for the monthly equal-notional net-return series (10,000 draws, deterministic seed 33220261024).
- Primary net expectancy must be positive at the registered stress cost; at least 3 of 4 discovery years and at least 2 of 3 confirmation years must be positive. Report per-pair results but do not select a subset after outcomes.
- Record total events, all skips, per-pair and monthly cohorts, holding-time distribution, spread/commission/slippage/swap-proxy contributions, full event ledger and hashes. Exact runner must be executed twice with identical economic outputs before closeout.
- PASS — SCREEN ONLY authorizes a separate target-feasibility review; it does not authorize a funded challenge, because the feed is not FundedNext's exact platform stream and the strategy has not yet been given a bounded-risk stop/position-sizing model and full two-phase account-equity replay.
- Otherwise the frozen implementation is GAGAL. Sample/data failure must be labeled separately from negative expectancy. Do not tune the 28-day horizon, sign, release-month selection, denominator, asset set, costs, or price dates after seeing outcomes.

## Required pre-outcome data gate

Before any prices are matched to a signal, validate the pinned source bytes/hashes; print all relevant position-table columns; verify unique currency market mappings; verify timestamp timezone/UTC semantics; report report-date vs knowledge-date lags; count estimated-release and non-reconciling rows; verify all price BID/ASK rows, duplicates, OHLC validity and gaps; and calculate eligible-event counts by partition. If any expected field is absent or the sample floors fail, do not calculate PnL. Source feasibility and this preregistration do not count as R332 performance evidence.

## Sources

- IMF WP 2025/153: https://www.imf.org/en/publications/wp/issues/2025/08/01/breaking-parity-equilibrium-exchange-rates-and-currency-premia-568656
- Official CFTC COT release schedule: https://www.cftc.gov/MarketReports/CommitmentsofTraders/ReleaseSchedule/index.htm
- Official CFTC explanation and historical data coverage: https://www.cftc.gov/MarketReports/CommitmentsofTraders/AbouttheCOTReports/index.htm
- Pinned point-in-time source dataset and provenance note: https://huggingface.co/datasets/ZipLime/commitments-of-traders/tree/917febb

**No market outcomes or R332 PnL were calculated when this registration was committed.**
