# R303 — EURUSD Spread-Shock Reversion: Final Report

**Binary verdict: GAGAL.** The locked candidate is rejected; no threshold, direction, cost, or exit tuning was used after outcomes.

## Primary result (T+5 fade, paired BID/ASK + 1 pip incremental round-trip cost)

| Period | Closed trades | Net R | PF_R | Mean R/trade | Median R/trade | Max closed R drawdown | Max loss streak | Trades/week |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Discovery 2017–2020 | 739 | -93.4071 | 0.7689 | -0.1264 | -0.3577 | 93.4071R | 9 | 3.536 |
| Validation 2021 | 66 | -7.3598 | 0.7774 | -0.1115 | -0.2491 | 14.4971R | 6 | 1.245 |

The pre-outcome eligibility audit found 1,129 discovery signals and 97 validation signals; after the frozen spread/entry/path gates, 856 discovery and 76 validation events were initially eligible at T+5, before position-overlap filtering. Thus the registered 100-trade validation minimum fails even before the final trade ledger is applied.

## Cost and latency stress

| Stream | Period | Trades | Net R | PF_R |
|---|---|---:|---:|---:|
| T+5 fade +0 pip | Discovery | 739 | +19.0664 | 1.0558 |
| T+5 fade +0 pip | Validation | 66 | +1.3384 | 1.0479 |
| T+5 fade +0.5 pip | Discovery | 739 | -37.1704 | 0.9002 |
| T+5 fade +0.5 pip | Validation | 66 | -3.0107 | 0.9013 |
| T+5 fade +2 pip | Discovery | 739 | -205.8806 | 0.5621 |
| T+5 fade +2 pip | Validation | 66 | -16.0580 | 0.5800 |
| T+10 fade +1 pip | Discovery | 727 | -117.0163 | 0.7095 |
| T+10 fade +1 pip | Validation | 65 | -5.4866 | 0.8266 |
| T+5 follow diagnostic +1 pip | Discovery | 745 | -155.5030 | 0.6459 |
| T+5 follow diagnostic +1 pip | Validation | 64 | -13.7828 | 0.5986 |

The zero-extra-cost point estimate becomes slightly positive but deteriorates once even +0.5 pip of incremental friction is added. The predeclared primary +1 pip case loses in both periods.

## Validation uncertainty

The 2021 weekly bootstrap used 5,000 circular moving-block resamples of four calendar weeks, seed 303, and all 52 Monday-start weeks including zero-trade weeks.

- Mean weekly net: -0.14153R
- 95% interval: [-0.40550R, +0.11319R]
- Bootstrap share of positive mean: 13.92%

The interval crosses zero and its lower bound is negative.

## Locked gate result

Only 2 of 13 gates passed: data-integrity checks and minimum discovery trade count. Failed gates include minimum validation sample, primary-cost expectancy and PF, +2-pip cost stress, discovery year stability (0/4 positive years), bootstrap lower bound, T+10 delay stress, and repository-level exact-code/ledger reproducibility. **No funded challenge replay was run** because the strategy-level gate failed.

## Integrity and limitations

- Source: pre-existing GitHub data artifact #11959096102, paired EURUSD M1 BID/ASK.
- Archive SHA-256: `b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e`.
- 4,415,493 source timestamps per side; timestamps paired exactly; zero duplicates, invalid OHLC rows, or negative spreads.
- 696,795 repeated flat-fill rows excluded using the registered prior-close/timestamp rule; missing rows were not synthesized.
- Candidate features/outcomes were restricted to discovery 2017–2020 and validation 2021. No candidate PnL was calculated for 2022+.
- 2017–2021 EURUSD is repeatedly used by prior project rounds, so this is not pristine program-level OOS.
- The exact corrected local runner SHA-256 is `cbfeafcd474acac8f11e7f286518114d422efdc030bae067cf072504e6aac8f9`. The full runner and row-level ledgers have not yet been transferred into the active GitHub branch at the time of this report, so end-to-end repository-only reproducibility is explicitly **not passed**. The primary outputs' local hashes are recorded in the manifest.
- No result here establishes FundedNext readiness or current broker-specific costs. No R303 signal block is retained.

## Artifact navigation

See `R303_INDEX.md` and `R303_DATA_MANIFEST.md` for archived summaries and source/output hashes. The exact runner and raw row-level ledgers remain unarchived; repository-only reproduction is not complete.