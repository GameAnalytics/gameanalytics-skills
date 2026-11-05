import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills/gameanalytics-tracking-plan/scripts"))
import check_plan as cp  # noqa: E402


def plan(*rows):
    out = []
    for i, (etype, event_id, values, per_user) in enumerate(rows):
        out.append((i + 2, {"event_type": etype, "event_id": event_id, "values": values,
                            "per_user_per_day": str(per_user)}))
    return out


class CheckPlanTests(unittest.TestCase):
    def test_template_passes(self):
        result = cp.check_plan(cp.read_rows(ROOT / "skills/gameanalytics-tracking-plan/assets/tracking-plan-template.csv"))
        self.assertTrue(result["ok"], result["errors"])
        self.assertEqual(result["warnings"], [])
        progression = next(b for b in result["budget"] if b["limit"].startswith("progression"))
        self.assertEqual(progression["planned"], 3 * 5 * 20)

    def test_cardinality_product_and_limit(self):
        result = cp.check_plan(plan(("design", "enemy:{kind}:{area}", "kind=1..200; area=1..80", 1)))
        design = next(b for b in result["budget"] if b["limit"].startswith("design"))
        self.assertEqual(design["planned"], 16000)
        self.assertFalse(result["ok"])

    def test_safe_line_is_a_warning(self):
        result = cp.check_plan(plan(("design", "enemy:{kind}", "kind=1..14000", 1)))
        self.assertTrue(result["ok"])
        self.assertTrue(any("safe line" in w for w in result["warnings"]))

    def test_dynamic_placeholder_rejected(self):
        result = cp.check_plan(plan(("design", "level:end:{score}", "score=1..10", 1)))
        self.assertTrue(any("dynamic value" in e for e in result["errors"]))

    def test_unbounded_placeholder_rejected(self):
        result = cp.check_plan(plan(("design", "shop:{item}", "", 1)))
        self.assertTrue(any("unbounded" in e for e in result["errors"]))

    def test_design_part_count_and_characters(self):
        result = cp.check_plan(plan(("design", "a:b:c:d:e:f", "", 1), ("design", "bad/char", "", 1)))
        self.assertTrue(any("1 to 5 parts" in e for e in result["errors"]))
        self.assertTrue(any("'bad/char'" in e for e in result["errors"]))

    def test_progression_status(self):
        result = cp.check_plan(plan(("progression", "{s}:Level{n}", "s=Begin|Complete; n=1..3", 2)))
        self.assertTrue(any("'Begin'" in e for e in result["errors"]))

    def test_resource_rules(self):
        result = cp.check_plan(plan(("resource", "{f}:{c}:shop:pack", "f=Source|Spend; c=Gems|Coins2", 1)))
        errors = " ".join(result["errors"])
        self.assertIn("'Spend'", errors)
        self.assertIn("'Coins2'", errors)

    def test_too_many_currencies(self):
        currencies = "|".join(f"Cur{chr(65 + i // 26)}{chr(65 + i % 26)}" for i in range(21))
        result = cp.check_plan(plan(("resource", "Source:{c}:reward:daily", f"c={currencies}", 1)))
        self.assertTrue(any("21 resource currencies" in e for e in result["errors"]))

    def test_custom_dimension_limits(self):
        values = "|".join(f"v{i}" for i in range(21))
        result = cp.check_plan(plan(("custom_dimension_01", "segment", f"values={values}", 0)))
        self.assertTrue(any("21 values" in e for e in result["errors"]))

    def test_events_per_user(self):
        result = cp.check_plan(plan(("design", "ui:tap", "", 520)))
        self.assertTrue(any("events per user per day" in e for e in result["errors"]))

    def test_casing_within_type_warns(self):
        result = cp.check_plan(plan(("design", "Shop:open", "", 1), ("design", "shop:close", "", 1)))
        self.assertTrue(any("inconsistent casing" in w for w in result["warnings"]))


if __name__ == "__main__":
    unittest.main()
