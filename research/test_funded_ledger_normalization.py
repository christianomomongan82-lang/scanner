import unittest
import pandas as pd

from replay_funded_challenge_from_ledger import normalize_r298_ledger


class LedgerNormalizationTests(unittest.TestCase):
    def setUp(self):
        self.idx = pd.date_range("2025-01-02T00:00:00Z", periods=5, freq="5min")
        bid = pd.DataFrame({
            "bid_open": [100.0, 100.0, 100.1, 100.2, 100.3],
            "bid_high": [100.5, 100.6, 100.7, 101.2, 100.8],
            "bid_low": [99.8, 99.9, 100.0, 98.8, 100.2],
            "bid_close": [100.1, 100.2, 100.3, 101.0, 100.4],
        }, index=self.idx)
        for col in ("open", "high", "low", "close"):
            bid[f"ask_{col}"] = bid[f"bid_{col}"] + 0.2
        self.bars = bid
        self.bars.attrs["bar_minutes"] = 5

    def row(self, *, direction="LONG", entry_i=0, exit_i=3, entry=100.2,
            exit_price=101.0, stop=99.2, exit_type="TARGET"):
        return {
            "index": 0, "direction": direction,
            "entry_timestamp_utc": self.idx[entry_i].isoformat(),
            "exit_timestamp_utc": self.idx[exit_i].isoformat(),
            "entry_price_executable_side": entry,
            "exit_price_executable_side": exit_price,
            "stop_price_executable_side": stop,
            "target_price_midpoint": 101.0,
            "exit_type": exit_type,
        }

    def test_same_bar_stop_gap_uses_open_fill(self):
        ledger = pd.DataFrame([self.row(
            entry_i=0, exit_i=0, entry=100.2, exit_price=100.0, stop=100.1,
            exit_type="STOP",
        )])
        out = normalize_r298_ledger(ledger, self.bars)
        self.assertTrue(bool(out.iloc[0]["exit_at_open"]))
        self.assertEqual(out.iloc[0]["exit_fill_type"], "OPEN")
        self.assertEqual(out.iloc[0]["entry_time_utc"], out.iloc[0]["exit_time_utc"])

    def test_same_bar_intrabar_stop_remains_intrabar(self):
        ledger = pd.DataFrame([self.row(
            entry_i=0, exit_i=0, entry=100.2, exit_price=99.8, stop=99.2,
            exit_type="STOP",
        )])
        out = normalize_r298_ledger(ledger, self.bars)
        self.assertFalse(bool(out.iloc[0]["exit_at_open"]))
        self.assertEqual(out.iloc[0]["exit_fill_type"], "INTRABAR")

    def test_time_exit_must_match_executable_side_open(self):
        ledger = pd.DataFrame([self.row(
            entry_i=0, exit_i=2, entry=100.2, exit_price=100.2, stop=99.2,
            exit_type="TIME",
        )])
        with self.assertRaisesRegex(ValueError, "TIME exit does not equal executable-side open"):
            normalize_r298_ledger(ledger, self.bars)

    def test_asks_prices_are_used_for_short_exit_validation(self):
        ledger = pd.DataFrame([self.row(
            direction="SHORT", entry_i=0, exit_i=2, entry=100.0,
            exit_price=float(self.bars.iloc[2]["ask_open"]), stop=101.0,
            exit_type="TIME",
        )])
        out = normalize_r298_ledger(ledger, self.bars)
        self.assertTrue(bool(out.iloc[0]["exit_at_open"]))


if __name__ == "__main__":
    unittest.main(verbosity=2)
