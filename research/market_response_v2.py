#!/usr/bin/env python3
"""MRM V2: gross midpoint response model plus independently locked spread gate.
Preregistered in GitHub before outcome calculations. Local research only.
"""
import json,time,sys
from pathlib import Path
import numpy as np,pandas as pd
from lightgbm import LGBMRegressor
from scipy.stats import spearmanr
sys.path.insert(0, str(Path(__file__).resolve().parent))
import market_response_v1 as v1
OUT=Path('/mnt/data/market_response_v2_results'); OUT.mkdir(exist_ok=True)
PIP=v1.PIP; DELAY=v1.ENTRY_DELAY_ROWS; HOLD=v1.MAX_HOLD; TP=v1.TP_PIPS; SL=v1.SL_PIPS

def mid_label(i,side,ts,a):
    e=i+DELAY; end=e+HOLD
    if end>=len(ts) or ts[e]-ts[i]!=DELAY*60000 or ts[end]-ts[e]!=HOLD*60000: return np.nan,-1,0
    mo=(a['bopen'][e]+a['aopen'][e])/2
    if side==1:
        target=mo+TP*PIP; stop=mo-SL*PIP
        for j in range(e,end+1):
            hi=(a['bhigh'][j]+a['ahigh'][j])/2; lo=(a['blow'][j]+a['alow'][j])/2
            if lo<=stop: return -SL,j,2
            if hi>=target: return TP,j,1
        return (((a['bclose'][end]+a['aclose'][end])/2)-mo)/PIP,end,3
    target=mo-TP*PIP; stop=mo+SL*PIP
    for j in range(e,end+1):
        hi=(a['bhigh'][j]+a['ahigh'][j])/2; lo=(a['blow'][j]+a['alow'][j])/2
        if hi>=stop: return -SL,j,2
        if lo<=target: return TP,j,1
    return (mo-((a['bclose'][end]+a['aclose'][end])/2))/PIP,end,3

