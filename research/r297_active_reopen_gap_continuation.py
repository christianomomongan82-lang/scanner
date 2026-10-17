#!/usr/bin/env python3
"""R297: XAUUSD weekend-gap continuation using the first genuinely active reopening bar.

R296 used a static Sunday 00:00 UTC quote block and is invalid as alpha evidence.
This runner excludes 2026 strategy outcomes and implements the locked R297 rules.
Dependencies: numpy, pandas.
"""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
import pandas as pd

BID_SHA = "b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575"
ASK_SHA = "b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9"
COSTS = (0.00, 0.10, 0.30, 0.50)
N_BOOT, SEED, BLOCK = 10000, 297, 4

def profit_factor(values):
    a = np.asarray(values, dtype=float)
    gains, losses = float(a[a > 0].sum()), float(-a[a < 0].sum())
    return gains / losses if losses > 0 else (float("inf") if gains > 0 else 0.0)

def load_data(data_dir):
    bp, ap = data_dir / "xauusd_bid_M5_2016-2026.csv.gz", data_dir / "xauusd_ask_M5_2016-2026.csv.gz"
    bh, ah = hashlib.sha256(bp.read_bytes()).hexdigest(), hashlib.sha256(ap.read_bytes()).hexdigest()
    if bh != BID_SHA or ah != ASK_SHA:
        raise ValueError(f"Archive hash mismatch: BID={bh} ASK={ah}")
    bid, ask = pd.read_csv(bp, compression="gzip"), pd.read_csv(ap, compression="gzip")
    schema = ["timestamp", "open", "high", "low", "close"]
    for label, d in [("BID", bid), ("ASK", ask)]:
        if d.columns.tolist() != schema or d.timestamp.duplicated().any():
            raise ValueError(f"{label} schema/duplicate timestamp failure")
    if len(bid) != 947326 or len(ask) != 947326:
        raise ValueError("Manifest row count mismatch")
    if not np.array_equal(bid.timestamp.to_numpy(), ask.timestamp.to_numpy()):
        raise ValueError("BID and ASK timestamps differ")
    d = pd.DataFrame({"timestamp": bid.timestamp.to_numpy()})
    for side, raw in [("bid", bid), ("ask", ask)]:
        for c in ("open", "high", "low", "close"):
            d[f"{side}_{c}"] = raw[c].to_numpy()
    d["dt"] = pd.to_datetime(d.timestamp, unit="ms", utc=True)
    # Sequester the whole 2026 segment before any signal/outcome calculation.
    after = pd.to_datetime(bid.timestamp, unit="ms", utc=True) >= pd.Timestamp("2026-01-01", tz="UTC")
    d = d[d.dt < pd.Timestamp("2026-01-01", tz="UTC")].copy().reset_index(drop=True)
    for side in ("bid", "ask"):
        cols = [f"{side}_{c}" for c in ("open", "high", "low", "close")]
        d[f"{side}_valid"] = (
            d[cols].notna().all(axis=1) & (d[cols] > 0).all(axis=1)
            & (d[f"{side}_high"] >= d[[f"{side}_open", f"{side}_close", f"{side}_low"]].max(axis=1))
            & (d[f"{side}_low"] <= d[[f"{side}_open", f"{side}_close", f"{side}_high"]].min(axis=1))
        )
    d["spread_open"] = d.ask_open - d.bid_open
    d["spread_close"] = d.ask_close - d.bid_close
    d["quote_valid"] = d.bid_valid & d.ask_valid & (d.spread_open >= 0) & (d.spread_close >= 0)
    # Static rows can exist despite manifest's no-synthesis flag; they are not active reopening bars.
    d["active"] = (
        (d.bid_high > d.bid_low) | (d.bid_open != d.bid_close)
        | (d.ask_high > d.ask_low) | (d.ask_open != d.ask_close)
    )
    meta = {
        "bid_sha256": bh, "ask_sha256": ah, "bid_rows": len(bid), "ask_rows": len(ask),
        "exact_paired_timestamps": True, "rows_before_2026_cutoff": len(d),
        "active_rows_before_cutoff": int(d.active.sum()),
        "static_rows_before_cutoff": int((~d.active).sum()),
        "last_used_utc": d.dt.max().isoformat(),
        "rows_from_2026_excluded": int(after.sum())
    }
    return d, meta

