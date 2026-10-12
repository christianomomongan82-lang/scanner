# R227–R234 — eight-idea raw-price H1 backtest batch

**Eight hypotheses were executed in one batch across ten index CFDs. Six had a discovery-eligible instrument and were evaluated on forward 2022–2025 plus diagnostic OOS 2026. R231 and R232 were not advanced because neither met its discovery eligibility gate. No candidate passed the locked forward gate.**

## 1. Locked experiment scoreboard

| ID / premise | Instrument selected on discovery | Discovery n | Discovery PF @2 bps | Forward n | Forward PF @1 bp | Forward PF @2 bps | OOS n | OOS PF @2 bps | Decision |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| R227 — Multi-horizon alignment momentum | France 40 | 1517 | 1.004 | 1305 | 0.871 | 0.837 | 238 | 0.718 | REJECT |
| R228 — Volatility-shock continuation | US Tech 100 | 1111 | 1.108 | 1157 | 1.099 | 1.058 | 206 | 0.679 | REJECT |
| R229 — High-range wick rejection | US500 | 309 | 1.355 | 379 | 1.072 | 1.016 | 52 | 0.562 | REJECT |
| R230 — Range sweep/re-entry | EU50 | 400 | 1.036 | 414 | 1.176 | 1.120 | 80 | 0.898 | REJECT |
| R231 — 72-active-bar efficiency trend | None | — | — | — | — | — | — | — | Discovery gate failed |
| R232 — 12-active-bar overextension reversal | None | — | — | — | — | — | — | — | Discovery gate failed |
| R233 — Cross-sectional 12-active-bar momentum | Australia 200 | 1301 | 1.039 | 1393 | 0.835 | 0.787 | 316 | 1.014 | REJECT |
| R234 — Weekend carry drift | FTSE 100 | 157 | 1.135 | 118 | 1.177 | 1.117 | 22 | 1.070 | REJECT |

### Why R231 and R232 stopped at discovery

- **R231:** No candidate reached 100 discovery closes. The highest-PF candidate was US Tech 100 with 32 trades and PF@2 bps of 1.305, below the minimum sample; the largest sample was just 39 trades.
- **R232:** No candidate met PF@2 bps >=1.00 with at least 100 closes. The best qualifying sample was FTSE 100, 570 trades, PF@2 bps of 0.937.

## 2. Registered rules

- **R227:** Return over 24 observed non-flat H1 bars >= +0.40% (or <= -0.40%), four-active-bar return confirms by >= +0.15% (or <= -0.15%), and current candle body agrees. Hold 8 elapsed hours.
- **R228:** Current H1 range >=2x the median range of the previous 24 observed non-flat H1 candles; four-active-bar return >= +/-0.20%; close in the top/bottom 20% of the candle. Continue direction; hold 4h.
- **R229:** Range >=2x median range of the prior 24 non-flat candles; lower wick >=60% with close in the upper 35% implies long, mirrored upper-wick condition implies short. Hold 4h.
- **R230:** Sweep the prior 24 non-flat candle high/low then close back inside by at least 0.15%, with the candle body confirming reversal. Fade the sweep; hold 4h.
- **R231:** Return over 72 observed active bars >= +/-0.80%, directional efficiency >=0.45 and current body confirms direction. Hold 12h.
- **R232:** Absolute return over 12 observed active bars >=0.80%; current body reverses and closes in the outer 30% toward reversal. Fade overextension; hold 6h.
- **R233:** At exact shared timestamps, rank ten indices by return over 12 observed active bars; take the top two if return >= +0.15% and bottom two if <= -0.15%, in the direction of the extreme. Hold 8h.
- **R234:** Friday H1 bar timestamped 14:00 UTC (closes at 15:00 UTC); prior 24 observed active-bar return >= +/-0.40%. Enter at the exact next active H1 open, hold at least 48 hours, exit at first non-flat open at/after horizon.

Lookbacks are in **observed non-flat candles**, not synthetic 24/72-hour bars. Flat closure candles are skipped; there is no forward-fill. Entry still requires the exact next H1 open after signal close.

## 3. Cost sensitivity — locked candidates, forward

| ID | Instrument | PF @0 bps | PF @1 bp | PF @2 bps | PF @3 bps | PF @5 bps |
|---|---|---:|---:|---:|---:|---:|
| R227 | France 40 | 0.905 | 0.871 | 0.837 | 0.805 | 0.744 |
| R228 | US Tech 100 | 1.141 | 1.099 | 1.058 | 1.020 | 0.946 |
| R229 | US500 | 1.130 | 1.072 | 1.016 | 0.964 | 0.868 |
| R230 | EU50 | 1.235 | 1.176 | 1.120 | 1.066 | 0.968 |
| R233 | Australia 200 | 0.886 | 0.835 | 0.787 | 0.741 | 0.659 |
| R234 | FTSE 100 | 1.240 | 1.177 | 1.117 | 1.061 | 0.956 |

