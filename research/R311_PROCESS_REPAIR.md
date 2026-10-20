# R311 process repair — common funded replay engine

Date: 2026-10-20  
Type: infrastructure correction, not a strategy experiment and not a market result.

## Root cause

The existing search-process audit explicitly called for a pause until the candidate ledger, common scoring contract, and funded challenge replay were in place. Despite that, research continued through R300–R310. Candidate reports still cannot be compared on a single outcome, and the project does not have a shared engine to measure the primary goal: completing both FundedNext phases before a rule breach and within 179 calendar days.

## Change delivered

- Added `funded_challenge_simulator.py`, a chronological two-phase account-equity replay.
- Added six synthetic unit tests covering sequential +8%/+5% phase completion, the five-day rule, floating-equity daily loss, static maximum loss, Quick Strike gating, open-risk cap, and timezone-aware input.
- The engine sizes risk from current closed balance at entry, checks floating equity on every MARK event, resets the phase reference balance for phase 2, and applies the project's 3% aggregate open-risk cap.
- Replay input must be an event path (OPEN/MARK/EXIT), not a closed-trade summary. It does not fill data gaps or infer intrabar prices.

## Verification

Local synthetic test result: **6/6 tests passed**.

This is an engine implementation result, not a strategy backtest, not a challenge pass, and not a pass-probability estimate. No market data was evaluated in this infrastructure patch.

## Still mandatory before any funded-readiness claim

1. Build and test each source-specific adapter that emits exact, conservative intrabar equity marks from the paired BID/ASK data, including adverse gap fills and stop-first conflicts.
2. Verify the precise server time/DST mapping against the intended platform. Europe/Helsinki is currently only a configurable research proxy.
3. Supply account-specific symbol contract sizes, commissions, swaps, and realistic manual-delay slippage.
4. Run at least 10,000 dependence-preserving sequential two-phase paths and report both-phase pass probability, breach probabilities and time-to-completion quantiles.
5. Commit the exact adapters, input hashes, full chronological event path/trade ledgers, and path outputs to GitHub so repository-only reproduction succeeds.

## Hard process gate

Do not label a strategy funded-ready based on PF or a closed-trade ledger. The engine must run on a validated position path and the two-phase ensemble must meet the existing funded-readiness criteria. Do not call this patch a strategy result.
