# R277 — Same-day-flat version of the synchronized cash-open breadth router

**Status: PREREGISTERED before calculation.**  
**Parent:** R276, synchronized 3-of-4 US cash-open opening-range breakout with exact T+10-minute mobile entry. R276's historical screen was positive, but its positions had a median hold near 18 hours, a 95th percentile above five days, and some holds near 60 days; overnight financing and floating daily-loss effects were not modeled. This child tests an economically motivated exit/holding mutation, not a signal-threshold retune.

## Hypothesis
A regular-session opening-range breakout is primarily an intraday price-discovery event. Forced liquidation at 16:00 America/New_York should reduce overnight/gap/swap exposure and the time during which funded daily-loss rules can be affected by floating P&L.

## Locked rules
- Same four US instruments, same opening range (09:30–09:55 NY), first completed breakout after 10:00 NY, same-direction breadth confirmation from at least 3 of 4 instruments on the exact same M5 timestamp, same stop at the opposite opening-range edge, same fixed 2R target.
- Timestamps label bar-open. Parent delayed and child entry is exact T+10 minutes from signal-bar open (bar completion plus an additional five-minute manual delay). Entries must occur strictly before 16:00 NY; signal bars later than 15:45 NY are ineligible for these delayed streams.
- If stop or target has not triggered before the exact 16:00 NY bar opens, exit at that bar's OPEN, without inspecting that bar's high/low. If the exact 16:00 timestamp is missing, skip the entry for this diagnostic rather than silently extend overnight.
- Stop-first when both stop and target are inside one M5 bar; stop/target gaps use the opening price. No same-instrument overlap. One accepted trade per index/date.
- Parent comparison: unfiltered first-breakout stream with same-day flat at T+10; child: synchronized 3-of-4 breadth router with the same execution and flat time. An ideal T+5 stream is diagnostic only.
- Same cached four-index M5 BID snapshots, same modeled extra round-trip costs of 1 and 2 bps of notional, same risk normalization and period attribution as R276. No interpolation or bar filling.
- Common four-feed coverage is required for every child event. The USSC2000 source begins 2018-08-08, so earlier timestamps cannot qualify.
- Discovery 2017–2021; exploratory forward screen 2022–2025; 2026 diagnostic only. Neither 2022–2025 nor the previously inspected 2026 index data is a clean untouched holdout.

## Locked screen gates
At least 100 closed trades in discovery and exploratory forward; discovery PF >=1.00 at +2 bps; forward PF >=1.10 at +1 bp and >=1.05 at +2 bps; every forward year with >=5 trades must have PF >=1.00 at +1 bp; the four-week circular bootstrap 95% lower bound for forward weekly net R at +1 bp must be above zero; and the child must improve forward mean net R/trade versus the matched T+10 parent. Report hold duration, yearly results, all skipped/missing-close reasons and costs. If any gate fails, R277 = GAGAL; do not rescue by changing the signal or cost rules.

## Promotion boundary
Even if the historical screen gates pass, this does not establish funded readiness. The data are BID-only, costs are modeled, and actual index CFD spread/commission/swaps and official floating-equity loss/Quick Strike mechanics remain unverified. A full rule-aware challenge replay is a separate gate; no such replay is run merely because a screen passes.

## Outputs
Standalone runner, compact JSON and report are stored in the active research branch. Calculations run locally, without a new GitHub Actions backtest workflow.
