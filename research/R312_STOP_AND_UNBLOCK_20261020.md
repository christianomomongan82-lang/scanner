# R312 — Research stop and unblock protocol

Date: 2026-10-20  
Type: process decision and implementation gate; **not a strategy backtest**.

## Decision

**PAUSE all new strategy backtests and parameter searches.** Do not start R312 as another signal hypothesis. The next work is to make a candidate's result executable, challenge-aware, and reproducible—not to generate another strategy before the scoring path is ready.

This is a process gate, not a claim that a profitable strategy is impossible.

## Root cause found

There are three separate problems. They must not be collapsed into one diagnosis:

1. **The tested signal rules have mostly failed on their own merits.** R302 was negative at the registered +$0.30/oz added-cost case: 179 discovery trades / PF_R 0.6398 / mean -0.1842R per trade, and 208 validation trades / PF_R 0.7299 / mean -0.1298R. Its validation result was also negative with $0 added cost, and the registered 15-minute delay worsened it. R300, R301 and the R309/R310 family likewise showed negative net results before or even without incremental costs. These are not failures that can be repaired by changing a simulator.
2. **Challenge evaluation was not wired into the strategy-search loop.** R311 added `funded_challenge_simulator.py` and eight synthetic tests, reported as 8/8 passing. That proves only the tested synthetic mechanics. No verified market-data adapter currently converts a real candidate into a conservative chronological `OPEN/MARK/EXIT` equity path for that engine. Therefore there is not yet a defensible funded-pass probability for any candidate.
3. **End-to-end reproducibility remains incomplete.** R302's report says its larger primary trade ledger, full pre-outcome audit and all-cost/delay row-level CSVs were not committed. The R309/R310 manifest similarly says the exact local runner and full row-level trade ledgers are not present as normal repository files. A summary JSON is not a substitute for the exact code and event/trade rows needed to reproduce the result from GitHub.

The search-process audit also found a program-level selection problem: 2017–2025 has been repeatedly inspected across related experiments. Treat these dates as contaminated for a final independent validation claim. Keep the protected XAUUSD 2026 interval unopened until a candidate is frozen and clears the historical gates.

## Verified challenge assumptions

The current public FundedNext Stellar 2-Step help page states Phase 1 +8%, Phase 2 +5%, 5% daily loss, 10% maximum loss, at least five separate trading days per phase, and no firm-imposed time limit. It defines Quick Strike trades as trades closed within 30 seconds and says the Quick Strike share must remain below 30%. The daily-loss calculation includes closed and running PnL plus charges, and resets at 00:00 server time.

Sources checked 2026-10-20:
- https://help.fundednext.com/en/articles/17255124-stellar-2-step-challenge
- https://help.fundednext.com/en/articles/8019811-how-can-i-calculate-the-daily-loss-limit

The project's `<=179 calendar days` acceptance test is a **project objective**, not a FundedNext rule. Keep the two separate in every report.

## Required repair sequence — no strategy test until these pass

### Gate A — freeze and identify the exact inputs
- Pick one already-registered candidate only after checking its locked rules and failure status. Do not retune closed candidates or reuse a failed rule as a new label.
- Record the input artifact IDs, source-member names, exact UTC cutoff, filtering rules, timestamp joins, gaps, and SHA-256 hashes.
- Use observed paired BID/ASK for side-correct entry/exit where available. A BID-only feed is not enough for a strong funded-readiness claim unless the missing side is conservatively reconstructed and clearly labelled as a model assumption.

### Gate B — make the calculation fully reproducible
- Commit the exact runner and dependency/version information.
- Commit the complete pre-outcome eligibility/skip ledger, trades, and the chronological event path—not just rounded summaries.
- Store one command that rebuilds the pre-outcome audit, trades, equity path, scorecards, and report from the archived inputs.
- Re-run checksums and compare recomputed outputs with the committed results; any unexplained mismatch is a failure.

