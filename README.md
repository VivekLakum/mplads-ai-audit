# MPLADS AI Audit Intelligence — SIH26102

Government-grade audit screening frontend for the existing MPLADS anomaly pipeline.

## Source of truth
The frontend reads the existing `outputs/anomaly_results.csv` and processed expenditure/allocation files. It does **not** reimplement or modify anomaly detection, rules, Isolation Forest, robust Z-score logic, feature engineering, lifecycle classification, weights, or thresholds.

Expected current output: 64,193 works — 54,946 NORMAL, 8,796 REVIEW, 423 HIGH, 28 CRITICAL.

## Run the self-contained demo
This package includes a vendored React runtime so the demo can be run without downloading Node dependencies:

```powershell
python -m pip install -r requirements.txt
uvicorn backend.api:app --reload
```

Open `http://127.0.0.1:8000`.

## Standard Vite workflow
`frontend/package.json`, `vite.config.js`, and `src/main.jsx` are included for a conventional React/Vite workflow when npm registry access is available. The chat build environment used for this delivery did not have npm network access, so the runnable demo uses the vendored React browser runtime rather than pretending an offline `npm install` succeeded.

## Included features
- Home / Command Center
- Lok Sabha and Rajya Sabha chamber views
- Interactive clickable SVG India state map
- State drill-down
- MP profile with initials placeholder when no photo source exists
- Work-level audit evidence
- Critical Cases queue
- Risk Explorer with server-side pagination
- Spending Outliers based on backend expenditure robust Z-score
- No line charts
- Audit-safe terminology and human-verification disclaimer

## Data discipline
Missing fields are shown as `Data Not Available`. Rajya Sabha constituency is never fabricated; the current schema has no nodal/assigned district field, so that value is explicitly unavailable.

## Original pipeline
The existing Python pipeline under `src/` and `run_pipeline.py` is retained. The original Streamlit dashboard is retained under `dashboard/` and is not used by the new web dashboard.

## Important map note
`frontend/public/maps/india-states.svg` is a compact interactive SVG navigation asset for the prototype. It is not intended as a legal or survey boundary source.
