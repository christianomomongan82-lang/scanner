# R334 — Acquisition Operations Log (2026-11-06)

This log records acquisition-pipeline failures and recovery. It does not amend the locked R334 preregistration and contains no market-performance conclusions.

## Confirmed failure: v2 whole-job cancellation

- Workflow run: https://github.com/christianomomongan82-lang/scanner/actions/runs/41971168353
- Conclusion: `cancelled`, after approximately 350 minutes.
- The job was designed to process all 160 annual symbol/side segments in one runner and only merge/upload after the entire loop. It had no intermediate persistence.
- Before cancellation it completed USDHUF M5 BID:
  - 2007: 70,583 rows; about 90m39s
  - 2008: 87,779 rows; about 114m06s
  - 2009: 87,418 rows; about 113m47s
- 2010 was interrupted. The 245,780 rows above existed only on the temporary runner and were lost because the job never reached its merge/upload stage. No artifact was produced.

## v3 recovery design

Workflow: `.github/workflows/r334_fx_market_quotes_v3.yml` on `main`.

- Each run handles one annual symbol/side segment.
- Each completed attempt writes a compressed CSV (when rows exist), compressed log, and JSON status to `data/r334-fx-market-quotes` before moving on.
- The next run is dispatched through GitHub Actions after each checkpoint. The final artifact is built only when all 160 segments have a terminal status.
- Data are not filled, forward-filled, or synthetically created. Empty/unavailable periods remain gaps and are retained in the logs/status for later completeness checks.
- The first implementation attempt exposed an unsupported CLI option (`--rate-limit-retries`); that option was removed. Runs 42098409283 and 42098450805 recorded the failed attempts as `NO_DATA_RETRY` rather than silently treating them as data.
- Run 42098498482 was started with the intermediate CLI configuration and is the third attempt for USDHUF BID 2007. It must not be confused with the latest workflow definition.
- Latest workflow commit: `268e7b7dc3a4281604bbcb9bd21630fc33fd000c`. It removes retry-on-empty (`-re`), retains failed-request retries and skip-after-retries (`-r 3 -fr`), and reduces the batch pause from 4,000ms to 2,000ms. This avoids repeatedly retrying normal empty subperiods; any missing in-session bars still need to be detected by the later gap audit.

## Current data status at log creation

- Only the initial USDHUF BID 2007 status/log checkpoints from failed CLI invocations had been committed.
- No complete annual CSV checkpoint was yet verified on the data branch.
- No combined BID/ASK dataset or R334 descriptive statistics had been produced.
- No alpha, strategy, PnL, or funded-challenge conclusions are authorized by this acquisition log.

## Integrity follow-up

After collection, verify each segment's CSV header, monotonic timestamps, duplicates, BID/ASK timestamp pairing, annual coverage, and M5 gaps during expected FX trading hours. A segment marked `DATA_WITH_POSSIBLE_GAPS` means only that rows were retrieved; it is not a claim of complete coverage.
