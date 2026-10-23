#!/usr/bin/env python3
"""R331 local-only VXN-banded Nasdaq reversion screen. No data download in this runner."""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, math
from datetime import date, timedelta
from pathlib import Path
import numpy as np
import pandas as pd

NY = "America/New_York"
DATA_START = date(2023, 10, 23)
START = pd.Timestamp("2023-10-25")
DISCOVERY_END = pd.Timestamp("2025-03-31")
CONFIRM_START = pd.Timestamp("2025-04-01")
END = pd.Timestamp("2026-10-21")
COSTS_BPS = (0.0, 2.0, 5.0, 10.0)
BOOTSTRAP_REPS = 10000
BOOTSTRAP_BLOCK_WEEKS = 4
BOOTSTRAP_SEED = 33120261023
EXPECTED_RTH_BARS = 78


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def parse_time(series: pd.Series) -> pd.DatetimeIndex:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().mean() > 0.95:
        if numeric.isna().any():
            raise ValueError("Timestamp appears numeric but includes unparsable rows")
        med = float(numeric.abs().median())
        unit = "ms" if med >= 1e11 else "s" if med >= 1e8 else None
        if unit is None:
            raise ValueError(f"Unrecognized numeric timestamp scale: {med}")
        out = pd.to_datetime(numeric, unit=unit, utc=True, errors="coerce")
    else:
        out = pd.to_datetime(series.astype(str).str.strip(), utc=True, errors="coerce")
    if out.isna().any():
        raise ValueError(f"Unparseable timestamps: {int(out.isna().sum())}")
    return pd.DatetimeIndex(out, name="timestamp_utc")


def read_side(path: Path, side: str):
    if not path.is_file():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, compression="infer")
    df.columns = [str(c).replace("\ufeff", "").strip().lower() for c in df.columns]
    tc = next((x for x in ("timestamp", "datetime", "date") if x in df.columns), None)
    if tc is None:
        raise ValueError(f"No timestamp column in {path}: {list(df.columns)}")
    needed = {"open", "high", "low", "close"}
    if not needed.issubset(df.columns):
        raise ValueError(f"Missing OHLC columns in {path}: {needed - set(df.columns)}")
    idx = parse_time(df[tc])
    out = df[["open", "high", "low", "close"]].apply(pd.to_numeric, errors="coerce")
    out.columns = [f"{x}_{side}" for x in ("open", "high", "low", "close")]
    out.index = idx
    if out.index.has_duplicates():
        raise ValueError(f"Duplicate timestamps in {path}: {int(out.index.duplicated().sum())}")
    out = out.sort_index()
    valid = np.isfinite(out.to_numpy(dtype=float)).all(axis=1)
    cols = [f"open_{side}", f"high_{side}", f"low_{side}", f"close_{side}"]
    o, h, l, c = (out[k] for k in cols)
    valid &= (h >= np.maximum(o, np.maximum(l, c))) & (l <= np.minimum(o, np.minimum(h, c))) & (h >= l) & (l > 0)
    invalid = int((~valid).sum())
    out = out.loc[valid]
    return out, {
        "file": path.name, "sha256": sha256(path), "rows_raw": int(len(df)),
        "rows_valid": int(len(out)), "invalid_ohlc_removed": invalid,
        "start_utc": out.index.min().isoformat() if len(out) else None,
        "end_utc": out.index.max().isoformat() if len(out) else None,
    }


