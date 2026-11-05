#!/usr/bin/env python3
"""R334 descriptive FX-market audit. No signals, trades, PnL, or strategy selection."""
from __future__ import annotations

import argparse
import json
import math
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

SYMBOLS = ("usdhuf", "eurnok", "usdzar", "eurusd")
PIP_SIZE = {"usdhuf": 0.01, "eurnok": 0.0001, "usdzar": 0.0001, "eurusd": 0.0001}
UTC = "UTC"
NY = "America/New_York"
M5 = pd.Timedelta(minutes=5)


def pct_summary(values: pd.Series, prefix: str = "") -> dict:
    x = pd.to_numeric(values, errors="coerce").replace([np.inf, -np.inf], np.nan).dropna()
    if x.empty:
        return {f"{prefix}n": 0}
    q = x.quantile([0.50, 0.75, 0.90, 0.95, 0.99])
    return {
        f"{prefix}n": int(x.size),
        f"{prefix}mean": float(x.mean()),
        f"{prefix}p50": float(q.loc[0.50]),
        f"{prefix}p75": float(q.loc[0.75]),
        f"{prefix}p90": float(q.loc[0.90]),
        f"{prefix}p95": float(q.loc[0.95]),
        f"{prefix}p99": float(q.loc[0.99]),
        f"{prefix}max": float(x.max()),
    }


def load_side(path: Path) -> tuple[pd.DataFrame, dict]:
    if not path.is_file():
        raise FileNotFoundError(path)
    df = pd.read_csv(path)
    required = ["timestamp", "open", "high", "low", "close"]
    if list(df.columns) != required:
        raise ValueError(f"{path.name}: header mismatch: {list(df.columns)}")
    raw_ts = pd.to_numeric(df["timestamp"], errors="coerce")
    if raw_ts.isna().any():
        raise ValueError(f"{path.name}: non-numeric timestamp rows={int(raw_ts.isna().sum())}")
    idx = pd.to_datetime(raw_ts, unit="ms", utc=True, errors="coerce")
    if idx.isna().any():
        raise ValueError(f"{path.name}: invalid epoch-ms timestamps")
    prices = df[["open", "high", "low", "close"]].apply(pd.to_numeric, errors="coerce")
    vals = prices.to_numpy(dtype=float)
    finite_rows = np.isfinite(vals).all(axis=1)
    positive_rows = (vals > 0).all(axis=1)
    o, h, l, c = (prices[k].to_numpy(dtype=float) for k in required[1:])
    ohlc_valid = (h >= np.maximum(o, c)) & (l <= np.minimum(o, c)) & (h >= l)
    quality = {
        "rows": int(len(df)),
        "first_timestamp_utc": idx.min().isoformat() if len(idx) else None,
        "last_timestamp_utc": idx.max().isoformat() if len(idx) else None,
        "monotonic_in_file": bool(idx.is_monotonic_increasing),
        "duplicate_timestamps": int(idx.duplicated().sum()),
        "nonfinite_ohlc_rows": int((~finite_rows).sum()),
        "nonpositive_ohlc_rows": int((~positive_rows).sum()),
        "invalid_ohlc_rows": int((~ohlc_valid).sum()),
        "bytes": int(path.stat().st_size),
    }
    prices.index = pd.DatetimeIndex(idx, name="timestamp_utc")
    return prices, quality


def market_open_ny(ts: pd.Timestamp) -> bool:
    local = ts.tz_convert(NY)
    weekday = local.weekday()
    minute = local.hour * 60 + local.minute
    # FX weekly closure: Friday 17:00 New York through Sunday 17:00 New York.
    if weekday == 5:
        return False
    if weekday == 4 and minute >= 17 * 60:
        return False
    if weekday == 6 and minute < 17 * 60:
        return False
    return True


def expected_missing_bars(index: pd.DatetimeIndex) -> tuple[int, dict[str, int], list[dict]]:
    monthly = Counter()
    gap_rows = []
    total = 0
    if len(index) < 2:
        return 0, {}, gap_rows
    ns = index.asi8
    gap_positions = np.flatnonzero(np.diff(ns) > M5.value)
    for i in gap_positions:
        left = index[i]
        right = index[i + 1]
        expected = pd.date_range(left + M5, right - M5, freq=M5, tz=UTC)
        active = [t for t in expected if market_open_ny(t)]
        if active:
            total += len(active)
            for t in active:
                monthly[t.strftime("%Y-%m")] += 1
            gap_rows.append({
                "previous_observed_utc": left.isoformat(),
                "next_observed_utc": right.isoformat(),
                "elapsed_minutes": (right - left).total_seconds() / 60,
                "expected_missing_m5_bars_excluding_weekly_close": len(active),
            })
    return total, dict(sorted(monthly.items())), gap_rows


