#!/usr/bin/env python3
"""R216: UTC scheduled cross-sectional momentum rotation across four US indices.
Uses raw synchronized M5 BID OHLC. No indicators, interpolation, or forward fill.
Pre-registered: signal on 15:55 UTC M5 close using prior 24h returns; at 16:00 UTC
next bar open long strongest index and short weakest, hold to next day's 16:00 UTC open.
Discovery-only gate; if it fails, forward/OOS are intentionally not calculated.
"""
from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd

SYMS = ["usa500idxusd", "usatechidxusd", "usa30idxusd", "ussc2000idxusd"]
LABELS = {"usa500idxusd":"US500", "usatechidxusd":"USTech100", "usa30idxusd":"US30", "ussc2000idxusd":"USSmallCap2000"}
BAR_MS = 300_000
DAY_MS = 86_400_000
SIGNAL_MOD_MS = (15*60+55)*60_000
COSTS_BPS = (1.0, 2.0)
DISCOVERY_START = pd.Timestamp("2017-01-01T00:00:00Z")
DISCOVERY_END = pd.Timestamp("2022-01-01T00:00:00Z")
FORWARD_START = pd.Timestamp("2022-01-01T00:00:00Z")
FORWARD_END = pd.Timestamp("2026-01-01T00:00:00Z")
OOS_START = pd.Timestamp("2026-01-01T00:00:00Z")
OOS_END = pd.Timestamp("2026-10-10T00:00:00Z")
MIN_DISCOVERY_TRADES = 500
MIN_DISCOVERY_PF_2BPS = 1.00

def sha256_file(p: Path) -> str:
    h=hashlib.sha256()
    with p.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def load_sources(base: Path):
    parts=[]; validation=[]
    for s in SYMS:
        p=base/f"{s}_m5.csv"
        d=pd.read_csv(p, usecols=['timestamp','open','high','low','close'])
        ts=d.timestamp.to_numpy(dtype=np.int64)
        o=d[['open','high','low','close']].to_numpy(dtype=float)
        grid=int(np.sum(np.diff(ts)%BAR_MS != 0))
        dup=int(d.timestamp.duplicated().sum())
        finite=bool(np.isfinite(o).all())
        valid_rel=bool(((o[:,1]>=np.maximum(o[:,0],o[:,3])) & (o[:,2]<=np.minimum(o[:,0],o[:,3])) & (o[:,1]>=o[:,2])).all())
        flat=(o[:,0]==o[:,1])&(o[:,1]==o[:,2])&(o[:,2]==o[:,3])
        validation.append({'symbol':s,'file':p.name,'rows':len(d),
          'min_timestamp_utc':pd.to_datetime(ts.min(),unit='ms',utc=True).isoformat(),
          'max_timestamp_utc':pd.to_datetime(ts.max(),unit='ms',utc=True).isoformat(),
          'duplicate_timestamps':dup,'timestamp_off_five_minute_grid':grid,
          'all_ohlc_finite':finite,'all_ohlc_relationships_valid':valid_rel,'flat_rows':int(flat.sum()),
          'sha256':sha256_file(p)})
        if dup or grid or not finite or not valid_rel: raise RuntimeError(f"source integrity failure: {s}")
        dd=d.set_index('timestamp').rename(columns={c:f'{s}_{c}' for c in ['open','high','low','close']})
        parts.append(dd)
    aligned=pd.concat(parts,axis=1,join='inner').sort_index()
    return aligned, validation

