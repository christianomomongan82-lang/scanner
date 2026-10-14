# R189 — Final Binary Verdict

**Decision: GAGAL (does not qualify as a funded-challenge strategy).**

Decision date: 2026-10-14  
Rule: the strategy must demonstrate a realistic, reproducible pass under the stated challenge rules. A favourable partial replay is not enough if a mandatory rule cannot be verified.

## Evidence considered

### Historical report (2016–2025, aggregate report only)

The locked R189 report reports 869 trades in the 2021–2025 forward interval, PF 1.3576, net +933.4 pips, and 3.342 trades/week after its +0.2-pip extra-cost setting. These aggregate figures could not be independently recomputed from the supplied archive because it does not contain the required `EURUSD_M1_2016-2025.xz`, `spread_2016-2025.csv.xz`, or the chronological 2016–2025 trade ledger. They are treated as reported figures, not independently verified results.

At the report's +1.0-pip extra-cost stress, forward PF falls to 1.0808 and net expectancy to +0.2741 pip/trade. Annual net pips are negative in 2022 (-49.8) and 2023 (-30.8). This is thin and cost-sensitive edge.

### Independent 2026 OOS execution check

Source: [R189 OOS 2026 results](https://github.com/christianomomongan82-lang/scanner/blob/r189-oos-2026-test/research/r189_oos_2026_results.json) and [chronological trade ledger](https://github.com/christianomomongan82-lang/scanner/blob/r189-oos-2026-test/research/r189_oos_2026_causal_trades.csv).

- Source window: 2026-01-01 through 2026-10-12 UTC; 344,580 common M1 quote rows.
- 55 eligible trades; PF 1.4845, +78.1 net pips, max closed-trade drawdown 24.8 pips at +0.2 pip additional cost.
- Observed frequency: 1.3509 trades/week, about 5.9/month. This is about 60% below the old report's 3.3423 trades/week forward frequency.
- Cost sensitivity: PF 1.3645 at +0.5 pip, 1.1874 at +1.0 pip, and 0.8995 at +2.0 pips beyond the model's already-observed quote-side execution.

### Sequential phase replay on the 2026 OOS ledger

This was a simplified, chronological close-to-close replay for a $6,000 Stellar 2-Step account using Phase 1 target $6,480, Phase 2 target $6,300 after reset, 5 separate trade days per phase, 5% daily loss threshold, and 10% static maximum-loss floor ($5,400). Risk was a percentage of current balance and each pip return was scaled using the locked 6-pip initial stop. The daily-loss check sees closed PnL only; it does not reconstruct live floating equity inside each M1 candle.

| Extra cost per trade | Risk/trade | Mechanical replay result | Phase 1 | Phase 2 | Interpretation |
|---:|---:|---|---|---|---|
| +0.2 pip | 1.00% | Both targets reached | 2026-03-23 | 2026-06-18 | Passes this simplified replay only |
| +0.2 pip | 1.25% | Both targets reached | 2026-03-19 | 2026-06-09 | Faster, but higher risk and still only simplified replay |
| +0.5 pip | 1.00% | Not both reached by 2026-10-02 | 2026-05-21 | Not reached | Fail in this sample window |
| +0.5 pip | 1.25% | Both targets reached | 2026-03-19 | 2026-06-18 | Simplified replay only |
| +1.0 pip | 0.25%–1.25% | No combination reached both targets by 2026-10-02 | Some settings did reach Phase 1 | Not reached | Cost stress fails speed objective |

These results are conditional on the 55-trade 2026 sequence. They do **not** establish full-sample pass probability; no intrabar floating-equity/stop path is captured by the trade ledger's minute-level exits.

## Mandatory compliance gate that fails

The current official FundedNext Stellar 2-Step rules include Quick Strike: positions closed within 30 seconds, with the share of recorded profit from those trades required to remain below 30% per cycle. Minute OHLC timestamps cannot reliably establish the sub-30-second close time or profit attribution. Since this is an explicit pass condition and the supplied test cannot establish compliance, R189 does not qualify as a demonstrated pass.

Official rules: https://help.fundednext.com/en/articles/17255124-stellar-2-step-challenge  
Quick Strike details: https://help.fundednext.com/en/articles/14702484-understanding-the-quick-strike-parameter-on-fundednext

## Final status

**GAGAL.** The simplified recent-data path shows that passing can happen under selected assumptions, but R189 has not met the complete acceptance test: historical sequence reproduction is unavailable, recent trade frequency is materially lower than the reported forward rate, performance degrades under higher costs, and mandatory Quick Strike compliance is not measurable with the available M1 ledger. Under the agreed binary rule, those are failures—not a provisional/candidate status.
