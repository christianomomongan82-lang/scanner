# R278 — Long-only same-day-flat US cash-open breadth router

**Status: PREREGISTERED before calculation.**  
**Parents:** R277 same-day-flat synchronized cash-open breadth router and the previously tested R206 cash-session opening-range setup. The child tests a structural direction restriction, not a stop/target/threshold search.

## Economic hypothesis
Broad equity indices have positive long-run drift and downside moves often have different speed and gap risk than upside moves. This candidate only trades synchronized upper-range breakouts; short breakouts are excluded. It uses the same 3-of-4 index confirmation, entry delay, exits and costs as R277, so its contribution can be isolated against a matched long-only parent.

## Locked rules
- Four U.S. index CFDs: USA500/S&P 500, USATECH/Nasdaq 100, USA30/Dow Jones and USSC2000/Small Cap 2000.
- Opening range is six exact M5 bars opening 09:30–09:55 America/New_York, all six present, at least four non-flat, positive high-low range.
- Signal is the first completed M5 close **strictly above** that index's opening-range high between 10:00 and 15:45 New York. Downside breaks are ignored. At most one upper-breakout signal per index/session date.
- Child entry eligibility: at least three of four indices must have an upper-breakout signal on the exact same M5 timestamp. All four feed timestamps must exist at that time; pre-2018-08-08 timestamps are ineligible because USSC2000 history is unavailable.
- Exact T+10-minute entry after signal bar open (M5 bar completion plus five additional minutes). Exact timestamp and non-flat entry bar required. Do not substitute nearest bars.
- Stop at the opening-range low; target 2R. Stops checked before targets on same-bar ambiguity. Opening gaps through a level use the opening price. If neither target nor stop is hit before 16:00 NY, exit at the exact 16:00 bar OPEN without reading that bar's high/low. No overnight carry; if the exact close bar is missing, skip the entry.
- One position at a time per index; no same-index overlap. Multiple indices may be entered on a synchronized signal.
- Parent for attribution: unfiltered long-only upper-breakout stream using identical T+10 entry and same-day exit. Child: 3-of-4 synchronized upper-breakout router. T+5 parent is diagnostic only.
- Costs: modeled round-trip deductions of 1 and 2 price basis points of entry notional, converted to R by initial stop risk. BID-only inputs are a screening proxy, not actual bid/ask/cost data.

## Locked screen protocol
Discovery 2017–2021; exploratory forward screen 2022–2025; diagnostic 2026. 2022–2025 and 2026 have extensive previous project exposure and are not clean program-level holdouts.
Required gates: >=100 discovery and >=100 exploratory-forward trades; discovery PF >=1.00 at +2 bps; forward PF >=1.10 at +1 bp and >=1.05 at +2 bps; all forward years with >=5 trades PF >=1.00 at +1 bp; 4-week circular weekly-net-R bootstrap 95% lower bound >0 at +1 bp; child forward mean net R/trade improves versus matched long-only T+10 parent. Any failed gate means R278 = GAGAL. No post-result parameter rescue.

## Promotion boundary
Even a screen pass is not funded-ready. There is no complete FundedNext floating-equity/daily-loss/Quick Strike replay in this experiment; BID-only inputs cannot establish the real broker's short-side execution or funding costs. Treat this as strategy research only.

## Outputs
Store standalone runner, compact results JSON, final report and trade ledger output in the research branch. No GitHub Actions backtest workflow is created.
