"""Local sensitivity only: official intrabar-aware R189 model plus delayed-fill offsets."""
import sys,json
from pathlib import Path
import numpy as np,pandas as pd
sys.path.insert(0,'/mnt/data')
import r189_dukascopy_historical_replay as r

def sim(df,bid,ask,signals,delay=0):
 n,idx=len(df),df.index
 bo,bh,bl,bc=(bid[k].to_numpy(float) for k in ('Open','High','Low','Close'))
 ao,ah,al,ac=(ask[k].to_numpy(float) for k in ('Open','High','Low','Close'))
 spread=(ao-bo)/r.PIP; trades=[]; active_exit=-1; overlap=spread_rej=censored=gap_fills=0
 for si,direction,_ in signals:
  e=si+1+delay
  if e>=n: continue
  if not np.isfinite(spread[e]) or spread[e]<-1e-9 or spread[e]>r.MAX_SPREAD_PIPS+1e-12: spread_rej+=1; continue
  if e<=active_exit: overlap+=1; continue
  entry=float(ao[e] if direction==1 else bo[e]); hard_stop=entry-direction*r.SL*r.PIP; target=entry+direction*r.TP*r.PIP
  fav=entry; trail_active=False; stop=hard_stop; scheduled=e+r.TIME_STOP_BARS
  if scheduled>=n: censored+=1; active_exit=n; continue
  exit_i=gross=reason=None
  for j in range(e,scheduled):
   active_stop=stop if trail_active else hard_stop
   if direction==1:
    if bo[j]<=active_stop:
     exit_i=j;gross=(bo[j]-entry)/r.PIP;reason='STOP_GAP_OPEN' if bo[j]<active_stop else ('TRAIL_STOP' if trail_active else 'STOP');gap_fills+=int(bo[j]<active_stop);break
    if bo[j]>=target:
     exit_i=j;gross=(bo[j]-entry)/r.PIP;reason='TARGET_GAP_OPEN';break
    stop_hit=bl[j]<=active_stop;target_hit=bh[j]>=target
   else:
    if ao[j]>=active_stop:
     exit_i=j;gross=-(ao[j]-entry)/r.PIP;reason='STOP_GAP_OPEN' if ao[j]>active_stop else ('TRAIL_STOP' if trail_active else 'STOP');gap_fills+=int(ao[j]>active_stop);break
    if ao[j]<=target:
     exit_i=j;gross=-(ao[j]-entry)/r.PIP;reason='TARGET_GAP_OPEN';break
    stop_hit=ah[j]>=active_stop;target_hit=al[j]<=target
   if stop_hit:
    exit_i=j;gross=direction*(active_stop-entry)/r.PIP;reason='TRAIL_STOP' if trail_active else 'STOP';break
   if target_hit: exit_i=j;gross=r.TP;reason='TARGET';break
   if direction==1:
    fav=max(fav,bh[j]);fv=(fav-entry)/r.PIP
    if fv>=r.MFE_TRIGGER:
     ns=entry+(fv-r.TRAIL)*r.PIP
     if (not trail_active) or ns>stop:stop=ns
     trail_active=True
     if bc[j]<stop-1e-12:exit_i=j;gross=(stop-entry)/r.PIP;reason='TRAIL_STOP_SAME_BAR';break
   else:
    fav=min(fav,al[j]);fv=(entry-fav)/r.PIP
    if fv>=r.MFE_TRIGGER:
     ns=entry-(fv-r.TRAIL)*r.PIP
     if (not trail_active) or ns<stop:stop=ns
     trail_active=True
     if ac[j]>stop+1e-12:exit_i=j;gross=-(stop-entry)/r.PIP;reason='TRAIL_STOP_SAME_BAR';break
  if exit_i is None:
   exit_i=scheduled;px=float(bo[exit_i] if direction==1 else ao[exit_i]);gross=direction*(px-entry)/r.PIP;reason='TIME_OPEN_CAUSAL'
  trades.append({'signal_utc':idx[si].isoformat(),'entry_utc':idx[e].isoformat(),'exit_utc':idx[exit_i].isoformat(),
   'entry_spread_pips':float(spread[e]),'direction':'LONG' if direction==1 else 'SHORT','gross_pips':float(gross),'exit_reason':reason})
  active_exit=exit_i
 return trades,{'spread_rejected':spread_rej,'overlap_skipped':overlap,'censored':censored,'gap_fills':gap_fills}

