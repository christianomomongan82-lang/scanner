#!/usr/bin/env python3
"""Exact local replay for preregistered R299; no 2022+ outcomes are calculated."""
import argparse, hashlib, pandas as pd, numpy as np, json
from pathlib import Path

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--data-dir", required=True, help="Directory containing the two exact .csv.gz members")
parser.add_argument("--output-dir", default="r299_output", help="Where CSV/JSON audit outputs are written")
args = parser.parse_args()
ROOT = Path(args.data_dir)
OUT = Path(args.output_dir)
OUT.mkdir(parents=True, exist_ok=True)
EXPECTED_CSV_SHA256 = {
    "usa500idxusd_m5.csv.gz": "df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee",
    "usatechidxusd_m5.csv.gz": "82b06c38f66cd1387097691baac1d45c9463b6540eea9dfe28a894d85e122f7c",
}
SOURCE_ARCHIVE_SHA256 = {
    "usa500_zip_sha256": "21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac",
    "usatech_zip_sha256": "91c7d44b0487e98eeea021712528910475e626bf433220a007629f3005fc66ad",
}
def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()
for filename, expected in EXPECTED_CSV_SHA256.items():
    path = ROOT / filename
    if not path.is_file():
        raise FileNotFoundError(f"Missing required input: {path}")
    actual = sha256_file(path)
    if actual != expected:
        raise ValueError(f"SHA-256 mismatch for {filename}: expected {expected}, got {actual}")
CUTOFF = pd.Timestamp('2022-01-01T00:00:00Z')

def load(name):
    f=ROOT/name
    d=pd.read_csv(f, compression='gzip')
    d=d.loc[pd.to_datetime(d['timestamp'],unit='ms',utc=True)<CUTOFF].copy()
    d['timestamp']=d['timestamp'].astype('int64')
    d=d.sort_values('timestamp').reset_index(drop=True)
    return d

def validate(d, label):
    assert not d.timestamp.duplicated().any(), label+' duplicate timestamps'
    assert d.timestamp.is_monotonic_increasing, label+' not monotonic'
    assert ((d.timestamp % 300000)==0).all(), label+' off M5 grid'
    assert (d.high>=d.low).all() and (d.high>=d[['open','close']].max(axis=1)).all() and (d.low<=d[['open','close']].min(axis=1)).all(),label+' invalid OHLC'
    d['active']=((d.high>d.low)|(d.open!=d.close))
    return d

usa=validate(load('usa500idxusd_m5.csv.gz'),'usa500')
tech=validate(load('usatechidxusd_m5.csv.gz'),'usatech')
for df in (usa,tech):
    df['dt']=pd.to_datetime(df.timestamp,unit='ms',utc=True).dt.tz_convert('America/New_York')
    df['date_ny']=df.dt.dt.date
    df['weekday']=df.dt.dt.weekday
    df['minute_day']=df.dt.dt.hour*60+df.dt.dt.minute

# timestamp-key maps, no row-number pairing
usa_map={int(t):i for i,t in enumerate(usa.timestamp.to_numpy())}
tech_map={int(t):i for i,t in enumerate(tech.timestamp.to_numpy())}
# Calibration source windows: seven active continuous M5 bars, signal bar local start 10:00-14:55 weekdays.
TS=tech.timestamp.to_numpy(); act=tech.active.to_numpy(); close=tech.close.to_numpy(dtype=float); dt=tech.dt
abs_rets=[]; valid_window_by_idx={}
for i in range(6,len(tech)):
    t=int(TS[i])
    if not all(act[i-6:i+1]): continue
    if not np.all(np.diff(TS[i-6:i+1])==300000): continue
    local=dt.iloc[i]
    if local.weekday()>=5 or not (10*60 <= local.hour*60+local.minute < 15*60): continue
    ret=close[i]/close[i-6]-1
    valid_window_by_idx[i]=ret
    if local.year==2016: abs_rets.append(abs(ret))
q95=float(np.quantile(abs_rets,0.95))

# Freeze first threshold crossing per New York date; selection occurs before target-side execution checks.
selected=[]
seen_dates=set()
for i,ret in valid_window_by_idx.items():
    local=dt.iloc[i]
    if local.year<2017 or local.year>=2022: continue
    if abs(ret)<q95: continue
    day=local.date()
    if day in seen_dates: continue
    seen_dates.add(day)
    selected.append({'idx':i,'timestamp':int(TS[i]),'date_ny':str(day),'source_return':float(ret),'direction':1 if ret>0 else -1})
selected.sort(key=lambda x:x['timestamp'])

