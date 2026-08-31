# MPLADS AI Audit Intelligence — Final Implementation Report

**Problem Statement:** SIH26102 — AI-powered system to detect anomalies, fraud, and
inefficiencies in MPLAD Scheme implementation.

**Dataset:** 64,193 works, 694 MPs, 35 states/UTs (existing pipeline output,
`outputs/anomaly_results.csv`).

This report covers only the work done in this delivery: closing the remaining
gaps between the existing project and the PS. The existing anomaly/risk
pipeline (`src/`, `run_pipeline.py`) was **not modified** and was **not
re-run** — every number below that comes from the original pipeline
(NORMAL/REVIEW/HIGH/CRITICAL counts, rule/ML/statistical scores) is
unchanged from the uploaded project.

---

## 1. PS Requirements — Status

| # | PS Requirement | Status | Notes |
|---|---|---|---|
| — | Sanctions/expenditure/progress/payment analysis | Already present | Existing pipeline |
| — | Risk-based alerts, decision-support dashboards | Already present | Existing pipeline + dashboard |
| — | Deterministic + statistical + ML anomaly detection | Already present | Existing pipeline (untouched) |
| 1 | **Duplicate work detection** | **Implemented** | New. See §2.1 |
| 2 | **Cost overrun detection** | **Implemented** | New. See §2.2. Dataset currently shows **zero** overruns where determinable |
| 3 | **Automated compliance monitoring** | **Implemented** | New. See §2.3 |
| 4 | **Early warning system** | **Implemented** | New. See §2.4 |
| 5 | **Predictive insights** | **Implemented as transparent risk estimate** | New. Explicitly not a guaranteed prediction — see §2.5 |
| 6 | **Trend analysis** | **Implemented** | New. See §2.6 |
| 7 | Stakeholder decision support (MP/State/District/Ministry hierarchy) | Already present, extended | Existing National → State → MP → Work hierarchy; new pages slot into the same navigation |
| 8 | Actionable recommendations | **Implemented** | Every early-warning and duplicate result carries a `recommended_action` string, never an accusation |
| 9 | Human-readable risk explanations (existing) | Preserved unchanged | Not touched |
| — | Implementing agency / GPS field matching for duplicates | **Cannot be determined** | Not present in source data — see §3 |

---

## 2. New Features (what was added)

### 2.1 Duplicate Work Detection (`backend/analytics.py`)
Distinct from the pipeline's existing *duplicate payment ledger record*
signal (which was already present and is unchanged). This is new
work-to-work comparison.

**Method:** description text is normalized (lowercased, punctuation and
boilerplate words stripped) and candidates are generated within blocks of
(MP, constituency, 4-token signature) to keep ~64k works tractable. Three
tiers are reported:

- **Tier A — "Potential Duplicate":** exactly two works from the same MP
  share an identical normalized description, the same sanctioned amount,
  and the same sanction date.
- **Tier B — "Possible Duplicate":** fuzzy text match (≥85% similarity),
  sanctioned amount within 5%, sanction dates within 30 days.
- **Tier C — "Batch / Repeated Work Pattern":** 3+ works sharing identical
  description + amount + date. Explicitly **not** labelled a duplicate —
  in this dataset this pattern almost always reflects one scheme rolled out
  as many identical units (e.g. dozens of identical LED poles sanctioned
  together), and is surfaced only for transparency.

Every result carries `"requires human audit verification"` and never
claims two works *are* duplicates.

An earlier version of this feature flagged tens of thousands of pairs
because MPLADS descriptions are frequently boilerplate-identical across
many legitimate installations (see §3). The three-tier design above was
adopted specifically to avoid that false-positive flood, at the cost of
being conservative — some true near-duplicates worded very differently
will not be caught.

### 2.2 Cost Overrun Analysis
Uses the existing pipeline fields (`expenditure_overrun_amount`,
`completion_overrun_amount`, `is_sanction_overrun`,
`completion_expenditure_comparison_available`) — **not recomputed**. This
module only interprets and exposes them, and adds a risk band derived
live from the dataset's own overrun-percentage distribution (33rd/67th
percentile), not an invented fixed threshold. Where sanctioned amount or a
comparable actual/completion amount isn't available, the API returns
`"Cost overrun cannot be determined from available source data"` rather
than a fabricated value.

### 2.3 Automated Compliance Monitoring
Per-work checks over fields that already exist in the pipeline output
(recommendation/sanction/payment/completion availability, approval
duration vs. the dataset's own 90th-percentile pattern, duplicate
indicators, lifecycle completeness). Statuses: `COMPLIANT`,
`PARTIALLY COMPLIANT`, `REQUIRES REVIEW`, `INSUFFICIENT DATA`.

Important correction made during testing: an initial version treated
"not yet sanctioned" as a failed compliance check, which produced a
misleading 81% REQUIRES REVIEW rate. Fixed so that recommendation-only
works (no sanction issued yet — a normal pipeline stage) are correctly
reported as `INSUFFICIENT DATA`, not non-compliant, matching the
requirement not to label missing data as a violation.

