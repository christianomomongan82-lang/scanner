# R205 — Independent Local Reproduction and Artifact Comparison

**Status: REPRODUCED — audit match PASS.** The data artifacts were downloaded from R205 into a local execution filesystem; the local engine rebuilt H4 and matched the released artifact.

- Run: https://github.com/christianomomongan82-lang/scanner/actions/runs/38160487617
- Source code inspected: research/r192_ger40.py and research/r205_breadth_confirmation_ten_index.py
- Source: ten Dukascopy H1/M5 BID-only snapshot pairs; timestamps are millisecond Unix UTC.
- Validation: finite OHLC, ordered indexes, no duplicate timestamps, no missing/invalid OHLC rows; no synthetic bars were added or forward-filled.
- Exact aggregate/skip-bin counts matched across all ten instruments.
- Audit comparison: 1,401 original trade rows vs 1,401 local; all 23 trade fields matched exactly or within 1e-12 for floating-point values; zero mismatches.
- Instrument/mode ledger: 20/20 rows matched; discovery selection and forward metrics matched.

## Locked R205 result

| Phase | Closed trades | PF at 1 bp | PF at 2 bps |
|---|---:|---:|---:|
| Discovery 2017–2021, US Small Cap 2000 | 19 | 1.7912 | 1.7825 |
| Forward 2022–2025, US Small Cap 2000 | 29 | 1.0487 | 1.0448 |

The worst qualifying forward entry-year cohort PF at 1 bp was 0.5698. Final decision: **REJECT** — below the minimum 30 forward closes; both forward PF thresholds fail; and the worst qualifying cohort is below 1.00.

BID-only historical prices and modeled 1/2 price-bps costs do not verify executable ask-side fills, live spread changes, broker/prop commissions, financing, or live slippage.

The full field-by-field comparison and all original/local trades are preserved in the attached local execution bundle delivered in the conversation.