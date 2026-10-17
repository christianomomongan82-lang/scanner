# Evolutionary Block Registry — 2026-10-16

Purpose: preserve what evidence supports, rejects, or has not tested. A useful execution component is not automatically an alpha component. Do not re-import a failed signal under a new name or optimize on a previously inspected segment.

## Reusable implementation / execution controls (not edge)

- **Quote-side accounting:** buy at ASK, sell/short at BID, and monitor long exits on BID / short exits on ASK. Preserve actual BID/ASK OHLC.
- **Data integrity:** verify provenance manifest and SHA-256, match timestamps one-to-one, detect nonpositive/negative spreads, and retain real missing-bar gaps instead of filling flat synthetic bars.
- **Manual-phone execution proxy:** signal bar opens at T; candle decision at T+5m; first executable entry is T+10m if both intervening M5 bars are exactly five minutes apart. Skip entries where the delay crosses the stop/target.
- **Intrabar/cutoff controls:** stop-first on same-bar SL/TP conflicts, adverse opening fill through stop, never inspect high/low later in the exact 16:45 New York bar when flattening at its open, no overnight exposure in these XAU M5 tests.
- These controls passed local smoke checks; they do not imply a positive trading edge. Actual FundedNext costs and challenge loss-rule mechanics remain incompletely verified.

## Signal / context blocks

| Block | Parent experiment | Evidence | Classification / disposition |
|---|---|---|---|
| Asia-session ER continuation gate ER >= 0.30 | R270-A | Maximum observed Asia ER 0.2101; zero trades | Structurally unreachable in tested data; do not lower threshold post-result |
| Asia outer-quartile balanced fade | R270-B | 290 discovery / 68 validation / 219 diagnostic-forward trades; net negative, forward bootstrap CI entirely negative | Failed for this exact instrument/time/session specification |
| Daily 20-session close-confirmed breakout | R271 | 57 discovery / 14 validation / 55 forward trades at +1 pip; all aggregates negative; validation under-sampled | Failed exact rule; no evidence to promote |
| H1 range-compression breakout | R257 | All candidate configurations had zero validation trades due grid coverage/eligibility checks | Implementation/data coverage failure; alpha not established or falsified |
| 24h/120h multihorizon momentum | R258 | Forward 2022–2025 PF 0.785 at +1 pip, net -3,848 pips; all four years negative | Failed; no parameter rescue |
| R272-A 12h displacement + six-bar pullback/reclaim + ER >= 0.45 | R272 | 972 raw triggers overall; maximum trigger ER 0.3249; zero signal overlap with gate | Structurally incompatible; no trades; do not retune R272 |
| R272-B 12h failed-excursion fade | R272 | 944 discovery trades -437.47R / PF 0.525; 957 validation -401.22R / PF 0.548 at +$0.30/oz; negative even at zero extra cost | Failed exact fade; don't reuse as an edge block |
| Directionally aligned 6h/12h continuation mutation | R273 | 131 discovery -78.12R; 278 validation -128.86R at +$0.30/oz; 4-week bootstrap CI below zero | Relative reduction in losses vs raw A, still negative; reject exact child and don't treat as proven block |
| M5 expansion impulse follow-through | R274 | 974 discovery -655.94R; 997 validation -430.65R at +$0.30/oz; zero-extra-cost results also negative; 0/5 validation years positive | Failed exact family/specification |
| M1 displacement / directional-consistency micro-pattern | R189 | Limited 2026 OOS looked positive (55 trades, PF 1.484 at +0.2 pip), but sample is small; phone execution delay and historical reproduction gaps remain | Unconfirmed lead only, not a bankable edge; require independent audit, no automatic parameter revival |

## Current evidence-weighted conclusion

- No signal block in the latest R270–R274 group is edge-backed for funded promotion.
- Do not carry the R272-B fade or R274 large-candle trigger into a composite: both lost before extra cost.
- R273's 28.68R validation improvement versus its raw-A ablation is only relative; the child still lost 128.86R.
- The current blocker is not a lack of trade frequency: R272/R273/R274 generated hundreds to thousands of trades with negative expectancy. Higher risk and extra trades cannot repair this.
- The next useful search should change instrument/family coverage and perform controlled component ablations; it should not continue threshold-tweaking a losing XAUUSD M5 trigger. Keep the final untouched holdout unopened until historical gates pass.

## Artifacts

- [R270 results](R270_SESSION_REGIME_ROUTER_RESULTS.md)
- [R271 results](R271_DAILY_TREND_BREAKOUT_RESULTS.md)
- [R272 result](R272_FINAL_VERDICT.md)
- [R273 result](R273_FINAL_REPORT.md)
- [R274 result](R274_FINAL_REPORT.md)

## R275 update (2026-10-17)

- **Execution controls retained:** require the exact post-delay timestamp, use executable quote sides, process opening gaps before intrabar ranges, and preserve data gaps.
- **No alpha component inherited:** the L80 signal is unconfirmed and the five-minute-delay child is GAGAL. The observed 2022–2025 interval is contaminated and source rows used a heuristic filter after a collector configured with synthetic flats; keep this as a negative diagnostic only.
- **Candidate row:**

