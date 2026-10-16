# R276–R279 — US cash-open breadth evolutionary batch (2026-10-17)

## Summary decision

No candidate is promoted for funded challenge use. R276 passed its locked historical statistical screen but failed promotion-level requirements: its 2026 diagnostic was negative, holding periods extended to nearly 60 days, and the preregistered full funded-challenge path comparison was not run. R277, R278 and R279 are **GAGAL** under their locked screen gates.

The four registered tests used the same four US-index M5 BID datasets, with discovery 2017–2021, exploratory forward 2022–2025 and diagnostic 2026. The latter two intervals have been repeatedly viewed in prior project research and are not clean untouched holdouts. All cost figures are modeled round-trip 1/2 price bps on BID-only data, not measured prop-firm/broker execution costs.

## Candidate scoreboard

| ID | Structural change | Discovery trades | Discovery PF +2 bp | Forward trades | Forward PF +1 / +2 bp | Forward net R +1 bp | 2026 PF +1 bp | Decision |
|---|---|---:|---:|---:|---:|---:|---:|---|
| R276 | 3-of-4 simultaneous same-direction breakout; T+10; 2R; no forced session flat | 767 | 1.138 | 828 | 1.289 / 1.257 | +147.06R | 0.748 | Historical screen PASS; **not promoted** |
| R277 | R276 with mandatory 16:00 NY flat, both directions | 842 | 0.989 | 969 | 1.187 / 1.139 | +71.25R | 0.916 | GAGAL |
| R278 | R277 long-only upper breakouts, fixed 2R, 16:00 flat | 435 | 0.889 | 508 | 1.403 / 1.346 | +69.10R | 0.877 | GAGAL |
| R279 | R278 with fixed 2R target removed | 435 | 0.873 | 508 | 1.395 / 1.339 | +67.80R | 0.877 | GAGAL |

## What the controlled changes taught us

- **Breadth composition (R276):** the 3-of-4 router increased mean R/trade and reduced historical forward drawdown versus the matched T+10 parent, but reduced trade count enough that total forward net R was lower than the unfiltered parent (147.06R vs 176.09R). It also lost in the project-contaminated 2026 diagnostic, with median hold 17.83 hours, p95 124.63 hours and maximum hold about 60 days. That is incompatible with promotion without a tested account-equity path and verified swaps/costs.
- **Same-day flat (R277):** controlled overnight duration, but discovery PF at +2 bp fell below 1.00, 2024 PF at +1 bp was 0.794, and the four-week bootstrap interval crossed zero (mean 0.341R/week; 95% CI −0.116 to 0.793). GAGAL.
- **Long-only (R278):** forward statistics looked materially stronger (PF 1.403 at +1 bp), and annual/weekly bootstrap gates passed; however discovery PF at +2 bp was only 0.889 and 2026 diagnostic PF at +1 bp was 0.877. GAGAL.
- **No fixed target (R279):** failed the same discovery PF gate and did not improve the R278 sibling: forward net R fell from 69.10R to 67.80R, PF from 1.403 to 1.395 and max DD rose from 17.26R to 17.99R. The evidence does not support removing the 2R target.

## Reproducibility and input limits

Source artifact IDs: 11709864394 (USA500), 11710370389 (USATECH), 11710730507 (USA30), 11710111254 (USSC2000). The USSC2000 series starts in August 2018; all child synchronized events require timestamp coverage in all four feeds, so earlier candidate events were excluded. No missing bars were forward-filled or synthesized by the research runner. The snapshots are BID-only. Actual index CFD spreads, commission, slippage, swap/overnight charges and contract multipliers are not independently verified.

Full two-phase challenge replay with daily floating equity, 5% daily loss, 10% static maximum loss, server-day resets, fees/swaps and Quick Strike compliance was not run. No candidate should be described as funded-ready. R276–R279 are stored as reports and compact results; the full row-level trade ledgers and local Python runners are not yet committed to GitHub and remain a reproducibility gap to close before relying on GitHub as the sole source of truth.

## Next search direction

Do not loosen these gates or keep tuning the same cash-open breakout family. A later generation should be a genuinely distinct hypothesis and should preserve the same causal timing, matched parent/child ablations, cost stresses, yearly stability and challenge-target completion objective. The full challenge replay belongs after a strategy qualifies, not as a substitute for a positive edge.
