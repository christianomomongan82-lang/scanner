# R331 initial screen result — 2026-10-24

**Binary verdict: GAGAL — SAMPLE/TARGET FEASIBILITY.** This specific R331 hypothesis is rejected for the intended funded-challenge use. It is not evidence that the overall income objective or every possible strategy is impossible.

## Why it failed

1. **Confirmation sample too small:** 33 primary delayed-entry trades versus the pre-registered minimum of 50. The experiment cannot qualify for promotion even if its observed returns were positive.
2. **Returns are negative before added costs in both partitions.** With the pre-registered primary execution delay (+10 minutes after signal bar open) and actual paired Dukascopy BID/ASK sides:
   - Discovery (2023-10-25 to 2025-03-31): 93 events, gross total **-267.35 bps**, mean **-2.87 bps/event**, event PF **0.752**.
   - Confirmation (2025-04-01 to 2026-10-21): 33 events, gross total **-397.32 bps**, mean **-12.04 bps/event**, event PF **0.665**.
3. At **5 bps additional round-trip cost**, discovery is **-732.35 bps** (mean -7.87 bps/event; PF 0.472) and confirmation is **-562.32 bps** (mean -17.04 bps/event; PF 0.564).
4. At 10 bps extra cost, confirmation is **-727.32 bps**. The strategy therefore fails economically even before considering full FundedNext execution differences.

## Execution and data checks

- BID rows: 1,312,261; ASK rows: 1,312,261; paired timestamps: 1,312,261.
- BID-only / ASK-only timestamps: 0 / 0; invalid OHLC rows removed: 0 on each side; negative open/close spread rows: 0.
- Complete 5-minute RTH bars: 72,637; 18 incomplete M5 bins were detected and not synthesized.
- VXN: 750 unique daily observations, 2023-10-25 through 2026-10-21; no duplicate dates. Provenance and limitations are documented in `research/R331_VXN_SOURCE_MANIFEST_20261023.md`.
- Input SHA-256:
  - BID gzip: `6659e34607788bf8fd20cee2a7b03a700cc10ff892b3d23136da1615993cb618`
  - ASK gzip: `5a816b8536dad1d01485e020eecddd55d85c6a00bea2f4bd5cb5abfe1a3bd2ca`
  - Local VXN CSV: `23c48798bb9691d8f9d168ea8c1356e4f3acd0df739372f3f679d76ca200e448`
- Local runner SHA-256 after fixes: `b7d19abdac1c0882d76f13dc9fb303712921090461b2e7611cc756b3d416e257`
- Result JSON SHA-256: `a3ba71b5f176bfa99595c4311b2ad4fee3f0fc30e776f4ff5f5a6d4ad6acec2f`
- Event-ledger SHA-256: `25c75ec6ac8d14c0f54ee03ac509e8f4821f39a671191a406cfd249d9b14cbd4`

## Process defects caught before accepting the result

The first local run exposed two implementation defects: (1) pandas `Index.has_duplicates` is a property, not a callable; (2) the session dictionary uses ISO-date string keys, but the evaluation loop checked membership using a `date` object. The first defect prevented execution; the second silently skipped every otherwise validated session. Both fixes were committed before the final run (commits `ab00b0f` and `d2c1b35`), and the final metrics above are from the rerun with both corrected.

## Decision

**Do not tune this hypothesis or promote it to funded replay.** It misses the minimum confirmation sample and has negative gross expectancy in both discovery and confirmation. Do not reinterpret the zero-trade first run as a strategy result; it was a code defect and was discarded.

This is an initial screen, not a complete FundedNext two-phase challenge simulation. Dukascopy CFD quotes are not guaranteed to match FundedNext quotes, and the screen does not establish any pass probability. The next research step should change the hypothesis family rather than search nearby thresholds for this losing configuration.
