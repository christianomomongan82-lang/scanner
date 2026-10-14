#!/usr/bin/env python3
"""R257: EURUSD H1 range-compression breakout with frozen training thresholds.

Compression thresholds are fitted only on 2017-2020. Eight fixed configurations
are ranked only on 2021 validation; 2022-2025 forward and 2026 OOS are never used
to select parameters. Actual quote-side H1 OHLC drives entry and exit.
"""
from __future__ import annotations
import hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

ROOT=Path("."); DATA=ROOT/"dl"/"r251_fx"; OUT=ROOT/"research"
PIP=0.0001
BREAKOUT_LOOKBACKS=(12,24)
COMPRESSION_QUANTILES=(0.20,0.30)
REWARD_RISKS=(1.5,2.0)
COMPRESSION_HOURS=6
MAX_HOLD_HOURS=24
MIN_STOP_PIPS=3.0
MAX_STOP_PIPS=60.0
EXTRA_COSTS=(0.0,0.5,1.0,2.0)
MIN_VALIDATION_TRADES=50
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
    if not path.is_file(): raise FileNotFoundError(f"Cached file not found: {path}")
    raw=pd.read_csv(path)
    raw.columns=[str(c).replace("\ufeff","").strip().lower() for c in raw.columns]
    tc=next((c for c in ("timestamp","datetime","date","time") if c in raw.columns),None)
    if tc is None: raise ValueError(f"No timestamp column in {path}")
    ts=raw[tc].astype(str).str.strip(); nums=pd.to_numeric(ts,errors="coerce")
    if nums.notna().mean()>.95:
        med=float(nums.abs().median()); unit="ms" if med>=1e11 else ("s" if med>=1e8 else None)
        if unit is None: raise ValueError(f"Unknown timestamp scale: {med}")
        idx=pd.to_datetime(nums,unit=unit,utc=True,errors="coerce")
    else: idx=pd.to_datetime(ts,utc=True,errors="coerce")
    req=["open","high","low","close"]; miss=set(req)-set(raw.columns)
    if miss or idx.isna().any(): raise ValueError(f"Invalid timestamps/OHLC; missing={miss}")
    bars=raw[req].apply(pd.to_numeric,errors="coerce")
    bars.columns=["Open","High","Low","Close"]; bars.index=pd.DatetimeIndex(idx,name="timestamp_utc")
    bars=bars.replace([np.inf,-np.inf],np.nan).dropna().sort_index()
    dups=int(bars.index.duplicated(keep="last").sum()); bars=bars.loc[~bars.index.duplicated(keep="last")]
    ok=((bars.High>=bars[["Open","Close"]].max(axis=1))&(bars.Low<=bars[["Open","Close"]].min(axis=1))&(bars.High>=bars.Low))
    invalid=int((~ok).sum()); bars=bars.loc[ok]
    gaps=bars.index.to_series().diff().dropna()
    return bars,{"rows":int(len(bars)),"duplicate_timestamps_removed":dups,"invalid_ohlc_rows_removed":invalid,
        "off_hour_timestamps":int(((bars.index.minute!=0)|(bars.index.second!=0)).sum()),
        "missing_hour_gaps":int((gaps>pd.Timedelta(hours=1)).sum()),"start_utc":bars.index[0].isoformat(),
        "end_utc":bars.index[-1].isoformat(),"sha256":hashlib.sha256(path.read_bytes()).hexdigest()}


def pf(vals):
    a=np.asarray(vals,dtype=float); gains=float(a[a>0].sum()); losses=float(-a[a<0].sum())
    if losses<=0:return "INF" if gains>0 else None
    return gains/losses


def safe_ge(v,x):
    return isinstance(v,(int,float,np.integer,np.floating)) and np.isfinite(v) and v>=x


def metrics(trades,start,end,cost):
    sample=[t for t in trades if start<=pd.Timestamp(t["entry_utc"])<end and start<=pd.Timestamp(t["exit_utc"])<end]
    vals=np.asarray([t["gross_pips"]-cost for t in sample],dtype=float)
    weeks=max((end-start).total_seconds()/(7*86400),1/7)
    return {"trades":int(len(vals)),"PF":pf(vals),"net_pips":float(vals.sum()) if len(vals) else 0.0,
        "mean_net_pips_per_trade":float(vals.mean()) if len(vals) else None,"win_rate":float(np.mean(vals>0)) if len(vals) else None,
        "trades_per_week":float(len(vals)/weeks)}


