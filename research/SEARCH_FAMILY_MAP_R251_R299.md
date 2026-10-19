# Search Family Map — R251–R299

Date audited: 2026-10-18  
Canonical ledger: [MASTER_SEARCH_LEDGER_R251_R299.csv](MASTER_SEARCH_LEDGER_R251_R299.csv)  
Scoring contract: [SEARCH_GOVERNANCE_AND_SCORING_V1.md](SEARCH_GOVERNANCE_AND_SCORING_V1.md)  
Experiment template: [EXPERIMENT_REGISTRATION_CARD_TEMPLATE_V1.md](EXPERIMENT_REGISTRATION_CARD_TEMPLATE_V1.md)

## Coverage statement

The normalized ledger contains 47 verified experiment/report records across R251–R299. R259 is excluded because the checkpoint explicitly calls it an accidental workflow incident, not an accepted experiment. No standalone R267 report/result was surfaced in this audit, so no R267 metrics or verdict are inferred. The index covers the audited recent generation; it is not an exhaustive ledger of every experiment numbered below R251.

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
