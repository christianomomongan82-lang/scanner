#!/usr/bin/env python3
"""R274 local-only runner; imports the stored R272 BID/ASK execution primitives."""
from __future__ import annotations
import os, json, importlib.util
from pathlib import Path
import numpy as np
import pandas as pd
HERE = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get('R274_DATA_DIR', '/mnt/data/r272_xauusd/data_exports/xauusd_m5_2016_2026'))
OUT_DIR = Path(os.environ.get('R274_OUTPUT_DIR', str(DATA_DIR / 'results_r274')))
os.environ['R272_DATA_DIR'] = str(DATA_DIR)
os.environ['R272_OUTPUT_DIR'] = str(OUT_DIR)
spec = importlib.util.spec_from_file_location('r272_engine_for_r274', HERE / 'r272_xauusd_dual_module.py')
engine = importlib.util.module_from_spec(spec)
spec.loader.exec_module(engine)
END_HIST = pd.Timestamp('2026-01-01T00:00:00Z')
COSTS = [0.0, 0.1, 0.3, 0.5]
PRIMARY = 0.3
SEED = 2742026
REPS = 10000
def metric_by_cost(tr):
    return {f'cost_{engine.cost_to_key(c)}': engine.metrics(tr, c) for c in COSTS}
def bootstrap(tr, cost):
    return engine.bootstrap_weekly(tr, cost, reps=REPS, seed=SEED)
def subset(tr, lo, hi):
    if tr.empty: return tr.copy()
    ts = pd.to_datetime(tr['signal_bar_time_utc'], utc=True)
    return tr[(ts >= lo) & (ts < hi)].copy()
def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    q_full, audit = engine.load_quotes()
    q = q_full[q_full['timestamp_utc'] < END_HIST].copy().reset_index(drop=True)
    del q_full
    f = engine.features(q)
    f['valid_context'] = f['A'].gt(0) & f['grid_ok']
    eligible = np.flatnonzero(f['valid_context'].to_numpy() & q['ny_weekday'].to_numpy() & (q['ny_minute'].to_numpy() >= 360) & (q['ny_minute'].to_numpy() <= 950))
    op, hi, lo, cl = (q[k].to_numpy(float) for k in ('bid_open','bid_high','bid_low','bid_close'))
    ask_hi = q['ask_high'].to_numpy(float); a = f['A'].to_numpy(float)
    er = f['ER'].to_numpy(float); net = f['net_move'].to_numpy(float)
    events = []; long_n = short_n = 0
    for i in eligible:
        if i < 146 or not np.isfinite(a[i]) or a[i] <= 0: continue
        rg = hi[i] - lo[i]
        if not np.isfinite(rg) or rg <= 0: continue
        body = abs(cl[i] - op[i])
        if rg < 2.0*a[i] or body < 0.80*a[i] or body/rg < 0.65: continue
        er_i = float(er[i]) if np.isfinite(er[i]) else 0.0
        net_i = float(net[i]) if np.isfinite(net[i]) else 0.0
        if cl[i] > op[i] and (hi[i]-cl[i])/rg <= 0.20:
            sig = {'module':'A','direction':1,'stop':float(lo[i]),'target':None,'A':float(a[i]),'ER':er_i,'net_move':net_i}
            events.append((int(i),sig)); long_n += 1
        elif cl[i] < op[i] and (cl[i]-lo[i])/rg <= 0.20:
            sig = {'module':'A','direction':-1,'stop':float(ask_hi[i]),'target':None,'A':float(a[i]),'ER':er_i,'net_move':net_i}
            events.append((int(i),sig)); short_n += 1
    day_positions = {}
    for j, day in enumerate(q['ny_date'].to_numpy()): day_positions.setdefault(day, []).append(j)
    used_days=set(); busy_until=-1; rows=[]; skips={}; candidates=0
    for i, sig in events:
        day=q.at[i,'ny_date']
        if i <= busy_until or day in used_days: continue
        candidates += 1
        row=engine.build_trade_for_signal(q,day_positions,i,sig)
        if row is None:
            skips['invalid_delayed_entry_or_RR']=skips.get('invalid_delayed_entry_or_RR',0)+1
            continue
        row['stream']='impulse_followthrough'; row['signal_year']=int(pd.Timestamp(row['signal_bar_time_utc']).year); row['signal_month']=pd.Timestamp(row['signal_bar_time_utc']).strftime('%Y-%m')
        rows.append(row); used_days.add(day); busy_until=int(row['exit_index'])
    trades=pd.DataFrame(rows)
    d0=pd.Timestamp('2016-01-01T00:00:00Z'); d1=pd.Timestamp('2021-01-01T00:00:00Z')
    disc=subset(trades,d0,d1); val=subset(trades,d1,END_HIST)
    disc_boot=bootstrap(disc,PRIMARY); val_boot=bootstrap(val,PRIMARY)
    annual={}
    if not val.empty:
        tmp=val.copy(); tmp['_year']=pd.to_datetime(tmp['signal_bar_time_utc'],utc=True).dt.year
        annual={str(y):engine.metrics(g,PRIMARY) for y,g in tmp.groupby('_year')}
    gates={
      'discovery_at_least_100_trades_and_positive_net_R':len(disc)>=100 and engine.metrics(disc,PRIMARY)['net_r']>0,
      'discovery_bootstrap_lower_95_positive':disc_boot['ci95'][0] is not None and disc_boot['ci95'][0]>0,
      'validation_at_least_200_trades_and_positive_net_R':len(val)>=200 and engine.metrics(val,PRIMARY)['net_r']>0,
      'validation_positive_at_cost_0p50':engine.metrics(val,0.5)['net_r']>0,
      'at_least_3_of_5_validation_years_positive':sum(1 for v in annual.values() if v['net_r']>0)>=3
    }
    result={'round':'R274','verdict':'GAGAL' if not all(gates.values()) else 'HISTORICAL_SCREEN_PASS_2026_NOT_OPENED','source':'Dukascopy; raw-only artifact 12031270051','primary_extra_cost_usd_per_oz':PRIMARY,'data_audit':{k:v for k,v in audit.items() if k!='source_manifest'},'historical_rows_through_2025_only':len(q),'eligible_context_bars':int(len(eligible)),'raw_signals':{'long':long_n,'short':short_n},'accepted_trade_candidates':candidates,'closed_trades':len(trades),'execution_skips':skips,'discovery':{'cost_metrics':metric_by_cost(disc),'bootstrap_primary':disc_boot},'validation':{'cost_metrics':metric_by_cost(val),'bootstrap_primary':val_boot,'annual_primary_cost':annual},'historical_gates':gates,'holdout_2026_opened':False}
    (OUT_DIR/'R274_results.json').write_text(json.dumps(result,indent=2,allow_nan=False),encoding='utf-8')
    trades.drop(columns=['entry_index','exit_index'],errors='ignore').to_csv(OUT_DIR/'R274_impulse_followthrough_trade_ledger_development_only.csv',index=False,float_format='%.8f')
    print(json.dumps({'verdict':result['verdict'],'historical_gates':gates,'discovery':engine.metrics(disc,PRIMARY),'validation':engine.metrics(val,PRIMARY),'discovery_bootstrap':disc_boot,'validation_bootstrap':val_boot},indent=2,allow_nan=False))
if __name__=='__main__': main()