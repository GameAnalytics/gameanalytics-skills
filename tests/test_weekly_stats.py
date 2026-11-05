import datetime as dt
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "skills/gameanalytics-weekly-report/scripts"))
import weekly_stats as ws  # noqa: E402

WEEK = dt.date(2026, 10, 26)
WEEK_OFFSETS = [0, 15, -10, 20, -5, 10, -15]


def daily_map(start, days, value_for_week):
    out = {}
    for i in range(days):
        day = start + dt.timedelta(days=i)
        week_index = (day - WEEK).days // 7
        out[day.isoformat()] = value_for_week(week_index)
    return out


def make_data(dau_this=1000, payers=50, new_users=300, revenue_this=500.0):
    start = WEEK - dt.timedelta(days=56)

    def dau(w):
        return dau_this if w == 0 else 1000 + WEEK_OFFSETS[(w + 7) % 7]

    def rev(w):
        return revenue_this / 7 if w == 0 else (500.0 + WEEK_OFFSETS[(w + 7) % 7]) / 7

    return {
        "game": {"id": "1", "name": "Test Game"},
        "week_start": WEEK.isoformat(),
        "daily": {
            "user_unique": daily_map(start, 63, dau),
            "new_users": daily_map(start, 63, lambda w: new_users),
            "revenue": daily_map(start, 63, rev),
            "paying_users": daily_map(start, 63, lambda w: payers),
            "session_unique": daily_map(start, 63, lambda w: 3000),
            "session_length": daily_map(start, 63, lambda w: 300),
        },
        "retention": {
            "d1": daily_map(start, 63, lambda w: 0.30),
            "d7": daily_map(start, 63, lambda w: 0.08),
        },
    }


def kpi(report, key):
    return next(item for item in report["kpis"] if item["key"] == key)


class NormalizeTests(unittest.TestCase):
    def test_raw_chunks_merge(self):
        chunk_a = {"result": [{"timestamp": "2026-10-01T00:00:00.000Z", "result": {"sum": 10.5, "sum_cents": 1050}}]}
        chunk_b = {"result": [{"timestamp": "2026-10-02T00:00:00.000Z", "result": {"sum": 2.0, "sum_cents": 200}}]}
        series = ws.normalize_series([chunk_a, chunk_b], "sum")
        self.assertEqual(series, {dt.date(2026, 10, 1): 10.5, dt.date(2026, 10, 2): 2.0})

    def test_date_value_rows(self):
        series = ws.normalize_series([{"date": "2026-10-01", "value": 3}], "x")
        self.assertEqual(series, {dt.date(2026, 10, 1): 3.0})

    def test_group_breakdown(self):
        raw = {"result": [
            {"timestamp": "2026-10-19T00:00:00.000Z", "result": [{"country_code": "US", "user_unique": 100}]},
            {"timestamp": "2026-10-26T00:00:00.000Z", "result": [{"country_code": "US", "user_unique": 150}]},
        ]}
        this, prev = ws.normalize_breakdown(raw, "country_code", "user_unique", WEEK, WEEK - dt.timedelta(days=7))
        self.assertEqual(this, {"US": 150.0})
        self.assertEqual(prev, {"US": 100.0})


class KpiTests(unittest.TestCase):
    def test_steady_week_not_flagged(self):
        report = ws.build_report(make_data())
        dau = kpi(report, "dau")
        self.assertAlmostEqual(dau["this"], 1000)
        self.assertEqual(dau["anomaly"]["method"], "trend-z")
        self.assertFalse(dau["anomaly"]["flagged"])

    def test_spike_flagged(self):
        report = ws.build_report(make_data(dau_this=1400))
        dau = kpi(report, "dau")
        self.assertTrue(dau["anomaly"]["flagged"])
        self.assertEqual(dau["anomaly"]["direction"], "up")
        self.assertGreater(dau["anomaly"]["z"], 4)

    def test_thin_money_not_flagged(self):
        report = ws.build_report(make_data(payers=5, revenue_this=2000.0))
        revenue = kpi(report, "revenue")
        self.assertTrue(revenue["thin"])
        self.assertFalse(revenue["anomaly"]["flagged"])

    def test_derived_rates(self):
        report = ws.build_report(make_data())
        self.assertAlmostEqual(kpi(report, "arpdau")["this"], 500.0 / 7000, places=6)
        self.assertAlmostEqual(kpi(report, "conversion")["this"], 50 / 1000)
        self.assertAlmostEqual(kpi(report, "sessions_per_user")["this"], 3.0)
        self.assertAlmostEqual(kpi(report, "session_length")["this"], 300)

    def test_retention_windows_and_weighting(self):
        data = make_data()
        d1 = data["retention"]["d1"]
        d1[(WEEK - dt.timedelta(days=1)).isoformat()] = 0.60
        report = ws.build_report(data)
        item = kpi(report, "d1")
        self.assertEqual(item["cohort_window"], ("2026-10-25", "2026-10-31"))
        self.assertAlmostEqual(item["this"], (6 * 0.30 + 0.60) / 7)
        self.assertEqual(kpi(report, "d7")["cohort_window"], ("2026-10-19", "2026-10-25"))

    def test_retention_percent_input(self):
        data = make_data()
        data["retention"]["d1"] = {k: v * 100 for k, v in data["retention"]["d1"].items()}
        self.assertAlmostEqual(kpi(ws.build_report(data), "d1")["this"], 0.30)

    def test_repeat_flag(self):
        first = ws.build_report(make_data(dau_this=1400))
        second = ws.build_report(make_data(dau_this=1400), previous=first)
        self.assertTrue(kpi(second, "dau")["anomaly"]["repeat"])

    def test_ad_revenue_row_omitted_when_zero(self):
        keys = [item["key"] for item in ws.build_report(make_data())["kpis"]]
        self.assertNotIn("ad_revenue", keys)

    def test_non_monday_rejected(self):
        data = make_data()
        data["week_start"] = "2026-10-27"
        with self.assertRaises(ValueError):
            ws.build_report(data)


class MoverTests(unittest.TestCase):
    def test_echo_and_small_slices_dropped(self):
        prev = {"US": 1000, "DE": 1000, "FR": 1000, "XX": 10}
        this = {"US": 1100, "DE": 1500, "FR": 800, "XX": 40}
        result = ws.rank_movers(this, prev)
        self.assertEqual([r["value"] for r in result["up"]], ["DE"])
        self.assertEqual([r["value"] for r in result["down"]], ["FR"])

    def test_markdown_renders(self):
        data = make_data(dau_this=1400)
        data["breakdowns"] = {"platform": {"user_unique": {"this": {"ios": 900, "android": 500},
                                                           "prev": {"ios": 500, "android": 500}}}}
        text = ws.to_markdown(ws.build_report(data))
        self.assertIn("| DAU (average) | 1,400 | 985 | +42.1% | anomaly (up) |", text)
        self.assertIn("Active users by platform", text)


if __name__ == "__main__":
    unittest.main()