| R275 L80 + phone-delay T+6 | R189/L80 | The unchanged L80 trigger became strongly negative with exact T+6 entry: 701 exploratory 2022–2025 trades, PF 0.694 and -786.3 pips at +1 pip; four-week bootstrap CI wholly negative | Failed execution-mutant; do not promote L80 or the T+6 stream as an edge |

## R276–R279 update (2026-10-17)

| Block / candidate | Evidence | Disposition |
|---|---|---|
| R276 synchronized 3-of-4 US cash-open breakout, two-sided, T+10, 2R | Historical statistical gates passed: 767 discovery trades / PF 1.138 at +2 bp; 828 exploratory-forward trades / PF 1.257 at +2 bp; bootstrap lower bound above zero. But diagnostic 2026 PF@+1 bp = 0.748 / −19.38R, total forward R below parent, and median/p95 holds 17.83h/124.63h with max ≈60 days. Challenge replay, swap and floating-loss checks absent. | **Not promoted.** A conditional screen result is not funded-ready evidence. |
| R277 same-day-flat two-sided router | Discovery PF@+2 bp 0.989; 2024 annual PF@+1 bp 0.794; four-week bootstrap 95% CI [−0.116, +0.793] R/week. | **GAGAL.** Session-flat fixed holding duration but failed three gates. |
| R278 long-only upper-breakout router | Forward PF@+1/+2 bp = 1.403/1.346 and bootstrap lower CI >0, but discovery PF@+2 bp = 0.889; diagnostic 2026 PF@+1 bp = 0.877. | **GAGAL.** Do not select/promote based on contaminated forward alone. |
| R279 R278 with no fixed target | Discovery PF@+2 bp = 0.873. Versus the R278 sibling, forward net fell from +69.10R to +67.80R; PF@+1 bp fell 1.403→1.395 and max DD rose 17.26R→17.99R. | **GAGAL.** Removing fixed TP has no supporting incremental contribution. |

Reusable implementation controls: exact M5 timestamps for phone latency; synchronized event-time coverage across all four instruments; session-close execution at the exact 16:00 New York open without peeking at that bar's range; exit-time attribution for weekly bootstrap; and trade-return drawdown sorted by realized exit order. These are simulator controls, not alpha blocks.

Data limitations remain: BID-only index snapshots, modeled 1/2 bps costs, USA Small Cap history only from 2018-08-08, and no verified CFD commissions/swaps/contract multipliers. Full row-level ledgers and local runner sources for R276–R279 are not committed to GitHub yet; reports and compact JSONs are stored, so full repository-only reproducibility remains incomplete.

## R280 update (2026-10-17)

| Candidate | Evidence | Disposition |
|---|---|---|
| R280 Nasdaq-led US cash-open follower breakout | 437 discovery trades / PF 0.875 at +2 bp; 426 exploratory-forward trades / PF 1.109 at +2 bp; PF@+1 bp 1.169 but 2023 and 2024 cohorts negative; four-week bootstrap 95% CI [−0.116, +0.381] R/week; diagnostic 2026 PF@+1 bp 0.744. | **GAGAL.** Timing filter increases mean R/trade versus matched followers but reduces total forward net R from +108.76R to +27.89R and fails discovery, annual and bootstrap gates. Do not carry this as alpha. |

R280 keeps the exact T+10 phone-execution assumption, same-day flat, quote-source timestamps and matched parent. Reusable control lessons are not edge evidence. Do not threshold-tune the 5–30-minute lag after this result.



## R281 update (2026-10-17) — EURUSD H1 compression-release replay: GAGAL

- Preregistration: [R281 locked design](research/R281_EURUSD_H1_COMPRESSION_RELEASE_PREREGISTRATION.md)
- Runner: [local replay source](research/r281_eurusd_h1_compression_release.py)
- Results: [compact machine-readable result](research/R281_results_compact.json) · [candidate grid CSV](research/R281_grid_summary.csv) · [final report](research/R281_FINAL_REPORT.md)
- R281 repairs the R257 eligibility/coverage implementation failure using strict H1 bars resampled from Dukascopy M1 BID/ASK. This is a same-family corrected replay, not a byte-for-byte reconstruction of R257's original H1 archive. The fixed grid remains Q20/Q30 × 12/24-bar breakout lookback × 1.5R/2R.
- Data: 57,191 complete H1 bars from 2016-01-03 through 2025-12-31 UTC. Input archive SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. The source collector used `-fl`; removal of 696,795 paired flat candidates is heuristic, so no future positive result could be promoted without verified no-flat source history.
- Fitted six-hour-range cutoffs on 2017-2020: Q20 = 20.8 pips; Q30 = 25.0 pips.
- All eight configurations lost in discovery at +1 pip (PF range 0.575-0.667; 88-392 trades). The best 2021 validation count was 10, below the preregistered 50-trade eligibility gate. Q20/B12 had a validation PF above 2 but only four trades and failed discovery PF; it is not a candidate.
- **Verdict: GAGAL.** Per the preregistration, the engine did not calculate/inspect 2022-2025 candidate outcomes. No candidate selection, no holdout opened, and no edge block retained.
- The compact metrics/summary and runner are in GitHub. Row-level per-configuration ledgers were generated locally but are not yet archived in the repository, so repository-only reproducibility remains incomplete. No GitHub Actions backtest was created or dispatched.

