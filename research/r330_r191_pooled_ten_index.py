#!/usr/bin/env python3
"""R330: locked R191 pooled across ten indices; hard-gate-first, no selection."""
from __future__ import annotations
import json, math, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research.r192_ger40 import parse_data, build_h4, signals_and_stops, truncation_gate, simulate, metric, metric_entry_cohort, trade_r, PERIODS
from research.r195_ten_index import ASSETS as _R195_ASSETS

ASSETS = dict(_R195_ASSETS)
CFG = {"id":"R191_BASE_55_27_RR2","role":"locked_baseline","breakout":55,"stop_bars":27}
COSTS = (1, 2, 3)
N_PATHS = 10000
SEED = 330191
SERVER_TZ = "Europe/Helsinki"
D0, D1 = PERIODS["discovery"]
F0, F1 = PERIODS["forward"]
O0 = PERIODS["oos2026"]
CHALLENGE_START = pd.Timestamp("2022-01-01", tz="UTC")
CHALLENGE_END = pd.Timestamp("2027-01-01", tz="UTC")
QUARTERS = [f"{y}Q{q}" for y in range(2022, 2027) for q in range(1, 5)]

def clean(x):
    if isinstance(x, dict): return {str(k):clean(v) for k,v in x.items()}
    if isinstance(x, (list,tuple)): return [clean(v) for v in x]
    if isinstance(x, (np.integer,)): return int(x)
    if isinstance(x, (np.bool_,)): return bool(x)
    if isinstance(x, (np.floating,float)):
        z=float(x)
        if math.isnan(z): return None
        if math.isinf(z): return "INF" if z>0 else "-INF"
        return z
    if isinstance(x, pd.Timestamp): return x.isoformat()
    if x is pd.NaT: return None
    return x

def dump(path, obj):
    Path(path).write_text(json.dumps(clean(obj), indent=2, ensure_ascii=False), encoding="utf-8")

def finite(x):
    return isinstance(x,(int,float,np.integer,np.floating)) and math.isfinite(float(x))

def valid_pf(x):
    return isinstance(x,(int,float,np.integer,np.floating)) and not math.isnan(float(x))

def pf_ge(x, threshold):
    return valid_pf(x) and float(x) >= threshold

def pf_gt(x, threshold):
    return valid_pf(x) and float(x) > threshold

def g(name, passed, observed, required, detail=""):
    return {"gate":name,"pass":bool(passed),"observed":observed,"required":required,"detail":detail}

def append_state(verdict, gates, common_end, headline):
    p=Path("PROJECT_STATE.md")
    old=p.read_text(encoding="utf-8") if p.exists() else "# Project state\n"
    title="## R330 — locked R191 pooled ten-index test"
    if title in old:
        old=old.split(title)[0].rstrip()+"\n"
    status = ("GATE-MISMATCH (definisi konvensi entry), strategi belum dievaluasi"
              if str(verdict).startswith("GATE-MISMATCH") else verdict)
    block=f"""

{title} (2026-10-24)

**Status: {status}.** {headline}

- Locked rule: R191 NY-wall-clock H4, long-only, breakout N=55, stop M=27 bars, RR=2; primary entry is the open of the next H4 bar (canonical); manual5m is diagnostic only. All ten indices pooled without selection if Gate 1 passes.
- Common observed data cutoff UTC: {common_end.isoformat() if common_end is not None else "not established"}.
- Full report and machine results: research/R330_FINAL_VERDICT.md and research/R330_results.json on branch research/r330-r191-pooled-ten-index.
- Gate ledger: {json.dumps(clean(gates), ensure_ascii=False)}
- No tuning, instrument removal, or rescue variant is authorized.
"""
    p.write_text(old+block,encoding="utf-8")

def metric_by_cost(trades,start,end):
    return {str(b):metric(trades,start,end,b) for b in COSTS}

def cohort_metric(trades, year, cutoff, bps, end_override=None):
    start=pd.Timestamp(f"{year}-01-01",tz="UTC")
    end=pd.Timestamp(f"{year+1}-01-01",tz="UTC")
    if end_override is not None: end=min(end,end_override)
    if end<=start: return {"entries":0,"n":0,"censored":0,"pf":float("nan"),"wins_r":0.0,"losses_r":0.0}
    return metric_entry_cohort(trades,start,end,cutoff,bps)

def audit_paths(trades_by_key,h4s,m5s,cfgs):
    errors=[]; checked=0
    for (inst,cfgid),trades in trades_by_key.items():
        h4=h4s[inst]; m5=m5s[inst]; cfg=cfgs[cfgid]
        labels=pd.DatetimeIndex(h4["label_utc"]).tz_convert("UTC")
        label_map={int(t.value):i for i,t in enumerate(labels)}
        hclose=pd.DatetimeIndex(h4["bar_close_utc"]).tz_convert("UTC")
        lows=h4.low.to_numpy(float)
        mt=m5.index.tz_convert("UTC")
        op=m5.open.to_numpy(float); hi=m5.high.to_numpy(float); lo=m5.low.to_numpy(float); cl=m5.close.to_numpy(float)
        flat=(op==hi)&(hi==lo)&(lo==cl)
        for tr in trades:
            checked+=1
            try:
                sig=pd.Timestamp(tr["signal_bar_utc"]).tz_convert("UTC"); i=label_map[int(sig.value)]
                close_t=pd.Timestamp(tr["signal_close_utc"]).tz_convert("UTC")
                ent_t=pd.Timestamp(tr["entry_time_utc"]).tz_convert("UTC")
                entry=float(tr["entry"]); stop=float(tr["sl"]); target=float(tr["tp"])
                if close_t!=hclose[i]: raise ValueError("signal close timestamp mismatch")
                if i<cfg["breakout"] or float(h4.close.iloc[i])<=float(h4.high.iloc[i-cfg["breakout"]:i].max()):
                    raise ValueError("signal is not a causal close above prior breakout highs")
                if not math.isclose(stop,float(np.min(lows[i-cfg["stop_bars"]+1:i+1])),rel_tol=0,abs_tol=1e-8):
                    raise ValueError("stop mismatch vs prefix low")
                mode=tr.get("mode","manual5m")
                if i+1>=len(hclose):
                    raise ValueError("signal has no following H4 bar")
                if mode=="ideal":
                    next_label=pd.Timestamp(h4.index[i+1]).tz_convert("UTC")
                    if ent_t!=next_label or not math.isclose(entry,float(h4.open.iloc[i+1]),rel_tol=0,abs_tol=1e-8):
                        raise ValueError("canonical entry does not equal next H4 bar open")
                else:
                    if ent_t<close_t+pd.Timedelta(minutes=5) or ent_t>=hclose[i+1]:
                        raise ValueError("manual5m entry violates five-minute delay or next-H4 window")
                if not math.isclose(target,entry+2*(entry-stop),rel_tol=0,abs_tol=1e-7):
                    raise ValueError("target not equal to RR2")
                j0=int(mt.searchsorted(ent_t,side="left"))
                if j0>=len(mt) or mt[j0]!=ent_t or not math.isclose(entry,float(op[j0]),rel_tol=0,abs_tol=1e-8):
                    raise ValueError("entry quote not matched to M5 opening bar")
                if tr.get("exit_time_utc") is not None:
                    ex_t=pd.Timestamp(tr["exit_time_utc"]).tz_convert("UTC")
                    j1=int(mt.searchsorted(ex_t,side="left"))
                    if j1>=len(mt) or mt[j1]!=ex_t or j1<j0: raise ValueError("exit timestamp absent from M5 path")
                    first=None
                    for j in range(j0,j1+1):
                        if flat[j]: continue
                        o,h,l=float(op[j]),float(hi[j]),float(lo[j])
                        if l<=stop or o<=stop:
                            first=(j,"SL_GAP_OPEN" if o<=stop else "SL",o if o<=stop else stop); break
                        if h>=target: first=(j,"TP",target); break
                    if first is None or first[0]!=j1: raise ValueError("stored exit is not first causal hit")
                    if first[1]!=tr["reason"] or not math.isclose(first[2],float(tr["exit"]),rel_tol=0,abs_tol=1e-7):
                        raise ValueError("exit reason/price differs from first hit")
            except Exception as e:
                if len(errors)<50: errors.append({"instrument":inst,"config":cfgid,"entry_time_utc":tr.get("entry_time_utc"),"error":str(e)})
    return {"pass":not errors,"trades_checked":checked,"errors":errors,
            "method":"Independent check of prefix stop, close/entry timestamps, RR2, M5 opening fill, and first SL-first/TP execution."}

