# FundedNext inactivity constraint — 2026-10-23

## Decision used by research

**Conservative simulator limit: no gap of 30 or more calendar days between accepted trade entries.** If the gap reaches 30 calendar days, the replay verdict is GAGAL due to inactivity. Do not place low-quality or arbitrary trades merely to reset the clock; a candidate must naturally generate a valid entry before the limit.

## Why 30 days, not 60

Official FundedNext sources conflict:
- Trading Objectives / general rules page states 60 consecutive days without a trade: https://fundednext.com/general-rules/cfds/trading-objectives
- Help Center inactivity article, updated 27 July 2026, states 30 consecutive calendar days and says CFD accounts are deactivated: https://help.fundednext.com/en/articles/8019664-is-there-an-inactivity-period-for-my-accounts-in-fundednext-cfd

Until FundedNext confirms the rule in writing for the exact Stellar 2-Step CFD account, the project uses 30 days as the safe upper bound. This is a conservative modelling choice, **not a claim that the conflicting official sources have been reconciled**.

## Replay semantics and limitations

- Measure the gap using calendar dates in the configured account/server timezone, from one accepted OPEN to the next accepted OPEN. A rejected/skipped signal does not reset activity.
- The simulator must fail closed when a new accepted entry arrives after a gap of 30 or more calendar days.
- This entry-to-entry check cannot independently prove that a truncated event file would not sit idle for 30 days after its last event. Full challenge replays must cover the complete attempted period and report the data/event horizon; do not silently treat a truncated path as complete.
- This constraint supplements—not replaces—daily loss, static maximum loss, phase targets/minimum trading days, Quick Strike/cycle handling, and the project day-179 speed gate.
- Do not manufacture trades to satisfy inactivity. If a strategy naturally leaves a gap that breaches the conservative limit, it is not eligible for promotion under this project configuration.

## Required follow-up

Before purchasing/starting a challenge, obtain written confirmation from FundedNext support for the exact account type and retain the response. If the firm confirms 60 days, update this rule only after recording the evidence and rerunning the simulator tests.
