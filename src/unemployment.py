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
    if not isinstance(raw, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame.")
    df = raw.copy()
    df.columns = df.columns.astype(str).str.strip()
    if df.columns.duplicated().any():
        duplicates = df.columns[df.columns.duplicated()].tolist()
        raise ValueError(f"Duplicate column names after trimming whitespace: {duplicates}")
    missing = [column for column in REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
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
    """Summarize regional unemployment and an inferred labour-force-weighted rate.

    Labour force is estimated as employed divided by the labour participation
    rate. Regional weekly observations are averaged within each month before
    regional estimates are combined. The weighted result is an approximation
    from the supplied estimates, not an independently verified official rate.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame.")
    data = df.copy()
    data.columns = data.columns.astype(str).str.strip()
    if data.columns.duplicated().any():
        duplicates = data.columns[data.columns.duplicated()].tolist()
        raise ValueError(f"Duplicate column names after trimming whitespace: {duplicates}")
    missing = [column for column in REQUIRED_COLUMNS if column not in data.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    data["Region"] = data["Region"].astype("string").str.strip()
    data["Date"] = pd.to_datetime(data["Date"], dayfirst=True, errors="coerce")
    for column in NUMERIC_COLUMNS:
        data[column] = pd.to_numeric(data[column], errors="coerce")

    if data.empty:
        raise ValueError("Monthly summary requires at least one observation.")
    if data[["Region", "Date", *NUMERIC_COLUMNS]].isna().any().any():
        raise ValueError("Monthly summary contains missing or invalid required values.")
    if data["Region"].eq("").any():
        raise ValueError("Monthly summary contains blank region names.")
    values = data[NUMERIC_COLUMNS].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("Monthly summary contains non-finite measures.")
    if not data["Estimated Unemployment Rate (%)"].between(0, 100).all():
        raise ValueError("Unemployment rate must be between 0 and 100.")
    participation_pct = data["Estimated Labour Participation Rate (%)"]
    if not participation_pct.between(0, 100).all():
        raise ValueError("Labour participation rate must be between 0 and 100.")
    if (data["Estimated Employed"] < 0).any():
        raise ValueError("Estimated employed values must not be negative.")
    participation = participation_pct / 100.0
    if participation.le(0).any():
        raise ValueError("Labour participation rate must be greater than 0 to infer labour force.")

    data["Month"] = data["Date"].dt.to_period("M").astype(str)
    data["Estimated Labour Force"] = data["Estimated Employed"] / participation
    data["Estimated Unemployed"] = (
        data["Estimated Labour Force"]
        * data["Estimated Unemployment Rate (%)"] / 100.0
    )

    # Average repeated observations within each region first, so regions with
    # more weekly records do not receive extra weight in the monthly estimate.
    regional = data.groupby(["Month", "Region"], as_index=False).agg(
        regional_unemployment_pct=("Estimated Unemployment Rate (%)", "mean"),
        estimated_labour_force=("Estimated Labour Force", "mean"),
        estimated_unemployed=("Estimated Unemployed", "mean"),
    )
    result = regional.groupby("Month", as_index=False).agg(
        regional_mean_unemployment_pct=("regional_unemployment_pct", "mean"),
        estimated_labour_force=("estimated_labour_force", "sum"),
        estimated_unemployed=("estimated_unemployed", "sum"),
        regions=("Region", "nunique"),
    )
    result["labour_force_weighted_unemployment_pct"] = (
        result["estimated_unemployed"] / result["estimated_labour_force"] * 100.0
    )
    return result
