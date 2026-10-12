# R235–R242 batch results

**Eight hypotheses were registered and tested together across ten H1 index CFDs. No strategy passed the final acceptance rule.** Four failed discovery eligibility; four were locked from discovery and evaluated on forward 2022–2025 and diagnostic OOS 2026.

## Results

| ID | Hypothesis | Locked asset | Discovery n | Discovery PF @2 bps | Forward n | Forward PF @1 bps | Forward PF @2 bps | OOS n | OOS PF @2 bps | Decision |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| R235 | Extreme close-location continuation | — | 2,877 | 0.725 | — | — | — | — | — | No discovery-eligible asset |
| R236 | Failed high-range impulse reversal | Japan 225 | 144 | 1.211 | 123 | 1.368 | 1.299 | 18 | 0.154 | Reject: insufficient inferential support |
| R237 | Five-bar directional run continuation | — | 2,023 | 0.883 | — | — | — | — | — | No discovery-eligible asset |
| R238 | One-bar price-shock follow-through | US Tech 100 | 306 | 1.362 | 320 | 1.244 | 1.197 | 51 | 0.418 | Reject: annual stability gate |
| R239 | Volatility-normalized overextension reversal | — | 309 | 0.776 | — | — | — | — | — | No discovery-eligible asset |
| R240 | Trend-stall absorption reversal | — | 43 | 0.493 | — | — | — | — | — | No discovery-eligible asset |
| R241 | Cross-sectional volatility-scaled momentum | France 40 | 629 | 1.201 | 819 | 1.001 | 0.961 | 156 | 0.856 | Reject: forward gates |
| R242 | Cross-sectional extreme-return reversal | US Small Cap 2000 | 1,919 | 1.063 | 2,449 | 1.074 | 1.034 | 445 | 1.011 | Reject: forward gates |

PF values use modeled round-trip cost deductions. Cost scenarios were 0, 1, 2, 3 and 5 bps per trade.

## Registered rules

- **R235:** current candle body/range >=0.70 and close in the outer 10% of its range; continue the direction, hold 2 observed active bars.
- **R236:** prior active candle has range >=1.75x the preceding 24-active-bar median and body/range >=0.75; current opposite candle closes across the prior candle midpoint; reverse, hold 3 active bars.
- **R237:** at least 4 of the latest 5 active candle bodies agree, 5-active-interval return >=0.40%, current candle confirms; continue, hold 4 active bars.
- **R238:** prior active one-step close return >=0.50% absolute; current candle confirms the same direction and closes in the outer 20%; continue, hold 3 active bars.
- **R239:** 12-active-interval return exceeds 1.80 times the 12-interval volatility scale; current body confirms reversal and closes in the outer 30%; fade, hold 4 active bars.
- **R240:** prior 3 active candle bodies agree and 3-active-interval return >=0.40%; current candle stalls with body/range <=0.15 and closes against the run in the outer 30%; fade, hold 4 active bars.
- **R241:** at exact shared timestamps, rank each instrument's 12-active-interval return divided by the prior 24-return volatility scale; trade scores >=+1.0 long and <=-1.0 short, hold 6 active bars.
- **R242:** at exact shared timestamps, fade the top/bottom two 4-active-interval returns when the extremes exceed +/-0.25%; hold 6 active bars.

Lookbacks use observed non-flat H1 candles only. No closure prices are forward-filled. Entry must be the exact next H1 open and non-flat. Exit is at the open of the selected future observed active bar.

## Deeper statistical read

R236's numerical forward PF and annual cohorts passed the PF-only gates, but the 4-week circular moving-block bootstrap gave mean net return +5.05 bps/trade with a 95% interval of -4.90 to +15.62; the unadjusted one-sided bootstrap p was 0.158 and the Holm-adjusted p across eight registered hypotheses was 1.000. Its OOS sample was only 18 trades and PF@2 bps was 0.154. It is **not** accepted.

R238 had a forward PF of 1.244/1.197 at modeled 1/2 bps, but the annual stability gate failed (2023 PF@1 bps 0.958); its OOS PF@2 bps was 0.418. R241 was near breakeven after 1 bp and negative at 2 bps. R242 stayed below the required forward PFs and failed annual stability.

## Audit

- 10/10 source H1 files passed timestamp-grid and OHLC integrity validation.
- 190/190 feature/signal prefix checks passed.
- 88/88 unique trade-ledger CSVs passed independent checks; 75,308 trade rows inspected; zero failed assertions.
- Ledger audit checks exact source entry/exit opens, signal-to-entry timestamp, active-bar horizon, price-return arithmetic, modeled costs, period boundaries, duplicate signals and overlapping same-symbol positions.
- Eight forward tests use Holm–Bonferroni correction for positive net expectancy at modeled 2 bps.
- Common-history discovery selection sensitivity is included. No alternative forward/OOS runs were made; alternate selections remain unvalidated diagnostics.

Source data are BID-only and costs are modeled, not verified broker/prop spreads, commissions, slippage or financing. Contract point values and actual funded drawdown rules are not simulated. No strategy is live/funded-ready.