# R283 Preregistration — US Index Cash-Open Gap Fade

**Status:** Locked before return/PF calculations. Test executed locally; no GitHub Actions workflow.

## Hypothesis
When a US index opens the regular cash session unusually far from the previous regular-session close, the gap is more likely to fade toward that close. This is distinct from R276–R280 cash-open breakout/breadth families.

## Universe and input
USA500 (`r205-usa500.zip`), USATECH (`usatech.zip`), USA30 (`usa30.zip`), USSC2000 (`ussc2000.zip`). Cached M5 BID-only OHLC; timestamps treated as bar-open timestamps; Small Cap archive starts Aug 2018. Session clock: America/New_York with DST.

## Frozen rules
1. Previous RTH close = 15:55–16:00 ET bar close; current cash open = 09:30–09:35 bar open.
2. Gap % = abs(open_0930 - prior_close) / abs(prior_close) × 100.
3. Per instrument, fit Q80 absolute gap % using only 2017–2020.
4. Trade only gaps at or above Q80.
5. Skip if prior close target was touched during 09:30 or 09:35 bar, or if target is no longer profitable at 09:40.
6. Entry at 09:40 ET, fading gap: short gap-up, long gap-down.
7. Target = prior close; stop distance = 0.75 × original gap.
8. Process opening gaps first; stop-first on same-bar stop/target; adverse gap through stop fills at open; target fills at target; otherwise exit at 15:55 bar close. No overnight.
9. Require exact 5-minute timestamps 09:40–15:55; never synthesize missing bars.
10. One event per instrument/session. Portfolio sizing/cross-asset exposure not modeled.
11. Model 1/2/4 bps round-trip costs; primary gates use 2 bps. These are not observed spreads.

## Gates
- Discovery 2017–2020: >=100 combined trades, PF >=1.05 and positive net R at +2 bps.
- Validation 2021: >=40 trades, PF >=1.00 and positive net R at +2 bps.
- Only if both pass, score exploratory 2022–2025 (>=100 trades, PF >=1.10, >=3/4 eligible positive years, and positive lower 95% four-week block-bootstrap bound).
- 2026 remains unopened.
- A screen pass cannot establish funded readiness without verified execution costs and account-path replay.

## Stop conditions
If discovery or validation fails, do not calculate/inspect 2022–2025 outcomes. Do not retune threshold, stop, delay, target or session times after results. Failure closes this exact specification.
