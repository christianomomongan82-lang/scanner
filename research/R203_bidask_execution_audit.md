# R203 — Execution-Fidelity Audit of the Locked R191 Baseline

**Verdict: REJECT under the existing robustness gates.** This is an execution audit, not a new alpha hypothesis.

## Locked strategy and execution

- Signal: completed New-York-wall-clock H4 BID close exceeds the preceding 55 H4 BID highs.
- Stop: lowest BID low over the signal bar and 26 preceding H4 bars (27 bars inclusive).
- Target: 2R, calculated from ASK entry relative to the BID stop.
- Entry: first available M5 ASK open at least five minutes after the H4 signal close and before the next actual H4 close.
- Exit: BID M5 OHLC. Stop is checked before target; a gap through the stop fills at BID open.
- H4 signals use the same canonical Dukascopy H1 BID snapshots used by the scanner pipeline. Snapshot row counts match the canonical grid: USA500 93,569 H1 rows; USATECH 93,568. Execution quotes come from supplied M1 bid/ask files, aggregated to M5 without forward-filling missing observations.

## Observed spread distribution

Spread in basis points relative to BID close, using the M1 quote snapshots:

| Instrument | Median spread | 95th percentile |
|---|---:|---:|
| USA 500 / S&P 500 | 1.334 bps | 2.635 bps |
| USA 100 Tech / Nasdaq 100 | 1.928 bps | 4.359 bps |

These are observed quote spreads, not broker commission/slippage measurements. Cost stress below is added on top of actual ASK-entry/BID-exit spread.

## Discovery-only comparison (2017–2021)

Selection rule: among the two instruments with bid/ask snapshots, require at least 10 closed discovery trades and PF >= 1.00 after an additional 0.5 bps stress, then select the one with fewer closed trades. Forward outcomes are not used for selection.

| Instrument | Closed trades | PF, actual quote sides | PF +0.5 bps | PF +1 bp | PF +2 bps |
|---|---:|---:|---:|---:|---:|
| USA 500 / S&P 500 | 41 | 1.905 | 1.896 | 1.887 | 1.870 |
| USA 100 Tech / Nasdaq 100 | 46 | 1.833 | 1.828 | 1.823 | 1.813 |

**Locked selection: USA 500 / S&P 500**, because it has fewer closed discovery trades among the eligible pair.

## One-time forward check (selected USA 500 only)

| Metric | Actual quote sides | +0.5 bps stress | +1 bp stress | +2 bps stress |
|---|---:|---:|---:|---:|
| Closed forward trades, 2022–2025 | 38 | 38 | 38 | 38 |
| PF, forward 2022–2025 | 1.617 | 1.612 | 1.607 | 1.596 |

The weakest eligible forward entry-year cohort is **2022**, with **10 trades and PF 0.497** under the +0.5 bps stress. Other cohorts were 2023 PF 2.791 (12 trades), 2024 PF 3.320 (8 trades), and 2025 PF 1.195 (8 closed trades out of 9 entries). The OOS interval ends at **2026-10-02 20:15 UTC**: 5 entries, 4 closed trades, PF 1.993 at +0.5 bps. That OOS sample is too small to override the poor 2022 cohort.

## Conclusion

Actual ASK-entry/BID-exit execution does not erase the baseline's aggregate PF on these two instruments, but the selected USA 500 candidate **fails the same robustness gate** because the 2022 cohort PF is below 1.00. The extra 0.5/1/2 bps values are stress tests, not verified broker costs; commission, live slippage, and instrument-specific costs remain unverified.

This audit is restricted to two indices with supplied bid/ask history. It does not convert the other eight BID-only instruments into actual bid/ask tests. It also does not supersede R194's original ten-index universe selection; it checks execution fidelity for the already locked baseline. No strategy should be called funded/live-ready from these results.

## Provenance

- `usa500idxusd_M1_bidask_UTC.csv.xz` SHA-256: `d75e7d6ab03df5ceaf8dc507cd34f3d4e1d256b0f9e5a0c073c31ed6ccaa7251`
- `usatechidxusd_M1_bidask_UTC.csv.xz` SHA-256: `dffc1cd7df4875b1ba818c09318e701ad2bfe5009b7804ea197d8d28b52f0b0d`
- Canonical H1 snapshots were obtained from the completed R202 cached-asset artifacts and verified against expected H1 row counts.
- R202 ten-index outcome: https://github.com/christianomomongan82-lang/scanner/actions/runs/38139241698
