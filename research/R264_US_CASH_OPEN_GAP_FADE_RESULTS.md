# R264 U.S. Cash-Open Gap-Fade — Results

Date: 2026-10-16
**Verdict: FAILED. No tuning; 2026 OOS was not inspected.** The locked gap-fade hypothesis fails discovery, validation and forward robustness gates.

## Data and fixed rules
- BID-only M5 snapshots from the existing GitHub-stored R205 artifacts. USA500: 886,206 rows; USATECH: 886,039 rows; both run from 2016-01-04 through 2026-10-09 UTC. No duplicate timestamps or invalid OHLC rows detected.
- Gap = 09:30 ET opening price relative to the previous available 15:55 ET bar close. Require absolute gap >=25 bps and the first M5 candle closes against the gap. Fade the gap; enter at 09:35 ET (ideal) or 09:40 ET (+5-minute delay). Stop at the first candle's extreme; target the prior RTH close; require reward/risk >=1 at actual entry. Maximum one trade per symbol/day; no overnight; unresolved trade exits at the 15:55 bar close.
- Fixed extra-cost stress is +2/+4/+6 bps per equal-notional trade. The data has no ASK side, so these are cost scenarios, not observed spread. Local Python performed every signal, fill, PnL and bootstrap calculation; no GitHub Actions backtest ran.

## Results by split — ideal entry

| Segment | Instrument | Trades | PF +2 bps | Net +2 bps | PF +4 bps | Net +4 bps | PF +6 bps | Net +6 bps |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| Discovery 2016–2020 | USA500 | 302 | 0.868 | -550.9 | 0.750 | -1,154.9 | 0.654 | -1,758.9 |
| Discovery 2016–2020 | USATECH | 336 | 0.763 | -1,374.8 | 0.675 | -2,046.8 | 0.600 | -2,718.8 |
| Discovery 2016–2020 | Combined | 638 | 0.807 | -1,925.6 | 0.707 | -3,201.6 | 0.623 | -4,477.6 |
| Validation 2021 | USA500 | 62 | 0.618 | -295.0 | 0.519 | -419.0 | 0.439 | -543.0 |
| Validation 2021 | USATECH | 57 | 1.165 | +145.3 | 1.033 | +31.3 | 0.919 | -82.7 |
| Validation 2021 | Combined | 119 | 0.909 | -149.7 | 0.787 | -387.7 | 0.685 | -625.7 |
| Forward 2022–2025 | USA500 | 267 | 1.039 | +135.9 | 0.896 | -398.1 | 0.780 | -932.1 |
| Forward 2022–2025 | USATECH | 266 | 1.100 | +496.5 | 0.993 | -35.5 | 0.900 | -567.5 |
| Forward 2022–2025 | Combined | 533 | 1.075 | +632.4 | 0.953 | -433.6 | 0.849 | -1,499.6 |

## Five-minute delayed entry — forward 2022–2025

| Instrument | Trades | PF +2 bps | Net +2 bps | PF +4 bps | Net +4 bps | PF +6 bps | Net +6 bps |
|---|---:|---:|---:|---:|---:|---:|---:|
| USA500 | 219 | 0.960 | -116.1 | 0.829 | -554.1 | 0.722 | -992.1 |
| USATECH | 224 | 0.985 | -63.2 | 0.887 | -511.2 | 0.803 | -959.2 |
| Combined | 443 | 0.975 | -179.3 | 0.863 | -1,065.3 | 0.769 | -1,951.3 |

## Forward annual stability — combined, ideal entry

| Year | Trades | PF +2 bps | PF +4 bps | PF +6 bps |
|---:|---:|---:|---:|---:|
| 2022 | 142 | 1.260 | 1.156 | 1.065 |
| 2023 | 126 | 1.071 | 0.932 | 0.817 |
| 2024 | 139 | 0.950 | 0.809 | 0.695 |
| 2025 | 126 | 0.897 | 0.786 | 0.693 |

Four-week circular weekly-PnL bootstrap at +4 bps (10,000 repetitions): ideal entry mean -2.07 bps/week, 36.22% positive means, 95% CI [-13.63, +10.25]. With +5-minute delay, mean -5.10 bps/week, 18.84% positive means, CI [-16.21, +7.22]. Both intervals include zero.

## Gate decision

**R264 FAILED.** Discovery PF is 0.807 at just +2 bps; validation PF is 0.909 at +2; forward combined PF reaches only 1.075 at +2 and drops to 0.953 at the primary +4 bps cost. Both instruments fall below PF 1.00 at +4 in forward data, the bootstrap interval includes zero, and the +5-minute delay result degrades to PF 0.863 at +4. The setup also has only a 10-minute median forward holding period in the ideal-entry replay.

Do not tune the gap threshold, target rule or candle confirmation after this result. The gap-fade candidate is closed. No 2026 OOS test was run because preregistered historical gates failed. This remains a BID-only screening replay, not a full ASK-side or funded-account simulation.