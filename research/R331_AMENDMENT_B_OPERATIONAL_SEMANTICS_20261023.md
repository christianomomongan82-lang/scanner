# R331 Amendment B — exact calculation semantics locked before outcomes

**Date:** 2026-10-23 UTC. This amendment fixes implementation choices before any price/event returns are calculated.

## Data input and bar construction

- Price source: paired Dukascopy USATECHIDXUSD M1 BID/ASK OHLC from the raw-only acquisition artifact defined by Amendment A. Source feed is not guaranteed to equal FundedNext's live platform quotes.
- Convert each UTC timestamp to an America/New_York local datetime and local trading date. Keep the original UTC timestamp in all raw/event output.
- Join BID and ASK only on exact timestamps. Do not interpolate, forward-fill, synthesize flat bars, or use an unmatched BID or ASK minute.
- A valid 5-minute bar requires exactly the five expected consecutive UTC M1 timestamps ending within that group and valid OHLC on both sides. If any minute is missing or invalid, the 5-minute bar is absent. The screen never silently repairs it.
- Signal bands use midpoint OHLC computed per value as (BID + ASK) / 2. Entry/exit fills use the correct executable quote side: long enters ASK and exits BID; short enters BID and exits ASK.
- A session requires valid complete 5-minute bars from 09:30 through 15:55 ET and a valid previous regular-session close. If required bars are missing, retain a diagnostic but do not fabricate signal or exit prices.
- Session close is midpoint close of the completed 15:55 ET bar (derived from paired M1 rows from 15:55 to 15:59), representing the last complete regular-session bar closing at 16:00 ET. No 16:00 timestamped bar is treated as regular-session price history.

## VXN and prior-session base

- VXN source series is the local-only CSV generated from the public mirror `https://github.com/fuxui/vix-vxn/blob/main/data/history.json`; mirror README states this series is pulled from the CBOE daily-history VXN CSV at `https://cdn.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv`.
- Raw VXN values must not be committed to the public project repo. The local CSV hash, row count, first/last date, mirror/source URLs, retrieval date and source limitations are stored in the results manifest; the values stay in the local analysis environment.
- Today's band uses the prior USATECH local regular-session midpoint close and the latest VXN daily close whose date is strictly earlier than today's local trading date. Never join same-day VXN into a signal, even if it is already available in the source file.
- Upper = prior midpoint close × (1 + prior VXN close / 1600); lower = prior midpoint close × (1 − prior VXN close / 1600). The formula represents ±(VXN/16)% of prior close, matching the registered interpretation.

## Signal and execution state machine

- Scan valid complete regular-session 5-minute bars in ascending local timestamp order from 09:30 through 15:55.
- The first bar with midpoint high >= upper or midpoint low <= lower is the only candidate breach of that session. If its high >= upper and its low <= lower within the same bar, mark the session ambiguous and skip it. Do not search later bars for a replacement signal.
- Upper-only breach creates a short/fade direction (-1); lower-only breach creates a long/fade direction (+1). The signal is only known at the completed bar close; no fill at the band or within the signal bar is allowed.
- Ideal diagnostic entry is the open of the following 5-minute bar. Primary manual-delay entry is the open of the bar one additional 5 minutes after that ideal entry: signal bar label + 10 minutes. A delayed entry must be no later than 15:25 ET so a 30-minute exit at 15:55 remains inside the regular session.
- The fixed exit is the open of the 5-minute bar whose timestamp is exactly 30 minutes after the selected entry timestamp. If that exact exit bar is unavailable, invalid, or outside regular hours, skip the event; never approximate the exit.
- The ideal-entry diagnostic uses exactly the same event rules but enters at signal-bar label + 5 minutes and exits exactly 30 minutes later. It cannot determine PASS because the user-compatible result is the 5-minute delayed entry.
- Long raw return = (exit BID open − entry ASK open) / entry ASK open. Short raw return = (entry BID open − exit ASK open) / entry BID open. Convert to basis points by multiplying by 10,000. The native BID/ASK entry/exit side asymmetry captures source-feed spread; additional cost scenarios are then subtracted as separately registered.
- No second entry in a session; no overlapping positions; no overnight hold. This is a fixed-horizon economic screen, not yet a stop/position-sizing model or challenge replay.

## Partitions and zero-inclusive inference

- Partition by local session date: discovery 2023-10-25 through 2025-03-31; confirmation 2025-04-01 through 2026-10-21. The latest allowed signal/exit session is 2026-10-21 because the VXN source series ends that day.
- Record every evaluated session in an event/skip ledger with VXN used, prior base close, band levels, first breach and reason for skips.
- For bootstrap only, aggregate net basis-point PnL into all ISO Monday-based calendar weeks in each partition, including weeks with zero events. Use a circular moving-block bootstrap with block length 4 weeks, 10,000 replications, seed 33120261023; resample the zero-inclusive weekly sequence and calculate the mean weekly net basis-point PnL in each replicate.
- Report the empirical 2.5% and 97.5% quantiles of the bootstrap mean. This is a diagnostic uncertainty interval, not proof the market regime distribution is stationary.
- Costs remain 0, 2, 5 and 10 bps round-trip, applied once per completed event. The registered primary result is 5 bps and the stress result is 10 bps.
- Sample gate remains >=50 completed eligible events in each partition. If unmet, verdict is GAGAL — SAMPLE/TARGET FEASIBILITY, not a finding of negative expectancy.

## Source/compliance caveats

The VXN mirror has daily values from 2023-10-25 through 2026-10-21 (750 observations as checked before R331 price outcomes); its README attributes VXN history to CBOE's official CSV. The raw series stays local to avoid republishing the index values in a public repo. Any discrepancy, missing prior VXN date, nonunique key, unmatched quote, or input-hash mismatch must be surfaced; no same-day/forward-filled substitute is permitted.

No R331 price/event/PnL outcome was calculated when this amendment was written.