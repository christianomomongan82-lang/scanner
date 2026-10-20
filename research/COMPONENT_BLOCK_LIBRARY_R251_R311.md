# Component Block Library — R251–R300

Date: 2026-10-18  
Source ledger: [MASTER_SEARCH_LEDGER_R251_R299.csv](MASTER_SEARCH_LEDGER_R251_R299.csv)  
Method: only record a component if its role/contribution is grounded in a locked report or explicit diagnostic. Do not infer that a block has positive alpha from a favorable point estimate.

## Executive finding

**No economic alpha block from the audited R251–R299 generation is approved as a standalone funded-ready module.** Some components showed relative improvement, while several technical practices are reusable. Keep these categories separate.

- **Reusable engineering practices** improve data integrity or measurement; they do not constitute market edge.
- **Diagnostic economic components** are worth remembering but remain unvalidated because the parent/child result was negative, contaminated, insufficiently sampled, or failed robustness.
- **Closed economic components** must not be re-parameterized on their old windows.
- **Invalid/unreachable components** cannot be counted as alpha evidence.

## A. Reusable engineering blocks

| Block ID | Definition | Evidence | Reuse rule |
|---|---|---|---|
| ENG_EXACT_TIMESTAMP_JOIN | Join instruments only on exact timestamp keys; never row-number pair or forward-fill missing bars | R299 data amendment reports 468,937 shared timestamps and excludes unique timestamps; R287–R288 use synchronized sessions | Reuse for every cross-instrument test; retain unmatched-row audit |
| ENG_NO_SYNTHETIC_TRADABLE_BARS | Leave missing/incomplete bars missing; do not create tradable OHLC | R257, R262, R271, R281–R282, R297–R298 data audits | Mandatory; any exception is preregistered and labeled |
| ENG_ACTIVE_QUOTE_REOPEN | Distinguish static/closed-market quote snapshots from first genuinely active quote after reopening | R296 invalidated; R297 corrected first-active M5 reopen | Mandatory for weekend/event gaps; R296 PnL is not evidence |
| ENG_EXEC_SIDE_BID_ASK | Long entries use ASK and long exits BID; short entries BID and exits ASK when quotes exist | R258, R260–R262, R269–R272, R297–R298 | Required for executable FX/XAU simulations; BID-only index results remain cost-sensitivity screens |
| ENG_PHONE_DELAY | Baseline fill is first exact observed quote after five minutes of reaction time following signal-bar close; M5 often means bar timestamp +10 min | R263, R264, R266, R275, R276–R280, R290 | Use consistently for intended manual workflow; additional-delay stress must be predeclared |
| ENG_STOP_GAP_COLLISION | Define open-gap stop fill and stop-first handling when stop and target touch within one bar | R262–R264, R269, R271, R297–R298 | Reuse as conservative execution convention; acknowledge OHLC cannot resolve intrabar order perfectly |
| ENG_BOOTSTRAP_WEEKLY_BLOCK | Resample calendar weeks in blocks and include zero-trade weeks for time-based opportunity systems | R258–R261, R266, R269–R299 | Reuse with fixed method/seed; confidence intervals diagnose uncertainty, not prove future success |
| ENG_MATCHED_PARENT_ABLATION | Compare parent, child, component, no-filter baseline and removed-event stream on the same dates/costs | R263–R280, R287–R295 | Mandatory for filters/routers/crossovers; relative improvement is not an absolute edge |
| ENG_BRANCH_REACHABILITY | Before PnL, calculate each router branch's feature coverage and attainable activation rate | R270 and R272 found an ER gate that never activated its continuation module | Mandatory; unreachable branch means the registered router design fails coverage before economics |
| ENG_ARTIFACT_REPRODUCIBILITY | Commit exact config, input hashes, runner, complete trade ledger, compact results and report | R268 explicitly failed repository-only reproduction because component CSVs were absent | Mandatory for every candidate; summary JSON alone is insufficient |

## B. Diagnostic economic blocks — not approved as alpha

