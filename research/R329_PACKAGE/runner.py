#!/usr/bin/env python3
"""R329 pre-outcome-only data and eligibility audit. Contains no PnL/outcome calculation."""
from __future__ import annotations
import argparse, gzip, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

PAIRS = ["audusd", "eurusd", "gbpusd", "nzdusd", "usdcad", "usdchf", "usdjpy"]
HORIZONS = [13, 26, 39]
H1 = 3_600_000
WEEK = 168 * H1
USD_LOAD = {p: (-1 if p.endswith("usd") else 1) for p in PAIRS}


def sha(path):
    h=hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(1024*1024),b""): h.update(b)
    return h.hexdigest()


def jwrite(path,obj):
    path.write_text(json.dumps(obj,sort_keys=True,indent=2,allow_nan=False)+"\n",encoding="utf-8")


def target_weights(signals,vols):
    """Feature-only inverse-vol weights with pair and USD-factor caps; no future-price access."""
    signals=np.asarray(signals,float); vols=np.asarray(vols,float)
    valid=np.isfinite(signals)&np.isfinite(vols)&(vols>0)&(signals!=0)
    raw=np.zeros(7,float); raw[valid]=np.sign(signals[valid])/vols[valid]
    gross0=float(np.abs(raw).sum())
    if gross0<=0: return np.zeros(7),{"gross_pre_cap":0.,"gross_after_pair_cap":0.,"gross_final":0.,"net_usd_final":0.,"usd_net_ratio_final":0.}
    raw/=gross0; raw=np.sign(raw)*np.minimum(np.abs(raw),.25)
    gross=float(np.abs(raw).sum()); load=raw*np.array([USD_LOAD[p] for p in PAIRS],float)
    pos=float(np.maximum(load,0).sum()); neg=float(np.maximum(-load,0).sum())
    if gross>0 and abs(pos-neg)>.30*gross+1e-12:
        if pos>neg: raw[load>0]*=(0. if neg==0 else min(1.,neg*1.30/(pos*.70)))
        else: raw[load<0]*=(0. if pos==0 else min(1.,pos*1.30/(neg*.70)))
    load=raw*np.array([USD_LOAD[p] for p in PAIRS],float); gross1=float(np.abs(raw).sum()); net=float(load.sum())
    return raw,{"gross_pre_cap":gross0,"gross_after_pair_cap":gross,"gross_final":gross1,"net_usd_final":net,"usd_net_ratio_final":abs(net)/gross1 if gross1>1e-12 else 0.}


def self_tests():
    msgs=[]
    w,m=target_weights([1,1,-1,-1,1,1,-1],[.01,.02,.03,.04,.02,.03,.04])
    assert np.max(np.abs(w))<=.25+1e-12 and m["usd_net_ratio_final"]<=.30+1e-10
    assert np.all((w==0)|(np.sign(w)==np.sign([1,1,-1,-1,1,1,-1])))
    msgs.append("mixed USD exposure cap and sign preservation: PASS")
    w,m=target_weights([-1,-1,-1,-1,1,1,1],np.ones(7)*.02)
    assert np.allclose(w,0) and m["gross_final"]==0
    msgs.append("one-way USD factor is flattened, not reversed: PASS")
    w,m=target_weights(np.zeros(7),np.ones(7)*.02)
    assert np.allclose(w,0)
    msgs.append("zero signal creates no position: PASS")
    w,_=target_weights(np.ones(7),[0,np.nan,1,1,1,1,1])
    assert w[0]==0 and w[1]==0
    msgs.append("invalid volatility is skipped: PASS")
    return msgs


