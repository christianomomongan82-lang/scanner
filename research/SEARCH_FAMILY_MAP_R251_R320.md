# Search Family Map — R251–R320

Date audited: 2026-10-21  
Canonical ledger: [MASTER_SEARCH_LEDGER_R251_R320.csv](MASTER_SEARCH_LEDGER_R251_R320.csv)  
Scoring contract: [SEARCH_PROCESS_IMPROVEMENT_PROTOCOL_V2.md](SEARCH_PROCESS_IMPROVEMENT_PROTOCOL_V2.md)  
Experiment template: [EXPERIMENT_REGISTRATION_CARD_TEMPLATE_V2.md](EXPERIMENT_REGISTRATION_CARD_TEMPLATE_V2.md)

## Coverage statement

The original audited base contains 47 verified experiment/report records across R251–R299. The expanded canonical ledger now contains 65 records through R320 (including records R300–R320 and process/data-validity entries); R259 remains excluded as a workflow incident and no metrics are inferred for R267. The index covers this audited research generation; it is not an exhaustive ledger of every experiment numbered below R251. Older historical sections below retain their original audit context; addenda at the end cover R312–R320.

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
