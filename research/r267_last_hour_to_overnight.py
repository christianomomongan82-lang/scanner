from pathlib import Path
import pandas as pd, numpy as np, json, hashlib

ROOT=Path('/mnt/data/r205_index_data')
OUT=Path('/mnt/data/R267_last_hour_overnight')
OUT.mkdir(exist_ok=True)
TZ='America/New_York'
COSTS=[2.0,4.0,6.0]
SPLITS=[('discovery_2016_2020','2016-01-01','2021-01-01'),('validation_2021','2021-01-01','2022-01-01'),('forward_2022_2025','2022-01-01','2026-01-01')]

def daily_sessions(path,sym):
    raw=pd.read_csv(path,compression='infer')
    df=raw.copy(); df.columns=[str(c).strip().lower() for c in df.columns]
    df['timestamp_utc']=pd.to_datetime(pd.to_numeric(df['timestamp'],errors='coerce'),unit='ms',utc=True,errors='coerce')
    for c in ['open','high','low','close']: df[c]=pd.to_numeric(df[c],errors='coerce')
    df=df.dropna(subset=['timestamp_utc','open','high','low','close']).sort_values('timestamp_utc')
    dup=int(df.timestamp_utc.duplicated(keep='last').sum()); df=df.drop_duplicates('timestamp_utc',keep='last').copy()
    valid=(df.high>=df[['open','close']].max(axis=1))&(df.low<=df[['open','close']].min(axis=1))&(df.low<=df[['open','close']].min(axis=1))&(df.high>=df.low)
    invalid=int((~valid).sum()); df=df.loc[valid].copy()
    df['timestamp_et']=df.timestamp_utc.dt.tz_convert(TZ); df['date_et']=df.timestamp_et.dt.date; df['hhmm']=df.timestamp_et.dt.strftime('%H:%M')
    rth=df.loc[df.hhmm.between('09:30','15:55')].copy()
    g=rth.groupby('date_et',sort=True); counts=g.size(); uniq=g.hhmm.nunique()
    complete=counts.index[(counts==78)&(uniq==78)]
    rth=rth.loc[rth.date_et.isin(complete)].copy()
    def at(tm,col):
        z=rth.loc[rth.hhmm.eq(tm)].set_index('date_et')[col]
        return z.loc[~z.index.duplicated(keep='last')]
    daily=rth.groupby('date_et',sort=True).agg(day_high=('high','max'),day_low=('low','min'))
    for tm,col,name in [('09:30','open','open_0930'),('14:00','open','open_1400'),('14:55','close','close_1455'),('15:00','open','open_1500'),('15:05','open','open_1505')]:
        daily[name]=at(tm,col)
    daily=daily.dropna(subset=['open_0930','open_1400','close_1455','open_1500','open_1505']).copy()
    daily=daily.loc[[pd.Timestamp(x).weekday()<5 for x in daily.index]].copy()
    daily.index=pd.DatetimeIndex(pd.to_datetime(daily.index.astype(str)),name='date')
    daily['signal_return_bps']=(daily.close_1455/daily.open_1400-1)*10000
    daily['signal']=np.sign(daily.signal_return_bps)
    # Exit at the next complete RTH session open; no synthetic missing bars.
    daily['next_date']=daily.index.to_series().shift(-1)
    daily['exit_0930']=daily.open_0930.shift(-1)
    q={'symbol':sym,'file':path.name,'input_rows':int(len(raw)),'valid_rows':int(len(df)),'duplicates_removed':dup,'invalid_ohlc_removed':invalid,
       'start_utc':df.timestamp_utc.min().isoformat(),'end_utc':df.timestamp_utc.max().isoformat(),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
       'complete_rth_sessions':int(len(daily))}
    return daily,q

def make_trades(mode):
    frames=[]; qual={}
    for sym,fn in [('USA500','usa500idxusd_m5.csv.gz'),('USATECH','usatechidxusd_m5.csv.gz')]:
        d,q=daily_sessions(ROOT/fn,sym); qual[sym]=q
        entry_col='open_1500' if mode=='ideal' else 'open_1505'
        x=d.copy()
        x['entry_date']=x.index
        x['exit_date']=x.next_date
        x['entry_price']=x[entry_col]
        x['exit_price']=x.exit_0930
        x=x.loc[x.signal.ne(0)&x.exit_date.notna()].copy()
        x=x.loc[(x.entry_date>=pd.Timestamp('2016-01-01'))&(x.entry_date<pd.Timestamp('2026-01-01'))&(x.exit_date<pd.Timestamp('2026-01-01'))].copy()
        x['symbol']=sym; x['mode']=mode; x['direction']=x.signal.astype(int)
        x['gross_bps']=x.direction*(x.exit_price/x.entry_price-1)*10000
        frames.append(x[['symbol','mode','entry_date','exit_date','direction','signal_return_bps','entry_price','exit_price','gross_bps']].reset_index(drop=True))
    trades=pd.concat(frames,ignore_index=True).sort_values(['entry_date','symbol']).reset_index(drop=True)
    return trades,qual

def metrics(x,cost):
    if len(x)==0:return {'trades':0,'PF':None,'net_bps':0.0,'gross_bps':0.0,'win_rate':None}
    z=x.gross_bps-cost; gains=float(z[z>0].sum()); losses=float(-z[z<0].sum()); pf=gains/losses if losses>0 else (float('inf') if gains>0 else None)
    return {'trades':int(len(x)),'PF':None if pf is None or not np.isfinite(pf) else float(pf),'net_bps':float(z.sum()),'gross_bps':float(x.gross_bps.sum()),'win_rate':float((z>0).mean()),'mean_net_bps_per_trade':float(z.mean())}

