#!/usr/bin/env python3
"""Rebuild an account-event path from a frozen trade ledger, then replay the FundedNext rules.

This utility never generates signals or retunes trades. It consumes a completed, locked trade
ledger plus the exact observed BID/ASK archive; it writes a normalized trade ledger, chronological
OPEN/MARK/EXIT event path, adapter audit, and one deterministic challenge-path result.

R298 format uses side-correct fills from the existing locked ledger. This is a single historical
path, not a Monte Carlo pass-probability estimate. The 14-day cycle schedule is anchored to the
first accepted trade for an unphased ledger; if a first phase completes and phase 2 starts, the
path must be re-generated with the actual phase boundary before treating it as fully rule-complete.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from funded_path_adapter import load_paired_bars, build_challenge_events
from funded_challenge_simulator import ChallengeRules, simulate_challenge

R298_COLUMNS = {
    "index": "source_ledger_index",
    "direction": "direction",
    "entry_timestamp_utc": "entry_time_utc",
    "exit_timestamp_utc": "exit_time_utc",
    "entry_price_executable_side": "entry_price",
    "exit_price_executable_side": "exit_price",
    "stop_price_executable_side": "stop_price",
    "exit_type": "exit_reason",
    "target_price_midpoint": "target_price",
}


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def normalize_r298_ledger(
    ledger: pd.DataFrame,
    bars: pd.DataFrame,
    *,
    risk_pct: float = 0.005,
    added_cost_price_units: float = 0.30,
    entry_price_tolerance: float = 0.001,
) -> pd.DataFrame:
    """Map the locked R298 output ledger into the canonical adapter input schema.

    An exit counts as an executable-open fill only if its registered exit price equals
    the appropriate observed BID open for a long or ASK open for a short. R298 TIME exits
    must be open fills. STOP/TARGET fills at an intrabar level remain INTRABAR. Gap exits at
    an executable open are preserved at that open, matching the source runner.
    """
    missing = [c for c in R298_COLUMNS if c not in ledger.columns]
    if missing:
        raise ValueError(f"R298 trade ledger missing columns: {missing}")
    if not 0 < risk_pct < 1:
        raise ValueError("risk_pct must be between zero and one")
    if added_cost_price_units < 0:
        raise ValueError("added_cost_price_units cannot be negative")

    result = []
    seen = set()
    for row in ledger.to_dict("records"):
        source_idx = str(row["index"])
        trade_id = f"R298-{int(row['index']):04d}"
        if trade_id in seen:
            raise ValueError(f"duplicate source-ledger row: {trade_id}")
        seen.add(trade_id)
        direction = str(row["direction"]).strip().upper()
        if direction not in {"LONG", "SHORT"}:
            raise ValueError(f"{trade_id}: invalid direction {direction}")
        entry_ts = pd.Timestamp(row["entry_timestamp_utc"])
        exit_ts = pd.Timestamp(row["exit_timestamp_utc"])
        if entry_ts.tzinfo is None or exit_ts.tzinfo is None:
            raise ValueError(f"{trade_id}: timestamps must carry timezone offsets")
        entry_ts, exit_ts = entry_ts.tz_convert("UTC"), exit_ts.tz_convert("UTC")
        if entry_ts not in bars.index or exit_ts not in bars.index:
            raise ValueError(f"{trade_id}: entry/exit is not an exact observed bar timestamp")
        entry = float(row["entry_price_executable_side"])
        exit_price = float(row["exit_price_executable_side"])
        stop = float(row["stop_price_executable_side"])
        target = float(row["target_price_midpoint"])
        side = "bid" if direction == "LONG" else "ask"
        exit_open = float(bars.loc[exit_ts, f"{side}_open"])
        exit_at_open = abs(exit_price - exit_open) <= entry_price_tolerance
        exit_type = str(row["exit_type"]).strip().upper()
        if exit_type == "TIME" and not exit_at_open:
            raise ValueError(f"{trade_id}: TIME exit does not equal executable-side open")
        if not exit_at_open:
            executable = bars.loc[exit_ts]
            high = float(executable[f"{side}_high"])
            low = float(executable[f"{side}_low"])
            if not low - entry_price_tolerance <= exit_price <= high + entry_price_tolerance:
                raise ValueError(f"{trade_id}: intrabar fill is outside executable-side OHLC")
        result.append({
            "trade_id": trade_id,
            "source_ledger_index": source_idx,
            "direction": direction,
            "entry_time_utc": entry_ts.isoformat(),
            "exit_time_utc": exit_ts.isoformat(),
            "entry_price": entry,
            "exit_price": exit_price,
            "stop_price": stop,
            "target_price": target,
            "exit_reason": exit_type,
            "risk_pct": risk_pct,
            "added_cost_price_units": added_cost_price_units,
            "exit_at_open": bool(exit_at_open),
            "exit_fill_type": "OPEN" if exit_at_open else "INTRABAR",
        })
    return pd.DataFrame(result)


def replay(
    bid_path: str | Path,
    ask_path: str | Path,
    ledger_path: str | Path,
    out_dir: str | Path,
    *,
    ledger_format: str = "r298",
    cutoff_utc: str = "2026-01-01T00:00:00Z",
    initial_balance: float = 6000.0,
    risk_pct: float = 0.005,
    added_cost_price_units: float = 0.30,
    server_timezone: str = "Europe/Helsinki",
) -> dict[str, Any]:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    bid_path, ask_path, ledger_path = Path(bid_path), Path(ask_path), Path(ledger_path)
    bars = load_paired_bars(bid_path, ask_path, cutoff_utc=cutoff_utc, bar_minutes=5)
    raw_ledger = pd.read_csv(ledger_path)
    if ledger_format.lower() == "r298":
        normalized = normalize_r298_ledger(
            raw_ledger, bars, risk_pct=risk_pct,
            added_cost_price_units=added_cost_price_units,
        )
    elif ledger_format.lower() == "canonical":
        normalized = raw_ledger.copy()
        if "risk_pct" not in normalized.columns:
            normalized["risk_pct"] = risk_pct
        if "added_cost_price_units" not in normalized.columns:
            normalized["added_cost_price_units"] = added_cost_price_units
    else:
        raise ValueError("ledger_format must be r298 or canonical")

    normalized_path = out / "normalized_trade_ledger.csv"
    normalized.to_csv(normalized_path, index=False)
    events, adapter_audit = build_challenge_events(
        normalized, bars, default_risk_pct=risk_pct,
        default_added_cost_price_units=added_cost_price_units,
        server_timezone=server_timezone,
    )
    events_path = out / "challenge_event_path.csv"
    events.to_csv(events_path, index=False)

    rules = ChallengeRules(
        initial_balance=initial_balance,
        server_timezone=server_timezone,
        max_calendar_days=179,
    )
    challenge = simulate_challenge(events.to_dict("records"), rules, default_risk_pct=risk_pct)
    result = {
        "scope": "single locked historical trade-ledger replay; no signal generation or parameter search",
        "ledger_format": ledger_format.lower(),
        "source_hashes": {
            "bid_sha256": sha256_file(bid_path),
            "ask_sha256": sha256_file(ask_path),
            "source_ledger_sha256": sha256_file(ledger_path),
        },
        "input": {
            "bars_before_exclusive_cutoff": len(bars),
            "cutoff_exclusive_utc": cutoff_utc,
            "trades": int(len(normalized)),
        },
        "adapter_audit": adapter_audit,
        "artifacts": {
            "normalized_trade_ledger_csv": str(normalized_path),
            "normalized_trade_ledger_sha256": sha256_file(normalized_path),
            "challenge_event_path_csv": str(events_path),
            "challenge_event_path_sha256": sha256_file(events_path),
            "challenge_event_path_bytes": events_path.stat().st_size,
        },
        "challenge_rules": {
            "initial_balance": initial_balance,
            "phase_targets": list(rules.phase_targets),
            "risk_pct_per_trade": risk_pct,
            "daily_loss_pct": rules.daily_loss_pct,
            "maximum_loss_pct": rules.max_loss_pct,
            "minimum_trading_days_per_phase": rules.min_trading_days,
            "server_timezone": server_timezone,
            "project_max_calendar_days": rules.max_calendar_days,
        },
        "challenge_result": challenge,
        "interpretation": (
            "One historical replay cannot estimate pass probability. The R298 candidate is already "
            "closed as GAGAL by its locked historical gates; use this run only to verify ledger-to-equity "
            "integration, not to promote the candidate."
        ),
    }
    result_path = out / "funded_replay_result.json"
    result_path.write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    print(json.dumps(result, indent=2, default=str))
    return result


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--bid", required=True, help="archived BID CSV/CSV.GZ")
    ap.add_argument("--ask", required=True, help="archived ASK CSV/CSV.GZ")
    ap.add_argument("--ledger", required=True, help="locked closed-trade ledger CSV")
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--ledger-format", choices=("r298", "canonical"), default="r298")
    ap.add_argument("--cutoff-utc", default="2026-01-01T00:00:00Z")
    ap.add_argument("--initial-balance", type=float, default=6000.0)
    ap.add_argument("--risk-pct", type=float, default=0.005)
    ap.add_argument("--added-cost-price-units", type=float, default=0.30)
    ap.add_argument("--server-timezone", default="Europe/Helsinki")
    a = ap.parse_args()
    replay(
        a.bid, a.ask, a.ledger, a.out_dir, ledger_format=a.ledger_format,
        cutoff_utc=a.cutoff_utc, initial_balance=a.initial_balance,
        risk_pct=a.risk_pct, added_cost_price_units=a.added_cost_price_units,
        server_timezone=a.server_timezone,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
