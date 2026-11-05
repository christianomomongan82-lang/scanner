# R334 — USDHUF Data Availability Probe (2026-11-05)

## Status

The initial long-range acquisition attempt failed, but follow-up probes show that the failure does NOT mean USDHUF M5 history is generally unavailable. It is consistent with one or more empty subrequests occurring inside the long-range download. No strategy signals, returns, alpha statistics, PnL, or challenge metrics were calculated.

## Probe A — BID/ASK and timeframe smoke test

GitHub Actions run: https://github.com/christianomomongan82-lang/scanner/actions/runs/41970640017  
Artifact: R334-USDHUF-data-availability-probe (artifact ID 13389159207; SHA-256 aee61c3912c29c7f81e8c397adebe2ec2f2ce06a10a7bccd949c0475e3271833).

| Request | Result | Rows | Actual first UTC | Actual last UTC |
|---|---|---:|---|---|
| USDHUF M5 BID, 2025-01-06 to 2025-01-10 | PASS | 1,152 | 2025-01-06 00:00 | 2025-01-09 23:55 |
| USDHUF M5 ASK, same window | PASS | 1,152 | 2025-01-06 00:00 | 2025-01-09 23:55 |
| USDHUF M5 BID, 2007-03-13 to 2007-04-01 | CLI returned empty-data error after writing a partial file | 1,044 partial rows | 2007-03-13 05:00 | 2007-03-16 19:55 |
| USDHUF H1 BID, 2007-03-13 to 2007-04-01 | PASS | 424 | 2007-03-13 04:00 | 2007-03-30 19:00 |
| USDHUF H1 BID, 2025-01-06 to 2025-01-10 | PASS | 96 | 2025-01-06 00:00 | 2025-01-09 23:00 |

The 2025 M5 BID and ASK files have exactly 1,152 common timestamps, zero BID-only timestamps, and zero ASK-only timestamps. All five CSV samples have zero duplicate timestamps.

SHA-256:
- 2025 M5 BID: adca7f638481cf1e7b3f9ed911b35b99b01dd67774bd5e58e723a907776992ab
- 2025 M5 ASK: 1ba0284d14376886c16ceb133688ac63669111e30a6ff5685c5a946d29517feb
- 2007 M5 partial BID: a2f4458b3649a0fd0422d142290d1ef6395a48b00cf7831a3b227950aedc902b

## Probe B — early-history windows

GitHub Actions run: https://github.com/christianomomongan82-lang/scanner/actions/runs/41970834606  
Artifact: R334-USDHUF-M5-earliest-year-probe (artifact ID 13389850638; SHA-256 fccdd453644bf75d4e844bfccd56c782cd9bc031de68b0d75e7e527402ab9bf9).

| Request | Result | Rows | Actual first UTC | Actual last UTC |
|---|---|---:|---|---|
| USDHUF M5 BID, 2007-03-20 to 2007-03-23 | PASS | 864 | 2007-03-20 00:00 | 2007-03-22 23:55 |
| USDHUF M5 BID, 2008-01-07 to 2008-01-11 | PASS | 1,152 | 2008-01-07 00:00 | 2008-01-10 23:55 |
| USDHUF M5 BID, 2010-01-04 to 2010-01-08 | PASS | 1,152 | 2010-01-04 00:00 | 2010-01-07 23:55 |
| USDHUF M5 BID, 2012-01-02 to 2012-01-06 | PASS | 1,152 | 2012-01-02 00:00 | 2012-01-05 23:55 |
| USDHUF M5 BID, 2015-01-05 to 2015-01-09 | PASS | 990 | 2015-01-05 00:00 | 2015-01-08 20:55 |
| USDHUF M5 BID, 2020-01-06 to 2020-01-10 | PASS | 1,116 | 2020-01-06 00:00 | 2020-01-09 23:55 |

SHA-256:
- 2007-03-20 M5 BID: 5c5e99e5ffdce2ba4005bad7299ac1748e5e5f69b8d7ea5714dfe7f759d99db6
- 2008 M5 BID: ca44e1d16e4d83e6a6d772883603f8701ecd0c27775c4ecf9087c5ca30998ad6
- 2010 M5 BID: 8ffe17aca948336752b78ccb0c272da4aa2d647f40294071881d6fc241c3462f
- 2012 M5 BID: e403da5313be8b59cb13d993a5890d83496be776826be35fd9c7a04c934dbd7a
- 2015 M5 BID: d4a176d6e96a5226a2b19b991e9ae869d0f49531edea064b08965e10f6cbe218
- 2020 M5 BID: 17264f7c3946cffee123b836ca6b370a05a243ab10ea0a47fd99d7f7c7fcf87d

All six CSVs have zero duplicate timestamps.

## Interpretation

1. USDHUF M5 is available in 2007, not only in recent years: at least the windows 2007-03-13 through 2007-03-16 and 2007-03-20 through 2007-03-22 downloaded successfully.
2. The earlier long-range command returned an empty-data error after creating a valid partial CSV. The file therefore must not be treated as a complete 2007-03-13 through 2007-04-01 dataset.
3. Small M5 windows in 2008, 2010, 2012, 2015, 2020 and 2025 succeeded. The 2015 and 2020 probes return fewer than 1,152 rows; this is not automatically a data defect, because the windows may include market closures/holidays and must be audited against expected FX trading hours.
4. The 2025 M5 BID/ASK timestamps pair exactly in the tested window.
5. Catalog earliest-start dates are not a substitute for actual downloaded coverage. The final raw acquisition must preserve and report all gaps and partial requests.

## Next acquisition correction

The next raw-only collection should use --retry-on-empty together with --no-fail-after-retries (CLI short option -fr) so an empty internal subrequest does not abort the entire larger range. The collector must preserve missing intervals, report every skipped/empty subrequest, and audit completeness afterward. It must not synthesize bars, forward-fill prices, or silently call the resulting cache complete.

The official dukascopy-node documentation explains that empty responses can be retried and that --no-fail-after-retries can skip a remaining failed period while continuing. Source: https://www.dukascopy-node.app/errors-and-empty-data

**R334 remains a market-data eligibility audit only. No alpha or trading-strategy conclusion is authorized by these availability probes.**
