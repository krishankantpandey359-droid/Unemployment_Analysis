"""Validation helpers for the India unemployment EDA notebook."""
from __future__ import annotations

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

    valid = (
        df["Region"].notna()
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
