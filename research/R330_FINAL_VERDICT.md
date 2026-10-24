# R330 FINAL VERDICT — REJECT at Gate 1

**Verdict: REJECT.** The persisted R191 manual5m two-index baseline has the expected 70 closed forward trades, but it does not reproduce the required PF@1bp=1.247. Observed PF is **1.491** after the same R192 trade-cost calculation. Under the locked instruction, this mismatch stops the round here.

## Gate 1 — R191 reference replication: FAIL

| Item | Required | Observed |
|---|---:|---:|
| Forward closed trades, USA500 + USATECH | 70 | 70 |
| PF @ 1bp, rounded to three decimals | 1.247 | 1.491 |
| Verdict | exact match | **FAIL** |

Observed raw PF: 1.490731327838. The archived trade ledger contains 72 forward entries, of which 70 closed before 2026-01-01 and 2 were censored. Using the helper's net-return convention, winning R sum = 59.891385367 and absolute losing R sum = 40.175841380.

**Reference evidence:** [R194 Actions run 38133085545](https://github.com/christianomomongan82-lang/scanner/actions/runs/38133085545), artifact `R194-ten-index-audit` (artifact ID 11700178416), cached common data cutoff 2026-10-09T20:00:00Z. The check used its persisted `trades.csv`, filtered to `mode=manual5m` and USA500 + USATECH, forward entries 2022-01-01 through 2025-12-31, closed outcomes before 2026-01-01. Cost calculation is identical to the R192 helper convention: net R = (exit − entry − entry × 1/10,000) / risk_points; PF = total positive net R / absolute total negative net R.

## Hard stop and remaining criteria

- **Gate 2 (truncation across all ten indices): NOT RUN in this R330 round.** Gate 1 failed first, so the sequential hard-stop rule prevents proceeding.
- Pooled forward n/PF, discovery PF, worst-year PF, N=40/55/80 neighborhood, leave-one-out, challenge simulator, correlation/overlap exposure, and causal path audit: **NOT RUN** in this R330 round.
- No 2026 OOS performance or challenge bootstrap results are reported. No index was excluded, and no parameter was changed.

The archived PF above is greater than 1.4; however, it belongs to the failed replication preflight, not a validated pooled candidate.

A **ledger-only consistency audit** of all 70 forward USA500/USATECH trades passed these checks: exact M5 entry timestamp; entry at least five minutes after signal close; risk points equal entry minus SL; TP equals entry + 2R; exit not before entry; TP/SL exit price matches the stored level; and gap-stop fills are at or below the stop. The recorded exits were 38 SL, 30 TP, and 2 SL-gap fills.

This is **not a full causality pass**: the archived artifact does not contain raw OHLC, so it cannot independently establish that the SL equals the trailing 27-H4-bar low or that the recorded exit was the first causal M5 stop/target hit. The corrected Actions runner includes this full path audit when PF > 1.4 and still hard-stops at Gate 1 if the replication mismatch remains. The required reproduction does not match.

## Decision

**REJECT. Stop at Gate 1.** Do not run tuning, neighborhoods, leave-one-out, or a challenge simulator to rescue this round. The root issue to resolve separately is why the persisted two-index baseline yields PF 1.491 while the required reference is 1.247; this report does not speculate about the cause.
