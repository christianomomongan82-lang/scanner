#!/usr/bin/env python3
"""R295 locked replay: positive breadth plus USA500 own-session directional confirmation."""
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
COSTS=(1,2,4); NBOOT=5000; SEED=295; BLOCK=4; TZ="America/New_York"

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
 ap=argparse.ArgumentParser()
 ap.add_argument("--data-dir",type=Path,required=True)
 ap.add_argument("--out-dir",type=Path,default=Path("R295_outputs"))
 args=ap.parse_args(); args.out_dir.mkdir(parents=True,exist_ok=True)
 sessions={}; audits=[]; metas=[]
 for symbol in HASHES:
  ss,au,meta=load(args.data_dir/f"{symbol}_m5.csv.gz",symbol)
  sessions[symbol]=ss; audits.extend(au); metas.append(meta)
 us=sessions["usa500idxusd"]; dates=sorted(d for d in us if "2017-01-01"<=d<="2021-12-31")
 candidate=[]; parent=[]; skipped=[]
 usa_dates=sorted(us)
 for day in dates:
  later=[d for d in usa_dates if d>day]
  if not later: continue
  nxt=later[0]
  if (pd.Timestamp(nxt)-pd.Timestamp(day)).days>7:
   skipped.append({"date":day,"next_usa500":nxt,"reason":"gap_over_7_days"}); continue
  split="discovery" if day<="2020-12-31" else "validation"
  boundary="2020-12-31" if split=="discovery" else "2021-12-31"
  if nxt>boundary:
   skipped.append({"date":day,"next_usa500":nxt,"reason":"split_boundary"}); continue
  valid={sym:series[day] for sym,series in sessions.items() if day in series}
  if len(valid)<3 or "usa500idxusd" not in valid:
   skipped.append({"date":day,"next_usa500":nxt,"reason":"fewer_than_three_valid_feeds"}); continue
  votes=sum(dayret(g)>0 for g in valid.values()); fraction=votes/len(valid)
  own_return=dayret(us[day])*100.0
  entry=float(us[day].iloc[77].open); exitp=float(us[nxt].iloc[0].open)
  if not(np.isfinite(entry) and np.isfinite(exitp) and entry>0 and exitp>0):
   skipped.append({"date":day,"next_usa500":nxt,"reason":"invalid_entry_exit"}); continue
  gross=(exitp/entry-1)*10000.0
  base={"entry_date":day,"exit_date":nxt,"year":int(day[:4]),"split":split,
        "entry_ts_ny":us[day].iloc[77]["dt"].isoformat(),"exit_ts_ny":us[nxt].iloc[0]["dt"].isoformat(),
        "entry_bid":entry,"exit_bid":exitp,"positive_votes":int(votes),"valid_feeds":int(len(valid)),
        "positive_fraction":float(fraction),"rth_return_usa500_pct":float(own_return),"gross_bp":float(gross)}
  if fraction>=.75:
   prow=dict(base,side="LONG",direction=1)
   for cost in COSTS: prow[f"net_bp_{cost}"]=float(gross-cost)
   parent.append(prow)
   if own_return>0:
    crow=dict(base,side="LONG",direction=1)
    for cost in COSTS: crow[f"net_bp_{cost}"]=float(gross-cost)
    candidate.append(crow)
 cdf=pd.DataFrame(candidate); pdf=pd.DataFrame(parent); sdf=pd.DataFrame(skipped)
 cdf.to_csv(args.out_dir/"R295_candidate_ledger.csv",index=False)
 pdf.to_csv(args.out_dir/"R295_matched_R293_parent_ledger.csv",index=False)
 pd.DataFrame(audits).to_csv(args.out_dir/"R295_session_quality_audit.csv",index=False)
 sdf.to_csv(args.out_dir/"R295_skipped_dates.csv",index=False)
 results={}
 for name,lo,hi in [("discovery","2017-01-01","2020-12-31"),("validation","2021-01-01","2021-12-31")]:
  c=cdf[cdf.entry_date.between(lo,hi)].copy(); p=pdf[pdf.entry_date.between(lo,hi)].copy()
  results[name]={"candidate":summaries(c),"matched_R293_parent":summaries(p)}
  if name=="discovery":
   results[name]["annual_candidate"]={str(y):summaries(c[c.year==y]) for y in range(2017,2021)}
  else:
   results[name]["candidate_bootstrap"]=bootstrap(c)
   results[name]["parent_bootstrap"]=bootstrap(p)
 d=results["discovery"]["candidate"]; v=results["validation"]["candidate"]
 annual=results["discovery"]["annual_candidate"]; boot=results["validation"]["candidate_bootstrap"]
 gates={
  "discovery_min_200_trades":d["trades"]>=200,
  "discovery_net_bp_2_positive":d["net_bp_2"]>0,
  "discovery_pf_2bp_ge_1_05":d["pf_2bp"] is not None and d["pf_2bp"]>=1.05,
  "discovery_at_least_2_of_4_years_positive":sum(q["net_bp_2"]>0 for q in annual.values())>=2,
  "discovery_pf_4bp_ge_0_90":d["pf_4bp"] is not None and d["pf_4bp"]>=.90,
  "validation_min_75_trades":v["trades"]>=75,
  "validation_net_bp_2_positive":v["net_bp_2"]>0,
  "validation_pf_2bp_ge_1_05":v["pf_2bp"] is not None and v["pf_2bp"]>=1.05,
  "validation_bootstrap_ci_lower_gt_zero":boot["ci95_low"]>0,
  "validation_pf_4bp_ge_0_90":v["pf_4bp"] is not None and v["pf_4bp"]>=.90}
 excluded=pdf[~pdf.entry_date.isin(set(cdf.entry_date))]
 removed_disc=excluded[excluded.entry_date.between("2017-01-01","2020-12-31")]
 removed_val=excluded[excluded.entry_date.between("2021-01-01","2021-12-31")]
 gains=float(removed_disc.loc[removed_disc.net_bp_2>0,"net_bp_2"].sum())
 losses=float(-removed_disc.loc[removed_disc.net_bp_2<0,"net_bp_2"].sum())
 diag={"parent_trades_discovery":int(len(pdf[pdf.entry_date.between("2017-01-01","2020-12-31")])),
       "child_trades_discovery":int(len(cdf[cdf.entry_date.between("2017-01-01","2020-12-31")])),
       "trades_removed_discovery":int(len(removed_disc)),"removed_discovery_net_bp_2":float(removed_disc.net_bp_2.sum()),
       "removed_discovery_pf_2bp":float(gains/losses) if losses>0 else None,
       "parent_trades_validation":int(len(pdf[pdf.entry_date.between("2021-01-01","2021-12-31")])),
       "child_trades_validation":int(len(cdf[cdf.entry_date.between("2021-01-01","2021-12-31")])),
       "trades_removed_validation":int(len(removed_val))}
 out={"candidate_id":"R295_BREADTH_PLUS_USA500_DIRECTION_CONFIRMATION",
      "verdict":"LULUS_HISTORICAL_SCREEN_ONLY" if all(gates.values()) else "GAGAL",
      "inputs":metas,"audited_instrument_session_rows":len(audits),
      "valid_sessions_by_symbol":{m["symbol"]:m["valid_sessions_through_2021"] for m in metas},
      "strategy_pnl_2022_plus_calculated":False,"results":results,"gates":gates,
      "filter_diagnostic":diag,
      "limitations":["M5 BID-only sources; costs at 1/2/4 bp are modeled, not observed executable costs.",
       "No live ask-side spread, slippage, commission, swaps, point value or overnight floating loss modeled.",
       "No FundedNext two-phase equity-aware challenge replay.",
       "2017-2021 is contaminated research data, not pristine program-level OOS.",
       "No R295 outcome PnL beyond 2021 was calculated."]}
 (args.out_dir/"R295_results_compact.json").write_text(json.dumps(out,indent=2,allow_nan=False))
 lines=["# R295 — Positive Breadth + USA500 Own-Session Direction Confirmation",
        f"\n**Verdict: {out['verdict']}**\n",
        "## Candidate and matched R293 parent\n",
        "| Metric | Discovery candidate | Discovery parent | Validation candidate | Validation parent |",
        "|---|---:|---:|---:|---:|"]
 for key,label in [("trades","Trades"),("net_bp_2","Net bp @2bp"),("pf_2bp","PF @2bp"),
                    ("net_bp_4","Net bp @4bp"),("pf_4bp","PF @4bp"),
                    ("max_closed_pnl_drawdown_pct_fixed_notional_2bp","Max closed-PnL DD (% fixed notional)")]:
  lines.append(f"| {label} | {d.get(key)} | {results['discovery']['matched_R293_parent'].get(key)} | {v.get(key)} | {results['validation']['matched_R293_parent'].get(key)} |")
 lines += [f"\n## Filter diagnostic\n\nThe own-USA500-positive condition removed {diag['trades_removed_discovery']} discovery trades. Their combined net result was {diag['removed_discovery_net_bp_2']:+.2f} bp at 2 bp modeled cost (PF {diag['removed_discovery_pf_2bp']:.3f}), so the extra condition discarded a net-profitable subset. It removed {diag['trades_removed_validation']} validation trades, leaving validation identical to R293.\n",
           "\n## Annual discovery cohorts @2bp\n","| Year | Trades | Net bp | PF |","|---|---:|---:|---:|"]
 for y,q in annual.items(): lines.append(f"| {y} | {q['trades']} | {q['net_bp_2']:.2f} | {q['pf_2bp']:.3f} |")
 lines += [f"\n## Validation bootstrap\n\nMean {boot['mean_weekly_bp']:.4f} bp/week; 95% CI [{boot['ci95_low']:.4f}, {boot['ci95_high']:.4f}] over {boot['weeks']} weeks including zeros (5,000 circular 4-week blocks, seed 295).",
           "\n## Locked gate results\n","| Gate | Result |","|---|---|"]
 for key,value in gates.items(): lines.append(f"| {key} | {'PASS' if value else 'FAIL'} |")
 lines += ["\n## Limitations\n","- Inputs are M5 BID-only; costs are modeled at 1/2/4 bp, not verified executable costs.",
           "- No swaps, overnight floating-loss model or FundedNext equity-path simulation.",
           "- No strategy PnL beyond 2021 was calculated; 2017–2021 is contaminated research data."]
 (args.out_dir/"R295_FINAL_REPORT.md").write_text("\n".join(lines)+"\n")
 print(json.dumps({"verdict":out["verdict"],"gates":gates,"filter_diagnostic":diag,"results":results,
                   "bootstrap":{k:v for k,v in boot.items() if k!="weekly_net_bp"}},indent=2))

if __name__=="__main__": main()
