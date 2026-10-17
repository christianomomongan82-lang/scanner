#!/usr/bin/env python3
"""Reproduce the locked R284 discovery/validation screen from extracted M5 BID CSV.gz inputs."""
import argparse, hashlib, json, pickle
from collections import defaultdict
from pathlib import Path
import numpy as np
import pandas as pd

ET='America/New_York'
FILES={'USA500':'usa500idxusd_m5.csv.gz','USATECH':'usatechidxusd_m5.csv.gz','USA30':'usa30idxusd_m5.csv.gz','USSC2000':'ussc2000idxusd_m5.csv.gz'}
COSTS=(1,2,4)
ARTIFACTS={'USA500':11709864394,'USATECH':11710370389,'USA30':11710730507,'USSC2000':11710111254}
ZIP_SHA={'USA500':'21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac','USATECH':'91c7d44b0487e98eeea021712528910475e626bf433220a007629f3005fc66ad','USA30':'53a54804f0584c69d52f41af08534e00effea66e7cc31872ae0438e7907e0fe6','USSC2000':'52216f5623a974dfaa0fb19e3cb28e2b2db589f1c07cef5cc8e5e2b383638872'}

def load_symbol(path,symbol,cache_dir):
    cp=cache_dir/f'{symbol}.pkl'
    if cp.exists():
        with cp.open('rb') as f:return pickle.load(f)
    df=pd.read_csv(path,compression='gzip')
    required=['timestamp','open','high','low','close']
    if any(c not in df.columns for c in required):raise ValueError(f'{symbol}: missing OHLC columns')
    if df.timestamp.duplicated().any():raise ValueError(f'{symbol}: duplicate timestamps')
    df=df.sort_values('timestamp',kind='stable').reset_index(drop=True)
    df['valid']=df[required].notna().all(axis=1)&(df.open>0)&(df.high>0)&(df.low>0)&(df.close>0)&(df.high>=df[['open','close','low']].max(axis=1))&(df.low<=df[['open','close','high']].min(axis=1))
    df['dt']=pd.to_datetime(df.timestamp,unit='ms',utc=True).dt.tz_convert(ET)
    df['flat']=(df.open==df.high)&(df.high==df.low)&(df.low==df.close)&(df.close==df.close.shift(1))
    df['day']=df.dt.dt.date; mins=df.dt.dt.hour*60+df.dt.dt.minute
    w=df[(df.dt.dt.dayofweek<5)&(mins>=600)&(mins<=955)]
    accepted=[]
    for day,g in w.groupby('day',sort=True):
        g=g.sort_values('timestamp'); midnight=pd.Timestamp(str(day)).tz_localize(ET)
        expected=pd.date_range(midnight+pd.Timedelta(hours=10),midnight+pd.Timedelta(hours=15,minutes=55),freq='5min')
        if len(g)!=72 or not pd.DatetimeIndex(g.dt).equals(expected):continue
        if not g.valid.all() or g.flat.any():continue
        sm=(g.dt.dt.hour*60+g.dt.dt.minute)<=715
        sig=g[sm]
        if len(sig)!=24:continue
        op=float(sig.iloc[0].open); cl=float(sig.iloc[-1].close); hi=float(sig.high.max()); lo=float(sig.low.min()); move=cl/op-1; dist=hi-lo
        em=g.index[(g.dt.dt.hour*60+g.dt.dt.minute)==725]
        if len(em)!=1 or not np.isfinite(move) or not np.isfinite(dist) or dist<=0:continue
        accepted.append({'symbol':symbol,'date':str(day),'year':int(str(day)[:4]),'move':move,'abs_move':abs(move),'direction':1 if move>0 else (-1 if move<0 else 0),'stop_dist':dist,'entry_idx':int(em[0]),'rows':g.reset_index(drop=True)})
    return accepted

def streams(sessions,thresholds):
    by=defaultdict(list)
    for sym,ss in sessions.items():
        for s in ss:
            q=thresholds[sym]; by[s['date']].append({**s,'q75':q,'strength':s['abs_move']/q})
    parent=[];child=[]
    for date,items in sorted(by.items()):
        if len(items)<3:continue
        s=sorted(items,key=lambda z:(-z['strength'],z['symbol']))[0]
        parent.append(s)
        if s['strength']>=1:child.append(s)
    return parent,child

