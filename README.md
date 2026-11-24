# Unemployment Analysis

## Project Overview

This project analyses unemployment patterns across regions of India using the CodeAlpha-style unemployment dataset. The notebook covers data cleaning, monthly regional trends, region-wise comparisons, pre-COVID versus COVID-period descriptions, correlation, and visual summaries.

## Dataset and provenance

The notebook loads the public CSV from the following source:

- [Unemployment_Rate_upto_11_2020.csv, GitHub source](https://raw.githubusercontent.com/SaiyamTuteja/EMPLOYMENT_AND_UNEMPLOYMENT_DATA_ANALYSIS/master/Unemployment_Rate_upto_11_2020.csv)
- [Upstream repository](https://github.com/SaiyamTuteja/EMPLOYMENT_AND_UNEMPLOYMENT_DATA_ANALYSIS)

The filename indicates coverage through November 2020. The analysis should be treated as a historical dataset exercise, not a current unemployment dashboard. The repository does not bundle a fixed CSV snapshot, so rerunning the notebook depends on the availability and unchanged contents of the upstream file.

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
6. Calculate monthly summaries by first averaging repeated observations within each region.
7. Plot both the unweighted mean of regional rates and an estimated labour-force-weighted rate. The weighted estimate infers labour force from employed people divided by the labour-participation rate.
8. Compare unemployment across regions.
9. Compare pre-COVID and COVID periods descriptively.
10. Explore correlations among the supplied numeric fields.
11. Visualize the main patterns.

## Interpretation and limitations

- The notebook reports two monthly measures: an unweighted mean of regional unemployment rates and an estimated labour-force-weighted rate.
- The weighted rate is inferred from supplied estimates. It is not an independently verified official national unemployment rate or a population-weighted estimate based on independently measured labour-force counts.
- Region-level comparisons are descriptive. Differences in regional coverage and record counts can affect the mean.
- The pre-COVID versus COVID comparison does not establish that COVID caused the observed changes.
- Correlation does not establish causation.
- The data ends around November 2020 based on the source file name. It does not represent current labour-market conditions.
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
- Monthly regional aggregation and an estimated labour-force-weighted unemployment summary.

Run tests:

```bash
python -m unittest discover -s tests -v
```

## Technologies

Python, Pandas, NumPy, Matplotlib, Seaborn, Jupyter Notebook, and GitHub Actions.

## Author

Srishti Pandey, MCA Data Science

## Latest GitHub Actions validation

Latest successful notebook and validation workflow on this PR branch before this documentation refresh: [GitHub Actions run #45447709371](https://github.com/krishankantpandey359-droid/Unemployment_Analysis/actions/runs/45447709371). It executed the PR notebook and tests; it does not verify features outside the configured checks.