def paired_m5(bid_path: Path, ask_path: Path):
    bid, bdiag = read_side(bid_path, "bid")
    ask, adiag = read_side(ask_path, "ask")
    common = bid.index.intersection(ask.index).sort_values()
    union = bid.index.union(ask.index)
    bid_only = int(len(bid.index.difference(ask.index)))
    ask_only = int(len(ask.index.difference(bid.index)))
    pair = bid.loc[common].join(ask.loc[common], how="inner")
    if pair.empty:
        raise ValueError("No paired BID/ASK timestamps")
    seconds_bad = int(((pair.index.second != 0) | (pair.index.microsecond != 0)).sum())
    pair = pair.loc[(pair.index.second == 0) & (pair.index.microsecond == 0)]
    neg_open = int(((pair.open_ask + 1e-10) < pair.open_bid).sum())
    neg_close = int(((pair.close_ask + 1e-10) < pair.close_bid).sum())
    if neg_open or neg_close:
        raise ValueError(f"Negative open/close spread rows: open={neg_open}, close={neg_close}")
    # Build each minute's midpoint OHLC before aggregation. Averaging the
    # separately aggregated BID/ASK highs or lows can create a synthetic extreme
    # that never occurred on any paired minute.
    pair["mid_open"] = (pair.open_bid + pair.open_ask) / 2
    pair["mid_high"] = (pair.high_bid + pair.high_ask) / 2
    pair["mid_low"] = (pair.low_bid + pair.low_ask) / 2
    pair["mid_close"] = (pair.close_bid + pair.close_ask) / 2
    pair["bar5_utc"] = pair.index.floor("5min")
    grp = pair.groupby("bar5_utc", sort=True)
    counts = grp.size()
    complete_labels = counts.index[counts == 5]
    # Five unique minute timestamps in each 5-minute bin means the bar is complete.
    # Executable-side bars retain their own BID/ASK highs/lows for fills/diagnostics;
    # the signal uses max/min of actual per-minute midpoint highs/lows.
    m5 = grp.agg({
        "open_bid":"first", "high_bid":"max", "low_bid":"min", "close_bid":"last",
        "open_ask":"first", "high_ask":"max", "low_ask":"min", "close_ask":"last",
        "mid_open":"first", "mid_high":"max", "mid_low":"min", "mid_close":"last"
    }).loc[complete_labels].copy()
    m5.index = pd.DatetimeIndex(m5.index, name="bar_open_utc")
    m5["local"] = m5.index.tz_convert(NY)
    m5["session_date"] = [x.date().isoformat() for x in m5["local"]]
    m5["local_hhmm"] = [x.strftime("%H:%M") for x in m5["local"]]
    m5["in_rth"] = [
        (x.hour > 9 or (x.hour == 9 and x.minute >= 30)) and
        (x.hour < 16) for x in m5["local"]
    ]
    m5 = m5.loc[m5.in_rth].copy()
    # No out-of-session bar may count as an RTH bar.
    return m5, {
        "bid": bdiag, "ask": adiag,
        "bid_only_timestamps": bid_only, "ask_only_timestamps": ask_only,
        "paired_rows": int(len(pair)), "paired_timestamp_union": int(len(union)),
        "minute_timestamps_with_nonzero_seconds": seconds_bad,
        "negative_open_spread_rows": neg_open, "negative_close_spread_rows": neg_close,
        "complete_m5_bars_all_sessions": int(len(complete_labels)),
        "complete_m5_bars_rth": int(len(m5)),
        "m5_bins_with_incomplete_minute_coverage": int((counts != 5).sum()),
        "start_m5_utc": m5.index.min().isoformat() if len(m5) else None,
        "end_m5_utc": m5.index.max().isoformat() if len(m5) else None,
    }


def read_vxn(path: Path):
    if not path.is_file():
        raise FileNotFoundError(path)
    df = pd.read_csv(path, parse_dates=["date"])
    if list(df.columns) != ["date", "close"] or df.empty:
        raise ValueError("VXN CSV must have exact columns date,close and data rows")
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    if df[["date", "close"]].isna().any().any() or (df.close <= 0).any():
        raise ValueError("VXN CSV contains invalid dates/values")
    if df.date.duplicated().any():
        raise ValueError("VXN CSV contains duplicate dates")
    df = df.sort_values("date")
    return df, {
        "file": path.name, "sha256": sha256(path), "rows": int(len(df)),
        "first_date": df.date.min().date().isoformat(),
        "last_date": df.date.max().date().isoformat(),
        "unique_dates": int(df.date.nunique()),
    }


