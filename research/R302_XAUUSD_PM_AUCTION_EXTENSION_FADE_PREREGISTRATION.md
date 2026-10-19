# R302 — XAUUSD PM Benchmark Pre-Auction Extension Fade — Preregistration

**Registration status: LOCKED BEFORE OUTCOME CALCULATION.** No trade PnL, win/loss, PF, annual result or bootstrap result has been inspected for R302 at commit time.

## Hypothesis and mechanism

The LBMA Gold Price PM auction is scheduled to start at 15:00 London time. A large absolute XAUUSD move into that benchmark window may reflect temporary inventory/hedging pressure that partially reverses once benchmark-related demand is matched. The registered trade fades only unusually large price moves immediately before the expected auction start; this is a testable hypothesis, not an asserted edge. LBMA describes the gold auctions as starting at 10:30 and 15:00 London time (see [LBMA precious-metal prices](https://www.lbma.org.uk/prices-and-data/lbma-precious-metal-prices) and [ICE IBA](https://www.ice.com/iba/lbma-precious-metals)).

This is a new XAU benchmark-event mechanism. It is not a threshold variation of R272–R274, the R297 weekend reopening gap, the R298 Asian-range sweep/reclaim, or R301 cross-asset safe-haven response. It will be closed regardless of outcome; no direction flip or parameter rescue is permitted.

## Frozen signal and execution rules

- **Instrument/feed:** XAUUSD M5 paired Dukascopy BID/ASK OHLC. Use exact shared timestamps. Buy entries use ASK; long exits use BID. Short entries use BID; short exits use ASK.
- **Data artifact:** GitHub Actions artifact #12031270051, collection run #38859918137. ZIP SHA-256: `2cde8338800fd7f4d5d4628512201c16757ef06bd90d51ffdc8ef9bea425ba1a`. BID gzip SHA-256: `b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575`. ASK gzip SHA-256: `b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9`.
- **Protected cutoff:** exclude all rows with timestamp >= 2026-01-01 00:00:00 UTC *before* building features, sessions, signals or outcomes. The 2026 interval may be opened only if every promotion gate below passes, and then only for this single frozen candidate.
- **Session clock:** convert UTC to `Europe/London` with daylight-saving transitions. Candidate date is Monday–Friday with a complete observed 5-minute grid at 14:30, 14:35, 14:40, 14:45, 14:50 and 14:55 London time. Do not synthesize/fill bars. Because a separate historical IBA non-publication calendar is not included in the data archive, this first screen is a scheduled-clock proxy; that limitation must be stated and must be resolved before any held-out promotion.
- **Signal measurement:** on the 14:55 bar, compute the 25-minute move as close of the 14:55 bar minus open of the 14:30 bar. This bar is known at 15:00 London time. Take at most one candidate per London calendar date.
- **Causal threshold:** calculate the 85th percentile of absolute pre-auction moves from the prior 60 valid weekday windows, requiring at least 40 previous observations. Include only observations strictly before the current date. No global full-sample quantile and no threshold tuning.
- **Direction:** if the move is above +Q85, SHORT; if below -Q85, LONG. Otherwise no trade.
- **Entry delay:** enter at the open of the exact shared BID/ASK M5 bar timestamped 14:55 + 10 minutes (15:05 London). Do not shift to a later bar to rescue a missing entry. Entry spread must be <= $1.00/oz and the stop distance must be at least 3 times that observed entry spread.
- **Volatility-sized stop:** use only bars timestamped before 14:55. Calculate each prior bar's true range from BID OHLC; stop distance = 2.0 × median true range of the 24 complete M5 bars immediately before the 14:55 signal bar. No trade if any required bar is missing, stop distance is nonpositive, or stop distance < 3 × entry spread.
- **Target/holding:** stop = 1R; target = 1R; maximum holding = 60 minutes from entry. Time exit at the open of the exact M5 bar timestamped entry + 60 minutes; do not inspect that bar's high/low. Require the entire entry-to-time-exit timestamp grid to be present.
- **Barrier execution:** monitor long stop/target on BID and short stop/target on ASK. If a bar opens through a stop, fill at the adverse opening price. If stop and target are both touched in one bar, stop first. A favorable target gap is capped at the target price. If a required bar is missing, mark the event ineligible before computing its PnL; do not forward-fill or synthesize a quote.
- **Costs:** quote-side spread is already reflected by BID/ASK. Subtract an additional round-trip friction of $0.30/oz in the primary score. Report $0.00 and $0.50/oz cost sensitivities. Net R = (executable-side price PnL − added friction) / initial stop distance.
- **Entry-delay stress:** repeat the frozen signal with entry at signal timestamp + 15 minutes and the same 60-minute max hold measured from the actual entry. No threshold, direction, stop-distance, or target changes.
- **Period split:** 2016 is warm-up only; discovery = 2017–2020; validation = 2021–2025. All 2022–2025 use is already program-contaminated and must not be described as pristine OOS. No candidate outcomes after 2025 are to be calculated unless all pre-2026 promotion gates pass.

## Promotion gates to nominate the one protected 2026 test

All gates are conjunctive; any required failure means **GAGAL**, close the candidate, and do not open 2026.

1. Data integrity: paired timestamps exact; zero duplicate/invalid OHLC rows; no synthetic bars; all feature/entry/exit timestamps causal.
2. At least 100 completed eligible discovery trades and 150 validation trades at the primary cost.
3. Net R > 0 and PF_R >= 1.05 in both discovery and validation at +$0.30/oz.
4. At least 3 of the 5 validation calendar years have positive net R at +$0.30/oz.
5. Validation 4-week circular block bootstrap (10,000 resamples, seed 302; calendar weeks with zero-trade weeks included) has a 95% CI lower bound > 0 for mean weekly net R.
6. Validation net R remains > 0 at +$0.50/oz extra cost.
7. Validation net R remains > 0 with the +15-minute entry-delay stress at +$0.30/oz.
8. Event-path integrity audit reports every skip reason and confirms no stop/target ordering uses future bars.

If all eight gates pass, nominate R302 for the single protected 2026 XAU test only after checking that the official IBA non-publication dates are excluded. Even a held-out price screen pass would not by itself mean FundedNext-ready: actual account-equity, DLL/MLL, fees, swaps, slippage and sequential two-phase target simulation remain separate gates.

## Fixed reporting requirements

Save the exact runner, pre-outcome eligibility audit, full trade ledger, annual and period summaries, weekly bootstrap input/result, compact JSON, final report and updated master ledger/evidence matrix to the active research branch. Report the binary result as **LULUS** or **GAGAL**; do not label a failed strategy as a promising candidate. No GitHub Actions backtest is permitted; all signals/PnL are calculated in local Python.
