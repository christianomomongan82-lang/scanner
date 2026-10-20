# R308 — Friday-Close to Monday-Reopen FX Return (LOCKED PREREGISTRATION)

**Locked before any R308 trade PnL.** This is a weekend-carry anomaly test, not a weekend-gap fade. R282's invalid test of a T+10 post-reopen fade remains closed; this rule carries a position from before the weekend and evaluates the executable reopen exit.

## Hypothesis and external rationale

A historical study using 1983–1988 interbank FX data reported positive spot returns from Friday close to Monday close under a trading-day definition, although the conclusion changed under a calendar-day definition. That ambiguity makes this a falsifiable test, not a presumed premium. Source: Hilliard & Tucker (1992), “A note on weekday, intraday, and overnight patterns in the interbank foreign exchange and listed currency options markets”: https://www.sciencedirect.com/science/article/pii/0378426692900647

**Fixed direction: LONG EURUSD** from Friday late session through the first active Monday reopening quote plus a five-minute reaction delay. No short/long selection after seeing the results.

## Rules

- Source: paired Dukascopy EURUSD M1 BID/ASK, cleaned with the registered rule: remove a minute only when both sides' OHLC are flat and equal the prior minute close, with an exact one-minute timestamp step. Do not fill any data gaps.
- Entry: exact active M5 open at 21:00 UTC on Friday. If missing, skip the weekend rather than moving entry time.
- Define reopening as the first active paired M5 bar whose timestamp is at least 24 hours after the most recent observed pre-weekend active M5 bar; require that reopening timestamp's local UTC weekday is Monday. No static/flat rows qualify. Planned exit is the first active paired M5 bar at/after reopening+5 minutes and no later than reopening+20 minutes. If no exact active quote exists, event is ineligible.
- Long enters ASK; long stop/target checks and exit use BID. Entry must have positive spread <=1.5 pips. No second entry per weekend.
- Risk D: median midpoint high-low range from the 12 M5 bars starting 18:00–18:55 UTC on each of the prior 20 complete Fridays, requiring at least 15 complete Friday windows; only prior Fridays qualify. Stop = 1.0D; target = 1.5D.
- Before the pre-weekend gap, check observed M5 bars for stop/target in chronological order; stop-first for same-bar hits. If the first reopening open gaps beyond the stop, fill at the adverse reopening BID open. A favorable target gap is filled at the target, not better than target. After reopening, monitor stops/target only on exact active bars before the registered delayed exit. If no barrier hits, exit at first executable BID close at the delayed exit timestamp; do not inspect the exit bar's high/low.
- Extra costs on top of observed BID/ASK: +0, +0.5, +1, +2 pips per round trip; primary +1 pip. This does not claim actual FundedNext swap/financing is known. A separate positive-swap stress is required for any funded-ready claim.
- Cutoff: no signal, outcome or exit at/after 2026-01-01 UTC. 2016 warm-up only; discovery 2017–2020, validation/diagnostic 2021–2025 is programme-contaminated, not pristine OOS.

## Hard gates

All conjunctive: paired data/active-reopen integrity; at least 100 discovery and 150 validation completed trades; net R>0 and PF_R>=1.05 in both discovery and validation at +1 pip; net R>0 and PF_R>=1.00 at +2 pips in both; >=3/4 discovery years positive; validation 4-week circular block bootstrap (10,000 resamples, seed 308, include zero-trade weeks) 95% lower bound for mean weekly net R >0; positive validation net R under +1 pip plus a predeclared weekend financing stress of -1.0 pip-equivalent per round trip; and complete repository reproduction of runner, exact configs, full trade/skip ledger, weekly inputs and results.

If any gate fails, **GAGAL**, close this exact rule and do not retune the entry clock, exit delay, stop/target or direction on these same dates. No 2026 outcomes may be opened to rescue a failed candidate. A passing signal screen would still require a separate challenge replay that models floating equity, weekend gap-through stops, verified provider swaps/fees, server-day reset, the +8% then +5% phase sequence and probability of completion within <180 calendar days.

## Output requirements

Save preregistration, data/event eligibility audit, runner, trade and skip ledgers, cost grid, annual summaries, weekly bootstrap, JSON and final report to GitHub. Backtest calculations happen locally in Python only; do not use GitHub Actions for the backtest.
