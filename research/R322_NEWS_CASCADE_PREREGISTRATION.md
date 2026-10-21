# R322 — USD high-impact news-cascade continuation (immutable preregistration)

Status: REGISTERED before event-outcome calculations.  
Research type: new economic-mechanism screen, not a funded-readiness claim.  
Primary input: EURUSD paired BID/ASK M1, Dukascopy source artifact 11959096102.  
Calendar input: Forex Factory historical calendar snapshot (community-maintained Hugging Face mirror), filtered to USD high-impact events.  
Calendar snapshot cutoff: 2025-04-07; events at/after 2025-04-08 are excluded. 2026 prices remain unopened.

## 1. Falsifiable mechanism

Prior FX microstructure research documents that macro-announcement responses can be amplified by stop-loss order flow and that exchange rates react rapidly to macroeconomic news. This study tests one narrow consequence: after a scheduled, high-impact US macro release produces an unusually large first five-minute EURUSD move, does the executable-side move continue after a further five-minute manual-entry delay?

This is not a claim that all scheduled news is directional. The trading signal uses only the first post-release price impulse, not actual-versus-forecast values, revised macro values, or a manually assigned bullish/bearish interpretation.

Sources motivating the hypothesis:
- “Exchange rate response to macronews: Through the lens of microstructure,” Journal of International Financial Markets, Institutions & Money (2011), DOI: https://doi.org/10.1016/j.intfin.2010.09.001
- “The high-frequency response of exchange rates and interest rates to macroeconomic announcements,” Journal of Monetary Economics (2007). The study documents rapid exchange-rate responses to macro surprises. Search record: https://www.sciencedirect.com/
- Historical event dataset card: https://huggingface.co/datasets/Ehsanrs2/Forex_Factory_Calendar (snapshot 2007-01-01–2025-04-07, approximately 83.4k events; DateTime carries a UTC offset; original display timezone Asia/Tehran).

## 2. Locked event set and event episode construction

