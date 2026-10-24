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
8. Stellar two-phase path simulation: 10,000 paired bootstrap paths built from quarterly 2022–2026 trade cohorts; risk 0.5% and 1.0% per trade; aggregate open stop-risk capped at 2%; phase 1 +8%, phase 2 +5%, daily loss limit 5%, static max loss 10%, at least five distinct closing-trade server days per phase. At each risk, pooled pass-both-within-5-years>=65%, combined DLL/MLL breach<=25%, and pass-both probability strictly exceeds R191-only with no higher breach probability.
9. If any reported PF exceeds 1.4, perform an independent entry/stop/first-exit causal audit. Audit failure rejects the run.

Any failed criterion means REJECT. After REJECT, do not tune, remove instruments, test rescue variants, or rerun to salvage the result. Store all results and the verdict in research/, and append the outcome to PROJECT_STATE.md. Do not edit scan.py or the scanner workflow.
