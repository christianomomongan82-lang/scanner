#!/usr/bin/env python3
"""R252: preregistered EURUSD H1 tail-event momentum vs reversal test.

Thresholds are fit only on 2017-2020. One winner is selected on calendar 2021
validation, then evaluated once on 2022-2025 forward and 2026 OOS. No forward/OOS
parameter tuning is allowed.
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
LOOKBACKS = (3, 6, 12)
DIRECTIONS = ("momentum", "reversal")
HOLD_HOURS = 4
TAIL_QUANTILE = 0.90
EXTRA_COSTS = (0.0, 0.5, 1.0, 2.0)
BOOTSTRAP_DRAWS = 2000
BOOTSTRAP_BLOCK_WEEKS = 4
MIN_VALIDATION_TRADES = 50

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
    duplicate_count = int(bars.index.duplicated(keep="last").sum())
    bars = bars.loc[~bars.index.duplicated(keep="last")]
    valid = (
        (bars.High >= bars[["Open", "Close"]].max(axis=1))
        & (bars.Low <= bars[["Open", "Close"]].min(axis=1))
        & (bars.High >= bars.Low)
    )
    invalid_count = int((~valid).sum())
    bars = bars.loc[valid]
    if bars.empty:
        raise ValueError(f"No valid quote bars in {path}")
    if (bars.High < bars.Low).any():
        raise ValueError(f"Invalid OHLC remains after validation in {path}")
    gaps = bars.index.to_series().diff().dropna()
    diag = {
        "rows": int(len(bars)),
        "duplicate_timestamps_removed": duplicate_count,
        "invalid_ohlc_rows_removed": invalid_count,
        "off_hour_timestamps": int(((bars.index.minute != 0) | (bars.index.second != 0)).sum()),
        "missing_hour_gaps": int((gaps > pd.Timedelta(hours=1)).sum()),
        "start_utc": bars.index[0].isoformat(),
        "end_utc": bars.index[-1].isoformat(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    return bars, diag


def pf(values):
    x = np.asarray(values, dtype=float)
    gp = float(x[x > 0].sum())
    gl = float(-x[x < 0].sum())
    if gl <= 0:
        return "INF" if gp > 0 else None
    return gp / gl


def make_candidate(bid, ask, lookback, mode, threshold):
    idx = bid.index
    close = bid.Close.to_numpy(float)
    n = len(idx)
    ret = np.full(n, np.nan, dtype=float)
    abs_ret = np.full(n, np.nan, dtype=float)
    valid_ret = np.zeros(n, dtype=bool)
    ns = idx.asi8
    hour_ns = int(pd.Timedelta(hours=1).value)
    for i in range(lookback, n):
        if ns[i] - ns[i - lookback] != lookback * hour_ns:
            continue
        r = close[i] / close[i - lookback] - 1.0
        if np.isfinite(r):
            ret[i] = r
            abs_ret[i] = abs(r)
            valid_ret[i] = True
    signal_idx = []
    for i in range(lookback + 1, n - HOLD_HOURS - 1):
        if not valid_ret[i] or not valid_ret[i - 1]:
            continue
        if ns[i] - ns[i - 1] != hour_ns:
            continue
        # A single entry is emitted when the rolling move first crosses its frozen
        # training-only tail threshold, not on every bar while beyond the threshold.
        if not (abs_ret[i] >= threshold and abs_ret[i - 1] < threshold):
            continue
        entry_i = i + 1
        exit_i = i + HOLD_HOURS + 1
        if ns[entry_i] - ns[i] != hour_ns:
            continue
        if ns[exit_i] - ns[entry_i] != HOLD_HOURS * hour_ns:
            continue
        direction = 1 if ret[i] > 0 else -1
        if mode == "reversal":
            direction *= -1
        signal_idx.append((i, entry_i, exit_i, direction, float(ret[i])))
    trades = []
    active_exit = -1
    overlap_skipped = 0
    for i, entry_i, exit_i, direction, signal_return in signal_idx:
        if entry_i <= active_exit:
            overlap_skipped += 1
            continue
        entry_bid = float(bid.Open.iloc[entry_i])
        entry_ask = float(ask.Open.iloc[entry_i])
        exit_bid = float(bid.Open.iloc[exit_i])
        exit_ask = float(ask.Open.iloc[exit_i])
        if not np.isfinite([entry_bid, entry_ask, exit_bid, exit_ask]).all():
            continue
        if entry_ask < entry_bid or exit_ask < exit_bid:
            raise ValueError(f"Invalid bid/ask quote at indices {entry_i}/{exit_i}")
        if direction == 1:
            gross = (exit_bid - entry_ask) / PIP
        else:
            gross = (entry_bid - exit_ask) / PIP
        signal_close = idx[i] + pd.Timedelta(hours=1)
        trades.append({
            "candidate": f"L{lookback:02d}_{mode.upper()}",
            "lookback_hours": lookback,
            "direction_rule": mode,
            "tail_quantile": TAIL_QUANTILE,
            "training_threshold_abs_return": threshold,
            "signal_close_utc": signal_close.isoformat(),
            "entry_utc": idx[entry_i].isoformat(),
            "exit_utc": idx[exit_i].isoformat(),
            "direction": "LONG" if direction == 1 else "SHORT",
            "signal_return": signal_return,
            "entry_bid": entry_bid, "entry_ask": entry_ask,
            "exit_bid": exit_bid, "exit_ask": exit_ask,
            "gross_pips": float(gross),
            "holding_hours": HOLD_HOURS,
        })
        active_exit = exit_i
    return trades, {"signal_crossings": len(signal_idx), "overlap_skipped": overlap_skipped}


def period_metrics(trades, start, end, cost):
    period = [
        t for t in trades
        if start <= pd.Timestamp(t["entry_utc"]) < end
        and pd.Timestamp(t["exit_utc"]) < end
        and pd.Timestamp(t["exit_utc"]) >= start
    ]
    values = np.asarray([t["gross_pips"] - cost for t in period], dtype=float)
    weeks = max((end - start).total_seconds() / (7 * 86400), 1 / 7)
    return {
        "trades": int(len(values)),
        "PF": pf(values),
        "net_pips": float(values.sum()) if len(values) else 0.0,
        "mean_net_pips_per_trade": float(values.mean()) if len(values) else None,
        "win_rate": float((values > 0).mean()) if len(values) else None,
        "trades_per_week": float(len(values) / weeks),
    }


def bootstrap_forward(trades, cost=1.0):
    forward = [
        t for t in trades
        if FORWARD_START <= pd.Timestamp(t["entry_utc"]) < FORWARD_END
        and pd.Timestamp(t["exit_utc"]) < FORWARD_END
    ]
    if len(forward) < 100:
        return {"draws": 0, "p_mean_positive": None, "ci95_mean_pips": None}
    first_monday = FORWARD_START.normalize()
    first_monday -= pd.Timedelta(days=first_monday.dayofweek)
    mondays = pd.date_range(first_monday, FORWARD_END, freq="W-MON", inclusive="left")
    weekly = {w: [] for w in mondays}
    for t in forward:
        dt = pd.Timestamp(t["entry_utc"])
        monday = dt.normalize() - pd.Timedelta(days=dt.dayofweek)
        if monday in weekly:
            weekly[monday].append(float(t["gross_pips"] - cost))
    arrs = [np.asarray(weekly[w], dtype=float) for w in mondays]
    rng = np.random.default_rng(252)
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


def safe_greater(value, threshold):
    return isinstance(value, (int, float, np.integer, np.floating)) and np.isfinite(value) and value >= threshold


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report_path = OUT / "R252_fx_threshold_results.json"
    trades_path = OUT / "R252_fx_threshold_trades.csv"
    annual_path = OUT / "R252_fx_threshold_annual.csv"
    report = {
        "status": "STARTED",
        "strategy_family": "EURUSD H1 threshold-crossing time-series momentum vs reversal",
        "verdict": "NOT_EVALUATED",
        "preregistered_design": {
            "candidates": [f"L{l:02d}_{d.upper()}" for l in LOOKBACKS for d in DIRECTIONS],
            "lookbacks_hours": list(LOOKBACKS),
            "signal": "first crossing of absolute L-hour EURUSD BID close return above its 2017-2020-only 90th percentile threshold",
            "modes": "momentum follows signed return; reversal fades signed return",
            "entry": "next exact hourly EURUSD open after completed signal candle",
            "exit": f"exactly {HOLD_HOURS} hours after entry at the next exact observed hourly open",
            "execution": "long ASK entry/BID exit; short BID entry/ASK exit",
            "threshold_fit_period": ["2017-01-01", "2021-01-01"],
            "validation_selection_period": ["2021-01-01", "2022-01-01"],
            "forward_period": ["2022-01-01", "2026-01-01"],
            "final_oos_period": ["2026-01-01", "2026-10-14"],
            "extra_cost_stress_pips_on_top_of_bid_ask": list(EXTRA_COSTS),
            "selection_rule": "among candidates with at least 50 validation trades, choose highest PF at +1 extra pip; tie-break higher mean net pips at +1, then higher trade count; forward and OOS results not used for selection",
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
        thresholds = {}
        all_candidates = {}
        diagnostics = {}
        for lookback in LOOKBACKS:
            ret = bid.Close / bid.Close.shift(lookback) - 1.0
            ns = bid.index.asi8
            valid = np.zeros(len(bid), dtype=bool)
            hour_ns = int(pd.Timedelta(hours=1).value)
            for i in range(lookback, len(bid)):
                valid[i] = (ns[i] - ns[i-lookback] == lookback * hour_ns) and np.isfinite(ret.iloc[i])
            close_time = bid.index + pd.Timedelta(hours=1)
            fit = valid & (close_time >= TRAIN_START) & (close_time < TRAIN_END)
            abs_train = np.abs(ret.to_numpy(float)[fit])
            if len(abs_train) < 1000:
                raise RuntimeError(f"Insufficient training returns for lookback={lookback}: {len(abs_train)}")
            thresholds[lookback] = float(np.quantile(abs_train, TAIL_QUANTILE))
            for mode in DIRECTIONS:
                trades, diag = make_candidate(bid, ask, lookback, mode, thresholds[lookback])
                name = f"L{lookback:02d}_{mode.upper()}"
                all_candidates[name] = trades
                diagnostics[name] = diag
        selection = []
        validation_metrics = {}
        for name, records in all_candidates.items():
            m = period_metrics(records, VALID_START, VALID_END, 1.0)
            validation_metrics[name] = m
            if m["trades"] >= MIN_VALIDATION_TRADES:
                pfval = m["PF"]
                sort_pf = float(pfval) if isinstance(pfval, (int, float)) and np.isfinite(pfval) else (-1.0 if pfval is None else 999.0)
                selection.append((sort_pf, m["mean_net_pips_per_trade"] or -999.0, m["trades"], name))
        if not selection:
            raise RuntimeError("No candidate reached the preregistered 50-trade validation minimum.")
        selection.sort(reverse=True)
        chosen = selection[0][3]
        records = all_candidates[chosen]
        trades_df = pd.DataFrame([
            {**r, **{f"net_pips_cost_{cost:.1f}": r["gross_pips"] - cost for cost in EXTRA_COSTS}}
            for r in records
        ])
        trades_df.to_csv(trades_path, index=False)

        phase_defs = {
            "discovery_2017_2020": (TRAIN_START, TRAIN_END),
            "validation_2021": (VALID_START, VALID_END),
            "forward_2022_2025": (FORWARD_START, FORWARD_END),
            "oos_2026": (OOS_START, OOS_END),
        }
        chosen_metrics = {
            phase: {str(cost): period_metrics(records, start, end, cost) for cost in EXTRA_COSTS}
            for phase, (start, end) in phase_defs.items()
        }
        candidate_scores = {
            name: {
                "threshold_abs_return": thresholds[int(name[1:3])],
                "validation_cost_1pip": validation_metrics[name],
                "discovery_cost_1pip": period_metrics(recs, TRAIN_START, TRAIN_END, 1.0),
            }
            for name, recs in all_candidates.items()
        }
        annual = []
        for year in range(2017, 2027):
            start, end = pd.Timestamp(f"{year}-01-01", tz="UTC"), pd.Timestamp(f"{year+1}-01-01", tz="UTC")
            annual.append({
                "year": year,
                **{f"PF_cost_{cost:.1f}": period_metrics(records, start, end, cost)["PF"] for cost in EXTRA_COSTS},
                **{f"trades_cost_{cost:.1f}": period_metrics(records, start, end, cost)["trades"] for cost in EXTRA_COSTS},
                **{f"mean_pips_cost_{cost:.1f}": period_metrics(records, start, end, cost)["mean_net_pips_per_trade"] for cost in EXTRA_COSTS},
            })
        pd.DataFrame(annual).to_csv(annual_path, index=False)
        bootstrap = bootstrap_forward(records, 1.0)
        fwd_years = [r for r in annual if 2022 <= r["year"] <= 2025 and r["trades_cost_1.0"] >= 20]
        selected_validation = chosen_metrics["validation_2021"]["1.0"]
        selected_discovery = chosen_metrics["discovery_2017_2020"]["1.0"]
        forward_1 = chosen_metrics["forward_2022_2025"]["1.0"]
        forward_2 = chosen_metrics["forward_2022_2025"]["2.0"]
        oos_1 = chosen_metrics["oos_2026"]["1.0"]
        gates = {
            "validation_min_50_trades": selected_validation["trades"] >= MIN_VALIDATION_TRADES,
            "validation_PF_at_1pip_ge_1.05": safe_greater(selected_validation["PF"], 1.05),
            "discovery_min_100_trades": selected_discovery["trades"] >= 100,
            "discovery_PF_at_1pip_ge_1.00": safe_greater(selected_discovery["PF"], 1.00),
            "forward_min_100_trades": forward_1["trades"] >= 100,
            "forward_PF_at_1pip_ge_1.10": safe_greater(forward_1["PF"], 1.10),
            "forward_PF_at_2pip_ge_1.05": safe_greater(forward_2["PF"], 1.05),
            "forward_frequency_ge_2_trades_per_week": safe_greater(forward_1["trades_per_week"], 2.0),
            "each_forward_year_with_20plus_trades_PF_ge_1_at_1pip": bool(fwd_years) and all(safe_greater(r["PF_cost_1.0"], 1.0) for r in fwd_years),
            "forward_4week_block_bootstrap_positive_95pct": bool(bootstrap["ci95_mean_pips"] and bootstrap["ci95_mean_pips"][0] > 0 and bootstrap["p_mean_positive"] >= 0.95),
            "oos_min_30_trades": oos_1["trades"] >= 30,
            "oos_PF_at_1pip_ge_1.00": safe_greater(oos_1["PF"], 1.00),
        }
        report.update({
            "status": "COMPLETE",
            "data": {
                "eurusd_bid": bdiag, "eurusd_ask": adiag,
                "common_hourly_rows": int(len(common)),
                "common_start_utc": common[0].isoformat(), "common_end_utc": common[-1].isoformat(),
                "extra_cost_is_added_on_top_of_observed_bidask": True,
            },
            "thresholds_fit_2017_2020_only": {str(k): v for k, v in thresholds.items()},
            "all_candidate_validation_and_discovery": candidate_scores,
            "candidate_diagnostics": diagnostics,
            "selected_candidate": chosen,
            "selected_validation_metrics_cost_1pip": selected_validation,
            "selected_metrics_by_period_and_cost": chosen_metrics,
            "annual_cohorts": annual,
            "forward_block_bootstrap_cost_1pip": bootstrap,
            "acceptance_gates": gates,
            "verdict": "LULUS" if all(gates.values()) else "GAGAL",
            "verdict_rule": "Every preregistered validation, discovery, forward, annual stability, bootstrap, frequency, and 2026 OOS gate must pass. No post-forward tuning.",
            "trade_ledger_sha256": hashlib.sha256(trades_path.read_bytes()).hexdigest(),
            "limitations": [
                "Historical data are Dukascopy EURUSD H1 quote-side opens and may differ from the exact funded broker feed.",
                "H1 opens model entry and exit; spread changes and slippage within the hour are not captured beyond observed open quotes.",
                "The one-minute R189 Quick Strike rule cannot be certified from this H1 experiment; any strategy passing alpha gates requires execution-granularity and challenge-rule validation before being called funded-ready."
            ],
        })
    except Exception as exc:
        report.update({
            "status": "FAILED_RUN",
            "verdict": "GAGAL",
            "error": f"{type(exc).__name__}: {exc}",
            "decision": "No partial performance result is accepted when the frozen data or calculation pipeline fails.",
        })
    report_path.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({
        "status": report["status"], "verdict": report["verdict"],
        "selected_candidate": report.get("selected_candidate"),
        "gates": report.get("acceptance_gates"), "error": report.get("error"),
    }, indent=2))
    if report["status"] != "COMPLETE":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
