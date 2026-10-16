#!/usr/bin/env python3
"""R282 locked EURUSD weekend-reopening gap-fade backtest; local execution only."""
from __future__ import annotations
import argparse, hashlib, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

PIP=0.0001
EXTRA_COSTS=(0.0,0.5,1.0,2.0)
GAP_MS=36*60*60*1000
DELAY_MS=10*60*1000
HOLD_MS=48*60*60*1000
SEED=2822026
ARCHIVE_SHA='b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e'
PERIODS={
 'discovery':('2017-01-01','2021-01-01'),
 'validation':('2021-01-01','2022-01-01'),
 'forward_2022_2025':('2022-01-01','2026-01-01'),
}

def sha256_file(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''): h.update(chunk)
    return h.hexdigest()

def load_data(zip_path):
    with zipfile.ZipFile(zip_path) as z:
        manifest=json.loads(z.read('manifest.json'))
        def read(side):
            with z.open(f'eurusd_{side}_M1_2016-2025.csv.gz') as f: df=pd.read_csv(f,compression='gzip')
            df['timestamp']=pd.to_numeric(df.timestamp,errors='raise').astype('int64')
            df=df.sort_values('timestamp').drop_duplicates('timestamp',keep='last').set_index('timestamp')
            return df[['open','high','low','close']].astype(float)
        bid0,ask0=read('bid'),read('ask')
    common=bid0.index.intersection(ask0.index).sort_values()
    bid,ask=bid0.loc[common].copy(),ask0.loc[common].copy()
    def bad(d):
        return ~((d.high>=d[['open','close']].max(axis=1))&(d.low<=d[['open','close']].min(axis=1))&(d.high>=d.low))
    valid=~(bad(bid).to_numpy()|bad(ask).to_numpy())
    bid=bid.iloc[np.flatnonzero(valid)].copy(); ask=ask.iloc[np.flatnonzero(valid)].copy()
    ts=bid.index.to_numpy(np.int64)
    bo,bh,bl,bc=(bid[c].to_numpy(float) for c in ('open','high','low','close'))
    ao,ah,al,ac=(ask[c].to_numpy(float) for c in ('open','high','low','close'))
    if np.any(ao-bo < -1e-9): raise RuntimeError('negative opening spread')
    # Same conservative paired flat-candidate heuristic as R275/R281 for -fl source.
    flatb=(bo==bh)&(bh==bl)&(bl==bc); flata=(ao==ah)&(ah==al)&(al==ac)
    consecutive=np.r_[False,np.diff(ts)==60000]
    copyb=np.isclose(bo,np.r_[np.nan,bc[:-1]],rtol=0,atol=1e-12)
    copya=np.isclose(ao,np.r_[np.nan,ac[:-1]],rtol=0,atol=1e-12)
    synthetic=flatb&flata&copyb&copya&consecutive
    removed=int(synthetic.sum()); keep=~synthetic
    bid=bid.iloc[np.flatnonzero(keep)].copy(); ask=ask.iloc[np.flatnonzero(keep)].copy()
    ts=bid.index.to_numpy(np.int64)
    arrays={'ts':ts}
    for side,df in [('b',bid),('a',ask)]:
        for col in ('open','high','low','close'): arrays[side+col[0]]=df[col].to_numpy(float)
    spread=(arrays['ao']-arrays['bo'])/PIP
    if np.any(spread < -1e-9): raise RuntimeError('negative opening spread after filter')
    audit={
      'source':'Dukascopy EURUSD M1 BID/ASK via dukascopy-node',
      'archive_sha256':sha256_file(zip_path),'expected_archive_sha256':ARCHIVE_SHA,
      'archive_sha_matches':sha256_file(zip_path)==ARCHIVE_SHA,
      'manifest_status':manifest.get('status'),'requested_window_utc':manifest.get('requested_window_utc'),
      'raw_bid_rows_after_dedupe':int(len(bid0)),'raw_ask_rows_after_dedupe':int(len(ask0)),
      'paired_valid_rows_before_flat_filter':int(len(common[valid])),
      'paired_synthetic_flat_candidates_removed':removed,'paired_rows_after_filter':int(len(ts)),
      'start_utc':pd.to_datetime(ts[0],unit='ms',utc=True).isoformat(),
      'end_utc':pd.to_datetime(ts[-1],unit='ms',utc=True).isoformat(),
      'opening_spread_pips':{'median':float(np.median(spread)),'p95':float(np.quantile(spread,.95)),'max':float(np.max(spread))},
      'caveat':'Source collector used -fl. Paired flat-candidate removal is heuristic and not proof all synthetic bars were removed.'}
    return arrays,audit

