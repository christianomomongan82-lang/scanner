#!/usr/bin/env python3
"""R207: fade failed US cash-session 30-minute opening-range breakouts.

One preregistered hypothesis: after the 09:30-10:00 New York opening range,
detect the first M5 close outside it; if a later non-flat M5 close re-enters
the range within 60 minutes, reverse the breakout at the next non-flat M5 open.
Stop at the extreme reached from breakout through failure; target 2R. One
attempt/day, one open position/instrument. BID-only bars are a screening proxy.
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
    """One candidate per NY date: fade the first breakout that fails within 60m."""
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

    candidates = []
    session_rows = []
    valid_days = 0
    breakout_days = 0
    failed_breakout_days = 0
    skipped_or_missing = 0
    skipped_or_inactive = 0
    skipped_zero_range = 0
    skipped_no_failure = 0

    for ny_day, group in frame.groupby("ny_date", sort=True):
        ids = group["row"].to_numpy(dtype=np.int64)
        minute_to_row = {
            int(minutes[i]): int(i)
            for i in ids
            if 570 <= int(minutes[i]) < 600
        }
        if any(m not in minute_to_row for m in OR_MINUTES):
            skipped_or_missing += 1
            session_rows.append({
                "instrument": instrument, "ny_date": str(ny_day), "valid_or": False,
                "reason": "missing_one_or_more_30m_range_bars",
            })
            continue

        or_ids = np.asarray([minute_to_row[m] for m in OR_MINUTES], dtype=np.int64)
        active_or = int((~flat[or_ids]).sum())
        or_high = float(np.max(hi[or_ids]))
        or_low = float(np.min(lo[or_ids]))
        if active_or < 4:
            skipped_or_inactive += 1
            session_rows.append({
                "instrument": instrument, "ny_date": str(ny_day), "valid_or": False,
                "reason": "fewer_than_four_nonflat_or_bars", "or_nonflat_bars": active_or,
                "or_high": or_high, "or_low": or_low,
            })
            continue
        if not (math.isfinite(or_high) and math.isfinite(or_low) and or_high > or_low):
            skipped_zero_range += 1
            session_rows.append({
                "instrument": instrument, "ny_date": str(ny_day), "valid_or": False,
                "reason": "invalid_or_range", "or_nonflat_bars": active_or,
                "or_high": or_high, "or_low": or_low,
            })
            continue

        valid_days += 1
        breakout_i = None
        breakout_direction = 0
        for i in ids:
            minute = int(minutes[i])
            if minute < SIGNAL_START or minute > LAST_SIGNAL_BAR or flat[i]:
                continue
            if close[i] > or_high:
                breakout_i, breakout_direction = int(i), 1
                break
            if close[i] < or_low:
                breakout_i, breakout_direction = int(i), -1
                break

        base = {
            "instrument": instrument, "ny_date": str(ny_day), "valid_or": True,
            "or_nonflat_bars": active_or, "or_high": or_high, "or_low": or_low,
            "or_range_points": or_high - or_low,
        }
        if breakout_i is None:
            session_rows.append({**base, "reason": "no_initial_breakout"})
            continue

        breakout_days += 1
        breakout_close = mt[breakout_i] + pd.Timedelta(minutes=5)
        failure_i = None
        deadline = breakout_close + pd.Timedelta(minutes=60)
        for j in ids:
            if int(j) <= breakout_i:
                continue
            minute = int(minutes[j])
            if minute > LAST_SIGNAL_BAR:
                break
            close_time = mt[j] + pd.Timedelta(minutes=5)
            if close_time > deadline:
                break
            if flat[j]:
                continue
            # Failure occurs only when a later completed close returns to the
            # original 30-minute opening range. A wick alone is insufficient.
            if breakout_direction == 1 and close[j] <= or_high:
                failure_i = int(j)
                break
            if breakout_direction == -1 and close[j] >= or_low:
                failure_i = int(j)
                break

        if failure_i is None:
            skipped_no_failure += 1
            session_rows.append({
                **base, "reason": "breakout_did_not_reenter_within_60m",
                "breakout_direction": "up" if breakout_direction == 1 else "down",
                "breakout_bar_open_utc": mt[breakout_i].isoformat(),
                "breakout_close_utc": breakout_close.isoformat(),
            })
            continue

        failed_breakout_days += 1
        # The stop is beyond the most adverse excursion from the initial breakout
        # through the confirmed re-entry close, known before entry.
        excursion = slice(breakout_i, failure_i + 1)
        if breakout_direction == 1:
            stop = float(np.max(hi[excursion]))
            trade_direction = -1
        else:
            stop = float(np.min(lo[excursion]))
            trade_direction = 1

        failure_close = mt[failure_i] + pd.Timedelta(minutes=5)
        entry_i = None
        for k in ids:
            if mt[k] < failure_close:
                continue
            if int(minutes[k]) >= SESSION_CLOSE:
                break
            if not flat[k]:
                entry_i = int(k)
                break

        session_rows.append({
            **base, "reason": "failed_breakout_confirmed",
            "breakout_direction": "up" if breakout_direction == 1 else "down",
            "trade_direction": "long" if trade_direction == 1 else "short",
            "breakout_bar_open_utc": mt[breakout_i].isoformat(),
            "breakout_close_utc": breakout_close.isoformat(),
            "failure_bar_open_utc": mt[failure_i].isoformat(),
            "failure_close_utc": failure_close.isoformat(),
            "breakout_excursion_extreme_stop": stop,
        })
        candidates.append({
            "config": "R207_US_ORB_FAILED_BREAKOUT_FADE_60M_RR2",
            "instrument": instrument,
            "ny_date": str(ny_day),
            "direction": "long" if trade_direction == 1 else "short",
            "direction_sign": trade_direction,
            "breakout_direction": "up" if breakout_direction == 1 else "down",
            "or_high": or_high,
            "or_low": or_low,
            "or_range_points": or_high - or_low,
            "or_nonflat_bars": active_or,
            "signal_bar_open_utc": mt[failure_i].isoformat(),
            "signal_close_utc": failure_close.isoformat(),
            "signal_i": failure_i,
            "breakout_bar_open_utc": mt[breakout_i].isoformat(),
            "breakout_close_utc": breakout_close.isoformat(),
            "breakout_excursion_extreme_stop": stop,
            "stop": stop,
            "entry_i": entry_i,
        })

    diag = {
        "ny_dates_in_data": int(frame["ny_date"].nunique()),
        "valid_opening_ranges": valid_days,
        "initial_breakout_days": breakout_days,
        "failed_breakout_candidates": failed_breakout_days,
        "days_skipped_missing_or_bars": skipped_or_missing,
        "days_skipped_inactive_or": skipped_or_inactive,
        "days_skipped_invalid_or_range": skipped_zero_range,
        "breakouts_without_failure_within_60m": skipped_no_failure,
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
        target = entry + RR * risk if direction == 1 else entry - RR * risk

        exit_time = None
        exit_price = np.nan
        reason = "OPEN_AT_DATA_END"
        flat_skipped = 0
        for j in range(entry_i, len(mt)):
            if flat[j]:
                flat_skipped += 1
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
            "breakout_direction": candidate["breakout_direction"],
            "breakout_bar_open_utc": candidate["breakout_bar_open_utc"],
            "breakout_close_utc": candidate["breakout_close_utc"],
            "breakout_excursion_extreme_stop": candidate["breakout_excursion_extreme_stop"],
            "or_high": candidate["or_high"],
            "or_low": candidate["or_low"],
            "or_range_points": candidate["or_range_points"],
            "or_nonflat_bars": candidate["or_nonflat_bars"],
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
            f"SOURCE PASS {inst}: M5={len(m5):,}; valid OR days={build_diag['valid_opening_ranges']:,}; "
            f"first breakouts={build_diag['first_breakout_signals']:,}; taken={len(trades):,}",
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
        "research": "R207: US cash-session failed opening-range breakout fade",
        "run_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "common_oos_cutoff_utc": common_end.isoformat(),
        "assets": source_meta,
        "locked_rule": {
            "session_timezone": TZ_NY,
            "opening_range": "six M5 bars opening 09:30, 09:35, 09:40, 09:45, 09:50 and 09:55 New York time; require all six and at least four non-flat bars",
            "signal": "first M5 close after 10:00 and no later than 15:50 ET that closes beyond the opening-range high or low",
            "entry": "first non-flat M5 open at or after the signal close and before 16:00 ET on the same New York date",
            "attempt_limit": "one first-breakout attempt per instrument per NY session date",
            "failure_confirmation": "first M5 close back inside the opening range within 60 minutes after the first close outside it; a wick alone is insufficient",
            "stop": "most adverse high/low from the first breakout bar through the confirmed failure close",
            "target": "2R from entry based on entry-to-excursion-stop risk",
            "exit": "M5 BID OHLC; SL before TP; gap through stop fills at open; no time stop; flat synthetic M5 bars skipped",
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
            "Only one pre-registered ORB rule is tested; no parameter grid.",
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

    print("\nR207 DISCOVERY/FORWARD LEDGER:", flush=True)
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
    print(ledger_df[cols[:-1] + ["forward_worst_entry_year_pf_1bp_n5plus"] + cols[-3:]].to_string(index=False), flush=True)
    print("\nLOCKED SELECTION + FORWARD VERDICT:", flush=True)
    print(json.dumps(selected, indent=2, default=safe), flush=True)
    print(f"Common OOS cutoff UTC: {common_end.isoformat()}", flush=True)
    print(f"Artifacts written to {out.resolve()}", flush=True)


if __name__ == "__main__":
    main()
