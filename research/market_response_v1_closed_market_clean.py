#!/usr/bin/env python3
"""Market Response Model v1: learn conditional executable EURUSD M1 trade outcomes.

Exploratory only. Train 2016-2019; use 2020-2021 only to lock score threshold;
2022-2025 are a program-level contaminated diagnostic, not pristine OOS.
Input is the retained GitHub Actions artifact containing Dukascopy BID/ASK M1.
All calculations are local; no GitHub Actions backtest is run.
"""
from __future__ import annotations
import json, time, hashlib
from pathlib import Path
import numpy as np
import pandas as pd
from numba import njit
from lightgbm import LGBMRegressor
from scipy.stats import spearmanr

ROOT=Path("/mnt/data/market_response_data")
OUT=Path("/mnt/data/market_response_v1_results")
OUT.mkdir(exist_ok=True)
PIP=0.0001
ENTRY_DELAY_ROWS=6       # sample bar at :29/:59; close :30/:00; enter 5 minutes later
MAX_HOLD=120
TP_PIPS=15.0
SL_PIPS=10.0
EXTRA_COST=0.5
SAMPLE_MOD=30

@njit(cache=True)
def simulate_one(i, side, ts, bo, bh, bl, bc, ao, ah, al, ac):
    """Net pips, exit index, reason 1=TP,2=SL,3=time."""
    e=i+ENTRY_DELAY_ROWS
    end=e+MAX_HOLD
    if end>=len(ts):
        return np.nan, -1, 0
    if ts[e]-ts[i] != ENTRY_DELAY_ROWS*60000 or ts[end]-ts[e] != MAX_HOLD*60000:
        return np.nan, -1, 0
    if side == 1:  # LONG: entry Ask, exits Bid
        entry=ao[e]; tp=entry+TP_PIPS*PIP; sl=entry-SL_PIPS*PIP
        for j in range(e, end+1):
            if bl[j] <= sl:  # conservative tie-break: stop first
                return -SL_PIPS-EXTRA_COST, j, 2
            if bh[j] >= tp:
                return TP_PIPS-EXTRA_COST, j, 1
        return (bc[end]-entry)/PIP-EXTRA_COST, end, 3
    else:  # SHORT: entry Bid, exits Ask
        entry=bo[e]; tp=entry-TP_PIPS*PIP; sl=entry+SL_PIPS*PIP
        for j in range(e, end+1):
            if ah[j] >= sl:
                return -SL_PIPS-EXTRA_COST, j, 2
            if al[j] <= tp:
                return TP_PIPS-EXTRA_COST, j, 1
        return (entry-ac[end])/PIP-EXTRA_COST, end, 3

def sha256(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''): h.update(b)
    return h.hexdigest()

def load_quotes():
    t0=time.time()
    bp=ROOT/'eurusd_bid_M1_2016-2025.csv.gz'; ap=ROOT/'eurusd_ask_M1_2016-2025.csv.gz'
    dtypes={'timestamp':'int64','open':'float32','high':'float32','low':'float32','close':'float32'}
    bid=pd.read_csv(bp,dtype=dtypes); ask=pd.read_csv(ap,dtype=dtypes)
    if len(bid)!=len(ask) or not np.array_equal(bid.timestamp.to_numpy(),ask.timestamp.to_numpy()):
        raise RuntimeError('BID/ASK timestamps are not exactly aligned')
    ts=bid.timestamp.to_numpy(dtype=np.int64); arr={}
    for pfx,df in [('b',bid),('a',ask)]:
        for col in ['open','high','low','close']:
            arr[pfx+col]=df[col].to_numpy(dtype=np.float64)
    del bid,ask
    print(f'Loaded {len(ts):,} matched rows in {time.time()-t0:.1f}s',flush=True)
    return ts,arr,{'rows':int(len(ts)),'start_utc':str(pd.to_datetime(ts[0],unit='ms',utc=True)),
      'end_utc':str(pd.to_datetime(ts[-1],unit='ms',utc=True)),
      'bid_sha256_gzip':sha256(bp),'ask_sha256_gzip':sha256(ap)}

