#!/usr/bin/env python3
"""R202: locked failed-breakout reversal at the prior 20-bar H4 channel edge.

Rule locked before reading forward results:
- long reversal when the signal H4 low pierces the prior 20-bar low but closes back above that low;
- short reversal when the signal H4 high pierces the prior 20-bar high but closes back below that high;
- reject ambiguous candles that pierce both channel edges; stop at the signal candle extreme; target 2R;
- manual execution at first non-flat M5 bar >=5 minutes after signal close and
  before the next actual H4 close; SL-first intrabar handling and gap-at-open;
- select the lowest-frequency instrument using 2017-2021 discovery only.
Only the selected instrument's forward 2022-2025 metrics are calculated/reported.
"""
from __future__ import annotations
import argparse, json, math, sys
from pathlib import Path
import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from research.r192_ger40 import (
    parse_data, build_h4, safe, PERIODS
)

CFG = {"id":"R202_FAILED_BREAKOUT_REVERSION_B20_RR2", "role":"locked_candidate",
       "lookback":20, "stop_rule":"signal_extreme"}
RR = 2.0
ASSETS = {
    "usa500idxusd":"USA 500 / S&P 500",
    "usatechidxusd":"USA 100 Tech / Nasdaq 100",
    "usa30idxusd":"USA 30 / Dow Jones",
    "ussc2000idxusd":"US Small Cap 2000",
    "deuidxeur":"Germany 40 / DAX",
    "gbridxgbp":"FTSE 100",
    "fraidxeur":"France 40 / CAC 40",
    "eusidxeur":"EU Stocks 50",
    "ausidxaud":"Australia 200",
    "jpnidxjpy":"Japan 200+",
}
D0, D1 = PERIODS["discovery"]
F0, F1 = PERIODS["forward"]
O0 = PERIODS["oos2026"][0]


def signals_and_stops(h4):
    hi=h4.high.to_numpy(float); lo=h4.low.to_numpy(float); cl=h4.close.to_numpy(float)
    n=len(h4); b=CFG["lookback"]
    sig=np.zeros(n,dtype=np.int8); stop=np.full(n,np.nan)
    for i in range(b,n):
        prior_high=float(np.max(hi[i-b:i])); prior_low=float(np.min(lo[i-b:i]))
        swept_low=bool(lo[i]<prior_low and cl[i]>prior_low)
        swept_high=bool(hi[i]>prior_high and cl[i]<prior_high)
        # Skip a candle that sweeps both sides; direction would be ambiguous.
        if swept_low and not (hi[i]>prior_high):
            sig[i]=1; stop[i]=float(lo[i])
        elif swept_high and not (lo[i]<prior_low):
            sig[i]=-1; stop[i]=float(hi[i])
    return sig, stop


def truncation_gate(h4, full_sig, full_stop):
    hi=h4.high.to_numpy(float); lo=h4.low.to_numpy(float); cl=h4.close.to_numpy(float)
    completed=h4.completed.to_numpy(bool); b=CFG["lookback"]; checked=0
    for i in np.flatnonzero(completed):
        checked+=1
        prefix_dir=0; st=np.nan
        if i>=b:
            prior_high=float(np.max(hi[i-b:i])); prior_low=float(np.min(lo[i-b:i]))
            swept_low=bool(lo[i]<prior_low and cl[i]>prior_low)
            swept_high=bool(hi[i]>prior_high and cl[i]<prior_high)
            if swept_low and not (hi[i]>prior_high):
                prefix_dir=1; st=float(lo[i])
            elif swept_high and not (lo[i]<prior_low):
                prefix_dir=-1; st=float(hi[i])
        if prefix_dir != int(full_sig[i]):
            return {"pass":False,"checked":checked,"bar":int(i),"reason":"failed-breakout direction mismatch"}
        if prefix_dir != 0 and not np.isclose(st,float(full_stop[i]),rtol=0,atol=1e-12):
            return {"pass":False,"checked":checked,"bar":int(i),"reason":"signal-extreme stop mismatch"}
    return {"pass":True,"checked":checked,"reason":"all completed-bar prefixes match"}


