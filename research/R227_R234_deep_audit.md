# R227–R234 independent deep audit

## Trade-ledger audit

- 92 unique trade-ledger CSVs audited; all 92 passed.
- 15 assertions per ledger, 1,380/1,380 assertions passed.
- 60,074 trade rows inspected against raw H1 BID OHLC.
- Verified source timestamps, signal close to next-open timing, exact raw entry/exit opens, non-flat execution bars, cost deductions, scheduled holding horizon, first non-flat exit at/after horizon, period boundaries, duplicate signals, side/direction, positive prices and symbol-level non-overlap.
- 180/180 feature/signal truncation-prefix checks passed; 10/10 source files passed basic OHLC and timestamp validation.

## Forward result interpretation

- **R227 / France 40:** PF@2 bps fell from 1.004 in discovery to 0.837 in forward and 0.718 in OOS; 2-bps mean expectancy is -4.527 bps/trade, with block-bootstrap 95% CI [-9.234, -0.612].
- **R228 / US Tech 100:** forward PF@1/@2 is 1.099/1.058. Annual PF@1 is above 1 in each year, but whole-period PF misses the threshold and OOS PF@2 is 0.679. Bootstrap interval crosses zero.
- **R229 / US500:** discovery PF@2 is 1.355 but falls to 1.016 in forward and 0.562 in OOS; 2022–23 lose while 2024–25 are positive. This is discovery-selection optimism and regime sensitivity.
- **R230 / EU50:** closest forward PF@1 is 1.176, but PF@2 is only 1.120. The weakest qualifying annual PF@1 is 0.647 in 2024 and OOS PF@2 is 0.898. Bootstrap CI crosses zero.
- **R233 / Australia 200:** forward PF@2 is 0.787; average net return is -4.010 bps/trade and the bootstrap CI is entirely below zero.
- **R234 / FTSE 100:** forward PF@1/@2 is 1.177/1.117, below the required PF@2; OOS has only 22 trades and is diagnostic only. The weakest forward annual PF@1 is 0.521.

## Discovery-only common-history sensitivity

R228's discovery selection changes from US Tech 100 to Australia 200 and R230 from EU50 to France 40 when re-ranked on common coverage beginning 2018-08-08. No alternate forward/OOS run was performed. This is a selection-stability diagnostic only and cannot promote a new finalist.

## Decision

No candidate passes PF >=1.15 at both modeled 1 and 2 bps plus annual cohort stability. R231 fails discovery sample size and R232 fails discovery PF. The other six are REJECT on forward. No strategy is declared live/funded-ready.
