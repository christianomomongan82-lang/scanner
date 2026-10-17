# R287 — Intraday Cross-Index Residual Reversion

**Verdict: GAGAL.** The preregistered residual-fade direction was strongly negative in discovery and validation. Its matched parent, which follows the same residual on the same events, was substantially better, but remains a diagnostic comparison—not a promoted strategy. The 2022–2025 and 2026 strategy outcomes were not calculated.

## Locked hypothesis

R287 tested whether the most unusually divergent US equity index, measured against the same-day median of the other eligible indices, reverts before the close. Per instrument, the Q75 absolute residual was fitted on 2017–2020 only; entry was at 13:05 ET and the position was force-closed at the 15:55 bar open. One selected index maximum per date, requiring at least three valid indices. The matched parent followed rather than faded the exact same residual, instrument and timestamps.

## Source data and quality

| Symbol | Extracted CSV SHA-256 | Valid RTH sessions (2017–2021) | Q75 absolute residual |
|---|---|---:|---:|
| USA500 | `df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee` | 1,230 | 0.070461% |
| USATECH | `82b06c38f66cd1387097691baac1d45c9463b6540eea9dfe28a894d85e122f7c` | 1,240 | 0.266395% |
| USA30 | `8fcef9d76b31e99ae8d0175e769307ab13f930ae3ec2c17ef6baf0311ea1783a` | 1,237 | 0.147506% |
| USSC2000 | `c01c97d8705453d3fa3fd4ac1d386e9c1d72ab27e3b7d57d6cde53da9dfdf6f0` | 836 | 0.434056% |

Common synchronized dates with at least three quality-valid indices: 1,228. One winner per day passed the normalized residual threshold on 745 dates: 552 trades in discovery and 193 in validation. Missing bars were never filled. The input archives are BID-only. A flat-candidate row rule is a conservative data-quality heuristic, not proof that every synthetic row has been identified.

## Primary results — modeled 2 bp round-trip cost

| Stream | Period | Trades | PF | Net bps | Max drawdown bps |
|---|---|---:|---:|---:|---:|
| **Candidate: fade residual** | Discovery 2017–2020 | 552 | 0.802 | -2,742.47 | 2,960.96 |
| Parent: follow residual | Discovery 2017–2020 | 552 | 1.044 | +534.47 | 1,441.49 |
| **Candidate: fade residual** | Validation 2021 | 193 | 0.628 | -1,510.80 | 1,556.09 |
| Parent: follow residual | Validation 2021 | 193 | 1.253 | +738.80 | 384.22 |

### Candidate annual results at 2 bp

| Year | Trades | PF | Net bps |
|---|---:|---:|---:|
| 2017 | 70 | 0.506 | -508.25 |
| 2018 | 150 | 0.704 | -1,334.58 |
| 2019 | 133 | 0.573 | -991.05 |
| 2020 | 199 | 1.015 | +91.42 |
| 2021 | 193 | 0.628 | -1,510.80 |

The fade candidate is negative in every discovery year except 2020, where the net was only slightly positive. Its validation loss is large and clear.

### Matched parent annual diagnostic at 2 bp

| Year | Trades | PF | Net bps |
|---|---:|---:|---:|
| 2017 | 70 | 1.340 | +228.25 |
| 2018 | 150 | 1.212 | +734.58 |
| 2019 | 133 | 1.293 | +459.05 |
| 2020 | 199 | 0.862 | -887.42 |
| 2021 | 193 | 1.253 | +738.80 |

This is useful directional evidence: on this preregistered event stream, following residual outperformance outperformed fading it. However, discovery PF at 2 bp was 1.044, below the project's 1.05 candidate gate, and direction selection after seeing this diagnostic creates selection bias. It is **not** a funded-ready strategy and cannot be promoted from this result alone.

## Cost sensitivity

| Stream / period | PF at 1 bp | PF at 2 bp | PF at 4 bp |
|---|---:|---:|---:|
| Fade / discovery | 0.838 | 0.802 | 0.734 |
| Fade / validation | 0.667 | 0.628 | 0.555 |
| Follow / discovery | 1.092 | 1.044 | 0.955 |
| Follow / validation | 1.330 | 1.253 | 1.114 |

## Binary gate decision for preregistered fade candidate

- PASS — discovery trade count (552 ≥ 200).
- FAIL — discovery PF at 2 bp (0.802 < 1.05) and net return (-2,742.47 bp).
- FAIL — positive annual cohorts (only 2020 was positive).
- PASS — validation trade count (193 ≥ 50).
- FAIL — validation PF at 2 bp (0.628 < 1.00) and net return (-1,510.80 bp).
- FAIL — PF at 4 bp in discovery (0.734) and validation (0.555).

**Final decision: GAGAL.** Do not retune the fade, lower the score threshold, or open later-period outcomes for this candidate. No funded challenge replay was run.

## Reproducibility and limitations

- Preregistration: [R287 locked hypothesis](R287_US_INDEX_INTRADAY_RESIDUAL_REVERSION_PREREGISTRATION.md)
- Local replay engine: [r287_intraday_residual_reversion.py](r287_intraday_residual_reversion.py)
- Machine-readable metrics: [R287 compact results](R287_results_compact.json)
- Candidate trade ledger: [R287 candidate ledger](R287_candidate_ledger_2017_2021.csv)
- Matched parent ledger: [R287 parent ledger](R287_matched_parent_ledger_2017_2021.csv)
- Source quality audit: [R287 session-quality audit](R287_session_quality_audit.csv)

All calculations ran locally in Python on GitHub-sourced snapshots. The primary 1/2/4 bp values are modeled cost stresses, not observed spreads or verified broker fees. This signal screen has no provider-rule-aware account equity simulation. No GitHub Actions backtest workflow was created or dispatched.
