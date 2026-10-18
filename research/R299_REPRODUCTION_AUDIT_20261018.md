# R299 Local Reproduction Audit — 2026-10-18

**Verdict remains GAGAL.** The locked R299 method was replayed locally from the exact M5 source members. Its frozen threshold, event/trade counts, cost results and validation bootstrap match the existing final report. No rule or threshold was changed, and no 2022+ strategy PnL was calculated.

## Exact inputs

| Input | Original archive SHA-256 | Extracted member SHA-256 |
|---|---|---|
| USA500 M5 | `21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac` | `df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee` |
| USATECH M5 | `91c7d44b0487e98eeea021712528910475e626bf433220a007629f3005fc66ad` | `82b06c38f66cd1387097691baac1d45c9463b6540eea9dfe28a894d85e122f7c` |

Data are joined on exact timestamps, never row number or forward fill. The exclusive outcome cutoff remains 2022-01-01 UTC; later bars are removed before feature construction and performance calculations.

## Replay match

- 2016 calibration windows: **15,293**.
- Frozen absolute-return Q95: **0.4476037999%**.
- First qualifying daily events / completed trades: **704 / 704**; skipped events: **0**.
- Discovery 2017–2020, 2 bp round-trip cost: **541 trades, −65.080R, PF_R 0.792**, maximum closed drawdown **75.442R**.
- Validation 2021, 2 bp: **163 trades, −21.376R, PF_R 0.764**, maximum closed drawdown **28.916R**.
- Validation weekly bootstrap: 52 Monday-start weeks including zero-trade weeks; four-week circular blocks; 10,000 samples, seed 299; mean **−0.41107R/week**, 95% CI **[−0.95826, +0.12894]**.

Discovery and validation expectancy gates fail; the bootstrap lower confidence bound also fails the registered positive-bound gate. The defect is not a mismatch in the data cutoff or replayed headline math: the registered strategy has negative net expectancy.

## Reproduction

Runner: [r299_usatech_leads_usa500_30m.py](r299_usatech_leads_usa500_30m.py).

```bash
python r299_usatech_leads_usa500_30m.py --data-dir /path/to/extracted-members --output-dir r299_output
```

Requires pandas and NumPy. It checks SHA-256 hashes of both extracted gzip members and writes a trade ledger, event/skip audit, validation weekly series, annual summary, and JSON metrics.

## Disposition

**R299 remains GAGAL and closed.** Do not tune its threshold, direction, holding horizon, stop/target or costs on these windows. BID-only index quotes and modeled costs do not verify executable ASK fills or the provider's equity-aware DLL/MLL challenge path. A next-generation test must use a materially distinct mechanism and frozen rules; 2022–2025 remains program-contaminated.