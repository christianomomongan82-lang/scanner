#!/usr/bin/env python3
"""R213: preregistered US cash-session breakout of the overnight price range.

Discovery is processed for all four US indices, then selection is frozen on
2017-2021 only. Forward/OOS are calculated only for that locked selection.
Raw M5 BID OHLC only; no standard indicators; session times use New York DST.
"""
from __future__ import annotations
import json, math
from pathlib import Path
import numpy as np
import pandas as pd

DATA = Path('/content/drive/MyDrive/dukascopy_idx')
OUT = Path('results/r213')
TZ = 'America/New_York'
RR = 2.0
ASSETS = {
    'usa500idxusd': 'USA 500 / S&P 500',
    'usatechidxusd': 'USA 100 Tech / Nasdaq 100',
    'usa30idxusd': 'USA 30 / Dow Jones',
    'ussc2000idxusd': 'US Small Cap 2000',
}
D0 = pd.Timestamp('2017-01-01', tz='UTC')
D1 = pd.Timestamp('2022-01-01', tz='UTC')
F0 = D1
F1 = pd.Timestamp('2026-01-01', tz='UTC')
O0 = F1

RULE = {
    'id': 'R213_US_OVERNIGHT_RANGE_FIRST_BREAKOUT_RR2',
    'overnight_range': 'active M5 BID bars timestamped 00:00 through 09:25 America/New_York inclusive; exact 114 five-minute timestamp grid required',
    'valid_overnight': 'all 114 timestamps present and at least 60 non-flat M5 bars; flat synthetic bars excluded from range extrema',
    'cash_session': '09:30 through 15:55 New York time, exact 78-bar timestamp grid required, at least 60 non-flat bars and a non-flat 15:55 bar',
    'signal': 'first non-flat M5 close after/at 09:30 and strictly before 15:55 whose close is above overnight high or below overnight low',
    'direction': 'long if close > overnight high, short if close < overnight low',
    'entry': 'next non-flat M5 bar open; must be before 15:55 New York time on the same date',
    'stop': 'signal M5 candle low for long, signal candle high for short',
    'target': '2R from actual entry-to-stop risk',
    'attempt_limit': 'one first-breakout attempt per instrument per valid New York session date',
    'exit': 'M5 BID OHLC; stop checked before target when both touched; gaps through stop fill at open; if still open, executable scheduled exit at 15:55 M5 open (before final bar range develops)',
    'cost_model': 'modeled round-trip cost = entry * (1 or 2 price basis points) / 10000; not actual spread, commission, financing, or live slippage',
    'selection': 'discovery only: >=50 closed discovery trades and PF@2bps >=1.00; select highest discovery closed trade count, then PF@2bps; no forward metrics for non-selected instruments',
    'periods': {'discovery': 'entry UTC 2017-01-01 to 2022-01-01; exits before 2022-01-01', 'forward': 'entry UTC 2022-01-01 to 2026-01-01; exits before 2026-01-01', 'oos': 'entry 2026 through common M5 data cutoff'},
}

