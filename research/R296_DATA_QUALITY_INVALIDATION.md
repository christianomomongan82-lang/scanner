# R296 — Data-Quality Invalidation

**Disposition: INVALID TEST / DATA-EVENT DEFINITION ERROR. Do not interpret R296's initial PnL as alpha evidence.**

The R296 runner selected the first raw Sunday timestamp, typically 00:00 UTC, as the reopening event and entered ten minutes later. Paired XAUUSD BID/ASK inspection showed that this was a static closed-market quote block: Sunday 00:00 rows had O=H=L=C and the same quotes repeated through 22:55 UTC, while actual active M5 bars began around 23:00 UTC. R296 therefore treated non-tradable quote snapshots as signal, entry and early-hold prices. The apparent all-loss result and its bootstrap do not test a tradable weekend-reopening strategy.

The raw manifest had include_synthetic_flat_bars=false, but the actual archive still contains long sequences of static rows. The manifest flag alone was insufficient to establish that every timestamp was tradable. The R272 data-quality code already used a repeated-flat detector; the first R296 attempt failed to apply that control to reopening timestamps.

This is a data-quality correction, not an alpha verdict. A separately locked follow-up, R297, defines the weekend reopening as the first genuinely active M5 bar after the static block, requires exact executable T+10 entry and T+4h exit, verifies the complete active-bar path, and preserves the original economic direction, spread-friction rule, costs, stop/target and holding horizon. The corrected rule was preregistered before its fresh PnL calculation.

**Decision:** discard R296 performance metrics from the signal evidence matrix. Keep the learned data-integrity requirement that raw manifest metadata must be backed by row-level quote activity validation.
