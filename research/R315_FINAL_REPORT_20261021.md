# R315 final report — XAUUSD M5 compression-to-range breakout

**Verdict: GAGAL at discovery.** Per the preregistered gates, no validation backtest was run and protected 2026 outcomes remained closed.

## Frozen setup

R315 tested whether a low 12-active-bar midpoint range, relative to the trailing 288 observed 12-bar range values, followed by a close beyond the previous 12-bar high/low could supply a compression-release breakout edge. A signal required at least 0.10 times the preceding 12-active-bar median BID true range beyond the channel. Entry was delayed until the exact active M5 open 10 minutes after the signal-bar open (five minutes after bar close plus a five-minute manual response allowance); the executable quote had to remain beyond the breakout threshold. Stop was 1R and target 1.5R, one signal per New York date, one open trade at a time, 60-minute maximum hold and conservative stop-first same-bar handling. Rolling features used prior observed active rows only; timestamps were not filled. An execution-path gap ended the trade at the last observed executable close. Rules were pre-registered at [R315 preregistration](R315_XAUUSD_COMPRESSION_BREAKOUT_PREREGISTRATION.md) before the PnL run.

## Discovery 2016–2020

| Metric | Result |
|---|---:|
| Qualified signal candidates | 1,513 |
| Completed trades | 1,280 |
| Net R, no additional cost | **−1,102.961R** |
| Net R, +$0.30/oz primary added cost | **−2,254.931R** |
| Net R, +$0.50/oz stress | **−3,022.912R** |
| PF_R, +$0.30/oz | **0.0459** |
| PF_R, +$0.50/oz | **0.0202** |
| Win rate, +$0.30/oz | **9.53%** |
| Exit reasons | 1,157 stops; 122 targets; 1 data-gap/time |

Every discovery year was negative at +$0.30/oz: 2016 −389.797R (256 trades), 2017 −543.432R (267), 2018 −474.788R (253), 2019 −570.959R (265), 2020 −275.956R (239). Even without additional friction the net R was strongly negative, so this is not a fee-only failure.

## Data provenance and artifacts

- Source ZIP SHA-256: `2cde8338800fd7f4d5d4628512201c16757ef06bd90d51ffdc8ef9bea425ba1a`.
- BID gzip SHA-256: `b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575`; ASK gzip SHA-256: `b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9`.
- Exclusive cutoff: `2026-01-01T00:00:00Z`. 2016–2020 phase source had 439,073 paired quote rows; 354,177 paired active rows were retained after invalid/static-bar filtering. Missing timestamps were not fabricated.
- Event ledger gzip: 136,027 bytes, SHA-256 `6708a6657dcb07b65546d61a329c793d047a1566864e342108f149876b401353`.
- Four-cost trade ledger gzip: 123,343 bytes, SHA-256 `cdfcb1e264467eee65ff53401aeb44a37d34c8e8a25b90073d327344dc6a1909`.
- Machine result JSON: [R315 discovery result](R315_DISCOVERY_RESULT.json); local output manifest SHA-256 `32f37842e78c1ed7c0506c5eabc4d5a78d87f8edf7dddfc80a316aa5d8f98c86`.

## Decision

R315 fails the preregistered discovery profitability gate. Do not run candidate-specific validation, invert the strategy, or modify the compression/breakout threshold to rescue it. R315 is **GAGAL**, not funded-ready. The protected 2026 sample was not used.
