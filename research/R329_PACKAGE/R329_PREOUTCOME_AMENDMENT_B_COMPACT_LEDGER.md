# R329 Pre-outcome Amendment B — compact deterministic eligibility archive
Date: 2026-10-22 UTC
Candidate outcomes/PnL at amendment time: **not computed**.

The first pre-outcome run passed the raw data gate and all registered sample gates. While preparing a GitHub-readable archive for the full eligibility/skip ledger, the verbose CSV compression was reduced by encoding timestamps as Unix seconds, period and reason fields as documented short codes, and purely diagnostic numeric fields at four decimal places. The full data rows remain deterministic; period/date eligibility, candidate horizons, signal/entry/exit times, skip/active status, eligible-leg count, lookback days, USD exposure ratio, and final gross weight are retained. No realized future returns are used.

- Exact code correction to CSV line terminator fixed before the rerun; the intended newline is a single LF.
- No signal formula, horizon grid, sizing rule, execution timestamp, data source/hash, date split, sample gate, cost rule, or candidate selection rule changed.
- PnL/returns/PF/drawdown/bootstrap remain uncomputed.
- This amendment supersedes neither Amendment A nor the original registered hypothesis; it changes only the deterministic archive representation.
