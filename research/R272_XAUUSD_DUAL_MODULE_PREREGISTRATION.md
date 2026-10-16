# R272 Pre-registration — XAUUSD 12-hour trend-pullback / balanced-sweep router

**Pre-registration commit date:** 2026-10-16  
**Status:** LOCKED BEFORE INSPECTING XAUUSD M5 RESULTS  
**Purpose:** test whether routing between two economically different price paths—pullback continuation in a persistent 12-hour move versus failed-range excursion in a balanced market—creates a useful integrated opportunity stream compatible with a five-minute phone execution delay. This is not a retune of R270 or R271.

## 1. Data and provenance
- Source: Dukascopy through `dukascopy-node`; XAUUSD M5 BID and ASK.
- Intended requested window: 2016-01-01 inclusive to 2026-10-16 exclusive UTC. Raw data collection only uses the branch/workflow `data/r272-xauusd-m5-2016-2026`; it may not compute features, signals, PnL, backtests or verdicts in GitHub Actions.
- Local computation only. Preserve quote sides and real timestamps. Never synthesize missing M5 bars. Match BID and ASK by exact timestamp.
- Discovery: signal days from 2016–2020.
- Historical validation: 2021–2025; considered exploratory with respect to the wider research program, not the final untouched holdout.
- Locked independent instrument-period diagnostic: 2026-01-01 through 2026-10-15. **Do not open this segment until all preregistered discovery/validation gates pass.**
- Timestamp in Dukascopy files is treated as bar open time. Convert it to America/New_York for session definitions and daylight-saving time. A candidate must also pass later account-specific cost and server-time verification.

## 2. Causal shared features
Use M5 bars only. At current signal bar index (t), signal is evaluated once bar (t) has closed. The shared context uses only the **144 completed bars before (t)**:
- (A_t): median of ((high-low)) over those 144 prior bars, in USD/oz.
- Net move (M_t = close_{t-1}-close_{t-145}).
- Path length (L_t = sum_{j=t-144}^{t-1}|close_j-close_{j-1}|).
- Efficiency ratio (ER_t=|M_t|/L_t), if (L_t>0).
- Prior 12-hour high, low and midpoint are computed from bars (t-144) through (t-1), excluding the current bar.
- Require all 144 bars present on the expected M5 grid, (A_t>0), and no missing price data inside that context. Missing bars are not filled.
- Entry signals are allowed only when the signal bar opens between 06:00 and 15:50 America/New_York on a weekday. Entry is at the next exact M5 bar open, giving five minutes from signal-bar close. One closed/open trade at a time and at most one trade per New York session day.

## 3. Module A — persistent-trend pullback continuation
Activate this module only when (ER_t ge 0.45) and (|M_t|ge4A_t). Direction is LONG if (M_t>0) and SHORT if (M_t<0).

Use the six completed bars ending at current signal bar (t):
- LONG: the maximum high of bars (t-6) through (t-1) minus the minimum low of bars (t-5) through (t) must be between (0.25A_t) and (1.00A_t); additionally (close_t>high_{t-1}).
- SHORT: the maximum high of bars (t-5) through (t) minus the minimum low of bars (t-6) through (t-1) must be between (0.25A_t) and (1.00A_t); additionally (close_t<low_{t-1}).
- Entry is the next M5 open at executable ASK for LONG / BID for SHORT.
- LONG initial stop is the minimum low of bars (t-5) through (t). SHORT initial stop is the maximum high of bars (t-5) through (t).
- Reject invalid entries or stop distance outside (0.50A_t) to (2.00A_t).
- Target is fixed at 1.50R from entry. Stop/target conditions are monitored on BID OHLC for longs and ASK OHLC for shorts.

## 4. Module B — balanced-regime failed-excursion reversal
Activate only when (ER_t le 0.20); the middle zone (0.20<ER_t<0.45) has no trade.

