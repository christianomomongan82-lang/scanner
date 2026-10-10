#!/usr/bin/env python3
"""R192 GER40 generalisation test. Rules locked before any PF is printed."""
from __future__ import annotations
import argparse, json, math
from pathlib import Path
import numpy as np
import pandas as pd

NY = "America/New_York"
RR = 2.0
# Eight pre-registered hypotheses: fixed R191 rule plus six coordinate neighbours
# and one joint downside corner. Neighbours are diagnostic only, never selected
# as replacements based on forward PF.
CONFIGS = [
    {"id":"H0_BASE_R191", "breakout":55, "stop_bars":27, "role":"locked_candidate"},
    {"id":"H1_B50_S27", "breakout":50, "stop_bars":27, "role":"neighbour"},
    {"id":"H2_B60_S27", "breakout":60, "stop_bars":27, "role":"neighbour"},
    {"id":"H3_B45_S27", "breakout":45, "stop_bars":27, "role":"neighbour"},
    {"id":"H4_B65_S27", "breakout":65, "stop_bars":27, "role":"neighbour"},
    {"id":"H5_B55_S22", "breakout":55, "stop_bars":22, "role":"neighbour"},
    {"id":"H6_B55_S32", "breakout":55, "stop_bars":32, "role":"neighbour"},
    {"id":"H7_B50_S22", "breakout":50, "stop_bars":22, "role":"joint_neighbour"},
]
PERIODS = {
    "discovery": (pd.Timestamp("2017-01-01", tz="UTC"), pd.Timestamp("2022-01-01", tz="UTC")),
    "forward": (pd.Timestamp("2022-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")),
    "oos2026": (pd.Timestamp("2026-01-01", tz="UTC"), None),
}

def parse_data(path: Path):
    raw = pd.read_csv(path)
    raw.columns = [str(c).replace("\ufeff","").strip().lower() for c in raw.columns]
    tcol = next((c for c in ("timestamp","time","t","date","datetime") if c in raw.columns), None)
    if tcol is None:
        raise ValueError("Timestamp column not found; columns=" + repr(raw.columns.tolist()))
    ts = raw.pop(tcol)
    num = pd.to_numeric(ts, errors="coerce")
    if num.notna().mean() > 0.95:
        med = float(num.abs().median())
        if med >= 1e11: idx = pd.to_datetime(num, unit="ms", utc=True, errors="coerce")
        elif med >= 1e8: idx = pd.to_datetime(num, unit="s", utc=True, errors="coerce")
        else: raise ValueError(f"Numeric timestamp scale unknown: {med}")
    else:
        idx = pd.to_datetime(ts, utc=True, errors="coerce")
    if pd.isna(idx).any():
        raise ValueError("Invalid timestamps found; aborting.")
    need = ["open","high","low","close"]
    missing = set(need) - set(raw.columns)
    if missing: raise ValueError(f"OHLC columns missing: {sorted(missing)}")
    df = raw[need].copy()
    for c in need:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    if df[need].isna().any().any() or not np.isfinite(df[need].to_numpy(dtype=float)).all():
        raise ValueError("Missing/non-finite OHLC; aborting rather than silently filling.")
    df.index = pd.DatetimeIndex(idx).tz_convert(NY)
    df.index.name = "timestamp_ny"
    df = df.sort_index()
    duplicates = int(df.index.duplicated(keep="last").sum())
    if duplicates: df = df.loc[~df.index.duplicated(keep="last")]
    if len(df) < 1000: raise ValueError(f"Insufficient source bars: {len(df)}")
    return df, duplicates

