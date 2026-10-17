# R285 Pre-outcome Data-Eligibility Amendment — DQ1

Date: 2026-10-17  
**Applied before calculating any signal return, PnL, PF, or trading verdict.** The original preregistration remains unchanged and archived.

## Why amendment is necessary

A coverage-only audit of the cached USA500 M5 file found that the original "reject the entire calendar month if any active date is imperfect" rule would retain only 15 of 48 discovery months (2017–2020) and 6 of 12 validation months (2021). No R285 trade returns or strategy performance had been calculated or viewed at the time of this audit. The original rule would make the sample ineligible largely due to one bad session spilling into otherwise valid months.

## Corrected, frozen calendar/quality rule

1. **Calendar session set:** a weekday is a market-session candidate if the observed RTH 09:30–15:55 ET data show any nonzero intraday range or non-identical valid OHLC movement. Completely flat placeholder-only weekdays are treated as non-session dates (e.g. market closures).
2. Determine the first three and last two calendar-session candidates of each month from this full observed active-session set, including any candidate session that later fails data-quality checks. Thus a missing/corrupt first session cannot cause a later session to be falsely relabeled as the first session.
3. A selected date may be traded only if it has all 78 expected, unique five-minute timestamps, valid OHLC, no repeated-flat candidate as defined in the original preregistration, and valid entry/exit timestamps. A selected date that fails is **skipped, not replaced** by another date. Missing data are never filled.
4. All signal direction, candidate dates (first three/last two), entry/exit times, cost model, sample splits and performance gates remain unchanged. This is a pre-outcome data-calendar correction only, not a performance-driven mutation or a relaxation of signal criteria.
5. If the corrected usable trade sample fails the registered gates, close R285 as GAGAL and do not change the setup after seeing outcomes. Discovery/validation are the only performance periods calculated initially; 2022–2025 and 2026 stay unopened unless all gates pass.

This amendment preserves calendar integrity while preventing one bad date from eliminating otherwise valid months. It does not assert that all feed artifacts are perfectly identified; the repeated-flat exclusion remains heuristic and the source is BID-only.
