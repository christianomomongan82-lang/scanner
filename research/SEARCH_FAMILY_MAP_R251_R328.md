# Search Family Map — R251–R328 (Canonical)

Date audited: 2026-10-21  
Canonical ledger: [MASTER_SEARCH_LEDGER_R251_R328.csv](MASTER_SEARCH_LEDGER_R251_R328.csv)  
Scoring contract: [SEARCH_PROCESS_IMPROVEMENT_PROTOCOL_V2.md](SEARCH_PROCESS_IMPROVEMENT_PROTOCOL_V2.md)  
Experiment template: [EXPERIMENT_REGISTRATION_CARD_TEMPLATE_V2.md](EXPERIMENT_REGISTRATION_CARD_TEMPLATE_V2.md)

## Coverage statement

The reconciled canonical ledger contains 76 unique experiment records across R251–R328; only R259 (workflow incident) and R267 (no standalone source record located) are absent. Records R300–R302 and R323–R328 were restored/reconstructed from their archived source reports and package summaries, with provenance links preserved. The index covers this audited research generation; it is not an exhaustive ledger of every experiment numbered below R251. Older historical sections below retain their original audit context; dated addenda cover R312–R328.

**Audited verdict: zero candidates promoted as funded-ready.** R276 had a historical screen pass but was not promoted. Data-invalid tests are labeled separately from economic failures so a missing-data problem is not mistaken for evidence that alpha is absent.

## 1. FX: trend, momentum, and breakout

### Lineage / coverage
- R252 — H1 tail-threshold momentum/reversal.
- R256 — H4 rolling breakout.
- R257 — H1 compression-release breakout; implementation/coverage failure left zero validation trades. R281 is the corrected-engine follow-up for the same family, not independent confirmation.
- R258 — 24-hour momentum aligned with 120-hour direction.
- R262 — H4 structural pullback continuation.
- R271 — daily 20-session breakout.
- R273 — XAU, not FX; keep separate despite its pullback-continuation wording.

### Learned
Momentum/trend has been tested at multiple horizons. R258 and R260 generated plenty of trades but were strongly negative after costs; R262 was positive in discovery before stress but negative in validation and all forward years. R271 has very low frequency and negative expectancy. The R257 result alone is an implementation failure, but R281 corrected the engine and still failed discovery and validation-count gates.

### Stop rule
Do not create another candidate that simply changes the breakout lookback, tail percentile, ATR multiple, or target of these exact rules. A future candidate must propose a distinct causal condition and must be selected without touching protected holdout outcomes.

## 2. FX: reversal, failed breakout, and sweep/reclaim

### Lineage / coverage
- R254 — Asian-range failed-break fade.
- R255 — rolling-extreme sweep/reclaim reversal.
- R260 — H1 shock-candle fade.
- R269 — London Asian-range sweep/reclaim.
- R270 — two-module Asia-session regime router (Module A unreachable; Module B negative).
- R282 — EURUSD weekend gap fade was data-inadequate; it is not economic evidence.
- R297 is the corrected XAU reopening-gap continuation after R296's event-time defect; it is gold-specific, not FX evidence.

### Learned
Several reversal designs have been tested. R255 and R260 were very high-frequency and strongly negative, so frequency is not the missing piece for those rules. R269 was negative even before incremental cost. R270 showed that a routing condition can be structurally unreachable: feature/branch coverage should be checked before any PnL.

### Stop rule
Do not repeat the same Asian/London sweep/reclaim triggers with a nearby threshold and call them new. A new reversal family needs a different economic mechanism (not a cosmetic trigger change), independent data evidence, and a pre-outcome reason why the prior negative results should not apply.

## 3. FX: sessions and range states

### Lineage / coverage
- R253 — Asian-range close breakout.
- R261 — London-window impulse continuation.
- R269 — London Asian-range sweep/reclaim.
- R270 — Asia-session regime router.
- R281 — H1 compression breakout corrected-engine replay.

### Learned
Session-based setups are not untested. Results show weak discovery/forward expectancy, instability, inadequate samples, or unreachable branches. A session label by itself is not an edge.

### Stop rule
Don't run another Asian/London open breakout or impulse by changing only the start/end clock, range percentile or holding time. Any future session-dependent candidate must demonstrate a new conditional relationship and pass pre-outcome feature coverage tests.

## 4. FX: cross-pair lead/lag

### Lineage / coverage
- R251 — GBPUSD impulse / EURUSD catch-up.
- R258 is single-pair multi-horizon momentum, not a true new cross-pair candidate.

### Learned
R251 failed cost stress and 2026 OOS. One cross-pair lag idea is insufficient to declare the entire family impossible, but the original catch-up rule is closed.

### Stop rule
No retuning R251's lag window or threshold on its old periods. A future cross-pair thesis must identify a new structural relationship and record synchronized quotes, correlation, direction selection, and an executable pair-cost model.

## 5. U.S. index cash-open / ORB / gap / breadth

