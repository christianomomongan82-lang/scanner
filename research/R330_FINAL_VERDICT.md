# R330 STATUS — GATE-MISMATCH (definisi konvensi entry), strategi belum dievaluasi

## Canonical Gate 1 run

The canonical source is stored as research/R191_CANONICAL_index_trend_long.py. Strategy code is unchanged; only the loader accepts repository M5 CSV.GZ cache. Gate 1 is decided by canonical output, not R192 ideal or manual5m.

| phase     | years_ny   |   canonical_n |   canonical_pf_1bp |   canonical_pf_2bp |   canonical_pf_3bp |   expected_n |   expected_pf_1bp |   expected_pf_2bp |
|:----------|:-----------|--------------:|-------------------:|-------------------:|-------------------:|-------------:|------------------:|------------------:|
| selection | 2017-2021  |            79 |            2.13445 |            2.12148 |            2.10862 |           78 |             2.082 |           nan     |
| forward   | 2022-2025  |            68 |            1.31035 |            1.30428 |            1.29825 |           70 |             1.247 |             1.241 |
| oos_2026  | 2026-2026  |            11 |            1.68332 |            1.67345 |            1.66365 |           11 |           nan     |             1.954 |

## First post-2017 trade-level divergence

The comparison below filters the trade streams to entry year >=2017 in New York. The full R192 ledger is still preserved, including pre-2017 trades, because a pre-period position can block a post-period signal.

{
  "instrument": "usa500idxusd",
  "trade_ordinal_within_instrument_post2017": 1,
  "comparison_window": "entry year >= 2017 in America/New_York",
  "different_fields": [
    "entry_timestamp",
    "entry_price",
    "sl",
    "risk"
  ],
  "canonical_trade": {
    "instrument": "usa500idxusd",
    "trade_ordinal": 1,
    "signal_bar_ny": "2017-01-24T13:00:00-05:00",
    "signal_bar_utc": "2017-01-24T18:00:00+00:00",
    "entry_time_ny": "2017-01-24T17:00:00-05:00",
    "entry_time_utc": "2017-01-24T22:00:00+00:00",
    "entry": 2281.531,
    "sl": 2256.061,
    "tp": 2332.4709999999995,
    "risk_points": 25.4699999999998,
    "gross_r": 2.0,
    "gross_exit_derived": 2332.4709999999995,
    "entry_year_ny": 2017
  },
  "r192_ideal_trade": {
    "config": "R191_BASE_55_27_RR2",
    "role": "locked_baseline",
    "breakout": 55,
    "stop_bars": 27,
    "mode": "ideal",
    "signal_bar_utc": "2017-03-01T06:00:00+00:00",
    "signal_close_utc": "2017-03-01T10:00:00+00:00",
    "entry_time_utc": "2017-03-01T10:00:00+00:00",
    "entry": 2374.12,
    "sl": 2358.349,
    "tp": 2405.6619999999994,
    "exit_time_utc": "2017-03-09T19:00:00+00:00",
    "exit": 2358.349,
    "reason": "SL",
    "entry_exact_m5_timestamp": true,
    "risk_points": 15.77099999999973,
    "flat_m5_bars_skipped_while_open": 504,
    "instrument": "usa500idxusd",
    "instrument_name": "USA 500 / S&P 500"
  },
  "bar_grid_checks": {
    "canonical_signal_label_exists_in_r192_grid": true,
    "canonical_entry_label_exists_in_r192_grid": true,
    "canonical_signal_label_exists_in_canonical_grid": true,
    "r192_bar_closing_at_canonical_entry_boundary_exists": false,
    "canonical_signal_close_boundary_utc": "2017-01-24T22:00:00+00:00",
    "r192_nearest_labels_utc": [
      "2017-01-24T10:00:00+00:00",
      "2017-01-24T14:00:00+00:00",
      "2017-01-24T18:00:00+00:00",
      "2017-01-24T22:00:00+00:00",
      "2017-01-25T02:00:00+00:00"
    ]
  },
  "same_signal_candidate_in_r192_h4": {
    "signal_label_ny": "2017-01-24T13:00:00-05:00",
    "signal_label_utc": "2017-01-24T18:00:00+00:00",
    "canonical_signal": true,
    "canonical_signal_close": 2279.8,
    "canonical_prior_55bar_high": 2278.058,
    "canonical_sl_27bar_low": 2256.061,
    "canonical_next_h4_open_time_utc": "2017-01-24T22:00:00+00:00",
    "canonical_next_h4_open": 2281.531,
    "canonical_risk": 25.4699999999998
  },
  "r192_position_blocker_at_candidate_signal_close": {
    "entry_time_utc": "2016-11-09T18:00:00+00:00",
    "entry_time_ny": "2016-11-09T13:00:00-05:00",
    "entry": 2158.969,
    "sl": 2054.219,
    "risk_points": 104.75,
    "exit_time_utc": "2017-02-23T14:25:00+00:00",
    "exit_time_ny": "2017-02-23T09:25:00-05:00",
    "reason": "TP",
    "opened_before_2017_NY": true,
    "still_active_at_signal_close": true
  },
  "cause_assessment": "One-position state: an R192 position opened before the canonical 2017 start was still active at this signal close; R192 therefore skipped the candidate. Canonical load() truncates source bars to NY year >= 2017 and resets active=-1, so it can take this trade."
}

Full ledgers: research/R330_G1_canonical_trades.csv and research/R330_G1_r192_ideal_trades.csv. Details: research/R330_G1_first_trade_mismatch.json.

## Manual5m diagnostic (not used for pass/fail)

| phase     | entry_convention   | pass_fail_use   |   n_1bp |   pf_1bp |   entries_1bp |   censored_1bp |   n_2bp |   pf_2bp |   entries_2bp |   censored_2bp |   n_3bp |   pf_3bp |   entries_3bp |   censored_3bp |
|:----------|:-------------------|:----------------|--------:|---------:|--------------:|---------------:|--------:|---------:|--------------:|---------------:|--------:|---------:|--------------:|---------------:|
| selection | manual5m           | False           |      90 |  1.6605  |            92 |              2 |      90 |  1.64828 |            92 |              2 |      90 |  1.6362  |            92 |              2 |
| forward   | manual5m           | False           |      70 |  1.49073 |            72 |              2 |      70 |  1.48264 |            72 |              2 |      70 |  1.47461 |            72 |              2 |
| oos_2026  | manual5m           | False           |      11 |  1.65741 |            13 |              2 |      11 |  1.64823 |            13 |              2 |      11 |  1.63911 |            13 |              2 |

## Decision

**GATE-MISMATCH (definisi konvensi entry), strategi belum dievaluasi.** Gate 2 and all pooled criteria are NOT RUN. No pooled PF, neighborhood, leave-one-out, correlation/overlap, or funded challenge simulation was calculated.
