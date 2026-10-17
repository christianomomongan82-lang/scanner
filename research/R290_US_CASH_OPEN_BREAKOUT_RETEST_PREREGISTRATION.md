# R290 — US Cash-Open Breakout-Retest Continuation (preregistration)

Locked before calculating any R290 signal PnL: 2026-10-17.

## Parent and materially different child
R263's first-confirmed-cross opening-range breakout failed across discovery, validation and forward cost stress. R290 does not retest that same entry rule or adjust its target: it requires a separate pullback/retest after the breakout before entry. The claim is that this confirmation removes first-push failures enough to improve net expectancy despite lower frequency. This is a new locked child, not a rescue of R263.

## Data
- Use only cached R205 M5 BID files from run 38160487617:
- USA500 (usa500idxusd_m5.csv.gz), artifact 11709864394, SHA-256 df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee.
- USATECH (usatechidxusd_m5.csv.gz), artifact 11710370389, SHA-256 82b06c38f66cd1387097691baac1d45c9463b6540eea9dfe28a894d85e122f7c.
- Source latest UTC: 2026-10-09 20:10:00. Data is BID-only; 2/4/6 bp are modeled extra round-trip costs, not observed quotes.
- Convert timestamps to America/New_York with DST. A valid session must contain the full expected cash-session M5 grid 09:30–15:55 (78 bars), valid OHLC and unique timestamps. No synthetic bars. For each index/session, report rejected sessions and reasons.

## Locked signal and execution rules
1. Opening range (OR) is high/low of the three M5 bars starting at 09:30, 09:35 and 09:40 ET.
2. From bars starting 09:45 through 11:00 ET inclusive, find the first candle close above OR high (long breakout) or below OR low (short breakout). Close determines side; if none, no setup that symbol/day.
3. After that breakout bar, wait for a later M5 candle to retest the broken boundary and close back outside in the breakout direction: long retest requires low <= OR high and close > OR high; short retest requires high >= OR low and close < OR low. The first qualifying retest must be confirmed no later than the 12:00 ET bar close. The breakout candle itself cannot double as its own retest.
4. Enter at the next M5 bar open, giving a five-minute manual/alert delay. If a long entry opens at or below OR high, or a short entry opens at or above OR low, skip it rather than assume an unfilled stop-entry. Skip if the opposite OR boundary gives non-positive initial risk distance.
5. Stop is the opposite OR boundary. Target is 1.5 × initial entry-to-stop distance in the trade direction. The trade's R denominator is the initial entry-to-stop distance.
6. At most one trade across both indices per US cash date. Use the earliest retest-confirmation timestamp among eligible symbols. If both qualify on the same timestamp, choose higher breakout excursion divided by OR width; tie-break alphabetically. Do not open a second trade on that date.
7. Begin stop/target inspection at the entry bar. If the open crosses a stop, fill at the open (adverse); if it opens through the target, fill at the open. If stop and target both touch in a single M5 bar, assume stop first. If neither hits, force exit at the close of the 15:55 ET bar (close occurs at 16:00). No overnight position.
8. For each trade, gross return = signed price change / entry price; gross R = signed price change / initial risk distance. Deduct cost stress as 2, 4 and 6 basis points of entry notional per round trip; net R subtracts the same dollar-equivalent cost divided by initial risk distance. Report net-R and net-bps PF, net, win rate, drawdown, trade count, exits, annual distribution and confidence interval. Costs are sensitivities, not actual provider quotes.

## Locked chronological gates
- Discovery: 2016–2020.
- Validation: 2021.
- Do not calculate post-2021 PnL unless every discovery and validation gate passes.
- Discovery gates: at least 300 combined trades; PF in net R >= 1.05 at 2 bp; net R > 0 at 2 bp; at least 3 of 5 years positive at 2 bp; PF in net R >= 0.90 at 4 bp.
- Validation gates: at least 100 trades; PF in net R >= 1.00 and net R > 0 at 2 bp; PF in net R >= 0.80 at 6 bp; four-week circular block-bootstrap 95% CI lower bound for mean weekly net R at 2 bp must be >0 (5,000 resamples, seed 290).
- Any failed gate means binary GAGAL. No OR length, retest window, stop, target, timing, direction, instrument or cost rescue on these same years.
- If all gates pass, 2022–2025 is still contaminated exploratory evidence (the program has already inspected this period in related US-index studies). The R290 report must clearly label that limit. 2026 outcome metrics remain conditional on a separate later decision and are not needed for this locked screen.
- Matched first-breakout-entry R263 figures are contextual only. No pooled post-hoc strategy shopping; the child is judged only on its locked gates.

## Research / promotion boundary
Use local Python/container calculations, not a GitHub Actions backtest workflow. Archive the exact replay runner, quality audit, accepted trade ledger, aggregate result JSON, annual summary and binary verdict. Even a pass is not funded-ready without verified execution-side prices/costs, contract-point value, commission/swap rules, real alert-to-order latency and an equity-aware daily/max-loss challenge replay.