def load_m5(path: Path):
    x = pd.read_csv(path)
    x.columns = [str(c).replace('\ufeff','').strip().lower() for c in x.columns]
    tcol = next((c for c in ('timestamp','time','t','date','datetime') if c in x.columns), None)
    if tcol is None: raise ValueError(f'{path}: timestamp column missing')
    ts = x.pop(tcol)
    num = pd.to_numeric(ts, errors='coerce')
    if num.notna().mean() > .95:
        med = float(num.abs().median())
        if med >= 1e11: idx = pd.to_datetime(num, unit='ms', utc=True, errors='coerce')
        elif med >= 1e8: idx = pd.to_datetime(num, unit='s', utc=True, errors='coerce')
        else: raise ValueError(f'{path}: unknown timestamp scale {med}')
    else: idx = pd.to_datetime(ts, utc=True, errors='coerce')
    cols = ['open','high','low','close']
    if idx.isna().any() or set(cols)-set(x.columns): raise ValueError(f'{path}: invalid timestamps or columns')
    x = x[cols].apply(pd.to_numeric, errors='coerce')
    if x.isna().any().any() or not np.isfinite(x.to_numpy(float)).all(): raise ValueError(f'{path}: invalid OHLC values')
    x.index = pd.DatetimeIndex(idx, name='timestamp_utc')
    x = x.sort_index()
    dups = int(x.index.duplicated(keep='last').sum())
    if dups: x = x.loc[~x.index.duplicated(keep='last')]
    if not x.index.is_monotonic_increasing or x.index.has_duplicates: raise ValueError(f'{path}: time index invalid')
    off_grid = int(((x.index.minute % 5 != 0) | (x.index.second != 0) | (x.index.microsecond != 0)).sum())
    if off_grid: raise ValueError(f'{path}: {off_grid} timestamps are not aligned to five minutes')
    x.index = x.index.tz_convert(TZ)
    flat = (x.open.to_numpy()==x.high.to_numpy()) & (x.high.to_numpy()==x.low.to_numpy()) & (x.low.to_numpy()==x.close.to_numpy())
    diag = {'rows':len(x), 'duplicates_removed':dups, 'off_grid_timestamps':off_grid,
            'flat_rows':int(flat.sum()), 'start_utc':x.index[0].tz_convert('UTC').isoformat(),
            'end_utc':x.index[-1].tz_convert('UTC').isoformat()}
    return x, flat, diag

def expected_grid(day, start_minute, n):
    start = pd.Timestamp(day).tz_localize(TZ) + pd.Timedelta(minutes=start_minute)
    return pd.date_range(start, periods=n, freq='5min')