# Return exact target path per frozen event. All six risk bars, exact T+10 entry and full M5 path to T+40 required.
UTS=usa.timestamp.to_numpy(); uact=usa.active.to_numpy(); uopen=usa.open.to_numpy(float); uhigh=usa.high.to_numpy(float); ulow=usa.low.to_numpy(float)
# Build metrics and audit using registered exact timestamp rules.
audits=[]; trades=[]
for ev in selected:
    T=ev['timestamp']; d=ev['direction']; reason=''; ui=[]
    # risk bars timestamps T-25 through T inclusive = 6 bars
    for j in range(-5,1):
        tt=T+j*300000
        ix=usa_map.get(tt)
        if ix is None: reason='missing_risk_timestamp'; break
        ui.append(ix)
    if not reason:
        if not all(uact[x] for x in ui): reason='inactive_risk_bar'
        elif not np.all(np.diff(UTS[ui])==300000): reason='noncontiguous_risk_bars'
    if reason:
        audits.append({**ev,'status':'SKIP','reason':reason}); continue
    R=float(np.mean((uhigh[ui]-ulow[ui])))
    if not np.isfinite(R) or R<=0:
        audits.append({**ev,'status':'SKIP','reason':'nonpositive_risk_range'}); continue
    entry_t=T+2*300000
    ei=usa_map.get(entry_t)
    if ei is None or not uact[ei]:
        audits.append({**ev,'status':'SKIP','reason':'missing_or_inactive_entry'}); continue
    entry=float(uopen[ei])
    stop=entry-d*R
    target=entry+d*1.5*R
    exit_t=entry_t+6*300000 # exact T+40
    # check bars beginning entry through entry+25m; don't inspect cap bar's high/low
    chosen_exit=None; exit_kind=None; exit_time=None
    invalid=False
    for k in range(6):
        bt=entry_t+k*300000
        bi=usa_map.get(bt)
        if bi is None:
            reason='missing_path_timestamp'; invalid=True; break
        if not uact[bi]:
            reason='inactive_path_bar'; invalid=True; break
        if k and (UTS[bi]-UTS[usa_map[bt-300000]]!=300000):
            reason='noncontiguous_path'; invalid=True; break
        op=float(uopen[bi]); hi=float(uhigh[bi]); lo=float(ulow[bi])
        if d==1:
            # adverse opening gap through stop first; target opening gap through target next.
            if op<=stop: chosen_exit=op; exit_kind='stop_gap'
            elif op>=target: chosen_exit=op; exit_kind='target_gap'
            elif lo<=stop and hi>=target: chosen_exit=stop; exit_kind='stop_collision'
            elif lo<=stop: chosen_exit=stop; exit_kind='stop'
            elif hi>=target: chosen_exit=target; exit_kind='target'
        else:
            if op>=stop: chosen_exit=op; exit_kind='stop_gap'
            elif op<=target: chosen_exit=op; exit_kind='target_gap'
            elif hi>=stop and lo<=target: chosen_exit=stop; exit_kind='stop_collision'
            elif hi>=stop: chosen_exit=stop; exit_kind='stop'
            elif lo<=target: chosen_exit=target; exit_kind='target'
        if chosen_exit is not None:
            exit_time=bt; break
    if invalid:
        audits.append({**ev,'status':'SKIP','reason':reason}); continue
    if chosen_exit is None:
        # exact entry+30-minute bar OPEN, do not inspect cap bar's range.
        xi=usa_map.get(exit_t)
        if xi is None or not uact[xi]:
            audits.append({**ev,'status':'SKIP','reason':'missing_or_inactive_time_exit'}); continue
        chosen_exit=float(uopen[xi]); exit_kind='time'; exit_time=exit_t
    gross_r=d*(chosen_exit-entry)/R
    row={**ev,'entry_time_utc':pd.to_datetime(entry_t,unit='ms',utc=True).isoformat(),'exit_time_utc':pd.to_datetime(exit_time,unit='ms',utc=True).isoformat(),
         'entry':entry,'exit':float(chosen_exit),'risk_distance':R,'exit_type':exit_kind,'hold_minutes':(exit_time-entry_t)/60000,'gross_R':gross_r}
    for cost in (1,2,4):
        row[f'net_R_{cost}bp']=(d*(chosen_exit-entry)-entry*cost/10000.0)/R
    trades.append(row); audits.append({**ev,'status':'TRADE','reason':'','exit_type':exit_kind})

tr=pd.DataFrame(trades).sort_values('timestamp').reset_index(drop=True)
aud=pd.DataFrame(audits).sort_values('timestamp').reset_index(drop=True)

def stats(frame, cost):
    vals=frame[f'net_R_{cost}bp'].to_numpy(float)
    cum=np.cumsum(vals)
    peaks=np.maximum.accumulate(np.r_[0.0,cum])[1:]
    dd=peaks-cum
    return {'trades':int(len(frame)),'net_R':float(vals.sum()),'PF_R':float(vals[vals>0].sum()/(-vals[vals<0].sum())) if (vals<0).any() else None,
            'win_rate_pct':float((vals>0).mean()*100) if len(vals) else None,'max_closed_DD_R':float(dd.max()) if len(dd) else 0.0,
            'longs':int((frame.direction==1).sum()),'shorts':int((frame.direction==-1).sum()),
            'stop_exits':int(frame.exit_type.str.startswith('stop').sum()),'target_exits':int(frame.exit_type.str.startswith('target').sum()),'time_exits':int((frame.exit_type=='time').sum()),
            'mean_hold_min':float(frame.hold_minutes.mean()) if len(frame) else None}
