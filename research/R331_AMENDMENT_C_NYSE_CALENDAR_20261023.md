# R331 Amendment C — exchange calendar, half-days and missing-source gate

**Committed before any R331 event/PnL calculation.**

## Session calendar

- Price bars are grouped by New York local trading date using the explicit America/New_York timezone; DST is handled through timezone conversion, not a fixed UTC offset.
- Full NYSE sessions require the 78 complete M5 bars labelled 09:30 through 15:55 ET (final bar closes 16:00).
- Explicit NYSE half-days require the 42 complete M5 bars labelled 09:30 through 12:55 ET (final bar closes 13:00). The fixed 30-minute exit must remain at or before the last in-session M5 open; a half-day setup that cannot satisfy this is skipped.
- Known regular holidays include New Year's, MLK Day, Presidents' Day, Good Friday, Memorial Day, Juneteenth, Independence Day observed, Labor Day, Thanksgiving, Christmas observed, and the 2025-01-09 market closure for President Carter's state funeral. Early closes include the day after Thanksgiving, a weekday Christmas Eve, and the scheduled trading day immediately before the observed Independence Day closure.
- Previous-session close comes from the immediately previous scheduled NYSE session's own last complete M5 close (15:55 for full session, 12:55 for half-day). If that previous scheduled session's quote stream is incomplete, today's setup is skipped. Never skip over an incomplete prior session to reuse an older close.

## Source data integrity

- Every scheduled exchange trading date between 2023-10-23 and 2026-10-21 must have at least one RTH quote bar in the raw source. If an entire expected trading session is absent, stop with GAGAL — DATA/PROCESS rather than letting the base close silently jump across it.
- Incomplete M5 groups are not synthesized or filled. A regular session missing any of its required complete M5 labels is invalid, and cannot generate a signal. If an invalid date is the immediately previous scheduled trading session, the current date also cannot use a stale fallback base close.
- VXN must contain an observation for each expected US trading date from its first available date (2023-10-25) through 2026-10-21. Missing expected VXN daily closes are a data/process stop, not a stale-value forward-fill.

These calendar/data rules add no strategy thresholds and were fixed before price outcomes. The raw VXN value series remains local only; its date coverage and local file hash may be published, not the series itself.