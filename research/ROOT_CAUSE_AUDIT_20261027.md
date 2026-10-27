# Root-cause audit: why the strategy research keeps failing
Date: 2026-10-27
Repository: `christianomomongan82-lang/scanner`
Branch: `research/root-cause-audit-20261027`
Scope: evidence review of the R189/R191 families and recorded research R251–R303. This is a synthesis, not a new backtest. The locked R332 preregistration is not changed or executed by this audit.

## Executive conclusion

The dominant explanation is **not one universal bug and not transaction cost alone**. Across the families actually tested, simple price-pattern rules often do not produce a durable conditional return advantage. A subset has an apparent gross/low-friction edge, but it is too fragile across years, too sensitive to realistic execution, or fails the account-path objective. The process also repeatedly used the same historical years to inform later hypotheses, so apparent winners are less reliable than their per-experiment “forward” label suggests.

There is an important correction to the shorthand “all strategies were bad before cost”: GitHub evidence does **not** support that literally for every experiment. R189, R292 and the canonical R191/R330 stream have positive results under at least some low-cost/aggregate views. They still fail to establish a sufficiently robust, reproducible, executable funded strategy. Many other strategies are demonstrably negative before *additional modeled costs*.

## 1. What the data say about signal quality

### Several valid tests were negative before additional cost

- **R258, multihorizon momentum:** forward PF was 0.832 on observed quote-side execution before the extra +1 pip stress, then 0.785 after it; all four 2022–2025 years were negative at the extra-cost setting. This is not a cost-only failure: the observed-quote result was already poor. Report: [R258 final verdict](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R258_FINAL_VERDICT.md).
- **R283, US-index cash-open gap fade:** the report's gross PF before modeled costs was 0.795 in discovery and 0.638 in validation. There were more stops than targets in both segments. Report/evidence: [evolutionary evidence matrix](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/EVIDENCE_MATRIX_20261016.json).
- **R291, transatlantic lead–lag:** discovery gross PF_R was 0.769 and net was −36.653R before costs; all four discovery years were negative. The one positive gross validation segment did not survive modeled costs, with an additional tiny-stop/cost-normalization pathology exposed in the audit.
- **R272-B, XAUUSD failed-sweep fade:** discovery −437.47R and validation −401.22R at the stated added-cost setting; the report says it was negative even with zero *incremental* cost.
- **R274, XAUUSD impulse follow-through:** discovery and validation were negative, and 0/5 validation years were positive; recorded as negative even at zero incremental friction.
- **R298, XAUUSD London sweep-and-reclaim:** at +$0.30/oz, discovery was −285.893R/PF 0.297 and validation −178.933R/PF 0.409. Even at zero *added* cost, discovery/validation remained −132.434R/PF 0.515 and −100.768R/PF 0.575. All five annual cohorts in both periods lost.

“Zero added cost” is not always “zero transaction cost”: when the engine enters at ASK and exits at BID (or vice versa), the observed spread remains embedded. Conversely, several index experiments use BID-only data and merely subtract a modeled basis-point charge, so their fee assumptions are not a measured broker cost.

### Other hypotheses had a small or unstable edge, not a robust one

- **R189/L80 historical Dukascopy replay:** PF was 1.442 at no *extra* cost, but only 1.082 at +1 pip for 2016–2025; discovery was 1.056 at +1 pip, and the four-week forward bootstrap interval crossed zero. Median hold was two minutes; 79.1% of trades exited within five minutes, which is not compatible with the current several-minute manual phone workflow. This is also not an exact reproduction of the missing original HistData archive. Report: [R189 replay](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R189_DUKASCOPY_HISTORY_RESULTS.md).
- **R292, unconditional USA500 overnight long:** gross discovery PF was 1.193, but PF was 1.094 at modeled 2bp and 1.002 at 4bp. Validation's 4-week weekly-net bootstrap interval crossed zero; closed-trade drawdown reached 38.57% of fixed notional in discovery. This looks partly like broad equity exposure/carry, not proof that the added price signal works.
- **R289, continental Europe cash-open gap continuation:** discovery and validation PF were above 1 at 2bp, but the validation weekly-bootstrap interval crossed zero. The locked gate correctly rejected it rather than declaring a small sample to be an edge.
- **R303, EURUSD spread-shock reversion:** zero-extra-friction aggregates were slightly positive, but both discovery and validation turned negative at +0.5 pip. This is a thin, friction-sensitive result rather than a robust edge.

