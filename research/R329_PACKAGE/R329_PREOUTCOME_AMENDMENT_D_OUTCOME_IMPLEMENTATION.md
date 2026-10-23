# R329 Pre-outcome Amendment D — Frozen Economic Implementation
Date: 2026-10-23 UTC
Status: **committed before any R329 outcome/PnL calculation**

This amendment locks the implementation file `outcome_runner.py` at GitHub commit `3905264282debf25924e41820654a50c470a2e60`. It adds no signal, instrument, parameter, period, or selection-rule change. It translates the existing R329 registration into an executable result contract.

## Run authorization
The script fails closed unless its input preflight summary explicitly says:
- `data_gate = PASS`;
- `candidate_sample_gates_pass = true`;
- `outcomes_computed = false`;
- the exact horizon set is 13, 26, and 39, and every registered sample gate is true.

The source CSVs are rechecked against the already pinned R323/Dukascopy manifest before any outcomes. Exact paired BID/ASK times are used; flat/static bars remain in the archive but cannot be signal, entry, or exit bars; missing bars are never filled.

## Fixed outcome definitions
- Signal: sign of each pair's H eligible weekly-observation log return, with volatility calculated from the trailing 13 weekly observations.
- Signal decision: Tuesday 10:00 UTC H1 close; baseline executable entry proxy: exact Tuesday 12:00 UTC observed open; exit at the next Tuesday 12:00 UTC observed open. This is a one-hour timestamp-resolution proxy, not a measured exact five-minute fill.
- Longs enter ASK and exit BID; shorts enter BID and exit ASK.
- Net weekly portfolio R is aggregated across the registered risk weights. PF_R is calculated from the chronological weekly portfolio R series, not pooled per-leg trade outcomes. Zero-trade scheduled weeks are retained as zero.
- Registered cost scenarios: extra slippage 0 / 0.5 / 1 / 2 pips per active leg and adverse swap proxy 2 / 4 pip-equivalents per seven-day hold, plus $10 round-trip commission per 100,000-base-unit standard lot converted into pair pips. The swap proxy is not represented as a verified provider swap quote.
- The prespecified primary case is +1 pip slip / 2-pip-week swap proxy; the stress case is +2 pip slip / 4-pip-week swap proxy.
- Bootstrap: 10,000 four-week circular moving-block samples with seed 329 and zero-trade weeks retained. Holm step-down adjustment is applied across the three discovery horizons.
- The horizon is selected by primary-cost discovery mean weekly R only; confirmation does not select a replacement.

## Boundaries
This amendment does not make the historical years independent OOS. Even an economic-screen pass cannot alone establish funded readiness. No XAUUSD 2026 data are accessed; no FundedNext challenge path is run by this economic runner. The challenge simulator is allowed only after the registered economic gates and independent-evidence requirements are satisfied.

No R329 PnL was calculated when this amendment was committed.