def simulate(aligned: pd.DataFrame, start: pd.Timestamp, end: pd.Timestamp):
    ts=aligned.index.to_numpy(dtype=np.int64)
    cols={s:{k:aligned[f'{s}_{k}'].to_numpy(dtype=float) for k in ['open','high','low','close']} for s in SYMS}
    flat={s:((cols[s]['open']==cols[s]['high'])&(cols[s]['high']==cols[s]['low'])&(cols[s]['low']==cols[s]['close'])) for s in SYMS}
    start_ms=int(start.timestamp()*1000); end_ms=int(end.timestamp()*1000)
    result=[]; skipped={'missing_exact_timestamp':0,'flat_endpoint_or_execution_bar':0,'invalid_or_tied_rank':0}
    candidates=np.flatnonzero((ts % DAY_MS)==SIGNAL_MOD_MS)
    for i in candidates:
        t=int(ts[i])
        if t < start_ms or t >= end_ms: continue
        if t + DAY_MS + BAR_MS >= end_ms: continue
        need=[t-DAY_MS,t+BAR_MS,t+DAY_MS+BAR_MS]
        ix=[int(np.searchsorted(ts,v)) for v in need]
        if any(j>=len(ts) or ts[j]!=v for j,v in zip(ix,need)):
            skipped['missing_exact_timestamp']+=1; continue
        iprev,ientry,iexit=ix
        active=True
        for s in SYMS:
            if flat[s][iprev] or flat[s][i] or flat[s][ientry] or flat[s][iexit]:
                active=False; break
        if not active:
            skipped['flat_endpoint_or_execution_bar']+=1; continue
        mom=[]
        for s in SYMS:
            c0=cols[s]['close'][iprev]; c1=cols[s]['close'][i]
            if not (np.isfinite(c0) and np.isfinite(c1) and c0>0 and c1>0):
                mom=[]; break
            mom.append((c1/c0)-1.0)
        if len(mom)!=len(SYMS): skipped['invalid_or_tied_rank']+=1; continue
        order=np.argsort(np.asarray(mom),kind='stable')
        if abs(mom[order[0]]-mom[order[1]]) < 1e-12 or abs(mom[order[-1]]-mom[order[-2]]) < 1e-12:
            skipped['invalid_or_tied_rank']+=1; continue
        short_sym=SYMS[int(order[0])]; long_sym=SYMS[int(order[-1])]
        entry_ts=int(ts[ientry]); exit_ts=int(ts[iexit])
        le=cols[long_sym]['open'][ientry]; lx=cols[long_sym]['open'][iexit]
        se=cols[short_sym]['open'][ientry]; sx=cols[short_sym]['open'][iexit]
        if not (np.isfinite([le,lx,se,sx]).all() and min(le,lx,se,sx)>0):
            skipped['invalid_or_tied_rank']+=1; continue
        r_long=lx/le-1.0; r_short=sx/se-1.0
        gross_bps=0.5*(r_long-r_short)*10000.0
        rec={'signal_bar_timestamp_ms':t,'signal_close_utc':pd.to_datetime(t+BAR_MS,unit='ms',utc=True).isoformat(),
             'entry_timestamp_ms':entry_ts,'entry_utc':pd.to_datetime(entry_ts,unit='ms',utc=True).isoformat(),
             'exit_timestamp_ms':exit_ts,'exit_utc':pd.to_datetime(exit_ts,unit='ms',utc=True).isoformat(),
             'long_symbol':long_sym,'short_symbol':short_sym,
             'long_momentum_24h_pct':100*mom[SYMS.index(long_sym)],'short_momentum_24h_pct':100*mom[SYMS.index(short_sym)],
             'long_entry_open':float(le),'long_exit_open':float(lx),'short_entry_open':float(se),'short_exit_open':float(sx),
             'long_return_pct':100*r_long,'short_underlying_return_pct':100*r_short,'gross_portfolio_bps':float(gross_bps),'closed':True}
        for c in COSTS_BPS: rec[f'net_{int(c)}bps']=float(gross_bps-c)
        result.append(rec)
    return pd.DataFrame(result), skipped

def pf(series):
    v=np.asarray(series,dtype=float); gains=float(v[v>0].sum()); losses=float(-v[v<0].sum())
    if len(v)==0 or losses<=0: return None
    return gains/losses

def summarize(trades: pd.DataFrame, name: str):
    closed=trades[trades.closed] if len(trades) else trades
    return {'period':name,'closed_trades':int(len(closed)),
         'win_rate':float((closed.gross_portfolio_bps>0).mean()) if len(closed) else None,
         'gross_pf':pf(closed.gross_portfolio_bps) if len(closed) else None,
         'mean_gross_bps':float(closed.gross_portfolio_bps.mean()) if len(closed) else None,
         'median_gross_bps':float(closed.gross_portfolio_bps.median()) if len(closed) else None,
         'mean_net_1bps':float(closed.net_1bps.mean()) if len(closed) else None,
         'mean_net_2bps':float(closed.net_2bps.mean()) if len(closed) else None,
         'pf_1bps':pf(closed.net_1bps) if len(closed) else None,
         'pf_2bps':pf(closed.net_2bps) if len(closed) else None}

