#!/usr/bin/env python3
"""R272 XAUUSD M5 dual-module router. Local computation only."""
from __future__ import annotations
import os, json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd

DATA_DIR = Path(os.environ.get("R272_DATA_DIR", "/mnt/data/r272_xauusd/data_exports/xauusd_m5_2016_2026"))
OUT_DIR = Path(os.environ.get("R272_OUTPUT_DIR", "/mnt/data/r272_xauusd/results"))
BID_PATH = DATA_DIR / "xauusd_bid_M5_2016-2026.csv.gz"
ASK_PATH = DATA_DIR / "xauusd_ask_M5_2016-2026.csv.gz"
MANIFEST_PATH = DATA_DIR / "manifest.json"
NY_TZ = "America/New_York"
BAR_MS = 5 * 60 * 1000
END_HIST = pd.Timestamp("2026-01-01T00:00:00Z")
COSTS = [0.0, 0.10, 0.30, 0.50]  # extra USD/oz round-trip beyond observed BID/ASK
PRIMARY_COST = 0.30
BOOT_REPS = 10_000
BOOT_SEED = 2722026


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def read_side(path: Path, prefix: str) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Missing required quote file: {path}")
    df = pd.read_csv(path, compression="gzip")
    cols = {str(c).strip().lower(): c for c in df.columns}
    time_col = next((cols[x] for x in ("timestamp", "datetime", "date", "time") if x in cols), None)
    if time_col is None:
        raise ValueError(f"No timestamp column in {path.name}; headers={list(df.columns)}")
    raw = df[time_col]
    if pd.api.types.is_numeric_dtype(raw):
        vals = pd.to_numeric(raw, errors="coerce")
        median_abs = float(vals.dropna().abs().median())
        unit = "ms" if median_abs >= 1e11 else "s"
        ts = pd.to_datetime(vals, unit=unit, utc=True, errors="coerce")
    else:
        ts = pd.to_datetime(raw.astype(str).str.replace("Z", "+00:00", regex=False), utc=True, errors="coerce")
    wanted = {}
    for field in ("open", "high", "low", "close"):
        if field not in cols:
            raise ValueError(f"Missing {field} in {path.name}; headers={list(df.columns)}")
        wanted[f"{prefix}_{field}"] = pd.to_numeric(df[cols[field]], errors="coerce")
    out = pd.DataFrame({"timestamp_utc": ts, **wanted})
    out = out.dropna().sort_values("timestamp_utc").reset_index(drop=True)
    duplicates = int(out["timestamp_utc"].duplicated().sum())
    if duplicates:
        raise ValueError(f"{path.name} has {duplicates} duplicate timestamps; no silent deduplication")
    return out


