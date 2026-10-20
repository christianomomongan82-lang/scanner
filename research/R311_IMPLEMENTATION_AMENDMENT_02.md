# R311 Implementation Amendment 02 — JSON Audit Serialization Only

**This amendment does not change the frozen signal, event clock, entries, exits, costs, periods, eligibility conditions or gates.**

The first complete local scoring execution wrote the event audit, trade ledger, simulation-skip CSV, annual scorecard and validation weekly series. It then stopped while writing the summary JSON because the skip-count aggregation used Python tuple keys, which JSON object keys cannot represent. No scorecard/report JSON was successfully written in that attempt.

The correction changes only serialization of `simulation_skip_reasons`: convert the grouped key/count table into a list of records containing `stream`, `entry_delay_minutes`, `reason`, and `count`. The checked-in runner now verifies both the original preregistered source hash and the exact patched-source hash `1bbe9f3b4798e2efdbfd59c8f8e3c40c0c277a7bd644ab4d2f2cc207e170f901` before execution.

Rerunning the fixed local script produced byte-identical hashes for the signal-independent event audit, trade ledger, skip audit, annual scorecard and weekly input compared with the first complete scoring pass. The final JSON was then generated successfully. The economic results were not used to alter the candidate; the R311 rules remain frozen and the screen fails on negative primary expectancy.
