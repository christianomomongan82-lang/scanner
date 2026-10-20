import unittest
from datetime import datetime, timedelta, timezone
from funded_challenge_simulator import ChallengeRules, simulate_challenge


T0 = datetime(2025, 1, 6, 12, 0, tzinfo=timezone.utc)


def event(days, event, trade_id, **kw):
    dt = T0 + timedelta(days=days)
    return {"timestamp_utc": dt.isoformat(), "event_seq": 1, "event": event, "trade_id": trade_id, **kw}


def win_trade(days, tid, risk_pct=0.01, realized_r=1.0, hold=60):
    return [
        event(days, "OPEN", tid, risk_pct=risk_pct),
        event(days, "EXIT", tid, realized_r=realized_r, hold_seconds=hold),
    ]


class ChallengeSimulatorTests(unittest.TestCase):
    def test_sequential_two_phase_pass_requires_min_days(self):
        events = []
        for d in range(8):
            events += win_trade(d, f"p1_{d}")
        for d in range(8, 13):
            events += win_trade(d, f"p2_{d}")
        result = simulate_challenge(events, ChallengeRules(server_timezone="UTC"))
        self.assertEqual(result["status"], "PASS_BOTH_PHASES_WITHIN_179D")
        self.assertEqual(result["phases_completed"], 2)
        self.assertEqual([x["phase"] for x in result["phase_results"]], [1, 2])
        self.assertTrue(all(x["trading_days"] >= 5 for x in result["phase_results"]))

    def test_pass_within_179_calendar_days(self):
        events = []
        for d in range(8):
            events += win_trade(d, f"p1fast_{d}")
        for d in range(175, 180):
            events += win_trade(d, f"p2fast_{d}")
        result = simulate_challenge(events, ChallengeRules(server_timezone="UTC"))
        self.assertEqual(result["status"], "PASS_BOTH_PHASES_WITHIN_179D")
        self.assertEqual(result["phases_completed"], 2)
        self.assertEqual(result["calendar_days_elapsed"], 179)

    def test_pass_too_slow_fails_project_speed_gate(self):
        events = []
        for d in range(8):
            events += win_trade(d, f"p1slow_{d}")
        for d in range(176, 181):
            events += win_trade(d, f"p2slow_{d}")
        result = simulate_challenge(events, ChallengeRules(server_timezone="UTC"))
        self.assertEqual(result["status"], "PASS_BOTH_PHASES_TOO_SLOW")
        self.assertEqual(result["phases_completed"], 2)
        self.assertEqual(result["calendar_days_elapsed"], 180)

    def test_daily_loss_includes_floating_loss(self):
        events = [
            event(0, "OPEN", "bad", risk_pct=0.01),
            event(0, "MARK", "bad", floating_r=-6.0),
        ]
        result = simulate_challenge(events, ChallengeRules(server_timezone="UTC"))
        self.assertEqual(result["status"], "BREACH_DAILY_LOSS")
        self.assertEqual(result["failure_reason"], "daily_loss_limit")

    def test_static_max_loss_floor(self):
        events = []
        for d in range(5):
            events += win_trade(d, f"loss_{d}", risk_pct=0.01, realized_r=-4.0, hold=60)
        result = simulate_challenge(events, ChallengeRules(server_timezone="UTC"))
        self.assertEqual(result["status"], "BREACH_MAX_LOSS")
        self.assertEqual(result["failure_reason"], "maximum_loss_limit")

    def test_quick_strike_blocks_phase_completion(self):
        events = []
        for d in range(8):
            events += win_trade(d, f"fast_{d}", hold=10)
        result = simulate_challenge(events, ChallengeRules(server_timezone="UTC"))
        self.assertNotEqual(result["status"], "PASS_BOTH_PHASES")
        self.assertEqual(result["phases_completed"], 0)
        self.assertGreaterEqual(result["phase_results"][-1]["quick_strike_share"], 0.30)

    def test_open_risk_cap_skips_overlapping_entry(self):
        events = [
            event(0, "OPEN", "first", risk_pct=0.02),
            event(0, "OPEN", "second", risk_pct=0.02),
            event(0, "EXIT", "first", realized_r=0.5, hold_seconds=60),
            event(1, "EXIT", "second", realized_r=1.0, hold_seconds=60),
        ]
        result = simulate_challenge(events, ChallengeRules(server_timezone="UTC"))
        self.assertEqual([x["trade_id"] for x in result["skipped_entries"]], ["second"])
        self.assertEqual(result["trades_closed"], 1)

    def test_rejects_timezone_naive_input(self):
        events = [{"timestamp_utc": "2025-01-01T00:00:00", "event": "OPEN", "trade_id": "x"}]
        with self.assertRaises(ValueError):
            simulate_challenge(events, ChallengeRules(server_timezone="UTC"))


if __name__ == "__main__":
    unittest.main()
