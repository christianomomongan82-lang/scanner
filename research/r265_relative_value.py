from pathlib import Path
import pandas as pd, numpy as np, json, hashlib

ROOT=Path('/mnt/data/r205_index_data')
OUT=Path('/mnt/data/R265_relative_value_results')
OUT.mkdir(exist_ok=True)
TZ='America/New_York'
COSTS=[2.0,4.0,6.0]

def load(path, symbol):
    df=pd.read_csv(path, compression='infer')
    df.columns=[str(c).strip().lower() for c in df.columns]
    ts=pd.to_datetime(pd.to_numeric(df['timestamp'],errors='coerce'),unit='ms',utc=True,errors='coerce')
    df=df.assign(timestamp_utc=ts).dropna(subset=['timestamp_utc'])
    for c in ['open','high','low','close']:
        df[c]=pd.to_numeric(df[c],errors='coerce')
    df=df.dropna(subset=['timestamp_utc','open','high','low','close']).sort_values('timestamp_utc')
    dup=int(df['timestamp_utc'].duplicated(keep='last').sum())
    df=df.drop_duplicates('timestamp_utc',keep='last').copy()
    valid=(df['high']>=df[['open','close']].max(axis=1))&(df['low']<=df[['open','close']].min(axis=1))&(df['high']>=df[['open','close']].min(axis=1))&(df['high']>=df['low'])
    invalid=int((~valid).sum())
    df=df.loc[valid].copy()
    df['timestamp_et']=df['timestamp_utc'].dt.tz_convert(TZ)
    df['date_et']=df['timestamp_et'].dt.date
    df['hhmm']=df['timestamp_et'].dt.strftime('%H:%M')
    rth=df.loc[(df['hhmm']>='09:30')&(df['hhmm']<='15:55')].copy()
    quality={'symbol':symbol,'file':path.name,'input_rows':int(len(pd.read_csv(path,compression='infer'))),
      'valid_rows':int(len(df)),'duplicate_timestamps_removed':dup,'invalid_ohlc_removed':invalid,
      'start_utc':df.timestamp_utc.min().isoformat(),'end_utc':df.timestamp_utc.max().isoformat(),
      'sha256_file':hashlib.sha256(path.read_bytes()).hexdigest(),'rth_rows':int(len(rth)),
      'rth_dates':int(rth.date_et.nunique())}
    rg=rth.groupby('date_et',sort=True)
    counts=rg.size(); uniq=rg.hhmm.nunique()
    complete_dates=counts.index[(counts==78)&(uniq==78)]
    rc=rth[rth.date_et.isin(complete_dates)]
    daily_agg=rc.groupby('date_et',sort=True).agg(high=('high','max'),low=('low','min'),bar_count=('open','size'))
    opens=rc[rc.hhmm.isin(['09:30','09:35'])].pivot(index='date_et',columns='hhmm',values='open')
    closes=rc[rc.hhmm=='15:55'].set_index('date_et')['close']
    qdf=daily_agg.join(opens.rename(columns={'09:30':'open930','09:35':'open935'})).join(closes.rename('close'))
    qdf=qdf.dropna(subset=['open930','open935','close']).sort_index()
    is_weekday=np.array([pd.Timestamp(d).weekday()<5 for d in qdf.index])
    qdf=qdf.loc[is_weekday & ((qdf['high']-qdf['low']).abs().to_numpy()>1e-12)].copy()
    qdf['date']=pd.to_datetime(qdf.index.astype(str))
    qdf.index=pd.Index(qdf.index,name='date')
    quality['complete_rth_days']=int(len(qdf))
    return qdf,quality

def build_pair():
    a,qa=load(ROOT/'usa500idxusd_m5.csv.gz','USA500')
    b,qb=load(ROOT/'usatechidxusd_m5.csv.gz','USATECH')
    dates=a.index.intersection(b.index)
    pair=pd.DataFrame(index=dates)
    for col in ['open930','open935','close','high','low']:
        pair[f'usa_{col}']=a.loc[dates,col]; pair[f'tech_{col}']=b.loc[dates,col]
    pair['ratio']=np.log(pair['tech_close']/pair['usa_close'])
    prevmean=pair['ratio'].shift(1).rolling(60,min_periods=60).mean()
    prevstd=pair['ratio'].shift(1).rolling(60,min_periods=60).std(ddof=1)
    pair['z']=(pair['ratio']-prevmean)/prevstd
    return pair.sort_index(),qa,qb

