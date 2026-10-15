# R260–R269 Failure Taxonomy — strategy-family diagnosis

Date: 2026-10-16  
**Portfolio/funded approval status: GAGAL.** No strategy in this range has passed the full execution-aware promotion gates. This document is a cross-experiment diagnosis, not a fresh performance backtest.

## Why this review exists

Repeatedly inventing single-entry variants on the same instruments, feed and 2022–2025 period creates selection bias. Every individual candidate still gets a binary verdict, but the family map should be used to avoid retuning failed hypotheses. A good-looking aggregate PF from a period already inspected is exploratory evidence only, not a fresh holdout.

## Candidate-family map

| Family | Experiments | Observed result | Current decision |
|---|---|---|---|
| Large-bar/shock reversal | [R260 report](R260_LOCAL_SHOCK_REVERSAL_RESULTS.md) | EURUSD H1; 7,961 trades. Forward 2022–2025 PF 0.438 at +1 pip; net −8,654.5 pips; bootstrap weekly 95% CI [−49.24, −34.51] pips/week. High frequency did not fix negative expectancy. | **GAGAL; close family variant** |
| London impulse continuation | [R261 report](R261_LONDON_IMPULSE_RESULTS.md) | Forward PF 0.984 at +1 pip; only 612 trades total. Discovery PF 0.938 and validation PF 1.574; forward annual results were mixed and four-week bootstrap crossed zero. | **GAGAL; no threshold rescue** |
| H4 structural pullback | [R262 report](R262_H4_STRUCTURE_PULLBACK_RESULTS.md) | Forward PF 0.815 after +1 pip; subsequent R268 delayed portfolio ledger showed component PF 0.561 over 479 forward trades. | **GAGAL; do not retune into R268** |
| US cash-open opening-range breakout | [R263 report](R263_US_CASH_OPEN_ORB_RESULTS.md) | Failed its standalone preregistered gates. On R268 delayed portfolio stream, USA500 had PF 0.912 over 969 trades and USATECH PF 0.967 over 951 forward trades at the modeled stress. | **GAGAL; close this variant** |
| US opening-gap fade | [R264 report](R264_US_OPENING_GAP_FADE_RESULTS.md) | Failed standalone economics/gates. | **GAGAL; do not treat as complementary edge** |
| Index relative-value mean reversion | [R265 audit](R265_EXPLORATORY_AUDIT.md) | Only 41 forward trades; PF 1.395 ideal / 1.313 delayed at +4 bps, but bootstrap interval crossed zero and no contemporaneous preregistration was found. | **GAGAL; exploratory and underpowered** |
| Strong-morning afternoon continuation | [R266 report](R266_INTRADAY_DRIFT_RESULTS.md) | Forward PF 1.145 ideal / 1.102 delayed at +4 bps over 725 trades, but discovery/validation were negative, 2023/2024 forward years were negative, and weekly bootstrap intervals included zero. | **GAGAL; apparent forward PF does not clear robustness gates** |
| Last-hour momentum to next RTH open | [R267 report](R267_LAST_HOUR_OVERNIGHT_PILOT.md) | Retrospective pilot: forward PF 0.878 ideal / 0.857 delayed at +4 bps; net negative and bootstrap uncertain. | **GAGAL; not a preregistered candidate** |
| Blend of EURUSD H4 pullback + US index ORB | [R268 report](R268_COMPOUND_PORTFOLIO_RESULTS.md) | Forward 2,399 trades, PF 0.823; $6,000 compounded to $3,374.61 (−43.76%); closed-equity DD 44.60%; static $5,400 floor crossed in 2023. | **GAGAL; combining failed streams did not create edge** |
| London Asian sweep/reclaim reversal | [R269 report](R269_LONDON_ASIAN_SWEEP_RESULTS.md) | Forward 242 trades, PF 0.657 and −78.91R at +1 pip; bootstrap 95% CI [−0.661, −0.078] R/week. Compounded equity crossed the $5,400 floor in 2024. | **GAGAL; close, no retuning** |

## Cross-family conclusions

1. **Frequency is not the bottleneck by itself.** R260 generated thousands of trades and still had strongly negative expectancy. A portfolio cannot be fixed by adding volume from another negative stream.
2. **Apparent forward-only success has not been robust enough.** R265 is too small/retrospective; R266's favorable aggregate forward PF conflicts with negative discovery and validation, negative years, and a bootstrap interval crossing zero.
3. **Execution horizon matters.** R189's delay audit already showed meaningful decay with five-minute manual execution latency. Candidates requiring rapid M1 handling should not be treated as usable in the user's email-to-MT5-phone workflow.
4. **Portfolio allocation is downstream of edge.** R268 showed that fractional-risk compounding and an aggregate open-risk cap do not repair negative components. Compounding amplifies both positive and negative expectancy.
5. **2022–2025 is no longer a clean untouched final holdout for this research program.** It has been repeatedly inspected across multiple candidate families. A newly authored strategy tested on those same years may be useful for exploration, but a LULUS there alone would not establish independent evidence after this amount of multiple testing.

## Decision for the next research stage

Do not run another near-duplicate M1 reversal, intraday momentum, cash-open ORB, or H4 pullback merely by changing thresholds. The next hypothesis should have an explicit economic rationale distinct from the closed families and a horizon compatible with a five-minute delay. Its first test should still be labeled GAGAL for promotion if the gate fails, and should not be tuned after inspecting any validation/forward results.

For a meaningful promotion claim, reserve genuinely future/untouched observations or an independent instrument/feed window. Do not use the same 2022–2025 aggregate as if it were still virgin OOS evidence. Before any new experiment, save its hypothesis, entry/exit semantics, spread/commission stress, latency, instrument/session definitions, and binary gates to GitHub.