summary={'q95':q95,'calibration_windows_2016':len(abs_rets),'valid_windows_through_2021':len(valid_window_by_idx),'events_selected':len(selected),'completed_trades':len(tr),
         'skip_counts':aud.loc[aud.status=='SKIP','reason'].value_counts().to_dict(),
         'rows':{'usa500':len(usa),'usatech':len(tech),'usa500_active':int(usa.active.sum()),'usatech_active':int(tech.active.sum())},
         'periods':{}}
for name,mask in [('discovery_2017_2020',tr.timestamp.map(lambda x:pd.Timestamp(x,unit='ms',tz='UTC').year).between(2017,2020)),('validation_2021',tr.timestamp.map(lambda x:pd.Timestamp(x,unit='ms',tz='UTC').year)==2021)]:
    fr=tr.loc[mask].copy()
    summary['periods'][name]={f'cost_{c}bp':stats(fr,c) for c in (1,2,4)}
    # annual summaries at each cost
    summary['periods'][name]['annual']={str(y):{f'cost_{c}bp':stats(fr.loc[fr.timestamp.map(lambda x:pd.Timestamp(x,unit='ms',tz='UTC').year)==y],c) for c in (1,2,4)} for y in sorted({pd.Timestamp(x,unit='ms',tz='UTC').year for x in fr.timestamp})}
# weekly validation bootstrap (4-week circular blocks; 10000 resamples; seed 299)
val=tr[tr.timestamp.map(lambda x:pd.Timestamp(x,unit='ms',tz='UTC').year)==2021].copy()
val['utc_dt']=pd.to_datetime(val.timestamp,unit='ms',utc=True)
val['ny_week']=val.utc_dt.dt.tz_convert('America/New_York').dt.tz_localize(None).dt.to_period('W-SUN').apply(lambda p:p.start_time.date())
week_start=pd.date_range('2021-01-04','2021-12-27',freq='W-MON')
week_dates=[x.date() for x in week_start]
weekly=[]
for d0 in week_dates:
    weekly.append(float(val.loc[val.ny_weak==d0.date() if isinstance(d0,pd.Timestamp) else val.ny_week==d0,'net_R_2bp'].sum()))
# Simplify with ISO week starting Monday keyed by local date
# Recalculate using NY dates to ensure Monday-start weeks including first incomplete week.
val['ny_date']=val.utc_dt.dt.tz_convert('America/New_York').dt.date
val['week_monday']=val.ny_date.map(lambda d: d-pd.Timedelta(days=d.weekday()))
weeks=pd.date_range('2021-01-04','2021-12-27',freq='W-MON').date
weekly=np.array([val.loc[val.week_monday==d,'net_R_2bp'].sum() for d in weeks],dtype=float)
rng=np.random.default_rng(299); n=len(weekly); bs=[]
for _ in range(10000):
    starts=rng.integers(0,n,size=int(np.ceil(n/4)))
    inds=np.concatenate([(np.arange(s,s+4)%n) for s in starts])[:n]
    bs.append(weekly[inds].mean())
summary['bootstrap_2021_2bp']={'weeks':len(weekly),'trade_weeks':int((weekly!=0).sum()),'mean_weekly_net_R':float(weekly.mean()),'ci95_lower':float(np.quantile(bs,0.025)),'ci95_upper':float(np.quantile(bs,0.975)),'resamples':10000,'block_len':4,'seed':299}
# Include all registered input identities and exact timestamp-key coverage in the machine-readable report.
summary["candidate"] = "R299_USATECH_LEADS_USA500_30M"
summary["verdict"] = "GAGAL"
summary["cutoff_utc_exclusive"] = "2022-01-01T00:00:00Z"
summary["source_archive_sha256"] = SOURCE_ARCHIVE_SHA256
summary["source_member_sha256"] = EXPECTED_CSV_SHA256
summary["timestamp_alignment_through_cutoff"] = {
    "shared_timestamps": int(len(set(usa.timestamp.astype(int)) & set(tech.timestamp.astype(int)))),
    "usa500_only_timestamps": int(len(set(usa.timestamp.astype(int)) - set(tech.timestamp.astype(int)))),
    "usatech_only_timestamps": int(len(set(tech.timestamp.astype(int)) - set(usa.timestamp.astype(int)))),
}
summary["cost_bps_round_trip"] = [1, 2, 4]
summary["period_definitions"] = {"discovery": "2017-2020", "validation": "2021", "calibration": "2016 only"}
# Export the exact artifacts needed to inspect/replay this locked result.
tr.to_csv(OUT / "R299_reproduced_trade_ledger.csv", index=False)
aud.to_csv(OUT / "R299_reproduced_event_audit.csv", index=False)
pd.DataFrame({"week_monday": weeks, "net_R_2bp": weekly}).to_csv(OUT / "R299_reproduced_validation_weekly_net_R.csv", index=False)
(OUT / "R299_reproduced_metrics.json").write_text(json.dumps(summary, indent=2))
print(json.dumps({k: summary[k] for k in ["candidate", "verdict", "q95", "calibration_windows_2016", "valid_windows_through_2021", "events_selected", "completed_trades", "skip_counts", "rows", "timestamp_alignment_through_cutoff", "periods", "bootstrap_2021_2bp"]}, indent=2))