def realized_volatility(close: pd.Series) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    idx = close.index
    r = np.log(close.astype(float)).diff()
    gaps = idx.to_series().diff()
    r = r.where(gaps.eq(M5))
    temp = pd.DataFrame({"r2": r.pow(2)}, index=idx)

    hour = temp.groupby(idx.floor("h"))["r2"]
    hour_n = hour.count()
    hour_rv = np.sqrt(hour.sum()).where(hour_n.eq(12)).dropna()

    day = temp.groupby(idx.floor("D"))["r2"]
    day_n = day.count()
    day_rv = np.sqrt(day.sum()).where(day_n.eq(288)).dropna()

    # Close-to-close hourly and daily returns; omit long gaps and weekend spans.
    hourly_close = close.groupby(idx.floor("h")).last()
    hourly_close = hourly_close.loc[hour_rv.index]
    hourly_ret = np.log(hourly_close).diff()
    hourly_gap = hourly_close.index.to_series().diff()
    hourly_ret = hourly_ret.where(hourly_gap.le(pd.Timedelta(minutes=90))).dropna()

    daily_close = close.resample("1D").last().dropna()
    daily_ret = np.log(daily_close).diff()
    daily_gap = daily_close.index.to_series().diff()
    daily_ret = daily_ret.where(daily_gap.le(pd.Timedelta(hours=36))).dropna()
    return hour_rv, day_rv, daily_ret, hourly_ret


def rolling_ranges(bid: pd.DataFrame) -> tuple[pd.Series, pd.Series]:
    idx = bid.index
    break_flag = idx.to_series().diff().ne(M5)
    run_id = break_flag.cumsum().to_numpy()
    range_1h = pd.Series(np.nan, index=idx, dtype=float)
    range_4h = pd.Series(np.nan, index=idx, dtype=float)
    for _, positions in pd.Series(np.arange(len(idx)), index=idx).groupby(run_id):
        loc = positions.to_numpy(dtype=int)
        if len(loc) < 48:
            continue
        part = bid.iloc[loc]
        r12 = part["high"].rolling(12, min_periods=12).max() - part["low"].rolling(12, min_periods=12).min()
        r48 = part["high"].rolling(48, min_periods=48).max() - part["low"].rolling(48, min_periods=48).min()
        range_1h.iloc[loc] = r12.to_numpy()
        range_4h.iloc[loc] = r48.to_numpy()
    return range_1h, range_4h