Keep only calendar rows satisfying every rule:
1. Currency = USD.
2. Impact = High / High Impact Expected (or numeric 3 only if the export's impact column is encoded numerically).
3. Event timestamp is present, exact to the minute, timezone-aware, not All Day, Tentative, or otherwise unscheduled.
4. Event name matches this fixed case-insensitive macro-release allowlist:
   - Employment Situation / Non-Farm Employment Change / Non-Farm Payrolls / Unemployment Rate / Average Hourly Earnings / Employment Cost Index / JOLTS Job Openings;
   - Consumer Price Index / CPI / Core CPI / Producer Price Index / PPI / Core PPI;
   - PCE Price Index / Core PCE / Personal Income / Personal Spending;
   - Retail Sales / Core Retail Sales / Durable Goods Orders / Core Durable Goods;
   - Gross Domestic Product / GDP;
   - ISM Manufacturing PMI / ISM Services PMI / ISM Non-Manufacturing PMI;
   - Initial Jobless Claims / Unemployment Claims / Jobless Claims;
   - Federal Funds Rate / FOMC Statement / FOMC Press Conference.
5. Speeches, interviews, bond auctions, oil inventories, holidays, non-US events, and all calendar rows outside the allowlist are excluded. Actual, forecast, previous and revised values are never read by the strategy runner.

Parse timestamps from the original ISO-8601 offset into UTC; do not infer the timezone from the computer's locale. Keep one event episode per cluster: sort selected events by UTC timestamp; cluster events whose timestamp is no more than 40 minutes after the first event in that cluster; anchor the cluster at the earliest event. A trade attempt from an episode blocks other attempts until its planned exit; no overlapping positions. Record every excluded/merged event in the event eligibility audit.

## 3. Locked signal, entry, risk and exit

- Instrument: EURUSD only; quote-side BID/ASK, paired on exact UTC timestamps.
- M1 source uses the verified artifact with ZIP SHA-256 `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`. Remove only the joint repeated-flat placeholder pattern already defined in the R321 runner; preserve gaps and never fabricate bars.
- Aggregate M5 using only exact complete five-minute bars; do not forward-fill.
- Event time T must align to an exact M5 open. Pre-event midpoint is the close of the M5 bar starting at T−5 minutes. Signal candle is the M5 bar starting at T and ending at T+5.
- Compute the median of absolute midpoint close-to-close changes over the previous 60 consecutive, complete M5 bars ending at T. No data from the signal candle may enter this baseline.
- A signal exists only when the absolute midpoint change from pre-event close to signal-candle close is at least 1.5 times that trailing median. Direction is the sign of this first post-release five-minute midpoint change.
- Delay entry until the exact M5 open at T+10 minutes, i.e. five full minutes after the signal candle has closed. If that timestamp or the required path is absent, skip; do not select a nearby bar.
- At T+10, require the midpoint open still to be at or beyond the signal-candle close in the signal direction. Otherwise skip; this is the locked manual-delay continuation check.
- Long entry = ASK open at T+10; short entry = BID open at T+10.
- Initial stop = opposite executable-side extreme of the first post-release signal candle: long stop = signal-candle BID low; short stop = signal-candle ASK high. Skip if the resulting entry-to-stop distance is non-positive or non-finite.
- Take profit = 1.5 × initial risk from the executable entry price. Do not widen the stop or alter the target.
- Check stop/target on each observed M5 bar from entry through the six bars starting T+10, T+15, T+20, T+25, T+30, T+35. Stop takes precedence when both stop and target are touched intrabar. If a bar opens through the stop, fill at the adverse executable open; if it opens beyond target, cap the fill at target. If no barrier triggers, exit at the exact executable-side open at T+40 (30 minutes after entry). A missing required exit quote invalidates the trade path and is audited, not forward-filled.
- Long exit prices use BID; short exit prices use ASK. Observed spread is already in those prices. Subtract additional round-trip cost stresses of 0, 0.5, 1.0 and 2.0 pips/trade. Primary cost = +1.0 pip.
- One accepted entry per 40-minute event episode, no overlapping trade; process exits before any subsequent entry.

## 4. Frozen periods and contamination

- Discovery: event timestamp 2016-01-01 through 2018-12-31 UTC.
- Confirmation: 2019-01-01 through 2020-12-31 UTC.
- Diagnostic only: 2021-01-01 through 2025-04-07 UTC.
- The price history behind these periods has been repeatedly viewed in prior project research. Therefore none is a clean project-level holdout; 2019–2025 results must be explicitly labelled contaminated diagnostics, not independent OOS evidence. No 2026 PnL is calculated.
- If the calendar's timestamp audit, event eligibility audit, complete M5 alignment, or sample gate fails, stop before PnL and verdict the registered run GAGAL — DATA/PROCESS.

## 5. Hard gates, fixed before outcomes

A standard screen must meet every applicable gate at the primary +1 pip cost:
- At least 200 completed trades in discovery and 100 completed trades in confirmation.
- Positive net R and profit factor PF_R ≥ 1.05 in both discovery and confirmation.
- PF_R ≥ 1.00 and positive net R under the +2 pip incremental-cost stress in both periods.
- Positive annual net R in at least 2 of the 3 discovery years; no single year may contribute more than 70% of discovery net R.
- Four-week circular block bootstrap, fixed seed 322, on weekly net R with zero-trade weeks preserved; confirmation lower 95% bound for mean weekly net R must exceed zero.
- At least 100 diagnostic trades if later years are evaluated; report year-by-year cost sensitivity, trades/week, holding time, win rate, mean/median R, max DD_R and losing streak.
- Any failed gate = GAGAL. No tuning, sign flip, alternate threshold, clock shift, alternate hold period, or selective year rescue after looking at outcomes.
- A historical screen pass cannot yet be a funded-ready pass because the history is contaminated. An edge passing these gates would require a separately frozen future forward period and account-level challenge replay before promotion.

## 6. Required archive

Before any PnL calculation, commit and read back this preregistration and the calendar/data-preflight source. The data-only acquisition stage may run on GitHub Actions, but it must not calculate signals or PnL. The signal runner and all outcome calculations run in local Python only. Archive the source manifest, event calendar subset checksum, source-data hash, full event/skip audit, M5 audit, locked runner, full trade ledger, weekly and annual scorecards, cost sensitivity, bootstrap, environment, hashes, deterministic second-run comparison, final binary verdict, master ledger, family map and PROJECT_STATE update.


## Amendment A — scheduled-time repair for known midnight placeholders (registered before outcome computation; 2026-10-21 UTC)

### Why this amendment is necessary
A source-only inspection of the filtered calendar (no price outcomes, signals, or PnL calculated) found that many otherwise named high-impact releases are recorded with local source date and a clock time of exactly `00:00` in the source's Asia/Tehran timezone. Example: the 2016-01-08 rows for "Non-Farm Employment Change", "Unemployment Rate" and "Average Hourly Earnings m/m" are all timestamped `2016-01-08T00:00:00+03:30`, whereas the BLS official calendar places Employment Situation at 08:30 Eastern. Blind timezone conversion would incorrectly move these scheduled US releases to the preceding UTC date and wrong market session. This is a calendar-data defect; it is not market outcome evidence. No signal calculation or PnL has been run.

Official schedule cross-check references:
- BLS Schedule of Releases for Employment Situation and CPI lists releases at 08:30 ET: https://www.bls.gov/schedule/news_release/empsit.htm and https://www.bls.gov/schedule/news_release/cpi.htm
- BLS schedule pages identify JOLTS and Employment Cost Index at 10:00 ET and 08:30 ET respectively: https://www.bls.gov/schedule/2025/
- BEA publishes GDP and Personal Income and Outlays on the official schedule at 08:30 ET: https://www.bea.gov/news/schedule/
- U.S. Census lists the Advance Monthly Retail Trade Report release at 08:30 ET: https://www.census.gov/retail/release_schedule.html
- ISM says Manufacturing PMI and Services PMI release at 10:00 ET: https://www.ismworld.org/supply-management-news-and-reports/reports/ism-pmi-reports/
- The input data card describes the calendar source's timezone as Asia/Tehran and its historical snapshot ending 2025-04-07: https://huggingface.co/datasets/Ehsanrs2/Forex_Factory_Calendar

### Frozen event-name mapping and timestamp policy
1. The timestamp correction applies only to the fixed allowlist already registered in Section 2. "ADP Non-Farm Employment Change" is explicitly excluded: it is not the BLS Employment Situation release. FOMC Meeting Minutes, FOMC Economic Projections, Fed speeches/testimony, other central-bank speakers, and any non-allowlisted event remain excluded.
2. Preserve the original `DateTime` calendar date string's first ten characters as the source-local calendar date. Do not derive the event date by converting a midnight placeholder to UTC.
3. For an allowlisted event whose source-local clock is exactly `00:00:00`, substitute the fixed release time below on that same source-local calendar date, interpreted in `America/New_York`, then convert with IANA timezone/DST rules to UTC:
   - **08:30 ET:** Non-Farm Employment Change / non-farm payrolls, Unemployment Rate, Average Hourly Earnings, CPI / Core CPI, PPI / Core PPI, PCE / Core PCE Price Index, Personal Income / Personal Spending / Outlays, Retail Sales / Core Retail Sales, Durable Goods Orders / Core Durable Goods, GDP / Advance / Preliminary / Final GDP, Initial Jobless Claims / Unemployment Claims, Employment Cost Index.
   - **10:00 ET:** ISM Manufacturing PMI, ISM Services PMI / ISM Non-Manufacturing PMI, JOLTS Job Openings.
   - **14:00 ET:** Federal Funds Rate and FOMC Statement.
   - **14:30 ET:** FOMC Press Conference.
4. For allowlisted rows whose original source-local clock is not midnight, parse the original offset-aware timestamp and retain it only if its converted America/New_York time matches the event-name's fixed release time within ±15 minutes. This is a validation gate, not a shift; any mismatch is excluded and written to the timestamp audit with reason. The local date must remain the same as the source date after converting to Eastern Time; otherwise exclude and audit. Rows whose event name cannot be assigned unambiguously to the registered categories are excluded with a reason, never guessed.
5. Do not use or export actual, forecast, previous or revised values in the event selection/strategy. Excluded source dates/times and the correction reason must be preserved in the pre-outcome audit.
6. Cluster only after timestamps are corrected and validated. Sort in UTC; group events no more than 40 minutes from each cluster's earliest timestamp; use earliest timestamp as episode anchor. No event is duplicated across episodes.
7. Store, read back and verify the correction-map version, calendar source SHA-256, input subset hash, corrected output hash, all 2,828 source row decisions, and the exact event-level audit before any price outcome metrics are computed.

This amendment supersedes any conflicting implication in Sections 2 or 3 that raw source clock time is trusted unchanged when it is midnight. It does not change the registered signal direction, five-minute manual delay, stop/target geometry, cost grid, period split, gates, bootstrap seed or any strategy parameter. The calendar repair is based only on timestamp correctness and official release schedules. It must be committed before PnL, and any inability to produce enough correctly scheduled events leads to **GAGAL — DATA/SAMPLE**, with no outcome rescue.
