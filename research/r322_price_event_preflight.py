#!/usr/bin/env python3
"""R322 pre-outcome price/calendar eligibility gate. It does not calculate trade PnL."""
from __future__ import annotations
import argparse, csv, hashlib, importlib.util, json, sys
from collections import Counter
from datetime import date, datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

EXPECTED_PRICE_ZIP_SHA = "b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e"
EXPECTED_R321_RUNNER_SHA256 = "8647e7e8d6cedf011c8b36d7dbd773e4c35650d91cd13d196fff6fdcc207d41c"
EXPECTED_EPISODE_SHA256 = "5e746bd3d8afccbc6ffb511b4a05d858ef06a17242e0a804a0cc168cec254b81"
FREQ = 300_000
PIP = 10_000.0
CUTOFF = pd.Timestamp("2026-01-01T00:00:00Z")

def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024*1024), b""):
            h.update(block)
    return h.hexdigest()

def period_for(ts: pd.Timestamp) -> str:
    d=ts.date()
    if date(2016,1,1) <= d < date(2019,1,1): return "discovery_2016_2018"
    if date(2019,1,1) <= d < date(2021,1,1): return "confirmation_2019_2020"
    if date(2021,1,1) <= d < date(2025,4,8): return "diagnostic_2021_2025-04-07"
    return "outside_locked_period"

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--price-zip",required=True,type=Path)
    ap.add_argument("--r321-runner",required=True,type=Path)
    ap.add_argument("--episodes-csv",required=True,type=Path)
    ap.add_argument("--output-dir",required=True,type=Path)
    args=ap.parse_args()
    for path in (args.price_zip,args.r321_runner,args.episodes_csv):
        if not path.is_file(): raise SystemExit(f"FAIL_CLOSED missing input: {path}")
    price_hash=sha_file(args.price_zip)
    runner_hash=sha_file(args.r321_runner)
    episode_hash=sha_file(args.episodes_csv)
    if price_hash != EXPECTED_PRICE_ZIP_SHA:
        raise SystemExit(f"FAIL_CLOSED price archive hash mismatch: {price_hash}")
    if runner_hash != EXPECTED_R321_RUNNER_SHA256:
        raise SystemExit(f"FAIL_CLOSED R321 cleaner hash mismatch: {runner_hash}")
    if episode_hash != EXPECTED_EPISODE_SHA256:
        raise SystemExit(f"FAIL_CLOSED corrected calendar episode hash mismatch: {episode_hash}")

    spec=importlib.util.spec_from_file_location("r321_locked_source_cleaner",args.r321_runner)
    if spec is None or spec.loader is None: raise SystemExit("FAIL_CLOSED cannot load registered R321 data cleaner")
    module=importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
    module.SOURCE=args.price_zip
    _,bars,mid,data_audit=module.read_source()
    ts=bars.index.to_numpy(dtype=np.int64)
    bclose=bars["bid_close"].to_numpy(float)
    bopen=bars["bid_open"].to_numpy(float)
    blow=bars["bid_low"].to_numpy(float)
    aopen=bars["ask_open"].to_numpy(float)
    ahigh=bars["ask_high"].to_numpy(float)
    mopen=mid["open"].to_numpy(float)
    mclose=mid["close"].to_numpy(float)
    rowmap={int(t):i for i,t in enumerate(ts)}
    eps=pd.read_csv(args.episodes_csv,keep_default_na=False)
    records=[]
    counts=Counter()
    for ep in eps.to_dict("records"):
        raw=ep["episode_time_utc"]
        et=pd.Timestamp(raw)
        if et.tzinfo is None:
            records.append({**ep,"period":"","status":"EXCLUDED","reason":"NAIVE_EPISODE_TIMESTAMP",
                            "impulse_pips":"","baseline_median_abs_pips":"","trigger_ratio":"",
                            "entry_bid_open":"","entry_ask_open":"","initial_risk_pips":""})
            counts["NAIVE_EPISODE_TIMESTAMP"]+=1; continue
        et=et.tz_convert("UTC")
        period=period_for(et)
        if et >= CUTOFF or period=="outside_locked_period":
            reason="OUTSIDE_LOCKED_PERIOD"
        elif et.value//1_000_000 % FREQ != 0:
            reason="EVENT_NOT_ON_EXACT_M5_GRID"
        else:
            reason=""
        k=rowmap.get(int(et.value//1_000_000))
        impulse=baseline=ratio=risk=entry_bid=entry_ask=""
        if not reason and k is None: reason="NO_EXACT_EVENT_M5_BAR"
        if not reason and k < 61: reason="INSUFFICIENT_60_CHANGE_BASELINE"
        if not reason and (not np.all(np.diff(ts[k-61:k+1])==FREQ)):
            reason="GAP_IN_PRE_EVENT_60_CHANGE_BASELINE"
        if not reason and (k==0 or int(ts[k-1]) != int(ts[k])-FREQ):
            reason="MISSING_PRE_EVENT_M5_BAR"
        if not reason:
            baseline_changes=np.abs(np.diff(mclose[k-61:k]))*PIP
            baseline=float(np.median(baseline_changes))
            impulse=float((mclose[k]-mclose[k-1])*PIP)
            ratio=abs(impulse)/baseline if baseline>0 else np.nan
            if not np.isfinite(baseline) or baseline<=0 or not np.isfinite(ratio):
                reason="INVALID_PRE_EVENT_BASELINE"
            elif abs(impulse) < 1.5*baseline:
                reason="NO_REGISTERED_1P5X_IMPULSE"
        direction=1 if isinstance(impulse,float) and impulse>0 else (-1 if isinstance(impulse,float) and impulse<0 else 0)
        entry_i=k+2 if (not reason and k is not None) else None
        if not reason and (entry_i is None or entry_i>=len(ts) or int(ts[entry_i])!=int(ts[k])+2*FREQ):
            reason="MISSING_EXACT_T_PLUS_10_ENTRY_BAR"
        if not reason:
            continued=(mopen[entry_i]>=mclose[k]) if direction==1 else (mopen[entry_i]<=mclose[k])
            if not continued: reason="NO_CONTINUATION_AT_MANUAL_DELAY"
        if not reason:
            entry_bid=float(bopen[entry_i]); entry_ask=float(aopen[entry_i])
            risk=float((entry_ask-blow[k])*PIP) if direction==1 else float((ahigh[k]-entry_bid)*PIP)
            if not np.isfinite(risk) or risk<=0: reason="NONPOSITIVE_OR_INVALID_INITIAL_RISK"
        # Check only exact timestamp/path availability through T+40. Do not inspect barrier hits or exits here.
        if not reason:
            required=np.arange(int(ts[k])+2*FREQ,int(ts[k])+9*FREQ,FREQ,dtype=np.int64)
            actual=ts[entry_i:entry_i+7]
            if len(actual)!=7 or not np.array_equal(actual,required):
                reason="MISSING_REQUIRED_POST_ENTRY_PRICE_PATH"
        if not reason:
            status="ELIGIBLE_SETUP_NO_OUTCOME_COMPUTED"
        else:
            status="EXCLUDED"
        counts[f"{period}:{status if not reason else reason}"]+=1
        record={**ep,"event_time_utc":et.isoformat().replace("+00:00","Z"),"period":period,
                "status":status,"reason":reason,"direction":"LONG" if direction==1 else ("SHORT" if direction==-1 else ""),
                "impulse_pips":impulse,"baseline_median_abs_pips":baseline,"trigger_ratio":ratio,
                "entry_time_utc":pd.to_datetime(int(ts[entry_i]),unit="ms",utc=True).isoformat() if entry_i is not None and entry_i<len(ts) else "",
                "entry_bid_open":entry_bid,"entry_ask_open":entry_ask,"initial_risk_pips":risk,
                "barrier_or_exit_outcome_read":False,"pnl_computed":False}
        records.append(record)
    args.output_dir.mkdir(parents=True,exist_ok=True)
    out=args.output_dir/"R322_PRICE_EVENT_ELIGIBILITY_PREFLIGHT.csv"
    fields=[]
    for row in records:
        for key in row:
            if key not in fields: fields.append(key)
    with out.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields,lineterminator="\n");w.writeheader();w.writerows(records)
    eligible=Counter(r["period"] for r in records if r.get("status")=="ELIGIBLE_SETUP_NO_OUTCOME_COMPUTED")
    source_rows=int(data_audit["source_paired_m1_rows"])
    result={
      "purpose":"pre-outcome exact time/path/sample eligibility only; never inspected stop/target hits or calculated PnL",
      "price_source_zip_sha256":price_hash,"R321_data_cleaner_sha256":runner_hash,
      "corrected_calendar_episode_csv_sha256":episode_hash,
      "raw_paired_m1_rows":source_rows,"clean_paired_m1_rows":data_audit["clean_paired_m1_rows"],
      "complete_m5_bars":data_audit["complete_m5_bars"],"m5_gaps_over_5m":data_audit["m5_gaps_over_5m"],
      "episode_rows_audited":len(records),"eligible_setup_counts_by_period":dict(eligible),
      "decision_counts":dict(counts),
      "pre-outcome_sample_floor":{"discovery_minimum":200,"confirmation_minimum":100,
           "discovery_eligible_setups":eligible["discovery_2016_2018"],
           "confirmation_eligible_setups":eligible["confirmation_2019_2020"],
           "can_reach_trade_count_floor":eligible["discovery_2016_2018"]>=200 and eligible["confirmation_2019_2020"]>=100},
      "results_csv":{"name":out.name,"bytes":out.stat().st_size,"sha256":sha_file(out)},
      "pnl_computed":False,
      "note":"Passing this setup-count floor only allows an outcome run; it is not a trading pass and does not establish completed-trade count."
    }
    (args.output_dir/"R322_PRICE_EVENT_ELIGIBILITY_PREFLIGHT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
