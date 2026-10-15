# R268 — Fixed-Fractional Compound Portfolio Diagnostic Results

Date: 2026-10-16  
**Verdict: GAGAL.** No tuning was performed. The portfolio lost money across discovery, validation, and forward periods.

Preregistration: [R268_COMPOUND_PORTFOLIO_PREREGISTRATION.md](R268_COMPOUND_PORTFOLIO_PREREGISTRATION.md)  
Runner: [r268_compound_portfolio.py](r268_compound_portfolio.py)  
Machine-readable summary: [R268_compound_portfolio_results.json](R268_compound_portfolio_results.json)

## Fixed setup

- Components: R262 EURUSD H4 structural pullback and R263 USA500/USATECH cash-open ORB, each using its five-minute delayed trade ledger.
- Additional cost: +1.0 pip per EURUSD R262 trade, +4.0 bps per index R263 trade.
- Starting equity $6,000; fixed fractional risk 0.25% of realized equity per accepted trade; maximum open initial risk 1.00% of realized equity. New signals are skipped if the cap would be exceeded.
- PnL is realized at saved exit events. Later trade size uses the updated equity, so this is a compounding simulation.
- The two component strategies were previously tested individually. This is a retrospective portfolio diagnostic, not independent proof of alpha. No outcomes after 2025 were used.

## Compounded equity results

Each historical split resets to $6,000 so period metrics are comparable.

| Period | Trades accepted | PF in net R | Net R | Ending equity | Return | Closed-equity max DD |
|---|---:|---:|---:|---:|---:|---:|
| Discovery 2016–2020 | 2,937 | 0.767 | -376.55 | $2,305.82 | -61.57% | 62.14% |
| Validation 2021 | 592 | 0.827 | -50.87 | $5,270.80 | -12.15% | 13.79% |
| Forward 2022–2025 | 2,399 | 0.823 | -225.18 | $3,374.61 | -43.76% | 44.60% |

No trades were omitted by the 1% open-risk cap in these runs. Therefore the cap did not improve this portfolio's recorded results.

## Forward yearly results

Each year below is separately compounded from $6,000, not chained from the prior year's ending balance.

| Year | Trades | PF in net R | Ending equity | Return | Closed-equity max DD |
|---|---:|---:|---:|---:|---:|
| 2022 | 593 | 1.009 | $6,018.14 | +0.30% | 7.12% |
| 2023 | 604 | 0.803 | $5,032.73 | -16.12% | 17.53% |
| 2024 | 598 | 0.746 | $4,836.73 | -19.39% | 19.67% |
| 2025 | 604 | 0.766 | $4,975.76 | -17.07% | 17.92% |

The four-week circular block bootstrap on forward weekly PnL, including zero-trade weeks, estimated mean weekly PnL of -0.208% of the reference $6,000 equity. Its 95% interval was [-0.315%, -0.102%]; none of 10,000 bootstrap means was positive.

## Component-level results in forward 2022–2025

| Component | Trades | PF in net R | Sum net R |
|---|---:|---:|---:|
| R262 EURUSD | 479 | 0.561 | -169.01 |
| R263 USA500 | 969 | 0.912 | -42.78 |
| R263 USATECH | 951 | 0.967 | -13.39 |

The joint portfolio fails because the combined forward PF is below 1.10, the net result is negative, three of four forward years lose money, the bootstrap interval is negative, and closed-equity drawdown exceeds 10%.

## Funded-rule implication

With a $6,000 reference account and a static 10% maximum-loss floor of $5,400, the forward closed-equity curve first falls below the floor on **2023-05-26 04:06 UTC** at $5,392.91. A challenge simulation would terminate there under that static floor; the rest of the forward curve is shown only as a research diagnostic. Floating intratrade losses are unavailable, so the actual rule breach could be earlier. This is not a challenge-pass probability estimate.

## Research-integrity qualification

The component outputs had already been inspected before the portfolio weights and risk overlay were set. This retrospective blend cannot be promoted based on the same periods, even if an aggregate metric had looked good. Here it also fails every major economic gate. Keep R262/R263 closed; do not tune their settings to rescue this blend.

## Data and execution limitations

- R262 and R263 are saved trade ledgers, not full tick-by-tick equity paths.
- Closed-equity drawdown does not include floating drawdown.
- The test does not exactly replay FundedNext's daily loss limit, the actual funded server/DST mapping, live slippage/commission, or Quick Strike close-duration measurement.
- The index cost is fixed +4 bps stress, not a directly observed live fill-cost distribution.
- Both component and combined tests end in 2025. No 2026 outcomes were used.


## Repository reproducibility audit — GAGAL

The numerical replay above was executed locally from these environment inputs:
- R262 trade ledger: R262_trades_delay_5m.csv (SHA-256 35ef952871ecef2dad363e47a9dd998d784501baebacb89910e936cb41e256ef).
- R263 trade ledger: R263_ORB_trades_delay_5m.csv (SHA-256 7a3acec0c4dc6c2e973f4ae52fb0d43c53ada7c60d8ad6d70990385430ef4e4b).

The exact two input trade-ledger CSVs are **not present as repository files on this branch**. The R268 runner is archived, but it expects those local CSV paths. The R262/R263 reports and result JSONs exist in GitHub; that is not enough to reconstruct the exact combined entry/exit stream. Therefore **repository-only reproduction of R268 is GAGAL**. Do not describe the current GitHub state as fully self-contained for this run. This is a storage/reproducibility failure separate from the economic verdict, which is also GAGAL.