def build_h4(h1, now_utc):
    rule = "4h"
    agg = h1.resample(rule, offset="1h", label="left", closed="left").agg(
        {"open":"first","high":"max","low":"min","close":"last"})
    cnt = h1["open"].resample(rule, offset="1h", label="left", closed="left").size()
    h4 = agg.dropna(subset=["open","high","low","close"]).copy()
    cnt = cnt.reindex(h4.index).fillna(0).astype(int)
    flat_h1 = int(((h1.open == h1.high) & (h1.high == h1.low) & (h1.low == h1.close)).sum())
    flat_h4 = int(((h4.open == h4.high) & (h4.high == h4.low) & (h4.low == h4.close)).sum())
    # Match the live R191 scanner: NY-local resampling, offset=1h, left/left,
    # drop empty bins only. Keep flat/partial non-empty bars and report their counts.
    labels_utc = h4.index.tz_convert("UTC")
    completed = (labels_utc + pd.Timedelta(hours=4)) <= now_utc
    h4["source_h1_count"] = cnt
    h4["completed"] = np.asarray(completed, dtype=bool)
    h4["label_utc"] = labels_utc
    partial = int((cnt < 4).sum())
    return h4, {"source_h1_rows":len(h1), "h4_rows":len(h4), "flat_h1_rows":flat_h1,
                "flat_h4_rows":flat_h4, "partial_h4_rows_lt4_h1":partial,
                "h1_start_utc":h1.index[0].tz_convert("UTC").isoformat(),
                "h1_end_utc":h1.index[-1].tz_convert("UTC").isoformat(),
                "flat_policy":"retained, counted, never forward-filled",
                "resample":"America/New_York; 4h; offset=1h; label=left; closed=left"}

def signals_and_stops(h4, cfg):
    hi = h4.high.to_numpy(float); lo = h4.low.to_numpy(float); cl = h4.close.to_numpy(float)
    n = len(h4); b = cfg["breakout"]; s = cfg["stop_bars"]
    sig = np.zeros(n, dtype=bool); stop = np.full(n, np.nan)
    for i in range(n):
        if i >= b: sig[i] = bool(cl[i] > np.max(hi[i-b:i]))
        if i >= s-1: stop[i] = float(np.min(lo[i-s+1:i+1]))
    return sig, stop

def truncation_gate(h4, cfg, full_sig, full_stop):
    # At every completed H4 bar i, recompute the decision from the prefix ending
    # at i only. This independent scalar path must exactly match full-series output.
    hi=h4.high.to_numpy(float); lo=h4.low.to_numpy(float); cl=h4.close.to_numpy(float)
    completed=h4.completed.to_numpy(bool); b=cfg["breakout"]; s=cfg["stop_bars"]
    checked=0
    for i in np.flatnonzero(completed):
        checked += 1
        trunc_sig = bool(i >= b and cl[i] > np.max(hi[i-b:i]))
        if trunc_sig != bool(full_sig[i]):
            return {"pass":False,"checked":checked,"bar":int(i),"reason":"signal mismatch"}
        if i >= s-1:
            prefix_stop = float(np.min(lo[i-s+1:i+1]))
            if not np.isclose(prefix_stop, float(full_stop[i]), rtol=0, atol=1e-12):
                return {"pass":False,"checked":checked,"bar":int(i),"reason":"stop mismatch"}
    return {"pass":True,"checked":checked,"reason":"all completed-bar prefixes match"}

