# R313 — XAUUSD Spread-Shock Normalization Reversion — Preregistration

Registered: 2026-10-21. Status before computation: **LOCKED / PnL not yet inspected**. Pre-computation execution clarifications: (a) spread normalization at the delayed entry uses the opening quote spread, not the not-yet-known closing spread of the entry bar; (b) timestamps are bar-open times, so a five-minute manual delay after the signal bar closes means entry at `t+10m`, two rows later on a contiguous M5 stream.

## Mechanism family and lineage

- Primary family: `XAU_LIQUIDITY_DISLOCATION` (new family; quoted-spread shock / temporary liquidity withdrawal, followed by price dislocation and quote normalization).
- Related but non-parent comparisons: R274 (M5 impulse continuation), R298 (London Asian-range sweep/reclaim), R302 (PM auction extension fade), R305/R306 (cross-asset USD impulse). Those hypotheses are closed and may not be tuned or relabeled as R313.
- Hypothesis: in XAUUSD spot/CFD quotes, an unusually wide observed spread paired with an unusually large short-horizon midpoint move can reflect temporary liquidity withdrawal. If the spread normalizes within the five-minute execution delay, fading the shock toward the pre-shock price may outperform a fixed-risk baseline after quote-side fills and realistic added-cost stress.
- This is a falsifiable hypothesis, not an asserted known edge. Dukascopy quote spread may not proxy the intended FundedNext account's spread or executable liquidity.

## Source and protected data policy

Use the checksum-verified paired Dukascopy XAUUSD M5 BID/ASK source already archived in this repository. Apply an exclusive cutoff at `2026-01-01T00:00:00Z` before any rolling feature or trade outcome is built. Discovery/diagnostic split: 2016–2020; validation/diagnostic split: 2021–2025. The latter is research-contaminated due prior project exploration and is not pristine program-level OOS. Do not calculate, preview, or score the reserved 2026 outcomes; a pass of this historical screen is necessary but not sufficient for any eventual final-holdout test.

## Fixed signal rules

1. Timestamps are UTC M5 bar-open times. A bar is eligible only if BID and ASK OHLC are paired at that timestamp, both OHLC rows are non-static, and observed OHLC values are valid. Missing rows remain missing; do not synthesize bars.
2. At a completed signal bar t, define close spread `spr_t = ask_close_t - bid_close_t` and midpoint close `mid_t = (ask_close_t + bid_close_t)/2`. Define the 15-minute shock return as `mid_t - mid_{t-3}`.
3. Spread shock: `spr_t` must exceed the trailing 95th percentile of close spreads from the previous 288 eligible, completed bars, excluding t. Price shock: the absolute 15-minute midpoint change must exceed the trailing 95th percentile of absolute 15-minute midpoint changes from the previous 288 eligible bars, excluding t. Use only fully observed timestamps at the exact three-bar lag; no forward fill.
4. On a valid joint shock, schedule an entry five minutes after the signal bar **closes** (timestamp `t+10m` from the signal bar's open, normally the M5 bar two rows later). The direction fades the 15-minute shock: buy after a negative shock, sell after a positive shock. At entry, require opening quote spread `ask_open - bid_open` at the delayed entry timestamp to be at or below the trailing 95th percentile of close spreads over the prior 288 eligible completed bars. The threshold excludes both the signal and entry bars. This is a pre-computation causality correction: the entry-bar close is not known at its open. If opening spread remains wide, skip the event; never enter at the event's historical quote.
5. Target is the pre-shock midpoint `mid_{t-3}`. Initial stop distance is the trailing median BID true range over the previous 144 eligible completed M5 bars, excluding t; use the midpoint shift only for the signal/target. Entry is executable: long enters at ASK open and exits at BID; short enters at BID open and exits at ASK. Do not mix bid/ask sides.
6. Require target reward / planned stop risk >= 1.00 at the actual delayed entry, or skip. Stop price is entry executable price minus/plus the fixed stop distance for a long/short, respectively. Fixed target uses the pre-shock midpoint translated to the relevant executable exit side at test time. Position is closed at stop or target on executable-side intrabar highs/lows; if both barriers are touched in the same bar, assume stop first. If neither is touched, exit at the last executable close at or before 60 minutes after entry; if the quote timestamp sequence is incomplete, terminate at last available paired quote before the horizon and mark the trade's exit reason as data-gap/time.
7. Accept at most one signal/trade per New York calendar date, and at most one open position. Consume a qualifying signal even if its spread fails to normalize, to avoid repeated attempts at the same shock. No overlapping trades.
8. No filtering by weekday, year, news calendar, direction, trend, or manually identified exceptions. No parameter grid, direction inversion, threshold changes, or post-hoc session restriction.

## Cost model and test grid

Use observed BID/ASK execution as base cost. Deduct additional round-trip friction of $0.00, $0.10, $0.30 (primary), and $0.50 per ounce from trade PnL. For each trade compute initial risk from the planned stop distance at delayed entry; `R = (direction * (exit_exec - entry_exec) - added_cost) / planned_stop_distance`. A stop and target are evaluated on quote-side executable prices; do not credit the midpoint as an executable fill.

## Required outputs and gates

Save row-level event ledger including every joint shock event, spread-normalization pass/skip, planned delayed entry, stop/target, realized exit, exact timestamp/side, gross dollars per ounce, added cost and R. Also save a separate cost-sensitivity trade ledger; year and period summaries; data manifest and checksums; weekly series including zero-trade weeks; 10,000-replicate circular four-calendar-week block bootstrap with fixed seed 313.

Primary score is challenge viability, not PF alone. Historical necessary gates:
- >=100 completed trades in both discovery and validation (if not met: insufficient sample, not a pass).
- Positive net R at +$0.30/oz in both periods.
- Validation PF_R >=1.05 at +$0.30/oz.
- >=3 of 5 validation years positive at +$0.30/oz.
- Validation weekly-net-R bootstrap lower 95% bound >0 at +$0.30/oz.
- Positive validation net R and PF_R >=0.90 at +$0.50/oz.
- Realized trade frequency, loss clustering, and stop distance must be compatible with a phone-execution funded path, but those checks cannot override any preceding failure.

Any failed hard gate = **GAGAL**; do not open 2026 or make rescue variants from the same sample. A historical screen pass only authorizes a separate readiness audit; it does not itself authorize live trading or imply a FundedNext pass. Unknown account-specific contract values, commissions, swaps, spread behavior, slippage, server reset timezone/DST and eligibility remain execution gates.
