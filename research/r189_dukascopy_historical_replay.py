#!/usr/bin/env python3
"""Local-only R189 locked-rule replay on historical Dukascopy EURUSD M1 BID/ASK.
Raw-data acquisition is separate. This script does not download and does not tune.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
import numpy as np
import pandas as pd

PIP = 0.0001
SL, TP, MFE_TRIGGER, TRAIL, TIME_STOP_BARS = 6.0, 18.0, 6.0, 0.0, 60
MAX_SPREAD_PIPS = 1.5
COSTS = [0.0, 0.2, 0.5, 0.8, 1.0, 2.0]
DATA = Path("data_exports/eurusd_m1_2016_2025")
OUT = Path("research/r189_dukascopy_history_local_results")


def read_bars(path: Path):
    raw = pd.read_csv(path, compression="infer")
    raw.columns = [str(c).replace("\ufeff", "").strip().lower() for c in raw.columns]
    col = next((c for c in ("timestamp", "datetime", "date") if c in raw.columns), None)
    if col is None:
        raise ValueError(f"Missing timestamp in {path}; columns={list(raw.columns)}")
    sr = raw[col].astype(str).str.strip()
    num = pd.to_numeric(sr, errors="coerce")
    if num.notna().mean() > .95:
        med = float(num.abs().median())
        unit = "ms" if med >= 1e11 else ("s" if med >= 1e8 else None)
        if not unit:
            raise ValueError(f"Unrecognized numeric timestamp scale {med}")
        idx = pd.to_datetime(num, unit=unit, utc=True, errors="coerce")
    else:
        idx = pd.to_datetime(sr, utc=True, errors="coerce")
    missing = {"open", "high", "low", "close"} - set(raw.columns)
    if missing or idx.isna().any():
        raise ValueError(f"Bad timestamps or missing OHLC: {missing}")
    d = raw[["open", "high", "low", "close"]].apply(pd.to_numeric, errors="coerce")
    d.columns = ["Open", "High", "Low", "Close"]
    d.index = pd.DatetimeIndex(idx, name="timestamp_utc")
    d = d.replace([np.inf, -np.inf], np.nan).dropna().sort_index()
    dupes = int(d.index.duplicated(keep="last").sum())
    d = d.loc[~d.index.duplicated(keep="last")]
    valid = ((d.High >= d[["Open", "Close"]].max(axis=1)) &
             (d.Low <= d[["Open", "Close"]].min(axis=1)) & (d.High >= d.Low))
    invalid = int((~valid).sum())
    d = d.loc[valid]
    return d, {"rows": len(d), "duplicate_timestamps_removed": dupes, "invalid_ohlc_removed": invalid,
               "start_utc": d.index[0].isoformat(), "end_utc": d.index[-1].isoformat(),
               "sha256_file": hashlib.sha256(path.read_bytes()).hexdigest()}


def l80_fast(df, w1=11, w2=12, disp_thr=15.0, body_thr=2.0, late_thr=0.80,
             dc_thr=7, s0=3, s1=11, dedup=14):
    close, op = df.Close.to_numpy(), df.Open.to_numpy()
    hours = ((df.index.hour - 5) % 24).to_numpy()
    n = len(df)
    step = np.diff(close, prepend=np.nan)
    sgnstep = np.sign(step)
    pos = (sgnstep == 1).astype(np.int32)
    neg = (sgnstep == -1).astype(np.int32)
    ppos = np.concatenate(([0], np.cumsum(pos, dtype=np.int64)))
    pneg = np.concatenate(([0], np.cumsum(neg, dtype=np.int64)))
    body = np.abs(close - op)
    d5 = close - np.roll(close, 5)
    d5[:5] = np.nan
    cand = []
    for w in (w1, w2):
        d = close - np.roll(close, w)
        d[:w] = np.nan
        with np.errstate(divide="ignore", invalid="ignore"):
            late = np.abs(d5) / np.abs(d)
        p_count = np.zeros(n, dtype=np.int64)
        n_count = np.zeros(n, dtype=np.int64)
        valid = np.arange(w, n)
        p_count[valid] = ppos[valid + 1] - ppos[valid - w + 1]
        n_count[valid] = pneg[valid + 1] - pneg[valid - w + 1]
        dsign = np.sign(d)
        same = np.where(dsign > 0, p_count, np.where(dsign < 0, n_count, 0))
        ok = ((hours >= s0) & (hours <= s1) & (np.abs(d) >= disp_thr * PIP) &
              (body >= body_thr * PIP) & (late >= late_thr) & (same >= dc_thr))
        for i in np.flatnonzero(ok):
            cand.append((int(i), 1 if d[i] < 0 else -1, "L80"))
    cand.sort(key=lambda z: z[0])
    out, last = [], -10**18
    for i, direction, src in cand:
        if i - last > dedup and i + 1 < n:
            out.append((i, direction, src))
            last = i
    return out


def simulate(df, bid, ask, signals, corrected_timeout):
    n, idx = len(df), df.index
    bo, bh, bl = (bid[k].to_numpy(float) for k in ("Open", "High", "Low"))
    ao, ah, al = (ask[k].to_numpy(float) for k in ("Open", "High", "Low"))
    spread = (ask.Open.to_numpy(float) - bid.Open.to_numpy(float)) / PIP
    trades, active_exit = [], -1
    spread_rejects = overlaps = censored = 0
    for si, direction, _src in signals:
        e = si + 1
        if e >= n:
            continue
        if not np.isfinite(spread[e]) or spread[e] < -1e-9 or spread[e] > MAX_SPREAD_PIPS + 1e-12:
            spread_rejects += 1
            continue
        if e <= active_exit:
            overlaps += 1
            continue
        entry = float(ask.Open.iat[e] if direction == 1 else bid.Open.iat[e])
        hard_stop = entry - direction * SL * PIP
        target = entry + direction * TP * PIP
        fav, trail_active, stop = entry, False, hard_stop
        scheduled = e + TIME_STOP_BARS
        if scheduled >= n:
            censored += 1
            active_exit = n
            continue
        last = scheduled - 1 if corrected_timeout else scheduled
        exit_i = gross = reason = None
        for j in range(e, last + 1):
            current_stop = stop if trail_active else hard_stop
            stop_hit = (bl[j] <= current_stop) if direction == 1 else (ah[j] >= current_stop)
            target_hit = (bh[j] >= target) if direction == 1 else (al[j] <= target)
            if stop_hit:
                exit_i = j
                gross = direction * (current_stop - entry) / PIP
                reason = "TRAIL_STOP" if trail_active else "STOP"
                break
            if target_hit:
                exit_i, gross, reason = j, TP, "TARGET"
                break
            if direction == 1:
                fav = max(fav, bh[j])
                favourable = (fav - entry) / PIP
                if favourable >= MFE_TRIGGER:
                    new_stop = entry + (favourable - TRAIL) * PIP
                    if new_stop > stop:
                        stop = new_stop
                    trail_active = True
            else:
                fav = min(fav, al[j])
                favourable = (entry - fav) / PIP
                if favourable >= MFE_TRIGGER:
                    new_stop = entry - (favourable - TRAIL) * PIP
                    if (not trail_active) or new_stop < stop:
                        stop = new_stop
                    trail_active = True
        if exit_i is None:
            exit_i = scheduled
            px = float(bid.Open.iat[exit_i] if direction == 1 else ask.Open.iat[exit_i])
            gross = direction * (px - entry) / PIP
            reason = "TIME_OPEN_CAUSAL" if corrected_timeout else "TIME_OPEN_LEGACY"
        trades.append({"signal_utc": idx[si].isoformat(), "entry_utc": idx[e].isoformat(),
                       "exit_utc": idx[exit_i].isoformat(), "direction": "LONG" if direction == 1 else "SHORT",
                       "entry_price": entry, "entry_spread_pips": float(spread[e]), "exit_reason": reason,
                       "gross_pips": float(gross), "engine": "causal_time_stop" if corrected_timeout else "legacy"})
        active_exit = exit_i
    return trades, {"signals_filtered_by_spread_in_sim": spread_rejects,
                    "overlap_skipped": overlaps, "end_of_data_censored": censored}


def metric(trades, cost, weeks):
    a = np.array([float(t["gross_pips"]) - cost for t in trades], dtype=float)
    gp, gl = float(a[a > 0].sum()), float(-a[a < 0].sum())
    eq = np.cumsum(a)
    dd = float(np.max(np.maximum.accumulate(np.r_[0.0, eq])[1:] - eq)) if len(a) else 0.0
    return {"trades": int(len(a)), "PF": gp / gl if gl else ("INF" if gp else None),
            "net_pips": float(a.sum()), "mean_net_pips_per_trade": float(a.mean()) if len(a) else None,
            "win_rate": float((a > 0).mean()) if len(a) else None, "max_drawdown_pips": dd,
            "trades_per_week": float(len(a) / weeks) if weeks else None}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    bid_path = DATA / "eurusd_bid_M1_2016-2025.csv.gz"
    ask_path = DATA / "eurusd_ask_M1_2016-2025.csv.gz"
    bid, bd = read_bars(bid_path)
    ask, ad = read_bars(ask_path)
    common = bid.index.intersection(ask.index).sort_values()
    if len(common) < 1_000_000:
        raise RuntimeError(f"Historical M1 coverage too small: {len(common)} common bars")
    bid, ask = bid.loc[common], ask.loc[common]
    df = bid.copy()
    spread = (ask.Open - bid.Open) / PIP
    if (spread < -1e-8).any():
        raise RuntimeError(f"Negative ask-bid spreads: {int((spread < -1e-8).sum())}")
    signals_all = l80_fast(df, disp_thr=15, late_thr=0.8)
    eligible = [(i, d, src) for i, d, src in signals_all
                if ((df.index[i].hour - 5) % 24) not in (6, 9) and i + 1 < len(df)
                and spread.iat[i + 1] <= MAX_SPREAD_PIPS + 1e-12]
    legacy, ld = simulate(df, bid, ask, eligible, False)
    causal, cd = simulate(df, bid, ask, eligible, True)
    pd.DataFrame(causal).to_csv(OUT / "R189_Dukascopy_2016_2025_causal_trades.csv", index=False)
    pd.DataFrame(legacy).to_csv(OUT / "R189_Dukascopy_2016_2025_legacy_trades.csv", index=False)
    periods = [("all_2016_2025", "2016-01-01", "2026-01-01"),
               ("discovery_2016_2020", "2016-01-01", "2021-01-01"),
               ("forward_2021_2025", "2021-01-01", "2026-01-01")]
    res = {}
    for name, ss, ee in periods:
        s, e = pd.Timestamp(ss, tz="UTC"), pd.Timestamp(ee, tz="UTC")
        tr = [t for t in causal if s <= pd.Timestamp(t["entry_utc"]) < e and pd.Timestamp(t["exit_utc"]) < e]
        res[name] = {f"extra_cost_{c:g}_pip": metric(tr, c, (e - s).total_seconds() / (7*24*3600)) for c in COSTS}
    annual = []
    for year in range(2016, 2026):
        s, e = pd.Timestamp(f"{year}-01-01", tz="UTC"), pd.Timestamp(f"{year+1}-01-01", tz="UTC")
        tr = [t for t in causal if s <= pd.Timestamp(t["entry_utc"]) < e and pd.Timestamp(t["exit_utc"]) < e]
        annual.append({"year": year, **{f"extra_cost_{c:g}_pip": metric(tr, c, (e - s).total_seconds() / (7*24*3600)) for c in COSTS}})
    # 4-week circular moving-block bootstrap of weekly 2021-2025 net PnL at +1 pip.
    s, e = pd.Timestamp("2021-01-01", tz="UTC"), pd.Timestamp("2026-01-01", tz="UTC")
    weeks = int(np.ceil((e - s).total_seconds() / (7*24*3600)))
    weekly = np.zeros(weeks)
    forward = [t for t in causal if s <= pd.Timestamp(t["entry_utc"]) < e and pd.Timestamp(t["exit_utc"]) < e]
    for t in forward:
        wi = int((pd.Timestamp(t["entry_utc"]) - s).total_seconds() // (7*24*3600))
        if 0 <= wi < weeks:
            weekly[wi] += float(t["gross_pips"]) - 1.0
    rng, reps, block = np.random.default_rng(1892026), 5000, 4
    count = int(np.ceil(weeks / block))
    means = np.empty(reps)
    for k in range(reps):
        starts = rng.integers(0, weeks, size=count)
        ix = np.concatenate([(q + np.arange(block)) % weeks for q in starts])[:weeks]
        means[k] = weekly[ix].mean()
    bootstrap = {"weeks": weeks, "trades": len(forward), "reps": reps, "seed": 1892026,
                 "mean_weekly_net_pips_at_plus1": float(weekly.mean()),
                 "probability_positive_mean_weekly_net": float((means > 0).mean()),
                 "ci95_mean_weekly_net_pips": [float(np.quantile(means, .025)), float(np.quantile(means, .975))]}
    quality = {"bid": bd, "ask": ad, "common_bars": len(common), "start_utc": common[0].isoformat(),
               "end_utc": common[-1].isoformat(), "negative_spread_count": int((spread < -1e-8).sum()),
               "spread_pips": {"min": float(spread.min()), "median": float(spread.median()),
                               "p95": float(spread.quantile(.95)), "max": float(spread.max())},
               "signals_before_hour_spread_filter": len(signals_all), "eligible_signals": len(eligible),
               "legacy_diagnostics": ld, "causal_diagnostics": cd,
               "causal_exits": pd.Series([t["exit_reason"] for t in causal]).value_counts().to_dict()}
    report = {"status": "COMPLETE", "round": "R189_HISTORICAL_DUKASCOPY_REPLAY",
              "verdict": "NOT_EXACT_HISTDATA_REPRODUCTION", "execution": "local Python only; data collection separate",
              "strategy": "Locked R189/L80 rules; no parameter optimization", "source_feed": "Dukascopy EURUSD M1 BID/ASK, 2016-2025",
              "parameters": {"displacement_pips": 15, "late_ratio_min": 0.8, "body_min_pips": 2,
                             "directional_consistency_min": 7, "signal_hours_fixed_GMT_minus_5": "03..11 excluding 06 and 09",
                             "dedup_bars": 14, "entry_spread_cap_pips": 1.5, "SL_pips": 6, "TP_pips": 18,
                             "MFE_trigger_pips": 6, "trailing_distance_pips": 0, "time_stop_bars": 60,
                             "cost_stress_pips": COSTS},
              "data_quality": quality, "causal_metrics": res, "forward_annual_causal": annual,
              "forward_bootstrap_at_plus1pip": bootstrap,
              "limitations": ["Dukascopy is a separate feed from the missing original HistData M1/spread archive; do not claim exact reproduction of formerly reported PF.",
                             "M1 OHLC cannot determine tick-level ordering when stop/target coincide; simulator checks stop before target.",
                             "No separate broker commission, live slippage, manual entry delay, or funded-provider DLL/MLL verification."]}
    (OUT / "R189_Dukascopy_2016_2025_results.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    pd.DataFrame(annual).to_csv(OUT / "R189_Dukascopy_2016_2025_annual.csv", index=False)
    print(json.dumps({"verdict": report["verdict"], "data_quality": quality, "causal_metrics": res,
                      "annual": annual, "bootstrap": bootstrap, "result_dir": str(OUT)}, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
