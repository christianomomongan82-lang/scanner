from pathlib import Path
import pandas as pd, numpy as np, json, hashlib

BASE=Path('/mnt/data')
OUT=BASE/'R268_compound_portfolio_results'
RISK_FRAC=.0025
MAX_OPEN_RISK_FRAC=.01
FX_COST_PIPS=1.0
INDEX_COST_BPS=4.0
PRIORITY={'R262':0,'R263_USA500':1,'R263_USATECH':2}
SPLITS=[
 ('discovery_2016_2020','2016-01-01','2021-01-01'),
 ('validation_2021','2021-01-01','2022-01-01'),
 ('forward_2022_2025','2022-01-01','2026-01-01')
]

def utc(s):
 return pd.to_datetime(s,utc=True,errors='coerce')

def load():
 frames=[]
 p=BASE/'R262_H4_structure_pullback_results/R262_trades_delay_5m.csv'
 d=pd.read_csv(p)
 d['entry_ts']=utc(d.entry_utc);d['exit_ts']=utc(d.exit_utc)
 d['module']='R262';d['symbol']='EURUSD'
 risk=pd.to_numeric(d.risk_pips,errors='coerce');gross=pd.to_numeric(d.gross_pips,errors='coerce')
 d['gross_r']=gross/risk;d['net_r']=(gross-FX_COST_PIPS)/risk
 d['cost_used']=FX_COST_PIPS;d['cost_unit']='pip';d['risk_denominator']=risk;d['entry_price']=pd.to_numeric(d.entry_price,errors='coerce')
 frames.append(d[['entry_ts','exit_ts','module','symbol','gross_r','net_r','cost_used','cost_unit','risk_denominator','entry_price']])
 p2=BASE/'R263_US_cash_open_ORB_results/R263_ORB_trades_delay_5m.csv'
 d=pd.read_csv(p2)
 d['entry_ts']=utc(d.entry_time_utc);d['exit_ts']=utc(d.exit_time_utc)
 d['symbol']=d.symbol.astype(str);d['module']='R263_'+d.symbol
 risk=pd.to_numeric(d.initial_risk_bps,errors='coerce');gross=pd.to_numeric(d.gross_bps,errors='coerce')
 d['gross_r']=gross/risk;d['net_r']=(gross-INDEX_COST_BPS)/risk
 d['cost_used']=INDEX_COST_BPS;d['cost_unit']='bps';d['risk_denominator']=risk;d['entry_price']=pd.to_numeric(d.entry,errors='coerce')
 frames.append(d[['entry_ts','exit_ts','module','symbol','gross_r','net_r','cost_used','cost_unit','risk_denominator','entry_price']])
 x=pd.concat(frames,ignore_index=True).dropna(subset=['entry_ts','exit_ts','gross_r','net_r','risk_denominator'])
 x=x[(x.exit_ts>=x.entry_ts)&(x.risk_denominator>0)&(x.entry_ts<pd.Timestamp('2026-01-01',tz='UTC'))&(x.exit_ts<pd.Timestamp('2026-01-01',tz='UTC'))].copy()
 x['priority']=x.module.map(PRIORITY).fillna(9).astype(int);x['trade_id']=np.arange(len(x))
 x=x.sort_values(['entry_ts','priority','symbol','trade_id']).reset_index(drop=True)
 meta={'R262':{'rows':int(len(frames[0])),'file':str(BASE/'R262_H4_structure_pullback_results/R262_trades_delay_5m.csv')},
       'R263':{'rows':int(len(frames[1])),'file':str(p2)},
       'fx_extra_cost_pips':FX_COST_PIPS,'index_extra_cost_bps':INDEX_COST_BPS,
       'input_sha256':{str(f):hashlib.sha256(Path(f).read_bytes()).hexdigest() for f in [BASE/'R262_H4_structure_pullback_results/R262_trades_delay_5m.csv',p2]}}
 return x,meta

def subset(x,lo,hi):
 lo=pd.Timestamp(lo,tz='UTC');hi=pd.Timestamp(hi,tz='UTC')
 return x[(x.entry_ts>=lo)&(x.entry_ts<hi)&(x.exit_ts<hi)].copy()

