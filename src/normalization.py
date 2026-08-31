import re
import pandas as pd
import numpy as np

def extract_strict_work_id(val):
    """Extracts strict normalized Work ID from text strings."""
    if pd.isna(val) or str(val).strip().lower() in ['nan', 'none', '']:
        return None
    val_str = str(val).strip()
    
    # Standard format: WS/MP<digits>/<year-range>/<work_id_digits>
    m = re.search(r'\b(WS\s*/\s*MP\s*\d+\s*/\s*\d{4}-\d{4}\s*/\s*\d+)\b', val_str, re.IGNORECASE)
    if m:
        return re.sub(r'\s+', '', m.group(1)).upper()
        
    # Single year format: WS/MP<digits>/<year>/<work_id_digits>
    m2 = re.search(r'\b(WS\s*/\s*MP\s*\d+\s*/\s*\d{4}\s*/\s*\d+)\b', val_str, re.IGNORECASE)
    if m2:
        return re.sub(r'\s+', '', m2.group(1)).upper()

    # General prefix format: WS/<alnum>/<year_range_or_year>/<digits>
    m3 = re.search(r'\b(WS\s*/\s*[A-Z0-9_]+\s*/\s*[0-9\-]+\s*/\s*\d+)\b', val_str, re.IGNORECASE)
    if m3:
        return re.sub(r'\s+', '', m3.group(1)).upper()
        
    return None

def normalize_mp_name(name):
    if pd.isna(name):
        return "Unknown MP"
    clean = str(name).strip()
    clean = re.sub(r'^(Shri|Smt\.|Smt|Dr\.|Dr|Hon\'ble|Honble)\s+', '', clean, flags=re.IGNORECASE).strip()
    clean = re.sub(r'\s*\(\d{4}-\d{2}\).*$', '', clean).strip()
    return clean.title()

def normalize_state(state):
    if pd.isna(state):
        return "Unknown State"
    clean = str(state).strip().title()
    # Canonical state name mappings
    mappings = {
        "Andaman & Nicobar Islands": "Andaman And Nicobar Islands",
        "Dadra & Nagar Haveli": "Dadra And Nagar Haveli",
        "Jammu & Kashmir": "Jammu And Kashmir",
        "Odisha": "Odisha",
        "Orissa": "Odisha"
    }
    return mappings.get(clean, clean)
