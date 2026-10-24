# R330 — CANONICAL GATE 1 PASS (PREFLIGHT ONLY)

**Gate 1: PASS. The final ten-index basket verdict is not yet available.**

The canonical R191 script was run twice using the same repository M5 BID cache. The H4 labels/OHLC and trade outputs were identical on both runs for USA500 and USATECH, and the current-cache baseline matches to three decimals.

| Period | n | PF@1bp | PF@2bp | PF@3bp |
|---|---:|---:|---:|---:|
| Selection 2017–2021 | 79 | 2.134 | 2.121 | 2.109 |
| Forward 2022–2025 | 68 | 1.310 | 1.304 | 1.298 |
| OOS 2026 | 11 | 1.683 | 1.673 | 1.664 |

The former targets (n=78/70/11, PF 2.082/1.247/1.954) came from an unavailable earlier data snapshot. The baseline shifted with the cache version, not with the R191 entry, signal, SL, TP, or simulation rules. No thresholds were changed.

## Data identity

- USA500 M5 BID SHA-256: `75d3c8dd64ba4647af7f5376ac219010dc2c65f46beb296f978257e770c90087` (11,805,722 bytes; 826,522 rows).
- USATECH M5 BID SHA-256: `b8f3b267e187669890f455486100133a29a78b5b5fcb4824c67d2b8f3acb8755` (13,248,558 bytes; 826,429 rows).
- Data spans: 2016-01-04T00:00:00Z to 2026-10-23T20:10:00Z UTC for both sources.
- Basket engine remains the provided canonical R191 M5-to-H4 resample and one-position sim. The basket uses every one of the ten indices from its first available source bar; no R192 numerical engine, tuning, variant, or instrument removal is permitted.

## What remains

The M5-only data-preparation run is active: [GitHub Actions run 40081030101](https://github.com/christianomomongan82-lang/scanner/actions/runs/40081030101). Gate 2, six locked PASS criteria, R191-only challenge-comparator sizing, and the PF>1.4 causal audit have **not** been calculated in this checkpoint. This report is not a PASS/REJECT decision on the basket strategy.