def week_monday(d: date) -> date:
    return d - timedelta(days=d.weekday())


def nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    first = date(year, month, 1)
    delta = (weekday - first.weekday()) % 7
    return first + timedelta(days=delta + 7 * (n - 1))


def last_weekday(year: int, month: int, weekday: int) -> date:
    last_day = date(year + (month == 12), 1 if month == 12 else month + 1, 1) - timedelta(days=1)
    delta = (last_day.weekday() - weekday) % 7
    return last_day - timedelta(days=delta)


def easter_sunday(year: int) -> date:
    # Gregorian computus (Meeus/Jones/Butcher).
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def observed_fixed(year: int, month: int, day: int) -> date:
    d = date(year, month, day)
    if d.weekday() == 5:
        return d - timedelta(days=1)
    if d.weekday() == 6:
        return d + timedelta(days=1)
    return d


def nyse_calendar(start: date, end: date):
    """Small explicit NYSE regular/early-close calendar for R331's 2023–2026 window."""
    holidays = set()
    early_closes = set()
    for y in range(start.year - 1, end.year + 2):
        for month, day in ((1, 1), (6, 19), (7, 4), (12, 25)):
            holidays.add(observed_fixed(y, month, day))
        holidays.add(nth_weekday(y, 1, 0, 3))       # MLK Day
        holidays.add(nth_weekday(y, 2, 0, 3))       # Presidents' Day
        holidays.add(easter_sunday(y) - timedelta(days=2))  # Good Friday
        holidays.add(last_weekday(y, 5, 0))         # Memorial Day
        holidays.add(nth_weekday(y, 9, 0, 1))       # Labor Day
        thanksgiving = nth_weekday(y, 11, 3, 4)
        holidays.add(thanksgiving)
        early_closes.add(thanksgiving + timedelta(days=1))
        christmas_eve = date(y, 12, 24)
        if christmas_eve.weekday() < 5:
            early_closes.add(christmas_eve)
        july4_obs = observed_fixed(y, 7, 4)
        candidate = july4_obs - timedelta(days=1)
        while candidate.weekday() >= 5 or candidate in holidays:
            candidate -= timedelta(days=1)
        early_closes.add(candidate)
    holidays.add(date(2025, 1, 9))  # US equity-market closure for President Carter's state funeral
    holidays = {d for d in holidays if start - timedelta(days=7) <= d <= end + timedelta(days=7)}
    early_closes = {d for d in early_closes if start <= d <= end and d not in holidays}
    trading_dates = []
    d = start
    while d <= end:
        if d.weekday() < 5 and d not in holidays:
            trading_dates.append(d)
        d += timedelta(days=1)
    return trading_dates, holidays, early_closes


def bootstrap_mean_ci(weekly: list[float], reps=BOOTSTRAP_REPS, block=BOOTSTRAP_BLOCK_WEEKS, seed=BOOTSTRAP_SEED):
    arr = np.asarray(weekly, dtype=float)
    if len(arr) < block:
        return {"reps": reps, "block_weeks": block, "seed": seed, "ci95_bps": None}
    rng = np.random.default_rng(seed)
    n = len(arr)
    nblocks = int(math.ceil(n / block))
    means = np.empty(reps)
    for r in range(reps):
        starts = rng.integers(0, n, size=nblocks)
        ix = np.concatenate([((s + np.arange(block)) % n) for s in starts])[:n]
        means[r] = arr[ix].mean()
    return {
        "reps": reps, "block_weeks": block, "seed": seed,
        "ci95_bps": [float(np.quantile(means, 0.025)), float(np.quantile(means, 0.975))],
        "bootstrap_probability_mean_positive": float((means > 0).mean()),
    }