def make_features(ts,a):
    t0=time.time()
    bo,bh,bl,bc=(a['bopen'],a['bhigh'],a['blow'],a['bclose'])
    ao,ah,al,ac=(a['aopen'],a['ahigh'],a['alow'],a['aclose'])
    mo=(bo+ao)/2; mh=(bh+ah)/2; ml=(bl+al)/2; mc=(bc+ac)/2
    spr=(ac-bc)/PIP; n=len(ts)
    minute=ts//60000
    idx=np.flatnonzero((minute%SAMPLE_MOD)==(SAMPLE_MOD-1))
    idx=idx[(idx>=240)&(idx+ENTRY_DELAY_ROWS+MAX_HOLD<n)]
    ok=(ts[idx]-ts[idx-240]==240*60000)&(ts[idx+ENTRY_DELAY_ROWS]-ts[idx]==ENTRY_DELAY_ROWS*60000)&(ts[idx+ENTRY_DELAY_ROWS+MAX_HOLD]-ts[idx+ENTRY_DELAY_ROWS]==MAX_HOLD*60000)
    idx=idx[ok]
    # Correct data-integrity rule: the archive includes static flat BID/ASK candles
    # during market closure, especially Sunday before the weekly open. Timestamp
    # continuity alone is insufficient. Remove any sample whose prior feature
    # window or forward trade path intersects a flat-run of >=30 M1 bars.
    flat_b=(bo==bh)&(bh==bl)&(bl==bc)
    flat_a=(ao==ah)&(ah==al)&(al==ac)
    flat_both=(flat_b & flat_a).astype(np.int8)
    run_start=np.flatnonzero(np.diff(np.r_[0,flat_both,0])==1)
    run_end=np.flatnonzero(np.diff(np.r_[0,flat_both,0])==-1)
    market_closed=np.zeros(n,dtype=bool)
    for rs,re in zip(run_start,run_end):
        if re-rs>=30:
            market_closed[rs:re]=True
    closed_prefix=np.r_[0,np.cumsum(market_closed,dtype=np.int64)]
    # Feature return at idx uses idx-240 to idx, so include both endpoints.
    look_closed=(closed_prefix[idx+1]-closed_prefix[idx-240])>0
    entry=idx+ENTRY_DELAY_ROWS; end=entry+MAX_HOLD
    path_closed=(closed_prefix[end+1]-closed_prefix[entry])>0
    keep=(~look_closed)&(~path_closed)
    print(f'Flat-run closed-market rows flagged: {int(market_closed.sum()):,}; candidates before filter: {len(idx):,}; excluded for closure exposure: {int((~keep).sum()):,}',flush=True)
    idx=idx[keep]
    print(f'Valid closure-clean candidate timestamps: {len(idx):,}',flush=True)
    r=np.zeros(n,dtype=np.float64); r[1:]=(mc[1:]-mc[:-1])/PIP
    absr=np.abs(r); pos=(r>0).astype(np.float64); neg=(r<0).astype(np.float64)
    def pref(x): return np.concatenate(([0.0],np.cumsum(x,dtype=np.float64)))
    pr=pref(r); pr2=pref(r*r); pa=pref(absr); pp=pref(pos); pn=pref(neg); sprpref=pref(spr)
    F={}
    def add(name,val): F[name]=np.asarray(val,dtype=np.float32)
    windows=[5,15,30,60,120,240]; retmap={}
    serh=pd.Series(mh); serl=pd.Series(ml)
    for w in windows:
        ret=(mc[idx]-mc[idx-w])/PIP; retmap[w]=ret; add(f'ret_{w}m',ret)
        sm=pr[idx+1]-pr[idx-w+1]; sm2=pr2[idx+1]-pr2[idx-w+1]
        vol=np.sqrt(np.maximum(sm2/w-(sm/w)**2,0.0)*w); add(f'vol_{w}m',vol)
        abs_sum=pa[idx+1]-pa[idx-w+1]
        add(f'eff_{w}m',np.abs(ret)/(abs_sum+1e-6))
        add(f'upfrac_{w}m',(pp[idx+1]-pp[idx-w+1])/w)
        add(f'dnfrac_{w}m',(pn[idx+1]-pn[idx-w+1])/w)
        hi=serh.rolling(w,min_periods=w).max().to_numpy()[idx]
        lo=serl.rolling(w,min_periods=w).min().to_numpy()[idx]
        ran=(hi-lo)/PIP; add(f'range_{w}m',ran)
        add(f'close_loc_{w}m',(mc[idx]-lo)/(hi-lo+1e-9))
        add(f'close_to_high_{w}m',(hi-mc[idx])/PIP)
        add(f'close_to_low_{w}m',(mc[idx]-lo)/PIP)
        del hi,lo,ran
    del serh,serl
    for short,long in [(5,60),(15,240),(30,120),(60,240)]:
        add(f'volratio_{short}_{long}',F[f'vol_{short}m']/(F[f'vol_{long}m']+0.05))
        add(f'rangeratio_{short}_{long}',F[f'range_{short}m']/(F[f'range_{long}m']+0.1))
    cr=np.maximum((mh[idx]-ml[idx])/PIP,0.01); body=(mc[idx]-mo[idx])/PIP
    add('last_body_pips',body); add('last_range_pips',cr); add('last_body_frac',body/cr)
    add('last_upper_wick_frac',(mh[idx]-np.maximum(mo[idx],mc[idx]))/(PIP*cr))
    add('last_lower_wick_frac',(np.minimum(mo[idx],mc[idx])-ml[idx])/(PIP*cr))
    add('last_close_loc',(mc[idx]-ml[idx])/(mh[idx]-ml[idx]+1e-9))
    add('ret_asym_15_60',retmap[15]-retmap[60]/4); add('ret_asym_60_240',retmap[60]-retmap[240]/4)
    add('spread_now_pips',spr[idx])
    for w in [15,60,240]:
        mean=(sprpref[idx+1]-sprpref[idx-w+1])/w
        add(f'spread_mean_{w}m',mean); add(f'spread_ratio_{w}m',spr[idx]/(mean+0.01))
    add('spread_over_vol15',spr[idx]/(F['vol_15m']+0.05))
    dt=pd.to_datetime(ts[idx],unit='ms',utc=True); hour=dt.hour.to_numpy()+dt.minute.to_numpy()/60.0; dow=dt.dayofweek.to_numpy()
    add('hour_sin',np.sin(2*np.pi*hour/24)); add('hour_cos',np.cos(2*np.pi*hour/24))
    add('weekday_sin',np.sin(2*np.pi*dow/5)); add('weekday_cos',np.cos(2*np.pi*dow/5))
    X=pd.DataFrame(F); finite=np.isfinite(X.to_numpy()).all(axis=1)
    idx=idx[finite]; X=X.loc[finite].reset_index(drop=True)
    print(f'Features: {X.shape[0]:,} rows x {X.shape[1]} columns, {time.time()-t0:.1f}s',flush=True)
    return idx,X