def main():
    t0=time.time(); ts,a,manifest=v1.load_quotes(); idx,X=v1.make_features(ts,a)
    netp,ex,reason,good=v1.build_labels(idx,ts,a)
    gross=np.full((len(idx),2),np.nan,dtype=np.float32); gx=np.full((len(idx),2),-1,dtype=np.int64)
    for k,i in enumerate(idx):
        gross[k,0],gx[k,0],_=mid_label(int(i),-1,ts,a)
        gross[k,1],gx[k,1],_=mid_label(int(i),1,ts,a)
    good=good & np.isfinite(gross).all(axis=1) & (gx>=0).all(axis=1)
    idx=idx[good]; X=X.loc[good].reset_index(drop=True); netp=netp[good]; ex=ex[good]; reason=reason[good]; gross=gross[good]
    years=pd.to_datetime(ts[idx],unit='ms',utc=True).year.to_numpy()
    train=years<=2019; valid=(years>=2020)&(years<=2021); fwd=(years>=2022)&(years<=2025)
    removed=[c for c in X.columns if c.startswith('spread_') or c=='spread_over_vol15']
    X=X.drop(columns=removed); Xbase=X.to_numpy(dtype=np.float32); n=len(X)
    entry_spread=(a['aopen'][idx+DELAY]-a['bopen'][idx+DELAY])/PIP
    spread_limit=float(np.quantile(entry_spread[train],.90)); cost_ok=entry_spread<=spread_limit
    sides=np.array([-1.,1.],dtype=np.float32); Xdup=np.repeat(Xbase,2,axis=0); sidecol=np.tile(sides,n)[:,None]
    ret_cols=[j for j,c in enumerate(X.columns) if c.startswith('ret_') or c in ('last_body_pips','ret_asym_15_60','ret_asym_60_240')]
    signed=np.column_stack([Xdup[:,j]*sidecol[:,0] for j in ret_cols]).astype(np.float32)
    XX=np.column_stack([Xdup,sidecol,signed]).astype(np.float32,copy=False)
    yy=np.column_stack([gross[:,0],gross[:,1]]).reshape(-1).astype(np.float32); train2=np.repeat(train,2)
    model=LGBMRegressor(objective='regression',n_estimators=350,learning_rate=0.035,num_leaves=23,min_child_samples=800,reg_lambda=8,reg_alpha=0.2,subsample=0.85,subsample_freq=1,colsample_bytree=0.85,n_jobs=4,random_state=20261023,verbosity=-1)
    tf=time.time(); model.fit(XX[train2],yy[train2]); fit_s=time.time()-tf
    pred=model.predict(XX).astype(np.float32).reshape(-1,2); score=np.maximum(pred[:,0],pred[:,1]); choice=(pred[:,1]>pred[:,0]).astype(np.int8)
    threshold=max(1.0,float(np.quantile(score[valid],.75))); eligible=(score>=threshold)&cost_ok
    diagnostics={}
    for name,mask in [('train_in_sample',train),('validation_2020_2021',valid),('forward_diagnostic_2022_2025',fwd)]:
        pg=score[mask].astype(float); rg=gross[np.flatnonzero(mask),choice[mask]].astype(float); rn=netp[np.flatnonzero(mask),choice[mask]].astype(float)
        diagnostics[name]={'events':int(mask.sum()),'spearman_gross':round(float(spearmanr(pg,rg).statistic),5),'spearman_net':round(float(spearmanr(pg,rn).statistic),5),'mean_gross':round(float(rg.mean()),4),'mean_net':round(float(rn.mean()),4),'top_quartile_gross':round(float(rg[pg>=np.quantile(pg,.75)].mean()),4),'top_quartile_net':round(float(rn[pg>=np.quantile(pg,.75)].mean()),4)}
    policy={}; periods={'validation':(pd.Timestamp('2020-01-01',tz='UTC').value//10**6,pd.Timestamp('2022-01-01',tz='UTC').value//10**6,valid),'forward':(pd.Timestamp('2022-01-01',tz='UTC').value//10**6,pd.Timestamp('2026-01-01',tz='UTC').value//10**6,fwd)}
    for name,(start,end,mask) in periods.items():
        selected=v1.run_policy(mask,idx,ts,netp,ex,reason,choice,eligible,start,end,'mrm_v2_selected')
        cost_only=v1.run_policy(mask,idx,ts,netp,ex,reason,choice,cost_ok,start,end,'mrm_v2_direction_no_score_filter')
        mom=(X['ret_60m'].to_numpy()>0).astype(np.int8)
        baseline=v1.run_policy(mask,idx,ts,netp,ex,reason,mom,cost_ok,start,end,'baseline_60m_momentum_cost_gate')
        policy[name]={'selected_plus_0_5':v1.metrics(selected,'selected_plus_0_5'),'selected_plus_1_0':v1.metrics([{**z,'pnl':z['pnl']-0.5} for z in selected],'selected_plus_1_0'),'model_direction_cost_gate':v1.metrics(cost_only,'model_direction_cost_gate'),'momentum_cost_gate':v1.metrics(baseline,'momentum_cost_gate'),'threshold_gross_pips':round(float(threshold),4),'spread_p90_training_pips':round(spread_limit,4),'eligible_fraction':round(float((eligible&mask).sum()/max(1,mask.sum())),4)}
        if name=='forward': pd.DataFrame(selected).to_csv(OUT/'market_response_v2_forward_trades.csv',index=False)
    fi=pd.DataFrame({'feature':list(X.columns)+['side_sign']+[f'signed_{X.columns[j]}' for j in ret_cols],'importance_gain':model.booster_.feature_importance(importance_type='gain'),'importance_split':model.booster_.feature_importance(importance_type='split')}).sort_values('importance_gain',ascending=False)
    fi.to_csv(OUT/'market_response_v2_feature_importance.csv',index=False)
    out={'id':'MRM-V2-GROSS-ALPHA-COST-DECOMPOSITION','verdict':'GAGAL','source':manifest|{'artifact_id':11959096102,'rows_decision_points':int(len(idx))},'method':{'train':'2016-2019','validation':'2020-2021','forward_diagnostic':'2022-2025 (contaminated at program level)','decision_cadence_min':30,'entry_delay_min':5,'tp_pips':TP,'sl_pips':SL,'max_hold_min':HOLD,'threshold_gross_pips':round(float(threshold),4),'spread_p90_training_pips':round(spread_limit,4),'extra_cost_primary_pips':0.5,'extra_cost_stress_pips':1.0,'model_fit_seconds':round(fit_s,2)},'diagnostics':diagnostics,'policy':policy,'limitations':['Not a FundedNext challenge replay','2020-2025 not pristine OOS','nominal barrier fills; gap-through slippage not modeled','SL-first when both barriers touch same M1 bar','extra cost is assumed, not broker-verified','protected XAUUSD 2026 not opened'],'runtime_seconds':round(time.time()-t0,2)}
    json.dump(out,open(OUT/'market_response_v2_summary.json','w'),indent=2)
    print(json.dumps({'diagnostics':diagnostics,'policy':policy,'runtime_seconds':out['runtime_seconds']},indent=2),flush=True)
if __name__=='__main__': main()
