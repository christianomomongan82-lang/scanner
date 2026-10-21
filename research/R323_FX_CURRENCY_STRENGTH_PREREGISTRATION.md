# R323 — USD-relative cross-sectional currency strength continuation

Status: **REGISTERED before strategy outcomes**. This is a distinct FX currency-factor screen, not a change to a prior threshold. No signals/PnL may be calculated until exact bid/ask data is acquired, hashed and passed through preflight.

## 1. Economic hypothesis and novelty

Foreign-exchange cross-sectional momentum means buying currencies that have strengthened relative to the USD and shorting those that have weakened. Menkhoff, Sarno, Schmeling and Schrimpf, “Currency momentum strategies,” *Journal of Financial Economics* 106(3), 2012, DOI https://doi.org/10.1016/j.jfineco.2012.06.009, report a historical winner–loser currency spread but specifically note that transaction costs and limits to arbitrage make it hard to exploit. A later study of currency momentum finds that cross-sectional return dispersion has information about momentum returns: https://doi.org/10.1016/j.jempfin.2019.07.002.

This test asks a deliberately narrow question: does 5-active-session relative currency strength predict a same-day four-hour directional move after a one-hour delay and conservative executable quote-side fills? It does **not** claim the multi-month academic effect transfers to an intraday horizon; this is exactly what the experiment must falsify or support.

Novelty relative to the project's closed families:
- R251 tested whether a common three-pair impulse predicts EURUSD lag catch-up; it did not rank and rotate a cross-section of currency factors.
- R252 tested a single FX return tail/direction relationship, not a winner-versus-loser portfolio across independently quoted currencies.
- R216 tested return ranks across US equity-index CFDs, not USD-relative strength among currency pairs. Its failure is an adverse prior and must be kept visible, not ignored.
- This is not a direction flip, threshold tweak or exit change to any closed family.

## 2. Frozen instruments and data

Instrument set, selected before outcome computation:
- EURUSD, GBPUSD, AUDUSD, NZDUSD (foreign currency is the base, USD the quote);
- USDCHF, USDCAD, USDJPY (USD is the base; invert the pair return to measure CHF/CAD/JPY strength against USD).

Data: Dukascopy H1 BID and ASK OHLC for every pair, UTC timestamps, 2017-01-01 inclusive through 2026-01-01 exclusive. Do not substitute BID-only peers. Acquisition workflow is strictly data-only; all feature, signal, trade, PnL and inference calculations must execute locally in Python. No synthetic rows, fill-forward prices, nearest-timestamp joins or look-ahead. Reject invalid OHLC; record duplicates and gaps before any selection; remove only data placeholders defined in the pre-outcome cleaning rule. The data manifest pins each of the 14 raw pair-side streams and their common timestamp integrity results.

Prices through 2025 have been inspected across many earlier FX experiments; the period split below is chronological but **not pristine project-level OOS**. A historical pass cannot by itself promote the strategy to funded-ready. The 2026 price window is excluded.

## 3. Signal construction

- Decision clock: UTC. For each UTC date, signal candle is the H1 bar whose open timestamp is 10:00 UTC. Its close is available at 11:00 UTC.
- For each of the seven pairs, use the midpoint close `(BID close + ASK close)/2` at 10:00 UTC. Calculate its 5-active-session log return versus the fifth preceding eligible 10:00-UTC signal observation. An eligible session is a date with valid 10:00 signal bars for all seven pairs; require exactly five prior eligible observations, no interpolation. Sign-invert USDCHF, USDCAD and USDJPY returns so positive means the named foreign currency strengthened against USD.
- Rank the seven foreign-currency-strength scores on that timestamp. For the top-ranked currency, plan a LONG foreign-currency exposure; for the bottom-ranked currency, plan a SHORT foreign-currency exposure. Ties break alphabetically by ISO currency code (AUD, CAD, CHF, EUR, GBP, JPY, NZD).
- Map direction to the real pair: for EURUSD/GBPUSD/AUDUSD/NZDUSD, long foreign strength = long pair; for USDCHF/USDCAD/USDJPY, long foreign strength = short pair. Reverse those directions for the weakest-ranked currency. Equal risk budget per leg; exactly two candidate legs per eligible signal date, no other ranks or parameter grids.
- A setup requires the chosen currency to be the top or bottom score among all seven. No extra dispersion, session or technical filter is allowed.

## 4. Delayed entry, risk and exit