def simulate_rejection(h4,m5):
    sig,stops=signals_and_stops(h4)
    h4utc=h4.index.tz_convert("UTC"); completed=h4.completed.to_numpy(bool)
    mt=m5.index.tz_convert("UTC")
    op=m5.open.to_numpy(float); hi=m5.high.to_numpy(float); lo=m5.low.to_numpy(float)
    close=m5.close.to_numpy(float)
    flat=(op==hi)&(hi==lo)&(lo==close)
    trades=[]; skipped_active=0; skipped_no_fill=0; skipped_invalid=0; last_exit=None
    for i in range(len(h4)-1):
        if not completed[i] or int(sig[i]) == 0:
            continue
        signal_time=pd.Timestamp(h4["bar_close_utc"].iloc[i]).tz_convert("UTC")
        if last_exit is not None and (pd.isna(last_exit) or not (last_exit<signal_time)):
            skipped_active+=1
            continue
        direction=int(sig[i]); stop=float(stops[i])
        left=int(mt.searchsorted(signal_time+pd.Timedelta(minutes=5),side="left"))
        next_close=pd.Timestamp(h4["bar_close_utc"].iloc[i+1]).tz_convert("UTC")
        right=int(mt.searchsorted(next_close,side="left"))
        start_j=next((j for j in range(left,right) if not flat[j]),None)
        if start_j is None:
            skipped_no_fill+=1
            continue
        entry_time=mt[start_j]; entry=float(op[start_j])
        if start_j>=len(mt) or not math.isfinite(entry-stop):
            skipped_invalid+=1
            continue
        if direction==1 and entry<=stop:
            skipped_invalid+=1; continue
        if direction==-1 and entry>=stop:
            skipped_invalid+=1; continue
        risk=(entry-stop) if direction==1 else (stop-entry)
        target=entry+RR*risk if direction==1 else entry-RR*risk
        exit_time=None; exit_price=np.nan; reason="OPEN_AT_DATA_END"; flat_skipped=0
        for j in range(start_j,len(mt)):
            if flat[j]:
                flat_skipped+=1
                continue
            o=float(op[j]); hh=float(hi[j]); ll=float(lo[j])
            if direction==1:
                if ll<=stop or o<=stop:
                    exit_price=o if o<=stop else stop
                    reason="SL_GAP_OPEN" if o<=stop else "SL"
                    exit_time=mt[j]; break
                if hh>=target:
                    exit_price=target; reason="TP"; exit_time=mt[j]; break
            else:
                if hh>=stop or o>=stop:
                    exit_price=o if o>=stop else stop
                    reason="SL_GAP_OPEN" if o>=stop else "SL"
                    exit_time=mt[j]; break
                if ll<=target:
                    exit_price=target; reason="TP"; exit_time=mt[j]; break
        trades.append({
            "config":CFG["id"],"role":CFG["role"],"mode":"manual5m",
            "lookback":CFG["lookback"],"direction":"long" if direction==1 else "short","stop_rule":CFG["stop_rule"],
            "signal_bar_utc":h4utc[i].isoformat(),"signal_close_utc":signal_time.isoformat(),
            "entry_time_utc":entry_time.isoformat(),"entry":entry,"sl":stop,"tp":target,
            "exit_time_utc":None if exit_time is None else exit_time.isoformat(),
            "exit":None if exit_time is None else float(exit_price),"reason":reason,
            "entry_exact_m5_timestamp":True,"risk_points":risk,
            "flat_m5_bars_skipped_while_open":flat_skipped,
        })
        last_exit=pd.NaT if exit_time is None else exit_time
        if pd.isna(last_exit):
            break
    return trades, {"signals":int(((sig!=0)&completed).sum()),"taken":len(trades),
                    "skipped_active":skipped_active,"skipped_no_tradable_fill":skipped_no_fill,
                    "skipped_invalid_risk":skipped_invalid}