def read_inputs(package,data_dir):
    manifest=json.loads((package/"data_manifest.json").read_text(encoding="utf-8"))
    if manifest.get("combined_ordered_stream_manifest_sha256")!="2db7c7d88b2f31965ff956dd5e017ce7f0b76a4ac1792dca4896833b884e85e0":
        raise ValueError("official combined stream manifest pin mismatch")
    exp={x["name"]:x for x in manifest["streams"]}; pairs={}; details={}; errors=[]; actual=0
    for p in PAIRS:
        sides={}
        for side in ("bid","ask"):
            name=f"{p}_h1_{side}.csv"; path=data_dir/name
            if name not in exp or not path.is_file(): errors.append(f"missing_stream:{name}"); continue
            got=sha(path); spec=exp[name]; actual+=1
            if got!=spec["sha256"]: errors.append(f"sha_mismatch:{name}")
            if path.stat().st_size!=spec["bytes"]: errors.append(f"size_mismatch:{name}")
            d=pd.read_csv(path)
            if not {"timestamp","open","high","low","close"}.issubset(d.columns): errors.append(f"bad_columns:{name}"); continue
            d["timestamp"]=pd.to_numeric(d.timestamp,errors="coerce")
            if d.timestamp.isna().any(): errors.append(f"bad_timestamp:{name}")
            d.timestamp=d.timestamp.astype("int64")
            vals=d[["open","high","low","close"]].apply(pd.to_numeric,errors="coerce").to_numpy(float)
            dup=int(d.timestamp.duplicated().sum()); aligned=int((d.timestamp%H1 != 0).sum()); nonfinite=int((~np.isfinite(vals)).any(axis=1).sum())
            bad=int(((d.high<d.low)|(d.high<d[["open","close"]].max(axis=1))|(d.low>d[["open","close"]].min(axis=1))).sum())
            mono=bool(d.timestamp.is_monotonic_increasing)
            if dup or aligned or nonfinite or bad or not mono: errors.append(f"row_integrity:{name}:dup={dup},align={aligned},nonfinite={nonfinite},bad_ohlc={bad},monotonic={mono}")
            details[name]={"sha256":got,"bytes":path.stat().st_size,"rows":len(d),"duplicates":dup,"misaligned_h1":aligned,"nonfinite_rows":nonfinite,"invalid_ohlc_rows":bad,"monotonic":mono,"flat_placeholder_rows":int(((d.high==d.low)&(d.open==d.close)).sum()),"start_utc":pd.to_datetime(int(d.timestamp.min()),unit="ms",utc=True).isoformat(),"end_utc":pd.to_datetime(int(d.timestamp.max()),unit="ms",utc=True).isoformat()}
            sides[side]=d
        if set(sides)!={"bid","ask"}: continue
        b,a=sides["bid"],sides["ask"]; bs=set(b.timestamp); ass=set(a.timestamp)
        if bs!=ass: errors.append(f"bid_ask_timestamp_mismatch:{p}:{len(bs-ass)}:{len(ass-bs)}")
        m=b.merge(a,on="timestamp",suffixes=("_bid","_ask"),how="inner",validate="one_to_one").sort_values("timestamp").reset_index(drop=True)
        so=m.open_ask-m.open_bid; sc=m.close_ask-m.close_bid
        no=int((so<0).sum()); nc=int((sc<0).sum())
        if no or nc: errors.append(f"negative_spread:{p}:{no}:{nc}")
        m["active"]=((m.high_bid>m.low_bid)|(m.high_ask>m.low_ask)|(m.open_bid!=m.close_bid)|(m.open_ask!=m.close_ask))
        m["mid_close"]=(m.close_bid+m.close_ask)/2; m["spread_open"]=so
        ts=m.timestamp.to_numpy(dtype="int64"); details[f"PAIR_{p}"]={"bid_rows":len(b),"ask_rows":len(a),"paired_timestamps":len(m),"bid_only":len(bs-ass),"ask_only":len(ass-bs),"negative_open_spreads":no,"negative_close_spreads":nc,"active_rows":int(m.active.sum()),"flat_rows":int((~m.active).sum()),"gaps_gt_1h":int(np.sum(np.diff(ts)>H1)),"median_open_spread_price":float(so.median()),"p95_open_spread_price":float(so.quantile(.95))}
        pairs[p]=m
    if actual!=14 or len(pairs)!=7: errors.append(f"coverage_count:streams={actual},pairs={len(pairs)}")
    sets=[set(x.timestamp.to_numpy(dtype="int64")) for x in pairs.values()]
    common=set.intersection(*sets) if len(sets)==7 else set()
    union=set.union(*sets) if len(sets)==7 else set()
    unmatched={p:len(set(m.timestamp.to_numpy(dtype="int64"))-common) for p,m in pairs.items()}
    details["CROSS_PAIR_SYNC"]={"exact_timestamp_intersection_rows":len(common),"union_rows":len(union),"unmatched_rows_by_pair":unmatched,"policy":"exact inner intersection only; no forward fill or nearest join"}
    audit={"experiment_id":"R329","mode":"PREOUTCOME_DATA_AUDIT_ONLY_NO_PNL","data_gate":"PASS" if not errors else "FAIL","fatal_errors":errors,"expected_streams":14,"actual_streams":actual,"expected_pairs":7,"actual_pairs":len(pairs),"period_utc":{"start_inclusive":"2017-01-01T00:00:00Z","end_exclusive":"2026-01-01T00:00:00Z"},"provider":"Dukascopy native H1 BID/ASK","official_source_workflow_run":39719343805,"source_manifest_sha256":manifest["combined_ordered_stream_manifest_sha256"],"flat_rows":"preserved; excluded only for active signal/entry/exit eligibility","gaps":"preserved; no synthetic bars or fill-forward","stream_audit":details}
    return pairs,common,audit,manifest,errors


