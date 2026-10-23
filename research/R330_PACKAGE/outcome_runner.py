#!/usr/bin/env python3
"""R330 locked local outcome runner. Refuses to calculate PnL without a frozen preflight PASS."""
import argparse, gzip, hashlib, json, platform
from pathlib import Path
import numpy as np
import pandas as pd

PAIRS = ["audusd","eurusd","gbpusd","nzdusd","usdcad","usdchf","usdjpy"]
HORIZONS = [13,26,39]
SLIPS = [0.0,0.5,1.0,2.0]
SWAPS = [2.0,4.0]
H1=3_600_000
WEEK=168*H1
LOAD=np.array([-1,-1,-1,-1,1,1,1],float)
PAIR_STRENGTH_SIGN=np.array([1,1,1,1,-1,-1,-1],float)
CURRENCY_CODES=["AUD","EUR","GBP","NZD","CAD","CHF","JPY"]
PERIODS={
 "discovery":(pd.Timestamp("2017-01-01T00:00:00Z"),pd.Timestamp("2021-01-01T00:00:00Z")),
 "confirmation":(pd.Timestamp("2021-01-01T00:00:00Z"),pd.Timestamp("2024-01-01T00:00:00Z")),
 "diagnostic":(pd.Timestamp("2024-01-01T00:00:00Z"),pd.Timestamp("2026-01-01T00:00:00Z"))}

def digest(p):
 h=hashlib.sha256()
 with open(p,"rb") as f:
  for b in iter(lambda:f.read(1<<20),b""): h.update(b)
 return h.hexdigest()

