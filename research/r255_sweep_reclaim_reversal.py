#!/usr/bin/env python3
"""R255: EURUSD H1 rolling-extreme sweep-and-reclaim reversal.

A signal requires the current candle to sweep a prior rolling extreme and close
back inside the prior range. Exact H1 history is required, no missing bars are
filled, and the validation year selects one configuration before forward/OOS.
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
LOOKBACKS = (12, 24, 48)
REWARD_RISKS = (1.0, 1.5, 2.0)
SWEEP_BUFFER_FRACTION = 0.02
HOLD_HOURS = 8
MIN_STOP_PIPS = 2.0
MAX_STOP_PIPS = 60.0
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
    if numeric.notna().mean() > .95:
        med = float(numeric.abs().median())
        unit = "ms" if med >= 1e11 else ("s" if med >= 1e8 else None)
        if unit is None: raise ValueError(f"Unknown timestamp scale in {path}: {med}")
        idx = pd.to_datetime(numeric, unit=unit, utc=True, errors="coerce")
    else:
        idx = pd.to_datetime(ts, utc=True, errors="coerce")
    required = ["open", "high", "low", "close"]
    missing = set(required)-set(raw.columns)
    if missing or idx.isna().any(): raise ValueError(f"Invalid timestamps/OHLC in {path}; missing={missing}")
    bars=raw[required].apply(pd.to_numeric,errors="coerce")
    bars.columns=["Open","High","Low","Close"]
    bars.index=pd.DatetimeIndex(idx,name="timestamp_utc")
    bars=bars.replace([np.inf,-np.inf],np.nan).dropna().sort_index()
    dups=int(bars.index.duplicated(keep="last").sum())
    bars=bars.loc[~bars.index.duplicated(keep="last")]
    valid=((bars.High>=bars[["Open","Close"]].max(axis=1))&(bars.Low<=bars[["Open","Close"]].min(axis=1))&(bars.High>=bars.Low))
    invalid=int((~valid).sum())
    bars=bars.loc[valid]
    if bars.empty: raise ValueError(f"No valid bars in {path}")
    gaps=bars.index.to_series().diff().dropna()
    return bars, {
        "rows":int(len(bars)),"duplicate_timestamps_removed":dups,"invalid_ohlc_rows_removed":invalid,
        "off_hour_timestamps":int(((bars.index.minute!=0)|(bars.index.second!=0)).sum()),
        "missing_hour_gaps":int((gaps>pd.Timedelta(hours=1)).sum()),
        "start_utc":bars.index[0].isoformat(),"end_utc":bars.index[-1].isoformat(),
        "sha256":hashlib.sha256(path.read_bytes()).hexdigest()
    }


def pf(values):
    x=np.asarray(values,dtype=float)
    gp=float(x[x>0].sum()); gl=float(-x[x<0].sum())
    if gl<=0: return "INF" if gp>0 else None
    return gp/gl


def safe_greater(value, threshold):
    return isinstance(value,(int,float,np.integer,np.floating)) and np.isfinite(value) and value>=threshold


def period_metrics(trades,start,end,cost):
    kept=[t for t in trades if start<=pd.Timestamp(t["entry_utc"])<end and start<=pd.Timestamp(t["exit_utc"])<end]
    vals=np.asarray([t["gross_pips"]-cost for t in kept],dtype=float)
    weeks=max((end-start).total_seconds()/(7*86400),1/7)
    return {"trades":int(len(vals)),"PF":pf(vals),"net_pips":float(vals.sum()) if len(vals) else 0.0,
        "mean_net_pips_per_trade":float(vals.mean()) if len(vals) else None,
        "win_rate":float((vals>0).mean()) if len(vals) else None,"trades_per_week":float(len(vals)/weeks)}


def prepare_rolling_levels(bid, ask, lookback):
    # Each shifted rolling value at i covers only bars i-lookback ... i-1.
    # Exact timestamp-grid checks in simulate reject windows spanning data gaps.
    bh = bid.High.rolling(lookback, min_periods=lookback).max().shift(1).to_numpy(float)
    bl = bid.Low.rolling(lookback, min_periods=lookback).min().shift(1).to_numpy(float)
    ah = ask.High.rolling(lookback, min_periods=lookback).max().shift(1).to_numpy(float)
    al = ask.Low.rolling(lookback, min_periods=lookback).min().shift(1).to_numpy(float)
    return {"prev_high_bid": bh, "prev_low_bid": bl, "prev_high_ask": ah, "prev_low_ask": al,
            "range_bid": bh - bl, "range_ask": ah - al}


def simulate(bid,ask,lookback,rr,levels):
    idx=bid.index
    trades=[]
    diag={"bars_seen":int(len(idx)),"invalid_or_gap_lookbacks":0,"no_sweep_reclaim":0,
          "ambiguous_two_sided_sweep":0,"invalid_forward_grid":0,"invalid_quotes":0,
          "invalid_stop_distance":0,"overlap_skipped":0,"trades_closed":0,
          "stop_first_collisions":0,"stop_exits":0,"target_exits":0,"time_exits":0}
    active_exit=-1
    for i in range(lookback,len(idx)-HOLD_HOURS-1):
        if idx[i]-idx[i-lookback]!=pd.Timedelta(hours=lookback):
            diag["invalid_or_gap_lookbacks"]+=1
            continue
        entry_i=i+1
        exit_i=entry_i+HOLD_HOURS
        if idx[entry_i]-idx[i]!=pd.Timedelta(hours=1) or idx[exit_i]-idx[entry_i]!=pd.Timedelta(hours=HOLD_HOURS):
            diag["invalid_forward_grid"]+=1
            continue
        prev_low_bid=float(levels["prev_low_bid"][i])
        prev_high_bid=float(levels["prev_high_bid"][i])
        prev_low_ask=float(levels["prev_low_ask"][i])
        prev_high_ask=float(levels["prev_high_ask"][i])
        range_bid=float(levels["range_bid"][i])
        range_ask=float(levels["range_ask"][i])
        if range_bid<=0 or range_ask<=0:
            diag["invalid_or_gap_lookbacks"]+=1
            continue
        buffer_bid=range_bid*SWEEP_BUFFER_FRACTION
        buffer_ask=range_ask*SWEEP_BUFFER_FRACTION
        low_sweep=(float(bid.Low.iloc[i]) < prev_low_bid-buffer_bid and float(bid.Close.iloc[i])>prev_low_bid and float(bid.Close.iloc[i])<=prev_high_bid)
        high_sweep=(float(ask.High.iloc[i]) > prev_high_ask+buffer_ask and float(ask.Close.iloc[i])<prev_high_ask and float(ask.Close.iloc[i])>=prev_low_ask)
        if low_sweep and high_sweep:
            diag["ambiguous_two_sided_sweep"]+=1
            continue
        if not low_sweep and not high_sweep:
            diag["no_sweep_reclaim"]+=1
            continue
        direction=1 if low_sweep else -1
        if entry_i<=active_exit:
            diag["overlap_skipped"]+=1
            continue
        entry_bid=float(bid.Open.iloc[entry_i]); entry_ask=float(ask.Open.iloc[entry_i])
        exit_bid=float(bid.Open.iloc[exit_i]); exit_ask=float(ask.Open.iloc[exit_i])
        quotes=np.asarray([entry_bid,entry_ask,exit_bid,exit_ask],dtype=float)
        if not np.isfinite(quotes).all() or entry_ask<entry_bid:
            diag["invalid_quotes"]+=1
            continue
        stop=float(bid.Low.iloc[i]) if direction==1 else float(ask.High.iloc[i])
        risk_px=entry_ask-stop if direction==1 else stop-entry_bid
        risk_pips=risk_px/PIP
        if not np.isfinite(risk_pips) or risk_pips<MIN_STOP_PIPS or risk_pips>MAX_STOP_PIPS:
            diag["invalid_stop_distance"]+=1
            continue
        target=entry_ask+rr*risk_px if direction==1 else entry_bid-rr*risk_px
        exit_price=None; exit_time=None; reason=None
        for j in range(entry_i,exit_i):
            if direction==1:
                op=float(bid.Open.iloc[j]); hi=float(bid.High.iloc[j]); lo=float(bid.Low.iloc[j])
                stop_hit=lo<=stop; target_hit=hi>=target
                if stop_hit:
                    if target_hit: diag["stop_first_collisions"]+=1
                    exit_price=op if op<=stop else stop; reason="STOP"
                elif target_hit:
                    exit_price=op if op>=target else target; reason="TARGET"
            else:
                op=float(ask.Open.iloc[j]); hi=float(ask.High.iloc[j]); lo=float(ask.Low.iloc[j])
                stop_hit=hi>=stop; target_hit=lo<=target
                if stop_hit:
                    if target_hit: diag["stop_first_collisions"]+=1
                    exit_price=op if op>=stop else stop; reason="STOP"
                elif target_hit:
                    exit_price=op if op<=target else target; reason="TARGET"
            if reason:
                exit_time=idx[j]
                break
        if reason is None:
            exit_time=idx[exit_i]
            exit_price=exit_bid if direction==1 else exit_ask
            reason="TIME_EXIT"
            diag["time_exits"]+=1
        elif reason=="STOP": diag["stop_exits"]+=1
        else: diag["target_exits"]+=1
        gross=(float(exit_price)-entry_ask)/PIP if direction==1 else (entry_bid-float(exit_price))/PIP
        trades.append({"candidate":f"L{lookback:02d}_RR{rr:.1f}","lookback_hours":lookback,"reward_risk_multiple":rr,
            "sweep_buffer_fraction_of_prior_range":SWEEP_BUFFER_FRACTION,
            "prior_low_bid":prev_low_bid,"prior_high_bid":prev_high_bid,
            "signal_close_utc":(idx[i]+pd.Timedelta(hours=1)).isoformat(),"entry_utc":idx[entry_i].isoformat(),
            "exit_utc":exit_time.isoformat(),"direction":"LONG" if direction==1 else "SHORT",
            "entry_bid":entry_bid,"entry_ask":entry_ask,"exit_price_executable":float(exit_price),
            "exit_reason":reason,"stop_price_reference":stop,"target_price_reference":target,
            "risk_pips_at_entry":risk_pips,"gross_pips":float(gross),
            "holding_hours":float((exit_time-idx[entry_i]).total_seconds()/3600)})
        diag["trades_closed"]+=1
        active_exit=exit_i if reason=="TIME_EXIT" else idx.searchsorted(exit_time)
    return trades,diag


def bootstrap_forward(trades,cost=1.0):
    forward=[t for t in trades if FORWARD_START<=pd.Timestamp(t["entry_utc"])<FORWARD_END and pd.Timestamp(t["exit_utc"])<FORWARD_END]
    if len(forward)<100:return {"draws":0,"p_mean_positive":None,"ci95_mean_pips":None}
    first=FORWARD_START.normalize()-pd.Timedelta(days=FORWARD_START.dayofweek)
    weeks=pd.date_range(first,FORWARD_END,freq="W-MON",inclusive="left")
    grouped={w:[] for w in weeks}
    for t in forward:
        dt=pd.Timestamp(t["entry_utc"]); monday=dt.normalize()-pd.Timedelta(days=dt.dayofweek)
        if monday in grouped: grouped[monday].append(float(t["gross_pips"]-cost))
    arrays=[np.asarray(grouped[w],dtype=float) for w in weeks]
    rng=np.random.default_rng(255); estimates=[]; n=len(arrays)
    for _ in range(BOOTSTRAP_DRAWS):
        sample=[]
        while len(sample)<n:
            start=int(rng.integers(0,n))
            for k in range(BOOTSTRAP_BLOCK_WEEKS):
                sample.append(arrays[(start+k)%n])
                if len(sample)>=n:break
        values=np.concatenate(sample) if sample else np.array([],dtype=float)
        if len(values):estimates.append(float(values.mean()))
    x=np.asarray(estimates,dtype=float)
    return {"draws":int(len(x)),"p_mean_positive":float(np.mean(x>0)) if len(x) else None,
        "ci95_mean_pips":[float(np.quantile(x,.025)),float(np.quantile(x,.975))] if len(x) else None,
        "method":"circular 4-week block bootstrap over forward entry-week trade returns"}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    report_path=OUT/"R255_sweep_reclaim_results.json"
    trades_path=OUT/"R255_sweep_reclaim_trades.csv"
    annual_path=OUT/"R255_sweep_reclaim_annual.csv"
    report={"status":"STARTED","strategy_family":"EURUSD rolling-extreme sweep-and-reclaim reversal","verdict":"NOT_EVALUATED",
      "preregistered_design":{
        "lookbacks_hours":list(LOOKBACKS),"signal_long":"BID low sweeps 2% below prior lookback BID low, then BID close reclaims above prior low and closes within prior BID range",
        "signal_short":"ASK high sweeps 2% above prior lookback ASK high, then ASK close reclaims below prior high and closes within prior ASK range",
        "entry":"next exact H1 open","exit":"8 exact elapsed hours later or earlier at stop/target",
        "stop":"signal candle sweep extreme using executable side (BID low for long, ASK high for short)",
        "targets_R":list(REWARD_RISKS),"one_position_at_a_time":True,"stop_first_same_bar":True,
        "valid_stop_distance_pips":[MIN_STOP_PIPS,MAX_STOP_PIPS],"extra_cost_stress_pips_on_top_of_bidask":list(EXTRA_COSTS),
        "selection":"highest 2021 validation PF at +1 extra pip among candidates with >=50 trades; tie-break mean, count; no forward/OOS selection"
      }}
    try:
        bid,bdiag=parse_bars(DATA/"eurusd_bid_H1.csv"); ask,adiag=parse_bars(DATA/"eurusd_ask_H1.csv")
        common=bid.index.intersection(ask.index).sort_values()
        if len(common)<20000:raise RuntimeError(f"Only {len(common)} common EURUSD BID/ASK bars")
        bid,ask=bid.loc[common],ask.loc[common]
        if (ask.Open<bid.Open).any():raise RuntimeError("EURUSD ASK open below BID open")
        candidates={};diagnostics={}
        rolling_levels={lookback:prepare_rolling_levels(bid,ask,lookback) for lookback in LOOKBACKS}
        for lookback in LOOKBACKS:
            for rr in REWARD_RISKS:
                name=f"L{lookback:02d}_RR{rr:.1f}"
                candidates[name],diagnostics[name]=simulate(bid,ask,lookback,rr,rolling_levels[lookback])
        validation={};ranks=[]
        for name,records in candidates.items():
            m=period_metrics(records,VALID_START,VALID_END,1.0);validation[name]=m
            if m["trades"]>=MIN_VALIDATION_TRADES:
                score=float(m["PF"]) if isinstance(m["PF"],(int,float)) and np.isfinite(m["PF"]) else (-1.0 if m["PF"] is None else 999.0)
                ranks.append((score,m["mean_net_pips_per_trade"] or -999.0,m["trades"],name))
        if not ranks:raise RuntimeError("No candidate met validation trade minimum")
        ranks.sort(reverse=True);chosen=ranks[0][3];records=candidates[chosen]
        pd.DataFrame([{**t,**{f"net_pips_cost_{cost:.1f}":t["gross_pips"]-cost for cost in EXTRA_COSTS}} for t in records]).to_csv(trades_path,index=False)
        phases={"discovery_2017_2020":(TRAIN_START,TRAIN_END),"validation_2021":(VALID_START,VALID_END),
            "forward_2022_2025":(FORWARD_START,FORWARD_END),"oos_2026":(OOS_START,OOS_END)}
        metrics={phase:{str(cost):period_metrics(records,a,b,cost) for cost in EXTRA_COSTS} for phase,(a,b) in phases.items()}
        annual=[]
        for year in range(2017,2027):
            a,b=pd.Timestamp(f"{year}-01-01",tz="UTC"),pd.Timestamp(f"{year+1}-01-01",tz="UTC")
            annual.append({"year":year,**{f"PF_cost_{cost:.1f}":period_metrics(records,a,b,cost)["PF"] for cost in EXTRA_COSTS},
                **{f"trades_cost_{cost:.1f}":period_metrics(records,a,b,cost)["trades"] for cost in EXTRA_COSTS},
                **{f"mean_pips_cost_{cost:.1f}":period_metrics(records,a,b,cost)["mean_net_pips_per_trade"] for cost in EXTRA_COSTS}})
        pd.DataFrame(annual).to_csv(annual_path,index=False)
        boot=bootstrap_forward(records,1.0)
        years=[x for x in annual if 2022<=x["year"]<=2025 and x["trades_cost_1.0"]>=20]
        val=metrics["validation_2021"]["1.0"];disc=metrics["discovery_2017_2020"]["1.0"]
        f1=metrics["forward_2022_2025"]["1.0"];f2=metrics["forward_2022_2025"]["2.0"];oos=metrics["oos_2026"]["1.0"]
        gates={"validation_min_50_trades":val["trades"]>=MIN_VALIDATION_TRADES,
          "validation_PF_at_1pip_ge_1.05":safe_greater(val["PF"],1.05),
          "discovery_min_100_trades":disc["trades"]>=100,
          "discovery_PF_at_1pip_ge_1.00":safe_greater(disc["PF"],1.0),
          "forward_min_100_trades":f1["trades"]>=100,
          "forward_PF_at_1pip_ge_1.10":safe_greater(f1["PF"],1.10),
          "forward_PF_at_2pip_ge_1.05":safe_greater(f2["PF"],1.05),
          "forward_frequency_ge_2_trades_per_week":safe_greater(f1["trades_per_week"],2.0),
          "each_forward_year_with_20plus_trades_PF_ge_1_at_1pip":bool(years) and all(safe_greater(x["PF_cost_1.0"],1.0) for x in years),
          "forward_4week_block_bootstrap_positive_95pct":bool(boot["ci95_mean_pips"] and boot["ci95_mean_pips"][0]>0 and boot["p_mean_positive"]>=.95),
          "oos_min_30_trades":oos["trades"]>=30,"oos_PF_at_1pip_ge_1.00":safe_greater(oos["PF"],1.0)}
        report.update({"status":"COMPLETE","data":{"eurusd_bid":bdiag,"eurusd_ask":adiag,"common_hourly_rows":int(len(common)),
            "common_start_utc":common[0].isoformat(),"common_end_utc":common[-1].isoformat(),"no_bars_synthesized":True},
            "candidate_validation_cost_1pip":validation,"selected_candidate":chosen,"candidate_diagnostics":diagnostics,
            "selected_metrics_by_period_and_cost":metrics,"annual_cohorts":annual,"forward_block_bootstrap_cost_1pip":boot,
            "acceptance_gates":gates,"verdict":"LULUS" if all(gates.values()) else "GAGAL",
            "verdict_rule":"All validation, discovery, forward, annual consistency, inferential, frequency, and OOS gates must pass.",
            "trade_ledger_sha256":hashlib.sha256(trades_path.read_bytes()).hexdigest(),
            "limitations":["H1 quote-side OHLC executes stop/target using stop-first handling when both are touched in a candle.",
                "Additional costs are stress assumptions, not confirmed broker commission/slippage.","This alpha test is not a funded-rule compliance replay."]})
    except Exception as exc:
        report.update({"status":"FAILED_RUN","verdict":"GAGAL","error":f"{type(exc).__name__}: {exc}","decision":"No partial result accepted if locked pipeline failed."})
    report_path.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":report["status"],"verdict":report["verdict"],"selected":report.get("selected_candidate"),
        "metrics":report.get("selected_metrics_by_period_and_cost"),"gates":report.get("acceptance_gates"),"error":report.get("error")},indent=2))
    if report["status"]!="COMPLETE":raise SystemExit(1)


if __name__=="__main__":main()
