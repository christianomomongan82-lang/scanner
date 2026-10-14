#!/usr/bin/env python3
"""R258: locked EURUSD multi-horizon momentum with bid/ask execution.
One hypothesis, no parameter search. All signal features use completed hourly bars.
"""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
from research.r251_fx_cross_pair import DATA, download_pair, parse_bars

OUT=Path("research")
PIP=0.0001
TRAIN_END=pd.Timestamp("2021-01-01",tz="UTC")
VALID_END=pd.Timestamp("2022-01-01",tz="UTC")
FORWARD_END=pd.Timestamp("2026-01-01",tz="UTC")
COSTS=(0.0,0.5,1.0,2.0)
CFG={
 "id":"R258_EURUSD_24H_120H_ALIGNED_MOMENTUM_Q65_RISK_HALF_24H_RANGE_RR2_HOLD24",
 "signal":"24-hour return magnitude above the 2017-2020 training-only 65th percentile, aligned with the 120-hour return sign",
 "threshold_quantile":0.65,"fast_horizon_hours":24,"slow_horizon_hours":120,
 "threshold_training_period":["2017-01-01","2021-01-01"],
 "entry":"next exact H1 open after completed signal H1 bar",
 "stop":"0.5 times the prior 24-bar high-low range, known at signal close",
 "target":"2R from executable-side entry",
 "max_holding_hours":24,"overlap":"one open position; no signal accepted before prior trade exit",
 "execution":"actual EURUSD ASK entry/BID exit for longs and BID entry/ASK exit for shorts; stop first on same-bar collisions; stop-gap fills use available executable open",
 "cost_stress_extra_pips_on_top_of_observed_quote_side_costs":list(COSTS),
 "no_missing_bar_fill":True
}
def pf(values):
 x=np.asarray(values,dtype=float)
 gp=float(x[x>0].sum()); gl=float(-x[x<0].sum())
 if gl<=0: return None
 return gp/gl
def safe_float(x):
 return float(x) if x is not None and np.isfinite(x) else None
def metrics(records,start,end,cost):
 a=[r for r in records if start<=pd.Timestamp(r["entry_utc"])<end]
 vals=np.array([r["gross_pips"]-cost for r in a],dtype=float)
 weeks=max((end-start).total_seconds()/(7*86400),1/7)
 return {"trades":len(a),"PF":safe_float(pf(vals)),"net_pips":float(vals.sum()) if len(vals) else 0.0,
         "mean_net_pips_per_trade":float(vals.mean()) if len(vals) else None,
         "win_rate":float(np.mean(vals>0)) if len(vals) else None,
         "trades_per_week":float(len(a)/weeks)}
def bootstrap(records,cost=1.0,draws=2000,seed=258):
 start=pd.Timestamp("2022-01-01",tz="UTC"); end=pd.Timestamp("2026-01-01",tz="UTC")
 weeks=pd.date_range(start=start.floor("D"),end=end,freq="W-MON")
 weekly=[]
 for a,b in zip(weeks[:-1],weeks[1:]):
  v=[r["gross_pips"]-cost for r in records if a<=pd.Timestamp(r["entry_utc"])<b]
  weekly.append(np.asarray(v,dtype=float))
 if sum(len(x) for x in weekly)<100:
  return {"draws":0,"p_mean_positive":None,"ci95_mean_pips":None}
 rng=np.random.default_rng(seed); estimates=[]; n=len(weekly); block=4
 for _ in range(draws):
  chosen=[]
  while len(chosen)<n:
   j=int(rng.integers(0,n))
   chosen.extend(weekly[(j+k)%n] for k in range(block))
  seq=[v for chunk in chosen[:n] for v in chunk]
  if seq: estimates.append(float(np.mean(seq)))
 arr=np.asarray(estimates)
 return {"draws":len(arr),"p_mean_positive":float(np.mean(arr>0)),
         "ci95_mean_pips":[float(np.quantile(arr,.025)),float(np.quantile(arr,.975))]}
