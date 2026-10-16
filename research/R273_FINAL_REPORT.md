# R273 — XAUUSD M5 aligned pullback continuation

**Verdict: GAGAL.** The locked 6-hour/12-hour direction-alignment mutation improved results relative to raw Module A, but both streams were materially negative before and after the preregistered additional cost. The independent 2026 segment was not opened.

## Parent lineage

- Parent R272-A raw six-bar continuation trigger and its swing stop / fixed 1.5R target.
- Parent R272 executable-side and manual-delay controls: T+10 minutes from signal-bar open (five minutes after signal close), no synthetic bars, skip broken intervening bars, and same-session 16:45 New York cutoff.
- Sole mutation: replace incompatible ER >= 0.45 router gate with sign agreement between 6-hour and 12-hour net moves. R272-B fade is excluded because it lost even at zero added cost.
- Exact R273 specification was committed before calculation: [preregistration](R273_ALIGNED_PULLBACK_CONTINUATION_PREREGISTRATION.md). The 2021–2025 data is exploratory and research-contaminated at the program level.

## Data

- Source: corrected raw-only GitHub artifact [12031270051](https://github.com/christianomomongan82-lang/scanner/actions/runs/38859918137), Dukascopy XAUUSD M5 BID/ASK. Collection workflow did not compute signals or PnL.
- 947,326 rows each side; all timestamps matched; zero duplicate timestamps; zero negative opening spreads; synthetic flat bars disabled; 572 gaps greater than five minutes preserved. Median opening spread $0.358/oz; p95 $1.117/oz.
- Historical calculation used 877,930 matched rows before 2026-01-01 UTC. The 2026 holdout was not used in feature/signal calculation.

## Outcomes at +$0.30/oz additional cost

| Stream | Period | Trades | Net R | PF | Mean R | Win rate |
|---|---|---:|---:|---:|---:|---:|
| Raw A ablation | 2016–2020 | 163 | -101.17 | 0.292 | -0.621 | 26.99% |
| Aligned child | 2016–2020 | 131 | -78.12 | 0.309 | -0.596 | 28.24% |
| Raw A ablation | 2021–2025 | 331 | -157.54 | 0.372 | -0.476 | 29.00% |
| Aligned child | 2021–2025 | 278 | -128.86 | 0.380 | -0.464 | 29.14% |

Even at zero additional cost, raw A/aligned child net R was -48.33/-35.46 in discovery and -92.08/-73.53 in validation. At +$0.50/oz the child was -106.56R in discovery and -165.74R in validation.

Four-week circular bootstrap (10,000 resamples, seed 2732026), primary cost +$0.30/oz:

- Discovery child weekly mean: -0.299R; 95% CI [-0.413, -0.189].
- Validation child weekly mean: -0.496R; 95% CI [-0.633, -0.360].

Raw A produced 972 trigger bars overall, 773 with 6h and 12h signs aligned and 199 not aligned. The child reduced validation loss by 28.68R versus raw A and retained 278/331 = 84.0% of baseline trades. This is a relative improvement, not an edge: both have materially negative expectancy.

## Locked gates

| Gate | Result |
|---|---|
| Discovery child >=50 trades and net R positive | **FAIL** — 131 trades, -78.12R |
| Discovery weekly bootstrap lower 95% bound >0 | **FAIL** — lower bound -0.413R/week |
| Validation child >=100 trades and net R positive | **FAIL** — 278 trades, -128.86R |
| Validation child positive at +$0.50/oz | **FAIL** — -165.74R |
| Validation child beats raw A and retains >=40% of baseline count | PASS — -128.86R vs -157.54R; retains 84.0% |

## Decision and next-generation learning

**R273 = GAGAL.** Do not open 2026, alter this child's alignment rule, or run a funded challenge replay. Directional alignment repairs the zero-trade incompatibility of R272-A and gives a relative improvement, but the underlying continuation trigger is still losing. This rejects this exact child and provides evidence against carrying the current R272-A setup as an edge-backed block. Do not combine it with the R272-B fade.

## Reproducibility note

The calculation used the local optimized mirror of the locked quote-side execution controls on the verified raw artifact and historical-only slice. The repository runner is stored separately and imports the R272 engine API; the result/report summarize the local run. The local trade ledgers were generated but their full row-level CSVs are not uploaded in this commit.