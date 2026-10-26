# R333 Data Amendment — GitHub Actions acquisition and survivor roster (2026-10-26)

## Authority and scope

This amendment clarifies execution of the locked R333 preregistration. The earlier browser-only Yahoo errors were not valid acquisition attempts under the user's corrected workflow. The sandbox must not access Yahoo directly. Yahoo data acquisition runs only inside GitHub Actions; cached data are then handed to the sandbox via a GitHub Actions artifact or committed CSV on the data branch.

The original R333 signal, exit, cost, timing, matched baselines, and G1–G11 criteria remain locked. This amendment does not permit calculating PnL using the four smoke-test tickers, selecting survivors by their trading result, or treating the current active-list roster as a historical point-in-time universe.

## Verified Yahoo smoke acquisition

GitHub Actions run [40309094513](https://github.com/christianomomongan82-lang/scanner/actions/runs/40309094513) succeeded from the Actions runner with *yfinance==1.7.0*, Python 3.12.15, interval *1d*, start *2010-01-01*, end omitted (provider current end), *auto_adjust=False*, *actions=True*, *repair=False*, and *keepna=True*. All four requested tickers succeeded on attempt 1. It committed four CSV files plus a manifest to the data branch. See *data/r333/manifests/latest.json* on *data/r333-idx-daily-yahoo*.

The raw cache and manifest are preserved exactly as acquired. Invalid/blank OHLC rows are not filled, repaired, or silently dropped. The data-quality counts and SHA-256 hashes appear in *R333_results.md* / *R333_results.json*.

## Official IDX listing/delisting audit

Actions metadata run [40309248358](https://github.com/christianomomongan82-lang/scanner/actions/runs/40309248358) fetched a current listed-securities payload from *block.idx.id*, yielding 962 rows / 962 unique codes. This is a current-listing snapshot, not point-in-time historical membership.

Delisted metadata has **not** been successfully fetched:
- *https://www.idx.co.id/primary/ListingActivity/GetDelisting?start=0&length=2000*: three attempts returned HTTP 403 Cloudflare challenge HTML (last response begins below).

    HTTP 403: <!DOCTYPE html><html lang="en-US"><head><title>Just a moment...</title><meta http-equiv="Content-Type" content="text/html; charset=UTF-8">

- *https://block.idx.id/primary/ListingActivity/GetDelisting?start=0&length=2000*: three attempts returned HTTP 404 with exact body below.

    HTTP 404: {"Message":"No HTTP resource was found that matches the request URI 'http://localhost:8000/api/ListingActivity/GetDelisting?length=2000&start=0'."}

- *https://www.idx.co.id/id/perusahaan-tercatat/aktivitas-pencatatan*: three attempts returned HTTP 403 Cloudflare challenge HTML.
- The page *https://block.idx.id/id/perusahaan-tercatat/aktivitas-pencatatan* loaded (HTTP 200), and a 15-JavaScript frontend scan [40309624911](https://github.com/christianomomongan82-lang/scanner/actions/runs/40309624911) found the page's documented data route string */primary/ListingActivity/GetDelisting* and public delisted-company report routes. Those strings are endpoint-discovery evidence only; they are not a delisted record set.

## Next authorized operation

Acquire raw daily history for the deterministic current-listing queue through GitHub Actions only, with at most 10 tickers per batch, *auto_adjust=False*, *actions=True*, five total attempts per ticker, and retry waits of 30, 120, 600 and 600 seconds. Commit each batch CSV and manifest to the data branch. This larger survivor-only cache is for coverage and feasibility audit; it does not resolve point-in-time market cap/shares/sectors or delisted membership.

## Verdict

*DATA_INADEQUATE*; alpha *NOT_TESTED*. No strategy PnL has been calculated. Every survivor-only summary must be labeled *survivorship-biased*; no edge claim is permitted without a separately justified and measured bias correction. Live broker fees, slippage, spread/queue and ARA/ARB fills remain unverified in a real account.
