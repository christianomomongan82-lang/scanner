#!/usr/bin/env python3
"""Locked R189 signal, fresh Dukascopy EURUSD M1 BID/ASK OOS data for 2026.
Compares legacy exit timing with a causal time-stop that exits at the scheduled bar OPEN
before using that bar's high/low. No parameter selection is performed on 2026 data.
"""
import hashlib, json, math, os, subprocess, time
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(".")
DATA = ROOT / "dl"
OUT = ROOT / "research"
OUT.mkdir(parents=True, exist_ok=True)
START = "2026-01-01"
END_EXCLUSIVE = "2026-10-13"  # last full UTC date expected through Oct 12
PIP = 0.0001
SL = 6.0
TP = 18.0
MFE = 6.0
TRAIL = 0.0
TIME_STOP = 60
MAX_SPREAD = 1.5
MARKUPS = [0.0, 0.2, 0.5, 0.8, 1.0, 2.0]

def download(inst, price_type, outname):
    DATA.mkdir(parents=True, exist_ok=True)
    path = DATA / f"{outname}.csv"
    path.unlink(missing_ok=True)
    cmd = [
        "npx", "--yes", "dukascopy-node", "-i", inst, "-from", START, "-to", END_EXCLUSIVE,
        "-t", "m1", "-p", price_type, "-utc", "0", "-f", "csv",
        "-dir", str(DATA), "-fn", outname, "-bs", "3", "-bp", "2000",
        "-r", "5", "-re", "-rp", "5000",
    ]
    env = os.environ.copy()
    patch = ROOT / "dukascopy_fetch_patch.cjs"
    if patch.exists():
        env["NODE_OPTIONS"] = (env.get("NODE_OPTIONS", "") + f" --require={patch.resolve()}").strip()
    last = "not attempted"
    for attempt in range(1, 4):
        try:
            p = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                               text=True, check=False, env=env, timeout=900)
            last = p.stdout[-12000:]
            if p.returncode == 0 and path.is_file() and path.stat().st_size > 0:
                return path, {"command_exit": p.returncode, "attempt": attempt, "log_tail": last}
            last = f"exit={p.returncode}; file_exists={path.exists()}; log_tail={last}"
        except Exception as e:
            last = f"{type(e).__name__}: {e}"
        time.sleep(attempt * 5)
    raise RuntimeError(f"download {inst}/{price_type} failed: {last}")

def load_bars(path):
    df = pd.read_csv(path)
    original_columns = list(df.columns)
    df.columns = [str(c).replace("\ufeff", "").strip().lower() for c in df.columns]
    if "timestamp" not in df.columns:
        raise ValueError(f"timestamp column missing in {path}; columns={original_columns}")
    raw = df["timestamp"]
    numeric = pd.to_numeric(raw, errors="coerce")
    if numeric.notna().mean() > 0.95:
        med = float(numeric.abs().median())
        unit = "ms" if med >= 1e11 else ("s" if med >= 1e8 else None)
        if not unit:
            raise ValueError(f"unknown numeric timestamp scale in {path}: median={med}")
        idx = pd.to_datetime(numeric, unit=unit, utc=True, errors="coerce")
    else:
        idx = pd.to_datetime(raw.astype(str), utc=True, errors="coerce")
    req = ["open", "high", "low", "close"]
    if idx.isna().any() or any(c not in df.columns for c in req):
        raise ValueError(f"bad timestamp or OHLC columns in {path}")
    for c in req:
        df[c] = pd.to_numeric(df[c], errors="coerce")
    out = df[req].copy()
    out.index = pd.DatetimeIndex(idx, name="timestamp_utc")
    out = out.replace([np.inf, -np.inf], np.nan).dropna().sort_index()
    dupes = int(out.index.duplicated(keep="last").sum())
    out = out.loc[~out.index.duplicated(keep="last")]
    valid = ((out.high >= out[["open", "close"]].max(axis=1)) &
             (out.low <= out[["open", "close"]].min(axis=1)) &
             (out.high >= out.low))
    invalid = int((~valid).sum())
    out = out.loc[valid]
    return out, {"input_rows": int(len(df)), "duplicates_removed": dupes,
                 "invalid_ohlc_rows": invalid, "columns": original_columns}