def simulate(h4, m5, cfg, mode):
    sig, stops = signals_and_stops(h4, cfg)
    h4utc = h4.index.tz_convert("UTC")
    completed = h4.completed.to_numpy(bool)
    mt = m5.index.tz_convert("UTC")
    op = m5.open.to_numpy(float); hi = m5.high.to_numpy(float); lo = m5.low.to_numpy(float)
    close = m5.close.to_numpy(float)
    flat = (op == hi) & (hi == lo) & (lo == close)
    trades=[]; skipped_active=0; skipped_no_fill=0; skipped_invalid_risk=0
    last_exit = None
    for i in range(len(h4)-1):
        if not completed[i] or not sig[i]: continue
        signal_time = h4utc[i] + pd.Timedelta(hours=4)
        # Strictly before the signal boundary: exit at the boundary itself is not known yet.
        if last_exit is not None and (pd.isna(last_exit) or not (last_exit < signal_time)):
            skipped_active += 1
            continue
        stop = float(stops[i])
        if mode == "ideal":
            entry_time = h4utc[i+1]
            entry = float(h4.open.iloc[i+1])
            start_j = int(mt.searchsorted(entry_time, side="left"))
            exact = bool(start_j < len(mt) and mt[start_j] == entry_time)
        else:
            # A manual alert is acted on five minutes after the H4 signal close.
            # Require a non-flat M5 bar within the following H4 window; no weekend
            # flat-bar fills and no stale signal carried into a later session.
            left = int(mt.searchsorted(signal_time + pd.Timedelta(minutes=5), side="left"))
            right = int(mt.searchsorted(signal_time + pd.Timedelta(hours=4), side="left"))
            start_j = next((j for j in range(left, right) if not flat[j]), None)
            if start_j is None:
                skipped_no_fill += 1
                continue
            entry_time = mt[start_j]; entry = float(op[start_j]); exact = True
        if start_j is None or start_j >= len(mt) or entry <= stop or not math.isfinite(entry-stop):
            skipped_invalid_risk += 1
            continue
        risk = entry - stop
        target = entry + RR*risk
        exit_time=None; exit_price=np.nan; reason="OPEN_AT_DATA_END"
        flat_skipped=0
        for j in range(start_j, len(mt)):
            # Dukascopy -fl emits synthetic unchanged-price bars during non-trading periods.
            # They are retained for R191-compatible H1/H4 signal construction, but cannot
            # trigger execution exits. The first subsequent non-flat bar captures any gap.
            if flat[j]:
                flat_skipped += 1
                continue
            o=float(op[j]); h=float(hi[j]); l=float(lo[j])
            # SL first if both levels occur in a bar; a gap through SL fills at open.
            if l <= stop or o <= stop:
                exit_price = o if o <= stop else stop
                reason = "SL_GAP_OPEN" if o <= stop else "SL"
                exit_time = mt[j]; break
            if h >= target:
                exit_price = target; reason="TP"; exit_time=mt[j]; break
        trades.append({"config":cfg["id"],"role":cfg["role"],"breakout":cfg["breakout"],
                       "stop_bars":cfg["stop_bars"],"mode":mode,"signal_bar_utc":h4utc[i].isoformat(),
                       "signal_close_utc":signal_time.isoformat(),"entry_time_utc":entry_time.isoformat(),
                       "entry":entry,"sl":stop,"tp":target,
                       "exit_time_utc":None if exit_time is None else exit_time.isoformat(),
                       "exit":None if exit_time is None else float(exit_price),"reason":reason,
                       "entry_exact_m5_timestamp":exact,"risk_points":risk,
                       "flat_m5_bars_skipped_while_open":flat_skipped})
        last_exit = pd.NaT if exit_time is None else exit_time
        if pd.isna(last_exit): break
    return trades, {"signals":int((sig & completed).sum()),"taken":len(trades),
                    "skipped_active":skipped_active,"skipped_no_tradable_fill":skipped_no_fill,
                    "skipped_invalid_risk":skipped_invalid_risk}

def to_ts(v):
    return pd.NaT if v is None or pd.isna(v) else pd.Timestamp(v)

def trade_r(tr, bps):
    if tr["exit"] is None: return np.nan
    cost = float(tr["entry"]) * bps / 10000.0   # modeled round-trip cost in price bps
    return (float(tr["exit"]) - float(tr["entry"]) - cost) / float(tr["risk_points"])

def metric(trades, start, end, bps):
    picked=[t for t in trades if start <= pd.Timestamp(t["entry_time_utc"]) < end]
    closed=[t for t in picked if t["exit_time_utc"] is not None and pd.Timestamp(t["exit_time_utc"]) < end]
    vals=np.array([trade_r(t,bps) for t in closed],dtype=float)
    wins=float(vals[vals>0].sum()) if len(vals) else 0.0
    losses=float(-vals[vals<0].sum()) if len(vals) else 0.0
    pf=(wins/losses if losses>0 else (float("inf") if wins>0 else float("nan")))
    return {"entries":len(picked),"n":len(closed),"censored":len(picked)-len(closed),
            "pf":pf,"wins_r":wins,"losses_r":losses}

def annual_rows(trades, cfg, mode, observed_end):
    rows=[]
    for year in range(2017,2027):
        start=pd.Timestamp(f"{year}-01-01",tz="UTC")
        end=pd.Timestamp(f"{year+1}-01-01",tz="UTC") if year<2026 else observed_end
        for bps in (1,2):
            m=metric(trades,start,end,bps)
            rows.append({"config":cfg["id"],"mode":mode,"year":year,"cost_bps_rt":bps,
                         "entries":m["entries"],"n_closed_within_year":m["n"],"censored":m["censored"],
                         "pf_closed_within_year":m["pf"],"wins_r":m["wins_r"],"losses_r":m["losses_r"]})
    return rows


