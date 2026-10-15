# R267 Last-Hour Momentum Into Overnight — Retrospective Exploratory Pilot

Date archived: 2026-10-16  
**Status: EXPLORATORY PILOT — FAILED; not a pre-registered experiment and never promotion-eligible.**

## Why this is retrospective
The calculation was completed before a contemporaneous preregistration had been committed to GitHub. The rules and output are archived transparently for audit only. Do not represent this as a formally preregistered candidate or use the result to nominate a strategy.

## Hypothesis and execution replay
Using complete regular-session M5 BID bars for USA500 and USATECH, take the direction of the move from the 14:00 ET bar open to the 14:55 ET bar close. Entry is at 15:00 ET bar open; the manual latency sensitivity enters at 15:05 ET. Exit at the next complete regular-session 09:30 ET bar open. One trade per instrument/session; positions are held overnight and through weekends where applicable. No trade whose exit date falls in 2026 was included. 2026 outcomes were not inspected.

Cost sensitivity is +2 / +4 / +6 bps per trade. These are fixed assumptions, not observed spreads: source data are BID-only. All signal, entry, exit, PnL and bootstrap calculations ran in local Python, not GitHub Actions.

## Results at +4 bps

| Execution | Segment | Trades | PF | Net bps |
|---|---|---:|---:|---:|
| Ideal 15:00 | Discovery 2016–2020 | 2,484 | 0.864 | -9,734.8 |
| Ideal 15:00 | Validation 2021 | 502 | 1.001 | +6.2 |
| Ideal 15:00 | Forward 2022–2025 | 1,986 | 0.878 | -7,469.5 |
| Delayed 15:05 | Discovery 2016–2020 | 2,484 | 0.865 | -9,563.6 |
| Delayed 15:05 | Validation 2021 | 502 | 0.965 | -410.5 |
| Delayed 15:05 | Forward 2022–2025 | 1,986 | 0.857 | -8,762.0 |

## Forward yearly results at +4 bps

| Execution | Year | Trades | PF | Net bps |
|---|---:|---:|---:|---:|
| Ideal | 2022 | 500 | 0.918 | -1,767.9 |
| Ideal | 2023 | 496 | 1.011 | +123.7 |
| Ideal | 2024 | 498 | 0.785 | -2,710.0 |
| Ideal | 2025 | 492 | 0.805 | -3,115.3 |
| Delayed | 2022 | 500 | 0.889 | -2,424.4 |
| Delayed | 2023 | 496 | 0.978 | -242.0 |
| Delayed | 2024 | 498 | 0.775 | -2,835.3 |
| Delayed | 2025 | 492 | 0.795 | -3,260.2 |

Forward results are negative for both instruments. Ideal-entry forward PF was 0.871 for USA500 and 0.884 for USATECH. After the 5-minute delay it was 0.849 and 0.864, respectively.

## Weekly block bootstrap (forward 2022–2025, +4 bps)
Four-week circular block bootstrap, 10,000 replications, includes every calendar week (including zero-trade weeks).

| Execution | Mean net bps/week | Bootstrap means positive | 95% interval bps/week |
|---|---:|---:|---:|
| Ideal 15:00 | -35.74 | 5.75% | [-80.65, +8.70] |
| Delayed 15:05 | -41.92 | 2.86% | [-85.98, +1.35] |

## Verdict
**FAILED.** Discovery and forward expectancy are negative, forward PF is below 1.00 at the primary +4 bps cost, most forward yearly cohorts lose money, both instruments are negative forward, and the bootstrap intervals cross zero. Do not tune this exact hypothesis; do not inspect 2026 to try to rescue it.

## Data integrity and limitations
- USA500 BID M5: 886,206 rows, zero duplicate timestamps and zero invalid OHLC rows; 2,757 complete RTH sessions.
- USATECH BID M5: 886,039 rows, zero duplicate timestamps and zero invalid OHLC rows; 2,756 complete RTH sessions.
- Data end: 2026-10-09 20:10 UTC. SHA-256 values are recorded in the companion machine-readable JSON.
- No ASK data, measured quote spread, broker commission, verified live slippage, funded timezone, DLL/MLL or Quick Strike simulation. This is not a funded-ready strategy.