def make_features(bid,ask):
    idx=bid.index; ns=idx.asi8; n=len(idx); hour=int(pd.Timedelta(hours=1).value)
    bid_high=bid.High.to_numpy(float); bid_low=bid.Low.to_numpy(float); bid_close=bid.Close.to_numpy(float)
    ask_high=ask.High.to_numpy(float); ask_low=ask.Low.to_numpy(float); ask_close=ask.Close.to_numpy(float)
    compress=np.full(n,np.nan); prior_high={}; prior_low={}
    exact6=np.zeros(n,dtype=bool)
    for i in range(COMPRESSION_HOURS,n):
        exact6[i]=(ns[i]-ns[i-COMPRESSION_HOURS]==COMPRESSION_HOURS*hour)
    # Vectorized prior-window extrema. Gaps are invalidated explicitly in the signal loop.
    comp_high=pd.Series(bid_high).rolling(COMPRESSION_HOURS,min_periods=COMPRESSION_HOURS).max().shift(1).to_numpy()
    comp_low=pd.Series(bid_low).rolling(COMPRESSION_HOURS,min_periods=COMPRESSION_HOURS).min().shift(1).to_numpy()
    compress=comp_high-comp_low
    for lookback in BREAKOUT_LOOKBACKS:
        prior_high[lookback]=pd.Series(bid_high).rolling(lookback,min_periods=lookback).max().shift(1).to_numpy()
        prior_low[lookback]=pd.Series(ask_low).rolling(lookback,min_periods=lookback).min().shift(1).to_numpy()
    return {"index":idx,"ns":ns,"hour_ns":hour,"bid_high":bid_high,"bid_low":bid_low,"bid_close":bid_close,
        "ask_high":ask_high,"ask_low":ask_low,"ask_close":ask_close,"compression_range":compress,
        "compression_high":comp_high,"compression_low":comp_low,"exact6":exact6,
        "prior_high":prior_high,"prior_low":prior_low}


