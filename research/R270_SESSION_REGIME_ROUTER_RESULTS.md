# R270 — Asia-session regime router results

Date: 2026-10-16  
**Verdict: GAGAL.** The locked two-module router did not create a useful combined stream.

## Input and implementation

- Preregistration: [R270_SESSION_REGIME_ROUTER_PREREGISTRATION.md](R270_SESSION_REGIME_ROUTER_PREREGISTRATION.md).
- Source: raw-only GitHub artifact **11959096102**, data-acquisition run **38697080604**; Dukascopy EURUSD M1 BID/ASK, 2016-01-01 through 2025-12-31.
- Download ZIP SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- 4,415,493 common BID/ASK minute timestamps. 841,826 timestamps absent inside the full UTC span includes expected FX market/weekend closures; missing bars were not synthesized.
- Local calculations; no GitHub Actions backtest workflow was run. Executable BID/ASK sides were used, plus added-cost sensitivities of 0, 0.5, 1 and 2 pips/trade.
- Splits: discovery 2016–2020, validation 2021, exploratory forward 2022–2025. 2022–2025 is contaminated by prior research and is not an untouched promotion holdout. The archived data has no 2026 quotes.

## Locked-module coverage

A diagnostic over 2,605 eligible London weekdays found maximum observed Asia efficiency ratio (ER) **0.2101**, so Module A's preregistered ER >= 0.30 condition never triggered: **0 trades**. This is a coverage failure, not a reason to lower its threshold after seeing results.

Module B generated 577 trades overall: 290 in 2016–2020, 68 in 2021, and 219 in 2022–2025. The router is therefore exactly identical to B and adds no independent opportunity stream.

## Stream metrics by period

All results below include observed BID/ASK price-side execution plus the indicated *additional* cost. Net return and PF are measured in initial-stop-risk units (R).

| Stream | Period | Trades | PF at +1 pip | Net R at +1 pip | Net R at +2 pips |
|---|---|---:|---:|---:|---:|
| A | 2016–2020 | 0 | N/A | 0.00 | 0.00 |
| A | 2021 | 0 | N/A | 0.00 | 0.00 |
| A | 2022–2025 | 0 | N/A | 0.00 | 0.00 |
| B / router | 2016–2020 | 290 | 0.712 | -65.97 | -117.80 |
| B / router | 2021 | 68 | 0.639 | -20.16 | -34.35 |
| B / router | 2022–2025 | 219 | 0.628 | -63.50 | -96.00 |

Forward annual router results at +1 additional pip: 2022 = 55 trades, PF 0.555, -19.81R; 2023 = 45 trades, PF 0.626, -13.24R; 2024 = 58 trades, PF 0.644, -15.30R; 2025 = 61 trades, PF 0.683, -15.15R. All four years were negative.

Forward weekly net-R bootstrap at +1 additional pip (four-week circular blocks, 10,000 replicates; seed 2702026): mean -0.304R/week; only 0.14% of bootstrap means positive; 95% interval [-0.484, -0.115] R/week. This is strongly adverse, not merely inconclusive.

At +0 additional pips beyond observed quotes, B/router was already negative: discovery -14.14R, 2021 -5.96R, forward -30.99R. At +0.5 pips the net R was -40.06, -13.06, and -47.24 respectively; the extra-cost stress worsened the result.

## $6,000 challenge reference proxy

A 3,000-path four-week block bootstrap using fixed-fractional sizing, +8% then +5% targets, a $5,400 static floor, and a 5% UTC-day loss proxy was only a diagnostic—not the verified FundedNext engine.

| Risk per trade | Router P(Phase 1 pass) | P(both phases) | P(loss-rule proxy breach) |
|---:|---:|---:|---:|
| 0.25% | 0.0% | 0.0% | 28.1% |
| 0.50% | 0.7% | 0.0% | 85.5% |
| 0.75% | 2.9% | 0.4% | 95.5% |
| 1.00% | 7.3% | 1.1% | 97.9% |

At the same risks, router completion probability did not outperform both standalone streams without worse proxy breach probability. Higher risk made occasional target hits more common but drove breach probability to roughly 95–98%; this is not a viable improvement. The simulator's loss-rule timing/server reset and live account-specific costs are not verified, so none of these numbers are live pass-odds estimates.

## Preregistered gates and verdict

- **GAGAL:** router net R was negative in discovery and validation.
- **GAGAL:** Module A had zero trades; the architecture never formed a two-module router.
- **GAGAL:** four-week block-bootstrap lower bound was negative and all four forward years were negative.
- **GAGAL:** +2-pip forward net R was negative.
- **GAGAL:** target-completion proxy did not improve against both standalone streams at the same risk without worsening the breach comparison.
- **GAGAL:** there is no untouched independent promotion window and official funded mechanics are not fully verified.

**Conclusion:** close this exact R270 configuration. Do not lower the ER threshold, retune exits, or try to rescue the result on the same sample. Next test must use a structurally different hypothesis and be preregistered before validation.

## Reproducibility caveat

The raw-data artifact, preregistration, report, and compact JSON are referenced/stored on GitHub. The exact local Python runner and full row-level CSV ledger have not been committed to this branch in this session, so the complete signal/PnL calculation is **not yet fully reproducible from repository files alone**. The source artifact ZIP hash is recorded above, and the local run files exist in the execution environment; do not describe this result as fully self-contained until the runner and ledger are stored.
