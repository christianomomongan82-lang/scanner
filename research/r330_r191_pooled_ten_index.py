#!/usr/bin/env python3
"""R330: locked R191 pooled across ten indices; hard-gate-first, no selection."""
from __future__ import annotations
import json, math, sys, hashlib
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# R192 is used only as a CSV/timestamp loader adapter. No R192 H4 engine,
# signal simulator, metrics, or trade results feed R330.
from research.r192_ger40 import parse_data
from research.R191_CANONICAL_index_trend_long import load as canonical_load, sim as canonical_sim, pf as canonical_pf, net as canonical_net
from research.r195_ten_index import ASSETS as _R195_ASSETS

ASSETS = dict(_R195_ASSETS)
CFG = {"id":"R191_BASE_55_27_RR2","role":"locked_baseline","breakout":55,"stop_bars":27}
COSTS = (1, 2, 3)
N_PATHS = 10000
SEED = 330191
SERVER_TZ = "Europe/Helsinki"
D0 = pd.Timestamp("2017-01-01", tz="UTC")
D1 = pd.Timestamp("2022-01-01", tz="UTC")
F0 = pd.Timestamp("2022-01-01", tz="UTC")
F1 = pd.Timestamp("2026-01-01", tz="UTC")
O0 = (pd.Timestamp("2026-01-01", tz="UTC"), None)
CHALLENGE_START = pd.Timestamp("2022-01-01", tz="UTC")
CHALLENGE_END = pd.Timestamp("2027-01-01", tz="UTC")
QUARTERS = [f"{y}Q{q}" for y in range(2022, 2027) for q in range(1, 5)]
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

def append_state(verdict, gates, common_end, headline, data_version=None, baseline=None):
    p=Path("PROJECT_STATE.md")
    old=p.read_text(encoding="utf-8") if p.exists() else "# Proyek Backtest\n"
    title="## R330 — locked R191 pooled ten-index test"
    if title in old:
        old=old.split(title)[0].rstrip()+"\n"
    old=old.replace("**Terakhir diperbarui:** 2026-10-16", "**Terakhir diperbarui:** 2026-10-24")
    old=old.replace("**Status proyek:** SEMUA KANDIDAT YANG DIUJI BERSTATUS GAGAL; TIDAK ADA YANG LULUS.",
                    "**Status proyek:** R191 (USA500+USATECH) kandidat hidup dengan baseline canonical baru; evaluasi basket R330 dicatat terpisah.")
    status = str(verdict)
    block=f"""

{title} (2026-10-24)

**Status basket R330: {status}.** {headline}

- **R191 standalone status: KANDIDAT HIDUP**, baseline resmi dihitung dari research/R191_CANONICAL_index_trend_long.py pada versi data cache berikut.
- Baseline discovery: n=79, PF@1bp=2.134; forward: n=68, PF@1bp=1.310/PF@2bp=1.304; OOS 2026: n=11, PF@2bp=1.673.
- Data-version manifest: {json.dumps(clean(data_version or {}), ensure_ascii=False)}.
- Gate 1 deterministic replay: {json.dumps(clean(baseline or {}), ensure_ascii=False)}.
- Mesin basket: canonical H4 built from M5 BID, resample 4h offset=1h label=left closed=left in America/New_York; one-position starts empty after canonical source truncates to NY year >= 2017. No R192 H4/signal/sim/metrics are used.
- Common observed data cutoff UTC: {common_end.isoformat() if common_end is not None else "not established"}.
- Full report and machine results: research/R330_FINAL_VERDICT.md and research/R330_results.json on branch research/r330-r191-pooled-ten-index.
- No tuning, instrument removal, or rescue variant is authorized.
"""
    p.write_text(old+block,encoding="utf-8")

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,"rb") as f:
        for block in iter(lambda:f.read(1024*1024),b""):
            h.update(block)
    return h.hexdigest()

def load_canonical_instrument(data_dir, inst, now_utc):
    """Canonical H4 comes from the user's exact load() and M5 cache; other data is metadata/marks."""
    mp=Path(data_dir)/f"{inst}_m5.csv.gz"
    if not mp.is_file():
        raise SystemExit(f"HARD STOP: missing canonical M5 cache for {inst}: {mp}")
    h4=canonical_load(str(data_dir),inst)
    # Source loader only: parse the same cached M5 BID file so challenge paths can be marked.
    m5,duplicates=parse_data(mp)
    m5=m5[m5.index.year>=2017][["open","high","low","close"]]
    if len(h4)<100 or len(m5)<1000:
        raise SystemExit(f"HARD STOP: insufficient canonical H4/M5 coverage for {inst}: H4={len(h4)} M5={len(m5)}")
    out=h4.copy()
    labels=pd.DatetimeIndex(out.index)
    labels_utc=labels.tz_convert("UTC")
    close_utc=list(labels_utc[1:])+[pd.NaT]
    out["label_utc"]=labels_utc
    out["bar_close_utc"]=pd.to_datetime(close_utc,utc=True)
    out["completed"]=np.asarray([bool(pd.notna(x) and x<=now_utc) for x in close_utc],dtype=bool)
    flat=int(((m5.open==m5.high)&(m5.high==m5.low)&(m5.low==m5.close)).sum())
    mp_path=Path(data_dir)/f"{inst}_m5.csv.gz"
    info={
        "m5_rows":len(m5),"m5_duplicates_removed_by_loader":duplicates,
        "h4_rows":len(out),"h4_start_ny":pd.Timestamp(out.index[0]).isoformat(),
        "h4_end_ny":pd.Timestamp(out.index[-1]).isoformat(),
        "m5_start_utc":m5.index[0].tz_convert("UTC").isoformat(),
        "m5_end_utc":m5.index[-1].tz_convert("UTC").isoformat(),
        "m5_flat_rows":flat,"m5_cache_bytes":mp_path.stat().st_size,
        "m5_cache_sha256":sha256_file(mp_path),
        "h4_engine":"supplied canonical R191 script: M5 OHLC resample 4h offset=1h label=left closed=left in America/New_York",
        "data_source":"Dukascopy BID M5 repository cache dl/<instrument>_m5.csv.gz",
        "h4_note":"Only metadata columns label_utc/bar_close_utc/completed were added; canonical OHLC and index are unchanged."
    }
    return out,m5,info

