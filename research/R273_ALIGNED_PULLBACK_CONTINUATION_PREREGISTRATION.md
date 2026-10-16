# R273 Pre-registration — XAUUSD M5 aligned pullback continuation

**Pre-registration status: LOCKED before any R273 signal/PnL calculation.** Date: 2026-10-16.

## Parent lineage and reason for the child

- **Parent R272-A/raw continuation trigger:** retain its six-bar pullback/reclaim pattern, 12-hour net displacement condition, swing stop and 1.5R fixed target as-is; do not alter thresholds.
- **Parent R272 execution controls:** inherit BID/ASK executable-side entries/exits, entry at T+10 minutes (signal bar close + five-minute manual delay), no synthetic-bar filling, exact gap checks and same-session cutoff handling.
- **Mutation M1:** remove the incompatible ER >= 0.45 router gate and instead require the 6-hour close-to-close move to have the same sign as the existing 12-hour net move. No magnitude threshold, parameter sweep, or secondary filter is added.
- **Discarded block:** do not include R272-B failed-excursion fade in this child because it lost on discovery and validation even at zero extra cost.
- R272's full history has already been viewed, so R273 is an explicitly history-informed exploratory generation; the 2021–2025 segment is not pristine at the program level. The reserved XAUUSD 2026 segment remains unopened unless this candidate first passes all locked historical gates.

## Data and causal definitions

- Source: corrected GitHub raw-only artifact `12031270051`, Dukascopy XAUUSD M5 BID/ASK, 2016-01-01 inclusive to 2026-10-16 exclusive UTC. Artifact provenance, row counts, hashes, and disabled synthetic flats must pass the R272 loader's manifest checks. Preserve gaps; never synthesize bars.
- Discovery: 2016–2020. Historical validation: 2021–2025 (exploratory, research-contaminated). Reserved candidate-specific diagnostic: 2026-01-01 through 2026-10-15; it must not be read unless all historical gates pass.
- M5 timestamp denotes bar open. Trigger evaluates after signal candle close. Entry is at index t+2 / T+10 minutes, five minutes after signal close; both interim five-minute intervals must be present exactly. Otherwise skip.
- For each signal bar t, define `A` as the median BID high-low range of the prior 144 completed M5 bars; `M12 = BID_close[t-1] - BID_close[t-145]`; `M6 = BID_close[t-1] - BID_close[t-73]`. Features must be causal; current signal bar is excluded from M12/M6/A context.

## Signal and execution — one locked child

1. Reuse R272's raw Module A trigger exactly: `abs(M12) >= 4*A`; if M12 is positive, long pullback depth is `max(BID_high[t-6:t-1]) - min(BID_low[t-5:t])` and current BID close must exceed prior bar BID high; if M12 is negative, short pullback depth uses ASK highs/lows as in the stored R272 runner and current BID close must be below prior bar BID low. Pullback depth must be between 0.25A and 1.00A.
2. **Child R273 aligned trigger:** the raw Module A setup is eligible only if `M6*M12 > 0`. This is the sole signal mutation versus the raw Module A ablation.
3. Entry at exact delayed executable open: ASK for long, BID for short. Stop = low extreme of signal bar and five preceding bars for long; high extreme of those six completed bars on ASK for short, matching the R272 setup. Reject risk distance outside 0.50A–2.00A. Fixed target = 1.50R.
4. Only weekdays; trigger bar opens between 06:00 and 15:50 America/New_York. Maximum one accepted trade per NY session day and one position at a time. No overnight position; force flat at the last executable quote at or before 16:45 NY. Use the exact 16:45 opening quote without reading that candle's later high/low.
5. Monitoring uses BID OHLC for long positions and ASK OHLC for short positions. Stop first if SL and TP are both touched within one candle. Stop gaps fill at the worse opening quote; targets fill at target price. Reject delayed entries if the executable quote has already crossed stop or target.
6. Additional round-trip cost beyond observed BID/ASK: $0.00, $0.10, $0.30 (primary), $0.50 per ounce. No trailing, news filter, position scaling, leverage/risk optimization, or stop/target sweep.

## Required comparisons and precommitted gates

Calculate the raw Module A ablation and aligned child on the identical quote stream, executable sides, cost sensitivities and execution timing. Report trade count, net R, PF, expectancy, win rate, year/month results, exit mix, rejected fills, four-week circular bootstrap of weekly net R (10,000 replicates, seed 2732026), and data checks. Do not run the R272-B fade.

Historical screen uses +$0.30/oz primary cost. Every gate must pass before opening 2026:

- Discovery child has at least 50 closed trades and positive net R.
- Discovery four-week block-bootstrap lower 95% bound for mean weekly net R is above zero.
- Validation child has at least 100 closed trades and positive net R; this is exploratory evidence, not clean program-level OOS.
- Validation child remains net positive at +$0.50/oz.
- On validation, the child has higher net R than the raw-A ablation and retains at least 40% of raw-A trade count; otherwise the alignment mutation adds no demonstrated value.
- The raw-A ablation is never a candidate for promotion unless it independently passes its own discovery/validation-positive and bootstrap gates; it is a comparison, not a way to select after the fact.

If any child historical gate fails, **R273 = GAGAL**; do not inspect the reserved 2026 slice, do not adjust the alignment rule, and do not rescue it by changing the A setup/SL/TP. If all historical gates pass, a separate locked run may open 2026 once; it still cannot be called funded-ready without account-rule-aware challenge replay and verified actual costs.

## Reproducibility

Existing runner and smoke tests from R272 are the reference for data loading, quote-side fills and cutoff handling. R273-specific code, result summary, binary verdict and compact trade ledger will be stored separately from R272 so the parent remains immutable. Calculations must run locally; GitHub Actions may only collect raw data, never signals or PnL.