def build_labels(idx,ts,a):
    t0=time.time(); n=len(idx); pnl=np.full((n,2),np.nan,dtype=np.float32)
    ex=np.full((n,2),-1,dtype=np.int64); reason=np.zeros((n,2),dtype=np.int8)
    for k,i in enumerate(idx):
        ps,es,rs=simulate_one(int(i),-1,ts,a['bopen'],a['bhigh'],a['blow'],a['bclose'],a['aopen'],a['ahigh'],a['alow'],a['aclose'])
        pl,el,rl=simulate_one(int(i),1,ts,a['bopen'],a['bhigh'],a['blow'],a['bclose'],a['aopen'],a['ahigh'],a['alow'],a['aclose'])
        pnl[k,0]=ps; ex[k,0]=es; reason[k,0]=rs; pnl[k,1]=pl; ex[k,1]=el; reason[k,1]=rl
    good=np.isfinite(pnl).all(axis=1)&(ex>=0).all(axis=1)
    print(f'Labels: {int(good.sum()):,} timestamps / {2*int(good.sum()):,} side outcomes in {time.time()-t0:.1f}s',flush=True)
    return pnl,ex,reason,good

def metrics(trades,label):
    if not trades: return {'label':label,'trades':0,'verdict':'NO_TRADES'}
    d=pd.DataFrame(trades).sort_values('entry_ts'); p=d.pnl.to_numpy(float)
    gp=float(p[p>0].sum()); gl=float(-p[p<0].sum()); eq=np.cumsum(p); peak=np.maximum.accumulate(np.r_[0,eq]); dd=peak[1:]-eq
    dt=pd.to_datetime(d.exit_ts,unit='ms',utc=True)
    weeks=max(1,len(dt.dt.to_period('W').unique()))
    out={'label':label,'trades':int(len(d)),'net_pips':round(float(p.sum()),3),'mean_pips':round(float(p.mean()),4),
      'median_pips':round(float(np.median(p)),3),'win_rate':round(float((p>0).mean()),4),
      'profit_factor':round(gp/gl,4) if gl else None,'max_drawdown_pips':round(float(dd.max()) if len(dd) else 0,3),
      'trades_per_calendar_week':round(len(d)/weeks,3),'median_hold_min':round(float(d.hold_min.median()),2),
      'tp_fraction':round(float((d.reason==1).mean()),4),'sl_fraction':round(float((d.reason==2).mean()),4),
      'timeout_fraction':round(float((d.reason==3).mean()),4),'yearly':{}}
    d['year']=dt.dt.year
    for y,g in d.groupby('year'):
        q=g.pnl.to_numpy(float); gl_y=-q[q<0].sum(); gp_y=q[q>0].sum()
        out['yearly'][str(int(y))]={'trades':int(len(g)),'net_pips':round(float(q.sum()),3),'mean_pips':round(float(q.mean()),4),'pf':round(float(gp_y/gl_y),4) if gl_y else None}
    d['week']=dt.dt.to_period('W').astype(str); w=d.groupby('week').pnl.sum().to_numpy(float)
    out['weekly_net_mean']=round(float(w.mean()),4) if len(w) else None
    if len(w)>=12:
        rng=np.random.default_rng(32123); B=3000; L=4; vals=np.empty(B)
        for b in range(B):
            starts=rng.integers(0,len(w),size=int(np.ceil(len(w)/L))); sample=[]
            for st in starts: sample.extend(w[(np.arange(L)+st)%len(w)].tolist())
            vals[b]=np.mean(sample[:len(w)])
        out['weekly_bootstrap_95ci_mean_pips']=[round(float(np.quantile(vals,.025)),4),round(float(np.quantile(vals,.975)),4)]
        out['weekly_bootstrap_prob_positive_mean']=round(float((vals>0).mean()),4)
    else: out['weekly_bootstrap_95ci_mean_pips']=None
    return out

