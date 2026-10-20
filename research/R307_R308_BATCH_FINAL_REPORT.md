# R307/R308 — Weekday Drift & Weekend Carry Batch: Final Report

**Binary verdicts: R307 GAGAL; R308 GAGAL — DATA/SAMPLE.** Both were preregistered before outcome work. Only R307 proceeded to PnL scoring; R308 was stopped at the pre-outcome eligibility gate because the archive did not provide the registered weekly reopening stream. No funded challenge replay was run.

## R307 — Intraday-of-the-week EURUSD drift

### Frozen hypothesis and execution

Motivated by Khademalomoom & Narayan (2020), “Intraday-of-the-week effects: What do the exchange rate data tell us?” (https://www.sciencedirect.com/science/article/pii/S1566014119302031), the frozen sign map was SHORT EURUSD on Monday/Tuesday and LONG on Wednesday/Thursday/Friday, during 08:05–12:00 Europe/London. This published finding is a motivation, not proof the effect exists on this feed.

Entry was at the exact active M5 open at 08:05 London. The only allowed delay stress was 08:10. The stop distance was the median of the prior 20 complete 48-bar local sessions (minimum 15); stop = 1R, no take profit, and time exit at the exact 12:00 open. Longs entered ASK/exited BID; shorts entered BID/exited ASK; stop gaps were filled at the adverse open. Extra friction grid: 0/0.5/1/2 pips per round trip. No overnight positions.

### Data and event coverage

Existing GitHub data-only artifact #11959096102 supplied paired EURUSD M1 BID/ASK. ZIP SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. Both sides had 4,415,493 rows before cutoff; no invalid OHLC rows, timestamp mismatch or negative open/close spreads. The registered flat-fill filter removed 696,795 rows; 3,718,698 active M1 timestamps remained. Exact aggregation created 736,076 complete M5 bars. There were 7,882 gaps longer than five minutes; gaps were not filled. The exclusive 2026-01-01 UTC cutoff was applied before features and events.

The pre-outcome event audit produced 1,028 eligible discovery sessions (2017–2020) and 1,281 validation/diagnostic sessions (2021–2025). These counts were established before PnL was calculated.

### Primary results — 08:05 entry, +1 pip extra cost

| Metric | Discovery 2017–2020 | Validation/diagnostic 2021–2025 |
|---|---:|---:|
| Trades | 1,028 | 1,281 |
| Net R | **-74.49R** | **-53.46R** |
| PF_R | 0.755 | 0.854 |
| Net pips | -2,398.43 | -1,823.15 |
| Max closed-trade DD | 78.07R | 55.04R |

The rule was already negative at **zero added friction**: discovery -41.33R / PF_R 0.855; validation -10.99R / PF_R 0.968. At +0.5 pip, it was -57.91R and -32.23R; at +2 pips, -107.65R and -95.93R. Therefore this is not a strategy that simply needs a cheaper fill.

The 08:10 entry-delay stress at +1 pip was worse: discovery -77.22R / PF_R 0.745; validation -55.76R / PF_R 0.846.

### Stability and inference

At +1 pip, all four discovery years were negative: 2017 -17.99R; 2018 -13.48R; 2019 -18.09R; 2020 -24.92R. In the diagnostic validation period, only 2024 was positive (+4.25R); 2021, 2022, 2023 and 2025 were negative.

The validation weekly bootstrap included all 261 Monday-start weeks from 2021–2025, including one zero-trade week; circular four-week blocks, 10,000 resamples, seed 307. Mean weekly net was **-0.20484R**, with 95% interval **[-0.37108R, -0.03328R]**. Only 0.98% of bootstrap means were positive. This result does not establish a positive statistical edge.

### Registered gate outcome

Two of eight gates passed: input/data integrity and minimum sample sizes. Gates for primary expectancy/PF, +2-pip cost stress, positive discovery-year stability, bootstrap lower bound, delayed-entry stress, and repository-only full reproducibility failed. **R307 = GAGAL.** Do not flip the weekday sign map or tune hours/stops on the same data.

## R308 — Friday-close to Monday-reopen weekend carry

R308 was motivated by an older interbank FX study reporting a Friday-close to Monday-close effect under one definition but not another (Hilliard & Tucker, 1992: https://www.sciencedirect.com/science/article/pii/0378426692900647). Its locked rule required a real observed >=24-hour data gap from a Friday active quote to an active Monday reopen, an exact Friday 21:00 UTC entry, and a delayed executable exit after the reopen.

The pre-outcome audit found 503 complete Friday risk windows, 178 exact Friday 21:00 entry bars, but only **two** qualifying Friday-to-Monday gaps across 2017–2025 (one in discovery and one in validation). The two long gaps occurred around New Year's holiday closures, not as a weekly weekend-reopening series. The registered minimum was 150 validation trades, which could not be met.

**R308 = GAGAL — DATA/SAMPLE before PnL. No R308 trade outcome or performance statistic was calculated.** This is not evidence that weekend carry itself has or lacks an edge. The archive cannot support the registered event definition; do not relax the gap condition or silently reinterpret weekend-active rows as executable market data.

## Challenge implication

No FundedNext challenge replay was run. R307 has negative expectancy even without added cost, and R308 failed its data/sample gate. Neither has a meaningful, defensible estimate of passing both phases in fewer than 180 days.

The user's target remains completing both Stellar 2-Step phases before any loss-rule breach and in **less than 180 calendar days**. Profit factor is diagnostic, not the project objective.

## Reproducibility caveat

Locked preregistrations, pre-outcome summary, final report, compact metrics and scorecards are stored on the GitHub branch. The local runner and full row-level CSV ledgers are identified by SHA-256 in the manifest but have not been verified as decoded row-level files in the repository. Repository-only complete reproduction remains a failed gate; this report does not claim otherwise.
