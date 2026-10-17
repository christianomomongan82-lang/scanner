# R283 — US Index Cash-Open Gap Fade

**Verdict: GAGAL.** The locked fade hypothesis is negative in both discovery and validation. Forward 2022–2025 was deliberately not scored after earlier gates failed.

## Locked method
- Universe: USA500, USATECH, USA30, USSC2000; cached M5 BID-only OHLC.
- Gap: 09:30 ET open versus prior RTH close (15:55 bar close).
- Per-instrument Q80 absolute percentage gap, fit only on 2017–2020.
- Entry 09:40 ET to model a 10-minute phone delay; fade the gap.
- Target prior RTH close; stop 0.75× original gap; stop-first on same-bar conflict; exit by 16:00 ET; no overnight.
- Modeled round-trip cost 1/2/4 bps of index notional. Primary screen uses 2 bps.

## Results at modeled 2 bps

| Segment | Trades | PF | Net R | Max DD R | Mean R/trade |
|---|---:|---:|---:|---:|---:|
| Discovery 2017–2020 | 709 | 0.748 | -77.900 | 82.564 | -0.110 |
| Validation 2021 | 163 | 0.599 | -34.830 | 36.837 | -0.214 |
| Forward 2022–2025 | Not scored | — | — | — | — |

Discovery and validation trade-count gates passed, but expectancy gates failed. At 1/2/4 bps, discovery PF was 0.771/0.748/0.705 and validation PF was 0.618/0.599/0.563. Do not tune this exact specification.

## Per-instrument PF / Net R at 2 bps

| Instrument | Discovery trades | Discovery PF | Discovery net R | Validation trades | Validation PF | Validation net R |
|---|---:|---:|---:|---:|---:|---:|
| USA500 | 198 | 0.689 | -27.731 | 43 | 0.462 | -12.918 |
| USATECH | 197 | 0.706 | -26.869 | 48 | 1.003 | +0.065 |
| USA30 | 197 | 0.829 | -13.916 | 30 | 0.287 | -12.481 |
| USSC2000 | 117 | 0.803 | -9.383 | 42 | 0.597 | -9.496 |

## Data / execution limitations
- All four feeds are BID-only; actual spread is unavailable and costs are modeled.
- Archive provenance is not independently verified in this run.
- 2021 and 2022–2025 are contaminated at program level; 2021 was used only as a historical gate.
- No actual CFD point value, spread, commission, slippage, swaps, correlated-portfolio limits, or FundedNext daily/max-loss equity-path replay was modeled.
- Data SHA-256: USA500 `21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac`; USATECH `91c7d44b0487e98eeea021712528910475e626bf433220a007629f3005fc66ad`; USA30 `53a54804f0584c69d52f41af08534e00effea66e7cc31872ae0438e7907e0fe6`; USSC2000 `52216f5623a974dfaa0fb19e3cb28e2b2db589f1c07cef5cc8e5e2b383638872`.

**Decision:** close R283 as failed; no alpha block retained, no forward segment opened, no GitHub Actions workflow launched.
