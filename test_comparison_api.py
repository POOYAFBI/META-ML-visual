from __future__ import annotations

import unittest

from backend.services.comparison import comparison


class ComparisonContractTest(unittest.TestCase):
    def test_regression_contract(self):
        data = comparison("regression")
        self.assert_contract(data, "regression", "rmse")
        row = data["rows"][0]
        for key in ("rmse", "mae", "r2", "normalized_rmse", "rank", "interpretation"):
            self.assertIn(key, row)

    def test_classification_contract(self):
        data = comparison("classification")
        self.assert_contract(data, "classification", "weighted_f1")
        row = data["rows"][0]
        for key in ("accuracy", "weighted_f1", "macro_f1", "rank", "interpretation"):
            self.assertIn(key, row)

    def assert_contract(self, data, task, primary_metric):
        self.assertEqual(data["task"], task)
        self.assertEqual(data["primary_metric"], primary_metric)
        self.assertEqual(len(data["summary_cards"]), 4)
        self.assertEqual(set(data["insights"]), {"overall_takeaway", "dataset_effect", "model_behavior", "metric_caution"})
        self.assertGreater(len(data["rows"]), 0)
        self.assertEqual(data["best"]["rank"], 1)
        self.assertIn(primary_metric, data["metric_definitions"])
        self.assertEqual(len(data["chart_config"]), 2)
        for row in data["rows"]:
            for key in (
                "id",
                "dataset_id",
                "dataset_label_fa",
                "dataset_label_en",
                "dataset_raw_name",
                "model_label_fa",
                "model_label_en",
                "model_raw_name",
            ):
                self.assertIn(key, row)


if __name__ == "__main__":
    unittest.main()
