# R307/R308 — Pre-outcome audit and eligibility decision

**This audit was run before calculating either candidate's PnL.** The protected cutoff at 2026-01-01T00:00:00Z was applied before any features/events. No signal PnL or outcome-based metric was calculated.

## Source integrity

- Source: existing GitHub EURUSD M1 BID/ASK data-only artifact #11959096102, collection run #38697080604.
- ZIP SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`; 4,415,493 raw rows per side before cutoff.
- BID/ASK timestamps matched exactly; 0 invalid OHLC, 0 negative open/close spreads.
- Registered repeated-flat filter removed 696,795 rows; 3,718,698 active M1 timestamps remained. The exact aggregator formed 736,076 complete active M5 bars, with 7,882 gaps greater than five minutes. Gaps were not filled.

## R307 — weekday-conditioned session drift eligibility

Registered schedule: Monday/Tuesday SHORT EURUSD, Wednesday–Friday LONG EURUSD, entry 08:05 Europe/London and time exit at 12:00; D is median of prior 20 complete 48-bar sessions and requires at least 15 prior complete sessions.

| Period | Complete eligible scheduled events before outcome calculation |
|---|---:|
| Discovery 2017–2020 | 1,028 |
| Validation/diagnostic 2021–2025 | 1,281 |

These meet the preregistered sample-size gate before outcome calculation. This supports continuing to the locked PnL screen; it is not evidence of an edge.

## R308 — Friday-to-Monday weekend carry eligibility failure

The registered R308 requires a genuine data gap of at least 24 hours, ending at an active Monday reopen after a Friday observed quote, plus an exact Friday 21:00 entry.

| Eligibility check | Count |
|---|---:|
| Complete Friday 18:00–18:55 UTC risk windows | 503 |
| Exact Friday 21:00 UTC active entry bars | 178 |
| Qualifying active reopen gaps meeting the literal Friday-to-Monday >=24h condition | **2** |
| Eligible event paths across 2017–2025 | **2** (1 discovery; 1 validation) |

The paired archive's post-flat-filter M5 timeline contains only two gaps meeting the registered >=24h Friday-to-Monday definition, both around New Year's holiday closures, not a weekly sequence of genuine weekend closures/reopenings. The data therefore do not provide the registered weekly event stream needed to test R308. By its locked minimum sample gate (at least 150 validation trades), R308 is **GAGAL — DATA/SAMPLE before PnL**. No R308 outcomes were calculated. Do not silently reinterpret weekend-active rows as real executable FX weekend quotes, and do not relax the gap definition after seeing the sample count.

## Audit artifact integrity

- Local full row-level pre-outcome eligibility CSV SHA-256: `9a8c7f0512f5b76565287ddbac22d44f784b647844903a85686cefbdf05ef348` (210,615 bytes).
- Local pre-outcome audit JSON: `R307_R308_preoutcome_audit.json`.
- This summary has been committed before R307 outcome calculations. The local row-level CSV is recorded by hash and is not represented as a decoded GitHub row file.