def metric_entry_cohort(trades, entry_start, entry_end, outcome_cutoff, bps):
    # Attribute all completed trade outcomes to the year the trade was entered.
    # For discovery, outcomes are cut off at 2022-01-01; forward at 2026-01-01;
    # OOS outcomes at the last available bar. Do not censor a trade just because
    # it crossed a calendar-year boundary.
    picked=[t for t in trades if entry_start <= pd.Timestamp(t["entry_time_utc"]) < entry_end]
    closed=[t for t in picked if t["exit_time_utc"] is not None and pd.Timestamp(t["exit_time_utc"]) < outcome_cutoff]
    vals=np.array([trade_r(t,bps) for t in closed],dtype=float)
    wins=float(vals[vals>0].sum()) if len(vals) else 0.0
    losses=float(-vals[vals<0].sum()) if len(vals) else 0.0
    pf=(wins/losses if losses>0 else (float("inf") if wins>0 else float("nan")))
    return {"entries":len(picked),"n":len(closed),"censored":len(picked)-len(closed),
            "pf":pf,"wins_r":wins,"losses_r":losses}


def annual_cohort_rows(trades, cfg, mode, observed_end):
    rows=[]
    for year in range(2017,2027):
        start=pd.Timestamp(f"{year}-01-01",tz="UTC")
        entry_end=pd.Timestamp(f"{year+1}-01-01",tz="UTC") if year<2026 else observed_end
        if year <= 2021:
            cutoff=PERIODS["discovery"][1]
            period="discovery_outcome_cutoff_2022"
        elif year <= 2025:
            cutoff=PERIODS["forward"][1]
            period="forward_outcome_cutoff_2026"
        else:
            cutoff=observed_end
            period="oos_observed_end"
        for bps in (1,2):
            m=metric_entry_cohort(trades,start,entry_end,cutoff,bps)
            rows.append({"config":cfg["id"],"mode":mode,"entry_year":year,"cost_bps_rt":bps,
                         "outcome_cutoff":period,"entries":m["entries"],"n_closed_by_cutoff":m["n"],
                         "censored_by_cutoff":m["censored"],"pf_entry_cohort":m["pf"],
                         "wins_r":m["wins_r"],"losses_r":m["losses_r"]})
    return rows

