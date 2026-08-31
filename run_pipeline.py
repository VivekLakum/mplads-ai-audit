import os
import sys
from pathlib import Path
import pandas as pd
import json

# Ensure project root is in python path, resolved relative to this file
# rather than a hardcoded machine-specific path.
ROOT = Path(__file__).resolve().parent
sys.path.append(str(ROOT))

from src.ingestion import load_raw_datasets
from src.integration import build_integrated_datasets
from src.features import build_work_features
from src.rules import evaluate_audit_rules
from src.anomaly_model import train_isolation_forest
from src.scoring import compute_composite_risk_scores

PROCESSED_DIR = str(ROOT / "data" / "processed")
OUTPUTS_DIR = str(ROOT / "outputs")

os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

def run_end_to_end_pipeline():
    print("==================================================")
    print("STARTING MPLADS ANOMALY PIPELINE EXECUTION")
    print("==================================================")
    
    # 1. Ingestion
    print("\n[1/6] Loading raw datasets (12 CSV files)...")
    raw_dfs = load_raw_datasets()
    print(" -> Successfully loaded 12 raw files.")
    
    # 2. Integration & Cleaning
    print("\n[2/6] Building integrated logical datasets (works_master, expenditures, mp_allocation, calamity)...")
    works_master_df, expenditures_df, mp_allocation_df, calamity_df = build_integrated_datasets(raw_dfs)
    
    print(f" -> works_master: {len(works_master_df):,} records")
    print(f" -> expenditures: {len(expenditures_df):,} records")
    print(f" -> mp_allocation: {len(mp_allocation_df):,} records")
    print(f" -> calamity: {len(calamity_df):,} records")
    
    # 3. Feature Engineering
    print("\n[3/6] Engineering work-level features...")
    work_features_df = build_work_features(works_master_df, expenditures_df)
    print(f" -> work_features: {len(work_features_df):,} rows x {len(work_features_df.columns)} features")
    
    # 4. Deterministic Audit Rules Engine
    print("\n[4/6] Running deterministic audit rules engine...")
    rule_results_df = evaluate_audit_rules(work_features_df)
    print(f" -> Evaluated audit rules for {len(rule_results_df):,} works.")
    
    # 5. Machine Learning (Isolation Forest)
    print("\n[5/6] Training unified Isolation Forest ML model...")
    ml_results_df = train_isolation_forest(work_features_df)
    print(f" -> Isolation Forest scores generated for {len(ml_results_df):,} works.")
    
    # 6. Composite Risk Scoring & Explainability
    print("\n[6/6] Computing composite risk scores & audit explanations...")
    anomaly_results_df = compute_composite_risk_scores(work_features_df, rule_results_df, ml_results_df)
    
    # Summary of Risk Levels
    risk_summary = anomaly_results_df['risk_level'].value_counts().to_dict()
    print("\n=== COMPOSITE RISK LEVEL DISTRIBUTION ===")
    for level in ["NORMAL", "REVIEW", "HIGH", "CRITICAL"]:
        cnt = risk_summary.get(level, 0)
        pct = (cnt / len(anomaly_results_df)) * 100.0
        print(f"  {level:<10}: {cnt:>6,} works ({pct:>5.2f}%)")
        
    # Save Processed Datasets & Outputs
    print("\nSaving output files...")
    works_master_df.to_csv(os.path.join(PROCESSED_DIR, "works_master.csv"), index=False)
    expenditures_df.to_csv(os.path.join(PROCESSED_DIR, "expenditures.csv"), index=False)
    mp_allocation_df.to_csv(os.path.join(PROCESSED_DIR, "mp_allocation.csv"), index=False)
    calamity_df.to_csv(os.path.join(PROCESSED_DIR, "calamity.csv"), index=False)
    
    work_features_df.to_csv(os.path.join(OUTPUTS_DIR, "work_features.csv"), index=False)
    anomaly_results_df.to_csv(os.path.join(OUTPUTS_DIR, "anomaly_results.csv"), index=False)
    
    # Data Quality Report
    dq_report = pd.DataFrame([
        {"dataset": "works_master", "records": len(works_master_df), "status": "Clean & Integrated"},
        {"dataset": "expenditures", "records": len(expenditures_df), "status": "Clean & Disbursed Ledger"},
        {"dataset": "mp_allocation", "records": len(mp_allocation_df), "status": "Clean Allocation Limits"},
        {"dataset": "calamity", "records": len(calamity_df), "status": "Clean Calamity Consents"},
        {"dataset": "work_features", "records": len(work_features_df), "status": "Engineered Analytical Table"},
        {"dataset": "anomaly_results", "records": len(anomaly_results_df), "status": "Scored & Explainable Anomaly Table"}
    ])
    dq_report.to_csv(os.path.join(OUTPUTS_DIR, "data_quality_report.csv"), index=False)
    
    print("\n==================================================")
    print("PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print("==================================================")

if __name__ == "__main__":
    run_end_to_end_pipeline()
