# R288 — Cross-Index Residual Follow-Through: Final Report

**Binary verdict: GAGAL.** The locked follow-residual child failed eight preregistered gates. No threshold, direction or timing rescue is allowed on the same test periods.

## Question tested
R287’s fade stream was negative in both development and validation, while its opposite-direction stream looked materially better. Because that side-by-side selection was post hoc, R287’s older sample could not validate the opposite direction. R288 therefore locked a new child and calculated its post-entry PnL only for 2022–2026.

## Frozen method
- Instruments: USA500, USATECH, USA30 and USSC2000.
- On complete, quality-eligible New York RTH sessions, signal return is 10:00 ET open to 12:55 ET close. Residual is symbol return minus the same-date median across at least three eligible symbols.
- Per-symbol Q75 of absolute residual is fitted on 2017–2020 only. Choose the symbol with the highest normalized absolute residual per day; alphabetical tie-break; minimum score 1.
- Follow the residual sign; enter 13:05 ET bar open and exit 15:55 ET bar open. At most one event per session.
- All four sources are M5 BID-only snapshots from R205 run 38160487617. Hypothetical round-trip costs are 1, 2 and 4 bp; they are not verified provider execution costs.

## Results — follow-residual candidate

| Period | Trades | PF at 1 bp | Net at 1 bp | PF at 2 bp | Net at 2 bp | PF at 4 bp | Net at 4 bp |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2022–2025 | 718 | 0.835 | -2,671.34 bp | 0.795 | -3,389.34 bp | 0.721 | -4,825.34 bp |
| 2026 later check | 154 | 1.019 | +37.54 bp | 0.943 | -116.46 bp | 0.807 | -424.46 bp |

### Annual detail at 2 bp
| Year | Trades | PF | Net |
|---|---:|---:|---:|
| 2022 | 196 | 0.718 | -2,070.10 bp |
| 2023 | 174 | 1.223 | +623.63 bp |
| 2024 | 187 | 0.922 | -212.10 bp |
| 2025 | 161 | 0.529 | -1,730.78 bp |

Only one of four 2022–2025 years was positive. Four-week circular block bootstrap for weekly net returns at 2 bp: mean -16.22 bp/week, 95% CI [-32.80, -0.30] (209 weekly observations; 5,000 replicates; seed 288). This supports a negative average weekly result over this sample.

## Matched same-event diagnostic (not a promoted strategy)
Fading the exact same selected events produced 718 trades and PF 1.035 / +517.34 bp over 2022–2025 at 2 bp cost, but PF fell to 0.940 and net fell to -918.66 bp at 4 bp. In 2026 the fade parent was negative at all three cost settings. It is not promoted: this paired diagnostic is exploratory and fails cost robustness.

## Failed gates
- 2022–2025: positive net at 2 bp, PF >= 1.05 at 2 bp, at least three positive years, PF >= 0.90 at 4 bp, and positive lower 95% bootstrap bound all failed.
- 2026: positive net at 2 bp, PF >= 1.00 at 2 bp, and positive net at 4 bp all failed.
- Trade-count gates passed, but that does not compensate for negative expectancy.

## Data quality, reproducibility and limits
Eligible sessions in the filtered source: USA500 2,409; USATECH 2,421; USA30 2,417; USSC2000 2,018. The latest source timestamp was 2026-10-09 20:10 UTC. Eligibility requires exactly 78 expected five-minute RTH bars, valid OHLC and no repeated-flat candidates; repeated-flat filtering is heuristic.

The source files are BID-only. Results do not model verified ask-side fills, the provider’s actual spread/slippage, contract multipliers, commissions or swaps. This is not a funded challenge simulation; no account-equity path with floating PnL, daily loss and max loss rules was run. The 2022–2025 period has been repeatedly used elsewhere in the project and is contaminated for program-level OOS; 2026 is only a later chronological diagnostic, not claimed as pristine program-level holdout.

**Evolutionary disposition:** retain the synchronized-session data-quality controls, frozen threshold fitting, deterministic event matching and matched-direction ablation as research methods only. Retain neither direction as an edge-backed signal block. The next generation must begin from structurally distinct/evidence-supported components, be preregistered, and optimize the probability/time profile of completing the two funded targets before breach—not PF in isolation.

## Archived row-level ledger

The paired event outcomes are archived as [R288_trade_ledger_outcome_compact.csv.gz](R288_trade_ledger_outcome_compact.csv.gz): 872 selected events, each stored once for the follow-residual candidate and once for the matched fade diagnostic (1,744 rows). The ledger contains gross basis-point returns; the preregistered modeled 1/2/4 bp costs are subtracted consistently by the replay runner.
