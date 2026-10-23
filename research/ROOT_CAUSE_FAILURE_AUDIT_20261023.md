# Root-cause audit: why the backtest programme keeps failing

**Date:** 2026-10-23. This is a diagnosis, not a new strategy result; no signal PnL was run for this audit.

## Executive finding

There is no single universal failure cause. The project has mixed three very different outcomes under “GAGAL”: (1) economic falsification, (2) discovery winners that fail out of sample, and (3) data/sample/governance stops where PnL was never calculated.

For the latest eight records R322–R329, six (R322–R325, R327–R328) stopped before a valid PnL verdict because sample/process gates failed. R326 had negative exploratory metrics but an incomplete V2 archive. R329 was an actual economic-screen failure. It is inaccurate to say all of R322–R328 were proven unprofitable. Equally, repeated economic failures cannot all be blamed on process defects.

**Dominant diagnosis:** the tested price-pattern and short-horizon FX hypotheses have not produced a persistent, executable return source. Multiple testing and repeated use of the same historical periods create occasional discovery winners that collapse in validation. Costs/latency amplify this, but do not explain every negative result.

## Direct evidence from our ledger

- **R321:** all 28 registered causal EURUSD price-state/horizon comparisons were negative at primary cost. Even at zero *additional* friction, the best pair remained negative (−0.2568 pip/event; PF 0.934). Its weekly bootstrap intervals were wholly negative. “Zero additional friction” still used executable BID/ASK prices; it did not remove the observed spread.
- **R329:** the selected 13-week seven-pair FX time-series-momentum portfolio was +1.811R in discovery before incremental commission/slippage/swap deductions, but −2.093R in confirmation on executable BID/ASK. With primary costs it was −2.606R/PF 0.862 in discovery and −5.283R/PF 0.651 in confirmation. The 26- and 39-week alternatives also failed. Only 2020 was positive among the three complete discovery years. Incremental costs worsened the result but cannot explain the confirmation sign reversal.
- **R317:** discovery +39.398R became validation −37.264R; validation remained −3.862R even at zero additional cost.
- **R318:** all five discovery-selected top configurations lost in validation (PF 0.787–0.867).
- **R319:** of 972 configurations, 11 passed discovery and 0/11 passed confirmation or the later diagnostic period; the selected candidate went from +17.038R/PF 1.208 to −25.860R/PF 0.555 in confirmation.
- **R320:** its single discovery-selected candidate was weak (+4.918R/PF 1.059) and became −5.173R/PF 0.917 in confirmation.
- Other cases (including R300–R311 and R326) also report multiple negative periods or negative results at zero *incremental* cost. That makes “we only need better cost assumptions” an insufficient explanation.

These examples indicate that the tested signal relationships were absent, too small, or nonpersistent under executable quotes and the entry-delay assumptions. They do not prove all trading strategies are impossible.

## Ranked explanations

These are evidence-weighted judgments, not statistically calibrated probabilities. Causes overlap.

### 1. No stable, cost-surviving edge in the tested price-pattern/short-horizon FX hypotheses — **very high likelihood; dominant economic cause**

The evidence is strongest where negative performance remains even before *additional* friction (R321, R317 validation, multiple R300–R311 tests) or where executable-side confirmation itself is negative (R329). Numerous EURUSD candle, impulse, breakout, sweep/reclaim, short-horizon momentum and session variants have not supplied a stable directional effect.

### 2. Multiple testing and contaminated validation — **very high likelihood for why discovery winners collapse**

R318 searched 972 rules; R319 searched 972 configurations, selected 11 discovery winners and then saw all 11 fail confirmation. R317 and R320 show similar discovery/validation reversals. The project also repeatedly examined 2017–2025; those periods are not fresh project-level holdout data. R319/R320 were registered after outcome calculations, so their own selection results cannot be treated as preregistered evidence.

This matches established methodology warnings:
- Bailey et al., *The Probability of Backtest Overfitting*: repeated selection makes ordinary holdout methods unreliable: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2326253
- Harvey, Liu and Zhu: new discoveries require a higher statistical hurdle after extensive multiple testing: https://www.nber.org/papers/w20592
- White's Reality Check: repeated reuse of data can make apparently good rules look better by chance: https://doi.org/10.1111/1468-0262.00152

Data reuse is a powerful explanation for false winners; it does **not** explain every losing candidate.

### 3. Too much hypothesis concentration and weak differentiation — **high likelihood**

The ledger repeatedly tests related chart-pattern/session/threshold variants, especially in EURUSD and other FX price-only data. Changing a threshold or naming a variant differently does not create a new economic return source. We have spent substantial effort searching candle geometry and short-horizon price continuation/reversal without identifying a mechanism that persists after delay and costs.

### 4. Costs, spread and manual latency — **high as an amplifier; not enough as a universal root cause**