def session_setup(day_df: pd.DataFrame, day: str, flat_all: np.ndarray):
    """Causal one-session setup builder from only that date's timestamped M5 bars."""
    mins = day_df.index.hour*60 + day_df.index.minute
    on_mask = (mins >= 0) & (mins <= 565)
    rth_mask = (mins >= 570) & (mins <= 955)
    on = day_df.loc[on_mask]
    rth = day_df.loc[rth_mask]
    if not on.index.equals(expected_grid(day, 0, 114)):
        return None, {'date':day,'valid':False,'reason':'overnight grid incomplete','overnight_rows':len(on),'rth_rows':len(rth)}
    if not rth.index.equals(expected_grid(day, 570, 78)):
        return None, {'date':day,'valid':False,'reason':'cash-session grid incomplete','overnight_rows':len(on),'rth_rows':len(rth)}
    on_flat = flat_all[day_df.index.get_indexer(on.index)]
    active_on = on.loc[~on_flat]
    rth_flat = flat_all[day_df.index.get_indexer(rth.index)]
    active_rth_n = int((~rth_flat).sum())
    if len(active_on) < 60:
        return None, {'date':day,'valid':False,'reason':'fewer than 60 non-flat overnight bars','overnight_nonflat':len(active_on),'rth_nonflat':active_rth_n}
    if active_rth_n < 60:
        return None, {'date':day,'valid':False,'reason':'fewer than 60 non-flat cash-session bars','overnight_nonflat':len(active_on),'rth_nonflat':active_rth_n}
    if bool(rth_flat[-1]):
        return None, {'date':day,'valid':False,'reason':'15:55 scheduled exit open is flat/non-executable','overnight_nonflat':len(active_on),'rth_nonflat':active_rth_n}
    overnight_high = float(active_on.high.max())
    overnight_low = float(active_on.low.min())
    if not (math.isfinite(overnight_high) and math.isfinite(overnight_low) and overnight_high > overnight_low):
        return None, {'date':day,'valid':False,'reason':'invalid overnight range','overnight_nonflat':len(active_on),'rth_nonflat':active_rth_n}
    signal_idx = None; direction = 0
    for i in range(len(rth)-1):
        if rth_flat[i]: continue
        c = float(rth.close.iloc[i])
        if c > overnight_high: signal_idx=i; direction=1; break
        if c < overnight_low: signal_idx=i; direction=-1; break
    signal_bar = rth.iloc[signal_idx] if signal_idx is not None else None
    stop = (float(signal_bar.low if direction==1 else signal_bar.high) if signal_bar is not None else None)
    diag = {'date':day,'valid':True,'reason':'no breakout close' if signal_idx is None else 'first overnight-range breakout close',
            'overnight_rows':len(on),'overnight_nonflat':len(active_on),'rth_rows':len(rth),'rth_nonflat':active_rth_n,
            'overnight_high':overnight_high,'overnight_low':overnight_low,
            'signal_timestamp_ny':None if signal_idx is None else rth.index[signal_idx].isoformat(),
            'direction':None if not direction else ('long' if direction==1 else 'short')}
    base = {'session_date_ny':day,'direction':('long' if direction==1 else 'short' if direction==-1 else None),
            'direction_sign':direction,'overnight_high':overnight_high,'overnight_low':overnight_low,
            'signal_time_ny':None if signal_idx is None else rth.index[signal_idx].isoformat(),
            'signal_time_utc':None if signal_idx is None else rth.index[signal_idx].tz_convert('UTC').isoformat(),
            'signal_open':None if signal_bar is None else float(signal_bar.open),
            'signal_high':None if signal_bar is None else float(signal_bar.high),
            'signal_low':None if signal_bar is None else float(signal_bar.low),
            'signal_close':None if signal_bar is None else float(signal_bar.close),
            'sl':stop,'signal_index_in_rth':signal_idx,'entry_index_in_rth':None,
            'rth_open_times':rth.index,'rth_open':rth.open.to_numpy(float),
            'rth_high':rth.high.to_numpy(float),'rth_low':rth.low.to_numpy(float),
            'rth_close':rth.close.to_numpy(float),'rth_flat':rth_flat,'trade_eligible':False}
    if signal_idx is None: return base, diag
    entry_idx = next((j for j in range(signal_idx+1, len(rth)-1) if not rth_flat[j]), None)
    if entry_idx is None:
        diag['reason']='signal exists but no non-flat entry before 15:55'; return base,diag
    entry_time = rth.index[entry_idx]
    entry = float(rth.open.iloc[entry_idx])
    risk = (entry-stop) if direction==1 else (stop-entry)
    if not math.isfinite(risk) or risk <= 0:
        diag['reason']='signal exists but entry-to-stop risk is invalid'; return base,diag
    target = entry + direction*RR*risk
    base.update({'entry_time_ny':entry_time.isoformat(),'entry_time_utc':entry_time.tz_convert('UTC').isoformat(),
        'entry':entry,'tp':target,'risk_points':float(risk),'entry_index_in_rth':entry_idx,'trade_eligible':True})
    return base, diag

