#!/usr/bin/env python3
"""R275: locked R189/L80 EURUSD M1 strategy under exact T+1 vs T+6 entry.
Run locally against the archived Dukascopy BID/ASK ZIP; calculations exclude 2026.
"""
from __future__ import annotations
import argparse, hashlib, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

PIP=0.0001
SL=6.0
TP=18.0
MFE_TRIGGER=6.0
TRAIL=0.0
TIME_STOP_BARS=60
MAX_SPREAD_PIPS=1.5
COSTS=[0.2,0.5,1.0,2.0]
SEED=2752026

def sha256_file(p):
    h=hashlib.sha256()
    with Path(p).open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()

def load_data(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        manifest=json.loads(z.read("manifest.json"))
        def read(side):
            name=f"eurusd_{side}_M1_2016-2025.csv.gz"
            with z.open(name) as f: raw=pd.read_csv(f,compression="gzip")
            raw.columns=[str(c).strip().lower().replace("\ufeff","") for c in raw.columns]
            required={"timestamp","open","high","low","close"}
            if not required.issubset(raw.columns): raise ValueError(f"{side} missing columns: {required-set(raw.columns)}")
            raw["timestamp"]=pd.to_numeric(raw.timestamp,errors="raise").astype("int64")
            return raw.set_index("timestamp").sort_index()[["open","high","low","close"]].astype(float)
        bid,ask=read("bid"),read("ask")
    br,ar=len(bid),len(ask)
    db,da=int(bid.index.duplicated().sum()),int(ask.index.duplicated().sum())
    bid=bid.loc[~bid.index.duplicated(keep="last")]
    ask=ask.loc[~ask.index.duplicated(keep="last")]
    common=bid.index.intersection(ask.index).sort_values()
    bid,ask=bid.loc[common].copy(),ask.loc[common].copy()
    if len(common)<1_000_000: raise RuntimeError(f"Too few common timestamps: {len(common)}")
    def invalid(df):
        return ~((df.high>=df[["open","close"]].max(axis=1)) & (df.low<=df[["open","close"]].min(axis=1)) & (df.high>=df.low))
    badb,bada=int(invalid(bid).sum()),int(invalid(ask).sum())
    valid=~(invalid(bid).to_numpy()|invalid(ask).to_numpy())
    bid,ask=bid.iloc[np.flatnonzero(valid)].copy(),ask.iloc[np.flatnonzero(valid)].copy()
    common=bid.index
    if not common.equals(ask.index): raise RuntimeError("BID/ASK timestamps lost alignment")
    spreads=(ask.open.to_numpy()-bid.open.to_numpy())/PIP
    if np.any(spreads < -1e-9): raise RuntimeError("Negative opening spread found")
    npre=len(common)
    # The source collector used -fl. Remove only the conservative paired flat-candidate pattern:
    # both sides are flat, equal their own previous close, and exactly one minute apart.
    flatb=(bid.open.to_numpy()==bid.high.to_numpy())&(bid.high.to_numpy()==bid.low.to_numpy())&(bid.low.to_numpy()==bid.close.to_numpy())
    flata=(ask.open.to_numpy()==ask.high.to_numpy())&(ask.high.to_numpy()==ask.low.to_numpy())&(ask.low.to_numpy()==ask.close.to_numpy())
    t=common.to_numpy(dtype=np.int64)
    onemin=np.r_[False,np.diff(t)==60000]
    prevb=np.r_[np.nan,bid.close.to_numpy()[:-1]]
    preva=np.r_[np.nan,ask.close.to_numpy()[:-1]]
    copyb=np.isclose(bid.open.to_numpy(),prevb,rtol=0,atol=1e-12)
    copya=np.isclose(ask.open.to_numpy(),preva,rtol=0,atol=1e-12)
    synth=flatb&flata&copyb&copya&onemin
    removed=int(synth.sum())
    keep=~synth
    bid,ask=bid.iloc[np.flatnonzero(keep)].copy(),ask.iloc[np.flatnonzero(keep)].copy()
    common=bid.index
    spreads=(ask.open.to_numpy()-bid.open.to_numpy())/PIP
    if np.any(spreads < -1e-9): raise RuntimeError("Negative opening spread after filter")
    audit={
      "source_archive":"EURUSD-M1-Dukascopy-BID-ASK-2016-2025; GitHub Actions artifact 11959096102",
      "archive_sha256":sha256_file(zip_path),"manifest_status":manifest.get("status"),
      "manifest_scope_note":manifest.get("important_scope_note"),"requested_window_utc":manifest.get("requested_window_utc"),
      "bid_rows_before_alignment":int(br),"ask_rows_before_alignment":int(ar),"common_rows_before_filter":int(npre),
      "duplicate_bid_timestamps_removed":db,"duplicate_ask_timestamps_removed":da,
      "invalid_bid_ohlc_rows_removed":badb,"invalid_ask_ohlc_rows_removed":bada,
      "candidate_synthetic_flat_rows_removed":removed,"candidate_synthetic_flat_pct_of_common":float(removed/npre*100),
      "paired_rows_after_filter":int(len(common)),
      "start_utc":pd.to_datetime(common[0],unit="ms",utc=True).isoformat(),
      "end_utc":pd.to_datetime(common[-1],unit="ms",utc=True).isoformat(),
      "opening_spread_pips":{"min":float(np.min(spreads)),"median":float(np.median(spreads)),"p95":float(np.quantile(spreads,.95)),"max":float(np.max(spreads))},
      "known_data_limit":"Archive collected with -fl; synthetic-flat candidate removal is heuristic, not proof all synthetic bars were removed. Any positive result needs a fresh verified no-flat feed."
    }
    return bid,ask,audit

def gen_signals(bid):
    close=bid.close.to_numpy(float); op=bid.open.to_numpy(float); n=len(close)
    utc=pd.to_datetime(bid.index,unit="ms",utc=True)
    wall=((utc.hour.to_numpy()-5)%24)
    step=np.sign(np.diff(close,prepend=np.nan))
    pos=(step==1).astype(np.int32); neg=(step==-1).astype(np.int32)
    ppos=np.r_[0,np.cumsum(pos,dtype=np.int64)]; pneg=np.r_[0,np.cumsum(neg,dtype=np.int64)]
    body=np.abs(close-op); d5=np.full(n,np.nan); d5[5:]=close[5:]-close[:-5]
    cand=[]; hours=(wall>=3)&(wall<=11)&(wall!=6)&(wall!=9)
    for w in (11,12):
        d=np.full(n,np.nan); d[w:]=close[w:]-close[:-w]
        with np.errstate(divide="ignore",invalid="ignore"): late=np.abs(d5)/np.abs(d)
        pc=np.zeros(n,dtype=np.int64); nc=np.zeros(n,dtype=np.int64); valid=np.arange(w,n)
        pc[valid]=ppos[valid+1]-ppos[valid-w+1]
        nc[valid]=pneg[valid+1]-pneg[valid-w+1]
        ds=np.sign(d); same=np.where(ds>0,pc,np.where(ds<0,nc,0))
        ok=hours&(np.abs(d)>=15*PIP)&(body>=2*PIP)&(late>=0.80)&(same>=7)
        for i in np.flatnonzero(ok):
            if i+1<n: cand.append((int(i),1 if d[i]<0 else -1,"L80"))
    cand.sort(key=lambda x:x[0]); out=[]; last=-10**18
    for item in cand:
        if item[0]-last>14: out.append(item); last=item[0]
    return out

def pf(values):
    a=np.asarray(values,float); gp=float(a[a>0].sum()); gl=float(-a[a<0].sum())
    return (float("inf") if gp>0 else None) if gl==0 else gp/gl

def max_dd(values):
    a=np.asarray(values,float)
    if len(a)==0:return 0.0
    eq=np.cumsum(a); peaks=np.maximum.accumulate(np.r_[0.0,eq])
    return float(np.max(peaks[1:]-eq))

def simulate(bid,ask,signals,delay_minutes):
    ts=bid.index.to_numpy(dtype=np.int64)
    bo,bh,bl=(bid[c].to_numpy(float) for c in ("open","high","low"))
    ao,ah,al=(ask[c].to_numpy(float) for c in ("open","high","low"))
    spr=(ao-bo)/PIP
    trades=[]; diag={"signals_received":len(signals),"missing_exact_entry_timestamp":0,"spread_rejected":0,"overlap_skipped":0,"end_censored":0,"entered":0}
    active_exit=-1; delay_ms=delay_minutes*60000
    for si,direction,_src in signals:
        wanted=ts[si]+delay_ms; e=int(np.searchsorted(ts,wanted))
        if e>=len(ts) or ts[e]!=wanted: diag["missing_exact_entry_timestamp"]+=1; continue
        if not np.isfinite(spr[e]) or spr[e]<-1e-9 or spr[e]>MAX_SPREAD_PIPS+1e-12:
            diag["spread_rejected"]+=1; continue
        if e<=active_exit: diag["overlap_skipped"]+=1; continue
        entry=float(ao[e] if direction==1 else bo[e])
        hard=entry-direction*SL*PIP; target=entry+direction*TP*PIP
        stop=hard; fav=entry; trail_active=False; scheduled=e+TIME_STOP_BARS
        if scheduled>=len(ts): diag["end_censored"]+=1; active_exit=len(ts); continue
        exit_i=exit_px=gross=reason=None
        for j in range(e,scheduled):
            current=stop if trail_active else hard
            # Resolve opening gaps before intrabar extremes; fills use executable quote side.
            if direction==1:
                if bo[j]<=current: exit_i=j; exit_px=bo[j]; gross=(exit_px-entry)/PIP; reason="TRAIL_STOP" if trail_active else "STOP_GAP"; break
                if bo[j]>=target: exit_i=j; exit_px=bo[j]; gross=(exit_px-entry)/PIP; reason="TARGET_GAP"; break
                if bl[j]<=current: exit_i=j; exit_px=current; gross=(exit_px-entry)/PIP; reason="TRAIL_STOP" if trail_active else "STOP"; break
                if bh[j]>=target: exit_i=j; exit_px=target; gross=(exit_px-entry)/PIP; reason="TARGET"; break
                fav=max(fav,bh[j]); favourable=(fav-entry)/PIP
                if favourable>=MFE_TRIGGER:
                    new=entry+(favourable-TRAIL)*PIP
                    if new>stop: stop=new
                    trail_active=True
            else:
                if ao[j]>=current: exit_i=j; exit_px=ao[j]; gross=(entry-exit_px)/PIP; reason="TRAIL_STOP" if trail_active else "STOP_GAP"; break
                if ao[j]<=target: exit_i=j; exit_px=ao[j]; gross=(entry-exit_px)/PIP; reason="TARGET_GAP"; break
                if ah[j]>=current: exit_i=j; exit_px=current; gross=(entry-exit_px)/PIP; reason="TRAIL_STOP" if trail_active else "STOP"; break
                if al[j]<=target: exit_i=j; exit_px=target; gross=(entry-exit_px)/PIP; reason="TARGET"; break
                fav=min(fav,al[j]); favourable=(entry-fav)/PIP
                if favourable>=MFE_TRIGGER:
                    new=entry-(favourable-TRAIL)*PIP
                    if not trail_active or new<stop: stop=new
                    trail_active=True
        if exit_i is None:
            exit_i=scheduled; exit_px=float(bo[exit_i] if direction==1 else ao[exit_i])
            gross=direction*(exit_px-entry)/PIP; reason="TIME_OPEN_CAUSAL"
        iso=lambda q:pd.to_datetime(q,unit="ms",utc=True).isoformat()
        trades.append({"signal_utc":iso(ts[si]),"entry_utc":iso(ts[e]),"exit_utc":iso(ts[exit_i]),
          "direction":"LONG" if direction==1 else "SHORT","delay_minutes":delay_minutes,"entry_price":entry,
          "entry_spread_pips":float(spr[e]),"exit_reason":reason,"gross_pips":float(gross),
          "bars_held":int(exit_i-e),"engine":"causal_gap_adverse_fill"})
        diag["entered"]+=1; active_exit=exit_i
    return trades,diag

def trade_net(trades,cost): return np.asarray([x["gross_pips"]-cost for x in trades],float)

def summarize(trades,cost,lo=None,hi=None):
    x=trades
    if lo is not None: x=[t for t in x if lo<=pd.Timestamp(t["entry_utc"])<hi and pd.Timestamp(t["exit_utc"])<hi]
    a=trade_net(x,cost); weeks=(hi-lo).total_seconds()/(7*24*3600) if lo is not None else None
    if weeks is None and len(x)>1: weeks=max((pd.Timestamp(x[-1]["entry_utc"])-pd.Timestamp(x[0]["entry_utc"])).total_seconds()/(7*24*3600),1/7)
    return {"trades":int(len(a)),"PF":pf(a),"net_pips":float(a.sum()) if len(a) else 0.0,
      "max_drawdown_pips":max_dd(a),"win_rate":float(np.mean(a>0)) if len(a) else None,
      "mean_net_pips_per_trade":float(a.mean()) if len(a) else None,"median_net_pips_per_trade":float(np.median(a)) if len(a) else None,
      "trades_per_week":float(len(a)/weeks) if weeks else None}

def subperiod(trades,lo,hi):
    lo=pd.Timestamp(lo,tz="UTC"); hi=pd.Timestamp(hi,tz="UTC")
    entered=[t for t in trades if lo<=pd.Timestamp(t["entry_utc"])<hi]
    complete=[t for t in entered if pd.Timestamp(t["exit_utc"])<hi]
    return complete,len(entered)-len(complete)

def weekly_bootstrap(trades,lo,hi,cost,reps=10000,block=4,seed=SEED):
    lo=pd.Timestamp(lo,tz="UTC"); hi=pd.Timestamp(hi,tz="UTC")
    weeks=int(np.ceil((hi-lo).total_seconds()/(7*24*3600))); weekly=np.zeros(weeks,float)
    for t in trades:
        et=pd.Timestamp(t["entry_utc"])
        if lo<=et<hi and pd.Timestamp(t["exit_utc"])<hi:
            k=min(int((et-lo).total_seconds()/(7*24*3600)),weeks-1); weekly[k]+=t["gross_pips"]-cost
    rng=np.random.default_rng(seed); means=np.empty(reps); n=len(weekly)
    for r in range(reps):
        seq=[]
        while len(seq)<n:
            s=int(rng.integers(0,n)); seq.extend(weekly[(s+np.arange(block))%n].tolist())
        means[r]=np.mean(seq[:n])
    ntrades=sum(1 for t in trades if lo<=pd.Timestamp(t["entry_utc"])<hi and pd.Timestamp(t["exit_utc"])<hi)
    return {"trades":int(ntrades),"calendar_weeks":n,"block_weeks":block,"replicates":reps,"seed":seed,
      "observed_mean_net_pips_per_week":float(weekly.mean()),"ci95_mean_weekly_net_pips":[float(x) for x in np.quantile(means,[.025,.975])],
      "probability_mean_weekly_net_positive":float(np.mean(means>0))}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-zip",default="/mnt/data/eurusd_m1_bid_ask.zip")
    ap.add_argument("--out-dir",default="/mnt/data/r275_outputs")
    args=ap.parse_args(); data=Path(args.data_zip); out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    bid,ask,audit=load_data(data); signals=gen_signals(bid)
    parent,dp=simulate(bid,ask,signals,1); child,dc=simulate(bid,ask,signals,6)
    periods={"discovery_2016_2020":("2016-01-01","2021-01-01"),"validation_2021":("2021-01-01","2022-01-01"),
      "exploratory_forward_2022_2025":("2022-01-01","2026-01-01"),"full_2016_2025":("2016-01-01","2026-01-01")}
    result={"round":"R275","status":"COMPLETE","candidate":"R189/L80 with exact five-minute manual delay after M1 candle close",
      "preregistration":"research/R275_R189_L80_MOBILE_DELAY_PREREGISTRATION.md","verdict":"GAGAL","data_audit":audit,
      "locked_rules":{"signal":"exact R189 L80; no parameter changes","parent_entry_delay_minutes_after_signal_bar_open":1,
       "child_entry_delay_minutes_after_signal_bar_open":6,"exact_timestamp_required":True,"SL_pips":SL,"TP_pips":TP,
       "MFE_trigger_pips":MFE_TRIGGER,"trailing_distance_pips":TRAIL,"time_stop_observed_bars":TIME_STOP_BARS,
       "entry_spread_max_pips":MAX_SPREAD_PIPS,"extra_cost_pips":COSTS,"periods":periods},
      "signal_stream":{"signals_before_entry_filters":len(signals)},
      "parent_T_plus_1":{"execution_diagnostics":dp,"full_sample_cost_stress":{str(c):summarize(parent,c) for c in COSTS},"periods":{}},
      "child_T_plus_6":{"execution_diagnostics":dc,"full_sample_cost_stress":{str(c):summarize(child,c) for c in COSTS},"periods":{}}}
    for name,(lo,hi) in periods.items():
        start,end=pd.Timestamp(lo,tz="UTC"),pd.Timestamp(hi,tz="UTC")
        p,px=subperiod(parent,lo,hi); ch,cx=subperiod(child,lo,hi)
        result["parent_T_plus_1"]["periods"][name]={"cross_boundary_exits_excluded":px,"cost_stress":{str(c):summarize(p,c,start,end) for c in COSTS}}
        result["child_T_plus_6"]["periods"][name]={"cross_boundary_exits_excluded":cx,"cost_stress":{str(c):summarize(ch,c,start,end) for c in COSTS}}
    years={}
    for y in range(2016,2026):
        lo=f"{y}-01-01"; hi=f"{y+1}-01-01"; yy,_=subperiod(child,lo,hi)
        years[str(y)]={str(c):summarize(yy,c,pd.Timestamp(lo,tz="UTC"),pd.Timestamp(hi,tz="UTC")) for c in COSTS}
    result["child_T_plus_6"]["annual_metrics"]=years
    boot=weekly_bootstrap(child,"2022-01-01","2026-01-01",1.0)
    result["child_T_plus_6"]["weekly_bootstrap_forward_2022_2025_plus_1pip"]=boot
    fw=result["child_T_plus_6"]["periods"]["exploratory_forward_2022_2025"]["cost_stress"]
    gates={"forward_trades_ge_100":fw["1.0"]["trades"]>=100,
      "forward_PF_ge_1p10_at_plus_1pip":fw["1.0"]["PF"] is not None and fw["1.0"]["PF"]>=1.10,
      "forward_PF_ge_1p05_at_plus_2pip":fw["2.0"]["PF"] is not None and fw["2.0"]["PF"]>=1.05,
      "every_year_with_20plus_trades_PF_ge_1_at_plus_1pip":all(v["1.0"]["PF"] is not None and v["1.0"]["PF"]>=1.0 for v in years.values() if v["1.0"]["trades"]>=20),
      "weekly_bootstrap_95pct_lower_gt_zero_at_plus_1pip":boot["ci95_mean_weekly_net_pips"][0]>0}
    result["child_T_plus_6"]["locked_gates"]=gates
    result["child_T_plus_6"]["verdict"]="LULUS_DIAGNOSTIK_SEMENTARA" if all(gates.values()) else "GAGAL"
    result["interpretation_limit"]="Exploratory screen only: 2022–2025 is contaminated, archive used -fl with heuristic flat-row filtering, and full challenge-rule/Quick Strike audit is not part of this run."
    (out/"R275_results_compact.json").write_text(json.dumps(result,indent=2),encoding="utf-8")
    pd.DataFrame(child).to_csv(out/"R275_child_T_plus_6_trades.csv",index=False)
    pd.DataFrame(parent).to_csv(out/"R275_parent_T_plus_1_trades.csv",index=False)
    print(json.dumps({"rows_after_filter":audit["paired_rows_after_filter"],"flat_candidates_removed":audit["candidate_synthetic_flat_rows_removed"],
      "signals":len(signals),"parent_diag":dp,"child_diag":dc,
      "parent_forward_plus1":result["parent_T_plus_1"]["periods"]["exploratory_forward_2022_2025"]["cost_stress"]["1.0"],
      "child_forward_plus1":fw["1.0"],"child_forward_plus2":fw["2.0"],"bootstrap":boot,"gates":gates,
      "verdict":result["child_T_plus_6"]["verdict"],"output_dir":str(out)},indent=2))

if __name__=="__main__": main()