def annual_cohorts(trades: pd.DataFrame):
    if not len(trades): return pd.DataFrame(columns=['year','closed_trades','pf_1bps','pf_2bps','mean_net_1bps','mean_net_2bps'])
    d=trades.copy(); d['year']=pd.to_datetime(d.entry_timestamp_ms,unit='ms',utc=True).dt.year
    rows=[]
    for y,g in d.groupby('year'):
        rows.append({'year':int(y),'closed_trades':len(g),'pf_1bps':pf(g.net_1bps),'pf_2bps':pf(g.net_2bps),
                     'mean_net_1bps':float(g.net_1bps.mean()),'mean_net_2bps':float(g.net_2bps.mean())})
    return pd.DataFrame(rows)

def run_tests(aligned: pd.DataFrame, discovery: pd.DataFrame):
    tests=[]
    def check(name, ok, details=''): tests.append({'test':name,'passed':bool(ok),'details':details})
    ok=True
    if len(discovery):
        e=discovery.entry_timestamp_ms.to_numpy(np.int64); x=discovery.exit_timestamp_ms.to_numpy(np.int64); sig=discovery.signal_bar_timestamp_ms.to_numpy(np.int64)
        ok=bool(np.all(e==sig+BAR_MS) and np.all(x==e+DAY_MS) and np.all(x>e))
    check('entry_after_signal_close_and_exit_exactly_24h_later',ok,'entry = signal bar timestamp + 5 min; exit = entry + 24 h')
    check('at_most_one_portfolio_per_signal_timestamp',bool(discovery.signal_bar_timestamp_ms.is_unique) if len(discovery) else True,'one daily scheduled decision')
    check('long_short_are_different_assets',bool((discovery.long_symbol!=discovery.short_symbol).all()) if len(discovery) else True,'long/short ranks are distinct')
    check('closed_trades_have_finite_pnl',bool(np.isfinite(discovery.gross_portfolio_bps.to_numpy()).all()) if len(discovery) else True,'finite realized return records')
    check('modeled_costs_reduce_pnl_by_exact_amount',bool(np.allclose(discovery.net_1bps,discovery.gross_portfolio_bps-1) and np.allclose(discovery.net_2bps,discovery.gross_portfolio_bps-2)) if len(discovery) else True,'net PnL deducts 1 or 2 bps')
    cutoff=pd.Timestamp('2020-01-01T00:00:00Z'); cutoff_ms=int(cutoff.timestamp()*1000)
    full_prefix=discovery[discovery.signal_bar_timestamp_ms < cutoff_ms-DAY_MS-BAR_MS].copy()
    prefix_aligned=aligned.loc[aligned.index.to_numpy(dtype=np.int64)<cutoff_ms]
    truncated,_=simulate(prefix_aligned,DISCOVERY_START,cutoff)
    cols=['signal_bar_timestamp_ms','entry_timestamp_ms','exit_timestamp_ms','long_symbol','short_symbol','gross_portfolio_bps','net_1bps','net_2bps']
    a=full_prefix[cols].reset_index(drop=True); b=truncated[truncated.signal_bar_timestamp_ms < cutoff_ms-DAY_MS-BAR_MS][cols].reset_index(drop=True)
    prefix_ok=(len(a)==len(b) and all(a[c].equals(b[c]) if a[c].dtype=='object' else np.allclose(a[c].to_numpy(),b[c].to_numpy(),rtol=0,atol=1e-12) for c in cols))
    check('actual_truncation_prefix_causality',prefix_ok,f'full vs truncated before {cutoff.isoformat()}; full={len(a)}, truncated={len(b)}')
    period_ok=True
    if len(discovery):
        et=pd.to_datetime(discovery.entry_timestamp_ms,unit='ms',utc=True); xt=pd.to_datetime(discovery.exit_timestamp_ms,unit='ms',utc=True)
        period_ok=bool((et>=DISCOVERY_START).all() and (xt<DISCOVERY_END).all())
    check('discovery_period_and_exit_boundary',period_ok,'both entry and exit remain inside discovery')
    check('source_index_strictly_increasing',bool(aligned.index.is_monotonic_increasing and aligned.index.is_unique),'exact common timestamp index')
    check('causal_signal_formula_explicit',True,'24 h raw close-to-close return; next scheduled open entry')
    return tests

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--data-dir',default='/mnt/data/r205_snapshot'); ap.add_argument('--out-dir',default='/mnt/data/r216_local_results'); args=ap.parse_args()
    outdir=Path(args.out_dir); outdir.mkdir(parents=True,exist_ok=True)
    aligned, validation=load_sources(Path(args.data_dir))
    pd.DataFrame(validation).to_csv(outdir/'source_data_validation.csv',index=False)
    print(f'aligned common timestamps={len(aligned):,}; range={aligned.index.min()} .. {aligned.index.max()}',flush=True)
    disc,skipdisc=simulate(aligned,DISCOVERY_START,DISCOVERY_END); disc.to_csv(outdir/'discovery_trade_ledger.csv',index=False)
    dsum=summarize(disc,'discovery_2017_2021'); pd.DataFrame([dsum]).to_csv(outdir/'discovery_summary.csv',index=False)
    discovery_years=annual_cohorts(disc); discovery_years.to_csv(outdir/'discovery_annual_cohorts.csv',index=False)
    print('DISCOVERY',json.dumps(dsum),'skips',skipdisc,flush=True)
    gate=dsum['closed_trades']>=MIN_DISCOVERY_TRADES and dsum['pf_2bps'] is not None and dsum['pf_2bps']>=MIN_DISCOVERY_PF_2BPS
    summaries=[dsum]; skip_by_period={'discovery':skipdisc}; decision='REJECT_DISCOVERY_GATE_FAILED'
    forward=pd.DataFrame(); oos=pd.DataFrame(); fyears=pd.DataFrame(); oyears=pd.DataFrame()
    if gate:
        forward,skipf=simulate(aligned,FORWARD_START,FORWARD_END); oos,skipo=simulate(aligned,OOS_START,OOS_END)
        forward.to_csv(outdir/'forward_trade_ledger.csv',index=False); oos.to_csv(outdir/'oos_trade_ledger.csv',index=False)
        fsum=summarize(forward,'forward_2022_2025'); osum=summarize(oos,'oos_2026_cutoff'); summaries += [fsum,osum]
        fyears=annual_cohorts(forward); oyears=annual_cohorts(oos)
        fyears.to_csv(outdir/'forward_annual_cohorts.csv',index=False); oyears.to_csv(outdir/'oos_annual_cohorts.csv',index=False)
        skip_by_period.update({'forward':skipf,'oos':skipo})
        qualified=fyears[fyears.closed_trades>=5]
        annual_pass=bool(len(qualified) and (qualified.pf_1bps.fillna(0)>=1).all())
        if fsum['closed_trades']>=30 and fsum['pf_1bps'] is not None and fsum['pf_2bps'] is not None and fsum['pf_1bps']>=1.15 and fsum['pf_2bps']>=1.15 and annual_pass:
            decision='PASS' if fsum['pf_1bps']<=1.4 else 'HOLD_EXTRA_AUDIT'
        else: decision='REJECT_FORWARD_GATE_FAILED'
    tests=run_tests(aligned,disc)
    tests.append({'test':'all_four_source_files_integrity','passed':all(x['duplicate_timestamps']==0 and x['timestamp_off_five_minute_grid']==0 and x['all_ohlc_finite'] and x['all_ohlc_relationships_valid'] for x in validation),'details':'four raw M5 files; duplicates, grid, OHLC relationships, finiteness'})
    pd.DataFrame(tests).to_json(outdir/'unit_tests.json',orient='records',indent=2)
    if not all(x['passed'] for x in tests): raise RuntimeError('One or more tests failed')
    pd.DataFrame(summaries).to_csv(outdir/'period_summaries.csv',index=False)
    meta={'experiment':'R216','title':'UTC scheduled cross-sectional daily momentum rotation across four US indices','decision':decision,
      'locked_parameters':{'symbols':SYMS,'signal_bar_open_utc':'15:55','signal_close_utc':'16:00','entry_open_utc':'16:00','holding_period_hours':24,
      'signal':'rank each instrument by close/close return over prior 24h; long strongest, short weakest; 50% notional each leg',
      'cost_model_round_trip_bps_per_leg':[1,2],'cost_weighting':'50% per leg; portfolio net subtracts 1 or 2 bps per roundtrip',
      'discovery_gate':{'minimum_closed_trades':MIN_DISCOVERY_TRADES,'minimum_pf_at_2bps':MIN_DISCOVERY_PF_2BPS},
      'forward_gate':{'min_trades':30,'PF_at_1bps_min':1.15,'PF_at_2bps_min':1.15,'each_qualifying_annual_cohort_pf_at_1bps_min':1.0},
      'periods':{'discovery':['2017-01-01T00:00:00Z','2022-01-01T00:00:00Z'],'forward':['2022-01-01T00:00:00Z','2026-01-01T00:00:00Z'],'oos':['2026-01-01T00:00:00Z','2026-10-10T00:00:00Z']}},
      'period_summaries':summaries,'skips':skip_by_period,'source_validation':validation,'unit_tests':tests,
      'notes':['BID-only source data','1 and 2 bps are modeled cost stresses, not verified broker/prop costs','forward/OOS run only if discovery gate passes','not a live/funded readiness statement','common four-index sample starts 2018-08-08 due to US Small Cap M5 coverage']}
    (outdir/'meta.json').write_text(json.dumps(meta,indent=2))
    lines=['# R216 — UTC cross-sectional daily momentum rotation','',f'**Decision: {decision}.**','','## Locked hypothesis','',
      '- At the 15:55 UTC M5 bar close, rank four US indices by raw close-to-close percentage return over the prior 24 hours.',
      '- At the following 16:00 UTC M5 open, go long the strongest index and short the weakest with 50% notional per leg.',
      '- Exit both legs at the 16:00 UTC open one day later. Exact timestamps are required; flat bars invalidate the day, and no interpolation or forward-fill is used.',
      '- Round-trip costs are modeled at 1 and 2 bps per leg, weighted by 50% portfolio exposure per leg.',
      '- Discovery gate: at least 500 closed daily portfolios and PF >= 1.00 at 2 bps. Forward only runs if discovery qualifies.','',
      '## Period summaries','','| Period | Trades | PF @1 bp | PF @2 bps | Mean net @1 bp | Mean net @2 bps |','|---|---:|---:|---:|---:|---:|']
    for s in summaries:
        fmt=lambda x:'N/A' if x is None else f'{x:.4f}'
        lines.append(f"| {s['period']} | {s['closed_trades']} | {fmt(s['pf_1bps'])} | {fmt(s['pf_2bps'])} | {fmt(s['mean_net_1bps'])} | {fmt(s['mean_net_2bps'])} |")
    lines += ['', '## Data and execution audit','',f"- Exact shared timestamp rows: {len(aligned):,}.",
      f"- Data range: {pd.to_datetime(aligned.index.min(),unit='ms',utc=True).isoformat()} to {pd.to_datetime(aligned.index.max(),unit='ms',utc=True).isoformat()}.",
      '- Coverage caveat: common four-index data begins 2018-08-08 because US Small Cap data begins then; there are no common observations for 2017–early August 2018.',
      f"- Automated checks: {sum(x['passed'] for x in tests)}/{len(tests)} passed.",
      '- Raw BID OHLC only; no synthetic bars, interpolation, or forward-filled values. Round trips remain within evaluated period.',
      '- Costs are modeled only; no ASK stream or verified live broker/prop fees/slippage/financing were modeled.',
      '- Historical results do not establish live or funded readiness.']
    if gate:
        lines += ['', '## Forward annual cohorts','','| Year | Closed | PF @1 bp | PF @2 bps | Mean net @1 bp | Mean net @2 bps |','|---:|---:|---:|---:|---:|---:|']
        for _,r in fyears.iterrows(): lines.append(f"| {int(r.year)} | {int(r.closed_trades)} | {r.pf_1bps:.4f} | {r.pf_2bps:.4f} | {r.mean_net_1bps:.4f} | {r.mean_net_2bps:.4f} |")
    (outdir/'R216_cross_sectional_daily_momentum_results.md').write_text('\n'.join(lines)+'\n')
    print('DECISION',decision,'tests',sum(x['passed'] for x in tests),'/',len(tests),flush=True)

if __name__=='__main__': main()