def simulate_one(setup, instrument):
    d=setup['direction_sign']; entry=setup['entry']; stop=setup['sl']; target=setup['tp']; r=setup['rth_open_times']
    op=setup['rth_open']; hi=setup['rth_high']; lo=setup['rth_low']; flat=setup['rth_flat']
    entry_i=setup['entry_index_in_rth']; end_i=len(r)-1
    exit_t=None; exit_px=None; reason=None
    for j in range(entry_i, end_i):
        if flat[j]: continue
        o=float(op[j]); h=float(hi[j]); l=float(lo[j])
        stop_hit = (l <= stop or o <= stop) if d==1 else (h >= stop or o >= stop)
        target_hit = (h >= target) if d==1 else (l <= target)
        if stop_hit:
            exit_px = o if ((o <= stop) if d==1 else (o >= stop)) else stop
            reason='SL_GAP_OPEN' if exit_px != stop else 'SL'
            exit_t=r[j]+pd.Timedelta(minutes=5); break
        if target_hit:
            exit_px=target; reason='TP'; exit_t=r[j]+pd.Timedelta(minutes=5); break
    if exit_t is None:
        o=float(op[end_i]); target_gap = (o >= target) if d==1 else (o <= target)
        stop_gap = (o <= stop) if d==1 else (o >= stop)
        if stop_gap:
            exit_px=o; reason='SL_GAP_OPEN'; exit_t=r[end_i]
        elif target_gap:
            exit_px=target; reason='TP_GAP_OPEN'; exit_t=r[end_i]
        else:
            exit_px=o; reason='SESSION_CUTOFF_OPEN'; exit_t=r[end_i]
    trade={k:v for k,v in setup.items() if k not in ('direction_sign','signal_index_in_rth','entry_index_in_rth','rth_open_times','rth_open','rth_high','rth_low','rth_close','rth_flat')}
    trade.update({'instrument':instrument,'instrument_name':ASSETS[instrument],'config':RULE['id'],
        'exit_time_ny':exit_t.isoformat(),'exit_time_utc':exit_t.tz_convert('UTC').isoformat(),'exit':float(exit_px),
        'reason':reason,'cost_1bp_price':entry/10000.0,
        'bars_to_exit':int(round((exit_t-r[entry_i]).total_seconds()/300))})
    return trade

def make_trades(m5, flat_all, inst):
    trades=[]; day_diags=[]; causal_checks=0
    flat_series=pd.Series(flat_all,index=m5.index)
    for day_obj, day_df in m5.groupby(m5.index.date, sort=False):
        day=str(day_obj); flat_day=flat_series.loc[day_df.index].to_numpy(bool)
        setup,diag=session_setup(day_df,day,flat_day); day_diags.append(diag)
        if setup is None: continue
        sig_i=setup['signal_index_in_rth']; r_times=setup['rth_open_times']; d=setup['direction_sign']
        expected_sig=None if sig_i is None else sig_i
        first_seen=None; stop_prefix=None
        for k in range(len(r_times)-1):
            if first_seen is None and not setup['rth_flat'][k]:
                close_k=float(setup['rth_close'][k])
                if close_k>setup['overnight_high']:
                    first_seen=k; stop_prefix=float(setup['rth_low'][k])
                elif close_k<setup['overnight_low']:
                    first_seen=k; stop_prefix=float(setup['rth_high'][k])
            prefix_expected=expected_sig if expected_sig is not None and expected_sig<=k else None
            if first_seen!=prefix_expected:
                raise RuntimeError(f'CAUSAL GATE FAIL {inst} {day} prefix {k}: incremental={first_seen}, expected={prefix_expected}')
            if first_seen is not None:
                expected_stop=float(setup['rth_low'][first_seen]) if d==1 else float(setup['rth_high'][first_seen])
                if not np.isclose(stop_prefix,expected_stop,rtol=0,atol=1e-12):
                    raise RuntimeError(f'STOP GATE FAIL {inst} {day} prefix {k}')
            causal_checks+=1
        if expected_sig is not None:
            sig_time=pd.Timestamp(setup['signal_time_ny'])
            prefix_end=sig_time
            prefix_df=day_df.loc[day_df.index<=prefix_end]
            if prefix_df.empty or prefix_df.index.max()!=prefix_end:
                raise RuntimeError(f'CAUSAL TRUNCATION GATE FAIL {inst} {day}: signal timestamp absent from prefix')
            pm=prefix_df.index.hour*60+prefix_df.index.minute
            pon=prefix_df.loc[(pm>=0)&(pm<=565)]
            pflat_all=flat_day[np.asarray(day_df.index<=prefix_end)]
            pflat=pflat_all[np.asarray((pm>=0)&(pm<=565))]
            if not pon.index.equals(expected_grid(day,0,114)):
                raise RuntimeError(f'CAUSAL TRUNCATION GATE FAIL {inst} {day}: overnight grid changed')
            pon_active=pon.loc[~pflat]
            if len(pon_active)<60:
                raise RuntimeError(f'CAUSAL TRUNCATION GATE FAIL {inst} {day}: insufficient causal overnight observations')
            ph=float(pon_active.high.max()); pl=float(pon_active.low.min())
            mask=(pm>=570)&(pm<=int(sig_time.hour*60+sig_time.minute))
            prth=prefix_df.loc[mask]; prth_flat=pflat_all[np.asarray(mask)]
            pi=None; pdir=0
            for jj in range(len(prth)):
                if prth_flat[jj]: continue
                cc=float(prth.close.iloc[jj])
                if cc>ph: pi=jj; pdir=1; break
                if cc<pl: pi=jj; pdir=-1; break
            if pi is None or prth.index[pi]!=sig_time or pdir!=d:
                raise RuntimeError(f'CAUSAL TRUNCATION GATE FAIL {inst} {day}: truncated signal differs')
            pst=float(prth.low.iloc[pi] if pdir==1 else prth.high.iloc[pi])
            if not np.isclose(pst,float(setup['sl']),rtol=0,atol=1e-12):
                raise RuntimeError(f'CAUSAL TRUNCATION GATE FAIL {inst} {day}: truncated stop differs')
        if setup.get('trade_eligible',False):
            trades.append(simulate_one(setup,inst))
    return trades,day_diags,causal_checks

