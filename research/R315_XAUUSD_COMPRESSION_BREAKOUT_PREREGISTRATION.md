# R315 — XAUUSD M5 Compression-to-Range Breakout — Preregistration

Registered: 2026-10-21. Status before computation: **LOCKED / R315 PnL not yet inspected**.

## Mechanism, distinct from prior tests

Test a volatility-compression-to-expansion breakout: a narrow twelve-bar price range forms relative to its own trailing history; price then closes beyond the prior twelve-bar extreme. The mechanism is range release/expansion, not blind time-of-day drift (R314), a lone impulse candle (R274), range sweep/reclaim (R298), post-auction extension fade (R302), or spread-shock reversion (R313). This is a falsifiable hypothesis, not a claimed edge.

## Data / split protection

Use checksum-verified paired Dukascopy XAUUSD M5 BID/ASK. Apply a strict exclusive cutoff of `2026-01-01T00:00:00Z` **before** any signal feature, entry, or outcome construction. Discovery: New York calendar years 2016–2020. Validation diagnostic split: 2021–2025; due previous project exploration this is not pristine program-wide OOS. Do not calculate, display, or score any 2026 outcome. Preserve missing gaps and exclude static/inactive bars; never synthesize bars.

## Fixed signal / trade logic

1. All times are M5 bar-open timestamps. At completed bar i, use midpoint OHLC `(BID+ASK)/2` for signal features. Define the prior-channel high/low as max midpoint high/min midpoint low over the 12 eligible paired active bars immediately before i; exclude bar i. Define prior-12-bar range as that high minus low.
2. Compression condition: prior-12-bar range must be <= the 20th percentile of the prior 288 completed 12-bar range observations, excluding the present signal bar and its range window. Require all 288 range observations to be fully defined on consecutive eligible bars; do not forward-fill or create bars.
3. Breakout condition: completed midpoint close of bar i must exceed prior-channel high by at least 0.10 times the median BID true range across the 12 completed bars before i (LONG), or fall below prior-channel low by at least the same amount (SHORT). If both directions somehow qualify, skip the event. No extra trend/session/calendar filters.
4. Alert is available at signal-bar close `i+5m`. Wait a further five minutes for manual execution; planned entry is exactly `i+10m`, the paired active M5 open. At that delayed entry, the executable quote-side entry (ASK open for long, BID open for short) must still be beyond the original breakout threshold in the breakout direction; otherwise skip. Only the first valid signal per New York calendar date can be attempted. One position at a time.
5. Initial stop distance = median BID true range over the 12 active bars before i, excluding the signal bar. Reject zero/missing distance. Stop = 1.00 × this distance from the actual delayed executable entry; target = 1.50 × the same distance. Long exits are executable on BID; short exits on ASK. If stop and target are touched within one bar, assume stop first. If price gaps through stop, fill at the worse executable opening quote; target is not improved beyond its limit. No fractional exits or partial fills.
6. Maximum holding time 60 minutes after delayed entry. If a missing active bar interrupts the quote grid before exit, flatten at the last observed executable close and label `data_gap_time`; if neither barrier is reached by the horizon, exit at the last executable close by 60 minutes. Do not fill or synthesize missing bars. Require 60 minutes of source room before the strict cutoff.
7. Deduct additional round-trip friction of $0.00, $0.10, $0.30 (primary) and $0.50 per ounce on top of the observed BID/ASK fills. Per-trade `R=(direction × (exit executable − entry executable) − added_cost)/initial_stop_distance`. Costs are not used to change signal eligibility except by final performance accounting.

## Required outputs

Event ledger must show every compression candidate, qualifying breakout, delayed-entry pass/skip, and reason. Trade ledger must include all four cost streams, entry/exit timestamps and quote-side prices, stop distance, stop/target, exit reason and realized R. Save year/period summary, zero-inclusive weekly net-R series, source manifests/checksums, and 10,000-replicate circular four-calendar-week block bootstrap (seed 315) of the validation primary-cost weekly series.

## Hard gates

A registered screen passes only if **all** hold at +$0.30/oz:
- >=100 completed trades in discovery and >=100 in validation;
- net R positive in discovery and in validation;
- validation PF_R >=1.05;
- at least 3 of five validation calendar years have positive net R;
- 95% block-bootstrap CI lower bound for validation mean weekly net R > 0.
At +$0.50/oz, validation net R must remain positive and PF_R >=0.90.

Any failed condition = **GAGAL**; no threshold change, direction inversion, or session/weekday rescue on this same sample. A historical screen pass authorizes a separate execution-readiness review, not live trading or a funded pass claim. Actual intended-account contract specs, fees, swaps, server reset/timezone/DST, spread/slippage and phone-execution handling remain separate gates.
