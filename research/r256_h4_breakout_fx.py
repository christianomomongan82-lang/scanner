#!/usr/bin/env python3
"""R256: EURUSD H4 rolling-range breakout, H1 quote-side execution.

H4 bars are built only from four exact consecutive H1 bars. Entry follows the
completed signal bar; stop/target are then executed on H1 BID/ASK OHLC. A single
winner is selected on 2021 validation; forward/OOS are held out.
"""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path(".")
DATA=ROOT/"dl"/"r251_fx"
OUT=ROOT/"research"
PIP=0.0001
LOOKBACK_H4=(12,24,48)
STOP_WINDOW_H4=(6,12,24)
RR=2.0
MAX_HOLD_HOURS=48
MIN_STOP_PIPS=3.0
MAX_STOP_PIPS=120.0
EXTRA_COSTS=(0.0,0.5,1.0,2.0)
MIN_VALIDATION_TRADES=15
BOOTSTRAP_DRAWS=2000
BOOTSTRAP_BLOCK_WEEKS=4

TRAIN_START=pd.Timestamp("2017-01-01T00:00:00Z")
TRAIN_END=pd.Timestamp("2021-01-01T00:00:00Z")
VALID_START=pd.Timestamp("2021-01-01T00:00:00Z")
VALID_END=pd.Timestamp("2022-01-01T00:00:00Z")
FORWARD_START=pd.Timestamp("2022-01-01T00:00:00Z")
FORWARD_END=pd.Timestamp("2026-01-01T00:00:00Z")
OOS_START=pd.Timestamp("2026-01-01T00:00:00Z")
OOS_END=pd.Timestamp("2026-10-14T00:00:00Z")


def parse_bars(path:Path):
    if not path.is_file(): raise FileNotFoundError(f"Cached quote file missing: {path}")
    raw=pd.read_csv(path)
    raw.columns=[str(c).replace("\ufeff","").strip().lower() for c in raw.columns]
    tcol=next((c for c in ("timestamp","datetime","date","time") if c in raw.columns),None)
    if tcol is None: raise ValueError(f"No timestamp column in {path}")
    ts=raw[tcol].astype(str).str.strip()
    numeric=pd.to_numeric(ts,errors="coerce")
    if numeric.notna().mean()>.95:
        med=float(numeric.abs().median()); unit="ms" if med>=1e11 else ("s" if med>=1e8 else None)
        if unit is None: raise ValueError(f"Unknown timestamp scale in {path}: {med}")
        idx=pd.to_datetime(numeric,unit=unit,utc=True,errors="coerce")
    else: idx=pd.to_datetime(ts,utc=True,errors="coerce")
    need=["open","high","low","close"]
    missing=set(need)-set(raw.columns)
    if missing or idx.isna().any(): raise ValueError(f"Invalid timestamp/OHLC in {path}; missing={missing}")
    bars=raw[need].apply(pd.to_numeric,errors="coerce")
    bars.columns=["Open","High","Low","Close"]; bars.index=pd.DatetimeIndex(idx,name="timestamp_utc")
    bars=bars.replace([np.inf,-np.inf],np.nan).dropna().sort_index()
    duplicates=int(bars.index.duplicated(keep="last").sum()); bars=bars.loc[~bars.index.duplicated(keep="last")]
    valid=((bars.High>=bars[["Open","Close"]].max(axis=1))&(bars.Low<=bars[["Open","Close"]].min(axis=1))&(bars.High>=bars.Low))
    invalid=int((~valid).sum()); bars=bars.loc[valid]
    gaps=bars.index.to_series().diff().dropna()
    return bars,{"rows":int(len(bars)),"duplicate_timestamps_removed":duplicates,"invalid_ohlc_rows_removed":invalid,
        "off_hour_timestamps":int(((bars.index.minute!=0)|(bars.index.second!=0)).sum()),
        "missing_hour_gaps":int((gaps>pd.Timedelta(hours=1)).sum()),
        "start_utc":bars.index[0].isoformat(),"end_utc":bars.index[-1].isoformat(),
        "sha256":hashlib.sha256(path.read_bytes()).hexdigest()}


