"""
Export company-specific data (symbol keyed) from MongoDB to CSV files.
Uses latest record per symbol from symbol_profile and symbol_info collections.
Intended for weekly run after update_symbol_profile and update_symbol_info.
"""
import os
from os.path import join

import pandas as pd
import market_data as md

from .symbol_financial_info.mdb_in_out import df_symbol_profile

# Subdir under SM_DATA_DIR for company CSVs (None = data_dir root)
COMPANY_CSV_SUBDIR = "company_data"

# Columns to export: symbol + these (use None to export all)
PROFILE_CSV_COLUMNS = [
    "symbol",
    "companyName",
    "sectorname",
    "primaryname",
    "marketCap",
    "divYield",
    "peRatioFwd",
    "estimateEps",
    "volume",
    "shortIntPctFloat",
]
INFO_CSV_COLUMNS = [
    "symbol",
    "peRatioFwd",
    "estimateEps",
    "divYield",
    "shortIntPctFloat",
    "marketCap",
    "volume",
    "evEbit",
    "evEbitda",
    "priceBook",
    "priceSales",
    "roe",
    "roa",
    "revenueGrowth",
]


def get_all_symbols_from_directories():
    """Unique symbols across all portfolio directories (from existing CSVs)."""
    dirs = md.get_directorys()
    symbols = set()
    for directory in dirs:
        symbols.update(md.get_symbols(directory=directory))
    return sorted(symbols)


def df_latest_profile_from_mdb(symbols=None):
    """DataFrame of latest symbol_profile per symbol (one row per symbol)."""
    df = df_symbol_profile(symbols=symbols or [])
    if df.empty or "Date" not in df.columns:
        return df
    df = df.sort_values("Date").groupby("symbol", as_index=False).last()
    return df


def df_latest_info_from_mdb(symbols=None):
    """DataFrame of latest symbol_info per symbol (one row per symbol)."""
    df = md.df_from_mdb_all_data(md.db_symbol_info, dateidx=False)
    if df.empty:
        return df
    if "_id" in df.columns:
        df = df.drop(columns=["_id"], errors="ignore")
    if "Date" not in df.columns:
        return df
    if symbols is not None:
        df = df[df["symbol"].isin(symbols)]
    df = df.sort_values("Date").groupby("symbol", as_index=False).last()
    return df


def _filter_columns(df, wanted):
    """Keep only columns that exist in df."""
    if wanted is None:
        return df
    existing = [c for c in wanted if c in df.columns]
    return df[existing] if existing else df


def export_profile_csv(output_dir=None, columns=PROFILE_CSV_COLUMNS):
    """Write symbol_profile (latest per symbol) to CSV. Returns path."""
    df = df_latest_profile_from_mdb()
    if df.empty:
        print("No symbol_profile data in MongoDB.")
        return None
    df = _filter_columns(df, columns)
    out_dir = output_dir or join(md.data_dir, COMPANY_CSV_SUBDIR)
    os.makedirs(out_dir, exist_ok=True)
    path = join(out_dir, "symbol_profile.csv")
    df.to_csv(path, index=False)
    print("Wrote symbol_profile:", path, "rows:", len(df))
    return path


def export_info_csv(output_dir=None, columns=INFO_CSV_COLUMNS):
    """Write symbol_info (latest per symbol) to CSV. Returns path."""
    df = df_latest_info_from_mdb()
    if df.empty:
        print("No symbol_info data in MongoDB.")
        return None
    df = _filter_columns(df, columns)
    out_dir = output_dir or join(md.data_dir, COMPANY_CSV_SUBDIR)
    os.makedirs(out_dir, exist_ok=True)
    path = join(out_dir, "symbol_info.csv")
    df.to_csv(path, index=False)
    print("Wrote symbol_info:", path, "rows:", len(df))
    return path


def export_company_csv(output_dir=None, profile_cols=PROFILE_CSV_COLUMNS, info_cols=INFO_CSV_COLUMNS):
    """
    One CSV with symbol + key profile and info fields (latest per symbol).
    Merges profile and info on symbol; info overwrites overlapping columns.
    """
    dfp = df_latest_profile_from_mdb()
    dfi = df_latest_info_from_mdb()
    if dfp.empty and dfi.empty:
        print("No profile or info data in MongoDB.")
        return None
    out_dir = output_dir or join(md.data_dir, COMPANY_CSV_SUBDIR)
    os.makedirs(out_dir, exist_ok=True)
    path = join(out_dir, "company_info.csv")

    if dfp.empty:
        df = _filter_columns(dfi, info_cols)
    elif dfi.empty:
        df = _filter_columns(dfp, profile_cols)
    else:
        dfp = _filter_columns(dfp, profile_cols)
        dfi = _filter_columns(dfi, info_cols)
        # merge: profile first, then info (info overwrites)
        df = dfp.merge(
            dfi,
            on="symbol",
            how="outer",
            suffixes=("", "_info"),
        )
        # drop duplicate columns from info merge
        dup = [c for c in df.columns if c.endswith("_info")]
        df = df.drop(columns=dup, errors="ignore")
    df.to_csv(path, index=False)
    print("Wrote company_info:", path, "rows:", len(df))
    return path


def run_export(
    profile=True,
    info=True,
    company=True,
    output_dir=None,
):
    """
    Export profile, info, and/or combined company CSV to CSVs.
    output_dir: default is SM_DATA_DIR/company_data/
    """
    output_dir = output_dir or join(md.data_dir, COMPANY_CSV_SUBDIR)
    paths = []
    if profile:
        p = export_profile_csv(output_dir=output_dir)
        if p:
            paths.append(p)
    if info:
        p = export_info_csv(output_dir=output_dir)
        if p:
            paths.append(p)
    if company:
        p = export_company_csv(output_dir=output_dir)
        if p:
            paths.append(p)
    return paths


if __name__ == "__main__":
    run_export()
