# R295 — Positive Breadth + USA500 Own-Session Direction Confirmation

**Verdict: GAGAL.** The extra confirmation failed to improve the locked R293 parent.

## Candidate and matched R293 parent

| Metric | Discovery candidate | Discovery parent | Validation candidate | Validation parent |
|---|---:|---:|---:|---:|
| Trades | 437 | 442 | 119 | 119 |
| Net bp @2bp | +1,253.10 | +1,320.41 | +249.78 | +249.78 |
| PF @2bp | 1.131 | 1.137 | 1.144 | 1.144 |
| Net bp @4bp | +379.10 | +436.41 | +11.78 | +11.78 |
| PF @4bp | 1.038 | 1.043 | 1.006 | 1.006 |
| Max closed-PnL drawdown (% fixed notional) | 24.54% | 24.54% | 4.20% | 4.20% |

## Filter diagnostic

The added condition that USA500's own cash-session return be positive removed only **5** of the parent’s 442 discovery trades and **0** of 119 validation trades. The five omitted discovery events produced **+67.31 bp net** at the modeled 2 bp cost (PF 1.692). Therefore the new condition discarded a net-profitable subset and reduced discovery profit and PF. Because no validation trades were removed, the validation stream is exactly the same as R293.

This is an unhelpful mutation, not progress toward a promoted system. The evidence suggests the added own-instrument confirmation is almost entirely redundant under R293's positive-breadth condition.

## Annual discovery cohorts @ 2 bp

| Year | Trades | Net bp | PF |
|---|---:|---:|---:|
| 2017 | 92 | +72.78 | 1.085 |
| 2018 | 94 | +679.84 | 1.486 |
| 2019 | 125 | -5.32 | 0.998 |
| 2020 | 126 | +505.80 | 1.105 |

## Validation bootstrap

Mean **+4.8034 bp/week**; 95% CI **[-5.5573, +14.3354] bp/week** over 52 Monday-start weeks including zero-trade weeks, using 5,000 circular four-week block resamples (seed 295). The lower bound crosses zero, so the preregistered stability gate fails.

## Locked gates

| Gate | Result |
|---|---|
| Discovery: minimum 200 trades | PASS |
| Discovery: positive net bp at 2 bp | PASS |
| Discovery: PF ≥ 1.05 at 2 bp | PASS |
| Discovery: at least 2 of 4 years positive | PASS |
| Discovery: PF ≥ 0.90 at 4 bp | PASS |
| Validation: minimum 75 trades | PASS |
| Validation: positive net bp at 2 bp | PASS |
| Validation: PF ≥ 1.05 at 2 bp | PASS |
| Validation: bootstrap CI lower bound > 0 | **FAIL** |
| Validation: PF ≥ 0.90 at 4 bp | PASS |

## Limitations

- Inputs are cached M5 BID-only feeds. Deductions of 1/2/4 bp are modeled costs, not verified executable costs.
- No live ask-side spread, slippage, commission, CFD point value, swaps, margin, or overnight floating equity was modeled.
- No FundedNext two-phase equity-aware challenge replay was run.
- 2017–2021 is contaminated historical research data, not pristine program-level out-of-sample evidence.
- **No R295 strategy PnL beyond 2021 was calculated.** Do not tune this failed rule using the same dates.
