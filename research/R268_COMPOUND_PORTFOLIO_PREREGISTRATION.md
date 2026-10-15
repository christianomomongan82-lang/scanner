# R268 — Fixed-Fractional Compound Portfolio Diagnostic

**Classification: retrospective portfolio diagnostic.** The components have previously been examined individually, so this combination is not treated as an independent discovery of alpha. The goal is to measure whether a simple, pre-fixed account-level compounding/risk overlay improves the joint return stream without tuning the component rules.

## Components — fixed before calculation

1. **R262 EURUSD H4 structural pullback**, use the saved 5-minute delayed trade ledger. Risk denominator = recorded risk_pips. Apply additional cost stress of +1.0 pip per trade.
2. **R263 USA500/USATECH cash-open opening-range breakout**, use the saved 5-minute delayed trade ledger. Risk denominator = recorded initial_risk_bps. Apply additional cost stress of +4.0 bps per trade.

Both source experiments are closed; their rules and signals must not be changed. R189 is excluded from this first joint replay because the locally available saved R189 ledger is an ideal-entry ledger, while this composite must use actual delayed-fill trade outcomes. Do not substitute an invented R189 delayed ledger.

## Fixed compounding and portfolio rules

- Initial equity: $6,000 (reference balance only; not a purchase recommendation).
- Each accepted trade risks 0.25% of realized account equity as measured at its entry event. Dollar risk/position size is fixed until that trade exits; PnL is credited/debited at the saved exit event.
- Maximum aggregate open initial risk: 1.00% of current realized equity. If a new trade would exceed the cap, skip the new trade (do not resize earlier positions). This is a conservative exposure cap, not a claim to recreate intratrade floating equity exactly.
- Event processing: on identical timestamps, process exits before new entries. At identical entry timestamps, deterministic priority is R262 EURUSD, then R263 USA500, then R263 USATECH.
- Trade R = (gross trade PnL − the fixed additional cost) divided by the saved stop-risk denominator. Compounded dollar PnL = risk dollars fixed at entry × net R. Equity then changes by that amount; later position sizes use the updated equity.
- Periods: discovery 2016–2020, validation 2021, forward 2022–2025. Do not include data after 2025 in this diagnostic.
- Report accepted/omitted trades, stand-alone module contributions, compounded equity, closed-equity maximum drawdown, forward yearly stability, costs and an all-week bootstrap. Also report simple non-compounded R results so sizing does not obscure expectancy.

## Decision gates

For an **economic-screen pass**, all of these must hold:
1. Combined discovery and validation net R both positive.
2. Combined forward net R positive and PF ≥ 1.10.
3. Every forward year positive after locked costs.
4. Forward bootstrap 95% interval for mean weekly net account return excludes zero on the positive side.
5. No closed-equity maximum drawdown of 10% or more under the fixed 0.25% risk rule.

Because the portfolio components were selected from already-inspected experiments, even an economic-screen pass does not by itself make the combination eligible for funded approval. The final outcome must still use only **LULUS** or **GAGAL**; a retrospective combination that cannot be independently validated is **GAGAL for promotion**.

## Explicit limitations

The saved ledgers are trade outcomes, not tick-by-tick account equity. Closed-equity drawdown omits floating intratrade drawdown. No exact FundedNext daily-loss replay or Quick Strike sub-30-second validation is possible from these trade ledgers. Index extra costs are fixed bps scenarios; they are not observed live spreads. No OOS beyond 2025 will be inspected in this diagnostic.