def identify_events(d):
    times = d.timestamp.to_numpy(dtype=np.int64)
    active_pos = np.flatnonzero(d.active.to_numpy(dtype=bool))
    active_times = times[active_pos]
    day = d.dt.iloc[active_pos].dt.dayofweek.to_numpy(dtype=np.int8)
    gap_mins = np.diff(active_times) / 60000.0
    hits = np.where((day[1:] == 6) & (day[:-1] == 4) & (gap_mins >= 1080) & (gap_mins <= 3600))[0] + 1
    events, audit = [], []
    for k in hits:
        pi, ci = int(active_pos[k-1]), int(active_pos[k])
        prev, cur = d.iloc[pi], d.iloc[ci]
        reasons = []
        between = d.iloc[pi+1:ci]
        if len(between):
            static = (
                (between.bid_open == between.bid_high) & (between.bid_high == between.bid_low) & (between.bid_low == between.bid_close)
                & (between.ask_open == between.ask_high) & (between.ask_high == between.ask_low) & (between.ask_low == between.ask_close)
            )
            if not bool(static.all()):
                reasons.append("nonstatic_intermediate_row")
        if not bool(prev.quote_valid) or not bool(cur.quote_valid):
            reasons.append("invalid_friday_or_active_sunday_quote")
        gap = (float(cur.ask_open) + float(cur.bid_open))/2 - (float(prev.ask_close) + float(prev.bid_close))/2
        fs, ss = float(prev.ask_close-prev.bid_close), float(cur.ask_open-cur.bid_open)
        if not np.isfinite(gap) or not np.isfinite(fs) or not np.isfinite(ss):
            reasons.append("nonfinite_gap_or_spread")
        if fs < 0 or ss < 0:
            reasons.append("negative_spread")
        if not abs(gap) > 2*(fs+ss):
            reasons.append("gap_not_above_2x_combined_spread")
        start = int(cur.timestamp)
        entry_ts, exit_ts = start + 600000, start + 14400000
        ei, xi = int(np.searchsorted(times, entry_ts)), int(np.searchsorted(times, exit_ts))
        if ei >= len(d) or times[ei] != entry_ts:
            reasons.append("missing_T_plus_10_entry")
        if xi >= len(d) or times[xi] != exit_ts:
            reasons.append("missing_T_plus_4h_exit")
        if ei < len(d) and times[ei] == entry_ts and xi < len(d) and times[xi] == exit_ts:
            expected = np.arange(entry_ts, exit_ts, 300000, dtype=np.int64)
            if not np.array_equal(times[ei:xi], expected):
                reasons.append("missing_M5_timestamp_inside_hold")
            path = d.iloc[ei:xi]
            if not bool(path.active.all()):
                reasons.append("static_quote_inside_holding_path")
            if not bool(path.quote_valid.all()):
                reasons.append("invalid_quote_inside_holding_path")
            if not bool(d.iloc[xi].active):
                reasons.append("static_forced_exit_quote")
            if not bool(d.iloc[xi].quote_valid):
                reasons.append("invalid_forced_exit_quote")
        ok = not reasons
        e = {
            "event_timestamp_utc": cur["dt"].isoformat(), "friday_timestamp_utc": prev["dt"].isoformat(),
            "gap_minutes": float(gap_mins[k-1]), "gap_mid_usd_oz": float(gap), "gap_abs_usd_oz": abs(float(gap)),
            "friday_close_spread": fs, "sunday_active_open_spread": ss,
            "entry_timestamp_utc": pd.to_datetime(entry_ts, unit="ms", utc=True).isoformat(),
            "exit_timestamp_utc": pd.to_datetime(exit_ts, unit="ms", utc=True).isoformat(),
            "year": int(cur["dt"].year), "eligible": ok, "skip_reason": "|".join(reasons)
        }
        audit.append(e)
        if ok:
            events.append({**e, "event_idx": ci, "entry_idx": ei, "exit_idx": xi})
    return events, audit