def simulate(bid,ask,features,lookback,quantile,threshold,rr):
    idx=features["index"]; ns=features["ns"]; hour=features["hour_ns"]; n=len(idx)
    bh=features["bid_high"]; bl=features["bid_low"]; bc=features["bid_close"]
    ah=features["ask_high"]; al=features["ask_low"]; ac=features["ask_close"]
    cr=features["compression_range"]; ch=features["compression_high"]; cl=features["compression_low"]
    prior_high=features["prior_high"][lookback]; prior_low=features["prior_low"][lookback]
    records=[]; active_exit=-1
    diag={"bars_seen":n,"invalid_compression_grid":0,"invalid_breakout_grid":0,"not_compressed_or_no_breakout":0,
        "overlap_skipped":0,"invalid_entry_exit_grid":0,"invalid_stop_distance":0,"invalid_quotes":0,
        "trades_closed":0,"stop_first_collisions":0,"stop_exits":0,"target_exits":0,"time_exits":0}
    for i in range(max(lookback,COMPRESSION_HOURS),n-MAX_HOLD_HOURS-1):
        if not features["exact6"][i] or not np.isfinite(cr[i]) or cr[i]<=0:
            diag["invalid_compression_grid"]+=1; continue
        if ns[i]-ns[i-lookback]!=lookback*hour:
            diag["invalid_breakout_grid"]+=1; continue
        if not (cr[i]<=threshold):
            diag["not_compressed_or_no_breakout"]+=1; continue
        long_sig=bc[i]>prior_high[i]
        short_sig=ac[i]<prior_low[i]
        if long_sig==short_sig:
            diag["not_compressed_or_no_breakout"]+=1; continue
        entry_i=i+1; exit_i=entry_i+MAX_HOLD_HOURS
        if ns[entry_i]-ns[i]!=hour or ns[exit_i]-ns[entry_i]!=MAX_HOLD_HOURS*hour or np.any(np.diff(ns[entry_i:exit_i+1])!=hour):
            diag["invalid_entry_exit_grid"]+=1; continue
        if entry_i<=active_exit:
            diag["overlap_skipped"]+=1; continue
        direction=1 if long_sig else -1
        ebid=float(bid.Open.iloc[entry_i]); eask=float(ask.Open.iloc[entry_i])
        if not np.isfinite([ebid,eask]).all() or eask<ebid:
            diag["invalid_quotes"]+=1; continue
        stop=float(bl[i]) if direction==1 else float(ah[i])
        risk=(eask-stop) if direction==1 else (stop-ebid)
        risk_pips=risk/PIP
        if not np.isfinite(risk_pips) or risk_pips<MIN_STOP_PIPS or risk_pips>MAX_STOP_PIPS:
            diag["invalid_stop_distance"]+=1; continue
        target=eask+rr*risk if direction==1 else ebid-rr*risk
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
                exit_time=idx[j]; break
        if reason is None:
            exit_time=idx[exit_i]; exit_price=float(bid.Open.iloc[exit_i] if direction==1 else ask.Open.iloc[exit_i])
            reason="TIME_EXIT"; diag["time_exits"]+=1
        elif reason=="STOP":diag["stop_exits"]+=1
        else:diag["target_exits"]+=1
        gross=(exit_price-eask)/PIP if direction==1 else (ebid-exit_price)/PIP
        records.append({"candidate":f"B{lookback:02d}_Q{int(quantile*100):02d}_RR{rr:.1f}",
            "breakout_lookback_hours":lookback,"compression_quantile":quantile,"compression_threshold_price":threshold,
            "compression_range_price":float(cr[i]),"reward_risk_multiple":rr,
            "signal_close_utc":(idx[i]+pd.Timedelta(hours=1)).isoformat(),"entry_utc":idx[entry_i].isoformat(),
            "exit_utc":exit_time.isoformat(),"direction":"LONG" if direction==1 else "SHORT",
            "entry_bid":ebid,"entry_ask":eask,"exit_price_executable":float(exit_price),"exit_reason":reason,
            "stop_price_reference":stop,"target_price_reference":target,"risk_pips_at_entry":risk_pips,
            "gross_pips":float(gross),"holding_hours":float((exit_time-idx[entry_i]).total_seconds()/3600)})
        active_exit=exit_i if reason=="TIME_EXIT" else int(np.searchsorted(ns,(pd.Timestamp(exit_time).value)))
        diag["trades_closed"]+=1
    return records,diag