def add_daily_marks(trades,m5,bps=2):
    mt=m5.index.tz_convert("UTC")
    op=m5.open.to_numpy(float); hi=m5.high.to_numpy(float); lo=m5.low.to_numpy(float); cl=m5.close.to_numpy(float)
    flat=(op==hi)&(hi==lo)&(lo==cl)
    for tr in trades:
        tr["_marks"]=[]
        tr["_r2"]=trade_r(tr,bps) if tr.get("exit") is not None else float("nan")
        if tr.get("exit_time_utc") is None: continue
        ent=pd.Timestamp(tr["entry_time_utc"]).tz_convert("UTC")
        ex=pd.Timestamp(tr["exit_time_utc"]).tz_convert("UTC")
        j0=int(mt.searchsorted(ent,side="left")); j1=int(mt.searchsorted(ex,side="left"))
        if j0>=len(mt) or j1>=len(mt) or mt[j0]!=ent or mt[j1]!=ex: continue
        entry=float(tr["entry"]); risk=float(tr["risk_points"])
        if risk<=0: continue
        days={}
        for j in range(j0,j1+1):
            if flat[j]: continue
            ts=mt[j]; day=str(ts.tz_convert(SERVER_TZ).date())
            # Do not use prices occurring after the recorded exit within the same M5 bar.
            low_px=float(lo[j]); high_px=float(hi[j])
            if j==j1:
                low_px=float(tr["exit"]); high_px=float(tr["exit"])
            rlow=(low_px-entry)/risk; rhigh=(high_px-entry)/risk
            d=days.setdefault(day,{"min_r":rlow,"min_t":ts,"max_r":rhigh,"max_t":ts,"close_r":None,"close_t":None})
            if rlow<d["min_r"]: d["min_r"]=rlow; d["min_t"]=ts
            if rhigh>d["max_r"]: d["max_r"]=rhigh; d["max_t"]=ts
            if j<j1:
                d["close_r"]=(float(cl[j])-entry)/risk
                d["close_t"]=ts+pd.Timedelta(minutes=5)
        marks=[]
        for d in days.values():
            marks.append((d["min_t"],float(d["min_r"]),"low"))
            marks.append((d["max_t"],float(d["max_r"]),"high"))
            if d["close_t"] is not None: marks.append((d["close_t"],float(d["close_r"]),"close"))
        # If high and low occur in the same M5 bar, process adverse low first.
        marks.sort(key=lambda x:(x[0],0 if x[2]=="close" else (1 if x[2]=="low" else 2)))
        tr["_marks"]=marks
    return trades

def pools_by_quarter(trades):
    pools={q:[] for q in QUARTERS}
    for tr in trades:
        if tr.get("exit_time_utc") is None or not tr.get("_marks") or not finite(tr.get("_r2")): continue
        ent=pd.Timestamp(tr["entry_time_utc"]).tz_convert("UTC")
        ex=pd.Timestamp(tr["exit_time_utc"]).tz_convert("UTC")
        if ent<CHALLENGE_START or ent>=CHALLENGE_END or ex>=CHALLENGE_END: continue
        q=str(ent.tz_localize(None).to_period("Q"))
        if q in pools: pools[q].append(tr)
    return pools