def build_h4(bid,ask):
    idx=bid.index
    first=idx[0].ceil("4h")
    last_start=(idx[-1]-pd.Timedelta(hours=3)).floor("4h")
    starts=pd.date_range(first,last_start,freq="4h")
    rows=[]; skipped=0
    for start in starts:
        expected=pd.date_range(start,periods=4,freq="h")
        pos=idx.get_indexer(expected)
        if (pos<0).any():
            skipped+=1; continue
        if any(idx[b]-idx[a]!=pd.Timedelta(hours=1) for a,b in zip(pos[:-1],pos[1:])):
            skipped+=1; continue
        rows.append({
            "start":start,
            "bid_open":float(bid.Open.iloc[pos[0]]),
            "bid_high":float(bid.High.iloc[pos].max()),
            "bid_low":float(bid.Low.iloc[pos].min()),
            "bid_close":float(bid.Close.iloc[pos[-1]]),
            "ask_open":float(ask.Open.iloc[pos[0]]),
            "ask_high":float(ask.High.iloc[pos].max()),
            "ask_low":float(ask.Low.iloc[pos].min()),
            "ask_close":float(ask.Close.iloc[pos[-1]]),
            "close_time":start+pd.Timedelta(hours=4),
        })
    if not rows: raise RuntimeError("No complete H4 bins built from exact H1 bars")
    h4=pd.DataFrame(rows).set_index("start")
    return h4,{"candidate_h4_bins":int(len(starts)),"complete_h4_bins":int(len(h4)),"skipped_incomplete_h4_bins":int(skipped),
        "complete_start_utc":h4.index[0].isoformat(),"complete_end_close_utc":h4.close_time.iloc[-1].isoformat(),
        "construction":"UTC-anchored 4-hour bins from four exact H1 BID/ASK candles; no fill or interpolation"}


def pf(values):
    x=np.asarray(values,dtype=float); gp=float(x[x>0].sum()); gl=float(-x[x<0].sum())
    if gl<=0:return "INF" if gp>0 else None
    return gp/gl


def safe_greater(v,t):
    return isinstance(v,(int,float,np.integer,np.floating)) and np.isfinite(v) and v>=t


def period_metrics(trades,start,end,cost):
    a=[t for t in trades if start<=pd.Timestamp(t["entry_utc"])<end and start<=pd.Timestamp(t["exit_utc"])<end]
    vals=np.asarray([t["gross_pips"]-cost for t in a],dtype=float)
    weeks=max((end-start).total_seconds()/(7*86400),1/7)
    return {"trades":int(len(vals)),"PF":pf(vals),"net_pips":float(vals.sum()) if len(vals) else 0.,
        "mean_net_pips_per_trade":float(vals.mean()) if len(vals) else None,"win_rate":float((vals>0).mean()) if len(vals) else None,
        "trades_per_week":float(len(vals)/weeks)}


