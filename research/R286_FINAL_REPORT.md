# R286 — US500 Three-Session Overextension Reversal

**Verdict: GAGAL.** The frozen reversal rule is negative at the primary 2 bp modeled cost in both discovery and validation. No 2022–2025 or 2026 trade outcomes were calculated or inspected.

## Locked rule

- At each valid US500 regular-hours close, calculate the three-session cumulative return `C_t/C_(t-3)-1`.
- The threshold is the 80th percentile of absolute valid three-session returns in discovery 2017–2020, frozen at **1.7307755%**. The fit used 858 valid signal windows.
- If the three-session move meets/exceeds the threshold, enter contrarian on the next active session: short after a positive extension, long after a negative extension.
- Entry: following session's 09:40 ET M5 bar open (T+10); exit: that session's 15:55 ET bar close. No overnight hold, stop, target or pyramiding in this initial signal screen.
- Matched parent uses exactly the same events and timestamps but follows the three-session move. Both streams use the same 1/2/4 bp modeled round-trip cost assumptions.

## Results at 2 bp modeled round-trip cost

| Stream | Period | Trades | PF | Net bps | Max drawdown bps |
|---|---|---:|---:|---:|---:|
| Contrarian candidate | Discovery 2017–2020 | 165 | 0.988 | -87.79 | 1,994.97 |
| Matched momentum parent | Discovery 2017–2020 | 165 | 0.926 | -572.21 | 2,140.84 |
| Contrarian candidate | Validation 2021 | 47 | 0.987 | -15.25 | 506.62 |
| Matched momentum parent | Validation 2021 | 47 | 0.859 | -172.75 | 641.42 |

The fade lost less than the matched continuation parent, but **relative improvement over a losing baseline is not positive edge**. The candidate remained negative in both time partitions.

## Candidate annual results at 2 bp

| Entry year | Trades | PF | Net bps |
|---|---:|---:|---:|
| 2017 | 1 | Not meaningful | +15.95 |
| 2018 | 51 | 0.592 | -1,315.07 |
| 2019 | 35 | 1.131 | +95.70 |
| 2020 | 78 | 1.319 | +1,115.63 |
| 2021 | 47 | 0.987 | -15.25 |

The discovery result was driven by 2020 gains and overwhelmed by 2018 losses. The 2017 positive figure is only one trade, so it does not provide meaningful evidence of annual stability.

## Cost sensitivity and gate decision

| Period | PF at 1 bp | PF at 2 bp | PF at 4 bp |
|---|---:|---:|---:|
| Discovery 2017–2020 | 1.010 | 0.988 | 0.945 |
| Validation 2021 | 1.028 | 0.987 | 0.911 |

PASS: discovery sample count, discovery 4 bp PF, validation sample count, validation 4 bp PF.
FAIL: discovery PF/net at 2 bp; validation PF/net at 2 bp.
The at-least-3-of-4 positive discovery years gate technically passed, but 2017 contained only one trade and is not meaningful support for stability.

**Final decision: GAGAL.** Do not tune Q80, reverse direction, change the lookback, or open later-period results to rescue this candidate. No funded challenge replay was run.

## Data, quality and execution limitations

- Input: cached GitHub R205 USA500 M5 BID-only artifact `11709864394`; archive SHA-256 `21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac`; extracted CSV SHA-256 `df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee`.
- 886,206 rows, from 2016-01-04 00:00 UTC to 2026-10-09 20:10 UTC. The session screen found 2,777 active RTH dates and 2,659 quality-eligible dates. Seven selected entry sessions were skipped for invalid/missing data.
- Cost inputs are modeled notional stresses, not observed BID/ASK, CFD commission, slippage or swap. The five-minute manual delay is approximated from bar timestamps. The result is not a funded-account equity-path replay.
- Data from 2022–2025 are research-contaminated and were not calculated for R286; 2026 was not opened.

## Reproduction artifacts

- Preregistration: [R286 locked rules](R286_US500_3SESSION_OVEREXTENSION_FADE_PREREGISTRATION.md)
- Results JSON: [R286 results](R286_results_compact.json)
- Replay source: [r286_us500_3session_fade.py](r286_us500_3session_fade.py)
- Candidate ledger: [R286 candidate trade ledger](R286_candidate_ledger_2017_2021.csv)
- Matched parent ledger: [R286 continuation comparison](R286_matched_parent_ledger_2017_2021.csv)
- Data-quality skip log: [R286 skipped signals](R286_skipped_signals.csv)

Calculations were performed locally in Python. No GitHub Actions backtest workflow was created or dispatched.
