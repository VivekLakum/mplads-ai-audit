import sys
import os
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from dashboard.app import load_app_data

anomaly_df, expenditures_df, allocation_df, calamity_df = load_app_data()

print("APP DATA LOADED SUCCESSFULLY IN HEADLESS TEST!")
print(f"Anomaly DF Shape: {anomaly_df.shape}")
print(f"Expenditures DF Shape: {expenditures_df.shape}")
print(f"Allocation DF Shape: {allocation_df.shape}")
print(f"Calamity DF Shape: {calamity_df.shape}")
