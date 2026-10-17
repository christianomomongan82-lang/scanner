#!/usr/bin/env python3
"""Compact R289 replay. Outcomes after 2021 are intentionally not scored unless gates pass."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
TZ='Europe/Berlin'; COSTS=(1,2,4); DISC=(2017,2020); VAL=2021
FILES={'DEUIDXEUR':'deuidxeur_m5.csv.gz','FRAIDXEUR':'fraidxeur_m5.csv.gz','EUSIDXEUR':'eusidxeur_m5.csv.gz'}
HASH={'DEUIDXEUR':'7ad37cb19545eef6111b928a97322c06c9f2478030a0c4282669542262303af4','FRAIDXEUR':'cc9e3d3b808d1bd284def820473658aa0ec319fe167b6355e0bcaddc83eebbf4','EUSIDXEUR':'f47aa66caf714570140c63ce4056db4c426b8ff4ff4f65e5fdd9920a402a1d48'}

def load(p,sym):
 d=pd.read_csv(p,compression='gzip')
 if d.columns.tolist()!=['timestamp','open','high','low','close'] or d.timestamp.duplicated().any(): raise ValueError(f'{sym}: schema/duplicate timestamp failure')
 d=d.sort_values('timestamp',kind='stable').reset_index(drop=True); d['dt']=pd.to_datetime(d.timestamp,unit='ms',utc=True).dt.tz_convert(TZ)
 d['date']=d.dt.dt.strftime('%Y-%m-%d'); d['minute']=d.dt.dt.hour*60+d.dt.dt.minute
 o=['open','high','low','close']; d['valid']=d[o].notna().all(axis=1)&(d[o]>0).all(axis=1)&(d.high>=d[['open','close','low']].max(axis=1))&(d.low<=d[['open','close','high']].min(axis=1))
 d['flat']=(d.open==d.high)&(d.high==d.low)&(d.low==d.close)&(d.close==d.close.shift(1))
 d=d[(d.dt.dt.dayofweek<5)&d.minute.between(540,1045)&(d.date>='2017-01-01')&(d.date<='2026-12-31')].copy()
 sessions,bars,audit={},{},[]
 for day,g in d.groupby('date',sort=True):
  g=g.sort_values('timestamp').reset_index(drop=True); mid=pd.Timestamp(day).tz_localize(TZ)
  exp=pd.date_range(mid+pd.Timedelta(hours=9),mid+pd.Timedelta(hours=17,minutes=25),freq='5min')
  reasons=[]
  if len(g)!=102: reasons.append('bar_count_not_102')
  elif not pd.DatetimeIndex(g.dt).equals(exp) or g.dt.duplicated().any(): reasons.append('timestamp_sequence_invalid')
  if not g.valid.all(): reasons.append('invalid_ohlc')
  if g.flat.any(): reasons.append('repeated_flat_candidate')
  ok=not reasons
  audit.append({'symbol':sym,'date':day,'year':int(day[:4]),'bar_count':len(g),'flat_candidate_count':int(g.flat.sum()),'eligible':ok,'reason':'|'.join(reasons)})
  if ok:
   ix={int(m):int(i) for i,m in enumerate(g.minute)}
   sessions[day]={'symbol':sym,'date':day,'year':int(day[:4]),'open_0900':float(g.iloc[ix[540]].open),'entry_0910':float(g.iloc[ix[550]].open),'close_1725':float(g.iloc[ix[1045]].close)}; bars[day]=g
 ts=pd.to_datetime(pd.read_csv(p,compression='gzip',usecols=['timestamp']).timestamp,unit='ms',utc=True)
 return sessions,bars,audit,ts.min().isoformat(),ts.max().isoformat()

def sim(e,bars,sign):
 g=bars[e['symbol']][e['date']]; ix=int(np.flatnonzero(g.minute.to_numpy()==550)[0]); entry=float(g.iloc[ix].open); gd=float(e['gap_points']); sd=.75*gd
 tp=entry+sign*gd; sl=entry-sign*sd; ex=None; reason=None; exts=None; exkind=None
 for j in range(ix,len(g)):
  z=g.iloc[j]; op,hi,lo=map(float,(z.open,z.high,z.low))
  if sign>0:
   if op<=sl: ex,reason=op,'stop_gap_open'
   elif op>=tp: ex,reason=op,'target_gap_open'
   elif lo<=sl: ex,reason=sl,'stop_both_touched' if hi>=tp else 'stop'
   elif hi>=tp: ex,reason=tp,'target'
  else:
   if op>=sl: ex,reason=op,'stop_gap_open'
   elif op<=tp: ex,reason=op,'target_gap_open'
   elif hi>=sl: ex,reason=sl,'stop_both_touched' if lo<=tp else 'stop'
   elif lo<=tp: ex,reason=tp,'target'
  if ex is not None: exts=z['dt'].isoformat(); exkind='triggered_within_m5_bar_approx_bar_start'; break
 if ex is None:
  z=g.iloc[-1]; ex=float(z.close); reason='session_close'; exts=(z['dt']+pd.Timedelta(minutes=5)).isoformat(); exkind='session_bar_close'
 gr=sign*(ex-entry)/sd; gb=sign*(ex-entry)/entry*10000
 r={k:e[k] for k in ('date','year','symbol','previous_session_date','gap_days','previous_close','open_0900','entry_0910','close_1725','gap_points','gap_pct','q80_abs_gap_pct','normalized_score','gap_sign')}
 r.update({'direction':'LONG' if sign>0 else 'SHORT','entry_ts':g.iloc[ix]['dt'].isoformat(),'exit_ts':exts,'exit_ts_kind':exkind,'entry_price_bid':entry,'exit_price_bid':ex,'exit_reason':reason,'gross_r':gr,'gross_bps':gb,'stop_distance_points':sd,'target_distance_points':gd})
 for c in COSTS:
  cp=entry*c/10000; r[f'net_r_{c}bp']=float(gr-cp/sd); r[f'net_bps_{c}bp']=float(gb-c)
 return r

def summary(ts,c):
 if not ts:return {'trades':0,'pf_r':None,'net_r':0.0,'mean_r':None,'median_r':None,'max_drawdown_r':0.0,'win_rate_pct':None,'net_bps':0.0,'pf_bps':None}
 x=np.asarray([t[f'net_r_{c}bp'] for t in ts]); b=np.asarray([t[f'net_bps_{c}bp'] for t in ts]); pos=x[x>0].sum(); neg=-x[x<0].sum(); eq=np.cumsum(x); dd=np.maximum.accumulate(np.r_[0.,eq])[1:]-eq
 return {'trades':len(x),'pf_r':float(pos/neg) if neg else None,'net_r':float(x.sum()),'mean_r':float(x.mean()),'median_r':float(np.median(x)),'max_drawdown_r':float(dd.max()),'win_rate_pct':float((x>0).mean()*100),'net_bps':float(b.sum()),'pf_bps':float(b[b>0].sum()/-b[b<0].sum()) if (b<0).any() else None,'mean_bps':float(b.mean()),'median_bps':float(np.median(b))}

def weekly(ts,yr):
 idx=pd.date_range(f'{yr}-01-01',f'{yr}-12-31',freq='W-MON'); sums={}
 for t in ts:
  d=pd.Timestamp(t['date']); mon=(d-pd.Timedelta(days=d.weekday())).normalize(); sums[mon]=sums.get(mon,0.)+t['net_r_2bp']
 return np.asarray([sums.get(x.normalize(),0.) for x in idx if x.year==yr])

def bootstrap(x):
 rng=np.random.default_rng(289); n=len(x); block=4; nb=int(np.ceil(n/block)); starts=rng.integers(0,n,size=(5000,nb)); samples=x[(starts[:,:,None]+np.arange(block)[None,None,:])%n].reshape(5000,-1)[:,:n]; means=samples.mean(axis=1)
 return {'mean_weekly_net_r':float(x.mean()),'ci95_low':float(np.quantile(means,.025)),'ci95_high':float(np.quantile(means,.975)),'weeks':n,'block_weeks':4,'replicates':5000,'seed':289}

def run(data,out):
 data=Path(data); out=Path(out); out.mkdir(parents=True,exist_ok=True); sess,bars,audits,src={}, {},[],{}
 for s,f in FILES.items():
  p=data/f; h=hashlib.sha256(p.read_bytes()).hexdigest()
  if h!=HASH[s]:raise ValueError(f'{s}: SHA-256 mismatch')
  ss,bb,aa,mn,mx=load(p,s); sess[s]=ss; bars[s]=bb; audits+=aa; src[s]={'file':f,'sha256_gz':h,'bytes':p.stat().st_size,'eligible_sessions':len(ss),'source_first_utc':mn,'source_last_utc':mx}
 gaps=[]
 for s,ss in sess.items():
  prev=None
  for day in sorted(ss):
   cur=ss[day]
   if prev is not None:
    delta=(pd.Timestamp(day)-pd.Timestamp(prev['date'])).days
    if 0<delta<=4:
     pts=cur['open_0900']-prev['close_1725']; gp=(cur['open_0900']/prev['close_1725']-1)*100
     gaps.append({**cur,'previous_session_date':prev['date'],'previous_close':prev['close_1725'],'gap_days':delta,'gap_points':abs(pts),'gap_pct':gp,'abs_gap_pct':abs(gp),'gap_sign':1 if pts>0 else (-1 if pts<0 else 0)})
   prev=cur
 df=pd.DataFrame(gaps); thresh={s:float(np.quantile(df[(df.symbol==s)&df.year.between(2017,2020)].abs_gap_pct,.8,method='linear')) for s in FILES}
 df['q80_abs_gap_pct']=df.symbol.map(thresh); df['normalized_score']=df.abs_gap_pct/df.q80_abs_gap_pct.replace(0,np.nan); df=df.replace([np.inf,-np.inf],np.nan).dropna(subset=['normalized_score'])
 chosen=[]
 for d,g in df.groupby('date',sort=True):
  w=g.sort_values(['normalized_score','symbol'],ascending=[False,True],kind='stable').iloc[0]
  if w.normalized_score>=1 and w.gap_sign!=0:chosen.append(w.to_dict())
 sig=pd.DataFrame(chosen); history=[e for e in sig.to_dict('records') if 2017<=int(e['year'])<=2021]; cont=[sim(e,bars,int(e['gap_sign'])) for e in history]; fade=[sim(e,bars,-int(e['gap_sign'])) for e in history]
 metrics={};annual={str(y):{f'{c}bp':summary([t for t in cont if t['year']==y],c) for c in COSTS} for y in range(2017,2022)}
 for label,lo,hi in [('discovery_2017_2020',2017,2020),('validation_2021',2021,2021)]:
  metrics[label]={}
  for name,stream in [('continuation_candidate',cont),('matched_fade_control',fade)]:
   ts=[t for t in stream if lo<=t['year']<=hi];metrics[label][name]={f'{c}bp':summary(ts,c) for c in COSTS}
 boot=bootstrap(weekly([t for t in cont if t['year']==2021],2021)); d=metrics['discovery_2017_2020']['continuation_candidate'];v=metrics['validation_2021']['continuation_candidate']; posyears=sum(annual[str(y)]['2bp']['net_r']>0 for y in range(2017,2021))
 gates={'discovery_trades_ge_200':d['2bp']['trades']>=200,'discovery_pf_r_2bp_ge_1_05':d['2bp']['pf_r']>=1.05,'discovery_net_r_positive_2bp':d['2bp']['net_r']>0,'discovery_positive_years_ge_3_of_4':posyears>=3,'discovery_pf_r_4bp_ge_0_90':d['4bp']['pf_r']>=.9,'validation_trades_ge_50':v['2bp']['trades']>=50,'validation_net_r_positive_2bp':v['2bp']['net_r']>0,'validation_pf_r_2bp_ge_1_00':v['2bp']['pf_r']>=1,'validation_pf_r_4bp_ge_0_90':v['4bp']['pf_r']>=.9,'validation_bootstrap_ci95_lower_gt_0':boot['ci95_low']>0}
 result={'candidate_id':'R289_CONTINENTAL_EUROPE_GAP_CONTINUATION','preregistration_commit':'f3dba6084362a2b27855031945ca700521d586bc','verdict':'LULUS_HISTORICAL_GATES' if all(gates.values()) else 'GAGAL','post_2021_pnl_calculated':bool(all(gates.values())),'data':src,'thresholds_abs_gap_pct':thresh,'coverage':{'eligible_sessions_by_symbol':{s:len(v) for s,v in sess.items()},'selected_events_by_year':{str(y):int((sig.year==y).sum()) for y in range(2017,2027)},'source_latest_utc':max(x['source_last_utc'] for x in src.values())},'metrics':metrics,'annual_continuation_candidate':annual,'validation_weekly_net_r_bootstrap_2bp':boot,'gates':gates,'failed_gates':[k for k,v in gates.items() if not v],'later_metrics':None,'limitations':['M5 BID-only; no observed ASK fills','modeled costs; actual spread/slippage and contract multipliers unverified','same-bar target/stop ambiguity resolved stop-first','no floating-equity funded challenge replay']}
 pd.DataFrame(audits).to_csv(out/'R289_session_quality_audit.csv',index=False);df.to_csv(out/'R289_gap_candidate_panel.csv',index=False);sig.to_csv(out/'R289_selected_signal_ledger.csv',index=False);pd.DataFrame([{'stream':'continuation_candidate',**t} for t in cont]+[{'stream':'matched_fade_control',**t} for t in fade]).to_csv(out/'R289_trade_ledger.csv',index=False);(out/'R289_results.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--data-dir',default='/mnt/data/r289data');ap.add_argument('--out-dir',default='/mnt/data/R289_compact_check');a=ap.parse_args();run(a.data_dir,a.out_dir)
