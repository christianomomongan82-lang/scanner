# R308 DQ1 — Reopening exit timestamp resolution

**Committed before any R308 outcome calculation.** This amendment resolves the exit quote convention without examining price outcomes.

The five-minute manual reaction delay after reopening is measured from the first active reopening M5 bar start. The planned time exit is the **open** of the first active paired M5 bar at/after reopening timestamp +5 minutes and no later than +20 minutes. Entry/exit quote sides remain LONG entry ASK open and long exit BID open. The chosen time-exit bar's high/low are not inspected. Stop/target may only be evaluated from the active reopening bar's executable open (for gap-through handling) and subsequent active bars strictly before the planned exit timestamp. Exact timestamps are mandatory; no later favorable substitute is allowed.
