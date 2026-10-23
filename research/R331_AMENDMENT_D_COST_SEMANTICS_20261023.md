# R331 Amendment D — additional-cost semantics after switching to BID/ASK

**Committed before any R331 event-return/PnL calculation.**

## Cost interpretation

The original 0/2/5/10 bps round-trip ladder was drafted while the screen used QQQ underlying OHLC, which does not contain the FundedNext CFD bid/ask spread. Amendment A changed the price input to paired USATECHIDXUSD BID/ASK, and Amendment B now executes longs at ASK/BID and shorts at BID/ASK. Consequently, the source-feed spread is already represented in the entry/exit side asymmetry.

To preserve the original numerical hurdle without double-labelling it as an observed broker spread, the ladder is now interpreted as **additional round-trip cost beyond the source's side-correct BID/ASK execution price**:

- 0 bps: source-side execution floor, no additional friction.
- 2 bps: optimistic additional platform/feed mismatch and fill-friction allowance.
- 5 bps: primary conservative additional platform/feed mismatch and fill-friction allowance; the registered PASS decision still uses this cost level.
- 10 bps: stress additional platform/feed mismatch and fill-friction allowance.

These are fixed sensitivities, not a statement that FundedNext charges a spread or commission equal to these values. The source BID/ASK spread and these additional deductions must be reported separately. R203's earlier source snapshot median/p95 spread values (median 1.928 bps, p95 4.359 bps for USATECHIDXUSD) are historical context only, not guaranteed FundedNext quotes for this window.

All R331 signal rules, VXN thresholds, date boundaries, five-minute additional entry delay, 30-minute exit, sample gate and binary verdict criteria remain unchanged. If the exact FundedNext symbol specification, spread/commission and financing cannot be verified after a screen pass, the candidate remains non-promotable.

No R331 price/event/PnL result was calculated when this amendment was written.