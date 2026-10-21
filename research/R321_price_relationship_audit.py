#!/usr/bin/env python3
"""R321 causal price-relationship audit. No parameter search or account-pass simulation."""
from __future__ import annotations
import hashlib, io, json, math, zipfile, gzip
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.stats import spearmanr

EXPERIMENT = "R321"
SOURCE = Path("/mnt/data/eurusd_raw_source.zip")
OUT = Path("/mnt/data/r321_results")
EXPECTED_ZIP_SHA = "b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e"
CUTOFF = pd.Timestamp("2026-01-01T00:00:00Z")
ANCHOR_MS = int(pd.Timestamp("2016-01-01T00:00:00Z").timestamp() * 1000)
FREQ = 300_000
CADENCE = 65 * 60_000
WEEK_MS = 7 * 24 * 60 * 60_000
MONDAY_ANCHOR_MS = int(pd.Timestamp("1970-01-05T00:00:00Z").timestamp() * 1000)
HORIZONS = (5, 15, 30, 60)
COSTS = (0.0, 0.5, 1.0, 1.5)
FEATURES = (
    "F1_RET15", "F2_RET30", "F3_RET60", "F4_ACCEL15",
    "F5_EFFICIENCY60", "F6_AUTOCORR_STATE", "F7_VOL_CONDITIONED_RET15",
)
BOOT_REPS = 2000
BOOT_SEED = 3212026
ALPHA_PER_TEST = 0.05 / 28

def sha_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()

def sha_clean(df: pd.DataFrame) -> str:
    h = hashlib.sha256()
    h.update(np.asarray(df.index, dtype="<i8").tobytes())
    for c in df.columns:
        h.update(np.asarray(df[c].to_numpy(), dtype="<f8").tobytes())
    return h.hexdigest()

def save_csv_gzip(df: pd.DataFrame, path: Path) -> None:
    payload = df.to_csv(index=False, lineterminator="\n", float_format="%.10g").encode("utf-8")
    with path.open("wb") as f:
        with gzip.GzipFile(filename="", mode="wb", fileobj=f, mtime=0, compresslevel=6) as gz:
            gz.write(payload)

