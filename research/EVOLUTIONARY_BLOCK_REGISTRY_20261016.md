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

