"""Build conservative OPEN/MARK/EXIT events from paired BID/ASK OHLC and a locked trade ledger.

This is infrastructure only. It does not create signals, infer absent candles, or decide a
trade's historical exit. The trade ledger must come from a separately frozen strategy runner.
Every active M5 bar contributes an adverse-side price mark, stop/target intrabar conflicts must
already be resolved by the runner using stop-first policy, and gap/time exits are tagged as
exiting at the bar open.
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

OHLC = ["open", "high", "low", "close"]
TRADE_COLUMNS = [
    "trade_id", "direction", "entry_time_utc", "exit_time_utc",
    "entry_price", "exit_price", "stop_price", "exit_reason",
]


def _timestamps(series: pd.Series, label: str) -> pd.DatetimeIndex:
    """Parse Unix milliseconds or timezone-aware text; reject naive timestamp text."""
    if pd.api.types.is_numeric_dtype(series):
        idx = pd.DatetimeIndex(pd.to_datetime(series, unit="ms", utc=True, errors="coerce"))
    else:
        text = series.astype(str).str.strip()
        has_tz = text.str.contains(r"(?:Z|[+-]\d{2}:?\d{2})$", case=False, regex=True)
        if not bool(has_tz.all()):
            raise ValueError(f"{label}: timestamps must include UTC Z or an explicit offset")
        idx = pd.DatetimeIndex(pd.to_datetime(series, utc=True, errors="coerce"))
    if idx.isna().any():
        raise ValueError(f"{label}: invalid timestamp values")
    return idx


def _read_side(path: str | Path, side: str, cutoff_utc: str | None) -> pd.DataFrame:
    df = pd.read_csv(path, compression="infer")
    if "timestamp" not in df.columns:
        raise ValueError(f"{side}: missing timestamp column")
    missing = [c for c in OHLC if c not in df.columns]
    if missing:
        raise ValueError(f"{side}: missing OHLC columns {missing}")
    idx = _timestamps(df["timestamp"], side)
    df = df[OHLC].copy()
    for col in OHLC:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df.index = idx
    df.index.name = "timestamp_utc"

    # Apply the protected cutoff before price/event construction.
    if cutoff_utc:
        cutoff = pd.Timestamp(cutoff_utc)
        if cutoff.tzinfo is None:
            raise ValueError("cutoff_utc must include Z or explicit UTC offset")
        df = df.loc[df.index < cutoff.tz_convert("UTC")]

    if df.index.has_duplicates:
        raise ValueError(f"{side}: duplicate timestamps after cutoff")
    if not df.index.is_monotonic_increasing:
        raise ValueError(f"{side}: timestamps are not strictly increasing")
    vals = df[OHLC].to_numpy(dtype="float64")
    if not bool(pd.notna(df[OHLC]).all().all()) or not bool(pd.Series(vals.ravel()).map(math.isfinite).all()):
        raise ValueError(f"{side}: missing/non-finite OHLC values")
    invalid = (
        (df["high"] < df[["open", "close"]].max(axis=1))
        | (df["low"] > df[["open", "close"]].min(axis=1))
        | (df["high"] < df["low"])
    )
    if bool(invalid.any()):
        raise ValueError(f"{side}: {int(invalid.sum())} invalid OHLC rows")
    return df.add_prefix(f"{side}_")


def load_paired_bars(
    bid_path: str | Path,
    ask_path: str | Path,
    *,
    cutoff_utc: str | None = None,
    bar_minutes: int = 5,
) -> pd.DataFrame:
    """Load exact paired BID/ASK bars and fail closed on timestamp mismatches."""
    if bar_minutes <= 0:
        raise ValueError("bar_minutes must be positive")
    bid = _read_side(bid_path, "bid", cutoff_utc)
    ask = _read_side(ask_path, "ask", cutoff_utc)
    bid_only = bid.index.difference(ask.index)
    ask_only = ask.index.difference(bid.index)
    if len(bid_only) or len(ask_only):
        raise ValueError(
            f"BID/ASK timestamps mismatch after cutoff: bid_only={len(bid_only)}, ask_only={len(ask_only)}"
        )
    bars = bid.join(ask, how="inner", validate="one_to_one").sort_index()
    if bars.empty:
        raise ValueError("no paired bars remain after cutoff")
    if bool((bars["ask_open"] < bars["bid_open"]).any()):
        raise ValueError("ASK open below BID open")
    if bool((bars["ask_close"] < bars["bid_close"]).any()):
        raise ValueError("ASK close below BID close")
    bars.attrs["bar_minutes"] = int(bar_minutes)
    bars.attrs["cutoff_utc"] = cutoff_utc
    return bars


def _dt(value: Any, label: str) -> pd.Timestamp:
    ts = pd.Timestamp(value)
    if ts.tzinfo is None:
        raise ValueError(f"{label}: timestamp must be timezone-aware: {value!r}")
    return ts.tz_convert("UTC")


def _as_bool(value: Any, default: bool = False) -> bool:
    if value is None or (isinstance(value, float) and math.isnan(value)) or str(value).strip() == "":
        return default
    if isinstance(value, bool):
        return value
    value = str(value).strip().lower()
    if value in {"1", "true", "yes", "y"}:
        return True
    if value in {"0", "false", "no", "n"}:
        return False
    raise ValueError(f"cannot parse boolean value {value!r}")


def _price_row(bars: pd.DataFrame, ts: pd.Timestamp, direction: str) -> dict[str, float]:
    row = bars.loc[ts]
    prefix = "bid" if direction == "LONG" else "ask"
    return {col: float(row[f"{prefix}_{col}"]) for col in OHLC}


def build_challenge_events(
    trades: pd.DataFrame | Iterable[dict[str, Any]],
    bars: pd.DataFrame,
    *,
    default_risk_pct: float = 0.005,
    default_added_cost_price_units: float = 0.0,
    entry_price_tolerance: float = 0.001,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Convert a fixed price ledger into conservative challenge-engine events.

    Required trade columns: trade_id, direction (LONG/SHORT), entry_time_utc, exit_time_utc,
    entry_price, exit_price, stop_price, exit_reason. Optional: risk_pct,
    added_cost_price_units, exit_at_open, exit_fill_type, target_price.

    added_cost_price_units is a round-trip friction expressed in the instrument's price units
    (e.g. $0.30/oz for XAUUSD). The full incremental friction is charged from entry onward,
    intentionally conservative for the intratrade rule path. Observed BID/ASK is represented
    directly by side-specific entry and mark prices. Account commissions/swaps must be converted
    to a per-unit price equivalent by a verified instrument/account adapter before using this.

    exit_fill_type=OPEN means exit at executable open (time exit/gap stop); INTRABAR means the
    locked strategy's intrabar fill, after a conservative adverse mark; TARGET_CAP means a
    favorable target gap filled at the locked target price. The strategy runner must already
    resolve same-bar stop/target ambiguity as stop-first.
    """
    if not 0 < default_risk_pct < 1:
        raise ValueError("default_risk_pct must be between 0 and 1")
    if default_added_cost_price_units < 0:
        raise ValueError("added cost cannot be negative")
    if entry_price_tolerance < 0:
        raise ValueError("entry_price_tolerance cannot be negative")
    if not isinstance(trades, pd.DataFrame):
        trades = pd.DataFrame(list(trades))
    missing = [c for c in TRADE_COLUMNS if c not in trades.columns]
    if missing:
        raise ValueError(f"trade ledger missing required columns: {missing}")
    if bars.empty or not isinstance(bars.index, pd.DatetimeIndex) or bars.index.tz is None:
        raise ValueError("bars must have a non-empty timezone-aware DatetimeIndex")
    if bars.index.has_duplicates or not bars.index.is_monotonic_increasing:
        raise ValueError("bars index must be unique and increasing")
    step = pd.Timedelta(minutes=int(bars.attrs.get("bar_minutes", 5)))
    event_rows: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    grid_gaps = 0
    entry_side_checks = 0
    open_exit_count = 0
    target_cap_exit_count = 0
    intrabar_exit_count = 0
    trades_used = 0

    # Sorting input ledger makes generated same-time event ordering deterministic.
    work = trades.copy()
    work["_entry"] = work["entry_time_utc"].map(lambda x: _dt(x, "entry_time_utc"))
    work["_exit"] = work["exit_time_utc"].map(lambda x: _dt(x, "exit_time_utc"))
    work = work.sort_values(["_entry", "_exit", "trade_id"], kind="stable")

    for _, tr in work.iterrows():
        tid = str(tr["trade_id"]).strip()
        if not tid or tid.lower() == "nan" or tid in seen_ids:
            raise ValueError(f"trade_id must be non-empty and unique: {tid!r}")
        seen_ids.add(tid)
        direction = str(tr["direction"]).strip().upper()
        if direction not in {"LONG", "SHORT"}:
            raise ValueError(f"{tid}: direction must be LONG or SHORT")
        entry_ts, exit_ts = tr["_entry"], tr["_exit"]
        if exit_ts <= entry_ts:
            raise ValueError(f"{tid}: exit must be later than entry")
        if entry_ts not in bars.index or exit_ts not in bars.index:
            raise ValueError(f"{tid}: entry/exit timestamp must map to exact observed bar opens")
        risk_pct = float(tr.get("risk_pct", default_risk_pct))
        if not 0 < risk_pct < 1:
            raise ValueError(f"{tid}: risk_pct must be between 0 and 1")
        entry = float(tr["entry_price"])
        exit_price = float(tr["exit_price"])
        stop = float(tr["stop_price"])
        stop_distance = abs(entry - stop)
        if not all(math.isfinite(x) for x in (entry, exit_price, stop, stop_distance)) or stop_distance <= 0:
            raise ValueError(f"{tid}: invalid entry/exit/stop prices")
        if (direction == "LONG" and stop >= entry) or (direction == "SHORT" and stop <= entry):
            raise ValueError(f"{tid}: stop lies on the wrong side of entry")
        entry_prefix = "ask" if direction == "LONG" else "bid"
        expected_entry = float(bars.loc[entry_ts, f"{entry_prefix}_open"])
        if abs(entry - expected_entry) > entry_price_tolerance:
            raise ValueError(
                f"{tid}: entry price {entry} does not match executable {entry_prefix.upper()} open "
                f"{expected_entry} at {entry_ts.isoformat()}"
            )
        entry_side_checks += 1

        requested_open = _as_bool(tr.get("exit_at_open"), default=False)
        fill_type = str(tr.get("exit_fill_type", "OPEN" if requested_open else "INTRABAR")).strip().upper()
        if fill_type not in {"OPEN", "INTRABAR", "TARGET_CAP"}:
            raise ValueError(f"{tid}: exit_fill_type must be OPEN, INTRABAR or TARGET_CAP")
        if requested_open and fill_type == "INTRABAR":
            raise ValueError(f"{tid}: exit_at_open conflicts with exit_fill_type=INTRABAR")
        if fill_type == "OPEN":
            exit_at_open = True
            exit_prefix = "bid" if direction == "LONG" else "ask"
            expected_exit = float(bars.loc[exit_ts, f"{exit_prefix}_open"])
            if abs(exit_price - expected_exit) > entry_price_tolerance:
                raise ValueError(
                    f"{tid}: open exit price {exit_price} does not match executable {exit_prefix.upper()} "
                    f"open {expected_exit} at {exit_ts.isoformat()}"
                )
            open_exit_count += 1
        elif fill_type == "TARGET_CAP":
            if not requested_open:
                raise ValueError(f"{tid}: TARGET_CAP must be marked exit_at_open=true")
            if "target_price" not in tr or pd.isna(tr["target_price"]):
                raise ValueError(f"{tid}: TARGET_CAP requires target_price")
            target = float(tr["target_price"])
            exit_prefix = "bid" if direction == "LONG" else "ask"
            open_price = float(bars.loc[exit_ts, f"{exit_prefix}_open"])
            favorable_gap = open_price >= target if direction == "LONG" else open_price <= target
            if not favorable_gap:
                raise ValueError(f"{tid}: TARGET_CAP selected but executable open did not gap favorably through target")
            if abs(exit_price - target) > entry_price_tolerance:
                raise ValueError(f"{tid}: TARGET_CAP exit price {exit_price} does not match target {target}")
            exit_at_open = True
            target_cap_exit_count += 1
        else:
            exit_at_open = False
            executable = _price_row(bars, exit_ts, direction)
            if exit_price < executable["low"] - entry_price_tolerance or exit_price > executable["high"] + entry_price_tolerance:
                raise ValueError(
                    f"{tid}: intrabar exit price {exit_price} is outside executable-side bar range "
                    f"[{executable['low']}, {executable['high']}]"
                )
            intrabar_exit_count += 1

        expected = pd.date_range(entry_ts, exit_ts, freq=step, tz="UTC")
        observed = bars.index[(bars.index >= entry_ts) & (bars.index <= exit_ts)]
        if len(expected) != len(observed) or not expected.equals(observed):
            grid_gaps += 1
            raise ValueError(
                f"{tid}: missing/inconsistent {step} timestamp grid between entry and exit; "
                f"expected={len(expected)} observed={len(observed)}"
            )

        extra_cost = tr.get("added_cost_price_units", default_added_cost_price_units)
        if pd.isna(extra_cost):
            extra_cost = default_added_cost_price_units
        extra_cost = float(extra_cost)
        if not math.isfinite(extra_cost) or extra_cost < 0:
            raise ValueError(f"{tid}: invalid added_cost_price_units")
        cost_r = extra_cost / stop_distance
        hold_seconds = float((exit_ts - entry_ts).total_seconds())
        raw_exit_r = ((exit_price - entry) if direction == "LONG" else (entry - exit_price)) / stop_distance
        realized_r = raw_exit_r - cost_r
        reason = str(tr["exit_reason"]).strip()

        event_rows.append({
            "timestamp_utc": entry_ts.isoformat(), "event_seq": 10, "event": "OPEN", "trade_id": tid,
            "risk_pct": risk_pct, "direction": direction, "source_bar_utc": entry_ts.isoformat(),
            "entry_price": entry, "stop_price": stop, "stop_distance": stop_distance,
        })

        # Each bar is treated conservatively: adverse executable-side extreme occurs first.
        # Exit-at-open events close before new entries and do not inspect that candle's later range.
        for ts in expected:
            if ts == exit_ts and exit_at_open:
                event_rows.append({
                    "timestamp_utc": ts.isoformat(), "event_seq": 5, "event": "EXIT", "trade_id": tid,
                    "realized_r": realized_r, "hold_seconds": hold_seconds, "exit_reason": reason,
                    "exit_price": exit_price, "raw_exit_r": raw_exit_r, "cost_r": cost_r,
                    "exit_at_open": True, "exit_fill_type": fill_type,
                })
                continue
            side = "bid" if direction == "LONG" else "ask"
            row = bars.loc[ts]
            adverse_price = float(row[f"{side}_low"] if direction == "LONG" else row[f"{side}_high"])
            floating_r = ((adverse_price - entry) if direction == "LONG" else (entry - adverse_price)) / stop_distance - cost_r
            event_rows.append({
                "timestamp_utc": ts.isoformat(), "event_seq": 20, "event": "MARK", "trade_id": tid,
                "floating_r": floating_r, "adverse_price": adverse_price, "direction": direction,
                "source_bar_utc": ts.isoformat(), "cost_r": cost_r,
            })
            if ts == exit_ts:
                event_rows.append({
                    "timestamp_utc": ts.isoformat(), "event_seq": 30, "event": "EXIT", "trade_id": tid,
                    "realized_r": realized_r, "hold_seconds": hold_seconds, "exit_reason": reason,
                    "exit_price": exit_price, "raw_exit_r": raw_exit_r, "cost_r": cost_r,
                    "exit_at_open": False, "exit_fill_type": fill_type,
                })
        trades_used += 1

    events = pd.DataFrame(event_rows)
    if not events.empty:
        events["_sort_time"] = pd.to_datetime(events["timestamp_utc"], utc=True)
        # EXIT-at-open before any new OPEN; OPEN before the bar's adverse MARK; intrabar EXIT after MARK.
        events = events.sort_values(["_sort_time", "event_seq", "trade_id"], kind="stable")
        events = events.drop(columns=["_sort_time"]).reset_index(drop=True)
    report = {
        "trade_count": trades_used,
        "event_count": int(len(events)),
        "entry_side_checks": entry_side_checks,
        "exit_at_open_count": open_exit_count,
        "target_cap_exit_count": target_cap_exit_count,
        "intrabar_exit_count": intrabar_exit_count,
        "grid_gaps": grid_gaps,
        "cutoff_utc": bars.attrs.get("cutoff_utc"),
        "bar_minutes": int(bars.attrs.get("bar_minutes", 5)),
        "mark_policy": "executable-side adverse OHLC extreme first; missing bars rejected; no synthetic bars",
        "extra_cost_policy": "full declared round-trip extra cost deducted from every mark for conservative risk checks and once from realized R",
    }
    return events, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bid_csv", help="BID OHLC CSV/CSV.GZ with timestamp milliseconds and OHLC")
    parser.add_argument("ask_csv", help="ASK OHLC CSV/CSV.GZ with timestamp milliseconds and OHLC")
    parser.add_argument("trades_csv", help="fixed trade ledger CSV")
    parser.add_argument("output_csv", help="output OPEN/MARK/EXIT event CSV")
    parser.add_argument("--cutoff-utc", default=None, help="exclusive cutoff, e.g. 2026-01-01T00:00:00Z")
    parser.add_argument("--bar-minutes", type=int, default=5)
    parser.add_argument("--risk-pct", type=float, default=0.005)
    parser.add_argument("--added-cost-price-units", type=float, default=0.0)
    args = parser.parse_args()
    bars = load_paired_bars(args.bid_csv, args.ask_csv, cutoff_utc=args.cutoff_utc, bar_minutes=args.bar_minutes)
    trades = pd.read_csv(args.trades_csv)
    events, report = build_challenge_events(
        trades, bars, default_risk_pct=args.risk_pct,
        default_added_cost_price_units=args.added_cost_price_units,
    )
    events.to_csv(args.output_csv, index=False)
    report_path = str(Path(args.output_csv).with_suffix(".audit.json"))
    import json
    Path(report_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps({**report, "output_csv": args.output_csv, "audit_json": report_path}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