Reusable learning: correct R257's implementation failure so it no longer hides possible triggers, but do not infer alpha from raw trade availability. This fixed compression-release specification is now closed; do not loosen its thresholds based on the failed result.


## R282 update (2026-10-17) — EURUSD weekend-reopening gap fade: GAGAL / DATA COVERAGE

- Preregistration: [R282 locked design](research/R282_EURUSD_WEEKEND_GAP_FADE_PREREGISTRATION.md)
- Runner: [local R282 runner](research/r282_eurusd_weekend_gap_fade.py)
- Results: [final report](research/R282_FINAL_REPORT.md) · [results JSON](research/R282_results.json) · [timestamp coverage audit](research/R282_event_coverage_audit.csv)
- The preregistered event detector looked for a ≥36-hour gap where the previous observed timestamp was Friday UTC and the current timestamp was Sunday/Monday UTC; entry required an exact T+10 minute timestamp. In the entire archive it found four ≥36-hour timestamp gaps and three matching weekday candidates. All three were at Sunday/Monday 00:00 UTC holiday/data-gap timestamps, not executable FX weekly reopenings; none had an exact T+10 timestamp. Zero trades opened.
- **Binary verdict: GAGAL at the discovery/validation data gate, but alpha was not tested.** Do not interpret zero trades as proof gap fading loses money. 2022–2025 forward outcomes were not calculated. Dataset provenance is the same Dukascopy M1 BID/ASK archive (artifact 11959096102, SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`); its paired-flat filter remains heuristic because the source used `-fl`.
- Close this event-detection/execution rule on this archive. Do not loosen the T+10 timestamp requirement or relabel midnight timestamps as a true weekly reopening after seeing the failure. A future gap study needs a separately preregistered, verifiably session-aware input or event definition.


## R282 update (2026-10-17) — weekend-reopening gap fade: INVALID TEST / DATA INADEQUATE

- Preregistration: [R282 design](research/R282_EURUSD_WEEKEND_GAP_FADE_PREREGISTRATION.md)
- Runner: [R282 local source](research/r282_eurusd_weekend_gap_fade.py)
- Results: [compact verdict](research/R282_results_compact.json) · [event audit](research/R282_event_audit.csv) · [report](research/R282_FINAL_REPORT.md)
- The input archive was collected with Dukascopy `-fl`; most Sunday reopening observations were omitted. Only three >=36-hour closures met the literal Friday-to-Sunday/Monday date rule, and none had exact sequential T+10 data. Zero trades were evaluated.
- Verdict is **invalid test due data**, not evidence for or against the hypothesis. No forward period outcomes calculated and no holdout opened. Retry only with verified BID/ASK M1 data retaining true weekend reopen observations. No Actions workflow launched.


## R283 update (2026-10-17) — US index cash-open gap fade: GAGAL

| Block / candidate | Evidence | Disposition |
|---|---|---|
| R283 Q80 cash-open gap fade, T+10 entry, prior-close target, 0.75×gap stop | 709 discovery trades, PF 0.748 and -77.90R at modeled 2 bps; 163 validation trades, PF 0.599 and -34.83R. 1/2/4 bps PF: discovery 0.771/0.748/0.705; validation 0.618/0.599/0.563. | **GAGAL.** Both expectancy gates fail; forward 2022–2025 was not opened. Do not retune this exact specification. |

R283 is not evidence that every gap strategy fails; it closes only this preregistered specification. BID-only archives and modeled costs prevent funded promotion regardless. Report and period summary are archived; runner/full ledger still need repository archiving for full reproducibility.


## R283 postmortem (2026-10-17; diagnostic, not an alpha block)

R283 US-index Q80 cash-open gap fade is **FAILED** and contributes no retained signal block. The local 872-trade ledger shows negative expectancy before modeled cost (gross PF 0.795 discovery; 0.638 validation). Target exits were 152 vs 237 stops in discovery, and 35 vs 72 stops in 2021 validation. Stop share increased from 33.43% to 44.17% while target share held around 21%. Gap-up fades (short positions) were materially worse than gap-down fades, but neither direction was profitable. Costs are not the root cause. This diagnostic does **not** establish that a gap-continuation strategy works; any continuation test requires a new frozen rule set. Do not tune R283.

Detailed evidence: `research/R283_TRADE_LEVEL_DIAGNOSTIC.md`, `research/R283_EXIT_DECOMPOSITION.csv`, `research/R283_DIRECTION_DECOMPOSITION.csv`, `research/R283_INSTRUMENT_YEAR_DECOMPOSITION.csv`, and `research/R283_DIAGNOSTIC_RESULTS.json`.

Persistence issue: full R283 ledger and runner still have not been committed to GitHub; repository-only reproduction is incomplete.


## R284 update (2026-10-17) — late-morning index continuation: FAILED

| Candidate block | Evidence | Disposition |
|---|---|---|
| R284 one-per-day strongest normalized 10:00–11:55 directional move; child gate score >= 1.0; T+10 entry; 1.0× range stop/1.5R target | Child discovery 380 trades / PF 0.864 / -13.108R at 2 bp; 0/4 discovery years positive; validation 114 / PF 1.066 / +1.326R; discovery PF at 4 bp 0.797. Matched parent was negative as well. | **GAGAL.** Do not tune threshold, reverse direction or change time window after results. No signal block retained. |

Reusable controls remain data/time integrity, exact phone-delay entry, one concurrent index position, gap-aware stop fill, same-bar stop-first, and force-flat at 15:55 bar open. These are execution controls, not alpha. The BID-only cost model and heuristic flat-bar filter remain limitations. R284 did not open 2022–2026 and did not run funded replay. Compact replay engine is archived as `research/r284_late_morning_continuation_replay.py` and its aggregate results were verified against the original local run (all discovery/validation parent/child counts, PF and net R matched exactly at 1/2/4 bp). Row-level ledger remains local and not archived.


## R285 update (2026-10-17) — US500 turn-of-month intraday seasonality: FAILED

| Candidate | Evidence | Disposition |
|---|---|---|
| First three / last two active US500 RTH sessions each month; LONG from 09:40 ET to 15:55 ET | At 2 bp: discovery 226 trades / PF 1.130 / +785.76 bp, but only 1/4 discovery years positive; 2021 validation 58 trades / PF 0.632 / -669.02 bp. Parent all-session long in 2021 was +539.74 bp. | **GAGAL.** Discovery total is dominated by 2020 and the 2021 validation result reverses sharply. Do not alter the calendar window/direction after outcome. |

Only the calendar-seasonality hypothesis was tested; no 2022–2026 strategy outcomes were calculated. Reusable artifacts: `research/r285_us500_tom_intraday.py`, `research/R285_candidate_ledger_2bp.csv`, and `research/R285_selected_session_skips.csv`. Runner was rerun from the exact extracted CSV and matched candidate/parent aggregate metrics at 1/2/4 bp. Source remains M5 BID-only and cost assumptions are not verified executable costs. No signal block retained.


## R286 update (2026-10-17) — US500 three-session overextension fade: FAILED

| Candidate | Evidence | Disposition |
|---|---|---|
| Fade the top-quintile absolute three-active-session return; next-session 09:40–15:55 ET intraday holding | At 2 bp: discovery 165 trades / PF 0.988 / -87.79 bp; validation 47 / PF 0.987 / -15.25 bp. Matched continuation parent also lost: -572.21 bp discovery and -172.75 bp validation. | **GAGAL.** Relative loss reduction against a weaker parent is not a positive edge; no signal block retained. |

The signal used Q80 1.7307755% fit on 858 discovery windows. Do not tune Q80 or change direction/time after results. 2022–2026 results were not calculated. Source is M5 BID-only with modeled 1/2/4 bp costs, and no funded replay was run. Artifacts archived: `R286_FINAL_REPORT.md`, `R286_results_compact.json`, `r286_us500_3session_fade.py`, candidate and matched-parent ledgers, and `R286_skipped_signals.csv`.


## R287 update (2026-10-17) — intraday cross-index residual fade: FAILED

| Candidate / component | Evidence | Disposition |
|---|---|---|
| Fade the highest normalized 10:00–12:55 index residual versus same-day cross-sectional median; enter 13:05, flat 15:55 | At 2 bp, fade PF 0.802 / -2,742.47 bp on 552 discovery trades; validation PF 0.628 / -1,510.80 bp on 193 trades. | **GAGAL.** Clear negative residual-fade edge; no signal block retained. |
| Matched residual-following parent | Same 745 events: discovery PF 1.044 / +534.47 bp; validation PF 1.253 / +738.80 bp at 2 bp. | Diagnostic only. Direction selection after seeing this side-by-side result introduces selection bias; it needs an independent pre-registered test, and discovery PF misses 1.05. Do not directly promote. |

R287 uses 4 correlated US index M5 BID-only snapshots, one index trade maximum per session, per-symbol Q75 residual magnitude fitted on discovery 2017–2020, and a five-minute manual-entry delay after bar confirmation. 2022–2026 outcomes were not calculated. No funded replay. Artifacts archived: preregistration, report, results JSON, local engine, paired row ledger, and session-quality summary.


## R288 (2026-10-17) — cross-index residual follow-through: GAGAL
- Parent diagnostic: R287. Mutation: follow residual sign instead of fading it, with all other rules frozen. R288 preregistration committed before scoring 2022–2026.
- At 2 bp modeled cost, follow residual loses in 2022–2025 (718 trades, PF 0.795, -3,389.34 bp) and in later 2026 check (154 trades, PF 0.943, -116.46 bp). At 4 bp PF is 0.721 and 0.807. Bootstrap lower bound is negative.
- Matched fade is not retained: its exploratory 2022–2025 result turns negative at 4 bp and loses in 2026.
- No signal block from either direction. Retain only research methods: synchronized session quality audit, frozen per-symbol threshold calculation, deterministic matched-event ablation, fixed-cost stress, block bootstrap.
- Artifacts: `R288_US_INDEX_INTRADAY_RESIDUAL_FOLLOW_PREREGISTRATION.md`, `R288_FINAL_REPORT.md`, `R288_results_compact.json`, `r288_us_index_intraday_residual_follow.py`, `R288_annual_follow_2bp.csv`.
- Data limits: BID-only M5; hypothetical 1/2/4 bp costs, heuristic flat-bar rejection; 2022–2025 is contaminated and 2026 is not claimed as a pristine program holdout. No funded challenge replay.


## R289 (2026-10-17) — continental Europe cash-open gap continuation: GAGAL
- Pre-registered Q80 absolute gap threshold per instrument fit only on 2017–2020; one strongest continental index gap/date; enter 09:10 Europe/Berlin, target 1.0 gap-distance, stop 0.75 gap-distance, M5 stop-first ambiguity.
- Discovery (251 trades) passes numeric gates: PF_R 1.224 at 2 bp, +20.682R; 4 bp PF_R 1.152; 3/4 positive years. Validation 2021 (61 trades) has PF_R 1.128 and +3.088R at 2 bp; 4 bp PF_R 1.057.
- **GAGAL** only because four-week circular bootstrap validation mean weekly net R CI [-0.1767, +0.2817] crosses zero. The failure gate was preregistered. No 2022+ outcome was calculated; no threshold or target/stop rescue.
- Matched gap-fade diagnostic is materially worse at 2 bp in discovery (-28.506R, PF_R 0.752) and validation (-10.414R, PF_R 0.664), but this relative comparison is not sufficient to promote continuation.
- Keep no signal-alpha block. Retain code/process components: complete cash-session screen, frozen calibration split, one event per date, M5 stop-first ambiguity, bootstrap gate. Data is BID-only, transaction costs modeled, EUSIDXEUR coverage is weaker in early years, and no funded equity replay was run.
- Artifacts: `R289_CONTINENTAL_EUROPE_GAP_CONTINUATION_PREREGISTRATION.md`, `R289_FINAL_REPORT.md`, `R289_results_compact.json`, `r289_continental_europe_gap_continuation.py`, `R289_annual_summary_2bp.csv`, `R289_validation_weekly_bootstrap_2bp.json`, `R289_session_quality_audit_summary.csv`.


## R290 (2026-10-17) — US cash-open breakout-retest: GAGAL
- Child mutation relative to R263: add a later boundary retest confirmed by a close back outside, then enter on the next M5 open; keep same OR family, with a frozen 1.5R target / opposite-range-boundary stop and one position total per US date.
- Discovery (2016–2020), 1,059 trades, at 2 bp: PF_R 0.834, -95.595R; all five years negative. PF_R 0.732 at 4 bp and 0.644 at 6 bp.
- Validation 2021: 214 trades, PF_R 1.220 and +20.925R at 2 bp, but 4-week block bootstrap weekly-net-R CI [-0.111, +0.884] includes zero and 6 bp PF_R falls to 0.961. The preregistered bootstrap lower-bound gate failed.
- Verdict **GAGAL**; no post-2021 PnL calculated. No OR/retest/stop/target retuning on the same windows; no signal alpha block retained.
- Reusable process template only: retest is structurally separate from first breakout entry; delayed next-bar fill; one total correlated-index position/day; stop-first OHLC ambiguity; binary discovery/validation gates.
- Artifacts: `R290_US_CASH_OPEN_BREAKOUT_RETEST_PREREGISTRATION.md`, `R290_FINAL_REPORT.md`, `R290_results_compact.json`, `r290_us_cash_open_breakout_retest.py`, `R290_annual_summary.csv`, `R290_validation_weekly_bootstrap_2bp.json`, `R290_session_quality_summary.csv`.
- Inputs M5 BID-only; modeled costs, no verified ask-side spread/point value/commission/swap, and no funded equity-path replay.


## R291 update (2026-10-17) — USA500-to-German cash-session lead/lag: GAGAL
- **Frozen hypothesis:** previous eligible USA500 cash-session return sign predicts the next German index cash session; absolute-return threshold Q75 fixed on 2017–2020, German entry 09:20 Berlin, initial stop uses the 09:00–09:15 range, target 1.5R and flat by session close.
- Discovery 2017–2020: 246 trades; gross PF_R 0.769 and -36.653R before any cost. At modeled 2 bp PF_R 0.451 and -134.421R; 4 bp PF_R 0.302. All four discovery years lose.
- Validation 2021: 74 trades; gross PF_R 1.228 / +8.547R, but 2 bp PF_R collapses to 0.178 / -173.679R. Four-week weekly-net-R bootstrap 95% CI [-9.525,+0.040] R/week; lower bound fails.
- One trade has only 0.02 index points of initial risk, making notional-based modeled fees approximately 75.6R at 1bp; this is an operational design flaw exposed by the locked rule, not a license to add a new distance filter on these same periods.
- **Disposition: GAGAL; do not tune or reverse the sign after inspecting results.** No 2022–2026 candidate PnL calculated. No alpha block retained.
- Reusable research-method components only: previous-session date alignment using IANA local zones, frozen Q75 calibration, explicit cost stress, and bootstrap gate. These are process controls, not edge.
- Artifacts: `R291_TRANSATLANTIC_LEAD_LAG_PREREGISTRATION.md`, `R291_FINAL_REPORT.md`, `R291_results_compact.json`, `r291_transatlantic_lead_lag.py`, `R291_annual_summary_2bp.csv`, `R291_validation_weekly_bootstrap_2bp.json`.
- Data caveats: cached M5 BID-only USA500 and DEUIDXEUR; modeled 1/2/4 bp cost assumptions; no verified ask-side spread/slippage, swap/commission, stop tick ordering or FundedNext equity-path replay. Validation is not an untouched project holdout.


## R292 update (2026-10-17) — USA500 overnight-only long carry: GAGAL
- Hypothesis family: equity-index overnight/intraday return decomposition. Long USA500 at the close proxy of the M5 bar starting 15:55 New York and exit at the next eligible session's 09:30 RTH open; no SL/TP or signal filters.
- Discovery 2017–2020: 978 trades; at modeled 2 bp PF 1.094 and +1,995.48 bp; at 4 bp PF 1.002 and +39.48 bp; 4/4 annual cohorts positive at 2 bp.
- Validation 2021: 250 trades; at modeled 2 bp PF 1.186 / +742.22 bp; at 4 bp PF 1.058. However, the four-week circular bootstrap of weekly net bp gives 95% CI [-2.24,+30.11] bp/week, lower bound crosses zero. The preregistered gate fails.
- Maximum closed-trade drawdown reaches 38.57% of fixed notional in the discovery sequence, concentrated in 2020. This is not a funded-account drawdown estimate; notional-to-equity sizing and overnight floating losses were not modeled.
- **Disposition: GAGAL, no alpha block retained, no 2022+ candidate PnL.** Do not tune the holding interval or inspect later years as a rescue.
- Artifacts: `R292_USA500_OVERNIGHT_CARRY_PREREGISTRATION.md`, `R292_FINAL_REPORT.md`, `R292_results_compact.json`, `r292_usa500_overnight_carry.py`, `R292_annual_summary_2bp.csv`, `R292_validation_weekly_bootstrap_2bp.json`.
- Data caveats: cached M5 BID-only, modeled 1/2/4 bp costs, no verified CFD ask-side fills/slippage/swaps, no overnight floating equity, and no FundedNext DLL/MLL equity-path replay.


## R293 update (2026-10-17) — USA500 overnight carry + closing cross-index breadth: GAGAL

- [Locked preregistration](R293_USA500_OVERNIGHT_BREADTH_FILTER_PREREGISTRATION.md) · [final report](R293_FINAL_REPORT.md) · [compact results](R293_results_compact.json) · [local runner](r293_usa500_overnight_breadth_filter.py).
- **Frozen child:** parent R292's last-RTH-close-to-next-RTH-open USA500 long exposure, filtered by cross-index breadth. At the 15:45 ET M5 bar close, require at least 75% of quality-valid indices (at least 3 feeds) to have a positive 09:30-open to 15:45-close return; enter USA500 at the 15:55 bar open and exit next valid session's 09:30 open. Child and unconditional parent are scored on the same eligible dates and timestamp rules.
- Inputs are cached USA500, USATECH, USA30 and USSC2000 M5 BID-only archives; all four registered SHA-256 hashes passed. The 2016–2021 session audit covered 5,531 instrument-session rows. Only 2017–2021 outcomes were calculated; **no 2022+ candidate PnL was calculated**.
- At modeled 2 bp round-trip cost: discovery 2017–2020 = 442 trades, +1,320.41 bp, PF 1.137; validation 2021 = 119 trades, +249.78 bp, PF 1.144. At 4 bp PF was 1.043 discovery / 1.006 validation. Candidate discovery closed-PnL drawdown was 24.54% of fixed notional, versus 37.96% for unconditional parent. However, the child earned less aggregate net bp and traded less often than parent in both periods.
- Locked validation four-week circular bootstrap (5,000 resamples, seed 293, 52 weeks including zero-trade weeks) gave mean +4.803 bp/week and 95% CI [-5.548, +14.232] bp/week. The lower bound crossed zero: **R293 = GAGAL**. No funded equity-path replay was run and no signal-alpha block is retained.
- Keep only the research lesson that this breadth filter improved relative PF and discovery drawdown in the sampled history; because it did not improve aggregate return and failed its robustness gate, it is not evidence of a validated alpha block. Reusing related 2017–2021 windows also does not provide clean independent OOS.
- Costs are modeled stresses, not observed broker costs; feeds are BID-only. ASK-side fills, slippage, commissions, overnight floating loss, swaps, margin and FundedNext DLL/MLL path were not validated. Do not retune the breadth threshold or reuse the same window to rescue R293.


## R294 update (2026-10-17) — symmetric extreme-breadth overnight direction: GAGAL

- [Locked preregistration](R294_USA500_TWO_SIDED_BREADTH_OVERNIGHT_PREREGISTRATION.md) · [final report](R294_FINAL_REPORT.md) · [compact results](R294_results_compact.json) · [local runner](r294_usa500_two_sided_breadth_overnight.py).
- R294 is a preregistered direction-mapping crossover from R293: preserve the positive breadth >=75% long rule, and add a mirrored short when <=25% of valid US index feeds are positive by the 15:45 ET close. Enter USA500 at the 15:55 bar open; exit next eligible RTH session's 09:30 open. Four R205 M5 BID archives passed the registered hashes; 5,531 instrument-session dates were audited. No PnL after 2021 was calculated.
- At modeled 2 bp round-trip cost, R294 had 786 discovery trades (442 long, 344 short), net -137.72 bp / PF 0.993 over 2017–2020; validation 2021 had 216 trades (119 long, 97 short), net -448.43 bp / PF 0.891. At 4 bp, PF fell to 0.918 discovery / 0.797 validation.
- Matched R293 positive-tail long-only remained stronger: discovery +1,320.41 bp / PF 1.137, validation +249.78 bp / PF 1.144. Unconditional long was also net positive in both partitions at 2 bp (+1,533.09 / +459.12 bp; PF 1.070 / 1.109). Adding shorts increased signal coverage but made total results materially worse than either parent.
- Validation 2021 weekly-net-bp bootstrap: mean -8.624 bp/week, 95% CI [-26.012, +7.195] across 52 weeks including zeros, 5,000 circular 4-week blocks, seed 294. Multiple hard gates failed; **R294 = GAGAL**. Do not retune or inspect post-2021 outcomes as a rescue. No funded challenge replay.
- No alpha block is retained. The lesson is directional: the negative-breadth short tail did not show overnight continuation edge on these periods; retain R293 positive-tail and unconditional-long values only as diagnostics, not approved strategies. BID-only short execution, ASK-side fills, real costs, swaps and overnight floating loss remain unverified.


## R295 update (2026-10-17) — positive breadth + USA500 own-session confirmation: GAGAL

- [Locked preregistration](R295_BREADTH_PLUS_USA500_DIRECTION_CONFIRMATION_PREREGISTRATION.md) · [final report](R295_FINAL_REPORT.md) · [compact results](R295_results_compact.json) · [local runner](r295_breadth_plus_usa500_direction_confirmation.py).
- **Mutation:** R293 positive-tail long-only stream plus one new alignment gate: USA500's own 09:30 open → 15:45 bar close return must also be positive. Keep the >=75% valid-index breadth threshold, USA500 15:55 M5 open entry, next valid USA500 09:30 open exit, and modeled 1/2/4 bp cost schedule unchanged. Four cached M5 BID sources passed registered SHA-256 checks; 5,531 instrument-session rows were audited. No post-2021 strategy PnL was calculated.
- At modeled 2 bp cost: discovery 2017–2020 candidate 437 trades, +1,253.10 bp / PF 1.131; its parent R293 had 442 trades, +1,320.41 bp / PF 1.137. Candidate validation 2021 was exactly identical to parent: 119 trades, +249.78 bp / PF 1.144.
- Diagnostic: own-session direction confirmation removed only 5 discovery trades and zero validation trades. Those five omitted discovery trades themselves summed to +67.31 bp net and PF 1.692 at 2 bp, so the new gate discarded a net-profitable subset and reduced the child total. This is a redundant/negative-value mutation.
- Validation weekly bootstrap (5,000 circular four-week resamples, seed 295, all 52 Monday-start weeks including zeros) mean +4.803 bp/week, 95% CI [-5.557, +14.335] bp/week. The lower bound crosses zero, so **R295 = GAGAL**. No funded challenge replay and no alpha block promoted.
- Evolutionary decision: close the R293 breadth-only micro-mutation family rather than adding more gates to try to rescue the same periods. Keep R293 as a diagnostic only; it had better relative discovery PF than R295 but failed robustness too. Future work should move to a materially distinct hypothesis family. Inputs are BID-only; real spread/ASK fills, slippage, commission, swap, overnight floating loss and the funded account equity path remain unverified.


## R296 update (2026-10-17) — INVALID TEST, data-event definition error

- [Original locked specification](R296_XAUUSD_WEEKEND_GAP_CONTINUATION_PREREGISTRATION.md) · [data-quality invalidation](R296_DATA_QUALITY_INVALIDATION.md).
- The first attempt incorrectly used the first Sunday raw timestamp (usually 00:00 UTC) as an executable market reopening. The paired BID/ASK file has static O=H=L=C quotes repeated from that timestamp through 22:55 UTC; actual active M5 bars begin around 23:00 UTC. The runner traded during a static closed-market quote block.
- Therefore R296's PnL/bootstraps are **invalid test output**, not evidence for or against the weekend-gap-continuation hypothesis, and must not be counted as a valid signal FAIL. The manifest's include_synthetic_flat_bars=false flag did not guarantee every row represented an active tradable quote. Row-level active-market validation is now mandatory.
- Do not use R296 performance to select a direction or tune R297. A separate correction candidate R297 was preregistered before calculating fresh PnL and changes only the event timestamp/data-eligibility logic to the first genuinely active Sunday M5 bar.

## R297 update (2026-10-17) — true-active XAUUSD weekend gap continuation: GAGAL

- [Locked preregistration](R297_XAUUSD_ACTIVE_REOPEN_GAP_CONTINUATION_PREREGISTRATION.md) · [final report](R297_FINAL_REPORT.md) · [compact results JSON](R297_results_compact.json) · [local runner](r297_active_reopen_gap_continuation.py).
- R297 uses the first Sunday M5 bar with real intrabar movement after the static closed-market quote block, compares its BID/ASK midpoint with the last active Friday bar close, requires a gap greater than twice the sum of those active quote spreads, then follows the gap direction at T+10 with a 1R stop, 1R target and exact T+4h maximum hold. Corrected runner validated both registered SHA-256 hashes, paired all 947,326 BID/ASK timestamps, and excluded all 69,396 data rows at/after 2026-01-01 before outcome calculations. **No 2026 strategy PnL was calculated.**
- There were 500 active weekend-gap events in 2016–2025; 52 met all locked spread, timestamp, quote and complete-path conditions. The candidate closed 24 trades in discovery (2016–2020) and 28 in validation (2021–2025).
- At +$0.30/oz extra cost, discovery produced **−6.161R / PF_R 0.460** over 24 trades. Validation was slightly positive at **+0.385R / PF_R 1.042** over 28 trades, below the PF gate. At +$0.50/oz, validation turned negative (−0.253R, PF_R 0.973). The 4-week weekly-net-R validation bootstrap mean was +0.00148R/week, 95% CI [-0.02939, +0.03141], which crosses zero.
- **R297 = GAGAL.** Discovery and validation trade-count gates fail; discovery net expectancy is negative; validation PF and bootstrap gates fail; the higher-cost validation result is negative. No signal block retained, no opposite-direction fade rescue, no later-period outcome calculation, and no funded challenge replay.
- Reusable learning: enforce row-level market-activity checks for weekend events, not manifest flags alone. The valid-active event screen is sparse (52 completed trades across ten years) and does not show robust continuation expectancy under these locked rules. Inputs have historical BID/ASK but do not verify FundedNext point value, commission, slippage, swap or live fills.


## R298 (2026-10-17) — XAUUSD London Asian-range sweep-and-reclaim reversal: GAGAL

- Locked preregistration: `R298_XAUUSD_LONDON_ASIA_RANGE_SWEEP_RECLAIM_PREREGISTRATION.md` (commit `fb59fd7c640fa055e32e6d86e8feee2e0d44eb0d`), committed before PnL calculation.
- Hypothesis: during 07:00–10:00 Europe/London, trade the first XAUUSD M5 sweep beyond 0.10× the completed UTC 00:00–05:55 Asian range that closes back inside; entry at signal-bar start +10 minutes, stop at the signal bar's executable-side extreme, target Asian midpoint, minimum planned reward/risk 1.00, maximum hold four hours. Paired BID/ASK fills and static-row exclusion were required.
- Registered hashes verified; 947,326 paired timestamps, 877,930 pre-2026 rows used, and all 69,396 rows at/after 2026-01-01 excluded before signal construction. 2,553 full active Asian ranges, 894 first-reclaim signals and 598 completed trades.
- At +$0.30/oz extra cost, discovery 2016–2020: 313 trades, **−285.893R / PF_R 0.297**. Validation 2021–2025: 285 trades, **−178.933R / PF_R 0.409**. Results were also negative with zero added cost: −132.434R / PF_R 0.515 discovery and −100.768R / PF_R 0.575 validation. All five annual cohorts in both periods were negative at +$0.30/oz.
- Validation weekly four-week circular bootstrap: mean −0.68557R/week, 95% CI [−0.89792, −0.47209], 10,000 resamples, seed 298. Every signal-economics/robustness gate failed, apart from minimum trade counts.
- **R298 = GAGAL.** Do not tune thresholds/exits or reverse direction on these dates. No 2026 PnL and no funded challenge replay. No alpha block retained.
- Artifacts: `R298_XAUUSD_LONDON_ASIA_RANGE_SWEEP_RECLAIM_PREREGISTRATION.md`, `R298_FINAL_REPORT.md`, `R298_results_compact.json`, `R298_annual_summary.csv`. Full local runner, trade ledger and audit tables are in the R298 research ZIP.
- Limitations: 2021–2025 is research-contaminated; data are historical BID/ASK quotes, not verified FundedNext execution. Broker costs, contract value, slippage, swaps, margin and two-phase account-equity/DLL/MLL behavior remain unverified.
