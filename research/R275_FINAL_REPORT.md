# R275 — R189/L80 Mobile-Delay Stress

**Verdict: GAGAL.** The locked five-minute execution-delay mutation fails every performance promotion gate. Do not retune this candidate or send it to challenge replay.

## Why this child was tested

R189/L80 remained an unconfirmed lead after an incomplete cross-feed robustness result. R275 left its signal rules unchanged and compared the canonical next-M1-open entry (T+1 minute after signal-bar open) with the user's practical phone delay: wait for the bar to finish, then five more minutes (exact T+6 minute entry). That tests an execution constraint, not a new signal threshold.

## Locked execution and data

- Signal rules remain the R189 L80 specification; no threshold search.
- Exact entry timestamps required. Actual quote sides: long ASK entry / BID exits, short BID entry / ASK exits. Entry spread ceiling 1.5 pips.
- SL 6 pips, TP 18 pips, zero-distance trail activates after +6 pips favorable excursion, 60 observed M1 bars time stop; no overlap. Opening gaps use executable opening price; stop-first for same-bar intrabar conflicts.
- Additional cost tests: +0.2, +0.5, +1.0 and +2.0 pips per trade.
- Source archive: Dukascopy EURUSD M1 BID/ASK artifact 11959096102, requested 2016–2025, archive SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- Original collection used Dukascopy's `-fl` option. A conservative pre-feature heuristic removed 696,795 paired rows (15.78%) when both BID/ASK candles were zero-range and copied their respective previous close on the exact next minute. 3,718,698 paired rows remained, with a 0.30-pip median and 0.80-pip p95 opening spread. **This filter is a heuristic, not proof that every synthetic flat bar was removed.** A positive result would require a fresh verified no-flat source before promotion; this candidate is negative regardless.
- Period 2022–2025 is contaminated by prior project research. It is an exploratory historical diagnostic, not a pristine independent holdout. No 2026 EURUSD data was used in R275 calculations, and the reserved 2026 XAUUSD holdout remains untouched.

## Main result: 2022–2025 at +1 additional pip

| Metric | Parent T+1 | Child T+6 |
|---|---:|---:|
| Trades | 699 | 701 |
| Profit factor | 0.839 | 0.694 |
| Net result | -378.5 pips | -786.3 pips |
| Maximum drawdown | 440.0 pips | 816.9 pips |
| Trades/week | 3.35 | 3.36 |

The five-minute delay worsened net outcome by 407.8 pips and increased maximum drawdown by 376.9 pips in this period. The child remains negative at +0.2-pip extra cost: 2022–2025 net -225.5 pips / PF 0.901. At +2 pips, net is -1,487.3 pips / PF 0.496.

### Child cost sensitivity

| Period | Trades | +0.2 pip PF / net | +0.5 pip PF / net | +1 pip PF / net | +2 pip PF / net |
|---|---:|---:|---:|---:|---:|
| Discovery 2016–2020 | 911 | 0.975 / -70.8 | 0.884 / -344.1 | 0.750 / -799.6 | 0.532 / -1,710.6 |
| Validation 2021 | 68 | 1.529 / +85.3 | 1.384 / +64.9 | 1.170 / +30.9 | 0.822 / -37.1 |
| Exploratory 2022–2025 | 701 | 0.901 / -225.5 | 0.817 / -435.8 | 0.694 / -786.3 | 0.496 / -1,487.3 |
| Full 2016–2025 | 1,680 | 0.960 / -211.0 | 0.870 / -715.0 | 0.738 / -1,555.0 | 0.525 / -3,235.0 |

Net figures are in pips. Because costs are charged per trade, trade counts are constant within each row.

## Locked gates

| Gate | Observed | Verdict |
|---|---|---|
| At least 100 completed exploratory-forward trades | 701 | PASS |
| PF >= 1.10 at +1 pip | 0.694 | FAIL |
| PF >= 1.05 at +2 pips | 0.496 | FAIL |
| Every entry-year with >=20 trades has PF >=1.00 at +1 pip | 2022–2025 annual PF: 0.722, 0.634, 0.832, 0.629 | FAIL |
| Four-week weekly-net-pips circular bootstrap at +1 pip has lower 95% bound >0 | mean -3.762 pips/week; CI [-5.252, -2.398] | FAIL |

All 10,000 bootstrap replicates used a fixed seed (2752026), 209 calendar weeks and four-week circular blocks. The CI is wholly negative.

## Evolutionary decision

**R275 = GAGAL.** Do not combine this delayed L80 stream with the failed XAUUSD blocks, raise risk to compensate, or tune the locked thresholds on this data. The useful inherited lesson is operational: the signal's edge does not survive this phone-entry delay under the tested costs. This rejects the specific L80 + T+6 execution system, not every conceivable future EURUSD hypothesis.

No funded challenge replay was run. Any future promotion still requires a robust independent test and a complete rule-aware $6k two-phase replay including intraday floating equity, all charges, five trading days per phase, loss rules and Quick Strike compliance.
