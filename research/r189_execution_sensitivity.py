#!/usr/bin/env python3
"""Local-only execution sensitivity audit for the locked R189/L80 replay.
Uses the same signal rules and parameters; it does not tune the strategy.
Expected input files: data_exports/eurusd_m1_2016_2025/*.csv.gz
"""
from pathlib import Path
import json
import sys
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from research.r189_dukascopy_historical_replay import (
    read_bars, l80_fast, PIP, SL, TP, MFE_TRIGGER, TRAIL,
    TIME_STOP_BARS, MAX_SPREAD_PIPS, COSTS
)
DATA = ROOT / "data_exports/eurusd_m1_2016_2025"
OUT = ROOT / "research/r189_dukascopy_history_local_results"

def simulate_intrabar(df, bid, ask, signals):
    n, idx = len(df), df.index
    bo,bh,bl,bc = (bid[k].to_numpy(float) for k in ("Open","High","Low","Close"))
    ao,ah,al,ac = (ask[k].to_numpy(float) for k in ("Open","High","Low","Close"))
    spread = (ao-bo)/PIP
    trades=[]; active_exit=-1; overlap=spread_rejects=censored=gap_fills=0
    for si,direction,_src in signals:
        e=si+1
        if e>=n: continue
        if not np.isfinite(spread[e]) or spread[e]<-1e-9 or spread[e]>MAX_SPREAD_PIPS+1e-12:
            spread_rejects+=1; continue
        if e<=active_exit: overlap+=1; continue
        entry=float(ao[e] if direction==1 else bo[e])
        hard_stop=entry-direction*SL*PIP
        target=entry+direction*TP*PIP
        fav=entry; trail_active=False; stop=hard_stop
        scheduled=e+TIME_STOP_BARS
        if scheduled>=n:
            censored+=1; active_exit=n; continue
        exit_i=gross=reason=None
        for j in range(e,scheduled):
            active_stop=stop if trail_active else hard_stop
            # Check existing orders at the open first; crossed stop orders fill at open.
            if direction==1:
                if bo[j] <= active_stop:
                    exit_i=j; gross=(bo[j]-entry)/PIP
                    reason="STOP_GAP_OPEN" if bo[j]<active_stop else ("TRAIL_STOP" if trail_active else "STOP")
                    gap_fills+=int(bo[j]<active_stop); break
                if bo[j] >= target:
                    exit_i=j; gross=(bo[j]-entry)/PIP; reason="TARGET_GAP_OPEN"; break
                stop_hit=bl[j] <= active_stop; target_hit=bh[j] >= target
            else:
                if ao[j] >= active_stop:
                    exit_i=j; gross=-(ao[j]-entry)/PIP
                    reason="STOP_GAP_OPEN" if ao[j]>active_stop else ("TRAIL_STOP" if trail_active else "STOP")
                    gap_fills+=int(ao[j]>active_stop); break
                if ao[j] <= target:
                    exit_i=j; gross=-(ao[j]-entry)/PIP; reason="TARGET_GAP_OPEN"; break
                stop_hit=ah[j] >= active_stop; target_hit=al[j] <= target
            # If both intrabar levels are touched, use stop-first.
            if stop_hit:
                exit_i=j; gross=direction*(active_stop-entry)/PIP
                reason="TRAIL_STOP" if trail_active else "STOP"; break
            if target_hit:
                exit_i=j; gross=TP; reason="TARGET"; break
            # Update a zero-distance trail to the best excursion seen.
            if direction==1:
                fav=max(fav,bh[j]); fav_pips=(fav-entry)/PIP
                if fav_pips>=MFE_TRIGGER:
                    new_stop=entry+(fav_pips-TRAIL)*PIP
                    if (not trail_active) or new_stop>stop: stop=new_stop
                    trail_active=True
                    # If close is below the new high-water mark, price retraced after the high.
                    if bc[j] < stop-1e-12:
                        exit_i=j; gross=(stop-entry)/PIP; reason="TRAIL_STOP_SAME_BAR"; break
            else:
                fav=min(fav,al[j]); fav_pips=(entry-fav)/PIP
                if fav_pips>=MFE_TRIGGER:
                    new_stop=entry-(fav_pips-TRAIL)*PIP
                    if (not trail_active) or new_stop<stop: stop=new_stop
                    trail_active=True
                    if ac[j] > stop+1e-12:
                        exit_i=j; gross=-(stop-entry)/PIP; reason="TRAIL_STOP_SAME_BAR"; break
        if exit_i is None:
            exit_i=scheduled; px=float(bo[exit_i] if direction==1 else ao[exit_i])
            gross=direction*(px-entry)/PIP; reason="TIME_OPEN_CAUSAL"
        trades.append({"signal_utc":idx[si].isoformat(),"entry_utc":idx[e].isoformat(),
            "exit_utc":idx[exit_i].isoformat(),"direction":"LONG" if direction==1 else "SHORT",
            "entry_price":entry,"entry_spread_pips":float(spread[e]),"exit_reason":reason,"gross_pips":float(gross)})
        active_exit=exit_i
    return trades,{"spread_rejects":spread_rejects,"overlap_skipped":overlap,"censored":censored,"gap_fills":gap_fills}

