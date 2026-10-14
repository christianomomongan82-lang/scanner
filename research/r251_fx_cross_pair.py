#!/usr/bin/env python3
"""R251 preregistered FX cross-pair lead-lag test. No threshold grid search."""
from __future__ import annotations
import calendar
import hashlib
import json
import subprocess
import time
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(".")
DATA = ROOT / "dl" / "r251_fx"
OUT = ROOT / "research"
START = date(2017, 1, 1)
END_EXCLUSIVE = date(2026, 10, 14)
PIP = 0.0001
PAIRS = ("eurusd", "gbpusd", "audusd", "usdchf")
COST_STRESS = (0.0, 0.5, 1.0, 2.0)
HOLD_HOURS = 4
LOOKBACK_HOURS = 3
MIN_MEDIAN_PEER_MOVE = 0.0005  # 5 basis points over the lookback
LAG_FRACTION = 0.50
MAX_COUNTERMOVE_FRACTION = 0.25

def parse_bars(path: Path):
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
        raise ValueError(f"Invalid timestamp or missing OHLC in {path}; missing={missing}")
    bars = raw[required].apply(pd.to_numeric, errors="coerce")
    bars.columns = ["Open", "High", "Low", "Close"]
    bars.index = pd.DatetimeIndex(idx, name="timestamp_utc")
    bars = bars.replace([np.inf, -np.inf], np.nan).dropna().sort_index()
    duplicate_count = int(bars.index.duplicated(keep="last").sum())
    bars = bars.loc[~bars.index.duplicated(keep="last")]
    valid = ((bars.High >= bars[["Open","Close"]].max(axis=1)) &
             (bars.Low <= bars[["Open","Close"]].min(axis=1)) &
             (bars.High >= bars.Low))
    invalid_count = int((~valid).sum())
    bars = bars.loc[valid]
    if bars.empty:
        raise ValueError(f"No valid bars in {path}")
    delta = bars.index.to_series().diff().dropna()
    diag = {
        "rows": int(len(bars)),
        "duplicate_timestamps_removed": duplicate_count,
        "invalid_ohlc_rows_removed": invalid_count,
        "hourly_grid_violations": int(((delta % pd.Timedelta(hours=1)) != pd.Timedelta(0)).sum()),
        "missing_hour_gaps": int((delta > pd.Timedelta(hours=1)).sum()),
        "start_utc": bars.index[0].isoformat(),
        "end_utc": bars.index[-1].isoformat(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }
    return bars, diag

def download_pair(pair: str, side: str):
    DATA.mkdir(parents=True, exist_ok=True)
    parts = []
    logs = []
    start_year, end_year = START.year, END_EXCLUSIVE.year
    for year in range(start_year, end_year + 1):
        chunk_start = max(START, date(year, 1, 1))
        chunk_end = min(END_EXCLUSIVE, date(year + 1, 1, 1))
        if chunk_start >= chunk_end:
            continue
        stem = f"{pair}_{side}_{year}"
        path = DATA / f"{stem}.csv"
        last_error = ""
        ok = False
        for attempt in range(1, 4):
            path.unlink(missing_ok=True)
            cmd = [
                "npx", "--yes", "dukascopy-node", "-i", pair,
                "-from", chunk_start.isoformat(), "-to", chunk_end.isoformat(),
                "-t", "h1", "-p", side, "-utc", "0", "-f", "csv", "-fl",
                "-dir", str(DATA), "-fn", stem, "-bs", "3", "-bp", "2000",
                "-r", "5", "-rp", "5000"
            ]
            try:
                proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                      text=True, check=False, timeout=900)
                last_error = (proc.stdout or "")[-1600:]
                if proc.returncode == 0 and path.is_file() and path.stat().st_size > 20:
                    probe = pd.read_csv(path, nrows=2)
                    if len(probe.columns) >= 5 and len(probe) > 0:
                        ok = True
                        logs.append({"pair": pair, "side": side, "year": year,
                                     "attempt": attempt, "bytes": path.stat().st_size})
                        break
            except Exception as exc:
                last_error = f"{type(exc).__name__}: {exc}"
            if attempt < 3:
                time.sleep(attempt * 2)
        if not ok:
            raise RuntimeError(f"Download failed {pair}/{side}/{year} after 3 attempts: {last_error}")
        parts.append(path)
    frames = [pd.read_csv(p) for p in parts]
    combined = pd.concat(frames, ignore_index=True)
    combined_path = DATA / f"{pair}_{side}_H1.csv"
    combined.to_csv(combined_path, index=False)
    return combined_path, logs

def profit_factor(values):
    x = np.asarray(values, dtype=float)
    gp = float(x[x > 0].sum())
    gl = float(-x[x < 0].sum())
    if gl <= 0:
        return float("inf") if gp > 0 else None
    return gp / gl

