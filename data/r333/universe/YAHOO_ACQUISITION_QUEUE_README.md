# R333 current-listing Yahoo acquisition queue

**Status:** source-acquisition queue only; not the final small-cap universe and not a trade list. No PnL is computed from this file.

- Source data: `current_idx_listed_roster.csv` on the same branch; Git blob SHA `943c4aba24ef097fd59d0781669321dd38d5f704`.
- Source endpoint: https://block.idx.id/primary/StockData/GetSecuritiesStock?code=&sector=&board=&start=0&length=2000
- Source response SHA-256: `92114ed2700e7b723b9d538de77009ac09561cff423fdda2c105088df066f6e9`; parsed response SHA-256: `db85c01ded27208bad3610d5dc1f3931dd3033bad1b03c84d4f6b53726896e82`.
- Frozen row count: **962 unique current listing codes**, preserving the source row order. Every Yahoo ticker is the current code plus `.JK`.
- Current listed shares and listing date are preserved for auditing only. Do **not** apply current shares retroactively to the 2016–2026 market-cap universe.
- **Survivorship warning:** no delisted-record set was successfully acquired. This queue excludes at least any delisted companies absent from the current roster and is therefore **survivorship-biased**. It cannot be treated as historical universe membership and cannot be used for an edge claim.
- All tickers are included for data coverage only; no selection, ranking, or removal is based on historical PnL. Some tickers may not resolve on Yahoo or may have a shorter history; failures must remain logged in each batch manifest.
- Collection contract: GitHub Actions only; yfinance daily from 2010-01-01 to provider current end, `auto_adjust=False`, `actions=True`, 5 total attempts/ticker, retry waits 30, 120, 600, 600 seconds; maximum 10 tickers per job batch.
- Batch ordering follows `source_row` in the official IDX snapshot. This ordering is for acquisition reproducibility only, not strategy ranking.

The locked R333 small-cap universe still requires historical listing/delisting membership, point-in-time shares and sectors, and the preregistered monthly market-cap/liquidity rules. That universe remains **not frozen**. Strategy gates and PnL remain **NOT_RUN**; alpha remains **NOT_TESTED**.
