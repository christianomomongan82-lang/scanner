#!/usr/bin/env python3
"""R251 preregistered FX lead-lag test. No parameter search.
Signal: a large GBPUSD hourly move that EURUSD has not yet followed, relative
to a rolling GBP->EUR beta estimated strictly from prior observations.
Enter next H1 open; exit at that H1 bar close. All fills use executable bid/ask.
"""
from __future__ import annotations
import json, subprocess, os
from pathlib import Path
import numpy as np
import pandas as pd

OUT=Path("research"); DATA=Path("dl/r251")
START="2016-01-01"; END="now"
PAIRS=("eurusd","gbpusd")
EXTRA_COST_PIPS=0.0  # bid/ask quotes already applied; no fabricated fixed spread
PIP=0.0001
CFG={"id":"R251_GBPUSD_LEADS_EURUSD_H1_Z15_BETA500_UNDERREACTION025_HOLD1",
     "lookback":500,"z_threshold":1.5,"underreaction_fraction":0.25,"hold_bars":1,
     "discovery":"2016-2020","forward":"2021-2025","oos":"2026"}

def download(pair, side):
    DATA.mkdir(parents=True,exist_ok=True)
    path=DATA/f"{pair}_h1_{side}.csv"
    cmd=["npx","--yes","dukascopy-node@1.50.0","-i",pair,"-from",START,"-to",END,
         "-t","h1","-p",side,"-utc","0","-f","csv","-fl","-dir",str(DATA),"-fn",path.stem,
         "-bs","3","-bp","2000","-r","5","-rp","5000"]
    p=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=2400)
    if p.returncode or not path.exists() or path.stat().st_size<1000:
        raise RuntimeError(f"download failed {pair} {side}: exit={p.returncode}; {p.stdout[-2000:]}")
    return path

def load(path):
    d=pd.read_csv(path)
    d.columns=[str(c).replace("\ufeff","").strip().lower() for c in d.columns]
    tc=next((c for c in ("timestamp","datetime","date","time") if c in d.columns),None)
    if tc is None: raise ValueError(f"timestamp column missing: {path}; {d.columns.tolist()}")
    ts=d.pop(tc); num=pd.to_numeric(ts,errors="coerce")
    if num.notna().mean()>.95:
        med=float(num.abs().median()); unit="ms" if med>=1e11 else "s" if med>=1e8 else None
        if unit is None: raise ValueError(f"unknown timestamp scale {med}")
        idx=pd.to_datetime(num,unit=unit,utc=True,errors="coerce")
    else: idx=pd.to_datetime(ts,utc=True,errors="coerce")
    if idx.isna().any(): raise ValueError(f"invalid timestamp in {path}")
    for c in ("open","high","low","close"):
        if c not in d: raise ValueError(f"missing {c} in {path}")
        d[c]=pd.to_numeric(d[c],errors="coerce")
    d.index=pd.DatetimeIndex(idx)
    d=d[["open","high","low","close"]].replace([np.inf,-np.inf],np.nan).dropna().sort_index()
    d=d.loc[~d.index.duplicated(keep="last")]
    if len(d)<10000: raise ValueError(f"insufficient rows {path}: {len(d)}")
    if ((d.high<d[["open","close"]].max(axis=1)) | (d.low>d[["open","close"]].min(axis=1)) | (d.high<d.low)).any():
        raise ValueError(f"invalid OHLC {path}")
    return d

def stats(trades):
    if not trades: return {"trades":0,"pf":None,"net_pips":0.0,"win_rate":None,"mean_pips":None}
    x=np.array([t["net_pips"] for t in trades],float)
    gains=float(x[x>0].sum()); losses=float(-x[x<0].sum())
    return {"trades":len(x),"pf":float(gains/losses) if losses else (float("inf") if gains else 0.0),
            "net_pips":float(x.sum()),"win_rate":float((x>0).mean()),"mean_pips":float(x.mean())}

