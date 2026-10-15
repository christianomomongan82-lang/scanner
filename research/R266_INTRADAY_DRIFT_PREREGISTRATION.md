# R266 preregistration — U.S. index afternoon continuation after a strong morning

**Status:** locked before the R266 calculation.  
**Decision class:** new hypothesis, not a modification of R263/R264.  
**Input:** existing GitHub-sourced BID-only M5 snapshots for USA500 and USATECH, 2016-01-04 through 2026-10-09 UTC. Calculations run locally in Python. The strategy evaluation is capped at entries through 2025-12-31; 2026 outcomes are not inspected.

## Hypothesis
After a meaningful directional move from the U.S. cash open through the 12:55 ET M5 bar, the same direction may persist into the final three hours of the cash session. Unlike the opening-range breakout/gap strategies, this enters at 13:00 ET and holds only to the cash close; unlike H1 momentum, it uses one intraday morning signal and no multi-day trend alignment.

## Locked signal and execution
- Timezone: \`America/New_York\`; use regular-session bar-start times only.
- Require a complete RTH session containing all 78 expected 5-minute bars from 09:30 through 15:55 ET. No synthetic bars are created.
- At the 13:00 ET decision point, calculate morning move in bps as \`(close of 12:55 bar / open of 09:30 bar - 1) * 10,000\`.
- A trade is eligible only when the absolute morning move is at least 0.5 × the median of the prior 20 completed sessions' daily range, expressed in bps of the prior session close. The current day is excluded from that rolling median.
- Direction follows the morning move: positive means long; negative means short. One trade maximum per symbol/session.
- Ideal entry: 13:00 ET bar open. Manual delay stress: 13:05 ET bar open. If the required entry bar is missing, skip the trade.
- Exit at the close of the 15:55 ET bar (cash-session close). No stops, targets, scaling, or overnight holding; this is a fixed-horizon test, not a claim of funded readiness.
- Evaluate separate instruments and combined trade ledger. Use fixed additional round-trip costs of +2, +4 and +6 bps per trade. These are sensitivity assumptions, not measured spreads: the available files are BID-only.

## Locked time splits and promotion gates
- Discovery: 2016–2020.
- Validation: 2021.
- Forward: 2022–2025.
- Do not inspect 2026 trade performance if any gate fails.
- At primary +4 bps cost: discovery and validation must each have positive net and PF ≥ 1.10; forward must have at least 100 trades, positive net and PF ≥ 1.10.
- Every forward calendar year must have PF ≥ 1.00 at +4 bps.
- Each index must have forward PF ≥ 1.00 at +4 bps.
- The five-minute delayed forward result must have positive net and PF ≥ 1.10 at +4 bps.
- Four-week circular block bootstrap over all forward calendar weeks, including zero-trade weeks, must have a 95% confidence interval for mean weekly net bps whose lower bound is above zero, for both entry modes.
- No parameter sweep or changes after viewing the results. Failure closes this exact hypothesis.

## Known limitations
The index data have no ASK side, verified live spread, commissions or slippage. A constant bps stress cannot prove fills. Funded provider timezone, DLL/MLL, Quick Strike rules and account-level risk remain unverified. Passing this historical screen would only authorize another validation step, not approval to buy or trade a funded challenge.