def metric_summary(ledger: pd.DataFrame, partition: str, delay: str, cost_bps: float, date_start: date, date_end: date):
    key = "primary" if delay == "primary" else "ideal"
    ev = ledger.loc[
        (ledger.partition == partition) & ledger["status"].eq("TRADE") & ledger[f"{key}_gross_bps"].notna()
    ].copy()
    net = ev[f"{key}_gross_bps"].astype(float) - cost_bps
    ev["net_bps"] = net
    ev["week_start"] = pd.to_datetime(ev.session_date).dt.date.map(week_monday)
    start_monday = week_monday(date_start)
    end_monday = week_monday(date_end)
    weeks = []
    monday = start_monday
    while monday <= end_monday:
        weeks.append(monday)
        monday += timedelta(days=7)
    weekly = ev.groupby("week_start").net_bps.sum().to_dict()
    weekly_vals = [float(weekly.get(w, 0.0)) for w in weeks]
    positive = float(net[net > 0].sum())
    negative = float(-net[net < 0].sum())
    # Chronological event-return curve, used only as a descriptive trade-sequence DD.
    eq = np.cumsum(net.to_numpy()) if len(net) else np.array([])
    if len(eq):
        peak = np.maximum.accumulate(np.maximum(eq, 0.0))
        dd = eq - peak
        maxdd = float(dd.min())
    else:
        maxdd = 0.0
    return {
        "partition": partition, "entry_method": delay, "extra_round_trip_cost_bps": cost_bps,
        "events": int(len(ev)),
        "gross_total_bps": float(ev[f"{key}_gross_bps"].sum()) if len(ev) else 0.0,
        "net_total_bps": float(net.sum()) if len(net) else 0.0,
        "net_mean_bps_per_event": float(net.mean()) if len(net) else None,
        "net_median_bps_per_event": float(net.median()) if len(net) else None,
        "net_win_rate": float((net > 0).mean()) if len(net) else None,
        "profit_factor_events": positive / negative if negative > 0 else None,
        "max_drawdown_cumulative_event_bps": maxdd,
        "weeks_zero_inclusive": len(weeks),
        "mean_net_bps_per_week": float(np.mean(weekly_vals)) if weekly_vals else None,
        "median_net_bps_per_week": float(np.median(weekly_vals)) if weekly_vals else None,
        "positive_week_rate": float(np.mean(np.asarray(weekly_vals) > 0)) if weekly_vals else None,
        "bootstrap_mean_week_ci95": bootstrap_mean_ci(weekly_vals),
        "weekly_net_bps": [{"week_start": w.isoformat(), "net_bps": v} for w, v in zip(weeks, weekly_vals)],
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bid", required=True, type=Path)
    ap.add_argument("--ask", required=True, type=Path)
    ap.add_argument("--vxn", required=True, type=Path)
    ap.add_argument("--out-dir", required=True, type=Path)
    args = ap.parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)

    m5, pdiag = paired_m5(args.bid, args.ask)
    vxn, vdiag = read_vxn(args.vxn)
    vxn_map = {r.date.date(): float(r.close) for r in vxn.itertuples(index=False)}
    vxn_dates = sorted(vxn_map)
    sessions = {}
    invalid_sessions = {}
    trading_dates, market_holidays, early_closes = nyse_calendar(DATA_START, END.date())
    # A trading-day VXN observation missing inside the registered signal window is
    # a source-data failure; the strategy may never carry a stale volatility close forward.
    vxn_missing_expected = [
        x.isoformat() for x in trading_dates
        if START.date() <= x <= END.date() and x >= vxn_dates[0] and x not in vxn_map
    ]
    if vxn_missing_expected:
        raise ValueError("GAGAL — DATA/PROCESS: VXN is missing expected NYSE daily closes, first="
                         + ",".join(vxn_missing_expected[:20]) + f"; count={len(vxn_missing_expected)}")
    rth_labels_by_day = {}
    for td in trading_dates:
        close_time = "13:00" if td in early_closes else "16:00"
        rth_labels_by_day[td.isoformat()] = [
            t.strftime("%H:%M")
            for t in pd.date_range("2000-01-03 09:30", f"2000-01-03 {close_time}", freq="5min", inclusive="left")
        ]
    observed_by_day = {k: g.sort_values("local").copy() for k, g in m5.groupby("session_date", sort=True)}
    no_session_data = [d.isoformat() for d in trading_dates if d.isoformat() not in observed_by_day]
    if no_session_data:
        raise ValueError("GAGAL — DATA/PROCESS: no RTH quote bars for expected NYSE sessions, first="
                         + ",".join(no_session_data[:20]) + f"; count={len(no_session_data)}")
    for td in trading_dates:
        day = td.isoformat()
        if day not in observed_by_day:
            continue
        g = observed_by_day[day]
        expected_labels = rth_labels_by_day[day]
        have = set(g.local_hhmm)
        missing = [x for x in expected_labels if x not in have]
        session_rows = g.loc[g.local_hhmm.isin(expected_labels)].copy()
        if len(session_rows) != len(expected_labels) or missing:
            invalid_sessions[day] = {"reason": "INCOMPLETE_RTH_M5_SESSION", "m5_bars": int(len(session_rows)),
                                     "expected_m5_bars": len(expected_labels), "missing_labels": missing}
        else:
            sessions[day] = session_rows.sort_values("local")

    trading_date_strs = [x.isoformat() for x in trading_dates]
    ledger_rows = []
    skip_counts = {}
    def emit(row):
        ledger_rows.append(row)
        if row.get("status") != "TRADE":
            reason = str(row.get("reason", row.get("status", "UNKNOWN")))
            skip_counts[reason] = skip_counts.get(reason, 0) + 1

    dates_to_evaluate = [x.isoformat() for x in trading_dates if START.date() <= x <= END.date()]
    for dstr in dates_to_evaluate:
        d = date.fromisoformat(dstr)
        partition = "discovery" if d <= DISCOVERY_END.date() else "confirmation" if d >= CONFIRM_START.date() else "embargo"
        if partition == "embargo":
            emit({"session_date": dstr, "partition": partition, "status": "NOT_SCORED", "reason": "PARTITION_BOUNDARY"})
            continue
        if d not in sessions:
            emit({"session_date": dstr, "partition": partition, "status": "SKIP", "reason": invalid_sessions.get(dstr, {}).get("reason", "INCOMPLETE_RTH_M5_SESSION"),
                  "rth_m5_bars": invalid_sessions.get(dstr, {}).get("m5_bars", 0)})
            continue
        earlier = [x for x in trading_date_strs if x < dstr]
        if not earlier:
            emit({"session_date": dstr, "partition": partition, "status": "SKIP", "reason": "NO_PREVIOUS_SESSION"})
            continue
        prev_date = earlier[-1]
        if prev_date not in sessions:
            emit({"session_date": dstr, "partition": partition, "status": "SKIP", "reason": "PREVIOUS_SESSION_INCOMPLETE", "previous_session_date": prev_date})
            continue
        # Strictly prior VXN date; no same-session VXN and no forward fill.
        prior_vxn_dates = [x for x in vxn_dates if x < d]
        if not prior_vxn_dates:
            emit({"session_date": dstr, "partition": partition, "status": "SKIP", "reason": "NO_PRIOR_VXN"})
            continue
        vxn_date = prior_vxn_dates[-1]
        vx = vxn_map[vxn_date]
        if 20 <= vx < 30:
            emit({"session_date": dstr, "partition": partition, "status": "NO_TRADE", "reason": "VXN_REGIME_OFF",
                  "previous_session_date": prev_date, "vxn_source_date": vxn_date, "regime": "middle"})
            continue
        regime = "low" if vx < 20 else "high"
        previous_close_label = rth_labels_by_day[prev_date][-1]
        prior_close = float(sessions[prev_date].loc[
            sessions[prev_date].local_hhmm.eq(previous_close_label), "mid_close"
        ].iloc[0])
        upper = prior_close * (1.0 + vx / 1600.0)
        lower = prior_close * (1.0 - vx / 1600.0)
        g = sessions[dstr]
        candidate = None
        ambiguous = None
        for ix, bar in g.iterrows():
            if bar.mid_high >= upper and bar.mid_low <= lower:
                ambiguous = ix
                break
            if bar.mid_high >= upper:
                candidate = (ix, bar, -1, "upper")
                break
            if bar.mid_low <= lower:
                candidate = (ix, bar, 1, "lower")
                break
        if ambiguous is not None:
            emit({"session_date": dstr, "partition": partition, "status": "SKIP", "reason": "SAME_BAR_TWO_SIDED_BREACH",
                  "previous_session_date": prev_date, "vxn_source_date": vxn_date, "regime": regime})
            continue
        if candidate is None:
            emit({"session_date": dstr, "partition": partition, "status": "NO_TRADE", "reason": "NO_BAND_BREACH",
                  "previous_session_date": prev_date, "vxn_source_date": vxn_date, "regime": regime})
            continue
        signal_ts, signal_bar, direction, breach_side = candidate
        loc_signal = signal_bar.local
        # signal bar label is its 5-min open; completion occurs exactly 5 minutes later.
        ideal_ts = signal_ts + pd.Timedelta(minutes=5)
        primary_ts = signal_ts + pd.Timedelta(minutes=10)
        ideal_exit_ts = ideal_ts + pd.Timedelta(minutes=30)
        primary_exit_ts = primary_ts + pd.Timedelta(minutes=30)
        bars_by_utc = {ix: row for ix, row in g.iterrows()}
        def fill_for(entry_ts, exit_ts):
            if entry_ts not in bars_by_utc or exit_ts not in bars_by_utc:
                return None
            entry_bar = bars_by_utc[entry_ts]
            exit_bar = bars_by_utc[exit_ts]
            session_close = "13:00" if d in early_closes else "16:00"
            latest_entry = (pd.Timestamp(f"{dstr} {session_close}", tz=NY) - pd.Timedelta(minutes=30)).strftime("%H:%M")
            last_exit_open = (pd.Timestamp(f"{dstr} {session_close}", tz=NY) - pd.Timedelta(minutes=5)).strftime("%H:%M")
            if entry_bar.local.strftime("%H:%M") > latest_entry or exit_bar.local.strftime("%H:%M") > last_exit_open:
                return None
            entry_px = float(entry_bar.open_ask if direction == 1 else entry_bar.open_bid)
            exit_px = float(exit_bar.open_bid if direction == 1 else exit_bar.open_ask)
            if not (entry_px > 0 and exit_px > 0):
                return None
            ret = ((exit_px - entry_px) / entry_px) * direction * 10000.0
            return {"entry_timestamp": entry_ts, "exit_timestamp": exit_ts,
                    "entry_price": entry_px, "exit_price": exit_px, "gross_bps": float(ret)}
        ideal_fill = fill_for(ideal_ts, ideal_exit_ts)
        primary_fill = fill_for(primary_ts, primary_exit_ts)
        if primary_fill is None:
            emit({"session_date": dstr, "partition": partition, "status": "SKIP", "reason": "NO_EXACT_DELAYED_ENTRY_OR_EXIT",
                  "previous_session_date": prev_date, "vxn_source_date": vxn_date, "regime": regime,
                  "signal_time_et": loc_signal.isoformat(), "breach_side": breach_side})
            continue
        emit({
            "session_date": dstr, "partition": partition, "status": "TRADE", "reason": "",
            "previous_session_date": prev_date, "vxn_source_date": vxn_date,
            "regime": regime, "direction": "LONG" if direction == 1 else "SHORT",
            "breach_side": breach_side, "signal_time_et": loc_signal.isoformat(),
            "ideal_entry_time_et": ideal_ts.tz_convert(NY).isoformat(),
            "ideal_exit_time_et": ideal_exit_ts.tz_convert(NY).isoformat(),
            "ideal_gross_bps": ideal_fill["gross_bps"] if ideal_fill else None,
            "primary_entry_time_et": primary_fill["entry_timestamp"].tz_convert(NY).isoformat(),
            "primary_exit_time_et": primary_fill["exit_timestamp"].tz_convert(NY).isoformat(),
            "primary_entry_price": primary_fill["entry_price"],
            "primary_exit_price": primary_fill["exit_price"],
            "primary_gross_bps": primary_fill["gross_bps"],
            # Do not disclose the actual VXN close or derived upper/lower band in public ledgers.
        })

    ledger = pd.DataFrame(ledger_rows)
    for required_col in ("primary_gross_bps", "ideal_gross_bps"):
        if required_col not in ledger.columns:
            ledger[required_col] = np.nan
    ledger_path = args.out_dir / "r331_session_event_ledger_local.csv"
    ledger.to_csv(ledger_path, index=False)
    # The public artifact later commits a redacted event ledger; raw quote and VXN values remain local.
    date_start = START.date()
    results = {}
    for partition, lo, hi in [
        ("discovery", START.date(), DISCOVERY_END.date()),
        ("confirmation", CONFIRM_START.date(), END.date()),
    ]:
        results[partition] = {}
        for entry_method in ("primary", "ideal"):
            results[partition][entry_method] = {}
            for cost in COSTS_BPS:
                results[partition][entry_method][str(cost)] = metric_summary(
                    ledger, partition, entry_method, cost, lo, hi
                )
        # Event count is the primary delayed-fill stream before cost.
        count = int(((ledger.partition == partition) & ledger.status.eq("TRADE") & ledger.primary_gross_bps.notna()).sum())
        results[partition]["eligible_events_primary"] = count
        results[partition]["eligible_sessions"] = int((ledger.partition == partition).sum())

    p = results["confirmation"]["primary"]["5.0"]
    d = results["discovery"]["primary"]["5.0"]
    s = results["confirmation"]["primary"]["10.0"]
    sample_ok = results["discovery"]["eligible_events_primary"] >= 50 and results["confirmation"]["eligible_events_primary"] >= 50
    if not sample_ok:
        verdict = "GAGAL — SAMPLE/TARGET FEASIBILITY"
    elif (d["net_total_bps"] > 0 and p["net_total_bps"] > 0 and
          p["bootstrap_mean_week_ci95"]["ci95_bps"] is not None and
          p["bootstrap_mean_week_ci95"]["ci95_bps"][0] > 0 and
          s["net_total_bps"] > 0 and p["net_mean_bps_per_event"] > 0):
        verdict = "PASS — SCREEN ONLY"
    else:
        verdict = "GAGAL — ECONOMIC SCREEN"

    public_sessions = ledger.copy()
    # Public ledger excludes any raw VXN values or derived band levels; only date key and categorical state remain.
    public_sessions_path = args.out_dir / "r331_session_event_ledger_redacted.csv"
    public_sessions.to_csv(public_sessions_path, index=False)
    summary = {
        "experiment": "R331",
        "binary_verdict": verdict,
        "claim_boundary": "Initial screen only; not FundedNext-ready; not a two-phase challenge replay.",
        "market_data": pdiag,
        "vxn_data": {
            **{k:v for k,v in vdiag.items() if k != "file"},
            "source_mirror_url": "https://github.com/fuxui/vix-vxn/blob/main/data/history.json",
            "source_original_url": "https://cdn.cboe.com/api/global/us_indices/daily_prices/VXN_History.csv",
            "raw_values_published": False,
            "limitation": "Public mirror; not an authenticated point-in-time vendor feed. Daily observation coverage 2023-10-25 to 2026-10-21."
        },
        "mechanics": {
            "session_timezone": NY, "regular_hours": "09:30-16:00 ET",
            "expected_regular_session_m5_bars": "78 for full days 09:30-16:00; 42 for scheduled half-days 09:30-13:00",
            "market_calendar": "explicit NYSE holidays, Good Friday, MLK/Presidents/Memorial/Labor/Thanksgiving/Christmas/Independence; half-days after Thanksgiving, eligible Christmas Eve/July 4; 2025-01-09 Carter funeral closure",
            "signal_reference": "prior valid regular-session midpoint close",
            "vxn_join": "latest VXN date strictly earlier than session date",
            "upper_lower_band": "prior midpoint close * (1 +/- VXN/1600)",
            "regime": "trade only VXN<20 or VXN>=30; [20,30) flat",
            "entry_primary": "signal M5 label +10 minutes (one extra 5m bar after ideal next-bar open)",
            "exit": "exactly 30 minutes after selected entry at M5 open; no exit outside regular hours",
            "entry_exit_quote_sides": "long ASK entry/BID exit; short BID entry/ASK exit",
            "cost_round_trip_bps": list(COSTS_BPS),
            "bootstrap": {"reps": BOOTSTRAP_REPS, "block_weeks": BOOTSTRAP_BLOCK_WEEKS, "seed": BOOTSTRAP_SEED},
            "discovery_period": f"{START.date()}..{DISCOVERY_END.date()}",
            "confirmation_period": f"{CONFIRM_START.date()}..{END.date()}",
        },
        "event_counts": {
            "ledger_sessions": int(len(ledger)),
            "trades_primary": {k: int(v["eligible_events_primary"]) for k,v in results.items()},
            "skip_no_trade_reasons": skip_counts,
            "invalid_sessions": len(invalid_sessions),
            "valid_sessions": len(sessions),
        },
        "partition_results": results,
        "promotion_limit": "A screen PASS must be independently reproduced and followed by exact FundedNext CFD spread/commission/swap verification, 5-minute entry execution validation, risk/exit design, floating-equity daily/max-loss simulation and complete two-phase challenge replay. No pass probability is inferred from this screen.",
        "source_hashes": {
            "bid_gzip_sha256": pdiag["bid"]["sha256"],
            "ask_gzip_sha256": pdiag["ask"]["sha256"],
            "vxn_local_csv_sha256": vdiag["sha256"],
        },
        "local_event_ledger_sha256": sha256(ledger_path),
        "redacted_event_ledger_sha256": sha256(public_sessions_path),
    }
    out_json = args.out_dir / "r331_results_local.json"
    out_json.write_text(json.dumps(summary, indent=2, default=str) + "\n")
    print(json.dumps({
        "binary_verdict": verdict,
        "data": {k: v for k, v in pdiag.items() if k not in ("bid","ask")},
        "vxn": vdiag,
        "discovery_primary_events": results["discovery"]["eligible_events_primary"],
        "confirmation_primary_events": results["confirmation"]["eligible_events_primary"],
        "discovery_primary_5bps": {k: v for k,v in results["discovery"]["primary"]["5.0"].items() if k not in ("weekly_net_bps",)},
        "confirmation_primary_5bps": {k: v for k,v in results["confirmation"]["primary"]["5.0"].items() if k not in ("weekly_net_bps",)},
        "confirmation_stress_10bps": {k:v for k,v in results["confirmation"]["primary"]["10.0"].items() if k not in ("weekly_net_bps",)},
        "result_json_sha256": sha256(out_json),
        "ledger_sha256_local": sha256(ledger_path),
        "public_redacted_ledger_sha256": sha256(public_sessions_path),
        "output_json": str(out_json),
        "local_ledger": str(ledger_path),
        "redacted_ledger": str(public_sessions_path),
    }, indent=2, default=str))


if __name__ == "__main__":
    main()
