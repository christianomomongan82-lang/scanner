# R331 — VXN-banded Nasdaq intraday mean-reversion screen

**Status: REGISTERED; no R331 price/PnL outcome calculated at registration.**
**Date:** 2026-10-23 UTC
**Purpose:** an initial economic falsification screen for a materially different, externally motivated mechanism. A screen pass is not a FundedNext-ready strategy.

## 1. Why this research lead was chosen

A recent, unreviewed preprint, Leander Seeck, *Volatility as a Signal Switch: Regime-dependent Intraday Mean Reversion in Nasdaq-100 Futures* (posted 2026-08-29; https://ssrn.com/abstract=7364204), reports an intraday Nasdaq-100 futures reversion effect after prices breach a daily band based on prior-session close and prior VXN. The band is ±VXN/16 percent, and the abstract reports positive 30-minute-exit Sharpe only at VXN extremes (<20 and >=30), with OOS 2023–2026. This is a reason to attempt an independently specified replication, not proof of an edge in retail CFD execution. It is a preprint, not established peer-reviewed evidence.

The lead is materially different from the project's closed candle/session and generic price-only trend families because it conditions the fade on an external implied-volatility state. The exact FundedNext CFD instrument of interest is USATECHIDXUSD; data availability/fidelity is a separate gate.

## 2. Data source and scope

Initial screen uses QQQ 5-minute stock-market OHLC aggregates as an underlying Nasdaq-100 proxy, plus daily VXN closes derived from CBOE's official VXN series. QQQ is an ETF proxy, not the FundedNext CFD or NQ futures. This screen cannot prove exact USATECHIDXUSD fills, spreads, swap, or funded-account rules.

- VXN source pointer: CBOE daily-history endpoint, https://cdn.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv; a public cache/mirror inspected for coverage is https://github.com/fuxui/vix-vxn/blob/main/data/history.json. The mirror's available VXN observations run from 2023-10-25 through 2026-10-21. Because CBOE index-data terms restrict redistribution, do not commit the raw daily VXN series to this public repository; store source identity, date coverage, request/version details, and hashes in the output manifest instead.
- Price source: Massive historical aggregate bars for QQQ, with source request parameters and coverage diagnostics recorded in the output manifest. Bars are derived from underlying ETF trades, not quoted FundedNext bid/ask.
- Window requested: 2023-10-25 through 2026-10-21, limited to common dates with VXN and valid regular-session price bars.
- Discovery: 2023-10-25 through 2025-03-31.
- Confirmation: 2025-04-01 through 2026-10-21.
- Important contamination note: the external preprint reports an overlapping OOS interval of 2023–2026. Our test is an independent-feed/mechanics replication, not a pristine unseen market holdout and not independent confirmation of the author’s sample.

## 3. Frozen signal mechanics

No grid search, no indicator mutation, no threshold optimization and no selection among instruments are authorized in R331.

1. Define regular session as 09:30–16:00 America/New_York. Use the prior regular session's final QQQ close as the base close for today's band. Use the prior completed VXN daily close only; same-day VXN is never allowed because it would be look-ahead.
2. Daily upper band = prior QQQ regular-session close × (1 + prior VXN close / 1600). Lower band = prior close × (1 − prior VXN close / 1600). This converts VXN/16 into a percentage distance, matching the published preprint's description.
3. Regime eligibility is frozen from prior-session VXN: eligible only if VXN < 20 or VXN >= 30. VXN in [20, 30) is flat/no-trade. The primary result combines both eligible extreme regimes; report each regime's contribution separately, but never choose one after observing outcomes.
4. Starting at 09:30 ET, detect the first completed 5-minute bar whose high reaches/exceeds the upper band or whose low reaches/falls below the lower band. If a bar reaches both bands, skip that session as ambiguous. If price opens beyond a band, mark the signal only after that bar is complete; do not fill retroactively at the band.
5. Only the first qualifying band breach per regular session is eligible. Upper-band breach means fade/short; lower-band breach means fade/long. No second entry if the opposite band is later reached.
6. The signal is only known at the completed breach-bar close. The ideal diagnostic entry is the next 5-minute bar open. The primary manual-latency entry is the first 5-minute bar open occurring 5 additional minutes after that ideal entry. If this entry does not permit an exit exactly 30 minutes later within the regular session, skip it. Report ideal entry only as a diagnostic, not as the user-compatible result.
7. Exit at the 5-minute bar open exactly 30 minutes after the selected entry. No stop/target optimization and no overnight holding in the signal screen. The screen's fixed-horizon return is not by itself a safe funded-trade specification; any positive screen still needs a separately registered bounded-risk and account-rule implementation before funded promotion.
8. For a short, gross return = (entry price − exit price) / entry price. For a long, gross return = (exit price − entry price) / entry price. Do not use intra-bar interpolation. An invalid/missing bar or a session/date alignment failure causes a skip or data/process failure, never a filled-forward bar.

## 4. Frozen cost ladder

The QQQ OHLC feed does not contain the actual FundedNext CFD bid/ask spread. R203's earlier, separate USATECH quote audit reported median spread 1.928 bps and 95th-percentile spread 4.359 bps; these figures motivate sensitivity scenarios but are not assumed to be the same feed/window or today's quote costs.

- 0 bps round-trip: gross diagnostic only.
- 2 bps round-trip: optimistic proxy floor.
- 5 bps round-trip: primary proxy cost, approximately covering the earlier USATECH 95th percentile before any extra manual slippage; not a verified FundedNext quote.
- 10 bps round-trip: stress proxy for wider spread, delay/market movement and slippage.

Subtract the listed fixed round-trip basis-point cost from each event's gross return. Report count, gross mean/median, net mean/median, total net, win rate, profit factor on event returns, and four-week block-bootstrap CI of zero-inclusive weekly net returns. Report slippage/cost sensitivity separately. A screen positive only at 0–2 bps but negative at 5 bps does not qualify.

## 5. Precommitted gates

An eligible event is one complete band-breach, selected entry and valid 30-minute exit. Before outcome scoring, verify data coverage, ET/DST mapping, prior VXN joins, duplicate/missing bars and event uniqueness.

- Minimum sample gate: at least 50 eligible events in each partition after the regime filter. Below this, verdict is GAGAL — SAMPLE/TARGET FEASIBILITY, not proof of negative alpha.
- Primary cost for the decision: 5 bps round-trip, plus the 5-minute manual entry delay.
- PASS — SCREEN ONLY requires all of: positive cumulative net return in both discovery and confirmation; confirmation lower 95% bound of the four-week circular moving-block-bootstrap mean weekly net return above zero; confirmation cumulative net return also positive at 10 bps stress; and the manual-delay result's net mean is positive.
- Otherwise close the frozen specification as GAGAL — ECONOMIC SCREEN. If data/provenance/reproduction fails, use GAGAL — DATA/PROCESS and do not claim an economic verdict.
- No parameter, regime cut, event direction, exit duration, asset, date boundary or cost assumption may be changed after viewing the outcome. No dropping losing months/instruments or testing alternative horizons after a failure.

## 6. Challenge feasibility boundary

This ETF proxy screen cannot be reported as a funded pass probability. A positive screen would only justify a separate pre-registered data/execution preflight on exact USATECHIDXUSD BID/ASK data, with 5-minute entry delay, documented spread/commission/swap, defined stop and position sizing, intrabar floating equity, daily/max-loss rules, Quick Strike/inactivity/day reset/minimum-day rules, and full two-phase replay by day 179. If exact instrument quotes cannot be obtained and modelled, the route remains non-promotable.

## 7. Reproduction

Store the exact QQQ raw-response identifiers/request parameters and hashes, VXN source/mirror URL plus hash (without redistributing the raw source series), full runner source, normalized event/skip ledger, daily/weekly result tables, block-bootstrap seed/results, logs and output hashes. Repeat the same frozen run twice and compare deterministic output hashes before closing. Run calculations locally in the ChatGPT/container environment; do not use GitHub Actions for signal/PnL computation.

**No R331 price, event-return or PnL outcome was calculated when this registration was written.**