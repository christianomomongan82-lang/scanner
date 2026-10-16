#!/usr/bin/env python3
"""R281 locked EURUSD H1 compression-release replay. Local only; requires pandas/numpy."""
import argparse, hashlib, json, zipfile
from pathlib import Path
import numpy as np
import pandas as pd

PIP=0.0001; COSTS=(0.0,0.5,1.0,2.0); QS=(0.20,0.30); LOOKBACKS=(12,24); RRS=(1.5,2.0)
TRAIN=pd.Timestamp('2017-01-01',tz='UTC'); TRAIN_END=pd.Timestamp('2021-01-01',tz='UTC')
VAL=pd.Timestamp('2021-01-01',tz='UTC'); END=pd.Timestamp('2022-01-01',tz='UTC')
ARCHIVE_SHA='b5a06ed7df292a6add87d3ce519ee66189d940244651ab005f57519ee48a0d2e'

def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 return h.hexdigest()

def load(zip_path):
 with zipfile.ZipFile(zip_path) as z:
  manifest=json.loads(z.read('manifest.json'))
  def rd(side):
   with z.open(f'eurusd_{side}_M1_2016-2025.csv.gz') as f: d=pd.read_csv(f,compression='gzip')
   d['timestamp']=pd.to_numeric(d.timestamp).astype('int64')
   return d.sort_values('timestamp').drop_duplicates('timestamp',keep='last').set_index('timestamp')[['open','high','low','close']].astype(float)
  b0,a0=rd('bid'),rd('ask')
 common=b0.index.intersection(a0.index).sort_values(); b=b0.loc[common]; a=a0.loc[common]
 def bad(d): return ~((d.high>=d[['open','close']].max(axis=1))&(d.low<=d[['open','close']].min(axis=1))&(d.high>=d.low))
 valid=~(bad(b).to_numpy()|bad(a).to_numpy()); b=b.iloc[np.flatnonzero(valid)]; a=a.iloc[np.flatnonzero(valid)]
 ts=b.index.to_numpy(np.int64); bo,bh,bl,bc=(b[c].to_numpy(float) for c in ('open','high','low','close')); ao,ah,al,ac=(a[c].to_numpy(float) for c in ('open','high','low','close'))
 flatb=(bo==bh)&(bh==bl)&(bl==bc); flata=(ao==ah)&(ah==al)&(al==ac); onemin=np.r_[False,np.diff(ts)==60000]
 synth=flatb&flata&np.isclose(bo,np.r_[np.nan,bc[:-1]],rtol=0,atol=1e-12)&np.isclose(ao,np.r_[np.nan,ac[:-1]],rtol=0,atol=1e-12)&onemin
 b=b.iloc[np.flatnonzero(~synth)]; a=a.iloc[np.flatnonzero(~synth)]; ts=b.index.to_numpy(np.int64)
 m=pd.DataFrame({'ts':ts,'bo':b.open.to_numpy(float),'bh':b.high.to_numpy(float),'bl':b.low.to_numpy(float),'bc':b.close.to_numpy(float),'ao':a.open.to_numpy(float),'ah':a.high.to_numpy(float),'al':a.low.to_numpy(float),'ac':a.close.to_numpy(float)})
 m['hour']=m.ts//3600000
 ag=m.groupby('hour',sort=True).agg(n=('ts','size'),fst=('ts','first'),lst=('ts','last'),bo=('bo','first'),bh=('bh','max'),bl=('bl','min'),bc=('bc','last'),ao=('ao','first'),ah=('ah','max'),al=('al','min'),ac=('ac','last'))
 ix=ag.index.to_numpy(np.int64); ag=ag[(ag.n==60)&(ag.fst==ix*3600000)&(ag.lst==ix*3600000+3540000)].copy(); ag['ts']=ag.index.to_numpy(np.int64)*3600000; ag=ag.reset_index(drop=True)
 x={k:ag[k].to_numpy(float if k!='ts' else np.int64) for k in ('bo','bh','bl','bc','ao','ah','al','ac','ts')}
 spread=(x['ao']-x['bo'])/PIP
 if np.any(spread < -1e-9): raise ValueError('negative opening spread')
 audit={'source':'Dukascopy EURUSD M1 BID/ASK via dukascopy-node','archive_sha256':sha(zip_path),'expected_archive_sha256':ARCHIVE_SHA,'archive_sha_matches':sha(zip_path)==ARCHIVE_SHA,'manifest_status':manifest.get('status'),'requested_window_utc':manifest.get('requested_window_utc'),'raw_bid_rows':int(len(b0)),'raw_ask_rows':int(len(a0)),'candidate_synthetic_flat_rows_removed':int(synth.sum()),'paired_m1_rows_post_filter':int(len(m)),'complete_h1_bars':int(len(ag)),'complete_h1_start_utc':pd.to_datetime(x['ts'][0],unit='ms',utc=True).isoformat(),'complete_h1_end_utc':pd.to_datetime(x['ts'][-1],unit='ms',utc=True).isoformat(),'dropped_incomplete_or_missing_h1_groups':int(m.hour.nunique()-len(ag)),'median_open_spread_pips':float(np.median(spread)),'p95_open_spread_pips':float(np.quantile(spread,.95)),'flat_filter_caveat':'Collector used -fl; paired flat removal is heuristic. Complete H1 requires 60 sequential paired M1 rows; gaps are never filled.'}
 return x,audit

