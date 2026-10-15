# R265 USA500–USATECH Relative-Value Mean Reversion — Preregistration

Date locked: 2026-10-16
Status: locked before calculation. This is a paired relative-value hypothesis; it is not a directional opening-range or gap-fade variant.

## Research question
When the USA500/USATECH relative-price ratio deviates unusually far from its trailing baseline, does a market-neutral long/short pair revert strongly enough to survive costs and a five-minute execution delay?

## Input and daily data construction
- Use only the existing GitHub-stored BID-only M5 files for USA500 and USATECH. No alternate feed or data endpoint.
- Convert M5 start timestamps to America/New_York using DST-aware timezone handling.
- Build one RTH daily candle only on dates where both indices have all 78 bars beginning 09:30 through 15:55 ET. Daily open is the 09:30 bar open; daily high/low are extrema of the 78 RTH bars; daily close is the 15:55 bar close. Missing bars are not fabricated.
- The pair's relative log-price is log(USATECH daily close / USA500 daily close); the constant scale difference between index price levels cancels in log-ratio changes.

## Locked signal and position rules
1. For each date t, calculate z_t = (current log-ratio close - mean of the previous 60 complete paired-session log-ratios) / sample standard deviation of those same previous 60 ratios. Current date t is excluded from the baseline window; only prior data forms the rolling mean and standard deviation.
2. If flat after session t close and z_t >= +2.0, schedule a pair trade to short USATECH and long USA500 at the next common session open. If z_t <= -2.0, schedule long USATECH and short USA500 at the next common session open. Otherwise no entry. Use only the first signal while flat.
3. Entry uses each leg's 09:30 ET BID M5 open; delayed sensitivity uses each leg's 09:35 ET BID M5 open (+5 minutes). The same delay treatment applies to scheduled exits. If either leg lacks the exact timestamp, skip that fill rather than inventing a price.
4. Exit signal is evaluated at daily close while the pair is held: exit if z_t crosses or reaches zero in the direction of mean reversion, if it moves adverse to the position and reaches absolute z >= 3.0 on the original side, or after 10 completed paired RTH sessions, whichever occurs first. The exit fills at the next common session's 09:30 open (or 09:35 for delayed mode).
5. One pair position at a time. Signals produced while a position is open are ignored; no stacking or reversing from a signal that occurred while occupied.
6. Returns are equal-notional long/short: average the long-leg and short-leg simple returns in basis points. Subtract +2, +4 or +6 bps per trade as the additional round-trip cost per leg / total equal-notional portfolio. Because data are BID-only, these costs are assumptions rather than observed spread-side costs.

## Fixed partitions and promotion gate
- Discovery: 2016–2020; validation: 2021; forward: 2022–2025; 2026 OOS is not considered unless historical forward and latency gates pass.
- Primary gate at +4 bps cost: at least 100 forward pair trades, PF >=1.10, and the four-week circular moving-block bootstrap 95% interval for mean weekly net bps entirely above zero.
- Manual-latency gate: forward PF >=1.10 at +4 bps when both entry and scheduled exit fills are delayed five minutes to 09:35 ET.
- Also report discovery/validation PF, +2/+4/+6 cost stresses, annual forward results, number of pairs, holding sessions, net bps, trade-equity drawdown and bootstrap.
- If validation or forward gate fails, mark the hypothesis failed; do not change z thresholds, lookback, exit z, holding limit, or cost schedule after seeing results.

## Execution boundary and limitations
All signal, position, cost, PF, drawdown, bootstrap and verdict calculations run locally in Python. GitHub Actions is not used for backtesting. The stored snapshots are BID-only; this cannot validate ASK quote-side fills, live commission/slippage, exact gap execution, or funded-provider DLL/MLL and Quick Strike rules. A pass would only qualify the candidate for additional verification, not approve it for funded trading.

## Data-cleaning amendment — 2026-10-16, before final report

The first diagnostic replay exposed a storage artifact: the retained M5 snapshots have timestamp rows throughout Sundays, including 78 flat placeholder candles at 09:30–15:55 ET, and 15 weekday dates with entirely flat RTH placeholders. Those are not U.S. RTH trading sessions even though a simple count-only completeness check would accept them. The unfiltered diagnostic results were discarded and are not used in the final report.

Official data-cleaning rule for the final replay: require a Monday–Friday date, all 78 unique expected RTH M5 timestamps, and a nonzero full-session range for each index. Then intersect the valid dates for both indices. This is a source-data integrity correction, not a change to any signal, entry, exit, cost, or promotion parameter. The final report identifies its use explicitly.