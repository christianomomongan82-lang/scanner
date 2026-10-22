# Market Response Model v2 — Preregistration

**Registered before V2 outcomes are calculated.** This is a new decomposition test motivated by V1's finding that spread features dominated gain importance; it is not a retune of V1.

## Hypothesis

Separating price-response prediction from transaction cost may prevent the prediction model from mostly learning spread avoidance. Train the model on gross midpoint TP/SL/time-stop PnL, remove all spread-derived features from the predictor, then apply observed executable BID/ASK PnL and a separately locked entry-spread gate to the selected trade stream.

## Fixed rules

- Universe/data: same retained GitHub artifact 11959096102, EURUSD Dukascopy M1 BID/ASK 2016–2025.
- Decision every 30 minutes at :29/:59 UTC; require 240 exact contiguous prior minutes.
- Entry exactly five minutes after signal bar close; skip if no complete 120-minute minute-by-minute forward path.
- Model label: midpoint-only gross PnL, TP 15 pips, SL 10 pips, maximum hold 120 minutes; stop-first if both barriers are hit in one M1 candle.
- Prediction features: same point-in-time price-action/context features as V1, but remove all spread-derived features. Add side and signed-return interaction columns.
- Model: one fixed LightGBM regressor, 350 trees, learning rate 0.035, 23 leaves, min child samples 800, L1 0.2, L2 8, row/column sampling 0.85, seed 20261023. No parameter search.
- Training: 2016–2019 only.
- Execution cost gate: reject an entry if its observed Ask-open minus Bid-open spread exceeds the 90th percentile of the prospective entry spreads in the 2016–2019 training sample. The spread gate is calculated from training data only.
- Score cutoff: max(1.0 gross pip, 75th percentile of max LONG score / SHORT score in 2020–2021). This uses prediction scores only, not validation PnL.
- Validation: 2020–2021. Forward diagnostic: 2022–2025. Model, score rule and spread cutoff remain frozen.
- Actual policy PnL: executable fills on correct quote sides, same nominal TP/SL/time stop, stop-first intrabar tie-break, and +0.5 pip incremental friction; report +1.0 pip stress as well.
- One position at a time; don't open while a prior trade is still active.

## Decision gates

V2 fails if selected trades are net negative after the registered cost model or show unstable negative annual outcomes. No 2020–2025 threshold retuning after results. The years 2020–2025 are not pristine program-level holdouts due prior project research, so even a positive V2 result cannot alone authorize a funded challenge. No access to the protected XAUUSD 2026 outcome window.

## Why this differs from V1

V1 asked the model to predict net executed PnL while including spread features, allowing it to use spread as a dominant predictor. V2 learns gross midpoint response from price/context features only, then evaluates transaction costs separately. Its aim is to diagnose directional information independently from execution friction, not to optimize a threshold or rescue V1.
