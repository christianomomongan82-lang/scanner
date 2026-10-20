# R306 — EURUSD USD-Factor Shock with XAU Underreaction (LOCKED PREREGISTRATION)

**Locked before any R306 trade outcomes are calculated.** This is the second candidate in the same-response cross-asset batch, with a conditional catch-up hypothesis different from R305's unconditional transmission.

## Hypothesis

When EURUSD makes an unusually large 30-minute move, that move can proxy a common USD-factor shock. Gold should tend to move in the same direction as EURUSD if USD is the common driver. This catch-up hypothesis predicts the delayed XAUUSD move only when gold's own preceding 30-minute move was unusually small, suggesting underreaction rather than already-completed transmission.

## Signal and execution

- Use exact paired timestamp joins between EURUSD M1 BID/ASK-derived complete M5 bars and XAUUSD M5 paired BID/ASK. No forward fill or synthetic bars.
- Exclude every outcome timestamp >= 2026-01-01T00:00:00Z before features/thresholds/outcomes. XAU 2026 is protected.
- At signal bar start t, EURUSD 30-minute midpoint return is the M5 midpoint close at t relative to t-30 minutes; it is known at t+5 minutes.
- Refresh once per UTC day: EURUSD shock threshold = 85th percentile of absolute EURUSD 30-minute midpoint returns over the prior 20 complete UTC calendar days, with >=1,000 prior valid observations. It is held constant for the day.
- XAU underreaction threshold = 50th percentile of absolute XAU 30-minute midpoint returns over the same prior 20 complete UTC calendar days, with >=1,000 observations; held constant for the UTC day.
- Candidate event when (a) absolute EURUSD 30-minute return >= its Q85, (b) preceding 30-minute EURUSD absolute return at the preceding M5 timestamp was below that same Q85, and (c) absolute XAU 30-minute return at t is <= its Q50. Conditions use only information known at signal close.
- Direction: follow EURUSD return sign in XAUUSD. EURUSD positive => long XAU; EURUSD negative => short XAU. No post-hoc direction flip.
- Entry: exact XAU M5 open at t+10 minutes (five minutes after signal close); if missing/inactive, skip. Long enters ASK, short enters BID.
- Risk distance: 1.5 x median BID true range of the prior 12 complete contiguous XAU M5 bars before entry. Stop 1R, target 1.5R, max holding 60 minutes (12 bars). Long exit/stop/target on BID; short on ASK. Stop-first on same-bar collisions; gap through stop fills at adverse open; time exit at executable close at 60 minutes.
- Require all 12 monitoring bars present and contiguous. One open position maximum; skip entries while a trade is open.
- Cost stress above observed BID/ASK: +$0, +$0.30 and +$0.50/oz per round trip; primary +$0.30. T+15-minute execution stress is also fixed: entry at exact t+20-minute XAU M5 open; same signal, stops/targets and 60-minute holding measured from delayed entry.
- Mirror-direction stream may be reported as diagnostic only and cannot replace the locked same-direction candidate after outcomes.

## Data provenance and periods

- EURUSD data-only artifact #11959096102; ZIP SHA-256 b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e; BID b588b7e07d9fea3748a84a1e3ecf29ccb2ea1d8ea52503f8579928a3cd4990cc; ASK 52e53dbb22ef11aee2d2c3d5e5b4ded6659d58c086189a327559253727e52f8b.
- XAU data-only artifact #12031270051; ZIP SHA-256 2cde8338800fd7f4d5d4628512201c16757ef06bd90d51ffdc8ef9bea425ba1a; BID b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575; ASK b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9.
- Discovery 2017–2020; validation/diagnostic 2021–2025 (not pristine program-level OOS; already contaminated). 2016 warm-up only. No 2026 PnL.
- R305 DQ1 threshold amendment applies to the daily causal threshold refresh.

## Hard gates

All conjunctive: integrity/executable event paths pass; >=100 trades in discovery and >=150 in validation; net R > 0 and PF_R >=1.05 in each period at +$0.30/oz; net R > 0 and PF_R >=1.00 in each period at +$0.50/oz; >=3/4 discovery years positive at primary cost; validation four-week circular bootstrap (10,000 samples, seed 306; all calendar weeks including zero-trade weeks) 95% lower bound for weekly net R >0; positive net R under T+15 execution delay at +$0.30/oz; exact code/config, full trade ledger, skip audit, weekly input, report and metrics reproducible from repository artifacts.

Any failure means **GAGAL**; do not modify threshold, direction, holding time or stop/target on these same periods. The 2022–2025 diagnostic is available to score only after the preregistered discovery/validation gates pass. No FundedNext challenge replay is run if the strategy screen fails. If it passes, conduct a separate provider-rule-verified account-equity replay for the <180-calendar-day funded-completion objective; do not call an unverified proxy provider-equivalent.

## Required artifacts

Save runner, source data manifest, pre-outcome eligibility audit, primary trade ledger, cost/delay scorecard, annual summary, weekly-bootstrap input/result, JSON, report, and checkpoint/ledger. The backtest runs locally in Python; no GitHub Actions backtest.
