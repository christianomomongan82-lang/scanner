# R213 — Bearish H4 Expansion Continuation

**Final verdict: REJECT.**  
Workflow run: https://github.com/christianomomongan82-lang/scanner/actions/runs/38491536437  
Audit artifact: https://github.com/christianomomongan82-lang/scanner/actions/runs/38491536437/artifacts/11861259317

## Locked hypothesis

Short-only continuation after a completed bearish UTC H4 candle whose range is at least 1.5x the median range of the previous 20 completed H4 candles and whose close lies in the bottom 25% of its own range. Entry is the first non-flat M5 BID open at least five minutes after the H4 signal close and before the next H4 close. Stop is the signal H4 high; target is 2R. One active position per instrument.

H4 bins require four consecutive H1 BID bars aligned to 00/04/08/12/16/20 UTC; incomplete bins are excluded. M5 exits check stop before target, fill a stop gap at the bar open, and skip flat synthetic bars. No standard indicators or parameter grid.

## Validation and assumptions

- Ten Dukascopy BID H1/M5 index datasets were validated and tested.
- The workflow's Python compilation and UTC H4 boundary/missing-bar test passed.
- The causal prefix/truncation gate passed for each completed H4 decision on all ten instruments.
- Discovery: entries 2017–2021. Forward: 2022–2025. OOS: 2026 through the common cutoff 2026-10-09 20:00 UTC.
- 1 bp and 2 bps are modeled round-trip price costs, not verified broker spread, commission or live slippage.

## Full instrument ledger

| Instrument | Discovery closes | Discovery PF @ 1 bp | Discovery PF @ 2 bp | Forward closes | Forward PF @ 1 bp | Forward PF @ 2 bp | Worst forward cohort PF @ 1 bp | OOS closes | OOS PF @ 1 bp | OOS PF @ 2 bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| USA 500 / S&P 500 | 311 | 0.7338 | 0.7094 | 252 | 0.9710 | 0.9472 | 0.6855 | 47 | 1.1014 | 1.0706 |
| USA 30 / Dow Jones | 301 | 0.7986 | 0.7750 | 237 | 0.8001 | 0.7797 | 0.4648 | 43 | 1.3948 | 1.3623 |
| FTSE 100 | 298 | 0.9460 | 0.9192 | 257 | 0.8378 | 0.8135 | 0.7560 | 52 | 1.2129 | 1.1826 |
| USA 100 Tech / Nasdaq 100 | 283 | 0.6890 | 0.6736 | 237 | 1.0320 | 1.0142 | 0.7820 | 37 | 1.1577 | 1.1376 |
| Japan 200+ | 279 | 0.9283 | 0.9073 | 250 | 0.9160 | 0.8988 | 0.5693 | 49 | 0.9566 | 0.9438 |
| Germany 40 / DAX | 277 | 1.0662 | 1.0406 | 225 | 1.0329 | 1.0088 | 0.8213 | 44 | 1.2294 | 1.2055 |
| Australia 200 | 272 | 0.7718 | 0.7496 | 233 | 0.9548 | 0.9297 | 0.8094 | 46 | 1.7754 | 1.7232 |
| France 40 / CAC 40 | 236 | 1.0682 | 1.0391 | 175 | 1.0087 | 0.9759 | 0.6593 | 42 | 1.0429 | 0.9131 |
| EU Stocks 50 | 208 | 1.0502 | 1.0224 | 193 | 0.8640 | 0.7794 | 0.7328 | 34 | 1.2021 | 1.1761 |
| US Small Cap 2000 | 185 | 1.0036 | 0.9876 | 251 | 0.9177 | 0.9027 | 0.6723 | 40 | 1.1741 | 1.1547 |

## Locked selection and verdict

Discovery eligibility required at least 30 closed trades and PF >= 1.00 at 2 bps. Selection favored the highest discovery trade count, with discovery PF@2bp as the tie-break. This selected **Germany 40 / DAX**: 277 discovery closes, PF 1.0406 at 2 bps.

| Selected DAX metric | Result |
|---|---:|
| Forward closed trades | 225 |
| Forward PF @ 1 bp | 1.0329 |
| Forward PF @ 2 bps | 1.0088 |
| Worst 2022–2025 entry-year cohort PF @ 1 bp | 0.8213 (2023, 64 closes) |
| OOS closed trades | 44 |
| OOS PF @ 1 bp | 1.2294 |
| OOS PF @ 2 bps | 1.2055 |

The candidate fails the locked forward gates: at least 30 trades, PF >= 1.15 at both cost levels, and worst eligible forward-year cohort PF >= 1.00. OOS 2026 is positive but does not override the failed 2022–2025 forward test.

**Conclusion: reject R213 as tested.** These BID-only simulations do not establish funded/live readiness; broker-specific commission, executable spread and live slippage remain unverified.
