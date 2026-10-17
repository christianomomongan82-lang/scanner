# R289 — Continental Europe Index Cash-Open Gap Continuation (preregistration)

Locked: 2026-10-17, before calculating gap thresholds, trades, returns, or PnL.

## Parent evidence and hypothesis
- New instrument/session family: continental European cash-open gaps in DEUIDXEUR (Germany 40), FRAIDXEUR (France 40), and EUSIDXEUR (Euro Stoxx 50).
- R283's US cash-open gap-fade specification failed. That outcome does not show whether European gaps continue, and its assets/session are not reused here. The economic hypothesis is that an unusually large overnight repricing in related European indexes may persist after the first ten minutes of the cash session rather than immediately fill.
- Primary child ID: R289_CONTINENTAL_EUROPE_GAP_CONTINUATION.
- Matched opposite-direction fade is a predeclared diagnostic control only. It cannot be promoted based on same-sample comparison.
- Only one selected trade is permitted per continental cash-session date to avoid stacking correlated indices.

## Data source and quality audit
- Cached R205 GitHub Actions run 38160487617; M5 BID-only snapshots, no ask-side history:
  - DEUIDXEUR artifact 11710710062; archive SHA-256 `0023f09e6697ce5d88a88734b42bd9ad0f676d4b55ba102466efa7e7b01cfaaa`; extracted M5 SHA-256 `7ad37cb19545eef6111b928a97322c06c9f2478030a0c4282669542262303af4`.
  - FRAIDXEUR artifact 11710800007; archive SHA-256 `b2c9c6740836dd04039f74d1300e714e6dc2d144848c6db2d09b0b0063e7d8e9`; extracted M5 SHA-256 `cc9e3d3b808d1bd284def820473658aa0ec319fe167b6355e0bcaddc83eebbf4`.
  - EUSIDXEUR artifact 11710326105; archive SHA-256 `f81cae65f5eb5925a4b8ac416d86868bc7aaac33836453eb22cba7defedf63f7`; extracted M5 SHA-256 `f47aa66caf714570140c63ce4056db4c426b8ff4ff4f65e5fdd9920a402a1d48`.
- Source spans 2016-01-04 to 2026-10-09. M5 BID-only; no tick-level fills.
- Data-quality-only session screening, in Europe/Berlin time, found complete eligible cash sessions (102 M5 bars, 09:00–17:25, valid OHLC, no duplicates, no repeated-flat candidate bars): DEUIDXEUR 2,481 across 2017–2026; FRAIDXEUR 2,458; EUSIDXEUR 2,023. EUSIDXEUR has lower session availability, especially early years. These are coverage counts only, not strategy outcomes.
- The UK index is excluded because its cash open is an hour earlier, preventing a fair same-time selection from the continental basket.

## Locked event, entry and exit rules
1. Convert source timestamps to `Europe/Berlin`; consider Monday–Friday local dates only.
2. A usable session requires exactly the 102 expected M5 bars from 09:00 through 17:25, valid OHLC, unique timestamps, and no repeated-flat candidate bar.
3. For each symbol/date, require a previous valid cash session for that symbol with a close date no more than four calendar days earlier. Previous-session reference price is the prior eligible session's 17:25 bar close. If no qualifying reference exists, skip the gap.
4. Compute opening gap percentage = (today's 09:00 open / previous valid session's 17:25 close − 1) × 100.
5. Fit each symbol's Q80 absolute gap percentage using only eligible 2017–2020 observations. Freeze the values. On each date, calculate `score = abs(gap_pct)/symbol_Q80` and select the highest score across the three symbols; alphabetical symbol is the deterministic tie-break. Skip if score < 1 or gap equals zero. All selected markets share the same local 09:00 cash open, so selection introduces no later-open lookahead.
6. Follow the gap sign. The signal is known at the 09:05 bar close; five-minute phone/manual execution delay means entry at the 09:10 bar open.
7. Let gap distance in price points = abs(today's 09:00 open − previous session close). At entry, set target one gap-distance in the continuation direction, and stop 0.75 gap-distance in the opposite direction. For LONG: TP = entry + gap_distance; SL = entry − 0.75×gap_distance. SHORT is mirrored.
8. Monitor M5 bars beginning with the entry bar through the 17:25 bar. Handle gaps through levels by filling at bar open when worse for stop / better for target; when stop and target are both touched within one M5 bar, assume stop first. If neither is hit, exit at the 17:25 bar close. Do not infer tick-level ordering.
9. Define gross R = signed exit-price change / (0.75×gap_distance). Define round-trip cost in price points as `entry_price × cost_bps / 10,000`; net R = gross R − cost_points/(0.75×gap_distance). Also report net directional bps = signed price return in bps minus the cost stress. Costs 1/2/4 bp are modeling assumptions, not observed provider costs.
10. The matched fade control uses exact same events and exits/risk distances but reverses direction. It is diagnostic only.

## Locked chronological test and gates
- Discovery: 2017–2020.
- Validation: 2021.
- Calculate 2022–2026 outcomes only if every discovery and validation gate below passes. Even if opened, these periods are not a pristine program-level holdout because the project's wider research has repeatedly inspected post-2021 markets.
- Primary scorecard uses the continuation stream's net R at 2 bp:
  - Discovery: at least 200 trades; PF in net R ≥ 1.05; aggregate net R > 0; at least 3 of 4 calendar years with positive net R; PF in net R at 4 bp ≥ 0.90.
  - Validation: at least 50 trades; net R > 0 and PF in net R ≥ 1.00 at 2 bp; PF in net R at 4 bp ≥ 0.90; four-week circular block-bootstrap 95% CI lower bound for mean weekly net R at 2 bp > 0 (5,000 replicates, fixed seed 289).
- Every gate must pass; any single miss means binary verdict GAGAL and the locked candidate is closed. No threshold, gap direction, stop/target ratio, timeframe or entry-time retuning after seeing results.
- Report the matched fade stream across the same events, but its metrics cannot be used to choose a winner or rescue the continuation child.
- No funded-ready status from this study alone: M5 BID-only prices, modeled costs, no validated CFD contract conversion, and no floating-equity DLL/MLL challenge replay.

## Reproducibility
- No GitHub Actions backtest will be run. Signal/stop simulation and statistics execute locally in Python.
- Archive exact runner, aggregate JSON, discovery/validation trade ledger, yearly and weekly summaries, session-quality audit, hashes and binary verdict in GitHub.


## Implementation clarification — 2026-10-17 (timestamp fields only; no PnL-rule change)

The first locked-screen run exposed a reporting-label issue: M5 rows are timestamped at bar start, whereas the forced session-close fill uses the 17:25 bar's close, which occurs at 17:30 local. On the corrected runner, the trade ledger will label stop/target event times only to the triggering M5 bar (not claim an exact tick timestamp), and the forced close as 17:30 local. This changes no entry, exit price, intrabar ordering, PnL, cost, gate or signal rule. The identical historical metric calculation will be rerun to verify the corrected implementation after this amendment.
