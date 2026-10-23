# R330 Amendment B — deterministic screen execution runtime

**Date:** 2026-10-23 UTC. Committed before any R330 PnL.
**Scope:** execution mechanics for the initial screen only; does not permit funded promotion.

## Runtime constraint

The local Python/container environment cannot resolve external hostnames, and the available GitHub connector can read the archived files but cannot transfer them into the local Python filesystem through the current connection. This was tested directly. To avoid claiming a Python run that did not happen, this amendment authorizes a **pure deterministic ECMAScript calculation core** in the current tool runtime for the R330 screen only.

The exact calculation core must be committed to GitHub before outcomes. The current run must fetch the archived CSVs from GitHub, verify each SHA-256, execute the frozen algorithm twice, and compare deterministic outputs. No GitHub Actions computation is authorized.

## Limits imposed by this exception

- This is a bounded environment workaround, not a general change to the project's default local-Python rule.
- A positive R330 result remains PASS — SCREEN ONLY, never funded-ready. It must be independently reproduced from the exact CSVs by Python and pass exact broker quote, five-minute entry, financing/swap, daily/max loss, and two-phase challenge replay before promotion.
- A negative robust R330 screen can reject this frozen specification; it does not prove that all trading or all strategies are impossible.
- If input verification or output reproducibility fails, record GAGAL — DATA/PROCESS and do not interpret partial numbers as economic evidence.

No R330 PnL was calculated when this amendment was written.