### Lineage / coverage
- R263 — base cash-open ORB; later entry-retest child R290.
- R264 and R283 — cash-open gap-fade rules on different specifications/universes.
- R276 — synchronized 3-of-4 breadth breakout; historical screen passed, not promoted.
- R277 — same-day-flat long/short variant of R276.
- R278 — long-only variant.
- R279 — removed fixed target from R278.
- R280 — Nasdaq-led follower breakout.
- R285 — turn-of-month intraday seasonality, not a simple ORB but shares USA500 M5 base.
- R286 — three-session overextension reversal, same base feed but different temporal mechanism.

### Learned
This is the densest test cluster. Multiple “children” change direction, entry confirmation, stop/target or whether the position holds overnight. R276's historical screen pass was not challenge-ready: holding time could be very long, 2026 diagnostic results were poor and no full equity-aware funded replay was completed. R277–R280 do not establish robust positive edge. R290's retest did not repair its parent’s broad discovery losses. R263/R264/R283 show that positive later point estimates can collapse under a consistent cost and delay stress.

### Stop rule
**Pause near-duplicate U.S. cash-open ORB, gap, target, delay and breadth mutations.** Any exception must provide a new mechanism ID and explain why it is not just another variant from this cluster before any outcomes are calculated.

## 6. U.S. index intraday drift and overnight carry

### Lineage / coverage
- R284 — normalized late-morning impulse continuation.
- R266 — afternoon continuation after a strong morning.
- R292 — overnight USA500 long base rate.
- R293 — positive-tail breadth filter of R292.
- R294 — bearish breadth mirror.
- R295 — extra own-session confirmation of R293.

### Learned
R293's filter improved PF relative to its base but produced less total return and failed the bootstrap. R294's short mirror damaged expectancy. R295 removed only five discovery trades and zero validation trades, so it added virtually no independent information and reduced discovery economics. R292 had positive point estimates at moderate cost but a high fixed-notional drawdown and failed uncertainty requirements.

### Stop rule
Close R292–R295 as one registered carry family. Don't add another nearly identical breadth threshold or symmetric short leg. A future overnight strategy must explicitly model swap, opening gaps, and floating daily/max loss before any challenge ranking.

## 7. Cross-index / cross-session / relative value

### Lineage / coverage
- R265 — USA tech/USA500 relative-value mean reversion; retrospective, only 41 forward trades.
- R276–R280 — index breadth / Nasdaq leader-follower relationships.
- R287 — fade cross-index residual; exact-event follow stream was a diagnostic parent.
- R288 — preregistered follow-residual child; failed in 2022–2025 and 2026.
- R289 — European index cash-open gap continuation.
- R291 — U.S. cash-session lead predicting the next German session.
- R299 — USATECH 30-minute impulse predicting USA500 follow-through.

### Learned
These tests span different mathematical definitions, but share some of the same index instruments, M5 archives, directional equity-market behavior and repeatedly examined years. A different pair of symbols does not automatically create independent evidence. R287 demonstrated a reversal/follow direction mismatch but the selected follow direction then failed in R288. R289 had positive point estimates but a validation bootstrap crossing zero plus a R-vs-notional normalization discrepancy. R299 was negative in both registered periods.

### Stop rule
No more lead-lag variants just changing 5–30 minutes to another window, nor repeated residual follow/fade on the same dates. Any next test must use an independent, predeclared mechanism and exact timestamp-key alignment; the baseline, child, and direction ablation must be scored together.

## 8. Gold (XAUUSD): intraday price action and routing

### Lineage / coverage
- R272 — dual-module router. A's ER>=0.45 branch fired zero times; B's failed-excursion fade was negative. Raw union and router were both negative.
- R273 — timeframe-aligned pullback continuation, reduced losses but still strongly negative.
- R274 — impulse follow-through, strongly negative across discovery and validation.
- R296 — invalid predecessor: static Sunday quote snapshots were incorrectly treated as active reopen.
- R297 — corrected first-active-reopen gap continuation, low sample and weak discovery.
- R298 — London Asian-range sweep/reclaim, strongly negative even with zero incremental cost.

### Learned
Gold price action is not untested. R272 is a key example of architecture failure: one branch was unreachable, and all active streams were negative. R296 must never be counted as valid economic evidence. R297 is the valid event-time-corrected version and failed; R298 failed strongly. Reports say the XAU 2026 outcome window remained unopened through these tests.

### Protected window
XAUUSD 2026 is the only identified instrument-period window in this recent family map that reports explicitly say remained unscored, but it is limited. It may be opened only once for one candidate after the candidate is frozen and all pre-2026 gates pass. It cannot be used to breed a second candidate.

## 9. Portfolio / evolutionary composition

### Lineage / coverage
- R268 — retrospective union of R262 and R263 with 0.25% fixed-fractional risk and 1% max open initial risk.
- R270 — FX router whose continuation branch was unreachable and remaining fade branch negative.
- R272 — XAU two-module router with unreachable continuation branch and negative active branch.

