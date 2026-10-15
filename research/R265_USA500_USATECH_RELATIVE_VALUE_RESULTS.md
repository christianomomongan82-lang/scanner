# R265 USA500–USATECH Relative-Value Mean Reversion — Results

Date: 2026-10-16
**Verdict: FAILED. The forward PF clears the PF-only hurdle, but the trade-count and bootstrap gates fail; discovery is negative. Do not tune this candidate. 2026 OOS was not inspected.**

## Data integrity and provenance

- Source files are the existing GitHub-stored BID-only M5 histories: `usa500idxusd_m5.csv.gz` (886,206 rows) and `usatechidxusd_m5.csv.gz` (886,039 rows). Each file has zero duplicate timestamps and zero invalid OHLC rows; both run through 2026-10-09 UTC.
- The initial diagnostic showed that the data also has Sunday RTH timestamp rows that are flat placeholders plus 15 weekday all-flat placeholder sessions. That preliminary pass was discarded. The official replay excludes weekends, requires all 78 unique expected 09:30–15:55 ET M5 bars, requires a nonzero full-session range for both instruments, and intersects their valid dates.
- After cleaning: USA500 has 2,742 valid sessions; USATECH has 2,741; 2,741 common paired sessions remain from 2016-01-04 through 2026-10-09. The data-cleaning amendment is appended to the preregistration. It changed data eligibility only, not strategy parameters.
- Since the archive is BID-only, ASK-side quotes and observed live spread are unavailable. Cost stress of +2/+4/+6 bps per completed equal-notional pair trade is an explicit assumption, not an observed quote-side cost. Trade return is the average return of each leg's notional; net return subtracts the specified cost once per pair. Drawdown is on the cumulative trade-return-bps series, not a funded-account percentage drawdown.
- Signals, PnL, metrics and bootstrap ran locally in Python; GitHub Actions did not run this backtest.

## Locked method

- Relative ratio: `log(USATECH RTH close / USA500 RTH close)`.
- At each session close, compute a z-score against the previous 60 complete paired-session ratios, excluding the current date from the baseline.
- If flat and z >= +2, schedule short USATECH / long USA500 at next paired session open. If z <= -2, schedule long USATECH / short USA500. Only one pair can be open; signals while occupied are ignored.
- Exit decision at session close: z returns through zero in the expected direction, reaches adverse z = +/-3 on the original side, or 10 paired sessions elapse. The exit fills at the next common session open.
- The latency sensitivity moves both entry and scheduled exit fill from 09:30 to 09:35 ET. No threshold/exit parameter was optimized.

## Results by partition

| Partition | Trades | PF +2 bps | Net +2 bps | PF +4 bps | Net +4 bps | PF +6 bps | Net +6 bps |
|---|---:|---:|---:|---:|---:|---:|---:|
| Discovery 2016–2020 | 45 | 0.913 | -142.7 | 0.862 | -232.7 | 0.813 | -322.7 |
| Validation 2021 | 8 | 1.578 | +122.2 | 1.488 | +106.2 | 1.404 | +90.2 |
| Forward 2022–2025 | 41 | 1.496 | +481.9 | 1.395 | +399.9 | 1.302 | +317.9 |
| All 2016–2025 | 103 | 1.052 | +171.5 | 0.990 | -34.5 | 0.932 | -240.5 |

The forward segment has positive PF even under the highest tested cost, but it contains only 41 trades across four years, below the preregistered 100-trade minimum. The validation sample is only 8 trades, and discovery is negative.

## Five-minute delayed fill sensitivity

| Partition | Trades | PF +2 bps | Net +2 bps | PF +4 bps | Net +4 bps | PF +6 bps | Net +6 bps |
|---|---:|---:|---:|---:|---:|---:|---:|
| Discovery 2016–2020 | 45 | 0.847 | -254.8 | 0.799 | -344.8 | 0.754 | -434.8 |
| Validation 2021 | 8 | 1.454 | +97.7 | 1.369 | +81.7 | 1.289 | +65.7 |
| Forward 2022–2025 | 41 | 1.404 | +414.4 | 1.313 | +332.4 | 1.227 | +250.4 |
| All 2016–2025 | 103 | 0.991 | -30.5 | 0.932 | -236.5 | 0.878 | -442.5 |

The forward PF remains above 1.10 after the fixed five-minute fill delay, but this does not repair low sample size, negative discovery, or statistical uncertainty.

## Forward annual diagnostic at +4 bps

| Year | Trades | PF | Net bps |
|---:|---:|---:|---:|
| 2022 | 12 | 1.762 | +277.0 |
| 2023 | 7 | 0.094 | -259.1 |
| 2024 | 13 | 2.214 | +257.0 |
| 2025 | 9 | 1.382 | +125.0 |

Annual trade counts are too small for strong independent conclusions, but they show that the aggregate forward gain is uneven and includes a severe 2023 loss.

## Bootstrap — forward weekly net bps at +4 bps cost

Four-week circular block bootstrap, 10,000 repetitions:

| Fill mode | Mean weekly net | Probability resampled mean > 0 | 95% interval |
|---|---:|---:|---:|
| Ideal 09:30 entry/exit | +1.91 bps | 79.00% | [-2.64, +6.66] bps/week |
| +5-minute delay | +1.59 bps | 74.56% | [-3.14, +6.43] bps/week |

Both intervals include zero. That means the observed positive forward result is not statistically decisive under the preregistered weekly block-bootstrap test.

## Decision against preregistered gates

- Forward trades >=100: **FAIL** (41).
- Forward PF >=1.10 at +4 bps: pass PF-only criterion (1.395 ideal; 1.313 delayed), but not sufficient by itself.
- Bootstrap 95% interval wholly positive: **FAIL** for ideal and delayed entry.
- Historical stability: **FAIL**; discovery PF at +4 bps is 0.862, with net -232.7 bps.
- Overall PF at +4 bps: 0.990 ideal and 0.932 delayed.

**Final verdict: FAILED / not approved as a strategy or funded portfolio component.** This is not proof that all relative-value trading is ineffective; it rejects this exact locked 60-session z-score rule on this dataset. No post-result threshold changes, and no 2026 OOS test, because the required historical gates did not pass.

## Remaining limitations

The dataset does not contain ASK prices. The return/cost model is therefore a BID-only screen with assumed costs, not a live-reproducible broker fill model. Broker commission/slippage, swaps/financing, FundedNext DLL/MLL implementation, and Quick Strike remain unverified.