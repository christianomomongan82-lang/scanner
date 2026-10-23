"""Chronological two-phase FundedNext Stellar 2-Step challenge replay.

Input is an ordered position path, not a closed-trade summary. A source-specific
OHLC/BID-ASK adapter must emit OPEN/MARK/EXIT events with exact timestamps.
All *_r values are net of observed BID/ASK, commission, swap, fee, and the
declared slippage scenario. MARK rows must include conservative intrabar equity
checkpoints (not just candle closes) wherever OHLC can breach a rule.

This module deliberately does not generate signals, infer missing path data,
or manufacture a Monte Carlo probability from a single historical path.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime, time, timedelta
from typing import Any, Iterable
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class ChallengeRules:
    initial_balance: float = 6000.0
    phase_targets: tuple[float, float] = (0.08, 0.05)
    daily_loss_pct: float = 0.05
    max_loss_pct: float = 0.10
    min_trading_days: int = 5
    quick_strike_max_share: float = 0.30
    daily_loss_reference: str = "initial_balance"
    server_timezone: str = "Europe/Helsinki"  # DST proxy; verify against actual account
    max_open_risk_pct: float = 0.03            # project-level portfolio cap, not a challenge rule
    max_calendar_days: int = 179               # project speed gate: complete before day 180
    quick_strike_cycle_days: int = 14            # FundedNext evaluation cycle anchored at first trade
    max_inactivity_days: int = 30                  # conservative cap while official sources conflict (calendar days)

    def validate(self) -> None:
        if self.initial_balance <= 0:
            raise ValueError("initial_balance must be positive")
        if len(self.phase_targets) != 2 or any(x <= 0 for x in self.phase_targets):
            raise ValueError("phase_targets must contain two positive fractions")
        if not 0 < self.daily_loss_pct < 1 or not 0 < self.max_loss_pct < 1:
            raise ValueError("loss percentages must be between 0 and 1")
        if self.min_trading_days < 1:
            raise ValueError("min_trading_days must be positive")
        if not 0 < self.quick_strike_max_share < 1:
            raise ValueError("quick_strike_max_share must be between 0 and 1")
        if self.daily_loss_reference not in {"initial_balance", "phase_start_balance"}:
            raise ValueError("unsupported daily_loss_reference")
        if self.max_open_risk_pct <= 0:
            raise ValueError("max_open_risk_pct must be positive")
        if self.max_calendar_days < 0:
            raise ValueError("max_calendar_days must be zero or greater")
        if self.quick_strike_cycle_days < 1:
            raise ValueError("quick_strike_cycle_days must be positive")
        if self.max_inactivity_days < 1:
            raise ValueError("max_inactivity_days must be positive")
        ZoneInfo(self.server_timezone)


def _parse_timestamp(value: Any) -> datetime:
    if isinstance(value, datetime):
        dt = value
    else:
        dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError(f"timestamp must include timezone/offset: {value!r}")
    return dt


def _quick_strike_share(gross_winning_profit: float, quick_winning_profit: float) -> float:
    if gross_winning_profit <= 0:
        return 0.0
    return quick_winning_profit / gross_winning_profit


def _as_event_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return False
    if isinstance(value, (int, float)):
        return value != 0
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def simulate_challenge(
    events: Iterable[dict[str, Any]],
    rules: ChallengeRules | None = None,
    default_risk_pct: float = 0.01,
) -> dict[str, Any]:
    """Replay an event stream once, chronologically, through both phases.

    Required event fields:
      timestamp_utc, event, trade_id
    event is OPEN, MARK, or EXIT (case-insensitive).
    OPEN: risk_pct optional (fraction, e.g. 0.01 = 1% of current closed balance).
    MARK: floating_r (current PnL in this trade's original risk units).
    EXIT: realized_r (net realized PnL in original risk units), hold_seconds.

    event_seq breaks ties for the same timestamp. Caller must order adverse
    intrabar checkpoints before later/favorable checkpoints; same-bar stop/target
    ambiguity must already be handled stop-first by the price-path adapter.
    """
    rules = rules or ChallengeRules()
    rules.validate()
    if default_risk_pct <= 0:
        raise ValueError("default_risk_pct must be positive")

    prepared = []
    for ordinal, raw in enumerate(events):
        row = dict(raw)
        for key in ("timestamp_utc", "event", "trade_id"):
            if key not in row:
                raise ValueError(f"event {ordinal} missing {key}")
        dt = _parse_timestamp(row["timestamp_utc"]).astimezone(ZoneInfo("UTC"))
        row["_dt"] = dt
        row["_ordinal"] = ordinal
        row["_seq"] = int(row.get("event_seq", 0))
        row["_event"] = str(row["event"]).strip().upper()
        if row["_event"] not in {"OPEN", "MARK", "EXIT"}:
            raise ValueError(f"unsupported event type: {row['_event']}")
        if not str(row["trade_id"]).strip():
            raise ValueError("trade_id must be non-empty")
        prepared.append(row)

    prepared.sort(key=lambda x: (x["_dt"], x["_seq"], x["_ordinal"]))
    if not prepared:
        return {
            "status": "PATH_EXHAUSTED", "binary_verdict": "GAGAL", "phases_completed": 0,
            "events_processed": 0, "trades_closed": 0, "skipped_entries": [],
            "phase_results": [], "failure_reason": "empty_event_stream",
            "rules": asdict(rules),
        }

    tz = ZoneInfo(rules.server_timezone)
    initial = float(rules.initial_balance)
    balance = initial
    phase_no = 1
    phase_start_balance = initial
    attempt_start_time = next((r["_dt"] for r in prepared if r["_event"] == "OPEN"), prepared[0]["_dt"])
    phase_start_time = attempt_start_time
    completion_time = None
    calendar_days_elapsed = None
    phase_entry_days: set[str] = set()
    phase_gross_wins = 0.0
    phase_quick_wins = 0.0
    cycle_gross_wins = 0.0
    cycle_quick_wins = 0.0
    cycle_anchor_date = None
    current_cycle_index = None
    last_accepted_entry_time: datetime | None = None
    daily_closed_pnl: dict[str, float] = {}
    active: dict[str, dict[str, Any]] = {}
    skipped_ids: set[str] = set()
    skipped_entries: list[dict[str, Any]] = []
    phase_results: list[dict[str, Any]] = []
    trades_closed = 0
    failure_reason = None
    breach_time = None
    status = "PATH_EXHAUSTED"
    events_processed = 0

    def active_float_pnl() -> float:
        return sum(pos["risk_cash"] * pos["floating_r"] for pos in active.values())

    def daily_key(dt: datetime) -> str:
        return dt.astimezone(tz).date().isoformat()

    def check_breaches(dt: datetime) -> str | None:
        nonlocal failure_reason, breach_time
        float_pnl = active_float_pnl()
        equity = balance + float_pnl
        day = daily_key(dt)
        daily_pnl = daily_closed_pnl.get(day, 0.0) + float_pnl
        daily_reference = initial if rules.daily_loss_reference == "initial_balance" else phase_start_balance
        daily_floor = -daily_reference * rules.daily_loss_pct
        max_loss_floor = phase_start_balance * (1.0 - rules.max_loss_pct)
        if daily_pnl <= daily_floor + 1e-9:
            failure_reason = "daily_loss_limit"
            breach_time = dt.isoformat()
            return "BREACH_DAILY_LOSS"
        if equity < max_loss_floor - 1e-9:
            failure_reason = "maximum_loss_limit"
            breach_time = dt.isoformat()
            return "BREACH_MAX_LOSS"
        return None

    def quick_share() -> float:
        # FundedNext evaluates Quick Strike on the active 14-day challenge cycle,
        # not cumulatively across the entire phase.
        return _quick_strike_share(cycle_gross_wins, cycle_quick_wins)

    def update_quick_cycle(dt: datetime, event: str, row: dict[str, Any]) -> str | None:
        nonlocal cycle_anchor_date, current_cycle_index, cycle_gross_wins, cycle_quick_wins
        nonlocal failure_reason, breach_time
        local_dt = dt.astimezone(tz)
        local_date = local_dt.date()
        if cycle_anchor_date is None:
            # The cycle starts on the first accepted position, not a candidate
            # OPEN that the risk controller will skip below.
            return None

        elapsed_days = (local_date - cycle_anchor_date).days
        if elapsed_days < 0:
            raise ValueError("event precedes the current phase's Quick Strike cycle anchor")
        cycle_index = elapsed_days // rules.quick_strike_cycle_days

        # FundedNext closes any remaining position automatically at cycle end
        # (23:45 server time); being open at 23:30 is not itself a loss-rule breach.
        # The adapter must emit that actual forced EXIT from the executable quote.
        # If the event is absent, fail the replay as invalid instead of fabricating
        # a FundedNext rule violation.
        is_last_cycle_day = elapsed_days % rules.quick_strike_cycle_days == rules.quick_strike_cycle_days - 1
        local_clock = local_dt.time().replace(tzinfo=None)
        if is_last_cycle_day and local_clock >= time(23, 45):
            if event == "OPEN":
                failure_reason = "entry_at_or_after_cycle_end"
                breach_time = dt.isoformat()
                return "INVALID_PATH_ENTRY_AT_CYCLE_END"
            if active:
                allowed_cycle_exit = (
                    event == "EXIT"
                    and local_clock == time(23, 45)
                    and bool(_as_event_bool(row.get("exit_at_open", False)))
                )
                if not allowed_cycle_exit:
                    failure_reason = "missing_cycle_auto_close_event"
                    breach_time = dt.isoformat()
                    return "INVALID_PATH_QUICK_STRIKE_CYCLE_OPEN_POSITION"

        if current_cycle_index is not None and cycle_index > current_cycle_index:
            if active:
                failure_reason = "position_open_across_cycle_boundary_missing_auto_close"
                breach_time = dt.isoformat()
                return "INVALID_PATH_QUICK_STRIKE_CYCLE_OPEN_POSITION"
            current_cycle_index = cycle_index
            cycle_gross_wins = 0.0
            cycle_quick_wins = 0.0
        return None

    def can_finish_phase() -> bool:
        target = phase_start_balance * (1.0 + rules.phase_targets[phase_no - 1])
        return (
            balance >= target - 1e-9
            and len(phase_entry_days) >= rules.min_trading_days
            and not active
            and quick_share() < rules.quick_strike_max_share
        )

    def finish_phase(dt: datetime) -> None:
        nonlocal phase_no, balance, phase_start_balance, phase_start_time
        nonlocal phase_entry_days, phase_gross_wins, phase_quick_wins, daily_closed_pnl
        nonlocal cycle_gross_wins, cycle_quick_wins, cycle_anchor_date, current_cycle_index
        phase_results.append({
            "phase": phase_no,
            "status": "LULUS",
            "start_time_utc": phase_start_time.isoformat(),
            "end_time_utc": dt.isoformat(),
            "start_balance": phase_start_balance,
            "closed_balance": balance,
            "closed_return_pct": balance / phase_start_balance - 1.0,
            "target_pct": rules.phase_targets[phase_no - 1],
            "trading_days": len(phase_entry_days),
            "gross_winning_profit": phase_gross_wins,
            "quick_strike_profit": phase_quick_wins,
            "phase_quick_strike_share_all_trades": _quick_strike_share(phase_gross_wins, phase_quick_wins),
            "quick_strike_share": quick_share(),
            "quick_strike_cycle_days": rules.quick_strike_cycle_days,
            "quick_strike_cycle_anchor_date": cycle_anchor_date.isoformat() if cycle_anchor_date else None,
            "quick_strike_cycle_start_date": (
                (cycle_anchor_date + timedelta(days=(current_cycle_index or 0) * rules.quick_strike_cycle_days)).isoformat()
                if cycle_anchor_date else None
            ),
            "quick_strike_cycle_index": current_cycle_index,
            "quick_strike_cycle_gross_winning_profit": cycle_gross_wins,
            "quick_strike_cycle_profit": cycle_quick_wins,
        })
        if phase_no == 2:
            return
        phase_no = 2
        # The two-step phases use a fresh initial reference balance.
        balance = initial
        phase_start_balance = initial
        phase_start_time = dt
        phase_entry_days = set()
        phase_gross_wins = 0.0
        phase_quick_wins = 0.0
        cycle_gross_wins = 0.0
        cycle_quick_wins = 0.0
        cycle_anchor_date = None
        current_cycle_index = None
        daily_closed_pnl = {}

    for row in prepared:
        dt = row["_dt"]
        event = row["_event"]
        tid = str(row["trade_id"])
        events_processed += 1

        cycle_status = update_quick_cycle(dt, event, row)
        if cycle_status:
            status = cycle_status
            break

        if event == "OPEN":
            if tid in active or tid in skipped_ids:
                raise ValueError(f"duplicate OPEN for trade_id {tid}")
            if phase_no > 2:
                break
            risk_pct = float(row.get("risk_pct", default_risk_pct))
            if not 0 < risk_pct < 1:
                raise ValueError(f"invalid risk_pct for {tid}: {risk_pct}")
            risk_cash = balance * risk_pct
            projected_open_risk = sum(p["risk_cash"] for p in active.values()) + risk_cash
            if projected_open_risk > phase_start_balance * rules.max_open_risk_pct + 1e-9:
                skipped_ids.add(tid)
                skipped_entries.append({
                    "trade_id": tid, "timestamp_utc": dt.isoformat(),
                    "reason": "portfolio_open_risk_cap",
                    "projected_open_risk_pct": projected_open_risk / phase_start_balance,
                    "cap_pct": rules.max_open_risk_pct,
                })
                continue
            if last_accepted_entry_time is not None and not active:
                previous_day = last_accepted_entry_time.astimezone(tz).date()
                current_day = dt.astimezone(tz).date()
                inactivity_gap = (current_day - previous_day).days
                if inactivity_gap >= rules.max_inactivity_days:
                    failure_reason = "inactivity_limit_reached"
                    breach_time = dt.isoformat()
                    status = "INACTIVITY_LIMIT_REACHED"
                    break
            active[tid] = {
                "risk_cash": risk_cash, "floating_r": 0.0,
                "entry_time": dt, "entry_day": daily_key(dt),
                "phase": phase_no,
            }
            if cycle_anchor_date is None:
                cycle_anchor_date = dt.astimezone(tz).date()
                current_cycle_index = 0
            phase_entry_days.add(daily_key(dt))
            last_accepted_entry_time = dt
            breach = check_breaches(dt)
            if breach:
                status = breach
                break

        elif tid in skipped_ids:
            continue

        elif event == "MARK":
            if tid not in active:
                raise ValueError(f"MARK without active OPEN for {tid}")
            if "floating_r" not in row:
                raise ValueError(f"MARK missing floating_r for {tid}")
            active[tid]["floating_r"] = float(row["floating_r"])
            breach = check_breaches(dt)
            if breach:
                status = breach
                break

        elif event == "EXIT":
            if tid not in active:
                raise ValueError(f"EXIT without active OPEN for {tid}")
            if "realized_r" not in row:
                raise ValueError(f"EXIT missing realized_r for {tid}")
            pos = active.pop(tid)
            realized_r = float(row["realized_r"])
            pnl = pos["risk_cash"] * realized_r
            balance += pnl
            day = daily_key(dt)
            daily_closed_pnl[day] = daily_closed_pnl.get(day, 0.0) + pnl
            trades_closed += 1
            if pnl > 0:
                phase_gross_wins += pnl
                cycle_gross_wins += pnl
                duration = float(row.get("hold_seconds", (dt - pos["entry_time"]).total_seconds()))
                if duration < 30.0:
                    phase_quick_wins += pnl
                    cycle_quick_wins += pnl
            breach = check_breaches(dt)
            if breach:
                status = breach
                break

        if can_finish_phase():
            completed_phase = phase_no
            finish_phase(dt)
            if completed_phase == 2:
                completion_time = dt
                calendar_days_elapsed = (dt.date() - attempt_start_time.date()).days
                status = (
                    "PASS_BOTH_PHASES_WITHIN_179D"
                    if calendar_days_elapsed <= rules.max_calendar_days
                    else "PASS_BOTH_PHASES_TOO_SLOW"
                )
                break

    if status == "PATH_EXHAUSTED" and active:
        failure_reason = "position_path_ends_with_open_position"
        status = "INVALID_PATH_OPEN_POSITION_AT_END"

    if status.startswith("BREACH_"):
        phase_results.append({
            "phase": phase_no, "status": "GAGAL",
            "failure_reason": failure_reason, "breach_time_utc": breach_time,
            "closed_balance": balance, "equity_at_breach": balance + active_float_pnl(),
            "daily_closed_pnl": daily_closed_pnl.get(daily_key(_parse_timestamp(breach_time)), 0.0),
            "floating_pnl": active_float_pnl(),
            "phase_start_balance": phase_start_balance,
            "max_loss_floor": phase_start_balance * (1.0 - rules.max_loss_pct),
        })
    elif status not in {"PASS_BOTH_PHASES_WITHIN_179D", "PASS_BOTH_PHASES_TOO_SLOW"}:
        phase_results.append({
            "phase": phase_no, "status": "BELUM_SELESAI",
            "closed_balance": balance, "phase_start_balance": phase_start_balance,
            "target_balance": phase_start_balance * (1.0 + rules.phase_targets[phase_no - 1]),
            "trading_days": len(phase_entry_days),
            "gross_winning_profit": phase_gross_wins,
            "quick_strike_profit": phase_quick_wins,
            "phase_quick_strike_share_all_trades": _quick_strike_share(phase_gross_wins, phase_quick_wins),
            "quick_strike_share": quick_share(),
            "quick_strike_cycle_days": rules.quick_strike_cycle_days,
            "quick_strike_cycle_anchor_date": cycle_anchor_date.isoformat() if cycle_anchor_date else None,
            "quick_strike_cycle_start_date": (
                (cycle_anchor_date + timedelta(days=(current_cycle_index or 0) * rules.quick_strike_cycle_days)).isoformat()
                if cycle_anchor_date else None
            ),
            "quick_strike_cycle_index": current_cycle_index,
            "quick_strike_cycle_gross_winning_profit": cycle_gross_wins,
            "quick_strike_cycle_profit": cycle_quick_wins,
            "open_positions_at_end": sorted(active.keys()),
        })

    return {
        "status": status,
        "binary_verdict": "LULUS" if status == "PASS_BOTH_PHASES_WITHIN_179D" else "GAGAL",
        "failure_reason": failure_reason,
        "breach_time_utc": breach_time,
        "attempt_start_time_utc": attempt_start_time.isoformat(),
        "completion_time_utc": completion_time.isoformat() if completion_time else None,
        "calendar_days_elapsed": calendar_days_elapsed,
        "speed_gate_max_calendar_days": rules.max_calendar_days,
        "phases_completed": sum(x["status"] == "LULUS" for x in phase_results),
        "events_processed": events_processed,
        "trades_closed": trades_closed,
        "skipped_entries": skipped_entries,
        "phase_results": phase_results,
        "ending_balance": balance,
        "open_positions_at_end": sorted(active.keys()),
        "rules": asdict(rules),
        "notes": [
            "A closed-trade ledger alone is not valid input; MARK events must include floating and conservative intrabar checkpoints.",
            "MARK/EXIT values must already include observed spread, commission, swap, fees and the tested slippage scenario.",
            "Europe/Helsinki is a seasonal server-time proxy, not platform-time verification.",
            "Inactivity is conservatively enforced as fewer than 30 calendar days between accepted entries because official FundedNext sources conflict; confirm exact account terms.",
            "This is one chronological path, not a 10,000-path pass-probability estimate.",
        ],
    }


def load_events_csv(path: str) -> list[dict[str, Any]]:
    """Load the event contract from CSV without inferring absent fields."""
    import csv
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main() -> int:
    import argparse
    import json

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("events_csv", help="chronological position-path CSV")
    parser.add_argument("--risk-pct", type=float, default=0.01, help="default per-trade risk fraction")
    parser.add_argument("--server-tz", default="Europe/Helsinki", help="server timezone proxy")
    args = parser.parse_args()
    events = load_events_csv(args.events_csv)
    rules = ChallengeRules(server_timezone=args.server_tz)
    result = simulate_challenge(events, rules=rules, default_risk_pct=args.risk_pct)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