### Learned
R268 fell from $6,000 to $3,374.61 on 2022–2025, with 0.823 net-R PF and 44.60% closed-equity drawdown; it also failed repository-only reproducibility because the exact component ledgers were not committed. This is not evidence that modular composition is useless. It shows that combining already-failed modules, or routing to a failed/unreachable branch, does not create edge.

### Stop rule
No portfolio composition using unverified/failed streams as if they were established alpha. For a future crossover, compare each parent, a matched baseline, component ablations, and the child on identical timestamps and cost assumptions before evaluating equity compounding.

## 10. What is still missing from the research system

1. **Component-level library.** The current ledger describes strategy experiments but not all atomic components (context, signal trigger, direction, entry delay, stop/target, session, instrument) with unique block IDs. Build this when the next candidate is decomposed; do not retroactively invent contribution claims.
2. **One normalized economic and funded scorecard.** Many historic reports use different units and cost grids. The governance file fixes a common future contract; historical values should remain in their native unit until they can be rebuilt from a common ledger.
3. **Repository completeness.** The R268 component trade ledgers and some local runners/row-level outputs are explicitly missing from the active branch. R189's exact original M1 history is also unavailable. A report/summary is not the same as full reproduction.
4. **Pristine validation.** Reused 2022–2025 and several FX/index 2026 windows cannot be called untouched program-level OOS. The limited XAU 2026 window should stay protected.
5. **Challenge-equivalent path simulation.** Some proxy replays exist, but no one common simulator has been validated against current provider server reset, intratrade floating equity, spreads, fee/slippage, swaps and all special rule constraints.

## Immediate research decision

- Do not start another near-duplicate U.S. index cash-open test.
- Do not revive closed FX/XAU candidates through parameter edits.
- Before choosing the next hypothesis, select a mechanism-family gap based on novelty, data/execution readiness, phone feasibility, and ability to complement existing exposure. Pre-register it using the v1 card.
- Only open the protected XAU 2026 window if a single candidate passes all frozen pre-2026 gates and is explicitly nominated as the one final test.

The system's evolution should improve because past experiments narrow the choices and inform which *new mechanism* to test—not because a failed candidate is mutated until one historical chart turns green.


## R303 — EURUSD spread-shock reversion: CLOSED / GAGAL

R303 tested a distinct quote-state mechanism: fade a large five-minute midpoint move only when observed EURUSD BID/ASK spread simultaneously reaches at least twice its trailing baseline and then normalizes at the first manual-compatible executable quote. The hypothesis was frozen before outcomes; T+5 was primary, T+10 was a fixed latency stress.

At +1 pip incremental round-trip cost, discovery 2017–2020 was 739 trades / -93.407R / PF_R 0.769; validation 2021 was 66 trades / -7.360R / PF_R 0.777. Validation's four-week weekly-net bootstrap 95% CI [-0.406, +0.113] crosses zero. Even the zero-extra-cost point estimate turns negative at +0.5 pip. Only 2/13 registered gates pass. **Close the R303 parameterization and do not retune this exact spread ratio, threshold, delay or exit on the same years.** The broader economic class is not universally disproved, but no R303 alpha block is retained.

Historical FX windows 2017–2021 have extensive program-level contamination. Exact runner and row-level ledger transfer to GitHub remains incomplete, so repository-only reproducibility is an additional failed gate. See [R303 report](R303_FINAL_REPORT.md), [index](R303_INDEX.md), and [manifest](R303_DATA_MANIFEST.md).

## 10. FX local-hours fixed-clock bias — R304

### Lineage / coverage
- R304 — short EURUSD during 08:00–12:00 Europe/London and long EURUSD during 08:00–12:00 America/New_York, entered after a fixed five-minute delay.

### Result and lesson
At +1 pip added round-trip friction, the combined stream lost -42.390R / PF_R 0.926 in discovery 2017–2020 and -15.560R / PF_R 0.889 in 2021 validation. Both modules were negative across 2017–2021; the +0.5 pip stress also turned both aggregate periods negative. The mirrored direction diagnostic was negative too. The local-trading-hours result described in published research does not reliably transfer to this EURUSD paired quote feed with the registered execution/cost model.

### Stop rule
Close this registered fixed-clock direction and do not change session times, direction, stop range or exit horizon on the same periods. A future session-related hypothesis must identify a distinct conditional mechanism rather than merely shift clock boundaries. The 2022+ R304 outcome window remains unscored after early gates failed.

## 11. Cross-asset EURUSD-to-XAU common-USD factor — R305/R306

### R305 — impulse transmission
A causal, trailing 20-calendar-day Q85 of absolute EURUSD 30-minute returns triggered same-direction XAUUSD trades with a manual-compatible five-minute post-close delay, 1R stop, 1.5R target and 60-minute limit. At +$0.30/oz added cost, discovery was 12,338 trades / -6,974.05R / PF_R 0.340; 2021–2025 validation/diagnostic was 14,201 trades / -4,486.27R / PF_R 0.536. Both periods were negative even at zero added cost; all scored years were negative. Validation bootstrap CI was entirely negative.

