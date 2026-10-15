# R263 U.S. Cash-Open Opening-Range Breakout — Preregistration

Date locked: 2026-10-16
Status: locked before calculation. This is one combined candidate hypothesis across two preselected U.S. index CFDs, not a parameter sweep.

## Question
Does a simple cash-open opening-range breakout on USA500 and USATECH show robust forward expectancy and retain it after realistic cost stress and a 5-minute execution delay suitable for phone-based manual execution?

## Data provenance and limitations
- Input: existing GitHub-stored R205 artifacts, extracted locally to /mnt/data/r205_index_data/: usa500idxusd_m5.csv.gz, usatechidxusd_m5.csv.gz.
- Feed: prior stored BID OHLC M5 snapshots, 2016–2026-10-09. These files contain no ASK series, so this screening test cannot reconstruct the exact quoted spread at entry and exit. Never describe the result as a full BID/ASK execution replay.
- Signals use only bars whose timestamps and OHLC exist. Do not synthesize missing bars.
- Trading sessions use America/New_York with DST handled by the timezone database.

## Locked setup
Each instrument is tested with the same rules:
1. Define each U.S. trading date by New York local date.
2. Opening range (OR) is the six M5 candles beginning at 09:30, 09:35, 09:40, 09:45, 09:50 and 09:55 ET. OR high is the maximum high of those candles; OR low is their minimum low. Reject the date if all six range candles are not present or any range candle has a flat OHLC.
3. Search for the first M5 close breakout whose bar begins from 10:00 ET inclusive to 12:00 ET exclusive:
   - Long: previous M5 close <= OR high and current close > OR high.
   - Short: previous M5 close >= OR low and current close < OR low.
   - Use the earliest qualifying direction only; maximum one trade per instrument per trading day.
4. Ideal entry: next available M5 bar open. Delayed-entry sensitivity: one additional M5 bar (+5 minutes) after ideal entry. Reject missing timestamp fills; do not substitute another fill.
5. Stop: opposite opening-range boundary (OR low for a long; OR high for a short). Reject a fill if its stop is not strictly on the risk side of the entry.
6. Target: 1.5R, where R is the entry-to-stop distance.
7. Simulate stop/target on BID M5 OHLC. If stop/target is crossed at open, fill at the open; if both are touched within a bar, use stop-first. Start checking high/low only on the actual entry bar and later bars, never on a bar preceding a delayed fill.
8. Exit at the close of the 15:55 ET candle if neither target nor stop is hit. No overnight holding.
9. Because this artifact is BID-only, do not claim exact spread-adjusted fills. Subtract a pre-registered fixed additional transaction-cost sensitivity of 2, 4 or 6 bps of entry notional from each trade's gross return. The test must show all three. The +4 bps case is the primary decision case; +6 bps is the stress case. These are explicit cost assumptions, not observed quotes from this dataset.

## Fixed partitions and gates
- Discovery: 2016–2020.
- Validation: 2021.
- Forward: 2022–2025.
- Do not run or inspect 2026 OOS as a strategy promotion step unless the locked candidate passes both the forward primary gate and the manual-latency gate.
- Evaluate each instrument separately and the combined portfolio using one equal-notional trade return per completed trade. Do not pick whichever index happens to look best after seeing results.
- Primary forward gate at +4 bps: combined PF >= 1.10, at least 100 combined trades, each instrument PF >= 1.00, and four-week circular moving-block bootstrap 95% confidence interval for mean forward weekly net return excludes zero on the positive side.
- Manual-latency gate: combined forward PF >= 1.10 at +4 bps with +5-minute entry delay, and each instrument forward PF > 0.95 at +4 bps.
- If either gate fails, mark candidate failed and do not tune or run 2026 OOS. A failing result is a valid result.
- Report annual forward stability, trade counts, PF/net return in bps, max trade-equity drawdown, median holding time, exact spread being unavailable, and latency sensitivity at +2/+4/+6 bps.

## Execution boundary
The raw OHLC input comes from GitHub storage; all resampling, signals, fills, costs, PF, drawdown, bootstrap and verdict calculations must run in the local Python/container session. No GitHub Actions backtest. No tuning after result inspection.

## Promotion limitations
Even a passing screen would not establish funded readiness: ASK-side quotes or equivalent verified spread data, broker commission/slippage, real alert-to-order latency, FundedNext daily/max loss calculations, and Quick Strike constraints would need separate verification. This is a BID-only research screen.