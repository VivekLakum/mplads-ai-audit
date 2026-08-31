import os
from pathlib import Path
import pandas as pd

# Resolve relative to this file's location (src/ingestion.py -> project root)
# instead of a hardcoded machine-specific path, so the pipeline runs on any
# machine and any folder name/location.
ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = str(ROOT / "data" / "raw")
PROCESSED_DIR = str(ROOT / "data" / "processed")

FILES_MAP = {
    "LS": {
        "recommended": os.path.join(RAW_DIR, "lok_sabha", "Works Recommended.csv"),
        "sanctioned": os.path.join(RAW_DIR, "lok_sabha", "Works Sanctioned.csv"),
        "expenditure": os.path.join(RAW_DIR, "lok_sabha", "Expenditure on Completed and On-going Works as on Date.csv"),
        "completed": os.path.join(RAW_DIR, "lok_sabha", "Works Completed.csv"),
        "allocation": os.path.join(RAW_DIR, "lok_sabha", "Allocated Limit for Honble MPs (1).csv"),
        "calamity": os.path.join(RAW_DIR, "lok_sabha", "Amount consented for Calamity.csv"),
    },
    "RS": {
        "recommended": os.path.join(RAW_DIR, "rajya_sabha", "Works Recommended.csv"),
        "sanctioned": os.path.join(RAW_DIR, "rajya_sabha", "Works Sanctioned.csv"),
        "expenditure": os.path.join(RAW_DIR, "rajya_sabha", "Expenditure on Completed and On-going Works as on Date.csv"),
        "completed": os.path.join(RAW_DIR, "rajya_sabha", "Works Completed.csv"),
        "allocation": os.path.join(RAW_DIR, "rajya_sabha", "Allocated Limit for Honble MPs.csv"),
        "calamity": os.path.join(RAW_DIR, "rajya_sabha", "Amount consented for Calamity.csv"),
    }
}

def load_raw_datasets():
    """Loads all 12 raw CSV datasets into a dictionary."""
    raw_dfs = {}
    for house in ["LS", "RS"]:
        for key, filepath in FILES_MAP[house].items():
            if os.path.exists(filepath):
                raw_dfs[(house, key)] = pd.read_csv(filepath, low_memory=False)
            else:
                raise FileNotFoundError(f"Raw file not found: {filepath}")
    return raw_dfs
