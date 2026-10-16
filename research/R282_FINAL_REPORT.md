# R282 — EURUSD weekend-reopening gap fade

**Binary verdict: GAGAL — data/event coverage gate; alpha was not tested.** The preregistered event detector found only three timestamp gaps matching its Friday-to-Sunday/Monday definition in a decade. All three occur at 00:00 UTC on dates that are holiday/data-gap artifacts rather than the normal Sunday FX reopening, and all three lack the exact +10-minute timestamp required for entry. No trade opened. Per the preregistration, the run stopped before inspecting 2022–2025 outcomes.

## What was tested
The locked hypothesis was to fade a weekly reopening gap toward the previous Friday executable close, enter exactly ten minutes after reopening, set a stop from the first ten-minute range plus 0.5 times the gap, and exit at target, stop, or 48-hour timeout. Costs were registered at +0.5/+1/+2 additional pips beyond observed BID/ASK.

## Data and coverage findings
- Input: Dukascopy EURUSD M1 BID/ASK data-only archive from GitHub artifact 11959096102.
- Archive SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e` (matched expected checksum).
- Requested date range: 2016-01-01 inclusive through 2026-01-01 exclusive.
- After timestamp alignment, OHLC checks, and the preregistered paired-flat heuristic: 3,718,698 paired rows; 696,795 paired flat candidates removed. The source collector used `-fl`; the paired-flat filter is heuristic.
- In the filtered data, only four adjacent-timestamp gaps are >=36 hours. Three match the weekday condition, and all three lack an exact +10-minute entry timestamp. The event audit is archived separately.
- The candidate gaps are 2017-12-29 21:59 -> 2018-01-01 00:00 UTC; 2020-12-25 07:59 -> 2020-12-27 00:00 UTC; and 2023-12-29 21:59 -> 2024-01-01 00:00 UTC. These are not reliable weekly market-reopening event timestamps for the locked entry model. The fourth large gap, 2020-12-31 21:59 -> 2021-01-03 00:00 UTC, fails the previous-Friday weekday condition.

## Results and decision
- Eligible events: 3; events with exact T+10 minute entry: 0; closed trades: 0.
- Discovery gates: fail (0/100 trades); validation gates: fail (0/30 trades).
- No PF is reportable with zero trades. This is **not evidence that weekend gap fading has negative expectancy**; the test never obtained valid entries.
- No 2022–2025 candidate outcomes were calculated, no forward data were opened for this signal, and no funded challenge replay was run.

## Learning retained
This specific event-detection + data/entry execution rule is invalid on the current Dukascopy archive. The dataset does not preserve enough valid reopening timestamps for this hypothesis under a strict exact-minute-delay rule. Do not fix this by relaxing the T+10 gate after seeing zero entries or by pretending the midnight timestamps are weekly opens. A future weekend-gap study would require a separately preregistered, verifiably session-aware source or event definition. **R282 is closed as a data-eligibility failure, not an alpha failure.**

## Reproducibility
- Preregistration: `research/R282_EURUSD_WEEKEND_GAP_FADE_PREREGISTRATION.md`
- Runner: `research/r282_eurusd_weekend_gap_fade.py`
- Machine-readable output: `research/R282_results.json`
- Event-coverage audit: `research/R282_event_coverage_audit.csv`
- No GitHub Actions backtest workflow was created or dispatched.
