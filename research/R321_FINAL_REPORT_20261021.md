# R321 final report — causal EURUSD price-relationship audit
**Date:** 2026-10-21 UTC  
**Binary verdict: GAGAL.** No strategy is funded-ready; no FundedNext challenge replay was run.

## Test
Registered before outcome calculation. EURUSD Dukascopy BID/ASK M1; seven causal price/state scores × four horizons (28 relationships); fixed 65-minute sampling cadence; five-minute delay from signal close to entry; executable-side BID/ASK prices; incremental round-trip cost sensitivity +0/+0.5/+1/+1.5 pips, with +1 pip primary. Discovery 2016–2018, confirmation 2019–2020, contaminated diagnostic 2021–2025. All data from 2026-01-01 UTC onward remained protected.

## Data gate: PASS
- Paired raw M1 rows: 4,415,493.
- Repeated-flat placeholders removed: 696,795.
- Clean paired M1 rows: 3,718,698.
- Complete exact M5 bars: 736,076.
- Gaps over five minutes preserved, not filled: 7,882.
- Source ZIP SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- Cleaned M1 SHA-256: `b4e24c2b7078808b13e4c0cc38e130a99a449fdb441d5362e2dbd9254a45ee21`.

## Result: fail
All 28/28 registered feature–horizon pairs had negative average executable net pips even with zero additional friction. The best pair at zero added cost still averaged -0.2568 pips/event (net PF 0.934).

At the primary +1 pip cost, the strongest pair was F6_AUTOCORR_STATE at 60 minutes, 48,879 events: mean net -1.2568 pips/event, median -1.30, win rate 42.21%, net PF 0.716, Spearman rho 0.0127. The state scores' modest relative improvement over simple-return baselines did not create profitable expectancy.

Best result in each cohort at +1 pip:
- Discovery: F6 / 15m, 16,045 events, -1.2624 pips/event, PF 0.520.
- Confirmation: F6 / 60m, 10,287 events, -1.2379 pips/event, PF 0.688.
- Diagnostic (contaminated): F6 / 60m, 23,057 events, -1.2472 pips/event, PF 0.724.

The strongest full-sample pair was negative in all ten calendar years. Its weekly-average-net-pips four-week block-bootstrap 95% intervals were wholly negative overall (-1.3668 to -1.1771), discovery (-1.4819 to -1.1091), and confirmation (-1.4210 to -1.0735).

## Decision
**R321 = GAGAL.** Close this registered family. Do not flip direction, tune thresholds, or promote neighbouring variants using the same history. This is a research falsification audit, not a candidate strategy or funded-pass estimate. The next test must use a materially different economic mechanism and be preregistered before outcome scoring.

## Reproducibility caveat
The local reconstructed runner followed the committed R321 calculation logic and registered parameters; comments and unused imports were omitted. The local full 56,633-event ledger was read back and its schema/row count verified. The bootstrap uses weekly average event-level net pips, with no-event weeks zero-filled; it is not funded-account equity PnL. GitHub-only archival of the full outputs remains incomplete, so do not claim end-to-end repository-only reproducibility yet.
