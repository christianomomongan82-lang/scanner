# R333 IDX roster / delisting audit — 2026-10-26

**Result:** current active-roster acquisition succeeded; delisted-history acquisition failed. Overall R333 remains DATA_INADEQUATE, alpha NOT_TESTED; no PnL.

## Run ledger

| Run | Purpose | GHA conclusion | What it actually proves |
|---|---|---|---|
| [40309248358](https://github.com/christianomomongan82-lang/scanner/actions/runs/40309248358) | official IDX roster/listing activity metadata source-only | SUCCESS | A current listed-securities JSON was validated and committed. It does not mean delisting records were acquired. |
| [40309624911](https://github.com/christianomomongan82-lang/scanner/actions/runs/40309624911) | official IDX frontend asset inspection only | SUCCESS | 15/15 JavaScript assets were fetched with HTTP 200 and committed; frontend route strings were inspected, no trading calculations. |
| [40309094513](https://github.com/christianomomongan82-lang/scanner/actions/runs/40309094513) | Yahoo daily OHLCV smoke collection via yfinance | SUCCESS | Four smoke tickers were acquired through the Actions runner and committed. Not a small-cap universe. |

## Official current roster

Source endpoint: *https://block.idx.id/primary/StockData/GetSecuritiesStock?code=&sector=&board=&start=0&length=2000* — HTTP 200; raw bytes 131,862; SHA-256 *92114ed2700e7b723b9d538de77009ac09561cff423fdda2c105088df066f6e9*. Parsed JSON SHA-256: *db85c01ded27208bad3610d5dc1f3931dd3033bad1b03c84d4f6b53726896e82*. The response reported 962 rows and 962 unique codes; the committed CSV *data/r333/universe/current_idx_listed_roster.csv* has a header plus 962 rows. It includes code, name, listing date, currently listed shares and listing board.

Current roster file Git blob SHA: *943c4aba24ef097fd59d0781669321dd38d5f704*. Raw page *data/r333/idx_metadata/stock_list_page.html*: 259,392 bytes, SHA-256 *dd625a89c43584976a9fc217426342d09a9b584798008ab12a54b5d9efb287b9*.

Attempts to the main *www.idx.co.id* current-roster endpoints:
- *https://www.idx.co.id/primary/StockData/GetSecuritiesStock?code=&sector=&board=&start=0&length=2000*: 3/3 HTTP 403 Cloudflare, final response body size 6,129 bytes.
- *https://www.idx.co.id/umbraco/Surface/StockData/GetSecuritiesStock?code=&sector=&board=&start=0&length=2000*: 3/3 HTTP 403 Cloudflare, final response body size 6,153 bytes.
- The documented *block.idx.id* endpoint succeeded and was saved as a source snapshot; no attempt was made to bypass the Cloudflare challenge.

## Delisting endpoints: exact latest errors

The source-only collector made three attempts for each endpoint, following its configured 10-second then 30-second retry sleeps.

1. *https://www.idx.co.id/primary/ListingActivity/GetDelisting?start=0&length=2000* — **3/3 HTTP 403**. Last logged error begins below.

    HTTP 403: <!DOCTYPE html><html lang="en-US"><head><title>Just a moment...</title><meta http-equiv="Content-Type" content="text/html; charset=UTF-8"><meta http-equiv="X-UA-Compatible" content="IE=Edge"><meta name="robots" content="noindex,nofollow">

    Last captured body: 5,979 bytes, content type *text/html; charset=UTF-8*.

2. *https://block.idx.id/primary/ListingActivity/GetDelisting?start=0&length=2000* — **3/3 HTTP 404**, body 147 bytes, JSON content type. Exact response:

    HTTP 404: {"Message":"No HTTP resource was found that matches the request URI 'http://localhost:8000/api/ListingActivity/GetDelisting?length=2000&start=0'."}

3. *https://www.idx.co.id/id/perusahaan-tercatat/aktivitas-pencatatan* — **3/3 HTTP 403** Cloudflare. Last captured body: 5,888 bytes, content type *text/html; charset=UTF-8*.

4. *https://block.idx.id/id/perusahaan-tercatat/aktivitas-pencatatan* — HTTP 200, 146,471 bytes, SHA-256 *bef90e211f4ac562334267ba0054740010b786bda55dd48980073c0cd703223d*. This HTML loads the public listing activity page but does not itself contain a tabular delisted roster.

## Frontend asset scan: exact finding

Run [40309624911](https://github.com/christianomomongan82-lang/scanner/actions/runs/40309624911) fetched **15/15** JavaScript assets; all reported HTTP 200. Manifest: *data/r333/manifests/idx-frontend-assets-latest.json*; artifact ZIP SHA-256 *994cf521bc3e4321f0e552271026068f618a7df55ff717fb578578bc057fb198*.

- *data/r333/idx_metadata/frontend_assets/1061432.js* contains *data-table:"/primary/ListingActivity/GetDelisting"* for the Delisting tab's data loader.
- *.../168d8db.js* contains public URLs under */en/market-data/statistical-reports/digital-statistic/monthly/corporate-action-of-listed-companies/delisted-company* and related quarterly routes.
- These are route strings only. The scan does not establish that a delisted response was fetched, nor did the raw manifest select any *selected_delistings* payload. The metadata manifest's *selected_delistings* is *null*.

## Data status and implication for universe

- Verified current listing snapshot: **962 codes**.
- Verified delisted history: **0 records successfully acquired** (this means none were retrieved, not that the exchange has no delisted stocks).
- Point-in-time monthly roster / historical shares outstanding / sector classifications: **not verified**.
- The current roster queue is therefore **survivorship-biased**. It may be used to acquire daily Yahoo bars for coverage diagnostics only; it is not the final historical small-cap universe and cannot pass the original R333 data gate.
- Do not calculate PnL until the pre-registered universe and required point-in-time fields are valid. If future descriptive calculations are intentionally run on current survivors, label every output *survivorship-biased* and do not claim edge without explicit measured correction.
- Broker live fee, slippage, actual bid/ask spread/queue and ARA/ARB execution remain unverified in a real account.
