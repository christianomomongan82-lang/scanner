#!/usr/bin/env python3
"""R287 locked cross-index residual reversion. PnL intentionally stops at 2021."""
import argparse, hashlib, json
from pathlib import Path
import numpy as np
import pandas as pd

TZ='America/New_York'
FILES={'USA500':'usa500idxusd_m5.csv.gz','USATECH':'usatechidxusd_m5.csv.gz','USA30':'usa30idxusd_m5.csv.gz','USSC2000':'ussc2000idxusd_m5.csv.gz'}
COSTS=(1,2,4)

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for chunk in iter(lambda:f.read(1<<20),b''): h.update(chunk)
    return h.hexdigest()

def load_sessions(path,symbol):
    d=pd.read_csv(path,compression='gzip')
    if d.columns.tolist()!=['timestamp','open','high','low','close']:
        raise ValueError(f'{symbol}: unexpected schema')
    if d.timestamp.duplicated().any(): raise ValueError(f'{symbol}: duplicate timestamps')
    d=d.sort_values('timestamp',kind='stable').reset_index(drop=True)
    d['dt_utc']=pd.to_datetime(d.timestamp,unit='ms',utc=True)
    d['dt']=d.dt_utc.dt.tz_convert(TZ)
    d['date']=d.dt.dt.strftime('%Y-%m-%d')
    d['minute']=d.dt.dt.hour*60+d.dt.dt.minute
    o=['open','high','low','close']
    d['valid']=d[o].notna().all(axis=1)&(d[o]>0).all(axis=1)&(d.high>=d[['open','close','low']].max(axis=1))&(d.low<=d[['open','close','high']].min(axis=1))
    d['flat_candidate']=(d.open==d.high)&(d.high==d.low)&(d.low==d.close)&(d.close==d.close.shift(1))
    r=d[(d.dt.dt.dayofweek<5)&d.minute.between(570,955)&(d.date>='2017-01-01')&(d.date<='2021-12-31')].copy()
    sessions={}; audits=[]
    for day,g in r.groupby('date',sort=True):
        g=g.sort_values('timestamp').reset_index(drop=True)
        active=(float(g.high.max())-float(g.low.min())>0) and ((g.open!=g.close).any() or (g.high!=g.low).any() or (g.close!=g.close.shift(1)).any())
        if not active: continue
        midnight=pd.Timestamp(day).tz_localize(TZ)
        expected=pd.date_range(midnight+pd.Timedelta(hours=9,minutes=30),midnight+pd.Timedelta(hours=15,minutes=55),freq='5min')
        exact=len(g)==78 and not g.dt.duplicated().any() and pd.DatetimeIndex(g.dt).equals(expected)
        reason=[]
        if len(g)!=78: reason.append('bar_count_not_78')
        elif not pd.DatetimeIndex(g.dt).equals(expected): reason.append('timestamp_sequence_invalid')
        if not g.valid.all(): reason.append('invalid_ohlc')
        if g.flat_candidate.any(): reason.append('repeated_flat_candidate')
        ok=bool(exact and g.valid.all() and not g.flat_candidate.any())
        rec={'symbol':symbol,'date':day,'year':int(day[:4]),'active':True,'bar_count':int(len(g)),'flat_candidate_count':int(g.flat_candidate.sum()),'eligible':ok,'reason':'|'.join(reason)}
        sess=None
        if ok:
            def one(minute):
                ix=np.flatnonzero(g.minute.to_numpy()==minute)
                return g.iloc[int(ix[0])] if len(ix)==1 else None
            op10,cl1255,op1305,op1555=one(600),one(775),one(785),one(955)
            if any(x is None for x in (op10,cl1255,op1305,op1555)):
                rec['eligible']=False; rec['reason']='required_timestamp_missing'
            else:
                ret=float(cl1255.close)/float(op10.open)-1
                pnl=(float(op1555.open)/float(op1305.open)-1)*10000
                sess={'symbol':symbol,'date':day,'year':int(day[:4]),'signal_return':ret,
                      'entry_open':float(op1305.open),'exit_open':float(op1555.open),
                      'raw_return_bps':pnl,'entry_ts':op1305.dt.isoformat(),'exit_ts':op1555.dt.isoformat()}
        audits.append(rec)
        if rec['eligible'] and sess is not None: sessions[day]=sess
    return sessions,audits

