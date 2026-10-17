#!/usr/bin/env python3
"""R286 locked US500 three-session overextension fade, local-only replay."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np,pandas as pd
TZ='America/New_York'; CSV_SHA='df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee'; COSTS=(1,2,4)
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def summ(ts,cost):
 a=np.array([x['gross_bps']-cost for x in ts],float)
 if not len(a):return {'trades':0,'pf':None,'net_bps':0.0,'max_drawdown_bps':0.0}
 pos=a[a>0].sum(); neg=-a[a<0].sum(); eq=np.cumsum(a); dd=np.maximum.accumulate(np.r_[0.,eq])[1:]-eq
 return {'trades':int(len(a)),'pf':float(pos/neg) if neg else None,'net_bps':float(a.sum()),'mean_bps':float(a.mean()),'median_bps':float(np.median(a)),'max_drawdown_bps':float(dd.max()),'positive_trade_pct':float((a>0).mean()*100)}
def run(csv,out):
 csv=Path(csv);out=Path(out);out.mkdir(parents=True,exist_ok=True); got=sha(csv)
 if got!=CSV_SHA:raise ValueError(f'CSV SHA mismatch {got}')
 d=pd.read_csv(csv,compression='gzip'); cols=['timestamp','open','high','low','close']
 if d.columns.tolist()!=cols or d.timestamp.duplicated().any():raise ValueError('source schema or timestamp uniqueness failure')
 d=d.sort_values('timestamp',kind='stable').reset_index(drop=True);d['dt_utc']=pd.to_datetime(d.timestamp,unit='ms',utc=True);d['dt']=d.dt_utc.dt.tz_convert(TZ);d['date']=d.dt.dt.strftime('%Y-%m-%d');d['minute']=d.dt.dt.hour*60+d.dt.dt.minute
 d['flat']=(d.open==d.high)&(d.high==d.low)&(d.low==d.close)&(d.close==d.close.shift(1))
 d['valid']=(d[cols[1:]].notna().all(axis=1)&(d[cols[1:]]>0).all(axis=1)&(d.high>=d[['open','close','low']].max(axis=1))&(d.low<=d[['open','close','high']].min(axis=1)))
 r=d[(d.dt.dt.dayofweek<5)&d.minute.between(570,955)].copy();sessions=[]; quality=[]
 for day,g in r.groupby('date',sort=True):
  g=g.sort_values('timestamp'); active=(g.high.max()-g.low.min()>0) and ((g.open!=g.close).any() or (g.high!=g.low).any() or (g.close!=g.close.shift(1)).any())
  if not active:continue
  exp=pd.date_range(pd.Timestamp(day).tz_localize(TZ)+pd.Timedelta(hours=9,minutes=30),pd.Timestamp(day).tz_localize(TZ)+pd.Timedelta(hours=15,minutes=55),freq='5min')
  exact=len(g)==78 and not g.dt.duplicated().any() and pd.DatetimeIndex(g.dt).equals(exp); ok=bool(exact and g.valid.all() and not g.flat.any()); reason=[]
  if len(g)!=78:reason.append('bar_count_not_78')
  elif not pd.DatetimeIndex(g.dt).equals(exp):reason.append('timestamp_sequence_invalid')
  if not g.valid.all():reason.append('invalid_ohlc')
  if g.flat.any():reason.append('repeated_flat_candidate')
  close=float(g.iloc[np.flatnonzero(g.minute.to_numpy()==955)[0]].close) if exact else None
  sessions.append({'date':day,'year':int(day[:4]),'close':close,'eligible':ok,'reason':'|'.join(reason),'rows':g.reset_index(drop=True) if ok else None})
  quality.append({'date':day,'year':int(day[:4]),'observed_rth_rows':int(len(g)),'active_rth_range':float(g.high.max()-g.low.min()),'flat_candidate_rows':int(g.flat.sum()),'eligible':ok,'reason':'|'.join(reason)})
 valid_moves=[]
 for i in range(3,len(sessions)):
  win=sessions[i-3:i+1]
  if not all(s['eligible'] and s['close'] is not None for s in win):continue
  mv=sessions[i]['close']/sessions[i-3]['close']-1
  valid_moves.append({'signal_idx':i,'signal_date':sessions[i]['date'],'signal_year':sessions[i]['year'],'move':float(mv),'abs_move':abs(float(mv))})
 fit=[x['abs_move'] for x in valid_moves if 2017<=x['signal_year']<=2020]
 if not fit:raise ValueError('No eligible discovery signal windows')
 q80=float(np.quantile(fit,.80,method='linear'));candidate=[];parent=[];skipped=[]
 for x in valid_moves:
  sy=x['signal_year'];i=x['signal_idx'];entry_idx=i+1
  if sy<2017 or entry_idx>=len(sessions):continue
  entry_session=sessions[entry_idx]
  if entry_session['year']>2021:continue
  if x['abs_move']<q80 or x['move']==0:continue
  if not entry_session['eligible']:
   skipped.append({'signal_date':x['signal_date'],'entry_date':entry_session['date'],'signal_move_pct':x['move']*100,'reason':entry_session['reason'] or 'entry_session_invalid'});continue
  g=entry_session['rows'];ei=np.flatnonzero(g.minute.to_numpy()==580);xi=np.flatnonzero(g.minute.to_numpy()==955)
  if len(ei)!=1 or len(xi)!=1:
   skipped.append({'signal_date':x['signal_date'],'entry_date':entry_session['date'],'signal_move_pct':x['move']*100,'reason':'entry_exit_timestamp_missing'});continue
  en=float(g.iloc[ei[0]].open);ex=float(g.iloc[xi[0]].close);raw=(ex/en-1)*10000
  common={'signal_date':x['signal_date'],'signal_year':sy,'date':entry_session['date'],'year':entry_session['year'],'three_session_move_pct':x['move']*100,'abs_move_pct':x['abs_move']*100,'threshold_q80_pct':q80*100,'entry':en,'exit':ex,'entry_ts':g.iloc[ei[0]]['dt'].isoformat(),'exit_ts':g.iloc[xi[0]]['dt'].isoformat()}
  child_dir=-1 if x['move']>0 else 1;par_dir=1 if x['move']>0 else -1
  candidate.append({**common,'direction':'SHORT' if child_dir<0 else 'LONG','gross_bps':raw*child_dir})
  parent.append({**common,'direction':'LONG' if par_dir>0 else 'SHORT','gross_bps':raw*par_dir})
 metrics={}
 for name,lo,hi in [('discovery_2017_2020',2017,2020),('validation_2021',2021,2021)]:
  metrics[name]={}
  for label,stream in [('candidate',candidate),('matched_parent',parent)]:
   ts=[t for t in stream if lo<=t['year']<=hi];metrics[name][label]={f'{c}bp':summ(ts,c) for c in COSTS}
 annual={str(y):summ([t for t in candidate if t['year']==y],2) for y in range(2017,2022)}
 dc=metrics['discovery_2017_2020']['candidate'];vc=metrics['validation_2021']['candidate']
 gates={'discovery_count_ge_150':dc['2bp']['trades']>=150,'discovery_pf_2bp_ge_1_05':dc['2bp']['pf'] is not None and dc['2bp']['pf']>=1.05,'discovery_net_positive_2bp':dc['2bp']['net_bps']>0,'discovery_positive_years_ge_3_of_4':sum(annual[str(y)]['net_bps']>0 for y in range(2017,2021))>=3,'validation_count_ge_45':vc['2bp']['trades']>=45,'validation_pf_2bp_ge_1_00':vc['2bp']['pf'] is not None and vc['2bp']['pf']>=1.0,'validation_net_positive_2bp':vc['2bp']['net_bps']>0,'discovery_pf_4bp_ge_0_90':dc['4bp']['pf'] is not None and dc['4bp']['pf']>=.90,'validation_pf_4bp_ge_0_90':vc['4bp']['pf'] is not None and vc['4bp']['pf']>=.90}
 result={'candidate_id':'R286_US500_3SESSION_OVEREXTENSION_FADE','verdict':'LULUS_HISTORICAL_GATES_PENDING_FORWARD' if all(gates.values()) else 'GAGAL','input':{'csv_sha256':got,'rows':int(len(d)),'first_utc':d.dt_utc.min().isoformat(),'last_utc':d.dt_utc.max().isoformat(),'artifact_id':11709864394,'timeframe':'M5 BID-only','timezone':TZ},'quality':{'active_rth_sessions':len(sessions),'quality_eligible_sessions':sum(s['eligible'] for s in sessions),'valid_3session_windows_2017_2020':len(fit),'q80_abs_three_session_return_pct':q80*100,'signals_skipped_invalid_entry':len(skipped)},'metrics':metrics,'annual_candidate_at_2bp':annual,'gates':gates,'failure_reasons':[k for k,v in gates.items() if not v],'forward_2022_2025_calculated':False,'2026_calculated':False,'funded_replay':False}
 (out/'R286_results_compact.json').write_text(json.dumps(result,indent=2)+'\n');pd.DataFrame(quality).to_csv(out/'R286_session_quality_audit.csv',index=False);pd.DataFrame(skipped).to_csv(out/'R286_skipped_signals.csv',index=False);pd.DataFrame(candidate).to_csv(out/'R286_candidate_ledger_2017_2021.csv',index=False);pd.DataFrame(parent).to_csv(out/'R286_matched_parent_ledger_2017_2021.csv',index=False)
 print(json.dumps(result,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--csv',default='/mnt/data/R285data/usa500idxusd_m5.csv.gz');p.add_argument('--out',default='/mnt/data/R286_outputs');a=p.parse_args();run(a.csv,a.out)
