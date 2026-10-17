# R289 — Continental Europe Cash-Open Gap Continuation: Final Report

**Binary verdict: GAGAL.** Nine of ten preregistered gates passed; the validation weekly-bootstrap lower confidence bound did not. Accordingly, no 2022–2026 PnL was calculated and the candidate is closed without retuning.

## Locked hypothesis and execution
The study tested whether an unusually large 09:00 Europe/Berlin cash-open gap in one of DEUIDXEUR, FRAIDXEUR and EUSIDXEUR tends to continue rather than fill. Each symbol's Q80 absolute gap threshold was fit on 2017–2020 only. The top normalized gap per date was selected deterministically; a position followed the gap direction, entered at the 09:10 M5 open after a five-minute decision/phone-execution delay, targeted one gap-distance and stopped at 0.75 gap-distance. One event maximum per date. Same-bar stop/target overlap was resolved stop-first. Cost stresses of 1/2/4 bp are assumptions, not observed costs.

Preregistration: [locked R289 design](R289_CONTINENTAL_EUROPE_GAP_CONTINUATION_PREREGISTRATION.md), including the timestamp clarification committed before rerunning. Exact replay implementation is archived compressed as [Python runner (.py.gz)](r289_continental_europe_gap_continuation.py.gz).

## Results

| Metric, continuation | Discovery 2017–2020 | Validation 2021 |
|---|---:|---:|
| Trades | 251 | 61 |
| PF in R at 2 bp cost | 1.2245 | 1.1283 |
| Net R at 2 bp cost | +20.682R | +3.088R |
| PF in R at 4 bp cost | 1.1517 | 1.0568 |
| Worst closed-trade drawdown at 2 bp | 7.236R | 5.326R |

Discovery was positive in 3 of 4 years: 2017 -4.759R; 2018 +5.252R; 2019 +3.447R; 2020 +16.742R. The 2020 contribution is large, so aggregate PF alone is not sufficient.

## Why it still fails
The preregistered four-week circular block bootstrap on validation 2021 weekly net R at 2 bp cost estimated a mean of +0.0594R/week, but the 95% interval was **[-0.1767R, +0.2817R]** (52 weekly observations, 5,000 resamples, seed 289). Because the lower bound is not above zero, the robustness gate failed. This leaves material uncertainty about whether the small validation sample has positive expectancy.

Important distinction: validation net R is positive at 2 bp, but validation net notional return is -20.28 bp after the modeled cost. These are different normalizations; the gate was explicitly based on net R, while this discrepancy is another reason not to overstate economic strength.

The same-event fade diagnostic was worse: discovery PF 0.752 / -28.506R and validation PF 0.664 / -10.414R at 2 bp. This side-by-side comparison is diagnostic and does not prove a universally valid continuation edge.

## Data and limitations
Source: R205 cached M5 BID-only index snapshots, latest timestamp 2026-10-09 19:55 UTC. Eligible sessions: DEUIDXEUR 2,481; FRAIDXEUR 2,458; EUSIDXEUR 2,023. EUSIDXEUR had materially weaker coverage in early years because repeated-flat candidate bars failed the preregistered quality filter. All results depend on heuristic exclusion of repeated-flat rows. M5 OHLC cannot establish exact tick-level path ordering. Actual provider spreads/slippage, contract multipliers, commissions and swaps are unverified; no floating-equity challenge path or daily/max-loss replay was run.

**No post-2021 PnL was calculated.** The project has already inspected post-2021 periods elsewhere, so even a successful historical screen would not have created a pristine program-level holdout.

Evolutionary disposition: close R289. Retain only the implementation methods (cash-session validation, frozen threshold fitting, one event per date, stop-first ambiguity, and block-bootstrap gate) rather than promoting this signal as funded-ready.