def summarize(trades,cost):
    a=np.asarray([t['gross_bps']-cost for t in trades],float)
    if not len(a): return {'trades':0,'pf':None,'net_bps':0.0,'max_drawdown_bps':0.0}
    wins=a[a>0].sum(); losses=-a[a<0].sum(); eq=np.cumsum(a)
    dd=np.maximum.accumulate(np.r_[0.0,eq])[1:]-eq
    return {'trades':int(len(a)),'pf':float(wins/losses) if losses else None,
            'net_bps':float(a.sum()),'mean_bps':float(a.mean()),'median_bps':float(np.median(a)),
            'max_drawdown_bps':float(dd.max()),'positive_trade_pct':float((a>0).mean()*100)}

def run(data_dir,out_dir):
    data_dir=Path(data_dir); out=Path(out_dir); out.mkdir(parents=True,exist_ok=True)
    sessions_by={}; audit=[]; sources={}
    for sym,fn in FILES.items():
        p=data_dir/fn; sources[sym]={'file':fn,'csv_sha256':sha256(p),'bytes':p.stat().st_size}
        ss,au=load_sessions(p,sym); sessions_by[sym]=ss; audit.extend(au)
    dates=sorted(set().union(*[set(v) for v in sessions_by.values()]))
    panel=[]
    for day in dates:
        available=[sessions_by[s][day] for s in FILES if day in sessions_by[s]]
        if len(available)<3: continue
        med=float(np.median([x['signal_return'] for x in available]))
        for x in available: panel.append({**x,'cross_section_median_return':med,'residual':float(x['signal_return']-med)})
    p=pd.DataFrame(panel)
    if p.empty: raise ValueError('No synchronized eligible sessions')
    thresholds={}
    for sym in FILES:
        a=p[(p.symbol==sym)&p.year.between(2017,2020)].residual.abs().to_numpy()
        if not len(a): raise ValueError(f'No discovery residual for {sym}')
        thresholds[sym]=float(np.quantile(a,.75,method='linear'))
    p['q75_abs_residual']=p.symbol.map(thresholds)
    p['normalized_score']=p.residual.abs()/p.q75_abs_residual.replace(0,np.nan)
    p=p.replace([np.inf,-np.inf],np.nan).dropna(subset=['normalized_score'])
    events=[]
    for day,g in p.groupby('date',sort=True):
        winner=g.sort_values(['normalized_score','symbol'],ascending=[False,True],kind='stable').iloc[0]
        if float(winner.normalized_score)<1 or float(winner.residual)==0: continue
        resid=float(winner.residual); raw=float(winner.raw_return_bps)
        common={'signal_date':day,'entry_date':day,'year':int(day[:4]),'symbol':str(winner.symbol),
          'late_morning_return_pct':float(winner.signal_return*100),
          'cross_section_median_return_pct':float(winner.cross_section_median_return*100),
          'residual_pct':resid*100,'q75_abs_residual_pct':float(winner.q75_abs_residual*100),
          'normalized_score':float(winner.normalized_score),'entry_open':float(winner.entry_open),
          'exit_open':float(winner.exit_open),'entry_ts':str(winner.entry_ts),'exit_ts':str(winner.exit_ts)}
        pdirection=1 if resid>0 else -1; cdirection=-pdirection
        events.append({'candidate':{**common,'direction':'LONG' if cdirection>0 else 'SHORT','gross_bps':raw*cdirection},
                       'parent':{**common,'direction':'LONG' if pdirection>0 else 'SHORT','gross_bps':raw*pdirection}})
    candidate=[e['candidate'] for e in events]; parent=[e['parent'] for e in events]
    metrics={}
    for segment,lo,hi in [('discovery_2017_2020',2017,2020),('validation_2021',2021,2021)]:
        metrics[segment]={}
        for name,stream in [('candidate',candidate),('matched_parent',parent)]:
            ts=[t for t in stream if lo<=t['year']<=hi]
            metrics[segment][name]={f'{c}bp':summarize(ts,c) for c in COSTS}
    annual={str(y):summarize([t for t in candidate if t['year']==y],2) for y in range(2017,2022)}
    canddisc=metrics['discovery_2017_2020']['candidate']; candval=metrics['validation_2021']['candidate']
    gates={'discovery_count_ge_200':canddisc['2bp']['trades']>=200,
      'discovery_pf_2bp_ge_1_05':canddisc['2bp']['pf'] is not None and canddisc['2bp']['pf']>=1.05,
      'discovery_net_positive_2bp':canddisc['2bp']['net_bps']>0,
      'discovery_positive_years_ge_2_of_4':sum(annual[str(y)]['net_bps']>0 for y in range(2017,2021))>=2,
      'validation_count_ge_50':candval['2bp']['trades']>=50,
      'validation_pf_2bp_ge_1_00':candval['2bp']['pf'] is not None and candval['2bp']['pf']>=1,
      'validation_net_positive_2bp':candval['2bp']['net_bps']>0,
      'discovery_pf_4bp_ge_0_90':canddisc['4bp']['pf'] is not None and canddisc['4bp']['pf']>=.90,
      'validation_pf_4bp_ge_0_90':candval['4bp']['pf'] is not None and candval['4bp']['pf']>=.90}
    result={'candidate_id':'R287_US_INDEX_INTRADAY_RESIDUAL_REVERSION',
      'verdict':'LULUS_HISTORICAL_GATES_PENDING_FORWARD' if all(gates.values()) else 'GAGAL',
      'source':sources,
      'method':{'signal':'10:00 open to 12:55 close return minus same-date cross-sectional median',
        'entry':'13:05 ET bar open','exit':'15:55 ET bar open',
        'threshold':'per-symbol Q75 absolute residual fitted on 2017-2020',
        'thresholds_abs_residual_pct':{k:v*100 for k,v in thresholds.items()},
        'score_gate':1,'modeled_round_trip_costs_bps':list(COSTS),'primary_cost_bps':2},
      'coverage':{'valid_session_counts_2017_2021':{s:len(v) for s,v in sessions_by.items()},
        'common_dates_with_3plus_symbols':int(p.date.nunique()),'selected_events':len(events),
        'candidate_trades_discovery':sum(2017<=t['year']<=2020 for t in candidate),
        'candidate_trades_validation':sum(t['year']==2021 for t in candidate)},
      'metrics':metrics,'candidate_annual_at_2bp':annual,'gates':gates,
      'failure_reasons':[k for k,v in gates.items() if not v],
      'post_2021_pnl_calculated':False,'2026_pnl_calculated':False,'funded_replay':False,
      'limitations':['M5 BID-only; no actual ASK fills','1/2/4 bp modeled costs, not verified provider costs',
        'No account-equity DLL/MLL replay']}
    (out/'R287_results_compact.json').write_text(json.dumps(result,indent=2)+'\n')
    pd.DataFrame(audit).to_csv(out/'R287_session_quality_audit.csv',index=False)
    p.to_csv(out/'R287_residual_panel_2017_2021.csv',index=False)
    pd.DataFrame(candidate).to_csv(out/'R287_candidate_ledger_2017_2021.csv',index=False)
    pd.DataFrame(parent).to_csv(out/'R287_matched_parent_ledger_2017_2021.csv',index=False)
    print(json.dumps(result,indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('--data-dir',default='/mnt/data/r284data')
    ap.add_argument('--out-dir',default='/mnt/data/R287_outputs')
    a=ap.parse_args(); run(a.data_dir,a.out_dir)