def audit_symbol(symbol: str, root: Path, out: Path) -> tuple[dict, pd.Series | None, list[dict], pd.DataFrame | None, pd.DataFrame | None, list[dict]]:
    stem = f"{symbol}_m5_"
    bid, qb = load_side(root / f"{stem}bid_2007-03-13_2026-11-01.csv")
    ask, qa = load_side(root / f"{stem}ask_2007-03-13_2026-11-01.csv")
    quality = {"symbol": symbol, "bid": qb, "ask": qa}

    duplicate = qb["duplicate_timestamps"] + qa["duplicate_timestamps"]
    invalid = (qb["nonfinite_ohlc_rows"] + qa["nonfinite_ohlc_rows"]
               + qb["nonpositive_ohlc_rows"] + qa["nonpositive_ohlc_rows"]
               + qb["invalid_ohlc_rows"] + qa["invalid_ohlc_rows"])
    bid_sorted = bid.sort_index()
    ask_sorted = ask.sort_index()
    paired = bid_sorted.index.intersection(ask_sorted.index)
    bid_only = bid_sorted.index.difference(ask_sorted.index)
    ask_only = ask_sorted.index.difference(bid_sorted.index)
    quality.update({
        "paired_timestamps": int(len(paired)),
        "bid_only_timestamps": int(len(bid_only)),
        "ask_only_timestamps": int(len(ask_only)),
        "paired_coverage_of_bid_pct": float(100 * len(paired) / max(1, len(bid_sorted))),
        "paired_coverage_of_ask_pct": float(100 * len(paired) / max(1, len(ask_sorted))),
    })

    exceptions = []
    if len(bid_only):
        exceptions.extend({"symbol": symbol, "exception": "bid_only_timestamp", "timestamp_utc": t.isoformat()} for t in bid_only[:1000])
    if len(ask_only):
        exceptions.extend({"symbol": symbol, "exception": "ask_only_timestamp", "timestamp_utc": t.isoformat()} for t in ask_only[:1000])

    status = "PASS_INPUT_INTEGRITY"
    block_reasons = []
    if duplicate:
        block_reasons.append("duplicate_timestamps")
    if invalid:
        block_reasons.append("invalid_ohlc_rows")
    if len(bid_only) or len(ask_only):
        block_reasons.append("bid_ask_timestamp_mismatch")

    if block_reasons:
        status = "GAGAL_SPREAD_ANALYSIS_BLOCKED"
        quality["block_reasons"] = block_reasons
        quality["status"] = status
        return quality, None, exceptions, None, None, []

    bid = bid_sorted.loc[paired]
    ask = ask_sorted.loc[paired]
    open_spread = ask["open"] - bid["open"]
    close_spread = ask["close"] - bid["close"]
    bad_open = open_spread <= 0
    bad_close = close_spread <= 0
    if bad_open.any() or bad_close.any():
        status = "GAGAL_SPREAD_ANALYSIS_BLOCKED"
        quality["nonpositive_open_spreads"] = int(bad_open.sum())
        quality["nonpositive_close_spreads"] = int(bad_close.sum())
        for ts in open_spread.index[bad_open][:1000]:
            exceptions.append({"symbol": symbol, "exception": "nonpositive_open_spread", "timestamp_utc": ts.isoformat()})
        for ts in close_spread.index[bad_close][:1000]:
            exceptions.append({"symbol": symbol, "exception": "nonpositive_close_spread", "timestamp_utc": ts.isoformat()})
        quality["status"] = status
        return quality, None, exceptions, None

    pip = PIP_SIZE[symbol]
    mid_open = (ask["open"] + bid["open"]) / 2
    spread_pips = open_spread / pip
    spread_bps_mid = open_spread / mid_open * 10000
    summary = {
        "symbol": symbol,
        "status": status,
        "pip_size_convention_price_units": pip,
        "pip_convention_note": "standard quote convention for descriptive normalization only; FundedNext contract/tick specification still requires terminal verification",
        "paired_bars": int(len(paired)),
        "actual_first_common_utc": paired.min().isoformat(),
        "actual_last_common_utc": paired.max().isoformat(),
    }
    summary.update(pct_summary(spread_pips, "open_spread_pips_"))
    summary.update(pct_summary(spread_bps_mid, "open_spread_bps_mid_"))
    summary.update(pct_summary(close_spread / pip, "close_spread_pips_"))

    same_bar_range = (bid["high"] - bid["low"]).replace(0, np.nan)
    range_1h, range_4h = rolling_ranges(bid)
    summary.update(pct_summary(open_spread / same_bar_range, "spread_to_m5_range_"))
    summary.update(pct_summary(open_spread / range_1h.replace(0, np.nan), "spread_to_rolling_1h_range_"))
    summary.update(pct_summary(open_spread / range_4h.replace(0, np.nan), "spread_to_rolling_4h_range_"))

    hourly_rows = []
    frame = pd.DataFrame({
        "spread_pips": spread_pips,
        "spread_close_pips": close_spread / pip,
        "spread_bps_mid": spread_bps_mid,
        "activity": 1,
    }, index=paired)
    hour_group = frame.groupby(paired.hour)
    for hour, group in hour_group:
        hourly_rows.append({
            "symbol": symbol,
            "utc_hour": int(hour),
            "observed_bars": int(len(group)),
            "spread_pips_median": float(group["spread_pips"].median()),
            "spread_pips_p90": float(group["spread_pips"].quantile(0.90)),
            "close_spread_pips_median": float(group["spread_close_pips"].median()),
            "close_spread_pips_p90": float(group["spread_close_pips"].quantile(0.90)),
            "spread_bps_mid_median": float(group["spread_bps_mid"].median()),
            "spread_bps_mid_p90": float(group["spread_bps_mid"].quantile(0.90)),
        })

    weekday_rows = []
    weekday_group = frame.groupby(paired.dayofweek)
    for day, group in weekday_group:
        weekday_rows.append({
            "symbol": symbol,
            "utc_weekday": int(day),
            "observed_bars": int(len(group)),
            "spread_pips_median": float(group["spread_pips"].median()),
            "spread_pips_p90": float(group["spread_pips"].quantile(0.90)),
            "close_spread_pips_median": float(group["spread_close_pips"].median()),
            "close_spread_pips_p90": float(group["spread_close_pips"].quantile(0.90)),
            "spread_bps_mid_median": float(group["spread_bps_mid"].median()),
            "spread_bps_mid_p90": float(group["spread_bps_mid"].quantile(0.90)),
        })

    hour_rv, day_rv, daily_ret, hourly_ret = realized_volatility(bid["close"])
    summary.update(pct_summary(hour_rv, "hourly_realized_vol_"))
    summary.update(pct_summary(day_rv, "daily_realized_vol_"))
    summary.update(pct_summary(hourly_ret.abs(), "hourly_abs_close_return_"))
    summary.update(pct_summary(daily_ret.abs(), "daily_abs_close_return_"))

    m5_logret = np.log(bid["close"]).diff()
    m5_gap = bid.index.to_series().diff()
    m5_logret = m5_logret.where(m5_gap.eq(M5))
    abs_m5 = m5_logret.abs()
    summary["abs_m5_return_autocorr_lag1"] = float(abs_m5.autocorr(lag=1))
    summary["abs_m5_return_autocorr_lag12"] = float(abs_m5.autocorr(lag=12))
    summary["abs_m5_return_autocorr_lag288"] = float(abs_m5.autocorr(lag=288))
    total_missing, monthly_missing, gap_rows = expected_missing_bars(paired)
    quality.update({
        "status": status,
        "nonpositive_open_spreads": 0,
        "nonpositive_close_spreads": 0,
        "expected_missing_m5_bars_excluding_weekly_close": total_missing,
        "gap_intervals_with_expected_missing_bars": int(len(gap_rows)),
    })
    summary["expected_missing_m5_bars_excluding_weekly_close"] = total_missing

    # Add intraday realized-volatility profile rows.
    rv_profile = hour_rv.groupby(hour_rv.index.hour).agg(
        n="count", median="median", p90=lambda x: x.quantile(0.90)
    )
    for row in hourly_rows:
        h = row["utc_hour"]
        if h in rv_profile.index:
            row["hourly_rv_n"] = int(rv_profile.loc[h, "n"])
            row["hourly_rv_median"] = float(rv_profile.loc[h, "median"])
            row["hourly_rv_p90"] = float(rv_profile.loc[h, "p90"])
        else:
            row["hourly_rv_n"] = 0
            row["hourly_rv_median"] = None
            row["hourly_rv_p90"] = None

    for month, count in monthly_missing.items():
        gap_rows.append({"symbol": symbol, "month_utc": month, "expected_missing_m5_bars": count, "record_type": "monthly"})
    return {**quality, "descriptive": summary}, daily_ret, exceptions, pd.DataFrame(hourly_rows), pd.DataFrame(weekday_rows), gap_rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-dir", type=Path, default=Path("raw/r334"))
    parser.add_argument("--output-dir", type=Path, default=Path("research/r334_audit_output"))
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    reports = []
    daily_returns = {}
    all_exceptions = []
    hourly_frames = []
    weekday_frames = []
    all_gap_records = []

    for symbol in SYMBOLS:
        report, daily_ret, exceptions, hourly, weekday, gap_rows = audit_symbol(symbol, args.data_dir, args.output_dir)
        reports.append(report)
        all_exceptions.extend(exceptions)
        if daily_ret is not None:
            daily_returns[symbol] = daily_ret.rename(symbol)
        if hourly is not None:
            hourly_frames.append(hourly)
        if weekday is not None:
            weekday_frames.append(weekday)
        all_gap_records.extend({"symbol": symbol, **row} for row in gap_rows)
        print(f"AUDIT {symbol}: {report['status']}")

    correlations = []
    if "eurusd" in daily_returns:
        baseline = daily_returns["eurusd"]
        for symbol, series in daily_returns.items():
            paired = pd.concat([series, baseline], axis=1, join="inner").dropna()
            corr = float(paired.iloc[:, 0].corr(paired.iloc[:, 1])) if len(paired) >= 2 else None
            correlations.append({
                "symbol": symbol,
                "baseline": "eurusd",
                "common_daily_return_observations": int(len(paired)),
                "correlation": corr,
                "first_common_date_utc": paired.index.min().isoformat() if len(paired) else None,
                "last_common_date_utc": paired.index.max().isoformat() if len(paired) else None,
            })

    result = {
        "experiment": "R334",
        "purpose": "market eligibility/descriptive audit only; no strategy signals, trades, PnL or alpha test",
        "timeframe": "M5",
        "price_sides": ["BID", "ASK"],
        "timezone": "UTC",
        "weekly_closure_exclusion": "Friday 17:00 to Sunday 17:00 America/New_York",
        "pip_size_conventions": PIP_SIZE,
        "reports": reports,
        "daily_return_correlations_vs_eurusd": correlations,
    }
    (args.output_dir / "R334_descriptive_audit.json").write_text(
        json.dumps(result, indent=2, allow_nan=False) + "\n", encoding="utf-8"
    )
    if all_exceptions:
        pd.DataFrame(all_exceptions).to_csv(args.output_dir / "R334_exceptions.csv", index=False)
    if hourly_frames:
        pd.concat(hourly_frames, ignore_index=True).to_csv(args.output_dir / "R334_spread_and_volatility_by_utc_hour.csv", index=False)
    if correlations:
        pd.DataFrame(correlations).to_csv(args.output_dir / "R334_daily_correlations_vs_eurusd.csv", index=False)
    if weekday_frames:
        pd.concat(weekday_frames, ignore_index=True).to_csv(args.output_dir / "R334_spread_by_utc_weekday.csv", index=False)
    if all_gap_records:
        pd.DataFrame(all_gap_records).to_csv(args.output_dir / "R334_expected_gaps_excluding_weekly_close.csv", index=False)
    print(f"OUTPUT {args.output_dir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