def run_path(pools, sampled, risk_fraction):
    events=[]
    for block_i,source_q in enumerate(sampled):
        source_start=pd.Period(source_q,freq="Q").start_time.tz_localize("UTC")
        synthetic_q=str(pd.Period("2022Q1",freq="Q")+block_i)
        synth_start=pd.Period(synthetic_q,freq="Q").start_time.tz_localize("UTC")
        delta=synth_start-source_start
        for rid,tr in enumerate(pools[source_q]):
            tid=(block_i,rid)
            ent=pd.Timestamp(tr["entry_time_utc"]).tz_convert("UTC")+delta
            ex=pd.Timestamp(tr["exit_time_utc"]).tz_convert("UTC")+delta
            if ent>=CHALLENGE_END: continue
            r=float(tr["_r2"])
            for mt,mr,kind in tr["_marks"]:
                mt=pd.Timestamp(mt).tz_convert("UTC")+delta
                if mt>=CHALLENGE_END: continue
                if kind=="close": pri=0
                elif mt==ent: pri=5 if kind=="low" else 6
                else: pri=1 if kind=="low" else 2
                events.append((mt,pri,tid,"mark",float(mr)))
            events.append((ent,4,tid,"entry",{"r":r,"exit":ex}))
            if ex<CHALLENGE_END:
                # Same-M5 entry and exit must be processed after that trade is opened and marked.
                exit_pri=7 if ex==ent else 3
                events.append((ex,exit_pri,tid,"exit",r))
    events.sort(key=lambda x:(x[0],x[1]))
    balance=100.0; phase=1; phase_days=set(); phase1_time=None
    active={}; current_day=None; day_start=100.0
    max_open=0; max_risk_pct=0.0; taken=0; blocked=0
    for ts,pri,tid,typ,payload in events:
        if ts>=CHALLENGE_END: break
        day=str(ts.tz_convert(SERVER_TZ).date())
        if day!=current_day:
            current_day=day
            day_start=balance+sum(p["risk_cash"]*p["mark_r"] for p in active.values())
        if typ=="mark":
            if tid in active: active[tid]["mark_r"]=float(payload)
        elif typ=="exit":
            if tid in active:
                p=active.pop(tid); balance+=p["risk_cash"]*float(payload); phase_days.add(day)
        elif typ=="entry":
            if balance<=0:
                blocked+=1
            else:
                rcash=balance*risk_fraction
                open_risk=sum(p["risk_cash"] for p in active.values())
                if open_risk+rcash>0.02*balance+1e-9: blocked+=1
                else:
                    active[tid]={"risk_cash":rcash,"mark_r":0.0,"exit":payload["exit"]}
                    taken+=1; max_open=max(max_open,len(active))
                    max_risk_pct=max(max_risk_pct,100.0*sum(p["risk_cash"] for p in active.values())/max(balance,1e-9))
        floating=sum(p["risk_cash"]*p["mark_r"] for p in active.values())
        equity=balance+floating
        if equity-day_start<=-5.0+1e-10:
            return {"outcome":"breach_DLL","breach":"DLL","elapsed_years":(ts-CHALLENGE_START).total_seconds()/(365.25*86400),"trades_taken":taken,"blocked_cap":blocked,"max_open_positions":max_open,"max_open_risk_pct":max_risk_pct}
        if equity<=90.0+1e-10:
            return {"outcome":"breach_MLL","breach":"MLL","elapsed_years":(ts-CHALLENGE_START).total_seconds()/(365.25*86400),"trades_taken":taken,"blocked_cap":blocked,"max_open_positions":max_open,"max_open_risk_pct":max_risk_pct}
        target=108.0 if phase==1 else 105.0
        if equity>=target and len(phase_days)>=5:
            active.clear()
            if phase==1:
                phase=2; phase1_time=ts; balance=100.0; day_start=100.0; phase_days=set()
            else:
                return {"outcome":"pass_both","breach":None,"phase1_time":phase1_time.isoformat() if phase1_time is not None else None,"completion_time":ts.isoformat(),"elapsed_years":(ts-CHALLENGE_START).total_seconds()/(365.25*86400),"trades_taken":taken,"blocked_cap":blocked,"max_open_positions":max_open,"max_open_risk_pct":max_risk_pct}
    return {"outcome":"unfinished_5y","breach":None,"elapsed_years":5.0,"trades_taken":taken,"blocked_cap":blocked,"max_open_positions":max_open,"max_open_risk_pct":max_risk_pct}

def challenge_sim(candidate,baseline):
    pool_c=pools_by_quarter(candidate); pool_b=pools_by_quarter(baseline)
    rng=np.random.default_rng(SEED)
    draws=rng.integers(0,len(QUARTERS),size=(N_PATHS,len(QUARTERS)))
    rows=[]; gates=[]
    for rf in (0.005,0.01):
        for label,pools in (("R191_only_USA500_USATECH",pool_b),("pooled_all_10_indices",pool_c)):
            outcomes=[]; ptime=[]; maxopen=[]; maxrisk=[]; ntaken=[]; nblocked=[]
            for k in range(N_PATHS):
                sampled=[QUARTERS[int(i)] for i in draws[k]]
                z=run_path(pools,sampled,rf)
                outcomes.append(z["outcome"])
                if z["outcome"]=="pass_both": ptime.append(z["elapsed_years"])
                maxopen.append(z["max_open_positions"]); maxrisk.append(z["max_open_risk_pct"])
                ntaken.append(z["trades_taken"]); nblocked.append(z["blocked_cap"])
            counts=pd.Series(outcomes).value_counts().to_dict()
            passed=100*counts.get("pass_both",0)/N_PATHS
            dll=100*counts.get("breach_DLL",0)/N_PATHS
            mll=100*counts.get("breach_MLL",0)/N_PATHS
            breach=dll+mll
            rows.append({"stream":label,"risk_per_trade_pct":rf*100,"paths":N_PATHS,
                "pass_both_within_5y_pct":passed,"breach_DLL_pct":dll,"breach_MLL_pct":mll,
                "failed_by_breach_pct":breach,"unfinished_5y_pct":100*counts.get("unfinished_5y",0)/N_PATHS,
                "median_years_if_passed":float(np.median(ptime)) if ptime else None,
                "p90_years_if_passed":float(np.quantile(ptime,.9)) if ptime else None,
                "mean_trades_taken":float(np.mean(ntaken)),"mean_blocked_by_2pct_cap":float(np.mean(nblocked)),
                "max_open_positions_observed":int(max(maxopen) if maxopen else 0),
                "max_open_risk_pct_observed":float(max(maxrisk) if maxrisk else 0.0),
                "quarter_trade_counts":{q:len(pools[q]) for q in QUARTERS}})
    for rf in (0.5,1.0):
        b=next(x for x in rows if x["stream"]=="R191_only_USA500_USATECH" and x["risk_per_trade_pct"]==rf)
        c=next(x for x in rows if x["stream"]=="pooled_all_10_indices" and x["risk_per_trade_pct"]==rf)
        better=c["pass_both_within_5y_pct"]>b["pass_both_within_5y_pct"]+1e-12 and c["failed_by_breach_pct"]<=b["failed_by_breach_pct"]+1e-12
        passed=c["pass_both_within_5y_pct"]>=65 and c["failed_by_breach_pct"]<=25 and better
        gates.append({"risk_per_trade_pct":rf,"pass_rate_gate":c["pass_both_within_5y_pct"]>=65,
            "breach_rate_gate":c["failed_by_breach_pct"]<=25,"better_than_R191_only":better,
            "candidate_pass_pct":c["pass_both_within_5y_pct"],"baseline_pass_pct":b["pass_both_within_5y_pct"],
            "candidate_breach_pct":c["failed_by_breach_pct"],"baseline_breach_pct":b["failed_by_breach_pct"],
            "pass":passed,"comparison":"Candidate pass-both rate must be strictly higher, with no higher DLL/MLL breach rate."})
    meta={"paths_per_stream_risk":N_PATHS,"seed":SEED,"quarter_blocks":QUARTERS,
        "candidate_quarter_counts":{q:len(pool_c[q]) for q in QUARTERS},
        "baseline_quarter_counts":{q:len(pool_b[q]) for q in QUARTERS},
        "risk_cap":"Skip an entry if total active stop-risk would exceed 2% of current phase balance.",
        "marking":"M5 intraday low/high extrema and last pre-exit close mark open positions; same-bar exit is after entry/marks and stop-first ordering is conservative. DLL includes marked floating PnL; MLL is a static 10% floor. Five distinct server-day trade closures required in each phase.",
        "server_day":"Europe/Helsinki seasonal GMT+2/GMT+3 proxy; verify against funded account server.",
        "limitations":["Quarter cohorts are synchronized across instruments to preserve observed cross-index co-occurrence, but a trade's marked path is shifted as a unit with its entry quarter.",
          "This is a bootstrap simulation of observed trade cohorts, not a future-price guarantee or a full broker/platform execution emulator."]}
    return rows,gates,meta

