# GitHub-Only Root-Cause Audit — Why Later Backtests Look Worse
Audit date: 2026-10-23
Scope: repository evidence in `christianomomongan82-lang/scanner`, including the R189 cross-feed replay, R218–R250 independent audit packages, R251–R310 master search ledger and per-round reports. The user-uploaded ZIP is not an audit data source; it was only context for the observation that pre-GitHub results looked better.

## Executive conclusion

**The deterioration is real in the stored experiment record, but it is not explained by one universal bug.** The GitHub history shows three major causes:
1. **Method/objective drift:** the project moved from an older EURUSD M1 setup (R189/L80) to many different FX/index/XAU hypotheses and different timeframes, feeds, cost units, and holding horizons. Those later results are not a controlled continuation of the older setup, so their weaker PFs do not by themselves prove the old strategy deteriorated.
2. **A large share of newer candidates have genuinely negative or unstable expectancy once tested across chronological splits and cost stress.** This is not just a data bug: multiple independent ledger audits passed, yet the strategies failed forward/inference gates.
3. **The older candidate's attractive historical report did not fully match the user's real execution constraints or a funded-account replay.** R189's historical cross-feed replay is not an exact reproduction of the original HistData results; its own report says it is not approved for funded/manual execution. R275 explicitly tests the five-minute phone delay and the result becomes substantially worse.

The process-level root cause is that we kept expanding the strategy search and changing research scope before resolving the older baseline's reproducibility and practical execution gap. That made the research ledger larger, but did not increase confidence that any candidate would pass the actual funded challenge.

## Evidence from GitHub

### 1. The newer rounds mostly failed for economic, not coding, reasons

R218–R250 have extensive independent audit evidence:
- R218–R226: 106/106 trade ledgers passed, 102,860 rows inspected, 90/90 causal-prefix checks and 100/100 registered tests passed. None of nine hypotheses passed forward gates.
- R227–R234: 92/92 unique ledgers passed, 60,074 trade rows inspected, 180/180 prefix checks and all 10 source files passed. No candidate passed PF >= 1.15 at both modeled 1 and 2 bps plus annual stability.
- R235–R242: 88/88 ledgers passed, 75,308 rows inspected, 190/190 prefix checks passed. R236 and R238 had forward PF above 1 at the primary modeled costs but failed inference/annual/OOS gates; the other candidates failed discovery or forward gates.
- R243–R250: 90/90 ledgers passed, 119,234 rows inspected, 190/190 prefix checks passed, zero failed assertions. R243–R245 failed discovery; R246–R250 failed forward/inference gates. Holm-adjusted positive-expectancy p-values were 1.000 for the eight registered hypotheses.
- R251–R310 master ledger classifies the recorded hypotheses as failed, non-promoted, data/sample-invalid, or otherwise not eligible. Examples include R258 (forward PF 0.785 at +1 pip, all four 2022–2025 years negative), R260 (forward PF 0.438 at +1 pip; 3,633 trades, all forward years negative), R298 (XAU London sweep/reclaim strongly negative), R299 (US index lead-lag not robust), and R305–R306 (cross-asset USD-factor candidates negative even at zero added cost).

This rules out the explanation that the entire late-stage collapse is merely a broken backtest engine. The audited index batches in particular passed source/ledger/causality checks while failing economically. However, their inputs are often BID-only and costs are modeled, so they are not equivalent to a broker-verified execution replay.

### 2. Repeatedly selecting on the same historical years weakened the evidence

The repository's own R276–R299 process audit states that no clean program-level holdout remained: discovery/validation windows and 2022–2026 diagnostics had already been examined across many related experiments. It also documents clusters of related strategies on the same US index M5 feeds and repeated years.

The master ledger labels 2022–2026 as already examined for many experiments. Nominal single-test bootstrap intervals do not correct the entire research program's multiple-selection bias. A later positive window is therefore not independent confirmation after dozens of neighboring hypotheses have been evaluated against it.

This does **not** mean every result is overfit. It means confidence in the overall winner-selection process is lower than a per-round report alone suggests.

### 3. The old R189 result is promising historically, but not a controlled, funded-ready baseline

The GitHub report `R189_DUKASCOPY_HISTORY_RESULTS.md` records a separate Dukascopy BID/ASK replay—not an exact reproduction of the original HistData archive. In that replay:
- 1,673 trades on the intrabar execution-sensitivity variant.
- At +0.2 pip extra friction: PF 1.360, net +1,800.9 pips across 2016–2025.
- At +1 pip extra friction: PF 1.082 overall.
- On the 2021–2025 slice, PF is 1.114 at +1 pip, but annual PF at +1 pip includes 2022 at 0.976.
- The four-week weekly-net bootstrap at +1 pip has 95% CI [-0.223, +2.489] pips/week, which crosses zero.
- The report says median holding time is 2 minutes, 30.7% exit within the entry minute, 47.5% within one minute, and 79.1% within five minutes. This is incompatible with the stated manual phone workflow without a delay-specific test.
- Its own verdict is NOT PASSED and explicitly says it is not approved for funded challenge or live manual execution.

