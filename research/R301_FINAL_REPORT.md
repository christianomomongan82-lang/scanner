# R301 — XAUUSD Safe-Haven Delayed Hedge Response — Final Report

**Binary verdict: GAGAL.** The locked hypothesis failed in both discovery and validation, even with zero incremental cost. The protected XAUUSD 2026 holdout remains unopened.

## Frozen hypothesis and execution

R301 tested whether a severe rolling 30-minute USA500 downside shock during New York cash hours predicts a delayed rise in XAUUSD only when gold itself has not risen over that same 30-minute window. USA500 is context-only (BID feed); positions are XAUUSD longs using paired observed BID/ASK bars.

The first eligible event per New York session enters five minutes after signal close. Stop distance is the prior-only XAU M5 ATR(12); target and stop are both 1R; maximum hold is 60 minutes; if both barriers are touched inside one M5 bar, stop is counted first. The primary incremental cost is $0.30/oz round trip, with $0.00, $0.10 and $0.50 stresses. Entry delay is stressed from five to ten minutes after signal close.

Discovery is 2017–2020; validation is 2021–2025. The validation interval is project-contaminated and is not pristine program-level OOS. All XAU/index timestamps at or after 2026-01-01T00:00:00Z were excluded before feature creation and outcomes.

## Primary outcomes at +$0.30/oz

| Metric | Discovery 2017–2020 | Validation 2021–2025 |
|---|---:|---:|
| Completed trades | 315 | 588 |
| Net result | **−170.908R** | **−189.406R** |
| PF_R | 0.327 | 0.509 |
| Net win rate | 35.6% | 40.6% |
| Maximum closed-R drawdown | 171.775R | 192.575R |
| Positive calendar years | 0 / 4 | 0 / 5 |

At **$0 extra cost**, discovery still lost −89.822R (PF_R 0.547) and validation lost −108.351R (PF_R 0.679). The result is not explained by the incremental cost assumption alone. At +$0.50/oz, discovery fell to −224.964R / PF_R 0.227 and validation to −243.444R / PF_R 0.417.

## Delay, inference and controls

- Ten-minute post-signal delay at +$0.30/oz: discovery −162.811R / PF_R 0.349; validation −166.559R / PF_R 0.550. Delay stress did not create positive expectancy.
- Validation weekly net-R bootstrap: 262 Monday-start weeks including zero-trade weeks; circular four-week blocks; 10,000 resamples; seed 301. Mean **−0.72293R/week**, 95% CI **[−0.91609R, −0.53769R]**. Even the upper bound is negative.
- Matched parent (same first USA500 downside shock without the gold-underreaction filter) at +$0.30/oz: discovery −228.526R / PF_R 0.378; validation −202.584R / PF_R 0.550. The condition reduced some losses but did not create positive alpha.
- Fixed 10:05 ET unconditional gold-long clock control was also negative: discovery −427.139R / PF_R 0.422; validation −318.290R / PF_R 0.601.
- Candidate exit reasons at primary cost: 558 stops, 347 targets, 46 time exits, 13 same-bar collisions resolved stop-first, 3 stop-gap exits and 2 target-gap exits. Candidate streams had no execution-path skips.

## Data and coverage audit

- Before cutoff, XAUUSD had 877,930 BID rows and 877,930 ASK rows. The 69,396 rows per side at/after cutoff were excluded. BID/ASK timestamps matched exactly; there were zero duplicates, invalid OHLC rows, or negative open/close spreads.
- USA500 had 818,601 rows before cutoff. A total of 2,558 complete weekday New York RTH sessions passed the required 78-bar, five-minute grid; 33 incomplete sessions were excluded.
- The frozen trigger selected 315 discovery-session trades and 588 validation-session trades. Signal thresholds used up to the prior 60 complete RTH sessions (minimum 40), never current/future observations.
- Source hashes and archive provenance are recorded in the data manifest. USA500 is BID-only and used only for event context.

## Registered gates

| Gate | Outcome |
|---|---|
| Data/event integrity | PASS |
| Discovery/validation trade minimum | PASS |
| Positive expectancy in both periods | FAIL |
| PF_R ≥ 1.05 in both periods | FAIL |
| +$0.50/oz cost stress | FAIL |
| At least 3/4 discovery years positive | FAIL (0/4) |
| Validation bootstrap lower bound > 0 | FAIL (upper bound also < 0) |
| Ten-minute delay expectancy | FAIL |
| Execution-path integrity | PASS |

**Three of nine gates passed. R301 is closed as GAGAL.** No parameter tuning, direction flip, or second attempt on the same dates is permitted under this candidate. No alpha block is retained. Do not open XAUUSD 2026 to rescue this hypothesis.

## Interpretation and limits

The gold-underreaction condition did not turn an equity downside shock into profitable delayed gold longs. The low win rate under the registered 1R:1R payoff and negative zero-cost result indicate a directional mechanism failure, not merely friction sensitivity. This historical R screen is not a funded-account return or FundedNext DLL/MLL replay. Funded readiness would require verified provider costs and a separate equity-aware two-phase challenge simulation.