def metric(trades,cost,weeks):
    a=np.array([x["gross_pips"]-cost for x in trades],float)
    gp=a[a>0].sum(); gl=-a[a<0].sum(); eq=np.cumsum(a)
    dd=float(np.max(np.maximum.accumulate(np.r_[0.,eq])[1:]-eq)) if len(a) else 0.
    return {"trades":int(len(a)),"PF":float(gp/gl) if gl else None,"net_pips":float(a.sum()),
        "max_drawdown_pips":dd,"win_rate":float((a>0).mean()) if len(a) else None,
        "trades_per_week":len(a)/weeks}

def main():
    bid,bd=read_bars(DATA/"eurusd_bid_M1_2016-2025.csv.gz")
    ask,ad=read_bars(DATA/"eurusd_ask_M1_2016-2025.csv.gz")
    common=bid.index.intersection(ask.index).sort_values()
    bid,ask=bid.loc[common],ask.loc[common]; df=bid.copy()
    spread=(ask.Open-bid.Open)/PIP
    signals_all=l80_fast(df,disp_thr=15,late_thr=.8)
    signals=[(i,d,s) for i,d,s in signals_all if ((df.index[i].hour-5)%24) not in (6,9)
        and i+1<len(df) and spread.iat[i+1]<=MAX_SPREAD_PIPS+1e-12]
    trades,diag=simulate_intrabar(df,bid,ask,signals)
    OUT.mkdir(parents=True,exist_ok=True)
    pd.DataFrame(trades).to_csv(OUT/"R189_Dukascopy_2016_2025_intrabar_trades.csv",index=False)
    periods=[("all_2016_2025","2016-01-01","2026-01-01"),("discovery_2016_2020","2016-01-01","2021-01-01"),("forward_2021_2025","2021-01-01","2026-01-01")]
    results={}
    for name,ss,ee in periods:
        s,e=pd.Timestamp(ss,tz="UTC"),pd.Timestamp(ee,tz="UTC")
        z=[t for t in trades if s<=pd.Timestamp(t["entry_utc"])<e and pd.Timestamp(t["exit_utc"])<e]
        weeks=(e-s).total_seconds()/(7*24*3600)
        results[name]={f"extra_cost_{c:g}_pip":metric(z,c,weeks) for c in COSTS}
    annual=[]
    for y in range(2016,2026):
        s,e=pd.Timestamp(f"{y}-01-01",tz="UTC"),pd.Timestamp(f"{y+1}-01-01",tz="UTC")
        z=[t for t in trades if s<=pd.Timestamp(t["entry_utc"])<e and pd.Timestamp(t["exit_utc"])<e]
        annual.append({"year":y,**{f"extra_cost_{c:g}_pip":metric(z,c,(e-s).total_seconds()/(7*24*3600)) for c in COSTS}})
    s,e=pd.Timestamp("2021-01-01",tz="UTC"),pd.Timestamp("2026-01-01",tz="UTC")
    weeks=int(np.ceil((e-s).total_seconds()/(7*24*3600))); weekly=np.zeros(weeks)
    forward=[t for t in trades if s<=pd.Timestamp(t["entry_utc"])<e and pd.Timestamp(t["exit_utc"])<e]
    for t in forward:
        wi=int((pd.Timestamp(t["entry_utc"])-s).total_seconds()//(7*24*3600))
        if 0<=wi<weeks: weekly[wi]+=t["gross_pips"]-1.0
    rng=np.random.default_rng(1892026); reps=5000; block=4; count=int(np.ceil(weeks/block)); means=np.empty(reps)
    for k in range(reps):
        starts=rng.integers(0,weeks,size=count)
        ix=np.concatenate([(q+np.arange(block))%weeks for q in starts])[:weeks]
        means[k]=weekly[ix].mean()
    bootstrap={"weeks":weeks,"trades":len(forward),"reps":reps,"seed":1892026,
        "mean_weekly_net_pips_at_plus1":float(weekly.mean()),
        "probability_positive_mean_weekly_net":float((means>0).mean()),
        "ci95_mean_weekly_net_pips":[float(np.quantile(means,.025)),float(np.quantile(means,.975))]}
    report={"status":"COMPLETE","execution":"local Python only","source_feed":"Dukascopy EURUSD M1 BID/ASK 2016-2025",
        "variant":"intrabar zero-distance trail; open-gap stop fills; stop-first intrabar collision",
        "parameters_locked":True,"eligible_signals":len(signals),"trade_count":len(trades),"diagnostics":diag,
        "exit_reasons":pd.Series([t["exit_reason"] for t in trades]).value_counts().to_dict(),
        "metrics":results,"annual":annual,"forward_bootstrap_at_plus1pip":bootstrap,
        "limitations":["Not exact reproduction of missing original HistData feed.","M1 OHLC cannot reveal tick-perfect sequencing.",
        "Manual phone latency/management, broker-specific commission, live slippage, funded DLL/MLL and Quick Strike are not validated."]}
    (OUT/"R189_Dukascopy_execution_sensitivity_results.json").write_text(json.dumps(report,indent=2,allow_nan=False)+"\n")
    print(json.dumps(report,indent=2,allow_nan=False))

if __name__=="__main__": main()