- SHORT: current bar high reaches at least (priorHigh+0.25A_t), and current close is back below priorHigh.
- LONG: current bar low reaches at least (priorLow-0.25A_t), and current close is back above priorLow.
- If one signal bar breaches both sides of the prior range, skip it as ambiguous.
- Entry is the next M5 open at executable ASK for LONG / BID for SHORT.
- LONG stop is current bar low minus (0.10A_t). SHORT stop is current bar high plus (0.10A_t).
- Target is the prior 12-hour range midpoint. Require reward/risk at entry to be at least 1.00; otherwise skip.
- Use the same correct executable sides for exit monitoring.

## 5. Shared route, fill, cost and exit policy
- The ER regime makes A and B mutually exclusive on a given bar. A signal can produce at most one trade per New York session day; no pyramiding or overlapping trades.
- If the next-bar entry opens at/beyond stop or target, skip the trade; do not award a favorable fill.
- For each M5 bar after entry, stop has priority if stop and target are both touched in the same bar. If the open gaps through a stop, fill at the worse opening executable quote; targets fill at target price when touched.
- Force flat at the last valid M5 executable quote at or before 16:45 New York time on the same New York calendar date. This is designed to avoid overnight exposure; it is not proof of zero swap until the actual account's server rollover and contract specifications are checked.
- Report price-side fills plus added round-trip cost sensitivities of $0.00, $0.10, $0.30 and $0.50 per ounce. Primary screening cost is +$0.30/oz beyond observed BID/ASK. Do not represent this as a verified FundedNext commission schedule; account-specific commission and fees remain a separate readiness gate.
- No trailing stop, news filter, position scaling, stop/target optimization or parameter sweep.

## 6. Required comparison
Report Module A alone under its router gate, Module B alone under its router gate, the routed stream A/B and a raw-union baseline that allows either module's raw trigger in any ER regime (predeclared conflict resolution: Module A takes priority if both trigger on the same bar). All comparisons use identical timestamps, executable sides, costs and entry delays. Report:
- trade count, net R, PF (diagnostic), mean/median R, win rate and holding time;
- yearly and monthly results, long/short contribution, stop/target/time-exit mix, trade overlap/skips;
- 4-week circular block bootstrap of weekly net R, 10,000 resamples with seed 2722026;
- cost sensitivity across all four levels;
- realistic challenge-path metrics only after the underlying signal-stream gates pass.

## 7. Historical screen and holdout opening gates
At the primary +$0.30/oz additional-cost assumption, all of the following must pass before inspecting 2026 output:
1. Discovery 2016–2020 routed stream has at least 100 closed trades and positive net R.
2. Validation 2021–2025 routed stream has at least 200 closed trades and positive net R.
3. Each module has at least 50 trades and positive net R in both discovery and validation; a losing module is not kept merely to inflate trade count.
4. The routed stream improves the preregistered target-completion diagnostic against both standalone modules, without higher loss-limit breach probability under identical risk and latency.
5. The +$0.50/oz sensitivity remains net positive in the validation segment.
If any gate fails, **R272 = GAGAL**, do not inspect 2026, and do not alter thresholds.

## 8. Independent XAUUSD 2026 screen
Only after every historical gate passes, unlock 2026-01-01 through 2026-10-15 once. R272 can only pass this screen if:
- at least 50 closed trades overall, with each module represented by at least 20 trades;
- +$0.30/oz net R positive and +$0.50/oz remains net positive;
- the lower 95% bound of four-week block-bootstrap mean weekly net R is above zero;
- at least 60% of completed calendar months have positive net R, and no single month contributes over 40% of total positive profit;
- both modules remain non-negative in combined OOS contribution and there is no unmodelled overlap or look-ahead.

If a historical or locked 2026 gate fails, the candidate is **GAGAL** and must not be retuned on those periods.

## 9. Funded-ready is a separate promotion decision
Even a successful signal-stream screen is not funded-ready automatically. To claim funded-ready, the project must also pass `FUNDED_READINESS_GATE_20261016.md` with an equity-aware, two-phase Challenge replay including current official DLL/MLL, server-time reset, commission/swap/fees, intratrade floating P&L, Quick Strike, minimum trading days, realistic slippage, and two-phase completion odds. Any missing mandatory implementation evidence means **GAGAL for funded readiness**.
