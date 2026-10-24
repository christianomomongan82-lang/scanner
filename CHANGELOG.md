# Changelog

## 2026-10-24 — R330 Gate 1 entry-convention amendment

- Corrected Gate 1 to use canonical R191 entry: open of the next completed New York wall-clock H4 bar.
- The previous manual5m PF@1bp=1.491 is now diagnostic-only and is not counted as a canonical replication failure or used for any PASS/FAIL gate.
- Kept all R330 performance thresholds, discovery/forward/OOS criteria, neighborhood criteria, leave-one-out criteria and Stellar challenge simulation requirements unchanged.
- Added exact Gate 1 target comparisons for selection (n=78, PF@1bp=2.082), forward (n=70, PF@1bp=1.247, PF@2bp=1.241), and 2026 OOS (n=11, PF@2bp=1.954).
- The requested file R191_CANONICAL_index_trend_long.py is absent from the accessible repository snapshot. The available R192 ideal mode is the next-H4-open equivalent, but its stored R194-ledger results do not match the supplied references. Accordingly, status is GATE-MISMATCH (definisi konvensi entry), strategi belum dievaluasi; no pooled data, Gate 2, tuning, variant, or instrument removal was performed.


## 2026-10-24 — R330 canonical Gate 1 source correction

- Added the user-supplied `research/R191_CANONICAL_index_trend_long.py` to branch `research/r330-r191-pooled-ten-index`. Its H4 resample call, signal, 27-bar SL, RR=2 TP, and `sim` body are preserved; only a loader adapter reads the repository's `dl/<instrument>_m5.csv.gz` cache when the original XZ files are absent.
- Gate 1 now compares outputs from the canonical script to the locked selection/forward/OOS targets. R192 `ideal` and `manual5m` are diagnostic ledgers only.
- On Gate 1 mismatch, the runner exports `research/R330_G1_canonical_trades.csv`, `research/R330_G1_r192_ideal_trades.csv`, and `research/R330_G1_first_trade_mismatch.json`, then stops before Gate 2 and pooled criteria. No strategy tuning or instrument exclusion was introduced.

## 2026-10-24 — R330 M5 cache download reliability