def simulate(h4,bid,ask,lookback,stop_window):
    hidx=h4.index; hclose=h4.close_time
    h1idx=bid.index
    trades=[]
    diag={"h4_bars_seen":int(len(h4)),"invalid_lookback_or_stop_grid":0,"no_breakout_signal":0,
        "invalid_entry_h1":0,"invalid_48h_horizon":0,"invalid_stop_distance":0,"overlap_skipped":0,
        "invalid_quotes":0,"trades_closed":0,"stop_first_collisions":0,"stop_exits":0,"target_exits":0,"time_exits":0}
    active_exit_h1=-1
    for i in range(max(lookback,stop_window-1),len(h4)-1):
        if hidx[i]-hidx[i-lookback]!=pd.Timedelta(hours=4*lookback):
            diag["invalid_lookback_or_stop_grid"]+=1; continue
        if hidx[i]-hidx[i-stop_window+1]!=pd.Timedelta(hours=4*(stop_window-1)):
            diag["invalid_lookback_or_stop_grid"]+=1; continue
        prior_high=float(h4.bid_high.iloc[i-lookback:i].max())
        prior_low=float(h4.ask_low.iloc[i-lookback:i].min())
        long_signal=float(h4.bid_close.iloc[i])>float(h4.bid_high.iloc[i-lookback:i].max())
        short_signal=float(h4.ask_close.iloc[i])<float(h4.ask_low.iloc[i-lookback:i].min())
        if long_signal and short_signal:
            diag["no_breakout_signal"]+=1; continue
        if not long_signal and not short_signal:
            diag["no_breakout_signal"]+=1; continue
        direction=1 if long_signal else -1
        entry_time=hclose.iloc[i]
        entry_i=int(h1idx.get_indexer([entry_time])[0])
        if entry_i<0 or entry_i+MAX_HOLD_HOURS>=len(h1idx) or h1idx[entry_i]!=entry_time:
            diag["invalid_entry_h1"]+=1; continue
        exit_i=entry_i+MAX_HOLD_HOURS
        if h1idx[exit_i]-h1idx[entry_i]!=pd.Timedelta(hours=MAX_HOLD_HOURS):
            diag["invalid_48h_horizon"]+=1; continue
        if entry_i<=active_exit_h1:
            diag["overlap_skipped"]+=1; continue
        ebid=float(bid.Open.iloc[entry_i]); eask=float(ask.Open.iloc[entry_i])
        scheduled_bid=float(bid.Open.iloc[exit_i]); scheduled_ask=float(ask.Open.iloc[exit_i])
        if not np.isfinite([ebid,eask,scheduled_bid,scheduled_ask]).all() or eask<ebid:
            diag["invalid_quotes"]+=1; continue
        if direction==1:
            stop=float(h4.bid_low.iloc[i-stop_window+1:i+1].min())
            risk_px=eask-stop
        else:
            stop=float(h4.ask_high.iloc[i-stop_window+1:i+1].max())
            risk_px=stop-ebid
        risk_pips=risk_px/PIP
        if not np.isfinite(risk_pips) or risk_pips<MIN_STOP_PIPS or risk_pips>MAX_STOP_PIPS:
            diag["invalid_stop_distance"]+=1; continue
        target=eask+RR*risk_px if direction==1 else ebid-RR*risk_px
        exit_price=None; exit_time=None; reason=None
        for j in range(entry_i,exit_i):
            if direction==1:
                op=float(bid.Open.iloc[j]); hi=float(bid.High.iloc[j]); lo=float(bid.Low.iloc[j])
                stop_hit=lo<=stop; target_hit=hi>=target
                if stop_hit:
                    if target_hit:diag["stop_first_collisions"]+=1
                    exit_price=op if op<=stop else stop; reason="STOP"
                elif target_hit:
                    exit_price=op if op>=target else target; reason="TARGET"
            else:
                op=float(ask.Open.iloc[j]); hi=float(ask.High.iloc[j]); lo=float(ask.Low.iloc[j])
                stop_hit=hi>=stop; target_hit=lo<=target
                if stop_hit:
                    if target_hit:diag["stop_first_collisions"]+=1
                    exit_price=op if op>=stop else stop; reason="STOP"
                elif target_hit:
                    exit_price=op if op<=target else target; reason="TARGET"
            if reason:
                exit_time=h1idx[j]; break
        if reason is None:
            exit_time=h1idx[exit_i]; exit_price=scheduled_bid if direction==1 else scheduled_ask; reason="TIME_EXIT"; diag["time_exits"]+=1
        elif reason=="STOP":diag["stop_exits"]+=1
        else:diag["target_exits"]+=1
        gross=(float(exit_price)-eask)/PIP if direction==1 else (ebid-float(exit_price))/PIP
        trades.append({"candidate":f"L{lookback:02d}_S{stop_window:02d}_RR{RR:.1f}",
            "breakout_lookback_h4":lookback,"stop_window_h4":stop_window,"RR":RR,
            "signal_close_utc":entry_time.isoformat(),"entry_utc":entry_time.isoformat(),"exit_utc":exit_time.isoformat(),
            "direction":"LONG" if direction==1 else "SHORT","entry_bid":ebid,"entry_ask":eask,
            "exit_price_executable":float(exit_price),"exit_reason":reason,"stop_price_reference":stop,
            "target_price_reference":target,"risk_pips_at_entry":risk_pips,"gross_pips":float(gross),
            "holding_hours":float((exit_time-entry_time).total_seconds()/3600)})
        diag["trades_closed"]+=1
        active_exit_h1=(exit_i if reason=="TIME_EXIT" else int(h1idx.get_indexer([exit_time])[0]))
    return trades,diag


