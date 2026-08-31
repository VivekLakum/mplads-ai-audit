import pandas as pd
import numpy as np
import re

def is_grand_total_row(row):
    """Detects if any cell in the row represents a Grand Total summary row."""
    for val in row:
        val_str = str(val).strip()
        if re.search(r'^\s*(Grand\s+Total|Total)\b', val_str, re.IGNORECASE):
            return True
    return False

def clean_dataframe(df):
    """Strips exactly one aggregate row and cleans row whitespace."""
    if df.empty:
        return df
    gt_mask = df.apply(is_grand_total_row, axis=1)
    df_clean = df[~gt_mask].copy()
    
    # Strip string columns
    for col in df_clean.select_dtypes(include=['object']).columns:
        df_clean[col] = df_clean[col].astype(str).str.strip()
        df_clean[col] = df_clean[col].replace({'nan': np.nan, 'None': np.nan, '': np.nan})
        
    return df_clean

def parse_amount(val):
    """Parses monetary strings with rupee symbols and commas into float64."""
    if pd.isna(val) or str(val).strip().lower() in ['nan', 'none', '']:
        return np.nan
    val_str = str(val).replace(',', '').replace('₹', '').replace('Rs.', '').replace('Rs', '').strip()
    try:
        return float(val_str)
    except:
        return np.nan

def parse_date(val):
    """Parses date strings into standardized pandas datetime objects."""
    if pd.isna(val) or str(val).strip().lower() in ['nan', 'none', '']:
        return pd.NaT
    return pd.to_datetime(val, errors='coerce')
