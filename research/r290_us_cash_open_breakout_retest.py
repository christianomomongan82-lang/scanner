#!/usr/bin/env python3
"""R290 pre-registered US opening-range breakout-retest test; later PnL is gated."""
from __future__ import annotations
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
TZ='America/New_York'; COSTS=(2,4,6); DISC=(2016,2020); VAL=2021
FILES={'USA500':'usa500idxusd_m5.csv.gz','USATECH':'usatechidxusd_m5.csv.gz'}
HASH={'USA500':'df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee','USATECH':'82b06c38f66cd1387097691baac1d45c9463b6540eea9dfe28a894d85e122f7c'}

def load_sessions(path,sym):
    d=pd.read_csv(path,compression='gzip')
    if d.columns.tolist()!=['timestamp','open','high','low','close'] or d.timestamp.duplicated().any():
        raise ValueError(f'{sym}: unexpected schema or duplicate timestamps')
    d=d.sort_values('timestamp',kind='stable').reset_index(drop=True)
    d['dt']=pd.to_datetime(d.timestamp,unit='ms',utc=True).dt.tz_convert(TZ)
    d['date']=d.dt.dt.strftime('%Y-%m-%d'); d['minute']=d.dt.dt.hour*60+d.dt.dt.minute
    o=['open','high','low','close']
    d['valid']=d[o].notna().all(axis=1)&(d[o]>0).all(axis=1)&(d.high>=d[['open','close','low']].max(axis=1))&(d.low<=d[['open','close','high']].min(axis=1))
    d['flat']=(d.open==d.high)&(d.high==d.low)&(d.low==d.close)&(d.close==d.close.shift(1))
    d=d[(d.dt.dt.dayofweek<5)&d.minute.between(570,955)&(d.date>='2016-01-01')&(d.date<='2026-12-31')].copy()
    sessions,bars,audit={},{},[]
    for day,g0 in d.groupby('date',sort=True):
        g=g0.sort_values('timestamp').reset_index(drop=True); mid=pd.Timestamp(day).tz_localize(TZ)
        exp=pd.date_range(mid+pd.Timedelta(hours=9,minutes=30),mid+pd.Timedelta(hours=15,minutes=55),freq='5min')
        reasons=[]
        if len(g)!=78: reasons.append('bar_count_not_78')
        elif not pd.DatetimeIndex(g.dt).equals(exp) or g.dt.duplicated().any(): reasons.append('timestamp_sequence_invalid')
        if not g.valid.all(): reasons.append('invalid_ohlc')
        if g.flat.any(): reasons.append('repeated_flat_candidate')
        ok=not reasons
        audit.append({'symbol':sym,'date':day,'year':int(day[:4]),'bar_count':int(len(g)),'flat_candidate_count':int(g.flat.sum()),'eligible':ok,'reason':'|'.join(reasons)})
        if ok: sessions[day]={'symbol':sym,'date':day,'year':int(day[:4])}; bars[day]=g
    raw_ts=pd.to_datetime(pd.read_csv(path,compression='gzip',usecols=['timestamp']).timestamp,unit='ms',utc=True)
    return sessions,bars,audit,raw_ts.min().isoformat(),raw_ts.max().isoformat()

