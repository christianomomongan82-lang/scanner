# R299 — USATECH 30-Minute Lead / USA500 30-Minute Follow-Through

**Verdict: GAGAL**

The preregistration and timestamp-key data-quality amendment were committed before candidate PnL. This screen uses 2016 only to calibrate Q95, 2017–2020 for discovery, and 2021 for validation. Every 2022+ row was excluded before calibration, event construction and outcomes. Validation 2021 is research-contaminated, so a pass would not prove program-level alpha.

## Source and data quality

- USA500 ZIP SHA-256: `21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac`
- USATECH ZIP SHA-256: `91c7d44b0487e98eeea021712528910475e626bf433220a007629f3005fc66ad`
- Raw rows: USA500 886,206; USATECH 886,039. Rows included through 2021: USA500 469,112; USATECH 468,943. Excluded 2022+ before signal construction: USA500 417,094; USATECH 417,096.
- Shared timestamps through cutoff: 468,937; USA500-only timestamps: 175; USATECH-only timestamps: 6. All event and trade alignment uses exact timestamp keys; no row-number pairing or forward-fill.
- UTC coverage used: USA500 2016-01-04T00:00:00+00:00 to 2021-12-31T21:10:00+00:00; USATECH 2016-01-04T00:00:00+00:00 to 2021-12-31T21:10:00+00:00.
- Active rows USA500 / USATECH: 352,205 / 352,938. Eligible calibration windows: 15,293; frozen absolute-return Q95: 0.4476037999%.
- First threshold events, max one per NY date: 704; completed trades: 704; skip reasons: `{}`.

## Results

Costs are modeled round-trip basis points of USA500 entry price. Source archives are BID-only; short fills and all actual ask-side spread/slippage remain unverified.

| Period | Cost | Trades | Net R | PF_R | Win rate | Max closed DD (R) | Long / short | Stop / target / time |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Discovery 2017–2020 | 1 bp | 541 | -28.268 | 0.903 | 43.3% | 41.663 | 236 / 305 | 253 / 154 / 134 |
| Discovery 2017–2020 | 2 bp | 541 | -65.080 | 0.792 | 41.2% | 75.442 | 236 / 305 | 253 / 154 / 134 |
| Discovery 2017–2020 | 4 bp | 541 | -138.704 | 0.612 | 39.9% | 143.870 | 236 / 305 | 253 / 154 / 134 |
| Validation 2021 | 1 bp | 163 | -9.095 | 0.891 | 42.9% | 18.827 | 79 / 84 | 69 / 41 / 53 |
| Validation 2021 | 2 bp | 163 | -21.376 | 0.764 | 41.1% | 28.916 | 79 / 84 | 69 / 41 / 53 |
| Validation 2021 | 4 bp | 163 | -45.936 | 0.565 | 37.4% | 51.678 | 79 / 84 | 69 / 41 / 53 |

## Annual results

| Year | Split | Cost bp | Trades | Net R | PF_R |
|---:|---|---:|---:|---:|---:|
| 2017 | discovery | 1 | 51 | -13.867 | 0.561 |
| 2017 | discovery | 2 | 51 | -19.655 | 0.446 |
| 2017 | discovery | 4 | 51 | -31.231 | 0.288 |
| 2018 | discovery | 1 | 161 | +0.949 | 1.011 |
| 2018 | discovery | 2 | 161 | -10.027 | 0.889 |
| 2018 | discovery | 4 | 161 | -31.977 | 0.688 |
| 2019 | discovery | 1 | 124 | +2.823 | 1.045 |
| 2019 | discovery | 2 | 124 | -6.168 | 0.908 |
| 2019 | discovery | 4 | 124 | -24.150 | 0.687 |
| 2020 | discovery | 1 | 205 | -18.173 | 0.840 |
| 2020 | discovery | 2 | 205 | -29.231 | 0.758 |
| 2020 | discovery | 4 | 205 | -51.347 | 0.618 |
| 2021 | validation | 1 | 163 | -9.095 | 0.891 |
| 2021 | validation | 2 | 163 | -21.376 | 0.764 |
| 2021 | validation | 4 | 163 | -45.936 | 0.565 |

## Validation quarterly results at 2 bp

| Quarter | Trades | Net R | PF_R |
|---:|---:|---:|---:|
| Q1 | 50 | +1.971 | 1.084 |
| Q2 | 34 | -5.509 | 0.734 |
| Q3 | 34 | -3.678 | 0.800 |
| Q4 | 45 | -14.159 | 0.495 |

## Validation 2021 weekly bootstrap at 2 bp

- 52 Monday-start weeks, including zero-trade weeks; trade weeks: 51.
- Mean weekly net R: -0.41107; circular four-week bootstrap 95% CI [-0.95826, +0.12894] R/week; 10,000 resamples; seed 299.

## Locked gates

| Gate | Result |
|---|---|
| calibration at least 1000 windows | PASS |
| calibration q95 finite positive | PASS |
| discovery min 75 trades | PASS |
| discovery positive net R at 2bp | FAIL |
| discovery PF R at least 1 05 at 2bp | FAIL |
| discovery at least 3 of 4 positive years at 2bp | FAIL |
| discovery positive net R at 4bp | FAIL |
| discovery PF R at least 0 90 at 4bp | FAIL |
| validation min 100 trades | PASS |
| validation positive net R at 2bp | FAIL |
| validation PF R at least 1 05 at 2bp | FAIL |
| validation at least 3 of 4 positive quarters at 2bp | FAIL |
| validation bootstrap CI lower gt zero at 2bp | FAIL |
| validation positive net R at 4bp | FAIL |
| validation PF R at least 0 90 at 4bp | FAIL |

## Decision

No candidate promoted; do not tune or reverse if any locked gate fails.

No 2022–2026 candidate PnL was calculated. These BID-only price series and modeled costs do not verify broker-side fills, actual spread, slippage, commissions, swaps, contract point value, margin or FundedNext equity/DLL/MLL. No funded challenge replay was performed.

## Independent local reproduction — 2026-10-18

The report's frozen Q95, selected/completed counts, 1/2/4 bp discovery and validation aggregates, exit counts and 2021 weekly bootstrap were independently reproduced from the exact source-member SHA-256 values in [R299_REPRODUCTION_AUDIT_20261018.md](R299_REPRODUCTION_AUDIT_20261018.md). The runner and artifact entry point are now indexed in [R299_INDEX.md](R299_INDEX.md). The verdict remains **GAGAL**; no method changes or 2022+ PnL were introduced by this audit.