def run(delay='ideal'):
    pair,qa,qb=build_pair()
    opcol='open930' if delay=='ideal' else 'open935'
    rows=[]; position=None; pending_entry=None
    dates=list(pair.index)
    for i,d in enumerate(dates):
        r=pair.loc[d]
        if position is not None and position.get('exit_due_date')==d:
            pxU=float(r[f'usa_{opcol}']); pxT=float(r[f'tech_{opcol}'])
            if position['direction']=='short_tech_long_usa':
                long_ret=(pxU-position['entry_usa'])/position['entry_usa']
                short_ret=(position['entry_tech']-pxT)/position['entry_tech']
            else:
                long_ret=(pxT-position['entry_tech'])/position['entry_tech']
                short_ret=(position['entry_usa']-pxU)/position['entry_usa']
            gross_bps=(long_ret+short_ret)*0.5*10000.0
            rows.append({'delay':delay,'entry_date':str(position['entry_date']),'exit_date':str(d),
              'direction':position['direction'],'entry_z':position['entry_z'],'exit_z':float(r['z']) if pd.notna(r['z']) else np.nan,
              'entry_usa':position['entry_usa'],'entry_tech':position['entry_tech'],'exit_usa':pxU,'exit_tech':pxT,
              'gross_bps':gross_bps,'holding_sessions':int(i-position['entry_i']),'exit_reason':position['exit_reason'],
              'exit_delay_minutes':0 if delay=='ideal' else 5})
            position=None
        if pending_entry is not None and pending_entry['due_date']==d and position is None:
            pxU=float(r[f'usa_{opcol}']); pxT=float(r[f'tech_{opcol}'])
            if pxU>0 and pxT>0:
                position={'direction':pending_entry['direction'],'entry_i':i,'entry_date':d,'entry_z':pending_entry['z'],
                  'entry_usa':pxU,'entry_tech':pxT,'exit_due_date':None,'exit_reason':None}
        pending_entry=None
        z=float(r['z']) if pd.notna(r['z']) else np.nan
        if position is not None and np.isfinite(z):
            signal=position['entry_z']; exit_reason=None
            if signal>=2.0 and z<=0.0: exit_reason='mean_reversion_to_zero'
            elif signal<=-2.0 and z>=0.0: exit_reason='mean_reversion_to_zero'
            elif signal>=2.0 and z>=3.0: exit_reason='adverse_z_stop'
            elif signal<=-2.0 and z<=-3.0: exit_reason='adverse_z_stop'
            elif (i-position['entry_i']+1)>=10: exit_reason='max_10_sessions'
            if exit_reason and i+1<len(dates):
                position['exit_due_date']=dates[i+1]; position['exit_reason']=exit_reason
        if position is None and pending_entry is None and np.isfinite(z) and i+1<len(dates):
            if z>=2.0: pending_entry={'due_date':dates[i+1],'direction':'short_tech_long_usa','z':z}
            elif z<=-2.0: pending_entry={'due_date':dates[i+1],'direction':'long_tech_short_usa','z':z}
    return pd.DataFrame(rows),pair,{'usa500':qa,'usatech':qb,'common_complete_sessions':int(len(pair)),
      'start_date':str(pair.index.min()),'end_date':str(pair.index.max()),'z_available_rows':int(pair.z.notna().sum()),
      'censored_open_position_at_end':int(position is not None)}

def metrics(trades,cost):
    x=trades.copy(); x['net_bps']=x.gross_bps-cost
    w=float(x.loc[x.net_bps>0,'net_bps'].sum()); l=float(-x.loc[x.net_bps<0,'net_bps'].sum())
    pf=w/l if l>0 else (float('inf') if w>0 else None)
    eq=x.net_bps.cumsum().to_numpy(float); dd=float(np.max(np.maximum.accumulate(np.r_[0.,eq])[1:]-eq)) if len(eq) else 0.0
    return {'trades':int(len(x)),'PF':None if pf is None or not np.isfinite(pf) else float(pf),
      'gross_bps':float(x.gross_bps.sum()) if len(x) else 0.0,'net_bps':float(x.net_bps.sum()) if len(x) else 0.0,
      'win_rate':float((x.net_bps>0).mean()) if len(x) else None,'max_trade_equity_dd_bps':dd,
      'median_holding_sessions':float(x.holding_sessions.median()) if len(x) else None,
      'mean_holding_sessions':float(x.holding_sessions.mean()) if len(x) else None}