def find_candidate(day,g,sym):
    mins=g.minute.to_numpy(); op=g.open.to_numpy(float); hi=g.high.to_numpy(float); lo=g.low.to_numpy(float); cl=g.close.to_numpy(float)
    by={int(m):int(i) for i,m in enumerate(mins)}
    if not all(m in by for m in (570,575,580,585,660,715,955)): return None
    ori=[by[570],by[575],by[580]]; orh=float(hi[ori].max()); orl=float(lo[ori].min()); width=orh-orl
    if not np.isfinite(width) or width<=0:return None
    breakout_i=None; sign=0; boundary=0.0
    for i in range(by[585],by[660]+1):
        if cl[i]>orh: breakout_i=i; sign=1; boundary=orh; break
        if cl[i]<orl: breakout_i=i; sign=-1; boundary=orl; break
    if breakout_i is None:return None
    excursion=abs(float(cl[breakout_i])-boundary)/width
    retest_i=None
    for i in range(breakout_i+1,by[715]+1):
        if sign>0 and lo[i]<=orh and cl[i]>orh: retest_i=i; break
        if sign<0 and hi[i]>=orl and cl[i]<orl: retest_i=i; break
    if retest_i is None or retest_i+1>=len(g):return None
    entry_i=retest_i+1; entry=float(op[entry_i]); stop=orl if sign>0 else orh
    if (sign>0 and entry<=orh) or (sign<0 and entry>=orl):return None
    risk=sign*(entry-stop)
    if not np.isfinite(risk) or risk<=0:return None
    return {'date':day,'year':int(day[:4]),'symbol':sym,'direction_sign':int(sign),'or_high':orh,'or_low':orl,'or_width':width,
      'breakout_ts':g.iloc[breakout_i]['dt'].isoformat(),'breakout_minute':int(mins[breakout_i]),'breakout_close':float(cl[breakout_i]),
      'breakout_excursion_over_or':float(excursion),'retest_ts':g.iloc[retest_i]['dt'].isoformat(),'retest_minute':int(mins[retest_i]),
      'entry_ts':g.iloc[entry_i]['dt'].isoformat(),'entry_minute':int(mins[entry_i]),'entry_price_bid':entry,'stop_price':float(stop),'risk_points':float(risk),
      'target_price':float(entry+sign*1.5*risk),'entry_index':int(entry_i),'or_range_width_points':float(width)}

def simulate(c,bars):
    g=bars[c['symbol']][c['date']]; sign=c['direction_sign']; entry=c['entry_price_bid']; stop=c['stop_price']; target=c['target_price']; risk=c['risk_points']; ix=c['entry_index']
    ex=None; reason=None; exts=None; extkind=None
    for j in range(ix,len(g)):
        z=g.iloc[j]; op,hi,lo=map(float,(z.open,z.high,z.low))
        if sign>0:
            if op<=stop: ex,reason=op,'stop_gap_open'
            elif op>=target: ex,reason=op,'target_gap_open'
            else:
                sh=lo<=stop; th=hi>=target
                if sh: ex,reason=stop,'stop_both_touched' if th else 'stop'
                elif th: ex,reason=target,'target'
        else:
            if op>=stop: ex,reason=op,'stop_gap_open'
            elif op<=target: ex,reason=op,'target_gap_open'
            else:
                sh=hi>=stop; th=lo<=target
                if sh: ex,reason=stop,'stop_both_touched' if th else 'stop'
                elif th: ex,reason=target,'target'
        if ex is not None: exts=z['dt'].isoformat(); extkind='triggered_within_m5_bar_approx_bar_start'; break
    if ex is None:
        z=g.iloc[-1]; ex=float(z.close); reason='session_close'; exts=(z['dt']+pd.Timedelta(minutes=5)).isoformat(); extkind='session_bar_close'
    signed=sign*(ex-entry); gross_r=signed/risk; gross_bps=signed/entry*10000
    r={k:v for k,v in c.items() if k not in ('entry_index',)}
    r.update({'exit_ts':exts,'exit_ts_kind':extkind,'exit_price_bid':float(ex),'exit_reason':reason,'gross_r':float(gross_r),'gross_bps':float(gross_bps),'holding_minutes':(pd.Timestamp(exts)-pd.Timestamp(c['entry_ts'])).total_seconds()/60})
    for cost in COSTS:
        r[f'net_r_{cost}bp']=float(gross_r-(entry*cost/10000)/risk); r[f'net_bps_{cost}bp']=float(gross_bps-cost)
    return r