def load_quotes() -> tuple[pd.DataFrame, dict]:
    bid = read_side(BID_PATH, "bid")
    ask = read_side(ASK_PATH, "ask")
    bid_n, ask_n = len(bid), len(ask)
    q = bid.merge(ask, on="timestamp_utc", how="inner", sort=True, validate="one_to_one")
    if q.empty:
        raise ValueError("No common BID/ASK timestamps")
    q["spread_open"] = q["ask_open"] - q["bid_open"]
    neg = int((q["spread_open"] < -1e-7).sum())
    if neg:
        raise ValueError(f"{neg} negative open spreads found")
    ts_ms = (q["timestamp_utc"].astype("int64") // 1_000_000).to_numpy(dtype=np.int64)
    diff = np.diff(ts_ms)
    grid_step = int(np.sum(diff == BAR_MS))
    out_of_grid = int(np.sum((diff % BAR_MS) != 0))
    audit = {
        "bid_rows": bid_n, "ask_rows": ask_n, "common_quote_rows": int(len(q)),
        "bid_sha256_gzip": sha256(BID_PATH), "ask_sha256_gzip": sha256(ASK_PATH),
        "negative_open_spread_rows": neg, "median_open_spread_usd_per_oz": float(q["spread_open"].median()),
        "p95_open_spread_usd_per_oz": float(q["spread_open"].quantile(.95)),
        "adjacent_five_minute_gaps": grid_step, "non_five_minute_timestamp_deltas": out_of_grid,
        "first_timestamp_utc": q["timestamp_utc"].iloc[0].isoformat(),
        "last_timestamp_utc": q["timestamp_utc"].iloc[-1].isoformat()
    }
    if MANIFEST_PATH.exists():
        audit["source_manifest"] = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    q["ny_time"] = q["timestamp_utc"].dt.tz_convert(NY_TZ)
    q["ny_date"] = q["ny_time"].dt.date
    q["ny_minute"] = q["ny_time"].dt.hour * 60 + q["ny_time"].dt.minute
    q["ny_weekday"] = q["ny_time"].dt.dayofweek < 5
    # This is data-side integrity only: no missing bars are filled.
    return q, audit


def features(q: pd.DataFrame) -> pd.DataFrame:
    f = q[["timestamp_utc", "ny_time", "ny_date", "ny_minute", "ny_weekday"]].copy()
    high, low, close = q["bid_high"], q["bid_low"], q["bid_close"]
    f["A"] = (high - low).shift(1).rolling(144, min_periods=144).median()
    f["prior_high"] = high.shift(1).rolling(144, min_periods=144).max()
    f["prior_low"] = low.shift(1).rolling(144, min_periods=144).min()
    f["prior_mid"] = (f["prior_high"] + f["prior_low"]) / 2.0
    f["net_move"] = close.shift(1) - close.shift(145)
    f["path_length"] = close.diff().abs().rolling(144, min_periods=144).sum().shift(1)
    f["ER"] = f["net_move"].abs() / f["path_length"].replace(0, np.nan)
    ts_ms = (q["timestamp_utc"].astype("int64") // 1_000_000).to_numpy(dtype=np.int64)
    step_ok = np.zeros(len(q), dtype=np.int8)
    if len(q) > 1:
        step_ok[1:] = (np.diff(ts_ms) == BAR_MS).astype(np.int8)
    # 145 consecutive 5-min intervals span the causal close-to-close window plus signal bar.
    f["grid_ok"] = pd.Series(step_ok, index=f.index).rolling(145, min_periods=145).sum().eq(145)
    f["valid_context"] = f["A"].gt(0) & f["ER"].notna() & f["prior_high"].notna() & f["grid_ok"]
    # Pre-compute six-bar raw price structure. Current bar is complete at the time of the signal.
    f["a_pullback_depth_long"] = (
        q["bid_high"].shift(0).rolling(6, min_periods=6).max().shift(1)
        - q["bid_low"].rolling(6, min_periods=6).min()
    )
    # Use explicit loops below for exact ranges / no look-ahead clarity.
    return f


def calc_raw_signals(q: pd.DataFrame, f: pd.DataFrame, i: int) -> tuple[dict | None, dict | None, str | None]:
    if i < 146 or not bool(f.at[i, "valid_context"]):
        return None, None, "context_missing_or_gap"
    local_time = f.at[i, "ny_time"]
    minute = int(f.at[i, "ny_minute"])
    if not bool(f.at[i, "ny_weekday"]) or minute < 360 or minute > 950:
        return None, None, "outside_entry_window"
    A = float(f.at[i, "A"])
    er = float(f.at[i, "ER"])
    net = float(f.at[i, "net_move"])
    prior_high = float(f.at[i, "prior_high"])
    prior_low = float(f.at[i, "prior_low"])
    prior_mid = float(f.at[i, "prior_mid"])
    close = float(q.at[i, "bid_close"])
    prev_close_high = float(q.at[i-1, "bid_high"])
    prev_close_low = float(q.at[i-1, "bid_low"])

    a_sig = None
    if abs(net) >= 4.0 * A:
        if net > 0:
            pullback_depth = float(np.max(q["bid_high"].to_numpy()[i-6:i]) - np.min(q["bid_low"].to_numpy()[i-5:i+1]))
            reclaim = close > prev_close_high
            if 0.25*A <= pullback_depth <= 1.00*A and reclaim:
                a_sig = {"module":"A", "direction":1, "stop":float(np.min(q["bid_low"].to_numpy()[i-5:i+1])),
                         "target_multiple":1.50, "target":None, "A":A, "ER":er, "net_move":net}
        elif net < 0:
            pullback_depth = float(np.max(q["ask_high"].to_numpy()[i-5:i+1]) - np.min(q["ask_low"].to_numpy()[i-6:i]))
            reclaim = close < prev_close_low
            if 0.25*A <= pullback_depth <= 1.00*A and reclaim:
                a_sig = {"module":"A", "direction":-1, "stop":float(np.max(q["ask_high"].to_numpy()[i-5:i+1])),
                         "target_multiple":1.50, "target":None, "A":A, "ER":er, "net_move":net}

    b_sig = None
    high = float(q.at[i, "bid_high"])
    low = float(q.at[i, "bid_low"])
    crossed_high = high >= prior_high + 0.25*A and close < prior_high
    crossed_low = low <= prior_low - 0.25*A and close > prior_low
    if crossed_high != crossed_low:
        if crossed_high:
            b_sig = {"module":"B", "direction":-1, "stop":float(q.at[i, "ask_high"] + 0.10*A),
                     "target_multiple":None, "target":prior_mid, "A":A, "ER":er, "net_move":net}
        else:
            b_sig = {"module":"B", "direction":1, "stop":float(q.at[i, "bid_low"] - 0.10*A),
                     "target_multiple":None, "target":prior_mid, "A":A, "ER":er, "net_move":net}
    return a_sig, b_sig, None


def build_trade_for_signal(q: pd.DataFrame, day_positions: dict, i: int, sig: dict) -> dict | None:
    entry_i = i + 1
    if entry_i >= len(q) or q.at[entry_i, "ny_date"] != q.at[i, "ny_date"]:
        return None
    d = int(sig["direction"])
    entry = float(q.at[entry_i, "ask_open"] if d == 1 else q.at[entry_i, "bid_open"])
    stop = float(sig["stop"])
    risk_dist = (entry - stop) if d == 1 else (stop - entry)
    A = float(sig["A"])
    if not np.isfinite(risk_dist) or risk_dist <= 0:
        return None
    if sig["module"] == "A" and not (0.50*A <= risk_dist <= 2.00*A):
        return None
    target = entry + d * 1.50 * risk_dist if sig["module"] == "A" else float(sig["target"])
    reward = d * (target - entry)
    if not np.isfinite(target) or reward <= 0:
        return None
    if sig["module"] == "B" and reward / risk_dist < 1.00:
        return None
    # Reject a delayed entry if the executable quote already crossed the stop or target.
    bid_o, ask_o = float(q.at[entry_i, "bid_open"]), float(q.at[entry_i, "ask_open"])
    if d == 1 and (bid_o <= stop or bid_o >= target):
        return None
    if d == -1 and (ask_o >= stop or ask_o <= target):
        return None

    day = q.at[i, "ny_date"]
    positions = day_positions.get(day, [])
    cutoff_candidates = [j for j in positions if int(q.at[j, "ny_minute"]) >= 16*60+45]
    cutoff_i = cutoff_candidates[0] if cutoff_candidates else (positions[-1] if positions else entry_i)
    if cutoff_i <= entry_i:
        return None

    exit_i = None
    exit_price = None
    reason = None
    for j in range(entry_i, cutoff_i):
        if d == 1:
            op, hi, lo = float(q.at[j,"bid_open"]), float(q.at[j,"bid_high"]), float(q.at[j,"bid_low"])
            if op <= stop:
                exit_i, exit_price, reason = j, op, "stop_gap"
            elif op >= target:
                exit_i, exit_price, reason = j, target, "target_gap"
            elif lo <= stop:
                exit_i, exit_price, reason = j, stop, "stop"
            elif hi >= target:
                exit_i, exit_price, reason = j, target, "target"
        else:
            op, hi, lo = float(q.at[j,"ask_open"]), float(q.at[j,"ask_high"]), float(q.at[j,"ask_low"])
            if op >= stop:
                exit_i, exit_price, reason = j, op, "stop_gap"
            elif op <= target:
                exit_i, exit_price, reason = j, target, "target_gap"
            elif hi >= stop:
                exit_i, exit_price, reason = j, stop, "stop"
            elif lo <= target:
                exit_i, exit_price, reason = j, target, "target"
        if exit_i is not None:
            break
    if exit_i is None:
        # Exit at the actual 16:45 open if present; otherwise at the prior available M5 close.
        if int(q.at[cutoff_i, "ny_minute"]) == 16*60+45:
            exit_i = cutoff_i
            exit_price = float(q.at[exit_i, "bid_open"] if d == 1 else q.at[exit_i, "ask_open"])
            exit_ts = q.at[exit_i, "timestamp_utc"]
            reason = "time_exit_1645_open"
        else:
            exit_i = cutoff_i
            exit_price = float(q.at[exit_i, "bid_close"] if d == 1 else q.at[exit_i, "ask_close"])
            exit_ts = q.at[exit_i, "timestamp_utc"] + pd.Timedelta(minutes=5)
            reason = "time_exit_last_close"
    else:
        exit_ts = q.at[exit_i, "timestamp_utc"]
    entry_ts = q.at[entry_i, "timestamp_utc"]
    # Same M5 bar winners count fully against the Quick Strike threshold as a conservative upper bound.
    same_bar = bool(exit_i == entry_i)
    gross_r = float(d * (float(exit_price) - entry) / risk_dist)
    row = {
        "signal_bar_time_utc": q.at[i, "timestamp_utc"].isoformat(),
        "signal_bar_close_utc": (q.at[i, "timestamp_utc"] + pd.Timedelta(minutes=5)).isoformat(),
        "signal_bar_time_ny": q.at[i, "ny_time"].isoformat(),
        "session_date_ny": str(day),
        "module": sig["module"], "direction": "LONG" if d == 1 else "SHORT", "direction_sign": d,
        "entry_time_utc": entry_ts.isoformat(), "entry_time_ny": q.at[entry_i, "ny_time"].isoformat(),
        "exit_time_utc": exit_ts.isoformat(), "exit_time_ny": (exit_ts.tz_convert(NY_TZ) if exit_ts.tzinfo is not None else exit_ts.tz_localize("UTC").tz_convert(NY_TZ)).isoformat(),
        "entry_index": int(entry_i), "exit_index": int(exit_i),
        "entry_price": entry, "exit_price": float(exit_price), "stop_price": stop, "target_price": target,
        "stop_distance_usd_per_oz": risk_dist, "A_usd_per_oz": A, "ER": float(sig["ER"]), "context_net_move_usd_per_oz": float(sig["net_move"]),
        "gross_r": gross_r, "gross_pnl_usd_per_oz": d * (float(exit_price) - entry),
        "exit_reason": reason, "same_m5_bar_exit_qs_upper_bound": same_bar,
        "holding_minutes_proxy": float((pd.Timestamp(exit_ts) - pd.Timestamp(entry_ts)).total_seconds()/60.0)
    }
    for cost in COSTS:
        key = cost_to_key(cost)
        row[f"net_r_{key}"] = gross_r - cost / risk_dist
        row[f"net_pnl_usd_per_oz_{key}"] = d * (float(exit_price)-entry) - cost
    return row


def cost_to_key(x: float) -> str:
    return f"{x:.2f}".replace(".", "p")


def metrics(trades: pd.DataFrame, cost: float) -> dict:
    key = f"net_r_{cost_to_key(cost)}"
    if trades.empty:
        return {"trades":0, "net_r":0.0, "pf":None, "mean_r":None, "win_rate":None, "positive_profit_r":0.0}
    vals = trades[key].to_numpy(float)
    win = vals[vals > 0].sum()
    loss = -vals[vals < 0].sum()
    pf = None if loss == 0 and win == 0 else (float("inf") if loss == 0 else float(win/loss))
    return {"trades":int(len(vals)), "net_r":float(vals.sum()), "pf":pf,
            "mean_r":float(vals.mean()), "median_r":float(np.median(vals)),
            "win_rate":float((vals>0).mean()), "positive_profit_r":float(win),
            "qs_profit_upper_bound_r":float(trades.loc[trades["same_m5_bar_exit_qs_upper_bound"] & (trades[key]>0),key].sum()),
            "qs_share_upper_bound":float(trades.loc[trades["same_m5_bar_exit_qs_upper_bound"] & (trades[key]>0),key].sum()/win) if win>0 else 0.0}


def run_stream(q: pd.DataFrame, f: pd.DataFrame, stream_name: str) -> pd.DataFrame:
    # Group bar indices by NY calendar date so each accepted position is flat before daily cutoff.
    day_positions: dict = {}
    for j, day in enumerate(q["ny_date"].to_numpy()):
        day_positions.setdefault(day, []).append(j)
    day_used = set()
    trades = []
    skip_counts: dict[str,int] = {}
    raw_signals = 0
    busy_until = -1
    for i in range(146, len(q)-1):
        day = q.at[i, "ny_date"]
        if i <= busy_until or day in day_used:
            continue
        a_sig, b_sig, skip = calc_raw_signals(q, f, i)
        if skip:
            skip_counts[skip] = skip_counts.get(skip,0)+1
            continue
        er = float(f.at[i,"ER"])
        chosen = None
        if stream_name == "A":
            if a_sig is not None and er >= 0.45:
                chosen = a_sig
        elif stream_name == "B":
            if b_sig is not None and er <= 0.20:
                chosen = b_sig
        elif stream_name == "router":
            if a_sig is not None and er >= 0.45:
                chosen = a_sig
            elif b_sig is not None and er <= 0.20:
                chosen = b_sig
        elif stream_name == "raw_union":
            if a_sig is not None:
                chosen = a_sig
            elif b_sig is not None:
                chosen = b_sig
        else:
            raise ValueError(stream_name)
        if chosen is None:
            continue
        raw_signals += 1
        row = build_trade_for_signal(q, day_positions, i, chosen)
        if row is None:
            skip_counts["invalid_delayed_entry_or_RR"] = skip_counts.get("invalid_delayed_entry_or_RR",0)+1
            continue
        row["stream"] = stream_name
        row["signal_year"] = int(pd.Timestamp(row["signal_bar_time_utc"]).year)
        row["signal_month"] = pd.Timestamp(row["signal_bar_time_utc"]).strftime("%Y-%m")
        row["raw_signals_before_validity"] = raw_signals
        trades.append(row)
        day_used.add(day)
        busy_until = int(row["exit_index"])
    out = pd.DataFrame(trades)
    out.attrs["skip_counts"] = skip_counts
    out.attrs["raw_signals"] = raw_signals
    return out


def period_metrics(trades: pd.DataFrame, cost: float) -> dict:
    return metrics(trades, cost)


def bootstrap_weekly(trades: pd.DataFrame, cost: float, reps=BOOT_REPS, seed=BOOT_SEED) -> dict:
    if trades.empty:
        return {"weeks":0,"mean_weekly_r":None,"ci95":[None,None],"positive_fraction":None}
    key=f"net_r_{cost_to_key(cost)}"
    t=trades.copy()
    t["entry_dt"]=pd.to_datetime(t["entry_time_utc"],utc=True).dt.tz_convert(NY_TZ).dt.tz_localize(None)
    t["week"]=t["entry_dt"].dt.normalize()-pd.to_timedelta(t["entry_dt"].dt.weekday,unit="D")
    start=pd.Timestamp("2026-01-05") if t["signal_year"].min()>=2026 else pd.Timestamp(f"{int(t['signal_year'].min())}-01-04")
    end=t["week"].max()
    weeks=pd.date_range(start=start,end=end,freq="W-MON")
    weekly=t.groupby("week")[key].sum().reindex(weeks,fill_value=0.0).to_numpy(float)
    if len(weekly)<4:
        return {"weeks":int(len(weekly)),"mean_weekly_r":float(weekly.mean()),"ci95":[None,None],"positive_fraction":None}
    rng=np.random.default_rng(seed)
    blocks=int(np.ceil(len(weekly)/4))
    starts=rng.integers(0,len(weekly),size=(reps,blocks))
    idx=(starts[:,:,None]+np.arange(4)[None,None,:])%len(weekly)
    sampled=weekly[idx].reshape(reps,-1)[:,:len(weekly)]
    means=sampled.mean(axis=1)
    return {"weeks":int(len(weekly)),"weeks_with_trades":int((weekly!=0).sum()),
            "mean_weekly_r":float(weekly.mean()),"ci95":[float(np.quantile(means,.025)),float(np.quantile(means,.975))],
            "positive_fraction":float((means>0).mean()),"replicates":reps,"block_weeks":4,"seed":seed}


def summarize_streams(all_trades: dict[str,pd.DataFrame], start: pd.Timestamp, end: pd.Timestamp) -> dict:
    summary={}
    for name,trades in all_trades.items():
        subset=trades[(pd.to_datetime(trades["signal_bar_time_utc"],utc=True)>=start)&(pd.to_datetime(trades["signal_bar_time_utc"],utc=True)<end)] if not trades.empty else trades
        summary[name]={f"cost_{cost_to_key(cost)}":period_metrics(subset,cost) for cost in COSTS}
        summary[name]["skip_counts"]=trades.attrs.get("skip_counts",{}) if not trades.empty else {}
        summary[name]["raw_signals_before_validity"]=trades.attrs.get("raw_signals",0) if not trades.empty else 0
    return summary


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    q, audit = load_quotes()
    # First calculate only through 2025. 2026 remains unopened unless every historical screen gate passes.
    q_dev = q[q["timestamp_utc"] < END_HIST].copy().reset_index(drop=True)
    f_dev = features(q_dev)
    stream_names = ["A","B","router","raw_union"]
    dev_trades = {name:run_stream(q_dev,f_dev,name) for name in stream_names}
    discovery_start=pd.Timestamp("2016-01-01T00:00:00Z")
    validation_start=pd.Timestamp("2021-01-01T00:00:00Z")
    historical_start=pd.Timestamp("2021-01-01T00:00:00Z")
    discovery_end=validation_start
    validation_end=END_HIST
    key_primary=f"net_r_{cost_to_key(PRIMARY_COST)}"
    dev_gate_results={}
    for name,tr in dev_trades.items():
        ts=pd.to_datetime(tr["signal_bar_time_utc"],utc=True) if not tr.empty else pd.Series([],dtype="datetime64[ns, UTC]")
        disc=tr[(ts>=discovery_start)&(ts<discovery_end)] if not tr.empty else tr
        valid=tr[(ts>=validation_start)&(ts<validation_end)] if not tr.empty else tr
        dev_gate_results[name]={
            "discovery":metrics(disc,PRIMARY_COST),"validation":metrics(valid,PRIMARY_COST),
            "validation_plus_0p50":metrics(valid,0.50),
        }
    router=dev_trades["router"]
    rts=pd.to_datetime(router["signal_bar_time_utc"],utc=True) if not router.empty else pd.Series([],dtype="datetime64[ns, UTC]")
    d_router=router[(rts>=discovery_start)&(rts<discovery_end)] if not router.empty else router
    v_router=router[(rts>=validation_start)&(rts<validation_end)] if not router.empty else router
    a_d=dev_trades["A"]; a_ts=pd.to_datetime(a_d["signal_bar_time_utc"],utc=True) if not a_d.empty else pd.Series([],dtype="datetime64[ns, UTC]")
    b_d=dev_trades["B"]; b_ts=pd.to_datetime(b_d["signal_bar_time_utc"],utc=True) if not b_d.empty else pd.Series([],dtype="datetime64[ns, UTC]")
    a_disc=a_d[(a_ts>=discovery_start)&(a_ts<discovery_end)] if not a_d.empty else a_d
    a_val=a_d[(a_ts>=validation_start)&(a_ts<validation_end)] if not a_d.empty else a_d
    b_disc=b_d[(b_ts>=discovery_start)&(b_ts<discovery_end)] if not b_d.empty else b_d
    b_val=b_d[(b_ts>=validation_start)&(b_ts<validation_end)] if not b_d.empty else b_d
    dev_gate_results["locked_historical_gates"]={
      "router_discovery_positive_100_trades":len(d_router)>=100 and metrics(d_router,PRIMARY_COST)["net_r"]>0,
      "router_validation_positive_200_trades":len(v_router)>=200 and metrics(v_router,PRIMARY_COST)["net_r"]>0,
      "module_A_positive_50_trades_both_segments":len(a_disc)>=50 and len(a_val)>=50 and metrics(a_disc,PRIMARY_COST)["net_r"]>0 and metrics(a_val,PRIMARY_COST)["net_r"]>0,
      "module_B_positive_50_trades_both_segments":len(b_disc)>=50 and len(b_val)>=50 and metrics(b_disc,PRIMARY_COST)["net_r"]>0 and metrics(b_val,PRIMARY_COST)["net_r"]>0,
      "router_validation_positive_at_0p50_cost":metrics(v_router,0.50)["net_r"]>0,
    }
    hist_pass=all(dev_gate_results["locked_historical_gates"].values())
    summary={
      "round":"R272","instrument":"XAUUSD","timeframe":"M5","primary_cost_usd_per_oz":PRIMARY_COST,
      "data_audit":audit,"historical_metrics":dev_gate_results,
      "historical_screen_pass":bool(hist_pass),
      "holdout_2026_opened":False,
      "final_verdict":"GAGAL_HISTORICAL_SCREEN" if not hist_pass else "HISTORICAL_SCREEN_PASS_2026_NOT_YET_RECORDED",
      "preregistration":"research/R272_XAUUSD_DUAL_MODULE_PREREGISTRATION.md",
      "holdout_protection_note":"The 2026 OOS was excluded from all signal/feature calculations in this run. It may be opened only by a separate run after the historical gates pass."
    }
    if hist_pass:
        # Only now recompute the same locked rules across the full sample and inspect the reserved 2026 slice.
        f_all=features(q)
        all_trades={name:run_stream(q,f_all,name) for name in stream_names}
        oos_start=END_HIST
        oos_end=pd.Timestamp("2026-10-16T00:00:00Z")
        oos_metrics={}
        for name,tr in all_trades.items():
            ts=pd.to_datetime(tr["signal_bar_time_utc"],utc=True) if not tr.empty else pd.Series([],dtype="datetime64[ns, UTC]")
            oos=tr[(ts>=oos_start)&(ts<oos_end)] if not tr.empty else tr
            oos_metrics[name]={f"cost_{cost_to_key(cost)}":metrics(oos,cost) for cost in COSTS}
            oos_metrics[name]["bootstrap_primary_cost"]=bootstrap_weekly(oos,PRIMARY_COST)
            if not oos.empty:
                oos_metrics[name]["months"]={}
                for month,mt in oos.groupby("signal_month"):
                    oos_metrics[name]["months"][month]={f"cost_{cost_to_key(cost)}":metrics(mt,cost) for cost in COSTS}
        summary["holdout_2026_opened"]=True
        summary["oos_2026_metrics"]=oos_metrics
        summary["final_verdict"]="GAGAL_OOS_GATE_NOT_YET_IMPLEMENTED"  # set below from pre-registered gates
        rt=oos_metrics["router"][f"cost_{cost_to_key(PRIMARY_COST)}"]
        rt_stress=oos_metrics["router"]["cost_0p50"]
        bt=oos_metrics["router"]["bootstrap_primary_cost"]
        monthly=oos_metrics["router"].get("months",{})
        positive_months=sum(1 for m in monthly.values() if m[f"cost_{cost_to_key(PRIMARY_COST)}"]["net_r"]>0)
        total_positive=sum(m[f"cost_{cost_to_key(PRIMARY_COST)}"]["positive_profit_r"] for m in monthly.values())
        largest_month=max((m[f"cost_{cost_to_key(PRIMARY_COST)}"]["positive_profit_r"] for m in monthly.values()),default=0.0)
        oos_gates={
          "router_oos_50_trades":rt["trades"]>=50,
          "router_oos_net_positive_at_primary_cost":rt["net_r"]>0,
          "router_oos_net_positive_at_0p50_cost":rt_stress["net_r"]>0,
          "bootstrap_lower_bound_positive":bt["ci95"][0] is not None and bt["ci95"][0]>0,
          "at_least_60_percent_positive_months":len(monthly)>0 and positive_months/len(monthly)>=0.60,
          "largest_month_not_over_40_percent_positive_profit":total_positive>0 and largest_month/total_positive<=0.40,
        }
        summary["locked_oos_gates"]=oos_gates
        summary["final_verdict"]="GAGAL" if not all(oos_gates.values()) else "SIGNAL_SCREEN_LULUS_FUNDED_READINESS_NOT_YET_TESTED"
        for name,tr in all_trades.items():
            clean=tr.drop(columns=["entry_index","exit_index"],errors="ignore")
            clean.to_csv(OUT_DIR/f"R272_{name}_trade_ledger.csv",index=False,float_format="%.8f")
    else:
        # Save only development trade ledgers; there is no 2026 output in this failure branch.
        for name,tr in dev_trades.items():
            clean=tr.drop(columns=["entry_index","exit_index"],errors="ignore")
            clean.to_csv(OUT_DIR/f"R272_{name}_trade_ledger_development_only.csv",index=False,float_format="%.8f")
    (OUT_DIR/"R272_results.json").write_text(json.dumps(summary,indent=2,allow_nan=False),encoding="utf-8")
    print(json.dumps({"round":summary["round"],"historical_screen_pass":summary["historical_screen_pass"],
        "holdout_2026_opened":summary["holdout_2026_opened"],"final_verdict":summary["final_verdict"],
        "historical_gates":dev_gate_results["locked_historical_gates"],
        "historical_metrics":dev_gate_results,"oos":summary.get("oos_2026_metrics",{})},indent=2,allow_nan=False))


if __name__=="__main__":
    main()
