#!/usr/bin/env python3
"""R294 locked replay: symmetric long/short on extreme cross-index closing breadth."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

HASHES = {
 "usa500idxusd":"df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee",
 "usatechidxusd":"82b06c38f66cd1387097691baac1d45c9463b6540eea9dfe28a894d85e122f7c",
 "usa30idxusd":"8fcef9d76b31e99ae8d0175e769307ab13f930ae3ec2c17ef6baf0311ea1783a",
 "ussc2000idxusd":"c01c97d8705453d3fa3fd4ac1d386e9c1d72ab27e3b7d57d6cde53da9dfdf6f0"
}
COSTS=(1,2,4); NBOOT=5000; SEED=294; BLOCK=4; TZ="America/New_York"

def pf(x):
 a=np.asarray(x,float); gain=a[a>0].sum(); loss=-a[a<0].sum()
 return float(gain/loss) if loss>0 else (float("inf") if gain>0 else None)

def load(path,symbol):
 sha=hashlib.sha256(path.read_bytes()).hexdigest()
 if sha!=HASHES[symbol]: raise ValueError(f"SHA mismatch for {symbol}: {sha}")
 d=pd.read_csv(path,compression="gzip")
 if d.columns.tolist()!=["timestamp","open","high","low","close"] or d.timestamp.duplicated().any():
  raise ValueError(f"Unexpected schema/duplicate timestamps: {symbol}")
 d=d.sort_values("timestamp",kind="stable").reset_index(drop=True)
 d["flat"]=(d.open==d.high)&(d.high==d.low)&(d.low==d.close)&(d.close==d.close.shift(1))
 d=d[d.timestamp<int(pd.Timestamp("2022-01-02",tz="UTC").timestamp()*1000)].copy()
 d["dt"]=pd.to_datetime(d.timestamp,unit="ms",utc=True).dt.tz_convert(TZ)
 d["date"]=d.dt.dt.strftime("%Y-%m-%d"); d["minute"]=d.dt.dt.hour*60+d.dt.dt.minute
 cols=["open","high","low","close"]
 d["ohlc_ok"]=d[cols].notna().all(axis=1)&(d[cols]>0).all(axis=1)&(d.high>=d[["open","close","low"]].max(axis=1))&(d.low<=d[["open","close","high"]].min(axis=1))
 r=d[(d.dt.dt.dayofweek<5)&d.minute.between(570,955)].copy()
 expected=np.arange(570,956,5); sessions={}; audit=[]
 for day,g0 in r.groupby("date",sort=True):
  g=g0.sort_values("timestamp").reset_index(drop=True); why=[]
  if len(g)!=78: why.append("bar_count")
  elif not np.array_equal(g.minute.to_numpy(int),expected): why.append("timestamp_grid")
  if not g.ohlc_ok.all(): why.append("invalid_ohlc")
  if g.flat.any(): why.append("repeated_flat_placeholder")
  ok=not why
  audit.append({"symbol":symbol,"date":day,"bars":len(g),"flat_rows":int(g.flat.sum()),"invalid_ohlc_rows":int((~g.ohlc_ok).sum()),"valid":ok,"reason":"|".join(why)})
  if ok: sessions[day]=g
 meta={"symbol":symbol,"sha256":sha,"valid_sessions_through_2021":len(sessions),"rth_dates_audited":int(r.date.nunique())}
 return sessions,audit,meta

def dayret(g): return float(g.iloc[75].close/g.iloc[0].open-1.0)

def summaries(df):
 o={"trades":int(len(df))}
 for c in COSTS:
  a=df[f"net_bp_{c}"].to_numpy(float) if len(df) else np.array([])
  o[f"net_bp_{c}"]=float(a.sum()) if len(a) else 0.0; o[f"pf_{c}bp"]=pf(a) if len(a) else None
 if len(df):
  a=df.net_bp_2.to_numpy(float); cum=np.r_[0,np.cumsum(a)]/100; dd=cum-np.maximum.accumulate(cum)
  o.update(gross_bp=float(df.gross_bp.sum()),win_rate_2bp_pct=float((a>0).mean()*100),mean_net_bp_2=float(a.mean()),
           max_closed_pnl_drawdown_pct_fixed_notional_2bp=float(-min(0,float(dd.min()))),
           long_trades=int((df.side=="LONG").sum()),short_trades=int((df.side=="SHORT").sum()))
 else: o.update(gross_bp=0.,win_rate_2bp_pct=None,mean_net_bp_2=None,max_closed_pnl_drawdown_pct_fixed_notional_2bp=0.,long_trades=0,short_trades=0)
 return o

def bootstrap(df):
 weeks={x.strftime("%Y-%m-%d"):0.0 for x in pd.date_range("2021-01-04","2021-12-27",freq="W-MON")}
 counts={k:0 for k in weeks}
 for _,r in df.iterrows():
  dt=pd.Timestamp(r.exit_date); k=(dt-pd.Timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
  if k in weeks: weeks[k]+=float(r.net_bp_2); counts[k]+=1
 vals=np.array(list(weeks.values())); rng=np.random.default_rng(SEED); means=np.empty(NBOOT); n=len(vals)
 for b in range(NBOOT):
  ids=[]
  while len(ids)<n:
   s=int(rng.integers(0,n)); ids.extend(((s+np.arange(BLOCK))%n).tolist())
  means[b]=vals[np.asarray(ids[:n],int)].mean()
 q=np.quantile(means,[.025,.975])
 return {"weeks":n,"weeks_with_trades":sum(v>0 for v in counts.values()),"mean_weekly_bp":float(vals.mean()),
         "ci95_low":float(q[0]),"ci95_high":float(q[1]),"resamples":NBOOT,"block_weeks":BLOCK,"seed":SEED}

def main():
 ap=argparse.ArgumentParser(); ap.add_argument("--data-dir",type=Path,required=True); ap.add_argument("--out-dir",type=Path,default=Path("R294_outputs")); a=ap.parse_args(); a.out_dir.mkdir(parents=True,exist_ok=True)
 sessions={}; audits=[]; metas=[]
 for s in HASHES:
  sessions[s],au,meta=load(a.data_dir/f"{s}_m5.csv.gz",s); audits+=au; metas.append(meta)
 us=sessions["usa500idxusd"]; dates=sorted(x for x in us if "2017-01-01"<=x<="2021-12-31")
 child=[]; r293=[]; parent=[]; skipped=[]
 all_us_dates=sorted(us)
 for day in dates:
  nxts=[x for x in all_us_dates if x>day]
  if not nxts: continue
  nxt=nxts[0]
  if (pd.Timestamp(nxt)-pd.Timestamp(day)).days>7:
   skipped.append({"date":day,"next_usa500":nxt,"reason":"gap_over_7_days"}); continue
  split="discovery" if day<="2020-12-31" else "validation"; edge="2020-12-31" if split=="discovery" else "2021-12-31"
  if nxt>edge: skipped.append({"date":day,"next_usa500":nxt,"reason":"split_boundary"}); continue
  valid={s:d[day] for s,d in sessions.items() if day in d}
  if len(valid)<3 or "usa500idxusd" not in valid:
   skipped.append({"date":day,"next_usa500":nxt,"reason":"fewer_than_three_feeds"}); continue
  pos=sum(dayret(g)>0 for g in valid.values()); n=len(valid); frac=pos/n
  entry=float(us[day].iloc[77].open); exitp=float(us[nxt].iloc[0].open)
  base={"entry_date":day,"exit_date":nxt,"year":int(day[:4]),"valid_feeds":n,"positive_votes":pos,"positive_fraction":frac,
        "entry_ts_ny":us[day].iloc[77]["dt"].isoformat(),"exit_ts_ny":us[nxt].iloc[0]["dt"].isoformat(),"entry_bid":entry,"exit_bid":exitp}
  g_long=(exitp/entry-1)*10000
  p=dict(base,side="LONG",gross_bp=g_long)
  for c in COSTS:p[f"net_bp_{c}"]=g_long-c
  parent.append(p)
  if frac>=.75:r293.append(p.copy())
  side=1 if frac>=.75 else (-1 if frac<=.25 else 0)
  if not side:continue
  gross=side*(exitp/entry-1)*10000; z=dict(base,side="LONG" if side==1 else "SHORT",gross_bp=gross)
  for c in COSTS:z[f"net_bp_{c}"]=gross-c
  child.append(z)
 cdf=pd.DataFrame(child); rdf=pd.DataFrame(r293); pdf=pd.DataFrame(parent); sdf=pd.DataFrame(skipped)
 cdf.to_csv(a.out_dir/"R294_candidate_ledger.csv",index=False); rdf.to_csv(a.out_dir/"R294_r293_positive_tail_ledger.csv",index=False); pdf.to_csv(a.out_dir/"R294_unconditional_long_parent_ledger.csv",index=False)
 pd.DataFrame(audits).to_csv(a.out_dir/"R294_session_quality_audit.csv",index=False); sdf.to_csv(a.out_dir/"R294_skipped_dates.csv",index=False)
 result={"candidate_id":"R294_USA500_TWO_SIDED_BREADTH_OVERNIGHT","inputs":metas,"strategy_pnl_2022_plus_calculated":False,"audited_sessions":len(audits),"results":{}}
 for nm,lo,hi in [("discovery","2017-01-01","2020-12-31"),("validation","2021-01-01","2021-12-31")]:
  result["results"][nm]={}
  for label,df in [("candidate",cdf),("r293_positive_tail_long_only",rdf),("unconditional_long",pdf)]:
   sub=df[df.entry_date.between(lo,hi)]; result["results"][nm][label]=summaries(sub)
   if nm=="discovery" and label=="candidate": result["results"][nm]["annual_candidate"]={str(y):summaries(sub[sub.year==y]) for y in range(2017,2021)}
  if nm=="validation":result["results"][nm]["candidate_bootstrap"]=bootstrap(cdf[cdf.entry_date.between(lo,hi)])
 d=result["results"]["discovery"]; v=result["results"]["validation"]; an=d["annual_candidate"]; b=v["candidate_bootstrap"]; x=d["candidate"]; y=v["candidate"]
 gates={"discovery_min_200_trades":x["trades"]>=200,"discovery_net_bp_2_positive":x["net_bp_2"]>0,"discovery_pf_2bp_ge_1_05":x["pf_2bp"] is not None and x["pf_2bp"]>=1.05,
 "discovery_at_least_2_of_4_years_positive":sum(q["net_bp_2"]>0 for q in an.values())>=2,"discovery_pf_4bp_ge_0_90":x["pf_4bp"] is not None and x["pf_4bp"]>=.90,
 "validation_min_75_trades":y["trades"]>=75,"validation_net_bp_2_positive":y["net_bp_2"]>0,"validation_pf_2bp_ge_1_05":y["pf_2bp"] is not None and y["pf_2bp"]>=1.05,
 "validation_bootstrap_ci_lower_gt_zero":b["ci95_low"]>0,"validation_pf_4bp_ge_0_90":y["pf_4bp"] is not None and y["pf_4bp"]>=.90}
 result["gates"]=gates; result["verdict"]="LULUS_HISTORICAL_SCREEN_ONLY" if all(gates.values()) else "GAGAL"
 result["limitations"]=["M5 BID-only feeds cannot establish short ASK-side exit fills.","1/2/4bp costs are modeled, not verified broker/prop costs.","No swaps, margin, overnight floating equity or FundedNext challenge replay.","2017-2021 is research-contaminated; not pristine OOS.","No 2022+ strategy PnL calculated."]
 (a.out_dir/"R294_results_compact.json").write_text(json.dumps(result,indent=2,allow_nan=False))
 lines=["# R294 — USA500 Two-Sided Extreme-Breadth Overnight Direction",f"\n**Verdict: {result['verdict']}**\n","Rules preregistered before candidate outcomes. No 2022+ candidate PnL calculated.","\n| Metric | Discovery 2017–2020 | Validation 2021 |","|---|---:|---:|"]
 for k,label in [("trades","Trades"),("long_trades","Long trades"),("short_trades","Short trades"),("net_bp_2","Net bp @2bp"),("pf_2bp","PF @2bp"),("net_bp_4","Net bp @4bp"),("pf_4bp","PF @4bp"),("max_closed_pnl_drawdown_pct_fixed_notional_2bp","Max closed-PnL DD (% fixed notional)")]:
  lines.append(f"| {label} | {x.get(k)} | {y.get(k)} |")
 lines+=["\n## Matched controls at 2 bp\n","| Series | Period | Trades | Net bp | PF |","|---|---|---:|---:|---:|"]
 for period in ["discovery","validation"]:
  for series,label in [("r293_positive_tail_long_only","R293 positive-tail long-only"),("unconditional_long","Unconditional long")]:
   q=result["results"][period][series]; lines.append(f"| {label} | {period} | {q['trades']} | {q['net_bp_2']:.2f} | {q['pf_2bp']:.3f} |")
 lines+=["\n## Annual discovery @2bp\n","| Year | Trades | Long | Short | Net bp | PF |","|---|---:|---:|---:|---:|---:|"]
 for year,q in an.items():lines.append(f"| {year} | {q['trades']} | {q['long_trades']} | {q['short_trades']} | {q['net_bp_2']:.2f} | {q['pf_2bp']:.3f} |")
 lines += [f"\n## Validation bootstrap\n\nMean {b['mean_weekly_bp']:.4f} bp/week; 95% CI [{b['ci95_low']:.4f}, {b['ci95_high']:.4f}], {b['weeks']} weeks including zeros, 5,000 circular 4-week blocks.","\n## Locked gates\n","| Gate | Result |","|---|---|"]
 for k,val in gates.items():lines.append(f"| {k} | {'PASS' if val else 'FAIL'} |")
 lines += ["\n## Limitations\n","- BID-only feeds do not verify short ASK-side entry/exit; 1/2/4bp are modeled cost sensitivities.","- No swaps, floating overnight losses, margin, spread/slippage verification, or funded equity path.","- No 2022+ PnL calculated; 2017-2021 is contaminated research data.","- A historical screen pass would still require an execution-aware, two-phase funded challenge replay."]
 (a.out_dir/"R294_FINAL_REPORT.md").write_text("\n".join(lines)+"\n")
 print(json.dumps({"verdict":result["verdict"],"gates":gates,"discovery":x,"validation":y,"bootstrap":b},indent=2))
if __name__=="__main__":main()
