#!/usr/bin/env python3
"""R254: preregistered EURUSD failed Asian-range breakout / reclaim test.

The signal requires a close outside the completed Asia range, preceded by a
close inside the range, followed by a close back inside. Entry is next H1 open.
All parameters are frozen before validation/forward/OOS results are examined.
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
EXCURSION_FRACTIONS = (0.0, 0.05)
REWARD_RISKS = (1.0, 1.5, 2.0)
MIN_STOP_PIPS = 3.0
MAX_STOP_PIPS = 50.0
RANGE_HOURS = tuple(range(0, 6))
REENTRY_SIGNAL_HOURS = tuple(range(7, 12))  # signal candle opens 07:00..11:00 UTC
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
    valid = ((bars.High >= bars[["Open", "Close"]].max(axis=1))
             & (bars.Low <= bars[["Open", "Close"]].min(axis=1))
             & (bars.High >= bars.Low))
    invalid = int((~valid).sum())
    bars = bars.loc[valid]
    if bars.empty:
        raise ValueError(f"No valid quote bars in {path}")
    gaps = bars.index.to_series().diff().dropna()
    return bars, {
        "rows": int(len(bars)),
        "duplicate_timestamps_removed": dups,
        "invalid_ohlc_rows_removed": invalid,
        "off_hour_timestamps": int(((bars.index.minute != 0) | (bars.index.second != 0)).sum()),
        "missing_hour_gaps": int((gaps > pd.Timedelta(hours=1)).sum()),
        "start_utc": bars.index[0].isoformat(),
        "end_utc": bars.index[-1].isoformat(),
        "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
    }


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
    selected = [t for t in trades
                if start <= pd.Timestamp(t["entry_utc"]) < end
                and start <= pd.Timestamp(t["exit_utc"]) < end]
    values = np.asarray([t["gross_pips"] - cost for t in selected], dtype=float)
    weeks = max((end-start).total_seconds() / (7*86400), 1/7)
    return {
        "trades": int(len(values)),
        "PF": pf(values),
        "net_pips": float(values.sum()) if len(values) else 0.0,
        "mean_net_pips_per_trade": float(values.mean()) if len(values) else None,
        "win_rate": float((values > 0).mean()) if len(values) else None,
        "trades_per_week": float(len(values)/weeks),
    }


def simulate_config(bid, ask, date_positions, excursion_fraction, rr_multiple):
    trades = []
    diag = {
        "calendar_days_seen": int(len(date_positions)),
        "days_with_complete_hourly_grid": 0,
        "days_skipped_incomplete_grid": 0,
        "days_skipped_invalid_range": 0,
        "days_skipped_no_failed_breakout": 0,
        "days_skipped_invalid_stop_distance": 0,
        "days_skipped_invalid_quotes": 0,
        "invalid_quote_nonfinite": 0,
        "invalid_entry_spread": 0,
        "trades_closed": 0,
        "stop_first_collisions": 0,
        "scheduled_time_exits": 0,
        "stop_exits": 0,
        "target_exits": 0,
    }
    for day, positions in date_positions.items():
        if positions is None:
            diag["days_skipped_incomplete_grid"] += 1
            continue
        diag["days_with_complete_hourly_grid"] += 1
        rpos = [positions[h] for h in RANGE_HOURS]
        upper = float(bid.High.iloc[rpos].max())
        lower = float(bid.Low.iloc[rpos].min())
        width = upper - lower
        width_pips = width/PIP
        if not np.isfinite([upper, lower]).all() or width_pips <= 0:
            diag["days_skipped_invalid_range"] += 1
            continue
        excursion = excursion_fraction*width
        chosen = None
        for hour in REENTRY_SIGNAL_HOURS:
            before_i = positions[hour-2]   # closes at the start of breakout candle
            breakout_i = positions[hour-1] # candle closing outside range
            reentry_i = positions[hour]    # candle closing back inside range
            before_close = float(bid.Close.iloc[before_i])
            breakout_close = float(bid.Close.iloc[breakout_i])
            reentry_close = float(bid.Close.iloc[reentry_i])
            if not (lower <= before_close <= upper and lower <= reentry_close <= upper):
                continue
            if breakout_close > upper + excursion:
                # Failed upside breakout; fade short. Use ASK highs for executable stop.
                stop = float(max(ask.High.iloc[breakout_i], ask.High.iloc[reentry_i]))
                direction = -1
                chosen = (reentry_i, positions[hour+1], direction, stop, before_i, breakout_i)
                break
            if breakout_close < lower - excursion:
                # Failed downside breakout; fade long. Use BID lows for executable stop.
                stop = float(min(bid.Low.iloc[breakout_i], bid.Low.iloc[reentry_i]))
                direction = 1
                chosen = (reentry_i, positions[hour+1], direction, stop, before_i, breakout_i)
                break
        if chosen is None:
            diag["days_skipped_no_failed_breakout"] += 1
            continue
        reentry_i, entry_i, direction, stop, before_i, breakout_i = chosen
        entry_time = bid.index[reentry_i] + pd.Timedelta(hours=1)
        if bid.index[entry_i] != entry_time:
            diag["days_skipped_incomplete_grid"] += 1
            continue
        exit_i = positions[EXIT_HOUR_UTC]
        ebid, eask = float(bid.Open.iloc[entry_i]), float(ask.Open.iloc[entry_i])
        scheduled_bid, scheduled_ask = float(bid.Open.iloc[exit_i]), float(ask.Open.iloc[exit_i])
        quotes = np.asarray([ebid,eask,scheduled_bid,scheduled_ask],dtype=float)
        if not np.isfinite(quotes).all():
            diag["days_skipped_invalid_quotes"] += 1
            diag["invalid_quote_nonfinite"] += 1
            continue
        if eask < ebid:
            diag["days_skipped_invalid_quotes"] += 1
            diag["invalid_entry_spread"] += 1
            continue
        risk_px = (eask-stop) if direction == 1 else (stop-ebid)
        risk_pips = risk_px/PIP
        if not np.isfinite(risk_pips) or risk_pips < MIN_STOP_PIPS or risk_pips > MAX_STOP_PIPS:
            diag["days_skipped_invalid_stop_distance"] += 1
            continue
        target = eask + rr_multiple*risk_px if direction == 1 else ebid - rr_multiple*risk_px
        exit_price, exit_time, reason = None, None, None
        for j in range(entry_i, exit_i):
            if direction == 1:
                so, sh, sl = float(bid.Open.iloc[j]), float(bid.High.iloc[j]), float(bid.Low.iloc[j])
                stop_hit, target_hit = sl <= stop, sh >= target
                if stop_hit:
                    if target_hit: diag["stop_first_collisions"] += 1
                    exit_price = so if so <= stop else stop
                    reason = "STOP"
                elif target_hit:
                    exit_price = so if so >= target else target
                    reason = "TARGET"
            else:
                so, sh, sl = float(ask.Open.iloc[j]), float(ask.High.iloc[j]), float(ask.Low.iloc[j])
                stop_hit, target_hit = sh >= stop, sl <= target
                if stop_hit:
                    if target_hit: diag["stop_first_collisions"] += 1
                    exit_price = so if so >= stop else stop
                    reason = "STOP"
                elif target_hit:
                    exit_price = so if so <= target else target
                    reason = "TARGET"
            if reason is not None:
                exit_time = bid.index[j]
                break
        if reason is None:
            exit_time = bid.index[exit_i]
            exit_price = scheduled_bid if direction == 1 else scheduled_ask
            reason = "TIME_EXIT_16UTC"
            diag["scheduled_time_exits"] += 1
        elif reason == "STOP":
            diag["stop_exits"] += 1
        else:
            diag["target_exits"] += 1
        gross = (float(exit_price)-eask)/PIP if direction == 1 else (ebid-float(exit_price))/PIP
        trades.append({
            "candidate": f"EXCUR{excursion_fraction:.2f}_RR{rr_multiple:.1f}",
            "excursion_fraction_of_range": excursion_fraction,
            "reward_risk_multiple": rr_multiple,
            "range_high_bid": upper,
            "range_low_bid": lower,
            "range_width_pips": width_pips,
            "pre_breakout_close_utc": (bid.index[before_i]+pd.Timedelta(hours=1)).isoformat(),
            "breakout_close_utc": (bid.index[breakout_i]+pd.Timedelta(hours=1)).isoformat(),
            "signal_close_utc": (bid.index[reentry_i]+pd.Timedelta(hours=1)).isoformat(),
            "entry_utc": entry_time.isoformat(),
            "exit_utc": exit_time.isoformat(),
            "direction": "LONG" if direction==1 else "SHORT",
            "entry_bid": ebid,
            "entry_ask": eask,
            "exit_price_executable": float(exit_price),
            "exit_reason": reason,
            "stop_price_reference": stop,
            "target_price_reference": target,
            "risk_pips_at_entry": risk_pips,
            "gross_pips": float(gross),
            "holding_hours": float((exit_time-entry_time).total_seconds()/3600),
        })
        diag["trades_closed"] += 1
    return trades, diag


def bootstrap_forward(trades, cost=1.0):
    forward = [t for t in trades if FORWARD_START <= pd.Timestamp(t["entry_utc"]) < FORWARD_END and pd.Timestamp(t["exit_utc"]) < FORWARD_END]
    if len(forward) < 100:
        return {"draws": 0, "p_mean_positive": None, "ci95_mean_pips": None}
    first_monday = FORWARD_START.normalize()-pd.Timedelta(days=FORWARD_START.dayofweek)
    mondays = pd.date_range(first_monday, FORWARD_END, freq="W-MON", inclusive="left")
    weekly = {w: [] for w in mondays}
    for t in forward:
        dt = pd.Timestamp(t["entry_utc"])
        monday = dt.normalize()-pd.Timedelta(days=dt.dayofweek)
        if monday in weekly: weekly[monday].append(float(t["gross_pips"]-cost))
    arrs = [np.asarray(weekly[w],dtype=float) for w in mondays]
    rng = np.random.default_rng(254)
    estimates=[]
    n=len(arrs)
    for _ in range(BOOTSTRAP_DRAWS):
        samples=[]
        while len(samples)<n:
            start=int(rng.integers(0,n))
            for k in range(BOOTSTRAP_BLOCK_WEEKS):
                samples.append(arrs[(start+k)%n])
                if len(samples)>=n: break
        values=np.concatenate(samples) if samples else np.array([],dtype=float)
        if len(values): estimates.append(float(values.mean()))
    x=np.asarray(estimates,dtype=float)
    return {"draws":int(len(x)),
            "p_mean_positive":float(np.mean(x>0)) if len(x) else None,
            "ci95_mean_pips":[float(np.quantile(x,.025)),float(np.quantile(x,.975))] if len(x) else None,
            "method":"circular 4-week block bootstrap over forward entry-week trade returns"}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    report_path=OUT/"R254_failed_breakout_results.json"
    trades_path=OUT/"R254_failed_breakout_trades.csv"
    annual_path=OUT/"R254_failed_breakout_annual.csv"
    report={
        "status":"STARTED","strategy_family":"EURUSD failed Asian-range breakout and reclaim",
        "verdict":"NOT_EVALUATED",
        "preregistered_design":{
            "asian_range":"BID high/low of H1 bars opening 00:00-05:00 UTC",
            "failed_upside":"pre-breakout close inside range; next H1 close beyond upper range+excursion; following H1 close back inside; fade short",
            "failed_downside":"pre-breakout close inside range; next H1 close below lower range-excursion; following H1 close back inside; fade long",
            "reentry_candle_open_hours_utc":list(REENTRY_SIGNAL_HOURS),
            "entry":"next exact H1 open after reclaim candle closes",
            "stop":"extreme of breakout and reclaim candles (ASK highs for short, BID lows for long)",
            "target":"1R, 1.5R, or 2R",
            "one_attempt_per_utc_day":True,
            "time_exit":"16:00 UTC open",
            "intrabar_policy":"executable BID/ASK H1 OHLC, stop-first on same-bar collision",
            "valid_stop_distance_pips":[MIN_STOP_PIPS,MAX_STOP_PIPS],
            "minimum_breakout_excursion_fraction_of_asian_range":list(EXCURSION_FRACTIONS),
            "extra_cost_stress_pips_on_top_of_observed_bidask":list(EXTRA_COSTS),
            "selection":"highest 2021 validation PF at +1 pip among candidates with >=50 trades; tie-break mean and count; no forward/OOS selection"
        }
    }
    try:
        bid,bdiag=parse_bars(DATA/"eurusd_bid_H1.csv")
        ask,adiag=parse_bars(DATA/"eurusd_ask_H1.csv")
        common=bid.index.intersection(ask.index).sort_values()
        if len(common)<20000: raise RuntimeError(f"Only {len(common)} common EURUSD BID/ASK rows")
        bid,ask=bid.loc[common],ask.loc[common]
        if (ask.Open<bid.Open).any(): raise RuntimeError("EURUSD ASK open below BID open")
        start_day,end_day=common[0].normalize(),common[-1].normalize()
        date_positions={}
        for day in pd.date_range(start_day,end_day,freq="D"):
            expected=pd.date_range(day,day+pd.Timedelta(hours=EXIT_HOUR_UTC),freq="h")
            p=bid.index.get_indexer(expected)
            if len(p)!=EXIT_HOUR_UTC+1 or (p<0).any():
                date_positions[day]=None
            else:
                date_positions[day]=p if all(bid.index[b]-bid.index[a]==pd.Timedelta(hours=1) for a,b in zip(p[:-1],p[1:])) else None
        candidates,diagnostics={},{}
        for excursion in EXCURSION_FRACTIONS:
            for rr in REWARD_RISKS:
                name=f"EXCUR{excursion:.2f}_RR{rr:.1f}"
                candidates[name],diagnostics[name]=simulate_config(bid,ask,date_positions,excursion,rr)
        validation_scores={}
        ranks=[]
        for name,records in candidates.items():
            m=period_metrics(records,VALID_START,VALID_END,1.0)
            validation_scores[name]=m
            if m["trades"]>=MIN_VALIDATION_TRADES:
                score=float(m["PF"]) if isinstance(m["PF"],(int,float)) and np.isfinite(m["PF"]) else (-1.0 if m["PF"] is None else 999.0)
                ranks.append((score,m["mean_net_pips_per_trade"] or -999.0,m["trades"],name))
        if not ranks: raise RuntimeError("No candidate met 50-trade validation minimum")
        ranks.sort(reverse=True)
        chosen=ranks[0][3]
        records=candidates[chosen]
        pd.DataFrame([{**t,**{f"net_pips_cost_{c:.1f}":t["gross_pips"]-c for c in EXTRA_COSTS} for t in records]).to_csv(trades_path,index=False)
        periods={"discovery_2017_2020":(TRAIN_START,TRAIN_END),"validation_2021":(VALID_START,VALID_END),"forward_2022_2025":(FORWARD_START,FORWARD_END),"oos_2026":(OOS_START,OOS_END)}
        metrics={phase:{str(cost):period_metrics(records,a,b,cost) for cost in EXTRA_COSTS} for phase,(a,b) in periods.items()}
        annual=[]
        for year in range(2017,2027):
            a,b=pd.Timestamp(f"{year}-01-01",tz="UTC"),pd.Timestamp(f"{year+1}-01-01",tz="UTC")
            annual.append({"year":year,
                **{f"PF_cost_{c:.1f}":period_metrics(records,a,b,c)["PF"] for c in EXTRA_COSTS},
                **{f"trades_cost_{c:.1f}":period_metrics(records,a,b,c)["trades"] for c in EXTRA_COSTS},
                **{f"mean_pips_cost_{c:.1f}":period_metrics(records,a,b,c)["mean_net_pips_per_trade"] for c in EXTRA_COSTS}})
        pd.DataFrame(annual).to_csv(annual_path,index=False)
        bootstrap=bootstrap_forward(records,1.0)
        fwd_years=[x for x in annual if 2022<=x["year"]<=2025 and x["trades_cost_1.0"]>=20]
        validation=metrics["validation_2021"]["1.0"]
        discovery=metrics["discovery_2017_2020"]["1.0"]
        f1,f2=metrics["forward_2022_2025"]["1.0"],metrics["forward_2022_2025"]["2.0"]
        oos=metrics["oos_2026"]["1.0"]
        gates={
            "validation_min_50_trades":validation["trades"]>=MIN_VALIDATION_TRADES,
            "validation_PF_at_1pip_ge_1.05":safe_greater(validation["PF"],1.05),
            "discovery_min_100_trades":discovery["trades"]>=100,
            "discovery_PF_at_1pip_ge_1.00":safe_greater(discovery["PF"],1.0),
            "forward_min_100_trades":f1["trades"]>=100,
            "forward_PF_at_1pip_ge_1.10":safe_greater(f1["PF"],1.10),
            "forward_PF_at_2pip_ge_1.05":safe_greater(f2["PF"],1.05),
            "forward_frequency_ge_2_trades_per_week":safe_greater(f1["trades_per_week"],2.0),
            "each_forward_year_with_20plus_trades_PF_ge_1_at_1pip":bool(fwd_years) and all(safe_greater(x["PF_cost_1.0"],1.0) for x in fwd_years),
            "forward_4week_block_bootstrap_positive_95pct":bool(bootstrap["ci95_mean_pips"] and bootstrap["ci95_mean_pips"][0]>0 and bootstrap["p_mean_positive"]>=0.95),
            "oos_min_30_trades":oos["trades"]>=30,
            "oos_PF_at_1pip_ge_1.00":safe_greater(oos["PF"],1.0),
        }
        report.update({
            "status":"COMPLETE","data":{"eurusd_bid":bdiag,"eurusd_ask":adiag,"common_hourly_rows":int(len(common)),"common_start_utc":common[0].isoformat(),"common_end_utc":common[-1].isoformat(),"no_bars_synthesized":True},
            "all_candidate_validation_cost_1pip":validation_scores,"selected_candidate":chosen,"candidate_execution_diagnostics":diagnostics,
            "selected_metrics_by_period_and_cost":metrics,"annual_cohorts":annual,"forward_block_bootstrap_cost_1pip":bootstrap,
            "acceptance_gates":gates,"verdict":"LULUS" if all(gates.values()) else "GAGAL",
            "verdict_rule":"All preregistered validation, discovery, forward, annual, bootstrap, frequency and OOS gates must pass.",
            "trade_ledger_sha256":hashlib.sha256(trades_path.read_bytes()).hexdigest(),
            "limitations":["BID/ASK execution uses H1 OHLC; same-bar stop/target collisions are resolved stop-first.","Extra commission/slippage costs are stress assumptions, not broker-confirmed measures.","This is an alpha test, not a funded-account compliance replay."]
        })
    except Exception as exc:
        report.update({"status":"FAILED_RUN","verdict":"GAGAL","error":f"{type(exc).__name__}: {exc}","decision":"No partial performance result is accepted when locked pipeline does not complete."})
    report_path.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":report["status"],"verdict":report["verdict"],"selected_candidate":report.get("selected_candidate"),"metrics":report.get("selected_metrics_by_period_and_cost"),"gates":report.get("acceptance_gates"),"error":report.get("error")},indent=2))
    if report["status"]!="COMPLETE": raise SystemExit(1)


if __name__=="__main__":
    main()