def split_metrics(trades):
    ans={}
    for name,start,end in [('discovery_2016_2020','2016-01-01','2021-01-01'),('validation_2021','2021-01-01','2022-01-01'),('forward_2022_2025','2022-01-01','2026-01-01')]:
        t=trades[(trades.entry_date>=start)&(trades.entry_date<end)].copy()
        ans[name]={f'cost_{int(c)}bps':metrics(t,c) for c in COSTS}
        if name=='forward_2022_2025':
            ans[name]['annual_by_entry_year']={str(y):{f'cost_{int(c)}bps':metrics(t[t.entry_date.str[:4]==str(y)],c) for c in COSTS} for y in range(2022,2026)}
    return ans

def bootstrap_weekly(trades,cost,seed=2652026,reps=10000,block=4):
    start=pd.Timestamp('2022-01-01'); end=pd.Timestamp('2026-01-01')
    nweeks=int(np.ceil((end-start).days/7)); weekly=np.zeros(nweeks)
    for _,t in trades.iterrows():
        d=pd.Timestamp(t.exit_date)
        if start<=d<end:
            wi=int((d-start).days//7)
            if 0<=wi<nweeks: weekly[wi]+=float(t.gross_bps)-cost
    rng=np.random.default_rng(seed); nblocks=int(np.ceil(nweeks/block)); means=np.empty(reps)
    for j in range(reps):
        starts=rng.integers(0,nweeks,size=nblocks)
        ix=np.concatenate([(x+np.arange(block))%nweeks for x in starts])[:nweeks]
        means[j]=weekly[ix].mean()
    return {'weeks':nweeks,'reps':reps,'seed':seed,'block_weeks':block,'mean_weekly_net_bps':float(weekly.mean()),
      'probability_positive_mean':float((means>0).mean()),'ci95_mean_weekly_net_bps':[float(np.quantile(means,.025)),float(np.quantile(means,.975))]}

def main():
    outputs={}
    for delay in ['ideal','delay5']:
        trades,pair,quality=run(delay)
        trades.to_csv(OUT/f'R265_trades_{delay}.csv',index=False)
        if delay=='ideal': pair.to_csv(OUT/'R265_pair_daily.csv')
        outputs[delay]={'delay_mode':delay,'data_quality':quality,'periods':split_metrics(trades),
          'bootstrap_forward_at_4bps':bootstrap_weekly(trades,4,seed=2652026+(delay=='delay5')),
          'trade_count':len(trades),'exit_reasons':trades.exit_reason.value_counts().to_dict() if len(trades) else {},
          'overall':{f'cost_{int(c)}bps':metrics(trades,c) for c in COSTS},
          'limitations':['BID-only index data; ASK-side prices and observed quoted spread unavailable.','Cost values are assumed basis points per equal-notional pair trade, not verified live execution cost.','No funded provider DLL/MLL or Quick Strike verification.']}
    report={'status':'COMPLETE','study':'R265 USA500-USATECH relative-value mean reversion',
      'verdict':'TBD - apply preregistered gates only','parameters_locked':True,
      'rules':{'lookback_sessions':60,'entry_z':2.0,'adverse_exit_z':3.0,'mean_reversion_exit_z':0.0,'max_holding_sessions':10,
        'entry':'next common RTH session open, 09:30 ET ideal or 09:35 ET delayed','exit_fill':'next common RTH session open / 09:35 delayed','cost_bps':COSTS},
      'ideal':outputs['ideal'],'delay5':outputs['delay5']}
    for mode in ['ideal','delay5']:
        forward=outputs[mode]['periods']['forward_2022_2025']['cost_4bps']; bt=outputs[mode]['bootstrap_forward_at_4bps']
        outputs[mode]['gate']={'forward_trades_ge_100':forward['trades']>=100,
          'forward_pf_ge_1_10':(forward['PF'] is not None and forward['PF']>=1.10),
          'bootstrap_95ci_positive':bt['ci95_mean_weekly_net_bps'][0]>0}
    gateok=all(outputs['ideal']['gate'].values()) and all(outputs['delay5']['gate'].values())
    report['verdict']='PASSED HISTORICAL SCREEN ONLY' if gateok else 'FAILED'
    report['gate_summary']={'ideal':outputs['ideal']['gate'],'delay5':outputs['delay5']['gate'],'all_gates_pass':gateok}
    (OUT/'R265_results.json').write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    print(json.dumps(report,indent=2,allow_nan=False))
if __name__=='__main__': main()