def summary(ts,cost):
    if not ts:return {'trades':0,'pf_r':None,'net_r':0.0,'mean_r':None,'median_r':None,'max_drawdown_r':0.0,'win_rate_pct':None,'net_bps':0.0,'pf_bps':None}
    x=np.asarray([t[f'net_r_{cost}bp'] for t in ts]); b=np.asarray([t[f'net_bps_{cost}bp'] for t in ts]); pos=x[x>0].sum(); neg=-x[x<0].sum(); eq=np.cumsum(x); dd=np.maximum.accumulate(np.r_[0.,eq])[1:]-eq
    return {'trades':int(len(x)),'pf_r':float(pos/neg) if neg else None,'net_r':float(x.sum()),'mean_r':float(x.mean()),'median_r':float(np.median(x)),'max_drawdown_r':float(dd.max()),'win_rate_pct':float((x>0).mean()*100),'net_bps':float(b.sum()),'pf_bps':float(b[b>0].sum()/-b[b<0].sum()) if (b<0).any() else None,'mean_bps':float(b.mean()),'median_bps':float(np.median(b))}

def weekly(ts,year,cost=2):
    idx=pd.date_range(f'{year}-01-01',f'{year}-12-31',freq='W-MON'); sums={}
    for t in ts:
        d=pd.Timestamp(t['date']); mon=(d-pd.Timedelta(days=d.weekday())).normalize(); sums[mon]=sums.get(mon,0.)+t[f'net_r_{cost}bp']
    return np.asarray([sums.get(d.normalize(),0.) for d in idx if d.year==year])

def bootstrap(x):
    rng=np.random.default_rng(290); n=len(x); block=4; nb=int(np.ceil(n/block)); starts=rng.integers(0,n,size=(5000,nb)); samples=x[(starts[:,:,None]+np.arange(block)[None,None,:])%n].reshape(5000,-1)[:,:n]; means=samples.mean(axis=1)
    return {'mean_weekly_net_r':float(x.mean()),'ci95_low':float(np.quantile(means,.025)),'ci95_high':float(np.quantile(means,.975)),'weeks':int(n),'block_weeks':4,'replicates':5000,'seed':290}