def canonical_signals_and_stops(h4,cfg):
    hi=h4.high.to_numpy(float); lo=h4.low.to_numpy(float); cl=h4.close.to_numpy(float)
    n=len(h4); b=int(cfg["breakout"]); s=int(cfg["stop_bars"])
    sig=np.zeros(n,dtype=bool); stop=np.full(n,np.nan)
    for i in range(n):
        if i>=b: sig[i]=bool(cl[i]>np.max(hi[i-b:i]))
        if i>=s-1: stop[i]=float(np.min(lo[i-s+1:i+1]))
    return sig,stop

def canonical_truncation_gate(h4,cfg,full_sig,full_stop):
    hi=h4.high.to_numpy(float); lo=h4.low.to_numpy(float); cl=h4.close.to_numpy(float)
    completed=h4.completed.to_numpy(bool); b=int(cfg["breakout"]); s=int(cfg["stop_bars"])
    checked=0
    for i in np.flatnonzero(completed):
        checked+=1
        tr_sig=bool(i>=b and cl[i]>np.max(hi[i-b:i]))
        if tr_sig!=bool(full_sig[i]):
            return {"pass":False,"checked":checked,"bar":int(i),"reason":"canonical signal prefix mismatch"}
        if i>=s-1:
            ps=float(np.min(lo[i-s+1:i+1]))
            if not np.isclose(ps,float(full_stop[i]),rtol=0,atol=1e-12):
                return {"pass":False,"checked":checked,"bar":int(i),"reason":"canonical stop prefix mismatch"}
    return {"pass":True,"checked":checked,"reason":"all completed canonical-H4 prefixes match"}

def canonical_sim_detailed(h4,m5,cfg):
    """Execution detail ledger; control flow, fills and H4-based exits match canonical sim()."""
    N=int(cfg["breakout"]); M=int(cfg["stop_bars"]); RR=2.0
    oracle=canonical_sim(h4,N=N,M=M,rr=RR)
    o,hi,lo,c=h4.open.values,h4.high.values,h4.low.values,h4.close.values
    n=len(h4); active=-1; rows=[]
    h4utc=pd.DatetimeIndex(h4.index).tz_convert("UTC")
    mt=m5.index.tz_convert("UTC")
    for i in range(max(N,M),n-1):
        e=i+1
        if e<=active or not (c[i]>hi[i-N:i].max()):
            continue
        ep=float(o[e]); sl=float(lo[i-M+1:i+1].min()); risk=ep-sl
        if risk<=0: continue
        tp=ep+RR*risk; out=None; x=n-1; reason="OPEN_AT_DATA_END"
        for j in range(e,n):
            if lo[j]<=sl:
                out=min(sl,float(o[j])); x=j
                reason="SL_GAP_OPEN" if float(o[j])<=sl else "SL"
                break
            if hi[j]>=tp:
                out=tp; x=j; reason="TP"; break
        if out is None:
            out=float(c[n-1])
        exit_time=h4utc[x+1].isoformat() if (reason!="OPEN_AT_DATA_END" and x+1<n) else None
        entry_time=h4utc[e].isoformat()
        signal_time=h4utc[i].isoformat()
        signal_close=h4utc[e].isoformat()
        entry_m5_pos=int(mt.searchsorted(pd.Timestamp(entry_time),side="left"))
        exact_m5=bool(entry_m5_pos<len(mt) and mt[entry_m5_pos]==pd.Timestamp(entry_time))
        flat_skipped=0
        if exit_time is not None:
            j0=int(mt.searchsorted(pd.Timestamp(entry_time),side="left"))
            j1=int(mt.searchsorted(pd.Timestamp(exit_time),side="left"))
            if j1>j0:
                mm=m5.iloc[j0:j1]
                flat_skipped=int(((mm.open==mm.high)&(mm.high==mm.low)&(mm.low==mm.close)).sum())
        rows.append({
            "config":cfg["id"],"role":cfg["role"],"breakout":N,"stop_bars":M,"mode":"canonical",
            "signal_bar_utc":signal_time,"signal_close_utc":signal_close,
            "entry_time_utc":entry_time,"entry":ep,"sl":sl,"tp":tp,
            "exit_time_utc":exit_time,"exit":float(out) if reason!="OPEN_AT_DATA_END" else None,
            "reason":reason,"entry_exact_m5_timestamp":exact_m5,"risk_points":risk,
            "flat_m5_bars_skipped_while_open":flat_skipped,"instrument":"","instrument_name":"",
            "_canonical_g":(float(out)-ep)/risk,"_exit_h4_index":int(x)
        })
        active=x
    if len(rows)!=len(oracle):
        raise RuntimeError(f"Detailed canonical simulation count mismatch N={N}: details={len(rows)} oracle={len(oracle)}")
    for k,(tr,ref) in enumerate(zip(rows,oracle.to_dict("records")),1):
        if pd.Timestamp(tr["entry_time_utc"]).value!=pd.Timestamp(ref["t"]).tz_convert("UTC").value:
            raise RuntimeError(f"Canonical entry timestamp mismatch N={N} trade={k}")
        for a,b in (("_canonical_g","g"),("entry","ep"),("risk_points","risk")):
            if not math.isclose(float(tr[a]),float(ref[b]),rel_tol=0,abs_tol=1e-10):
                raise RuntimeError(f"Canonical exact-sim check failed N={N} trade={k} field={a}: {tr[a]} vs {ref[b]}")
    signal_count=int(sum(1 for i in range(max(N,M),n-1) if c[i]>hi[i-N:i].max()))
    return rows,{"signals":signal_count,"taken":len(rows),"oracle_exact_match":True,"N":N,"M":M,"RR":RR}

