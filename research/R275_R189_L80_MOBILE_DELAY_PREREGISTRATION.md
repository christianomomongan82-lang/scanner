# R275 — R189/L80 mobile-delay stress

**Status: PREREGISTERED before local calculation.**  
**Parent:** R189/L80 (the only recent candidate with a positive, but thin and cost-sensitive, 2026 fresh-feed result).  
**Prior cross-feed evidence:** R259 was GAGAL: 2022–2025 failed at +2 pips, the +1-pip weekly bootstrap lower bound crossed zero, and 2022 was negative. This is not an approved edge block.

## Question
Does the locked EURUSD M1 L80 signal survive the user's actual phone workflow: wait for the M1 signal candle to close, then incur five additional minutes before entry? This is a structural execution mutation, not a parameter optimization.

## Locked signal and trade rules
- Reuse R189's unchanged L80 signal logic: 11/12-bar displacement windows; displacement >=15 pips; candle body >=2 pips; late ratio >=0.80; directional consistency >=7; fixed GMT-5 wall clock 03:00–11:59 with hours 06 and 09 excluded; 14-bar de-duplication. Do not search signal thresholds.
- A bar timestamp denotes its opening time. Entry after a completed signal candle plus a five-minute manual delay is at the exact timestamp T+6 minutes. The comparator parent enters at exact T+1 minute. If the exact executable entry timestamp is absent, skip the signal instead of silently entering at a later bar.
- Use actual quote sides: long ASK entry/BID exits; short BID entry/ASK exits. Reject entry spread >1.5 pips.
- Keep R189 exits unchanged: SL 6 pips, TP 18 pips, activate zero-distance trailing after +6 pips favorable excursion, time exit after 60 observed M1 bars. Stops are checked before targets on the same bar; adverse opening gaps fill at the worse executable open.
- No overlapping trades. Exits are processed chronologically. Add per-trade extra-cost stresses of +0.2, +0.5, +1.0 and +2.0 pips.

## Data and known limitation
- Input: GitHub raw-data artifact 11959096102, EURUSD M1 BID/ASK, Dukascopy, requested window 2016-01-01 through 2025-12-31 UTC; archive SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- The collector used Dukascopy's `-fl` option. Before feature creation, conservatively exclude paired timestamps where both BID and ASK OHLC are zero-range, equal the preceding side's close, and follow the preceding row by exactly one minute; preserve all remaining timestamps and gaps. This is a heuristic against synthetic flat-fill rows, not a substitute for a new verified no-flat raw collection. If a result appears positive, it cannot be promoted without that cleaner collection.
- Period cuts are attributed by entry time: discovery 2016–2020, 2021 separately, and exploratory 2022–2025. 2022–2025 is known contaminated by previous research, so it is not a clean final holdout. Do not use the 2026 EURUSD sample to tune this candidate; prior R189 work already inspected it.

## Locked diagnostic gates
To keep the five-minute child for a later challenge-path study, require at least 100 completed trades in 2022–2025, PF >=1.10 at +1 pip and >=1.05 at +2 pips, no year with >=20 trades below PF 1.00 at +1 pip, and a positive lower 95% bound for a four-week circular block bootstrap of weekly net pips at +1 pip. Report parent and child on the same preprocessed rows, including trade frequency and skipped delayed entries. Failure is **GAGAL** for this phone-execution mutation; do not rescue it by changing thresholds. Even a pass is not funded-ready: official rule-aware challenge replay and Quick Strike compliance remain separate gates.

## Expected outputs
Store the standalone local runner, data audit, compact JSON metrics, and compact chronological trade ledger in this repository. The calculations run locally; no new GitHub Actions backtest workflow is used.
