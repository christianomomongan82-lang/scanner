# R214 — Short H4 Compression-Channel Breakdown

**Final verdict: REJECT — no discovery-eligible candidate.**  
Workflow run: https://github.com/christianomomongan82-lang/scanner/actions/runs/38491992365  
Audit artifact: https://github.com/christianomomongan82-lang/scanner/actions/runs/38491992365/artifacts/11862133116

## Locked hypothesis

Short-only H4 breakdown: the completed H4 close must be below the previous 20-bar H4 low after the median range of the preceding 5 H4 bars contracts to <=0.6x the median range of the preceding 20 H4 bars. Stop is the highest high of the signal bar plus the previous 9 H4 bars; target is 2R. Entry is the first non-flat M5 BID open >=5 minutes after signal close and before the next H4 close. One active position per instrument.

The ten-index universe used cached Dukascopy BID H1/M5 data, complete UTC H4 bars only, M5 stop-first exits and gap-stop-at-open handling. The workflow's compilation, H4 boundary test, snapshot validation and causal-prefix checks passed. Costs are modeled at 1 and 2 price bps round-trip; these are not verified broker costs.

Discovery entries are 2017–2021; forward entries 2022–2025; OOS entries 2026 to common cutoff 2026-10-09 20:00 UTC. The locked discovery eligibility gate requires >=30 discovery closes and PF >=1.00 at 2 bps. No forward results are used to substitute a different asset.

## Results

| Instrument | Discovery closes | Discovery PF @ 2 bp | Forward closes | Forward PF @ 2 bp | OOS closes |
|---|---:|---:|---:|---:|---:|
| EU Stocks 50 | 12 | 0.3800 | 5 | 1.3059 | 0 |
| France 40 / CAC 40 | 8 | 0.0000 | 7 | 0.3260 | 1 |
| FTSE 100 | 4 | 0.6571 | 3 | 0.0000 | 0 |
| USA 100 Tech / Nasdaq 100 | 4 | 1.9535 | 1 | INF (one-sided sample) | 2 |
| US Small Cap 2000 | 4 | 1.9843 | 2 | INF (one-sided sample) | 2 |
| Australia 200 | 3 | 0.0000 | 2 | 0.0000 | 2 |
| Japan 200+ | 3 | 0.0000 | 2 | 0.0000 | 0 |
| Germany 40 / DAX | 2 | 1.9520 | 2 | 0.0000 | 1 |
| USA 30 / Dow Jones | 2 | 0.0000 | 2 | INF (one-sided sample) | 1 |
| USA 500 / S&P 500 | 2 | 0.0000 | 2 | 0.0000 | 2 |

## Conclusion

No index reached 30 discovery closes; the largest count was only 12, so **there is no eligible asset to carry into forward selection**. A few tiny samples show high or infinite PF because their loss denominator is zero; those results are not credible evidence of edge. The short-only compression breakdown is rejected for inadequate signal frequency and insufficient discovery evidence. It is not funded/live-ready.