def bootstrap_forward(trades,cost=1.0):
    f=[t for t in trades if FORWARD_START<=pd.Timestamp(t["entry_utc"])<FORWARD_END and pd.Timestamp(t["exit_utc"])<FORWARD_END]
    if len(f)<80:return {"draws":0,"p_mean_positive":None,"ci95_mean_pips":None}
    first=FORWARD_START.normalize()-pd.Timedelta(days=FORWARD_START.dayofweek)
    weeks=pd.date_range(first,FORWARD_END,freq="W-MON",inclusive="left")
    grouped={w:[] for w in weeks}
    for t in f:
        dt=pd.Timestamp(t["entry_utc"]); monday=dt.normalize()-pd.Timedelta(days=dt.dayofweek)
        if monday in grouped:grouped[monday].append(float(t["gross_pips"]-cost))
    arrays=[np.asarray(grouped[w],dtype=float) for w in weeks]
    rng=np.random.default_rng(256); est=[]; n=len(arrays)
    for _ in range(BOOTSTRAP_DRAWS):
        sample=[]
        while len(sample)<n:
            start=int(rng.integers(0,n))
            for k in range(BOOTSTRAP_BLOCK_WEEKS):
                sample.append(arrays[(start+k)%n])
                if len(sample)>=n:break
        vals=np.concatenate(sample) if sample else np.array([],dtype=float)
        if len(vals):est.append(float(vals.mean()))
    x=np.asarray(est,dtype=float)
    return {"draws":int(len(x)),"p_mean_positive":float(np.mean(x>0)) if len(x) else None,
        "ci95_mean_pips":[float(np.quantile(x,.025)),float(np.quantile(x,.975))] if len(x) else None,
        "method":"circular 4-week block bootstrap over forward entry-week trade returns"}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    report_path=OUT/"R256_h4_breakout_results.json"
    trades_path=OUT/"R256_h4_breakout_trades.csv"
    annual_path=OUT/"R256_h4_breakout_annual.csv"
    report={"status":"STARTED","strategy_family":"EURUSD H4 rolling breakout with H1 execution","verdict":"NOT_EVALUATED",
        "preregistered_design":{"lookbacks_h4":list(LOOKBACK_H4),"stop_windows_h4":list(STOP_WINDOW_H4),"target_RR":RR,
        "long_signal":"completed H4 BID close above maximum BID high of preceding lookback bars",
        "short_signal":"completed H4 ASK close below minimum ASK low of preceding lookback bars",
        "stop":"minimum BID low for long or maximum ASK high for short over signal H4 bar plus preceding stop-window bars",
        "entry":"next exact H1 open at completed H4 close boundary","execution":"actual H1 BID/ASK OHLC; stop-first for same-bar collisions",
        "maximum_holding_hours":MAX_HOLD_HOURS,"selection":"highest 2021 validation PF at +1 pip with >=15 validation trades; tie-break expectancy and count"}}
    try:
        bid,bdiag=parse_bars(DATA/"eurusd_bid_H1.csv"); ask,adiag=parse_bars(DATA/"eurusd_ask_H1.csv")
        common=bid.index.intersection(ask.index).sort_values()
        if len(common)<20000:raise RuntimeError(f"Only {len(common)} common EURUSD BID/ASK rows")
        bid,ask=bid.loc[common],ask.loc[common]
        if (ask.Open<bid.Open).any():raise RuntimeError("EURUSD ASK open below BID open")
        h4,hdiag=build_h4(bid,ask)
        candidates={};diags={}
        for lookback in LOOKBACK_H4:
            for stopwin in STOP_WINDOW_H4:
                name=f"L{lookback:02d}_S{stopwin:02d}_RR{RR:.1f}"
                candidates[name],diags[name]=simulate(h4,bid,ask,lookback,stopwin)
        validation={};ranks=[]
        for name,recs in candidates.items():
            m=period_metrics(recs,VALID_START,VALID_END,1.0);validation[name]=m
            if m["trades"]>=MIN_VALIDATION_TRADES:
                score=float(m["PF"]) if isinstance(m["PF"],(int,float)) and np.isfinite(m["PF"]) else (-1.0 if m["PF"] is None else 999.0)
                ranks.append((score,m["mean_net_pips_per_trade"] or -999.0,m["trades"],name))
        if not ranks:raise RuntimeError("No candidate met 15-trade validation minimum")
        ranks.sort(reverse=True);chosen=ranks[0][3];recs=candidates[chosen]
        pd.DataFrame([{**t,**{f"net_pips_cost_{c:.1f}":t["gross_pips"]-c for c in EXTRA_COSTS}} for t in recs]).to_csv(trades_path,index=False)
        periods={"discovery_2017_2020":(TRAIN_START,TRAIN_END),"validation_2021":(VALID_START,VALID_END),
            "forward_2022_2025":(FORWARD_START,FORWARD_END),"oos_2026":(OOS_START,OOS_END)}
        metrics={phase:{str(c):period_metrics(recs,a,b,c) for c in EXTRA_COSTS} for phase,(a,b) in periods.items()}
        annual=[]
        for year in range(2017,2027):
            a,b=pd.Timestamp(f"{year}-01-01",tz="UTC"),pd.Timestamp(f"{year+1}-01-01",tz="UTC")
            annual.append({"year":year,**{f"PF_cost_{c:.1f}":period_metrics(recs,a,b,c)["PF"] for c in EXTRA_COSTS},
                **{f"trades_cost_{c:.1f}":period_metrics(recs,a,b,c)["trades"] for c in EXTRA_COSTS},
                **{f"mean_pips_cost_{c:.1f}":period_metrics(recs,a,b,c)["mean_net_pips_per_trade"] for c in EXTRA_COSTS}})
        pd.DataFrame(annual).to_csv(annual_path,index=False)
        boot=bootstrap_forward(recs,1.0)
        years=[x for x in annual if 2022<=x["year"]<=2025 and x["trades_cost_1.0"]>=10]
        disc=metrics["discovery_2017_2020"]["1.0"]; val=metrics["validation_2021"]["1.0"]
        f1=metrics["forward_2022_2025"]["1.0"];f2=metrics["forward_2022_2025"]["2.0"];oos=metrics["oos_2026"]["1.0"]
        gates={"validation_min_15_trades":val["trades"]>=MIN_VALIDATION_TRADES,
            "validation_PF_at_1pip_ge_1.05":safe_greater(val["PF"],1.05),
            "discovery_min_30_trades":disc["trades"]>=30,"discovery_PF_at_1pip_ge_1.00":safe_greater(disc["PF"],1.0),
            "forward_min_80_trades":f1["trades"]>=80,"forward_PF_at_1pip_ge_1.10":safe_greater(f1["PF"],1.10),
            "forward_PF_at_2pip_ge_1.05":safe_greater(f2["PF"],1.05),
            "forward_frequency_ge_1_trade_per_week":safe_greater(f1["trades_per_week"],1.0),
            "each_forward_year_with_10plus_trades_PF_ge_1_at_1pip":bool(years) and all(safe_greater(x["PF_cost_1.0"],1.0) for x in years),
            "forward_4week_block_bootstrap_positive_95pct":bool(boot["ci95_mean_pips"] and boot["ci95_mean_pips"][0]>0 and boot["p_mean_positive"]>=.95),
            "oos_min_20_trades":oos["trades"]>=20,"oos_PF_at_1pip_ge_1.00":safe_greater(oos["PF"],1.0)}
        report.update({"status":"COMPLETE","data":{"eurusd_bid":bdiag,"eurusd_ask":adiag,"h4_construction":hdiag,
            "common_h1_rows":int(len(common)),"common_h1_start_utc":common[0].isoformat(),"common_h1_end_utc":common[-1].isoformat(),
            "no_missing_h1_bars_synthesized":True},
            "candidate_validation_cost_1pip":validation,"selected_candidate":chosen,"candidate_diagnostics":diags,
            "selected_metrics_by_period_and_cost":metrics,"annual_cohorts":annual,"forward_block_bootstrap_cost_1pip":boot,
            "acceptance_gates":gates,"verdict":"LULUS" if all(gates.values()) else "GAGAL",
            "verdict_rule":"All preregistered validation, discovery, forward PF/cost, annual, bootstrap, frequency, and OOS gates must pass.",
            "trade_ledger_sha256":hashlib.sha256(trades_path.read_bytes()).hexdigest(),
            "limitations":["H4 bar boundaries are UTC-anchored and built only from four exact H1 bars.","H1 quote-side OHLC is used for execution; same-bar stop/target collisions are stop-first.",
                "Extra costs are stress assumptions, not broker-confirmed commission/slippage.","This alpha test is not a funded-rule compliance replay."]})
    except Exception as exc:
        report.update({"status":"FAILED_RUN","verdict":"GAGAL","error":f"{type(exc).__name__}: {exc}","decision":"No partial performance result is accepted when the locked pipeline fails."})
    report_path.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":report["status"],"verdict":report["verdict"],"selected":report.get("selected_candidate"),
        "metrics":report.get("selected_metrics_by_period_and_cost"),"gates":report.get("acceptance_gates"),"error":report.get("error")},indent=2))
    if report["status"]!="COMPLETE":raise SystemExit(1)


if __name__=="__main__":main()