def pf(x):
    x = np.asarray(x, dtype=float)
    gains = float(x[x > 0].sum())
    losses = float(-x[x < 0].sum())
    if losses == 0:
        return None if gains == 0 else "INF"
    return gains / losses

def max_dd(x):
    x = np.asarray(x, dtype=float)
    if len(x) == 0: return 0.0
    eq = np.cumsum(x)
    peak = np.maximum.accumulate(np.r_[0.0, eq])
    return float(np.max(peak[1:] - eq))

def metrics(rows, markup=0.2, n_weeks=None):
    vals = np.array([r["gross_pips"] - markup for r in rows], dtype=float)
    return {
        "closed_trades": int(len(vals)),
        "pf": pf(vals),
        "net_pips": float(vals.sum()) if len(vals) else 0.0,
        "max_drawdown_pips": max_dd(vals),
        "win_rate": float((vals > 0).mean()) if len(vals) else None,
        "mean_pips_per_trade": float(vals.mean()) if len(vals) else None,
        "trades_per_calendar_week": (float(len(vals) / n_weeks) if n_weeks and len(vals) else None),
    }

def signals(df):
    close = df["close"].to_numpy(float)
    op = df["open"].to_numpy(float)
    idx = df.index
    n = len(df)
    step = np.diff(close, prepend=np.nan)
    sgn = np.sign(step)
    pos = (sgn == 1).astype(np.int64)
    neg = (sgn == -1).astype(np.int64)
    pp = np.r_[0, np.cumsum(pos)]
    pn = np.r_[0, np.cumsum(neg)]
    d5 = close - np.roll(close, 5)
    d5[:5] = np.nan
    candidates = []
    for w in (11, 12):
        d = close - np.roll(close, w)
        d[:w] = np.nan
        with np.errstate(divide="ignore", invalid="ignore"):
            late = np.abs(d5) / np.abs(d)
        same = np.where(d > 0, pp[np.arange(n)+1] - pp[np.maximum(0, np.arange(n)-w+1)],
                        np.where(d < 0, pn[np.arange(n)+1] - pn[np.maximum(0, np.arange(n)-w+1)], 0))
        ok = (
            np.isfinite(d) & np.isfinite(late) &
            (idx.hour >= 3) & (idx.hour <= 11) &
            (np.abs(d) >= 15.0 * PIP) &
            (np.abs(close-op) >= 2.0 * PIP) &
            (late >= 0.80) & (same >= 7)
        )
        for i in np.flatnonzero(ok):
            candidates.append((int(i), 1 if d[i] < 0 else -1))
    candidates.sort(key=lambda x: x[0])  # stable: w=11 precedes w=12 at equal index
    accepted, last = [], -10**18
    for i, direction in candidates:
        if i - last > 14 and i + 1 < n and idx[i].hour not in (6, 9):
            accepted.append((i, direction))
            last = i
    return accepted

