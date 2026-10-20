# R302 — Ledger Reassembly / Reproducibility Notes

## Repository storage status — COMPLETE

All four row-level CSV outputs are now committed in this active branch. The restoration commit is [cd42a9a4c5092ff34705d17580706b6a2ac8628f](https://github.com/christianomomongan82-lang/scanner/commit/cd42a9a4c5092ff34705d17580706b6a2ac8628f). Each output checksum was checked against the original manifest before commit, and the GitHub branch tree was read back afterward to confirm the committed file sizes and paths.

| File | Data rows (header excluded) | Bytes | SHA-256 |
|---|---:|---:|---|
| [R302_primary_cost_trade_ledger.csv](R302_primary_cost_trade_ledger.csv) | 387 | 126,330 | `43d31c21186e679e3e463e092ddbd40cca5a20382c3632d52b5b639314394903` |
| [R302_preoutcome_eligibility_audit.csv](R302_preoutcome_eligibility_audit.csv) | 2,336 | 288,734 | `d66a6762f3a59e282078fdf69dd1646d5ad2a930bc6cd92562cd4eb871f3a3a3` |
| [R302_all_cost_delay_streams_and_skips.csv](R302_all_cost_delay_streams_and_skips.csv) | 4,644 | 1,537,582 | `3dcb874f70c64c3704b311aea4753f2dba9655c8f985f5ab0d7cff370999e683` |
| [R302_all_valid_trade_ledger.csv](R302_all_valid_trade_ledger.csv) | 4,638 | 1,527,805 | `d0b2138af8096157e0343fda60d19760b9e7bd34615ce924850f245cbf42d910` |

The source ZIP and both raw BID/ASK members were independently hash-checked against [R302_DATA_MANIFEST.md](R302_DATA_MANIFEST.md). The recovery replay initially exposed a dependency-version mismatch with pandas 3.0; rerunning with the original environment versions (NumPy 2.3.5 and pandas 2.2.3) reproduced the four original CSV SHA-256 values exactly. The recovery run also reproduced the locked binary result below. The one-shot recovery workflow was removed after publication; no persistent backtest workflow remains.

## Locked strategy result — unchanged

**Verdict: GAGAL.** At $0.30/oz additional round-trip friction, discovery 2017–2020 produced 179 trades, −32.9644576459R and PF_R 0.6397595. Validation 2021–2025 produced 208 trades, −26.9914313008R and PF_R 0.7298631. Only 3 of 8 preregistered historical gates passed. The validation weekly bootstrap mean was −0.1030207R/week, with 95% interval [−0.1894478, −0.0155725].

The scheduled-clock proxy does not apply the historical official IBA auction non-publication calendar. The protected 2026 interval remains unopened, and this candidate is not FundedNext-ready. The storage repair does not change any strategy verdict or open the protected period.