The repeated finding is therefore: many patterns do not predict the next executable price path well enough; others only look good under generous costs, selected periods, or weak samples.

## 2. Why the same failure pattern repeats

### A. We mostly test transformations of the same information

Many “different” strategies are close relatives in information terms: recent return/displacement, a rolling high/low break, a range expansion, a failed break, a sweep/reclaim, or the opposite directional interpretation of one of these. Changing continuation to fade does not create a new source of predictive information. It only changes the mapping from the same recent OHLC history to a trade.

Across R251–R258 and R270–R303, the labels cover different families, but most inputs are still price bars, recent ranges, sessions, and thresholds. The tests do not show that these particular conditional patterns have a durable advantage. Several gross-negative examples above are direct evidence. This does **not** prove that all price-only trading is impossible; it means the rules actually tested have not demonstrated a dependable advantage.

### B. The research program has a multiple-testing / winner's-curse problem

A preregistration can protect an individual experiment from tuning after seeing its outcomes. It does not make later research independent if those same years are repeatedly inspected to invent the next hypothesis. The evidence matrix explicitly records:
- 2021–2025 as repeatedly viewed and contaminated for program-level validation;
- 2022–2025 as research-contaminated for several index experiments;
- 2026 index results as diagnostic, not an untouched global holdout.

So a “forward pass” for one round is not automatically an independent program-level confirmation. Repeatedly choosing the next idea based on the same historical patterns makes it likely that the best-looking examples are exaggerated by chance. This explains why isolated positive slices repeatedly fail elsewhere; it does not by itself explain every negative gross result.

### C. Execution costs and latency destroy thin edges

Where the signal is already weak, the edge has little room to pay spread, fees, slippage, and delay. R189 is the clearest operational example: fast exits cannot be reproduced by placing a manual MT5 order after an email alert. R275's delayed L80 variant fell to PF 0.694 at +1 extra pip. R303 became negative at +0.5 pip. These are not all the same cause as a gross-negative strategy, but they compound the problem.

Some cost estimates in the index reports are explicitly modeled bps rather than measured ASK/BID spreads, commissions, and live slippage. Therefore cost-stress results are screening evidence, not final live-economics proof.

### D. Several tests have genuine data/implementation failures

The project has correctly recorded important invalid or untested results:
- **R257:** zero validation trades were caused by eligibility/coverage implementation problems. The corrected R281 replay produced trades, but every locked discovery configuration still lost at +1 pip (PF 0.575–0.667). R257 itself is not proof of no edge; R281 is evidence against the tested corrected configurations.
- **R296:** the runner treated static Sunday quote rows as a tradable market reopening. Its PnL is invalid and must not count as a strategy failure. Corrected R297 then failed its locked gates with a very small sample.
- **R282 weekend-gap tests:** the raw feed lacked the necessary active reopening timestamps, so zero evaluated trades means data inadequacy, not negative expectancy.
- **R189:** the original HistData M1/spread archive and chronological ledger were unavailable; the Dukascopy replay is a different-feed replication, not an exact historical reproduction.
- **R330:** the canonical R191 results shifted when the M5 cache version changed, even though the rule stayed locked. The current run passed determinism and prefix checks against its actual cache, but this is a reminder that data version and provenance must be pinned before interpreting changes.

These issues weaken the reliability of particular rounds and show that previous summaries sometimes mixed “signal failed,” “not testable,” and “test invalid.” They are not a plausible single explanation for all strategy losses, because multiple valid replays were negative in both discovery and validation.

### E. Aggregate edge is not enough; regimes and correlations matter for funded passing

