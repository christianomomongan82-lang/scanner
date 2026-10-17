# R290 — US Cash-Open Breakout-Retest Continuation: Final Report

**Verdict: GAGAL.** The separately confirmed retest entry did not repair the failed discovery expectancy of the parent opening-range breakout. All post-2021 PnL was withheld because the locked discovery/validation gates failed.

## Locked hypothesis
Unlike R263's entry on the first close beyond the opening range, R290 waits for a later M5 bar to touch the broken boundary and close back outside in the breakout direction. The opening range is the high/low of bars starting 09:30, 09:35 and 09:40 ET; first breakout-close is searched through the 11:00 ET bar. Retest confirmation must finish by 12:00 ET. Entry is the following M5 open, stop is the opposite OR boundary and target is 1.5R. The next-bar entry models a five-minute alert/phone delay. Only one trade total across USA500 and USATECH is allowed per date; same-bar stop/target ambiguity is resolved stop-first. Costs 2/4/6 bp are assumptions, not observed spreads.

Preregistration: [R290 locked rules](R290_US_CASH_OPEN_BREAKOUT_RETEST_PREREGISTRATION.md). Runner: [r290_us_cash_open_breakout_retest.py](r290_us_cash_open_breakout_retest.py).

## Results

| Period | Trades | PF in R at 2 bp | Net R at 2 bp | PF in R at 4 bp | PF in R at 6 bp |
|---|---:|---:|---:|---:|---:|
| Discovery 2016–2020 | 1,059 | 0.834 | −95.595R | 0.732 | 0.644 |
| Validation 2021 | 214 | 1.220 | +20.925R | 1.082 | 0.961 |

Discovery was negative in all five years: 2016 −24.80R; 2017 −30.60R; 2018 −20.70R; 2019 −0.60R; 2020 −18.90R, at 2 bp modeled cost. In validation, the standalone point estimates were positive at 2 bp, but PF dropped below 1 at 6 bp (0.961).

The four-week circular block bootstrap on 2021 weekly net R at 2 bp gave mean +0.402R/week, 95% CI **[−0.111R, +0.884R]** (52 weeks, 5,000 resamples, seed 290). The lower bound crosses zero.

## Failed locked gates
Five gates failed: discovery PF ≥1.05 at 2 bp, positive discovery net R, at least three positive discovery years, discovery PF ≥0.90 at 4 bp, and validation bootstrap lower bound >0. The trade-count gates passed and 2021 point estimates looked positive, but that does not outweigh the broad, repeated discovery losses.

**No 2022–2026 PnL was calculated.** This was not rescued by changing the opening range, retest window, stop, target, entry or instruments. No signal block is promoted from R290.

## Inputs and limits
Source: R205 cached M5 BID-only artifacts, run 38160487617; USA500 artifact 11709864394 and USATECH artifact 11710370389. Latest source timestamp 2026-10-09 20:10 UTC. Complete 09:30–15:55 New York sessions after quality filtering: USA500 2,659; USATECH 2,671. Repeated-flat candidate bars and incomplete sessions were excluded. Actual ask-side fills, CFD point value, spread/slippage, commissions and swaps are not verified; no funded-account floating-equity/daily-loss/max-loss replay was run.

Evolutionary disposition: close R290. Retain only the method of requiring a distinct retest rather than entry on the first break as a reusable hypothesis template—not as a proven alpha component. A further candidate must be a materially different mechanism, pre-registered before its outcomes are calculated.
