# R311 Implementation Amendment 01 — Pre-Outcome Timestamp-Grid Audit

**Recorded before any R311 PnL calculation.** The first local implementation dry run produced no trade outcomes; it stopped at the empty-ledger aggregation because its coverage audit falsely rejected all dates. No PnL, win/loss, signal-performance summary, or outcome-based statistic was calculated in that attempt.

## Defect found

The first pre-outcome contiguity check tested the required risk bars through 09:50 Tokyo and then jumped directly to the 10:00 entry bar. It omitted the 09:55 M5 bar, which is the five-minute observation interval between the 09:55 signal close and the 10:00 delayed entry. Therefore every otherwise-present event was incorrectly labeled `noncontiguous_required_grid`.

## Frozen correction

Before any outcome run, require and audit the exact active M5 sequence:
`09:25, 09:30, 09:35, 09:40, 09:45, 09:50, 09:55, 10:00, 10:05, 10:10, 10:15, 10:20, 10:25, 10:30, 10:35` Tokyo local time.
Each adjacent timestamp must differ by exactly five minutes, each derived M5 bar must be formed from five active, exact, contiguous M1 rows on both BID and ASK, and no missing bar is synthesized. The 09:55 bar verifies the post-signal waiting interval; it is not used to form the signal return or the risk distance.

Separate shared signal/path eligibility from entry-specific T+5 and T+10 spread/risk eligibility. T+5 remains the primary execution; T+10 remains the preregistered delay stress. Signal, risk, direction, exit geometry, cost grid, time split, and pass/fail thresholds are unchanged.

This is a coverage-code correction detected before PnL, not a strategy mutation. The corrected runner and exact input/archive hash must be committed before the next outcome calculation.
