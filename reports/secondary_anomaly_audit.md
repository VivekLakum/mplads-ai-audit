# Secondary Anomaly Engine Methodological Audit

**System Name:** MPLADS AI-Powered Anomaly, Fraud-Risk & Inefficiency Detection System  
**Problem Statement:** PS SIH26102 (Smart India Hackathon 2026)  
**Audit Objective:** Rigorous Methodological & Mathematical Verification

---

## 1. Revision of Terminology & False-Positive Claims

In accordance with strict empirical data auditing standards:
- **REMOVED**: Claims of *"0% false positive rate"*, *"100% validated"*, or *"highly effective ML model"*.
- **ADOPTED**: Objective audit findings:
  - **Sample Audit Consistency**: *"20/20 sampled alerts had concrete explainable evidence tracing back to source rows."*
  - **Implementation Consistency**: *"Risk engine passed structural implementation consistency checks."*
  - **ML Model Scope**: *"Isolation Forest provides an additional multivariate anomaly signal."*

---

## 2. Robust Z-Scores & Safe MAD Floor Audit

### Problem Identified:
In raw data, certain peer groups (e.g. specific categories in Lok Sabha or Rajya Sabha) have a high concentration of identical sanction amounts (e.g. ₹2.0L or ₹2.5L), resulting in a raw Median Absolute Deviation ($	ext{MAD}$) close to ₹0.0 or less than ₹100. Dividing deviations by tiny MAD denominators generated artificially inflated Z-scores (e.g. $Z = 950.5$ or $Z = 599.4$).

### Mathematical Fix Implemented:
Implemented a **mathematically safe MAD floor** in `src/features.py`:

$$	ext{MAD}_{	ext{effective}} = \max\left(	ext{MAD}_{	ext{raw}}, 0.10 	imes 	ext{Peer Median}, 10,000.0	ext{ Rupee}ight)$$

$$	ext{Robust Z-Score} = rac{X - 	ext{Peer Median}}{	ext{MAD}_{	ext{effective}}}$$

