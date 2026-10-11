#!/usr/bin/env python3
"""R217 rule mirror: H1 BID time-series momentum with a raw-price directional-efficiency gate.
The exact audited local runner and full ledgers are in r217_local_execution_bundle.zip.
"""
from pathlib import Path
import argparse
import numpy as np
import pandas as pd

SYMS=['usa500idxusd','usatechidxusd','usa30idxusd','ussc2000idxusd','deuidxeur','gbridxgbp','fraidxeur','eusidxeur','ausidxaud','jpnidxjpy']
LABELS={'usa500idxusd':'US500','usatechidxusd':'USTech100','usa30idxusd':'US30','ussc2000idxusd':'USSmallCap2000','deuidxeur':'Germany40','gbridxgbp':'FTSE100','fraidxeur':'France40','eusidxeur':'EU50','ausidxaud':'Australia200','jpnidxjpy':'Japan225'}
H=3600000; LOOKBACK=24; ER_MIN=.35; RET_MIN=.0025; HOLD=4
D0=pd.Timestamp('2017-01-01T00:00:00Z'); D1=pd.Timestamp('2022-01-01T00:00:00Z')
F0=pd.Timestamp('2022-01-01T00:00:00Z'); F1=pd.Timestamp('2026-01-01T00:00:00Z')
O0=pd.Timestamp('2026-01-01T00:00:00Z'); O1=pd.Timestamp('2026-10-10T00:00:00Z')

def load(base,s):
    d=pd.read_csv(base/f'{s}_h1.csv',usecols=['timestamp','open','high','low','close'])
    ts=d.timestamp.to_numpy(np.int64); o=d[['open','high','low','close']].to_numpy(float)
    flat=(o[:,0]==o[:,1])&(o[:,1]==o[:,2])&(o[:,2]==o[:,3])
    assert not d.timestamp.duplicated().any()
    assert np.isfinite(o).all()
    assert np.all(o[:,1]>=np.maximum(o[:,0],o[:,3])) and np.all(o[:,2]<=np.minimum(o[:,0],o[:,3])) and np.all(o[:,1]>=o[:,2])
    assert np.all(np.diff(ts)%H==0)
    return d,flat

def make_features(d,flat):
    ts=d.timestamp.to_numpy(np.int64); close=d.close.to_numpy(float); n=len(d)
    contig=np.r_[False,np.diff(ts)==H]
    exact=pd.Series(contig.astype(np.int8)).rolling(LOOKBACK,min_periods=LOOKBACK).sum().to_numpy()==LOOKBACK
    logc=np.log(close); diff=np.r_[np.nan,np.diff(logc)]
    path=pd.Series(np.abs(diff)).rolling(LOOKBACK,min_periods=LOOKBACK).sum().to_numpy()
    ret=close/np.roll(close,LOOKBACK)-1; ret[:LOOKBACK]=np.nan
    er=np.abs(logc-np.roll(logc,LOOKBACK))/path; er[:LOOKBACK]=np.nan
    ok=exact&np.isfinite(ret)&np.isfinite(er)&(path>0)&(close>0)
    ret[~ok]=np.nan; er[~ok]=np.nan
    schedule=((ts+H)%(4*H)==0)&(~flat)
    return ts,d.open.to_numpy(float),flat,ret,er,schedule

def pf(x):
    x=np.asarray(x,float); x=x[np.isfinite(x)]
    loss=-x[x<0].sum()
    return None if not len(x) or loss<=0 else float(x[x>0].sum()/loss)

def run(d,flat,features,s,start,end):
    ts,op,flat,ret,er,schedule=features
    a=int(start.timestamp()*1000); b=int(end.timestamp()*1000); trades=[]; busy=-1
    for i in np.flatnonzero(schedule):
        j=i+1
        if j>=len(ts): continue
        et=int(ts[j])
        if et<a or et>=b: continue
        if et!=int(ts[i])+H or not np.isfinite(ret[i]) or not np.isfinite(er[i]): continue
        if abs(ret[i])<RET_MIN or er[i]<ER_MIN or flat[j] or et<busy: continue
        due=et+HOLD*H; k=int(np.searchsorted(ts,due,side='left'))
        while k<len(ts) and (ts[k]<due or flat[k]): k+=1
        if k>=len(ts) or ts[k]>=b: continue
        xt=int(ts[k]); busy=xt
        direction=1 if ret[i]>0 else -1; entry=float(op[j]); exitp=float(op[k])
        gross=direction*(exitp/entry-1)*10000
        q={'symbol':s,'label':LABELS[s],'signal_bar_timestamp_ms':int(ts[i]),'signal_close_utc':pd.to_datetime(ts[i]+H,unit='ms',utc=True).isoformat(),
           'signal_return_24h_pct':float(ret[i]*100),'directional_efficiency':float(er[i]),'direction':direction,'side':'LONG' if direction>0 else 'SHORT',
           'entry_timestamp_ms':et,'entry_utc':pd.to_datetime(et,unit='ms',utc=True).isoformat(),'entry_open':entry,'scheduled_exit_timestamp_ms':due,
           'exit_timestamp_ms':xt,'exit_utc':pd.to_datetime(xt,unit='ms',utc=True).isoformat(),'holding_hours':(xt-et)/H,'exit_open':exitp,'gross_bps':gross,'closed':True}
        q['net_1bps']=gross-1; q['net_2bps']=gross-2; trades.append(q)
    return pd.DataFrame(trades)

