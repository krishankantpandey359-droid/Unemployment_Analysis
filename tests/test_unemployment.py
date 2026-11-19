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


    def test_trims_column_whitespace_before_required_column_validation(self):
        raw = self.raw.rename(columns={
            "Region": " Region ",
            "Date": " Date ",
        })
        cleaned, audit = clean_unemployment_data(raw)
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
