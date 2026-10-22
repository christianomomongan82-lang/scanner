# R329 — Seven-pair FX time-series momentum portfolio
**Status: LOCKED PREREGISTRATION — no signal PnL authorized before candidate-specific V2 preflight passes.**  
Registered UTC: 2026-10-22/23  
Parent/lineage: new portfolio mechanism; not a rescue of R258 or R323.

## 1. Falsifiable hypothesis and novelty

**Hypothesis:** A portfolio that independently follows each pair's own medium-horizon return direction, with inverse-volatility risk weights and a hard cap on aggregate USD-factor exposure, can produce positive executable risk-normalized returns at a weekly rebalance cadence after spread, commission, adverse slippage, and swap-cost stress.

Economic motivation: time-series momentum is a distinct portfolio-level hypothesis. Moskowitz, Ooi & Pedersen (2012), DOI https://doi.org/10.1016/j.jfineco.2011.11.003, document 1–12 month time-series momentum in liquid futures. That paper motivates the test; it does not show the same edge exists in these OTC FX CFDs.

This differs from:
- R258: one EURUSD pair, 24h/120h direction alignment.
- R323: cross-sectional rank of seven currencies using five eligible sessions, trading the strongest and weakest pair.
- Earlier candle/session/range rules: no candle geometry, event trigger, session breakout, reversal or cross-sectional rank is used here.

The tested hypothesis is the **multi-week per-instrument time-series return direction within a risk-normalized, USD-exposure-capped portfolio**. No parameters may be changed after any outcomes are inspected. If the novelty review identifies meaningful overlap that is not resolved by this description and the actual frozen code, stop before outcomes.

## 2. Universe and pinned data

Seven native paired BID/ASK H1 FX pairs:
EURUSD, GBPUSD, AUDUSD, NZDUSD, USDCHF, USDCAD, USDJPY.

Source: Dukascopy H1 BID/ASK, UTC, 2017-01-01 inclusive through 2026-01-01 exclusive. Archive/acquisition provenance is GitHub data-only workflow run 39719343805, artifact 12400822266. Composite ordered stream manifest SHA-256: `2db7c7d88b2f31965ff956dd5e017ce7f0b76a4ac1792dca4896833b884e85e0`. All fourteen constituent hashes and byte counts are enumerated in `data_manifest.json`. Input rows remain as downloaded; do not delete flat/static rows silently, forward-fill gaps, synthesize candles, pair by row number or join approximate timestamps. Exact BID/ASK pairing and all-seven-pair timestamp consistency are required for a portfolio rebalance.

Price data from 2017–2025 has been examined by earlier project studies. It is development/diagnostic evidence, **not a pristine project-level OOS set**. All 2026 data are excluded. The reserved XAUUSD 2026 data must remain unopened.

## 3. Locked grid and signal clock

Exactly three candidate configurations; no other grid dimensions:
- lookback = 13 eligible weekly observations;
- lookback = 26 eligible weekly observations;
- lookback = 39 eligible weekly observations.

Each eligible scheduled observation is a Tuesday 10:00 UTC H1 bar whose close is known at 11:00 UTC. All seven pairs must have exact, valid, active BID/ASK bars at the signal time. For candidate horizon H, each pair's signal is the sign of log(mid-close at current signal / mid-close H prior eligible weekly observations earlier). Exact zeros produce no position. H is counted on the common, active weekly observation calendar; no interpolation is permitted. The same direction is applied until the scheduled next rebalance; this is time-series momentum, not top/bottom ranking across pairs.

Baseline entry proxy: use the exact active H1 open at Tuesday 12:00 UTC. This is the first hourly bar open at least five minutes after the signal close and is a conservative one-hour timestamp-resolution proxy, **not an exact T+5-minute quote**. The current data source is H1 and cannot determine the actual quote at T+5. A promotion-grade claim for actual phone execution needs five-minute or finer quote evidence or a separately validated fill calibration. Do not pretend H1 OHLC proves an exact five-minute fill.

Rebalance/exit: close the prior weekly positions at the exact Tuesday 12:00 UTC executable open and open the new target positions on that same timestamp. One holding period is exactly 168 hours if the next scheduled bar exists; no lookahead and no next-bar interpolation. Only timestamps with complete active quotes for all required pairs, exact signal history, exact entry and exact scheduled next-week exit qualify. Gaps remain missing. Weekend and overnight exposure is allowed in the research model and must receive a swap-cost treatment.

## 4. Portfolio weights and correlation constraint

For each pair at the signal close:
1. Calculate the standard deviation of the last 13 one-week log returns, including only completed eligible weekly observations up to the signal close. Require 13 returns and a strictly positive finite standard deviation.
2. Raw signed risk weight = sign(H-week return) / 13-week volatility. Normalize absolute weights to gross risk weight 1 before caps.
3. Hard single-pair cap: clip any absolute pair weight at 0.25 of the normalized pre-cap gross budget; do not redistribute the clipped amount.
4. USD-factor loading for a signed pair position is -1 for EURUSD/GBPUSD/AUDUSD/NZDUSD and +1 for USDCHF/USDCAD/USDJPY. If absolute net USD exposure exceeds 30% of remaining gross exposure, scale only the majority USD-exposure side down to the exact 30% bound. If the opposing side is zero, that scheduled portfolio is flat; do not create the opposite trade.
5. Weights are risk fractions, not fixed-lot equal weights. The single weekly portfolio's total pre-cap 1R means a one-standard-deviation adverse move across all allocated pair positions costs at most 1R by construction; any unused weight remains cash. Do not increase risk to rescue weak economics.

