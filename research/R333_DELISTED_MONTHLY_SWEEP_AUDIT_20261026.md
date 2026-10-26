# R333 — Audit Lengkap Endpoint Bulanan Delisting IDX (2026-10-26)

## Verdict sumber delisting

**BISA — untuk laporan bulanan resmi yang diterbitkan dalam jendela 2010-01 sampai 2026-10.** Ini tidak mengklaim riwayat sebelum 2010 atau bahwa seluruh harga harian saham delisted tersedia di Yahoo.

Run GitHub Actions: [40342501539](https://github.com/christianomomongan82-lang/scanner/actions/runs/40342501539)  
Commit data branch: [3cd913264572242b7d71e4104e7f32e540ba3972](https://github.com/christianomomongan82-lang/scanner/commit/3cd913264572242b7d71e4104e7f32e540ba3972) on `data/r333-idx-daily-yahoo`.

The documented official IDX monthly report page's frontend chunk disclosed this endpoint:

`https://block.idx.id/primary/DigitalStatistic/GetApiDataPaginated?urlName=LINK_DELISTING&periodYear={year}&periodMonth={month}&periodType=monthly&isPrint=False&cumulative=false&pageSize=2000&pageNumber={page}&orderBy=`

The route was discovered from the official IDX page and JavaScript chunk, not guessed. No Cloudflare challenge was bypassed, no fallback source was used, and no private endpoint was used.

## Full-month coverage result

| Check | Result |
|---|---:|
| Requested coverage | 2010-01 through 2026-10 |
| Expected months | 202 |
| Months returned HTTP 200 with valid JSON | **202/202** |
| Failed, missing or pagination-inconsistent months | **0** |
| Raw report rows before deduplication | 65 |
| Deduplicated event rows | **65** |
| Unique ticker codes in delisted events | **65** |
| Per-month `data` row count matching `meta.totalItems` | **202/202** |
| Schema errors for required fields `code`, `issuerName`, `ListingDate`, `DeListingDate` | 0 |
| Pages required | 1 for each month; each reported total was below page size 2,000 |
| Strategy calculation/PnL | **NOT RUN** |

The automated checks established that every month in the requested window returned a valid report, that each response's row count matched its own `meta.totalItems`, and that all returned event rows had the required fields. This is substantially stronger than the original three spot probes.

## The three requested probes, cross-checked against the sweep

| Report month | HTTP | `data` rows | `meta.totalItems` | Example reported events |
|---|---:|---:|---:|---|
| 2010-01 | 200 | 1 | 1 | BATI, delisting 04 January 2010 |
| 2020-01 | 200 | 2 | 2 | ITTG, 23 January 2020; BORN, 20 January 2020 |
| 2026-10 | 200 | 0 | 0 | No delisting rows in this month's report |

A zero-row report for 2026-10 is a valid empty month in the source, not evidence that IDX has no delisted companies.

## Saved outputs and integrity references

- Latest sweep manifest: [idx-delisted-monthly-sweep-latest.json](https://github.com/christianomomongan82-lang/scanner/blob/data/r333-idx-daily-yahoo/data/r333/manifests/idx-delisted-monthly-sweep-latest.json). Git blob SHA: `89c04ea3263805d33dd3e25391f8235b49d0f043`.
- Raw monthly JSON snapshots: [delisted_monthly_sweep/](https://github.com/christianomomongan82-lang/scanner/tree/data/r333-idx-daily-yahoo/data/r333/idx_metadata/delisted_monthly_sweep).
- Consolidated event CSV: [delisted_events_2010-01_to_2026-10.csv](https://github.com/christianomomongan82-lang/scanner/blob/data/r333-idx-daily-yahoo/data/r333/idx_metadata/delisted_monthly_sweep/delisted_events_2010-01_to_2026-10.csv). Rows including header: 66; SHA-256: `0ccfb9ae8a5eacfbbe3e4936244a9c85df8cb737a227730baa47dda75b1fa6b3`; Git blob SHA: `d07db7050349971832166f12623fe847b9f68c8b`.
- Monthly audit CSV: [monthly_coverage_audit.csv](https://github.com/christianomomongan82-lang/scanner/blob/data/r333-idx-daily-yahoo/data/r333/idx_metadata/delisted_monthly_sweep/monthly_coverage_audit.csv). Rows including header: 203; SHA-256: `dcad3c5f9887238c249462ebe2f9d358b5aea65051123b207d38d1e524abc6c2`; Git blob SHA: `27208f9736ee2ef8071e9c233eec69b986629e9c`.

## Important boundary: this does not make the R333 backtest data-ready

The official report solves one data question: historical delisting event records are now available for every published month in this tested window. It does **not** by itself supply daily OHLCV for the 65 delisted names, and it does not validate the completeness of Yahoo price history for tickers returning HTTP 404. The active roster has current shares outstanding, not monthly point-in-time share counts for all years. Point-in-time sectors also remain unverified.

The wider Yahoo cache audit remains:
- 921/962 requested ticker CSVs acquired; 41 tickers returned HTTP 404.
- 1,124 invalid/blank OHLC rows across the 921 acquired stock CSVs; no repair was made.
- Corporate-action/split adjustment semantics remain not independently verified.
- Executable bid-ask spread/queue fills are not present in Yahoo daily OHLCV.

Therefore, **official delisting-event coverage = PASS for 2010-01–2026-10**, but **R333 overall data gate = DATA_INADEQUATE**. The historical small-cap universe is not frozen, Stage 1–2 stay blocked, and alpha remains NOT_TESTED. Do not describe this data-gate failure as evidence that there is no edge.