def run_sim(df, bid, ask, sigs, corrected_timeout):
    n = len(df)
    idx = df.index
    bo, bh, bl, bc = [bid[k].to_numpy(float) for k in ("open", "high", "low", "close")]
    ao, ah, al, ac = [ask[k].to_numpy(float) for k in ("open", "high", "low", "close")]
    spread = (ao - bo) / PIP
    rows = []
    active_exit = -1
    censored = 0
    skipped_spread = 0
    skipped_overlap = 0
    for si, direction in sigs:
        e = si + 1
        if e >= n: continue
        if not np.isfinite(spread[e]) or spread[e] < 0 or spread[e] > MAX_SPREAD + 1e-12:
            skipped_spread += 1
            continue
        if e <= active_exit:
            skipped_overlap += 1
            continue
        ep = ao[e] if direction == 1 else bo[e]
        hard_sl = ep - direction * SL * PIP
        target = ep + direction * TP * PIP
        fav = ep
        trail_active = False
        stop = hard_sl
        scheduled = e + TIME_STOP
        if scheduled >= n:
            censored += 1
            active_exit = n  # no later trades may be opened inside this truncated window
            continue
        last = min(n - 1, scheduled)
        exit_i = None
        gross = None
        reason = None

        # In corrected mode, exit at the scheduled OPEN before checking that candle's
        # high/low. Legacy mode preserves the old engine's intrabar check on that candle.
        process_until = last if not corrected_timeout else min(last, scheduled - 1)
        for j in range(e, process_until + 1):
            current_stop = stop if trail_active else hard_sl
            stop_hit = (bl[j] <= current_stop) if direction == 1 else (ah[j] >= current_stop)
            target_hit = (bh[j] >= target) if direction == 1 else (al[j] <= target)
            if stop_hit:
                exit_i, gross, reason = j, direction * (current_stop - ep) / PIP, ("TRAIL_STOP" if trail_active else "STOP")
                break
            if target_hit:
                exit_i, gross, reason = j, TP, "TARGET"
                break
            if direction == 1:
                fav = max(fav, bh[j])
                mfe = (fav - ep) / PIP
                if mfe >= MFE:
                    ns = ep + (mfe - TRAIL) * PIP
                    if ns > stop: stop = ns
                    trail_active = True
            else:
                fav = min(fav, al[j])
                mfe = (ep - fav) / PIP
                if mfe >= MFE:
                    ns = ep - (mfe - TRAIL) * PIP
                    if (not trail_active) or ns < stop: stop = ns
                    trail_active = True
            if j == last and j > e:
                px = bo[j] if direction == 1 else ao[j]
                exit_i, gross, reason = j, direction * (px - ep) / PIP, "TIME_OPEN_LEGACY"
                break

        if exit_i is None:
            if corrected_timeout:
                # All bars before scheduled are clear; exit at executable price on scheduled open.
                j = scheduled
                px = bo[j] if direction == 1 else ao[j]
                exit_i, gross, reason = j, direction * (px - ep) / PIP, "TIME_OPEN_CAUSAL"
            else:
                # End-of-data without a planned time stop: censor, do not fabricate an exit.
                censored += 1
                active_exit = n
                continue

        rows.append({
            "signal_utc": idx[si].isoformat(),
            "entry_utc": idx[e].isoformat(),
            "exit_utc": idx[exit_i].isoformat(),
            "direction": "LONG" if direction == 1 else "SHORT",
            "entry_price": float(ep),
            "exit_reason": reason,
            "gross_pips": float(gross),
            "entry_spread_pips": float(spread[e]),
            "legacy_or_corrected": "corrected" if corrected_timeout else "legacy",
        })
        active_exit = exit_i
    return rows, {"spread_filtered": skipped_spread, "overlap_skipped": skipped_overlap, "censored": censored}

