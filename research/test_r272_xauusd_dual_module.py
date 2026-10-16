"""R272 engine smoke tests: delayed entry, cutoff fills, gaps and data provenance."""
import importlib.util
import hashlib
import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pandas as pd

p = Path(__file__).resolve().parent / "r272_xauusd_dual_module.py"
spec = importlib.util.spec_from_file_location("r272", p)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

# Synthetic weekday M5 quote tape, New York 08:00–16:45.
ny = pd.date_range("2026-01-05 08:00", "2026-01-05 16:45", freq="5min", tz="America/New_York")
utc = ny.tz_convert("UTC")
n = len(ny)
q = pd.DataFrame({
    "timestamp_utc": utc,
    "ny_time": ny,
    "ny_date": ny.date,
    "ny_minute": ny.hour * 60 + ny.minute,
    "ny_weekday": True,
})
for side, off in (("bid", 0.0), ("ask", 0.1)):
    q[f"{side}_open"] = 100 + off
    q[f"{side}_high"] = 100.3 + off
    q[f"{side}_low"] = 99.8 + off
    q[f"{side}_close"] = 100.05 + off

signal_i = int((ny == pd.Timestamp("2026-01-05 10:00", tz="America/New_York")).argmax())
pos = {q.ny_date.iloc[0]: list(range(n))}
sig = {"module": "A", "direction": 1, "stop": 99.0, "A": 1.0,
       "ER": 0.5, "net_move": 5.0, "target_multiple": 1.5, "target": None}
entry_i = signal_i + 2
target = 100.1 + (100.1 - 99.0) * 1.5
q.loc[entry_i + 2, "bid_high"] = target + 0.3
row = m.build_trade_for_signal(q, pos, signal_i, sig)
assert row is not None
assert row["entry_index"] == entry_i
assert row["entry_time_utc"] == q.at[entry_i, "timestamp_utc"].isoformat()
assert row["execution_delay_after_signal_close_minutes"] == 5.0
assert row["exit_reason"] == "target"
assert abs(row["exit_price"] - target) < 1e-9

# At exact 16:45 cutoff, use only the executable open; do not inspect later range.
cutoff_i = int((ny == pd.Timestamp("2026-01-05 16:45", tz="America/New_York")).argmax())
q2 = q.copy()
q2.loc[cutoff_i, "bid_open"] = 102.0
q2.loc[cutoff_i, "ask_open"] = 102.1
row2 = m.build_trade_for_signal(q2, pos, signal_i, sig)
assert row2 is not None and row2["exit_reason"] == "target_gap_at_cutoff"
assert abs(row2["exit_price"] - target) < 1e-9
q3 = q2.copy()
q3.loc[cutoff_i, "bid_open"] = 98.0
q3.loc[cutoff_i, "ask_open"] = 98.1
row3 = m.build_trade_for_signal(q3, pos, signal_i, sig)
assert row3 is not None and row3["exit_reason"] == "stop_gap_at_cutoff"
assert row3["exit_price"] == 98.0

# Stable zero-trade metrics schema.
empty = m.metrics(pd.DataFrame(), 0.30)
assert empty["positive_profit_r"] == 0.0 and empty["qs_share_upper_bound"] == 0.0

# Any missing intervening five-minute interval must reject entry.
q4 = q.copy()
q4.loc[signal_i + 1, "timestamp_utc"] += pd.Timedelta(minutes=5)
assert m.build_trade_for_signal(q4, pos, signal_i, sig) is None

# Loader accepts only a complete manifest proving synthetic flats were disabled.
with tempfile.TemporaryDirectory() as td:
    root = Path(td)
    bid_path = root / "xauusd_bid_M5_2016-2026.csv.gz"
    ask_path = root / "xauusd_ask_M5_2016-2026.csv.gz"
    manifest_path = root / "manifest.json"
    stamps = pd.date_range("2016-01-01T00:00:00Z", periods=3, freq="5min")
    for path, off in ((bid_path, 0.0), (ask_path, 0.1)):
        d = pd.DataFrame({
            "timestamp": (stamps.astype("int64") // 1_000_000),
            "open": [100 + off] * 3, "high": [100.2 + off] * 3,
            "low": [99.8 + off] * 3, "close": [100.05 + off] * 3,
        })
        d.to_csv(path, index=False, compression="gzip")

    def make_manifest(flat_flag):
        return {
            "status": "RAW_DATA_COLLECTION_ONLY",
            "source_feed": "Dukascopy through dukascopy-node",
            "instrument": "XAUUSD", "timeframe": "M5",
            "requested_window_utc": {
                "start_inclusive": "2016-01-01", "end_exclusive": "2026-10-16",
            },
            "include_synthetic_flat_bars": flat_flag,
            "outputs": {
                side: {
                    "file": path.name, "rows": 3,
                    "sha256_gzip_file": hashlib.sha256(path.read_bytes()).hexdigest(),
                }
                for side, path in (("bid", bid_path), ("ask", ask_path))
            },
        }

    with patch.object(m, "BID_PATH", bid_path), patch.object(m, "ASK_PATH", ask_path), patch.object(m, "MANIFEST_PATH", manifest_path):
        manifest_path.write_text(json.dumps(make_manifest(False)))
        loaded, audit = m.load_quotes()
        assert len(loaded) == 3 and audit["source_manifest"]["include_synthetic_flat_bars"] is False
        manifest_path.write_text(json.dumps(make_manifest(True)))
        try:
            m.load_quotes()
        except ValueError as exc:
            assert "synthetic flat bars were disabled" in str(exc)
        else:
            raise AssertionError("runner must reject data allowing synthetic flat bars")

print("R272 syntax and functional smoke checks: PASS")
print({
    "entry_time_ny": row["entry_time_ny"],
    "delay_after_close_min": row["execution_delay_after_signal_close_minutes"],
    "normal_exit": row["exit_reason"],
    "cutoff_target": row2["exit_reason"],
    "cutoff_stop": row3["exit_reason"],
    "gap_rejected": True,
    "manifest_no_flats_accepted_and_flats_rejected": True,
})
