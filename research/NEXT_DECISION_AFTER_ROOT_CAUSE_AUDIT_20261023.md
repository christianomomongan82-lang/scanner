# Next decision after root-cause audit — 2026-10-23

## Decision

**Do not run R330 as another price-pattern variant. Do not spend money on a challenge yet.** No candidate is currently funded-ready, and the project has no valid estimate of probability of completing both phases by day 179.

The next work unit is a bounded *universe and economic-mechanism reset*, not signal PnL:

1. Inventory instruments and data that can be sourced and traded under the current FundedNext CFD account: currencies, global indices, commodities/metals, crypto and stocks. Official product references:
   - https://fundednext.com/general-rules/cfds/symbols-and-conditions
   - https://help.fundednext.com/en/articles/8224087-fundednext-tradable-assets-what-can-i-trade-on-fundednext-cfd-accounts
2. For each candidate instrument, verify historical BID/ASK coverage, gaps/static rows, actual symbol sizing, commissions, swap, market sessions and spread. Preserve independent data/source hashes; do not silently substitute a data feed or call already inspected periods pristine OOS.
3. Rank a small number of **economically distinct** research directions by (a) external empirical basis, (b) independence from closed price-pattern families, (c) feasibility with five-minute manual entry delay, (d) adequate opportunity count within 179 days, and (e) realistic net risk/reward under FundedNext rules.
4. The first direction to evaluate is a diversified, multi-asset return-persistence/trend hypothesis across genuinely different asset classes—not another seven-pair FX-only portfolio and not a re-tune of R329. Literature documents time-series momentum across equity-index, currency, commodity and bond futures, but this is a reason to test, not proof for retail CFDs: https://doi.org/10.1016/j.jfineco.2011.11.003. Explicitly reject the direction if it cannot plausibly meet the 179-day target or data/cost fidelity is inadequate.
5. Freeze all definitions, universe, sample requirements, costs and selection method before PnL. Do not lower sample gates after looking. If no valid data or sufficient opportunities are available, record a target-feasibility/data failure instead of inventing a negative economic result.
6. Only candidates that pass economic, stability, sample, multiple-testing, cost and execution gates may enter the chronological two-phase FundedNext simulator. Estimate completion/breach/time distributions with dependence-preserving paths; a single backtest or PF cannot prove a pass probability.

## Why this is the chosen reset

The audited history shows repeated failures among EURUSD candle, short-horizon momentum, session/range, sweep/reclaim and related patterns. R317–R320 show discovery winners that did not survive confirmation; R321's 28 price-state/horizon relationships were negative even with zero additional friction; R329's seven-pair FX trend portfolio was negative in confirmation before extra commission/slippage/swap. Repeating those exact families or nearby thresholds has low information value.

FundedNext's published CFD menu is broader than the tested universe: FX, indices, commodities, crypto and stocks are listed, with symbol-specific spread/commission/swap terms. Broadening the universe does not itself guarantee alpha; it creates a way to test whether previously omitted, less-related return sources add genuine diversification and usable opportunity frequency.

## Stop/continue criteria

- **CONTINUE to registered PnL only if:** data/source provenance and executable-side pricing are verified; instrument contracts and cost terms can be modelled credibly; the hypothesis is materially distinct; the sample/frequency rationale is written before outcomes; and its potential return distribution is not obviously too slow for day 179.
- **STOP the candidate before PnL if:** its evidence is only a cosmetic mutation of a closed family, there is no reliable cost/source data, the opportunity rate cannot support the target, or the idea needs unregistered selection across many variants.
- **STOP the funded route for now if:** no candidate survives these gates. That result would mean “no validated route found with current evidence,” not a proof that all trading is impossible. Do not buy a challenge on hope or use higher risk to compensate for missing edge.

## Required verdict vocabulary

- GAGAL — ECONOMIC: preregistered PnL ran and failed economic gates.
- GAGAL — DATA/PROCESS: valid economics could not be evaluated.
- GAGAL — TARGET FEASIBILITY: signal frequency/return capacity cannot plausibly meet day 179.
- GAGAL — CHALLENGE: a valid chronological account replay breaches rules or misses day 179.
- LULUS: only after the frozen candidate completes both phases by day 179 without rule breach under the registered realistic execution model and uncertainty assessment.

This decision does not claim that the next hypothesis will succeed. It replaces unbounded trial-and-error with one bounded, evidence-led research reset and explicit stop criteria.