def find_events(x):
    ts=x['ts']; dif=np.diff(ts)
    candidates=np.flatnonzero(dif>=GAP_MS)+1
    prev_dt=pd.to_datetime(ts[candidates-1],unit='ms',utc=True)
    cur_dt=pd.to_datetime(ts[candidates],unit='ms',utc=True)
    ok=(np.asarray(prev_dt.dayofweek)==4)&np.isin(np.asarray(cur_dt.dayofweek),[6,0])
    idx=candidates[ok]
    events=[]
    for i in idx:
        prev=i-1; t=int(ts[i])
        mid_open=(x['bo'][i]+x['ao'][i])/2
        mid_friday=(x['bc'][prev]+x['ac'][prev])/2
        gap_pips=(mid_open-mid_friday)/PIP
        if abs(gap_pips)<1e-12: continue
        events.append({'event_index':int(i),'friday_index':int(prev),'event_ts':t,
                       'friday_close_mid':float(mid_friday),'gap_pips':float(gap_pips),
                       'direction':'SHORT' if gap_pips>0 else 'LONG'})
    return events, {'long_gap_timestamps_ge_36h':int(len(candidates)), 'friday_to_sunday_monday_events':int(len(events))}

def pf(values):
    a=np.asarray(values,float); g=float(a[a>0].sum()); l=float(-a[a<0].sum())
    if l==0: return float('inf') if g>0 else None
    return g/l

def simulate(x,events):
    ts=x['ts']; trades=[]; diag={'events':len(events),'not_exact_delay_timestamp':0,'nonsequential_first_11_minutes':0,
      'target_already_filled_at_entry':0,'invalid_stop_distance':0,'overlap_skipped':0,'censored_end':0,'entry_spread_gt_1p5':0}
    last_exit=-1
    for ev in events:
        i=ev['event_index']; t=int(ts[i]); desired=t+DELAY_MS
        # Need all first 10 minutes plus exact delayed-entry minute, with no filtered/missing timestamps.
        if i+10>=len(ts) or ts[i+10]!=desired:
            diag['not_exact_delay_timestamp']+=1; continue
        if not np.array_equal(ts[i:i+11],t+np.arange(11,dtype=np.int64)*60000):
            diag['nonsequential_first_11_minutes']+=1; continue
        e=i+10
        if e<=last_exit:
            diag['overlap_skipped']+=1; continue
        gap=abs(ev['gap_pips'])*PIP
        short=ev['gap_pips']>0
        if short:
            direction=-1
            entry=float(x['bo'][e]); target=float(x['ac'][ev['friday_index']])
            stop=float(np.max(x['ah'][i:i+10])+0.5*gap)
            risk=stop-entry
            if entry<=target:
                diag['target_already_filled_at_entry']+=1; continue
        else:
            direction=1
            entry=float(x['ao'][e]); target=float(x['bc'][ev['friday_index']])
            stop=float(np.min(x['bl'][i:i+10])-0.5*gap)
            risk=entry-stop
            if entry>=target:
                diag['target_already_filled_at_entry']+=1; continue
        if not np.isfinite(risk) or risk<=0:
            diag['invalid_stop_distance']+=1; continue
        entry_spread=(x['ao'][e]-x['bo'][e])/PIP
        timeout_ts=int(ts[e]+HOLD_MS)
        timeout_idx=int(np.searchsorted(ts,timeout_ts,side='left'))
        xi=xp=reason=None
        stop_side='b' if direction==1 else 'a'
        op=x[stop_side+'open']; hi=x[stop_side+'high']; lo=x[stop_side+'low']
        end_scan=min(timeout_idx,len(ts))
        for j in range(e,end_scan):
            if direction==1:
                if op[j]<=stop: xi,xp,reason=j,float(op[j]),'STOP_GAP'; break
                if op[j]>=target: xi,xp,reason=j,float(op[j]),'TARGET_GAP'; break
                st=lo[j]<=stop; tp=hi[j]>=target
            else:
                if op[j]>=stop: xi,xp,reason=j,float(op[j]),'STOP_GAP'; break
                if op[j]<=target: xi,xp,reason=j,float(op[j]),'TARGET_GAP'; break
                st=hi[j]>=stop; tp=lo[j]<=target
            if st:
                xi,xp,reason=j,stop,'STOP_BOTH' if tp else 'STOP'; break
            if tp:
                xi,xp,reason=j,target,'TARGET'; break
        if xi is None:
            if timeout_idx>=len(ts):
                diag['censored_end']+=1; continue
            xi=timeout_idx; xp=float(op[xi]); reason='TIME_OPEN'
        gross=(xp-entry)/PIP if direction==1 else (entry-xp)/PIP
        iso=lambda k:pd.to_datetime(int(k),unit='ms',utc=True).isoformat()
        trades.append({'event_utc':iso(t),'friday_close_utc':iso(ts[ev['friday_index']]),'entry_utc':iso(ts[e]),'exit_utc':iso(ts[xi]),
          'gap_pips':ev['gap_pips'],'direction':'LONG' if direction==1 else 'SHORT','entry_spread_pips':entry_spread,
          'entry_price':entry,'target_price':target,'stop_price':stop,'risk_pips':risk/PIP,'exit_price':xp,'exit_reason':reason,
          'gross_pips':float(gross),'bars_held':int(xi-e)})
        last_exit=xi
    diag['closed_trades']=len(trades)
    diag['spread_p95_pips']=float(np.quantile([t['entry_spread_pips'] for t in trades],.95)) if trades else None
    return trades,diag

