# R329 Pre-outcome Amendment C — compact candidate data-audit output
Date: 2026-10-22 UTC
Candidate outcomes/PnL at amendment time: **not computed**.

The original data-integrity JSON duplicated all 14 per-stream file hashes and byte counts already frozen in data_manifest.json. The runner will now emit a compact deterministic audit with the source-manifest hash, input-integrity totals, per-pair BID/ASK counts and spread/gap statistics, exact cross-pair timestamp-intersection counts, and explicit pre-outcome-only status. Per-file SHA-256 and byte count remain frozen and verified by the full source manifest.

This changes only duplicate output representation. Signal features, eligibility, horizons, sizing, date windows, costs and candidate gates are unchanged. The amendment is made before any realized returns/PnL are calculated.
