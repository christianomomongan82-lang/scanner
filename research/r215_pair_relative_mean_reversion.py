#!/usr/bin/env python3
"""R215 discovery-stage mirror. Raw M5 BID OHLC only; no ask reconstruction or ffill.
The exact full local engine/audit package is the R215 local execution ZIP.
"""
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

BAR_MS=300_000; H=12; WINDOW=144; ENTRY=2.0; EXIT=.25; STOP=3.5; MAX_HOLD=144
COSTS=(1.0,2.0)
PAIRS=[('usa500idxusd','usatechidxusd','US500 vs US Tech 100'),
       ('usa500idxusd','usa30idxusd','US500 vs US30'),
       ('usa500idxusd','ussc2000idxusd','US500 vs US Small Cap 2000')]
START=pd.Timestamp('2017-01-01T00:00:00Z'); END=pd.Timestamp('2022-01-01T00:00:00Z')

def readpair(base,a,b):
    use=['timestamp','open','high','low','close']
    x=pd.read_csv(base/f'{a}_m5.csv',usecols=use).rename(columns={k:f'{a}_{k}' for k in use[1:]})
    y=pd.read_csv(base/f'{b}_m5.csv',usecols=use).rename(columns={k:f'{b}_{k}' for k in use[1:]})
    d=x.merge(y,on='timestamp',how='inner',validate='one_to_one',sort=True).reset_index(drop=True)
    d['time']=pd.to_datetime(d.timestamp,unit='ms',utc=True)
    return d

def features(d,a,b):
    o=d[['timestamp','time',f'{a}_open',f'{a}_high',f'{a}_low',f'{a}_close',f'{b}_open',f'{b}_high',f'{b}_low',f'{b}_close']].copy()
    af=(o[f'{a}_open']==o[f'{a}_high'])&(o[f'{a}_high']==o[f'{a}_low'])&(o[f'{a}_low']==o[f'{a}_close'])
    bf=(o[f'{b}_open']==o[f'{b}_high'])&(o[f'{b}_high']==o[f'{b}_low'])&(o[f'{b}_low']==o[f'{b}_close'])
    ts=o.timestamp.to_numpy(np.int64); active=(~af&~bf).to_numpy(bool)
    contiguous=np.r_[False,np.diff(ts)==BAR_MS]; valid=active&contiguous
    lv=pd.Series(valid.astype(np.int8)).rolling(H+1,min_periods=H+1).sum().eq(H+1)
    lr=(np.log(o[f'{a}_close'].astype(float))-np.log(o[f'{a}_close'].astype(float).shift(H)))-\
       (np.log(o[f'{b}_close'].astype(float))-np.log(o[f'{b}_close'].astype(float).shift(H)))
    r=lr.where(lv); mean=r.rolling(WINDOW,min_periods=WINDOW).mean(); sd=r.rolling(WINDOW,min_periods=WINDOW).std(ddof=0)
    o['z']=((r-mean)/sd.replace(0,np.nan)).replace([np.inf,-np.inf],np.nan)
    o['active']=active; o['oa']=o[f'{a}_open']; o['ob']=o[f'{b}_open']
    return o

def pf(x):
    x=np.asarray(x,float); win=x[x>0].sum(); loss=-x[x<0].sum()
    return None if len(x)==0 or loss==0 else float(win/loss)

