# R218–R226 batch branch

This branch captures the result summary and extended audit from one local batch of nine registered raw-price H1 hypotheses, evaluated across ten index CFD data streams.

The full 150-file execution bundle is provided in the conversation download. It contains the exact local Python engine, independent audit/robustness scripts, all 90 instrument-discovery ledgers, selected forward/OOS ledgers, cost sensitivity, annual cohorts, and bootstrap results. The source CSVs are retained separately in the R205 snapshot artifacts; the bundle includes source hashes, not duplicate raw data.

Decision: none passed the forward acceptance rule. R221 was stopped at the discovery sample gate (maximum 26 trades versus minimum 100). The other eight selected an asset on discovery only and were evaluated in forward 2022–2025 and OOS 2026.

To qualify, a strategy needs at least 30 forward closes, PF >=1.15 at modeled 1 and 2 bps, and each annual cohort with >=5 trades PF >=1 at 1 bp. All costs are modeled, the stream is BID-only, and this does not establish funded/live readiness.