def phase_replay(records,cost,risk_pct):
 bal=6000.0; phase=1; days=set(); daily_date=None; daily_start=bal; daily_pnl=0.0
 mll=5400.0; p1=p2=None; processed=0; reason=None
 for r in records:
  if not ("2026-01-01"<=r["entry_utc"][:10]<"2027-01-01"): continue
  net=r["gross_pips"]-cost
  risk_pips=r["stop_pips"]
  if risk_pips<=0: continue
  pnl=bal*(risk_pct/100.0)*(net/risk_pips)
  exit_day=r["exit_utc"][:10]
  if exit_day!=daily_date:
   daily_date=exit_day; daily_start=bal; daily_pnl=0.0
  bal+=pnl; daily_pnl+=pnl; days.add(r["entry_utc"][:10]); processed+=1
  if bal<=mll:
   reason="STATIC_MLL"; break
  if daily_pnl<=-0.05*daily_start:
   reason="CLOSED_PNL_DLL_PROXY"; break
  target=6480.0 if phase==1 else 6300.0
  if bal>=target and len(days)>=5:
   if phase==1:
    p1=exit_day; phase=2; bal=6000.0; mll=5400.0
    days=set(); daily_date=None; daily_start=bal; daily_pnl=0.0
   else:
    p2=exit_day
    return {"risk_pct":risk_pct,"result":"BOTH_PHASES_REACHED_SIMPLIFIED_REPLAY",
            "phase1_date":p1,"phase2_date":p2,"trades_processed":processed}
 return {"risk_pct":risk_pct,"result":"FAILED_TO_PASS_IN_2026_OOS",
         "phase1_date":p1,"phase2_date":p2,"trades_processed":processed,
         "ending_phase":phase,"ending_balance":round(bal,2),"reason":reason}