def overlap(trades,start,end):
    ev=[]
    for t in trades:
        a=pd.Timestamp(t["entry_time_utc"]).tz_convert("UTC")
        b=pd.Timestamp(t["exit_time_utc"]).tz_convert("UTC") if t.get("exit_time_utc") else end
        if a>=end or b<=start: continue
        a=max(a,start); b=min(b,end)
        if b>a: ev.extend([(a,1),(b,-1)])
    ev.sort(key=lambda z:(z[0],z[1]))
    active=0; max_active=0; prev=start; span=(end-start).total_seconds(); ge3=0.0
    for ts,d in ev:
        if ts>prev and active>=3: ge3+=(ts-prev).total_seconds()
        active+=d; max_active=max(max_active,active); prev=ts
    if prev<end and active>=3: ge3+=(end-prev).total_seconds()
    return {"window_start_utc":start.isoformat(),"window_end_utc":end.isoformat(),
        "pct_elapsed_time_with_3_or_more_open":100*ge3/span if span else 0,
        "max_simultaneous_positions":max_active,"uncapped_max_open_risk_pct_at_0_5_each":max_active*.5,
        "uncapped_max_open_risk_pct_at_1_0_each":max_active*1.0,
        "note":"Raw historical overlap before the simulator's 2% open-stop-risk cap."}

def correlations(trades,start,end):
    days=pd.date_range(start.floor("D"),(end-pd.Timedelta(seconds=1)).floor("D"),freq="D")
    series={}
    for inst in ASSETS:
        val=defaultdict(float)
        for t in trades:
            if t.get("instrument")!=inst or t.get("exit_time_utc") is None: continue
            ex=pd.Timestamp(t["exit_time_utc"]).tz_convert("UTC")
            if start<=ex<end: val[ex.floor("D")]+=float(trade_r(t,2))
        series[inst]=pd.Series([val.get(d,0.0) for d in days],index=days)
    mat=pd.DataFrame(series,index=days); corr=mat.corr(min_periods=10)
    pairs=[float(corr.iloc[i,j]) for i in range(len(corr.columns)) for j in range(i+1,len(corr.columns)) if pd.notna(corr.iloc[i,j])]
    return corr,{"period":"Daily realized risk-normalized R at 2bp, forward through common cutoff",
        "daily_sample_count":len(days),"pairs_with_defined_correlation":len(pairs),
        "mean_pairwise_daily_correlation":float(np.mean(pairs)) if pairs else None,
        "median_pairwise_daily_correlation":float(np.median(pairs)) if pairs else None,
        "min_pairwise_daily_correlation":float(np.min(pairs)) if pairs else None,
        "max_pairwise_daily_correlation":float(np.max(pairs)) if pairs else None}

