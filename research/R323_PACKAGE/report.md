# R323 terminal report

**Verdict: GAGAL — DATA/SAMPLE**  
**Failure class:** DATA/PROCESS  
**First failed gate:** minimum sample  
**Strategy PnL computed:** NO

## Exact pre-outcome counts

| Period | Eligible legs | Eligible active dates | Required legs | Required dates | Gate |
|---|---:|---:|---:|---:|---|
| Discovery 2017–2020 | 410 | 205 | 1,000 | 500 | FAIL |
| Confirmation 2021–2023 | 270 | 135 | 600 | 300 | FAIL |
| Diagnostic 2024–2025 | 166 | 83 | Diagnostic only | Diagnostic only | Not promotable |

The raw source passed integrity checks: 14 BID/ASK streams, 78,361 timestamps per stream, exact BID/ASK pairing, no duplicate timestamps, no invalid OHLC, no misaligned H1 timestamps, no negative opening/closing spreads. The corrected source audit records 36 gaps over one hour in each raw stream and each pair-common series; missing periods remain missing.

The 5-session ranking and the prior-20-session risk window use UTC weekdays only. The original zero-gap report and weekend-inclusive sample counts are superseded. The corrected eligibility result was regenerated in two clean Python processes, with byte-identical outputs. The local V2 validator tests passed 7/7.

**Per the frozen rule, calculation stopped before any PnL.** Net R, PF, drawdown, annual profitability, weekly net-R and bootstrap are deliberately `NOT CALCULATED`; blank trade and weekly ledgers are not zero-PnL samples.

This result does **not** establish that currency strength lacks a tradable edge. It establishes that this specific R323 setup does not meet its predeclared evidence-size gate. R323 is closed without tuning or relaxing its thresholds.

Historical data through 2025 is project-contaminated, and 2026 remains excluded. No funded-readiness or pass-probability claim is supported.
