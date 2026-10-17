# R284 — US Index Late-Morning Impulse Continuation

**Verdict: GAGAL.** The locked candidate failed its discovery gates. The validation-year result was slightly positive at the primary modeled cost, but it cannot override a negative 2017–2020 discovery result. Per preregistration, 2022–2025 and 2026 outcomes were not calculated or opened.

## Locked hypothesis and execution

- Candidate: `R284_LATE_MORNING_CROSS_SECTIONAL_CONTINUATION`.
- Per session/instrument, signal return = 11:55 bar close divided by 10:00 bar open minus 1; this close is known at 12:00 New York time.
- Require exact, valid 5-minute bars from 10:00 through 15:55 ET; reject sessions containing repeated-flat OHLC candidate bars and preserve missing-bar gaps. This flat-row test is a conservative heuristic, not proof that all synthetic rows are identified.
- Require at least three eligible instruments on a date. Select the instrument with the largest absolute late-morning return divided by its own discovery-only Q75 threshold. Parent takes every such daily selection; child takes it only if normalized magnitude is at least 1.0.
- Fit Q75 on 2017–2020 only. Enter the 12:05 bar open (T+10 from 11:55 bar open to model close-confirmation plus five-minute manual delay). Stop = 1.0× the 10:00–11:55 full range; target = 1.5× range. Stop-first for same-bar conflicts; adverse open fills through stops; force-flat at the 15:55 bar open without inspecting that bar's high/low.
- M5 BID-only OHLC; 1/2/4 basis-point round-trip costs are modeled stresses, not measured CFD costs. This is not a funded-account replay.

## Primary results (2 bp modeled cost)

| Stream | Segment | Trades | PF | Net R | Max DD R |
|---|---|---:|---:|---:|---:|
| Parent, no magnitude gate | Discovery 2017–2020 | 981 | 0.822 | -47.650 | 53.517 |
| Child, Q75 magnitude gate | Discovery 2017–2020 | 380 | 0.864 | -13.108 | 16.264 |
| Parent, no magnitude gate | Validation 2021 | 251 | 0.941 | -3.266 | 10.064 |
| Child, Q75 magnitude gate | Validation 2021 | 114 | 1.066 | +1.326 | 4.840 |

The child reduces the parent’s discovery loss in absolute R, but remains net-negative; this is not evidence of positive expectancy. Validation has 114 trades and a small positive result, but discovery is negative and the cost stress fails.

### Child annual results at 2 bp

| Year | Trades | PF | Net R |
|---|---:|---:|---:|
| 2017 | 34 | 0.604 | -3.011 |
| 2018 | 116 | 0.998 | -0.051 |
| 2019 | 77 | 0.609 | -6.957 |
| 2020 | 153 | 0.926 | -3.090 |
| 2021 | 114 | 1.066 | +1.326 |

None of the four discovery years was positive.

## Binary gates

- PASS — discovery trade count (380 ≥ 200).
- FAIL — discovery PF at 2 bp (0.864 < 1.05).
- FAIL — discovery net R at 2 bp (-13.108R).
- FAIL — at least two positive discovery years (0 of 4).
- PASS — validation trade count (114 ≥ 50).
- PASS — validation PF at 2 bp (1.066 ≥ 1.00).
- PASS — validation net R at 2 bp (+1.326R).
- FAIL — discovery PF at 4 bp (0.797 < 0.90).
- PASS — validation PF at 4 bp (0.964 ≥ 0.90).

**Final decision: GAGAL.** Do not lower the magnitude threshold, change the window/stop/target, reverse direction, or open later-period outcomes to rescue this exact candidate. No challenge replay was run.

## Data provenance and limitations

Four cached R205 GitHub Actions artifacts were used, with the same M5 BID-only source snapshots referenced in R283:

- USA500 artifact `11709864394`, ZIP SHA-256 `21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac`.
- USATECH artifact `11710370389`, ZIP SHA-256 `91c7d44b0487e98eeea021712528910475e626bf433220a007629f3005fc66ad`.
- USA30 artifact `11710730507`, ZIP SHA-256 `53a54804f0584c69d52f41af08534e00effea66e7cc31872ae0438e7907e0fe6`.
- USSC2000 artifact `11710111254`, ZIP SHA-256 `52216f5623a974dfaa0fb19e3cb28e2b2db589f1c07cef5cc8e5e2b383638872`.

Session counts after exact-window/quality screening: USA500 2,662; USATECH 2,675; USA30 2,672; USSC2000 2,022. Rejections in the 10:00–15:55 window included missing/nonexact bars and repeated-flat candidates (the latter may be synthetic-flat possibilities, not a definitive classification). Q75 thresholds were USA500 0.38935%, USATECH 0.53805%, USA30 0.39004%, USSC2000 0.67862%.

The compact replay engine [r284_late_morning_continuation_replay.py](r284_late_morning_continuation_replay.py) is now archived on this branch and was checked against the full local run: all parent/child trade counts, PFs and net-R totals matched exactly for discovery and validation at 1/2/4 bp. The row-level trade ledger is still local and not archived, so the individual trade list is not yet repository-reproducible. No GitHub Actions backtest workflow was launched. The index data are BID-only and the cost model does not verify actual spreads, commissions, swaps, slippage, point value, or FundedNext equity-path rules.