So R189 should not be discarded as worthless; it is a historically promising lead. But the repository itself does not support the stronger claim that it was already a robust funded-ready strategy.

### 4. The execution-delay experiment is a concrete reason old results did not transfer

R275 keeps R189/L80 signal rules fixed and tests exact T+1 versus a phone-compatible T+6 entry. On the 2022–2025 diagnostic period at +1 pip extra cost:
- Parent T+1: 699 trades, PF 0.839, net -378.5 pips, max drawdown 440.0 pips.
- Child T+6: 701 trades, PF 0.694, net -786.3 pips, max drawdown 816.9 pips.
- The delay worsened net result by 407.8 pips and increased maximum drawdown by 376.9 pips.
- The child remains negative at +0.2 pip extra cost (PF 0.901).

R275 is not a clean test of whether all earlier results were false; it is a test that the exact L80 setup does not survive the user's specified delayed execution in this period. But this is directly relevant to the funded objective: a strategy that works only at near-immediate M1 execution is not usable through email alerts and manual phone placement.

### 5. Actual BID/ASK audit also weakens the older index-baseline narrative

R203's locked R191 H4 index breakout baseline had aggregate forward PF 1.617 for the selected USA500 under observed ASK-entry/BID-exit execution, but only 38 forward trades. The 2022 entry-year cohort had 10 trades and PF 0.497; OOS had only four closed trades. The report therefore rejects the baseline under annual-robustness gates. This is another example where aggregate PF looked strong but sample and year consistency did not support promotion.

### 6. Data defects exist, but must be separated from strategy failures

Examples in the GitHub history:
- R257 had a coverage/eligibility defect that yielded zero validation trades; its original outcome is a data/implementation failure, not evidence of negative alpha. Corrected follow-up R281 still failed the discovery and validation-sample gates.
- R270's continuation module was structurally unreachable under its registered ER threshold; the active fade module was negative.
- R272's Module A was also unreachable (zero trades) while Module B was materially negative even at zero incremental cost.
- R282 was data-inadequate because the required reopening stream was missing; it must not count as an economic failure.
- R296's XAU reopening event-time issue was corrected in R297; only the corrected result is valid evidence for that exact setup.
- MRM V1's flat/closed-market contamination was corrected separately on 2026-10-23, but the corrected forward result remained negative (PF 0.821). This is a real bug that did not explain the overall failure.

These are real engineering issues, but the ledger also contains many well-audited candidates that fail on expectancy. Fixing data plumbing alone will not create an edge.

## Root-cause ranking

1. **Primary process failure — search drift without a single controlled comparison to the older baseline.** The project changed instruments, timeframe, mechanisms, feed, cost unit, and entry assumptions across successive rounds. As a result, many new rounds were not measuring whether we were getting closer to the original practical objective.
2. **Primary strategy failure — the tested hypotheses mostly do not have robust net expectancy.** High trade counts often coexist with PF below 1 after costs; many positive discovery estimates reverse in forward years.
3. **Primary real-world transfer failure — the best-known FX lead has not survived a phone-delay test.** R275 is direct evidence.
4. **Program-level statistical failure — repeated reuse of the same market years and related strategy families.** Candidate-level gates were useful, but aggregate winner confidence was overstated if interpreted as independent discovery.
5. **Secondary engineering/data failures — synthetic flat bars, unreachable branches, invalid coverage grids, inconsistent versions and historical feed mismatches.** Important, but not a universal explanation.

## What should change, based on this audit

- Stop generating unrelated rounds until the ledger comparison is complete.
- Do not treat R189, R191, R276 or any aggregate-PF winner as a promoted baseline. Keep them as leads with explicit unresolved constraints.
- Use the same locked data feed, timestamps, quote sides, costs, entry delay and funded-equity simulator for any head-to-head comparison.
- A future test must answer one question: does it improve probability and time-to-pass under the actual phone workflow and funded limits versus a reproducible baseline? If not, it does not advance.
- Preserve program-level holdout status honestly; do not call previously viewed 2022–2026 data pristine OOS.
- Keep data-invalid outcomes separate from economic GAGAL outcomes.

## Final audit verdict

**The newer research looks worse mainly because it tested many genuinely weak hypotheses under stricter/varied evaluation, while the older standout result was not yet validated under the same data/execution/selection contract.** The archive does not support blaming one universal bug or claiming all old results were fake. The most actionable mismatch is that R189/L80's very short holding times do not fit manual delayed execution, and its delay-specific child R275 failed. The other major failure is process drift: many rounds were launched without a stable, common, funded-objective comparison.
