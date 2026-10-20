# R308 — Binary pre-outcome verdict: GAGAL (DATA/SAMPLE)

The locked Friday-close-to-Monday-reopen test required a true observed gap of >=24 hours from a Friday active quote to an active Monday reopening. The existing paired EURUSD archive, after its registered repeated-flat filter and exact M5 construction, contains only **two** such eligible event paths across discovery 2017–2020 and validation 2021–2025 (one in each period). The only qualifying gaps coincide with New Year's holiday closures, not a weekly reopen series. The rule's minimum-validation sample requirement is >=150 trades, so the candidate fails that hard gate before any outcome calculation.

**No PnL, direction, or outcome statistics were calculated for R308.** This is a data/event-coverage failure, not evidence that weekend FX carry itself is profitable or unprofitable. Do not relax the gap definition or select another Friday entry time on this archive after observing the sparse event count. A proper future study would require a feed that verifiably represents active trading and a real weekly reopen, plus exact FundedNext financing assumptions.

- [Locked registration](R308_FRIDAY_CLOSE_MONDAY_REOPEN_CARRY_PREREGISTRATION.md)
- [Exit timestamp amendment](R308_DQ1_REOPEN_EXIT_CLARIFICATION.md)
- [Pre-outcome audit](R307_R308_PREOUTCOME_AUDIT.md)