- Entry: exact H1 open at 12:00 UTC, one full hour after the 10:00 signal bar closes at 11:00. Require exact synchronized BID/ASK entry bars for all seven pairs (rank calculation) and exact chosen-pair quote timestamps. Skip if any is absent; no nearest-bar fallback.
- Manual-delay continuation gate: at the chosen pair's 12:00 midpoint open, it must still lie in the expected rank direction relative to that pair's 10:00 signal-bar midpoint close. For an intended long foreign-currency exposure, midpoint at entry must be above its signal close for XUSD pairs and below for USDX pairs; reverse this for an intended short.
- Volatility-defined initial risk: for each pair and signal date, compute the range of the four-hour 12:00–16:00 UTC window on each of the previous 20 eligible sessions with exact complete H1 bars at 12, 13, 14 and 15 UTC. Risk distance is the median of those 20 session ranges, where each range is maximum BID/ASK midpoint high minus minimum BID/ASK midpoint low across the four bars. Require all 20 prior ranges; no current-day bars after entry enter the risk estimate.
- Long pair entry is ASK open; short pair entry is BID open. Stop is 1.0 risk-distance against the executable entry; target is 1.5 risk-distance in favor. Positions are held only during 12:00–16:00 UTC and are exited by the exact 16:00 UTC open if neither barrier triggers.
- For bars 12:00, 13:00, 14:00 and 15:00 UTC, test the executable exit side (BID for long, ASK for short). Check opening gaps first; stops gap-fill at the worse observed open, targets are capped at target. Intrabar ambiguity where both stop and target are touched resolves stop-first. A missing H1 bar anywhere in the required window invalidates that day's full two-leg basket before PnL is calculated.
- A pair can have at most one position at a time; previous-day exits at 16:00 precede a new day's 12:00 entries. No weekend holdings; a missing required bar skips the affected day's planned trade. All trades close by the 16:00 UTC open, outside the usual late-New-York FX rollover.

## 5. Execution-cost model and measures

- Side-correct historical BID/ASK execution prices already include the observed quoted spread.
- Extra round-trip slippage/commission stress applied independently per closed trade: 0, 0.5, 1.0 and 2.0 pair pips; primary = +1.0 pip. Pip is 0.0001 for non-JPY pairs and 0.01 for USDJPY. Cost converts to R by dividing price cost by that trade's fixed pre-entry risk distance.
- Report trade ledger, signal/currency ranks, skip reasons, exact entry/exit quotes, exit reason, risk distance, gross/net R at each cost, per-trade time, yearly/quarterly cohorts, 4-week block bootstrap of daily portfolio net R with zero-trade dates preserved, PF_R, mean/median R, max DD_R, losing streak, trades/day and portfolio leg exposure.
- No simultaneous cross-section can be entered if either selected leg lacks the exact entry/exit path; skip the whole basket date so the primary portfolio has consistent two-leg exposure.

## 6. Frozen periods and pass/fail gates

- Discovery: 2017-01-01 through 2020-12-31 UTC.
- Confirmation: 2021-01-01 through 2023-12-31 UTC.
- Diagnostic only: 2024-01-01 through 2025-12-31 UTC, contaminated and not eligible for candidate promotion.
- Minimum completed legs: 1,000 discovery and 600 confirmation. Minimum eligible trading dates: 500 discovery and 300 confirmation.
- At primary +1 pip extra cost: positive total net R and PF_R >= 1.05 in both discovery and confirmation.
- At +2 pip extra cost: positive total net R and PF_R >= 1.00 in both periods.
- At least 3 of 4 discovery years must be net-positive at +1 pip, and no year may contribute more than 70% of discovery net R.
- A 4-week circular bootstrap with fixed seed 323 and 10,000 resamples on confirmation daily portfolio net R must have 95% lower confidence bound > 0; all calendar days, including zero-trade dates, remain in the series.
- Any failed gate = **GAGAL**. Do not change lookback, rank count, clock, delay, risk distance, stop/target, asset list or periods after outcomes; no parameter search. A sample/data gate may stop before calculating PnL.
- If all signal gates pass, that still does not grant funded readiness. Historical project windows are contaminated and broker swaps/contract semantics/live execution are not yet fully verified; a separately frozen forward window and account-level challenge-path replay are required before any promotion.

## 7. Preregistered archive contract

Archive and read back: this preregistration; data-only acquisition code/workflow; raw bid/ask archive and its SHA-256; data audit; exact runner; calendar/session and eligibility audit; full chronological trade and skip ledger; annual/quarterly and cost scorecards; weekly/daily series; bootstrap; two clean run hashes; environment; machine JSON; final report; master ledger; family map; and PROJECT_STATE update. The local runner must complete two deterministic runs before claiming reproducibility.
