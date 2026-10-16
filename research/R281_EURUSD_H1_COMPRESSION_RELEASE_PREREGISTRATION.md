# R281 — Repair and strict replay of EURUSD H1 compression-release breakout
**Status before calculation: PRE-REGISTERED; results not inspected.**  
**Purpose:** test the previously *untested because of a zero-trade eligibility/coverage failure* R257 H1 compression-release mechanism with a corrected local engine. This is an implementation repair, not a post-loss parameter rescue. The fixed candidate grid and thresholds below are inherited unchanged from R257.

## Hypothesis
A six-hour contraction in the EURUSD H1 range may precede a close-confirmed escape from the prior 12- or 24-hour high/low. This is a volatility-compression/release hypothesis, structurally distinct from cash-open range breakouts, large-candle impulse continuation, and failed-sweep fading.

## Data and provenance
- Input: Dukascopy EURUSD M1 BID/ASK archive collected through dukascopy-node, file `/mnt/data/eurusd_m1_bid_ask.zip` during the local run.
- Requested coverage: 2016-01-01 inclusive through 2026-01-01 exclusive; source archive manifest says DATA_DOWNLOAD_COMPLETE. Strategy calculations use only 2017-01-01 through 2025-12-31. 2026 is not present in this archive and is not used.
- Archive SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- Source feed caveat: collector used `-fl`; paired synthetic-flat candidates are removed with the same conservative heuristic used in R275 (both BID and ASK OHLC flat, each equal to its prior close, and timestamp exactly one minute after prior). This is heuristic, not proof all synthetic bars are removed. Preserve gaps; do not fabricate bars.
- Construct H1 BID and ASK OHLC only from an hour with exactly 60 paired, unique, sequential M1 timestamps after the flat-candidate filter. Drop incomplete hours. Do not bridge missing hours or weekends. All hours are UTC-clock buckets.
- Verify unique timestamps, valid OHLC, BID/ASK alignment, and nonnegative opening spread. Report SHA-256 of the archive and input audit.

## Locked signal and execution rules
1. For each completed H1 candle at index (i), compute the range of the **six immediately preceding valid consecutive H1 candles**: maximum high minus minimum low. Use a six-hour sequence that contains no timestamp gaps.
2. Fit the 20th and 30th percentile thresholds of that six-hour range using only qualifying observations with signal timestamps in 2017-01-01 through 2020-12-31. Thresholds are fixed before evaluating any 2021 selection outcome.
3. A signal is allowed when the preceding six-hour range is at or below the relevant fitted threshold. No other indicators, session filters, or regime filters.
4. Breakout condition is evaluated at the completed signal H1 close:
   - Long: BID close is strictly greater than the maximum BID high of the preceding (N) H1 candles.
   - Short: ASK close is strictly less than the minimum ASK low of the preceding (N) H1 candles.
   - (N) is fixed to 12 or 24. All lookback bars must be exact sequential H1 timestamps.
5. The pre-registered grid is exactly eight configurations: compression quantile (q\in\{0.20,0.30\}), breakout lookback (N\in\{12,24\}), fixed reward:risk (R\in\{1.5,2.0\}). No additional grid points or threshold changes.
6. Entry: next exact H1 bar open; long buys ASK open and short sells BID open. If the next exact hour is absent, skip the signal. There is no manual-phone delay in this test: it is an H1 strategy with entry only after a completed H1 signal and execution at the next H1 open. This is not evidence for M1 latency-sensitive execution.
7. Stop: for a long, signal candle BID low; for a short, signal candle ASK high. If the executable entry is already at/beyond the stop, skip the trade. Target is entry plus/minus (R\) times the absolute entry-to-stop distance. Do not round target or stop beyond native quotes.
8. Trade exits are checked on executable quote sides: long exits use BID OHLC; short exits use ASK OHLC. Process opening gaps first with adverse executable opening fills. If stop and target both lie within a single candle range and neither opening-gap rule resolves the exit, assume stop first. If no stop/target is hit within 24 following H1 bars, close at the executable open of bar (entry+24), if present. No lookahead beyond that point.
9. One open position per configuration; ignore new signals while a trade for that same configuration is open. Configurations are evaluated separately and are not combined. End-boundary trades whose exit falls outside a reporting period are excluded from that period.
10. Stress extra costs on top of observed BID/ASK execution: 0.0, 0.5, 1.0, and 2.0 pips per completed round trip; subtract the cost once from each trade's gross pips.

## Pre-registered periods and selection
- Threshold fitting / discovery diagnostics: 2017-01-01 to 2021-01-01.
- Validation and sole candidate selection: 2021-01-01 to 2022-01-01.
- Gate-conditional exploratory forward screen: 2022-01-01 to 2026-01-01. These years are research-contaminated and cannot count as pristine OOS.
- 2026 XAUUSD M5 holdout is unrelated to this repair and remains unopened.
- Select among the eight configurations using **highest 2021 validation PF at +1 pip**, with tie-breaks by higher mean net pips/trade then higher number of completed validation trades. Configurations with fewer than 50 completed validation trades are ineligible. Do not select based on 2022-2025.
- If no configuration has at least 50 validation trades, mark R281 **GAGAL — minimum validation coverage not met**, and do not interpret any later-period outcome as selection evidence.
- If a configuration is selected, run the fixed screens below on that selected configuration; do not select another if any gate fails.

## Locked gates for continuing to exploratory forward
All must pass for the selected configuration:
1. At least 100 completed discovery trades over 2017-2020.
2. Discovery PF at +1 pip ≥ 1.00.
3. Validation PF at +1 pip ≥ 1.10 and net pips > 0.
4. Validation PF at +2 pips ≥ 1.00.
Only if all four pass, calculate 2022-2025 exploratory forward metrics. Those metrics are a screen, not clean OOS promotion evidence.

## Locked exploratory forward gates
For a forward *screen pass only*: at least 100 completed trades; PF ≥ 1.10 at +1 pip; PF ≥ 1.05 at +2 pips; every calendar year with ≥20 trades has PF ≥1.00 at +1 pip; and 4-week circular block-bootstrap 95% CI for mean weekly net pips at +1 pip has lower bound >0 (10,000 replicates, seed 2812026). Failure of any criterion is a binary **GAGAL**. Passing does not mean funded-ready; a separate challenge-account-path replay and broker cost audit would still be required.

## Required artifacts
Commit the exact local runner, this preregistration, machine-readable results JSON, completed-trade ledger(s) for every evaluated configuration and selected configuration, validation/annual tables, and final report to the active research branch. Document any implementation mismatch with R257. Do not create or dispatch a GitHub Actions backtest workflow.
