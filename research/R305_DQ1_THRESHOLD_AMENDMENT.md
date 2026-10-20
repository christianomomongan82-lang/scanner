# R305 DQ1 — Threshold refresh and event-crossing definition

**Committed before any R305 outcome calculation.** This amendment resolves implementation details without observing any trade PnL.

For deterministic and causal calculation, the EURUSD absolute 30-minute return Q85 threshold is refreshed once per UTC calendar day, using only valid 30-minute returns with timestamps in the preceding 20 complete UTC calendar days and strictly before the current UTC day begins; require at least 1,000 observations. The same threshold is held constant for that UTC day.

The first-cross condition compares the absolute **preceding 30-minute return** (the rolling 30-minute return ending one M5 bar before the current signal) with the current day's Q85 threshold. The signal is eligible when the current 30-minute return is at/above Q85 and the preceding 30-minute return was below Q85. It does not compare a five-minute return with a thirty-minute threshold.

All other locked R305 parameters remain unchanged. The same once-per-day causal threshold refresh is used for the XAU Q50 underreaction filter described in the additional R306 preregistration.
