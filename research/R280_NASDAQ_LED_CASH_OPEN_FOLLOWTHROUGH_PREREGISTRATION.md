# R280 — Nasdaq-led cash-open breakout follow-through

**Status: PREREGISTERED before calculation.**  
**Parents:** R206 US cash-session opening-range breakout and R276–R279 synchronized breadth-router family. This hypothesis changes event ordering: a US Tech 100 (Nasdaq) opening-range breakout leads and a different index follows in the same direction within a short, fixed time window. It is not another simultaneous 3-of-4 breadth filter.

## Economic hypothesis
The Nasdaq may lead risk sentiment during the US cash open. When it breaks its first 30-minute opening range and another US index subsequently breaks its own opening range in the same direction shortly afterward, the follower may be catching up to a market-wide move. If the follower only breaks much later or in the opposite direction, this hypothesis does not apply.

## Locked universe and signals
- Data: cached Dukascopy M5 BID OHLC snapshots for USA500, USATECH (Nasdaq 100), USA30 and USSC2000. BID-only prices and modeled costs are a screening proxy; not actual broker execution.
- For each New York weekday and each instrument, create exactly one first opening-range breakout signal after the 09:30–09:55 ET range is complete, using completed M5 bars opening 10:00 through 15:45 ET. Opening range must have all six exact bars, at least four non-flat bars and positive width. Up breakout is first close strictly above the OR high; down breakout is first close strictly below the OR low.
- **Leader:** first USATECH / Nasdaq 100 breakout of the day.
- **Follower universe:** USA500, USA30 and USSC2000 only; Nasdaq is not itself a child trade.
- A follower signal is eligible only when its first signal occurs strictly 5 to 30 minutes after the Nasdaq signal (inclusive 5m steps), on the same New York date, with the same direction. There is no tuning of the window after the result.
- When the Nasdaq has no breakout, the follower signal is too early, more than 30 minutes late, or in the opposite direction, the follower signal is not taken by the child. Do not replace either the Nasdaq signal or follower signal with later same-day candidates.
- Exact T+10-minute entry from the follower signal-bar open (M5 bar completion plus another five minutes for manual phone execution); require exact timestamp, non-flat entry, and no same-asset overlap. No nearest-bar substitutions.
- Stop is the follower's opposite opening-range edge; fixed target 2R; stop-first on ambiguous same-bar stop/target; opening gaps through levels exit at the open. If neither stop nor target fires before 16:00 ET, force-flat at the exact 16:00 M5 bar open without inspecting that bar's high/low. Missing exact 16:00 row means skip.
- Costs: modeled 1 and 2 price bps round-trip on BID-only data, converted to R based on initial stop risk. No overnight carry.
- **Matched parent:** same first breakout signals on the three follower instruments with no Nasdaq lead/same-direction/time-window filter, identical T+10 entry, stop, target, costs and same-day-flat exit. This isolates incremental value of lead-lag filtering.

## Periods and locked gates
- Discovery: 2017-01-01 through 2021-12-31.
- Exploratory forward: 2022-01-01 through 2025-12-31; this period is contaminated by prior project research, so it is not a clean final holdout.
- Diagnostic: 2026 through common available source end; this period has also been repeatedly inspected elsewhere in the project.
- Require >=100 child closes in discovery and forward; discovery PF >=1.00 at +2 bps; forward PF >=1.10 at +1 bp and >=1.05 at +2 bps; every forward year with >=5 closes PF >=1.00 at +1 bp; four-week circular bootstrap 95% lower bound for weekly net R at +1 bp >0; and forward mean net R/trade greater than the matched follower parent. If any gate fails, R280=GAGAL. No parameter rescue, no selecting another leader after seeing results.

## Promotion boundary
A screen pass does not establish funded readiness. The index snapshots are BID-only, costs are modeled, and the complete account equity path, floating daily loss, provider contract sizing/fees and Quick Strike are not tested here. No challenge replay occurs merely because this screen is positive.

## Outputs
Store a local runner, compact results, trade ledger and readable report. Calculations are local Python from the cached source artifacts; do not start a new GitHub Actions backtest workflow.