def pnl_r(t,bps):
    d=1 if t['direction']=='long' else -1
    gross=d*(float(t['exit'])-float(t['entry']))
    cost=float(t['entry'])*bps/10000.0
    return (gross-cost)/float(t['risk_points'])

def metric(trades,start,end,outcome_cutoff,bps):
    chosen=[t for t in trades if start<=pd.Timestamp(t['entry_time_utc'])<end]
    closed=[t for t in chosen if pd.Timestamp(t['exit_time_utc'])<outcome_cutoff]
    vals=np.asarray([pnl_r(t,bps) for t in closed],dtype=float)
    wins=float(vals[vals>0].sum()) if len(vals) else 0.0
    losses=float(-vals[vals<0].sum()) if len(vals) else 0.0
    pf=(wins/losses if losses>0 else (float('inf') if wins>0 else float('nan')))
    return {'entries':len(chosen),'closed':len(closed),'censored':len(chosen)-len(closed),'pf':pf,'wins_r':wins,'losses_r':losses}

def finite(x): return isinstance(x,(int,float,np.integer,np.floating)) and math.isfinite(float(x))
def json_safe(x):
    if isinstance(x,dict): return {str(k):json_safe(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [json_safe(v) for v in x]
    if isinstance(x,(np.integer,)): return int(x)
    if isinstance(x,(np.floating,float)):
        if math.isnan(float(x)): return None
        if math.isinf(float(x)): return 'INF' if x>0 else '-INF'
        return float(x)
    if isinstance(x,pd.Timestamp): return x.isoformat()
    return x

def main():
    parsed={}; flatmaps={}; data_diag={}
    print('R213: local source/data checks',flush=True)
    for inst in ASSETS:
        x,flat,d=load_m5(DATA/f'{inst}_m5.csv')
        parsed[inst]=x; flatmaps[inst]=flat; data_diag[inst]=d
        print(f'  {inst}: rows={len(x):,}, duplicates={d["duplicates_removed"]}, flat={d["flat_rows"]:,}, end={d["end_utc"]}',flush=True)
    discovery_trades={}; discovery_rows=[]; diags={}; gate_counts={}
    print('R213: discovery only (2017-2021); forward metrics not yet calculated',flush=True)
    for inst,x in parsed.items():
        disc_mask=(x.index.tz_convert('UTC')>=D0) & (x.index.tz_convert('UTC')<D1)
        xdisc=x.loc[disc_mask]; fdisc=flatmaps[inst][np.asarray(disc_mask)]
        t,days,checks=make_trades(xdisc,fdisc,inst)
        discovery_trades[inst]=t; diags[inst]=days; gate_counts[inst]=checks
        for bps in (1,2):
            discovery_rows.append({'instrument':inst,'instrument_name':ASSETS[inst],'cost_bps_rt':bps,**metric(t,D0,D1,D1,bps)})
        print(f'  {inst}: discovery valid/trade sessions={sum(d.get("valid",False) for d in days):,}/{len(t):,}; causal prefix checks={checks:,}',flush=True)
    dd=pd.DataFrame(discovery_rows); piv=dd.pivot(index='instrument',columns='cost_bps_rt',values=['closed','pf'])
    selection=[]
    for inst in ASSETS:
        n=int(piv.loc[inst,('closed',1)]); pf1=float(piv.loc[inst,('pf',1)]); pf2=float(piv.loc[inst,('pf',2)])
        eligible=n>=50 and math.isfinite(pf2) and pf2>=1.0
        selection.append({'instrument':inst,'instrument_name':ASSETS[inst],'discovery_closed':n,
            'discovery_pf_1bp':pf1,'discovery_pf_2bp':pf2,'eligible':eligible,
            'selection_rule':'eligible by discovery only; highest closed count, then PF@2bp'})
    elig=[r for r in selection if r['eligible']]
    elig.sort(key=lambda r:(-r['discovery_closed'],-r['discovery_pf_2bp'],r['instrument']))
    selected=dict(elig[0]) if elig else None
    (OUT/'discovery_selection.json').write_text(json.dumps(json_safe({'rule':RULE,'discovery_ledger':selection,'selected':selected}),indent=2))
    forward_rows=[]; cohorts=[]; oos_rows=[]; full_selected_trades=[]; selected_gate_count=0
    if selected:
        inst=selected['instrument']; x=parsed[inst]
        mask=x.index.tz_convert('UTC')<pd.Timestamp('2026-10-10T00:00:00Z')
        xf=x.loc[mask]; ff=flatmaps[inst][np.asarray(mask)]
        tr,days,checks=make_trades(xf,ff,inst)
        full_selected_trades=tr; selected_gate_count=checks
        common_end=min(pd.Timestamp(d['end_utc'])+pd.Timedelta(minutes=5) for d in data_diag.values())
        for bps in (1,2):
            forward_rows.append({'instrument':inst,'instrument_name':ASSETS[inst],'cost_bps_rt':bps,**metric(tr,F0,F1,F1,bps)})
            oos_rows.append({'instrument':inst,'instrument_name':ASSETS[inst],'cost_bps_rt':bps,**metric(tr,O0,common_end,common_end,bps)})
        for year in range(2022,2026):
            st=pd.Timestamp(f'{year}-01-01',tz='UTC'); en=pd.Timestamp(f'{year+1}-01-01',tz='UTC')
            for bps in (1,2): cohorts.append({'instrument':inst,'entry_year':year,'cost_bps_rt':bps,**metric(tr,st,en,F1,bps)})
        fwd1=next(r for r in forward_rows if r['cost_bps_rt']==1); fwd2=next(r for r in forward_rows if r['cost_bps_rt']==2)
        eligible_coh=[c for c in cohorts if c['cost_bps_rt']==1 and c['closed']>=5]
        worst=min((c['pf'] for c in eligible_coh if finite(c['pf'])),default=None)
        count_ok=fwd1['closed']>=30
        pfs_ok=finite(fwd1['pf']) and fwd1['pf']>=1.15 and finite(fwd2['pf']) and fwd2['pf']>=1.15
        year_ok=all(finite(c['pf']) and c['pf']>=1.0 for c in eligible_coh)
        normal=count_ok and pfs_ok and year_ok
        high_pf=(finite(fwd1['pf']) and fwd1['pf']>1.4) or (finite(fwd2['pf']) and fwd2['pf']>1.4)
        verdict='HOLD_EXTRA_AUDIT' if normal and high_pf else 'PASS' if normal else 'REJECT'
        selected.update({'forward_closed':fwd1['closed'],'forward_pf_1bp':fwd1['pf'],'forward_pf_2bp':fwd2['pf'],
            'forward_trades_gate_pass':count_ok,'forward_both_costs_gate_pass':pfs_ok,'forward_cohort_gate_pass':year_ok,
            'worst_eligible_forward_cohort_pf_1bp':worst,'high_pf_extra_audit_required':bool(normal and high_pf),'verdict':verdict})
        for r in oos_rows: r['common_oos_cutoff_utc']=common_end.isoformat()
        for c in cohorts:
            c['cohort_gate_applicable']=c['cost_bps_rt']==1 and c['closed']>=5
            c['cohort_gate_pass']=None if not c['cohort_gate_applicable'] else bool(finite(c['pf']) and c['pf']>=1.0)
    else:
        common_end=min(pd.Timestamp(d['end_utc'])+pd.Timedelta(minutes=5) for d in data_diag.values())
        verdict='REJECT_IN_DISCOVERY_NO_ELIGIBLE_INSTRUMENT'
    disc_cohorts=[]
    for inst,t in discovery_trades.items():
        for year in range(2017,2022):
            st=pd.Timestamp(f'{year}-01-01',tz='UTC'); en=pd.Timestamp(f'{year+1}-01-01',tz='UTC')
            for bps in (1,2): disc_cohorts.append({'instrument':inst,'entry_year':year,'cost_bps_rt':bps,**metric(t,st,en,D1,bps)})
    dd.to_csv(OUT/'discovery_ledger.csv',index=False)
    pd.DataFrame(disc_cohorts).to_csv(OUT/'discovery_annual_cohorts.csv',index=False)
    pd.DataFrame(forward_rows).to_csv(OUT/'selected_forward_ledger.csv',index=False)
    pd.DataFrame(cohorts).to_csv(OUT/'selected_forward_annual_cohorts.csv',index=False)
    pd.DataFrame(oos_rows).to_csv(OUT/'selected_oos_ledger.csv',index=False)
    pd.DataFrame(full_selected_trades).to_csv(OUT/'selected_all_trades.csv',index=False)
    meta={'research':'R213 local preregistered overnight-range breakout','rule':RULE,'source':'Dukascopy BID M5 OHLC snapshot',
          'run_utc':pd.Timestamp.now(tz='UTC').isoformat(),'data':data_diag,'selection_ledger':selection,
          'selected':selected,'verdict':verdict,'common_oos_cutoff_utc':common_end.isoformat(),
          'selected_causal_prefix_checks':selected_gate_count,'discovery_causal_prefix_checks':gate_counts,
          'audit_notes':['No forward PFs were calculated for discovery-ineligible or non-selected symbols.',
                         'BID-only OHLC; 1/2 bps are modeled round-trip price costs, not verified execution costs.',
                         'All flat M5 bars excluded from overnight range extrema, signal detection, entry, and in-position intrabar execution.',
                         'Scheduled session liquidation occurs at 15:55 bar open, before that bar’s high/low develops; 15:55 must be a non-flat source bar.',
                         'The signal M5 close is known at the next five-minute boundary; entry is a later M5 open, never earlier than signal close.']}
    (OUT/'meta.json').write_text(json.dumps(json_safe(meta),indent=2))
    print('\nDISCOVERY LEDGER (forward not used for selection):')
    print(pd.DataFrame(selection).to_string(index=False))
    print('\nSELECTED FORWARD LEDGER:')
    print(pd.DataFrame(forward_rows).to_string(index=False) if forward_rows else 'Not calculated; no eligible discovery candidate.')
    print('\nSELECTED FORWARD ENTRY-YEAR COHORTS:')
    print(pd.DataFrame(cohorts).to_string(index=False) if cohorts else 'Not applicable.')
    print('\nSELECTED OOS LEDGER:')
    print(pd.DataFrame(oos_rows).to_string(index=False) if oos_rows else 'Not applicable.')
    print('\nVERDICT:',verdict,'; outputs:',OUT,flush=True)

if __name__=='__main__': main()
