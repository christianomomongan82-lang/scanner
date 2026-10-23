# R330 Amendment A — pre-outcome universe/data acquisition limit

**Date:** 2026-10-23 UTC  
**Status:** Committed before PnL; supersedes the universe list in the original R330 registration only.  
**Reason:** Data acquisition feasibility, not observed strategy outcomes.

## Why this amendment exists

The initial 15-symbol universe was registered before outcomes. During raw-file acquisition, the connected Massive API returned a rate-limit rejection for subsequent symbol requests after three successful sequential acquisitions in a batch. Five planned stock symbols were not archived, and no R330 PnL had been calculated. Rather than quietly drop missing instruments after viewing results or repeatedly attempting the same blocked batch, this amendment freezes a reproducible 10-instrument dataset using symbols whose raw daily histories can be archived and verified.

## Frozen R330 universe after Amendment A

- US stock CFDs: AAPL, AMZN, GOOG, MSFT, NVDA, TSLA, AMD, META.
- Crypto CFDs: BTCUSD, ETHUSD.

Excluded before PnL, with no outcome examined: BABA, NFLX, INTC, NKE, KO. SPCX remains excluded because it cannot supply the complete two-year lookback. No symbol may be added or substituted after outcomes. The original R330 signal, lookback, volatility scaling, weekly schedule, dates, cost sensitivity, and verdict rules are unchanged.

## Data window and split

- Requested: 2024-10-23 through 2026-10-22.
- Discovery: 2024-10-23 through 2025-10-22.
- Confirmation: 2025-10-23 through 2026-10-22.
- Raw source files must be archived for all 10 symbols and hashes verified before any R330 outcome is calculated.

## Important limitation

Ten symbols across eight US equities and two highly correlated cryptocurrencies is still a narrow universe. This can only be an initial screen. A positive screen would require a new registered data expansion/quote-execution preflight; it cannot be promoted based on this reduced universe. A negative robust screen closes this exact specification without proving all trend trading is impossible.

**No R330 PnL was calculated before or after this amendment was written.**
