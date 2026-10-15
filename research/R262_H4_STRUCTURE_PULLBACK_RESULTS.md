# R262 H4 Structural Pullback Continuation — Results

Date: 2026-10-16  
**Verdict: FAILED. Candidate closed; no parameter tuning and no 2026 OOS run.** The preregistered forward gate failed clearly on the 2022–2025 sample.

## Data and fixed rules

The test used the stored Dukascopy EURUSD M1 BID/ASK 2016–2025 artifact; signal generation and all fills/PnL were computed in local Python. Raw side files contained 4,415,493 matched minute quotes. The cleaner removed 666,490 pre-reopen Sunday closed-market placeholder rows; no synthetic bars were added. Resampling produced 16,090 active H4 candles. The locked signal yielded 2,268 raw candidates and 1,358 candidates after four-active-H4-bar de-duplication.

This candidate compared two non-overlapping five-active-H4-bar price-structure segments. Long: recent segment makes a higher high and higher low than the prior segment, followed by two consecutive down closes. Short is the exact mirror. Entry is at next active H4 bucket's first available M1 quote (ASK long/BID short). Stop is the prior three completed H4 bars' swing extreme, target is 1.5R, and time stop is 48 elapsed hours. Stop/target execution is simulated on M1 BID/ASK; stop-first is used when both levels are touched in one M1 bar. Latency offsets of +1/+3/+5 minutes after ideal fill were tested. No parameters were tuned.

## Historical splits — ideal entry

| Segment | Trades | PF, no extra cost | Net pips, no extra cost | PF at +0.5 pip | PF at +1 pip | PF at +2 pips |
|---|---:|---:|---:|---:|---:|---:|
| Discovery 2016–2020 | 646 | 1.134 | +551.4 | 1.053 | 0.979 | 0.848 |
| Validation 2021 | 132 | 0.819 | -143.7 | 0.748 | 0.684 | 0.573 |
| Forward 2022–2025 | 503 | 0.815 | -722.5 | 0.760 | 0.710 | 0.620 |

The candidate already loses in validation and forward data before added execution cost. Forward results are negative after every tested cost level. At +1 pip, forward net is -1,225.5 pips and trade-equity maximum drawdown is 1,225.5 pips.

## Forward annual stability at +1 pip

| Year | Trades | PF | Net pips |
|---:|---:|---:|---:|
| 2022 | 120 | 0.805 | -236.8 |
| 2023 | 134 | 0.728 | -292.3 |
| 2024 | 119 | 0.673 | -217.0 |
| 2025 | 130 | 0.623 | -479.5 |

The four-week circular bootstrap at +1 pip gave a mean weekly net of -5.86 pips; only 0.06% of 5,000 resampled means were positive, and the 95% interval was [-9.24, -2.60] pips/week. The interval is wholly negative.

## Fill-latency sensitivity — forward 2022–2025

| Additional delay after ideal entry | Trades | PF at +0.5 pip | Net at +0.5 pip | PF at +1 pip | Net at +1 pip | PF at +2 pips |
|---:|---:|---:|---:|---:|---:|---:|
| 0 minutes | 503 | 0.760 | -974.0 | 0.710 | -1,225.5 | 0.620 |
| 1 minute | 493 | 0.786 | -863.1 | 0.735 | -1,109.6 | 0.644 |
| 3 minutes | 483 | 0.738 | -1,086.7 | 0.691 | -1,328.2 | 0.607 |
| 5 minutes | 479 | 0.752 | -1,015.8 | 0.704 | -1,255.3 | 0.620 |

The +1 pip forward weekly-bootstrap 95% confidence intervals remain entirely negative for all latency settings:
- Ideal: [-9.24, -2.60] pips/week.
- +1 minute: [-8.77, -1.78].
- +3 minutes: [-9.80, -2.94].
- +5 minutes: [-9.60, -2.36].

## Execution and diagnosis

At ideal fill, median initial risk was 8.4 pips; median entry spread 0.3 pip and 95th percentile 0.6 pip. Median holding time was 85 minutes and the 90th percentile 953 minutes. The slower holding period is more operationally compatible with a phone than R189, but its actual expectancy is strongly negative.

## Gate decision

**R262 FAILED.** Discovery does not clear PF 1.10 at +0.5 pip, validation PF is 0.819 even before extra cost, forward PF is only 0.815 before extra cost, all four forward years are negative at +1 pip, and the bootstrap confidence interval is entirely negative. No reason remains to investigate an OOS 2026 pass or to tune this candidate.

This is not proof that all H4 pullback systems are impossible; it is a rejection of this precisely defined setup. Next hypothesis must be meaningfully different. This is a Dukascopy feed test, not a reproduction of the missing original HistData archive. Live commission, swap, broker slippage, and funded-provider rules are not validated.
