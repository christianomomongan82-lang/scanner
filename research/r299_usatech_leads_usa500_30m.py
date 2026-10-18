#!/usr/bin/env python3
"""Deterministic local replay of preregistered R299. No 2022+ outcomes are scored."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd

ARCHIVE_SHA256 = {
    "usa500_archive": "21d37f9b6faf12094cba2243d8b13ecf9973468e2b09b24e16a9cfa67ed4ceac",
    "usatech_archive": "91c7d44b0487e98eeea021712528910475e626bf433220a007629f3005fc66ad",
}
MEMBER_SHA256 = {
    "usa500idxusd_m5.csv.gz": "df2a5edfa49cb15f8bcf5b13577e95907a0f0c54d02c7feed8bdbb7e3b6c49ee",
    "usatechidxusd_m5.csv.gz": "82b06c38f66cd1387097691baac1d45c9463b6540eea9dfe28a894d85e122f7c",
}
CUTOFF = pd.Timestamp("2022-01-01T00:00:00Z")
COSTS = (1, 2, 4)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_bars(root, filename, label):
    path = root / filename
    if sha256(path) != MEMBER_SHA256[filename]:
        raise ValueError(f"SHA-256 mismatch for {filename}")
    # Hard cutoff before activity checks, feature construction or PnL.
    df = pd.read_csv(path, compression="gzip")
    df = df.loc[pd.to_datetime(df.timestamp, unit="ms", utc=True) < CUTOFF].copy()
    df["timestamp"] = df.timestamp.astype("int64")
    if df.timestamp.duplicated().any() or not df.timestamp.is_monotonic_increasing:
        raise ValueError(f"{label}: duplicate or non-monotonic timestamps")
    if not (df.timestamp % 300000 == 0).all():
        raise ValueError(f"{label}: timestamp not on M5 grid")
    good = (
        (df.high >= df.low)
        & (df.high >= df[["open", "close"]].max(axis=1))
        & (df.low <= df[["open", "close"]].min(axis=1))
    )
    if not good.all():
        raise ValueError(f"{label}: invalid OHLC")
    df["active"] = (df.high > df.low) | (df.open != df.close)
    df["dt"] = pd.to_datetime(df.timestamp, unit="ms", utc=True).dt.tz_convert("America/New_York")
    return df.reset_index(drop=True)


def net_stats(frame, cost):
    values = frame[f"net_R_{cost}bp"].to_numpy(float)
    cumulative = np.cumsum(values)
    peak = np.maximum.accumulate(np.r_[0.0, cumulative])[1:]
    drawdown = peak - cumulative
    return {
        "trades": int(len(frame)),
        "net_R": float(values.sum()),
        "PF_R": float(values[values > 0].sum() / (-values[values < 0].sum())) if (values < 0).any() else None,
        "win_rate_pct": float((values > 0).mean() * 100) if len(values) else None,
        "max_closed_DD_R": float(drawdown.max()) if len(drawdown) else 0.0,
        "longs": int((frame.direction == 1).sum()),
        "shorts": int((frame.direction == -1).sum()),
        "stop_exits": int(frame.exit_type.str.startswith("stop").sum()),
        "target_exits": int(frame.exit_type.str.startswith("target").sum()),
        "time_exits": int((frame.exit_type == "time").sum()),
        "mean_hold_min": float(frame.hold_minutes.mean()) if len(frame) else None,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", required=True, help="Directory with the two exact M5 .csv.gz archive members")
    parser.add_argument("--output-dir", default="r299_output", help="Directory for generated CSV/JSON artifacts")
    args = parser.parse_args()
    root, out = Path(args.data_dir), Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    usa = load_bars(root, "usa500idxusd_m5.csv.gz", "USA500")
    tech = load_bars(root, "usatechidxusd_m5.csv.gz", "USATECH")
    usa_ts, tech_ts = usa.timestamp.to_numpy(), tech.timestamp.to_numpy()
    usa_map = {int(t): i for i, t in enumerate(usa_ts)}
    tech_map = {int(t): i for i, t in enumerate(tech_ts)}
    tech_active = tech.active.to_numpy()
    tech_close = tech.close.to_numpy(float)
    tech_dt = tech.dt

    # Valid source impulse: seven active, contiguous M5 bars at a weekday 10:00-14:55 NY bar start.
    valid_returns, calibration_abs = {}, []
    for i in range(6, len(tech)):
        if not tech_active[i - 6:i + 1].all():
            continue
        stamps = tech_ts[i - 6:i + 1]
        if not np.all(np.diff(stamps) == 300000):
            continue
        local = tech_dt.iloc[i]
        minute = local.hour * 60 + local.minute
        if local.weekday() >= 5 or not (600 <= minute < 900):
            continue
        ret = tech_close[i] / tech_close[i - 6] - 1
        valid_returns[i] = ret
        if local.year == 2016:
            calibration_abs.append(abs(ret))
    if len(calibration_abs) < 1000:
        raise ValueError(f"Insufficient calibration windows: {len(calibration_abs)}")
    q95 = float(np.quantile(calibration_abs, 0.95))
    if not np.isfinite(q95) or q95 <= 0:
        raise ValueError("Invalid frozen Q95 threshold")

    # First qualifying signal per NY date is selected before target-side execution checks.
    selected, seen_days = [], set()
    for i, ret in valid_returns.items():
        local = tech_dt.iloc[i]
        if local.year < 2017 or local.year >= 2022 or abs(ret) < q95:
            continue
        day = local.date()
        if day in seen_days:
            continue
        seen_days.add(day)
        selected.append({
            "idx": i, "timestamp": int(tech_ts[i]), "date_ny": str(day),
            "source_return": float(ret), "direction": 1 if ret > 0 else -1
        })
    selected.sort(key=lambda event: event["timestamp"])

    usa_active = usa.active.to_numpy()
    uopen, uhigh, ulow = usa.open.to_numpy(float), usa.high.to_numpy(float), usa.low.to_numpy(float)
    events, trades = [], []
    for event in selected:
        t, direction = event["timestamp"], event["direction"]
        reason, risk_idx = "", []
        for offset in range(-5, 1):
            ix = usa_map.get(t + offset * 300000)
            if ix is None:
                reason = "missing_risk_timestamp"
                break
            risk_idx.append(ix)
        if not reason and not usa_active[risk_idx].all():
            reason = "inactive_risk_bar"
        if not reason and not np.all(np.diff(usa_ts[risk_idx]) == 300000):
            reason = "noncontiguous_risk_bars"
        if reason:
            events.append({**event, "status": "SKIP", "reason": reason})
            continue
        risk = float(np.mean(uhigh[risk_idx] - ulow[risk_idx]))
        if not np.isfinite(risk) or risk <= 0:
            events.append({**event, "status": "SKIP", "reason": "nonpositive_risk_range"})
            continue

        entry_t = t + 10 * 60 * 1000
        entry_i = usa_map.get(entry_t)
        if entry_i is None or not usa_active[entry_i]:
            events.append({**event, "status": "SKIP", "reason": "missing_or_inactive_entry"})
            continue
        entry = float(uopen[entry_i])
        stop, target = entry - direction * risk, entry + direction * 1.5 * risk
        time_exit_t = entry_t + 30 * 60 * 1000
        exit_price = exit_type = exit_t = None
        invalid_reason = ""
        # Inspect entry bar through entry+25m; the cap bar is used only at its OPEN.
        for k in range(6):
            bar_t = entry_t + k * 300000
            bi = usa_map.get(bar_t)
            if bi is None:
                invalid_reason = "missing_path_timestamp"
                break
            if not usa_active[bi]:
                invalid_reason = "inactive_path_bar"
                break
            if k and usa_ts[bi] - usa_ts[usa_map[bar_t - 300000]] != 300000:
                invalid_reason = "noncontiguous_path"
                break
            op, hi, lo = float(uopen[bi]), float(uhigh[bi]), float(ulow[bi])
            if direction == 1:
                if op <= stop:
                    exit_price, exit_type = op, "stop_gap"
                elif op >= target:
                    exit_price, exit_type = op, "target_gap"
                elif lo <= stop and hi >= target:
                    exit_price, exit_type = stop, "stop_collision"
                elif lo <= stop:
                    exit_price, exit_type = stop, "stop"
                elif hi >= target:
                    exit_price, exit_type = target, "target"
            else:
                if op >= stop:
                    exit_price, exit_type = op, "stop_gap"
                elif op <= target:
                    exit_price, exit_type = op, "target_gap"
                elif hi >= stop and lo <= target:
                    exit_price, exit_type = stop, "stop_collision"
                elif hi >= stop:
                    exit_price, exit_type = stop, "stop"
                elif lo <= target:
                    exit_price, exit_type = target, "target"
            if exit_price is not None:
                exit_t = bar_t
                break
        if invalid_reason:
            events.append({**event, "status": "SKIP", "reason": invalid_reason})
            continue
        if exit_price is None:
            cap_i = usa_map.get(time_exit_t)
            if cap_i is None or not usa_active[cap_i]:
                events.append({**event, "status": "SKIP", "reason": "missing_or_inactive_time_exit"})
                continue
            exit_price, exit_type, exit_t = float(uopen[cap_i]), "time", time_exit_t

        gross = direction * (exit_price - entry) / risk
        trade = {
            **event,
            "entry_time_utc": pd.to_datetime(entry_t, unit="ms", utc=True).isoformat(),
            "exit_time_utc": pd.to_datetime(exit_t, unit="ms", utc=True).isoformat(),
            "entry": entry, "exit": float(exit_price), "risk_distance": risk,
            "exit_type": exit_type, "hold_minutes": (exit_t - entry_t) / 60000, "gross_R": gross,
        }
        for cost in COSTS:
            trade[f"net_R_{cost}bp"] = (direction * (exit_price - entry) - entry * cost / 10000.0) / risk
        trades.append(trade)
        events.append({**event, "status": "TRADE", "reason": "", "exit_type": exit_type})

    ledger = pd.DataFrame(trades).sort_values("timestamp").reset_index(drop=True)
    event_audit = pd.DataFrame(events).sort_values("timestamp").reset_index(drop=True)
    year = ledger.timestamp.map(lambda x: pd.Timestamp(x, unit="ms", tz="UTC").year)
    report = {
        "candidate": "R299_USATECH_LEADS_USA500_30M",
        "verdict": "GAGAL",
        "cutoff_utc_exclusive": "2022-01-01T00:00:00Z",
        "source_archive_sha256": ARCHIVE_SHA256,
        "source_member_sha256": MEMBER_SHA256,
        "q95": q95,
        "calibration_windows_2016": len(calibration_abs),
        "valid_windows_through_2021": len(valid_returns),
        "events_selected": len(selected),
        "completed_trades": len(ledger),
        "skip_counts": event_audit.loc[event_audit.status == "SKIP", "reason"].value_counts().to_dict(),
        "rows": {
            "usa500": len(usa), "usatech": len(tech),
            "usa500_active": int(usa_active.sum()), "usatech_active": int(tech_active.sum()),
        },
        "timestamp_alignment_through_cutoff": {
            "shared_timestamps": len(set(map(int, usa_ts)) & set(map(int, tech_ts))),
            "usa500_only_timestamps": len(set(map(int, usa_ts)) - set(map(int, tech_ts))),
            "usatech_only_timestamps": len(set(map(int, tech_ts)) - set(map(int, usa_ts))),
        },
        "periods": {},
    }
    for name, mask in [
        ("discovery_2017_2020", year.between(2017, 2020)),
        ("validation_2021", year == 2021),
    ]:
        frame = ledger.loc[mask].copy()
        report["periods"][name] = {f"cost_{cost}bp": net_stats(frame, cost) for cost in COSTS}
        report["periods"][name]["annual"] = {
            str(y): {f"cost_{cost}bp": net_stats(frame.loc[year.loc[frame.index] == y], cost) for cost in COSTS}
            for y in sorted(set(year.loc[frame.index]))
        }

    # Monday-start NY calendar weeks including zero-trade weeks; circular blocks of 4 weeks.
    validation = ledger.loc[year == 2021].copy()
    ny_dates = pd.to_datetime(validation.timestamp, unit="ms", utc=True).dt.tz_convert("America/New_York").dt.date
    validation["week_monday"] = ny_dates.map(lambda d: d - pd.Timedelta(days=d.weekday()))
    weeks = pd.date_range("2021-01-04", "2021-12-27", freq="W-MON").date
    weekly = np.array([validation.loc[validation.week_monday == d, "net_R_2bp"].sum() for d in weeks], dtype=float)
    rng = np.random.default_rng(299)
    boot = []
    for _ in range(10000):
        starts = rng.integers(0, len(weekly), size=int(np.ceil(len(weekly) / 4)))
        indices = np.concatenate([np.arange(s, s + 4) % len(weekly) for s in starts])[:len(weekly)]
        boot.append(weekly[indices].mean())
    report["bootstrap_2021_2bp"] = {
        "weeks": len(weekly), "trade_weeks": int((weekly != 0).sum()),
        "mean_weekly_net_R": float(weekly.mean()),
        "ci95_lower": float(np.quantile(boot, 0.025)), "ci95_upper": float(np.quantile(boot, 0.975)),
        "resamples": 10000, "block_len": 4, "seed": 299,
    }

    ledger.to_csv(out / "R299_reproduced_trade_ledger.csv", index=False)
    event_audit.to_csv(out / "R299_reproduced_event_audit.csv", index=False)
    pd.DataFrame({"week_monday": weeks, "net_R_2bp": weekly}).to_csv(out / "R299_reproduced_validation_weekly_net_R.csv", index=False)
    (out / "R299_reproduced_metrics.json").write_text(json.dumps(report, indent=2))
    annual_rows = []
    for name, block in report["periods"].items():
        for y, metrics in block["annual"].items():
            for cost, values in metrics.items():
                annual_rows.append({"period": name, "year": y, "cost": cost, **values})
    pd.DataFrame(annual_rows).to_csv(out / "R299_reproduced_annual_summary.csv", index=False)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
