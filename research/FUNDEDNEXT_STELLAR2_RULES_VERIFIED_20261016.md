# FundedNext Stellar 2-Step CFD — Official Rule Verification

**Verified on:** 2026-10-16  
**Scope:** current public FundedNext CFD Stellar 2-Step challenge rules. Recheck before any purchase because platform terms can change.

## Rule matrix for the $6,000 reference account

| Rule | Official requirement | Dollar / implementation implication |
|---|---|---|
| Phase 1 target | +8% of initial phase balance | $6,480 closed balance target; +$480 closed P&L |
| Phase 2 target | +5% of initial phase balance | Fresh $6,000 Phase 2 reference; $6,300 closed balance target; +$300 closed P&L |
| Daily loss limit | 5% of initial account balance; reset at 00:00 server time | $300 daily limit. Includes today's closed trade results plus current floating P&L, commission, swap and fees. |
| Maximum loss limit | 10% of the phase's initial balance; static floor | Equity/balance must not fall below $5,400 on the $6,000 reference account. Floating loss counts. |
| Minimum trading days | At least five separate calendar days, with at least one trade on each | Track dates of actual trade entries using server calendar dates. |
| Time limit | No maximum time limit | Slow-but-profitable is permitted by the rules, but the project's own speed gate still applies. |
| Quick Strike | Must remain strictly below 30% during the Challenge | Profitable trades closed within 30 seconds contribute to the Quick Strike profit numerator. At 20%, a warning is issued; at 30% or above, progress is held until below the threshold. |
| Phase target measurement | Closed-position P&L | Floating profit does not count toward target attainment, though floating P&L counts toward loss limits. |
| Server clock | Seasonal GMT+2 outside DST and GMT+3 during DST | Daily reset cannot be simulated with fixed UTC midnight. The exact server mapping must be checked against the actual platform before use. |
| Funded-account risk rule | Maximum 3% total risk at any time once at FundedNext Account stage | Keep separate from Challenge-phase rules; do not incorrectly label this as a Challenge rule. |
| Minimum age | 18 years old to open a FundedNext trading account | The account cannot be opened before age eligibility. Until then, only research/paper simulation. |

## Daily-loss formula implementation

The Help Center defines current daily loss as the sum of **closed trade results for the current server day + results from open positions**. The computation includes swap charges, commissions and fees. The daily P&L reset occurs at server midnight, while any pre-existing floating loss can still make a new day immediately breach the limit. This means a simple closed-balance-only daily drawdown check is not equivalent.

For backtest replay, track separately:
1. closed P&L accumulated since current server midnight;
2. current floating P&L across every open position, including trades opened earlier;
3. commissions, swap and fees, charged to realized or floating P&L as appropriate;
4. total equity for the static maximum-loss floor;
5. closed P&L against target and Quick Strike profit attribution.

Use the official server's confirmed seasonal time mapping. `Europe/Helsinki` may be used as a research proxy for GMT+2/+3 seasonal shifts, but it is not considered verified until compared with observed platform timestamps.

## Official sources

- Stellar 2-Step Challenge and Quick Strike / minimum days / targets: https://help.fundednext.com/en/articles/17255124-stellar-2-step-challenge
- Daily loss rule and daily P&L formula, including open positions, commissions and swap: https://help.fundednext.com/en/articles/8019811-how-can-i-calculate-the-daily-loss-limit
- Seasonal GMT+2/GMT+3 server-time description and static maximum-loss floor: https://help.fundednext.com/en/articles/9941519-daily-loss-limit-vs-maximum-loss-limit
- Quick Strike definition and enforcement: https://help.fundednext.com/en/articles/14702484-understanding-the-quick-strike-parameter-on-fundednext
- FundedNext account-stage 3% risk ceiling: https://help.fundednext.com/en/articles/14702245-what-are-the-risk-limits-on-a-fundednext-account
- Age eligibility (minimum 18): https://help.fundednext.com/en/articles/8020259-is-there-any-age-restriction-to-joining-fundednext

## Remaining operational verification before any funded-readiness claim

- Exact broker/platform server timezone and DST transition behavior on the user's actual account.
- Account-type-specific symbol naming, contract size, commission, swap, spread and execution specifications.
- Real slippage distribution for manual execution after an email alert and phone interaction.
- Tick or sufficiently fine quote-path replay of equity, open-position P&L, stop gaps and simultaneous SL/TP cases.
- FundedNext's current Challenge-stage rule semantics as displayed in the account dashboard at the time of any eventual enrollment.

A correct public rule summary is necessary, but not sufficient, to call any strategy funded-ready.