def summary(x,p):
    return {'period':p,'closed_trades':len(x),'mean_net_1bps':float(x.net_1bps.mean()) if len(x) else None,'mean_net_2bps':float(x.net_2bps.mean()) if len(x) else None,
            'pf_1bps':pf(x.net_1bps) if len(x) else None,'pf_2bps':pf(x.net_2bps) if len(x) else None}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--data-dir',default='/mnt/data/r205_snapshot');ap.add_argument('--out-dir',default='r217-results');args=ap.parse_args()
    base=Path(args.data_dir);out=Path(args.out_dir);out.mkdir(parents=True,exist_ok=True); by={}; ledgers=[]; rows=[]
    for s in SYMS:
        d,fl=load(base,s); f=make_features(d,fl)
        # True feature prefix test: no values may depend on rows beyond a 2020 cutoff.
        cut=int(pd.Timestamp('2020-01-01T00:00:00Z').timestamp()*1000); pref=d[d.timestamp<cut].reset_index(drop=True)
        _,flp=load_frame(pref); fp=make_features(pref,flp)
        sel=d.timestamp.to_numpy(np.int64)<cut
        assert np.array_equal(np.isnan(f[3][sel]),np.isnan(fp[3]))
        assert np.allclose(f[3][sel][np.isfinite(f[3][sel])],fp[3][np.isfinite(fp[3])],rtol=0,atol=1e-12)
        assert np.array_equal(np.isnan(f[4][sel]),np.isnan(fp[4]))
        assert np.allclose(f[4][sel][np.isfinite(f[4][sel])],fp[4][np.isfinite(fp[4])],rtol=0,atol=1e-12)
        x=run(d,fl,f,s,D0,D1); x.to_csv(out/f'discovery_{s}_ledger.csv',index=False)
        r=summary(x,'discovery_2017_2021'); r.update({'symbol':s,'label':LABELS[s],'eligible':len(x)>=100 and pf(x.net_2bps) is not None and pf(x.net_2bps)>=1})
        rows.append(r); by[s]=(d,fl,f,x)
    pd.DataFrame(rows).to_csv(out/'discovery_selection.csv',index=False)
    valid=[r for r in rows if r['eligible']]
    if not valid:
        print('REJECT_NO_DISCOVERY_ELIGIBLE_CANDIDATE'); return
    valid.sort(key=lambda r:(-(r['pf_2bps'] or -1),-r['closed_trades']))
    chosen=valid[0]['symbol']; d,fl,f,disc=by[chosen]
    fw=run(d,fl,f,chosen,F0,F1); oo=run(d,fl,f,chosen,O0,O1)
    fw.to_csv(out/'selected_forward_ledger.csv',index=False); oo.to_csv(out/'selected_oos_ledger.csv',index=False)
    sums=[summary(disc,'discovery_2017_2021'),summary(fw,'forward_2022_2025'),summary(oo,'oos_2026_cutoff')]
    pd.DataFrame(sums).to_csv(out/'period_summaries.csv',index=False)
    print('selected',chosen,'summaries',sums)
    if not (sums[1]['closed_trades']>=30 and (sums[1]['pf_1bps'] or 0)>=1.15 and (sums[1]['pf_2bps'] or 0)>=1.15): print('REJECT_FORWARD_GATE_FAILED')

def load_frame(d):
    o=d[['open','high','low','close']].to_numpy(float)
    flat=(o[:,0]==o[:,1])&(o[:,1]==o[:,2])&(o[:,2]==o[:,3])
    return d,flat

if __name__=='__main__': main()