def trade(s,cost):
    if not s['direction']:return None
    g=s.get('rows',s.get('session_rows')); t=g.dt_et if 'dt_et' in g.columns else g.dt; m=t.dt.hour*60+t.dt.minute
    en=int(np.flatnonzero(m.to_numpy()==725)[0]); flat=int(np.flatnonzero(m.to_numpy()==955)[0])
    entry=float(g.iloc[en].open); d=int(s['direction']); dist=float(s['stop_dist']); stop=entry-d*dist; target=entry+d*1.5*dist
    xp=None; reason=None; xt=None
    for i in range(en,flat):
        r=g.iloc[i]; o,h,l=float(r.open),float(r.high),float(r.low)
        if d>0:
            if o<=stop:xp,reason=o,'STOP_GAP'
            elif o>=target:xp,reason=target,'TARGET_GAP_CONSERVATIVE'
            elif l<=stop and h>=target:xp,reason=stop,'STOP_FIRST_BOTH_TOUCHED'
            elif l<=stop:xp,reason=stop,'STOP'
            elif h>=target:xp,reason=target,'TARGET'
        else:
            if o>=stop:xp,reason=o,'STOP_GAP'
            elif o<=target:xp,reason=target,'TARGET_GAP_CONSERVATIVE'
            elif h>=stop and l<=target:xp,reason=stop,'STOP_FIRST_BOTH_TOUCHED'
            elif h>=stop:xp,reason=stop,'STOP'
            elif l<=target:xp,reason=target,'TARGET'
        if xp is not None:xt=(r.dt_et if 'dt_et' in r.index else r.dt).isoformat();break
    if xp is None: xp=float(g.iloc[flat].open); reason='FORCE_FLAT_1555_OPEN';xt=(g.iloc[flat].dt_et if 'dt_et' in g.columns else g.iloc[flat].dt).isoformat()
    gross=d*(xp-entry)/dist; cost_r=entry*cost/10000/dist
    return {'stream':None,'date':s['date'],'year':s['year'],'symbol':s['symbol'],'net_r':gross-cost_r,'exit_reason':reason,'cost_bps_round_trip':cost}

def summ(ts):
    a=np.array([x['net_r'] for x in ts],float); w=a[a>0];l=a[a<0]
    eq=np.cumsum(a); dd=np.maximum.accumulate(np.r_[0.,eq])[1:]-eq
    return {'trades':int(len(a)),'pf':float(w.sum()/abs(l.sum())) if len(l) and abs(l.sum()) else None,'net_r':float(a.sum()),'max_dd_r':float(dd.max()) if len(dd) else 0.}

def main():
    p=argparse.ArgumentParser();p.add_argument('--data-dir',required=True);p.add_argument('--cache-dir');p.add_argument('--out',required=True);a=p.parse_args()
    data=Path(a.data_dir); cache=Path(a.cache_dir) if a.cache_dir else data/'cache';cache.mkdir(parents=True,exist_ok=True)
    ss={sym:load_symbol(data/fname,sym,cache) for sym,fname in FILES.items()}
    q={sym:float(np.quantile([x['abs_move'] for x in v if 2017<=x['year']<=2020 and x['abs_move']>0],.75,method='linear')) for sym,v in ss.items()}
    parent,child=streams(ss,q); rows={'parent':[],'child':[]}
    for name,stream in [('parent',parent),('child',child)]:
        for s in stream:
            if 2017<=s['year']<=2021:
                for c in COSTS:
                    t=trade(s,c)
                    if t:t['stream']=name;rows[name].append(t)
    metrics={}
    for name in rows:
        metrics[name]={}
        for seg,lo,hi in [('discovery',2017,2020),('validation',2021,2021)]:
            metrics[name][seg]={str(c)+'bp':summ([t for t in rows[name] if lo<=t['year']<=hi and t['cost_bps_round_trip']==c]) for c in COSTS}
    years={str(y):summ([t for t in rows['child'] if t['year']==y and t['cost_bps_round_trip']==2]) for y in range(2017,2022)}
    out={'candidate_id':'R284_LATE_MORNING_CROSS_SECTIONAL_CONTINUATION','thresholds_q75':q,'metrics':metrics,'child_annual_at_2bp':years,'forward_outcomes_calculated':False,'2026_outcomes_calculated':False}
    Path(a.out).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':main()
