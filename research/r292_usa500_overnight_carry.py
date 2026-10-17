#!/usr/bin/env python3
"""R292 locked replay: long USA500 from final US RTH bar close to next RTH open."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

EXPECTED_SHA256 = "df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee"
TZ = "America/New_York"
COSTS = (1, 2, 4)
BOOTSTRAPS = 5000
SEED = 292
BLOCK_WEEKS = 4

def profit_factor(values):
    x=np.asarray(values,dtype=float)
    gains=x[x>0].sum(); losses=-x[x<0].sum()
    return float(gains/losses) if losses>0 else (float("inf") if gains>0 else None)

def load_sessions(path):
    if hashlib.sha256(path.read_bytes()).hexdigest()!=EXPECTED_SHA256:
        raise ValueError("Source SHA-256 mismatch; do not substitute a different feed.")
    d=pd.read_csv(path,compression="gzip")
    if d.columns.tolist()!=["timestamp","open","high","low","close"] or d.timestamp.duplicated().any():
        raise ValueError("Unexpected schema or duplicate timestamps.")
    d=d.sort_values("timestamp",kind="stable").reset_index(drop=True)
    d["dt"]=pd.to_datetime(d.timestamp,unit="ms",utc=True).dt.tz_convert(TZ)
    d["date"]=d.dt.dt.strftime("%Y-%m-%d")
    d["minute"]=d.dt.dt.hour*60+d.dt.dt.minute
    o=["open","high","low","close"]
    d["valid"]=d[o].notna().all(axis=1)&(d[o]>0).all(axis=1)&(d.high>=d[["open","close","low"]].max(axis=1))&(d.low<=d[["open","close","high"]].min(axis=1))
    d["flat"]=(d.open==d.high)&(d.high==d.low)&(d.low==d.close)&(d.close==d.close.shift(1))
    d=d[(d.dt.dt.dayofweek<5)&d.minute.between(570,955)].copy()
    sessions={}; audit=[]
    for day,g0 in d.groupby("date",sort=True):
        g=g0.sort_values("timestamp").reset_index(drop=True)
        start=pd.Timestamp(day).tz_localize(TZ)
        exp=pd.date_range(start+pd.Timedelta(minutes=570),start+pd.Timedelta(minutes=955),freq="5min")
        reasons=[]
        if len(g)!=78: reasons.append("bar_count")
        elif not pd.DatetimeIndex(g["dt"]).equals(exp) or g["dt"].duplicated().any(): reasons.append("timestamp_sequence")
        if not g.valid.all(): reasons.append("invalid_ohlc")
        if g.flat.any(): reasons.append("repeated_flat_placeholder")
        ok=not reasons
        audit.append({"date":day,"year":int(day[:4]),"bars":len(g),"flat_count":int(g.flat.sum()),"eligible":ok,"reason":"|".join(reasons)})
        if ok: sessions[day]=g
    return sessions,audit,int(len(d))

def summarize(frame):
    a=frame["net_bp_2"].to_numpy(float) if len(frame) else np.array([])
    out={"trades":int(len(frame))}
    for c in COSTS:
        out[f"net_bp_{c}"]=float(frame[f"net_bp_{c}"].sum()) if len(frame) else 0.0
        out[f"pf_bp_{c}"]=profit_factor(frame[f"net_bp_{c}"]) if len(frame) else None
    out.update({"gross_net_bp":float(frame.gross_bp.sum()) if len(frame) else 0.0,
                "gross_pf_bp":profit_factor(frame.gross_bp) if len(frame) else None,
                "win_rate_2bp_pct":float((a>0).mean()*100) if len(a) else None,
                "mean_net_bp_2":float(a.mean()) if len(a) else None})
    cum=np.r_[0.0,np.cumsum(a)]/100.0; peaks=np.maximum.accumulate(cum); dd=cum-peaks
    out["fixed_notional_cumulative_pnl_pct_2bp"]=float(cum[-1])
    out["max_closed_pnl_drawdown_pct_of_notional_2bp"]=float(-min(0.0,float(dd.min())))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source",type=Path,required=True,help="Exact usa500idxusd_m5.csv.gz file")
    ap.add_argument("--out",type=Path,default=Path("R292_outputs"))
    args=ap.parse_args(); args.out.mkdir(parents=True,exist_ok=True)
    sessions,audit,filtered_rows=load_sessions(args.source)
    dates=sorted(sessions); rows=[]; skipped=[]
    for i,day in enumerate(dates[:-1]):
        nextday=dates[i+1]
        if day<"2017-01-01" or day>"2021-12-31": continue
        if (pd.Timestamp(nextday)-pd.Timestamp(day)).days>7:
            skipped.append({"entry_date":day,"next_session":nextday,"reason":"gap_over_7_calendar_days"}); continue
        if int(day[:4])<=2020 and nextday>"2020-12-31": continue
        if day.startswith("2021") and nextday>"2021-12-31": continue
        entry=float(sessions[day].iloc[-1].close); exitp=float(sessions[nextday].iloc[0].open)
        gross=(exitp/entry-1)*10000
        row={"entry_date":day,"exit_date":nextday,"year":int(day[:4]),
             "entry_ts":(sessions[day].iloc[-1]["dt"]+pd.Timedelta(minutes=5)).isoformat(),
             "exit_ts":sessions[nextday].iloc[0]["dt"].isoformat(),
             "entry_close_bid":entry,"exit_open_bid":exitp,"gross_bp":float(gross)}
        for c in COSTS: row[f"net_bp_{c}"]=float(gross-c)
        rows.append(row)
    trades=pd.DataFrame(rows)
    trades.to_csv(args.out/"R292_trade_ledger.csv",index=False)
    pd.DataFrame(audit).to_csv(args.out/"R292_session_quality_audit.csv",index=False)
    pd.DataFrame(skipped,columns=["entry_date","next_session","reason"]).to_csv(args.out/"R292_skipped_sessions.csv",index=False)
    disc=trades[trades.entry_date.between("2017-01-01","2020-12-31")].copy()
    val=trades[trades.entry_date.between("2021-01-01","2021-12-31")].copy()
    annual={str(y):summarize(disc[disc.year==y]) for y in range(2017,2021)}
    weeks={d.strftime("%Y-%m-%d"):0.0 for d in pd.date_range("2020-12-28","2021-12-27",freq="W-MON")}
    for _,r in val.iterrows():
        date=pd.Timestamp(r.exit_date); key=(date-pd.Timedelta(days=date.weekday())).strftime("%Y-%m-%d")
        if key in weeks: weeks[key]+=float(r.net_bp_2)
    vals=np.array(list(weeks.values()),float); rng=np.random.default_rng(SEED); means=[]
    for _ in range(BOOTSTRAPS):
        ix=[]
        while len(ix)<len(vals):
            s=int(rng.integers(0,len(vals))); ix.extend(((s+np.arange(BLOCK_WEEKS))%len(vals)).tolist())
        means.append(vals[np.asarray(ix[:len(vals)],int)].mean())
    ci=np.quantile(means,[.025,.975])
    bootstrap={"weeks_including_zero_trade_weeks":len(vals),"weeks_with_trade":int((vals!=0).sum()),
        "mean_weekly_net_bp":float(vals.mean()),"ci95_mean_weekly_net_bp":[float(ci[0]),float(ci[1])],
        "positive_mean_bootstrap_share":float((np.asarray(means)>0).mean()),"block_weeks":BLOCK_WEEKS,
        "resamples":BOOTSTRAPS,"seed":SEED}
    dsum=summarize(disc); vsum=summarize(val); positive_years=sum(annual[str(y)]["net_bp_2"]>0 for y in range(2017,2021))
    gates={"discovery_min_500_trades":dsum["trades"]>=500,"discovery_net_bp_2_positive":dsum["net_bp_2"]>0,
      "discovery_pf_2bp_ge_1_05":dsum["pf_bp_2"]>=1.05,"at_least_3_of_4_discovery_years_positive":positive_years>=3,
      "discovery_pf_4bp_ge_0_90":dsum["pf_bp_4"]>=.90,"validation_min_100_trades":vsum["trades"]>=100,
      "validation_net_bp_2_positive":vsum["net_bp_2"]>0,"validation_pf_2bp_ge_1_05":vsum["pf_bp_2"]>=1.05,
      "validation_bootstrap_ci_lower_gt_zero":bootstrap["ci95_mean_weekly_net_bp"][0]>0,
      "validation_pf_4bp_ge_0_90":vsum["pf_bp_4"]>=.90}
    result={"id":"R292_USA500_OVERNIGHT_LONG_CARRY","verdict":"LULUS" if all(gates.values()) else "GAGAL",
      "source":{"sha256":EXPECTED_SHA256,"rows_after_rth_filter":filtered_rows,"eligible_sessions":len(sessions),
        "session_count_by_year":{str(y):sum(d.startswith(str(y)) for d in sessions) for y in range(2017,2022)},"bid_only":True},
      "rule":"Long at final eligible 15:55 NY M5 bar close and exit at next eligible 09:30 NY M5 bar open; constant notional, no stop/target; 1/2/4 bp modeled round-trip costs.",
      "discovery_2017_2020":dsum,"annual_discovery_2bp":annual,"validation_2021":vsum,
      "validation_weekly_bootstrap_2bp":bootstrap,"session_quality_audit_rows":len(audit),"skipped_long_gaps":len(skipped),
      "positive_discovery_years":int(positive_years),"gates":gates}
    (args.out/"R292_results_compact.json").write_text(json.dumps(result,indent=2,allow_nan=False)+"\n")
    (args.out/"R292_validation_weekly_bootstrap_2bp.json").write_text(json.dumps(bootstrap,indent=2)+"\n")
    annual_rows=[]
    for y,z in annual.items():
        annual_rows.append({"period":"discovery_2017_2020","year":y,"trades":z["trades"],"pf_bp_2":z["pf_bp_2"],"net_bp_2":z["net_bp_2"],"net_bp_4":z["net_bp_4"],"gross_net_bp":z["gross_net_bp"],"max_closed_pnl_drawdown_pct_of_notional_2bp":z["max_closed_pnl_drawdown_pct_of_notional_2bp"]})
    for name,z in [("discovery_2017_2020",dsum),("validation_2021",vsum)]:
        annual_rows.append({"period":name,"year":"TOTAL","trades":z["trades"],"pf_bp_2":z["pf_bp_2"],"net_bp_2":z["net_bp_2"],"net_bp_4":z["net_bp_4"],"gross_net_bp":z["gross_net_bp"],"max_closed_pnl_drawdown_pct_of_notional_2bp":z["max_closed_pnl_drawdown_pct_of_notional_2bp"]})
    pd.DataFrame(annual_rows).to_csv(args.out/"R292_annual_summary_2bp.csv",index=False)
    print(json.dumps({"verdict":result["verdict"],"discovery":dsum,"validation":vsum,"bootstrap":bootstrap,"gates":gates},indent=2))
if __name__=="__main__": main()