def trade_r_mixed(tr,bps):
    if tr["exit"] is None:
        return np.nan
    cost=float(tr["entry"])*bps/10000.0
    if tr["direction"]=="long":
        return (float(tr["exit"])-float(tr["entry"])-cost)/float(tr["risk_points"])
    return (float(tr["entry"])-float(tr["exit"])-cost)/float(tr["risk_points"])


def metric_mixed(trades,start,end,bps):
    picked=[t for t in trades if start <= pd.Timestamp(t["entry_time_utc"]) < end]
    closed=[t for t in picked if t["exit_time_utc"] is not None and pd.Timestamp(t["exit_time_utc"]) < end]
    vals=np.array([trade_r_mixed(t,bps) for t in closed],dtype=float)
    wins=float(vals[vals>0].sum()) if len(vals) else 0.0
    losses=float(-vals[vals<0].sum()) if len(vals) else 0.0
    pf=(wins/losses if losses>0 else (float("inf") if wins>0 else float("nan")))
    return {"entries":len(picked),"n":len(closed),"censored":len(picked)-len(closed),
            "pf":pf,"wins_r":wins,"losses_r":losses}


def metric_entry_cohort_mixed(trades,entry_start,entry_end,outcome_cutoff,bps):
    picked=[t for t in trades if entry_start <= pd.Timestamp(t["entry_time_utc"]) < entry_end]
    closed=[t for t in picked if t["exit_time_utc"] is not None and pd.Timestamp(t["exit_time_utc"]) < outcome_cutoff]
    vals=np.array([trade_r_mixed(t,bps) for t in closed],dtype=float)
    wins=float(vals[vals>0].sum()) if len(vals) else 0.0
    losses=float(-vals[vals<0].sum()) if len(vals) else 0.0
    pf=(wins/losses if losses>0 else (float("inf") if wins>0 else float("nan")))
    return {"entries":len(picked),"n":len(closed),"censored":len(picked)-len(closed),
            "pf":pf,"wins_r":wins,"losses_r":losses}


