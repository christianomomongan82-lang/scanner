# R331 Amendment D — minute-level midpoint construction and cost interpretation

**Committed before any event return or PnL was calculated.**

## Midpoint OHLC construction

- Join BID and ASK on the exact same M1 UTC timestamp.
- At each valid paired M1 timestamp, compute `mid_open=(bid_open+ask_open)/2`, `mid_high=(bid_high+ask_high)/2`, `mid_low=(bid_low+ask_low)/2`, and `mid_close=(bid_close+ask_close)/2`.
- Aggregate M5 midpoint bars from these M1 midpoint series: first midpoint open, maximum minute midpoint high, minimum minute midpoint low, last midpoint close. A complete M5 bar requires exactly five unique valid paired minute timestamps in that bin.
- Do **not** calculate a M5 midpoint high as `(max(bid_high)+max(ask_high))/2` or a midpoint low as `(min(bid_low)+min(ask_low))/2`; BID/ASK extremes can occur on different minutes, creating a synthetic price extreme not observed on any paired minute.
- Preserve BID and ASK aggregates separately for executable entry/exit fills. Long entry uses ASK open and exit uses BID open; short entry uses BID open and exit uses ASK open.

## Cost-ladder interpretation

- Side-correct ASK/BID entry and exit already includes the spread of the Dukascopy source feed in the gross trade result.
- The registered 0/2/5/10 bps per-round-trip ladder is **additional** friction beyond those source-feed executable sides, to stress extra slippage, platform/feed differences, and any fee that can be converted defensibly to a comparable return basis. It is not a replacement for the observed BID/ASK spread and must not be described as “adding the p95 spread” a second time.
- For decision purposes the 5 bps scenario remains primary and 10 bps remains stress, exactly as frozen earlier. Actual FundedNext platform costs remain unknown until quote/contract terms can be verified; this screen is not a platform-specific net backtest.

These are data-processing and interpretation clarifications, not post-result strategy changes. No R331 outcome had been calculated at the time of this amendment.