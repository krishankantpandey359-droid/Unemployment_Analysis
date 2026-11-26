# Unemployment Analysis

## Project Overview

This project analyses unemployment patterns across regions of India using the CodeAlpha-style unemployment dataset. The notebook covers data cleaning, monthly regional trends, region-wise comparisons, pre-COVID versus COVID-period descriptions, correlation, and visual summaries.

## Dataset and provenance

The notebook loads the public CSV from the following source:

- [Unemployment_Rate_upto_11_2020.csv, GitHub source](https://raw.githubusercontent.com/SaiyamTuteja/EMPLOYMENT_AND_UNEMPLOYMENT_DATA_ANALYSIS/master/Unemployment_Rate_upto_11_2020.csv)
- [Upstream repository](https://github.com/SaiyamTuteja/EMPLOYMENT_AND_UNEMPLOYMENT_DATA_ANALYSIS)

The upstream filename includes `upto_11_2020`, but the CSV snapshot inspected for this audit contains observations from January through October 2020, with 31 October 2020 as the latest recorded date. The analysis is a historical dataset exercise, not a current unemployment dashboard. The repository does not bundle a fixed CSV snapshot, so rerunning the notebook depends on the availability and unchanged contents of the upstream file.

Main fields:
- Region
- Date
- Estimated Unemployment Rate (%)
- Estimated Employed
- Estimated Labour Participation Rate (%)

## Analysis performed

1. Load the public CSV.
2. Inspect columns, types, missing values, and summary statistics.
3. Normalize column names and validate required fields.
4. Parse dates and numeric measures.
5. Remove exact duplicate records and invalid rows.
6. Calculate the unweighted monthly mean of the available regional unemployment rates.
7. Compare unemployment across regions.
8. Compare pre-COVID and COVID periods descriptively.
9. Explore correlations among the supplied numeric fields.
10. Visualize the main patterns.

## Interpretation and limitations

- The `main` notebook reports both the unweighted mean of regional unemployment rates and an estimated labour-force-weighted rate.
- Repeated observations are first averaged within each region and month, so regions with more weekly records do not receive extra weight.
- The weighted result is inferred from supplied employment and labour-participation estimates, not independently measured labour-force counts. It is an approximation, not an official national unemployment estimate.
- Region-level comparisons are descriptive. Differences in regional coverage and record counts can affect the mean.
- The pre-COVID versus COVID comparison does not establish that COVID caused the observed changes.
- Correlation does not establish causation.
- The inspected CSV records end on 31 October 2020, despite the upstream filename containing `upto_11_2020`. It does not represent current labour-market conditions.
- The upstream CSV is fetched at notebook runtime and is not pinned to a commit in this repository. For strict reproducibility, archive an approved snapshot with its retrieval date and checksum.
- Cleaning rules remove rows with invalid dates, non-finite values, out-of-range percentage values, negative employment, or blank region names. Review the audit output before interpreting results.

## Reusable validation module

`src/unemployment.py` provides:
- Required-column validation after trimming header whitespace.
- Duplicate-column detection after normalization.
- Date and numeric parsing.
- Exact duplicate removal.
- Range and finite-value validation.
- A row-count audit before and after cleaning.

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Technologies

Python, Pandas, NumPy, Matplotlib, Seaborn, Jupyter Notebook, and GitHub Actions.

## Author

Srishti Pandey, MCA Data Science

## Latest GitHub Actions validation

Latest successful main-branch workflow run verified on 26 November 2026: [GitHub Actions run #45804944646](https://github.com/krishankantpandey359-droid/Unemployment_Analysis/actions/runs/45804944646). This confirms the configured automated checks, not every manual or deployment feature.
