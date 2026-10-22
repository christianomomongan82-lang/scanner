# Edge Search Reset Plan — 2026-10-22

**Status: PLAN / NO NEW SIGNAL PnL AUTHORIZED YET.** This document changes the research approach; it does not certify a strategy or permit a funded challenge.

## Decision

Stop generating another single-market candle/session variant. The project has many tests, but no strategy is approved for FundedNext. R321's 28 raw-price relation/horizon tests were negative; R326's exploratory result was negative in all three cohorts and all nine years; R323–R328 mostly stopped on sample, novelty, or package gates, not positive evidence. Repeating the same search style is not a credible route to the target.

The monotonic quantity we can require is **research integrity**, not candidate PnL. A real hypothesis may correctly fail. Promising that each successive backtest will improve would encourage selection bias and post-hoc tuning.

## Root cause

1. **Hypothesis concentration:** too much weight on candle geometry, short-horizon momentum, session breakouts/fades and threshold variations, often on EURUSD.
2. **Repeated data use:** EURUSD 2017–2025 and US indices 2017–2026 are contaminated/examined; they cannot be marketed as untouched out-of-sample validation. XAUUSD 2026 remains protected.
3. **Signal-by-signal optimization misses the actual objective:** the project goal is the probability of finishing both challenge phases by day 179 without a rule breach, not PF or trade count in isolation.
4. **The process stop became an open-ended loop:** unrecoverable historical package gaps should be explicitly classified and excluded from promotion, not used as a permanent reason to repeat the same audit. Existing records must still be reconciled and verified before new PnL is allowed.
5. **Execution and challenge mechanics matter:** quote-side BID/ASK fills, five-minute alert-to-entry delay, realistic friction, concurrent floating P&L, swap/commission, server-day reset, and the two-phase sequence must be applied after—not used to invent—a signal.

## Step 1 — Close the current governance debt once

Before any new signal PnL:
- **R317/R318:** if exact source runner/full row artifacts cannot be recovered from the repository, record them as irrecoverable historical archive failures and permanently non-promotable. Keep the published diagnostics; do not invent missing rows.
- **R319/R320:** retain their deterministic rerun evidence, but mark them exploratory because registration followed the outcome calculation; no retroactive “preregistered” claim. Explicitly record the remaining full-ledger storage gap/resolution.
- **R326:** the repository package currently shows a single base64 archive fragment plus compact report/results, not the full verified runner/ledger/weekly series. Unless the complete original bundle can be independently recovered and hash-verified, classify the archive as irrecoverable and non-promotable. Its negative metrics are diagnostic only.
- **R323–R328:** record each actual state faithfully: sample failure, novelty/process failure, or exploratory negative outcome. A sample gate failure is not proof of an alpha failure. An incomplete V2 package is not a closed economic verdict.
- Create one authoritative master ledger and family map through R328, reconcile all IDs/row counts/hashes and evidence links, read them back from GitHub, and run the V2 validator on the resulting compliant candidate package. Do not add PnL to the historical records or reopen closed families to clear this gate.

This is a one-time closeout task. If an artifact is demonstrably unavailable, classify it; do not keep asking the next experiment to inherit the same ambiguity.

## Step 2 — Change the search unit from a chart pattern to an economic return source

### First research lead: a diversified currency relative-strength portfolio

A published FX literature line reports cross-sectional momentum: currencies that were recent winners outperformed recent losers in broad samples. The authors also stress that transaction costs and limits to arbitrage matter. This is **a research lead, not evidence that this CFD implementation will work**. See Menkhoff et al., *Currency Momentum Strategies* (Journal of Financial Economics, 2012), also listed by the BIS:
- https://doi.org/10.1016/j.jfineco.2012.06.009
- https://www.bis.org/publ/work366.htm

This must not be a renamed R323 rerun. R323 tested a five-session USD-relative strength trigger with delayed individual entries and failed the preregistered pre-outcome sample gate (410 discovery / 270 confirmation legs versus its own higher gates); it produced no PnL evidence. A new portfolio-level design is only eligible after a written novelty audit explains the substantive difference: cross-sectional winner/loser portfolio construction, multi-week horizon, scheduled rebalancing, balanced USD exposure, portfolio overlap and risk caps, and a separate cost/swap treatment. If the audit concludes it is only a horizon/threshold mutation, reject it before PnL and choose a genuinely different family.

### Requirements for any candidate

- Start with one locked economic mechanism and a small, explicitly registered candidate set (normally <=100; prefer far fewer), not an open-ended threshold hunt.
- Use only available signal-time information; exact paired BID/ASK data; no fabricated bars; five-minute delayed executable entry where relevant; adverse gap and SL/TP collision treatment.
- Check sample eligibility before computing outcomes. Freeze discovery, confirmation, contamination declaration, candidate-selection rule, all cost stresses, annual stability and zero-inclusive weekly inference before PnL.
- Model commissions and swaps. If reliable historical swap inputs are unavailable, disclose that limitation and use predeclared conservative stress bounds; do not silently pretend spread is the only cost.
- Record the full screened grid, selected candidate, trade/skip ledger, weekly net-R series, run logs and hashes in GitHub; two clean deterministic runs; read back the committed artifacts.
- Reject any candidate whose edge vanishes at realistic cost or whose confirmation weekly block-bootstrap lower bound is not positive. Do not rescue it by increasing risk or changing parameters on the inspected period.

## Step 3 — Test the objective the user actually cares about

Only a candidate/system that clears the economic, stability, cost and reproducibility gates may enter the challenge engine. Replay the actual chronological streams through the complete FundedNext two-phase rules and estimate, with dependence-aware sequential paths:
- P(Phase 1 and Phase 2 completed without a breach and by day 179);
- probability of daily-limit and static-max-loss breaches;
- median / P90 / P95 time-to-funded among successful paths;
- drawdown, loss-streak, concurrency, spread/slippage/swap and delay sensitivity.

Use the exact broker symbol sizes, commission/swap and server reset/DST once verified. Test the registered risk range, including the user's intended range, but do not elevate risk to manufacture a pass rate. One isolated historical trade sequence is not a probability estimate.

## Decision gates

1. **Governance clear:** master ledger/family map through R328 reconciled; unrecoverable records classified; V2 validator passes on the new package.
2. **Economic edge:** positive net expectancy and required PF gates in discovery and independent confirmation, costs/stress passed, stable years, enough trades, weekly confidence bound above zero.
3. **Generalization:** use a genuinely held-out instrument-period or future timestamp-locked evidence. Do not repeatedly inspect XAUUSD 2026; unlock it once only after the pre-2026 gates pass.
4. **Funded pass:** actual challenge-rule replay demonstrates a nontrivial P(by day 179) with acceptable breach risk. Only this result answers whether the system meets the target.

If all candidate families fail these gates, the honest result is **GAGAL / no edge found so far**. It is not permission to lower the gates, recycle failed families, or claim a funded pass.

## Research references on false discoveries

- Bailey et al., *The Probability of Backtest Overfitting*: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
- Bailey & López de Prado, *The Deflated Sharpe Ratio*: https://doi.org/10.3905/jpm.2014.40.5.094
- White, *A Reality Check for Data Snooping*: https://doi.org/10.1111/1468-0262.00152

These methods address multiple testing and selection bias. They support a more reliable research process; they do not guarantee alpha.