def run(package,data_dir,out_dir):
    out_dir.mkdir(parents=True,exist_ok=True); tests=self_tests()
    pairs,common,audit,manifest,errors=read_inputs(package,data_dir); jwrite(out_dir/"data_audit.json",audit)
    if errors:
        summary={"experiment_id":"R329","verdict":"GAGAL","first_failed_gate":"data_gate","outcomes_computed":False,"pnl_computed":False,"self_tests":tests,"errors":errors}
        jwrite(out_dir/"preflight_summary.json",summary); return summary
    lookup={p:{int(t):bool(a) for t,a in zip(m.timestamp,m.active)} for p,m in pairs.items()}
    mids={p:{int(t):float(c) for t,c in zip(m.timestamp,m.mid_close)} for p,m in pairs.items()}
    common=sorted(common); common_set=set(common); snapshots=[]; snap_prices=[]
    for t in common:
        dt=pd.to_datetime(t,unit="ms",utc=True)
        if dt.weekday()!=1 or dt.hour!=10 or dt.minute: continue
        if not all(lookup[p].get(t,False) for p in PAIRS): continue
        vals=np.array([mids[p][t] for p in PAIRS],float)
        if np.isfinite(vals).all() and (vals>0).all(): snapshots.append(t); snap_prices.append(vals)
    snap_prices=np.asarray(snap_prices,float); snap_idx={t:i for i,t in enumerate(snapshots)}
    schedule=pd.date_range("2017-01-03","2025-12-30",freq="W-TUE",tz="UTC")
    periods={"discovery":(pd.Timestamp("2017-01-01T00:00:00Z"),pd.Timestamp("2021-01-01T00:00:00Z")),"confirmation":(pd.Timestamp("2021-01-01T00:00:00Z"),pd.Timestamp("2024-01-01T00:00:00Z")),"diagnostic":(pd.Timestamp("2024-01-01T00:00:00Z"),pd.Timestamp("2026-01-01T00:00:00Z"))}
    rows=[]
    for h in HORIZONS:
        for day in schedule:
            t=int(day.timestamp()*1000)+10*H1; dt=pd.to_datetime(t,unit="ms",utc=True)
            period=next((k for k,(lo,hi) in periods.items() if lo<=dt<hi),"excluded")
            r={"experiment_id":"R329","horizon_weeks":h,"signal_timestamp_utc":dt.isoformat(),"entry_timestamp_utc":pd.to_datetime(t+2*H1,unit="ms",utc=True).isoformat(),"exit_timestamp_utc":pd.to_datetime(t+2*H1+WEEK,unit="ms",utc=True).isoformat(),"period":period,"eligible":False,"reason":"","eligible_leg_count":0,"calendar_days_in_lookback":"","usd_net_ratio_final":"","gross_weight_final":0.0}
            if period=="excluded": r["reason"]="outside_registered_period"; rows.append(r); continue
            if t not in common_set: r["reason"]="signal_timestamp_not_common_to_all_pairs"; rows.append(r); continue
            if t not in snap_idx: r["reason"]="signal_bar_inactive_in_at_least_one_pair"; rows.append(r); continue
            j=snap_idx[t]
            if j<h or j<13: r["reason"]="insufficient_eligible_weekly_history"; rows.append(r); continue
            en=t+2*H1; ex=en+WEEK
            if en not in common_set: r["reason"]="entry_timestamp_not_common_to_all_pairs"; rows.append(r); continue
            if ex not in common_set: r["reason"]="scheduled_exit_timestamp_not_common_to_all_pairs"; rows.append(r); continue
            if not all(lookup[p].get(en,False) for p in PAIRS): r["reason"]="entry_bar_inactive_in_at_least_one_pair"; rows.append(r); continue
            if not all(lookup[p].get(ex,False) for p in PAIRS): r["reason"]="exit_bar_inactive_in_at_least_one_pair"; rows.append(r); continue
            # Pre-outcome inputs only, ending at the current signal close; no post-entry prices/returns are computed.
            logp=np.log(snap_prices); signal=logp[j]-logp[j-h]; weekly=np.diff(logp[j-13:j+1],axis=0); vols=np.std(weekly,axis=0,ddof=1)
            if not np.isfinite(signal).all() or not np.isfinite(vols).all() or (vols<=0).any(): r["reason"]="invalid_signal_or_trailing_volatility"; rows.append(r); continue
            w,meta=target_weights(signal,vols); legs=int(np.sum(np.abs(w)>1e-12))
            r["eligible_leg_count"]=legs; r["calendar_days_in_lookback"]=(pd.to_datetime(t,unit="ms",utc=True)-pd.to_datetime(snapshots[j-h],unit="ms",utc=True)).days; r["usd_net_ratio_final"]=round(meta["usd_net_ratio_final"],12); r["gross_weight_final"]=round(meta["gross_final"],12)
            if legs==0: r["reason"]="flat_after_usd_exposure_cap_or_zero_signal"; rows.append(r); continue
            r["eligible"]=True;r["reason"]="eligible_preoutcome_only";rows.append(r)
    df=pd.DataFrame(rows)
    # Compact, deterministic archive encoding; reason/period maps are documented in ELIGIBILITY_AUDIT_SCHEMA.md.
    reason_codes={"outside_registered_period":"X","signal_timestamp_not_common_to_all_pairs":"S_TS","signal_bar_inactive_in_at_least_one_pair":"S_INACTIVE","insufficient_eligible_weekly_history":"HIST","entry_timestamp_not_common_to_all_pairs":"E_TS","scheduled_exit_timestamp_not_common_to_all_pairs":"X_TS","entry_bar_inactive_in_at_least_one_pair":"E_INACTIVE","exit_bar_inactive_in_at_least_one_pair":"X_INACTIVE","invalid_signal_or_trailing_volatility":"FEATURE","flat_after_usd_exposure_cap_or_zero_signal":"FLAT","eligible_preoutcome_only":"OK"}
    period_codes={"discovery":"D","confirmation":"C","diagnostic":"G","excluded":"X"}
    compact_df=pd.DataFrame({"h":df.horizon_weeks.astype("int8"),"t":pd.to_datetime(df.signal_timestamp_utc,utc=True).astype("int64")//10**9,"en":pd.to_datetime(df.entry_timestamp_utc,utc=True).astype("int64")//10**9,"ex":pd.to_datetime(df.exit_timestamp_utc,utc=True).astype("int64")//10**9,"p":df.period.map(period_codes),"ok":df.eligible.astype("int8"),"why":df.reason.map(reason_codes),"n":df.eligible_leg_count.astype("int8"),"days":pd.to_numeric(df.calendar_days_in_lookback,errors="coerce").fillna(-1).astype("int16"),"usd":pd.to_numeric(df.usd_net_ratio_final,errors="coerce").fillna(-1).round(4),"gross":df.gross_weight_final.round(4)})
    if compact_df.why.isna().any() or compact_df.p.isna().any(): raise ValueError("unmapped eligibility archive code")
    with (out_dir/"eligibility_skip_audit.csv.gz").open("wb") as raw:
        with gzip.GzipFile(filename="",mode="wb",fileobj=raw,mtime=0,compresslevel=9) as gz: gz.write(compact_df.to_csv(index=False,lineterminator="\\n").encode())
    results=[]; all_pass=True
    for h in HORIZONS:
        z=df[(df.horizon_weeks==h)&df.period.isin(["discovery","confirmation","diagnostic"])]
        res={"horizon_weeks":h}
        for name in ("discovery","confirmation","diagnostic"):
            x=z[z.period==name]; res[name]={"eligible_leg_opportunities":int(x.eligible_leg_count.sum()),"eligible_rebalance_dates":int(x.eligible.sum()),"scheduled_dates_audited":int(len(x))}
        gates={"discovery_legs_ge_200":res["discovery"]["eligible_leg_opportunities"]>=200,"discovery_dates_ge_100":res["discovery"]["eligible_rebalance_dates"]>=100,"confirmation_legs_ge_100":res["confirmation"]["eligible_leg_opportunities"]>=100,"confirmation_dates_ge_70":res["confirmation"]["eligible_rebalance_dates"]>=70}
        res["sample_gates"]=gates;res["sample_gate_pass"]=all(gates.values());all_pass &= res["sample_gate_pass"];results.append(res)
    summary={"experiment_id":"R329","verdict":"PREFLIGHT_PASS" if all_pass else "GAGAL","first_failed_gate":None if all_pass else "sample_gate","outcomes_computed":False,"pnl_computed":False,"data_gate":"PASS","candidate_sample_gates_pass":bool(all_pass),"active_common_tuesday_10utc_snapshots":int(len(snapshots)),"horizons":results,"self_tests":tests,"source_data_manifest_sha256":manifest["combined_ordered_stream_manifest_sha256"],"interpretation":"Eligibility and historical features only. No realized returns, PnL, PF, drawdown or bootstrap were computed. Project-contaminated years are not independent OOS."}
    jwrite(out_dir/"preflight_summary.json",summary)
    (out_dir/"preflight_test_log.txt").write_text("\n".join(tests+["14 raw BID/ASK streams hash/row audit: PASS","exact BID/ASK timestamps and exact seven-pair timestamp intersection: PASS","invalid OHLC, duplicate rows, H1 alignment and negative spread checks: PASS","active Tuesday signal/entry/exit coverage audit: COMPLETE","candidate sample gates: "+("PASS" if all_pass else "FAIL"),"outcome/PnL calculation: NOT RUN by design","2026 data excluded; XAUUSD 2026 not opened"])+"\n",encoding="utf-8")
    return summary


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument("--data-dir",type=Path,required=True);p.add_argument("--package-dir",type=Path,default=Path(__file__).resolve().parent);p.add_argument("--out-dir",type=Path,default=None);a=p.parse_args()
    result=run(a.package_dir.resolve(),a.data_dir.resolve(),(a.out_dir or a.package_dir).resolve());print(json.dumps(result,sort_keys=True,indent=2));return 0 if result.get("candidate_sample_gates_pass",False) else 2

if __name__=="__main__": raise SystemExit(main())