def bootstrap_forward(trades,cost=1.0):
    f=[t for t in trades if FORWARD_START<=pd.Timestamp(t["entry_utc"])<FORWARD_END and pd.Timestamp(t["exit_utc"])<FORWARD_END]
    if len(f)<100:return {"draws":0,"p_mean_positive":None,"ci95_mean_pips":None}
    first=FORWARD_START.normalize()-pd.Timedelta(days=FORWARD_START.dayofweek)
    weeks=pd.date_range(first,FORWARD_END,freq="W-MON",inclusive="left"); grouped={w:[] for w in weeks}
    for t in f:
        dt=pd.Timestamp(t["entry_utc"]); monday=dt.normalize()-pd.Timedelta(days=dt.dayofweek)
        if monday in grouped:grouped[monday].append(float(t["gross_pips"]-cost))
    arrays=[np.asarray(grouped[w],dtype=float) for w in weeks]; rng=np.random.default_rng(257); estimates=[]; n=len(arrays)
    for _ in range(BOOTSTRAP_DRAWS):
        sample=[]
        while len(sample)<n:
            start=int(rng.integers(0,n))
            for k in range(BOOTSTRAP_BLOCK_WEEKS):
                sample.append(arrays[(start+k)%n])
                if len(sample)>=n:break
        vals=np.concatenate(sample) if sample else np.array([],dtype=float)
        if len(vals):estimates.append(float(vals.mean()))
    a=np.asarray(estimates,dtype=float)
    return {"draws":int(len(a)),"p_mean_positive":float(np.mean(a>0)) if len(a) else None,
        "ci95_mean_pips":[float(np.quantile(a,.025)),float(np.quantile(a,.975))] if len(a) else None,
        "method":"circular 4-week block bootstrap over forward entry-week trade returns"}


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    report_path=OUT/"R257_compression_breakout_results.json"; trades_path=OUT/"R257_compression_breakout_trades.csv"; annual_path=OUT/"R257_compression_breakout_annual.csv"
    report={"status":"STARTED","strategy_family":"EURUSD H1 range-compression breakout",
        "verdict":"NOT_EVALUATED","preregistered_design":{"compression_window_hours":COMPRESSION_HOURS,
        "compression_threshold_fit_period":["2017-01-01","2021-01-01"],"compression_quantiles":list(COMPRESSION_QUANTILES),
        "breakout_lookback_hours":list(BREAKOUT_LOOKBACKS),"target_RR":list(REWARD_RISKS),
        "long_signal":"six prior H1 bars compressed below the training-only range quantile and current BID close breaks previous lookback high",
        "short_signal":"six prior H1 bars compressed below the training-only range quantile and current ASK close breaks previous lookback low",
        "entry":"next exact H1 open","stop":"opposite extreme of completed breakout H1 candle","maximum_holding_hours":MAX_HOLD_HOURS,
        "intrabar_execution":"actual BID/ASK H1 OHLC, stop-first if stop/target both touched","extra_cost_stress_pips_on_top_of_observed_bidask":list(EXTRA_COSTS),
        "selection":"highest 2021 validation PF at +1 pip among candidates with at least 50 trades; tie-break expectancy then count; no forward/OOS tuning"}}
    try:
        bid,bdiag=parse_bars(DATA/"eurusd_bid_H1.csv"); ask,adiag=parse_bars(DATA/"eurusd_ask_H1.csv")
        common=bid.index.intersection(ask.index).sort_values()
        if len(common)<20000:raise RuntimeError(f"Only {len(common)} common EURUSD BID/ASK bars")
        bid,ask=bid.loc[common],ask.loc[common]
        if (ask.Open<bid.Open).any():raise RuntimeError("EURUSD ASK open below BID open")
        feats=make_features(bid,ask); thresholds={}
        ns=feats["ns"]; hour=feats["hour_ns"]; ranges=feats["compression_range"]; exact6=feats["exact6"]; close_times=common+pd.Timedelta(hours=1)
        trainvals=[]
        for i in range(COMPRESSION_HOURS,len(common)):
            if exact6[i] and TRAIN_START<=close_times[i]<TRAIN_END and np.isfinite(ranges[i]) and ranges[i]>0:
                trainvals.append(float(ranges[i]))
        if len(trainvals)<1000:raise RuntimeError(f"Insufficient training compression ranges: {len(trainvals)}")
        for q in COMPRESSION_QUANTILES:thresholds[q]=float(np.quantile(trainvals,q))
        candidates={};diagnostics={}
        for lookback in BREAKOUT_LOOKBACKS:
            for q in COMPRESSION_QUANTILES:
                for rr in REWARD_RISKS:
                    name=f"B{lookback:02d}_Q{int(q*100):02d}_RR{rr:.1f}"
                    candidates[name],diagnostics[name]=simulate(bid,ask,feats,lookback,q,thresholds[q],rr)
        validation={};ranks=[]
        for name,recs in candidates.items():
            m=metrics(recs,VALID_START,VALID_END,1.0);validation[name]=m
            if m["trades"]>=MIN_VALIDATION_TRADES:
                score=float(m["PF"]) if isinstance(m["PF"],(int,float)) and np.isfinite(m["PF"]) else (-1.0 if m["PF"] is None else 999.0)
                ranks.append((score,m["mean_net_pips_per_trade"] or -999.0,m["trades"],name))
        if not ranks:raise RuntimeError("No candidate reached the 50-trade validation minimum")
        ranks.sort(reverse=True);selected=ranks[0][3]; records=candidates[selected]
        pd.DataFrame([{**t,**{f"net_pips_cost_{c:.1f}":t["gross_pips"]-c for c in EXTRA_COSTS}} for t in records]).to_csv(trades_path,index=False)
        periods={"discovery_2017_2020":(TRAIN_START,TRAIN_END),"validation_2021":(VALID_START,VALID_END),
            "forward_2022_2025":(FORWARD_START,FORWARD_END),"oos_2026":(OOS_START,OOS_END)}
        period_metrics={name:{str(c):metrics(records,a,b,c) for c in EXTRA_COSTS} for name,(a,b) in periods.items()}
        annual=[]
        for year in range(2017,2027):
            a,b=pd.Timestamp(f"{year}-01-01",tz="UTC"),pd.Timestamp(f"{year+1}-01-01",tz="UTC")
            annual.append({"year":year,**{f"PF_cost_{c:.1f}":metrics(records,a,b,c)["PF"] for c in EXTRA_COSTS},
                **{f"trades_cost_{c:.1f}":metrics(records,a,b,c)["trades"] for c in EXTRA_COSTS},
                **{f"mean_pips_cost_{c:.1f}":metrics(records,a,b,c)["mean_net_pips_per_trade"] for c in EXTRA_COSTS}})
        pd.DataFrame(annual).to_csv(annual_path,index=False)
        boot=bootstrap_forward(records,1.0)
        fyears=[x for x in annual if 2022<=x["year"]<=2025 and x["trades_cost_1.0"]>=20]
        disc=period_metrics["discovery_2017_2020"]["1.0"]; val=period_metrics["validation_2021"]["1.0"]
        f1=period_metrics["forward_2022_2025"]["1.0"]; f2=period_metrics["forward_2022_2025"]["2.0"]; oos=period_metrics["oos_2026"]["1.0"]
        gates={"validation_min_50_trades":val["trades"]>=MIN_VALIDATION_TRADES,"validation_PF_at_1pip_ge_1.05":safe_ge(val["PF"],1.05),
            "discovery_min_100_trades":disc["trades"]>=100,"discovery_PF_at_1pip_ge_1.00":safe_ge(disc["PF"],1.0),
            "forward_min_100_trades":f1["trades"]>=100,"forward_PF_at_1pip_ge_1.10":safe_ge(f1["PF"],1.10),
            "forward_PF_at_2pip_ge_1.05":safe_ge(f2["PF"],1.05),"forward_frequency_ge_2_trades_per_week":safe_ge(f1["trades_per_week"],2.0),
            "each_forward_year_with_20plus_trades_PF_ge_1_at_1pip":bool(fyears) and all(safe_ge(x["PF_cost_1.0"],1.0) for x in fyears),
            "forward_4week_block_bootstrap_positive_95pct":bool(boot["ci95_mean_pips"] and boot["ci95_mean_pips"][0]>0 and boot["p_mean_positive"]>=.95),
            "oos_min_30_trades":oos["trades"]>=30,"oos_PF_at_1pip_ge_1.00":safe_ge(oos["PF"],1.0)}
        report.update({"status":"COMPLETE","data":{"eurusd_bid":bdiag,"eurusd_ask":adiag,"common_hourly_rows":int(len(common)),
            "common_start_utc":common[0].isoformat(),"common_end_utc":common[-1].isoformat(),"compression_training_observations":len(trainvals),
            "compression_thresholds_price":{str(k):v for k,v in thresholds.items()},"no_missing_bars_synthesized":True},
            "candidate_validation_cost_1pip":validation,"selected_candidate":selected,"candidate_diagnostics":diagnostics,
            "selected_metrics_by_period_and_cost":period_metrics,"annual_cohorts":annual,"forward_block_bootstrap_cost_1pip":boot,
            "acceptance_gates":gates,"verdict":"LULUS" if all(gates.values()) else "GAGAL",
            "verdict_rule":"Every discovery, validation, forward cost, annual stability, bootstrap, frequency, and 2026 OOS gate must pass.",
            "trade_ledger_sha256":hashlib.sha256(trades_path.read_bytes()).hexdigest(),
            "limitations":["H1 quote-side OHLC execution may differ from the exact funded broker feed.","Additional costs are stress assumptions, not verified commission/slippage.","This is an alpha test, not a full funded-rule compliance simulation."]})
    except Exception as exc:
        report.update({"status":"FAILED_RUN","verdict":"GAGAL","error":f"{type(exc).__name__}: {exc}","decision":"No partial PF is accepted when the locked test pipeline fails."})
    report_path.write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(json.dumps({"status":report["status"],"verdict":report["verdict"],"selected":report.get("selected_candidate"),
        "metrics":report.get("selected_metrics_by_period_and_cost"),"gates":report.get("acceptance_gates"),"error":report.get("error")},indent=2))
    if report["status"]!="COMPLETE":raise SystemExit(1)


if __name__=="__main__":main()
