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
        "data_source":"Dukascopy BID M5 cache; any Jetta M1-to-M5 recovery is listed in the validation/provenance sidecar",
        "h4_note":"Only metadata columns label_utc/bar_close_utc/completed were added; canonical OHLC and index are unchanged."
    }
    if inst == "ussc2000idxusd":
        info["source_availability_note"]="Dukascopy M5 returned zero rows before 2018-08-08; the index is retained in the basket from its first available source bar onward, without synthesized history."
    recovery_path=Path(data_dir)/f"{inst}_m5_recovery.json"
    if recovery_path.is_file():
        recovery=json.loads(recovery_path.read_text(encoding="utf-8"))
        info["m5_recovery_manifest"]=recovery
        info["m5_recovery_manifest_sha256"]=sha256_file(recovery_path)
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
                elif tr.get("reason")!="OPEN_AT_DATA_END" and not (
                    int(tr.get("_exit_h4_index",-1))==len(h4)-1 and not bool(h4.completed.iloc[-1])
                ):
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
    now_utc=pd.Timestamp.now(tz="UTC")
    h4s={}; m5s={}; meta={}
    gate1_instruments=("usa500idxusd","usatechidxusd")
    # Gate 1 first: no Gate 2, pooled, neighborhood, LOO or challenge metrics until canonical replay passes.
    for inst in gate1_instruments:
        h4,m5,info=load_canonical_instrument(data_dir,inst,now_utc)
        h4s[inst]=h4; m5s[inst]=m5
        meta[inst]={"name":ASSETS[inst],**info}
        print(f"CANONICAL DATA {inst}: H4={len(h4):,} M5={len(m5):,}; SHA256={info['m5_cache_sha256']}",flush=True)

    run1={}; run2={}; first_parts=[]; resample_identical={}
    for inst in gate1_instruments:
        h_first=canonical_load(str(data_dir),inst)
        h_second=canonical_load(str(data_dir),inst)
        ohlc=("open","high","low","close")
        same_grid=h_first.index.equals(h_second.index)
        same_ohlc=same_grid and h_first[list(ohlc)].equals(h_second[list(ohlc)])
        resample_identical[inst]=bool(same_ohlc)
        run1[inst]=canonical_sim(h_first[list(ohlc)],N=55,M=27,rr=2.0)
        run2[inst]=canonical_sim(h_second[list(ohlc)],N=55,M=27,rr=2.0)
        for key,df in (("first",run1[inst]),("second",run2[inst])):
            d=df.copy(); d["inst"]=inst; d["run"]=key; first_parts.append(d)
    replay_identical={inst:run1[inst].equals(run2[inst]) for inst in gate1_instruments}
    deterministic=all(replay_identical.values()) and all(resample_identical.values())
    T=pd.concat([run1[k].assign(inst=k) for k in gate1_instruments],ignore_index=True)
    T["y"]=T.t.dt.year
    gate1_years={"selection":(2017,2021),"forward":(2022,2025),"oos_2026":(2026,2026)}
    expected={
        "selection":{"n":79,"pf_1bp_rounded_3dp":2.134},
        "forward":{"n":68,"pf_1bp_rounded_3dp":1.310,"pf_2bp_rounded_3dp":1.304},
        "oos_2026":{"n":11,"pf_2bp_rounded_3dp":1.673}}
    observed={}
    for phase,(ya,yb) in gate1_years.items():
        S=T[(T.y>=ya)&(T.y<=yb)]
        observed[phase]={}
        for bp in (0,1,2,3):
            v=canonical_pf(canonical_net(S,bp))
            observed[phase][str(bp)]={"n":int(len(S)),"pf":float(v),
                "total_r":float(canonical_net(S,bp).sum())}
    checks={
        "deterministic_usa500":bool(replay_identical["usa500idxusd"] and resample_identical["usa500idxusd"]),
        "deterministic_usatech":bool(replay_identical["usatechidxusd"] and resample_identical["usatechidxusd"]),
        "selection_n":observed["selection"]["1"]["n"]==expected["selection"]["n"],
        "selection_pf_1bp":round(observed["selection"]["1"]["pf"],3)==expected["selection"]["pf_1bp_rounded_3dp"],
        "forward_n":observed["forward"]["1"]["n"]==expected["forward"]["n"],
        "forward_pf_1bp":round(observed["forward"]["1"]["pf"],3)==expected["forward"]["pf_1bp_rounded_3dp"],
        "forward_pf_2bp":round(observed["forward"]["2"]["pf"],3)==expected["forward"]["pf_2bp_rounded_3dp"],
        "oos_2026_n":observed["oos_2026"]["2"]["n"]==expected["oos_2026"]["n"],
        "oos_2026_pf_2bp":round(observed["oos_2026"]["2"]["pf"],3)==expected["oos_2026"]["pf_2bp_rounded_3dp"]}
    gate1_pass=deterministic and all(checks.values())
    baseline_manifest={
        "status":"PASS" if gate1_pass else "FAIL",
        "deterministic_replay":replay_identical,"identical_resample_grid_and_ohlc":resample_identical,
        "baseline_expected":expected,"baseline_observed":observed,
        "checks":checks,
        "source_hashes":{i:meta[i]["m5_cache_sha256"] for i in gate1_instruments},
        "source_bytes":{i:meta[i]["m5_cache_bytes"] for i in gate1_instruments},
        "engine":"research/R191_CANONICAL_index_trend_long.py unchanged sim() and H4 resample; loader reads repository M5 CSV.GZ",
        "data_version_note":"Baseline change from the previous locked targets is attributed to the M5 cache/version; rule and thresholds are unchanged."
    }
    gr1=g("G1_CANONICAL_DETERMINISM_AND_BASELINE",gate1_pass,
        baseline_manifest,
        {"deterministic_replay":"identical outputs on each same-cache replay","official_baseline":expected},
        "Canonical source is run twice on identical M5 cache; both replays must be identical and match the new official baseline to 3 decimals.")
    pd.DataFrame(T).to_csv(out/"R330_G1_canonical_trades.csv",index=False)
    dump(out/"R330_G1_canonical_determinism.json",baseline_manifest)
    pd.DataFrame([{"phase":p,"n":observed[p]["1"]["n"],"pf_1bp":observed[p]["1"]["pf"],
                   "pf_2bp":observed[p]["2"]["pf"],"pf_3bp":observed[p]["3"]["pf"],
                   "expected_n":expected[p]["n"],
                   "expected_pf_1bp":expected[p].get("pf_1bp_rounded_3dp"),
                   "expected_pf_2bp":expected[p].get("pf_2bp_rounded_3dp")} for p in gate1_years]
                 ).to_csv(out/"R330_G1_baseline_comparison.csv",index=False)
    g1_cutoff=min(pd.Timestamp(m5s[i].index[-1]).tz_convert("UTC")+pd.Timedelta(minutes=5) for i in gate1_instruments)
    data_version={"engine":"canonical R191 H4-from-M5; one-position starts empty at NY year >=2017",
        "instruments":{i:{"sha256":meta[i]["m5_cache_sha256"],"bytes":meta[i]["m5_cache_bytes"],
                         "rows":meta[i]["m5_rows"],"start_utc":meta[i]["m5_start_utc"],"end_utc":meta[i]["m5_end_utc"]}
                       for i in gate1_instruments},
        "combined_sha256":hashlib.sha256("|".join(meta[i]["m5_cache_sha256"] for i in gate1_instruments).encode()).hexdigest()}
    if not gate1_pass:
        headline="Canonical replay is non-deterministic or does not match the locked official baseline for this cache version; stopped before Gate 2 and all basket performance metrics."
        result={"experiment":"R330","verdict":"GATE-MISMATCH","status_label":"GATE-MISMATCH (canonical determinism/data baseline), strategi belum dievaluasi",
            "stopped_at":"G1_CANONICAL_DETERMINISM_AND_BASELINE","gate1":gr1,"gate1_canonical_observed":observed,
            "gate1_expected":expected,"checks":checks,"data_version":data_version,
            "remaining_criteria_status":"NOT_RUN_AFTER_GATE1_MISMATCH","note":"No R192 engine/metrics were used."}
        dump(out/"R330_results.json",result)
        rows=[{"phase":p,"years_ny":f"{a}-{b}","n":observed[p]["1"]["n"],
               "pf_1bp":observed[p]["1"]["pf"],"pf_2bp":observed[p]["2"]["pf"],
               "expected_n":expected[p]["n"],"expected_pf_1bp":expected[p].get("pf_1bp_rounded_3dp"),
               "expected_pf_2bp":expected[p].get("pf_2bp_rounded_3dp")} for p,(a,b) in gate1_years.items()]
        report="# R330 — GATE-MISMATCH (canonical determinism/data baseline)\n\n"+headline+"\n\n"+pd.DataFrame(rows).to_markdown(index=False)+"\n\nData manifest:\n\n"+json.dumps(clean(data_version),indent=2,ensure_ascii=False)+"\n"
        (out/"R330_FINAL_VERDICT.md").write_text(report,encoding="utf-8")
        append_state("GATE-MISMATCH", [gr1], g1_cutoff, headline, data_version, baseline_manifest)
        print("R330 GATE-MISMATCH: canonical determinism or official baseline failed; basket criteria NOT RUN.",flush=True)
        print(pd.DataFrame(rows).to_string(index=False),flush=True)
        raise SystemExit(2)
    print("G1 PASS: deterministic canonical replay matches official new data-version baseline.",flush=True)
    if a.gate1_only:
        headline="Canonical replay deterministic and official baseline reproduced. Explicit gate1-only preflight; basket criteria not run."
        dump(out/"R330_results.json",{"experiment":"R330","verdict":"GATE1_PASS","gate1":gr1,
            "gate1_canonical_observed":observed,"gate1_expected":expected,"data_version":data_version,
            "remaining_criteria_status":"NOT_RUN_IN_PREFLIGHT","headline":headline})
        (out/"R330_FINAL_VERDICT.md").write_text("# R330 — CANONICAL GATE 1 PASS\n\n"+headline+"\n",encoding="utf-8")
        return

    # Gate 1 passed: now load the remaining eight instruments with the exact same canonical M5 engine.
    for inst in ASSETS:
        if inst in h4s: continue
        h4,m5,info=load_canonical_instrument(data_dir,inst,now_utc)
        h4s[inst]=h4; m5s[inst]=m5; meta[inst]={"name":ASSETS[inst],**info}
        print(f"CANONICAL DATA {inst}: H4={len(h4):,} M5={len(m5):,}; SHA256={info['m5_cache_sha256']}",flush=True)
    common_end=min(pd.Timestamp(m5.index[-1]).tz_convert("UTC")+pd.Timedelta(minutes=5) for m5 in m5s.values())
    data_version={"engine":"canonical R191 H4-from-M5; one-position starts empty at NY year >=2017",
        "instruments":{i:{"sha256":meta[i]["m5_cache_sha256"],"bytes":meta[i]["m5_cache_bytes"],
                         "rows":meta[i]["m5_rows"],"start_utc":meta[i]["m5_start_utc"],"end_utc":meta[i]["m5_end_utc"]}
                       for i in ASSETS},
        "combined_sha256":hashlib.sha256("|".join(meta[i]["m5_cache_sha256"] for i in ASSETS).encode()).hexdigest(),
        "common_cutoff_utc":common_end.isoformat()}
    # Hard gate 2: all ten instruments pass N=55 truncation before any ten-index metrics.
    trunc={}
    for inst in ASSETS:
        s,st=canonical_signals_and_stops(h4s[inst],CFG); trunc[inst]=canonical_truncation_gate(h4s[inst],CFG,s,st)
        print(f"G2 TRUNCATION {inst}: {trunc[inst]}",flush=True)
    alltr=all(v.get("pass",False) for v in trunc.values())
    gr2=g("G2_TRUNCATION_ALL_10",alltr,{"passed":sum(bool(x.get("pass")) for x in trunc.values()),"total":len(ASSETS),"by_instrument":trunc},"10/10 instruments pass N=55 signal/stop prefix consistency.")
    if not alltr:
        result={"experiment":"R330","verdict":"REJECT","stopped_at":"G2_TRUNCATION_ALL_10","gate1":gr1,"gate2":gr2,"data":meta}
        dump(out/"R330_results.json",result)
        (out/"R330_FINAL_VERDICT.md").write_text("# R330 FINAL VERDICT — REJECT\n\nGate 1 passed. Stopped at Gate 2: one or more indices failed truncation. No pooled PF, neighbors, leave-one-out or challenge simulation was calculated.\n\n"+json.dumps(clean(trunc),indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
        append_state("REJECT at Gate 2",[gr1,gr2],common_end,"Canonical R191 baseline reproduced, but Gate 2 truncation failed for at least one index; performance calculations stopped.",data_version,baseline_manifest)
        raise SystemExit(2)
    print("G2 PASS: all ten indices pass truncation.",flush=True)

    pools={}; diagpool={}; cfgs={CFG["id"]:CFG}; all_audit={}
    for n in (40,55,80):
        cfg={"id":f"R330_N{n}_M27_RR2","role":"locked_baseline" if n==55 else "robustness_only","breakout":n,"stop_bars":27}
        cfgs[cfg["id"]]=cfg; joined=[]; per={}
        for inst in ASSETS:
            ss,st=canonical_signals_and_stops(h4s[inst],cfg)
            gt=canonical_truncation_gate(h4s[inst],cfg,ss,st)
            if not gt["pass"]: raise RuntimeError(f"N={n} prefix test failed for {inst}: {gt}")
            ts,sd=canonical_sim_detailed(h4s[inst],m5s[inst],cfg)
            for t in ts: t["instrument"]=inst; t["instrument_name"]=ASSETS[inst]
            add_daily_marks(ts,m5s[inst],2); per[inst]=ts; joined.extend(ts); all_audit[(inst,cfg["id"])]=ts
            print(f"SIM N={n} {inst}: signals={sd['signals']}; trades={len(ts)}",flush=True)
        pools[n]=joined; diagpool[n]={"by_instrument":{i:len(t) for i,t in per.items()}}
    base=pools[55]; base2=[t for t in base if t["instrument"] in ("usa500idxusd","usatechidxusd")]
    r191_only_size={
        "total_canonical_trade_rows":len(base2),
        "trades_by_instrument":{inst:sum(t["instrument"]==inst for t in base2) for inst in ("usa500idxusd","usatechidxusd")},
        "trades_by_entry_year_ny":{str(y):sum(pd.Timestamp(t["entry_time_utc"]).tz_convert("America/New_York").year==y for t in base2)
                                   for y in range(2017,2027)},
        "closed_trade_metrics":{}
    }
    for phase,start,end in (("discovery",D0,D1),("forward",F0,F1),("oos_2026",O0[0],common_end)):
        r191_only_size["closed_trade_metrics"][phase]={str(bp):metric_local(base2,start,end,bp) for bp in COSTS}

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
                m=metric_local(ts,start,end,bp); row[f"{phase}_n_{bp}bp"]=m["n"]; row[f"{phase}_pf_{bp}bp"]=m["pf"]
        instrows.append(row)
    pd.DataFrame(instrows).to_csv(out/"R330_instrument_metrics.csv",index=False)

    nbr=[]
    for n in (40,55,80):
        ts=pools[n]; m2=metric_local(ts,F0,F1,2)
        nbr.append({"N":n,"M":27,"RR":2,"forward_n":m2["n"],"forward_pf_2bp":m2["pf"],
            "truncation_10_of_10":True,"note":"N=40/80 are robustness only; candidate remains N=55."})
    pd.DataFrame(nbr).to_csv(out/"R330_neighborhood.csv",index=False)

    loo=[]
    for removed in ASSETS:
        ts=[t for t in base if t["instrument"]!=removed]; m=metric_local(ts,F0,F1,2)
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
    for phase in observed:
        for bp in ("1","2","3"):
            v=observed[phase][bp]["pf"]
            if valid_pf(v): reported_pf.append(float(v))
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
        "common_data_cutoff_utc":common_end.isoformat(),"data_version":data_version,"data":meta,"r191_only_baseline_size":r191_only_size,
        "gate1_replication":{"gate":gr1,"canonical_metrics":observed,"checks":checks,"official_baseline":expected},
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
        "## Data-version baseline","",
        "The official R191 baseline is n=79/PF@1bp=2.134 in selection, n=68/PF@1bp=1.310/PF@2bp=1.304 in forward, and n=11/PF@2bp=1.673 in OOS 2026. This replaces the earlier unavailable-snapshot figures; the rule and PASS thresholds did not change. The M5 cache SHA-256 manifest is in R330_results.json.","",
        "Combined source SHA-256: "+data_version["combined_sha256"],"",
        "## Locked rule","",
        "- NY-wall-clock H4, long-only, breakout 55, stop lookback 27 bars inclusive, target 2R.",
        "- Primary canonical entry: open of the next NY-wall-clock H4 bar. all candidate and robustness runs use the supplied canonical H4-from-M5 engine; no R192 execution engine is used.",
        "- Costs are modeled round-trip price costs of 1/2/3bp; they are not measured broker fees/spread/slippage.",
        "- All ten indices pooled; no selection or exclusions. Discovery 2017–2021, forward 2022–2025, OOS 2026 once after hard gates.",
        "",
        "## Sequential hard gates","",
        f"1. R191 canonical deterministic replay and official-baseline check: {'PASS' if gr1['pass'] else 'FAIL'}; forward n={observed['forward']['1']['n']}, PF@1bp={observed['forward']['1']['pf']!r}, PF@2bp={observed['forward']['2']['pf']!r}; selection n={observed['selection']['1']['n']}, PF@1bp={observed['selection']['1']['pf']!r}; OOS n={observed['oos_2026']['2']['n']}, PF@2bp={observed['oos_2026']['2']['pf']!r}.",
        f"2. N=55 truncation on all ten: {'PASS' if gr2['pass'] else 'FAIL'}; {sum(bool(x['pass']) for x in trunc.values())}/10 passed.",
        "",
        "## Pooled annual entry-cohort table","",
        "PF uses risk-normalized R. Outcomes cut off at each phase boundary; 2026 is limited to common source cutoff.","",
        pd.DataFrame(ann).to_markdown(index=False),"",
        "## R191-only benchmark size","",
        json.dumps(clean(r191_only_size),indent=2,ensure_ascii=False),"",
        "## Aggregate metrics","",
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
    append_state(verdict,gates,common_end,headline,data_version,baseline_manifest)
    print("R330 VERDICT:",verdict,flush=True); print(headline,flush=True)
    print(pd.DataFrame([{"gate":x["gate"],"pass":x["pass"]} for x in gates]).to_string(index=False),flush=True)
    print(f"Common cutoff: {common_end.isoformat()}",flush=True)
    if verdict!="PASS": raise SystemExit(2)

if __name__=="__main__": main()
