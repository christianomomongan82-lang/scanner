"""Infrastructure-only smoke test against the archived XAUUSD BID/ASK artifact.

This test verifies the raw archive and exercises the price adapter on one deliberately synthetic
position. It does not generate any signal, measure strategy expectancy, or estimate challenge-pass
probability.
"""
import hashlib
import json
import os
from pathlib import Path
import unittest

import pandas as pd

from funded_path_adapter import load_paired_bars, build_challenge_events


BID_SHA256 = "b30eb4864db0777b6df612f3e43ccda9cc59db5ca09974191eabdaca1f6ff575"
ASK_SHA256 = "b9b174a83df70507be4ab0cd556432a0d14fbac2e596e787325bd1f163772fc9"
CUTOFF = "2026-01-01T00:00:00Z"


class RealArchiveSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        root = Path(os.environ.get("RAW_DATA_DIR", "../raw")).resolve()
        cls.bid_path = root / "xauusd_bid_M5_2016-2026.csv.gz"
        cls.ask_path = root / "xauusd_ask_M5_2016-2026.csv.gz"
        cls.manifest_path = root / "manifest.json"
        for path in (cls.bid_path, cls.ask_path, cls.manifest_path):
            if not path.is_file():
                raise FileNotFoundError(f"required raw archive file missing: {path}")
        cls.manifest = json.loads(cls.manifest_path.read_text(encoding="utf-8"))
        cls.bid_hash = hashlib.sha256(cls.bid_path.read_bytes()).hexdigest()
        cls.ask_hash = hashlib.sha256(cls.ask_path.read_bytes()).hexdigest()
        if cls.bid_hash != BID_SHA256 or cls.ask_hash != ASK_SHA256:
            raise AssertionError("raw BID/ASK member SHA-256 does not match registered source manifest")
        cls.bars = load_paired_bars(
            cls.bid_path, cls.ask_path, cutoff_utc=CUTOFF, bar_minutes=5,
        )

    def test_exact_archived_source_and_exclusive_cutoff(self):
        self.assertEqual(len(self.bars), 877930)
        self.assertEqual(self.bars.index[0], pd.Timestamp("2016-01-03T00:00:00Z"))
        self.assertEqual(self.bars.index[-1], pd.Timestamp("2025-12-31T21:55:00Z"))
        self.assertTrue((self.bars.index < pd.Timestamp(CUTOFF)).all())
        self.assertEqual(int((self.bars.index.to_series().diff() > pd.Timedelta(minutes=5)).sum()), 530)
        self.assertEqual(self.manifest["outputs"]["bid"]["rows"], 947326)
        self.assertEqual(self.manifest["outputs"]["ask"]["rows"], 947326)

    def test_adapter_emits_path_from_one_synthetic_position_on_real_quotes(self):
        # Prefer a full, observed 20-minute window in ordinary weekday hours so
        # this test exercises real parsed quotes rather than a synthetic price series.
        bars = self.bars
        step = pd.Timedelta(minutes=5)
        chosen = None
        for i in range(1000, len(bars) - 4):
            ts = bars.index[i]
            local = ts.tz_convert("Europe/London")
            if local.weekday() >= 5 or not (8 <= local.hour <= 16):
                continue
            window = bars.index[i:i + 4]
            if len(window) == 4 and window.equals(pd.date_range(ts, periods=4, freq=step, tz="UTC")):
                # At least one non-flat executable-side bar proves the price path
                # is not just a row of constant quote snapshots.
                part = bars.iloc[i:i + 4]
                if ((part["bid_high"] > part["bid_low"]) | (part["ask_high"] > part["ask_low"])).any():
                    chosen = (i, window)
                    break
        self.assertIsNotNone(chosen, "no complete active-looking weekday quote window found")
        i, window = chosen
        entry_ts, exit_ts = window[0], window[-1]
        entry_price = float(bars.loc[entry_ts, "ask_open"])
        exit_price = float(bars.loc[exit_ts, "bid_open"])
        trades = [{
            "trade_id": "INFRA-SMOKE-ONLY", "phase": 1, "direction": "LONG",
            "entry_time_utc": entry_ts.isoformat(), "exit_time_utc": exit_ts.isoformat(),
            "entry_price": entry_price, "stop_price": entry_price - 5.0,
            "exit_price": exit_price, "exit_reason": "SMOKE_TIME_EXIT",
            "exit_at_open": True, "added_cost_price_units": 0.0,
        }]
        events, report = build_challenge_events(trades, bars)
        self.assertEqual(report["trade_count"], 1)
        self.assertEqual(report["entry_side_checks"], 1)
        self.assertEqual(report["grid_gaps"], 0)
        self.assertEqual(int((events["event"] == "OPEN").sum()), 1)
        self.assertEqual(int((events["event"] == "MARK").sum()), 3)
        self.assertEqual(int((events["event"] == "EXIT").sum()), 1)
        self.assertEqual(len(events), 5)
        self.assertTrue(events["timestamp_utc"].map(lambda x: pd.Timestamp(x) < pd.Timestamp(CUTOFF)).all())
        print(json.dumps({
            "scope": "infrastructure smoke test; no strategy outcome scored",
            "bid_sha256": self.bid_hash,
            "ask_sha256": self.ask_hash,
            "bars_pre_cutoff": len(self.bars),
            "gaps_gt_5m_preserved": 530,
            "synthetic_position_count": 1,
            "events_emitted": len(events),
            "chosen_entry_utc": entry_ts.isoformat(),
            "chosen_exit_utc": exit_ts.isoformat(),
            "strategy_pnl_scored": False,
        }, sort_keys=True))


if __name__ == "__main__":
    unittest.main(verbosity=2)
