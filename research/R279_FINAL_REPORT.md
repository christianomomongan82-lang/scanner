# R279 — Long-only breadth router without fixed take-profit

**Verdict: GAGAL.** Removing the fixed 2R cap does not improve the matched R278 child, and the locked discovery-cost gate still fails.

## Locked mutation
Same long-only first upper breakout from R278; three-of-four simultaneous confirmation; exact T+10 entry; stop at opening-range low; no fixed TP; close at exact 16:00 New York bar open if stop has not triggered. Same data, instrument eligibility, cost stress and period definitions.

Data: Dukascopy M5 BID OHLC snapshots from R205 artifacts 11709864394 (USA500), 11710370389 (USATECH), 11710730507 (USA30), 11710111254 (USSC2000). USSC2000 begins 2018-08-08; synchronized events before common four-feed coverage are excluded. Data are BID-only and round-trip 1/2 price bps are modeled, not verified broker spreads or commissions. 2022–2025 is research-contaminated; 2026 is diagnostic and has also been repeatedly viewed in this project. No challenge path replay was run.

## Results
| Period | Trades | PF +1 bp | Net R +1 bp | PF +2 bp | Net R +2 bp |
|---|---:|---:|---:|---:|---:|
| Discovery 2017–2021 | 435 | 0.923 | −14.64 | 0.873 | −24.86 |
| Exploratory forward 2022–2025 | 508 | 1.395 | +67.80 | 1.339 | +59.44 |
| Diagnostic 2026 | 67 | 0.877 | −2.63 | 0.826 | −3.85 |

Forward bootstrap at +1 bp: mean 0.324R/week; 95% interval [0.042R, 0.609R], 10,000 four-week circular blocks. All four 2022–2025 yearly PFs exceed 1 at +1 bp, though 2025 is nearly flat (PF 1.024).

## Locked gate failure and ablation conclusion
Discovery PF at +2 bps is 0.873 (<1.00), so the candidate fails. Removing the 2R target also did **not** improve results versus R278's target-capped child: forward +1 bp net R fell from +69.10 to +67.80, PF from 1.403 to 1.395, and max drawdown rose from 17.26R to 17.99R. Therefore the fixed 2R target is not shown to be the component harming this setup. No retuning or challenge replay.