### 2.4 Early Warning System
Combines the existing `risk_level` with the new duplicate, cost-overrun,
and compliance signals into `Immediate Review` / `Priority Review` /
`Monitor`, each with plain-language reasons and a non-accusatory
recommended action (e.g. "Review sanction, expenditure and completion
records"). Never uses the word "fraud".

### 2.5 Predictive Insights (Risk Estimate)
Explicitly labelled **"Risk estimate (not a guaranteed prediction)"**
throughout the API and UI. This is a transparent, rule-based estimate
built only from fields the pipeline already produces (lifecycle status,
sanction-to-completion duration, expenditure ratio, vendor concentration),
compared against the dataset's own percentile distribution. It does
**not** use or duplicate the pipeline's ML anomaly model (`Isolation
Forest` in `anomaly_model.py`, untouched). Outputs: Delay Risk, Completion
Risk, Expenditure Risk, and a combined Future Review Priority
(LOW/MEDIUM/HIGH), each with a stated reason.

### 2.6 Trend Analysis
Time-series aggregation by month over `sanction_date`, `expenditure_date`,
and `completion_date`, plus risk-level distribution over time, filterable
by chamber/state/MP. Only months actually present in the data are
returned — no interpolated or fabricated periods. Presented as bar-list
tables in the UI (no line charts, matching the existing UI constraint).

### 2.7 Work Page Enrichment
The existing work detail page (`/work/{id}`) — deterministic/statistical/ML
evidence blocks were **not changed** — now also shows: Recommended
Action, Compliance Status, Cost Overrun, Risk Estimate, and any
Duplicate-Work matches, positioned above the original evidence panel.

---

## 3. Requirements That Cannot Be Fully Verified From Available Data

- **Implementing agency, GPS/location fields:** not present in the source
  MPLADS export. Duplicate detection therefore relies only on MP,
  constituency, description text, amount, and date — it cannot use a
  physical location or contracting-agency match, which would meaningfully
  reduce false positives/negatives.
- **Cost overruns:** determinable for 12,000 of 64,193 works (the rest
  lack a comparable sanctioned + completion/expenditure pair). Of those
  12,000, the pipeline's own overrun fields show **zero** works exceeding
  their sanctioned amount — this is a genuine finding from the data, not
  a placeholder or a bug (verified directly against
  `outputs/anomaly_results.csv`).
- **Approval-duration and lifecycle thresholds** used by the compliance
  engine are computed live from this dataset's own percentile
  distribution (e.g. the 90th percentile of `recommendation_to_sanction_days`),
  not from an external, invented government rule — because no such
  documented rule exists in the source data.
- **81% of works (52,193 / 64,193) have no sanction record at all** in
  this snapshot (`has_sanctioned = False`) — they exist only as
  recommendations. All PS26102 requirements that depend on a sanction
  (cost overrun, most compliance checks, delay estimation) are correctly
  reported as not-yet-applicable for those works, not flagged as
  problems.

---

## 4. New API Endpoints

All endpoints are read-only, additive, and prefixed to avoid any
collision with the existing API surface (`/api/health`, `/api/summary`,
`/api/works`, `/api/work/{id}`, `/api/critical`, `/api/state/{name}`,
`/api/mp/{id}`, `/api/quick/spending-outliers`, `/api/filters`,
`/api/meta`, `/api/states` — all unchanged).

| Endpoint | Purpose |
|---|---|
| `GET /api/duplicates` | Paginated duplicate-work pairs (`tier=A\|B\|All`) |
| `GET /api/duplicates/summary` | Counts by tier + batch patterns |
| `GET /api/duplicates/batches` | Tier C batch/repeated-work groups |
| `GET /api/cost-overruns` | Paginated flagged overruns (filters: chamber, state, band, q) |
| `GET /api/cost-overruns/summary` | Determinable/flagged counts, band thresholds |
| `GET /api/compliance` | Paginated compliance results (filter: status, chamber, state) |
| `GET /api/compliance/summary` | Status counts |
| `GET /api/compliance/{work_id}` | Single-work compliance detail |
| `GET /api/early-warnings` | Paginated early warnings (filter: severity, state) |
| `GET /api/early-warnings/summary` | Severity counts |
| `GET /api/predictions` | Paginated risk estimates (filter: priority, chamber, state) |
| `GET /api/predictions/summary` | Aggregate counts per risk dimension |
| `GET /api/predictions/{work_id}` | Single-work risk estimate |
| `GET /api/trends?metric=sanctions\|expenditure\|completions\|risk` | Time-series by month, filterable by chamber/state/mp_id |
| `GET /api/work/{id}` (enriched) | Existing endpoint; now also returns `cost_overrun`, `compliance`, `prediction`, `early_warning`, `duplicate_matches` |

---

## 5. Test Results (this session)

**Backend — clean-room startup test:** stopped all processes, started
`uvicorn backend.api:app` from a cold state. Completed successfully in
~40–45 seconds (one-time cost: pre-computing duplicate detection,
compliance, and prediction caches at startup — see §6 for why). Verified
`/api/health` reports `64193` works and `master_loaded: true`.

**Backend — determinism check:** `/api/compliance/summary` and
`/api/duplicates/summary` produce byte-for-byte identical output across
two independent full server restarts:
```
COMPLIANT: 8741, PARTIALLY COMPLIANT: 2864, REQUIRES REVIEW: 395, INSUFFICIENT DATA: 52193
Potential Duplicate (Tier A): 79, Possible Duplicate (Tier B): 300, Batch patterns: 150
```

**Frontend — production build:** `npx vite build` from a clean `dist/`
succeeds: `dist/index.html` + `dist/assets/index-*.js` (209 KB, gzip 64 KB),
0 errors, 0 warnings.

**Frontend — full navigation regression (Playwright, headless Chromium):**
14/14 checks passed — real in-app SPA navigation (hash-based, not full
page reloads) through every required page in sequence, then back to Home,
with console-error, page-error, and failed-request listeners attached
throughout:

| Page | Result |
|---|---|
| Home | OK |
| Critical Cases | OK |
| Risk Explorer | OK |
| Outliers | OK |
| MP Profile | OK |
| State Page | OK |
| Work Details | OK |
| Potential Duplicates | OK |
| Cost Overruns | OK |
| Compliance | OK |
| Early Warnings | OK |
| Trends | OK |
| Predictions | OK |
| Home (return trip) | OK |

Zero console errors, zero page errors, zero failed requests, no blank
pages across the full run.

**Bugs found and fixed during this session (not new features):**

1. **Compliance mislabeling** — "not yet sanctioned" was initially scored
   as a failed check, producing 81% REQUIRES REVIEW. Fixed to
   `INSUFFICIENT DATA` per the PS's own instruction not to treat missing
   data as non-compliance.
2. **Predictive priority banding collapse** — quantile-based HIGH/MEDIUM/LOW
   cutoffs collapsed to a binary split on this dataset's discrete value
   distribution (no MEDIUM tier appeared). Fixed to derive priority
   directly from component risk levels.
3. **Non-deterministic duplicate tie-breaking** — Python hash-seed
   randomization could change which fuzzy pairs fell inside the top-300
   cutoff across restarts, which also shifted compliance counts. Fixed
   with an explicit secondary sort key on `work_id`.
4. **Pre-existing frontend crash** (not introduced by this delivery):
   `StatePage`, `WorkPage`, and `Outliers` used
   `useEffect(()=>api(...).then(setD), [deps])` without braces, which
   returns the Promise itself as the effect's cleanup function. React then
   throws `"destroy is not a function"` and crashes the whole app when
   navigating away from any of those three pages. Fixed by wrapping each
   effect body in braces so nothing is returned.
5. **Cold-cache request hang** — `/api/work/{id}` looks up duplicate,
   compliance, and prediction results; on a cold cache the first request
   triggered all three computations synchronously (~30–45s total),
   exceeding typical client timeouts. Fixed by pre-warming those caches
   once at application startup instead of on the first request. This
   changes only *when* the computation runs, not what it computes —
   verified identical output before and after.

No other analytical logic was changed.

---

## 6. Known Limitations

- **Startup cost:** the backend now takes ~40–45 seconds to become ready
  (duplicate detection, compliance, and prediction caches are computed
  once at startup rather than lazily). This trades a longer startup for
  guaranteeing no individual request hangs.
- **Duplicate detection is a heuristic screening tool**, not a guarantee.
  It cannot see fields not present in the dataset (GPS coordinates,
  implementing agency, per-unit serial numbers). Genuinely distinct works
  with boilerplate-identical text and coincidentally close amounts/dates
  may still appear as candidates; true duplicates using very different
  wording, far-apart amounts, or missing description text may be missed.
- **Cost overrun determinability is capped by the data:** only ~19% of
  works (12,000/64,193) have both a sanctioned amount and a comparable
  actual/completion figure. The other 81% correctly report "cannot be
  determined" rather than being silently excluded or guessed.
- **Compliance and delay thresholds are dataset-relative**, not sourced
  from an external documented government rule (none was available in the
  source data). This is disclosed in every relevant API response
  (`band_thresholds_pct.note`, compliance check text).
- **Predictive insights are heuristic risk estimates**, not a trained
  forecasting model. They are explicitly labelled as such everywhere they
  appear (API `label` field and UI eyebrow text) to avoid overstating
  confidence.
- The existing risk pipeline, its weights (Rule 50% / ML 30% / Statistical
  20%), and its 64,193/54,946/8,796/423/28 NORMAL/REVIEW/HIGH/CRITICAL
  breakdown are unchanged and were not re-validated in this session beyond
  confirming the API still serves them correctly.

---

## 7. What Was Deliberately Not Touched

- `src/anomaly_model.py`, `src/rules.py`, `src/scoring.py`,
  `src/features.py`, `src/integration.py`, `src/cleaning.py`,
  `src/normalization.py`, `src/ingestion.py`, `run_pipeline.py`
- `outputs/anomaly_results.csv`, `outputs/work_features.csv`,
  `data/raw/`, `data/processed/`
- The original dashboard's visual design, color scheme, and existing
  pages' layout (new pages match the existing style; nothing was
  redesigned)
- `dashboard/app.py` (legacy Streamlit dashboard, retained but unused by
  the web frontend, as in the original project)