def run_policy(mask,idx,ts,pnl,ex,reason,side_choice,eligible,start_ts,end_ts):
    ii=np.flatnonzero(mask&eligible&(ts[idx+ENTRY_DELAY_ROWS]>=start_ts)&(ts[idx+ENTRY_DELAY_ROWS]<end_ts))
    trades=[]; busy_until=-1
    for k in ii:
        i=int(idx[k]); e=i+ENTRY_DELAY_ROWS
        if ts[e]<=busy_until: continue
        s=int(side_choice[k]); x=int(ex[k,s]); p=float(pnl[k,s])
        if x<0 or not np.isfinite(p): continue
        trades.append({'entry_ts':int(ts[e]),'exit_ts':int(ts[x]),'pnl':p,'hold_min':float((ts[x]-ts[e])/60000.0),
          'reason':int(reason[k,s]),'side':'LONG' if s==1 else 'SHORT','sample_i':i})
        busy_until=int(ts[x])
    return trades

def main():
    t0=time.time(); ts,a,manifest=load_quotes(); idx,X=make_features(ts,a); pnl,ex,reason,good=build_labels(idx,ts,a)
    idx=idx[good]; X=X.loc[good].reset_index(drop=True); pnl=pnl[good]; ex=ex[good]; reason=reason[good]
    years=pd.to_datetime(ts[idx],unit='ms',utc=True).year.to_numpy()
    train=years<=2019; valid=(years>=2020)&(years<=2021); fwd=(years>=2022)&(years<=2025)
    side=np.array([-1.0,1.0],dtype=np.float32); Xbase=X.to_numpy(dtype=np.float32); Xdup=np.repeat(Xbase,2,axis=0)
    sided=np.tile(side,len(X))[:,None]
    ret_cols=[j for j,c in enumerate(X.columns) if c.startswith('ret_') or c in ('last_body_pips','ret_asym_15_60','ret_asym_60_240')]
    signed=np.empty((len(Xdup),len(ret_cols)),dtype=np.float32)
    for z,j in enumerate(ret_cols): signed[:,z]=Xdup[:,j]*sided[:,0]
    Xtrain=np.column_stack([Xdup,sided,signed]).astype(np.float32,copy=False)
    names=list(X.columns)+['side_sign']+[f'signed_{X.columns[j]}' for j in ret_cols]
    y=np.column_stack([pnl[:,0],pnl[:,1]]).reshape(-1).astype(np.float32); train2=np.repeat(train,2)
    model=LGBMRegressor(objective='regression',n_estimators=350,learning_rate=0.035,num_leaves=23,max_depth=-1,
      min_child_samples=800,reg_lambda=8.0,reg_alpha=0.2,subsample=0.85,subsample_freq=1,colsample_bytree=0.85,
      n_jobs=4,random_state=20261023,verbosity=-1)
    print(f'Training on {int(train.sum()):,} timestamps / {int(train2.sum()):,} directional observations; {Xtrain.shape[1]} features',flush=True)
    tf=time.time(); model.fit(Xtrain[train2],y[train2]); fit_s=time.time()-tf
    pred=model.predict(Xtrain).astype(np.float32).reshape(-1,2); maxpred=np.maximum(pred[:,0],pred[:,1]); choice=(pred[:,1]>pred[:,0]).astype(np.int8)
    threshold=max(0.5,float(np.quantile(maxpred[valid],.75)))
    scored=[]
    for k in np.flatnonzero(valid|fwd):
        scored.append({'sample_ts':int(ts[idx[k]]),'year':int(years[k]),'pred_short':float(pred[k,0]),'pred_long':float(pred[k,1]),
          'chosen_side':'LONG' if choice[k] else 'SHORT','chosen_pred':float(maxpred[k]),
          'realized_pnl_selected_pips':float(pnl[k,choice[k]]),'long_pnl_pips':float(pnl[k,1]),'short_pnl_pips':float(pnl[k,0]),
          'long_hold_min':float((ts[ex[k,1]]-ts[idx[k]+ENTRY_DELAY_ROWS])/60000),
          'short_hold_min':float((ts[ex[k,0]]-ts[idx[k]+ENTRY_DELAY_ROWS])/60000)})
    pd.DataFrame(scored).to_csv(OUT/'market_response_v1_scored_events.csv',index=False)
    diagnostics={}
    for name,mask in [('train_in_sample',train),('validation_2020_2021',valid),('forward_diagnostic_2022_2025',fwd)]:
        pp=maxpred[mask].astype(float); yy=pnl[np.flatnonzero(mask),choice[mask]].astype(float)
        rho=float(spearmanr(pp,yy).statistic); qs=np.quantile(pp,np.linspace(0,1,11)); dec=[]
        for d in range(10):
            sel=(pp>=qs[d])&((pp<qs[d+1]) if d<9 else (pp<=qs[d+1])); z=yy[sel]
            dec.append({'low':round(float(qs[d]),4),'high':round(float(qs[d+1]),4),'n':int(sel.sum()),
              'mean_net_pips':round(float(z.mean()),4) if len(z) else None,'win_rate':round(float((z>0).mean()),4) if len(z) else None})
        diagnostics[name]={'n_events':int(mask.sum()),'spearman':round(rho,5),'mean_pips':round(float(yy.mean()),4),
          'top_quartile_mean_pips':round(float(yy[pp>=np.quantile(pp,.75)].mean()),4),
          'bottom_quartile_mean_pips':round(float(yy[pp<=np.quantile(pp,.25)].mean()),4),'deciles':dec}
    eligible=maxpred>=threshold
    periods={'validation_2020_2021':(pd.Timestamp('2020-01-01',tz='UTC').value//10**6,pd.Timestamp('2022-01-01',tz='UTC').value//10**6,valid),
      'forward_diagnostic_2022_2025':(pd.Timestamp('2022-01-01',tz='UTC').value//10**6,pd.Timestamp('2026-01-01',tz='UTC').value//10**6,fwd)}
    policy={}
    for name,(start,end,mask) in periods.items():
        ml=run_policy(mask,idx,ts,pnl,ex,reason,choice,eligible,start,end)
        allmask=np.ones(len(idx),dtype=bool)
        unfiltered=run_policy(mask,idx,ts,pnl,ex,reason,choice,allmask,start,end)
        mom_choice=(X['ret_60m'].to_numpy()>0).astype(np.int8)
        baseline=run_policy(mask,idx,ts,pnl,ex,reason,mom_choice,allmask,start,end)
        policy[name]={'selective_plus_0_5pip':metrics(ml,'selective_plus_0_5pip'),
          'selective_plus_1pip':metrics([{**z,'pnl':z['pnl']-0.5} for z in ml],'selective_plus_1pip'),
          'model_direction_unfiltered':metrics(unfiltered,'model_direction_unfiltered'),
          'baseline_60m_momentum':metrics(baseline,'baseline_60m_momentum'),
          'threshold_pips':round(float(threshold),4),'eligible_fraction':round(float((eligible&mask).sum()/max(1,mask.sum())),4)}
        if name.startswith('forward'): pd.DataFrame(ml).to_csv(OUT/'market_response_v1_forward_trades.csv',index=False)
    fi=pd.DataFrame({'feature':names,'importance_gain':model.booster_.feature_importance(importance_type='gain'),
       'importance_split':model.booster_.feature_importance(importance_type='split')}).sort_values('importance_gain',ascending=False)
    fi.to_csv(OUT/'market_response_v1_feature_importance.csv',index=False)
    summary={'id':'MRM-V1-EURUSD-M1-2016-2025','status':'EXPLORATORY_RUN_COMPLETE_NOT_FUNDED_APPROVED',
      'data':{**manifest,'source':'GitHub Actions artifact 11959096102','sample_n':int(len(idx)),'features':int(X.shape[1]),
        'feature_names':list(X.columns),'decision_cadence_minutes':30,'entry_delay_after_bar_close_minutes':5,'take_profit_pips':TP_PIPS,
        'stop_loss_pips':SL_PIPS,'max_hold_minutes':MAX_HOLD,'extra_cost_primary_pips':EXTRA_COST,'extra_cost_stress_total_pips':1.0,
        'barrier_tie_break':'SL first if TP and SL both touch in one M1 bar.'},
      'splits':{'train':'2016-2019','validation':'2020-2021; threshold uses score distribution only',
        'forward_diagnostic':'2022-2025; frozen model; not pristine program-level OOS'},
      'model':{'type':'LightGBM LGBMRegressor','fixed_parameters':{'n_estimators':350,'learning_rate':0.035,'num_leaves':23,
        'min_child_samples':800,'reg_lambda':8.0,'reg_alpha':0.2,'subsample':0.85,'colsample_bytree':0.85,'random_state':20261023},
        'fit_seconds':round(fit_s,2),'model_columns':int(Xtrain.shape[1]),'threshold_pips':round(float(threshold),4)},
      'prediction_diagnostics':diagnostics,'policy_results':policy,
      'limitations':['2020-2025 are not pristine program-level holdouts.','Not a FundedNext equity-aware challenge replay.',
        'Extra friction is a fixed sensitivity, not verified broker costs.','M1 OHLC intrabar ordering is approximate; SL-first is conservative.',
        'Overlapping event labels are not independent trades.','No 2026 EURUSD source data in this artifact; protected XAUUSD 2026 was not opened.'],
      'runtime_seconds':round(time.time()-t0,2)}
    with open(OUT/'market_response_v1_summary.json','w') as f: json.dump(summary,f,indent=2)
    print('Saved results:',OUT,flush=True)
if __name__=='__main__': main()