## 5. Cost contract and known limits

Executable-side prices: buys enter ASK and exit BID; sells enter BID and exit ASK. These observed quote sides account for observed spread; do not subtract the spread a second time.

FundedNext's currently published Stellar 1-Step/2-Step rules list Forex commission as $5 per side; public rule: https://fundednext.com/general-rules/cfds/symbols-and-conditions. Preliminary R accounting assumes the standard 100,000-unit FX lot convention and calculates pair-specific USD pip value from observed quotes. Exact challenge-platform contract size and commission implementation must be verified before any funded-ready statement.

Because exact per-symbol live swap point values cannot be confirmed from the available raw archive, the discovery screen will use an explicit **adverse swap-cost proxy**, not a claim about actual FundedNext swaps: 2 pip-equivalents per 7-calendar-day holding period per active leg as the primary stress and 4 pip-equivalents as the higher-cost stress. Actual symbol-specific swaps/rollover must be sourced from the platform before any challenge replay or funded-ready claim. This conservative proxy does not credit potentially positive carry.

Extra adverse slippage grid, round trip per active leg: 0 / 0.5 / 1 / 2 pips; primary +1 pip. All outcomes, if authorized after preflight, include observed BID/ASK execution, $10 per standard-lot round trip commission converted to R using the pair's USD pip value at entry, and the registered adverse swap proxy. Cost units and conversions must be logged by pair. Report both +1 pip plus 2-pip/week swap primary and +2 pips plus 4-pip/week swap stress.

## 6. Partitions, sample, selection and statistical gates

- Discovery: 2017-01-01 through 2020-12-31.
- Confirmation: 2021-01-01 through 2023-12-31.
- Diagnostic only: 2024-01-01 through 2025-12-31.
- Excluded/protected: 2026-01-01 onward.

Before any outcome computation, require:
- data integrity PASS across all 14 streams;
- at least 200 completed-leg-eligible opportunities and 100 eligible weekly rebalance dates in discovery, and at least 100 eligible-leg opportunities and 70 weekly dates in confirmation, for every candidate; count actual active legs separately from flat/skip dates;
- complete 13/26/39-week feature history and exact entry/exit timestamps; no future price outcomes inspected;
- exact runner, config, environment, preregistration and output schema all read back from GitHub; candidate-specific V2 preflight must PASS.

Outcome gates if preflight passes:
- Primary net R > 0 and PF_R >= 1.05 for the discovery-selected horizon in both discovery and confirmation under observed BID/ASK + $5/side commission + +1 pip adverse slippage + 2 pip-equivalent swap per 7-day holding period.
- At higher stress (+2 pips and 4 pip-equivalent swap/week), net R > 0 and PF_R >= 1.00 in both periods.
- For complete discovery years 2018–2020, at least 2 of 3 positive; no one full year accounts for more than 70% of positive total discovery net R. 2017 is reported as a partial warm-up year, not counted as a full annual gate.
- Use weekly block bootstrap with zero-trade weeks preserved, 10,000 replicates, four-week blocks, frozen seed 329. The 95% lower confidence bound of mean weekly net R must exceed zero on discovery and confirmation. Apply Holm adjustment across the three prespecified discovery candidates.
- Keep full grid and scorecard for all three horizons. Choose at most one horizon using the preregistered rule: highest discovery mean weekly net R at primary cost; tie-break by higher adjusted bootstrap lower bound, then lower portfolio maximum drawdown. Confirmation may evaluate that frozen selection but must not select an alternative.
- If the data/sample gate fails, stop without calculating PnL. A sample failure is not evidence against the economics.

The periods are project-contaminated; no positive historical result alone permits funded promotion. Even an economic screen pass requires independent timestamp-locked forward evidence before generalizing. Challenge replay is gated behind economic validation and platform-specific contract/swap verification.

## 7. Required archive and status

No outcomes have been calculated as of this registration. `first_outcome_compute_at_utc` remains null until and unless the V2 preflight passes and the authorized outcome run starts.

The package must contain V2-required preregistration, exact runner/config/environment, source manifest/audit, deterministic eligibility+skip ledger, preflight log, full three-horizon grid, scorecard, selected-horizon full chronological leg ledger, annual cohorts, zero-inclusive weekly-R series, results, run log, output hash manifest and two-run reproducibility check. Local Python/container is the compute environment; GitHub is storage/versioning only. Do not use GitHub Actions for signal/PnL calculation.

**Failure interpretation:** DATA/PROCESS is not an economic conclusion; DATA/SAMPLE is not negative-alpha proof; an economic gate failure closes this registered candidate and must not be rescued by changing lookbacks/caps/costs/periods after results.
