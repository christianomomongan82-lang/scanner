# R303 DQ1 — Pre-outcome execution-eligibility clarification

**Timestamp:** 2026-10-19 UTC, before the event eligibility audit and before any candidate PnL.
**Amends:** `R303_EURUSD_SPREAD_SHOCK_REVERSION_PREREGISTRATION.md`
**Purpose:** Remove ambiguity around delayed execution if flat-filled/non-tradable minute rows have been excluded.

For both T+5 primary and T+10 delay stress, locate the first active paired M1 bar whose start is at or after the specified signal-close-plus-delay timestamp. It must occur within five wall-clock minutes of that earliest eligible timestamp. If no such bar exists, record `NO_ACTIVE_QUOTE_IN_ENTRY_WINDOW`. On that first active quote only, apply the locked spread-normalization gate (open spread <= 1.5 × pre-event baseline); if it fails, record `SPREAD_NOT_NORMALIZED_ON_FIRST_ACTIVE_QUOTE` and skip. Do not wait for a later favorable spread. This change is an execution-eligibility clarification, not a price-performance or signal-threshold change.

All other locked rules remain unchanged. The audit must be committed before PnL is calculated.
