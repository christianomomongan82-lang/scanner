#!/usr/bin/env python3
"""R291 locked local replay: USA500 prior cash-session return -> German index session."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

HASH = {
    "USA500": "df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee",
    "DEU": "7ad37cb19545eef6111b928a97322c06c9f2478030a0c4282669542262303af4",
}
COSTS=(1,2,4); BOOT=5000; SEED=291; BLOCK=4

def load(path, sym, tz, lo, hi, n):
    if hashlib.sha256(path.read_bytes()).hexdigest()!=HASH[sym]:
        raise ValueError(f"{sym}: source SHA256 mismatch")
    d=pd.read_csv(path,compression="gzip")
    if d.columns.tolist()!=["timestamp","open","high","low","close"] or d.timestamp.duplicated().any():
        raise ValueError(f"{sym}: schema mismatch or duplicate timestamps")
    d=d.sort_values("timestamp",kind="stable").reset_index(drop=True)
    d["dt"]=pd.to_datetime(d.timestamp,unit="ms",utc=True).dt.tz_convert(tz)
    d["date"]=d.dt.dt.strftime("%Y-%m-%d")
    d["minute"]=d.dt.dt.hour*60+d.dt.dt.minute
    c=["open","high","low","close"]
    d["valid"]=d[c].notna().all(axis=1)&(d[c]>0).all(axis=1)&(d.high>=d[["open","close","low"]].max(axis=1))&(d.low<=d[["open","close","high"]].min(axis=1))
    d["flat"]=(d.open==d.high)&(d.high==d.low)&(d.low==d.close)&(d.close==d.close.shift(1))
    x=d[(d.dt.dt.dayofweek<5)&d.minute.between(lo,hi)]
    sessions={}; audits=[]
    for day,g0 in x.groupby("date",sort=True):
        g=g0.sort_values("timestamp").reset_index(drop=True)
        start=pd.Timestamp(day).tz_localize(tz)
        exp=pd.date_range(start+pd.Timedelta(minutes=lo),start+pd.Timedelta(minutes=hi),freq="5min")
        why=[]
        if len(g)!=n: why.append("bar_count")
        elif not pd.DatetimeIndex(g["dt"]).equals(exp) or g.dt.duplicated().any(): why.append("timestamp_sequence")
        if not g.valid.all(): why.append("invalid_ohlc")
        if g.flat.any(): why.append("repeated_flat_placeholder")
        ok=not why
        audits.append({"symbol":sym,"date":day,"year":int(day[:4]),"bar_count":len(g),"flat_count":int(g.flat.sum()),"eligible":ok,"reason":"|".join(why)})
        if ok:sessions[day]=g
    return sessions,pd.DataFrame(audits)

def pf(x):
    x=np.asarray(x,float); gain=x[x>0].sum(); loss=-x[x<0].sum()
    return float(gain/loss) if loss>0 else (float("inf") if gain>0 else None)

def summ(df,cost):
    x=df[f"net_r_{cost}bp"].to_numpy(float) if len(df) else np.array([])
    if not len(x): return {"trades":0,"pf_r":None,"net_r":0.0,"mean_r":None,"median_r":None,"win_rate_pct":None,"max_closed_trade_dd_r":0.0}
    eq=np.cumsum(x); dd=eq-np.maximum.accumulate(np.r_[0,eq])[1:]
    return {"trades":int(len(x)),"pf_r":pf(x),"net_r":float(x.sum()),"mean_r":float(x.mean()),"median_r":float(np.median(x)),"win_rate_pct":float((x>0).mean()*100),"max_closed_trade_dd_r":float(-min(0,dd.min()))}

def trade(day,usday,r,threshold,g):
    g=g.reset_index(drop=True); opening=g.iloc[:4]; z=g.iloc[4]
    sign=1 if r>0 else -1; ent=float(z.open)
    stop=float(opening.low.min() if sign>0 else opening.high.max())
    risk=ent-stop if sign>0 else stop-ent
    if not np.isfinite(risk) or risk<=0:return None,"invalid_or_gapped_open_stop"
    target=ent+sign*1.5*risk; ex=None; why=None; exts=None
    for j in range(4,len(g)):
        b=g.iloc[j]; op,hi,lo=map(float,(b.open,b.high,b.low))
        if sign>0:
            if op<=stop:ex,why=op,"stop_gap_open"
            elif op>=target:ex,why=op,"target_gap_open"
            elif lo<=stop:ex,why=stop,("stop_both_touched" if hi>=target else "stop")
            elif hi>=target:ex,why=target,"target"
        else:
            if op>=stop:ex,why=op,"stop_gap_open"
            elif op<=target:ex,why=op,"target_gap_open"
            elif hi>=stop:ex,why=stop,("stop_both_touched" if lo<=target else "stop")
            elif lo<=target:ex,why=target,"target"
        if ex is not None: exts=b["dt"].isoformat(); break
    if ex is None:
        b=g.iloc[-1]; ex=float(b.close); why="scheduled_session_close"; exts=(b["dt"]+pd.Timedelta(minutes=5)).isoformat()
    move=sign*(ex-ent); gr=move/risk
    out={"date":day,"year":int(day[:4]),"signal_us_date":usday,"signal_us_return":float(r),"threshold":float(threshold),"direction":"LONG" if sign>0 else "SHORT","entry_ts":z["dt"].isoformat(),"entry_price_bid_proxy":ent,"stop_price":stop,"target_price":float(target),"risk_points":float(risk),"exit_ts":exts,"exit_price_bid_proxy":float(ex),"exit_reason":why,"gross_r":float(gr),"gross_bp":float(move/ent*10000)}
    for c in COSTS:
        out[f"net_r_{c}bp"]=float(gr-(ent*c/10000)/risk); out[f"net_bp_{c}bp"]=float(move/ent*10000-c)
    return out,None

def bootstrap(v):
    weeks={m.strftime("%Y-%m-%d"):0.0 for m in pd.date_range("2020-12-28","2021-12-27",freq="W-MON")}
    if len(v):
        q=v.copy(); dt=pd.to_datetime(q.date); q["week"]=(dt-pd.to_timedelta(dt.dt.weekday,unit="D")).dt.strftime("%Y-%m-%d")
        for k,z in q.groupby("week")["net_r_2bp"].sum().items():
            if k in weeks:weeks[k]=float(z)
    vals=np.array(list(weeks.values())); rng=np.random.default_rng(SEED); n=len(vals); means=[]
    for _ in range(BOOT):
        ix=[]
        for _ in range(int(np.ceil(n/BLOCK))):
            s=int(rng.integers(0,n)); ix.extend((s+np.arange(BLOCK))%n)
        means.append(vals[np.asarray(ix[:n],int)].mean())
    ci=np.quantile(means,[.025,.975])
    return {"weeks_including_zero_trade_weeks":n,"weeks_with_trade":int((vals!=0).sum()),"mean_weekly_net_r":float(vals.mean()),"bootstrap_replicates":BOOT,"block_length_weeks":BLOCK,"seed":SEED,"mean_weekly_net_r_ci95":[float(ci[0]),float(ci[1])],"bootstrap_probability_mean_positive":float((np.asarray(means)>0).mean())}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--usa500",required=True,type=Path);ap.add_argument("--deu",required=True,type=Path)
    ap.add_argument("--out",default="R291_outputs",type=Path);a=ap.parse_args();a.out.mkdir(parents=True,exist_ok=True)
    us,ua=load(a.usa500,"USA500","America/New_York",570,955,78)
    deu,da=load(a.deu,"DEU","Europe/Berlin",540,955,84)
    ur={d:float(g.iloc[-1].close/g.iloc[0].open-1) for d,g in us.items()}
    cal=np.array([abs(r) for d,r in ur.items() if "2017-01-01"<=d<="2020-12-31"])
    threshold=float(np.quantile(cal,.75,method="linear")); rows=[]; skipped=[]
    for day,g in deu.items():
        if day>"2021-12-31":continue
        if day<"2017-01-01":continue
        prev=[d for d in ur if d<day]
        if not prev:skipped.append({"date":day,"reason":"no_prior_US_session"});continue
        usday=max(prev)
        if (pd.Timestamp(day)-pd.Timestamp(usday)).days>4:skipped.append({"date":day,"signal_us_date":usday,"reason":"prior_US_session_older_than_4_days"});continue
        r=ur[usday]
        if abs(r)<threshold:continue
        t,why=trade(day,usday,r,threshold,g)
        if why:skipped.append({"date":day,"signal_us_date":usday,"reason":why})
        elif t:rows.append(t)
    ledger=pd.DataFrame(rows);ledger.to_csv(a.out/"R291_trade_ledger_2017_2021.csv",index=False)
    pd.concat([ua,da],ignore_index=True).to_csv(a.out/"R291_session_quality_audit.csv",index=False)
    pd.DataFrame(skipped).to_csv(a.out/"R291_skipped_signals.csv",index=False)
    d=ledger[ledger.date.between("2017-01-01","2020-12-31")].copy();v=ledger[ledger.date.between("2021-01-01","2021-12-31")].copy()
    calr=ledger.gross_r.to_numpy(float)
    result={"id":"R291_TRANSATLANTIC_LEAD_LAG","verdict":None,"threshold_q75_abs_US500_RTH_return":threshold,"threshold_calibration_sessions":int(len(cal)),"source":{"USA500_SHA256":HASH["USA500"],"DEU_SHA256":HASH["DEU"],"USA500_eligible_sessions":len(us),"DEU_eligible_sessions":len(deu),"prices":"BID-only M5; costs modeled, not observed"},"gross":{"discovery_2017_2020":{"trades":len(d),"pf_r":pf(d.gross_r),"net_r":float(d.gross_r.sum())},"validation_2021":{"trades":len(v),"pf_r":pf(v.gross_r),"net_r":float(v.gross_r.sum())}},"periods":{}}
    for name,x in [("discovery_2017_2020",d),("validation_2021",v)]:
        result["periods"][name]={f"{c}bp":summ(x,c) for c in COSTS}
        if name.startswith("discovery"):result["periods"][name]["annual_2bp"]={str(y):summ(x[x.year==y],2) for y in range(2017,2021)}
    b=bootstrap(v);result["bootstrap_validation_2bp"]=b
    d2,d4=summ(d,2),summ(d,4);v2,v4=summ(v,2),summ(v,4)
    py=sum(result["periods"]["discovery_2017_2020"]["annual_2bp"][str(y)]["net_r"]>0 for y in range(2017,2021))
    gates={"discovery_min_100_trades":d2["trades"]>=100,"discovery_pf_at_2bp_ge_1_05":d2["pf_r"] is not None and d2["pf_r"]>=1.05,"discovery_net_r_positive":d2["net_r"]>0,"discovery_at_least_3_of_4_years_positive":py>=3,"discovery_pf_at_4bp_ge_0_90":d4["pf_r"] is not None and d4["pf_r"]>=.90,"validation_min_50_trades":v2["trades"]>=50,"validation_pf_at_2bp_ge_1_05":v2["pf_r"] is not None and v2["pf_r"]>=1.05,"validation_net_r_positive":v2["net_r"]>0,"validation_bootstrap_95pct_CI_lower_gt_zero":b["mean_weekly_net_r_ci95"][0]>0,"validation_pf_at_4bp_ge_0_90":v4["pf_r"] is not None and v4["pf_r"]>=.90}
    result["gates"]=gates;result["verdict"]="LULUS" if all(gates.values()) else "GAGAL";result["positive_discovery_years"]=int(py)
    (a.out/"R291_results_compact.json").write_text(json.dumps(result,indent=2,allow_nan=False))
    print(json.dumps({"verdict":result["verdict"],"threshold":threshold,"periods":result["periods"],"bootstrap":b,"gates":gates},indent=2))
if __name__=="__main__":main()