def simulate(d, e):
    gap, distance = float(e["gap_mid_usd_oz"]), abs(float(e["gap_mid_usd_oz"]))
    side = 1 if gap > 0 else -1
    entry_row = d.iloc[e["entry_idx"]]
    entry = float(entry_row.ask_open if side == 1 else entry_row.bid_open)
    if not np.isfinite(entry) or entry <= 0 or distance <= 0:
        return None, "invalid_entry_or_gap_distance"
    stop = entry-distance if side == 1 else entry+distance
    target = entry+distance if side == 1 else entry-distance
    if stop <= 0 or target <= 0:
        return None, "invalid_stop_or_target"
    op, high, low = (("bid_open","bid_high","bid_low") if side == 1 else ("ask_open","ask_high","ask_low"))
    exit_price = exit_time = exit_reason = None
    for j in range(e["entry_idx"], e["exit_idx"]):
        bar = d.iloc[j]
        if not bool(bar.active) or not bool(bar.quote_valid):
            return None, "invalid_or_static_quote_inside_hold"
        o, h, l, ts = float(bar[op]), float(bar[high]), float(bar[low]), bar["dt"]
        if side == 1:
            if o <= stop: exit_price, exit_reason, exit_time = o, "STOP_GAP", ts; break
            if o >= target: exit_price, exit_reason, exit_time = o, "TARGET_GAP", ts; break
            if l <= stop: exit_price, exit_reason, exit_time = stop, "STOP", ts; break
            if h >= target: exit_price, exit_reason, exit_time = target, "TARGET", ts; break
        else:
            if o >= stop: exit_price, exit_reason, exit_time = o, "STOP_GAP", ts; break
            if o <= target: exit_price, exit_reason, exit_time = o, "TARGET_GAP", ts; break
            if h >= stop: exit_price, exit_reason, exit_time = stop, "STOP", ts; break
            if l <= target: exit_price, exit_reason, exit_time = target, "TARGET", ts; break
    if exit_price is None:
        ex = d.iloc[e["exit_idx"]]
        exit_price, exit_time, exit_reason = float(ex.bid_open if side == 1 else ex.ask_open), ex["dt"], "TIME"
    pnl = exit_price-entry if side == 1 else entry-exit_price
    r = {k:e[k] for k in ("event_timestamp_utc","friday_timestamp_utc","year","gap_minutes","gap_mid_usd_oz","gap_abs_usd_oz","friday_close_spread","sunday_active_open_spread","entry_timestamp_utc","exit_timestamp_utc")}
    r.update({
        "side":"LONG" if side == 1 else "SHORT", "entry_price_executable":entry, "stop_level":stop, "target_level":target,
        "exit_timestamp_actual_utc":exit_time.isoformat(), "exit_reason":exit_reason, "exit_price_executable":exit_price,
        "risk_distance_usd_oz":distance, "gross_usd_oz":float(pnl), "gross_R":float(pnl/distance),
        "hold_minutes":float((exit_time-entry_row["dt"]).total_seconds()/60)
    })
    for c in COSTS:
        r[f"net_usd_oz_{c:.2f}"] = float(pnl-c)
        r[f"net_R_{c:.2f}"] = float((pnl-c)/distance)
    return r, None

def summarize(df, cost):
    a = df[f"net_R_{cost:.2f}"].to_numpy(float) if len(df) else np.array([])
    if not len(a):
        return {"trades":0,"net_R":0.0,"PF_R":None,"win_rate_pct":None,"max_closed_R_drawdown":0.0}
    cum = np.r_[0,np.cumsum(a)]; dd = cum-np.maximum.accumulate(cum)
    return {
        "trades":int(len(df)),"net_R":float(a.sum()),"PF_R":float(profit_factor(a)),
        "mean_R":float(a.mean()),"median_R":float(np.median(a)),"win_rate_pct":float((a>0).mean()*100),
        "max_closed_R_drawdown":float(-min(0,float(dd.min()))),"longs":int((df.side=="LONG").sum()),
        "shorts":int((df.side=="SHORT").sum()),"stop_exits":int(df.exit_reason.isin(["STOP","STOP_GAP"]).sum()),
        "target_exits":int(df.exit_reason.isin(["TARGET","TARGET_GAP"]).sum()),"time_exits":int((df.exit_reason=="TIME").sum()),
        "mean_hold_minutes":float(df.hold_minutes.mean())
    }