Several candidates are cost-fragile, and R275 showed delay sensitivity. A five-minute alert-to-entry process is incompatible with signals whose edge decays over only a few minutes. Neely and Weller's out-of-sample FX technical-rule study found no excess returns after realistic transaction costs and trading-hour restrictions: https://www.sciencedirect.com/science/article/abs/pii/S0261560602001018. But empirical work does not say every technical rule is always unprofitable: Hsu, Taylor and Wang found that FX rule profitability varied over time across 30 currencies and 21,000+ rules: https://www.sciencedirect.com/science/article/pii/S0022199616300472.

R329 also has real limitations: H1 bars were an hourly bar-open proxy rather than the exact executable quote five minutes after the signal, and swap stress was a proxy, not verified symbol-specific funding. These limitations weaken precision in its estimated magnitude, but do not rescue its negative confirmation result.

### 5. Data/implementation/archive defects — **high for named affected experiments; medium as a programme-wide explanation**

Known examples include hourly coverage/flat-row defects (R257/R281), missing active reopening rows (R282), and static Sunday quotes misclassified as active reopening (R296). R329's local executed runner was not byte-identical to the pinned repository runner. R317/R318 lack complete runner/grid/row-ledger packages. These defects prevent promotion or weaken reproduction for the affected records; they do not explain away every well-audited negative result.

### 6. Sample gates are preventing economic evaluation — **very high for why the latest batch has so few actual PnL verdicts**

Six of R322–R328 stopped before valid PnL. Examples: R322 had 131 discovery / 49 confirmation setups versus registered floors of 200 / 100; R323 had 410 / 270 legs against 1,000 / 600; R324 had 341 / 222 against 400 / 250; R325 had 593 discovery setups against 600. R327/R328 also failed frozen sample floors.

Those are not proof of negative alpha. They are sample/process or target-feasibility failures. The workflow's weakness is that generic minimum trade counts are not automatically a statistical-power measure and are not the same as probability of meeting the day-179 account target. High-frequency signals can still be highly correlated; low-frequency signals may lack the opportunity count needed to pass in time.

**Correction:** future sample gates must be preregistered with explicit statistical precision/power or economic-feasibility reasoning, accounting for serial dependence and the challenge deadline. Never lower a gate after seeing a failed count. If the signal is too rare for the objective, label it **GAGAL — TARGET FEASIBILITY/SAMPLE**, not “proven unprofitable.”

### 7. Challenge speed and safe risk are in tension — **very high as a separate target blocker**

The actual target is not just positive PF: it is +8% then +5% within 179 days without a daily/static loss breach. Prior legacy R189 results reported a roughly 12–14 month median at 0.5% risk versus roughly five months at 1% but higher breach rates; those figures need current runner/source validation before being relied upon. R270's old context/router challenge proxy reported no more than 1.1% deadline completion and 97.9% breach at 1% risk. No current candidate has a validated pass probability. R321/R329 did not reach funded replay after failing economic gates.

The literature on time-series momentum is not a contradiction: Moskowitz, Ooi and Pedersen documented 1–12 month persistence across 58 futures across several asset classes: https://doi.org/10.1016/j.jfineco.2011.11.003. R329 was only seven mostly USD-linked FX CFD pairs, not that diversified futures universe; its negative result rejects the frozen R329 specification, not the whole literature.

## What this means operationally

1. **Do not start R330 as an automatic next step.** We need a materially distinct economic return source, not a nearby threshold change.
2. **Separate verdicts:** ECONOMIC FAIL only when PnL gates ran; DATA/PROCESS FAIL when the experiment could not be validly scored; TARGET-FEASIBILITY/SAMPLE FAIL when there cannot be enough opportunities for day 179; CHALLENGE FAIL only after rule-aware account replay.
3. **Do not treat 2017–2025 or US-index 2017–2026 as clean holdout.** Keep the reserved segment locked until a frozen candidate passes earlier gates.
4. **Pre-register the whole grid and selection method before PnL.** Account for multiple testing and serial dependence; do not tune on validation after failure.
5. **Design around actual execution from the start:** five-minute delay, executable BID/ASK, symbol-specific commission/swap, adverse gap/slippage, and verified platform time. R329's hourly proxy and swap assumptions must not be treated as exact.
6. **Promotion requires a complete rule-aware two-phase path**, including daily/max loss, deadline, dependencies and sequential paths. PF alone is not a pass probability.
7. **Progress should be monotonic in research integrity, not backtest PnL.** Requiring every experiment to show a higher PnL would incentivize selecting against inspected history—the same process that produced R317–R320's discovery/validation reversals.

## Current decision

**No candidate is proven funded-ready, and no supported probability of passing both phases by day 179 currently exists.** The most likely root cause is the combination of weak/nonpersistent hypotheses and a search process that repeatedly over-selected discovery winners from reused data, with cost/latency friction and some data/governance defects. The next action should repair and redirect the research design, not retune a closed candidate. No new signal PnL was authorized or calculated in this audit.
