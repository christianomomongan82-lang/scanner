# R333 current IDX listed roster snapshot (pre-PnL)

- Source URL: https://block.idx.id/primary/StockData/GetSecuritiesStock?code=&sector=&board=&start=0&length=2000
- Display/source page: https://block.idx.id/id/data-pasar/data-saham/daftar-saham/
- Official domain: `block.idx.id` (IDX/BEI public domain).
- Retrieved by GitHub Actions run: 40308193067 (source-only; no PnL).
- Snapshot time (UTC): 2026-10-26T10:32:27Z to 2026-10-26T10:34:30Z.
- Original response JSON SHA-256: `92114ed2700e7b723b9d538de77009ac09561cff423fdda2c105088df066f6e9` (`listed_securities_block.json`). Parsed JSON SHA-256: `db85c01ded27208bad3610d5dc1f3931dd3033bad1b03c84d4f6b53726896e82` (`listed_securities_block_parsed.json`).
- Source reported rows: 962; unique ticker codes: 962; duplicate ticker codes: 0; rows with missing code/listing date/invalid listed shares: 0.
- CSV is sorted by official endpoint source order as an archived roster snapshot, not by PnL or strategy metric.
- This is **not the locked historical small-cap universe** and not a final trade list. It reports current listing metadata only: `Code`, `Name`, `ListingDate`, `Shares`, `ListingBoard`.
- It does not establish the membership of IDX at each historical month, point-in-time shares outstanding/sectors, 60-day median traded value, or complete delisted coverage. Do not use current `Shares` retroactively.
- Until those requirements are satisfied, R333 remains `DATA_INADEQUATE`, alpha `NOT_TESTED`. Any survivor-only historic report must say `survivorship-biased`; no edge claim without an explicit, defensible correction.
- Raw source file: `data/r333/idx_metadata/listed_securities_block.json`
- Parsed source file: `data/r333/idx_metadata/listed_securities_block_parsed.json`
