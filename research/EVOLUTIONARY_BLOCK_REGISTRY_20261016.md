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
