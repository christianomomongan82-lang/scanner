# R215 — Two-Sided H4 Compression Channel Breakout

**Final verdict: REJECT.**  
Workflow run: https://github.com/christianomomongan82-lang/scanner/actions/runs/38492402821  
Audit artifact: https://github.com/christianomomongan82-lang/scanner/actions/runs/38492402821/artifacts/11862880022

## Locked hypothesis

After the median range of the previous 5 completed UTC H4 bars contracts to <=0.6x the median range of the previous 20 bars, trade a completed H4 close above the previous 20-bar high (long) or below the previous 20-bar low (short). Stop is the 10-bar low for longs or 10-bar high for shorts; target is 2R. Entry is the first non-flat M5 BID open >=5 minutes after signal close and before the next H4 close. One active position per instrument.

All ten cached Dukascopy BID H1/M5 index snapshots were validated. Python compilation, UTC H4 boundary/missing-bar checks and causal prefix/truncation checks passed. Costs are modeled at 1 and 2 price bps round-trip, not verified broker-specific costs. Discovery entries: 2017–2021; forward: 2022–2025; OOS: 2026 to common cutoff 2026-10-09 20:00 UTC.

## Full instrument ledger

| Instrument | Discovery closes | Discovery PF @ 1 bp | Discovery PF @ 2 bp | Forward closes | Forward PF @ 1 bp | Forward PF @ 2 bp | Worst forward cohort PF @ 1 bp | OOS closes | OOS PF @ 1 bp | OOS PF @ 2 bp |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| EU Stocks 50 | 30 | 1.2914 | 1.2778 | 17 | 0.8238 | 0.8145 | 0.8461 | 4 | 0.6585 | 0.6504 |
| France 40 / CAC 40 | 26 | 1.2191 | 1.2067 | 19 | 0.7045 | 0.6966 | 0.4936 | 3 | 3.3732 | 3.3491 |
| USA 100 Tech / Nasdaq 100 | 24 | 3.2976 | 3.2625 | 18 | 0.2471 | 0.2442 | 0.0000 | 3 | 0.9939 | 0.9878 |
| FTSE 100 | 15 | 2.2556 | 2.2260 | 6 | 0.0000 | 0.0000 | — | 1 | INF* | INF* |
| USA 30 / Dow Jones | 12 | 0.9847 | 0.9696 | 13 | 1.2374 | 1.2250 | — | 2 | 1.9822 | 1.9647 |
| USA 500 / S&P 500 | 12 | 0.6565 | 0.6476 | 16 | 1.9738 | 1.9480 | 1.3050 | 5 | 1.3214 | 1.3096 |
| US Small Cap 2000 | 10 | 1.9868 | 1.9737 | 9 | 3.9806 | 3.9612 | — | 3 | 0.9951 | 0.9903 |
| Germany 40 / DAX | 8 | 1.1876 | 1.1753 | 11 | 1.1323 | 1.1219 | — | 2 | INF* | INF* |
| Japan 200+ | 7 | 0.3232 | 0.3136 | 8 | 0.6610 | 0.6554 | — | 1 | INF* | INF* |
| Australia 200 | 5 | 0.0000 | 0.0000 | 4 | 0.6612 | 0.6559 | — | 2 | 0.0000 | 0.0000 |

*INF means the sample contained gains but no losses, so PF is mathematically infinite; these tiny samples are not evidence of a robust edge.*

## Locked selection and verdict

Discovery eligibility required at least 30 closed trades and PF >=1.00 at 2 bps. The discovery-only frequency rule selected **EU Stocks 50**, with 30 discovery closes and PF 1.2778 at 2 bps.

| Selected EU Stocks 50 metric | Result |
|---|---:|
| Forward closed trades | 17 |
| Forward PF @ 1 bp | 0.8238 |
| Forward PF @ 2 bps | 0.8145 |
| Worst 2022–2025 entry-year cohort PF @ 1 bp | 0.8461 |
| OOS closed trades | 4 |
| OOS PF @ 2 bps | 0.6504 |

The candidate fails the locked forward gates: it has fewer than 30 forward closes, PF below 1.15 at both cost levels, and worst forward-year cohort PF below 1.00. OOS is also weak and too small to rescue the result.

**Conclusion: reject R215 as tested.** It is not funded/live-ready. Broker-specific commission, executable spread and live slippage remain unverified.