def main():
    report = {
        "status": "STARTED",
        "method": "R189 locked parameters applied once to fresh 2026 Dukascopy EURUSD M1 bid/ask; no re-optimization.",
        "test_window_requested_utc": {"from": START, "to_exclusive": END_EXCLUSIVE},
        "params": {"displacement_pips": 15, "late_ratio_min": 0.8, "body_pips_min": 2,
                   "directional_consistency_min": 7, "signal_hours_utc": "03-11 except 06 and 09",
                   "dedup_bars": 14, "spread_cap_pips": MAX_SPREAD, "SL_pips": SL, "TP_pips": TP,
                   "MFE_trigger_pips": MFE, "trail_pips": TRAIL, "time_stop_minutes": TIME_STOP,
                   "extra_markup_stress_pips_per_trade": MARKUPS},
        "source": "Dukascopy EURUSD M1 OHLC, bid and ask downloaded separately with dukascopy-node; prices include quoted bid/ask execution. This is a different feed from the missing historical R189 raw files.",
    }
    try:
        bp, blog = download("eurusd", "bid", "eurusd_bid")
        ap, alog = download("eurusd", "ask", "eurusd_ask")
        bid, bdiag = load_bars(bp)
        ask, adiag = load_bars(ap)
        common = bid.index.intersection(ask.index).sort_values()
        bid, ask = bid.loc[common], ask.loc[common]
        spread = (ask["open"] - bid["open"]) / PIP
        # Common rows are required so each signal and executable quote use identical timestamps.
        data_bad = int((spread < -1e-9).sum())
        if len(common) < 10000: raise ValueError(f"too few common bid/ask M1 bars: {len(common)}")
        if data_bad:
            raise ValueError(f"ask open below bid open in {data_bad} common bars")
        df = bid.copy()
        sigs = signals(df)
        # Candidate reduction is as locked: signal dedup first, then spread cap at entry.
        cap_sigs = [(i, d) for i, d in sigs if i + 1 < len(df) and spread.iloc[i+1] <= MAX_SPREAD]
        legacy, ldiag = run_sim(df, bid, ask, cap_sigs, corrected_timeout=False)
        corrected, cdiag = run_sim(df, bid, ask, cap_sigs, corrected_timeout=True)
        start, end = df.index.min(), df.index.max()
        n_weeks = max((end - start).total_seconds() / (7*24*3600), 1/7)
        report.update({
            "status": "COMPLETE",
            "data": {
                "bid_file_sha256": hashlib.sha256(bp.read_bytes()).hexdigest(),
                "ask_file_sha256": hashlib.sha256(ap.read_bytes()).hexdigest(),
                "bid_diagnostics": bdiag, "ask_diagnostics": adiag,
                "bid_rows_common": int(len(bid)), "ask_rows_common": int(len(ask)),
                "common_rows": int(len(common)), "negative_spreads": data_bad,
                "data_start_utc": start.isoformat(), "data_end_utc": end.isoformat(),
                "min_spread_pips": float(spread.min()), "median_spread_pips": float(spread.median()),
                "p95_spread_pips": float(spread.quantile(0.95)), "max_spread_pips": float(spread.max()),
                "signals_before_spread_filter": int(len(sigs)),
                "signals_after_spread_filter": int(len(cap_sigs)),
                "n_weeks_calendar": float(n_weeks),
                "download_bid_attempt": blog["attempt"], "download_ask_attempt": alog["attempt"],
                "download_logs_tail": {"bid": blog["log_tail"][-2000:], "ask": alog["log_tail"][-2000:]},
            },
            "legacy_execution": {
                "diagnostics": ldiag,
                "baseline_markup_0_2_pips": metrics(legacy, 0.2, n_weeks),
                "markup_stress": [{"markup_pips": c, **metrics(legacy, c, n_weeks)} for c in MARKUPS],
            },
            "causal_time_stop_execution": {
                "diagnostics": cdiag,
                "baseline_markup_0_2_pips": metrics(corrected, 0.2, n_weeks),
                "markup_stress": [{"markup_pips": c, **metrics(corrected, c, n_weeks)} for c in MARKUPS],
                "monthly": [],
            },
            "comparison": {
                "legacy_closed_trades": len(legacy), "corrected_closed_trades": len(corrected),
                "legacy_pf_markup_0_2": metrics(legacy,0.2,n_weeks)["pf"],
                "corrected_pf_markup_0_2": metrics(corrected,0.2,n_weeks)["pf"],
                "legacy_net_markup_0_2": metrics(legacy,0.2,n_weeks)["net_pips"],
                "corrected_net_markup_0_2": metrics(corrected,0.2,n_weeks)["net_pips"],
            },
        })
        monthly = {}
        for r in corrected:
            m = r["entry_utc"][:7]
            monthly.setdefault(m, []).append(r)
        report["causal_time_stop_execution"]["monthly"] = []
        for m, rs in sorted(monthly.items()):
            weeks_in_month = float(pd.Period(m, freq="M").days_in_month / 7.0)
            report["causal_time_stop_execution"]["monthly"].append({
                "month_utc": m, **metrics(rs, 0.2, weeks_in_month)
            })
        # Write machine-readable summary and auditable trade ledgers.
        (OUT / "r189_oos_2026_results.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
        pd.DataFrame(legacy).to_csv(OUT / "r189_oos_2026_legacy_trades.csv", index=False)
        pd.DataFrame(corrected).to_csv(OUT / "r189_oos_2026_causal_trades.csv", index=False)
    except Exception as e:
        report.update({"status": "FAILED", "error": f"{type(e).__name__}: {e}"})
        (OUT / "r189_oos_2026_results.json").write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
        print(json.dumps(report, indent=2))
        # Return a usable failed artifact rather than fail before commit.
        return
    print(json.dumps(report, indent=2, allow_nan=False))

if __name__ == "__main__":
    main()
