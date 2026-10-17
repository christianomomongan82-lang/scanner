# R291 — U.S. Cash-Session Lead → German Index Follow-Through
**Status:** preregistered before scoring candidate PnL  
**Candidate:** R291_TRANSATLANTIC_LEAD_LAG  
**Instrument pair:** USA500IDXUSD (signal) → DEUIDXEUR (target)  
**Data:** cached R205 Dukascopy-node M5 BID-only archives; no new provider and no GitHub Actions backtest

## Hypothesis
A large directional U.S. cash-session move may carry information into the next available German cash-session move because the U.S. market closes after Europe. This is a cross-session lead/lag hypothesis, not an opening-range breakout, cross-sectional residual, or same-session momentum strategy.

## Frozen inputs and provenance
- `usa500idxusd_m5.csv.gz`, SHA-256 `df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee`; cached artifact previously recorded as ID 11709864394.
- `deuidxeur_m5.csv.gz`, SHA-256 `7ad37cb19545eef6111b928a97322c06c9f2478030a0c4282669542262303af4`; extracted from cached R205 artifact `r205-asset-deuidxeur.zip` (archive SHA-256 `0023f09e6697ce5d88a88734b42bd9ad0f676d4b55ba102466efa7e7b01cfaaa`).
- Both files use schema `timestamp,open,high,low,close`. Prices are BID-only, not executable two-sided quotes. All cost rates below are assumptions, not observed broker costs.
- Timezone must be derived with IANA zones `America/New_York` and `Europe/Berlin`, so DST transitions follow the local exchange clock.
- Reject sessions with incomplete/incorrect five-minute timestamps, invalid OHLC, or a repeated-flat placeholder defined as OHLC all equal and close equal to the prior row's close. Never fill missing bars.

## Frozen signal and execution
1. A complete USA500 cash session consists of M5 bar starts 09:30–15:55 New York time (78 bars). Its signed return is last-bar close / first-bar open − 1.
2. Fit one threshold only: the 75th percentile of absolute signed returns from eligible USA500 sessions dated 2017-01-01 through 2020-12-31. Freeze it for all later periods. A signal qualifies when absolute return is at least this threshold; direction is the sign of that return.
3. For each eligible German session date, take the most recent eligible USA500 session with a New York calendar date strictly before that German-local date. Only use it if it is no more than four calendar days old. No same-date U.S. information is permitted.
4. German session eligibility requires every M5 bar start 09:00–15:55 Europe/Berlin (84 bars). If the prior USA500 return qualifies, trade DEUIDXEUR in that direction at the 09:20 bar open. This is a scheduled signal with a ten-minute execution buffer after 09:10 local; it does not depend on future bars.
5. Initial stop is the low of German bars starting 09:00, 09:05, 09:10 and 09:15 for a long, or their high for a short. Skip if entry is at or through the stop, or risk distance is nonpositive. Target is 1.5R from entry. One trade maximum per German session.
6. Starting at the 09:20 entry bar, resolve opening gaps at bar open; otherwise if stop and target are both touched inside one M5 bar, assume the stop occurs first. If neither is reached, exit at the close of the 15:55 bar. No overnight holding.
7. Calculate gross R from BID OHLC proxy prices. Apply modeled round-trip cost sensitivities of 1, 2 and 4 basis points of entry notional, deducted from every trade in R. Because the feed is BID-only, these costs do not certify bid/ask-side fills. Do not claim the costs reproduce live CFD execution.

## Locked periods and gates
- Calibration/Discovery: 2017–2020. Threshold fit and discovery PnL both use this interval, so discovery performance is exploratory.
- Validation: 2021. It has been repeatedly inspected in the broader project and is not an untouched program-level holdout.
- **Do not calculate or inspect 2022–2026 candidate PnL unless all gates below pass.**
- Discovery gates at modeled 2 bp: at least 100 closed trades; PF in net R ≥ 1.05; total net R > 0; at least three of four calendar years have positive net R.
- Cost robustness gate: discovery PF in net R at 4 bp ≥ 0.90.
- Validation gates at modeled 2 bp: at least 50 closed trades; PF in net R ≥ 1.05; net R > 0; and a 4-week circular block bootstrap (5,000 resamples, seed 291) of weekly net R has a 95% percentile CI lower bound strictly above zero.
- Validation cost gate: PF in net R at 4 bp ≥ 0.90.
- Any unmet gate = **GAGAL**. Do not modify the threshold, entry time, direction, stop, target, session, instrument or cost assumption after seeing results. No second pass through 2021 to rescue the candidate.
- If every gate passes, later-period testing must be separately logged as exploratory because the project has repeatedly examined those years. Even a historical pass does not establish funded readiness: a separate broker-quote, latency, stop-gap, equity/DLL/MLL and challenge-duration replay remains mandatory.

## Known limits
BID-only M5 feed, modeled basis-point costs, heuristic flat-candle exclusion, OHLC intrabar sequencing, and no tick-level execution. Current project-level data from 2021 onward are contaminated by earlier research; no period here is a pristine untouched holdout. This is a narrow alpha screen only, not an order to trade or buy a challenge.