def cohort_pf(trades,year,bps):
    start=pd.Timestamp(f"{year}-01-01",tz="UTC")
    end=pd.Timestamp(f"{year+1}-01-01",tz="UTC")
    return metric_entry_cohort_mixed(trades,start,end,F1,bps)


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-dir",default="dl"); ap.add_argument("--out",default="results")
    args=ap.parse_args(); data_dir=Path(args.data_dir); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    assets_data={}; gate_report={}; source_meta={}; discovery_rows=[]; trades_by_inst={}
    observed_ends={}
    # Validate every instrument and run prefix/truncation tests before calculating PF.
    for inst,name in ASSETS.items():
        hp=data_dir/f"{inst}_h1.csv.gz"; mp=data_dir/f"{inst}_m5.csv.gz"
        if not hp.is_file() or not mp.is_file():
            raise SystemExit(f"HARD STOP: missing required source for {inst}")
        h1,d1=parse_data(hp); m5,d2=parse_data(mp)
        h4,diag=build_h4(h1,pd.Timestamp.now(tz="UTC"))
        sig,stops=signals_and_stops(h4)
        gate=truncation_gate(h4,sig,stops); gate_report[inst]=gate
        if not gate["pass"]:
            raise SystemExit(f"HARD STOP: truncation gate failed for {inst}: {gate}")
        assets_data[inst]=(h4,m5)
        observed_ends[inst]=m5.index[-1].tz_convert("UTC")+pd.Timedelta(minutes=5)
        source_meta[inst]={"name":name,"h1_rows":len(h1),"m5_rows":len(m5),
            "h1_duplicates_removed":d1,"m5_duplicates_removed":d2,
            "h1_start_utc":h1.index[0].tz_convert("UTC").isoformat(),
            "h1_end_utc":h1.index[-1].tz_convert("UTC").isoformat(),
            "m5_start_utc":m5.index[0].tz_convert("UTC").isoformat(),
            "m5_end_utc":m5.index[-1].tz_convert("UTC").isoformat(),**diag}
        print(f"TRUNCATION PASS {inst}: prefixes={gate['checked']}; H1={len(h1):,}; M5={len(m5):,}",flush=True)

    common_end=min(observed_ends.values())
    # Discovery selection: do not calculate/report forward metrics for unselected assets.
    for inst,name in ASSETS.items():
        h4,m5=assets_data[inst]
        trades,diag=simulate_rejection(h4,m5)
        trades_by_inst[inst]=trades
        d1m=metric_mixed(trades,D0,D1,1); d2m=metric_mixed(trades,D0,D1,2)
        discovery_rows.append({"instrument":inst,"instrument_name":name,
            "discovery_entries":d2m["entries"],"discovery_closed":d2m["n"],
            "discovery_censored":d2m["censored"],"discovery_pf_1bp":d1m["pf"],
            "discovery_pf_2bp":d2m["pf"],"signals":diag["signals"],"taken":diag["taken"],
            "skipped_active":diag["skipped_active"],"skipped_no_tradable_fill":diag["skipped_no_tradable_fill"],
            "skipped_invalid_risk":diag["skipped_invalid_risk"]})
    ledger=pd.DataFrame(discovery_rows)
    eligible=ledger[(ledger.discovery_closed>=10)&np.isfinite(pd.to_numeric(ledger.discovery_pf_2bp,errors="coerce"))&
                    (pd.to_numeric(ledger.discovery_pf_2bp,errors="coerce")>=1.0)].copy()
    eligible=eligible.sort_values(["discovery_closed","discovery_pf_2bp","instrument"],
                                  ascending=[True,False,True],kind="stable")
    selected_result=None; selected_trades=[]; cohort_rows=[]
    if not eligible.empty:
        pick=eligible.iloc[0].to_dict(); inst=pick["instrument"]
        selected_trades=trades_by_inst[inst]
        f1=metric_mixed(selected_trades,F0,F1,1); f2=metric_mixed(selected_trades,F0,F1,2)
        year_pfs=[]
        for year in range(2022,2026):
            cm=cohort_pf(selected_trades,year,1)
            if cm["n"]>=5 and isinstance(cm["pf"],(int,float)) and math.isfinite(float(cm["pf"])):
                year_pfs.append(float(cm["pf"]))
            for bps in (1,2):
                row=cohort_pf(selected_trades,year,bps)
                cohort_rows.append({"instrument":inst,"entry_year":year,"cost_bps_rt":bps,
                    "entries":row["entries"],"closed_by_2026":row["n"],"censored_by_2026":row["censored"],
                    "pf_entry_cohort":row["pf"]})
        worst=min(year_pfs) if year_pfs else None
        suspicious=isinstance(f1["pf"],(int,float)) and math.isfinite(float(f1["pf"])) and float(f1["pf"])>1.4
        normal_pass=(f1["n"]>=30 and isinstance(f1["pf"],(int,float)) and math.isfinite(float(f1["pf"])) and f1["pf"]>=1.15
            and isinstance(f2["pf"],(int,float)) and math.isfinite(float(f2["pf"])) and f2["pf"]>=1.15 and (worst is None or worst>=1.0))
        verdict="HOLD_EXTRA_AUDIT" if normal_pass and suspicious else "PASS" if normal_pass else "REJECT"
        o1=metric_mixed(selected_trades,O0,common_end,1); o2=metric_mixed(selected_trades,O0,common_end,2)
        selected_result={"instrument":inst,"instrument_name":pick["instrument_name"],
            "selection_basis":"fewest closed discovery trades 2017-2021 among assets with >=10 closes and discovery PF@2bp >=1.00",
            "discovery_closed":int(pick["discovery_closed"]),"discovery_pf_1bp":safe(pick["discovery_pf_1bp"]),
            "discovery_pf_2bp":safe(pick["discovery_pf_2bp"]),
            "forward_2022_2025_closed":f1["n"],"forward_2022_2025_censored":f1["censored"],
            "forward_pf_1bp":safe(f1["pf"]),"forward_pf_2bp":safe(f2["pf"]),
            "forward_worst_entry_year_pf_1bp_n5plus":worst,
            "oos_2026_to_common_cutoff_closed":o1["n"],"oos_2026_pf_1bp":safe(o1["pf"]),
            "oos_2026_pf_2bp":safe(o2["pf"]),"forward_verdict":verdict,
            "signals":int(pick["signals"]),"taken":int(pick["taken"])}
    else:
        selected_result={"forward_verdict":"NO_DISCOVERY_ELIGIBLE_CANDIDATE",
            "note":"No instrument reached >=10 closed discovery trades and PF@2bp >=1.00; forward holdout was not evaluated."}

    meta={"research":"R202 failed-breakout rejection reversal across ten equity indices",
        "run_utc":pd.Timestamp.now(tz="UTC").isoformat(),"cfg":CFG,
        "locked_rule":{"direction":"long on failed downside break; short on failed upside break","signal":"signal H4 wicks through one prior 20-bar channel edge but closes back inside the old channel; skip two-sided sweeps",
            "stop":"signal candle low for long, signal candle high for short","target":"2R",
            "entry":"first non-flat M5 BID bar >= signal close +5 minutes and before next actual H4 close",
            "exit":"M5 BID OHLC; SL checked before TP; gap through stop fills at open; no time stop",
            "cost_model":"modeled 1bp and 2bp round-trip price costs; not measured broker fees/spreads/slippage"},
        "periods":{"discovery":"entries 2017-2021, outcomes closed before 2022-01-01",
            "forward":"selected instrument only; entries 2022-2025, outcomes closed before 2026-01-01",
            "oos":"selected instrument only; entries 2026 through common data cutoff"},
        "common_oos_cutoff_utc":common_end.isoformat(),"assets":source_meta,"truncation_gates":gate_report,
        "discovery_ledger":discovery_rows,"selected_candidate_forward_result":selected_result,
        "guardrails":["All ten assets must pass data and causal truncation checks before PF is calculated.",
            "Instrument selection uses discovery closed trade count and discovery PF only.",
            "Forward metrics are computed/reported only for the locked selection. If it fails, do not replace it using other assets' forward outcomes.",
            "Only one failed-breakout reversal hypothesis is tested in this round; do not treat a reject as license for parameter fishing.",
            "This is research evidence, not proof of live profitability."]}
    (out/"meta.json").write_text(json.dumps(meta,indent=2,default=safe),encoding="utf-8")
    ledger.sort_values(["discovery_closed","instrument"],kind="stable").to_csv(out/"discovery_ledger.csv",index=False)
    pd.DataFrame(selected_trades).to_csv(out/"selected_trades.csv",index=False)
    pd.DataFrame(cohort_rows).to_csv(out/"selected_forward_entry_cohorts.csv",index=False)
    print("\nR202 DISCOVERY RANKING — no forward metrics shown for non-selected assets:",flush=True)
    print(ledger.sort_values(["discovery_closed","instrument"],kind="stable").to_string(index=False),flush=True)
    print("\nLOCKED SELECTION + SINGLE FORWARD VERDICT:",flush=True)
    print(json.dumps(selected_result,indent=2,default=safe),flush=True)
    print(f"Common OOS cutoff UTC: {common_end.isoformat()}",flush=True)
    print(f"Artifacts written to {out.resolve()}",flush=True)

if __name__=="__main__":
    main()
