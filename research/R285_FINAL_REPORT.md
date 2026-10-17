# R285 — US500 Turn-of-Month Intraday Seasonality

**Verdict: GAGAL.** The calendar-conditioned long-only intraday stream fails its registered stability and validation gates. The 2022–2025 and 2026 outcome periods were not calculated or inspected.

## Locked hypothesis and data amendment

The hypothesis was that recurring allocation/rebalancing around month boundaries might produce a measurable same-day US500 long drift. Entry is 09:40 ET and exit is the 15:55 ET bar close; no overnight holding is used. Qualifying dates are the first three and final two observed active RTH sessions of each calendar month. The matched parent buys every eligible US500 session with the same entry/exit.

Before calculating PnL, a data-quality audit found the initial rule that invalidated a whole month because of one bad session would leave only 15/48 discovery months and 6/12 validation months. This would have made the sample underpowered. The pre-outcome amendment [R285 DQ1](R285_DQ1_PREOUTCOME_CALENDAR_AMENDMENT.md) ranks dates from all observed active sessions; a selected session that is incomplete/invalid is skipped and never replaced. Strategy direction, date window, timestamps, costs and gates were not changed. The original preregistration is unchanged and archived.

## Results — primary 2 bp modeled round-trip cost

| Stream | Period | Trades | PF | Net bps | Max drawdown bps |
|---|---|---:|---:|---:|---:|
| Turn-of-month candidate | Discovery 2017–2020 | 226 | 1.130 | +785.76 | 1,194.19 |
| All-session matched parent | Discovery 2017–2020 | 979 | 0.985 | -380.59 | 3,621.30 |
| Turn-of-month candidate | Validation 2021 | 58 | 0.632 | -669.02 | 669.02 |
| All-session matched parent | Validation 2021 | 251 | 1.099 | +539.74 | 587.56 |

## Candidate annual results at 2 bp

| Year | Trades | PF | Net bps |
|---|---:|---:|---:|
| 2017 | 55 | 0.816 | -132.96 |
| 2018 | 57 | 0.766 | -502.78 |
| 2019 | 56 | 0.905 | -136.29 |
| 2020 | 58 | 1.883 | +1,557.79 |
| 2021 | 58 | 0.632 | -669.02 |

The positive discovery total is dominated by 2020; only 1 of 4 discovery years was positive. The strategy then underperformed the all-session long baseline badly during 2021, while the baseline remained positive at the primary modeled cost.

## Cost stress and locked gates

| Period | PF at 1 bp | PF at 2 bp | PF at 4 bp |
|---|---:|---:|---:|
| Discovery 2017–2020 | 1.170 | 1.130 | 1.053 |
| Validation 2021 | 0.659 | 0.632 | 0.583 |

PASS: discovery trade count, discovery PF/net at 2 bp, validation sample count, and discovery PF at 4 bp.
FAIL: at least 3/4 positive discovery years (1/4); validation PF at 2 bp and net return; validation PF at 4 bp.

**Final decision: GAGAL.** Do not change the calendar window or direction after seeing results. No later-period outcomes were opened and no funded-challenge replay was run.

## Data quality and execution limitations

- Input: cached GitHub R205 USA500 M5 BID-only snapshot, artifact `11709864394`, ZIP SHA-256 `21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac`; extracted CSV SHA-256 `df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee`.
- Source contains 886,206 rows from 2016-01-04 00:00 UTC to 2026-10-09 20:10 UTC. Session screen: 2,777 active RTH dates, 2,659 quality-eligible dates. Of 650 calendar-selected dates across covered archive, 36 were skipped due to incomplete timestamps or repeated-flat candidates.
- Costs of 1/2/4 bp are assumptions, not measured CFD spreads, commissions, slippage or swaps. BID-only data do not verify executable ASK-side entry/exit.
- This is a signal screen, not a funded-account simulation. The data have prior use in this research program; any passing result on these years would still be exploratory.

## Reproduction artifacts

- Preregistration: [R285_US500_TURN_OF_MONTH_INTRADAY](R285_US500_TURN_OF_MONTH_INTRADAY_PREREGISTRATION.md)
- Pre-outcome data amendment: [R285_DQ1](R285_DQ1_PREOUTCOME_CALENDAR_AMENDMENT.md)
- Machine metrics: [R285 results JSON](R285_results_compact.json)
- Replay source: [r285_us500_tom_intraday.py](r285_us500_tom_intraday.py)
- Candidate ledger: [Candidate trade ledger at 2 bp](R285_candidate_ledger_2bp.csv)
- Matched parent baseline metrics are recorded in the JSON; the archived replay runner reconstructs this baseline.
- Quality audit: [selected-date skip log](R285_selected_session_skips.csv)

Replay runner `r285_us500_tom_intraday.py` is archived and was rerun from the extracted CSV; counts, PF and net bps matched the local result for candidate and parent at all 1/2/4 bp cost levels. The row-level candidate ledger contains all 284 trades through validation 2021. No GitHub Actions backtest was created or dispatched.