def simulate(f):
    start=int(START.timestamp()*1000); end=int(END.timestamp()*1000); ts=f.timestamp.to_numpy(np.int64)
    z=f.z.to_numpy(float); active=f.active.to_numpy(bool); oa=f.oa.to_numpy(float); ob=f.ob.to_numpy(float)
    records=[]; state=None; pending=None
    i0=max(0,int(np.searchsorted(ts,start))-1); i1=min(len(f),int(np.searchsorted(ts,end))+1)
    for i in range(i0,i1):
        t=int(ts[i])
        if t>=end: break
        if pending is not None:
            q=pending; pending=None
            if t==q['t']+BAR_MS and t>=start and active[i] and t<end:
                s=q['sign']; state={'entry_i':i,'entry_ts':t,'entry_a':float(oa[i]),'entry_b':float(ob[i]),'sa':-s,'sb':s,'z0':q['z'],'sign':s,'pending_exit':False,'reason':None,'exit_signal_ts':None}
        if state is not None and state['pending_exit']:
            if t>state['exit_signal_ts'] and active[i] and t<end:
                gross=.5*(state['sa']*(oa[i]/state['entry_a']-1)+state['sb']*(ob[i]/state['entry_b']-1))*10000
                rec={**state,'exit_i':i,'exit_ts':t,'gross_bps':float(gross),'reason':state['reason'],'closed':True}
                for c in COSTS: rec[f'net_{int(c)}bps']=float(gross-c)
                records.append(rec); state=None
        if state is not None and not state['pending_exit']:
            elapsed=(t-state['entry_ts'])/BAR_MS; zi=z[i]; reason=None
            if elapsed>=MAX_HOLD: reason='max_hold_12h'
            elif np.isfinite(zi) and state['sign']*zi<=EXIT: reason='mean_reversion_0.25z'
            elif np.isfinite(zi) and state['sign']*zi>=STOP: reason='divergence_stop_3.5z'
            if reason:
                state['pending_exit']=True; state['reason']=reason; state['exit_signal_ts']=t
        if state is None and pending is None and t>=start and t+BAR_MS<end and i+1<len(f):
            zi=z[i]; zp=z[i-1] if i>0 and ts[i]-ts[i-1]==BAR_MS else np.nan
            if np.isfinite(zi) and np.isfinite(zp) and abs(zp)<ENTRY and abs(zi)>=ENTRY:
                pending={'t':t,'z':float(zi),'sign':1 if zi>0 else -1}
    if state is not None: records.append({**state,'closed':False,'reason':'censored_at_period_end'})
    out=pd.DataFrame(records); closed=out[out.closed==True] if len(out) else out
    return out,{'entries':len(out),'closed':len(closed),'censored':len(out)-len(closed),
                'pf_1bps':pf(closed.net_1bps) if len(closed) else None,'pf_2bps':pf(closed.net_2bps) if len(closed) else None}

def main():
    p=argparse.ArgumentParser(); p.add_argument('--data-dir',default='/mnt/data/r205_snapshot'); p.add_argument('--out-dir',default='r215-discovery-results'); args=p.parse_args()
    base=Path(args.data_dir); outdir=Path(args.out_dir); outdir.mkdir(parents=True,exist_ok=True)
    rows=[]
    for a,b,label in PAIRS:
        d=readpair(base,a,b); f=features(d,a,b)
        # Truncation gate: the prefix is identical whether built alone or within the full series.
        n=min(160_000,len(d)); zfull=f.z.iloc[:n].to_numpy(); zprefix=features(d.iloc[:n].copy(),a,b).z.to_numpy()
        causal=bool(np.array_equal(np.isnan(zfull),np.isnan(zprefix)) and np.allclose(zfull[np.isfinite(zfull)],zprefix[np.isfinite(zprefix)],rtol=0,atol=1e-13))
        if not causal: raise RuntimeError(f'causal prefix gate failed for {label}')
        ledger,stats=simulate(f); ledger.to_csv(outdir/f'discovery_{a}_{b}_ledger.csv',index=False)
        rows.append({'pair':label,'a_symbol':a,'b_symbol':b,'discovery_entries':stats['entries'],'discovery_closed':stats['closed'],'discovery_censored':stats['censored'],
                     'discovery_pf_1bps':stats['pf_1bps'],'discovery_pf_2bps':stats['pf_2bps'],'causality_prefix_gate':causal,'paired_rows':len(f),'feature_valid_rows':int(f.z.notna().sum()),
                     'paired_flat_or_inactive_rows':int((~f.active).sum()),'min_time':f.time.min().isoformat(),'max_time':f.time.max().isoformat()})
        print(label,stats,flush=True)
    eligible=[r for r in rows if r['discovery_closed']>=30 and r['discovery_pf_2bps'] is not None and r['discovery_pf_2bps']>=1]
    pd.DataFrame(rows).to_csv(outdir/'discovery_selection.csv',index=False)
    if eligible:
        eligible.sort(key=lambda r:(r['discovery_closed'],-r['discovery_pf_2bps']))
        print('Eligible locked selection:',eligible[0]['pair'])
    else:
        print('REJECT: no discovery-eligible pair. Do not run forward/OOS or tune thresholds.')
if __name__=='__main__': main()
