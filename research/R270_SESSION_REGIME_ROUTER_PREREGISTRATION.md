# R270 — Asia-session regime router (EURUSD M1 BID/ASK)

Date: 2026-10-16
**Purpose:** test a pre-locked, two-module signal router. This is a new exploratory composition, not a rescue/tuning of R260/R261/R269. The primary downstream question is whether the integrated stream gives a better realistic funded-target completion profile than either module alone; PF remains a diagnostic.

## Input and reproducibility
- Input: GitHub Actions data-only artifact 11959096102 from run 38697080604; EURUSD-M1-Dukascopy-BID-ASK-2016-2025, monthly Dukascopy M1 BID/ASK, UTC timestamps, 2016-01-01 inclusive to 2026-01-01 exclusive.
- Calculations run locally in Python. The acquisition workflow performed data collection only, not backtesting. No backtest GitHub Actions workflow may be run.
- Use only timestamps common to BID and ASK; do not fill missing minute bars. Convert UTC to Europe/London for session/DST handling. Preserve raw BID/ASK sides.
- Splits locked: discovery 2016–2020; validation 2021; exploratory forward 2022–2025. The latter has already been inspected in earlier research and is not a clean untouched promotion holdout. 2026 is absent from this archive.
- Entry quote is at exactly 08:06 London local time, after Asia feature bar 07:59 closes at 08:00 and a five-minute manual execution delay. If 08:06 is absent, skip. Long entry uses ASK; short entry uses BID. Long exit monitoring uses BID; short uses ASK.
- Primary incremental cost: +1.0 pip per trade beyond observed BID/ASK; sensitivity +0, +0.5, +2 pips. Apply additional cost to trade PnL, not by distorting signal prices.

## Causal feature window
For each London-local weekday, use M1 bars whose open timestamps are 00:00–07:59.
- Asia range = max BID high − min BID low; midpoint = average of those extrema.
- Asia net move = last available BID close in window − first available BID open.
- Asia path length = sum of absolute consecutive BID close-to-close changes within the window. Efficiency ratio (ER) = abs(net move) / path length, only if path length > 0.
- Close location = (last close − range low) / Asia range.
- Require at least 450 unique minute bars in the feature window, nonzero range and the exact 08:06 entry timestamp. Do not synthesize missing bars.

## Locked router (one eligible trade maximum per London-local day)
**Module A — directional continuation**
- Active when ER >= 0.30 and Asia close location >= 0.75 with positive Asia net move (LONG), or close location <= 0.25 with negative net move (SHORT).
- Entry at the delayed executable quote at 08:06.
- Stop is the Asia midpoint. Invalidate if entry is at/beyond the stop, if the stop/target was touched between the signal close and delayed entry, or if R:R to the fixed target is below 1.00.
- Target = entry + 1.5 × (entry − midpoint) for LONG; entry − 1.5 × (midpoint − entry) for SHORT.

**Module B — balanced-session fade**
- Active when ER <= 0.15 and the last Asia close is in the outer quartile of the range (location >= 0.75 => SHORT; location <= 0.25 => LONG).
- Entry at the same delayed executable quote at 08:06.
- Target = Asia midpoint.
- Stop is 0.25 × Asia range beyond the swept-side edge (SHORT stop = range high + 0.25×range; LONG stop = range low − 0.25×range).
- Invalidate if entry is at/beyond stop/target, if stop/target was touched between feature-window close and entry, or if reward/risk < 1.00.

## Conflict/exit policy
- ER cannot satisfy both modules. If ambiguous or invalid, do not trade that day; do not choose another signal later that day.
- Max holding = 8 elapsed hours from entry. At each M1 bar, stop has priority if stop and target are both touched. If the open is through a stop, fill at the worse executable opening quote; target fills at target. Otherwise exit at the first available bar open at/after the 8-hour time limit. Missing bars remain missing.
- Long stop/target observations use BID OHLC; short stop/target observations use ASK OHLC. Use the corresponding executable side for stop-gap and time-stop fills.
- No pyramiding, no overnight hold, no trailing stop, no parameter sweeps, no post-result rule changes.

## Comparisons and primary gates
Report module A alone, module B alone, router A/B, and the count/skip reasons under the identical data/entry/cost rules. Report risk-normalized R distribution, net R, PF, expectancy, sample size, per-year/segment outcomes, maximum drawdown and bootstrap uncertainty.

A separate reference-only challenge path diagnostic uses a $6,000 Phase 1 starting balance, +8% target, $5,400 static floor, 5% daily-loss proxy, and then a fresh $6,000 Phase 2 starting balance with +5% target. Fixed-fractional risks tested are 0.25%, 0.50%, 0.75%, 1.00% per trade; positions are sized from current realized equity. Daily reset is UTC solely as a proxy. Intratrade price-path data is used for drawdown where available. These assumptions are not a verified FundedNext challenge engine because current official server-time/reset/floating-equity/DLL semantics and actual account-specific costs have not all been evidenced. Do not label this diagnostic funded-ready.

For each stream/risk, estimate phase target-hit-before-breach odds, both-phase completion proxy, time-to-target quantiles, loss-limit breaches and failure reason, preserving order/clustering with four-week blocks. Compare router against A and B under identical assumptions. Report PF only as a diagnostic, not the objective.

**Historical signal-stream screen LULUS requires all:** (1) the router is net positive at +1 pip in both discovery and 2021 validation; (2) both modules have >=50 trades in discovery and >=20 in validation, so conditional results are not based on tiny samples; (3) on the already-inspected 2022–2025 diagnostic period, router target-completion proxy is better than both standalone modules at the same risk settings without a worse breach rate; (4) the weekly block-bootstrap lower 95% bound of forward net R is >0; (5) costs +2 pips retain positive forward net R; (6) 2022–2025 annual results are net positive in at least 3 of 4 years.
A high-risk configuration is not promoted merely because it sometimes hits the target. If any gate fails, locked R270 is GAGAL; no retuning. Even a positive historic screen would not independently promote the system because the forward period is contaminated by prior inspection and the funded-rule proxy is not verified. A failed screen closes this exact router.