### R306 — XAU underreaction catch-up
This locked conditional child required the same EURUSD shock plus XAU's absolute preceding 30-minute move at/below its trailing 20-day median, then followed the EURUSD sign in XAU. At +$0.30/oz, discovery was 3,322 trades / -2,058.60R / PF_R 0.304; validation/diagnostic was 4,004 trades / -1,398.50R / PF_R 0.497. Both periods were negative even at zero added cost; validation bootstrap CI was entirely negative.

### Stop rule
Close both rules. Do not flip the direction, alter the Q85/Q50 thresholds, stops, targets, or hold duration on these same periods. The common-USD directional assumption did not yield a cost-surviving tradeable relationship in the registered feed. XAUUSD 2026 remains protected and unscored. Any future cross-asset proposal needs a distinct information mechanism, not another sign/threshold variant.

## 12. Intraday-of-the-week EURUSD drift — R307

R307 used the published weekday-specific sign map: short EURUSD Monday/Tuesday, long Wednesday–Friday, from 08:05–12:00 Europe/London. At +1 pip incremental round-trip cost, discovery 2017–2020 produced 1,028 trades / -74.491R / PF_R 0.755; the contaminated 2021–2025 validation/diagnostic produced 1,281 trades / -53.462R / PF_R 0.854. Both were negative even at zero added cost, the 08:10 delay was worse, and the validation weekly-bootstrap 95% interval was wholly negative.

**Stop rule:** Close this sign map on the current periods. Do not reverse weekday directions or shift the session on the same years. The published broad intraday-of-week anomaly did not transfer into a cost-surviving EURUSD rule under this feed and execution model.

## 13. Weekend carry event-coverage failure — R308

R308 attempted a fixed LONG EURUSD held from Friday 21:00 UTC through the first executable quote five minutes after a genuine active Monday reopening. The data-only audit found just two observed >=24h Friday-to-Monday active gaps over 2017–2025, both around New Year closures rather than a recurring weekly FX reopening series. The preregistered minimum of 150 validation trades is impossible on these data.

**Disposition:** GAGAL — DATA/SAMPLE before PnL. Do not interpret this as evidence for or against weekend carry alpha, and do not relax the active-gap requirement or switch Friday entry time after seeing the scarcity. A valid future study needs a source with verifiable real FX weekly reopening timestamps plus broker financing assumptions.


## 14. Cross-asset FX/gold relative-value snapback — R309/R310 (2026-10-20)

### R309 — rolling-z residual snapback
- Mechanism: fade a one-hour extreme rolling-beta residual return in the paired EURUSD/XAUUSD feed.
- Baseline-cost results: discovery 2017–2020 = 3,576 trades, -991.56R, PF 0.338; diagnostic 2021–2025 = 3,665 trades, -644.44R, PF 0.512.
- Both periods lost even at zero *additional* costs. Every scored year 2017–2025 was negative. The four-week weekly-bootstrap 95% interval was wholly negative at [-2.939, -2.005]R/week.
- Failure lesson: a rolling z-score can return to normal because an older shock exits the rolling feature window, not because a position recovered.

### R310 — actual post-entry residual-move exit
- Parent: R309. Mutation: change exit geometry only; retain the registered signal, direction, beta estimate, cost model and timing.
- Baseline-cost results: discovery = 3,003 trades, -804.58R, PF 0.553; diagnostic 2021–2025 = 3,125 trades, -544.15R, PF 0.681.
- It reduced losses versus R309 but stayed negative even at zero additional costs; all nine scored years were negative; weekly-bootstrap 95% interval [-2.578, -1.604]R/week.
- Both R309 and R310 pass only the source-integrity and minimum-trade gates (2/8); both are GAGAL. No funded-challenge replay is permitted.
- Exact EURUSD repeated-flat filtering was matched to the data manifest: 696,795 repeated flat placeholders removed, 3,718,698 active paired minute timestamps, 736,076 complete M5 bars, and 732,199 exact common EURUSD/XAUUSD M5 timestamps. The XAUUSD 2026 outcome window remains unscored.
- Repository-only reproducibility remains a failed gate until the exact runner and full row-level ledgers are committed as ordinary files. The source audit, annual summary, cost/delay scorecard, bootstrap, and final report are archived.
- Stop rule: close this exact cross-asset snapback family. Do not flip direction or sweep the same z thresholds, beta lookback, exit barrier, or holding duration on inspected years. A genuinely distinct economic mechanism is required for the next batch.