def metrics(records, start, end, cost):
    a = [r for r in records if start <= pd.Timestamp(r["entry_utc"]) < end]
    values = np.array([r["gross_pips"] - cost for r in a], dtype=float)
    weeks = max((end - start).total_seconds() / (7 * 86400), 1 / 7)
    return {
        "trades": len(a),
        "PF": profit_factor(values),
        "net_pips": float(values.sum()) if len(values) else 0.0,
        "mean_net_pips_per_trade": float(values.mean()) if len(values) else None,
        "win_rate": float(np.mean(values > 0)) if len(values) else None,
        "trades_per_week": float(len(a) / weeks),
    }

def bootstrap_forward_weekly(trades, cost=1.0, draws=2000, seed=251):
    fwd_start, fwd_end = pd.Timestamp("2022-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
    weeks = pd.date_range(fwd_start.floor("D"), fwd_end, freq="W-MON", tz="UTC")
    if len(weeks) < 8:
        return {"draws": 0, "p_mean_positive": None, "ci95_mean_pips": None}
    weekly = []
    for i, w in enumerate(weeks[:-1]):
        end = weeks[i+1]
        vals = [t["gross_pips"] - cost for t in trades if w <= pd.Timestamp(t["entry_utc"]) < end]
        weekly.append(np.asarray(vals, dtype=float))
    if sum(len(x) for x in weekly) < 20:
        return {"draws": 0, "p_mean_positive": None, "ci95_mean_pips": None}
    rng = np.random.default_rng(seed)
    block_len = 4
    estimates = []
    nweek = len(weekly)
    for _ in range(draws):
        sampled = []
        while len(sampled) < nweek:
            j = int(rng.integers(0, nweek))
            sampled.extend(weekly[(j+k) % nweek] for k in range(block_len))
        seq = [v for arr in sampled[:nweek] for v in arr]
        if seq:
            estimates.append(float(np.mean(seq)))
    arr = np.asarray(estimates)
    return {"draws": int(len(arr)), "p_mean_positive": float(np.mean(arr > 0)),
            "ci95_mean_pips": [float(np.quantile(arr, 0.025)), float(np.quantile(arr, 0.975))]}

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report_path = OUT / "R251_fx_cross_pair_results.json"
    trades_path = OUT / "R251_fx_cross_pair_trades.csv"
    annual_path = OUT / "R251_fx_cross_pair_annual.csv"
    report = {
        "status": "STARTED",
        "strategy": "R251 FX cross-pair consensus and EURUSD lag catch-up",
        "verdict": "NOT_EVALUATED",
        "parameters_locked_before_test": {
            "signal_pairs": ["GBPUSD", "AUDUSD", "inverse USDCHF"],
            "lookback_hours": LOOKBACK_HOURS,
            "all_three_peers_same_sign": True,
            "minimum_median_peer_abs_return": MIN_MEDIAN_PEER_MOVE,
            "EURUSD_signed_return_max_fraction_of_peer_median": LAG_FRACTION,
            "EURUSD_adverse_return_max_fraction_of_peer_median": MAX_COUNTERMOVE_FRACTION,
            "entry": "next exact shared H1 open after completed signal H1 candle",
            "exit": f"open after {HOLD_HOURS} exact elapsed hours",
            "overlap": "one position at a time; overlapping signals skipped",
            "risk_or_stop": "not searched; this is an alpha validation gate before challenge sizing",
            "cost_stress_extra_pips_on_top_of_EURUSD_bid_ask": list(COST_STRESS),
        },
        "periods_utc": {
            "discovery": ["2017-01-01", "2022-01-01"),
            "forward": ["2022-01-01", "2026-01-01"),
            "oos_2026": ["2026-01-01", END_EXCLUSIVE.isoformat()),
        },
        "notes": [
            "All signals use completed H1 closes only; orders use next shared exact hourly open.",
            "No missing bars are synthesized, no series are forward-filled, and signal/entry/exit intervals must be exact hourly timestamps.",
            "USDCHF returns are sign-inverted before peer consensus so positive peer consensus means EURUSD-up.",
            "Execution PnL uses actual EURUSD quote sides: long enters ASK and exits BID; short enters BID and exits ASK.",
            "No parameter grid search is performed; thresholds are frozen in this script before discovery/forward/OOS metrics are calculated.",
        ],
    }
    try:
        raw = {}
        diagnostics = {}
        downloads = []
        for pair in PAIRS:
            sides = ("bid", "ask") if pair == "eurusd" else ("bid",)
            for side in sides:
                path, logs = download_pair(pair, side)
                bars, diag = parse_bars(path)
                raw[(pair, side)] = bars
                diagnostics[f"{pair}_{side}"] = diag
                downloads.extend(logs)
        # Intersect all four signal bid series and EURUSD ask execution series.
        common = raw[("eurusd","bid")].index
        for key in (("eurusd","ask"), ("gbpusd","bid"), ("audusd","bid"), ("usdchf","bid")):
            common = common.intersection(raw[key].index)
        common = common.sort_values()
        if len(common) < 30000:
            raise RuntimeError(f"Only {len(common)} exactly aligned shared H1 bars; refusing to score")
        series = {key: bars.loc[common] for key, bars in raw.items()}
        t = common
        # Need exact consecutive hourly bars for the lookback window and horizon.
        records = []
        counters = {"potential_signal": 0, "bad_time_grid": 0, "overlap_skipped": 0, "entry_exit_missing": 0}
        active_exit = -1
        for i in range(LOOKBACK_HOURS, len(t) - HOLD_HOURS - 1):
            # Timestamp indices are bar-open timestamps; signal observed at i+1 hour.
            if any(t[j] - t[j-1] != pd.Timedelta(hours=1)
                   for j in range(i-LOOKBACK_HOURS+1, i+1)):
                counters["bad_time_grid"] += 1
                continue
            if t[i+1] - t[i] != pd.Timedelta(hours=1) or t[i+HOLD_HOURS+1] - t[i+1] != pd.Timedelta(hours=HOLD_HOURS):
                counters["entry_exit_missing"] += 1
                continue
            peer_returns = np.array([
                series[("gbpusd","bid")].Close.iloc[i] / series[("gbpusd","bid")].Close.iloc[i-LOOKBACK_HOURS] - 1,
                series[("audusd","bid")].Close.iloc[i] / series[("audusd","bid")].Close.iloc[i-LOOKBACK_HOURS] - 1,
                -(series[("usdchf","bid")].Close.iloc[i] / series[("usdchf","bid")].Close.iloc[i-LOOKBACK_HOURS] - 1),
            ], dtype=float)
            if not (np.all(peer_returns > 0) or np.all(peer_returns < 0)):
                continue
            direction = 1 if np.all(peer_returns > 0) else -1
            peer_median = float(np.median(np.abs(peer_returns)))
            eur_ret = float(series[("eurusd","bid")].Close.iloc[i] /
                            series[("eurusd","bid")].Close.iloc[i-LOOKBACK_HOURS] - 1)
            if peer_median < MIN_MEDIAN_PEER_MOVE:
                continue
            # EURUSD must lag: no more than half the peer median in the consensus
            # direction, and no counter-move greater than one quarter of peer median.
            directed_eur = direction * eur_ret
            if not (-MAX_COUNTERMOVE_FRACTION * peer_median <= directed_eur <= LAG_FRACTION * peer_median):
                continue
            counters["potential_signal"] += 1
            entry_i, exit_i = i + 1, i + HOLD_HOURS + 1
            if entry_i <= active_exit:
                counters["overlap_skipped"] += 1
                continue
            ebid = float(series[("eurusd","bid")].Open.iloc[entry_i])
            eask = float(series[("eurusd","ask")].Open.iloc[entry_i])
            xbid = float(series[("eurusd","bid")].Open.iloc[exit_i])
            xask = float(series[("eurusd","ask")].Open.iloc[exit_i])
            if not np.isfinite([ebid,eask,xbid,xask]).all() or eask < ebid or xask < xbid:
                raise RuntimeError(f"Invalid EURUSD quote-side price at trade indices {entry_i}/{exit_i}")
            entry = eask if direction == 1 else ebid
            exit_price = xbid if direction == 1 else xask
            gross = direction * (exit_price - entry) / PIP
            records.append({
                "signal_close_utc": (t[i] + pd.Timedelta(hours=1)).isoformat(),
                "entry_utc": t[entry_i].isoformat(),
                "exit_utc": t[exit_i].isoformat(),
                "direction": "LONG" if direction == 1 else "SHORT",
                "peer_return_gbpusd": float(peer_returns[0]),
                "peer_return_audusd": float(peer_returns[1]),
                "peer_return_inv_usdchf": float(peer_returns[2]),
                "peer_median_abs_return": peer_median,
                "eurusd_lookback_return": eur_ret,
                "entry_bid": ebid, "entry_ask": eask,
                "exit_bid": xbid, "exit_ask": xask,
                "gross_pips_after_observed_bid_ask": float(gross),
                "holding_hours": HOLD_HOURS,
            })
            active_exit = exit_i
        if not records:
            raise RuntimeError("No eligible trades; strategy fails discovery data sufficiency.")
        dftrades = pd.DataFrame(records)
        dftrades.to_csv(trades_path, index=False)
        discovery = (pd.Timestamp("2017-01-01", tz="UTC"), pd.Timestamp("2022-01-01", tz="UTC"))
        forward = (pd.Timestamp("2022-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"))
        oos = (pd.Timestamp("2026-01-01", tz="UTC"), pd.Timestamp(END_EXCLUSIVE, tz="UTC"))
        phase = {}
        for name, (a,b) in (("discovery", discovery), ("forward",forward), ("oos_2026",oos)):
            phase[name] = {str(cost): metrics(records,a,b,cost) for cost in COST_STRESS}
        years = []
        for year in range(2017, 2027):
            a,b = pd.Timestamp(f"{year}-01-01",tz="UTC"), pd.Timestamp(f"{year+1}-01-01",tz="UTC")
            years.append({"year":year, **{f"PF_cost_{cost}":metrics(records,a,b,cost)["PF"] for cost in COST_STRESS},
                          **{f"trades_cost_{cost}":metrics(records,a,b,cost)["trades"] for cost in COST_STRESS},
                          **{f"mean_pips_cost_{cost}":metrics(records,a,b,cost)["mean_net_pips_per_trade"] for cost in COST_STRESS}})
        pd.DataFrame(years).to_csv(annual_path,index=False)
        bootstrap = bootstrap_forward_weekly(records, cost=1.0)
        forward_y = [r for r in years if 2022 <= r["year"] <= 2025 and r["trades_cost_1.0"] >= 20]
        gates = {
            "discovery_min_100_trades": phase["discovery"]["1.0"]["trades"] >= 100,
            "discovery_PF_at_1pip_ge_1.05": isinstance(phase["discovery"]["1.0"]["PF"],(float,int)) and phase["discovery"]["1.0"]["PF"] >= 1.05,
            "forward_min_100_trades": phase["forward"]["1.0"]["trades"] >= 100,
            "forward_PF_at_1pip_ge_1.10": isinstance(phase["forward"]["1.0"]["PF"],(float,int)) and phase["forward"]["1.0"]["PF"] >= 1.10,
            "forward_PF_at_2pip_ge_1.05": isinstance(phase["forward"]["2.0"]["PF"],(float,int)) and phase["forward"]["2.0"]["PF"] >= 1.05,
            "forward_each_year_with_20plus_trades_PF_ge_1_at_1pip": bool(forward_y) and all(isinstance(y["PF_cost_1.0"],(float,int)) and y["PF_cost_1.0"] >= 1.0 for y in forward_y),
            "forward_4week_block_bootstrap_mean_positive_95pct": bool(bootstrap["ci95_mean_pips"] and bootstrap["ci95_mean_pips"][0] > 0 and bootstrap["p_mean_positive"] >= 0.95),
            "oos_2026_min_30_trades": phase["oos_2026"]["1.0"]["trades"] >= 30,
            "oos_2026_PF_at_1pip_ge_1.00": isinstance(phase["oos_2026"]["1.0"]["PF"],(float,int)) and phase["oos_2026"]["1.0"]["PF"] >= 1.0,
        }
        report.update({
            "status":"COMPLETE",
            "data":{"pairs":diagnostics,"common_hourly_rows":int(len(common)),
                    "common_start_utc":t[0].isoformat(),"common_end_utc":t[-1].isoformat(),
                    "downloads":downloads,"sha256_trade_ledger":hashlib.sha256(trades_path.read_bytes()).hexdigest()},
            "signals_and_execution":{**counters,"executed_trades":len(records)},
            "metrics":phase,
            "annual_cohorts":years,
            "forward_block_bootstrap_cost_1pip":bootstrap,
            "acceptance_gates":gates,
            "verdict":"LULUS" if all(gates.values()) else "GAGAL",
            "verdict_rule":"All predeclared discovery, forward, annual stability, bootstrap, and 2026 OOS gates must pass. No after-the-fact tuning.",
            "limitations":[
                "Dukascopy historical H1 quotes may differ from the user's exact funded broker feed.",
                "Bid/ask execution modeled from H1 open prices; intrahour quote path and live slippage are not observed.",
                "Challenge pass probability is not claimed from this alpha test; a separate chronological risk replay is required only if all strategy acceptance gates pass."
            ]
        })
    except Exception as exc:
        report.update({"status":"FAILED_RUN","verdict":"GAGAL","error":f"{type(exc).__name__}: {exc}",
                       "decision":"The experiment is scored as GAGAL if the frozen dataset/download/validation pipeline cannot complete; no partial PF may be used."})
    report_path.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":report["status"],"verdict":report["verdict"],"report":str(report_path),
                      "trades":report.get("signals_and_execution",{}).get("executed_trades"),
                      "gates":report.get("acceptance_gates",{}),"error":report.get("error")},indent=2))
    if report["status"] != "COMPLETE":
        raise SystemExit(1)

if __name__ == "__main__":
    main()