def read_source():
    if sha_file(SOURCE) != EXPECTED_ZIP_SHA:
        raise RuntimeError("Raw ZIP SHA-256 mismatch; no calculation permitted.")
    with zipfile.ZipFile(SOURCE) as z:
        bid = pd.read_csv(z.open("eurusd_bid_M1_2016-2025.csv.gz"), compression="gzip")
        ask = pd.read_csv(z.open("eurusd_ask_M1_2016-2025.csv.gz"), compression="gzip")
    for df in (bid, ask):
        df["timestamp"] = pd.to_numeric(df["timestamp"], errors="raise").astype("int64")
        df.set_index("timestamp", inplace=True)
        if not df.index.is_monotonic_increasing or df.index.has_duplicates:
            raise RuntimeError("Source timestamps unsorted or duplicated.")
        for c in ("open", "high", "low", "close"):
            df[c] = pd.to_numeric(df[c], errors="raise").astype("float64")
    if not bid.index.equals(ask.index):
        raise RuntimeError("BID/ASK timestamp sets differ; paired feed gate failed.")
    cutoff_ms = int(CUTOFF.timestamp() * 1000)
    # The pinned archive is manifest-scoped to end-exclusive 2026-01-01; assert rather than copy-filter it.
    if int(bid.index.max()) >= cutoff_ms or int(ask.index.max()) >= cutoff_ms:
        raise RuntimeError("Source archive contains rows at/after protected cutoff.")
    if not bid.index.equals(ask.index):
        raise RuntimeError("BID/ASK pairing changed after cutoff.")
    names = [f"{s}_{c}" for s in ("bid", "ask") for c in ("open", "high", "low", "close")]
    source_paired_rows = int(len(bid))
    paired = pd.concat([bid.add_prefix("bid_"), ask.add_prefix("ask_")], axis=1)
    paired = paired[names]
    ts = paired.index.to_numpy(dtype=np.int64)
    values = [paired[c].to_numpy(dtype=np.float64) for c in names]
    # Remove a current paired placeholder only when each side’s current OHLC all carry forward
    # the preceding row close: BID O/H/L/C == prior BID close and likewise for ASK.
    repeated = np.zeros(len(paired), dtype=bool)
    for side in ("bid", "ask"):
        prior_close = paired[f"{side}_close"].to_numpy(dtype=np.float64)[:-1]
        for col in ("open", "high", "low", "close"):
            current = paired[f"{side}_{col}"].to_numpy(dtype=np.float64)[1:]
            repeated[1:] |= False
            if col == "open":
                side_match = current == prior_close
            else:
                side_match &= current == prior_close
        if side == "bid":
            repeated[1:] = side_match
        else:
            repeated[1:] &= side_match
    repeated[0] = False
    removed = int(repeated.sum())
    keep = ~repeated
    array_map = dict(zip(names, values))
    # Validate only rows that survive the registered joint placeholder filter.
    invalid = 0
    for side in ("bid", "ask"):
        o, h, l, close_arr = (array_map[f"{side}_{x}"] for x in ("open","high","low","close"))
        bad = (~np.isfinite(o) | ~np.isfinite(h) | ~np.isfinite(l) | ~np.isfinite(close_arr) |
               (h < np.maximum(o,close_arr)) | (l > np.minimum(o,close_arr)) | (h < l))
        invalid += int(np.sum(keep & bad))
    if invalid:
        raise RuntimeError(f"Invalid retained OHLC rows: {invalid}")
    bad_spread = keep & ((array_map["ask_open"] < array_map["bid_open"]) |
                         (array_map["ask_close"] < array_map["bid_close"]))
    if bool(bad_spread.any()):
        raise RuntimeError(f"ASK below BID at open/close on {int(bad_spread.sum())} retained rows.")
    # Hash cleaned rows as canonical little-endian arrays without materializing another 3.7M-row frame.
    clean_ts = ts[keep]
    clean_hash_obj = hashlib.sha256()
    clean_hash_obj.update(np.asarray(clean_ts, dtype="<i8").tobytes())
    for name in names:
        clean_hash_obj.update(np.asarray(array_map[name][keep], dtype="<f8").tobytes())
    clean_hash = clean_hash_obj.hexdigest()
    # Fast exact five-minute aggregation: each bucket has exactly five possible UTC minute starts.
    if np.any(clean_ts % 60_000 != 0):
        raise RuntimeError("Source timestamps are not UTC-minute aligned.")
    buckets = (clean_ts // FREQ) * FREQ
    bucket_ts, starts, counts = np.unique(buckets, return_index=True, return_counts=True)
    good = counts == 5
    bar_ts = bucket_ts[good]
    bars = pd.DataFrame(index=np.asarray(bar_ts, dtype=np.int64))
    for side in ("bid", "ask"):
        for field in ("open", "high", "low", "close"):
            arr = array_map[f"{side}_{field}"][keep]
            if field == "open":
                by_bucket = arr[starts]
            elif field == "high":
                by_bucket = np.maximum.reduceat(arr, starts)
            elif field == "low":
                by_bucket = np.minimum.reduceat(arr, starts)
            else:
                by_bucket = arr[starts + counts - 1]
            bars[f"{side}_{field}"] = by_bucket[good]
    # Ensure first and last minute timestamp cover the exact full five-minute bin.
    # (With five unique timestamps assigned to this bucket, this implies all five are present.)
    mid = pd.DataFrame(index=bars.index)
    for x in ("open","high","low","close"):
        mid[x] = (bars[f"bid_{x}"] + bars[f"ask_{x}"]) / 2.0
    gap_ms = np.diff(bars.index.to_numpy(dtype=np.int64))
    m5_gaps = int((gap_ms != FREQ).sum())
    if len(clean_ts) != 3_718_698 or len(bars) != 736_076:
        raise RuntimeError(f"Cleaned row/bar counts differ from registered baseline: M1={len(clean_ts)}, M5={len(bars)}")
    audit = {
        "status":"DATA_PASS",
        "source_paired_m1_rows":source_paired_rows,
        "raw_zip_sha256":EXPECTED_ZIP_SHA,
        "clean_paired_m1_rows":int(len(clean_ts)),
        "joint_repeated_flat_rows_removed":removed,
        "m1_invalid_retained_rows":invalid,
        "complete_m5_bars":int(len(bars)),
        "m5_gaps_over_5m":m5_gaps,
        "m1_first_utc":pd.to_datetime(int(clean_ts[0]),unit="ms",utc=True).isoformat(),
        "m1_last_utc":pd.to_datetime(int(clean_ts[-1]),unit="ms",utc=True).isoformat(),
        "m5_first_utc":pd.to_datetime(bars.index.min(),unit="ms",utc=True).isoformat(),
        "m5_last_utc":pd.to_datetime(bars.index.max(),unit="ms",utc=True).isoformat(),
        "clean_paired_m1_sha256":clean_hash,
        "cutoff_utc_exclusive":"2026-01-01T00:00:00Z",
        "m5_rule":"Only five unique contiguous paired M1 timestamps in exact UTC five-minute bucket; never synthesize bars.",
        "placeholder_rule":"Drop current row when current BID O/H/L/C all equal the preceding BID close and current ASK O/H/L/C all equal the preceding ASK close; this joint repeated-flat placeholder rule is independent of timestamp continuity. Never synthesize missing timestamps."
    }
    return None, bars, mid, audit

def add_features(bars: pd.DataFrame, mid: pd.DataFrame):
    ts = bars.index.to_numpy(dtype=np.int64)
    seg = np.zeros(len(ts), dtype=np.int32)
    if len(ts) > 1:
        seg[1:] = np.cumsum(np.diff(ts) != FREQ)
    close = mid["close"].to_numpy()
    r = np.full(len(close), np.nan)
    r[1:] = np.log(close[1:] / close[:-1])
    rs = pd.Series(r)
    roll3 = rs.rolling(3, min_periods=3).sum().to_numpy()
    roll6 = rs.rolling(6, min_periods=6).sum().to_numpy()
    roll12 = rs.rolling(12, min_periods=12).sum().to_numpy()
    abs12 = pd.Series(np.abs(r)).rolling(12, min_periods=12).sum().to_numpy()
    eff = np.divide(roll12, abs12, out=np.full(len(r), np.nan), where=abs12 > 0)
    accel = roll3 - pd.Series(roll3).shift(3).to_numpy()
    # Lag-1 autocorrelation among the trailing 12 five-minute returns.
    def lagcorr(x):
        a, b = x[:-1], x[1:]
        if len(a) < 2 or np.std(a) == 0 or np.std(b) == 0:
            return np.nan
        return float(np.corrcoef(a, b)[0,1])
    ac = rs.rolling(12, min_periods=12).apply(lagcorr, raw=True).to_numpy()
    ac_state = np.sign(roll12) * ac
    vol3 = rs.rolling(3, min_periods=3).std(ddof=0)
    volmedian = vol3.shift(1).rolling(48, min_periods=24).median()
    volcondition = roll3 * (vol3 / volmedian).to_numpy()
    scores = pd.DataFrame({
        "F1_RET15":roll3, "F2_RET30":roll6, "F3_RET60":roll12,
        "F4_ACCEL15":accel, "F5_EFFICIENCY60":eff,
        "F6_AUTOCORR_STATE":ac_state, "F7_VOL_CONDITIONED_RET15":volcondition
    })
    # Rolling windows must remain inside a single uninterrupted M5 segment.
    need = {"F1_RET15":3,"F2_RET30":6,"F3_RET60":12,"F4_ACCEL15":6,
            "F5_EFFICIENCY60":12,"F6_AUTOCORR_STATE":12,"F7_VOL_CONDITIONED_RET15":50}
    for f,n in need.items():
        valid = np.zeros(len(seg),dtype=bool)
        valid[n:] = seg[n:] == seg[:-n]
        scores.loc[~valid,f] = np.nan
    return scores, seg

def build_ledger(bars, mid, scores):
    ts = bars.index.to_numpy(dtype=np.int64)
    close_times = ts + FREQ
    sampled = ((close_times - ANCHOR_MS) % CADENCE == 0) & (close_times < int(CUTOFF.timestamp()*1000))
    ks = np.flatnonzero(sampled)
    rowmap = {int(t):i for i,t in enumerate(ts)}
    bid_o=bars["bid_open"].to_numpy(); bid_c=bars["bid_close"].to_numpy()
    ask_o=bars["ask_open"].to_numpy(); ask_c=bars["ask_close"].to_numpy()
    mid_o=mid["open"].to_numpy(); mid_c=mid["close"].to_numpy()
    feats=scores.to_numpy(dtype=float)
    rows=[]
    for k in ks:
        signal_close = int(close_times[k])
        entry_ts = signal_close + FREQ  # signal closes at t; wait five full minutes; entry at open t+5.
        entry_i = rowmap.get(entry_ts)
        row={
            "signal_close_utc":pd.to_datetime(signal_close,unit="ms",utc=True).isoformat(),
            "signal_close_ms":signal_close,
            "year":int(pd.to_datetime(signal_close,unit="ms",utc=True).year),
            "week_start_ms":int(MONDAY_ANCHOR_MS + ((signal_close-MONDAY_ANCHOR_MS)//WEEK_MS)*WEEK_MS),
            "entry_open_ms":entry_ts if entry_i is not None else np.nan,
            "entry_open_utc":pd.to_datetime(entry_ts,unit="ms",utc=True).isoformat() if entry_i is not None else "",
            "entry_skip_reason":"" if entry_i is not None else "MISSING_EXACT_DELAY_ENTRY_BAR",
            "entry_bid_open":float(bid_o[entry_i]) if entry_i is not None else np.nan,
            "entry_ask_open":float(ask_o[entry_i]) if entry_i is not None else np.nan,
            "entry_mid_open":float(mid_o[entry_i]) if entry_i is not None else np.nan,
        }
        for j,f in enumerate(FEATURES):
            row[f+"_score"] = float(feats[k,j]) if np.isfinite(feats[k,j]) else np.nan
        for h in HORIZONS:
            hb=h//5
            ex_i = entry_i + hb - 1 if entry_i is not None else None
            expected = entry_ts + (hb-1)*FREQ if entry_i is not None else None
            if ex_i is None or ex_i >= len(ts) or int(ts[ex_i]) != expected or not np.isfinite(bid_c[ex_i]) or not np.isfinite(ask_c[ex_i]):
                row[f"exit_{h}m_utc"]=""
                row[f"skip_{h}m"]="MISSING_EXACT_HORIZON_EXIT_BAR"
                row[f"mid_fwd_{h}m_pips"]=np.nan
                row[f"exit_bid_close_{h}m"]=np.nan
                row[f"exit_ask_close_{h}m"]=np.nan
                row[f"exit_mid_close_{h}m"]=np.nan
                for f in FEATURES: row[f"gross_exec_{f}_{h}m_pips"]=np.nan
                continue
            row[f"exit_{h}m_utc"]=pd.to_datetime(int(ts[ex_i]+FREQ),unit="ms",utc=True).isoformat()
            row[f"skip_{h}m"]=""
            row[f"mid_fwd_{h}m_pips"]=(mid_c[ex_i]-mid_o[entry_i])*10000.0
            row[f"exit_bid_close_{h}m"]=float(bid_c[ex_i])
            row[f"exit_ask_close_{h}m"]=float(ask_c[ex_i])
            row[f"exit_mid_close_{h}m"]=float(mid_c[ex_i])
            for j,f in enumerate(FEATURES):
                score=feats[k,j]
                if not np.isfinite(score) or score == 0:
                    row[f"gross_exec_{f}_{h}m_pips"]=np.nan
                elif score > 0:
                    row[f"gross_exec_{f}_{h}m_pips"]=(bid_c[ex_i]-ask_o[entry_i])*10000.0
                else:
                    row[f"gross_exec_{f}_{h}m_pips"]=(bid_o[entry_i]-ask_c[ex_i])*10000.0
        rows.append(row)
    ledger=pd.DataFrame(rows)
    ledger["cohort"]=np.select(
        [ledger["year"].between(2016,2018),ledger["year"].between(2019,2020),ledger["year"].between(2021,2025)],
        ["discovery","confirmation","diagnostic"],default="EXCLUDED")
    return ledger

def pf(values):
    x=np.asarray(values,dtype=float); x=x[np.isfinite(x)]
    gains=x[x>0].sum(); losses=-x[x<0].sum()
    return float(gains/losses) if losses>0 else (None if gains==0 else "inf")

def score_table(ledger):
    overall=[]; annual=[]
    for f in FEATURES:
        fcol=f+"_score"
        for h in HORIZONS:
            gcol=f"gross_exec_{f}_{h}m_pips"; mcol=f"mid_fwd_{h}m_pips"
            base=ledger.loc[np.isfinite(ledger[fcol]) & ledger[gcol].notna()].copy()
            score=base[fcol].to_numpy(dtype=float)
            target=base[mcol].to_numpy(dtype=float)
            rho,praw=spearmanr(score,target) if len(base)>2 and np.std(score)>0 and np.std(target)>0 else (np.nan,np.nan)
            # Midpoint-return top/bottom decile spread is a continuous-score diagnostic.
            qlo,qhi=np.quantile(score,[0.1,0.9]) if len(score) else (np.nan,np.nan)
            bot=base.loc[base[fcol]<=qlo,mcol].mean() if len(base) else np.nan
            top=base.loc[base[fcol]>=qhi,mcol].mean() if len(base) else np.nan
            gross=base[gcol].to_numpy(dtype=float)
            for cost in COSTS:
                net=gross-cost
                overall.append({
                    "feature":f,"horizon_minutes":h,"incremental_roundtrip_cost_pips":cost,
                    "eligible_directional_events":int(np.isfinite(gross).sum()),
                    "spearman_rho_midpoint_forward":float(rho) if np.isfinite(rho) else np.nan,
                    "spearman_p_raw":float(praw) if np.isfinite(praw) else np.nan,
                    "mean_net_pips_per_event":float(np.nanmean(net)) if np.isfinite(net).any() else np.nan,
                    "median_net_pips":float(np.nanmedian(net)) if np.isfinite(net).any() else np.nan,
                    "win_rate_net":float(np.mean(net[np.isfinite(net)]>0)) if np.isfinite(net).any() else np.nan,
                    "profit_factor_net":pf(net),
                    "top_minus_bottom_decile_mid_pips":float(top-bot) if np.isfinite(top) and np.isfinite(bot) else np.nan,
                    "top_decile_mid_pips":float(top) if np.isfinite(top) else np.nan,
                    "bottom_decile_mid_pips":float(bot) if np.isfinite(bot) else np.nan,
                })
            # Annual / cohort outcomes at registered primary +1 pip cost only.
            for cohort,part in base.groupby("cohort",sort=True):
                v=part[gcol].to_numpy(dtype=float)-1.0
                annual.append({"feature":f,"horizon_minutes":h,"period_type":"cohort","period":cohort,
                               "n":int(np.isfinite(v).sum()),"mean_net_pips":float(np.nanmean(v)) if np.isfinite(v).any() else np.nan,
                               "median_net_pips":float(np.nanmedian(v)) if np.isfinite(v).any() else np.nan,
                               "win_rate_net":float(np.mean(v[np.isfinite(v)]>0)) if np.isfinite(v).any() else np.nan,
                               "profit_factor_net":pf(v)})
            for year,part in base.groupby("year",sort=True):
                v=part[gcol].to_numpy(dtype=float)-1.0
                annual.append({"feature":f,"horizon_minutes":h,"period_type":"year","period":int(year),
                               "n":int(np.isfinite(v).sum()),"mean_net_pips":float(np.nanmean(v)) if np.isfinite(v).any() else np.nan,
                               "median_net_pips":float(np.nanmedian(v)) if np.isfinite(v).any() else np.nan,
                               "win_rate_net":float(np.mean(v[np.isfinite(v)]>0)) if np.isfinite(v).any() else np.nan,
                               "profit_factor_net":pf(v)})
    return pd.DataFrame(overall), pd.DataFrame(annual)

def weekly_series(ledger):
    first=int(MONDAY_ANCHOR_MS + ((ANCHOR_MS-MONDAY_ANCHOR_MS)//WEEK_MS)*WEEK_MS)
    last=int(MONDAY_ANCHOR_MS + ((int(CUTOFF.timestamp()*1000)-MONDAY_ANCHOR_MS)//WEEK_MS)*WEEK_MS)
    weeks=np.arange(first,last+1,WEEK_MS,dtype=np.int64)
    records=[]
    for f in FEATURES:
        s=ledger[f+"_score"].to_numpy(dtype=float)
        for h in HORIZONS:
            gross=ledger[f"gross_exec_{f}_{h}m_pips"].to_numpy(dtype=float)
            w=ledger["week_start_ms"].to_numpy(dtype=np.int64)
            for week in weeks:
                mask=(w==week)&np.isfinite(gross)&np.isfinite(s)&(s!=0)
                v=gross[mask]-1.0
                records.append({"feature":f,"horizon_minutes":h,"week_start_ms":int(week),
                                "week_start_utc":pd.to_datetime(int(week),unit="ms",utc=True).date().isoformat(),
                                "trade_count":int(mask.sum()),
                                "net_pips_sum":float(np.sum(v)) if len(v) else 0.0,
                                "mean_net_pips":float(np.mean(v)) if len(v) else 0.0})
    return pd.DataFrame(records)

def block_bootstrap(weekly: pd.DataFrame):
    result=[]
    # One-sided null that mean weekly outcome <= 0; circular four-week blocks preserve local dependence.
    for f in FEATURES:
        for h in HORIZONS:
            s=weekly.loc[(weekly.feature==f)&(weekly.horizon_minutes==h)].sort_values("week_start_ms")
            x=s["mean_net_pips"].to_numpy(dtype=float)
            if len(x)<20:
                result.append({"feature":f,"horizon_minutes":h,"cohort":"ALL_REGISTERED_WEEKS","n_weeks":len(x),"mean_weekly_net_pips":np.nan,"p_raw_one_sided":np.nan,"p_bonferroni_28":np.nan,"bootstrap_ci95_low":np.nan,"bootstrap_ci95_high":np.nan})
                continue
            rng=np.random.default_rng(BOOT_SEED + FEATURES.index(f)*100 + HORIZONS.index(h))
            n=len(x); bsize=4; nblocks=math.ceil(n/bsize); B=BOOT_REPS
            starts=rng.integers(0,n,size=(B,nblocks))
            offsets=np.arange(bsize,dtype=np.int64)
            ids=(starts[:,:,None]+offsets[None,None,:])%n
            ids=ids.reshape(B,-1)[:,:n]
            observed=float(np.mean(x))
            centered=x-observed
            null_means=np.mean(centered[ids],axis=1)
            raw=float((1+np.sum(null_means>=observed))/(B+1)) if observed>0 else 1.0
            boot_means=np.mean(x[ids],axis=1)
            lo,hi=np.quantile(boot_means,[0.025,0.975])
            result.append({"feature":f,"horizon_minutes":h,"cohort":"ALL_REGISTERED_WEEKS","n_weeks":n,
                           "mean_weekly_net_pips":observed,"p_raw_one_sided":raw,
                           "p_bonferroni_28":min(raw*28,1.0),"bootstrap_ci95_low":float(lo),"bootstrap_ci95_high":float(hi)})
            for cohort,start,end in (("discovery",2016,2018),("confirmation",2019,2020)):
                # A separate blocked inference only within the exact registered chronological cohort.
                if cohort=="discovery": lo_y,hi_y=2016,2018
                else: lo_y,hi_y=2019,2020
                subset=ledger_cohort_weeks(weekly,s,lo_y,hi_y)
                xx=subset["mean_net_pips"].to_numpy(dtype=float)
                if len(xx)<20: continue
                rng2=np.random.default_rng(BOOT_SEED + FEATURES.index(f)*100 + HORIZONS.index(h) + (10_000 if cohort=="confirmation" else 5_000))
                nn=len(xx); nb=math.ceil(nn/bsize)
                st=rng2.integers(0,nn,size=(B,nb))
                ii=((st[:,:,None]+offsets[None,None,:])%nn).reshape(B,-1)[:,:nn]
                obs=float(np.mean(xx)); null=np.mean((xx-obs)[ii],axis=1)
                p=float((1+np.sum(null>=obs))/(B+1)) if obs>0 else 1.0
                bm=np.mean(xx[ii],axis=1); cl,ch=np.quantile(bm,[0.025,0.975])
                result.append({"feature":f,"horizon_minutes":h,"cohort":cohort,"n_weeks":nn,
                               "mean_weekly_net_pips":obs,"p_raw_one_sided":p,"p_bonferroni_28":min(p*28,1.0),
                               "bootstrap_ci95_low":float(cl),"bootstrap_ci95_high":float(ch)})
    return pd.DataFrame(result)

def ledger_cohort_weeks(weekly, subset, lo_year, hi_year):
    # Use registered week-level rows; exclude weeks whose Monday lies outside the cohort.
    dates=pd.to_datetime(subset["week_start_ms"],unit="ms",utc=True)
    mask=dates.dt.year.between(lo_year,hi_year)
    return subset.loc[mask]

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    paired,bars,mid,audit=read_source()
    scores,_=add_features(bars,mid)
    # Only signal-close times in fixed cadence; build causal feature-to-executable-outcome ledger.
    ledger=build_ledger(bars,mid,scores)
    audit.update({
        "m5_feature_sample_rows":int(len(ledger)),
        "eligible_entry_rows":int(ledger["entry_skip_reason"].eq("").sum()),
        "entry_skip_counts":ledger.loc[ledger.entry_skip_reason.ne(""),"entry_skip_reason"].value_counts().to_dict(),
        "cohort_counts":ledger["cohort"].value_counts().to_dict(),
        "sampling_cadence_minutes":65,
        "prediction_horizons_minutes":list(HORIZONS),
        "registered_features":list(FEATURES),
        "registered_pair_tests":28,
        "data_audit_result":"PASS" if audit["status"]=="DATA_PASS" else "COUNT_MISMATCH_REVIEW_REQUIRED",
    })
    scorecard,annual=score_table(ledger)
    weekly=weekly_series(ledger)
    boot=block_bootstrap(weekly)
    # Complete event ledger including raw scores, exact timestamps, skips, quotes via base outcome fields.
    save_csv_gzip(ledger,OUT/"R321_PREDICTION_EVENT_LEDGER.csv.gz")
    scorecard.to_csv(OUT/"R321_SCORECARD_ALL_COSTS.csv",index=False,lineterminator="\n",float_format="%.10g")
    annual.to_csv(OUT/"R321_ANNUAL_COHORT_SCORECARD.csv",index=False,lineterminator="\n",float_format="%.10g")
    save_csv_gzip(weekly,OUT/"R321_WEEKLY_NET_PIPS_ZERO_INCLUSIVE.csv.gz")
    boot.to_csv(OUT/"R321_BLOCK_BOOTSTRAP.csv",index=False,lineterminator="\n",float_format="%.10g")
    (OUT/"R321_DATA_AUDIT.json").write_text(json.dumps(audit,indent=2,sort_keys=True)+"\n")
    env={"python":__import__("sys").version.split()[0],"pandas":pd.__version__,"numpy":np.__version__,
         "scipy":__import__("scipy").__version__,"script_sha256":sha_file(Path(__file__)),
         "source_zip_sha256":sha_file(SOURCE),"output_dir":str(OUT)}
    (OUT/"R321_ENVIRONMENT.json").write_text(json.dumps(env,indent=2,sort_keys=True)+"\n")
    manifest=[]
    for p in sorted(OUT.iterdir()):
        if p.is_file() and p.name!="R321_OUTPUT_MANIFEST.json":
            manifest.append({"path":p.name,"bytes":p.stat().st_size,"sha256":sha_file(p)})
    (OUT/"R321_OUTPUT_MANIFEST.json").write_text(json.dumps(manifest,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"data_audit":audit,"outputs":[{"path":x["path"],"bytes":x["bytes"],"sha256":x["sha256"]} for x in manifest]},indent=2,sort_keys=True))

if __name__=="__main__":
    main()
