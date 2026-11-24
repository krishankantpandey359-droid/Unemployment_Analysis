import unittest

import numpy as np
import pandas as pd

from src.unemployment import (
    clean_unemployment_data,
    summarize_monthly_unemployment,
)


class TestUnemploymentDataCleaning(unittest.TestCase):
    def setUp(self):
        self.raw = pd.DataFrame(
            {
                "Region": ["A", "B", "A"],
                "Date": ["31-01-2020", "31-01-2020", "31-01-2020"],
                "Estimated Unemployment Rate (%)": [10.0, 20.0, 10.0],
                "Estimated Employed": [1000, 2000, 1000],
                "Estimated Labour Participation Rate (%)": [40.0, 50.0, 40.0],
            }
        )

    def test_valid_rows_and_duplicate_audit(self):
        cleaned, audit = clean_unemployment_data(self.raw)
        self.assertEqual(len(cleaned), 2)
        self.assertEqual(audit["exact_duplicate_rows_removed"], 1)
        self.assertEqual(audit["rows_after_cleaning"], 2)
        self.assertEqual(str(cleaned["Date"].dtype), "datetime64[ns]")

    def test_rejects_out_of_range_percentages(self):
        raw = self.raw.iloc[:2].copy()
        raw.loc[0, "Estimated Unemployment Rate (%)"] = 101
        cleaned, audit = clean_unemployment_data(raw)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(audit["invalid_rows_removed"], 1)

    def test_rejects_negative_employment(self):
        raw = self.raw.iloc[:2].copy()
        raw.loc[0, "Estimated Employed"] = -1
        cleaned, _ = clean_unemployment_data(raw)
        self.assertEqual(len(cleaned), 1)

    def test_rejects_infinite_employment_values(self):
        raw = self.raw.iloc[:2].copy()
        raw["Estimated Employed"] = raw["Estimated Employed"].astype(float)
        raw.loc[0, "Estimated Employed"] = float("inf")
        cleaned, audit = clean_unemployment_data(raw)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(audit["invalid_rows_removed"], 1)

    def test_rejects_invalid_dates(self):
        raw = self.raw.iloc[:2].copy()
        raw.loc[0, "Date"] = "not-a-date"
        cleaned, audit = clean_unemployment_data(raw)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(audit["invalid_rows_removed"], 1)

    def test_rejects_blank_region(self):
        raw = self.raw.iloc[:2].copy()
        raw.loc[0, "Region"] = "   "
        cleaned, audit = clean_unemployment_data(raw)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(audit["invalid_rows_removed"], 1)

    def test_missing_required_column_fails(self):
        with self.assertRaisesRegex(ValueError, "Missing required columns"):
            clean_unemployment_data(self.raw.drop(columns=["Region"]))

    def test_empty_valid_dataset_fails(self):
        raw = self.raw.iloc[:1].copy()
        raw["Estimated Unemployment Rate (%)"] = 150
        with self.assertRaisesRegex(ValueError, "No valid rows"):
            clean_unemployment_data(raw)

    def test_trims_column_whitespace_before_validation(self):
        raw = self.raw.rename(columns={"Region": " Region ", "Date": " Date "})
        cleaned, _ = clean_unemployment_data(raw)
        self.assertEqual(len(cleaned), 2)
        self.assertIn("Region", cleaned.columns)
        self.assertIn("Date", cleaned.columns)

    def test_rejects_duplicate_columns_after_whitespace_normalization(self):
        raw = self.raw.copy()
        raw[" Region "] = raw["Region"]
        with self.assertRaisesRegex(ValueError, "Duplicate column names"):
            clean_unemployment_data(raw)

    def test_rejects_non_dataframe_input(self):
        with self.assertRaisesRegex(TypeError, "DataFrame"):
            clean_unemployment_data([{"Region": "A"}])


class TestMonthlyUnemploymentSummary(unittest.TestCase):
    def setUp(self):
        self.raw = pd.DataFrame(
            {
                "Region": ["A", "A", "B"],
                "Date": ["01-01-2020", "15-01-2020", "31-01-2020"],
                "Estimated Unemployment Rate (%)": [10.0, 20.0, 30.0],
                "Estimated Employed": [900.0, 800.0, 1600.0],
                "Estimated Labour Participation Rate (%)": [90.0, 80.0, 80.0],
            }
        )

    def test_groups_observations_by_region_before_monthly_weighting(self):
        result = summarize_monthly_unemployment(self.raw)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.loc[0, "Month"], "2020-01")
        self.assertEqual(result.loc[0, "regions"], 2)
        self.assertAlmostEqual(result.loc[0, "regional_mean_unemployment_pct"], 22.5)
        self.assertAlmostEqual(
            result.loc[0, "labour_force_weighted_unemployment_pct"], 25.0
        )

    def test_rejects_out_of_range_unemployment_rate(self):
        raw = self.raw.copy()
        raw.loc[0, "Estimated Unemployment Rate (%)"] = 101
        with self.assertRaisesRegex(ValueError, "between 0 and 100"):
            summarize_monthly_unemployment(raw)

    def test_rejects_zero_labour_participation(self):
        raw = self.raw.copy()
        raw.loc[0, "Estimated Labour Participation Rate (%)"] = 0
        with self.assertRaisesRegex(ValueError, "greater than 0"):
            summarize_monthly_unemployment(raw)

    def test_rejects_non_finite_numeric_values(self):
        raw = self.raw.copy()
        raw.loc[0, "Estimated Employed"] = np.inf
        with self.assertRaisesRegex(ValueError, "non-finite"):
            summarize_monthly_unemployment(raw)

    def test_rejects_missing_required_values(self):
        raw = self.raw.copy()
        raw.loc[0, "Date"] = "invalid-date"
        with self.assertRaisesRegex(ValueError, "missing or invalid"):
            summarize_monthly_unemployment(raw)


if __name__ == "__main__":
    unittest.main(verbosity=2)
