import unittest

import pandas as pd

from src.unemployment import clean_unemployment_data


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
        cleaned, audit = clean_unemployment_data(raw)
        self.assertEqual(len(cleaned), 1)

    def test_rejects_infinite_employment_values(self):
        raw = self.raw.iloc[:2].copy()
        raw["Estimated Employed"] = raw["Estimated Employed"].astype(float)
        raw.loc[0, "Estimated Employed"] = float("inf")
        cleaned, audit = clean_unemployment_data(raw)
        self.assertEqual(len(cleaned), 1)
        self.assertEqual(audit["invalid_rows_removed"], 1)

    def test_rejects_invalid_dates_and_blank_regions(self):
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


if __name__ == "__main__":
    unittest.main()


from src.unemployment import summarize_monthly_unemployment


def test_weighted_monthly_summary_uses_inferred_labour_force_weights():
    raw = pd.DataFrame({
        "Region": ["A", "B"],
        "Date": ["31-01-2020", "31-01-2020"],
        "Estimated Unemployment Rate (%)": [10.0, 20.0],
        "Estimated Employed": [900.0, 800.0],
        "Estimated Labour Participation Rate (%)": [90.0, 80.0],
    })
    result = summarize_monthly_unemployment(raw)
    assert result.loc[0, "regional_mean_unemployment_pct"] == 15.0
    # Both inferred labour forces equal 1,000, so weighted rate is 15%.
    assert result.loc[0, "labour_force_weighted_unemployment_pct"] == 15.0
    assert result.loc[0, "regions"] == 2


def test_weighted_monthly_summary_rejects_invalid_rates():
    raw = pd.DataFrame({
        "Region": ["A"],
        "Date": ["31-01-2020"],
        "Estimated Unemployment Rate (%)": [101.0],
        "Estimated Employed": [900.0],
        "Estimated Labour Participation Rate (%)": [90.0],
    })
    with unittest.TestCase().assertRaisesRegex(ValueError, "between 0 and 100"):
        summarize_monthly_unemployment(raw)


def test_weighted_monthly_summary_rejects_zero_participation():
    raw = pd.DataFrame({
        "Region": ["A"],
        "Date": ["31-01-2020"],
        "Estimated Unemployment Rate (%)": [10.0],
        "Estimated Employed": [0.0],
        "Estimated Labour Participation Rate (%)": [0.0],
    })
    with unittest.TestCase().assertRaisesRegex(
        ValueError, "greater than 0"
    ):
        summarize_monthly_unemployment(raw)