R330 is the most important counterexample to “everything is negative before cost.” With the canonical R191 long-only H4 breakout pooled over ten indices, forward 2022–2025 PF was **1.301 at modeled 2bp**, and discovery PF was 1.508. But the worst forward year, 2022, had PF **0.561**. The pooled challenge simulator failed:
- At 0.5% risk/trade, pass-both within five years was 50.7%, below the 65% gate, and DLL/MLL breach was 21.48% versus 5.75% for R191-only.
- At 1.0% risk/trade, basket pass-both was 46.17% versus 54.52% for R191-only, with breach 29.33% versus 28.57%.

Adding ten index CFDs did not create independent opportunities in the way ten unrelated bets would. They share broad equity/risk regimes; the locked test itself showed the 2022 weakness and worse challenge trade-off. A healthy pooled PF can therefore coexist with poor funded-challenge reliability.

Also, the “causality audit” in R330 is a *no-lookahead/prefix-consistency audit* of signals and trade mechanics, not proof of causal predictive power in the statistical/economic sense. Passing it means the tested computation appears time-consistent; it does not establish a tradable alpha.

## 3. What is the main root cause?

Evidence-weighted ranking:

1. **Primary:** the majority of the tested price-pattern hypotheses have no demonstrated robust conditional edge under their locked entry/exit rules. A number are negative even before additional friction.
2. **Second:** the search loop repeatedly varies interpretations of similar OHLC information, while the same historical periods inform later decisions. This makes occasional positive results easy to overrate and prevents a clean program-level claim of out-of-sample success.
3. **Third:** weak edges are further eroded by cost and the real execution delay. This is especially severe for M1/short-hold systems.
4. **Fourth:** regime concentration and correlated index exposures make aggregate backtest results a poor proxy for a challenge pass.
5. **Important reliability issue:** data bugs and source-version changes have invalidated some individual experiments; they require separate labels, not being counted as negative-alpha evidence.

What we **cannot** claim from the current archive is a precise percentage of all historical experiments that were gross-negative: many reports store only cost-adjusted PF, and some raw trade ledgers are not archived. A proper count requires a unified ledger that separates gross PnL, observed quote-side spread, incremental cost, modeled-only cost, and invalid/untested runs.

## 4. Changes this audit supports

1. Stop describing every result as merely “bad.” Every round should receive one of these distinct dispositions: **negative expectancy**, **edge too cost-sensitive**, **regime/robustness failure**, **funded-path failure**, **invalid test**, or **data-insufficient/untested**.
2. Do not rescue old signals by adjusting thresholds or stop/target after seeing the failed years.
3. Before running any future strategy, explicitly state the proposed source of edge and measure the signal's incremental predictive value against a matched unconditional/randomized baseline; separate signal quality from stop/target design and execution.
4. Require a master experiment ledger and a clean prospective holdout. Since index years 2022–2026 have been repeatedly inspected, they should not be presented as untouched global OOS.
5. Keep the fully locked R332 preregistration unchanged. Its useful question is whether one common trend rule across less-redundant asset classes improves robustness; it must be treated as a test, not assumed to solve the above problems. If its gates fail, record the reason and do not mutate the rule after the result.

## Sources inspected

- [R251–R258 failure taxonomy](https://github.com/christianomomongan82-lang/scanner/blob/r251-fx-cross-pair-lead-lag/research/R251_R258_failure_taxonomy.md)
- [R270–R303 evidence matrix](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/EVIDENCE_MATRIX_20261016.json)
- [R270–R303 evolutionary block registry](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/EVOLUTIONARY_BLOCK_REGISTRY_20261016.md)
- [R189 Dukascopy replay results](https://github.com/christianomomongan82-lang/scanner/blob/local-backtest/r189-dukascopy-history/research/R189_DUKASCOPY_HISTORY_RESULTS.md)
- [R330 results JSON](https://github.com/christianomomongan82-lang/scanner/blob/research/r330-r191-pooled-ten-index/research/R330_results.json)
- [R330 final verdict](https://github.com/christianomomongan82-lang/scanner/blob/research/r330-r191-pooled-ten-index/research/R330_FINAL_VERDICT.md)
- [R332 locked preregistration](https://github.com/christianomomongan82-lang/scanner/blob/research/r332-multi-asset-trend/research/R332_LOCKED_PREREGISTRATION.md)