def jwrite(p,obj):
 Path(p).write_text(json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")

def csvwrite(df,p,compressed=False):
 if compressed:
  with open(p,"wb") as raw:
   with gzip.GzipFile(filename="",mode="wb",fileobj=raw,compresslevel=9,mtime=0) as gz:
    gz.write(df.to_csv(index=False,float_format="%.12g",lineterminator="\n").encode())
 else:
  df.to_csv(p,index=False,float_format="%.12g",lineterminator="\n")

def weight(signal,vol):
 strength=np.asarray(signal,float)*PAIR_STRENGTH_SIGN
 if (not np.isfinite(strength).all()) or float(np.ptp(strength))<1e-12:
  return np.zeros(7,float)
 top=sorted(range(7),key=lambda i:(-strength[i],CURRENCY_CODES[i]))[:2]
 bottom=sorted(range(7),key=lambda i:(strength[i],CURRENCY_CODES[i]))[:2]
 raw=np.zeros(7,float)
 for i in top: raw[i]=0.25*PAIR_STRENGTH_SIGN[i]
 for i in bottom: raw[i]=-0.25*PAIR_STRENGTH_SIGN[i]
 return raw

def block_boot(x, reps, rng):
 x=np.asarray(x,float); n=len(x); k=(n+3)//4; out=np.empty(reps)
 starts=rng.integers(0,n,size=(reps,k))
 idx=(starts[:,:,None]+np.arange(4)[None,None,:])%n
 idx=idx.reshape(reps,-1)[:,:n]
 return x[idx].mean(axis=1)

def run(data,manifest_path,preflight_path,out,reps=10000):
 pre=json.loads(Path(preflight_path).read_text())
 if pre.get("data_gate")!="PASS" or pre.get("candidate_sample_gates_pass") is not True or pre.get("outcomes_computed") is not False:
  raise ValueError("No PnL: candidate-specific preflight must explicitly PASS before outcomes")
 if {int(x["horizon_weeks"]) for x in pre["horizons"]}!=set(HORIZONS) or not all(x["sample_gate_pass"] for x in pre["horizons"]):
  raise ValueError("No PnL: preflight does not cover the exact frozen candidate grid")
 manifest=json.loads(Path(manifest_path).read_text())
 if manifest.get("combined_ordered_stream_manifest_sha256")!="2db7c7d88b2f31965ff956dd5e017ce7f0b76a4ac1792dca4896833b884e85e0":
  raise ValueError("Source manifest identity mismatch")
 expected={x["name"]:x for x in manifest["streams"]}
 dfs={}; audit=[]
 for pair in PAIRS:
  side={}
  for s in ["bid","ask"]:
   name=f"{pair}_h1_{s}.csv"; path=Path(data)/name; got=digest(path); exp=expected[name]
   if got!=exp["sha256"] or path.stat().st_size!=exp["bytes"]: raise ValueError(f"Source hash mismatch: {name}")
   d=pd.read_csv(path); ts=pd.to_numeric(d.timestamp,errors="raise").astype("int64")
   if ts.duplicated().any() or not ts.is_monotonic_increasing or (ts%H1).any(): raise ValueError(f"Timestamp integrity failure: {name}")
   v=d[["open","high","low","close"]].to_numpy(float)
   bad=(d.high<d.low)|(d.high<d[["open","close"]].max(axis=1))|(d.low>d[["open","close"]].min(axis=1))
   if not np.isfinite(v).all() or bad.any(): raise ValueError(f"OHLC integrity failure: {name}")
   d["timestamp"]=ts; side[s]=d
  b,a=side["bid"],side["ask"]
  if not np.array_equal(b.timestamp.to_numpy(),a.timestamp.to_numpy()): raise ValueError(f"BID/ASK timestamp mismatch {pair}")
  m=b.merge(a,on="timestamp",suffixes=("_b","_a"),validate="one_to_one").sort_values("timestamp")
  for q in ("open","close"):
   if (m[f"{q}_a"]<m[f"{q}_b"]).any(): raise ValueError(f"Negative spread {pair}")
  m["active"]=(m.high_b>m.low_b)|(m.high_a>m.low_a)|(m.open_b!=m.close_b)|(m.open_a!=m.close_a)
  m["mid"]=(m.close_b+m.close_a)/2
  dfs[pair]=m.set_index("timestamp",drop=False)
  audit.append({"pair":pair,"rows":len(m),"active_rows":int(m.active.sum()),"flat_rows":int((~m.active).sum()),
                "bidask_exact":True,"sha_bid":digest(Path(data)/f"{pair}_h1_bid.csv"),"sha_ask":digest(Path(data)/f"{pair}_h1_ask.csv")})
 sets=[set(f.index.tolist()) for f in dfs.values()]; common=set.intersection(*sets)
 snaps=[]; prices=[]
 active={}; mid={}; rows={}
 for p,f in dfs.items():
  active[p]=dict(zip(f.timestamp.astype(int),f.active.astype(bool)))
  mid[p]=dict(zip(f.timestamp.astype(int),f.mid.astype(float)))
  rows[p]={int(r.timestamp):r for r in f.itertuples(index=False)}
 for t in sorted(common):
  dt=pd.to_datetime(t,unit="ms",utc=True)
  if dt.weekday()==1 and dt.hour==10 and dt.minute==0 and all(active[p].get(t,False) for p in PAIRS):
   px=np.array([mid[p][t] for p in PAIRS])
   if np.isfinite(px).all() and (px>0).all(): snaps.append(int(t)); prices.append(px)
 prices=np.asarray(prices,float); snapidx={t:i for i,t in enumerate(snaps)}
 sched=pd.date_range("2017-01-03","2025-12-30",freq="W-TUE",tz="UTC")
 weeks=[]; legs=[]
 for h in HORIZONS:
  for day in sched:
   t=int(day.timestamp()*1000)+10*H1; dt=pd.to_datetime(t,unit="ms",utc=True)
   period=next((k for k,(lo,hi) in PERIODS.items() if lo<=dt<hi),"excluded")
   rec={"horizon_weeks":h,"signal_timestamp_utc":dt.isoformat(),"period":period,"eligible":False,"reason":"","leg_count":0}
   en=t+2*H1; ex=en+WEEK
   if period=="excluded": rec["reason"]="outside_period"
   elif t not in snapidx: rec["reason"]="signal_not_active_or_missing"
   elif snapidx[t]<h or snapidx[t]<13: rec["reason"]="insufficient_history"
   elif en not in common or ex not in common: rec["reason"]="entry_exit_missing"
   elif not all(active[p].get(en,False) and active[p].get(ex,False) for p in PAIRS): rec["reason"]="entry_exit_inactive"
   elif pd.to_datetime(ex,unit="ms",utc=True)>=PERIODS[period][1]: rec["reason"]="exit_crosses_period_boundary"
   else:
    j=snapidx[t]; signal=np.log(prices[j])-np.log(prices[j-h])
    vol=np.std(np.diff(np.log(prices[j-13:j+1]),axis=0),axis=0,ddof=1)
    if not np.isfinite(vol).all() or (vol<=0).any(): rec["reason"]="invalid_volatility"
    else:
     w=weight(signal,vol); ids=np.where(np.abs(w)>1e-12)[0]
     if not len(ids): rec["reason"]="flat_after_caps"
     else:
      rec["eligible"]=True; rec["reason"]="eligible"; rec["leg_count"]=len(ids)
      for sl in SLIPS:
       for sw in SWAPS: rec[f"R_slip{sl:g}_swap{sw:g}"]=0.0
      for i in ids:
       p=PAIRS[i]; sign=1 if w[i]>0 else -1; ps=.01 if p=="usdjpy" else .0001
       e=rows[p][en]; x=rows[p][ex]
       eb,ea,xb,xa=map(float,[e.open_b,e.open_a,x.open_b,x.open_a]); em=(eb+ea)/2
       exret=float(np.log(xb/ea) if sign>0 else np.log(eb/xa))
       pipvalue=10.0 if p.endswith("usd") else 100000*ps/em
       comm=10.0/pipvalue
       lr={"horizon_weeks":h,"period":period,"entry_timestamp_utc":pd.to_datetime(en,unit="ms",utc=True).isoformat(),
           "exit_timestamp_utc":pd.to_datetime(ex,unit="ms",utc=True).isoformat(),"pair":p,"direction":"LONG" if sign>0 else "SHORT",
           "weight":float(w[i]),"vol13_log":float(vol[i]),"signal_log_return":float(signal[i]),
           "entry_bid":eb,"entry_ask":ea,"exit_bid":xb,"exit_ask":xa,"commission_pips_per_stdlot":comm,
           "executable_log_return_before_incremental_cost":exret}
       for sl in SLIPS:
        for sw in SWAPS:
         rr=abs(w[i])*(exret-(comm+sl+sw)*ps/em)/vol[i]
         rec[f"R_slip{sl:g}_swap{sw:g}"]+=float(rr); lr[f"net_R_slip{sl:g}_swap{sw:g}"]=float(rr)
       legs.append(lr)
   for sl in SLIPS:
    for sw in SWAPS: rec.setdefault(f"R_slip{sl:g}_swap{sw:g}",0.0)
   weeks.append(rec)
 W=pd.DataFrame(weeks)
 for sl in SLIPS:
  for sw in SWAPS: W[f"R_slip{sl:g}_swap{sw:g}"]=pd.to_numeric(W[f"R_slip{sl:g}_swap{sw:g}"],errors="coerce").fillna(0)
 L=pd.DataFrame(legs)
 W["entry_date"]=pd.to_datetime(W.signal_timestamp_utc,utc=True).dt.date.astype(str)
 grid=[]
 for h in HORIZONS:
  for per in PERIODS:
   base=W[(W.horizon_weeks==h)&(W.period==per)]
   for sl in SLIPS:
    for sw in SWAPS:
     x=base[f"R_slip{sl:g}_swap{sw:g}"].to_numpy(float); win=x[x>0].sum(); loss=-x[x<0].sum()
     curve=np.r_[0,np.cumsum(x)]
     grid.append({"horizon_weeks":h,"period":per,"slippage_pips":sl,"swap_pips_per_week":sw,"weeks":len(x),
       "active_weeks":int((base.leg_count>0).sum()),"active_legs":int(base.leg_count.sum()),"net_R":float(x.sum()),
       "mean_weekly_R":float(x.mean()),"PF_R":float(win/loss) if loss else (float("inf") if win else 0.),
       "max_closed_weekly_R_drawdown":float(np.max(np.maximum.accumulate(curve)-curve)),"positive_weeks":int((x>0).sum()),"negative_weeks":int((x<0).sum())})
 G=pd.DataFrame(grid)
 rng=np.random.default_rng(329); scores=[]; boot={}
 for h in HORIZONS:
  for per in ["discovery","confirmation"]:
   b=W[(W.horizon_weeks==h)&(W.period==per)]; x=b["R_slip1_swap2"].to_numpy(float)
   bs=block_boot(x,reps,rng); null=block_boot(x-x.mean(),reps,rng)
   low=float(np.percentile(bs,5)); pv=float((1+(null>=x.mean()).sum())/(reps+1))
   win=x[x>0].sum(); loss=-x[x<0].sum()
   row={"horizon_weeks":h,"period":per,"weeks":len(x),"active_weeks":int((b.leg_count>0).sum()),"active_legs":int(b.leg_count.sum()),
        "net_R":float(x.sum()),"mean_weekly_R":float(x.mean()),"PF_R":float(win/loss) if loss else 0.,
        "max_drawdown_R":float(np.max(np.maximum.accumulate(np.r_[0,np.cumsum(x)])-np.r_[0,np.cumsum(x)])),
        "bootstrap_lower_95_mean_weekly_R":low,"bootstrap_p_one_sided":pv}
   scores.append(row); boot[(h,per)]={"lower":low,"p":pv}
 order=sorted((boot[(h,"discovery")]["p"],h) for h in HORIZONS); holm={}; running=0.
 for rank,(pval,h) in enumerate(order):
  running=max(running,min(1.,(len(order)-rank)*pval)); holm[h]=running
 for r in scores: r["holm_adjusted_discovery_p"]=holm[r["horizon_weeks"]]
 S=pd.DataFrame(scores)
 disc=S[S.period=="discovery"].sort_values(["mean_weekly_R","bootstrap_lower_95_mean_weekly_R","max_drawdown_R"],ascending=[False,False,True])
 chosen=int(disc.iloc[0].horizon_weeks)
 def gr(per,sl,sw): return G[(G.horizon_weeks==chosen)&(G.period==per)&(G.slippage_pips==sl)&(G.swap_pips_per_week==sw)].iloc[0]
 d,c=gr("discovery",1,2),gr("confirmation",1,2); ds,cs=gr("discovery",2,4),gr("confirmation",2,4)
 ann=[]
 for h in HORIZONS:
  for yr in range(2017,2026):
   z=W[(W.horizon_weeks==h)&(pd.to_datetime(W.signal_timestamp_utc,utc=True).dt.year==yr)&W.period.isin(PERIODS)]
   for sl,sw,label in [(1,2,"primary"),(2,4,"stress")]:
    x=z[f"R_slip{sl:g}_swap{sw:g}"].to_numpy(float)
    ann.append({"horizon_weeks":h,"year":yr,"cost_case":label,"weeks":len(x),"active_weeks":int((z.leg_count>0).sum()),"net_R":float(x.sum()),"mean_weekly_R":float(x.mean()) if len(x) else 0.})
 A=pd.DataFrame(ann); yy=A[(A.horizon_weeks==chosen)&(A.cost_case=="primary")&A.year.isin([2018,2019,2020])]
 pos=yy[yy.net_R>0]; posyears=len(pos); maxshare=float(pos.net_R.max()/pos.net_R.sum()) if len(pos) and pos.net_R.sum()>0 else 1.
 gates={
 "primary_discovery_net_R_positive":bool(d.net_R>0),"primary_discovery_PF_ge_1_05":bool(d.PF_R>=1.05),
 "primary_confirmation_net_R_positive":bool(c.net_R>0),"primary_confirmation_PF_ge_1_05":bool(c.PF_R>=1.05),
 "stress_discovery_net_R_positive":bool(ds.net_R>0),"stress_discovery_PF_ge_1_00":bool(ds.PF_R>=1.),
 "stress_confirmation_net_R_positive":bool(cs.net_R>0),"stress_confirmation_PF_ge_1_00":bool(cs.PF_R>=1.),
 "at_least_2_of_3_discovery_years_positive":bool(posyears>=2),"no_discovery_year_over_70pct_positive_net_R":bool(maxshare<=.70),
 "discovery_bootstrap_lower_gt_zero":bool(boot[(chosen,"discovery")]["lower"]>0),
 "confirmation_bootstrap_lower_gt_zero":bool(boot[(chosen,"confirmation")]["lower"]>0),
 "holm_adjusted_discovery_p_lt_0_05":bool(holm[chosen]<.05)}
 result={"experiment_id":"R330","verdict":"LULUS" if all(gates.values()) else "GAGAL","first_failed_gate":next((k for k,v in gates.items() if not v),None),
  "outcomes_computed":True,"pnl_computed":True,"selected_horizon_weeks":chosen,"data_gate":"PASS","candidate_specific_preflight_sha256":digest(Path(preflight_path)),
  "source_manifest_sha256":manifest["combined_ordered_stream_manifest_sha256"],"primary_cost":{"slippage_pips":1,"adverse_swap_pips_week":2,"commission_usd_round_trip_per_standard_lot":10},
  "stress_cost":{"slippage_pips":2,"adverse_swap_pips_week":4},"gate_values":gates,
  "discovery":{"net_R":float(d.net_R),"PF_R":float(d.PF_R),"bootstrap_lower":boot[(chosen,"discovery")]["lower"],"holm_adjusted_p":holm[chosen]},
  "confirmation":{"net_R":float(c.net_R),"PF_R":float(c.PF_R),"bootstrap_lower":boot[(chosen,"confirmation")]["lower"]},
  "stress_discovery":{"net_R":float(ds.net_R),"PF_R":float(ds.PF_R)},"stress_confirmation":{"net_R":float(cs.net_R),"PF_R":float(cs.PF_R)},
  "discovery_years_2018_2020":{"positive_years":int(posyears),"max_share_positive_net_R":maxshare},"bootstrap_replicates":reps,"bootstrap_method":"four-week circular block bootstrap; zero-trade weeks included; RNG seed 329; Holm step-down across three discovery horizons",
  "contamination":"2017-2025 previously inspected; not independent program-level OOS","challenge_replay":"NOT_RUN; required only if economic gates pass plus independent evidence and provider contract/swap verification"}
 out=Path(out); out.mkdir(parents=True,exist_ok=True)
 audit_report={"experiment_id":"R330","data_gate":"PASS","mode":"outcome source revalidation","streams":audit,"common_timestamps":len(common),"active_weekly_snapshots":len(snaps)}
 jwrite(out/"data_audit.json",audit_report)
 csvwrite(W,out/"weekly_all_configs.csv.gz",True);csvwrite(L,out/"all_leg_ledger.csv.gz",True);csvwrite(G.replace([np.inf,-np.inf],np.nan),out/"full_grid.csv.gz",True)
 csvwrite(S,out/"scorecard.csv");csvwrite(A,out/"annual_cohort.csv")
 csvwrite(L[L.horizon_weeks==chosen],out/"finalist_trade_ledger.csv.gz",True)
 csvwrite(W[["horizon_weeks","signal_timestamp_utc","period","leg_count","R_slip1_swap2"]].rename(columns={"R_slip1_swap2":"net_R"}),out/"weekly_net_r.csv")
 csvwrite(W[["horizon_weeks","signal_timestamp_utc","period","eligible","reason","leg_count"]],out/"eligibility_skip_audit.csv.gz",True)
 jwrite(out/"results.json",result)
 report=["# R330 economic screen",f"**Verdict: {result['verdict']}**",f"Selected H: {chosen} weeks",
   f"Discovery net R/PF: {d.net_R:.6f}/{d.PF_R:.6f}; bootstrap lower {boot[(chosen,'discovery')]['lower']:.8f}; Holm p {holm[chosen]:.6g}",
   f"Confirmation net R/PF: {c.net_R:.6f}/{c.PF_R:.6f}; bootstrap lower {boot[(chosen,'confirmation')]['lower']:.8f}",
   f"Stress discovery net R/PF: {ds.net_R:.6f}/{ds.PF_R:.6f}",f"Stress confirmation net R/PF: {cs.net_R:.6f}/{cs.PF_R:.6f}","",
   "## Gate details"]+[f"- {'PASS' if v else 'FAIL'}: {k}" for k,v in gates.items()]+["",
   "Historical 2017-2025 results are project-contaminated, H1 data support an exact one-hour proxy rather than measured five-minute fills, and swaps are proxy costs, not verified symbol swap quotes. No challenge replay or funded-ready claim is justified by this screen."]
 Path(out/"report.md").write_text("\n".join(report)+"\n")
 (out/"run.log").write_text(f"R330 run\nPython {platform.python_version()}\nNumPy {np.__version__}\npandas {pd.__version__}\nmanifest={manifest['combined_ordered_stream_manifest_sha256']}\npreflight_sha={digest(Path(preflight_path))}\nresult={result['verdict']}\n",encoding="utf-8")
 return result

def main():
 p=argparse.ArgumentParser();p.add_argument("--data-dir",required=True);p.add_argument("--manifest",required=True);p.add_argument("--preflight-summary",required=True);p.add_argument("--out-dir",required=True);p.add_argument("--bootstrap",type=int,default=10000)
 a=p.parse_args();print(json.dumps(run(a.data_dir,a.manifest,a.preflight_summary,a.out_dir,a.bootstrap),indent=2,sort_keys=True))
if __name__=="__main__": main()
