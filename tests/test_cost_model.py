import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "cost"))

from cost_model import as_markdown, estimate, line_cost, load_json  # noqa: E402


class LineCostTests(unittest.TestCase):
    def test_hourly_price_is_scaled_to_a_month(self):
        # 2 servers x $0.0168/h x 730 h = $24.528
        self.assertAlmostEqual(line_cost({"usd": 0.0168, "unit": "hour"}, 2), 24.528)

    def test_non_hourly_price_is_not_scaled(self):
        # 40 GB x $0.08 per GB-month = $3.20
        self.assertAlmostEqual(line_cost({"usd": 0.08, "unit": "GB-month"}, 40), 3.20)

    def test_negative_quantity_rejected(self):
        with self.assertRaises(ValueError):
            line_cost({"usd": 1, "unit": "month"}, -1)


class EstimateTests(unittest.TestCase):
    PRICES = {"a": {"usd": 1.0, "unit": "month"}, "b": {"usd": 0.01, "unit": "hour"}}

    def test_total_is_sum_of_lines(self):
        scenario = {"items": [{"item": "A", "price": "a", "quantity": 3},
                              {"item": "B", "price": "b", "quantity": 1}]}
        lines, total = estimate(scenario, self.PRICES)
        self.assertEqual(len(lines), 2)
        self.assertAlmostEqual(total, 3 + 7.30)

    def test_unknown_price_key_rejected(self):
        with self.assertRaises(KeyError):
            estimate({"items": [{"item": "X", "price": "missing", "quantity": 1}]}, self.PRICES)

    def test_markdown_has_total_row(self):
        table = as_markdown("demo", [("A", 1.0), ("B", 3.0)], 4.0)
        self.assertIn("| **Total** | **4.00** | 100% |", table)
        self.assertLess(table.index("| B |"), table.index("| A |"))  # most expensive first


class RepositoryDataTests(unittest.TestCase):
    """Pin the published totals so ARCHITECTURE.md can't silently drift from the model."""

    def setUp(self):
        self.prices = load_json(ROOT / "cost" / "pricing.json")["prices"]
        self.scenarios = load_json(ROOT / "cost" / "scenarios.json")

    def test_small_total(self):
        _, total = estimate(self.scenarios["small"], self.prices)
        self.assertAlmostEqual(total, 147.563, places=2)

    def test_production_total(self):
        _, total = estimate(self.scenarios["production"], self.prices)
        self.assertAlmostEqual(total, 426.757, places=2)


if __name__ == "__main__":
    unittest.main()