The pre-registered forward pass requires >=30 closed trades, PF >=1.15 at both modeled 1 and 2 bps, and PF >=1.00 at 1 bp for every qualifying annual cohort with >=5 trades. **None passes.**

## 4. Weekly block-bootstrap expectancy (2 bps)

2,000 circular resamples per cell; each block contains four consecutive calendar weeks including zero-trade weeks. The interval is a diagnostic for mean net bps/trade, not a performance guarantee.

| ID | Trades | Mean net bps/trade | 95% interval | Bootstrap P(mean > 0) |
|---|---:|---:|---|---:|
| R227 | 1305 | -4.527 | [-9.234, -0.612] | 0.012 |
| R228 | 1157 | +1.518 | [-3.021, +6.191] | 0.744 |
| R229 | 379 | +0.303 | [-6.537, +8.383] | 0.531 |
| R230 | 414 | +2.322 | [-3.243, +8.459] | 0.788 |
| R233 | 1393 | -4.010 | [-6.452, -1.540] | 0.001 |
| R234 | 118 | +2.133 | [-6.116, +12.188] | 0.664 |

R227 and R233 have intervals entirely below zero. The intervals for R228/R229/R230/R234 all cross zero, so their positive sample means are not statistically robust.

## 5. Annual forward cohort stability at 1 bp

| ID | 2022 PF | 2023 PF | 2024 PF | 2025 PF | Annual gate |
|---|---:|---:|---:|---:|---|
| R227 | 0.993 | 1.005 | 0.798 | 0.670 | FAIL |
| R228 | 1.003 | 1.077 | 1.135 | 1.278 | PASS |
| R229 | 0.801 | 0.758 | 1.382 | 1.598 | FAIL |
| R230 | 1.798 | 1.028 | 0.647 | 1.021 | FAIL |
| R233 | 0.641 | 0.909 | 0.739 | 1.182 | FAIL |
| R234 | 1.444 | 0.521 | 1.049 | 1.589 | FAIL |

R228 passes the annual sub-gate but still fails whole-period PF thresholds and deteriorates badly in OOS. R230 has the most visibly regime-sensitive yearly profile: strong 2022 but PF@1 bps of only 0.647 in 2024.

## 6. Audit

- Source data: 10/10 H1 files passed duplicate-timestamp, hourly-grid, finiteness, and OHLC-relationship checks. SHA-256 fingerprints are included in source validation.
- Causality: 180/180 feature/signal comparisons passed using full data versus data truncated at 2020-01-01.
- Independent ledger audit: 92 unique trade-ledger CSVs passed 15 checks each (1,380/1,380 checks); 60,074 trade rows inspected against raw source data.
- Checks cover source timestamps, signal-close/entry time, entry/exit opens, active execution bars, cost deductions at 0/1/2/3/5 bps, scheduled horizon, first non-flat exit, period boundaries, trade direction, duplicates, positive prices and non-overlap.
- 98 ledger writes resulted in 92 unique filenames because selected discovery ledgers were rewritten in place with period metadata.
- Data are BID-only. Costs are modeled, not verified live broker/prop spread, commissions, financing or slippage. Contract point value and funded drawdown rules are not simulated.

## 7. Equal-history discovery selection sensitivity

US Small Cap history starts on 2018-08-08, later than some other instruments. A discovery-only selection sensitivity was run over the shared interval 2018-08-08 through 2021-12-31; **no alternative forward/OOS tests were run**.

| ID | Original asset | Common-window choice | Changed? | Common-window PF@2 |
|---|---|---|---|---:|
| R227 | France 40 | France 40 | No | 1.038 |
| R228 | US Tech 100 | Australia 200 | Yes | 1.211 |
| R229 | US500 | US500 | No | 1.207 |
| R230 | EU50 | France 40 | Yes | 1.144 |
| R231 | None | None | — | No eligible asset |
| R232 | None | None | — | Best PF only 0.966 |
| R233 | Australia 200 | Australia 200 | No | 1.039 |
| R234 | FTSE 100 | FTSE 100 | No | 1.227 |

Two of six original asset selections changed under common history. These alternate assets are **not validated**; the sensitivity only flags selection instability. All primary forward decisions remain REJECT.

**Bottom line:** no strategy from this batch qualifies as a funded/live candidate. The price stream is BID-only, costs are modeled, and no actual platform drawdown rules or contract-specific exposure sizing are simulated.