Report: [R309/R310 batch final report](R309_R310_BATCH_FINAL_REPORT.md). Scorecard: [cost/delay scorecard](R309_R310_cost_delay_scorecard.csv). Annual results: [annual summary](R309_R310_annual_summary.csv). Data audit: [data audit JSON](R309_R310_data_audit.json). Bootstrap: [validation bootstrap JSON](R309_R310_validation_weekly_bootstrap.json).


## 15. R311 — Tokyo FX fixing post-event fade — CLOSED / GAGAL (2026-10-21 local)

- **Registered mechanism:** fade the 15-minute EURUSD midpoint-return sign ending at the Tokyo 09:55 fixing; delayed T+5 executable-side entry, 1R stop/target, 30-minute maximum hold.
- **Primary +1 pip extra-cost evidence:** discovery 2017–2020 = 750 trades, -360.843R, PF_R 0.3445; validation 2021 = 143 trades, -73.799R, PF_R 0.3161. Both period estimates were negative even at zero extra cost. Validation weekly block-bootstrap 95% interval was [-1.8635, -0.9933]R/week. The T+10 fade and matched follow-direction control were negative too.
- **Disposition:** close this exact rule and retain no alpha block. Do not reverse the sign, change the Tokyo event clock, or tune horizon/stops/targets against these already-inspected data. The outcome is evidence against this registered rule on this feed, not proof that all fixing-related mechanisms are impossible.
- **Execution/data lessons only:** require active BID/ASK rows on both sides, exact minute timestamps, complete M5 aggregation, explicit waiting bar between signal and delayed fill, exact entry/exit side, stop-first intrabar collision, and serialize grouped skip reasons as tabular JSON rather than tuple-keyed objects.
- **Reproducibility status:** code, preregistration, compact results and report are in GitHub. Full original CSV outputs are currently identified by local SHA-256 in [R311 manifest](R311_DATA_MANIFEST.md) but are not all ordinary committed row-level artifacts; therefore end-to-end repository artifact gate remains false until the artifact archive or full outputs are stored and read back.
- **Search governance:** follow the R312 stop/unblock contract. Do not launch R312 or another signal hypothesis on the same development windows until real-data funded-path replay and required repository reproducibility are complete. Next work is infrastructure/traceability, not a parameter rescue.

Report: [R311 final report](R311_FINAL_REPORT.md). Index: [R311 artifact index](R311_INDEX.md). Preregistration: [R311 locked preregistration](R311_EURUSD_TOKYO_FIX_POST_EVENT_REVERSAL_PREREGISTRATION.md).


## 16. R312 — challenge path integration audit (not an alpha family)

- Purpose: replay the already-failed R298 candidate through the paired-quote adapter and challenge engine to test the infrastructure, not find alpha.
- Result: the reconstructed R298 stream remained strongly negative (discovery -285.893R; validation -178.933R). One historical $6,000 account path at 0.5% risk breached static maximum loss after 26 closed trades. This is not a Monte Carlo pass-probability estimate.
- Disposition: infrastructure evidence only; no candidate promotion. Keep broker/account contract settings and actual server reset/timezone confirmation as separate unresolved gates.

## 17. R313–R316 — XAU follow-up families (closed / archive status varies)

- **R313 spread-shock normalization reversion:** reported diagnostic loss even at zero additional cost; close the family. The report/runner/full-ledger archive was not fully re-verified during the later process audit, so treat it as rejected exploratory evidence, not a reproduction-complete run.
- **R314 fixed NY clock-time drift:** 96 candidates, zero positive candidates at +$0.30/oz; best active clock/direction had 1,290 trades and -605.866R / PF 0.427. Close fixed-slot directional drift on the inspected sample; do not reverse/neighbor-slot rescue.
- **R315 compression-to-range breakout:** discovery failed sharply even at zero added cost: 1,280 trades, -1,102.961R, PF 0.0459 at +$0.30/oz. No validation was run after the discovery gate failed. Close this exact signal rule.
- **R316 prior-session momentum:** prior report notes were negative, but its complete source/result package was not read-back-verified here. Mark archive-incomplete and not promotable; do not treat the recorded summary as a complete reproduction.

## 18. R317/R318 — clean EURUSD M5 batch (closed / archive-incomplete)

- A strict repeated-flat placeholder audit removed 696,795 rows from the original EURUSD feed, leaving 3,718,698 paired M1 rows and 736,076 exact complete M5 bars. The earlier R317 preliminary table is invalid; the cleaned report supersedes it.
- R317 discovery was +39.398R / PF 1.138 at +0.5 pip, but validation was -37.264R / PF 0.888 at the same cost and -3.862R even with zero incremental cost.
- R318 screened 972 price-action configurations; its top five discovery-selected candidates all failed 2021–2025 diagnostic validation, with net R from -16.48R to -30.23R for the top five.
- **Process defect:** the original runner and full row-level artifacts were not recovered and read-back-verified. The cleaned summary is useful for rejecting these configurations, but the package cannot be described as end-to-end reproducible. Do not carry this archive gap forward; it remains a historical defect to learn from.

