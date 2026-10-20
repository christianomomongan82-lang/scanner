import unittest
import tempfile
from pathlib import Path
import pandas as pd

from funded_path_adapter import load_paired_bars, build_challenge_events


class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.idx = pd.date_range("2025-01-02T00:00:00Z", periods=5, freq="5min")
        bid = pd.DataFrame({
            "timestamp": [int(ts.timestamp() * 1000) for ts in self.idx],
            "open": [100, 100.0, 100.1, 100.2, 100.3],
            "high": [100.5, 100.6, 100.7, 101.2, 100.8],
            "low": [99.8, 99.9, 100.0, 98.8, 100.2],
            "close": [100.1, 100.2, 100.3, 101.0, 100.4],
        })
        ask = bid.copy()
        for col in ("open", "high", "low", "close"):
            ask[col] += 0.2
        self.bid_path = self.root / "bid.csv.gz"
        self.ask_path = self.root / "ask.csv.gz"
        bid.to_csv(self.bid_path, index=False, compression="gzip")
        ask.to_csv(self.ask_path, index=False, compression="gzip")
        self.bars = load_paired_bars(self.bid_path, self.ask_path, bar_minutes=5)

    def tearDown(self):
        self.tmp.cleanup()

    def test_paired_bars_and_cutoff_are_applied_before_pairing(self):
        ask = pd.read_csv(self.ask_path, compression="gzip").iloc[:-1]
        ask.to_csv(self.ask_path, index=False, compression="gzip")
        bars = load_paired_bars(
            self.bid_path, self.ask_path,
            cutoff_utc=self.idx[-1].isoformat(), bar_minutes=5,
        )
        self.assertEqual(len(bars), 4)
        self.assertEqual(bars.index[-1], self.idx[-2])

    def test_long_marks_use_bid_low_and_entry_uses_ask_open(self):
        trades = [{
            "trade_id": "L1", "direction": "LONG",
            "entry_time_utc": self.idx[0].isoformat(), "exit_time_utc": self.idx[3].isoformat(),
            "entry_price": 100.2, "stop_price": 99.2, "exit_price": 101.0,
            "exit_reason": "TP", "added_cost_price_units": 0.1,
        }]
        events, report = build_challenge_events(trades, self.bars)
        mark = events[(events.event == "MARK") & (events.trade_id == "L1")].iloc[0]
        exit_event = events[(events.event == "EXIT") & (events.trade_id == "L1")].iloc[0]
        self.assertAlmostEqual(mark.adverse_price, 99.8)
        self.assertAlmostEqual(mark.floating_r, -0.5)
        self.assertAlmostEqual(exit_event.realized_r, 0.7)
        self.assertEqual(report["entry_side_checks"], 1)

    def test_short_marks_use_ask_high_and_entry_uses_bid_open(self):
        trades = [{
            "trade_id": "S1", "direction": "SHORT",
            "entry_time_utc": self.idx[0].isoformat(), "exit_time_utc": self.idx[3].isoformat(),
            "entry_price": 100.0, "stop_price": 101.0, "exit_price": 99.0,
            "exit_reason": "TP", "added_cost_price_units": 0.1,
        }]
        events, _ = build_challenge_events(trades, self.bars)
        mark = events[(events.event == "MARK") & (events.trade_id == "S1")].iloc[0]
        exit_event = events[(events.event == "EXIT") & (events.trade_id == "S1")].iloc[0]
        self.assertAlmostEqual(mark.adverse_price, 100.7)
        self.assertAlmostEqual(mark.floating_r, -0.8)
        self.assertAlmostEqual(exit_event.realized_r, 0.9)

    def test_exit_at_open_precedes_new_entry_and_skips_exit_bar_extremes(self):
        trades = [
            {"trade_id": "OLD", "direction": "LONG", "entry_time_utc": self.idx[0].isoformat(),
             "exit_time_utc": self.idx[2].isoformat(), "entry_price": 100.2, "stop_price": 99.2,
             "exit_price": 100.1, "exit_reason": "TIME_OPEN", "exit_at_open": True},
            {"trade_id": "NEW", "direction": "LONG", "entry_time_utc": self.idx[2].isoformat(),
             "exit_time_utc": self.idx[4].isoformat(), "entry_price": 100.3, "stop_price": 99.3,
             "exit_price": 100.3, "exit_reason": "TIME_OPEN", "exit_at_open": True},
        ]
        events, _ = build_challenge_events(trades, self.bars)
        at_t = events[events.timestamp_utc == self.idx[2].isoformat()]
        order = list(zip(at_t.event, at_t.trade_id))
        self.assertLess(order.index(("EXIT", "OLD")), order.index(("OPEN", "NEW")))
        self.assertFalse(any((at_t.event == "MARK") & (at_t.trade_id == "OLD")))

    def test_favorable_target_gap_fills_at_target_cap(self):
        bars = self.bars.copy()
        t = self.idx[4]
        bars.loc[t, ["bid_open", "bid_high", "bid_low", "bid_close"]] = [101.5, 101.7, 101.2, 101.4]
        bars.loc[t, ["ask_open", "ask_high", "ask_low", "ask_close"]] = [101.7, 101.9, 101.4, 101.6]
        trades = [{
            "trade_id": "TG", "direction": "LONG",
            "entry_time_utc": self.idx[0].isoformat(), "exit_time_utc": t.isoformat(),
            "entry_price": 100.2, "stop_price": 99.2, "target_price": 101.0,
            "exit_price": 101.0, "exit_reason": "TP_GAP_CAPPED",
            "exit_at_open": True, "exit_fill_type": "TARGET_CAP",
        }]
        events, report = build_challenge_events(trades, bars)
        exit_event = events[(events.event == "EXIT") & (events.trade_id == "TG")].iloc[0]
        self.assertAlmostEqual(exit_event.exit_price, 101.0)
        self.assertTrue(bool(exit_event.exit_at_open))
        self.assertEqual(report["target_cap_exit_count"], 1)
        self.assertAlmostEqual(exit_event.realized_r, 0.8)

    def test_missing_bar_grid_fails_closed(self):
        trades = [{
            "trade_id": "GAP", "direction": "LONG",
            "entry_time_utc": self.idx[0].isoformat(), "exit_time_utc": self.idx[4].isoformat(),
            "entry_price": 100.2, "stop_price": 99.2, "exit_price": 100.6,
            "exit_reason": "TP",
        }]
        with self.assertRaisesRegex(ValueError, "missing/inconsistent"):
            build_challenge_events(trades, self.bars.drop(self.idx[2]))

    def test_wrong_executable_entry_price_fails_closed(self):
        trades = [{
            "trade_id": "BAD", "direction": "LONG",
            "entry_time_utc": self.idx[0].isoformat(), "exit_time_utc": self.idx[3].isoformat(),
            "entry_price": 100.0, "stop_price": 99.0, "exit_price": 101.0,
            "exit_reason": "TP",
        }]
        with self.assertRaisesRegex(ValueError, "does not match executable ASK open"):
            build_challenge_events(trades, self.bars)

    def test_wrong_side_stop_fails_closed(self):
        trades = [{
            "trade_id": "BADSTOP", "direction": "LONG",
            "entry_time_utc": self.idx[0].isoformat(), "exit_time_utc": self.idx[3].isoformat(),
            "entry_price": 100.2, "stop_price": 100.5, "exit_price": 101.0,
            "exit_reason": "TP",
        }]
        with self.assertRaisesRegex(ValueError, "wrong side of entry"):
            build_challenge_events(trades, self.bars)

    def test_adverse_mark_is_before_intrabar_exit(self):
        trades = [{
            "trade_id": "ORDER", "direction": "LONG",
            "entry_time_utc": self.idx[0].isoformat(), "exit_time_utc": self.idx[3].isoformat(),
            "entry_price": 100.2, "stop_price": 99.2, "exit_price": 99.2,
            "exit_reason": "SL", "exit_at_open": False,
        }]
        events, _ = build_challenge_events(trades, self.bars)
        same = events[events.timestamp_utc == self.idx[3].isoformat()]
        self.assertLess(list(same.event).index("MARK"), list(same.event).index("EXIT"))


    def _cycle_test_bars(self):
        idx = pd.date_range("2025-01-02T00:00:00Z", "2025-01-04T00:00:00Z", freq="5min")
        base = 100.0 + pd.Series(range(len(idx)), dtype=float).to_numpy() * 0.001
        bars = pd.DataFrame(index=idx)
        bars["bid_open"] = base
        bars["bid_high"] = base + 0.10
        bars["bid_low"] = base - 0.10
        bars["bid_close"] = base + 0.02
        for col in ("open", "high", "low", "close"):
            bars[f"ask_{col}"] = bars[f"bid_{col}"] + 0.20
        bars.attrs["bar_minutes"] = 5
        return bars

    def test_trade_is_forced_closed_at_cycle_end_executable_open(self):
        bars = self._cycle_test_bars()
        cutoff = pd.Timestamp("2025-01-03T23:45:00Z")
        end = pd.Timestamp("2025-01-04T00:00:00Z")
        trades = [{
            "trade_id": "AUTO", "phase": 1, "direction": "LONG",
            "entry_time_utc": bars.index[0].isoformat(), "exit_time_utc": end.isoformat(),
            "entry_price": bars.iloc[0]["ask_open"], "stop_price": bars.iloc[0]["ask_open"] - 1,
            "exit_price": bars.loc[end, "bid_open"], "exit_reason": "PLANNED_TIME_EXIT",
            "exit_at_open": True, "added_cost_price_units": 0.1,
        }]
        events, report = build_challenge_events(
            trades, bars, server_timezone="UTC", quick_strike_cycle_days=2,
        )
        exit_event = events[(events.event == "EXIT") & (events.trade_id == "AUTO")].iloc[0]
        self.assertEqual(pd.Timestamp(exit_event.timestamp_utc), cutoff)
        self.assertAlmostEqual(exit_event.exit_price, bars.loc[cutoff, "bid_open"])
        self.assertEqual(exit_event.exit_reason, "CYCLE_AUTO_CLOSE")
        self.assertTrue(bool(exit_event.exit_at_open))
        self.assertEqual(report["cycle_auto_close_count"], 1)

    def test_missing_cycle_end_quote_fails_closed(self):
        bars = self._cycle_test_bars()
        cutoff = pd.Timestamp("2025-01-03T23:45:00Z")
        end = pd.Timestamp("2025-01-04T00:00:00Z")
        bars = bars.drop(cutoff)
        trades = [{
            "trade_id": "NOCUTOFF", "phase": 1, "direction": "LONG",
            "entry_time_utc": pd.Timestamp("2025-01-02T00:00:00Z").isoformat(),
            "exit_time_utc": end.isoformat(),
            "entry_price": 100.2, "stop_price": 99.2,
            "exit_price": 101.0, "exit_reason": "PLANNED_TIME_EXIT", "exit_at_open": True,
        }]
        with self.assertRaisesRegex(ValueError, "cycle auto-close quote missing"):
            build_challenge_events(
                trades, bars, server_timezone="UTC", quick_strike_cycle_days=2,
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
