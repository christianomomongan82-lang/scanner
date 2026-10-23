# R330 — Cross-sectional multi-week currency momentum portfolio

**Status before calculation: registered; no R330 outcome/PnL calculated.**

## Hypothesis

At each eligible Tuesday 10:00 UTC H1 close, rank AUD, EUR, GBP, NZD, CAD, CHF and JPY by their relative-to-USD 13-, 26-, or 39-week return. Long the two strongest currencies versus USD and short the two weakest, in four volatility-normalized risk slots of 0.25 each. Rebalance weekly with an exact 12:00 UTC H1 entry bar and next Tuesday 12:00 UTC exit. Currency ranks are computed from data known by the signal close. Ties are resolved alphabetically by ISO currency code.

The mechanism is cross-sectional continuation: relative winners are expected to keep outperforming relative losers. This is distinct from R329's per-pair time-series direction and from R323's five-session rank with same-day intraday holding. The broad currency-momentum literature motivates a falsifiable test but does not imply this implementation has an edge: Menkhoff et al., *Currency momentum strategies*, Journal of Financial Economics (2012), DOI https://doi.org/10.1016/j.jfineco.2012.06.009.

## Instruments and source

Seven native paired Dukascopy H1 BID/ASK pairs: EURUSD, GBPUSD, AUDUSD, NZDUSD, USDCHF, USDCAD and USDJPY. Source data cover 2017-01-01 through 2025-12-31; exact BID/ASK and seven-pair timestamps only. All missing rows remain missing and static rows remain in the raw source but are ineligible as a tradable signal/entry/exit bar. Input file hashes are frozen in `data_manifest.json`; its combined ordered stream manifest hash is `2db7c7d88b2f31965ff956dd5e017ce7f0b76a4ac1792dca2dca2dca2dca2dca` is intentionally replaced below by the validated source hash in the machine registration.

## Portfolio rules

- Grid exactly: 13, 26, 39 prior eligible common weekly observations; no other parameters.
- Foreign-currency score is the pair log return for XUSD pairs and the negated pair log return for USDX pairs.
- Top 2 are long foreign-currency exposure; bottom 2 are short foreign-currency exposure. Each is 0.25 risk budget; only four positions per scheduled week. Tie breaks use ISO currency code.
- Direction maps to executable pair trades: long foreign currency means long XUSD or short USDX; short foreign currency is the reverse.
- Signal closes Tuesday 11:00 UTC; entry uses exact Tuesday 12:00 UTC H1 open. Exit uses the next Tuesday 12:00 UTC H1 open. This is a one-hour bar-resolution proxy, not an exact T+5-minute fill.
- Per-leg R scales the executable-side log-return by the trailing 13-week standard deviation of weekly pair log returns and the 0.25 risk slot. Longs enter ASK / exit BID; shorts enter BID / exit ASK. Stop/target is not used; the portfolio is time-exit only after one week.
- Primary costs: +1 pip adverse slippage, $10 round-trip commission per assumed 100,000-unit standard lot, and 2 pip-equivalent adverse swap per seven-day hold in addition to observed BID/ASK. High-cost stress is +2 pip slippage and 4 pip-equivalent adverse swap. Swap assumption is a conservative proxy, not the actual symbol-specific FundedNext swap.
- Discovery: 2017–2020; confirmation: 2021–2023; diagnostic only: 2024–2025; 2026 excluded. These historical periods are project-contaminated; even a positive result is only a development lead, not independent OOS proof.

## Gates and decision

Each horizon must have at least 200 eligible discovery legs / 100 dates and 100 confirmation legs / 70 dates before outcomes. If any required source or sample gate fails, stop with no PnL. If preflight passes, select one horizon on discovery mean weekly net R at the primary cost and never substitute another horizon based on confirmation. Economic pass requires positive net R and PF_R >= 1.05 in discovery and confirmation at primary cost, positive net R and PF_R >= 1.00 in both periods under stress, at least two of 2018–2020 positive, no year contributing more than 70% of positive discovery net R, and positive 95% lower bounds from the registered 10,000-replicate four-week circular block bootstrap in both periods with Holm adjustment across three candidates.

This test is historical exploratory evidence only. It cannot by itself justify a FundedNext challenge replay because 2017–2025 has been inspected in prior work, the H1 source cannot prove a true five-minute fill, and symbol-specific swaps / contract settings require external verification. XAUUSD 2026 remains protected.