## 19. R319/R320 — H1/M15 pullback and H4 channel breakout (closed / reproducible generation, not formal preregistration)

- **R319:** 972 configurations, 11 met a 2016–2018 discovery screen; none passed the 2019–2020 confirmation or 2021–2025 diagnostic. Selected candidate had +17.038R / PF 1.208 discovery, -25.860R / PF 0.555 confirmation, -67.757R / PF 0.632 diagnostic at +1 pip incremental cost.
- **R320:** 162 configurations, only one met discovery selection. The selected candidate had +4.918R / PF 1.059 discovery, -5.173R / PF 0.917 confirmation, -2.286R / PF 0.983 diagnostic at +1 pip. At zero extra cost, diagnostic was only +5.677R / PF 1.045.
- Output generation was repeated twice with matching deterministic hashes after the gzip-header fix. Runners, restore script, result summaries and hashes are archived in [R319/R320 manifest](R319_R320_ARCHIVE_MANIFEST.md).
- **Process defect:** their registration/source was committed after outcome calculation, not before it. These were exploratory, not formally preregistered runs. Detailed row-level result files regenerate from the runners but are not all stored as static GitHub files. Do not represent this as satisfying the stronger v2 archival contract.

## 20. Forward process rule

The binding process rule is now [Search Process Improvement Protocol v2](SEARCH_PROCESS_IMPROVEMENT_PROTOCOL_V2.md). The next search is blocked until it passes v2 preflight. A negative market result can still count as progress; any regression in registration timing, data integrity, deterministic reruns or artifact completeness blocks the next hypothesis. Keep protected XAUUSD 2026 closed unless the registered pre-2026 gates pass.

## 21. Causal price-state prediction audit — R321 (2026-10-21)

- **Registered family claim:** whether causal return acceleration, 60-minute path efficiency, lag-1 return autocorrelation, or volatility-conditioned recent return predicts the next executable EURUSD move beyond simple 15/30/60-minute return scores. Signal sampling was sparse/non-overlapping at a fixed 65-minute cadence; entry was delayed five minutes after signal close; entry/exit used observed paired BID/ASK.
- **Result: R321 = GAGAL.** All 28 registered feature–horizon pairs were negative at the primary +1 pip incremental round-trip cost. Even with zero additional friction, the best pair (F6 autocorrelation state / 60 minutes) averaged -0.2568 pips/event, PF 0.934. At +1 pip it averaged -1.2568 pips/event, PF 0.716 over 48,879 events. The block-bootstrap weekly-return interval was wholly negative in discovery and confirmation.
- **Research lesson:** slight directional correlation is not an executable edge. The predictive-state variants did not overcome the spread and registered friction on this feed. Close the family; no direction flip, threshold tuning, or nearby horizon rescue on these same dates.
- **Process lesson and caveat:** two local reconstructed-runner replays produced identical scorecard, annual/cohort, bootstrap, event-ledger, and weekly-series outputs. However, the local runner bytes did not match the committed runner's blob, and full required row-level output readback from GitHub remains incomplete. R321 therefore does not yet pass the strict-v2 closeout invariant; next signal search stays blocked until exact-runner/reproducibility repair is completed.
- Artifacts: [R321 preregistration](R321_CAUSAL_PRICE_RELATIONSHIP_AUDIT_PREREGISTRATION.md), [final report](R321_FINAL_REPORT_20261021.md), [compact summary](R321_RESULTS_SUMMARY.json), [reproduction audit](R321_REPRODUCTION_AUDIT_20261021.md).


## 22. R321 exact-source reproduction — CLOSED / GAGAL EDGE (2026-10-21)