def period_trades(trades,lo,hi):
    lo=pd.Timestamp(lo,tz='UTC'); hi=pd.Timestamp(hi,tz='UTC')
    return [t for t in trades if lo<=pd.Timestamp(t['entry_utc'])<hi and pd.Timestamp(t['exit_utc'])<hi]

def summarize(trades,cost):
    v=np.array([t['gross_pips']-cost for t in trades],float); eq=np.cumsum(v)
    dd=float(np.max(np.maximum.accumulate(np.r_[0.,eq])[1:]-eq)) if len(v) else 0.
    return {'trades':int(len(v)),'PF':pf(v),'net_pips':float(v.sum()) if len(v) else 0.,
      'mean_net_pips_per_trade':float(v.mean()) if len(v) else None,'win_rate':float(np.mean(v>0)) if len(v) else None,
      'max_drawdown_pips':dd,'median_gap_pips':float(np.median([t['gap_pips'] for t in trades])) if trades else None}

def weekly_bootstrap(trades,cost):
    lo=pd.Timestamp('2022-01-01',tz='UTC'); hi=pd.Timestamp('2026-01-01',tz='UTC')
    weeks=int(np.ceil((hi-lo).total_seconds()/(7*24*3600))); weekly=np.zeros(weeks,float)
    for t in trades:
        et=pd.Timestamp(t['entry_utc'])
        if lo<=et<hi:
            k=min(int((et-lo).total_seconds()/(7*24*3600)),weeks-1); weekly[k]+=t['gross_pips']-cost
    rng=np.random.default_rng(SEED); means=np.empty(10000); n=len(weekly)
    for r in range(len(means)):
        seq=[]
        while len(seq)<n:
            s=int(rng.integers(0,n)); seq.extend(weekly[(s+np.arange(4))%n].tolist())
        means[r]=np.mean(seq[:n])
    return {'weeks':weeks,'block_weeks':4,'replicates':10000,'seed':SEED,'mean_weekly_net_pips':float(weekly.mean()),
      'ci95_mean_weekly_net_pips':[float(q) for q in np.quantile(means,[.025,.975])],'probability_weekly_mean_positive':float(np.mean(means>0))}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--data-zip',default='/mnt/data/eurusd_m1_bid_ask.zip'); ap.add_argument('--out-dir',default='/mnt/data/r282_outputs'); args=ap.parse_args()
    if sha256_file(args.data_zip)!=ARCHIVE_SHA: raise SystemExit('Unexpected EURUSD archive SHA-256; stopped.')
    out=Path(args.out_dir); out.mkdir(parents=True,exist_ok=True)
    x,audit=load_data(args.data_zip); events,event_diag=find_events(x); trades,exec_diag=simulate(x,events)
    periods={name:period_trades(trades,*bounds) for name,bounds in PERIODS.items() if name!='forward_2022_2025'}
    costs={str(c):{'discovery':summarize(periods['discovery'],c),'validation':summarize(periods['validation'],c)} for c in EXTRA_COSTS}
    gates={'discovery_trades_ge_100':costs['1.0']['discovery']['trades']>=100,
      'discovery_PF_plus1_ge_1':costs['1.0']['discovery']['PF'] is not None and costs['1.0']['discovery']['PF']>=1.0,
      'validation_trades_ge_30':costs['1.0']['validation']['trades']>=30,
      'validation_PF_plus1_ge_1p10_and_net_positive':costs['1.0']['validation']['PF'] is not None and costs['1.0']['validation']['PF']>=1.10 and costs['1.0']['validation']['net_pips']>0,
      'validation_PF_plus2_ge_1':costs['2.0']['validation']['PF'] is not None and costs['2.0']['validation']['PF']>=1.0}
    proceed=all(gates.values())
    result={'round':'R282','candidate':'EURUSD weekend-reopening gap fade','preregistration':'research/R282_EURUSD_WEEKEND_GAP_FADE_PREREGISTRATION.md',
      'verdict':'NOT_YET_PROMOTED' if proceed else 'GAGAL','stage':'FORWARD_SCREEN_AUTHORIZED' if proceed else 'STOPPED_AT_DISCOVERY_VALIDATION_GATE',
      'data_audit':audit,'event_diagnostics':event_diag,'execution_diagnostics':exec_diag,
      'locked_rules':{'weekend_gap_min_hours':36,'prior_timestamp_weekday_utc':'Friday','reopen_timestamp_weekday_utc':['Sunday','Monday'],'entry_delay_minutes':10,'opening_range_minutes':10,'stop_extension_gap_multiple':0.5,'target':'previous Friday executable close','timeout_hours':48,'extra_cost_pips':list(EXTRA_COSTS)},
      'period_cost_stress':costs,'discovery_validation_gates':gates,'forward_stage_authorized':bool(proceed),
      'limitations':['Dukascopy collector used -fl; paired flat removal is heuristic.','2022-2025 is research-contaminated exploratory data, not pristine OOS.','No verified FundedNext actual fees/swaps or challenge-account equity path.']}
    if proceed:
        fw=period_trades(trades,*PERIODS['forward_2022_2025'])
        annual={}
        for y in range(2022,2026): annual[str(y)]={str(c):summarize(period_trades(fw,f'{y}-01-01',f'{y+1}-01-01'),c) for c in EXTRA_COSTS}
        boot=weekly_bootstrap(fw,1.0)
        fg={'forward_trades_ge_100':summarize(fw,1.0)['trades']>=100,
          'forward_PF_plus1_ge_1p10':summarize(fw,1.0)['PF'] is not None and summarize(fw,1.0)['PF']>=1.10,
          'forward_PF_plus2_ge_1p05':summarize(fw,2.0)['PF'] is not None and summarize(fw,2.0)['PF']>=1.05,
          'every_year_with_10plus_trades_PF_ge_1':all(v['1.0']['PF'] is not None and v['1.0']['PF']>=1 for v in annual.values() if v['1.0']['trades']>=10),
          'weekly_bootstrap_lower_bound_gt_zero':boot['ci95_mean_weekly_net_pips'][0]>0}
        result.update({'stage':'EXPLORATORY_FORWARD_SCREEN_COMPLETE','forward_cost_stress':{str(c):summarize(fw,c) for c in EXTRA_COSTS},'annual_forward_cost_stress':annual,'weekly_bootstrap_plus1pip':boot,'forward_gates':fg,'verdict':'SCREEN PASS — NOT FUNDED-READY' if all(fg.values()) else 'GAGAL'})
        pd.DataFrame(fw).to_csv(out/'R282_forward_trades.csv',index=False)
    result['all_closed_trades_count']=len(trades)
    pd.DataFrame(trades).to_csv(out/'R282_all_closed_trades.csv',index=False)
    with open(out/'R282_results.json','w') as f: json.dump(result,f,indent=2,allow_nan=False)
    print(json.dumps({'events':event_diag,'execution':exec_diag,'cost_stress':costs,'gates':gates,'forward_authorized':proceed,'verdict':result['verdict']},indent=2,allow_nan=False))
if __name__=='__main__': main()