def replay(x, audit, out):
 ts=x['ts']; run=np.zeros(len(ts),np.int32)
 for i in range(1,len(ts)): run[i]=run[i-1]+1 if ts[i]-ts[i-1]==3600000 else 0
 r6=np.full(len(ts),np.nan)
 for i in range(6,len(ts)):
  if run[i-1]>=5 and ts[i]-ts[i-1]==3600000: r6[i]=np.max(x['bh'][i-6:i])-np.min(x['bl'][i-6:i])
 tr=(ts>=TRAIN.value//1000000)&(ts<TRAIN_END.value//1000000)&np.isfinite(r6)
 thresholds={str(q):float(np.quantile(r6[tr],q)) for q in QS}
 def pf(v):
  g=v[v>0].sum(); l=-v[v<0].sum()
  return float(g/l) if l>0 else (float('inf') if g>0 else None)
 def summ(t,c):
  v=np.array([z['gross_pips']-c for z in t],float); eq=np.cumsum(v)
  dd=float(np.max(np.maximum.accumulate(np.r_[0,eq])[1:]-eq)) if len(v) else 0.
  return {'trades':len(v),'PF':pf(v),'net_pips':float(v.sum()) if len(v) else 0.0,'mean_net_pips_per_trade':float(v.mean()) if len(v) else None,'max_drawdown_pips':dd}
 def period(t,lo,hi): return [z for z in t if lo<=pd.Timestamp(z['entry_utc'])<hi and pd.Timestamp(z['exit_utc'])<hi]
 results={}; cutoff=END.value//1000000
 for q in QS:
  comp=np.isfinite(r6)&(r6<=thresholds[str(q)])
  for lb in LOOKBACKS:
   raw=[]
   for i in range(lb,len(ts)):
    if run[i-1]<lb-1 or ts[i]-ts[i-1]!=3600000 or not comp[i]: continue
    lg=x['bc'][i]>np.max(x['bh'][i-lb:i]); sh=x['ac'][i]<np.min(x['al'][i-lb:i])
    if lg!=sh: raw.append((i,1 if lg else -1))
   for rr in RRS:
    key=f'Q{int(q*100):02d}_B{lb}_RR{rr:g}'; trades=[]; last_exit=-1; diag={'raw_signals':len(raw),'not_exact_next_hour':0,'entry_at_or_beyond_stop':0,'overlap_skipped':0,'censored_end':0}
    for i,direction in raw:
     if ts[i]>=cutoff: break
     if i+1>=len(ts) or ts[i+1]-ts[i]!=3600000: diag['not_exact_next_hour']+=1; continue
     e=i+1
     if ts[e]>=cutoff: diag['censored_end']+=1; continue
     if e<=last_exit: diag['overlap_skipped']+=1; continue
     entry=float(x['ao'][e] if direction==1 else x['bo'][e]); stop=float(x['bl'][i] if direction==1 else x['ah'][i]); risk=entry-stop if direction==1 else stop-entry
     if risk<=0: diag['entry_at_or_beyond_stop']+=1; continue
     target=entry+direction*rr*risk; timeout=e+24; xi=xp=why=None
     for j in range(e,min(e+24,len(ts))):
      if ts[j]>=cutoff: break
      if direction==1:
       if x['bo'][j]<=stop: xi,xp,why=j,float(x['bo'][j]),'STOP_GAP'; break
       if x['bo'][j]>=target: xi,xp,why=j,float(x['bo'][j]),'TARGET_GAP'; break
       st=x['bl'][j]<=stop; tp=x['bh'][j]>=target
       if st: xi,xp,why=j,stop,'STOP_BOTH' if tp else 'STOP'; break
       if tp: xi,xp,why=j,target,'TARGET'; break
      else:
       if x['ao'][j]>=stop: xi,xp,why=j,float(x['ao'][j]),'STOP_GAP'; break
       if x['ao'][j]<=target: xi,xp,why=j,float(x['ao'][j]),'TARGET_GAP'; break
       st=x['ah'][j]>=stop; tp=x['al'][j]<=target
       if st: xi,xp,why=j,stop,'STOP_BOTH' if tp else 'STOP'; break
       if tp: xi,xp,why=j,target,'TARGET'; break
     if xi is None:
      if timeout>=len(ts) or ts[timeout]>=cutoff: diag['censored_end']+=1; continue
      xi=timeout; xp=float(x['bo'][xi] if direction==1 else x['ao'][xi]); why='TIME_OPEN'
     iso=lambda z:pd.to_datetime(int(z),unit='ms',utc=True).isoformat()
     trades.append({'signal_utc':iso(ts[i]),'entry_utc':iso(ts[e]),'exit_utc':iso(ts[xi]),'direction':'LONG' if direction==1 else 'SHORT','q':q,'lookback':lb,'rr':rr,'entry':entry,'stop':stop,'target':target,'risk_pips':risk/PIP,'entry_spread_pips':(x['ao'][e]-x['bo'][e])/PIP,'exit':xp,'exit_reason':why,'gross_pips':(xp-entry)/PIP if direction==1 else (entry-xp)/PIP,'bars_held':xi-e})
     last_exit=xi
    pd.DataFrame(trades).to_csv(out/f'R281_{key}_discovery_validation_trades.csv',index=False)
    dis=period(trades,TRAIN.value//1000000,TRAIN_END.value//1000000); val=period(trades,VAL.value//1000000,END.value//1000000)
    results[key]={'q':q,'breakout_lookback':lb,'rr':rr,'discovery_plus1':summ(dis,1.),'discovery_cost_stress':{str(c):summ(dis,c) for c in COSTS},'validation_cost_stress':{str(c):summ(val,c) for c in COSTS},'diagnostics':diag}
 eligible=[k for k,v in results.items() if v['validation_cost_stress']['1.0']['trades']>=50]
 selected=sorted(eligible,key=lambda k:(-(results[k]['validation_cost_stress']['1.0']['PF'] or -1),-(results[k]['validation_cost_stress']['1.0']['mean_net_pips_per_trade'] or -1e99),-results[k]['validation_cost_stress']['1.0']['trades']))[0] if eligible else None
 gates={}
 if selected:
  v=results[selected]; gates={'discovery_trades_ge_100':v['discovery_plus1']['trades']>=100,'discovery_PF_plus1_ge_1':v['discovery_plus1']['PF'] is not None and v['discovery_plus1']['PF']>=1,'validation_PF_plus1_ge_1p10_and_net_positive':v['validation_cost_stress']['1.0']['PF'] is not None and v['validation_cost_stress']['1.0']['PF']>=1.1 and v['validation_cost_stress']['1.0']['net_pips']>0,'validation_PF_plus2_ge_1':v['validation_cost_stress']['2.0']['PF'] is not None and v['validation_cost_stress']['2.0']['PF']>=1}
 d={'round':'R281','verdict':'GAGAL','stage':'STOPPED_AT_PREREGISTERED_VALIDATION_GATE','preregistration':'research/R281_EURUSD_H1_COMPRESSION_RELEASE_PREREGISTRATION.md','data':audit,'threshold_fit':{'fitted_using_only_2017_2020':thresholds,'observations':int(tr.sum())},'selection_rule':'highest validation PF at +1 pip among candidates with >=50 validation trades; tie-break mean then trade count','selected_candidate':selected,'eligible_candidates':eligible,'forward_stage_authorized':bool(selected is not None and all(gates.values())),'grid':results,'stage1_gates':gates,'decision':'No candidate eligible: best validation count is 10, and all eight discovery PFs are below 0.668 at +1 pip. No 2022-2025 outcomes are calculated.','limitations':['2022-2025 is contaminated exploratory data, not pristine OOS.','Dukascopy collector used -fl; flat-row removal is heuristic.','No verified FundedNext fees/swaps or challenge equity-path replay.']}
 with open(out/'R281_results_compact.json','w') as f: json.dump(d,f,indent=2,allow_nan=False)
 with open(out/'R281_grid_summary.csv','w') as f:
  f.write('config,q,breakout_lookback,rr,discovery_trades,discovery_PF_plus1,discovery_net_pips_plus1,validation_trades,validation_PF_plus1,validation_net_pips_plus1,validation_PF_plus2,validation_net_pips_plus2,eligible_50_validation\\n')
  for k,v in results.items():
   a=v['discovery_plus1']; b=v['validation_cost_stress']['1.0']; c=v['validation_cost_stress']['2.0']
   f.write(f"{k},{v['q']},{v['breakout_lookback']},{v['rr']},{a['trades']},{a['PF']},{a['net_pips']},{b['trades']},{b['PF']},{b['net_pips']},{c['PF']},{c['net_pips']},{b['trades']>=50}\\n")
 print(json.dumps({'bars':audit['complete_h1_bars'],'thresholds':d['threshold_fit'],'grid':{k:{'discovery':v['discovery_plus1'],'validation':v['validation_cost_stress']['1.0']} for k,v in results.items()},'selected':selected,'forward_authorized':d['forward_stage_authorized'],'verdict':d['verdict']},indent=2,allow_nan=False))

def main():
 p=argparse.ArgumentParser(); p.add_argument('--data-zip',default='/mnt/data/eurusd_m1_bid_ask.zip'); p.add_argument('--out-dir',default='/mnt/data/r281_outputs'); a=p.parse_args(); out=Path(a.out_dir); out.mkdir(parents=True,exist_ok=True)
 if sha(a.data_zip)!=ARCHIVE_SHA: raise SystemExit('Unexpected archive SHA-256. Stop.')
 x,audit=load(a.data_zip); replay(x,audit,out)
if __name__=='__main__': main()
