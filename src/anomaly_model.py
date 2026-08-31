import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import RobustScaler

def train_isolation_forest(df_feat):
    """Trains a unified Isolation Forest model across all works with parliament_house retained as a feature."""
    df_ml = df_feat.copy()
    
    # Feature Selection for ML
    df_ml['parliament_house_encoded'] = np.where(df_ml['parliament_house'] == 'Lok Sabha', 1.0, 0.0)
    
    ml_feature_cols = [
        'sanctioned_amount',
        'total_expenditure',
        'completion_amount',
        'payment_count',
        'vendor_count',
        'vendor_concentration_score',
        'largest_payment_ratio',
        'duplicate_payment_count',
        'sanc_robust_zscore',
        'exp_robust_zscore',
        'parliament_house_encoded'
    ]
    
    X = df_ml[ml_feature_cols].copy()
    
    # Convert to numeric and use population medians for missing values.
    # Missingness is not treated as anomaly evidence.
    for col in ml_feature_cols:
        X[col] = pd.to_numeric(X[col], errors='coerce')
        median_value = X[col].median()
        X[col] = X[col].fillna(
            median_value if pd.notnull(median_value) else 0.0
        )
        
    # Log transform monetary features to handle extreme skewness
    monetary_cols = ['sanctioned_amount', 'total_expenditure', 'completion_amount']
    for col in monetary_cols:
        X[col] = np.log1p(np.maximum(0.0, X[col]))
        
    # Scale features using RobustScaler
    scaler = RobustScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Isolation Forest
    clf = IsolationForest(
        n_estimators=150,
        contamination='auto',
        random_state=42,
        n_jobs=-1
    )
    clf.fit(X_scaled)
    
    # Decision function (lower score means more anomalous)
    raw_scores = clf.decision_function(X_scaled)
    
    # Invert raw score so higher = more anomalous (0.0 to 1.0)
    # Min-Max normalize inverted raw scores
    inv_scores = -raw_scores
    min_s, max_s = inv_scores.min(), inv_scores.max()
    ml_score = (inv_scores - min_s) / max(max_s - min_s, 1e-6)
    
    # Compute ML Anomaly Percentile (0 to 100)
    percentiles = pd.Series(ml_score).rank(pct=True) * 100.0
    
    res_df = pd.DataFrame({
        "work_id": df_feat["work_id"],
        "ml_anomaly_score": np.round(ml_score, 4),
        "ml_anomaly_percentile": np.round(percentiles, 1)
    })
    
    return res_df