def simulate(x,start_equity=6000.):
 entries={};exits={}
 for t in x.itertuples(index=False):
  entries.setdefault(t.entry_ts,[]).append(t);exits.setdefault(t.exit_ts,[]).append(t)
 equity=start_equity;peak=equity;maxdd=0.;active={};events=[];skipped=[];weekly={}
 def close(t,ts):
  nonlocal equity,peak,maxdd
  if t.trade_id not in active:return
  pos=active.pop(t.trade_id);pnl=pos['risk_dollars']*float(t.net_r);equity+=pnl
  week=ts.normalize()-pd.Timedelta(days=ts.weekday())
  weekly[week]=weekly.get(week,0.)+pnl;peak=max(peak,equity);maxdd=max(maxdd,(peak-equity)/peak if peak>0 else 1.)
  row=pos['row'];row.update({'exit_ts':ts.isoformat(),'net_r':float(t.net_r),'pnl_dollars':pnl,'equity_after_exit':equity});events.append(row)
 for ts in sorted(set(entries)|set(exits)):
  for t in sorted([z for z in exits.get(ts,[]) if z.entry_ts<ts],key=lambda z:(z.priority,z.symbol,z.trade_id)):close(t,ts)
  for t in sorted(entries.get(ts,[]),key=lambda z:(z.priority,z.symbol,z.trade_id)):
   rd=equity*RISK_FRAC;op=sum(v['risk_dollars'] for v in active.values())
   if equity<=0 or op+rd>equity*MAX_OPEN_RISK_FRAC+1e-8:
    skipped.append({'trade_id':int(t.trade_id),'module':t.module,'symbol':t.symbol,'entry_ts':ts.isoformat(),'reason':'OPEN_RISK_CAP'});continue
   row={'trade_id':int(t.trade_id),'module':t.module,'symbol':t.symbol,'entry_ts':ts.isoformat(),'entry_equity':equity,'risk_dollars':rd,'gross_r':float(t.gross_r),'net_r':float(t.net_r),'cost_used':float(t.cost_used),'cost_unit':t.cost_unit,'entry_price':float(t.entry_price)}
   active[t.trade_id]={'risk_dollars':rd,'row':row}
  for t in sorted([z for z in exits.get(ts,[]) if z.entry_ts==ts],key=lambda z:(z.priority,z.symbol,z.trade_id)):close(t,ts)
 led=pd.DataFrame(events);skip=pd.DataFrame(skipped)
 return {'starting_equity':start_equity,'ending_equity':equity,'total_return_pct':(equity/start_equity-1)*100,
  'closed_equity_max_drawdown_pct':maxdd*100,'accepted_trades':len(led),'skipped_due_open_risk_cap':len(skip),'still_open_at_period_end':len(active),
  'accepted_ledger':led,'skipped_ledger':skip,'weekly_pnl_dollars':weekly}

def pf(r):
 a=np.asarray(r,float);gp=a[a>0].sum();gl=-a[a<0].sum()
 return float(gp/gl) if gl>0 else (float('inf') if gp>0 else None)

def bootstrap(weekly,start,end,seed,reps=10000,block=4):
 lo=pd.Timestamp(start,tz='UTC');hi=pd.Timestamp(end,tz='UTC');cur=lo.normalize()-pd.Timedelta(days=lo.weekday())
 weeks=[]
 while cur<hi:weeks.append(cur);cur+=pd.Timedelta(days=7)
 values=np.array([weekly.get(w,0.)/6000*100 for w in weeks]);rng=np.random.default_rng(seed);means=np.empty(reps);nb=int(np.ceil(len(values)/block));steps=np.arange(block)
 for i in range(reps):
  ix=np.concatenate([(s+steps)%len(values) for s in rng.integers(0,len(values),size=nb)])[:len(values)];means[i]=values[ix].mean()
 return {'weeks_including_zero_trade_weeks':len(values),'block_weeks':block,'reps':reps,'seed':seed,'mean_weekly_pnl_pct_of_reference_equity':float(values.mean()),'prob_bootstrap_mean_positive':float((means>0).mean()),'ci95_mean_weekly_pct':[float(np.quantile(means,.025)),float(np.quantile(means,.975))]}

def simple_stats(x):
 o={}
 for m,g in x.groupby('module'):
  r=g.net_r.to_numpy(float);o[m]={'trades':len(g),'PF_net_R':pf(r),'sum_net_R':float(r.sum()),'mean_net_R':float(r.mean()),'win_rate':float((r>0).mean())}
 return o

def summarize(x,name,lo,hi,seed):
 trades=subset(x,lo,hi);s=simulate(trades);l=s['accepted_ledger'];r=l.net_r.to_numpy(float) if len(l) else np.array([])
 mods={}
 if len(l):
  for m,g in l.groupby('module'):mods[m]={'accepted_trades':len(g),'sum_net_R':float(g.net_r.sum()),'PF_net_R':pf(g.net_r),'pnl_dollars':float(g.pnl_dollars.sum())}
 out={k:v for k,v in s.items() if k not in ('accepted_ledger','skipped_ledger','weekly_pnl_dollars')}
 out.update({'period':name,'input_trades_in_period':len(trades),'independent_module_R_stats':simple_stats(trades),'accepted_module_contribution':mods,
  'accepted_trade_PF_net_R':pf(r),'sum_accepted_net_R':float(r.sum()) if len(r) else 0.,'mean_accepted_net_R':float(r.mean()) if len(r) else None,
  'bootstrap_weekly_pnl':bootstrap(s['weekly_pnl_dollars'],lo,hi,seed),'annual_compound':{}})
 if name=='forward_2022_2025':
  for y in range(2022,2026):
   yr=subset(x,f'{y}-01-01',f'{y+1}-01-01');ys=simulate(yr);yl=ys['accepted_ledger']
   out['annual_compound'][str(y)]={k:v for k,v in ys.items() if k not in ('accepted_ledger','skipped_ledger','weekly_pnl_dollars')}
   out['annual_compound'][str(y)].update({'PF_net_R':pf(yl.net_r) if len(yl) else None,'sum_net_R':float(yl.net_r.sum()) if len(yl) else 0.})
 return out,s