def main():
    files={}
    for p in PAIRS:
        for side in ("bid","ask"):
            files[(p,side)]=load(download(p,side))
    # Align all four quote series by exact UTC timestamp; no forward fill.
    ix=files[("eurusd","bid")].index
    for d in files.values(): ix=ix.intersection(d.index)
    ix=ix.sort_values()
    if len(ix)<20000: raise RuntimeError(f"too few common bars: {len(ix)}")
    q={k:v.reindex(ix) for k,v in files.items()}
    # Signal is calculated only from completed bar closes. Beta uses strictly prior returns.
    gbp=q[("gbpusd","bid")].close.pct_change()
    eur=q[("eurusd","bid")].close.pct_change()
    lb=int(CFG["lookback"])
    beta=(eur.shift(1).rolling(lb,min_periods=lb).cov(gbp.shift(1)) /
          gbp.shift(1).rolling(lb,min_periods=lb).var())
    gbp_sd=gbp.shift(1).rolling(lb,min_periods=lb).std()
    eur_ret=eur
    expected=beta*gbp
    # Large GBP impulse; EUR under-reacts in the same completed hour.
    z=gbp/gbp_sd
    sig=np.where((z>=CFG["z_threshold"]) & (eur_ret < CFG["underreaction_fraction"]*expected),1,
       np.where((z<=-CFG["z_threshold"]) & (eur_ret > CFG["underreaction_fraction"]*expected),-1,0))
    sig=pd.Series(sig,index=ix).shift(1).fillna(0).astype(int) # enter next H1 open
    times=ix
    ledger=[]
    for i in np.flatnonzero(sig.to_numpy()):
        if i+1>=len(ix): continue
        direction=int(sig.iloc[i]); entry_i=i
        # Trade at the next bar open; close at the end of that same bar.
        if direction==1:
            entry=float(q[("eurusd","ask")].open.iloc[entry_i])
            exitp=float(q[("eurusd","bid")].close.iloc[entry_i])
        else:
            entry=float(q[("eurusd","bid")].open.iloc[entry_i])
            exitp=float(q[("eurusd","ask")].close.iloc[entry_i])
        net=(exitp-entry)/PIP*direction-EXTRA_COST_PIPS
        ledger.append({"entry_utc":times[entry_i].isoformat(),"direction":"LONG" if direction==1 else "SHORT",
                       "entry":entry,"exit":exitp,"net_pips":float(net)})
    # Non-overlapping by design: one H1 position per entry signal, no position stacking.
    df=pd.DataFrame(ledger)
    periods=[("discovery","2016-01-01","2021-01-01"),("forward","2021-01-01","2026-01-01"),("oos2026","2026-01-01","2027-01-01")]
    result={"status":"COMPLETED","config":CFG,"data":{"common_rows":len(ix),"start_utc":ix[0].isoformat(),"end_utc":ix[-1].isoformat(),
             "source":"Dukascopy H1 bid/ask","instruments":list(PAIRS),"extra_cost_pips":EXTRA_COST_PIPS},
            "periods":{},"verdict":"FAIL"}
    for name,a,b in periods:
        if df.empty: part=[]
        else: part=df.loc[(df.entry_utc>=a)&(df.entry_utc<b)].to_dict("records")
        result["periods"][name]=stats(part)
    # Hard, predeclared gates. No tuning on forward/OOS.
    f=result["periods"]["forward"]; o=result["periods"]["oos2026"]
    result["gates"]={
      "forward_min_100_trades":bool(f["trades"]>=100),
      "forward_pf_at_least_1_15":bool(f["pf"] is not None and f["pf"]>=1.15),
      "oos_min_20_trades":bool(o["trades"]>=20),
      "oos_pf_at_least_1_10":bool(o["pf"] is not None and o["pf"]>=1.10)}
    result["verdict"]="PASS" if all(result["gates"].values()) else "FAIL"
    OUT.mkdir(exist_ok=True)
    (OUT/"R251_fx_lead_lag_results.json").write_text(json.dumps(result,indent=2,allow_nan=False))
    if not df.empty: df.to_csv(OUT/"R251_fx_lead_lag_trades.csv",index=False)
    print(json.dumps(result,indent=2,allow_nan=False))
    print("R251 FINAL VERDICT:",result["verdict"])

if __name__=="__main__": main()