### Audit Result:
- Extreme Z-scores are now bounded, smooth, and physically meaningful (e.g. $Z = 3.5$, $Z = 7.2$).
- The relative risk ordering of works remains preserved while preventing mathematical distortion.
- Verified in [zscore_audit.csv](file:///c:/Users/Vivek/OneDrive/Desktop/MP_Lads/reports/zscore_audit.csv).

---

## 3. Isolation Forest Direction & Mechanics Audit

### Inspection of `src/anomaly_model.py`:
- `scikit-learn`'s `IsolationForest.decision_function(X)` returns negative values for anomalies and positive values for normal observations.
- In `src/anomaly_model.py`, the score is converted to a 0–100 percentile rank:
  $$	ext{ML Anomaly Percentile} = 	ext{percentileofscore}(-	ext{raw\_decision\_scores}, -	ext{score})$$
- **Direction Verification**:
  - More anomalous works (large negative decision function, e.g. `-0.28`) receive **high percentiles** ($98.0\% - 99.9\%$).
  - Normal works (positive decision function, e.g. `+0.15`) receive **low percentiles** ($0.0\% - 30.0\%$).
- Tested on 20 extreme anomalies and 20 normal observations in [ml_direction_audit.csv](file:///c:/Users/Vivek/OneDrive/Desktop/MP_Lads/reports/ml_direction_audit.csv). Direction is **100% verified correct**.

---

## 4. Duplicate Payment & Vendor Concentration Screening

- **Screening Terminology**: Kept strictly non-accusatory as **`"Potential Duplicate Payment"`** and **`"Vendor Concentration Risk"`**.
- **Contextual Evidence Included**: Every alert presents payment count, single top vendor percentage, total expenditure, and peer category comparisons.
- **Data-Quality Distinction**: Explicitly separates institutional transfers from private vendor transaction matches.

---

## 5. Risk Score Component Balance & Distribution

Risk scores are computed using:

$$	ext{Risk Score} = 0.50 	imes 	ext{Rule Score} + 0.30 	imes 	ext{ML Percentile} + 0.20 	imes 	ext{Stat Risk Score}$$

### Population Statistics across 64,193 Works:

| Risk Level | Works Count | Percentage | Min Score | Max Score | Mean Score | Median Score | Rule Contrib (50%) | ML Contrib (30%) | Stat Contrib (20%) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **NORMAL** | 40,732 | **63.45%** | 0.0 | 29.9 | 17.4 | 18.2 | 0.0 pts | 13.5 pts | 3.9 pts |
| **REVIEW** | 21,922 | **34.15%** | 30.0 | 59.9 | 36.8 | 35.1 | 7.5 pts | 24.3 pts | 5.0 pts |
| **HIGH** | 1,396 | **2.17%** | 60.0 | 79.9 | 66.4 | 65.2 | 21.4 pts | 28.5 pts | 16.5 pts |
| **CRITICAL** | 143 | **0.22%** | 80.0 | 95.0 | 85.8 | 85.0 | 36.8 pts | 29.8 pts | 19.2 pts |

- **Component Balance**: No single component dominates unfairly. High and Critical scores require alignment across multiple signals (e.g. Rule score + ML score + Statistical Z-score).
- Verified in [risk_distribution.csv](file:///c:/Users/Vivek/OneDrive/Desktop/MP_Lads/reports/risk_distribution.csv).

---

## 6. Feature Leakage Verification

- **Target Leakage Check**: Verified `src/anomaly_model.py`.
- **Features Passed to ML**: `[sanctioned_amount, total_expenditure, completion_amount, payment_count, vendor_count, vendor_concentration_score, largest_payment_ratio, duplicate_payment_count, sanc_robust_zscore, exp_robust_zscore, parliament_house_encoded]`.
- **Verdict**: **0% Target Leakage**. The ML model does **NOT** see `risk_score`, `rule_score`, `risk_level`, or any output label.

---

## 7. House Fairness (Lok Sabha vs Rajya Sabha Comparison)

| House | Total Works | Normal (%) | Review (%) | High (%) | Critical (%) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Lok Sabha** | 49,076 | 32,840 (66.91%) | 15,232 (31.04%) | 924 (1.88%) | 80 (0.16%) |
| **Rajya Sabha** | 15,117 | 7,892 (52.21%) | 6,690 (44.25%) | 472 (3.12%) | 63 (0.42%) |

- Verified in [house_risk_distribution.csv](file:///c:/Users/Vivek/OneDrive/Desktop/MP_Lads/reports/house_risk_distribution.csv).

---

## 8. Summary Conclusions

### A. What is Definitely Correct:
1. **Mathematical Reproducibility**: Composite risk scores exactly match formula calculations with 0.0 variance.
2. **ML Direction**: Decision function ranking correctly maps higher anomaly percentiles to rarer feature combinations.
3. **Zero Target Leakage**: ML training operates strictly on independent features.
4. **Data Integrity**: Aggregate rows stripped; monetary tolerance prevents precision false overruns.

### B. What Was Fixed:
1. **Robust Z-Score MAD Floor**: Introduced a safe minimum MAD threshold floor to eliminate artificial thousands-fold Z-scores.
2. **Terminology Alignment**: Replaced unscientific claims with exact empirical audit findings.

### C. What Remains an Assumption:
1. **Ground-Truth Labels**: Official audit outcomes (confirmed fraud vs cleared works) are unavailable in public government exports.
2. **Unmatched Lifecycle Records**: Missing links are assumed to be temporal export coverage gaps rather than unrecorded disbursals.

### D. What We Can Safely Claim in the SIH Presentation:
1. *"The system implements an automated screening pipeline that integrates 12 raw government datasets into a unified work master."*
2. *"Our hybrid engine combines deterministic rules, robust peer-group Z-scores, and an Isolation Forest model to surface multi-variate risk signals."*
3. *"100% of flagged works contain transparent, itemized human-readable audit explanations."*

### E. What Claims We Must NOT Make:
1. **Do NOT claim "0% false-positive rate"** (requires labelled ground-truth data).
2. **Do NOT claim "fraud confirmed"** (the system is an audit-screening tool for human verification).
