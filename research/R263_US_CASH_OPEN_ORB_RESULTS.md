# R263 U.S. Cash-Open Opening-Range Breakout — Results

Date: 2026-10-16
**Verdict: FAILED. The locked candidate fails discovery, validation, forward-cost, and bootstrap gates. No parameter tuning; 2026 OOS was not inspected.**

## Data and execution
- Inputs: stored BID-only M5 histories for USA500 and USATECH, originally retained as GitHub artifacts from R205. USA500: 886,206 valid rows; USATECH: 886,039; both run from 2016-01-04 00:00 UTC through 2026-10-09 20:10 UTC. No duplicate timestamps or invalid OHLC rows detected.
- Signal timezone: America/New_York with DST handled. Opening range: six M5 bars from 09:30 through 09:55 ET. First confirmed close cross of OR high/low between 10:00 and 12:00 ET; one trade max per index per U.S. date.
- Entry: next M5 open, with +5-minute delayed entry as a separate locked sensitivity. Stop at the opposite OR boundary; target 1.5R; stop/target monitored on M5 OHLC; open gaps filled at the open and simultaneous stop/target touches are stop-first. No overnight positions; unresolved trades close at the 15:55 ET bar close.
- Important limitation: the retained data is BID-only. It does not supply ASK-side fills or observed spread for this test. Costs of +2/+4/+6 basis points per trade are explicit sensitivity assumptions, not quoted spread measurements from this artifact. Metrics are normalized return basis points per equal-notional trade; drawdown is cumulative trade-return bps, not a funded account percentage drawdown.
- All calculations below were run locally in Python. GitHub Actions did not calculate any strategy results.

## Split results — ideal next-bar entry

| Segment | Instrument | Trades | PF +2 bps | Net +2 bps | PF +4 bps | Net +4 bps | PF +6 bps | Net +6 bps |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Discovery 2016–2020 | USA500 | 1,173 | 0.872 | -3,157.4 | 0.789 | -5,503.4 | 0.714 | -7,849.4 |
| Discovery 2016–2020 | USATECH | 1,143 | 0.894 | -3,302.0 | 0.828 | -5,588.0 | 0.767 | -7,874.0 |
| Discovery 2016–2020 | Combined | 2,316 | 0.885 | -6,459.4 | 0.811 | -11,091.4 | 0.743 | -15,723.4 |
| Validation 2021 | USA500 | 239 | 0.802 | -887.8 | 0.712 | -1,365.8 | 0.633 | -1,843.8 |
| Validation 2021 | USATECH | 229 | 0.992 | -48.9 | 0.920 | -506.9 | 0.853 | -964.9 |
| Validation 2021 | Combined | 468 | 0.911 | -936.7 | 0.831 | -1,872.7 | 0.757 | -2,808.7 |
| Forward 2022–2025 | USA500 | 973 | 1.058 | +1,248.8 | 0.969 | -697.2 | 0.888 | -2,643.2 |
| Forward 2022–2025 | USATECH | 952 | 1.043 | +1,229.2 | 0.977 | -674.8 | 0.916 | -2,578.8 |
| Forward 2022–2025 | Combined | 1,925 | 1.049 | +2,478.0 | 0.974 | -1,372.0 | 0.904 | -5,222.0 |

## Five-minute entry delay — forward 2022–2025

| Instrument | Trades | PF +2 bps | Net +2 bps | PF +4 bps | Net +4 bps | PF +6 bps | Net +6 bps |
|---|---:|---:|---:|---:|---:|---:|---:|
| USA500 | 969 | 1.059 | +1,233.8 | 0.968 | -704.2 | 0.885 | -2,642.2 |
| USATECH | 951 | 1.070 | +1,976.4 | 1.003 | +74.4 | 0.939 | -1,827.6 |
| Combined | 1,920 | 1.065 | +3,210.2 | 0.988 | -629.8 | 0.916 | -4,469.8 |

Four-week circular block bootstrap of forward combined weekly net bps at +4 bps cost (10,000 reps):
- Ideal entry: mean -6.56 bps/week; 34.26% of bootstrap means positive; 95% interval [-35.79, +23.70] bps/week.
- +5-minute entry delay: mean -3.01 bps/week; 40.24% positive; 95% interval [-30.25, +25.08] bps/week.

Both intervals include zero. Combined forward PF at the primary +4 bps case is below 1.10 in both entry scenarios; both instruments are below 1.00 at ideal entry. Discovery and validation were also negative even at +2 bps. The candidate therefore fails the preregistered gates.

## Forward annual stability — combined, ideal entry

| Year | Trades | PF +2 bps | PF +4 bps | PF +6 bps |
|---:|---:|---:|---:|---:|
| 2022 | 479 | 1.161 | 1.105 | 1.052 |
| 2023 | 477 | 1.110 | 1.020 | 0.937 |
| 2024 | 489 | 0.944 | 0.854 | 0.773 |
| 2025 | 480 | 0.911 | 0.836 | 0.768 |

The edge, even at the lower +2 bps assumption, is not stable across 2024–2025. Costs at +4 bps turn aggregate forward net negative; at +6 bps it is substantially negative.

## Final gate

**R263 FAILED.** The candidate cannot pass discovery/validation, fails forward PF >= 1.10 at the primary +4 bps cost, and its forward bootstrap interval includes zero. The +5-minute latency case also fails. No 2026 OOS test was run because it was explicitly conditional on passing the historical forward and latency gates. Do not optimize the opening range, target multiple or time window in response to these results.

This rejects this particular cash-open ORB definition, not every opening-range strategy. A new test must be a meaningfully different hypothesis, preregistered before looking at its results. A passing result on another hypothesis would still require ASK-side execution data and separate FundedNext-rule/real-latency validation before funded approval.