def main():
 OUT.mkdir(parents=True,exist_ok=True)
 report={"status":"STARTED","strategy":"R258 EURUSD aligned 24h/120h multi-horizon momentum",
         "verdict":"GAGAL","locked_rule":CFG}
 try:
  paths={side:download_pair("eurusd",side)[0] for side in ("bid","ask")}
  bid,bd= parse_bars(paths["bid"]); ask,ad=parse_bars(paths["ask"])
  common=bid.index.intersection(ask.index).sort_values()
  if len(common)<30000: raise ValueError(f"insufficient bid/ask overlap {len(common)}")
  start=common.min().floor("h"); end=common.max().floor("h")
  ix=pd.date_range(start=start,end=end,freq="h")
  b=bid.reindex(ix); a=ask.reindex(ix)
  valid=(b[["Open","High","Low","Close"]].notna().all(axis=1)&a[["Open","High","Low","Close"]].notna().all(axis=1))
  invalid_open_spread=int(((a.Open<b.Open)&valid).sum())
  if invalid_open_spread: raise ValueError(f"negative executable open spreads found: {invalid_open_spread}")
  close=b.Close
  ret24=close/close.shift(24)-1.0
  ret120=close/close.shift(120)-1.0
  contiguous_120=valid.astype(int).rolling(121,min_periods=121).sum().eq(121)
  eligible=contiguous_120 & ret24.notna() & ret120.notna()
  train=eligible & (ix<TRAIN_END)
  threshold=float(ret24.loc[train].abs().quantile(CFG["threshold_quantile"]))
  ranges=(b.High.rolling(24,min_periods=24).max()-b.Low.rolling(24,min_periods=24).min())
  direction=np.zeros(len(ix),dtype=np.int8)
  long=(ret24>=threshold)&(ret120>0)&eligible
  short=(ret24<=-threshold)&(ret120<0)&eligible
  direction[long.to_numpy()]=1; direction[short.to_numpy()]=-1
  records=[]; skipped={"invalid_signal_window":0,"missing_execution_grid":0,"overlap":0,"invalid_stop":0}
  last_exit_idx=-1
  bid_arr={c:b[c].to_numpy(float) for c in ("Open","High","Low","Close")}
  ask_arr={c:a[c].to_numpy(float) for c in ("Open","High","Low","Close")}
  valid_arr=valid.to_numpy(bool); range_arr=ranges.to_numpy(float)
  times=ix
  for sig_i in np.flatnonzero(direction):
   entry_i=sig_i+1
   if entry_i>=len(ix): continue
   if entry_i<last_exit_idx:
    skipped["overlap"]+=1; continue
   exit_i=entry_i+24
   if exit_i>=len(ix) or not valid_arr[entry_i:exit_i+1].all() or not np.all(np.diff(times[entry_i:exit_i+1].asi8)==pd.Timedelta(hours=1).value):
    skipped["missing_execution_grid"]+=1; continue
   d=int(direction[sig_i]); dist=0.5*range_arr[sig_i]
   if not np.isfinite(dist) or dist<3*PIP:
    skipped["invalid_stop"]+=1; continue
   if d==1:
    ep=ask_arr["Open"][entry_i]; sl=ep-dist; tp=ep+2*dist
   else:
    ep=bid_arr["Open"][entry_i]; sl=ep+dist; tp=ep-2*dist
   exitp=None; reason=None; actual_exit_i=None
   for j in range(entry_i,exit_i):
    if d==1:
     op,hi,lo=bid_arr["Open"][j],bid_arr["High"][j],bid_arr["Low"][j]
     if op<=sl: exitp=op; reason="STOP_GAP"; actual_exit_i=j; break
     if lo<=sl: exitp=sl; reason="STOP"; actual_exit_i=j; break
     if hi>=tp: exitp=tp; reason="TARGET"; actual_exit_i=j; break
    else:
     op,hi,lo=ask_arr["Open"][j],ask_arr["High"][j],ask_arr["Low"][j]
     if op>=sl: exitp=op; reason="STOP_GAP"; actual_exit_i=j; break
     if hi>=sl: exitp=sl; reason="STOP"; actual_exit_i=j; break
     if lo<=tp: exitp=tp; reason="TARGET"; actual_exit_i=j; break
   if exitp is None:
    actual_exit_i=exit_i
    exitp=bid_arr["Open"][exit_i] if d==1 else ask_arr["Open"][exit_i]
    reason="TIME"
   gross=(exitp-ep)/PIP*d
   records.append({"signal_utc":times[sig_i].isoformat(),"entry_utc":times[entry_i].isoformat(),
    "exit_utc":times[actual_exit_i].isoformat(),"direction":"LONG" if d==1 else "SHORT",
    "entry_price":float(ep),"exit_price":float(exitp),"stop_pips":float(dist/PIP),
    "gross_pips":float(gross),"gross_R":float(gross/(dist/PIP)),"exit_reason":reason})
   last_exit_idx=actual_exit_i
  report["data"]={"instrument":"EURUSD","source":"Dukascopy H1 BID/ASK","common_quote_rows":int(len(common)),
   "grid_hours":int(len(ix)),"valid_common_hours":int(valid.sum()),"missing_or_incomplete_hours":int((~valid).sum()),
   "negative_open_spread_rows":invalid_open_spread,"bid_diagnostics":bd,"ask_diagnostics":ad,
   "start_utc":common.min().isoformat(),"end_utc":common.max().isoformat(),
   "threshold_abs_24h_return_fitted_only_on_2017_2020":threshold,
   "training_feature_observations":int(train.sum()),"download_requests":[]}
  report["diagnostics"]={"signals":int(np.count_nonzero(direction)),**{k:int(v) for k,v in skipped.items()},
   "completed_trades":len(records),"exit_counts":{k:sum(r["exit_reason"]==k for r in records) for k in ("STOP_GAP","STOP","TARGET","TIME")}}
  df=pd.DataFrame(records)
  periods=[("discovery",pd.Timestamp("2017-01-01",tz="UTC"),TRAIN_END),
   ("validation_2021",TRAIN_END,VALID_END),("forward",VALID_END,FORWARD_END),
   ("oos2026",FORWARD_END,ix[-1]+pd.Timedelta(hours=1))]
  report["periods"]={}
  for name,s,e in periods:
   report["periods"][name]={str(cost):metrics(records,s,e,cost) for cost in COSTS}
  report["forward_annual"]={}
  for y in range(2022,2026):
   s=pd.Timestamp(f"{y}-01-01",tz="UTC"); e=pd.Timestamp(f"{y+1}-01-01",tz="UTC")
   report["forward_annual"][str(y)]={str(cost):metrics(records,s,e,cost) for cost in COSTS}
  report["forward_bootstrap_extra_cost_1pip"]=bootstrap(records,1.0)
  report["challenge_replay_2026_oos"]=[phase_replay(records,1.0,r) for r in (0.25,0.5,0.75,1.0)]
  d=report["periods"]["discovery"]["1.0"]; v=report["periods"]["validation_2021"]["1.0"]
  f1=report["periods"]["forward"]["1.0"]; f2=report["periods"]["forward"]["2.0"]
  o=report["periods"]["oos2026"]["1.0"]; boot=report["forward_bootstrap_extra_cost_1pip"]
  annual_qual=[report["forward_annual"][str(y)]["1.0"] for y in range(2022,2026)
               if report["forward_annual"][str(y)]["1.0"]["trades"]>=20]
  annual_ok=bool(annual_qual) and all(m["PF"] is not None and m["PF"]>=1.0 for m in annual_qual)
  challenge_ok=any(x["result"]=="BOTH_PHASES_REACHED_SIMPLIFIED_REPLAY" for x in report["challenge_replay_2026_oos"])
  report["acceptance_gates"]={
   "discovery_at_least_100_trades_and_PF_1pip_ge_1.00":bool(d["trades"]>=100 and d["PF"] is not None and d["PF"]>=1.00),
   "validation_2021_at_least_30_trades_and_PF_1pip_ge_1.00":bool(v["trades"]>=30 and v["PF"] is not None and v["PF"]>=1.00),
   "forward_at_least_100_trades":bool(f1["trades"]>=100),
   "forward_PF_1pip_ge_1.10":bool(f1["PF"] is not None and f1["PF"]>=1.10),
   "forward_PF_2pip_ge_1.05":bool(f2["PF"] is not None and f2["PF"]>=1.05),
   "forward_trade_frequency_ge_2_per_week":bool(f1["trades_per_week"]>=2.0),
   "all_qualifying_forward_years_PF_1pip_ge_1":annual_ok,
   "4week_bootstrap_positive_expectancy_prob_ge_0.95":bool(boot["p_mean_positive"] is not None and boot["p_mean_positive"]>=0.95 and boot["ci95_mean_pips"] and boot["ci95_mean_pips"][0]>0),
   "oos_at_least_30_trades_and_PF_1pip_ge_1.00":bool(o["trades"]>=30 and o["PF"] is not None and o["PF"]>=1.00),
   "challenge_replay_reaches_both_phases_in_2026_OOS":challenge_ok
  }
  report["verdict"]="LULUS" if all(report["acceptance_gates"].values()) else "GAGAL"
  report["status"]="COMPLETED"
  (OUT/"R258_multihorizon_momentum_results.json").write_text(json.dumps(report,indent=2,allow_nan=False))
  df.to_csv(OUT/"R258_multihorizon_momentum_trades.csv",index=False)
  annual_rows=[]
  for y,period in report["forward_annual"].items():
   for cost,met in period.items(): annual_rows.append({"year":y,"extra_cost_pips":cost,**met})
  pd.DataFrame(annual_rows).to_csv(OUT/"R258_multihorizon_momentum_annual.csv",index=False)
  print(json.dumps(report,indent=2,allow_nan=False))
  print("R258 FINAL VERDICT:",report["verdict"])
 except Exception as exc:
  report.update({"status":"FAILED_RUN","verdict":"GAGAL","error":f"{type(exc).__name__}: {exc}"})
  (OUT/"R258_multihorizon_momentum_results.json").write_text(json.dumps(report,indent=2,allow_nan=False))
  raise
if __name__=="__main__": main()
