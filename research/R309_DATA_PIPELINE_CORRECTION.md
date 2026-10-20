# R309 Data-Pipeline Correction — Preliminary Run Voided

The first R309 implementation incorrectly removed every paired M1 bar whose own OHLC was flat. That filter removed 713,969 rows and produced 725,853 EURUSD M5 bars, which did not match the committed EURUSD data audit (696,795 removed rows and 736,076 complete active M5 bars). The resulting R309 metrics are **VOID and must not be used as evidence or to choose strategy parameters**.

The source-level audit established the registered repeated-placeholder rule that reproduces the source manifest count: remove a paired minute only when both BID and ASK bars are flat AND each side's current flat price equals that side's immediately previous minute close. This rule removes 696,795 rows and leaves 3,718,698 active paired timestamps. The first quiet flat bar after a real price change remains; repeated flat placeholders matching the previous close are removed.

The R309 signal/entry/exit/cost rules are unchanged. The runner will be corrected to use that filter, the EURUSD M5 count must match the audit, and the entire R309 scoring pass will be rerun. No preliminary R309 scorecard or PnL was committed to the research ledger. This is a data-integrity correction, not a strategy-parameter adjustment.
