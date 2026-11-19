"""Validation helpers for the India unemployment EDA notebook."""
from __future__ import annotations

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = [
    "Region",
    "Date",
    "Estimated Unemployment Rate (%)",
    "Estimated Employed",
    "Estimated Labour Participation Rate (%)",
]
NUMERIC_COLUMNS = REQUIRED_COLUMNS[2:]


def clean_unemployment_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Validate, normalize and clean a copy of the supplied regional dataset."""
    missing = [column for column in REQUIRED_COLUMNS if column not in raw.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    df = raw.copy()
    df.columns = df.columns.astype(str).str.strip()
    df["Region"] = df["Region"].astype("string").str.strip()
    df["Date"] = pd.to_datetime(df["Date"], dayfirst=True, errors="coerce")

    for column in NUMERIC_COLUMNS:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    before = len(df)
    duplicate_rows = int(df.duplicated().sum())
    df = df.drop_duplicates().copy()

    finite_numeric = np.isfinite(df[NUMERIC_COLUMNS].to_numpy(dtype=float)).all(axis=1)
    valid = (
        finite_numeric
        & df["Region"].notna()
        & df["Region"].ne("")
        & df["Date"].notna()
        & df["Estimated Unemployment Rate (%)"].between(0, 100)
        & df["Estimated Employed"].ge(0)
        & df["Estimated Labour Participation Rate (%)"].between(0, 100)
    )
    invalid_rows = int((~valid).sum())
    df = df.loc[valid].copy()

    if df.empty:
        raise ValueError("No valid rows remain after data validation.")

    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    audit = {
        "rows_before_cleaning": before,
        "exact_duplicate_rows_removed": duplicate_rows,
        "invalid_rows_removed": invalid_rows,
        "rows_after_cleaning": len(df),
    }
    return df.reset_index(drop=True), audit


def summarize_monthly_unemployment(df: pd.DataFrame) -> pd.DataFrame:
    """Compare simple regional mean with a labour-force-weighted estimate.

    Estimated labour force is derived as employed / participation rate.
    The weighted value is an approximation from the supplied estimates,
    not an independently verified official national rate.
    """
    required = set(REQUIRED_COLUMNS)
    missing = sorted(required - set(df.columns))
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    data = df.copy()
    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")
    if data[NUMERIC_COLUMNS].isna().any().any():
        raise ValueError("Monthly summary contains missing or non-numeric measures.")
    if not np.isfinite(data[NUMERIC_COLUMNS].to_numpy(dtype=float)).all():
        raise ValueError("Monthly summary contains non-finite measures.")
    if not data["Estimated Unemployment Rate (%)"].between(0, 100).all():
        raise ValueError("Unemployment rate must be between 0 and 100.")
    if not data["Estimated Labour Participation Rate (%)"].between(0, 100).all():
        raise ValueError("Labour participation rate must be between 0 and 100.")
    if (data["Estimated Employed"] < 0).any():
        raise ValueError("Estimated employed values must not be negative.")

    participation = data["Estimated Labour Participation Rate (%)"] / 100.0
    data["Estimated Labour Force"] = np.where(
        participation > 0,
        data["Estimated Employed"] / participation,
        np.nan,
    )
    data["Unemployed Estimate"] = (
        data["Estimated Labour Force"]
        * data["Estimated Unemployment Rate (%)"] / 100.0
    )
    grouped = data.groupby("Date", sort=True)
    result = grouped.agg(
        regional_mean_unemployment_pct=(
            "Estimated Unemployment Rate (%)", "mean"
        ),
        estimated_labour_force=("Estimated Labour Force", "sum"),
        estimated_unemployed=("Unemployed Estimate", "sum"),
        regions=("Region", "nunique"),
    ).reset_index()
    result["labour_force_weighted_unemployment_pct"] = np.where(
        result["estimated_labour_force"] > 0,
        result["estimated_unemployed"] / result["estimated_labour_force"] * 100,
        np.nan,
    )
    return result