def summarize(trades):
    o={}
    for nm,lo,hi in SPLITS:
        x=trades.loc[(trades.entry_date>=pd.Timestamp(lo))&(trades.entry_date<pd.Timestamp(hi))].copy()
        o[nm]={'combined':{f'cost_{int(c)}bps':metrics(x,c) for c in COSTS},'by_symbol':{s:{f'cost_{int(c)}bps':metrics(x[x.symbol.eq(s)],c) for c in COSTS} for s in ['USA500','USATECH']}}
        if nm=='forward_2022_2025':
            o[nm]['annual']={str(y):{f'cost_{int(c)}bps':metrics(x[x.entry_date.dt.year.eq(y)],c) for c in COSTS} for y in range(2022,2026)}
    return o

def bootstrap(trades,cost,seed,reps=10000,block=4):
    start=pd.Timestamp('2022-01-01'); end=pd.Timestamp('2026-01-01'); n=int(np.ceil((end-start).days/7)); weekly=np.zeros(n)
    x=trades.loc[(trades.entry_date>=start)&(trades.entry_date<end)]
    for r in x.itertuples():
        j=int((r.entry_date-start).days//7)
        if 0<=j<n:weekly[j]+=float(r.gross_bps)-cost
    rng=np.random.default_rng(seed); nb=int(np.ceil(n/block)); means=np.empty(reps); steps=np.arange(block)
    for k in range(reps):
        ix=np.concatenate([(s+steps)%n for s in rng.integers(0,n,size=nb)])[:n]; means[k]=weekly[ix].mean()
    return {'weeks_including_zero_trade_weeks':n,'reps':reps,'seed':seed,'block_weeks':block,'mean_weekly_net_bps':float(weekly.mean()),'prob_mean_positive':float((means>0).mean()),'ci95_mean_weekly_net_bps':[float(np.quantile(means,.025)),float(np.quantile(means,.975))]}

def main():
    res={'study':'R267 last-hour price momentum predicts next RTH open return','date':'2026-10-16','status':'COMPLETE','verdict':'FAILED','parameters_locked':True,
      'rules':{'timezone':TZ,'signal':'sign of return from 14:00 ET bar open to 14:55 ET bar close (known at 15:00 ET)','entry_ideal':'15:00 ET bar open','entry_delay5':'15:05 ET bar open','exit':'next complete RTH session 09:30 ET bar open','position':'long if signal return positive, short if negative; one trade per symbol/day','holding':'overnight to next regular session, weekends included; no 2026 outcome trades included','cost_bps':[2,4,6]},
      'splits':{'discovery':'2016–2020','validation':'2021','forward':'2022–2025'},'data':{},'modes':{},'limitations':['Input is BID-only. Fixed bps costs are sensitivities, not observed spreads.','No live broker slippage, commission, funded DLL/MLL or Quick Strike replay.','Trades with exit dates in 2026 are omitted so OOS prices do not enter a historical segment.']}
    for mode,seed in [('ideal',2672026),('delay5',2672031)]:
        t,q=make_trades(mode); t.to_csv(OUT/f'R267_trades_{mode}.csv',index=False); res['data']=q; sums=summarize(t); boot=bootstrap(t,4,seed)
        gates={}
        for nm in ['discovery_2016_2020','validation_2021','forward_2022_2025']:
            m=sums[nm]['combined']['cost_4bps']; gates[nm+'_net_positive_pf_ge_1_10']=m['net_bps']>0 and m['PF'] is not None and m['PF']>=1.10
        f=sums['forward_2022_2025']
        gates['forward_trade_count_ge_100']=f['combined']['cost_4bps']['trades']>=100
        gates['all_forward_years_pf_ge_1_00']=all(x['cost_4bps']['PF'] is not None and x['cost_4bps']['PF']>=1 for x in f['annual'].values())
        gates['both_symbols_forward_pf_ge_1_00']=all(f['by_symbol'][s]['cost_4bps']['PF'] is not None and f['by_symbol'][s]['cost_4bps']['PF']>=1 for s in ['USA500','USATECH'])
        gates['bootstrap_ci_lower_above_zero']=boot['ci95_mean_weekly_net_bps'][0]>0
        res['modes'][mode]={'trade_count':int(len(t)),'summary':sums,'bootstrap_forward_cost4':boot,'gates':gates}
    ideal=res['modes']['ideal']['gates']; delayed=res['modes']['delay5']['gates']
    delay_fw=res['modes']['delay5']['summary']['forward_2022_2025']['combined']['cost_4bps']
    delayed['delay5_forward_net_positive_pf_ge_1_10']=delay_fw['net_bps']>0 and delay_fw['PF'] is not None and delay_fw['PF']>=1.10
    ci_both=all(res['modes'][m]['bootstrap_forward_cost4']['ci95_mean_weekly_net_bps'][0]>0 for m in ['ideal','delay5'])
    for m in ['ideal','delay5']:res['modes'][m]['gates']['both_bootstrap_ci_lower_above_zero']=ci_both
    res['gate_summary']={'all_gates_pass':all(all(g.values()) for g in [ideal,delayed]),'ideal':ideal,'delay5':delayed}
    res['data']={'USA500':daily_sessions(ROOT/'usa500idxusd_m5.csv.gz','USA500')[1],'USATECH':daily_sessions(ROOT/'usatechidxusd_m5.csv.gz','USATECH')[1], 'ask_side_available':False,'oos_2026_inspected':False,'cutoff':'entry and exit dates must be before 2026-01-01'}
    (OUT/'R267_results.json').write_text(json.dumps(res,indent=2,allow_nan=False)+'\n')
    print(json.dumps(res,indent=2,allow_nan=False))
if __name__=='__main__':main()
