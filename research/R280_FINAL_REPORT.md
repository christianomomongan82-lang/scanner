# R280 — Nasdaq-led cash-open breakout follow-through

**Verdict: GAGAL.** The new lead–lag hypothesis improves per-trade expectancy in the contaminated 2022–2025 window, but fails discovery robustness, yearly stability and bootstrap gates.

## Locked hypothesis and execution
The first USATECH/Nasdaq 100 opening-range breakout of a New York weekday acts as leader. A first breakout on USA500, USA30 or USSC2000 is taken only if it occurs 5–30 minutes later on the same day and in the same direction. The child enters exactly T+10 minutes after the follower signal-bar open, stops at the follower's opposite opening-range edge, uses a fixed 2R target, and force-flattens at the exact 16:00 New York M5 bar open if no stop/target has hit. The same three-index follower breakout stream without the Nasdaq lead/lag filter is the matched parent. No parameter tuning occurred.

## Data audit
Data are the existing R205 Dukascopy M5 BID snapshots: USA500 artifact 11709864394, USATECH artifact 11710370389, USA30 artifact 11710730507 and USSC2000 artifact 11710111254. USSC2000 starts 2018-08-08. The source includes flat closed-market rows and no missing bars were interpolated. Cost deductions of 1/2 price bps round-trip are modeled only and are not verified real broker or prop-firm execution costs. Period 2022–2025 is contaminated by previous research; 2026 is diagnostic and already inspected in this project.

## Matched parent and child results
| Stream | Period | Trades | PF +1 bp | Net R +1 bp | PF +2 bp | Net R +2 bp | Max DD R +1 bp |
|---|---|---:|---:|---:|---:|---:|---:|
| Parent follower breakouts | Discovery 2017–2021 | 3,046 | 0.994 | −7.47 | 0.931 | −91.67 | 93.59 |
| Parent follower breakouts | Exploratory forward 2022–2025 | 2,994 | 1.090 | +108.76 | 1.033 | +40.65 | 51.23 |
| Parent follower breakouts | Diagnostic 2026 | 578 | 0.852 | −32.37 | 0.801 | −44.90 | 42.81 |
| Nasdaq-led child | Discovery 2017–2021 | 437 | 0.930 | −13.97 | 0.875 | −25.66 | 34.77 |
| Nasdaq-led child | Exploratory forward 2022–2025 | 426 | 1.169 | +27.89 | 1.109 | +18.62 | 28.55 |
| Nasdaq-led child | Diagnostic 2026 | 82 | 0.744 | −8.21 | 0.705 | −9.76 | 9.36 |

Eligible child signals: 1,084 out of 7,502 first-breakout follower signals, of which 426 closed trades fell in the exploratory forward period. The lead–lag filter improved mean forward net R/trade versus its matched parent (0.0655R vs 0.0363R), but total net R was much lower because it selected fewer trades.

## Locked forward cohorts at +1 bp
| Year | Trades | PF | Net R |
|---|---:|---:|---:|
| 2022 | 116 | 1.188 | +8.87 |
| 2023 | 105 | 0.977 | −0.99 |
| 2024 | 98 | 0.787 | −9.03 |
| 2025 | 107 | 1.908 | +29.04 |

Four-week circular weekly-net-R bootstrap at +1 bp: mean 0.1334R/week, 95% interval [−0.1156R, +0.3805R] across 209 weeks and 10,000 resamples.

## Gate verdict
Failed:
- Discovery PF at +2 bp is 0.875 (<1.00).
- Annual stability fails: 2023 and 2024 have PF <1.00 at +1 bp.
- Bootstrap lower confidence bound is below zero.

The forward PF gates and relative mean-R/trade improvement over the parent passed; that is insufficient to promote a hypothesis when discovery and inference fail. Diagnostic 2026 also deteriorated sharply (PF 0.744 at +1 bp). No challenge replay was run and no follow-on parameter repair is permitted for this locked candidate.

## Evolutionary lesson
The Nasdaq lead–lag condition reduces trade count and realized drawdown but has not established a robust alpha block. It should be recorded as a failed timing hypothesis, not merged with earlier failed breakout signals. The next research generation should move to a materially different market mechanism rather than further adjusting the 5–30 minute window, stop, or target.
