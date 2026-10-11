#!/usr/bin/env python3
"""R209: fade US cash-session opening gaps back toward the prior session close.

On a valid prior RTH session, compare its 16:00 New York close with the next
session's 09:30 open. If the first M5 candle closes against the gap direction,
enter a fade at the next non-flat open, target the prior close, and stop at the
first candle extreme. Only trade if the target is at least 2R away. Exit at TP,
SL or 16:00 ET. BID-only screening with 1/2bp cost stress.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research.r192_ger40 import parse_data

TZ_NY = "America/New_York"
RR = 2.0
OR_MINUTES = tuple(range(570, 600, 5))  # 09:30 through 09:55 ET bar opens
SIGNAL_START = 600                         # 10:00 ET
LAST_SIGNAL_BAR = 950                      # 15:50 ET; entry no later than 15:55
SESSION_CLOSE = 960                       # 16:00 ET

ASSETS = {
    "usa500idxusd": "USA 500 / S&P 500",
    "usatechidxusd": "USA 100 Tech / Nasdaq 100",
    "usa30idxusd": "USA 30 / Dow Jones",
    "ussc2000idxusd": "US Small Cap 2000",
}

DISCOVERY_START = pd.Timestamp("2017-01-01", tz="UTC")
DISCOVERY_END = pd.Timestamp("2022-01-01", tz="UTC")
FORWARD_START = DISCOVERY_END
FORWARD_END = pd.Timestamp("2026-01-01", tz="UTC")
OOS_START = FORWARD_END


def session_bounds_utc(day):
    """Return the regular US cash-session 09:30/16:00 boundaries in UTC."""
    d = pd.Timestamp(day).date()
    start = pd.Timestamp(f"{d.isoformat()} 09:30", tz=TZ_NY).tz_convert("UTC")
    end = pd.Timestamp(f"{d.isoformat()} 16:00", tz=TZ_NY).tz_convert("UTC")
    return start, end


def finite_number(x):
    return isinstance(x, (int, float, np.integer, np.floating)) and math.isfinite(float(x))


def make_candidates(m5, instrument):
    """One gap-fade candidate/day when first-candle confirmation and >=2R hold."""
    mt = m5.index.tz_convert("UTC")
    local = mt.tz_convert(TZ_NY)
    minutes = (local.hour * 60 + local.minute).to_numpy(dtype=np.int16)
    day_keys = np.asarray(local.date, dtype=object)
    op = m5.open.to_numpy(float)
    hi = m5.high.to_numpy(float)
    lo = m5.low.to_numpy(float)
    close = m5.close.to_numpy(float)
    flat = (op == hi) & (hi == lo) & (lo == close)
    frame = pd.DataFrame({"ny_date": day_keys, "row": np.arange(len(m5), dtype=np.int64)})
    groups = [(ny_day, group["row"].to_numpy(dtype=np.int64))
              for ny_day, group in frame.groupby("ny_date", sort=True)]

    # A valid prior regular-hours session supplies its final M5 close (15:55 bar).
    session_info = {}
    skipped_session_quality = 0
    for ny_day, ids in groups:
        rth_ids = ids[(minutes[ids] >= 570) & (minutes[ids] < SESSION_CLOSE)]
        rth_minutes = minutes[rth_ids]
        if len(rth_ids) < 70 or len(np.unique(rth_minutes)) < 70 or int(np.max(rth_minutes, initial=-1)) < 955:
            skipped_session_quality += 1
            continue
        nonflat = int((~flat[rth_ids]).sum())
        if nonflat < 60:
            skipped_session_quality += 1
            continue
        open_rows = rth_ids[minutes[rth_ids] == 570]
        if len(open_rows) == 0:
            skipped_session_quality += 1
            continue
        last_i = int(rth_ids[-1])
        session_info[ny_day] = {
            "close": float(close[last_i]),
            "last_close_utc": (mt[last_i] + pd.Timedelta(minutes=5)).isoformat(),
            "rth_bars": int(len(rth_ids)),
            "rth_nonflat": nonflat,
            "open_i": int(open_rows[0]),
        }

    valid_dates = sorted(session_info)
    previous_for_date = {
        valid_dates[i]: valid_dates[i - 1]
        for i in range(1, len(valid_dates))
    }
    candidates = []
    session_rows = []
    days_with_gap = 0
    reversal_signals = 0
    taken_candidates = 0
    skipped_no_previous_session = 0
    skipped_no_open_bar = 0
    skipped_no_reversal = 0
    skipped_target_passed = 0
    skipped_rr = 0
    skipped_no_entry = 0

    for ny_day, ids in groups:
        if ny_day not in session_info:
            continue
        prev_day = previous_for_date.get(ny_day)
        if prev_day is None:
            skipped_no_previous_session += 1
            session_rows.append({
                "instrument": instrument, "ny_date": str(ny_day), "valid_session": True,
                "reason": "no_prior_valid_rth_session",
            })
            continue
        open_i = int(session_info[ny_day]["open_i"])
        if flat[open_i]:
            skipped_no_open_bar += 1
            session_rows.append({
                "instrument": instrument, "ny_date": str(ny_day), "valid_session": True,
                "reason": "first_0930_bar_is_flat",
            })
            continue

        prior_close = float(session_info[prev_day]["close"])
        open_price = float(op[open_i])
        gap = open_price - prior_close
        gap_pct = gap / prior_close if prior_close else np.nan
        base = {
            "instrument": instrument, "ny_date": str(ny_day), "valid_session": True,
            "prior_session_date": str(prev_day),
            "prior_session_close": prior_close,
            "prior_session_close_utc": session_info[prev_day]["last_close_utc"],
            "opening_price": open_price, "opening_gap_points": gap,
            "opening_gap_pct": gap_pct,
        }
        if not math.isfinite(gap) or gap == 0:
            skipped_no_reversal += 1
            session_rows.append({**base, "reason": "zero_or_invalid_opening_gap"})
            continue
        days_with_gap += 1
        # Only the first completed M5 candle after the cash open confirms a fade.
        first_close = float(close[open_i])
        if gap > 0:
            direction = -1
            confirmed = first_close < open_price
        else:
            direction = 1
            confirmed = first_close > open_price
        signal_close = mt[open_i] + pd.Timedelta(minutes=5)
        if not confirmed:
            skipped_no_reversal += 1
            session_rows.append({
                **base, "reason": "first_m5_candle_did_not_close_against_gap",
                "first_bar_open_utc": mt[open_i].isoformat(),
                "first_bar_close": first_close,
                "first_bar_high": float(hi[open_i]), "first_bar_low": float(lo[open_i]),
            })
            continue
        reversal_signals += 1

        # Entry is the next non-flat M5 open after the first candle closes.
        rth_ids = ids[(minutes[ids] >= 570) & (minutes[ids] < SESSION_CLOSE)]
        entry_i = None
        for k in rth_ids:
            if mt[k] < signal_close:
                continue
            if not flat[k]:
                entry_i = int(k)
                break
        if entry_i is None:
            skipped_no_entry += 1
            session_rows.append({
                **base, "reason": "no_nonflat_entry_bar_after_first_candle",
                "first_bar_open_utc": mt[open_i].isoformat(),
                "first_bar_close_utc": signal_close.isoformat(),
            })
            continue

        entry = float(op[entry_i])
        stop = float(hi[open_i] if direction == -1 else lo[open_i])
        target = prior_close
        risk = stop - entry if direction == -1 else entry - stop
        reward = entry - target if direction == -1 else target - entry
        if (direction == -1 and not entry > target) or (direction == 1 and not entry < target):
            skipped_target_passed += 1
            session_rows.append({
                **base, "reason": "prior_close_target_already_passed_by_entry",
                "direction": "short" if direction == -1 else "long",
                "entry_time_utc": mt[entry_i].isoformat(), "entry": entry, "target": target,
            })
            continue
        rr = reward / risk if risk > 0 else np.nan
        if not math.isfinite(rr) or rr < RR:
            skipped_rr += 1
            session_rows.append({
                **base, "reason": "gap_fill_reward_less_than_2R",
                "direction": "short" if direction == -1 else "long",
                "entry_time_utc": mt[entry_i].isoformat(), "entry": entry,
                "sl": stop, "target": target, "potential_reward_risk": rr,
            })
            continue

        taken_candidates += 1
        session_rows.append({
            **base, "reason": "gap_fade_candidate",
            "direction": "short" if direction == -1 else "long",
            "first_bar_open_utc": mt[open_i].isoformat(),
            "first_bar_close_utc": signal_close.isoformat(),
            "first_bar_high": float(hi[open_i]), "first_bar_low": float(lo[open_i]),
            "direction_sign": direction,
            "entry_time_utc": mt[entry_i].isoformat(), "entry": entry,
            "sl": stop, "target": target, "potential_reward_risk": rr,
        })
        candidates.append({
            "config": "R209_US_RTH_OPENING_GAP_FADE_TO_PRIOR_CLOSE_RR2",
            "instrument": instrument,
            "ny_date": str(ny_day),
            "direction": "short" if direction == -1 else "long",
            "direction_sign": direction,
            "prior_session_date": str(prev_day),
            "prior_session_close": target,
            "opening_price": open_price,
            "opening_gap_points": gap,
            "opening_gap_pct": gap_pct,
            "first_bar_open_utc": mt[open_i].isoformat(),
            "signal_bar_open_utc": mt[open_i].isoformat(),
            "signal_close_utc": signal_close.isoformat(),
            "first_bar_high": float(hi[open_i]),
            "first_bar_low": float(lo[open_i]),
            "or_high": float(hi[open_i]),
            "or_low": float(lo[open_i]),
            "or_range_points": float(hi[open_i] - lo[open_i]),
            "or_nonflat_bars": 1,
            "stop": stop,
            "target": target,
            "potential_reward_risk": rr,
            "entry_i": entry_i,
        })

    diag = {
        "ny_dates_in_data": int(frame["ny_date"].nunique()),
        "valid_rth_sessions": int(len(session_info)),
        "prior_sessions_skipped_quality": int(skipped_session_quality),
        "days_with_valid_prior_close_and_nonflat_open": int(days_with_gap),
        "first_candle_reversal_signals": int(reversal_signals),
        "eligible_gap_fade_candidates_rr2": int(taken_candidates),
        "sessions_skipped_no_previous_rth": int(skipped_no_previous_session),
        "sessions_skipped_no_0930_bar": int(skipped_no_open_bar),
        "sessions_skipped_no_reversal": int(skipped_no_reversal),
        "sessions_skipped_target_passed": int(skipped_target_passed),
        "sessions_skipped_reward_risk_below_2": int(skipped_rr),
        "sessions_skipped_no_entry": int(skipped_no_entry),
    }
    return candidates, session_rows, diag

def simulate_candidates(m5, candidates):
    """Sequential one-position execution; flat M5 bars cannot fill or trigger exits."""
    mt = m5.index.tz_convert("UTC")
    op = m5.open.to_numpy(float)
    hi = m5.high.to_numpy(float)
    lo = m5.low.to_numpy(float)
    close = m5.close.to_numpy(float)
    flat = (op == hi) & (hi == lo) & (lo == close)

    trades = []
    skipped_active = 0
    skipped_no_fill = 0
    skipped_invalid_risk = 0
    last_exit = None
    local_trade = mt.tz_convert(TZ_NY)
    trade_minutes = (local_trade.hour * 60 + local_trade.minute).to_numpy(dtype=np.int16)
    trade_dates = np.asarray(local_trade.date, dtype=object)

    for candidate in candidates:
        signal_close = pd.Timestamp(candidate["signal_close_utc"])
        if last_exit is not None:
            if pd.isna(last_exit):
                skipped_active += 1
                continue
            if not (last_exit < signal_close):
                skipped_active += 1
                continue

        entry_i = candidate["entry_i"]
        if entry_i is None:
            skipped_no_fill += 1
            continue
        entry_time = mt[entry_i]
        entry = float(op[entry_i])
        direction = int(candidate["direction_sign"])
        stop = float(candidate["stop"])
        risk = entry - stop if direction == 1 else stop - entry
        if not math.isfinite(risk) or risk <= 0:
            skipped_invalid_risk += 1
            continue
        target = float(candidate["target"])

        exit_time = None
        exit_price = np.nan
        reason = "OPEN_AT_DATA_END"
        flat_skipped = 0
        candidate_day = pd.Timestamp(candidate["ny_date"]).date()
        for j in range(entry_i, len(mt)):
            if trade_dates[j] != candidate_day:
                # End-of-session is mandatory for an opening-gap fade.
                exit_price = float(close[j - 1]) if j > entry_i else entry
                exit_time = mt[j]
                reason = "EOD"
                break
            if flat[j]:
                flat_skipped += 1
                if int(trade_minutes[j]) == 955:
                    exit_price = float(close[j])
                    exit_time = mt[j] + pd.Timedelta(minutes=5)
                    reason = "EOD"
                    break
                continue
            o, hh, ll = float(op[j]), float(hi[j]), float(lo[j])
            if direction == 1:
                if ll <= stop or o <= stop:
                    exit_price = o if o <= stop else stop
                    reason = "SL_GAP_OPEN" if o <= stop else "SL"
                    exit_time = mt[j]
                    break
                if hh >= target:
                    exit_price, reason, exit_time = target, "TP", mt[j]
                    break
            else:
                if hh >= stop or o >= stop:
                    exit_price = o if o >= stop else stop
                    reason = "SL_GAP_OPEN" if o >= stop else "SL"
                    exit_time = mt[j]
                    break
                if ll <= target:
                    exit_price, reason, exit_time = target, "TP", mt[j]
                    break

        trades.append({
            "config": candidate["config"],
            "instrument": candidate["instrument"],
            "ny_date": candidate["ny_date"],
            "direction": candidate["direction"],
            "or_high": candidate["or_high"],
            "or_low": candidate["or_low"],
            "or_range_points": candidate["or_range_points"],
            "or_nonflat_bars": candidate["or_nonflat_bars"],
            "prior_session_date": candidate["prior_session_date"],
            "prior_session_close": candidate["prior_session_close"],
            "opening_price": candidate["opening_price"],
            "opening_gap_points": candidate["opening_gap_points"],
            "opening_gap_pct": candidate["opening_gap_pct"],
            "first_bar_open_utc": candidate["first_bar_open_utc"],
            "first_bar_high": candidate["first_bar_high"],
            "first_bar_low": candidate["first_bar_low"],
            "potential_reward_risk": candidate["potential_reward_risk"],
            "signal_bar_open_utc": candidate["signal_bar_open_utc"],
            "signal_close_utc": candidate["signal_close_utc"],
            "entry_time_utc": entry_time.isoformat(),
            "entry": entry,
            "sl": stop,
            "tp": target,
            "exit_time_utc": None if exit_time is None else exit_time.isoformat(),
            "exit": None if exit_time is None else float(exit_price),
            "reason": reason,
            "entry_exact_m5_timestamp": True,
            "risk_points": risk,
            "flat_m5_bars_skipped_while_open": flat_skipped,
        })
        last_exit = pd.NaT if exit_time is None else exit_time
        if pd.isna(last_exit):
            break

    diag = {
        "candidate_signals": len(candidates),
        "taken": len(trades),
        "skipped_active": skipped_active,
        "skipped_no_tradable_fill": skipped_no_fill,
        "skipped_invalid_risk": skipped_invalid_risk,
    }
    return trades, diag


def trade_r(trade, bps):
    if trade["exit"] is None:
        return np.nan
    cost = float(trade["entry"]) * bps / 10000.0
    if trade["direction"] == "long":
        return (float(trade["exit"]) - float(trade["entry"]) - cost) / float(trade["risk_points"])
    return (float(trade["entry"]) - float(trade["exit"]) - cost) / float(trade["risk_points"])


def metric(trades, start, end, outcome_cutoff, bps):
    picked = [t for t in trades if start <= pd.Timestamp(t["entry_time_utc"]) < end]
    closed = [
        t for t in picked
        if t["exit_time_utc"] is not None and pd.Timestamp(t["exit_time_utc"]) < outcome_cutoff
    ]
    vals = np.asarray([trade_r(t, bps) for t in closed], dtype=float)
    wins = float(vals[vals > 0].sum()) if len(vals) else 0.0
    losses = float(-vals[vals < 0].sum()) if len(vals) else 0.0
    pf = wins / losses if losses > 0 else (float("inf") if wins > 0 else float("nan"))
    return {
        "entries": len(picked), "closed": len(closed), "censored": len(picked) - len(closed),
        "pf": pf, "wins_r": wins, "losses_r": losses,
    }


def cohort_metrics(trades, year, outcome_cutoff, bps):
    start = pd.Timestamp(f"{year}-01-01", tz="UTC")
    end = pd.Timestamp(f"{year + 1}-01-01", tz="UTC")
    return metric(trades, start, end, outcome_cutoff, bps)


def safe(x):
    if isinstance(x, (np.integer,)):
        return int(x)
    if isinstance(x, (np.floating, float)):
        if math.isnan(float(x)):
            return None
        if math.isinf(float(x)):
            return "INF" if x > 0 else "-INF"
        return float(x)
    if isinstance(x, (pd.Timestamp,)):
        return x.isoformat()
    return x


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default="dl")
    ap.add_argument("--out", default="results")
    args = ap.parse_args()
    data_dir = Path(args.data_dir)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    all_trades = []
    all_sessions = []
    diagnostics = {}
    source_meta = {}
    trades_by_asset = {}
    entry_counts = {}
    observed_ends = {}

    # Validate each BID snapshot before any PF is computed.
    for inst, name in ASSETS.items():
        path = data_dir / f"{inst}_m5.csv.gz"
        if not path.is_file():
            raise SystemExit(f"HARD STOP: missing M5 source for {inst}: {path}")
        m5, duplicates = parse_data(path)
        if len(m5) < 10000:
            raise SystemExit(f"HARD STOP: too few M5 rows for {inst}: {len(m5)}")
        if not m5.index.is_monotonic_increasing or m5.index.has_duplicates:
            raise SystemExit(f"HARD STOP: unsorted or duplicate M5 index for {inst}")
        candidates, session_rows, build_diag = make_candidates(m5, inst)
        trades, sim_diag = simulate_candidates(m5, candidates)
        trades_by_asset[inst] = trades
        all_trades.extend(trades)
        all_sessions.extend(session_rows)
        diagnostics[inst] = {**build_diag, **sim_diag}
        entry_counts[inst] = len(trades)
        observed_ends[inst] = m5.index[-1].tz_convert("UTC") + pd.Timedelta(minutes=5)
        source_meta[inst] = {
            "name": name,
            "m5_rows": len(m5),
            "duplicates_removed": duplicates,
            "start_utc": m5.index[0].tz_convert("UTC").isoformat(),
            "end_utc": m5.index[-1].tz_convert("UTC").isoformat(),
            "flat_rows": int(((m5.open == m5.high) & (m5.high == m5.low) & (m5.low == m5.close)).sum()),
            **build_diag,
            **sim_diag,
        }
        print(
            f"SOURCE PASS {inst}: M5={len(m5):,}; valid RTH sessions={build_diag['valid_rth_sessions']:,}; "
            f"gap fades passing >=2R={build_diag['eligible_gap_fade_candidates_rr2']:,}; taken={len(trades):,}",
            flush=True,
        )

    common_end = min(observed_ends.values())
    ledger = []
    annual_cohorts = []
    for inst, name in ASSETS.items():
        trades = trades_by_asset[inst]
        m = {
            "instrument": inst,
            "instrument_name": name,
            **diagnostics[inst],
        }
        spans = {
            "discovery": (DISCOVERY_START, DISCOVERY_END, DISCOVERY_END),
            "forward": (FORWARD_START, FORWARD_END, FORWARD_END),
            "oos": (OOS_START, common_end, common_end),
        }
        for phase, (start, end, cutoff) in spans.items():
            for bps in (1, 2):
                met = metric(trades, start, end, cutoff, bps)
                m[f"{phase}_entries"] = met["entries"]
                m[f"{phase}_closed"] = met["closed"]
                m[f"{phase}_censored"] = met["censored"]
                m[f"{phase}_pf_{bps}bp"] = met["pf"]
        for year in range(2017, 2027):
            if year <= 2021:
                cutoff = DISCOVERY_END
            elif year <= 2025:
                cutoff = FORWARD_END
            else:
                cutoff = common_end
            for bps in (1, 2):
                cm = cohort_metrics(trades, year, cutoff, bps)
                annual_cohorts.append({
                    "instrument": inst, "instrument_name": name,
                    "entry_year": year, "cost_bps_rt": bps,
                    "entries": cm["entries"], "n_closed_by_cutoff": cm["closed"],
                    "censored_by_cutoff": cm["censored"], "pf_entry_cohort": cm["pf"],
                    "wins_r": cm["wins_r"], "losses_r": cm["losses_r"],
                })
        ledger.append(m)

    ledger_df = pd.DataFrame(ledger)
    cohort_df = pd.DataFrame(annual_cohorts)
    # Select by discovery only. Within eligible assets, maximize discovery frequency to
    # reflect the stated need for enough trades; tie-break by discovery PF@2bp.
    eligible = ledger_df[
        (ledger_df["discovery_closed"] >= 50)
        & ledger_df["discovery_pf_2bp"].apply(finite_number)
        & (ledger_df["discovery_pf_2bp"] >= 1.0)
    ].copy()
    eligible = eligible.sort_values(
        ["discovery_closed", "discovery_pf_2bp", "instrument"],
        ascending=[False, False, True], kind="stable"
    )

    selected = None
    if len(eligible):
        pick = eligible.iloc[0].to_dict()
        inst = pick["instrument"]
        fwd1 = float(pick["forward_pf_1bp"])
        fwd2 = float(pick["forward_pf_2bp"])
        cohort_rows = cohort_df[
            (cohort_df["instrument"] == inst)
            & (cohort_df["cost_bps_rt"] == 1)
            & cohort_df["entry_year"].between(2022, 2025)
            & (cohort_df["n_closed_by_cutoff"] >= 5)
        ]
        pf_list = [float(x) for x in cohort_rows["pf_entry_cohort"] if finite_number(x)]
        worst = min(pf_list) if pf_list else None
        suspicious = math.isfinite(fwd1) and fwd1 > 1.4
        base_pass = (
            int(pick["forward_closed"]) >= 30
            and math.isfinite(fwd1) and fwd1 >= 1.15
            and math.isfinite(fwd2) and fwd2 >= 1.15
            and (worst is None or worst >= 1.0)
        )
        verdict = "HOLD_EXTRA_AUDIT" if base_pass and suspicious else "PASS" if base_pass else "REJECT"
        selected = {
            "instrument": inst,
            "instrument_name": pick["instrument_name"],
            "selection_rule": "highest number of closed discovery trades among assets with >=50 discovery closes and discovery PF@2bp >=1.00; tie-break by PF@2bp",
            "discovery_closed": int(pick["discovery_closed"]),
            "discovery_pf_1bp": pick["discovery_pf_1bp"],
            "discovery_pf_2bp": pick["discovery_pf_2bp"],
            "forward_closed": int(pick["forward_closed"]),
            "forward_pf_1bp": fwd1,
            "forward_pf_2bp": fwd2,
            "forward_worst_entry_year_pf_1bp_n5plus": worst,
            "forward_pf_gt_1_4_extra_audit_required": bool(suspicious),
            "oos_closed": int(pick["oos_closed"]),
            "oos_pf_1bp": pick["oos_pf_1bp"],
            "oos_pf_2bp": pick["oos_pf_2bp"],
            "forward_verdict": verdict,
        }
    else:
        selected = {
            "forward_verdict": "NO_DISCOVERY_ELIGIBLE_CANDIDATE",
            "note": "No instrument reached >=50 discovery closes and PF@2bp >=1.00; forward metrics cannot select a replacement.",
        }

    meta = {
        "research": "R209: US cash-session opening-gap fade to prior regular-session close",
        "run_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "common_oos_cutoff_utc": common_end.isoformat(),
        "assets": source_meta,
        "locked_rule": {
            "session_timezone": TZ_NY,
            "reference_level": "previous valid RTH session's 16:00 New York close",
            "gap_trigger": "next valid session's 09:30 M5 open differs from prior RTH close; first 5-minute candle must close against the gap direction",
            "entry": "first non-flat M5 open at or after the 09:30 candle close and before 16:00 ET",
            "attempt_limit": "one opening-gap candidate per instrument per NY session date",
            "stop": "first 09:30 M5 candle high for shorts or low for longs",
            "target": "prior valid RTH session close; only trades with target reward/risk >=2 at entry are eligible",
            "time_exit": "any open position is closed at the regular-session close if neither stop nor target is hit",
            "exit": "M5 BID OHLC; SL before TP; gap through stop fills at open; close at 16:00 ET when neither stop nor target hits; flat synthetic M5 bars skipped",
            "cost_model": "1bp and 2bp modeled round-trip cost relative to entry price; not verified actual spread, commissions or slippage",
            "selection": "discovery-only eligibility: >=50 closed trades and PF@2bp >=1.00; among eligible choose highest discovery closed-trade count, then PF@2bp",
            "validation": "forward 2022-2025 requires >=30 closed trades, PF >=1.15 at both modeled costs, and worst eligible entry-year cohort PF >=1.00; PF >1.40 requires separate extra audit",
        },
        "periods": {
            "discovery": "entries 2017-2021, outcomes must close before 2022-01-01",
            "forward": "entries 2022-2025, outcomes must close before 2026-01-01",
            "oos": "entries 2026 to common available M5 cutoff",
        },
        "selection_eligible_instruments": eligible["instrument"].tolist(),
        "locked_selected_candidate": selected,
        "guardrails": [
            "Only one preregistered session-opening-gap-fade rule is tested; no parameter grid.",
            "Selection is frozen on discovery only; do not replace a failed candidate after viewing forward results.",
            "BID-only M5 execution is a screening proxy and is not proof of executable short-side fills.",
            "Broker commissions, instrument-specific spread and live slippage remain unverified.",
            "The result is research evidence, not proof of funded/live readiness.",
        ],
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=safe), encoding="utf-8")
    ledger_df.to_csv(out / "instrument_ledger.csv", index=False)
    cohort_df.to_csv(out / "annual_entry_cohorts.csv", index=False)
    pd.DataFrame(all_trades).to_csv(out / "all_trades.csv", index=False)
    pd.DataFrame(all_sessions).to_csv(out / "opening_range_sessions.csv", index=False)

    print("\nR209 DISCOVERY/FORWARD LEDGER:", flush=True)
    cols = [
        "instrument", "discovery_closed", "discovery_pf_1bp", "discovery_pf_2bp",
        "forward_closed", "forward_pf_1bp", "forward_pf_2bp",
        "forward_worst_entry_year_pf_1bp_n5plus", "oos_closed", "oos_pf_1bp", "oos_pf_2bp",
    ]
    # Add worst forward cohort as a display-only metric for each asset.
    for ix, row in ledger_df.iterrows():
        inst = row["instrument"]
        c = cohort_df[
            (cohort_df["instrument"] == inst) & (cohort_df["cost_bps_rt"] == 1)
            & cohort_df["entry_year"].between(2022, 2025)
            & (cohort_df["n_closed_by_cutoff"] >= 5)
        ]
        vals = [float(x) for x in c["pf_entry_cohort"] if finite_number(x)]
        ledger_df.loc[ix, "forward_worst_entry_year_pf_1bp_n5plus"] = min(vals) if vals else np.nan
    print(ledger_df[cols].to_string(index=False), flush=True)
    print("\nLOCKED SELECTION + FORWARD VERDICT:", flush=True)
    print(json.dumps(selected, indent=2, default=safe), flush=True)
    print(f"Common OOS cutoff UTC: {common_end.isoformat()}", flush=True)
    print(f"Artifacts written to {out.resolve()}", flush=True)


if __name__ == "__main__":
    main()