def main():
 OUT.mkdir(exist_ok=True);x,meta=load();res={'study':'R268 fixed-fractional compound portfolio diagnostic','date':'2026-10-16','status':'COMPLETE','verdict':'GAGAL','classification':'RETROSPECTIVE_DIAGNOSTIC_NOT_INDEPENDENTLY_VALIDATED',
 'parameters_locked':True,'preregistration':'R268_COMPOUND_PORTFOLIO_PREREGISTRATION.md',
 'method':{'initial_equity_usd':6000,'risk_per_trade_pct_of_realized_equity':.25,'maximum_open_initial_risk_pct':1.,'FX_extra_cost_pips':1.,'index_extra_cost_bps':4.,
  'components':['R262 EURUSD H4 structural pullback, 5-min delayed ledger','R263 USA500/USATECH cash-open ORB, 5-min delayed ledger'],
  'entry_priority':['R262 EURUSD','R263 USA500','R263 USATECH'],'compounding':'fixed fractional risk, sized at entry equity; add pnl at exit',
  'no_2026_trades_included':True,'component_outcomes_previously_inspected':True},'data':meta,'periods':{},'limitations':[
  'Retrospective combination of already-inspected components; cannot be promoted from these same intervals.',
  'Trade ledgers provide closed outcomes, not full tick-by-tick floating equity. Drawdown is closed-equity drawdown only.',
  'No exact daily-loss or Quick Strike sub-30-second replay.',
  'Index costs are fixed bps assumptions, not observed live spreads.',
  'Do not interpret compounded history as a challenge pass-probability estimate.']}
 allsim=simulate(x)
 res['all_history']={k:v for k,v in allsim.items() if k not in ('accepted_ledger','skipped_ledger','weekly_pnl_dollars')}
 for k,df in [('all_history',allsim['accepted_ledger']),('all_history_skipped',allsim['skipped_ledger'])]:
  path=OUT/f'R268_{k}.csv';df.to_csv(path,index=False);res.setdefault('ledgers',{})[k]={'file':path.name,'rows':len(df),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 for i,(n,a,b) in enumerate([('discovery_2016_2020','2016-01-01','2021-01-01'),('validation_2021','2021-01-01','2022-01-01'),('forward_2022_2025','2022-01-01','2026-01-01')]):
  q,s=summarize(x,n,a,b,2682026+i);res['periods'][n]=q
  for k,df in [('accepted',s['accepted_ledger']),('skipped',s['skipped_ledger'])]:
   path=OUT/f'R268_{n}_{k}.csv';df.to_csv(path,index=False);res['ledgers'][n+'_'+k]={'file':path.name,'rows':len(df),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
 d=res['periods'];fw=d['forward_2022_2025'];g={
  'discovery_net_positive':d['discovery_2016_2020']['ending_equity']>6000 and d['discovery_2016_2020']['sum_accepted_net_R']>0,
  'validation_net_positive':d['validation_2021']['ending_equity']>6000 and d['validation_2021']['sum_accepted_net_R']>0,
  'forward_net_positive_PF_ge_1_10':fw['ending_equity']>6000 and fw['accepted_trade_PF_net_R'] is not None and fw['accepted_trade_PF_net_R']>=1.1,
  'every_forward_year_positive':all(v['ending_equity']>6000 for v in fw['annual_compound'].values()),
  'bootstrap_CI_lower_above_zero':fw['bootstrap_weekly_pnl']['ci95_mean_weekly_pct'][0]>0,
  'closed_equity_max_DD_below_10pct':fw['closed_equity_max_drawdown_pct']<10,
  'independent_validation_available':False}
 g['promotion_eligible']=all(g.values());res['decision_gates']=g
 res['economic_screen_pass']=all(v for k,v in g.items() if k!='independent_validation_available' and k!='promotion_eligible')
 res['verdict']='LULUS' if g['promotion_eligible'] else 'GAGAL'
 res['decision']='GAGAL FOR PROMOTION: retrospective combination, selection bias and economic gates fail.'
 (OUT/'R268_compound_portfolio_results.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
 print(json.dumps(res,indent=2,allow_nan=False))
if __name__=='__main__':main()
