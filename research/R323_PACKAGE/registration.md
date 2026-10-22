# R323 registered experiment — frozen terminal sample-gate failure

**Registration status:** outcome-free hypothesis and implementation rules were committed before any PnL calculation. The latest pre-outcome amendment is commit `e999874fc2596dd1bef96f679e7a3b2e417953d0`.

## Hypothesis and fixed rules

Rank AUD/CAD/CHF/EUR/GBP/JPY/NZD using 5 active UTC weekday session log returns versus USD at the 10:00 UTC H1 bar. At 12:00 UTC, buy the strongest and short the weakest only if direction still continued after the one-hour delay. Native paired H1 BID/ASK, exact timestamp matching, no fill-forward, no weekend signals/lookbacks, no parameter grid. Risk is median prior 20 eligible active weekday 12:00–16:00 UTC midpoint ranges; stop 1R, target 1.5R, forced exit at 16:00 UTC, gap stops adverse-filled and ambiguous SL/TP resolved stop-first. Stress extra cost 0/0.5/1/2 pips per trade; primary +1 pip.

## Data and pre-outcome process

Fourteen native streams for seven pairs were fetched in data-only workflow run [39719343805](https://github.com/christianomomongan82-lang/scanner/actions/runs/39719343805), then committed on the research branch. Composite stream-manifest SHA-256: `2db7c7d88b2f31965ff956dd5e017ce7f0b76a4ac1792dca4896833b884e85e0`. Source audit status: PASS. Each BID and ASK stream has 78,361 rows; per pair, 78,361 exact BID/ASK timestamps and no unmatched rows. No timestamp duplicates, invalid OHLC, H1 misalignment or negative open/close spread. Each stream/pair has 36 gaps greater than one hour; total raw-stream gap ledger has 756 entries; gaps are retained, not interpolated. The earlier zero-gap output was invalid because datetime resolution had been misinterpreted; it was corrected before any PnL.

Weekend bars remain in raw files but are excluded from active-session calculations. Eligibility and the sample gate were run twice in separate clean Python processes; generated audit/eligibility/report files matched byte-for-byte. The V2 package validator and seven regression tests pass locally.

## Terminal decision

**Verdict: GAGAL — DATA/SAMPLE.** Discovery has 410 eligible legs across 205 active dates against a minimum of 1,000 legs / 500 dates. Confirmation has 270 eligible legs across 135 active dates against a minimum of 600 legs / 300 dates. Both frozen sample gates fail. Per registration, no PnL, PF, drawdown, annual profitability, or bootstrap was calculated. This is a sample/evidence failure, not evidence that the currency-strength hypothesis lacks alpha. The R323 registered test is closed; no changes to thresholds or lookbacks are permitted to rescue this run.