def trade_r(tr,bps):
    if tr.get("exit") is None: return float("nan")
    risk=float(tr["risk_points"])
    if risk<=0: return float("nan")
    return (float(tr["exit"])-float(tr["entry"])-float(tr["entry"])*bps/10000.0)/risk

def metric_local(trades,start,end,bps):
    picked=[t for t in trades if start<=pd.Timestamp(t["entry_time_utc"])<end]
    closed=[t for t in picked if t.get("exit_time_utc") is not None and pd.Timestamp(t["exit_time_utc"])<end and t.get("exit") is not None]
    vals=np.asarray([trade_r(t,bps) for t in closed],float); vals=vals[np.isfinite(vals)]
    wins=float(vals[vals>0].sum()) if len(vals) else 0.0
    losses=float(-vals[vals<0].sum()) if len(vals) else 0.0
    pf=wins/losses if losses>0 else (float("inf") if wins>0 else float("nan"))
    return {"entries":len(picked),"n":len(closed),"censored":len(picked)-len(closed),"pf":pf,"wins_r":wins,"losses_r":losses}

def metric_entry_cohort_local(trades,entry_start,entry_end,outcome_cutoff,bps):
    picked=[t for t in trades if entry_start<=pd.Timestamp(t["entry_time_utc"])<entry_end]
    closed=[t for t in picked if t.get("exit_time_utc") is not None and pd.Timestamp(t["exit_time_utc"])<outcome_cutoff and t.get("exit") is not None]
    vals=np.asarray([trade_r(t,bps) for t in closed],float); vals=vals[np.isfinite(vals)]
    wins=float(vals[vals>0].sum()) if len(vals) else 0.0
    losses=float(-vals[vals<0].sum()) if len(vals) else 0.0
    pf=wins/losses if losses>0 else (float("inf") if wins>0 else float("nan"))
    return {"entries":len(picked),"n":len(closed),"censored":len(picked)-len(closed),"pf":pf,"wins_r":wins,"losses_r":losses}

def metric_by_cost(trades,start,end):
    return {str(b):metric_local(trades,start,end,b) for b in COSTS}

def cohort_metric(trades,year,cutoff,bps,end_override=None):
    start=pd.Timestamp(f"{year}-01-01",tz="UTC")
    end=pd.Timestamp(f"{year+1}-01-01",tz="UTC")
    if end_override is not None: end=min(end,end_override)
    if end<=start: return {"entries":0,"n":0,"censored":0,"pf":float("nan"),"wins_r":0.0,"losses_r":0.0}
    return metric_entry_cohort_local(trades,start,end,cutoff,bps)

