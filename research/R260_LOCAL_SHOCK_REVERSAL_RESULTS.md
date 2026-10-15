# R260 — Final Local Backtest Verdict

**Verdict: GAGAL.** The single-hour shock-reversal hypothesis fails discovery, validation, forward, annual-consistency, bootstrap, and 2026 OOS gates. Parameters were not retuned.

## Where it ran and what data was used

The backtest was executed in the current local session/container, not GitHub Actions. Input OHLC data was downloaded from GitHub Actions artifact **11916174401**, `R258-multihorizon-momentum-audit.zip`, containing EURUSD H1 BID and ASK snapshots from 2017-01-01 00:00 UTC through 2026-10-13 23:00 UTC.

- BID: 85,170 valid rows, zero duplicates, zero invalid OHLC rows. SHA-256: `68d667ef6e84d4357207da86dc0ffd18453bbfa91837d0dd1349ac82bb6c47bf`
- ASK: 85,170 valid rows, zero duplicates, zero invalid OHLC rows. SHA-256: `8b9d3660213fae55bf0066c42fd093badc4a8092ddb2a0ca1672bbac5bcc7b91`
- Common valid quotes: 85,170; 582 hourly grid points missing/incomplete and left missing; zero negative open spreads.
- Spread in pips: median 0.40, 95th percentile 7.40, maximum 23.10.

## Locked rule

Use the 90th percentile of absolute completed BID candle body size in pips fit only on 2017–2020 (threshold = **12.90 pips**). Fade a qualifying candle: bearish body -> long next exact H1 open; bullish body -> short next exact H1 open. Stop at the prior shock candle's executable-side extreme; target 1R; hold up to six hours. One position at a time, actual BID/ASK execution, stop-first same-bar collision handling, stop-gap exits at open, no synthetic missing bars. Stress additional per-trade costs of 0, 0.5, 1 and 2 pips. No parameter tuning.

## Results

| Period | Trades | PF at +1 pip | Net pips at +1 pip | PF at +2 pips |
|---|---:|---:|---:|---:|
| Discovery 2017–2020 | 3,309 | 0.412 | -7,868.8 | 0.297 |
| Validation 2021 | 589 | 0.288 | -1,619.6 | 0.192 |
| Forward 2022–2025 | 3,633 | 0.438 | -8,654.5 | 0.322 |
| OOS 2026 to Oct 13 | 430 | 0.450 | -877.2 | 0.319 |

Forward frequency was 17.41 trades/week. High frequency did not help. Win rate was 26.1% in forward after the +1 pip stress. Each forward year failed PF >= 1.0 at +1 pip:

| Year | Trades | PF at +1 pip | Net pips at +1 pip |
|---|---:|---:|---:|
| 2022 | 1,406 | 0.488 | -3,205.1 |
| 2023 | 808 | 0.385 | -1,938.6 |
| 2024 | 508 | 0.500 | -890.5 |
| 2025 | 911 | 0.375 | -2,620.3 |

Four-week circular block bootstrap on forward weekly net pips after +1 pip: P(positive mean weekly net) = **0.0%**; 95% CI **[-49.24, -34.51] pips/week**.

## Gate verdict

Only the sample-size/frequency gates passed. Validation PF, discovery PF, forward PF at both cost stresses, annual stability, bootstrap, and OOS PF all failed. **Close this hypothesis; do not rescue it by tuning on forward/OOS.**

## Interpretation and caveats

The single-hour shock-fade hypothesis did not show an edge on this BID/ASK H1 snapshot. The research-wide strategy family was formed after earlier experiments were seen, so the 2026 window is not fully untouched across the entire project; any future apparent winner needs further external validation. This does not test R189. R189's required 2016–2025 M1 raw feed is not present in the available GitHub artifacts; the available EURUSD artifact is H1.