- The earlier reproduction caveat is superseded. The exact current runner (`research/R321_price_relationship_audit.py`, commit `25d8c2ac93b62f728fe68041a6b4804777077a8e`, Git blob SHA-1 `8afc5bd8b9206f4d772e585446228daa2640707b`) was executed twice locally. All eight generated output files matched exactly across the two clean runs, including the 56,633 × 70 event ledger and the manifest.
- Input source was restored from data artifact `11959096102` / acquisition run `38697080604`; ZIP size 67,719,731 bytes and SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e` matched the locally downloaded bytes. Archive currently expires 2027-01-13 07:11:24 UTC; refresh before expiry.
- R321 remains **GAGAL**: all 28 feature/horizon pairs were negative at +1 pip incremental cost. Best zero-extra-cost result was still negative (F6 autocorrelation state / 60m: mean -0.2568 pip/event, PF 0.934); at +1 pip mean -1.2568, PF 0.716.
- Process disposition: deterministic regeneration gate is now closed; full row-level output need not be stored as a huge Git blob because it is recreated and hash-verified from the source artifact + committed exact runner. This is a process pass, not a strategy pass. No 2026 PnL or challenge replay was performed.
- Audit: [official-source reproduction audit](R321_OFFICIAL_REPRODUCTION_AUDIT_20261021.md). Only a new economic hypothesis, frozen before its outcomes, may enter the next round; no sign, horizon or threshold rescue of R321.


## R322 — USD scheduled macro-release cascade — GAGAL / DATA-SAMPLE (2026-10-21)

- Registered hypothesis: a large first five-minute EURUSD midpoint move after a scheduled high-impact USD release continues after a further five-minute manual-entry delay. Entry, stop, target, clustering, costs and minimum samples were frozen in [R322 preregistration](R322_NEWS_CASCADE_PREREGISTRATION.md), with a pre-outcome timestamp-repair amendment committed after the calendar integrity audit.
- Calendar quality: of 2,828 high-impact USD rows, 1,199 midnight placeholder timestamps were replaced by the locked official Eastern schedule on the source-local calendar date; 544 non-midnight records validated; 107 schedule conflicts and one date mismatch were excluded; 977 out-of-family rows were excluded. The 1,743 retained rows became 973 episodes after the registered 40-minute clustering rule.
- Local price/calendar preflight used the hash-pinned EURUSD archive and exact committed R321 data cleaner. It evaluated no stop/target hits or PnL. Only 131 discovery (2016-2018) and 49 confirmation (2019-2020) setups met the locked signal, delay, risk-geometry and exact-path gates, below the registered 200/100 minimum completed-trade counts. There is no possible way for this rule to reach those minimums because at most one trade can arise per episode.
- **Disposition: R322 = GAGAL — DATA/SAMPLE.** Stop before outcome calculation. Do not tune thresholds, widen the calendar family, modify the schedule mapping, flip direction, or shorten delay on these dates. This is sample/execution feasibility failure, not evidence that no news edge can exist. No PnL, PF, drawdown or challenge pass probability was calculated; 2026 stayed unopened.
- The exact committed price/event preflight was run twice; its 973-row eligibility CSV hash matched both times: `5b58b271e20c0453e241e7a6f0259c453f0b3949fe04deada38a51dc31a90edf`. Its 2,184-byte summary JSON hash matched twice: `8546f87e94e3e3241110f91165fa5aeecd620ddef6856803c5a1d776a4f09a0b`. Outputs are deterministically regenerated from the committed scripts and independently hash-pinned input artifacts.
- Supporting files: [preflight report](R322_PREFLIGHT_REPORT_20261021.md), [machine summary](R322_PRICE_EVENT_ELIGIBILITY_PREFLIGHT.json), [official-source timestamp correction logic](r322_correct_event_times.py), [price/event preflight source](r322_price_event_preflight.py). Data-only calendar action: [run 39601019683](https://github.com/christianomomongan82-lang/scanner/actions/runs/39601019683).


## R323–R328 governance disposition — 2026-10-22

**Search is BLOCKED. No new strategy PnL, challenge replay or R329 registration is allowed until V2 package/ledger gaps are closed or explicitly recorded as unrecoverable.** EURUSD 2017–2025 is already contaminated across this project.

| ID | Mechanism | Underlying observed data/sample finding | Official project disposition |
|---|---|---|---|
| R323 | Cross-sectional USD-relative currency strength | 410 discovery legs vs 1,000; 270 confirmation vs 600; no PnL. | GAGAL — DATA/PROCESS; archive package is not V2 CLOSED. |
| R324 | Asian-range sweep then close-back-inside | 341 discovery vs 400; 222 confirmation vs 250; no PnL. | GAGAL — DATA/PROCESS; overlaps closed sweep/reclaim family and V2 preflight/novelty gate absent. |
| R325 | Fixed Asian-range breakout | 593 discovery vs 600; confirmation 441; holdout 306; no PnL. | GAGAL — DATA/PROCESS; overlaps R253 session breakout and R281 range/compression family. |
| R326 | Raw M5 impulse continuation | Exploratory local calculation was negative across discovery, confirmation and holdout: at +0.5 pip expectancy/PF = -0.250R/0.659, -0.209R/0.708, -0.264R/0.644; every year negative. | GAGAL — DATA/PROCESS / NOT CLOSED. Metrics are preserved as exploratory only because V2 pre-outcome review and complete repository archive were missing. |
| R327 | Overnight stretch fade | 342 discovery vs 500; 272 confirmation vs 300; 187 holdout vs 200; no PnL. | GAGAL — DATA/PROCESS; session/reversal novelty review not completed. |
| R328 | Rolling M5 compression breakout | 298 discovery vs 350; 233 confirmation vs 250; holdout 183; no PnL. | GAGAL — DATA/PROCESS; overlaps existing compression/session-breakout family. |

### Lessons and hard stop

- Data-quality passing and deterministic sample counts are not an experiment-level V2 pass. Preregistration, novelty review, V2 preflight, runner/dependency archive, row-level outputs, hash manifest and readback-verified closeout are separate mandatory gates.
- R323–R328 reused already-inspected EURUSD quote history. None creates a pristine project-level OOS result.
- R324, R325 and R328 are variants of already-covered session/range/rejection/breakout ideas; R326 is a near-duplicate momentum/impulse idea; R327 is a session-conditioned reversal idea. Do not produce more round-number variants of these mechanisms.
- R326's negative metrics are useful warnings but not a formally closed EDGE verdict under V2; preserve that distinction. Do not claim a funded-ready strategy exists.
- Restore/verify the exact R326 runner, normalized trade ledger, zero-inclusive weekly-R series, output manifest and package test evidence, or explicitly record the archive gate as irrecoverable. Also reconcile the pre-V2 R317/R318 and R319/R320 static archive gaps. Close/disposition the five old open scanner smoke-test issues.
- **Until these are done: no additional PnL search.** A compliance-blocked run is GAGAL — DATA/PROCESS; it cannot be converted into edge evidence by changing the strategy.

## Canonical reconciliation and research reset — 2026-10-22

**Canonical ledger:** [MASTER_SEARCH_LEDGER_R251_R328.csv](MASTER_SEARCH_LEDGER_R251_R328.csv). The CSV was rebuilt and read back from GitHub: 76 experiment rows, 15 columns each, unique IDs in ascending order from R251 through R328, with only R259/R267 absent for the reasons above. R300/R301 were restored from the prior preserved ledger; R302 was rebuilt from its linked final report. R312–R320 schema omissions were repaired by splitting combined period fields; R323–R328 were rewritten as correctly quoted CSV records. The file was parsed and verified after commit.

### Missing archive dispositions are now explicit, not an indefinite blocker

- **R317/R318:** historical signal outcomes remain GAGAL. Exact runner/full row-level output archives are absent from current repository evidence. Treat both as historical non-promotable records unless original artifacts are recovered; never claim end-to-end reproducibility or retune these families on inspected periods.
- **R319/R320:** deterministic runner/source restoration evidence exists, but the original registrations followed outcome calculation. They remain exploratory/non-promotable; no retroactive preregistration claim. Preserve the static-ledger gap as an exception, not as a reason to keep repeating the same archive audit.
- **R326:** current repository package lacks a complete verified runner + normalized trade ledger + zero-inclusive weekly series + complete output manifest. The negative outcome metrics are exploratory diagnostics only. Mark the package archive non-promotable from currently available repository evidence; do not use it to justify a parameter rescue.
- **R323:** the data gate and 7/7 process smoke tests passed, but the pre-outcome sample gate did not (410 discovery legs vs 1,000; 270 confirmation vs 600). No PnL was calculated. This is not a negative-edge finding.
- **R324/R325/R327/R328:** sample counts failed and/or the V2/novelty process was incomplete. No PnL was calculated. These are not evidence of negative expectancy; their overlapping/repeated families must not be mutated on the same inspected periods.
- **R300/R301/R302:** now represented in the canonical ledger. R300 and R301 lost their registered tests; R302 failed 5 of 8 historical promotion gates and remains GAGAL. These do not constitute promotable alpha.
- **R321:** process/reproduction PASS, signal GAGAL; all 28 registered raw-price/horizon relations were negative at +1 pip, and the best tested relation was negative even at zero added cost.
- **R322:** GAGAL at the frozen pre-outcome sample gate (131 eligible discovery setups vs 200 required; 49 confirmation vs 100); no PnL was calculated.

The five old scanner smoke-test issues (#1, #2, #3, #5, #6) were already dispositioned and closed in commit [aa3782f867dd4dcfc0dc7855987ad979b52c9056](https://github.com/christianomomongan82-lang/scanner/commit/aa3782f867dd4dcfc0dc7855987ad979b52c9056). They are not a current blocker.

### New search rules

1. Stop round-number variations of the existing EURUSD candle, session breakout, compression, sweep/reclaim and short-horizon momentum families.
2. Before any new signal PnL, require a candidate-specific immutable V2 registration and successful V2 preflight/readback, exact data manifest and runner/environment, source-time causal checks, frozen selection rule/cost grid/latency, and complete output plan.
3. The next research hypothesis should be a **portfolio-level economic mechanism**, not a renamed single-session trigger. A currency winner/loser relative-strength portfolio is a literature-backed lead only if the novelty audit proves it is materially different from R323's five-session intraday signal and a defensible fee/swap model is available. If not, reject it before PnL and choose another family.
4. Keep the primary objective tied to the real funded target: P(both phases completed by day 179 with no daily/max-loss breach), time-to-funded distribution, risk tails and costs. PF/expectancy remain necessary economic gates, not the end goal.
5. XAUUSD 2026 remains protected. Do not unlock it to select or rescue a candidate.

**Governance result:** the *historical ledger/family-map reconciliation* is now closed with explicit exceptions. This does not approve a new signal run. The continuing PnL stop is candidate-specific: no new outcome calculation until a genuinely distinct candidate's own V2 preflight passes. This is meant to be a one-time historical archive closeout, not another loop.