def safe(x):
    if isinstance(x,(np.integer,)): return int(x)
    if isinstance(x,(np.floating,float)):
        if math.isnan(float(x)): return None
        if math.isinf(float(x)): return "INF" if x>0 else "-INF"
        return float(x)
    if pd.isna(x): return None
    return x

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--m5-csv",required=True); ap.add_argument("--h1-csv",required=True); ap.add_argument("--out",default="results")
    args=ap.parse_args(); out=Path(args.out); out.mkdir(parents=True,exist_ok=True)
    now=pd.Timestamp.now(tz="UTC")
    m5,dups_m5=parse_data(Path(args.m5_csv))
    h1,dups_h1=parse_data(Path(args.h1_csv))
    h4,datadiag=build_h4(h1,now)
    if len(h4)<100: raise RuntimeError("Too few H4 bars.")
    # Causality/truncation is a hard gate and runs before any PF calculations.
    gates={}
    for cfg in CONFIGS:
        sig,stops=signals_and_stops(h4,cfg)
        gates[cfg["id"]]=truncation_gate(h4,cfg,sig,stops)
    gate_ok=all(g["pass"] for g in gates.values())
    meta={"signal_data":"Dukascopy GER40/deuidxeur H1 BID (R191-compatible H4 source)",
          "entry_exit_data":"Dukascopy GER40/deuidxeur M5 BID","run_utc":now.isoformat(),
          "source_duplicates_removed":{"h1":dups_h1,"m5":dups_m5},
          "m5_source":{"rows":len(m5),"flat_rows":int(((m5.open==m5.high)&(m5.high==m5.low)&(m5.low==m5.close)).sum()),"start_utc":m5.index[0].tz_convert("UTC").isoformat(),"end_utc":m5.index[-1].tz_convert("UTC").isoformat()},
          **datadiag,"hypothesis_count":len(CONFIGS),
          "configs":CONFIGS,"truncation_gates":gates,
          "execution_assumptions":{"ideal":"next H4 bar open, R191 comparability only",
             "manual":"first non-flat M5 bar at or after signal close + 5 minutes, strictly within next 4 hours; otherwise skip",
             "exit":"M5 BID OHLC; SL checked before TP; gap through SL fills at open; no time-stop",
             "cost":"1bp and 2bp round-trip price cost, cost points = entry * bp / 10000",
             "flat_bars":"H1/H4 source flats retained and reported to match R191; synthetic flat M5 bars are skipped for both entry and exit; first subsequent non-flat bar is used for gap execution; no forward-fill",
             "discovery":"2017-2021 trades only if exit also occurs before 2022-01-01",
             "forward":"entry 2022-2025, counted only if exit occurs before 2026-01-01; cross-boundary trades censored",
             "oos":"entry 2026; outcomes observed up to the last available M5 bar"}}
    (out/"meta.json").write_text(json.dumps(meta,indent=2,default=safe),encoding="utf-8")
    if not gate_ok:
        print("HARD STOP: TRUNCATION GATE FAILED. No PF calculated or printed.")
        print(json.dumps(gates,indent=2))
        raise SystemExit(2)
    print("TRUNCATION GATE PASS for all 8 pre-registered hypotheses; checked every completed H4 prefix.",flush=True)
    ledger=[]; annual=[]; annual_cohort=[]; all_trades=[]
    d0,d1=PERIODS["discovery"]
    f0,f1=PERIODS["forward"]
    o0=PERIODS["oos2026"][0]
    observed_end=m5.index[-1].tz_convert("UTC")+pd.Timedelta(minutes=5)
    for cfg in CONFIGS:
        for mode in ("ideal","manual5m"):
            trades,diag=simulate(h4,m5,cfg,mode); all_trades.extend(trades)
            d1m=metric(trades,d0,d1,1); d2m=metric(trades,d0,d1,2)
            f1m=metric(trades,f0,f1,1); f2m=metric(trades,f0,f1,2)
            o1m=metric(trades,o0,observed_end,1); o2m=metric(trades,o0,observed_end,2)
            ann=annual_rows(trades,cfg,mode,observed_end); annual.extend(ann)
            cohort=annual_cohort_rows(trades,cfg,mode,observed_end); annual_cohort.extend(cohort)
            # Apply the worst-year gate to entry-year cohorts, including trades
            # closed in a later year but before the locked forward boundary.
            ann_forward=[r for r in cohort if 2022<=r["entry_year"]<=2025 and r["cost_bps_rt"]==1 and r["n_closed_by_cutoff"]>=5]
            worst=min([float(r["pf_entry_cohort"]) for r in ann_forward if isinstance(r["pf_entry_cohort"],(int,float))],default=float("nan"))
            # High PF is a hard hold/reject until an independent extra audit is performed.
            suspicious=(isinstance(f1m["pf"],(int,float)) and f1m["pf"]>1.4)
            base_metrics=(f1m["n"]>=30 and isinstance(f1m["pf"],(int,float)) and f1m["pf"]>=1.15
                          and (not ann_forward or worst>=1.0) and not suspicious)
            ledger.append({"config":cfg["id"],"role":cfg["role"],"mode":mode,
                "breakout":cfg["breakout"],"stop_bars":cfg["stop_bars"],
                "discovery_n":d1m["n"],"discovery_censored":d1m["censored"],
                "discovery_pf_1bp":d1m["pf"],"discovery_pf_2bp":d2m["pf"],
                "forward_entries":f1m["entries"],"forward_n":f1m["n"],"forward_censored":f1m["censored"],
                "forward_pf_1bp":f1m["pf"],"forward_pf_2bp":f2m["pf"],
                "forward_worst_year_pf_1bp_n5plus":worst if not math.isnan(worst) else None,
                "oos2026_entries":o1m["entries"],"oos2026_n":o1m["n"],
                "oos2026_pf_1bp":o1m["pf"],"oos2026_pf_2bp":o2m["pf"],
                "signals":diag["signals"],"taken":diag["taken"],"skipped_active":diag["skipped_active"],
                "skipped_no_tradable_fill":diag["skipped_no_tradable_fill"],
                "skipped_invalid_risk":diag["skipped_invalid_risk"],
                "pf_gt_1_4_extra_audit_required":suspicious,
                "metrics_pass_except_neighbourhood":base_metrics})
    # Neighborhood is evaluated only on discovery, never selected on forward PF.
    manual={r["config"]:r for r in ledger if r["mode"]=="manual5m"}
    base=manual["H0_BASE_R191"]
    coord=["H1_B50_S27","H2_B60_S27","H3_B45_S27","H4_B65_S27","H5_B55_S22","H6_B55_S32"]
    neighbor_passes=sum(1 for k in coord if isinstance(manual[k]["discovery_pf_2bp"],(int,float))
                        and manual[k]["discovery_n"]>=5 and manual[k]["discovery_pf_2bp"]>=1.0)
    corner=manual["H7_B50_S22"]
    corner_ok=(corner["discovery_n"]<5 or
               (isinstance(corner["discovery_pf_2bp"],(int,float)) and corner["discovery_pf_2bp"]>=1.0))
    discovery_ok=(base["discovery_n"]>=10 and isinstance(base["discovery_pf_2bp"],(int,float))
                  and base["discovery_pf_2bp"]>=1.0)
    neighbourhood_ok=discovery_ok and neighbor_passes>=4 and corner_ok
    for row in ledger:
        if row["mode"]!="manual5m": 
            row["verdict"]="REJECT"
            row["reason"]="ideal open is comparison only; manual5m is the execution gate"
        elif row["config"]=="H0_BASE_R191":
            row["neighbourhood_neighbor_passes_out_of_6"]=neighbor_passes
            row["neighbourhood_corner_ok"]=corner_ok
            row["neighbourhood_pass"]=neighbourhood_ok
            if row["metrics_pass_except_neighbourhood"] and neighbourhood_ok:
                row["verdict"]="PROMOTE"
                row["reason"]="all pre-locked statistical, cost, year, execution and discovery-neighborhood gates passed"
            else:
                row["verdict"]="REJECT"
                why=[]
                if row["forward_n"]<30: why.append("forward n < 30")
                if not isinstance(row["forward_pf_1bp"],(int,float)) or row["forward_pf_1bp"]<1.15: why.append("forward PF@1bp < 1.15/undefined")
                if row["forward_worst_year_pf_1bp_n5plus"] is not None and row["forward_worst_year_pf_1bp_n5plus"]<1.0: why.append("worst eligible entry-year cohort PF < 1.00")
                if row["pf_gt_1_4_extra_audit_required"]: why.append("PF > 1.4 requires independent causality audit")
                if not neighbourhood_ok: why.append(f"neighborhood gate failed (discovery PF@2bp passes={neighbor_passes}/6; base discovery n={base['discovery_n']}; corner_ok={corner_ok})")
                row["reason"]="; ".join(why) if why else "one or more locked gates failed"
        else:
            row["verdict"]="REJECT"
            row["reason"]="pre-registered neighborhood diagnostic only; cannot replace locked R191 base based on forward outcome"
    pd.DataFrame(ledger).to_csv(out/"ledger.csv",index=False)
    pd.DataFrame(annual).to_csv(out/"annual.csv",index=False)
    pd.DataFrame(annual_cohort).to_csv(out/"annual_cohort.csv",index=False)
    pd.DataFrame(all_trades).to_csv(out/"trades.csv",index=False)
    print("\nLEDGER (manual5m is primary; all 8 hypotheses were pre-registered):",flush=True)
    show=pd.DataFrame([r for r in ledger if r["mode"]=="manual5m"])
    cols=["config","breakout","stop_bars","discovery_n","discovery_pf_1bp","discovery_pf_2bp",
          "forward_n","forward_pf_1bp","forward_pf_2bp","forward_worst_year_pf_1bp_n5plus",
          "oos2026_n","oos2026_pf_1bp","verdict"]
    print(show[cols].to_string(index=False),flush=True)
    print("\nBASELINE MANUAL5M YEARLY BREAKDOWN (closed within calendar year; diagnostic only):",flush=True)
    baseann=pd.DataFrame([r for r in annual if r["config"]=="H0_BASE_R191" and r["mode"]=="manual5m"])
    print(baseann.to_string(index=False),flush=True)
    print("\nBASELINE MANUAL5M ENTRY-YEAR COHORTS (used for worst-year PASS gate):",flush=True)
    basecohort=pd.DataFrame([r for r in annual_cohort if r["config"]=="H0_BASE_R191" and r["mode"]=="manual5m"])
    print(basecohort.to_string(index=False),flush=True)
    print("\nH4 signals retain/report flat H1/H4 source bars for R191 compatibility; synthetic flat M5 bars are skipped for entry AND exit. The next tradable non-flat M5 bar captures post-closure gaps; no forward-fill.")
    print(f"Total hypotheses tried this round: {len(CONFIGS)}. Forward computed once per pre-locked config.")
    print(f"Artifacts written to {out.resolve()}")

if __name__=="__main__": main()
