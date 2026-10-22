#!/usr/bin/env python3
"""R323 frozen FX currency-strength continuation test.

Default mode: local strategy computation only; expects the fourteen H1 BID/ASK CSVs
under dl/r323. --audit-only performs acquisition/data integrity checks only and never
constructs signals, trades, or PnL. No downloader or parameter search is included.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math, platform, sys
from pathlib import Path
from datetime import datetime, timezone
import numpy as np
import pandas as pd

PAIRS = ("eurusd", "gbpusd", "audusd", "nzdusd", "usdchf", "usdcad", "usdjpy")
CURRENCIES = ("AUD", "CAD", "CHF", "EUR", "GBP", "JPY", "NZD")
PAIR_FOR = {"EUR":"eurusd","GBP":"gbpusd","AUD":"audusd","NZD":"nzdusd",
            "CHF":"usdchf","CAD":"usdcad","JPY":"usdjpy"}
FOREIGN_IS_BASE = {"eurusd":True,"gbpusd":True,"audusd":True,"nzdusd":True,
                   "usdchf":False,"usdcad":False,"usdjpy":False}
START = pd.Timestamp("2017-01-01T00:00:00Z")
END = pd.Timestamp("2026-01-01T00:00:00Z")
COSTS = (0.0, 0.5, 1.0, 2.0)
PRIMARY = 1.0
DISCOVERY = (pd.Timestamp("2017-01-01", tz="UTC"), pd.Timestamp("2021-01-01", tz="UTC"))
CONFIRM = (pd.Timestamp("2021-01-01", tz="UTC"), pd.Timestamp("2024-01-01", tz="UTC"))
DIAGNOSTIC = (pd.Timestamp("2024-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC"))

class GateError(RuntimeError):
    pass

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda:f.read(1024*1024), b""): h.update(chunk)
    return h.hexdigest()

def parse_timestamps(series: pd.Series):
    s=series.astype(str).str.strip()
    num=pd.to_numeric(s, errors="coerce")
    if num.notna().mean() > 0.95:
        med=float(num.abs().median())
        unit="ms" if med>=1e11 else ("s" if med>=1e8 else None)
        if unit is None: return pd.DatetimeIndex(pd.to_datetime(s, utc=True, errors="coerce"))
        return pd.DatetimeIndex(pd.to_datetime(num, unit=unit, utc=True, errors="coerce"))
    return pd.DatetimeIndex(pd.to_datetime(s, utc=True, errors="coerce"))

def load_stream(path: Path):
    if not path.exists():
        raise GateError(f"missing required raw stream: {path}")
    raw=pd.read_csv(path)
    raw.columns=[str(c).replace("\ufeff","").strip().lower() for c in raw.columns]
    tc=next((c for c in ("timestamp","datetime","date","time") if c in raw.columns),None)
    if tc is None: raise GateError(f"timestamp column missing: {path.name}")
    idx=parse_timestamps(raw.pop(tc))
    missing=set(("open","high","low","close"))-set(raw.columns)
    if missing: raise GateError(f"missing OHLC columns in {path.name}: {sorted(missing)}")
    vals=raw[["open","high","low","close"]].apply(pd.to_numeric,errors="coerce")
    vals=vals.replace([np.inf,-np.inf],np.nan)
    invalid_ts=int(idx.isna().sum())
    valid_ts=~idx.isna()
    idx=idx[valid_ts]
    vals=vals.loc[valid_ts].copy()
    raw_rows=len(raw)
    vals.index=idx
    pre_range=len(vals)
    in_range=(vals.index>=START)&(vals.index<END)
    out_of_range=int((~in_range).sum())
    vals=vals.loc[in_range]
    hour_aligned=((vals.index.minute==0)&(vals.index.second==0)&(vals.index.microsecond==0))
    misaligned=int((~hour_aligned).sum())
    vals=vals.loc[hour_aligned]
    finite=vals.notna().all(axis=1)
    valid_ohlc=(vals["high"]>=vals[["open","close"]].max(axis=1)) & (vals["low"]<=vals[["open","close"]].min(axis=1)) & (vals["high"]>=vals["low"])
    good=finite&valid_ohlc
    invalid_ohlc=int((~good).sum())
    vals=vals.loc[good].sort_index(kind="mergesort")
    duplicate_count=int(vals.index.duplicated(keep=False).sum())
    dup_unique=int(vals.index[vals.index.duplicated(keep=False)].nunique())
    uniq=vals.loc[~vals.index.duplicated(keep="last")]
    times=uniq.index.unique().sort_values()
    diffs=np.diff(times.asi8)/1e9 if len(times)>1 else np.array([],dtype=float)
    gaps=diffs[diffs>3600.0]
    info={
      "file":path.name,"bytes":int(path.stat().st_size),"sha256":sha256_file(path),
      "raw_rows":int(raw_rows),"invalid_timestamps":invalid_ts,"out_of_range_rows":out_of_range,
      "misaligned_h1_rows":misaligned,"invalid_ohlc_rows_excluded":invalid_ohlc,
      "duplicate_rows_detected":duplicate_count,"duplicate_timestamp_values":dup_unique,
      "valid_unique_rows":int(len(uniq)),
      "start_utc":times[0].isoformat() if len(times) else None,
      "end_utc":times[-1].isoformat() if len(times) else None,
      "gaps_gt_1h":int(len(gaps)),
      "max_gap_hours":float(gaps.max()/3600) if len(gaps) else 0.0
    }
    # Return a unique diagnostic series only to allow a complete manifest to be written.
    # Any duplicate/malformed timestamp remains a fatal pre-outcome gate.
    return uniq, info

def load_all(data_dir: Path):
    streams={}; audit={"experiment":"R323","mode":"data_audit","range_utc":[START.isoformat(),END.isoformat()],
       "source":"Dukascopy H1 BID/ASK","expected_streams":len(PAIRS)*2,"streams":{},"pairs":{},
       "fatal_errors":[],"cleaning":{"no_fill_forward":True,"exact_timestamp_intersection":True,
       "invalid_ohlc":"excluded and counted","duplicate_timestamps":"fatal data gate",
       "repeated_flat_bars":"preserved; no placeholder deletion"}}
    for pair in PAIRS:
        for side in ("bid","ask"):
            p=data_dir/f"{pair}_h1_{side}.csv"
            try: d,info=load_stream(p)
            except Exception as e:
                audit["fatal_errors"].append(str(e)); continue
            streams[(pair,side)]=d
            audit["streams"][p.name]=info
            if info["invalid_timestamps"] or info["misaligned_h1_rows"] or info["duplicate_rows_detected"]:
                audit["fatal_errors"].append(
                  f"{p.name}: invalid_ts={info['invalid_timestamps']}, misaligned={info['misaligned_h1_rows']}, duplicates={info['duplicate_rows_detected']}")
            start=pd.Timestamp(info["start_utc"]) if info["start_utc"] else None
            end=pd.Timestamp(info["end_utc"]) if info["end_utc"] else None
            if start is None or start>pd.Timestamp("2017-01-15T00:00:00Z") or end is None or end<pd.Timestamp("2025-12-15T00:00:00Z"):
                audit["fatal_errors"].append(f"{p.name}: coverage does not span required 2017–2025 window")
            if info["valid_unique_rows"]<10000:
                audit["fatal_errors"].append(f"{p.name}: fewer than 10,000 valid unique H1 rows")
    bars={}
    for pair in PAIRS:
        if (pair,"bid") not in streams or (pair,"ask") not in streams: continue
        b,a=streams[(pair,"bid")],streams[(pair,"ask")]
        bi=set(b.index.asi8.tolist()); ai=set(a.index.asi8.tolist())
        common=b.index.intersection(a.index).sort_values()
        crossed_open=int(((a.loc[common,"open"]-b.loc[common,"open"]) < -1e-10).sum())
        crossed_close=int(((a.loc[common,"close"]-b.loc[common,"close"]) < -1e-10).sum())
        if crossed_open or crossed_close:
            audit["fatal_errors"].append(f"{pair}: negative quote spread at common open/close bars ({crossed_open}/{crossed_close})")
        sp_open=(a.loc[common,"open"]-b.loc[common,"open"])
        sp_close=(a.loc[common,"close"]-b.loc[common,"close"])
        spreads=pd.concat([sp_open.rename("open"),sp_close.rename("close")])
        audit["pairs"][pair]={
          "bid_rows":len(b),"ask_rows":len(a),"common_exact_timestamps":len(common),
          "bid_unmatched_rows":len(b)-len(common),"ask_unmatched_rows":len(a)-len(common),
          "negative_open_spreads":crossed_open,"negative_close_spreads":crossed_close,
          "spread_price_min":float(spreads.min()) if len(spreads) else None,
          "spread_price_median":float(spreads.median()) if len(spreads) else None,
          "spread_price_p95":float(spreads.quantile(.95)) if len(spreads) else None,
          "spread_price_max":float(spreads.max()) if len(spreads) else None,
          "common_start_utc":common[0].isoformat() if len(common) else None,
          "common_end_utc":common[-1].isoformat() if len(common) else None,
          "gaps_gt_1h":int((np.diff(common.asi8)/1e9>3600).sum()) if len(common)>1 else 0
        }
        if len(common)<10000: audit["fatal_errors"].append(f"{pair}: fewer than 10,000 exact BID/ASK rows")
        z=pd.DataFrame(index=common)
        for c in ("open","high","low","close"):
            z["bid_"+c]=b.loc[common,c].astype(float)
            z["ask_"+c]=a.loc[common,c].astype(float)
            z["mid_"+c]=(z["bid_"+c]+z["ask_"+c])/2.0
        bars[pair]=z
    audit["all_14_streams_present"]=len(streams)==14
    audit["all_7_pairs_present"]=len(bars)==7
    audit["data_gate"]="FAIL" if audit["fatal_errors"] or len(streams)!=14 or len(bars)!=7 else "PASS"
    audit["runtime"]={"python":platform.python_version(),"pandas":pd.__version__,"numpy":np.__version__}
    return bars,audit

def pip_size(pair): return 0.01 if pair.endswith("jpy") else 0.0001

def utc_day(d): return pd.Timestamp(d, tz="UTC")

def period_name(ts):
    if DISCOVERY[0] <= ts < DISCOVERY[1]: return "discovery"
    if CONFIRM[0] <= ts < CONFIRM[1]: return "confirmation"
    if DIAGNOSTIC[0] <= ts < DIAGNOSTIC[1]: return "diagnostic"
    return "excluded"

def time_at(day, hour):
    ts=pd.Timestamp(day)
    ts=ts.tz_localize("UTC") if ts.tzinfo is None else ts.tz_convert("UTC")
    return ts.normalize()+pd.Timedelta(hours=hour)

def make_ranges(bars):
    ranges={}
    for pair,z in bars.items():
        daily={}
        groups={}
        for ts,row in z.iterrows():
            if ts.hour in (12,13,14,15): groups.setdefault(ts.normalize(),[]).append((ts.hour,row))
        for day,items in groups.items():
            byh={h:r for h,r in items}
            if not all(h in byh for h in (12,13,14,15)): continue
            hi=max(float(byh[h]["mid_high"]) for h in (12,13,14,15))
            lo=min(float(byh[h]["mid_low"]) for h in (12,13,14,15))
            if math.isfinite(hi-lo) and hi>lo: daily[day]=hi-lo
        ranges[pair]=daily
    return ranges

def entry_candidates(bars, audit):
    ranges=make_ranges(bars)
    date_sets=[]
    for pair,z in bars.items():
        date_sets.append(set(z.index[z.index.hour==10].normalize()))
    common_dates=sorted(set.intersection(*date_sets)) if date_sets else []
    # Require all seven exact, common 10:00 signal bars; then use the fifth prior
    # eligible common date for the 5-active-session currency-strength score.
    rows={pair:{t:row for t,row in z.iterrows()} for pair,z in bars.items()}
    candidates=[]; skips=[]
    min_history=max(20,5)
    for k,day in enumerate(common_dates):
        if k<5:
            skips.append({"date":day.date().isoformat(),"reason":"less_than_five_prior_common_signal_sessions"})
            continue
        prior=common_dates[k-5]
        scores={}
        for cur,pair in PAIR_FOR.items():
            now=rows[pair].get(time_at(day,10)); prev=rows[pair].get(time_at(prior,10))
            if now is None or prev is None or float(now["mid_close"])<=0 or float(prev["mid_close"])<=0:
                scores={}; break
            val=math.log(float(now["mid_close"])/float(prev["mid_close"]))
            if not FOREIGN_IS_BASE[pair]: val=-val
            scores[cur]=val
        if len(scores)!=7:
            skips.append({"date":day.date().isoformat(),"reason":"missing_exact_signal_bar_or_invalid_price"}); continue
        ranked=sorted(CURRENCIES,key=lambda c:(-scores[c],c))
        planned=[(ranked[0],"strongest",1),(ranked[-1],"weakest",-1)]
        legs=[]; reasons=[]
        for cur,role,foreign_dir in planned:
            pair=PAIR_FOR[cur]
            pair_dir=foreign_dir if FOREIGN_IS_BASE[pair] else -foreign_dir
            sig=rows[pair].get(time_at(day,10)); ent=rows[pair].get(time_at(day,12))
            if sig is None or ent is None:
                reasons.append(f"{role}_missing_signal_or_entry"); continue
            entry_mid=float(ent["mid_open"]); sig_close=float(sig["mid_close"])
            if (entry_mid-sig_close)*pair_dir <= 0:
                reasons.append(f"{role}_continuation_gate_failed"); continue
            # Median range of 20 pair-specific complete 12:00–16:00 prior sessions.
            hist=sorted((d,r) for d,r in ranges[pair].items() if d<day)
            if len(hist)<20:
                reasons.append(f"{role}_fewer_than_20_prior_risk_sessions"); continue
            risk=float(np.median([r for _,r in hist[-20:]]))
            if not math.isfinite(risk) or risk<=0:
                reasons.append(f"{role}_invalid_risk_distance"); continue
            # Both exit barrier path (12:00 through 15:00) and the forced 16:00 exit
            # must exist on this exact pair BID/ASK stream.
            path_hours=(12,13,14,15,16)
            path={h:rows[pair].get(time_at(day,h)) for h in path_hours}
            if any(path[h] is None for h in path_hours):
                reasons.append(f"{role}_missing_exact_12_to_16_path"); continue
            entry=float(ent["ask_open"] if pair_dir==1 else ent["bid_open"])
            legs.append({"date":day.date().isoformat(),"currency":cur,"role":role,"pair":pair,
              "direction":pair_dir,"direction_text":"LONG" if pair_dir==1 else "SHORT",
              "score":float(scores[cur]),"score_gap_top_bottom":float(scores[ranked[0]]-scores[ranked[-1]]),
              "signal_close_mid":sig_close,"entry_time":time_at(day,12).isoformat(),"entry_price":entry,
              "entry_mid":entry_mid,"risk":risk,"pip_size":pip_size(pair),
              "risk_pips":risk/pip_size(pair),"path_hours":path_hours,
              "path":{h:{k:float(v) for k,v in path[h].items()} for h in path_hours}})
        if reasons or len(legs)!=2:
            skips.append({"date":day.date().isoformat(),"reason":";".join(sorted(set(reasons))) or "basket_not_two_legs",
                          "top_currency":ranked[0],"bottom_currency":ranked[-1]})
            continue
        # Keep a basket only if both chosen legs passed; the full positions close by 16:00.
        candidates.append({"date":day.date().isoformat(),"day":day,"top_currency":ranked[0],
                           "bottom_currency":ranked[-1],"legs":legs})
    audit["eligibility"]={
      "common_10utc_sessions":len(common_dates),"candidate_baskets_after_all_preoutcome_gates":len(candidates),
      "eligible_legs":2*len(candidates),"skipped_dates":len(skips),
      "sample_by_period":{p:{"legs":2*sum(period_name(c["day"])==p for c in candidates),
                            "active_days":sum(period_name(c["day"])==p for c in candidates)}
                          for p in ("discovery","confirmation","diagnostic")},
      "skip_reason_counts":pd.Series([s["reason"] for s in skips],dtype="string").value_counts().sort_index().to_dict()
    }
    return candidates,skips,ranges

def simulate_leg(leg):
    d=leg["direction"]; entry=leg["entry_price"]; r=leg["risk"]
    stop=entry-d*r; target=entry+d*1.5*r
    exit_px=None; exit_ts=None; reason=None
    for hour in (12,13,14,15):
        bar=leg["path"][hour]
        op=bar["bid_open"] if d==1 else bar["ask_open"]
        hi=bar["bid_high"] if d==1 else bar["ask_high"]
        lo=bar["bid_low"] if d==1 else bar["ask_low"]
        ts=(pd.Timestamp(leg["date"],tz="UTC")+pd.Timedelta(hours=hour)).isoformat()
        # Opening gaps receive priority and use the adverse open/capped target fill.
        if d==1 and op<=stop:
            exit_px=min(op,stop); exit_ts=ts; reason="STOP_GAP"; break
        if d==1 and op>=target:
            exit_px=target; exit_ts=ts; reason="TARGET_GAP_CAPPED"; break
        if d==-1 and op>=stop:
            exit_px=max(op,stop); exit_ts=ts; reason="STOP_GAP"; break
        if d==-1 and op<=target:
            exit_px=target; exit_ts=ts; reason="TARGET_GAP_CAPPED"; break
        stop_hit=(lo<=stop) if d==1 else (hi>=stop)
        target_hit=(hi>=target) if d==1 else (lo<=target)
        # Intrabar ambiguity is resolved stop-first.
        if stop_hit:
            exit_px=stop; exit_ts=ts; reason="STOP"; break
        if target_hit:
            exit_px=target; exit_ts=ts; reason="TARGET"; break
    if exit_px is None:
        bar=leg["path"][16]
        exit_px=bar["bid_open"] if d==1 else bar["ask_open"]
        exit_ts=(pd.Timestamp(leg["date"],tz="UTC")+pd.Timedelta(hours=16)).isoformat()
        reason="TIME_EXIT_16UTC"
    gross_r=d*(exit_px-entry)/r
    return {k:v for k,v in leg.items() if k not in ("path","path_hours")} | {
      "exit_time":exit_ts,"exit_price":float(exit_px),"exit_reason":reason,"gross_R":float(gross_r),
      "risk_distance_price":float(r),"risk_pips":float(leg["risk_pips"]),
      "holding_minutes":int((pd.Timestamp(exit_ts)-pd.Timestamp(leg["entry_time"])).total_seconds()/60)}

def pf_value(x):
    x=np.asarray(x,dtype=float)
    gains=float(x[x>0].sum()); losses=float(-x[x<0].sum())
    if losses==0: return "INF" if gains>0 else None
    return gains/losses

def pf_pass(v, threshold):
    return (v=="INF") or (isinstance(v,(int,float)) and math.isfinite(v) and v>=threshold)

def metric(rows,cost):
    x=np.array([t["gross_R"]-cost*t["pip_size"]/t["risk_distance_price"] for t in rows],dtype=float)
    pos=x[x>0]; neg=x[x<0]
    eq=np.cumsum(x)
    curve=np.r_[0.0,eq]
    dd=float(np.max(np.maximum.accumulate(curve)-curve)) if len(x) else 0.0
    return {"legs":int(len(x)),"net_R":float(x.sum()),"mean_R":float(x.mean()) if len(x) else None,
      "median_R":float(np.median(x)) if len(x) else None,"PF_R":pf_value(x),
      "win_rate":float((x>0).mean()) if len(x) else None,"max_drawdown_sequential_R":dd,
      "max_losing_streak":max_losing_streak(x)}

def max_losing_streak(x):
    best=cur=0
    for v in x:
        if v<0: cur+=1; best=max(best,cur)
        else: cur=0
    return int(best)

def csv_text(df):
    return df.to_csv(index=False,lineterminator="\n",float_format="%.12g")

def json_text(obj):
    return json.dumps(obj,indent=2,sort_keys=True,allow_nan=False)+"\n"

def audit_outputs(bars,audit,out_dir):
    files={}
    files["R323_DATA_AUDIT.json"]=json_text(audit)
    cov=[]
    for pair,z in bars.items():
        cov.append({"pair":pair,"rows":len(z),"start_utc":z.index[0].isoformat() if len(z) else None,
                    "end_utc":z.index[-1].isoformat() if len(z) else None,
                    "median_spread_pips":float(np.median(np.r_[((z.bid_open-z.ask_open)/pip_size(pair)).abs().values,
                                                               ((z.bid_close-z.ask_close)/pip_size(pair)).abs().values])) if len(z) else None})
    files["R323_PAIR_COVERAGE.csv"]=csv_text(pd.DataFrame(cov))
    return files

def eligibility_csv(candidates,skips):
    rows=[]
    good={x["date"]:x for x in candidates}
    for c in candidates: rows.append({"date":c["date"],"status":"ELIGIBLE","top_currency":c["top_currency"],"bottom_currency":c["bottom_currency"],"reason":""})
    for s in skips: rows.append({"date":s["date"],"status":"SKIP","top_currency":s.get("top_currency",""),"bottom_currency":s.get("bottom_currency",""),"reason":s["reason"]})
    return csv_text(pd.DataFrame(rows).sort_values(["date","status"]) if rows else pd.DataFrame(columns=["date","status","top_currency","bottom_currency","reason"]))

def build_pnl_outputs(candidates,skips,audit):
    trade_rows=[]
    for c in candidates:
        for leg in c["legs"]: trade_rows.append(simulate_leg(leg))
    df=pd.DataFrame(trade_rows).sort_values(["date","entry_time","pair","role"]).reset_index(drop=True)
    score=[]; yearly=[]
    periods={"discovery":DISCOVERY,"confirmation":CONFIRM,"diagnostic":DIAGNOSTIC}
    for pname,(a,b) in periods.items():
        part=df[(pd.to_datetime(df["entry_time"],utc=True)>=a)&(pd.to_datetime(df["entry_time"],utc=True)<b)] if len(df) else df
        for cost in COSTS:
            m=metric(part.to_dict("records"),cost)
            score.append({"period":pname,"extra_cost_pips":cost,**m})
    for year in range(2017,2026):
        a=pd.Timestamp(f"{year}-01-01",tz="UTC"); b=pd.Timestamp(f"{year+1}-01-01",tz="UTC")
        part=df[(pd.to_datetime(df["entry_time"],utc=True)>=a)&(pd.to_datetime(df["entry_time"],utc=True)<b)] if len(df) else df
        for cost in COSTS:
            yearly.append({"year":year,"extra_cost_pips":cost,**metric(part.to_dict("records"),cost)})
    # Daily confirmation portfolio series retains every calendar day including zero-trade days.
    conf_dates=pd.date_range(CONFIRM[0],CONFIRM[1]-pd.Timedelta(days=1),freq="D",tz="UTC")
    daily=pd.Series(0.0,index=conf_dates)
    for row in trade_rows:
        ts=pd.Timestamp(row["entry_time"])
        if CONFIRM[0]<=ts<CONFIRM[1]:
            cst=PRIMARY*row["pip_size"]/row["risk_distance_price"]
            daily.loc[ts.normalize()]+=row["gross_R"]-cst
    vals=daily.to_numpy(float); reps=10000; block=28; rng=np.random.default_rng(323)
    n=len(vals); blocks=int(math.ceil(n/block)); boots=np.empty(reps,dtype=float)
    for i in range(reps):
        starts=rng.integers(0,n,size=blocks)
        ix=np.concatenate([((s+np.arange(block))%n) for s in starts])[:n]
        boots[i]=float(vals[ix].mean())
    boot={"period":"2021-01-01/2023-12-31","daily_observations":n,"zero_trade_days":int((daily==0).sum()),
      "mean_daily_net_R_at_plus1pip":float(vals.mean()),"bootstrap":"circular 28-day blocks",
      "reps":reps,"seed":323,"lower_95_mean_daily_net_R":float(np.quantile(boots,0.025)),
      "upper_95_mean_daily_net_R":float(np.quantile(boots,0.975))}
    # Evaluate all frozen gates without changing any parameter.
    sc={(x["period"],x["extra_cost_pips"]):x for x in score}
    elig=audit.get("eligibility",{}).get("sample_by_period",{})
    d=elig.get("discovery",{"legs":0,"active_days":0}); c=elig.get("confirmation",{"legs":0,"active_days":0})
    gates={
      "discovery_min_1000_eligible_legs":d.get("legs",0)>=1000,
      "discovery_min_500_eligible_days":d.get("active_days",0)>=500,
      "confirmation_min_600_eligible_legs":c.get("legs",0)>=600,
      "confirmation_min_300_eligible_days":c.get("active_days",0)>=300,
      "discovery_plus1pip_positive_net_R":sc.get(("discovery",1.0),{}).get("net_R",0)>0,
      "confirmation_plus1pip_positive_net_R":sc.get(("confirmation",1.0),{}).get("net_R",0)>0,
      "discovery_plus1pip_PF_R_ge_1_05":pf_pass(sc.get(("discovery",1.0),{}).get("PF_R"),1.05),
      "confirmation_plus1pip_PF_R_ge_1_05":pf_pass(sc.get(("confirmation",1.0),{}).get("PF_R"),1.05),
      "discovery_plus2pip_positive_net_R":sc.get(("discovery",2.0),{}).get("net_R",0)>0,
      "confirmation_plus2pip_positive_net_R":sc.get(("confirmation",2.0),{}).get("net_R",0)>0,
      "discovery_plus2pip_PF_R_ge_1_00":pf_pass(sc.get(("discovery",2.0),{}).get("PF_R"),1.00),
      "confirmation_plus2pip_PF_R_ge_1_00":pf_pass(sc.get(("confirmation",2.0),{}).get("PF_R"),1.00),
      "bootstrap_lower_95_gt_zero":boot["lower_95_mean_daily_net_R"]>0
    }
    yrs=[x for x in yearly if x["extra_cost_pips"]==1.0 and 2017<=x["year"]<=2020]
    positive_years=sum(x["net_R"]>0 for x in yrs)
    disc_net=sc.get(("discovery",1.0),{}).get("net_R",0)
    concentration=max((x["net_R"]/disc_net for x in yrs),default=math.inf) if disc_net>0 else None
    gates["at_least_3_of_4_discovery_years_positive"]=positive_years>=3
    gates["no_discovery_year_over_70pct_of_net_R"]=(concentration is not None and concentration<=0.70)
    if not all(gates.values()):
        verdict="GAGAL — EDGE/ROBUSTNESS"
    else: verdict="LULUS"
    # Add extra cost metrics to a full trade ledger; no tuning or ranking across variants.
    allcost=[]
    for tr in trade_rows:
        for cost in COSTS:
            net=tr["gross_R"]-cost*tr["pip_size"]/tr["risk_distance_price"]
            allcost.append({k:v for k,v in tr.items() if k not in ("path","path_hours")} | {"extra_cost_pips":cost,"net_R":net})
    report={"experiment":"R323","status":"COMPLETED","verdict":verdict,
      "data_gate":"PASS","data_gate_fatal_errors":[],"periods":score,"annual":yearly,
      "eligibility":audit["eligibility"],"gates":gates,"discovery_positive_years":positive_years,
      "max_discovery_year_contribution_fraction":concentration,"bootstrap":boot,
      "costs_tested_pips":list(COSTS),"primary_cost_pips":PRIMARY,
      "interpretation":"Historical pass is not funded readiness: 2017–2025 has prior project exposure; separate clean forward data and account-level execution replay remain required."}
    files={
      "R323_TRADE_LEDGER_ALL_COSTS.csv":csv_text(pd.DataFrame(allcost)),
      "R323_PERIOD_SCORECARD.csv":csv_text(pd.DataFrame(score)),
      "R323_YEAR_SCORECARD.csv":csv_text(pd.DataFrame(yearly)),
      "R323_CONFIRMATION_DAILY_NET_R.csv":csv_text(pd.DataFrame({"date_utc":[x.isoformat() for x in daily.index],"net_R_plus1pip":vals})),
      "R323_BOOTSTRAP.json":json_text(boot),
      "R323_FINAL_RESULT.json":json_text(report)
    }
    lines=["# R323 final result","",f"**Verdict: {verdict}**","","## Eligibility and frozen gates",
      f"- Discovery eligible legs/days: {d.get('legs',0)} / {d.get('active_days',0)} (minimum 1,000 / 500)",
      f"- Confirmation eligible legs/days: {c.get('legs',0)} / {c.get('active_days',0)} (minimum 600 / 300)",
      f"- Confirmation bootstrap lower 95% bound, daily net R at +1 pip: {boot['lower_95_mean_daily_net_R']:.8g}",
      "", "## Gate results"]
    lines.extend([f"- {'PASS' if ok else 'FAIL'} — {name}" for name,ok in gates.items()])
    lines += ["","## Period scorecard at +1 pip","", "| Period | Legs | Net R | PF_R | Mean R | Max sequential DD_R |","|---|---:|---:|---:|---:|---:|"]
    for name in ("discovery","confirmation","diagnostic"):
        m=sc.get((name,1.0),{})
        lines.append(f"| {name} | {m.get('legs',0)} | {m.get('net_R',0):.6f} | {m.get('PF_R')} | {m.get('mean_R')} | {m.get('max_drawdown_sequential_R')} |")
    lines += ["","## Limits","",
      "All calculations use exact matched BID/ASK timestamps, correct entry/exit quote sides, one-hour delayed entry, the preregistered 1R stop/1.5R target, stop-first intrabar ambiguity, and the locked cost stresses.",
      "The diagnostic 2024–2025 cohort is contaminated and cannot promote the strategy. A historical LULUS is not a funded-readiness claim."]
    files["R323_FINAL_REPORT.md"]="\n".join(lines)+"\n"
    return files,report

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-dir",default="dl/r323")
    ap.add_argument("--out-dir",default="research/R323_RESULTS")
    ap.add_argument("--audit-only",action="store_true",help="data validation only; do not build signals or outcomes")
    args=ap.parse_args()
    data_dir=Path(args.data_dir); out_dir=Path(args.out_dir); out_dir.mkdir(parents=True,exist_ok=True)
    bars,audit=load_all(data_dir)
    if args.audit_only:
        (out_dir/"R323_DATA_AUDIT.json").write_text(json_text(audit),encoding="utf-8")
        print(json.dumps({"mode":"data_audit_only","data_gate":audit["data_gate"],
          "fatal_errors":audit["fatal_errors"],"streams":len(audit["streams"]),"pairs":len(bars)},indent=2))
        return 0 if audit["data_gate"]=="PASS" else 2
    if audit["data_gate"]!="PASS":
        (out_dir/"R323_DATA_AUDIT.json").write_text(json_text(audit),encoding="utf-8")
        (out_dir/"R323_FINAL_REPORT.md").write_text("# R323 final result\n\n**Verdict: GAGAL — DATA/PROCESS**\n\n"+ "\n".join("- "+x for x in audit["fatal_errors"])+"\n",encoding="utf-8")
        print(json.dumps({"verdict":"GAGAL — DATA/PROCESS","fatal_errors":audit["fatal_errors"]},indent=2))
        return 2
    candidates,skips,ranges=entry_candidates(bars,audit)
    # First write outcome-free eligibility and sample gate. Do not compute PnL if it fails.
    eligibility_text=eligibility_csv(candidates,skips)
    elig=audit["eligibility"]["sample_by_period"]
    sample_ok=(elig["discovery"]["legs"]>=1000 and elig["discovery"]["active_days"]>=500 and
               elig["confirmation"]["legs"]>=600 and elig["confirmation"]["active_days"]>=300)
    datafiles=audit_outputs(bars,audit,out_dir)
    datafiles["R323_ELIGIBILITY_LEDGER.csv"]=eligibility_text
    if not sample_ok:
        report={"experiment":"R323","status":"STOPPED_BEFORE_PNL","verdict":"GAGAL — DATA/SAMPLE",
          "data_gate":"PASS","eligibility":audit["eligibility"],
          "sample_gates":{"discovery_1000_legs_500_days":elig["discovery"]["legs"]>=1000 and elig["discovery"]["active_days"]>=500,
            "confirmation_600_legs_300_days":elig["confirmation"]["legs"]>=600 and elig["confirmation"]["active_days"]>=300},
          "note":"Sample gate failed; no PnL, PF, drawdown, or bootstrap was calculated."}
        datafiles["R323_FINAL_RESULT.json"]=json_text(report)
        datafiles["R323_FINAL_REPORT.md"]="# R323 final result\n\n**Verdict: GAGAL — DATA/SAMPLE**\n\nSample gate failed before outcome calculation. No PnL, PF, drawdown, or bootstrap was calculated.\n\n"+ "\n".join(f"- {p}: {v['legs']} eligible legs, {v['active_days']} active days" for p,v in elig.items())+"\n"
        for name,txt in datafiles.items(): (out_dir/name).write_text(txt,encoding="utf-8")
        print(json.dumps(report,indent=2))
        return 1
    # Run the same frozen calculation twice in fresh function calls and compare exact text bytes.
    files1,report1=build_pnl_outputs(candidates,skips,audit)
    files2,report2=build_pnl_outputs(candidates,skips,audit)
    identical=(files1==files2 and json_text(report1)==json_text(report2))
    if not identical:
        datafiles["R323_FINAL_RESULT.json"]=json_text({"experiment":"R323","verdict":"GAGAL — DATA/PROCESS","reason":"two deterministic in-process runs differed"})
        datafiles["R323_FINAL_REPORT.md"]="# R323 final result\n\n**Verdict: GAGAL — DATA/PROCESS**\n\nTwo deterministic computations differed byte-for-byte.\n"
    else:
        datafiles.update(files1)
    for name,txt in datafiles.items(): (out_dir/name).write_text(txt,encoding="utf-8")
    names=sorted(datafiles)
    hashes={}
    for name in names:
        hashes[name]=hashlib.sha256(datafiles[name].encode("utf-8")).hexdigest()
    repro={"experiment":"R323","two_computations_identical":identical,
      "run1_sha256":hashes,"run2_sha256":hashes if identical else None,
      "note":"Hashes cover deterministic output bytes; this manifest is excluded from recursive hashing."}
    (out_dir/"R323_REPRODUCIBILITY.json").write_text(json_text(repro),encoding="utf-8")
    result=report1 if identical else {"verdict":"GAGAL — DATA/PROCESS","reason":"non-deterministic output"}
    result["two_runs_identical"]=identical
    print(json.dumps({"verdict":result["verdict"],"two_runs_identical":identical,
      "eligibility":audit["eligibility"],"scorecard":result.get("periods"),"gates":result.get("gates")},indent=2,allow_nan=False))
    return 0 if identical and result["verdict"]=="LULUS" else 1

if __name__=="__main__":
    raise SystemExit(main())
