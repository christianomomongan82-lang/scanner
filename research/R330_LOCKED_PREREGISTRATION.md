# R330 — Locked preregistration

Status: locked before pooled forward/OOS calculations. Branch: research/r330-r191-pooled-ten-index.

## Candidate and universe
Apply the unchanged R191 rule to every index in the existing ten-index R195 universe: USA500, USATECH, USA30, US Small Cap 2000, Germany 40, FTSE 100, France 40, EU Stocks 50, Australia 200 and Japan 200. No index selection or removal.

- Long-only; America/New_York wall-clock H4.
- Signal: completed H4 close exceeds the preceding 55 H4 highs.
- Stop: lowest low over the signal H4 bar and preceding 26 H4 bars (27 bars inclusive).
- Target: 2R.
- Manual entry proxy: first non-flat M5 BID bar at/after signal close +5 minutes and before the next actual NY H4 close.
- M5 BID OHLC exits, stop checked first when stop and target overlap; gap through stop fills at the open.
- Candidate parameters are frozen at N=55, M=27, RR=2. N=40 and N=80 are robustness-only diagnostics; they cannot replace the candidate.

## Periods and costs
Discovery entries: 2017-01-01 through 2021-12-31, with outcomes closed before 2022-01-01. Forward entries: 2022-01-01 through 2025-12-31, with outcomes closed before 2026-01-01. OOS entries: 2026 through the common cutoff, opened only once after both hard gates pass. All reported trade-cost sensitivities use modeled round-trip price costs of 1, 2 and 3 basis points.

## Sequential hard gates
1. Reproduce the existing USA500+USATECH R191 manual-execution forward result: n=70 and PF@1bp=1.247 rounded to 3 decimals. If mismatch, stop immediately.
2. R191 signal and stop prefix/truncation checks pass on all ten indices. If any fails, stop immediately.
3. Pooled forward: n>=150 and PF@2bp>=1.15.
4. Pooled discovery PF@2bp>=1.00.
5. Worst of all four pooled forward entry-year cohorts PF@2bp>=0.80; every year must have closed outcomes.
6. Pooled forward PF@2bp>=1.00 for each robustness-only N=40, 55, 80. Candidate N/M/RR remains 55/27/2.
7. Each leave-one-index-out pooled forward portfolio PF@2bp>=1.05.
8. Stellar two-phase path simulation: 10,000 paired bootstrap paths built from quarterly 2022–2026 trade cohorts; risk 0.5% and 1.0% per trade; aggregate open stop-risk capped at 2%; phase 1 +8%, phase 2 +5%, daily loss limit 5%, static max loss 10%, at least five distinct closing-trade server days per phase. For open-position mark-to-market, record daily M5 low/high extrema and the last pre-exit close; process adverse low before high if both occur in one bar, process entry before marks on the entry bar, and process same-bar exits after the entry/marks. At each risk, pooled pass-both-within-5-years>=65%, combined DLL/MLL breach<=25%, and pass-both probability strictly exceeds R191-only with no higher breach probability.
9. If any reported PF exceeds 1.4, perform an independent entry/stop/first-exit causal audit. Audit failure rejects the run.

Any failed criterion means REJECT. After REJECT, do not tune, remove instruments, test rescue variants, or rerun to salvage the result. Store all results and the verdict in research/, and append the outcome to PROJECT_STATE.md. Do not edit scan.py or the scanner workflow.


## Amendment — Gate 1 entry convention (2026-10-24)

This amends the definition of Gate 1 only; it does not change any PASS threshold or downstream criterion.

- Canonical mode is entry at the open of the next New York wall-clock H4 bar. The Gate 1 reference targets are: selection n=78/PF@1bp=2.082; forward n=70/PF@1bp=1.247/PF@2bp=1.241; 2026 OOS n=11/PF@2bp=1.954. All comparisons are to three decimals.
- manual5m is retained as a separate diagnostic table and must never be used for Gate 1 or other PASS/FAIL decisions when canonical is the primary convention.
- If any canonical reference value fails, stop and report exact observed values. Status must be GATE-MISMATCH (definisi konvensi entry), strategi belum dievaluasi—not a strategy performance REJECT.
- The specifically named R191_CANONICAL_index_trend_long.py was not present in the available tracked repository. The R192 ideal mode is the available implementation that opens at the next H4 bar and is explicitly labelled canonical-equivalent if used.
- All pooled PASS criteria remain exactly as originally locked. No tuning, variant, or instrument removal is allowed after a gate mismatch.
