# R307 — Intraday-of-the-Week FX Drift (LOCKED PREREGISTRATION)

**Locked before any R307 trade PnL.** Candidate type: new weekday-conditioned return mechanism. Related R304 fixed-clock local-hours candidate remains closed and is not retuned.

## Hypothesis and rationale

Khademalomoom & Narayan (2020), “Intraday-of-the-week effects: What do the exchange rate data tell us?” report that currency rates against USD tended to depreciate especially on Mondays/Tuesdays and appreciate on the other weekdays, with statistically significant day-of-week intraday patterns. This external finding is the reason for the sign map, not evidence that it survives for EURUSD on the present broker-like feed. Source: https://www.sciencedirect.com/science/article/pii/S1566014119302031

**Fixed sign map for EURUSD:** SHORT on Monday/Tuesday; LONG on Wednesday/Thursday/Friday. No sign selection by backtest results.

## Rules

- Feed: paired Dukascopy EURUSD M1 BID/ASK, aggregated to exact complete active M5 bars using only five contiguous M1 observations; no forward-fill or synthetic bars.
- Time zone: `Europe/London` with IANA daylight-saving transitions.
- One trade per Monday–Friday local date. Entry at exact 08:05 London M5 open (fixed clock trigger 08:00 plus five-minute manual-compatible delay). If exact active quote missing, skip; no later substitute.
- Exit at exact 12:00 London M5 open. No overnight holding, re-entry, trailing or profit target.
- Risk distance D: median of the prior 20 **complete 48-bar sessions**, each containing every active M5 timestamp from 08:00 through 11:55 London-local, using midpoint session high-low. Require at least 15 prior complete sessions; only prior dates allowed.
- Stop = 1.0D. LONG stop/exit uses BID; SHORT stop/exit uses ASK. A stop-gap fills at the adverse executable open; otherwise at the stop level on first touch. No stop hit means exit at 12:00 executable open without inspecting that bar's high/low.
- Entry-delay stress: shift the entry from 08:05 to exact 08:10 London M5 open, leaving stop distance and 12:00 time exit unchanged. Both paths must be fully contiguous and observed.
- Extra round-trip friction on top of observed BID/ASK: +0, +0.5, +1, +2 pips; primary +1 pip.
- Cutoff: no feature/event/outcome at or after 2026-01-01 UTC. Data window 2016–2025. 2016 is warm-up. Discovery 2017–2020. Validation/diagnostic 2021–2025 is program-contaminated and must not be claimed as pristine OOS.

## Hard gates

All conjunctive: source/execution integrity; at least 200 discovery trades and 250 validation trades; net R>0 and PF_R>=1.05 for both discovery and validation at +1 pip; net R>0 and PF_R>=1.00 in both at +2 pips; >=3/4 discovery years positive at +1 pip; validation circular 4-week block bootstrap (10,000 resamples, seed 307, include every calendar week including zero-trade weeks) 95% lower bound for mean weekly net R >0; validation net R>0 at +1 pip under the 08:10 delayed-entry stress; and complete repository-reproducible runner/config/ledger/output artifacts.

If any gate fails, **GAGAL**, do not retune the sign map, session clock, stop or exit using these years, and do not open any protected period to rescue the rule. Do not run a funded challenge replay unless every strategy gate passes. If strategy gates pass, a separate verified account-equity challenge replay is required for the project objective: both phases completed before a loss-rule breach in fewer than 180 calendar days.

## Output requirements

Commit pre-outcome eligibility audit before calculating PnL; save exact code, input hashes, cost/delay grid, annual scorecard, every trade/skip record, weekly bootstrap input/result, compact JSON and final report. Calculations must run locally in Python. No GitHub Actions backtest.
