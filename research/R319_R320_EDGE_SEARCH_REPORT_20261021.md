# R319–R320 — Edge Search and Reproducibility Checkpoint (2026-10-21)

FINAL VERDICT: GAGAL. No strategy in either batch qualifies for a funded challenge. This is a completed negative research result, not a pending candidate.

## Data audit

Source: GitHub Actions data-only artifact 11959096102, run 38697080604. Archive size 67,719,731 bytes; SHA-256 b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e. Paired BID/ASK each have 4,415,493 rows. A strict joint repeated-flat filter removed 696,795 placeholder rows, leaving 3,718,698 paired M1 rows. Exact complete aggregation yielded M5 736,076 bars, M15 240,883, H1 57,191 and H4 12,348. Observed gaps were preserved: 7,882 M5 gaps over five minutes, 5,665 M15 gaps, 3,227 H1 gaps and 2,406 H4 gaps over four hours. No missing timestamps were filled.

Accounting uses ASK for long entries and BID for long exits; BID for short entries and ASK for short exits. Entry requires the exact M5 open 10 minutes after signal close. Primary added round-trip friction is 1 pip on top of observed spread; spread cap 1.2 pips. Stop-target collision is stop-first; stops gap-fill at the worse executable open; targets get no gap improvement. One position per configuration at a time.

## R319 — H1 displacement + M15 pullback continuation

Grid: 54 signal combinations ×18 exit geometries = 972 configurations. Selection on discovery 2016–2018 only required at least 120 trades, positive net R and PF at least 1.05. Eleven configurations met that discovery screen. Zero of those 11 met positive net R and PF at least 1.05 in confirmation 2019–2020; zero met that gate in diagnostic 2021–2025.

Top discovery-selected configuration R319-0555: H1 lookback 12; displacement threshold 3.5× trailing H1 true range; M15 pullback length 2 and magnitude 0.75× prior median M15 TR; stop 1.5× prior median M5 TR; target 1.5R; max hold 240 minutes.

| Period | Trades | Net R (+1 pip extra cost) | PF | Max DD (R) |
|---|---:|---:|---:|---:|
| Discovery 2016–2018 | 163 | +17.038 | 1.208 | 9.810 |
| Confirmation 2019–2020 | 86 | −25.860 | 0.555 | 31.654 |
| Diagnostic 2021–2025 | 270 | −67.757 | 0.632 | 72.946 |

R319-0555 was already −36.809R / PF 0.775 at zero additional friction and −52.283R / PF 0.699 at +0.5 pip in 2021–2025. Costs make performance worse, but do not explain the full failure. R319 = GAGAL. Do not keep tuning this family on the same sample.

## R320 — H4 close-confirmed channel breakout

Slower price-action family chosen to fit multi-minute manual execution delay. Nine signal combinations ×18 exit geometries = 162 configurations. Prior 6/12/24 completed H4 bar channel; break buffer 0/0.1/0.25× prior median H4 TR; stop 1.0/1.5× median H4 TR; target 1.5/2/3R; max hold 24/48/96 hours. Only one configuration met the discovery screen, and zero candidates met the same positive-net/PF gate on confirmation or diagnostic.

Selected R320-0154: channel 24 H4 bars, buffer 0.25× prior median H4 TR, stop 1.5× median H4 TR, target 1.5R, max hold 24 hours.

| Period | Trades | Net R (+1 pip extra cost) | PF | Max DD (R) |
|---|---:|---:|---:|---:|
| Discovery 2016–2018 | 210 | +4.918 | 1.059 | 11.136 |
| Confirmation 2019–2020 | 149 | −5.173 | 0.917 | 11.191 |
| Diagnostic 2021–2025 | 309 | −2.286 | 0.983 | 27.407 |

The discovery result was weak; 2018 was negative, confirmation was negative, and 2021, 2023 and 2024 were negative. Diagnostic 2021–2025 was only +5.677R / PF 1.045 at zero additional friction, failing a realistic execution-cost gate. R320 = GAGAL; no post-hoc session/direction/threshold rescue.

## Audit limits and decision

2019–2025 have already been inspected in previous project experiments, so they are not pristine project-wide OOS. These periods are useful for rejecting the current candidates but cannot prove no strategy can ever work. Protected 2026 outcomes stayed unopened because neither batch passed the pre-2026 gate. Specifications were frozen in each local source before that run's grid calculation, but the source was not separately committed to GitHub before outcomes; do not label these runs formally preregistered.

R319 and R320 runner source is stored as numbered base64 parts under research/archive; restore with restore_r319_r320_runners.sh. The report and compact results below are the durable result record. Runners regenerate full grids, scorecards and ledgers from the pinned raw artifact. These current rounds now have a source, source hash, exact data audit, fixed selection rule, and stored decision record. Earlier R317/R318 still have a separate historical runner/ledger archival gap; do not claim those older runs were retroactively fixed.

FINAL: R319 GAGAL; R320 GAGAL; funded-ready strategy count remains zero. Do not deploy either strategy in a funded challenge.