def bootstrap(df):
    weeks={d.strftime("%Y-%m-%d"):0.0 for d in pd.date_range("2021-01-04","2025-12-29",freq="W-MON")}
    for _,row in df.iterrows():
        dt=pd.Timestamp(row.exit_timestamp_actual_utc); monday=(dt-pd.Timedelta(days=dt.weekday())).strftime("%Y-%m-%d")
        if monday in weeks: weeks[monday]+=float(row["net_R_0.30"])
    vals=np.array(list(weeks.values()),float); rng=np.random.default_rng(SEED); n=len(vals); means=np.empty(N_BOOT)
    for b in range(N_BOOT):
        ids=[]
        while len(ids)<n:
            s=int(rng.integers(0,n)); ids.extend(((s+np.arange(BLOCK))%n).tolist())
        means[b]=vals[np.asarray(ids[:n],int)].mean()
    q=np.quantile(means,[.025,.975])
    return {"weeks":n,"weeks_with_trades":int((vals!=0).sum()),"mean_weekly_net_R":float(vals.mean()),
            "ci95_low":float(q[0]),"ci95_high":float(q[1]),"resamples":N_BOOT,"block_weeks":BLOCK,"seed":SEED}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--data-dir",type=Path,required=True)
    ap.add_argument("--out-dir",type=Path,default=Path("R297_outputs"))
    args=ap.parse_args(); args.out_dir.mkdir(parents=True,exist_ok=True)
    d,meta=load_data(args.data_dir); events,audit=identify_events(d)
    pd.DataFrame(audit).to_csv(args.out_dir/"R297_event_quality_audit.csv",index=False)
    weekend_audit=d[d.dt.dt.dayofweek.isin([4,6])][["timestamp","dt","bid_open","bid_high","bid_low","bid_close","ask_open","ask_high","ask_low","ask_close","active","quote_valid"]].copy()
    weekend_audit.to_csv(args.out_dir/"R297_weekend_activity_audit.csv.gz",index=False,compression="gzip")
    trades=[]; skips=[]
    for e in events:
        tr,why=simulate(d,e)
        if tr is None: skips.append({"event_timestamp_utc":e["event_timestamp_utc"],"reason":why})
        else: trades.append(tr)
    t=pd.DataFrame(trades); t.to_csv(args.out_dir/"R297_trade_ledger.csv",index=False)
    pd.DataFrame(skips,columns=["event_timestamp_utc","reason"]).to_csv(args.out_dir/"R297_simulation_skips.csv",index=False)
    if t.empty: raise RuntimeError("No completed trades; candidate is data-ineligible")
    result={"candidate_id":"R297_XAUUSD_ACTIVE_REOPEN_GAP_CONTINUATION","input_provenance":meta,
            "weekend_active_gap_candidates_audited":len(audit),"eligible_events_after_locked_quality_and_friction":len(events),
            "completed_trades":len(t),"simulation_skips":len(skips),"strategy_pnl_2026_calculated":False,
            "discovery":{},"validation":{}}
    adf=pd.DataFrame(audit)
    for name,lo,hi,years in [("discovery","2016-01-01","2020-12-31",range(2016,2021)),("validation","2021-01-01","2025-12-31",range(2021,2026))]:
        sub=t[t.event_timestamp_utc.str[:10].between(lo,hi)].copy()
        result[name]={"by_cost":{f"{c:.2f}":summarize(sub,c) for c in COSTS},"yearly":{},
                      "events_audited":int(adf.event_timestamp_utc.str[:10].between(lo,hi).sum())}
        for y in years:
            yr=sub[sub.year==y]
            result[name]["yearly"][str(y)]={f"{c:.2f}":summarize(yr,c) for c in COSTS}
        if name=="validation": result[name]["bootstrap_cost_0.30"]=bootstrap(sub)
    d30=result["discovery"]["by_cost"]["0.30"]; v30=result["validation"]["by_cost"]["0.30"]
    d50=result["discovery"]["by_cost"]["0.50"]; v50=result["validation"]["by_cost"]["0.50"]; boot=result["validation"]["bootstrap_cost_0.30"]
    dpos=sum(result["discovery"]["yearly"][str(y)]["0.30"]["net_R"]>0 for y in range(2016,2021))
    vpos=sum(result["validation"]["yearly"][str(y)]["0.30"]["net_R"]>0 for y in range(2021,2026))
    gates={
        "discovery_min_75_trades":d30["trades"]>=75,"discovery_net_R_positive":d30["net_R"]>0,
        "discovery_PF_R_ge_1_05":d30["PF_R"] is not None and d30["PF_R"]>=1.05,
        "discovery_at_least_3_of_5_years_positive":dpos>=3,"discovery_cost_0.50_net_positive":d50["net_R"]>0,
        "discovery_cost_0.50_PF_ge_0.90":d50["PF_R"] is not None and d50["PF_R"]>=.90,
        "validation_min_100_trades":v30["trades"]>=100,"validation_net_R_positive":v30["net_R"]>0,
        "validation_PF_R_ge_1_05":v30["PF_R"] is not None and v30["PF_R"]>=1.05,
        "validation_at_least_3_of_5_years_positive":vpos>=3,"validation_bootstrap_CI_lower_gt_zero":boot["ci95_low"]>0,
        "validation_cost_0.50_net_positive":v50["net_R"]>0,"validation_cost_0.50_PF_ge_0.90":v50["PF_R"] is not None and v50["PF_R"]>=.90
    }
    result["year_positive_counts"]={"discovery":dpos,"validation":vpos}
    result["gates"]=gates; result["verdict"]="LULUS_HISTORICAL_SCREEN_ONLY" if all(gates.values()) else "GAGAL"
    result["limitations"]=[
        "R296 used static 00:00 UTC Sunday quotes and its PnL is invalid, not signal evidence.",
        "R297 uses the first active Sunday M5 bar and excludes static quotes inside the holding path.",
        "Observed BID/ASK quotes do not guarantee funded fills; added costs are modeled stresses.",
        "2021-2025 has prior XAU research exposure, not pristine program-level OOS.",
        "No 2026 strategy outcomes or FundedNext equity-aware challenge replay were run."
    ]
    (args.out_dir/"R297_results_compact.json").write_text(json.dumps(result,indent=2,allow_nan=False))
    lines=["# R297 — XAUUSD Active Weekend-Reopening Gap Continuation",f"\n**Verdict: {result['verdict']}**\n","No strategy PnL after 2025-12-31 was calculated.","",
      "| Metric | Discovery 2016–2020 | Validation 2021–2025 |","|---|---:|---:|"]
    for key,label in [("trades","Trades"),("net_R","Net R @ +$0.30/oz"),("PF_R","PF_R @ +$0.30/oz"),("win_rate_pct","Win rate %"),
                      ("max_closed_R_drawdown","Max closed R drawdown"),("stop_exits","Stop exits"),("target_exits","Target exits"),("time_exits","4h time exits")]:
        lines.append(f"| {label} | {d30.get(key)} | {v30.get(key)} |")
    lines += ["\n## Data-eligibility audit\n",f"- Active weekend-gap candidates audited: {len(audit)}.",
              f"- Events passing locked quality/friction/path gates: {len(events)}.",f"- Completed trades: {len(t)}; simulation skips: {len(skips)}.",
              "\n## Cost sensitivity at +$0.50/oz\n",f"- Discovery: {d50['trades']} trades, net {d50['net_R']:.3f}R, PF_R {d50['PF_R']:.3f}.",
              f"- Validation: {v50['trades']} trades, net {v50['net_R']:.3f}R, PF_R {v50['PF_R']:.3f}.",
              "\n## Annual cohorts at +$0.30/oz\n","| Year | Trades | Net R | PF_R |","|---|---:|---:|---:|"]
    for year in range(2016,2026):
        split="discovery" if year<=2020 else "validation"
        q=result[split]["yearly"][str(year)]["0.30"]
        lines.append(f"| {year} | {q['trades']} | {q['net_R']:.3f} | {q['PF_R'] if q['PF_R'] is not None else 'n/a'} |")
    lines += [f"\n## Validation weekly bootstrap @ +$0.30/oz\n\nMean {boot['mean_weekly_net_R']:.5f}R/week; 95% CI [{boot['ci95_low']:.5f}, {boot['ci95_high']:.5f}] across {boot['weeks']} Monday-start weeks, including zero-trade weeks (10,000 circular four-week blocks, seed 297).",
              "\n## Locked gates\n","| Gate | Result |","|---|---|"]
    for key,value in gates.items(): lines.append(f"| {key} | {'PASS' if value else 'FAIL'} |")
    lines += ["\n## Interpretation\n","R296 used a static Sunday quote block and is invalid as alpha evidence. R297 corrects the event to the first active reopening bar; it fails the locked discovery/validation requirements. No 2026 outcomes or funded challenge replay were run.",
              "\n## Limitations\n","- BID/ASK history does not guarantee live funded fills; added costs are modeled.",
              "- 2021–2025 has prior XAU research exposure, not pristine program-level OOS.",
              "- 2026 results were not calculated."]
    (args.out_dir/"R297_FINAL_REPORT.md").write_text("\n".join(lines)+"\n")
    print(json.dumps({"verdict":result["verdict"],"eligible_events":len(events),"closed_trades":len(t),"gates":gates,
                      "discovery":d30,"validation":v30,"bootstrap":boot},indent=2))
if __name__=="__main__":
    main()
