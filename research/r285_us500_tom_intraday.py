#!/usr/bin/env python3
"""R285 exact local replay: US500 turn-of-month intraday seasonality.
Only calculate 2017-2021 outcomes. Does not score any later period.
"""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd
TZ='America/New_York'
CSV_SHA='df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee'
COSTS=(1,2,4)
def sha(p):
 h=hashlib.sha256(); f=open(p,'rb')
 for b in iter(lambda:f.read(1<<20),b''): h.update(b)
 f.close(); return h.hexdigest()
def summary(trades,cost):
 a=np.array([x['gross_bps']-cost for x in trades],float)
 if not len(a): return {'trades':0,'pf':None,'net_bps':0.0,'max_drawdown_bps':0.0}
 pos=a[a>0].sum(); neg=-a[a<0].sum(); eq=np.cumsum(a); dd=np.maximum.accumulate(np.r_[0.,eq])[1:]-eq
 return {'trades':int(len(a)),'pf':float(pos/neg) if neg else None,'net_bps':float(a.sum()),'mean_bps':float(a.mean()),'median_bps':float(np.median(a)),'max_drawdown_bps':float(dd.max()),'positive_trade_pct':float((a>0).mean()*100)}
def run(csv,out):
 csv=Path(csv); out=Path(out); out.mkdir(parents=True,exist_ok=True)
 got=sha(csv)
 if got!=CSV_SHA: raise ValueError(f'CSV SHA-256 mismatch: {got}')
 d=pd.read_csv(csv,compression='gzip')
 if d.columns.tolist()!=['timestamp','open','high','low','close']: raise ValueError('Unexpected source schema')
 if d.timestamp.duplicated().any(): raise ValueError('Duplicate source timestamps')
 d=d.sort_values('timestamp',kind='stable').reset_index(drop=True)
 d['dt_utc']=pd.to_datetime(d.timestamp,unit='ms',utc=True); d['dt']=d.dt_utc.dt.tz_convert(TZ); d['date']=d.dt.dt.strftime('%Y-%m-%d'); d['minute']=d.dt.dt.hour*60+d.dt.dt.minute
 d['flat']=(d.open==d.high)&(d.high==d.low)&(d.low==d.close)&(d.close==d.close.shift(1))
 d['valid']=(d[['open','high','low','close']].notna().all(axis=1)&(d[['open','high','low','close']]>0).all(axis=1)&(d.high>=d[['open','close','low']].max(axis=1))&(d.low<=d[['open','close','high']].min(axis=1)))
 r=d[(d.dt.dt.dayofweek<5)&d.minute.between(570,955)].copy()
 sessions=[]; quality=[]
 for day,g in r.groupby('date',sort=True):
  g=g.sort_values('timestamp'); active=(g.high.max()-g.low.min()>0) and ((g.open!=g.close).any() or (g.high!=g.low).any() or (g.close!=g.close.shift(1)).any())
  if not active: continue
  exp=pd.date_range(pd.Timestamp(day).tz_localize(TZ)+pd.Timedelta(hours=9,minutes=30),pd.Timestamp(day).tz_localize(TZ)+pd.Timedelta(hours=15,minutes=55),freq='5min')
  exact=len(g)==78 and not g.dt.duplicated().any() and pd.DatetimeIndex(g.dt).equals(exp)
  ok=bool(exact and g.valid.all() and not g.flat.any()); reasons=[]
  if len(g)!=78: reasons.append('bar_count_not_78')
  elif not pd.DatetimeIndex(g.dt).equals(exp): reasons.append('timestamp_sequence_invalid')
  if not g.valid.all(): reasons.append('invalid_ohlc')
  if g.flat.any(): reasons.append('repeated_flat_candidate')
  sessions.append({'date':day,'year':int(day[:4]),'month':day[:7],'eligible':ok,'reason':'|'.join(reasons),'rows':g.reset_index(drop=True) if ok else None})
  quality.append({'date':day,'year':int(day[:4]),'month':day[:7],'observed_rth_rows':len(g),'active_rth_range':float(g.high.max()-g.low.min()),'flat_candidate_rows':int(g.flat.sum()),'calendar_session':True,'trade_eligible':ok,'reason':'|'.join(reasons)})
 cal=pd.DataFrame([{k:v for k,v in s.items() if k!='rows'} for s in sessions])
 cal['first_rank']=cal.groupby('month').cumcount()+1
 cal['last_rank']=cal.groupby('month')['date'].transform(lambda x:len(x)-pd.Series(np.arange(len(x)),index=x.index))
 cal['candidate']=(cal.first_rank<=3)|(cal.last_rank<=2)
 lookup={s['date']:s for s in sessions}; candidate=[]; skipped=[]
 for row in cal[cal.candidate].itertuples(index=False):
  s=lookup[row.date]
  if not s['eligible']:
   skipped.append({'date':row.date,'year':row.year,'month':row.month,'skip_reason':s['reason'] or 'quality_fail'}); continue
  g=s['rows']; ei=np.flatnonzero(g.minute.to_numpy()==580); xi=np.flatnonzero(g.minute.to_numpy()==955)
  if len(ei)!=1 or len(xi)!=1: skipped.append({'date':row.date,'year':row.year,'month':row.month,'skip_reason':'entry_exit_timestamp_missing'}); continue
  en=float(g.iloc[ei[0]].open); ex=float(g.iloc[xi[0]].close)
  candidate.append({'date':row.date,'year':row.year,'month':row.month,'gross_bps':(ex/en-1)*10000,'entry':en,'exit':ex,'entry_ts':g.iloc[ei[0]]['dt'].isoformat(),'exit_ts':g.iloc[xi[0]]['dt'].isoformat(),'signal':'LONG_TURN_OF_MONTH'})
 parent=[]
 for s in sessions:
  if s['eligible'] and 2017<=s['year']<=2021:
   g=s['rows']; ei=np.flatnonzero(g.minute.to_numpy()==580); xi=np.flatnonzero(g.minute.to_numpy()==955)
   if len(ei)==1 and len(xi)==1:
    parent.append({'date':s['date'],'year':s['year'],'month':s['month'],'gross_bps':(float(g.iloc[xi[0]].close)/float(g.iloc[ei[0]].open)-1)*10000,'entry_ts':g.iloc[ei[0]]['dt'].isoformat(),'exit_ts':g.iloc[xi[0]]['dt'].isoformat()})
 metrics={}
 for name,lo,hi in [('discovery_2017_2020',2017,2020),('validation_2021',2021,2021)]:
  metrics[name]={}
  for label,source in [('candidate',candidate),('matched_parent',parent)]:
   ts=[t for t in source if lo<=t['year']<=hi]
   metrics[name][label]={f'{c}bp':summary(ts,c) for c in COSTS}
 annual={str(y):summary([t for t in candidate if t['year']==y],2) for y in range(2017,2022)}
 dc=metrics['discovery_2017_2020']['candidate']; vc=metrics['validation_2021']['candidate']
 gates={'discovery_count_ge_150':dc['2bp']['trades']>=150,'discovery_pf_2bp_ge_1_05':bool(dc['2bp']['pf'] is not None and dc['2bp']['pf']>=1.05),'discovery_net_positive_2bp':dc['2bp']['net_bps']>0,'discovery_positive_years_ge_3_of_4':sum(annual[str(y)]['net_bps']>0 for y in range(2017,2021))>=3,'validation_count_ge_45':vc['2bp']['trades']>=45,'validation_pf_2bp_ge_1_00':bool(vc['2bp']['pf'] is not None and vc['2bp']['pf']>=1.0),'validation_net_positive_2bp':vc['2bp']['net_bps']>0,'discovery_pf_4bp_ge_0_90':bool(dc['4bp']['pf'] is not None and dc['4bp']['pf']>=.90),'validation_pf_4bp_ge_0_90':bool(vc['4bp']['pf'] is not None and vc['4bp']['pf']>=.90)}
 result={'candidate_id':'R285_US500_TURN_OF_MONTH_INTRADAY','verdict':'LULUS_HISTORICAL_GATES_PENDING_FORWARD' if all(gates.values()) else 'GAGAL','input':{'csv_sha256':got,'rows':int(len(d)),'first_utc':d.dt_utc.min().isoformat(),'last_utc':d.dt_utc.max().isoformat(),'timeframe':'M5 BID-only','timezone':TZ},'quality':{'active_rth_sessions':len(sessions),'quality_eligible_sessions':sum(x['eligible'] for x in sessions),'calendar_selected_sessions':int(cal.candidate.sum()),'selected_sessions_skipped':len(skipped),'candidate_trades':{'discovery_2017_2020':sum(2017<=x['year']<=2020 for x in candidate),'validation_2021':sum(x['year']==2021 for x in candidate)}},'metrics':metrics,'annual_candidate_at_2bp':annual,'gates':gates,'forward_2022_2025_calculated':False,'2026_calculated':False,'funded_replay':False}
 (out/'R285_results_compact.json').write_text(json.dumps(result,indent=2)+'\n'); pd.DataFrame(quality).to_csv(out/'R285_session_quality_audit.csv',index=False); pd.DataFrame(skipped).to_csv(out/'R285_selected_session_skips.csv',index=False); pd.DataFrame([t for t in candidate if 2017<=t['year']<=2021]).to_csv(out/'R285_candidate_ledger_2017_2021.csv',index=False); pd.DataFrame(parent).to_csv(out/'R285_parent_ledger_2017_2021.csv',index=False)
 print(json.dumps(result,indent=2))
if __name__=='__main__':
 ap=argparse.ArgumentParser(); ap.add_argument('--csv',default='/mnt/data/R285data/usa500idxusd_m5.csv.gz'); ap.add_argument('--out',default='/mnt/data/R285_outputs'); a=ap.parse_args(); run(a.csv,a.out)
