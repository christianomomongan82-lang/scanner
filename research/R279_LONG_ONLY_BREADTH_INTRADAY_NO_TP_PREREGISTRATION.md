# R279 — Long-only breadth-confirmed cash-open breakout with close-only exit

**Status: PREREGISTERED before calculation.**  
**Parent:** R278, long-only upper opening-range breakout with 3-of-4 synchronization, 2R target, and same-day liquidation. R278 passed its exploratory-forward PF/stability/bootstrap sub-gates but failed its discovery PF-at-cost gate. R279 changes only the exit payoff shape; the trigger, universe, breadth, entry delay and initial stop are frozen.

## Economic hypothesis
A synchronized broad-market upside breakout may have positive intraday drift on trend days. A fixed 2R cap may truncate large winners; the mutation instead retains the initial opening-range-low stop and exits at the exact 16:00 New York open if the stop has not fired. The position is never held overnight.

## Locked rules
- Four index universe and input snapshots remain USA500, USATECH, USA30 and USSC2000 Dukascopy M5 BID OHLC.
- Opening range: six exact M5 bars opening 09:30–09:55 NY; require all timestamps, at least four non-flat bars and positive range.
- Signal: first completed M5 close strictly above that asset's OR high from 10:00–15:45 NY; no short signals.
- Child requires at least 3 of 4 upper-breakout signals at the exact same M5 timestamp and exact source timestamp coverage for all four instruments.
- Entry exact T+10 minutes after signal-bar open; non-flat bar and exact timestamp required.
- Initial stop at the OR low. **No fixed take-profit.** If stop is not hit first, exit at the exact 16:00 NY bar OPEN; do not inspect that bar's high/low. If close timestamp missing, skip entry.
- Stop-first on ambiguous bars; stop gap exits at the worse opening proxy. No same-instrument overlap.
- Costs are 1 and 2 modeled price basis points per round trip on BID-only data, converted to R by initial stop risk.
- Matched baseline: R278 2R-target stream on the same locked signals and same-day-flat exit. Child removes only the fixed 2R take-profit.

## Locked screen gates
Discovery 2017–2021; exploratory forward 2022–2025; diagnostic 2026. Require >=100 discovery and >=100 forward trades, discovery PF >=1.00 at +2 bps, forward PF >=1.10 at +1 bp and >=1.05 at +2 bps, every forward year with >=5 trades PF >=1.00 at +1 bp, four-week circular bootstrap 95% lower bound >0 at +1 bp, and higher forward mean net R/trade than the matched 2R parent. Any failed gate means R279 = GAGAL. No follow-on target/stop tuning using these outcomes.

## Promotion boundary
Any positive screen is diagnostic only. BID-only data, modeled costs, previously inspected historical intervals, no verified broker swap/commission schedule and no full floating-equity/Quick Strike replay prevent funded-ready claims.

## Outputs
Store the standalone runner, machine-readable result, report and trade ledger outputs in the active research branch. No GitHub Actions calculation workflow is created.