def run(data_dir,out_dir):
    data_dir=Path(data_dir); out_dir=Path(out_dir); out_dir.mkdir(parents=True,exist_ok=True); sessions,bars,audits,sources={},{},[],{}
    for sym,filename in FILES.items():
        p=data_dir/filename; sha=hashlib.sha256(p.read_bytes()).hexdigest()
        if sha!=HASH[sym]:raise ValueError(f'{sym} SHA-256 mismatch: {sha}')
        ss,bb,aa,mn,mx=load_sessions(p,sym); sessions[sym]=ss; bars[sym]=bb; audits+=aa
        sources[sym]={'file':filename,'sha256_gz':sha,'bytes':p.stat().st_size,'eligible_sessions':len(ss),'source_first_utc':mn,'source_last_utc':mx}
    candidates=[]
    for sym in FILES:
        for day,g in bars[sym].items():
            c=find_candidate(day,g,sym)
            if c is not None:candidates.append(c)
    canddf=pd.DataFrame(candidates); accepted=[]
    if not canddf.empty:
        for day,g in canddf.groupby('date',sort=True):
            w=g.sort_values(['retest_minute','breakout_excursion_over_or','symbol'],ascending=[True,False,True],kind='stable').iloc[0].to_dict()
            accepted.append(w)
    signals=pd.DataFrame(accepted)
    hist=[simulate(c,bars) for c in accepted if 2016<=c['year']<=2021]
    metrics={}; annual={str(y):{f'{c}bp':summary([t for t in hist if t['year']==y],c) for c in COSTS} for y in range(2016,2022)}
    for label,lo,hi in [('discovery_2016_2020',2016,2020),('validation_2021',2021,2021)]:
        metrics[label]={}
        ts=[t for t in hist if lo<=t['year']<=hi]
        metrics[label]['breakout_retest_candidate']={f'{c}bp':summary(ts,c) for c in COSTS}
    d=metrics['discovery_2016_2020']['breakout_retest_candidate']; v=metrics['validation_2021']['breakout_retest_candidate']; pyears=sum(annual[str(y)]['2bp']['net_r']>0 for y in range(2016,2021))
    boot=bootstrap(weekly([t for t in hist if t['year']==2021],2021,2))
    gates={'discovery_trades_ge_300':d['2bp']['trades']>=300,'discovery_pf_r_2bp_ge_1_05':d['2bp']['pf_r'] is not None and d['2bp']['pf_r']>=1.05,'discovery_net_r_positive_2bp':d['2bp']['net_r']>0,'discovery_positive_years_ge_3_of_5':pyears>=3,'discovery_pf_r_4bp_ge_0_90':d['4bp']['pf_r'] is not None and d['4bp']['pf_r']>=.90,'validation_trades_ge_100':v['2bp']['trades']>=100,'validation_pf_r_2bp_ge_1_00':v['2bp']['pf_r'] is not None and v['2bp']['pf_r']>=1.0,'validation_net_r_positive_2bp':v['2bp']['net_r']>0,'validation_pf_r_6bp_ge_0_80':v['6bp']['pf_r'] is not None and v['6bp']['pf_r']>=.80,'validation_bootstrap_ci95_lower_gt_0':boot['ci95_low']>0}
    passed=all(gates.values()); later_metrics=None; later=[]
    if passed:
        later=[simulate(c,bars) for c in accepted if c['year']>=2022]
        later_metrics={}
        for label,lo,hi in [('exploratory_2022_2025',2022,2025),('later_check_2026',2026,2026)]:later_metrics[label]={f'{c}bp':summary([t for t in later if lo<=t['year']<=hi],c) for c in COSTS}
    alltrades=hist+later
    result={'candidate_id':'R290_US_CASH_OPEN_BREAKOUT_RETEST','preregistration_commit':'8476caf1c9953de446ac9713f24625a04b46d206','verdict':'LULUS_HISTORICAL_GATES' if passed else 'GAGAL','post_2021_pnl_calculated':bool(passed),'data':sources,'method':{'timezone':TZ,'opening_range':'09:30,09:35,09:40 M5 bars; high/low envelope','first_breakout':'first confirmed M5 close beyond OR boundary from 09:45 to 11:00','retest':'later bar must touch broken boundary and close back outside; confirmed by 12:00 close','entry':'next M5 bar open after retest close; skip if entry reopens inside the OR','stop':'opposite OR boundary','target_R':1.5,'max_positions':'one trade total across both instruments per US date','same_bar':'stop first','modeled_cost_bps':[2,4,6]},'coverage':{'eligible_sessions_by_symbol':{s:len(v) for s,v in sessions.items()},'raw_qualifying_retests_by_year':{str(y):int((canddf.year==y).sum()) for y in range(2016,2027)} if not canddf.empty else {},'selected_signals_by_year':{str(y):int((signals.year==y).sum()) for y in range(2016,2027)} if not signals.empty else {},'source_latest_utc':max(v['source_last_utc'] for v in sources.values())},'metrics':metrics,'annual_candidate':annual,'validation_weekly_net_r_bootstrap_2bp':boot,'gates':gates,'failed_gates':[k for k,v in gates.items() if not v],'later_metrics':later_metrics,'limitations':['M5 BID-only; added costs are assumptions rather than measured spreads/slippage','cash-open ORB parent R263 failed; this child uses retest confirmation before entry','2022–2025 is contaminated exploratory evidence if reached','no verified CFD point value/commission/swap model or funded equity path']}
    pd.DataFrame(audits).to_csv(out_dir/'R290_session_quality_audit.csv',index=False); canddf.to_csv(out_dir/'R290_candidate_retests.csv',index=False); signals.to_csv(out_dir/'R290_selected_signal_ledger.csv',index=False); pd.DataFrame(alltrades).to_csv(out_dir/'R290_trade_ledger.csv',index=False)
    (out_dir/'R290_results.json').write_text(json.dumps(result,indent=2,allow_nan=False)+'\n'); print(json.dumps(result,indent=2,allow_nan=False))
if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--data-dir',default='/mnt/data/r288data'); ap.add_argument('--out-dir',default='/mnt/data/R290_outputs'); a=ap.parse_args(); run(a.data_dir,a.out_dir)