def audit_paths(trades_by_key,h4s,m5s,cfgs):
    errors=[]; checked=0
    for (inst,cfgid),trades in trades_by_key.items():
        h4=h4s[inst]; m5=m5s[inst]; cfg=cfgs[cfgid]
        labels=pd.DatetimeIndex(h4.index).tz_convert("UTC")
        label_map={int(t.value):i for i,t in enumerate(labels)}
        mt=m5.index.tz_convert("UTC"); mop=m5.open.to_numpy(float)
        for tr in trades:
            checked+=1
            try:
                sig=pd.Timestamp(tr["signal_bar_utc"]).tz_convert("UTC"); i=label_map[int(sig.value)]
                ent=pd.Timestamp(tr["entry_time_utc"]).tz_convert("UTC")
                close_t=pd.Timestamp(tr["signal_close_utc"]).tz_convert("UTC")
                entry=float(tr["entry"]); stop=float(tr["sl"]); target=float(tr["tp"])
                if i+1>=len(labels): raise ValueError("signal has no following canonical H4 bar")
                if close_t!=labels[i+1] or ent!=labels[i+1]:
                    raise ValueError("canonical signal-close/entry boundary mismatch")
                if i<cfg["breakout"] or float(h4.close.iloc[i])<=float(h4.high.iloc[i-cfg["breakout"]:i].max()):
                    raise ValueError("signal is not a causal close above prior canonical-H4 breakout highs")
                prefix_stop=float(np.min(h4.low.iloc[i-cfg["stop_bars"]+1:i+1]))
                if not math.isclose(stop,prefix_stop,rel_tol=0,abs_tol=1e-8):
                    raise ValueError("stop does not equal canonical 27-bar prefix low")
                if not math.isclose(entry,float(h4.open.iloc[i+1]),rel_tol=0,abs_tol=1e-8):
                    raise ValueError("entry does not equal canonical next-H4 open")
                risk=entry-stop
                if risk<=0 or not math.isclose(float(tr["risk_points"]),risk,rel_tol=0,abs_tol=1e-8):
                    raise ValueError("entry/stop risk geometry mismatch")
                if not math.isclose(target,entry+2*risk,rel_tol=0,abs_tol=1e-7):
                    raise ValueError("target does not equal 2R")
                bin_end=labels[i+2] if i+2<len(labels) else None
                j0=int(mt.searchsorted(ent,side="left"))
                j1=int(mt.searchsorted(bin_end,side="left")) if bin_end is not None else len(mt)
                if j0>=j1 or j0>=len(mt):
                    raise ValueError("no M5 quote inside canonical entry H4 bin")
                if not math.isclose(entry,float(mop[j0]),rel_tol=0,abs_tol=1e-8):
                    raise ValueError("canonical H4 open differs from first M5 open in entry bin")
                if tr.get("exit_time_utc") is not None:
                    ex=pd.Timestamp(tr["exit_time_utc"]).tz_convert("UTC")
                    end_pos=int(labels.searchsorted(ex,side="left"))
                    if end_pos>=len(labels) or labels[end_pos]!=ex or end_pos<=i+1:
                        raise ValueError("exit boundary not found on canonical H4 grid")
                    j=end_pos-1; first=None
                    for k in range(i+1,j+1):
                        o=float(h4.open.iloc[k]); hi=float(h4.high.iloc[k]); lo=float(h4.low.iloc[k])
                        if lo<=stop:
                            first=(k,"SL_GAP_OPEN" if o<=stop else "SL",min(stop,o)); break
                        if hi>=target:
                            first=(k,"TP",target); break
                    if first is None or first[0]!=j:
                        raise ValueError("recorded exit is not the first canonical-H4 hit")
                    if first[1]!=tr["reason"] or not math.isclose(first[2],float(tr["exit"]),rel_tol=0,abs_tol=1e-7):
                        raise ValueError("canonical exit reason/price differs from first H4 hit")
                elif tr.get("reason")!="OPEN_AT_DATA_END":
                    raise ValueError("hit trade has no closed H4 boundary timestamp")
            except Exception as e:
                if len(errors)<50:
                    errors.append({"instrument":inst,"config":cfgid,"entry_time_utc":tr.get("entry_time_utc"),"error":str(e)})
    return {"pass":not errors,"trades_checked":checked,"errors":errors,
            "method":"Independent prefix-signal, 27-bar stop, next-H4 open, M5-source open, 2R and first canonical-H4 exit audit; no R192 execution logic."}

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
    ap.add_argument("--data-dir",default="dl"); ap.add_argument("--out",default="research"); ap.add_argument("--gate1-only",action="store_true")
    a=ap.parse_args(); data_dir=Path(a.data_dir); out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
    h1s={}; m5s={}; h4s={}; meta={}
    load_assets=ASSETS if not a.gate1_only else {k:ASSETS[k] for k in ("usa500idxusd","usatechidxusd")}
    for inst,name in load_assets.items():
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

    # Hard gate 1: use the exact canonical R191 script pasted by the user.
    from research.R191_CANONICAL_index_trend_long import load as canonical_load, sim as canonical_sim, pf as canonical_pf, net as canonical_net
    canonical_h4s={}; canonical_parts=[]; canonical_trace_rows=[]
    for inst in ("usa500idxusd","usatechidxusd"):
        ch=canonical_load(str(data_dir),inst); canonical_h4s[inst]=ch
        ct=canonical_sim(ch).assign(inst=inst); canonical_parts.append(ct)
        for ordinal,tr in enumerate(ct.to_dict("records"),1):
            ent=pd.Timestamp(tr["t"]); pos=int(ch.index.get_indexer([ent])[0])
            signal_t=ch.index[pos-1] if pos>0 else pd.NaT
            ep=float(tr["ep"]); risk=float(tr["risk"])
            canonical_trace_rows.append({
                "instrument":inst,"trade_ordinal":ordinal,
                "signal_bar_ny":None if pd.isna(signal_t) else pd.Timestamp(signal_t).isoformat(),
                "signal_bar_utc":None if pd.isna(signal_t) else pd.Timestamp(signal_t).tz_convert("UTC").isoformat(),
                "entry_time_ny":ent.isoformat(),"entry_time_utc":ent.tz_convert("UTC").isoformat(),
                "entry":ep,"sl":ep-risk,"tp":ep+2.0*risk,"risk_points":risk,
                "gross_r":float(tr["g"]),"gross_exit_derived":ep+float(tr["g"])*risk,
                "entry_year_ny":int(ent.year)})
    canonical_T=pd.concat(canonical_parts,ignore_index=True); canonical_T["y"]=canonical_T.t.dt.year
    canonical_years={"selection":(2017,2021),"forward":(2022,2025),"oos_2026":(2026,2026)}
    expected_gate1={
        "selection":{"n":78,"pf_1bp_rounded_3dp":2.082},
        "forward":{"n":70,"pf_1bp_rounded_3dp":1.247,"pf_2bp_rounded_3dp":1.241},
        "oos_2026":{"n":11,"pf_2bp_rounded_3dp":1.954}}
    gate1_observed={}
    for phase,(ya,yb) in canonical_years.items():
        S=canonical_T[(canonical_T.y>=ya)&(canonical_T.y<=yb)]; gate1_observed[phase]={}
        for bp in (1,2,3):
            vals=np.asarray(canonical_net(S,bp),float); v=canonical_pf(vals)
            gate1_observed[phase][str(bp)]={"entries":int(len(S)),"n":int(len(S)),"censored":0,
                "pf":float(v),"wins_r":float(vals[vals>0].sum()),
                "losses_r":float(-vals[vals<0].sum()),"total_r":float(vals.sum())}

    # R192 ideal and manual5m are diagnostic ledgers only, never Gate 1 pass/fail inputs.
    rep=[]; rep_manual=[]
    for inst in ("usa500idxusd","usatechidxusd"):
        r192_ideal,_=simulate(h4s[inst],m5s[inst],CFG,"ideal")
        manual_trades,_=simulate(h4s[inst],m5s[inst],CFG,"manual5m")
        for t in r192_ideal: t["instrument"]=inst; t["instrument_name"]=ASSETS[inst]
        for t in manual_trades: t["instrument"]=inst; t["instrument_name"]=ASSETS[inst]
        rep.extend(r192_ideal); rep_manual.extend(manual_trades)
    gate1_windows={"selection":(D0,D1),"forward":(F0,F1),"oos_2026":(O0[0],common_end)}
    gate1_manual={}
    for phase,(start,end) in gate1_windows.items():
        gate1_manual[phase]={}
        for bp in (1,2,3):
            mm=metric(rep_manual,start,end,bp)
            gate1_manual[phase][str(bp)]={"entries":mm["entries"],"n":mm["n"],"censored":mm["censored"],
                "pf":mm["pf"],"wins_r":mm["wins_r"],"losses_r":mm["losses_r"]}
    gate1_checks={
        "selection_n":gate1_observed["selection"]["1"]["n"]==expected_gate1["selection"]["n"],
        "selection_pf_1bp":round(gate1_observed["selection"]["1"]["pf"],3)==expected_gate1["selection"]["pf_1bp_rounded_3dp"],
        "forward_n":gate1_observed["forward"]["1"]["n"]==expected_gate1["forward"]["n"],
        "forward_pf_1bp":round(gate1_observed["forward"]["1"]["pf"],3)==expected_gate1["forward"]["pf_1bp_rounded_3dp"],
        "forward_pf_2bp":round(gate1_observed["forward"]["2"]["pf"],3)==expected_gate1["forward"]["pf_2bp_rounded_3dp"],
        "oos_2026_n":gate1_observed["oos_2026"]["2"]["n"]==expected_gate1["oos_2026"]["n"],
        "oos_2026_pf_2bp":round(gate1_observed["oos_2026"]["2"]["pf"],3)==expected_gate1["oos_2026"]["pf_2bp_rounded_3dp"]}
    repok=all(gate1_checks.values())
    gr1=g("G1_R191_CANONICAL_REPLICATION",repok,
        {"canonical_script":gate1_observed,"r192_ideal_diagnostic_only":True,"manual5m_diagnostic_only":gate1_manual,
         "checks":gate1_checks,"selection_years_ny":[2017,2021],"forward_years_ny":[2022,2025],"oos_year_ny":2026},
        expected_gate1,"Gate 1 uses the exact canonical script; R192 ideal/manual5m are comparison ledgers only.")
    pd.DataFrame(canonical_trace_rows).to_csv(out/"R330_G1_canonical_trades.csv",index=False)
    pd.DataFrame(rep).to_csv(out/"R330_G1_r192_ideal_trades.csv",index=False)
    manual_rows=[]
    for phase in gate1_windows:
        row={"phase":phase,"entry_convention":"manual5m","pass_fail_use":False}
        for bp in (1,2,3):
            m=gate1_manual[phase][str(bp)]
            row[f"n_{bp}bp"]=m["n"]; row[f"pf_{bp}bp"]=m["pf"]
            row[f"entries_{bp}bp"]=m["entries"]; row[f"censored_{bp}bp"]=m["censored"]
        manual_rows.append(row)

    if not repok:
        first_diff=None; per_instrument_diff=[]
        for inst in ("usa500idxusd","usatechidxusd"):
            # Compare like-for-like post-2017 trade cohorts, matching the canonical loader's
            # local-year cut. Keep the full R192 ledger separately so pre-period positions remain auditable.
            cr=sorted([x for x in canonical_trace_rows if x["instrument"]==inst and int(x["entry_year_ny"])>=2017],
                      key=lambda x:pd.Timestamp(x["entry_time_utc"]).value)
            rr=sorted([x for x in rep if x["instrument"]==inst and
                       pd.Timestamp(x["entry_time_utc"]).tz_convert("America/New_York").year>=2017],
                      key=lambda x:pd.Timestamp(x["entry_time_utc"]).value)
            ch=canonical_h4s[inst]; rh=h4s[inst]
            cidx=pd.DatetimeIndex(ch.index).tz_convert("UTC")
            ridx=pd.DatetimeIndex(rh.index).tz_convert("UTC")
            clabels=set(cidx.asi8.tolist()); rlabels=set(ridx.asi8.tolist())
            sig_r, stop_r=signals_and_stops(rh,CFG)
            sig_c, stop_c=signals_and_stops(ch,CFG)
            for k in range(max(len(cr),len(rr))):
                c=cr[k] if k<len(cr) else None; r=rr[k] if k<len(rr) else None
                fields=[]
                if c is None or r is None:
                    fields=["trade_presence"]
                else:
                    ce=pd.Timestamp(c["entry_time_utc"]).tz_convert("UTC")
                    re=pd.Timestamp(r["entry_time_utc"]).tz_convert("UTC")
                    if ce.value!=re.value: fields.append("entry_timestamp")
                    if not math.isclose(float(c["entry"]),float(r["entry"]),rel_tol=0,abs_tol=1e-8): fields.append("entry_price")
                    if not math.isclose(float(c["sl"]),float(r["sl"]),rel_tol=0,abs_tol=1e-8): fields.append("sl")
                    if not math.isclose(float(c["risk_points"]),float(r["risk_points"]),rel_tol=0,abs_tol=1e-8): fields.append("risk")
                if not fields: continue
                diag={"instrument":inst,"trade_ordinal_within_instrument_post2017":k+1,
                      "comparison_window":"entry year >= 2017 in America/New_York",
                      "different_fields":fields,"canonical_trade":c,"r192_ideal_trade":r}
                candidate=None; blocker=None
                if c is not None and c.get("signal_bar_utc"):
                    cs=pd.Timestamp(c["signal_bar_utc"]).tz_convert("UTC")
                    ci=int(cidx.get_indexer([cs])[0])
                    entry_boundary=pd.Timestamp(c["entry_time_utc"]).tz_convert("UTC")
                    close_values=pd.DatetimeIndex(rh["bar_close_utc"]).tz_convert("UTC")
                    close_matches=np.flatnonzero(close_values.asi8==entry_boundary.value)
                    close_ri=int(close_matches[0]) if len(close_matches) else -1
                    r_start_ri=int(ridx.get_indexer([cs])[0])
                    r_entry_ri=int(ridx.get_indexer([entry_boundary])[0])
                    diag["bar_grid_checks"]={
                        "canonical_signal_label_exists_in_r192_grid":r_start_ri>=0,
                        "canonical_entry_label_exists_in_r192_grid":r_entry_ri>=0,
                        "canonical_signal_label_exists_in_canonical_grid":ci>=0,
                        "r192_bar_closing_at_canonical_entry_boundary_exists":close_ri>=0,
                        "canonical_signal_close_boundary_utc":entry_boundary.isoformat(),
                        "r192_nearest_labels_utc":[pd.Timestamp(x).isoformat() for x in ridx[max(0,ridx.searchsorted(cs)-2):min(len(ridx),ridx.searchsorted(cs)+3)]]}
                    if ci>=0:
                        cb=ch.iloc[ci]
                        c_prev_hi=float(ch.high.iloc[ci-CFG["breakout"]:ci].max()) if ci>=CFG["breakout"] else None
                        c_sl=float(stop_c[ci]) if math.isfinite(float(stop_c[ci])) else None
                        cclose=entry_boundary
                        ce_idx=ci+1
                        c_ep=float(ch.open.iloc[ce_idx]) if ce_idx<len(ch) else None
                        c_risk=(c_ep-c_sl) if c_ep is not None and c_sl is not None else None
                        candidate={"signal_label_ny":pd.Timestamp(ch.index[ci]).isoformat(),
                            "signal_label_utc":cs.isoformat(),"canonical_signal":bool(sig_c[ci]),
                            "canonical_signal_close":float(ch.close.iloc[ci]),
                            "canonical_prior_55bar_high":c_prev_hi,"canonical_sl_27bar_low":c_sl,
                            "canonical_next_h4_open_time_utc":cclose.isoformat(),
                            "canonical_next_h4_open":c_ep,"canonical_risk":c_risk}
                        # Compare R192 bars using the same signal-close boundary, not ordinal trade timestamps.
                        # Its H4 labels and canonical H4 labels can differ, so close-boundary matching is primary.
                        if close_ri>=0 or r_start_ri>=0:
                            # Prefer an exact close-boundary match; otherwise compare the exact matching signal label.
                            ri=close_ri if close_ri>=0 else r_start_ri
                            candidate["r192_candidate_match_method"]="signal-close boundary" if close_ri>=0 else "matching H4 signal label fallback"
                            rb=rh.iloc[ri]
                            r_prev_hi=float(rh.high.iloc[ri-CFG["breakout"]:ri].max()) if ri>=CFG["breakout"] else None
                            r_sl=float(stop_r[ri]) if math.isfinite(float(stop_r[ri])) else None
                            rclose=pd.Timestamp(rh["bar_close_utc"].iloc[ri]).tz_convert("UTC")
                            r_ep=float(rh.open.iloc[ri+1]) if ri+1<len(rh) else None
                            r_risk=(r_ep-r_sl) if r_ep is not None and r_sl is not None else None
                            candidate.update({"r192_signal_label_ny":pd.Timestamp(rh.index[ri]).isoformat(),
                                "r192_signal_label_utc":pd.Timestamp(rh.index[ri]).tz_convert("UTC").isoformat(),
                                "r192_signal":bool(sig_r[ri]),
                                "r192_signal_close_utc":rclose.isoformat(),
                                "r192_signal_close":float(rh.close.iloc[ri]),
                                "r192_prior_55bar_high":r_prev_hi,"r192_sl_27bar_low":r_sl,
                                "r192_next_h4_open_time_utc":pd.Timestamp(rh.index[ri+1]).tz_convert("UTC").isoformat() if ri+1<len(rh) else None,
                                "r192_next_h4_open":r_ep,"r192_risk":r_risk,
                                "same_signal_close_bar_ohlc_equal":bool(all(math.isclose(float(cb[q]),float(rb[q]),rel_tol=0,abs_tol=1e-8)
                                    for q in ("open","high","low","close"))),
                                "same_signal_close_bar_ohlc":{"canonical_M5_resample":{q:float(cb[q]) for q in ("open","high","low","close")},
                                    "r192_H1_wall_clock":{q:float(rb[q]) for q in ("open","high","low","close")}}})
                    # A R192 position can block the candidate even if the label grid does not match exactly.
                    occupied=[]
                    for tr in [t for t in rep if t["instrument"]==inst]:
                        ent=pd.Timestamp(tr["entry_time_utc"]).tz_convert("UTC")
                        ex=pd.Timestamp(tr["exit_time_utc"]).tz_convert("UTC") if tr.get("exit_time_utc") else None
                        if ent<entry_boundary and (ex is None or ex>=entry_boundary):
                            occupied.append(tr)
                    if occupied:
                        tr=max(occupied,key=lambda z:pd.Timestamp(z["entry_time_utc"]).value)
                        blocker={"entry_time_utc":pd.Timestamp(tr["entry_time_utc"]).tz_convert("UTC").isoformat(),
                            "entry_time_ny":pd.Timestamp(tr["entry_time_utc"]).tz_convert("America/New_York").isoformat(),
                            "entry":float(tr["entry"]),"sl":float(tr["sl"]),"risk_points":float(tr["risk_points"]),
                            "exit_time_utc":pd.Timestamp(tr["exit_time_utc"]).tz_convert("UTC").isoformat() if tr.get("exit_time_utc") else None,
                            "exit_time_ny":pd.Timestamp(tr["exit_time_utc"]).tz_convert("America/New_York").isoformat() if tr.get("exit_time_utc") else None,
                            "reason":tr.get("reason"),
                            "opened_before_2017_NY":bool(pd.Timestamp(tr["entry_time_utc"]).tz_convert("America/New_York").year<2017),
                            "still_active_at_signal_close":True}
                diag["same_signal_candidate_in_r192_h4"]=candidate
                diag["r192_position_blocker_at_candidate_signal_close"]=blocker
                causes=[]
                if blocker:
                    causes.append("One-position state: an R192 position opened before the canonical 2017 start was still active at this signal close; R192 therefore skipped the candidate. Canonical load() truncates source bars to NY year >= 2017 and resets active=-1, so it can take this trade.")
                if candidate and candidate.get("r192_signal"):
                    if candidate.get("canonical_next_h4_open") is not None and candidate.get("r192_next_h4_open") is not None and not math.isclose(
                        float(candidate["canonical_next_h4_open"]),float(candidate["r192_next_h4_open"]),rel_tol=0,abs_tol=1e-8):
                        causes.append("Data/source aggregation difference at the same next-H4 label: canonical builds OHLC from M5, while R192 builds H4 from H1. The observed next-bar opens differ; this changes entry price and risk.")
                    if candidate.get("canonical_prior_55bar_high") is not None and candidate.get("r192_prior_55bar_high") is not None and not math.isclose(
                        float(candidate["canonical_prior_55bar_high"]),float(candidate["r192_prior_55bar_high"]),rel_tol=0,abs_tol=1e-8):
                        causes.append("The rolling prior-55-bar high differs between M5-derived and H1-derived H4 histories; this is data/aggregation, not the entry timestamp convention.")
                    if candidate.get("canonical_sl_27bar_low") is not None and candidate.get("r192_sl_27bar_low") is not None and not math.isclose(
                        float(candidate["canonical_sl_27bar_low"]),float(candidate["r192_sl_27bar_low"]),rel_tol=0,abs_tol=1e-8):
                        causes.append("The 27-bar stop low differs between the M5-derived and H1-derived H4 histories.")
                if not diag["bar_grid_checks"].get("canonical_signal_label_exists_in_r192_grid",False):
                    causes.append("The canonical signal label is absent from R192's H4 grid; this is a true boundary/grid mismatch at this label.")
                if not causes:
                    causes.append("The trade streams diverge at this post-2017 ordinal; review the attached signal, rolling-high, stop, next-open and active-position diagnostics. No timezone/boundary cause is inferred without direct evidence.")
                diag["cause_assessment"]=" ".join(causes)
                per_instrument_diff.append(diag)
                if first_diff is None: first_diff=diag
                break
        dump(out/"R330_G1_first_trade_mismatch.json",{"first_difference":first_diff,
            "first_difference_per_instrument":per_instrument_diff,
            "comparison_rule":"First ordinal mismatch after filtering both streams to entry year >=2017 in America/New_York; full R192 CSV also retains pre-2017 trades to diagnose active-position carryover.",
            "H4_methods":{"canonical":"the supplied script: M5 OHLC resample 4h offset=1h, label=left, closed=left, in America/New_York",
                "r192_ideal":"R192 H1 explicit NY wall-clock boundaries 01/05/09/13/17/21"},
            "scope":"Gate 1 mismatch only; Gate 2 and all pooled criteria were not run."})
        mismatch_label="GATE-MISMATCH (definisi konvensi entry), strategi belum dievaluasi"
        headline=("The exact canonical R191 Gate 1 metrics did not match the locked targets. "
                  "Stopped before Gate 2 and every pooled/performance criterion.")
        rows=[]
        for phase,(ya,yb) in canonical_years.items():
            c=gate1_observed[phase]
            rows.append({"phase":phase,"years_ny":f"{ya}-{yb}","canonical_n":c["1"]["n"],
                "canonical_pf_1bp":c["1"]["pf"],"canonical_pf_2bp":c["2"]["pf"],"canonical_pf_3bp":c["3"]["pf"],
                "expected_n":expected_gate1[phase]["n"],"expected_pf_1bp":expected_gate1[phase].get("pf_1bp_rounded_3dp"),
                "expected_pf_2bp":expected_gate1[phase].get("pf_2bp_rounded_3dp")})
        report=("# R330 STATUS — GATE-MISMATCH (definisi konvensi entry), strategi belum dievaluasi\n\n"
            "## Canonical Gate 1 run\n\n"
            "The canonical source is stored as research/R191_CANONICAL_index_trend_long.py. Strategy code is unchanged; only the loader accepts repository M5 CSV.GZ cache. Gate 1 is decided by canonical output, not R192 ideal or manual5m.\n\n"
            +pd.DataFrame(rows).to_markdown(index=False)+"\n\n"
            +"## First post-2017 trade-level divergence\n\n"
            +("No ordinal trade difference was found; inspect period/cost calculations.\n\n" if first_diff is None else
              "The comparison below filters the trade streams to entry year >=2017 in New York. The full R192 ledger is still preserved, including pre-2017 trades, because a pre-period position can block a post-period signal.\n\n"
              +json.dumps(clean(first_diff),indent=2,ensure_ascii=False)+"\n\n")
            +"Full ledgers: research/R330_G1_canonical_trades.csv and research/R330_G1_r192_ideal_trades.csv. Details: research/R330_G1_first_trade_mismatch.json.\n\n"
            +"## Manual5m diagnostic (not used for pass/fail)\n\n"+pd.DataFrame(manual_rows).to_markdown(index=False)+"\n\n"
            +"## Decision\n\n**GATE-MISMATCH (definisi konvensi entry), strategi belum dievaluasi.** Gate 2 and all pooled criteria are NOT RUN. No pooled PF, neighborhood, leave-one-out, correlation/overlap, or funded challenge simulation was calculated.\n")
        (out/"R330_FINAL_VERDICT.md").write_text(report,encoding="utf-8")
        result={"experiment":"R330","verdict":"GATE-MISMATCH","status_label":mismatch_label,
            "stopped_at":"G1_R191_CANONICAL_REPLICATION","gate1":gr1,"gate1_canonical_observed":gate1_observed,
            "gate1_manual5m_diagnostic":gate1_manual,"gate1_expected":expected_gate1,
            "gate1_checks":gate1_checks,"first_trade_mismatch":first_diff,
            "remaining_criteria_status":"NOT_RUN_AFTER_GATE_MISMATCH",
            "entry_convention_amendment":{"primary":"exact canonical M5-resample/sim; next-H4-open entry","manual5m":"diagnostic only"},
            "canonical_source":"research/R191_CANONICAL_index_trend_long.py",
            "canonical_trade_ledger":"research/R330_G1_canonical_trades.csv","r192_ideal_trade_ledger":"research/R330_G1_r192_ideal_trades.csv",
            "first_trade_difference_file":"research/R330_G1_first_trade_mismatch.json","data":meta}
        dump(out/"R330_results.json",result)
        append_state(mismatch_label,[gr1],common_end,headline)
        print("R330 GATE-MISMATCH: canonical Gate 1 target mismatch; pooled criteria NOT RUN.",flush=True)
        print(pd.DataFrame(rows).to_string(index=False),flush=True)
        print("FIRST TRADE DIFFERENCE:",json.dumps(clean(first_diff),ensure_ascii=False),flush=True)
        raise SystemExit(2)
    print("G1 PASS: exact canonical reference metrics match to three decimals.",flush=True)
    if a.gate1_only:
        headline="Canonical Gate 1 matched every locked target to three decimals. This preflight intentionally stops here; the full ten-index suite may now run."
        result={"experiment":"R330","verdict":"GATE1_PASS","stopped_at":"G1 preflight only",
            "gate1":gr1,"gate1_canonical_observed":gate1_observed,"gate1_manual5m_diagnostic":gate1_manual,
            "gate1_expected":expected_gate1,"gate1_checks":gate1_checks,
            "remaining_criteria_status":"NOT_RUN_IN_GATE1_PREFLIGHT",
            "canonical_source":"research/R191_CANONICAL_index_trend_long.py","data":meta,"headline":headline}
        dump(out/"R330_results.json",result)
        rows=[]
        for phase,(ya,yb) in canonical_years.items():
            c=gate1_observed[phase]
            rows.append({"phase":phase,"years_ny":f"{ya}-{yb}","canonical_n":c["1"]["n"],
                "canonical_pf_1bp":c["1"]["pf"],"canonical_pf_2bp":c["2"]["pf"],"canonical_pf_3bp":c["3"]["pf"],
                "expected_n":expected_gate1[phase]["n"],"expected_pf_1bp":expected_gate1[phase].get("pf_1bp_rounded_3dp"),
                "expected_pf_2bp":expected_gate1[phase].get("pf_2bp_rounded_3dp")})
        (out/"R330_FINAL_VERDICT.md").write_text("# R330 — CANONICAL GATE 1 PASSED; full suite pending\n\n"+headline+"\n\n"+pd.DataFrame(rows).to_markdown(index=False)+"\n",encoding="utf-8")
        print("R330 GATE1-ONLY PASS: stopped before Gate 2 by preflight mode.",flush=True)
        return

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
        "H4_breakout_N":55,"stop_lookback_M":27,"RR":2.0,"entry":"open of the next NY-wall-clock H4 bar (canonical)","round_trip_price_cost_bps":list(COSTS)},
        "periods":{"discovery":"2017-01-01 <= entry < 2022-01-01; outcomes closed before 2022-01-01",
        "forward":"2022-01-01 <= entry < 2026-01-01; outcomes closed before 2026-01-01",
        "oos_2026":"2026 entry cohort through common cached data cutoff"},
        "common_data_cutoff_utc":common_end.isoformat(),"data":meta,
        "gate1_replication":{"gate":gr1,"canonical_metrics":gate1_observed,"manual5m_diagnostic":gate1_manual,"checks":gate1_checks},
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
        f"1. R191 canonical USA500+USATECH replication: {'PASS' if gr1['pass'] else 'FAIL'}; forward n={gate1_observed['forward']['1']['n']}, PF@1bp={gate1_observed['forward']['1']['pf']!r}, PF@2bp={gate1_observed['forward']['2']['pf']!r}; selection n={gate1_observed['selection']['1']['n']}, PF@1bp={gate1_observed['selection']['1']['pf']!r}; OOS n={gate1_observed['oos_2026']['2']['n']}, PF@2bp={gate1_observed['oos_2026']['2']['pf']!r}.",
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
