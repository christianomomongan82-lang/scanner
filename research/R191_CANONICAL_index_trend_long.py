import sys, glob, warnings
from pathlib import Path
import numpy as np, pandas as pd
warnings.filterwarnings('ignore')
N, M, RR = 55, 27, 2.0
def load(folder, inst):
    f = (glob.glob(f'{folder}/{inst}_M5_bidask_UTC*.xz') or glob.glob(f'{folder}/{inst}_M5*xz'))
    if f:
        d = pd.read_csv(f[0], index_col=0, parse_dates=True)
        d.index = d.index.tz_convert('America/New_York')
    else:
        # Repository cache adapter only: retain the original H4 resampling and strategy logic below.
        cached = Path(folder) / f'{inst}_m5.csv.gz'
        if not cached.is_file():
            raise FileNotFoundError(f'No canonical M5 source or repository cache found for {inst} in {folder}')
        from research.r192_ger40 import parse_data
        d, _ = parse_data(cached)
        d.index = d.index.tz_convert('America/New_York')
    d = d[d.index.year >= 2017][['open', 'high', 'low', 'close']]
    return d.resample('4h', offset='1h', label='left', closed='left').agg({'open': 'first', 'high': 'max', 'low': 'min', 'close': 'last'}).dropna()
def sim(h, N=N, M=M, rr=RR):
    o, hi, lo, c = h.open.values, h.high.values, h.low.values, h.close.values; n = len(h); rows = []; active = -1
    for i in range(max(N, M), n - 1):
        e = i + 1
        if e <= active or not (c[i] > hi[i - N:i].max()): continue
        ep = o[e]; sl = lo[i - M + 1:i + 1].min(); risk = ep - sl
        if risk <= 0: continue
        tp = ep + rr * risk; out = None; x = n - 1
        for j in range(e, n):
            if lo[j] <= sl: out = min(sl, o[j]); x = j; break
            if hi[j] >= tp: out = tp; x = j; break
        if out is None: out = c[n - 1]
        rows.append((h.index[e], (out - ep) / risk, ep, risk)); active = x
    return pd.DataFrame(rows, columns=['t', 'g', 'ep', 'risk'])
def pf(x):
    x = np.asarray(x, float); gp = x[x > 0].sum(); gl = -x[x < 0].sum(); return gp / gl if gl > 0 else np.inf
def net(t, bp): return t.g - bp * 1e-4 * t.ep / t.risk
if __name__ == '__main__':
    folder = sys.argv[1] if len(sys.argv) > 1 else '.'
    H = {k: load(folder, k) for k in ('usa500idxusd', 'usatechidxusd')}
    T = pd.concat([sim(h).assign(inst=k) for k, h in H.items()]); T['y'] = T.t.dt.year
    for lab, a, b in (('SELEKSI 2017-2021', 2017, 2021), ('FORWARD 2022-2025', 2022, 2025), ('OOS 2026', 2026, 2026)):
        S = T[(T.y >= a) & (T.y <= b)]
        print(f'{lab}: n={len(S)} | PF @0bp {pf(net(S,0)):.3f} @1bp {pf(net(S,1)):.3f} @2bp {pf(net(S,2)):.3f} | totalR@1bp {net(S,1).sum():+.1f}')
        print('   per tahun @1bp:', {int(y): (len(g), round(pf(net(g, 1)), 2)) for y, g in S.groupby('y')})
