# R332 — Preregistrasi terkunci: H4 multi-asset trend-following

Status: dikunci sebelum pembacaan hasil strategi. Branch dibuat dari main: research/r332-multi-asset-trend.
Tujuan: satu aturan trend-following H4 yang sama lintas kelas aset, tanpa tuning per instrumen. Kegagalan satu gate berarti REJECT; setelah REJECT dilarang varian, tuning, atau penghapusan aset.

## Universe kandidat, urutan tetap, dan provenance

| Order | Kelas | Dukascopy ID | Arah |
|---:|---|---|---|
| 1 | Indeks | usa500idxusd | LONG-only |
| 2 | Indeks | usatechidxusd | LONG-only |
| 3 | Logam mulia | xauusd | LONG + SHORT |
| 4 | Energi / Light Crude Oil | lightcmdusd | LONG + SHORT |
| 5 | Obligasi pemerintah / Euro Bund | bundtreur | LONG + SHORT |
| 6 | FX | eurusd | LONG + SHORT |
| 7 | FX | usdjpy | LONG + SHORT |
| 8 | FX | audusd | LONG + SHORT |
| 9 | Kripto | btcusd; eligible only if actual M5 data begins in 2017 or earlier | LONG + SHORT |

Public instrument-catalog provenance: usa500/usatech: https://www.dukascopy-node.app/instruments/idx_america ; XAUUSD: https://www.dukascopy-node.app/instrument/xauusd ; Light Crude: https://www.dukascopy-node.app/instrument/lightcmdusd ; Euro Bund: https://www.dukascopy-node.app/instrument/bundtreur ; EURUSD: https://www.dukascopy-node.app/instrument/eurusd ; USDJPY: https://www.dukascopy-node.app/instrument/usdjpy ; AUDUSD: https://www.dukascopy-node.app/instrument/audusd ; BTCUSD: https://www.dukascopy-node.app/instrument/btcusd .

Catalog eligibility is not accepted as proof of the downloaded cache coverage. Record actual first/last timestamps, row count, bytes and SHA-256 of every chosen BID M5 cache. Downloader is dukascopy-node 1.50.0, UTC offset 0. No alternative-source fallback. If required acquisition still fails by the second workflow attempt, STOP and report the exact instrument/date/failure stage; do not spend further time trying to bypass Dukascopy.

Use only daily close-to-close returns from discovery (2017–2021) for de-duplication. Consider candidates in the fixed order above. Drop the later candidate if abs(correlation) > 0.70 against any already selected candidate; if exactly 0.70, retain it. Require at least 250 overlapping daily returns for a correlation decision; otherwise hard-stop for data insufficiency. Freeze and record the final universe before calculation of any strategy PF, trade counts or forward/OOS metrics. After final universe lock, no instruments may be added or removed based on strategy results.

## Fixed strategy rule

- H4 bars are made from M5 BID by the unchanged R191 canonical loader/resampler: America/New_York index; 4h frequency, offset 1h, label left, closed left.
- LONG when close[i] > max(high[i-55:i]); SHORT when close[i] < min(low[i-55:i]).
- Entry = open[i+1].
- LONG SL = minimum low over the 27 bars ending at signal bar i, inclusive. SHORT SL = maximum high over the same 27 bars, inclusive.
- TP is entry plus direction times 2R. One open position per instrument. No time stop.
- Check SL before TP. If a bar opens through SL, fill at that bar's open; otherwise fill at SL. If SL and TP are both reached inside the same bar, SL wins.
- Indices usa500idxusd and usatechidxusd are LONG-only, a priori because of the equity premium hypothesis. Other final classes trade LONG and SHORT.
- For cost bps in {1,2,3}, net_R = gross_R - bps * 1e-4 * entry / risk. Primary evaluation cost is 2bp.
- Discovery: 2017-01-01 to 2022-01-01; forward: 2022-01-01 to 2026-01-01; OOS entry cohort: 2026-01-01 to the single common completed-source cutoff. Do not report OOS in progress or reuse another cutoff.

## Hard gates and binary criteria

Gate 1: run unchanged canonical R191 load+sim twice on the same cached M5 BID files. Both runs must be deterministic and match to 3 decimals: selection n=79, PF@1bp=2.134; forward n=68, PF@1bp=1.310 and PF@2bp=1.304; OOS 2026 n=11, PF@2bp=1.673. If the local cache version does not exactly match, report that cause and STOP before strategy basket metrics.

Gate 2: causal truncation consistency must pass for every instrument in the final universe, comparing signal and 27-bar stop at each completed prefix against calculations on the full H4 history. Any failure = STOP.

1. Pooled forward n >= 150 and PF@2bp >= 1.15.
2. Pooled discovery PF@2bp >= 1.00.
3. Worst of forward years 2022–2025 PF@2bp >= 0.80; 2022 must be included.
4. At least 3 classes other than the class with the most forward trades have forward PF@2bp > 1.00.
5. Neighborhood N=40/55/80 (M=27, RR=2) each has pooled forward PF@2bp >= 1.00.
6. Leave-one-CLASS-out pooled forward PF@2bp >= 1.05 for every class removed.
7. Stellar 2-Step simulation: +8% then +5%, DLL 5%, static MLL 10%, at least 5 distinct trading days per phase, up to 5 years for evaluation. Bootstrap quarterly blocks from 2022–2026, 10,000 synchronized paths, seed 332019, risk 0.5% and 1.0% per trade, aggregate open stop-risk cap 2%. At BOTH risks: pass both phases within 5 years >=65%, breach DLL/MLL combined <=25%, pass rate strictly greater than R191-only, and breach rate no greater than R191-only. Candidate and baseline use the exact same simulator.
8. If pooled discovery or forward PF@2bp > 1.4, independent causality audit must pass.

One criterion failing means REJECT. After REJECT, stop; no new variants, tuning, alternative threshold, or instrument removal.

## Required reporting

Save research/R332_results.md and research/R332_results.json. Include annual pooled 2017–2026 rows (n, PF@1/2/3bp, total net R@2bp), selected-universe provenance/checksums and correlation dedup decisions, by-class diagnostics, forward class correlation, maximum simultaneous positions/open risk, all gate verdicts, challenge simulation versus R191-only, and causality audit if required. Update PROJECT_STATE.md. Explicitly state that live commissions/spread and actual funded-account floating risk are unverified.