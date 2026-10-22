# Research Policy Amendment — Separate Exploration from Promotion
Date: 2026-10-23
Branch: `local-backtest/market-response-model-v1-20261023`
Status: proposed operating correction based on audit of the current search rules.

## Executive decision

Keep the funded-promotion standard strict. Change the *search process* so that exploratory discovery is not forced to carry the full paperwork and evidence burden of a promotion candidate.

The current process has conflated two distinct questions:
1. Is this hypothesis worth exploring further?
2. Has this exact frozen system earned the right to be called funded-ready?

A negative exploratory screen can kill a weak idea cheaply. It must not be presented as proof that an entire economic mechanism is impossible. A promising exploratory screen is only a lead, never a funded pass claim.

## Two-lane research system

### Lane A — Exploration and discovery

Purpose: search broadly and cheaply for conditional return structure; rapidly reject weak hypotheses.

Allowed:
- Batch-test multiple clearly described, structurally distinct hypotheses and small predeclared parameter grids on development data.
- Use automated data-integrity, eligibility, and quote-side checks before PnL.
- Record a compact experiment manifest: hypothesis/family, instruments, timeframe, dates, data hashes, entry/exit definition, cost assumptions, candidate count, and verdict.
- Run fast first-pass economics with observed BID/ASK where available, the intended five-minute manual delay, and a modest adverse-cost case. Additional full stress grids can be reserved for survivors.
- Use previously inspected periods as development/diagnostic data, explicitly labeled contaminated. Results there may help reject or prioritize ideas, but may not establish independent OOS evidence.
- Keep an idea alive as an *unconfirmed lead* when evidence is inconclusive because of low event count or data coverage; label it DATA/SAMPLE-INCONCLUSIVE rather than pretending it has negative alpha.

Not allowed:
- Claim a discovery result is OOS, robust, funded-ready, or a valid pass probability.
- Inspect the protected final holdout to choose symbols, thresholds, rules, or among candidates.
- Re-label a cosmetic retune of a closed candidate as a new family.
- Omit negative results or fail to record how many variants were screened.

### Lane B — Candidate promotion

Only survivors from Lane A enter this lane. Before validation outcomes are calculated, freeze:
- exact rules and all parameter values;
- candidate identity, family/lineage, and selection rationale;
- data source, quote sides, timestamps, checksums, and eligibility policy;
- intended five-minute execution delay, executable entry/exit prices, fees, swaps and cost stress;
- discovery/validation/forward boundaries and all prior exposure to those periods;
- runner, configuration, output ledger, and scoring contract.

Then apply the existing strict promotion gates: independent evidence, realistic execution, complete chronological trade ledger, cost/slippage robustness, and verified two-phase challenge replay with floating equity, daily/max loss rules, minimum days, and uncertainty-aware path simulations.

No gate is relaxed by this amendment. The change is that only a screened survivor needs the full promotion-grade process.

## Family restrictions: narrow them to what the evidence actually supports

A family closure applies to the exact registered mechanism and close descendants whose only change is symbol, timeframe, threshold, clock window, stop/target, or entry timing.

A genuinely different causal mechanism may be explored if it:
- has a written pre-outcome rationale for why prior negative evidence does not already test it;
- is tagged as a new mechanism, not a rescue of a failed candidate;
- is evaluated on development data without touching protected holdout outcomes;
- receives no presumption of profitability and must still pass the same promotion gates.

Do not infer that all reversal, momentum, session, cross-market, or machine-learning approaches are impossible because a subset of specifications failed. Conversely, do not use broad labels such as “new AI model” or “new market regime” to disguise the same signal.

## Efficient search order

1. **Coverage check:** confirm active quotes, event availability, feature reachability, and adequate usable data before expensive PnL.
2. **Broad discovery:** search diverse mechanisms/instruments/timeframes; record all variants and rank leads by net conditional economics, event count, stability, and distinctness—not PF alone.
3. **Cheap falsification:** reject hypotheses that are negative after observed spread or fail even at zero *incremental* cost, unless the data/implementation test itself is invalid.
4. **Survivor audit:** check matched baseline, ablation, annual/regime distribution, delay sensitivity, and additional-cost sensitivity.
5. **Freeze and promote:** preregister only survivors; use independent/untouched evidence and the existing full funded scorecard.
6. **Update the evolutionary library:** preserve why each idea failed and which components are reusable engineering versus unproven alpha.

## Interpretation labels

Use separate labels for:
- `GAGAL — ECONOMIC SCREEN`: valid exploratory test, negative economics.
- `GAGAL — DATA/IMPLEMENTATION`: test cannot support an economic conclusion.
- `INCONCLUSIVE — SAMPLE/COVERAGE`: insufficient eligible events or reachability.
- `SURVIVOR — DISCOVERY ONLY`: worth freezing for promotion tests; not validated.
- `GAGAL — PROMOTION`: frozen candidate failed one or more required promotion gates.
- `LULUS — FUNDED-READY`: all mandatory promotion gates pass.

The project may continue to report the user-facing final binary outcome as LULUS/GAGAL for a candidate, but internal diagnostic labels must distinguish a bad strategy from a bad or inadequate test.

## Immediate application to current project

- Do not resume near-duplicate R302–R310 or MRM V1/V2 retuning on their old periods.
- Keep R189 as an unconfirmed lead requiring reconciliation and independent evidence; its delay sensitivity is a real concern, not grounds to discard it without review.
- Do not run another strategy family until the repository contains a reproducible local runner, full event/trade ledger, and the common scoring adapter. This is a prerequisite for trustworthy measurement, not a reason to narrow the economic hypothesis space.
- Use existing contaminated years for discovery only. Keep the protected final window closed until a single frozen survivor clears the predeclared historical gates.
- GitHub remains storage/versioning; compute backtests locally in the ChatGPT/container environment, not in GitHub Actions.

## Bottom line

Loosen the *exploration workflow*, not the *proof standard*. Search broadly, screen cheaply, keep failures informative, and reserve expensive independent validation plus the full funded replay for actual survivors. This improves search throughput without manufacturing a pass claim or weakening protection against overfitting.
