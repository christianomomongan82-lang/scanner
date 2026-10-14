#!/usr/bin/env python3
"""R253: preregistered EURUSD UTC Asian-range breakout execution test.

A closed H1 close outside the completed 00:00-05:00 UTC range is the signal.
Entries occur only at the following exact H1 open. Stop/target collisions are
resolved stop-first. Buffer/RR alternatives are chosen only on 2021 validation;
2022-2025 and 2026 remain untouched acceptance periods.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(".")
DATA = ROOT / "dl" / "r251_fx"
OUT = ROOT / "research"
PIP = 0.0001
BUFFERS = (0.0, 0.05)       # fraction of the completed 00:00-05:00 range
REWARD_RISKS = (1.0, 1.5, 2.0)
MIN_STOP_PIPS = 5.0
MAX_STOP_PIPS = 60.0
ENTRY_SIGNAL_HOURS = tuple(range(6, 11))  # signal candle opens 06:00..10:00 UTC
RANGE_HOURS = tuple(range(0, 6))
EXIT_HOUR_UTC = 16
EXTRA_COSTS = (0.0, 0.5, 1.0, 2.0)
MIN_VALIDATION_TRADES = 50
BOOTSTRAP_DRAWS = 2000
BOOTSTRAP_BLOCK_WEEKS = 4

TRAIN_START = pd.Timestamp("2017-01-01T00:00:00Z")
TRAIN_END = pd.Timestamp("2021-01-01T00:00:00Z")
VALID_START = pd.Timestamp("2021-01-01T00:00:00Z")
VALID_END = pd.Timestamp("2022-01-01T00:00:00Z")
FORWARD_START = pd.Timestamp("2022-01-01T00:00:00Z")
FORWARD_END = pd.Timestamp("2026-01-01T00:00:00Z")
OOS_START = pd.Timestamp("2026-01-01T00:00:00Z")
OOS_END = pd.Timestamp("2026-10-14T00:00:00Z")


def parse_bars(path: Path):
    if not path.is_file():
        raise FileNotFoundError(f"Cached quote file not found: {path}")
    raw = pd.read_csv(path)
    raw.columns = [str(c).replace("\ufeff", "").strip().lower() for c in raw.columns]
    tcol = next((c for c in ("timestamp", "datetime", "date", "time") if c in raw.columns), None)
    if tcol is None:
        raise ValueError(f"No timestamp field in {path}: {list(raw.columns)}")
    ts = raw[tcol].astype(str).str.strip()
    numeric = pd.to_numeric(ts, errors="coerce")
    if numeric.notna().mean() > 0.95:
        med = float(numeric.abs().median())
        unit = "ms" if med >= 1e11 else ("s" if med >= 1e8 else None)
        if unit is None:
            raise ValueError(f"Unknown timestamp scale in {path}: {med}")
        idx = pd.to_datetime(numeric, unit=unit, utc=True, errors="coerce")
    else:
        idx = pd.to_datetime(ts, utc=True, errors="coerce")
    required = ["open", "high", "low", "close"]
    missing = set(required) - set(raw.columns)
    if missing or idx.isna().any():
        raise ValueError(f"Invalid timestamps or missing OHLC in {path}; missing={missing}")
    bars = raw[required].apply(pd.to_numeric, errors="coerce")
    bars.columns = ["Open", "High", "Low", "Close"]
    bars.index = pd.DatetimeIndex(idx, name="timestamp_utc")
    bars = bars.replace([np.inf, -np.inf], np.nan).dropna().sort_index()
    dups = int(bars.index.duplicated(keep="last").sum())
    bars = bars.loc[~bars.index.duplicated(keep="last")]
    valid = (
        (bars.High >= bars[["Open", "Close"]].max(axis=1))
        & (bars.Low <= bars[["Open", "Close"]].min(axis=1))
        & (bars.High >= bars.Low)
    )
    invalid = int((~valid).sum())
    bars = bars.loc[valid]
    if bars.empty:
        raise ValueError(f"No valid quote bars in {path}")
    delta = bars.index.to_series().diff().dropna()
    diagnostics = {
        "rows": int(len(bars)),
        "duplicate_timestamps_removed": dups,
        "invalid_ohlc_rows_removed": invalid,
        "off_hour_timestamps": int(((bars.index.minute != 0) | (bars.index.second != 0)).sum()),
        "missing_hour_gaps": int((delta > pd.Timedelta(hours=1)).sum()),
        "start_utc": bars.index[0].isoformat(),
        "end_utc": bars.index[-1].isoformat(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    return bars, diagnostics


def pf(values):
    x = np.asarray(values, dtype=float)
    gp = float(x[x > 0].sum())
    gl = float(-x[x < 0].sum())
    if gl <= 0:
        return "INF" if gp > 0 else None
    return gp / gl


def safe_greater(value, threshold):
    return isinstance(value, (int, float, np.integer, np.floating)) and np.isfinite(value) and value >= threshold


def period_metrics(trades, start, end, cost):
    kept = [
        t for t in trades
        if start <= pd.Timestamp(t["entry_utc"]) < end
        and start <= pd.Timestamp(t["exit_utc"]) < end
    ]
    v = np.asarray([t["gross_pips"] - cost for t in kept], dtype=float)
    weeks = max((end - start).total_seconds() / (7 * 86400), 1 / 7)
    return {
        "trades": int(len(v)),
        "PF": pf(v),
        "net_pips": float(v.sum()) if len(v) else 0.0,
        "mean_net_pips_per_trade": float(v.mean()) if len(v) else None,
        "win_rate": float((v > 0).mean()) if len(v) else None,
        "trades_per_week": float(len(v) / weeks),
    }


def simulate_config(bid, ask, date_positions, buffer_fraction, rr_multiple):
    trades = []
    diagnostics = {
        "calendar_days_seen": int(len(date_positions)),
        "days_with_complete_hourly_grid": 0,
        "days_skipped_incomplete_grid": 0,
        "days_skipped_no_breakout": 0,
        "days_skipped_invalid_stop_distance": 0,
        "days_skipped_invalid_quotes": 0,
        "trades_closed": 0,
        "stop_first_collisions": 0,
        "scheduled_time_exits": 0,
        "stop_exits": 0,
        "target_exits": 0,
    }
    for day, positions in date_positions.items():
        # Positions correspond to exact hourly opens 00:00 through 16:00 UTC.
        if positions is None:
            diagnostics["days_skipped_incomplete_grid"] += 1
            continue
        diagnostics["days_with_complete_hourly_grid"] += 1
        rpos = [positions[h] for h in RANGE_HOURS]
        upper = float(bid.High.iloc[rpos].max())
        lower = float(bid.Low.iloc[rpos].min())
        width_pips = (upper - lower) / PIP
        if not np.isfinite([upper, lower]).all() or width_pips <= 0:
            diagnostics["days_skipped_invalid_quotes"] += 1
            continue
        buffer_px = (upper - lower) * buffer_fraction
        signal_i = None
        direction = 0
        for hour in ENTRY_SIGNAL_HOURS:
            i = positions[hour]
            c = float(bid.Close.iloc[i])
            if c > upper + buffer_px:
                signal_i, direction = i, 1
                break
            if c < lower - buffer_px:
                signal_i, direction = i, -1
                break
        if signal_i is None:
            diagnostics["days_skipped_no_breakout"] += 1
            continue
        entry_i = positions[(bid.index[signal_i] + pd.Timedelta(hours=1)).hour]
        # Index by timestamp to avoid accidentally treating a missing bar as a next bar.
        entry_time = bid.index[signal_i] + pd.Timedelta(hours=1)
        if bid.index[entry_i] != entry_time:
            diagnostics["days_skipped_incomplete_grid"] += 1
            continue
        exit_i = positions[EXIT_HOUR_UTC]
        entry_bid = float(bid.Open.iloc[entry_i])
        entry_ask = float(ask.Open.iloc[entry_i])
        scheduled_bid = float(bid.Open.iloc[exit_i])
        scheduled_ask = float(ask.Open.iloc[exit_i])
        if not np.isfinite([entry_bid, entry_ask, scheduled_bid, scheduled_ask]).all() or entry_ask < entry_bid or scheduled_ask < scheduled_bid:
            diagnostics["days_skipped_invalid_quotes"] += 1
            continue
        if direction == 1:
            stop = lower
            risk_px = entry_ask - stop
        else:
            stop = upper
            risk_px = stop - entry_bid
        risk_pips = risk_px / PIP
        if not np.isfinite(risk_pips) or risk_pips < MIN_STOP_PIPS or risk_pips > MAX_STOP_PIPS:
            diagnostics["days_skipped_invalid_stop_distance"] += 1
            continue
        if direction == 1:
            target = entry_ask + rr_multiple * risk_px
        else:
            target = entry_bid - rr_multiple * risk_px
        exit_price = None
        exit_reason = None
        exit_time = None
        for j in range(entry_i, exit_i):
            if direction == 1:
                so = float(bid.Open.iloc[j])
                sh = float(bid.High.iloc[j])
                sl = float(bid.Low.iloc[j])
                stop_hit = sl <= stop
                target_hit = sh >= target
                if stop_hit:
                    if target_hit:
                        diagnostics["stop_first_collisions"] += 1
                    exit_price = so if so <= stop else stop
                    exit_reason = "STOP"
                elif target_hit:
                    exit_price = so if so >= target else target
                    exit_reason = "TARGET"
            else:
                so = float(ask.Open.iloc[j])
                sh = float(ask.High.iloc[j])
                sl = float(ask.Low.iloc[j])
                stop_hit = sh >= stop
                target_hit = sl <= target
                if stop_hit:
                    if target_hit:
                        diagnostics["stop_first_collisions"] += 1
                    exit_price = so if so >= stop else stop
                    exit_reason = "STOP"
                elif target_hit:
                    exit_price = so if so <= target else target
                    exit_reason = "TARGET"
            if exit_reason is not None:
                exit_time = bid.index[j]
                break
        if exit_reason is None:
            exit_time = bid.index[exit_i]
            exit_price = scheduled_bid if direction == 1 else scheduled_ask
            exit_reason = "TIME_EXIT_16UTC"
            diagnostics["scheduled_time_exits"] += 1
        elif exit_reason == "STOP":
            diagnostics["stop_exits"] += 1
        elif exit_reason == "TARGET":
            diagnostics["target_exits"] += 1
        if direction == 1:
            gross_pips = (float(exit_price) - entry_ask) / PIP
        else:
            gross_pips = (entry_bid - float(exit_price)) / PIP
        trades.append({
            "candidate": f"BUF{buffer_fraction:.2f}_RR{rr_multiple:.1f}",
            "buffer_fraction_of_range": buffer_fraction,
            "reward_risk_multiple": rr_multiple,
            "range_high_bid": upper,
            "range_low_bid": lower,
            "range_width_pips": width_pips,
            "signal_close_utc": (bid.index[signal_i] + pd.Timedelta(hours=1)).isoformat(),
            "entry_utc": entry_time.isoformat(),
            "exit_utc": exit_time.isoformat(),
            "direction": "LONG" if direction == 1 else "SHORT",
            "entry_bid": entry_bid,
            "entry_ask": entry_ask,
            "exit_price_executable": float(exit_price),
            "exit_reason": exit_reason,
            "stop_price_reference": stop,
            "target_price_reference": target,
            "risk_pips_at_entry": risk_pips,
            "gross_pips": float(gross_pips),
            "holding_hours": float((exit_time - entry_time).total_seconds() / 3600),
        })
        diagnostics["trades_closed"] += 1
    return trades, diagnostics


def bootstrap_forward(trades, cost=1.0):
    forward = [
        t for t in trades
        if FORWARD_START <= pd.Timestamp(t["entry_utc"]) < FORWARD_END
        and pd.Timestamp(t["exit_utc"]) < FORWARD_END
    ]
    if len(forward) < 100:
        return {"draws": 0, "p_mean_positive": None, "ci95_mean_pips": None}
    first_monday = FORWARD_START.normalize() - pd.Timedelta(days=FORWARD_START.dayofweek)
    mondays = pd.date_range(first_monday, FORWARD_END, freq="W-MON", inclusive="left")
    weekly = {w: [] for w in mondays}
    for t in forward:
        dt = pd.Timestamp(t["entry_utc"])
        monday = dt.normalize() - pd.Timedelta(days=dt.dayofweek)
        if monday in weekly:
            weekly[monday].append(float(t["gross_pips"] - cost))
    arrs = [np.asarray(weekly[w], dtype=float) for w in mondays]
    rng = np.random.default_rng(253)
    estimates = []
    n = len(arrs)
    for _ in range(BOOTSTRAP_DRAWS):
        sampled = []
        while len(sampled) < n:
            start = int(rng.integers(0, n))
            for k in range(BOOTSTRAP_BLOCK_WEEKS):
                sampled.append(arrs[(start + k) % n])
                if len(sampled) >= n:
                    break
        values = np.concatenate(sampled) if sampled else np.array([], dtype=float)
        if len(values):
            estimates.append(float(values.mean()))
    x = np.asarray(estimates, dtype=float)
    return {
        "draws": int(len(x)),
        "p_mean_positive": float(np.mean(x > 0)) if len(x) else None,
        "ci95_mean_pips": [float(np.quantile(x, 0.025)), float(np.quantile(x, 0.975))] if len(x) else None,
        "method": "circular 4-week block bootstrap over forward entry-week trade returns",
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report_path = OUT / "R253_session_range_results.json"
    trades_path = OUT / "R253_session_range_trades.csv"
    annual_path = OUT / "R253_session_range_annual.csv"
    report = {
        "status": "STARTED",
        "strategy_family": "EURUSD UTC Asian-range close breakout",
        "verdict": "NOT_EVALUATED",
        "preregistered_design": {
            "range_window_utc": "bars opening 00:00-05:00 UTC inclusive; complete by 06:00",
            "signal_window_utc": "first completed H1 candle opening 06:00-10:00 UTC with close beyond range plus buffer",
            "entry": "next exact H1 bar open after signal candle closes",
            "initial_stop": "opposite edge of completed Asian range",
            "target": "1R, 1.5R, or 2R from entry-to-stop distance",
            "max_positions": "one attempt per UTC day and candidate",
            "intrabar_execution": "BID OHLC for long exits, ASK OHLC for short exits; stop checked before target; stop gaps filled at observed bar open",
            "scheduled_exit": "16:00 UTC open if neither stop nor target was hit before that open",
            "valid_risk_range_pips": [MIN_STOP_PIPS, MAX_STOP_PIPS],
            "buffer_fractions_of_range": list(BUFFERS),
            "reward_risk_multiples": list(REWARD_RISKS),
            "extra_cost_stress_pips_on_top_of_observed_bidask": list(EXTRA_COSTS),
            "selection_rule": "choose candidate with highest 2021 validation PF at +1 pip among candidates with >=50 validation trades; tie-break mean net pips then trade count; 2017-2020 and all 2022+ periods are not used for selection",
        },
    }
    try:
        bid, bdiag = parse_bars(DATA / "eurusd_bid_H1.csv")
        ask, adiag = parse_bars(DATA / "eurusd_ask_H1.csv")
        common = bid.index.intersection(ask.index).sort_values()
        if len(common) < 20000:
            raise RuntimeError(f"Only {len(common)} common EURUSD bid/ask H1 bars; refusing to test")
        bid, ask = bid.loc[common], ask.loc[common]
        if (ask.Open < bid.Open).any():
            raise RuntimeError("EURUSD ASK open below BID open")
        start_day = common[0].normalize()
        end_day = common[-1].normalize()
        date_positions = {}
        skipped_days = 0
        for day in pd.date_range(start_day, end_day, freq="D"):
            expected = pd.date_range(day, day + pd.Timedelta(hours=EXIT_HOUR_UTC), freq="h")
            p = bid.index.get_indexer(expected)
            if len(p) != EXIT_HOUR_UTC + 1 or (p < 0).any():
                date_positions[day] = None
                skipped_days += 1
            else:
                good = True
                for left, right in zip(p[:-1], p[1:]):
                    if bid.index[right] - bid.index[left] != pd.Timedelta(hours=1):
                        good = False
                        break
                date_positions[day] = p if good else None
                if not good:
                    skipped_days += 1
        candidate_trades = {}
        candidate_diagnostics = {}
        for buffer_fraction in BUFFERS:
            for rr in REWARD_RISKS:
                name = f"BUF{buffer_fraction:.2f}_RR{rr:.1f}"
                trades, diagnostics = simulate_config(bid, ask, date_positions, buffer_fraction, rr)
                candidate_trades[name] = trades
                candidate_diagnostics[name] = diagnostics
        validation_rank = []
        validation_scores = {}
        for name, trades in candidate_trades.items():
            m = period_metrics(trades, VALID_START, VALID_END, 1.0)
            validation_scores[name] = m
            if m["trades"] >= MIN_VALIDATION_TRADES:
                score_pf = float(m["PF"]) if isinstance(m["PF"], (int, float)) and np.isfinite(m["PF"]) else (-1.0 if m["PF"] is None else 999.0)
                validation_rank.append((score_pf, m["mean_net_pips_per_trade"] or -999.0, m["trades"], name))
        if not validation_rank:
            raise RuntimeError("No candidate met the preregistered 50-trade validation minimum.")
        validation_rank.sort(reverse=True)
        chosen = validation_rank[0][3]
        trades = candidate_trades[chosen]
        trade_frame = pd.DataFrame([
            {**t, **{f"net_pips_cost_{cost:.1f}": t["gross_pips"] - cost for cost in EXTRA_COSTS}}
            for t in trades
        ])
        trade_frame.to_csv(trades_path, index=False)
        phases = {
            "discovery_2017_2020": (TRAIN_START, TRAIN_END),
            "validation_2021": (VALID_START, VALID_END),
            "forward_2022_2025": (FORWARD_START, FORWARD_END),
            "oos_2026": (OOS_START, OOS_END),
        }
        metrics = {
            phase: {str(cost): period_metrics(trades, start, end, cost) for cost in EXTRA_COSTS}
            for phase, (start, end) in phases.items()
        }
        annual = []
        for year in range(2017, 2027):
            start, end = pd.Timestamp(f"{year}-01-01", tz="UTC"), pd.Timestamp(f"{year+1}-01-01", tz="UTC")
            annual.append({
                "year": year,
                **{f"PF_cost_{cost:.1f}": period_metrics(trades, start, end, cost)["PF"] for cost in EXTRA_COSTS},
                **{f"trades_cost_{cost:.1f}": period_metrics(trades, start, end, cost)["trades"] for cost in EXTRA_COSTS},
                **{f"mean_pips_cost_{cost:.1f}": period_metrics(trades, start, end, cost)["mean_net_pips_per_trade"] for cost in EXTRA_COSTS},
            })
        pd.DataFrame(annual).to_csv(annual_path, index=False)
        bootstrap = bootstrap_forward(trades, 1.0)
        fwd_years = [x for x in annual if 2022 <= x["year"] <= 2025 and x["trades_cost_1.0"] >= 20]
        validation = metrics["validation_2021"]["1.0"]
        discovery = metrics["discovery_2017_2020"]["1.0"]
        forward_1, forward_2 = metrics["forward_2022_2025"]["1.0"], metrics["forward_2022_2025"]["2.0"]
        oos = metrics["oos_2026"]["1.0"]
        gates = {
            "validation_min_50_trades": validation["trades"] >= MIN_VALIDATION_TRADES,
            "validation_PF_at_1pip_ge_1.05": safe_greater(validation["PF"], 1.05),
            "discovery_min_100_trades": discovery["trades"] >= 100,
            "discovery_PF_at_1pip_ge_1.00": safe_greater(discovery["PF"], 1.00),
            "forward_min_100_trades": forward_1["trades"] >= 100,
            "forward_PF_at_1pip_ge_1.10": safe_greater(forward_1["PF"], 1.10),
            "forward_PF_at_2pip_ge_1.05": safe_greater(forward_2["PF"], 1.05),
            "forward_frequency_ge_2_trades_per_week": safe_greater(forward_1["trades_per_week"], 2.0),
            "each_forward_year_with_20plus_trades_PF_ge_1_at_1pip": bool(fwd_years) and all(safe_greater(x["PF_cost_1.0"], 1.0) for x in fwd_years),
            "forward_4week_block_bootstrap_positive_95pct": bool(bootstrap["ci95_mean_pips"] and bootstrap["ci95_mean_pips"][0] > 0 and bootstrap["p_mean_positive"] >= 0.95),
            "oos_min_30_trades": oos["trades"] >= 30,
            "oos_PF_at_1pip_ge_1.00": safe_greater(oos["PF"], 1.00),
        }
        report.update({
            "status": "COMPLETE",
            "data": {
                "eurusd_bid": bdiag,
                "eurusd_ask": adiag,
                "common_hourly_rows": int(len(common)),
                "common_start_utc": common[0].isoformat(),
                "common_end_utc": common[-1].isoformat(),
                "calendar_days": int(len(date_positions)),
                "days_with_incomplete_or_missing_hourly_grid": int(skipped_days),
                "no_missing_bars_synthesized": True,
            },
            "all_candidate_validation_cost_1pip": validation_scores,
            "selected_candidate": chosen,
            "candidate_execution_diagnostics": candidate_diagnostics,
            "selected_metrics_by_period_and_cost": metrics,
            "annual_cohorts": annual,
            "forward_block_bootstrap_cost_1pip": bootstrap,
            "acceptance_gates": gates,
            "verdict": "LULUS" if all(gates.values()) else "GAGAL",
            "verdict_rule": "Every validation, discovery, forward, annual stability, bootstrap, frequency, and 2026 OOS gate must pass. No post-forward tuning.",
            "trade_ledger_sha256": hashlib.sha256(trades_path.read_bytes()).hexdigest(),
            "limitations": [
                "BID and ASK OHLC are hourly bars; when both stop and target are touched in the same H1 bar, the test conservatively assumes stop first.",
                "Actual historical quote-side prices are used at H1 open and within-bar extrema; broker commissions and slippage are still represented by additional cost stresses, not live measurements.",
                "Funded-specific compliance cannot be proven from this alpha test alone; any strategy passing must be simulated against the firm's complete account rules before being called funded-ready."
            ],
        })
    except Exception as exc:
        report.update({
            "status": "FAILED_RUN",
            "verdict": "GAGAL",
            "error": f"{type(exc).__name__}: {exc}",
            "decision": "No partial performance result is accepted when the locked data or calculation pipeline fails.",
        })
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({
        "status": report["status"],
        "verdict": report["verdict"],
        "selected_candidate": report.get("selected_candidate"),
        "metrics": report.get("selected_metrics_by_period_and_cost"),
        "gates": report.get("acceptance_gates"),
        "error": report.get("error"),
    }, indent=2))
    if report["status"] != "COMPLETE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