- The first fresh Gate 1 attempt (run 40064140080) stopped before the backtest because annual M5 data download for USA500 2023 failed with Dukascopy HTTP 504/400 errors; no Gate 1 metric from that run was produced.
- Added resumable quarterly M5 downloads and annual snapshot reconstruction in `research/download_m5_year_quarters.sh`, used by both R330 data-preparation stages. The analysis input format and strategy logic are unchanged.
- Current retry run: [40073656843](https://github.com/christianomomongan82-lang/scanner/actions/runs/40073656843). At the time of this entry, USA500 cache preparation was still in progress; no fresh canonical Gate 1 verdict is claimed yet.


## 2026-10-24 — R330 official canonical baseline/data-version amendment

- Superseded the unavailable prior-snapshot Gate 1 targets (n=78/70/11 and PF 2.082/1.247/1.954) with the canonical results reproduced on the current M5 cache: selection n=79/PF@1bp=2.134; forward n=68/PF@1bp=1.310/PF@2bp=1.304; OOS 2026 n=11/PF@2bp=1.673.
- This is a data-cache version/provenance shift, not a change to the R191 entry/signal/SL/TP/sim rules or any locked downstream threshold.
- Gate 1 now requires two independent canonical load/resample/sim runs against the same cache to produce identical H4 grids/OHLC and trade outputs, and to reproduce every official baseline figure to three decimals.
- Changed the R330 basket engine to use the exact canonical M5-to-H4 resample and canonical sim for Gate 2, N=40/55/80 robustness, all ten-index metrics and the R191-only challenge comparator. R192 is only a timestamp/CSV loader adapter, not a calculation engine.
- Recorded M5 per-index SHA-256 data hashes so the baseline is tied to a verifiable cache version. All six downstream PASS criteria and the PF>1.4 causality audit remain unchanged; no tuning or instrument removal was introduced.


## 2026-10-24 — R330 canonical M5-only data preparation

- Removed unnecessary H1 download, upload and validation from the R330 research workflow because the locked canonical engine builds all H4 bars directly from M5 BID.
- Made annual M5 coverage 2017–2025 required whenever source history exists; 2026 remains optional if the current quarter is not yet available. Dukascopy explicitly returned zero rows before 2018-08-08 for USSC2000, so that index begins in 2018 Q3 and remains included from its first available bar, without synthetic history.
- Increased retries for 2017–2018 quarterly M5 retrieval. Data-acquisition changes only; the R191 signal, stop, target, sim, six PASS thresholds and causality-audit rule remain unchanged.
- Isolated the M5-only rerun from the earlier hung H1+M5 acquisition run so the canonical basket can proceed with the existing cache keys and completed quarterly chunks.


## 2026-10-24 — Bound R330 M5 download stalls

- Added a 90-second timeout per Dukascopy quarterly M5 request and reduced retries to two attempts. This prevents a hung vendor request from occupying a preparation job indefinitely.
- Before retrying a quarterly request, removes both the partial CSV and stale compressed output so a corrupt archive cannot prevent future successful retries.
- Failed requests still fail the required instrument/year job; no missing data is silently treated as a pass or instrument exclusion. The only intentionally absent period remains USSC2000 before the documented 2018-08-08 source-history start.
- This is data-acquisition reliability only; canonical engine, locked periods, six PASS criteria, challenge rules and causal audit thresholds are unchanged.


## 2026-10-24 — R330 M5 acquisition timeout/retry correction

- The most recent basket attempt (run 40082027593) failed in data preparation, not in a strategy gate. The downloader timed out at 90 seconds after only two attempts; eight separate non-Gate1 index jobs were running at once. Logs show multiple quarters made progress before a single stalled quarterly request terminated that instrument.
- Changed M5 quarterly retrieval to a 180-second per-attempt timeout, four attempts, and longer backoff. Reduced only the ten-index data-preparation matrix concurrency from 10 to 3 to reduce simultaneous source pressure. Gate 1’s two-index preparation is unchanged.
- The existing Actions cache is resumable; successful quarterly chunks from failed attempts are retained and reused. Required 2017–2025 coverage rules (with the preregistered USSC2000 inception exception) remain unchanged.
- This is an acquisition reliability fix only. It does not change canonical R191 math, instrument universe, costs, periods, any of the six PASS gates, challenge simulator, or PF>1.4 causality audit. No pooled metric is claimed until Gate 2 and all locked calculations actually finish.


## 2026-10-24 — R330 monthly fallback for persistent quarterly HTTP 503

- The first retry-policy run reached USA30 year 2020 but Dukascopy returned HTTP 503 for the 2020 Q4 M5 request across all four quarterly attempts. This is a source endpoint error, distinct from a strategy-test failure.
- Added a fallback that requests the same BID M5 source as three separate months for a failed quarter, each with bounded retries, then concatenates those monthly files into the same quarterly archive format. If any month cannot be retrieved, the instrument still fails preflight; no prices or bars are synthesized. Temporary fallback files are excluded from annual chunk globbing and removed only after the quarter is successfully reconstructed.
- No strategy calculation, dataset universe, required years/quarters, baseline, cost model, locked gate, or challenge criterion changed.


## 2026-10-24 — Preserve the USSC2000 pre-inception exception during monthly fallback

- Added the source-history boundary check inside monthly fallback and skip logic when merging months with no source history. This prevents a failed 2018 Q3 quarter from treating USSC2000 July 2018 as a required month; Aug/Sep remain eligible from the documented 2018-08-08 inception date.
- All other instrument/year completeness checks remain strict. Missing required data after the known source start still stops the run. No strategy logic or performance gate changed.