| Block ID | Observed evidence | Why not approved | Permitted future use |
|---|---|---|---|
| DIAG_US_SYNC_BREADTH_3OF4 | R276 historical screen improved risk-normalized PF and drawdown relative to its matched parent | 2026 diagnostic negative, very long holding-time tail, BID-only input and no challenge-equity replay | Use only as a hypothesis/ablation reference, not as an approved module; no near-duplicate cash-open children |
| DIAG_US500_POSITIVE_BREADTH_CARRY | R293 improved PF versus unconditional overnight long at 2bp | Lower total return than parent; validation bootstrap crossed zero; overnight floating loss/swap not modeled | Use as a diagnostic baseline only; exact family R292–R295 is closed |
| DIAG_CROSS_INDEX_FOLLOW_RESIDUAL | R287's same-event follow stream was better than its fade stream | Follow child R288 was negative in its own frozen later sample and cost stress | Treat as evidence that the registered fade direction was wrong on that sample—not proof that following residual is a positive alpha block |
| DIAG_EUROPE_GAP_CONTINUATION | R289 discovery PF 1.2245 / validation PF 1.1283 at 2bp | Validation bootstrap included zero; only 61 validation trades; net-R vs net-notional return sign needs reconciliation | Preserve as a research observation; no rescue/tuning on the same data |
| DIAG_XAU_HTF_ALIGNMENT | R273 alignment reduced loss compared with raw parent | Both parent and aligned child materially negative in discovery and validation | Do not inherit the alignment filter as positive edge; new candidate needs independent evidence |
| DIAG_NASDAQ_LEAD_LAG | R280 improved mean forward R/trade vs matched parent in contaminated 2022–2025 | Failed discovery, annual stability and bootstrap; 2026 diagnostic negative | Do not adjust 5–30-minute lag window on existing periods |
| DIAG_OVERNIGHT_CARRY_BASE_RATE | R292 positive discovery/validation point estimates at 2bp | Bootstrap crossed zero, ~38.57% fixed-notional drawdown, overnight floating loss and swaps not modeled | Use only for historical context; do not use as approved portfolio capital |
| DIAG_RELATIVE_VALUE_PAIR | R265 forward PF 1.395 ideal / 1.313 delayed at +4bp | Only 41 forward trades, confidence intervals cross zero, no contemporaneous preregistration | Not promotion-eligible; require a new independently locked study before reuse |

## C. Closed negative signal blocks

These are exact registered rules or close descendants. Do not re-open their old data to change thresholds, windows, exits, direction or instrument selection.

| Block family | Closed examples | Main diagnosis |
|---|---|---|
| FX_H1_SHOCK_FADE | R260 | Very high frequency but strongly negative expectancy before/after costs |
| FX_ROLLING_EXTREME_SWEEP | R255 | 2,824 forward trades, PF 0.786; OOS PF 0.671 |
| FX_LONDON_ASIA_SWEEP | R269 | Negative even at zero incremental cost; all four forward years negative |
| FX_MULTI_HORIZON_MOMENTUM | R258 | Forward PF 0.785 at +1 pip, all years negative, simulated challenge failed at all tested risks |
| FX_H4_STRUCTURE_PULLBACK | R262 | Discovery edge disappears in validation and forward; bootstrap wholly negative |
| FX_LONDON_IMPULSE | R261 | Discovery and forward not profitable; validation/OOS point wins are too small/unstable |
| FX_DAILY_20_SESSION_BREAKOUT | R271 | Low frequency and negative before added cost across aggregate periods |
| FX_ASIA_ROUTER_MODULE_B | R270 | Active branch negative before incremental cost |
| XAU_IMPULSE_FOLLOW | R274 | Strongly negative across discovery and validation, even at zero added cost |
| XAU_REOPEN_GAP_CONTINUATION | R297 | Only 24 discovery/28 validation trades; discovery PF 0.460; validation weak and turns negative under higher cost |
| XAU_LONDON_SWEEP_RECLAIM | R298 | Discovery PF 0.297 and validation PF 0.409 at +$0.30/oz; all annual cohorts negative |
| XAU_DUAL_MODULE_ROUTER | R272 | Continuation module unreachable; active fade and combined streams negative |
| US_CASH_OPEN_ORB | R263, R290 | Broad discovery losses; retest did not repair parent; cost/delay gates fail |
| US_CASH_OPEN_GAP_FADE | R264, R283 | Negative/stress-sensitive at primary execution costs |
| US_INDEX_CASH_OPEN_MUTATIONS | R277–R280 | Same family mutations do not establish independent robust alpha; 2022–2026 is contaminated |
| US_INDEX_LATE_MORNING_DRIFT | R284, R266 | Discovery/validation weakness and annual/bootstrap instability |
| US_INDEX_TURN_OF_MONTH | R285 | Positive discovery concentrated in one year; sharp validation loss |
| US_INDEX_OVEREXTENSION_FADE | R286 | Near-flat PF below 1 and negative net in both registered splits |
| US_INDEX_RESIDUAL_FADE/FOLLOW | R287–R288 | Fade very negative; follow-on candidate fails; no supported block remains |
| US_SESSION_TO_GERMANY_LEAD | R291 | Negative in discovery and validation, tiny-stop cost distortion |
| US500_OVERNIGHT_CARRY_FILTERS | R292–R295 | Related family closed: uncertain base rate, short mirror negative, own-session filter redundant |
| USATECH_TO_USA500_30M_LEAD | R299 | Negative PF and net R in both discovery and validation |

