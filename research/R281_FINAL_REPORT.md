# R281 — EURUSD H1 compression-release breakout

**Verdict: GAGAL.** The corrected local engine now produces trades, but none of the eight preregistered configurations meets the minimum 50 closed validation trades in calendar 2021. More importantly, every configuration is strongly negative during discovery (2017–2020) at +1 pip additional round-trip cost. Per the preregistration, the engine stopped at the validation gate and did not calculate or inspect strategy outcomes for 2022–2025.

## Why this experiment was run
R257 previously reported zero validation trades for every candidate because its eligibility/coverage checks invalidated almost the entire hourly grid. That result was not reliable evidence that the signal itself had no edge. R281 replays the same fixed family and exact grid with a corrected implementation, without adding parameter points or selecting from later-period outcomes. It uses EURUSD H1 bars constructed from Dukascopy M1 BID/ASK, rather than claiming to reproduce R257's original H1 archive bit-for-bit.

## Data audit
- Source: Dukascopy EURUSD M1 BID/ASK via dukascopy-node; requested coverage 2016-01-01 to 2026-01-01 exclusive.
- Archive SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- Paired M1 observations: 4,415,493 before the paired flat-candidate heuristic; 696,795 removed; 3,718,698 remained.
- Strict complete H1 candles: 57,191, from 2016-01-03 23:00 UTC through 2025-12-31 20:00 UTC. 5,574 incomplete/missing hourly groups were dropped; no bars were filled.
- Median observed H1 opening spread: 0.30 pip; 95th percentile: 0.80 pip.
- **Important limitation:** the source collector used `-fl`; removing paired flat candidates is a heuristic, not proof that all synthetic rows were removed. Any future positive result would require verified no-flat quote history before promotion.

## Locked grid results
Cost shown here is +1 extra pip per round trip, on top of quote-side BID/ASK execution.

| Configuration | Discovery trades | Discovery PF | Discovery net pips | Validation trades | Validation PF | Validation net pips |
|---|---:|---:|---:|---:|---:|---:|
| Q20 / B12 / 1.5R | 271 | 0.615 | -1,042.35 | 4 | 2.065 | +58.80 |
| Q20 / B12 / 2R | 263 | 0.576 | -1,192.20 | 4 | 2.065 | +58.80 |
| Q20 / B24 / 1.5R | 90 | 0.622 | -378.30 | 0 | n/a | 0.00 |
| Q20 / B24 / 2R | 88 | 0.667 | -336.60 | 0 | n/a | 0.00 |
| Q30 / B12 / 1.5R | 392 | 0.617 | -1,593.50 | 10 | 0.755 | -49.55 |
| Q30 / B12 / 2R | 375 | 0.614 | -1,622.50 | 10 | 0.514 | -107.90 |
| Q30 / B24 / 1.5R | 126 | 0.600 | -602.75 | 0 | n/a | 0.00 |
| Q30 / B24 / 2R | 122 | 0.575 | -652.50 | 0 | n/a | 0.00 |

The fitted six-hour range thresholds, using only eligible 2017–2020 observations, were 20.8 pips at Q20 and 25.0 pips at Q30.

## Gates and decision
- Minimum 50 validation trades for candidate selection: **FAIL** (best count 10).
- Discovery PF at +1 pip at least 1.00: **FAIL for all eight candidates** (PF range 0.575–0.667).
- No candidate was selected. No 2022–2025 forward metrics were calculated.
- No FundedNext challenge-path simulation was run because the signal failed the historical screen.

## Learning retained
1. Correcting R257's zero-trade eligibility failure made the H1 setup executable; the old zero-trade result should not be treated as an alpha finding.
2. Once executable, the locked family showed consistently negative discovery expectancy across the full preregistered grid, and 2021 was too sparse to qualify even the higher-PF Q20/B12 cells.
3. Do not loosen quantiles, shorten lookbacks, or pick the four-trade validation PF after the fact. **R281 is closed as GAGAL; no alpha block is retained.**

## Reproducibility
- Preregistration: `research/R281_EURUSD_H1_COMPRESSION_RELEASE_PREREGISTRATION.md`
- Input archive is GitHub data-only artifact 11959096102; the large compressed archive is not stored as a regular source file. Verify the SHA-256 above before replay.
- The replay runner and eight discovery/validation ledgers are generated locally; the compact results JSON and grid summary record the tested grid and why the forward stage was not authorized. Row-level ledgers still need to be archived to GitHub for full repository-only reproduction.
- No GitHub Actions backtest workflow was created or dispatched.
