# R243–R250 batch results

**Decision: no candidate passed.** Five of eight hypotheses met discovery selection criteria and were tested on forward data; all five failed the forward acceptance gate. The other three had no instrument meeting the discovery gate.

| ID | Hypothesis | Selected asset | Discovery n | Discovery PF@2 bps | Forward n | Forward PF@1 bps | Forward PF@2 bps | OOS n | OOS PF@2 bps | Holm-adjusted p | Decision |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| R243 | Large opening-gap continuation | — | 135 | 0.859 | — | — | — | — | — | 1.000 | NO_DISCOVERY_ELIGIBLE_ASSET |
| R244 | Large opening-gap rejection | — | 127 | 0.702 | — | — | — | — | — | 1.000 | NO_DISCOVERY_ELIGIBLE_ASSET |
| R245 | Long-wick rejection reversal | — | 2,946 | 0.863 | — | — | — | — | — | 1.000 | NO_DISCOVERY_ELIGIBLE_ASSET |
| R246 | Compression/range-expansion breakout | EU50 | 274 | 1.153 | 198 | 0.677 | 0.641 | 38 | 1.014 | 1.000 | REJECT_FORWARD_GATE_FAILED |
| R247 | Directional-efficiency continuation | Germany 40 | 768 | 1.100 | 721 | 0.874 | 0.817 | 125 | 1.138 | 1.000 | REJECT_FORWARD_GATE_FAILED |
| R248 | Session opening-range breakout | Germany 40 | 488 | 1.102 | 212 | 0.841 | 0.768 | 41 | 0.482 | 1.000 | REJECT_FORWARD_GATE_FAILED |
| R249 | UTC hour-of-week seasonality | US Small Cap 2000 | 3,208 | 1.037 | 4,914 | 0.904 | 0.862 | 998 | 0.877 | 1.000 | REJECT_FORWARD_GATE_FAILED |
| R250 | Cross-index breadth-confirmed momentum | Japan 225 | 1,957 | 1.016 | 2,200 | 0.945 | 0.906 | 458 | 0.801 | 1.000 | REJECT_FORWARD_GATE_FAILED |

## Locked protocol
Discovery: 2017–2021; require at least 100 closed trades and PF >=1.00 at modeled 2 bps; instrument selection uses discovery only. Forward: 2022–2025; require at least 30 trades, PF >=1.15 at both 1 and 2 bps, and each annual cohort with at least five trades PF >=1.00 at 1 bps. OOS diagnostic runs from 2026-01-01 through the source cutoff on 2026-10-09 UTC.

## Audit
- 10/10 H1 OHLC source files passed integrity checks.
- 190/190 causal prefix tests passed.
- 90/90 independent ledger audits passed, covering 119,234 trade rows.
- Zero failed assertions.
- 2,000 circular four-week block-bootstrap resamples per forward candidate; one-sided expectancy p-values Holm-adjusted across eight hypotheses.

Costs of 0/1/2/3/5 bps are modeled, not verified broker/prop-firm costs. This is not a live/funded-ready strategy result.