## D. Unreachable, redundant, or invalid blocks

| Block ID | Evidence | Disposition |
|---|---|---|
| INVALID_FX_WEEKEND_GAP_SOURCE | R282 found 3 candidate events and zero exact T+10 tradable signals because collection/filtering removed required reopening observations | GAGAL due to data; not evidence for/against the market hypothesis |
| INVALID_XAU_STATIC_SUNDAY_REOPEN | R296 treated static Sunday quote snapshots as active; corrected by R297 using first genuine active bar | R296 invalid; only R297 is usable evidence for that exact continuation setup |
| UNREACHABLE_R270_MODULE_A | Maximum observed Asia ER 0.2101; registered gate was ER >=0.30; module never fired | Do not lower threshold on same sample; a future router needs fresh rationale and reachability gate |
| UNREACHABLE_R272_MODULE_A | Maximum 12-hour ER 0.3249; registered gate ER >=0.45; zero trades | Do not lower threshold on same sample; router failed as designed |
| REDUNDANT_R295_CONFIRMATION | Removed only 5/442 discovery events and 0/119 validation events; removed discovery events were net profitable | Do not reuse this filter as an added confirmation |

## E. Evolutionary selection rules derived from these records

1. **No economic block receives “trusted alpha” status from this library.** The currently reusable blocks are engineering/test-design blocks only.
2. A relative winner is a source of a new hypothesis, not a promoted child. The next child must be locked before using any fresh confirmation period.
3. Before crossover, identify the component's demonstrated contribution on matched events. If both parents are negative, a combination can be tested as a hypothesis but cannot inherit credibility just because their triggers differ.
4. Require component reachability and event-frequency checks before PnL; R270/R272 show why.
5. Require exact repository reproducibility; R268 shows that a result may be economically negative and still have a separate reproducibility failure.
6. The next portfolio architecture must be grown from independently supported alpha blocks. Until then, keep searching for a genuinely new mechanism rather than unioning the closed streams.

## E. R300 — FX London fixing-window fade — CLOSED / GAGAL

- **Block ID:** FX_LONDON_FIX_POST_EVENT_REVERSAL.
- **Evidence:** R300 tested a preregistered fade of the EURUSD midpoint return from 15:40 to 15:55 London, with entry delayed until 16:05 to avoid trading into the fixing window. At +1 pip extra cost: discovery 1,024 trades, −257.011R, PF 0.573; validation 257 trades, −59.981R, PF 0.580. Both sides were also negative at zero extra cost.
- **Matched control:** following the same pre-fix return lost too (discovery −228.183R / PF 0.607 and validation −64.372R / PF 0.560 at +1 pip).
- **Disposition:** no alpha signal block retained. Reuse only exact BID/ASK joins, London DST mapping, phone-delay alignment, active-bar checks, and stop-first collision controls. No time-window, direction, stop/target, or hold-period rescue on the same dates.
- **Limits:** historical FX periods are programme-contaminated; no account-specific cost or equity-aware FundedNext challenge path.


## F. R311 — Tokyo fixing fade — CLOSED / GAGAL

- **Proposed signal block:** `FX_TOKYO_FIX_POST_EVENT_FADE` — not retained as an alpha block.
- **Evidence at +1 pip incremental round-trip cost:** discovery 2017–2020 = 750 trades / -360.843R / PF_R 0.3445; validation 2021 = 143 trades / -73.799R / PF_R 0.3161. Both were negative before added friction; validation 4-week weekly bootstrap CI was entirely negative [-1.8635, -0.9933]R/week. The registered T+10 fade and matched follow stream did not repair the mechanism.
- **Permitted reuse:** only engineering/test-design components such as exact paired BID/ASK timestamp joins, active-bar coverage, local-time mapping, explicit delayed-fill grids, pre-outcome eligibility, conservative intrabar stop-first checks and reproducible skip serialization. These are not evidence of alpha.
- **Stop rule:** do not flip the direction or adjust fixing clock, threshold, holding time or barrier distances on these same dates. Any future benchmark hypothesis must use a distinct economic mechanism and, under R312, wait until repository-complete runner/ledger and real-data funded-path replay are reproducible.