bid,_=r.read_bars(r.DATA/'eurusd_bid_M1_2016-2025.csv.gz');ask,_=r.read_bars(r.DATA/'eurusd_ask_M1_2016-2025.csv.gz')
common=bid.index.intersection(ask.index).sort_values();bid,ask=bid.loc[common],ask.loc[common];df=bid.copy();spread=(ask.Open-bid.Open)/r.PIP
allsigs=r.l80_fast(df,disp_thr=15,late_thr=.8)
sigs=[(i,d,s) for i,d,s in allsigs if ((df.index[i].hour-5)%24) not in (6,9) and i+6<len(df)]
periods=[('all_2016_2025','2016-01-01','2026-01-01'),('discovery_2016_2020','2016-01-01','2021-01-01'),('forward_2021_2025','2021-01-01','2026-01-01')]
rows=[]; boots=[]; annual_rows=[]; diag_all={}
for lag in [0,1,3,5]:
 tr,diag=sim(df,bid,ask,sigs,lag);diag_all[str(lag)]=diag
 for pname,ss,ee in periods:
  s,e=pd.Timestamp(ss,tz='UTC'),pd.Timestamp(ee,tz='UTC'); z=[t for t in tr if s<=pd.Timestamp(t['entry_utc'])<e and pd.Timestamp(t['exit_utc'])<e]
  for c in [.5,1.0]:
   rows.append({'extra_delay_after_ideal_fill_minutes':lag,'period':pname,'extra_cost_pips':c,**r.metric(z,c,(e-s).total_seconds()/(7*24*3600)),
                'spread_rejected':diag['spread_rejected'],'overlap_skipped':diag['overlap_skipped'],'gap_fills':diag['gap_fills']})
 for y in range(2021,2026):
  s,e=pd.Timestamp(f'{y}-01-01',tz='UTC'),pd.Timestamp(f'{y+1}-01-01',tz='UTC');z=[t for t in tr if s<=pd.Timestamp(t['entry_utc'])<e and pd.Timestamp(t['exit_utc'])<e]
  annual_rows.append({'extra_delay_after_ideal_fill_minutes':lag,'year':y,**{f'PF_plus_{c:g}':r.metric(z,c,(e-s).total_seconds()/(7*24*3600))['PF'] for c in [.5,1.0]},
                      'trades':len(z),'net_plus_0.5':r.metric(z,.5,1)['net_pips'],'net_plus_1':r.metric(z,1.,1)['net_pips']})
 s,e=pd.Timestamp('2021-01-01',tz='UTC'),pd.Timestamp('2026-01-01',tz='UTC');weeks=int(np.ceil((e-s).total_seconds()/(7*24*3600)))
 z=[t for t in tr if s<=pd.Timestamp(t['entry_utc'])<e and pd.Timestamp(t['exit_utc'])<e]
 for cost in [.5,1.0]:
  weekly=np.zeros(weeks)
  for t in z:
   wi=int((pd.Timestamp(t['entry_utc'])-s).total_seconds()//(7*24*3600))
   if 0<=wi<weeks:weekly[wi]+=t['gross_pips']-cost
  rng=np.random.default_rng(1892026+lag*100+int(cost*10));reps=5000;block=4;nb=int(np.ceil(weeks/block));means=np.empty(reps)
  for k in range(reps):
   starts=rng.integers(0,weeks,size=nb);ix=np.concatenate([(q+np.arange(block))%weeks for q in starts])[:weeks];means[k]=weekly[ix].mean()
  boots.append({'extra_delay_after_ideal_fill_minutes':lag,'extra_cost_pips':cost,'trades':len(z),'mean_weekly_net_pips':float(weekly.mean()),
   'prob_positive_mean':float((means>0).mean()),'ci95':[float(np.quantile(means,.025)),float(np.quantile(means,.975))]})
OUT=r.OUT;OUT.mkdir(parents=True,exist_ok=True)
pd.DataFrame(rows).to_csv(OUT/'R189_official_intrabar_delay_stress.csv',index=False);pd.DataFrame(annual_rows).to_csv(OUT/'R189_official_intrabar_delay_annual.csv',index=False)
summary={'status':'COMPLETE','model':'Matches the repo official intrabar sensitivity logic; adds fixed fill delay offsets only, no strategy tuning.',
 'delay_definition':'0=next-M1-open baseline; 1/3/5 means additional minutes after the ideal fill, so signal-to-fill roughly 2/4/6 minutes after signal close.',
 'eligible_signals_before_delayed_spread_test':len(sigs),'diagnostics_by_delay':diag_all,'results':rows,'annual_forward':annual_rows,'bootstrap':boots}
(OUT/'R189_official_intrabar_delay_stress.json').write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
print(json.dumps(summary,indent=2,allow_nan=False))