def main():
    import argparse
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-dir",default="dl"); ap.add_argument("--out",default="research")
    a=ap.parse_args(); data_dir=Path(a.data_dir); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    h1s={}; m5s={}; h4s={}; meta={}
    for inst,name in ASSETS.items():
        hp=data_dir/f"{inst}_h1.csv.gz"; mp=data_dir/f"{inst}_m5.csv.gz"
        if not hp.is_file() or not mp.is_file(): raise SystemExit(f"HARD STOP: missing cache for {inst}: {hp} / {mp}")
        h1,d1=parse_data(hp); m5,d2=parse_data(mp); h4,diag=build_h4(h1,pd.Timestamp.now(tz="UTC"))
        h1s[inst]=h1; m5s[inst]=m5; h4s[inst]=h4
        meta[inst]={"name":name,"h1_rows":len(h1),"m5_rows":len(m5),"h1_duplicates_removed":d1,"m5_duplicates_removed":d2,
            "h1_start_utc":h1.index[0].tz_convert("UTC").isoformat(),"h1_end_utc":h1.index[-1].tz_convert("UTC").isoformat(),
            "m5_start_utc":m5.index[0].tz_convert("UTC").isoformat(),"m5_end_utc":m5.index[-1].tz_convert("UTC").isoformat(),
            "flat_m5_rows":int(((m5.open==m5.high)&(m5.high==m5.low)&(m5.low==m5.close)).sum()),**diag}
        print(f"DATA {inst}: H1={len(h1):,}, M5={len(m5):,}",flush=True)
    common_end=min(m5.index[-1].tz_convert("UTC")+pd.Timedelta(minutes=5) for m5 in m5s.values())

    # Hard gate 1: canonical R191 execution (open of the next H4 bar).
    # manual5m is computed only as a comparison table and never affects Gate 1.
    rep=[]; rep_manual=[]
    for inst in ("usa500idxusd","usatechidxusd"):
        canonical_trades,_=simulate(h4s[inst],m5s[inst],CFG,"ideal")
        manual_trades,_=simulate(h4s[inst],m5s[inst],CFG,"manual5m")
        for t in canonical_trades:
            t["instrument"]=inst; t["instrument_name"]=ASSETS[inst]
        for t in manual_trades:
            t["instrument"]=inst; t["instrument_name"]=ASSETS[inst]
        rep.extend(canonical_trades); rep_manual.extend(manual_trades)

    gate1_windows={
        "selection":(D0,D1),
        "forward":(F0,F1),
        "oos_2026":(O0[0],common_end),
    }
    gate1_observed={}
    gate1_manual={}
    for phase,(start,end) in gate1_windows.items():
        gate1_observed[phase]={}
        gate1_manual[phase]={}
        for bp in (1,2,3):
            cm=metric(rep,start,end,bp)
            mm=metric(rep_manual,start,end,bp)
            for dest,m in ((gate1_observed,cm),(gate1_manual,mm)):
                dest[phase][str(bp)]={
                    "entries":m["entries"],"n":m["n"],"censored":m["censored"],
                    "pf":m["pf"],"wins_r":m["wins_r"],"losses_r":m["losses_r"]}
    expected_gate1={
        "selection":{"n":78,"pf_1bp_rounded_3dp":2.082},
        "forward":{"n":70,"pf_1bp_rounded_3dp":1.247,"pf_2bp_rounded_3dp":1.241},
        "oos_2026":{"n":11,"pf_2bp_rounded_3dp":1.954},
    }
    def rounded_pf(phase,bp):
        v=gate1_observed[phase][str(bp)]["pf"]
        return round(float(v),3) if finite(v) else None
    gate1_checks={
        "selection_n":gate1_observed["selection"]["1"]["n"]==expected_gate1["selection"]["n"],
        "selection_pf_1bp":rounded_pf("selection",1)==expected_gate1["selection"]["pf_1bp_rounded_3dp"],
        "forward_n":gate1_observed["forward"]["1"]["n"]==expected_gate1["forward"]["n"],
        "forward_pf_1bp":rounded_pf("forward",1)==expected_gate1["forward"]["pf_1bp_rounded_3dp"],
        "forward_pf_2bp":rounded_pf("forward",2)==expected_gate1["forward"]["pf_2bp_rounded_3dp"],
        "oos_2026_n":gate1_observed["oos_2026"]["2"]["n"]==expected_gate1["oos_2026"]["n"],
        "oos_2026_pf_2bp":rounded_pf("oos_2026",2)==expected_gate1["oos_2026"]["pf_2bp_rounded_3dp"],
    }
    repok=all(gate1_checks.values())
    gr1=g("G1_R191_CANONICAL_REPLICATION",repok,
        {"canonical_open_next_H4":gate1_observed,"manual5m_diagnostic_only":gate1_manual,
         "checks":gate1_checks,"selection_window_utc":[D0.isoformat(),D1.isoformat()],
         "forward_window_utc":[F0.isoformat(),F1.isoformat()],
         "oos_2026_window_utc":[O0[0].isoformat(),common_end.isoformat()]},
        expected_gate1,
        "Canonical mode means entry at open of next H4 bar; manual5m is excluded from pass/fail.")
    print("G1 CANONICAL REPLICATION:",gr1,flush=True)
    manual_rows=[]
    for phase in gate1_windows:
        row={"phase":phase,"entry_convention":"manual5m","pass_fail_use":False}
        for bp in (1,2,3):
            m=gate1_manual[phase][str(bp)]
            row[f"n_{bp}bp"]=m["n"]; row[f"pf_{bp}bp"]=m["pf"]
            row[f"entries_{bp}bp"]=m["entries"]; row[f"censored_{bp}bp"]=m["censored"]
        manual_rows.append(row)
    pd.DataFrame(manual_rows).to_csv(out/"R330_manual5m_gate1_diagnostic.csv",index=False)

    all_gate1_pfs=[
        gate1_observed[p][str(bp)]["pf"] for p in gate1_windows for bp in (1,2,3)
    ] + [
        gate1_manual[p][str(bp)]["pf"] for p in gate1_windows for bp in (1,2,3)
    ]
    causality_needed=any(finite(v) and float(v)>1.4 for v in all_gate1_pfs)
    if causality_needed:
        audit_map={}
        for inst in ("usa500idxusd","usatechidxusd"):
            audit_map[(inst,CFG["id"])]=[
                t for t in rep+rep_manual if t.get("instrument")==inst
            ]
        causal=audit_paths(audit_map,h4s,m5s,{CFG["id"]:CFG})
        causal["required"]=True
        print(f"G1 PF>1.4 CAUSALITY AUDIT: {causal}",flush=True)
    else:
        causal={"required":False,"pass":True,"trades_checked":0,"errors":[],
                "detail":"No Gate 1 canonical/manual diagnostic PF exceeded 1.4."}

    if not repok:
        mismatch_label="GATE-MISMATCH (definisi konvensi entry), strategi belum dievaluasi"
        headline=("Canonical Gate 1 did not match the locked reference; no ten-index truncation, pooled "
                  "performance, neighborhood, leave-one-out, correlation/overlap or challenge simulation was run.")
        result={"experiment":"R330","verdict":"GATE-MISMATCH","stopped_at":"G1_R191_CANONICAL_REPLICATION",
                "gate1":gr1,"gate1_canonical_observed":gate1_observed,"gate1_manual5m_diagnostic":gate1_manual,
                "gate1_expected":expected_gate1,"gate1_checks":gate1_checks,"causality_audit":causal,
                "data":meta,"remaining_criteria_status":"NOT_RUN_AFTER_GATE_MISMATCH",
                "entry_convention_amendment":{"primary":"canonical next-H4 open","manual5m":"diagnostic only"},
                "note":"The specifically named R191_CANONICAL_index_trend_long.py was not present in the repository snapshot. The available R192 mode 'ideal' enters at the open of the next H4 bar. This is a canonical-equivalent check, not proof the missing named file was executed."}
        dump(out/"R330_results.json",result)
        rows=[]
        for phase in gate1_windows:
            c=gate1_observed[phase]
            rows.append({"phase":phase,"canonical_n":c["1"]["n"],"canonical_pf_1bp":c["1"]["pf"],
                         "canonical_pf_2bp":c["2"]["pf"],"canonical_pf_3bp":c["3"]["pf"],
                         "expected_n":expected_gate1[phase]["n"],
                         "expected_pf_1bp":expected_gate1[phase].get("pf_1bp_rounded_3dp"),
                         "expected_pf_2bp":expected_gate1[phase].get("pf_2bp_rounded_3dp")})
        report=("# R330 STATUS — GATE-MISMATCH (entry convention), strategy not evaluated\n\n"
                "## Definition amendment\n\n"
                "Gate 1 uses canonical entry: the open of the next H4 bar. The previous manual5m PF of 1.491 is not a canonical replication failure and is not used for pass/fail. manual5m is a diagnostic table only.\n\n"
                "The named file R191_CANONICAL_index_trend_long.py is absent from the tracked repository snapshot. The figures below come from the available R192 mode ideal, which enters at the next H4 open; they are not represented as execution of that missing file.\n\n"
                "## Gate 1 comparison\n\n"+pd.DataFrame(rows).to_markdown(index=False)+"\n\n"
                "Window caveat: the available R192 helper labels discovery/selection as entries 2017-01-01 to 2022-01-01. Since the named canonical file is missing, the requested selection-window definition could not be independently verified.\n\n"
                "## Manual5m diagnostic (not used for pass/fail)\n\n"+pd.DataFrame(manual_rows).to_markdown(index=False)+"\n\n"
                "## Causality diagnostic when PF > 1.4\n\n"
                +f"- Required: {causality_needed}; audit result: {'PASS' if causal.get('pass') else 'FAIL'}; trades checked: {causal.get('trades_checked',0)}.\n\n"
                +(json.dumps(clean(causal.get("errors",[])),indent=2,ensure_ascii=False) if causal.get("errors") else "No path errors were reported by this audit.\n")
                +"\n## Decision\n\n"
                "**GATE-MISMATCH (definisi konvensi entry), strategi belum dievaluasi.** No Gate 2, pooled metrics, neighborhood, LOO, or challenge simulation was run. No tuning, instrument removal, or replacement variant was attempted.\n")
        (out/"R330_FINAL_VERDICT.md").write_text(report,encoding="utf-8")
        append_state(mismatch_label,[gr1],common_end,headline)
        raise SystemExit(2)
    print("G1 PASS: all canonical reference metrics match to three decimals.",flush=True)

    # Hard gate 2: all ten instruments pass N=55 truncation before any ten-index metrics.
    trunc={}
    for inst in ASSETS:
        s,st=signals_and_stops(h4s[inst],CFG); trunc[inst]=truncation_gate(h4s[inst],CFG,s,st)
        print(f"G2 TRUNCATION {inst}: {trunc[inst]}",flush=True)
    alltr=all(v.get("pass",False) for v in trunc.values())
    gr2=g("G2_TRUNCATION_ALL_10",alltr,{"passed":sum(bool(x.get("pass")) for x in trunc.values()),"total":len(ASSETS),"by_instrument":trunc},"10/10 instruments pass N=55 signal/stop prefix consistency.")
    if not alltr:
        result={"experiment":"R330","verdict":"REJECT","stopped_at":"G2_TRUNCATION_ALL_10","gate1":gr1,"gate2":gr2,"data":meta}
        dump(out/"R330_results.json",result)
        (out/"R330_FINAL_VERDICT.md").write_text("# R330 FINAL VERDICT — REJECT\n\nGate 1 passed. Stopped at Gate 2: one or more indices failed truncation. No pooled PF, neighbors, leave-one-out or challenge simulation was calculated.\n\n"+json.dumps(clean(trunc),indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        append_state("REJECT at Gate 2",[gr1,gr2],common_end,"R191 replication passed, but truncation failed for at least one index; performance calculations stopped.")
        raise SystemExit(2)
    print("G2 PASS: all ten indices pass truncation.",flush=True)

    pools={}; diagpool={}; cfgs={CFG["id"]:CFG}; all_audit={}
    for n in (40,55,80):
        cfg={"id":f"R330_N{n}_M27_RR2","role":"locked_baseline" if n==55 else "robustness_only","breakout":n,"stop_bars":27}
        cfgs[cfg["id"]]=cfg; joined=[]; per={}
        for inst in ASSETS:
            ss,st=signals_and_stops(h4s[inst],cfg)
            gt=truncation_gate(h4s[inst],cfg,ss,st)
            if not gt["pass"]: raise RuntimeError(f"N={n} prefix test failed for {inst}: {gt}")
            ts,sd=simulate(h4s[inst],m5s[inst],cfg,"ideal")
            for t in ts: t["instrument"]=inst; t["instrument_name"]=ASSETS[inst]
            add_daily_marks(ts,m5s[inst],2); per[inst]=ts; joined.extend(ts); all_audit[(inst,cfg["id"])]=ts
            print(f"SIM N={n} {inst}: signals={sd['signals']}; trades={len(ts)}",flush=True)
        pools[n]=joined; diagpool[n]={"by_instrument":{i:len(t) for i,t in per.items()}}
    base=pools[55]; base2=[t for t in base if t["instrument"] in ("usa500idxusd","usatechidxusd")]

    # Manual5m is a second, diagnostic-only pooled table. It cannot affect gates.
    manual_base=[]
    for inst in ASSETS:
        mt,_=simulate(h4s[inst],m5s[inst],CFG,"manual5m")
        for t in mt:
            t["instrument"]=inst; t["instrument_name"]=ASSETS[inst]
        manual_base.extend(mt)
    manual_pooled_rows=[]
    for phase,start,end in (("discovery",D0,D1),("forward",F0,F1),("oos_2026",O0[0],common_end)):
        for bp in COSTS:
            mm=metric(manual_base,start,end,bp)
            manual_pooled_rows.append({"phase":phase,"entry_convention":"manual5m","cost_bps":bp,
                "entries":mm["entries"],"n":mm["n"],"censored":mm["censored"],"pf":mm["pf"],
                "wins_r":mm["wins_r"],"losses_r":mm["losses_r"],"pass_fail_use":False})
    pd.DataFrame(manual_pooled_rows).to_csv(out/"R330_manual5m_pooled_diagnostic.csv",index=False)

    agg={}
    for phase,start,end in (("discovery",D0,D1),("forward",F0,F1),("oos_2026",O0[0],common_end)):
        agg[phase]=metric_by_cost(base,start,end)
    dis_pf=agg["discovery"]["2"]["pf"]; fwd=agg["forward"]["2"]
    ann=[]
    for year in range(2017,2027):
        if year<=2021: cutoff=D1; phase="discovery"
        elif year<=2025: cutoff=F1; phase="forward"
        else: cutoff=common_end; phase="oos_2026"
        end_override=common_end if year==2026 else None
        row={"year":year,"phase":phase}
        for bp in COSTS:
            m=cohort_metric(base,year,cutoff,bp,end_override)
            for k in ("entries","n","censored","pf","wins_r","losses_r"): row[f"{k}_{bp}bp"]=m[k]
        ann.append(row)
    pd.DataFrame(ann).to_csv(out/"R330_pooled_annual.csv",index=False)
    fw_year=[r for r in ann if 2022<=r["year"]<=2025]
    worstpf=min([float(r["pf_2bp"]) for r in fw_year if valid_pf(r["pf_2bp"])],default=None)
    four_have_trades=len(fw_year)==4 and all(r["n_2bp"]>0 and valid_pf(r["pf_2bp"]) for r in fw_year)

    instrows=[]
    for inst in ASSETS:
        ts=[t for t in base if t["instrument"]==inst]; row={"instrument":inst,"instrument_name":ASSETS[inst]}
        for phase,start,end in (("discovery",D0,D1),("forward",F0,F1),("oos_2026",O0[0],common_end)):
            for bp in COSTS:
                m=metric(ts,start,end,bp); row[f"{phase}_n_{bp}bp"]=m["n"]; row[f"{phase}_pf_{bp}bp"]=m["pf"]
        instrows.append(row)
    pd.DataFrame(instrows).to_csv(out/"R330_instrument_metrics.csv",index=False)

    nbr=[]
    for n in (40,55,80):
        ts=pools[n]; m2=metric(ts,F0,F1,2)
        nbr.append({"N":n,"M":27,"RR":2,"forward_n":m2["n"],"forward_pf_2bp":m2["pf"],
            "truncation_10_of_10":True,"note":"N=40/80 are robustness only; candidate remains N=55."})
    pd.DataFrame(nbr).to_csv(out/"R330_neighborhood.csv",index=False)

    loo=[]
    for removed in ASSETS:
        ts=[t for t in base if t["instrument"]!=removed]; m=metric(ts,F0,F1,2)
        loo.append({"removed_instrument":removed,"remaining_instruments":9,"forward_n":m["n"],"forward_pf_2bp":m["pf"],"pass":pf_ge(m["pf"],1.05)})
    pd.DataFrame(loo).to_csv(out/"R330_leave_one_out.csv",index=False)

    corr,corr_summary=correlations(base,F0,common_end)
    corr.to_csv(out/"R330_daily_correlation_matrix.csv")
    ov=overlap(base,F0,common_end)
    dump(out/"R330_correlation_overlap.json",{"correlation":corr_summary,"overlap":ov})

    reported_pf=[]
    for mm in agg.values():
        for m in mm.values():
            if valid_pf(m["pf"]): reported_pf.append(float(m["pf"]))
    for row in ann+nbr+instrows+loo:
        for k,v in row.items():
            if "pf" in k and valid_pf(v): reported_pf.append(float(v))
    need_causality=any(pf_gt(v,1.4) for v in reported_pf)
    if need_causality:
        caus=audit_paths(all_audit,h4s,m5s,cfgs); caus["required"]=True
    else:
        caus={"pass":True,"required":False,"trades_checked":0,"errors":[],"detail":"No reported pooled/annual/neighborhood PF exceeded 1.4."}

    simrows,sim_gates,sim_meta=challenge_sim(base,base2)
    pd.DataFrame([{k:v for k,v in r.items() if k!="quarter_trade_counts"} for r in simrows]).to_csv(out/"R330_challenge_simulation.csv",index=False)

    gates=[gr1,gr2]
    gates.append(g("G3_POOLED_FORWARD",fwd["n"]>=150 and pf_ge(fwd["pf"],1.15),
        {"n":fwd["n"],"pf_2bp":fwd["pf"]},{"n_min":150,"pf_2bp_min":1.15}))
    gates.append(g("G4_POOLED_DISCOVERY",pf_ge(dis_pf,1.00),{"pf_2bp":dis_pf},{"pf_2bp_min":1.00}))
    gates.append(g("G5_WORST_FORWARD_YEAR",four_have_trades and worstpf is not None and pf_ge(worstpf,.80),
        {"worst_year_pf_2bp":worstpf,"four_years_have_closed_trades":four_have_trades,"years":fw_year},
        {"pf_2bp_min":0.80,"all_four_years_have_closed_trades":True}))
    gates.append(g("G6_NEIGHBORHOOD_N40_55_80",all(pf_ge(r["forward_pf_2bp"],1.00) for r in nbr),
        nbr,"All three pooled forward PF@2bp>=1.00; candidate remains N=55."))
    gates.append(g("G7_LEAVE_ONE_OUT",all(r["pass"] for r in loo),loo,"Every leave-one-out portfolio forward PF@2bp>=1.05."))
    gates.append(g("G8_STELLAR_2STEP_SIMULATION",all(x["pass"] for x in sim_gates),{"risk_level_gates":sim_gates,"rows":simrows,"simulator":sim_meta},
        "At each risk, pass-both >=65%, DLL+MLL breach<=25%, and better than R191-only without higher breach rate."))
    gates.append(g("G9_CAUSALITY_IF_PF_GT_1_4",caus.get("pass",False),caus,"If any reported PF>1.4, independent trade-path audit must pass."))
    verdict="PASS" if all(x["pass"] for x in gates) else "REJECT"
    failed=[x["gate"] for x in gates if not x["pass"]]
    headline=(f"All locked gates passed. Forward n={fwd['n']}, PF@2bp={fwd['pf']}, discovery PF@2bp={dis_pf}, worst forward year PF@2bp={worstpf}."
        if verdict=="PASS" else "Failed gates: "+", ".join(failed)+". No tuning, instrument removal or rescue variant was run.")
    result={"experiment":"R330","verdict":verdict,"run_utc":pd.Timestamp.now(tz="UTC").isoformat(),
        "branch":"research/r330-r191-pooled-ten-index","locked_rule":{"direction":"long-only","timezone":"America/New_York",
        "H4_breakout_N":55,"stop_lookback_M":27,"RR":2.0,"entry":"first non-flat M5 BID bar at/after signal close +5m and before next actual NY H4 close","round_trip_price_cost_bps":list(COSTS)},
        "periods":{"discovery":"2017-01-01 <= entry < 2022-01-01; outcomes closed before 2022-01-01",
        "forward":"2022-01-01 <= entry < 2026-01-01; outcomes closed before 2026-01-01",
        "oos_2026":"2026 entry cohort through common cached data cutoff"},
        "common_data_cutoff_utc":common_end.isoformat(),"data":meta,
        "gate1_replication":{"gate":gr1,"metrics":repm,"prefix":gate1_prefix},
        "gate2_truncation":{"gate":gr2,"by_instrument":trunc},
        "pooled_metrics":agg,"pooled_annual":ann,"instrument_metrics":instrows,"neighborhood":nbr,"leave_one_out":loo,
        "correlation_overlap":{"daily_correlations":corr_summary,"overlap":ov},
        "causality_audit":caus,"challenge_simulation":simrows,"challenge_gates":sim_gates,"challenge_simulator":sim_meta,
        "gates":gates,"final_verdict":verdict,"headline":headline,
        "guardrails":["No instrument is selected or dropped.","N=40/80 are robustness checks only; they cannot replace N=55.","After REJECT no tuning, variant, or instrument removal is permitted."]}
    dump(out/"R330_results.json",result)
    pd.DataFrame([{k:v for k,v in t.items() if not k.startswith("_")} for t in base]).to_csv(out/"R330_pooled_trades.csv",index=False)
    pd.DataFrame([{"gate":x["gate"],"pass":x["pass"],"observed":json.dumps(clean(x["observed"]),ensure_ascii=False),
        "required":json.dumps(clean(x["required"]),ensure_ascii=False),"detail":x["detail"]} for x in gates]).to_csv(out/"R330_gate_ledger.csv",index=False)
    report=[
        "# R330 FINAL VERDICT — R191 pooled over all ten indices","",f"**VERDICT: {verdict}.** {headline}","",
        "## Locked rule","",
        "- NY-wall-clock H4, long-only, breakout 55, stop lookback 27 bars inclusive, target 2R.",
        "- Primary canonical entry: open of the next NY-wall-clock H4 bar. manual5m is diagnostic only and excluded from all pass/fail gates.",
        "- Costs are modeled round-trip price costs of 1/2/3bp; they are not measured broker fees/spread/slippage.",
        "- All ten indices pooled; no selection or exclusions. Discovery 2017–2021, forward 2022–2025, OOS 2026 once after hard gates.",
        "",
        "## Sequential hard gates","",
        f"1. R191 USA500+USATECH replication: {'PASS' if gr1['pass'] else 'FAIL'}; forward n={repm['n']}, PF@1bp={repm['pf']!r}; required n=70 and PF=1.247 rounded to 3 decimals.",
        f"2. N=55 truncation on all ten: {'PASS' if gr2['pass'] else 'FAIL'}; {sum(bool(x['pass']) for x in trunc.values())}/10 passed.",
        "",
        "## Pooled annual entry-cohort table","",
        "PF uses risk-normalized R. Outcomes cut off at each phase boundary; 2026 is limited to common source cutoff.","",
        pd.DataFrame(ann).to_markdown(index=False),"",
        "## Aggregate metrics","",
        "## Manual5m diagnostic table (not used for pass/fail)","",
        pd.DataFrame(manual_pooled_rows).to_markdown(index=False),"",
        pd.DataFrame([{"phase":p,"cost_bps":int(bp),"n":m["n"],"PF":m["pf"],"entries":m["entries"],"censored":m["censored"]} for p,mm in agg.items() for bp,m in mm.items()]).to_markdown(index=False),"",
        "## Correlation and simultaneous exposure","",
        f"- Mean/median/max pairwise daily correlation: {corr_summary['mean_pairwise_daily_correlation']!r} / {corr_summary['median_pairwise_daily_correlation']!r} / {corr_summary['max_pairwise_daily_correlation']!r}.",
        f"- Time with 3+ simultaneous open positions: {ov['pct_elapsed_time_with_3_or_more_open']:.5f}% of elapsed forward/OOS window; maximum overlap: {ov['max_simultaneous_positions']}.",
        f"- Uncapped maximum exposure based on overlap: {ov['uncapped_max_open_risk_pct_at_0_5_each']:.2f}% at 0.5% each and {ov['uncapped_max_open_risk_pct_at_1_0_each']:.2f}% at 1% each. Simulator caps aggregate stop-risk at 2%.","",
        "## Stellar 2-Step challenge simulator","",
        pd.DataFrame([{k:v for k,v in r.items() if k!="quarter_trade_counts"} for r in simrows]).to_markdown(index=False),"",
        "10,000 paired quarterly-bootstrap paths per stream and risk setting. Quarterly draws are synchronized across instruments. Floating-equity marks use daily M5 lows, highs and pre-exit closes; same-entry/exit M5 bars are processed after entry, with adverse low before high; server-day boundaries use Europe/Helsinki seasonal GMT+2/GMT+3 as a proxy. This resamples observed trade cohorts, not raw future price bars.","",
        "## Neighborhood","",
        pd.DataFrame(nbr).to_markdown(index=False),"",
        "## Leave one out","",
        pd.DataFrame(loo).to_markdown(index=False),"",
        "## Gate-by-gate verdict","",
        pd.DataFrame([{"gate":x["gate"],"result":"PASS" if x["pass"] else "FAIL","detail":x["detail"]} for x in gates]).to_markdown(index=False),"",
        "## Causality audit","",
        f"- Required because any report PF>1.4: {need_causality}. Audit pass: {caus.get('pass')}; checked trades: {caus.get('trades_checked',0)}.",
        json.dumps(clean(caus.get("errors",[])),indent=2,ensure_ascii=False) if caus.get("errors") else "No causality errors reported.","",
        "## Decision policy","",
        "A single failed gate means REJECT. No tuning, dropping instruments, or rescue variant is run after a reject.","",
        "## Stored artefacts","",
        "- R330_results.json: full machine-readable outputs.",
        "- R330_pooled_annual.csv: pooled year-by-year counts and PF by 1/2/3bp.",
        "- R330_instrument_metrics.csv, R330_neighborhood.csv, R330_leave_one_out.csv.",
        "- R330_daily_correlation_matrix.csv and R330_correlation_overlap.json.",
        "- R330_challenge_simulation.csv, R330_gate_ledger.csv and R330_pooled_trades.csv."
    ]
    (out/"R330_FINAL_VERDICT.md").write_text("\n".join(report)+"\n",encoding="utf-8")
    append_state(verdict,gates,common_end,headline)
    print("R330 VERDICT:",verdict,flush=True); print(headline,flush=True)
    print(pd.DataFrame([{"gate":x["gate"],"pass":x["pass"]} for x in gates]).to_string(index=False),flush=True)
    print(f"Common cutoff: {common_end.isoformat()}",flush=True)
    if verdict!="PASS": raise SystemExit(2)

if __name__=="__main__": main()
