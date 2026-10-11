#!/usr/bin/env python3
"""R214: H4 three-bar impulse exhaustion + structural reversal, local Python engine."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit

ASSETS = {
    "usa500idxusd":"USA 500 / S&P 500", "usatechidxusd":"USA 100 Tech / Nasdaq 100",
    "usa30idxusd":"USA 30 / Dow Jones", "ussc2000idxusd":"US Small Cap 2000",
    "deuidxeur":"Germany 40 / DAX", "gbridxgbp":"FTSE 100", "fraidxeur":"France 40 / CAC 40",
    "eusidxeur":"EU Stocks 50", "ausidxaud":"Australia 200", "jpnidxjpy":"Japan 200+",
}
RR=2.0
D0=pd.Timestamp("2017-01-01",tz="UTC"); D1=pd.Timestamp("2022-01-01",tz="UTC")
F0=D1; F1=pd.Timestamp("2026-01-01",tz="UTC"); O0=F1
RULE={
 "id":"R214_H4_THREE_BAR_IMPULSE_STRUCTURE_REVERSAL_RR2",
 "long":"Three prior completed H4 candles bearish with strictly descending closes; current completed H4 candle bullish and closes above prior H4 high.",
 "short":"Three prior completed H4 candles bullish with strictly ascending closes; current completed H4 candle bearish and closes below prior H4 low.",
 "h4":"UTC 00/04/08/12/16/20, only exact four consecutive H1 source bars, incomplete bins skipped; no fill or forward-fill.",
 "entry":"First non-flat M5 BID open at or after signal H4 close +5 minutes and strictly before next scheduled H4 close.",
 "stop":"Signal H4 low for long; signal H4 high for short.",
 "target":"2R from actual entry-to-stop risk.",
 "execution":"One position per instrument; M5 BID OHLC; SL checked before TP; stop gaps filled at available open; flat synthetic M5 bars skipped; open trades censored at data end.",
 "cost":"Modeled round-trip price cost entry*1bp and entry*2bp; not measured spread/commission/financing/live slippage.",
 "selection":"Discovery only: >=30 closed and PF@2bp >=1.00; choose fewest trades, then higher PF@2bp; no forward-based replacement.",
 "periods":{"discovery":"2017–2021, exits strictly before 2022-01-01 UTC","forward":"2022–2025, exits strictly before 2026-01-01 UTC","oos":"2026 through common data cutoff"}
}

def load_csv(path:Path):
    x=pd.read_csv(path)
    x.columns=[str(c).replace("\ufeff","").strip().lower() for c in x.columns]
    tc=next((c for c in ("timestamp","time","t","date","datetime") if c in x.columns),None)
    if tc is None: raise ValueError(f"Missing timestamp column: {path}")
    ts=x.pop(tc); num=pd.to_numeric(ts,errors="coerce")
    if num.notna().mean()>.95:
        med=float(num.abs().median())
        if med>=1e11: idx=pd.to_datetime(num,unit="ms",utc=True,errors="coerce")
        elif med>=1e8: idx=pd.to_datetime(num,unit="s",utc=True,errors="coerce")
        else: raise ValueError(f"Unknown timestamp numeric scale {med}: {path}")
    else: idx=pd.to_datetime(ts,utc=True,errors="coerce")
    cols=["open","high","low","close"]
    if idx.isna().any() or set(cols)-set(x.columns): raise ValueError(f"Invalid timestamp/OHLC columns: {path}")
    x=x[cols].apply(pd.to_numeric,errors="coerce")
    if x.isna().any().any() or not np.isfinite(x.to_numpy(float)).all(): raise ValueError(f"Invalid OHLC values: {path}")
    x.index=pd.DatetimeIndex(idx,name="timestamp_utc"); x=x.sort_index()
    dup=int(x.index.duplicated(keep="last").sum())
    if dup: x=x.loc[~x.index.duplicated(keep="last")]
    if not x.index.is_monotonic_increasing or x.index.has_duplicates: raise ValueError(f"Timestamp index invalid: {path}")
    if path.stem.endswith("_h1"):
        off=int(((x.index.minute!=0)|(x.index.second!=0)|(x.index.microsecond!=0)).sum())
    elif path.stem.endswith("_m5"):
        off=int(((x.index.minute%5!=0)|(x.index.second!=0)|(x.index.microsecond!=0)).sum())
    else: raise ValueError(f"Filename must end in _h1 or _m5: {path}")
    if off: raise ValueError(f"Off-grid timestamps ({off}): {path}")
    o=x.open.to_numpy(float); h=x.high.to_numpy(float); l=x.low.to_numpy(float); c=x.close.to_numpy(float)
    bad=(h<np.maximum(o,c))|(l>np.minimum(o,c))|(h<l)|~np.isfinite(np.vstack([o,h,l,c])).all(axis=0)
    if bad.any(): raise ValueError(f"Invalid OHLC relationship ({int(bad.sum())}): {path}")
    flat=(o==h)&(h==l)&(l==c)
    meta={"path":path.name,"rows":len(x),"duplicates_removed":dup,"off_grid_timestamps":off,
          "start_utc":x.index[0].isoformat(),"end_utc":x.index[-1].isoformat(),
          "flat_rows":int(flat.sum()),"invalid_ohlc_rows":int(bad.sum())}
    return x,flat,meta

def build_h4_utc(h1,cutoff):
    idx=h1.sort_index().index.tz_convert("UTC"); ns=idx.asi8; hour=np.int64(3600*10**9)
    starts=np.flatnonzero((idx.minute==0)&(idx.second==0)&(idx.hour%4==0))
    starts=starts[starts+3<len(idx)]
    good=starts[(ns[starts+1]==ns[starts]+hour)&(ns[starts+2]==ns[starts]+2*hour)&(ns[starts+3]==ns[starts]+3*hour)]
    labels=idx.take(good); rights=labels+pd.Timedelta(hours=4)
    o=h1.open.to_numpy(float); h=h1.high.to_numpy(float); l=h1.low.to_numpy(float); c=h1.close.to_numpy(float)
    out=pd.DataFrame({"bar_close_utc":rights,"open":o[good],
        "high":np.maximum.reduce([h[good],h[good+1],h[good+2],h[good+3]]),
        "low":np.minimum.reduce([l[good],l[good+1],l[good+2],l[good+3]]),
        "close":c[good+3],"completed":np.asarray(rights<=cutoff,dtype=bool),
        "source_h1_count":np.full(len(good),4,dtype=np.int8)},index=pd.DatetimeIndex(labels,tz="UTC",name="label_utc"))
    expected=max(0,len(pd.date_range(idx[0].floor("4h"),idx[-1].floor("4h")+pd.Timedelta(hours=4),freq="4h"))-1)
    return out,{"h4_bars":len(out),"h4_completed_bars":int(out.completed.sum()),
        "h4_incomplete_or_missing_bins_skipped":int(expected-len(out)),
        "h4_start_utc":out.index[0].isoformat(),"h4_last_close_utc":out.bar_close_utc.iloc[-1].isoformat(),
        "h4_anchor":"UTC 00/04/08/12/16/20; exact four consecutive H1 bars"}

def signals_stops(h4):
    o=h4.open.to_numpy(float); hi=h4.high.to_numpy(float); lo=h4.low.to_numpy(float); c=h4.close.to_numpy(float)
    sig=np.zeros(len(h4),dtype=np.int8); st=np.full(len(h4),np.nan)
    for i in range(3,len(h4)):
        dn=(c[i-3]<o[i-3] and c[i-2]<o[i-2] and c[i-1]<o[i-1] and c[i-1]<c[i-2]<c[i-3])
        up=(c[i-3]>o[i-3] and c[i-2]>o[i-2] and c[i-1]>o[i-1] and c[i-1]>c[i-2]>c[i-3])
        if dn and c[i]>o[i] and c[i]>hi[i-1]: sig[i]=1; st[i]=lo[i]
        elif up and c[i]<o[i] and c[i]<lo[i-1]: sig[i]=-1; st[i]=hi[i]
    return sig,st

def truncation_gate(h4,sig,st):
    o=h4.open.to_numpy(float); hi=h4.high.to_numpy(float); lo=h4.low.to_numpy(float); c=h4.close.to_numpy(float)
    checked=0
    for i in np.flatnonzero(h4.completed.to_numpy(bool)):
        checked+=1; sd=0; stop=np.nan
        if i>=3:
            dn=(c[i-3]<o[i-3] and c[i-2]<o[i-2] and c[i-1]<o[i-1] and c[i-1]<c[i-2]<c[i-3])
            up=(c[i-3]>o[i-3] and c[i-2]>o[i-2] and c[i-1]>o[i-1] and c[i-1]>c[i-2]>c[i-3])
            if dn and c[i]>o[i] and c[i]>hi[i-1]: sd=1; stop=lo[i]
            elif up and c[i]<o[i] and c[i]<lo[i-1]: sd=-1; stop=hi[i]
        if sd!=int(sig[i]): return {"pass":False,"checked":checked,"bar":int(i),"reason":"signal mismatch"}
        if sd and not np.isclose(stop,float(st[i]),rtol=0,atol=1e-12):
            return {"pass":False,"checked":checked,"bar":int(i),"reason":"stop mismatch"}
    return {"pass":True,"checked":checked,"reason":"all completed H4 prefixes match independent recomputation"}

@njit
def _sim(hclose,completed,sig,st,mt,op,hi,lo,flat):
    cap=len(hclose); oi=np.full(cap,-1,np.int64); ej=np.full(cap,-1,np.int64); xj=np.full(cap,-1,np.int64)
    ep=np.full(cap,np.nan); xp=np.full(cap,np.nan); sl=np.full(cap,np.nan); tp=np.full(cap,np.nan); risk=np.full(cap,np.nan)
    why=np.zeros(cap,np.int8); n=0; active=0; nofill=0; badrisk=0; last_exit=np.int64(-1)
    five=np.int64(5*60*10**9); four=np.int64(4*60*60*10**9)
    for i in range(len(hclose)):
        if not completed[i] or sig[i]==0: continue
        if last_exit!=-1 and not last_exit<hclose[i]: active+=1; continue
        left=np.searchsorted(mt,hclose[i]+five); right=np.searchsorted(mt,hclose[i]+four)
        j=left
        while j<right and j<len(mt) and flat[j]: j+=1
        if j>=right or j>=len(mt): nofill+=1; continue
        d=sig[i]; en=op[j]; stop=st[i]; r=(en-stop) if d==1 else (stop-en)
        if not math.isfinite(r) or r<=0: badrisk+=1; continue
        target=en+d*2.0*r; kx=-1; px=np.nan; reason=np.int8(4)
        for k in range(j,len(mt)):
            if flat[k]: continue
            oo=op[k]; hh=hi[k]; ll=lo[k]
            stop_hit=(ll<=stop or oo<=stop) if d==1 else (hh>=stop or oo>=stop)
            tgt_hit=(hh>=target) if d==1 else (ll<=target)
            if stop_hit:
                gap=(oo<=stop) if d==1 else (oo>=stop); px=oo if gap else stop
                reason=np.int8(3 if gap else 1); kx=k; break
            if tgt_hit: px=target; reason=np.int8(2); kx=k; break
        oi[n]=i; ej[n]=j; xj[n]=kx; ep[n]=en; xp[n]=px; sl[n]=stop; tp[n]=target; risk[n]=r; why[n]=reason; n+=1
        if kx<0: last_exit=np.int64(9223372036854775807); break
        last_exit=mt[kx]+five
    return oi[:n],ej[:n],xj[:n],ep[:n],xp[:n],sl[:n],tp[:n],risk[:n],why[:n],active,nofill,badrisk

def simulate(h4,m5,flat,sig,st,inst):
    mt=m5.index.tz_convert("UTC"); ns=mt.asi8.astype(np.int64); closes=pd.DatetimeIndex(h4.bar_close_utc).tz_convert("UTC").asi8.astype(np.int64)
    z=_sim(closes,h4.completed.to_numpy(bool),np.asarray(sig,np.int8),np.asarray(st,float),ns,
        m5.open.to_numpy(float),m5.high.to_numpy(float),m5.low.to_numpy(float),np.asarray(flat,bool))
    ii,ee,xx,ep,xp,sl,tp,risk,why,active,nofill,badrisk=z; labels={1:"SL",2:"TP",3:"SL_GAP_OPEN",4:"OPEN_AT_DATA_END"}; trades=[]
    for q in range(len(ii)):
        i=int(ii[q]); j=int(ee[q]); k=int(xx[q]); d=int(sig[i]); xt=None if k<0 else mt[k]+pd.Timedelta(minutes=5)
        trades.append({"instrument":inst,"instrument_name":ASSETS[inst],"config":RULE["id"],
          "direction":"long" if d==1 else "short","signal_bar_utc":h4.index[i].isoformat(),
          "signal_close_utc":pd.Timestamp(int(closes[i]),tz="UTC").isoformat(),"entry_time_utc":mt[j].isoformat(),
          "entry":float(ep[q]),"sl":float(sl[q]),"tp":float(tp[q]),"risk_points":float(risk[q]),
          "exit_time_utc":None if xt is None else xt.isoformat(),"exit":None if k<0 else float(xp[q]),
          "reason":labels[int(why[q])],"bars_held":None if k<0 else k-j+1})
    return trades,{"signals":int(((np.asarray(sig)!=0)&h4.completed.to_numpy(bool)).sum()),"taken":len(trades),
        "skipped_active":int(active),"skipped_no_fill":int(nofill),"skipped_invalid_risk":int(badrisk)}

def finite(x): return isinstance(x,(int,float,np.integer,np.floating)) and math.isfinite(float(x))
def pnl_r(t,bps):
    if t["exit"] is None: return np.nan
    d=1 if t["direction"]=="long" else -1
    return (d*(float(t["exit"])-float(t["entry"]))-float(t["entry"])*bps/10000.0)/float(t["risk_points"])
def metric(tr,start,end,cutoff,bps):
    picked=[t for t in tr if start<=pd.Timestamp(t["entry_time_utc"])<end]
    closed=[t for t in picked if t["exit_time_utc"] is not None and pd.Timestamp(t["exit_time_utc"])<cutoff]
    v=np.asarray([pnl_r(t,bps) for t in closed],float); wins=float(v[v>0].sum()) if len(v) else 0.; losses=float(-v[v<0].sum()) if len(v) else 0.
    pf=wins/losses if losses>0 else (float("inf") if wins>0 else float("nan"))
    return {"entries":len(picked),"closed":len(closed),"censored":len(picked)-len(closed),"pf":pf,"wins_r":wins,"losses_r":losses}
def safe(x):
    if isinstance(x,dict): return {str(k):safe(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [safe(v) for v in x]
    if isinstance(x,np.integer): return int(x)
    if isinstance(x,(np.floating,float)):
        if math.isnan(float(x)): return None
        if math.isinf(float(x)): return "INF" if x>0 else "-INF"
        return float(x)
    return x

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--data-dir",default="/mnt/data/r205_snapshot"); ap.add_argument("--out",default="/mnt/data/r214_local_results")
    args=ap.parse_args(); data=Path(args.data_dir); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    dataobj={}; source_meta={}
    for inst in ASSETS:
        h1,h1flat,h1meta=load_csv(data/f"{inst}_h1.csv"); m5,m5flat,m5meta=load_csv(data/f"{inst}_m5.csv")
        dataobj[inst]={"h1":h1,"m5":m5,"flat":m5flat}; source_meta[inst]={"h1":h1meta,"m5":m5meta}
    m5_end=min(v["m5"].index[-1]+pd.Timedelta(minutes=5) for v in dataobj.values())
    h1_end=min(v["h1"].index[-1]+pd.Timedelta(hours=1) for v in dataobj.values())
    signal_end=min(m5_end,h1_end); h4s={}; h4diag={}; gates={}; discovered={}; disc_rows=[]
    for inst,v in dataobj.items():
        h4,hm=build_h4_utc(v["h1"],min(signal_end,v["h1"].index[-1]+pd.Timedelta(hours=1),v["m5"].index[-1]+pd.Timedelta(minutes=5)))
        sig,st=signals_stops(h4); gate=truncation_gate(h4,sig,st); gates[inst]=gate; h4diag[inst]=hm
        if not gate["pass"]: raise SystemExit(f"TRUNCATION GATE FAILED {inst}: {gate}")
        h4s[inst]=(h4,sig,st)
        m5=v["m5"]; mask=m5.index.tz_convert("UTC")<D1; dm=m5.loc[mask]; flat=v["flat"][np.asarray(mask)]
        dc=min(D1,dm.index[-1]+pd.Timedelta(minutes=5)); dh=h4.loc[(h4.bar_close_utc<=dc).to_numpy()]
        tr,diag=simulate(dh,dm,flat,sig[:len(dh)],st[:len(dh)],inst); discovered[inst]=tr
        for bps in (1,2): disc_rows.append({"instrument":inst,"instrument_name":ASSETS[inst],"cost_bps_rt":bps,**metric(tr,D0,D1,D1,bps),**diag})
    select=[]
    for inst,tr in discovered.items():
        a=metric(tr,D0,D1,D1,1); b=metric(tr,D0,D1,D1,2); eligible=b["closed"]>=30 and finite(b["pf"]) and b["pf"]>=1.
        select.append({"instrument":inst,"instrument_name":ASSETS[inst],"discovery_closed":b["closed"],"discovery_pf_1bp":a["pf"],"discovery_pf_2bp":b["pf"],"eligible":eligible})
    elig=sorted([r for r in select if r["eligible"]],key=lambda r:(r["discovery_closed"],-r["discovery_pf_2bp"],r["instrument"]))
    selected=dict(elig[0]) if elig else None; frows=[]; cohorts=[]; oos=[]; alltr=[]; verdict="REJECT_IN_DISCOVERY_NO_ELIGIBLE_INSTRUMENT"
    if selected:
        inst=selected["instrument"]; v=dataobj[inst]; h4,sig,st=h4s[inst]
        fcut=min(signal_end,v["h1"].index[-1]+pd.Timedelta(hours=1)); xcut=min(m5_end,v["m5"].index[-1]+pd.Timedelta(minutes=5))
        mask=v["m5"].index.tz_convert("UTC")<xcut; m5=v["m5"].loc[mask]; flat=v["flat"][np.asarray(mask)]
        hh=h4.loc[(h4.bar_close_utc<=fcut).to_numpy()]; tr,diag=simulate(hh,m5,flat,sig[:len(hh)],st[:len(hh)],inst); alltr=tr
        for bps in (1,2):
            frows.append({"instrument":inst,"instrument_name":ASSETS[inst],"cost_bps_rt":bps,**metric(tr,F0,F1,F1,bps)})
            oos.append({"instrument":inst,"instrument_name":ASSETS[inst],"cost_bps_rt":bps,**metric(tr,O0,m5_end,m5_end,bps)})
        for year in range(2022,2026):
            start=pd.Timestamp(f"{year}-01-01",tz="UTC"); end=pd.Timestamp(f"{year+1}-01-01",tz="UTC")
            for bps in (1,2): cohorts.append({"instrument":inst,"entry_year":year,"cost_bps_rt":bps,**metric(tr,start,end,F1,bps)})
        f1=next(r for r in frows if r["cost_bps_rt"]==1); f2=next(r for r in frows if r["cost_bps_rt"]==2)
        yc=[r for r in cohorts if r["cost_bps_rt"]==1 and r["closed"]>=5]; worst=min((r["pf"] for r in yc if finite(r["pf"])),default=None)
        countok=f1["closed"]>=30; pfok=finite(f1["pf"]) and f1["pf"]>=1.15 and finite(f2["pf"]) and f2["pf"]>=1.15
        yearok=bool(yc) and all(finite(r["pf"]) and r["pf"]>=1 for r in yc); normal=countok and pfok and yearok
        verdict="HOLD_EXTRA_AUDIT" if normal and (f1["pf"]>1.4 or f2["pf"]>1.4) else "PASS" if normal else "REJECT"
        selected.update({"forward_closed":f1["closed"],"forward_pf_1bp":f1["pf"],"forward_pf_2bp":f2["pf"],
          "worst_forward_entry_year_pf_1bp_n5plus":worst,"count_gate_pass":countok,"both_cost_pf_gate_pass":pfok,
          "annual_cohort_gate_pass":yearok,"verdict":verdict,"forward_diag":diag})
        for r in cohorts:
            r["cohort_gate_applicable"]=r["cost_bps_rt"]==1 and r["closed"]>=5
            r["cohort_gate_pass"]=None if not r["cohort_gate_applicable"] else bool(finite(r["pf"]) and r["pf"]>=1.)
        for r in oos: r["common_oos_cutoff_utc"]=m5_end.isoformat()
    def dumpcsv(name,rows): pd.DataFrame(rows).to_csv(out/name,index=False)
    dumpcsv("discovery_ledger.csv",disc_rows); dumpcsv("discovery_selection.csv",select)
    ann=[]
    for inst,tr in discovered.items():
        for year in range(2017,2022):
            start=pd.Timestamp(f"{year}-01-01",tz="UTC"); end=pd.Timestamp(f"{year+1}-01-01",tz="UTC")
            for bps in (1,2): ann.append({"instrument":inst,"entry_year":year,"cost_bps_rt":bps,**metric(tr,start,end,D1,bps)})
    dumpcsv("discovery_annual_cohorts.csv",ann); dumpcsv("selected_forward_ledger.csv",frows)
    dumpcsv("selected_forward_annual_cohorts.csv",cohorts); dumpcsv("selected_oos_ledger.csv",oos); dumpcsv("selected_all_trades.csv",alltr)
    meta={"research":"R214 H4 three-bar impulse exhaustion + confirmed structure reversal","rule":RULE,
      "run_type":"local Python execution; no Actions backtest launched","source":"R205 Dukascopy BID-only H1/M5 snapshots",
      "source_run_url":"https://github.com/christianomomongan82-lang/scanner/actions/runs/38160487617",
      "common_signal_cutoff_utc":signal_end.isoformat(),"common_oos_cutoff_utc":m5_end.isoformat(),
      "assets":source_meta,"h4_aggregation":h4diag,"truncation_gates":gates,"discovery_selection":select,"selected":selected,"verdict":verdict}
    (out/"meta.json").write_text(json.dumps(safe(meta),indent=2))
    print(pd.DataFrame(select).to_string(index=False)); print(pd.DataFrame(frows).to_string(index=False)); print(pd.DataFrame(cohorts).to_string(index=False)); print("VERDICT",verdict)

if __name__=="__main__": main()