### Gate C — validate the market-to-equity adapter and challenge engine
- Convert the locked candidate's trades into chronological `OPEN/MARK/EXIT` events.
- Emit conservative intrabar equity marks for every point at which daily loss or maximum loss could be breached; resolve ambiguous OHLC stop/target bars adverse-first, apply gap fills, and do not synthesize missing bars.
- Include observed spread, commissions, swaps, fees, and the agreed manual-entry delay/slippage scenario in the events.
- Verify the actual platform's server timezone and DST/reset boundary instead of assuming the configured proxy is correct.
- Add tests for day resets, profitable-day extension of the daily-loss allowance, overnight floating losses, overlapping positions, gap-through-stop fills, same-bar conflict handling, and both-phase completion. Synthetic tests must be rerun from committed source; passing them must not be presented as a market result.

### Gate D — run the funded objective, not just strategy diagnostics
Only after Gates A–C pass and the candidate has positive, sufficiently robust costed expectancy:
- Replay both phases sequentially with the actual +8%/+5% targets, daily/static-loss boundaries, five trading days per phase, Quick Strike, sizing, and aggregate exposure controller.
- Run at least 10,000 dependence-preserving sequential paths; do not sample trades as independent if the source has clustered outcomes. Record the block method and seed.
- Report both-phase pass probability, daily-loss breach probability, maximum-loss breach probability, median/90th-percentile completion time, and the probability of completing by project day 179.
- Use the user's manual execution constraints in the primary path and stress at longer delays; do not promote a strategy that only works at zero delay.

## Resume rule

New signal research resumes only after the real-data adapter, reproducible path artifacts, and challenge replay contract above have passed. Every later candidate must be preregistered with its economic mechanism, parent/component lineage, data windows already viewed, and binary gates. Failed families stay closed; improvements discovered after looking at outcomes are diagnostics, not fresh validation.

**Current status:** no candidate is funded-ready; strategy search remains paused; R311 is an infrastructure starting point, not a completed funded-readiness solution.


## Progress update — paired-quote event adapter added (2026-10-20)

Two infrastructure artifacts have now been added to this branch:

- \`research/funded_path_adapter.py\`: loads paired BID/ASK OHLC, applies an exclusive cutoff before pairing/validation, refuses missing trade-time grids, verifies side-correct entry/exit prices, and emits \`OPEN/MARK/EXIT\` events. It uses BID-low checkpoints for longs and ASK-high checkpoints for shorts; adverse checkpoints are processed before intrabar exits. Time/open exits are processed before new entries. Favorable target gaps can be capped at the registered target.
- \`research/test_funded_path_adapter.py\`: nine unit tests covering the core path-conversion and fail-closed cases.
- \`research/R312_XAU_SOURCE_AUDIT.json\`: independent source integrity and smoke-test record.

The existing XAUUSD M5 paired data artifact #12031270051 was downloaded and its ZIP/BID/ASK SHA-256 hashes matched the manifest. After the exclusive 2026 cutoff, 877,930 exact paired bars remained from 2016-01-03 00:00 UTC through 2025-12-31 21:55 UTC. No duplicate timestamps, invalid OHLC rows, ASK-below-BID open/close rows, or unmatched timestamps were found. There are 530 gaps longer than five minutes; the loader does not fill them, and a trade touching an incomplete five-minute grid is rejected.

Local unit-test result for the adapter implementation: **9/9 passed**. A separate smoke test built five challenge events from one deliberately synthetic position placed on real archived quote bars. This was only an infrastructure test: **no strategy PnL or funded pass probability was calculated**.

### What this does and does not fix

The adapter closes one infrastructure gap, but it does not finish R312. The adapter still needs to be bound to a frozen strategy runner that outputs the required price ledger; exact broker contract/commission/swap mapping and account server-time reset must be verified; and the generated event stream must be replayed through the challenge engine. Only after those checks pass can sequential challenge-path simulations be run. No candidate is funded-ready based on this update.
