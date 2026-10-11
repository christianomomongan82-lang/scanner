# R216 — UTC cross-sectional daily momentum rotation

**Decision: REJECT_FORWARD_GATE_FAILED.**

## Locked hypothesis

- At the 15:55 UTC M5 bar close, rank four US indices by raw close-to-close percentage return over the prior 24 hours.
- At the following 16:00 UTC M5 open, go long the strongest index and short the weakest with 50% notional per leg.
- Exit both legs at the 16:00 UTC open one day later. Exact timestamps are required; flat bars invalidate the day, and no interpolation or forward-fill is used.
- Round-trip costs are modeled at 1 and 2 bps per leg, weighted by 50% portfolio exposure per leg.
- Discovery gate: at least 500 closed daily portfolios and PF >= 1.00 at 2 bps. Forward only runs if discovery qualifies.

## Period summaries

| Period | Trades | PF @1 bp | PF @2 bps | Mean net @1 bp | Mean net @2 bps |
|---|---:|---:|---:|---:|---:|
| Discovery 2017–2021* | 503 | 1.1078 | 1.0462 | 1.7891 bps | 0.7891 bps |
| Forward 2022–2025 | 605 | 0.8188 | 0.7734 | -3.5020 bps | -4.5020 bps |
| OOS 2026** | 119 | 1.0179 | 0.9529 | 0.2695 bps | -0.7305 bps |

*The common four-index sample starts 2018-08-08 because US Small Cap data begins then; there are no common observations for 2017–early August 2018.  
**OOS is diagnostic only and cannot override the forward rejection.

## Forward annual cohorts

| Year | Closed | PF @1 bp | PF @2 bps | Mean net @1 bp | Mean net @2 bps |
|---:|---:|---:|---:|---:|---:|
| 2022 | 154 | 0.5658 | 0.5343 | -10.3365 bps | -11.3365 bps |
| 2023 | 151 | 0.8079 | 0.7650 | -3.9068 bps | -4.9068 bps |
| 2024 | 151 | 1.1407 | 1.0795 | 2.3905 bps | 1.3905 bps |
| 2025 | 149 | 0.8755 | 0.8194 | -1.9998 bps | -2.9998 bps |

## Data and execution audit

- Exact shared timestamp rows: 699,130.
- Common data range: 2018-08-08T13:30:00Z to 2026-10-09T20:10:00Z.
- Automated checks: 10/10 passed, including an actual full-versus-truncated prefix test.
- Raw BID OHLC only; no synthetic bars, interpolation, or forward-filled values. Entry and exit stay within their evaluation period.
- Costs are modeled only; there is no ASK stream or verified broker/funded spread, commission, slippage, financing, or contract-specific sizing.
- Historical results do not establish live/funded readiness.
