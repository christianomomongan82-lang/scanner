# R299 — USATECH 30-Minute Impulse Leads USA500: Locked Preregistration

**Status at commit:** hypothesis and gates locked; no R299 candidate PnL has been calculated.  
**Date:** 2026-10-18. This is a new lagged cross-index lead/lag hypothesis; it is not R287/R288's same-time residual trade, R291's prior-session USA500-to-Germany lead/lag, an opening-range breakout, or an overnight carry.

## Hypothesis
A large US technology-index move over the latest 30 minutes during the US cash session predicts a same-direction move in the broad USA500 index over the following 30 minutes. Signal direction is determined exclusively by USATECH; USA500 is the traded instrument.

## Registered inputs and cutoff
- Source: cached M5 BID archives inside `usa500idxusd_m5.zip` and `usatechidxusd_m5.zip`.
- USA500 source ZIP SHA-256: `21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac`.
- USATECH source ZIP SHA-256: `91c7d44b0487e98eeea021712528910475e626bf433220a007629f3005fc66ad`.
- Expected M5 members: `usa500idxusd_m5.csv.gz` and `usatechidxusd_m5.csv.gz`; columns are `timestamp, open, high, low, close` (Unix milliseconds UTC).
- Source feeds are BID-only; quote-side ASK fills cannot be observed. Model round-trip transaction cost at 1, 2, and 4 basis points of USA500 entry price. These are sensitivity assumptions, not broker quotes.
- Read/check the archive SHA and exact timestamp pairing, uniqueness, M5 alignment and OHLC ordering. Do not synthesize candles. A BID bar is active if high > low or open != close; the source impulse's 7 bars and target's trailing-range bars must be active and timestamp-contiguous.
- **Outcome cutoff: 2022-01-01T00:00:00Z.** All observations timestamped 2022 or later must be removed before threshold calibration, signal construction, trade simulation or any performance calculation. No R299 PnL for 2022–2026 unless every registered gate passes.
- Calibration: 2016 calendar year only. Discovery: 2017–2020. Validation: calendar year 2021 only. The validation period is already research-contaminated and is an eligibility screen, not pristine program-level OOS.

## Fixed signal construction
1. Convert timestamps to `America/New_York` and consider only weekday signal bars whose local start time is in `[10:00, 15:00)`. This ensures the delayed entry and 30-minute max hold remain inside cash-session hours.
2. A valid USATECH 30-minute return at signal-bar index i is `USATECH_close[i] / USATECH_close[i-6] - 1`. Both endpoints and all seven intervening 5-minute bars must be active; timestamps must be exactly five minutes apart. The signal is known only at the close of bar i.
3. Freeze the threshold as the empirical 95th percentile of the **absolute** valid 30-minute USATECH percentage returns from eligible signal-time bars in **2016 only**. Do not recalibrate it in discovery or validation. Require at least 1,000 valid calibration windows; otherwise mark the test invalid for insufficient calibration and do not change the percentile.
4. During each later US trading date, select only the **first** eligible signal bar for which the absolute return is greater than or equal to the frozen 2016 threshold. Direction is LONG on positive USATECH return and SHORT on negative. Do not take a second signal that date, even if the first signal later fails execution eligibility.
5. Target USA500's initial risk distance is the arithmetic mean of the six BID high-low ranges from signal timestamp i-5 through i inclusive. All six target bars must be active, contiguous, and closed by the signal decision time. A missing/static bar, nonpositive range, or bad OHLC makes this date ineligible.
6. Simulate the user's manual response delay: enter USA500 at the exact BID open at timestamp i + 10 minutes. Skip if that exact active row is missing. Risk distance R is fixed to the six-bar average range calculated at signal time. LONG stop = entry - R and target = entry + 1.5R; SHORT stop = entry + R and target = entry - 1.5R. No stop/target tuning, trailing, scaling, re-entry, or direction inversion.
7. Walk USA500 M5 bars from the entry timestamp through the exact entry +30-minute time cap. Require every bar active and every timestamp contiguous. Long positions use BID OHLC; shorts are only a BID-proxy approximation. Stop takes priority when stop and target are both touched within one bar. If bar open gaps through a stop or target, fill at the open; otherwise fill at level. If neither is hit, exit at the exact +30-minute bar open. If a path is invalid, skip and record the reason rather than filling a later bar.
8. Only one attempted trade per New York local date. No positions are carried past the cash session. Net trade R at friction bps c is `(direction_sign * (exit - entry) - entry*c/10000) / R`. Score all 1/2/4-bp costs. PF_R is gross positive net-R divided by absolute gross negative net-R at that cost.

## Frozen pass/fail gates
**All listed gates must pass; no averaging.** If calibration is invalid, or any candidate hard gate fails, R299 is GAGAL and no 2022+ PnL is calculated.

- Calibration 2016: at least 1,000 valid windows; frozen Q95 must be finite and positive.
- Discovery 2017–2020 at 2 bp: at least 75 completed trades; positive total net R; PF_R >= 1.05; at least 3 of 4 calendar years positive.
- Discovery 2017–2020 at 4 bp: positive total net R and PF_R >= 0.90.
- Validation 2021 at 2 bp: at least 100 completed trades; positive total net R; PF_R >= 1.05; at least 3 of 4 calendar quarters positive.
- Validation weekly net-R bootstrap at 2 bp: use all 52 Monday-start weeks of 2021, including zero-trade weeks; circular blocks of four weeks, 10,000 resamples, seed 299. The 95% CI lower bound for mean weekly net R must be strictly greater than zero.
- Validation 2021 at 4 bp: positive total net R and PF_R >= 0.90.
- If any gate fails, do not tune the Q95 cutoff, holding interval, stop/target multiple, time window or target instrument on the same sample. Do not test the reverse direction as a rescue.

## Mandatory audit outputs
Commit to `research/`: exact replay runner; final report with calibration, source hashes, cutoffs, eligible signals, skipped events, results at each cost, annual/quarterly breakdown, max closed-trade drawdown, bootstrap CI and explicit gates; compact JSON; complete attempted-signal/skip audit; completed-trade ledger; annual and quarterly summaries; 2021 weekly net-R series; and data manifest. Link all outputs from `R299_INDEX.md` and append the disposition to project checkpoint and evolution/evidence registries.

## Interpretation limits
This is a candidate screen, not a FundedNext-ready claim. The available archives are BID-only, so actual spread/ASK-side fills, slippage, commissions, swaps, contract specs and account equity/DLL/MLL are unverified. Validation 2021 is contaminated by prior US-index research. Even a pass cannot certify alpha; it can only justify a separate untouched test and broker-specific equity-aware challenge replay.
