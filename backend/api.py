from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend import analytics
from backend import explain

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
PROCESSED = ROOT / "data" / "processed"
FRONTEND = ROOT / "frontend"

app = FastAPI(
    title="MPLADS AI Audit Intelligence API",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


def _read(name: str, path: Path) -> pd.DataFrame:
    file_path = path / name
    if not file_path.exists():
        raise FileNotFoundError(f"Required data file not found: {file_path}")
    return pd.read_csv(file_path, low_memory=False)


def _read_optional(candidates: list[Path]) -> pd.DataFrame:
    for path in candidates:
        if path.exists():
            return pd.read_csv(path, low_memory=False)
    return pd.DataFrame()


# ---------------------------------------------------------------------------
# SOURCE DATA
# ---------------------------------------------------------------------------

ANOM = _read("anomaly_results.csv", OUTPUTS)
EXP = _read("expenditures.csv", PROCESSED)
ALLOC = _read("mp_allocation.csv", PROCESSED)

# The integrated MPLADS work table is the source for descriptive/lifecycle
# fields. Different pipeline versions may place it in outputs or processed.
WORKS = _read_optional(
    [
        OUTPUTS / "works_master.csv",
        PROCESSED / "works_master.csv",
        OUTPUTS / "integrated_works.csv",
        PROCESSED / "integrated_works.csv",
    ]
)


def _ensure_work_id(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df
    out = df.copy()
    if "work_id" in out.columns:
        out["work_id"] = out["work_id"].astype("string").str.strip()
    return out


ANOM = _ensure_work_id(ANOM)
EXP = _ensure_work_id(EXP)
ALLOC = _ensure_work_id(ALLOC)
WORKS = _ensure_work_id(WORKS)

# Parse dates in both datasets before joining.
DATE_COLUMNS = [
    "recommended_date",
    "sanction_date",
    "completion_date",
    "first_payment_date",
    "last_payment_date",
]

for df in [ANOM, WORKS, EXP]:
    for col in DATE_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")


# ---------------------------------------------------------------------------
# JOIN: preserve anomaly/risk fields AND recover original MPLADS fields
# ---------------------------------------------------------------------------

def build_work_data() -> pd.DataFrame:
    """
    Build the API's canonical work-level dataset.

    ANOM is authoritative for risk fields.
    WORKS is authoritative for original MPLADS descriptive/lifecycle fields.
    The join is strictly on work_id.

    Existing non-null ANOM values are preserved. Missing ANOM fields are
    filled from WORKS without overwriting risk calculations.
    """
    out = ANOM.copy()

    if WORKS.empty or "work_id" not in WORKS.columns:
        return out

    master = WORKS.copy()

    # Prevent duplicate columns from creating _x/_y confusion.
    master = master.drop_duplicates(subset=["work_id"], keep="first")

    # Fields that belong to the original MPLADS work record.
    preferred_master_fields = [
        "work_description",
        "work_status_raw",
        "lifecycle_status",
        "recommended_date",
        "sanction_date",
        "first_payment_date",
        "last_payment_date",
        "completion_date",
        "recommended_amount",
        "sanctioned_amount",
        "completion_amount",
        "work_category",
        "state",
        "constituency",
        "mp_name",
        "parliament_house",
        "elected_nominated",
        "district",
        "nodal_district",
        "party",
        "photo_url",
    ]

    available = [c for c in preferred_master_fields if c in master.columns]
    master = master[["work_id"] + available]

    out = out.merge(
        master,
        on="work_id",
        how="left",
        suffixes=("", "__master"),
    )

    # Fill only missing values in ANOM from the master dataset.
    for col in available:
        master_col = f"{col}__master"
        if master_col not in out.columns:
            continue

        if col not in out.columns:
            out[col] = out[master_col]
        else:
            missing = out[col].isna() | (out[col].astype("string").str.strip() == "")
            out.loc[missing, col] = out.loc[missing, master_col]

        out.drop(columns=[master_col], inplace=True)

    return out


WORK_DATA = build_work_data()

# Ensure columns expected by existing API code exist.
DEFAULT_COLUMNS = {
    "total_expenditure": np.nan,
    "sanctioned_amount": np.nan,
    "completion_amount": np.nan,
    "risk_score": np.nan,
    "risk_level": "NORMAL",
    "primary_reason": "Data Not Available",
    "work_category": "Data Not Available",
    "lifecycle_status": "Data Not Available",
}

for col, default in DEFAULT_COLUMNS.items():
    if col not in WORK_DATA.columns:
        WORK_DATA[col] = default


# Stable MP ID must be based on chamber + MP name.
WORK_DATA["_mp_id"] = (
    WORK_DATA["parliament_house"].fillna("").astype(str)
    + "|"
    + WORK_DATA["mp_name"].fillna("").astype(str)
).map(
    lambda s: "MP-" + hashlib.sha1(s.encode("utf-8")).hexdigest()[:10].upper()
)


STATE_ALIASES = {
    "Jammu And Kashmir": "Jammu & Kashmir",
    "Andaman And Nicobar Islands": "Andaman & Nicobar Islands",
}


# ---------------------------------------------------------------------------
# SERIALIZATION HELPERS
# ---------------------------------------------------------------------------

def clean(v):
    if v is None:
        return None

    if isinstance(v, (float, np.floating)) and pd.isna(v):
        return None

    if isinstance(v, (np.integer,)):
        return int(v)

    if isinstance(v, (np.floating,)):
        return None if np.isnan(v) else float(v)

    if isinstance(v, pd.Timestamp):
        return None if pd.isna(v) else v.strftime("%Y-%m-%d")

    if isinstance(v, np.ndarray):
        return v.tolist()

    return v


def record(row: pd.Series) -> dict:
    d = {
        k: clean(v)
        for k, v in row.to_dict().items()
        if not k.startswith("_")
    }
    d["mp_id"] = row.get("_mp_id")
    d["state_display"] = STATE_ALIASES.get(
        row.get("state"),
        row.get("state"),
    )
    return d


def risk_summary(df: pd.DataFrame) -> dict:
    if df.empty:
        return {k: 0 for k in ["NORMAL", "REVIEW", "HIGH", "CRITICAL"]}

    c = df["risk_level"].fillna("NORMAL").value_counts().to_dict()
    return {
        k: int(c.get(k, 0))
        for k in ["NORMAL", "REVIEW", "HIGH", "CRITICAL"]
    }


def money_summary(df: pd.DataFrame) -> dict:
    def total(col):
        if col not in df.columns:
            return 0.0
        return float(
            pd.to_numeric(df[col], errors="coerce").fillna(0).sum()
        )

    return {
        "sanctioned": total("sanctioned_amount"),
        "expenditure": total("total_expenditure"),
        "completion": total("completion_amount"),
    }


def duration_days(row: pd.Series):
    """
    Recommendation -> completion when both exist.
    Otherwise sanction -> completion.
    If either pair is incomplete, return None.
    """
    rec = pd.to_datetime(row.get("recommended_date"), errors="coerce")
    sanc = pd.to_datetime(row.get("sanction_date"), errors="coerce")
    comp = pd.to_datetime(row.get("completion_date"), errors="coerce")

    if pd.notna(rec) and pd.notna(comp):
        return int((comp - rec).days)

    if pd.notna(sanc) and pd.notna(comp):
        return int((comp - sanc).days)

    return None


def api_work_record(row: pd.Series) -> dict:
    d = record(row)
    d["duration_days"] = duration_days(row)

    # Explicitly expose the fields used by the public UI.
    for field in [
        "work_description",
        "work_status_raw",
        "lifecycle_status",
        "recommended_date",
        "sanction_date",
        "first_payment_date",
        "completion_date",
        "recommended_amount",
        "sanctioned_amount",
        "completion_amount",
        "total_expenditure",
        "work_category",
        "risk_level",
        "risk_score",
        "primary_reason",
        "rule_score",
        "stat_risk_score",
        "ml_anomaly_score",
        "ml_anomaly_percentile",
    ]:
        d[field] = clean(row.get(field))

    return d


# ---------------------------------------------------------------------------
# FILTERING
# ---------------------------------------------------------------------------

def apply_filters(
    df: pd.DataFrame,
    chamber=None,
    state=None,
    district=None,
    constituency=None,
    risk=None,
    q=None,
    min_score=None,
    max_score=None,
):
    out = df

    if chamber and chamber != "All":
        out = out[out.parliament_house == chamber]

    if state and state != "All":
        out = out[out.state == state]

    if district and district != "All":
        if "district" not in out.columns:
            return out.iloc[0:0]
        out = out[out.district.fillna("").astype(str) == district]

    if constituency and constituency != "All":
        out = out[
            out.constituency.fillna("").astype(str) == constituency
        ]

    if risk and risk != "All":
        out = out[out.risk_level == risk]

    if q:
        ql = q.lower().strip()

        work_id = out["work_id"].fillna("").astype(str).str.lower()
        mp_name = out["mp_name"].fillna("").astype(str).str.lower()

        description = (
            out["work_description"].fillna("").astype(str).str.lower()
            if "work_description" in out.columns
            else pd.Series("", index=out.index)
        )

        constituency_values = (
            out["constituency"].fillna("").astype(str).str.lower()
            if "constituency" in out.columns
            else pd.Series("", index=out.index)
        )
        vendor_values = (
            out["vendor_name"].fillna("").astype(str).str.lower()
            if "vendor_name" in out.columns
            else pd.Series("", index=out.index)
        )

        out = out[
            work_id.str.contains(ql, regex=False)
            | mp_name.str.contains(ql, regex=False)
            | description.str.contains(ql, regex=False)
            | constituency_values.str.contains(ql, regex=False)
            | vendor_values.str.contains(ql, regex=False)
        ]

    if min_score is not None:
        out = out[
            pd.to_numeric(out.risk_score, errors="coerce") >= min_score
        ]

    if max_score is not None:
        out = out[
            pd.to_numeric(out.risk_score, errors="coerce") <= max_score
        ]

    return out


analytics.configure(
    work_data=WORK_DATA,
    exp=EXP,
    clean_fn=clean,
    api_work_record_fn=api_work_record,
    apply_filters_fn=apply_filters,
)
analytics.warm_caches()
app.include_router(analytics.router)


# ---------------------------------------------------------------------------
# API
# ---------------------------------------------------------------------------

@app.get("/api/health")
def health():
    return {
        "status": "ok",
        "works": int(len(WORK_DATA)),
        "anomaly_rows": int(len(ANOM)),
        "master_loaded": not WORKS.empty,
        "master_rows": int(len(WORKS)),
        "source": "anomaly_results.csv + works_master.csv when available",
    }


@app.get("/api/summary")
def summary(chamber: str = "All"):
    df = WORK_DATA if chamber == "All" else WORK_DATA[
        WORK_DATA.parliament_house == chamber
    ]

    return {
        "total_works": int(len(df)),
        "risk": risk_summary(df),
        "money": money_summary(df),
        "mp_count": int(df["_mp_id"].nunique()),
        "state_count": int(df["state"].nunique()),
        "duplicate_payment_count": int(
            pd.to_numeric(
                df.get("duplicate_payment_count", 0),
                errors="coerce",
            ).fillna(0).sum()
        ),
        "risk_weights": {
            "rule": 0.50,
            "ml": 0.30,
            "statistical": 0.20,
        },
        "risk_terminology": [
            "NORMAL",
            "REVIEW",
            "HIGH",
            "CRITICAL",
        ],
    }


@app.get("/api/states")
def states(chamber: str = "All"):
    df = WORK_DATA if chamber == "All" else WORK_DATA[
        WORK_DATA.parliament_house == chamber
    ]

    g = (
        df.groupby("state", dropna=False)
        .agg(
            total_works=("work_id", "count"),
            high_risk=("risk_level", lambda s: int((s == "HIGH").sum())),
            critical=("risk_level", lambda s: int((s == "CRITICAL").sum())),
            review=("risk_level", lambda s: int((s == "REVIEW").sum())),
            normal=("risk_level", lambda s: int((s == "NORMAL").sum())),
            expenditure=("total_expenditure", "sum"),
            risk_score=("risk_score", "mean"),
        )
        .reset_index()
    )

    return [
        {
            **{k: clean(v) for k, v in r.items()},
            "state_display": STATE_ALIASES.get(
                r["state"],
                r["state"],
            ),
        }
        for r in g.to_dict("records")
    ]


@app.get("/api/state/{name}")
def state_detail(name: str, chamber: str = "All"):
    raw = next(
        (
            k
            for k, v in STATE_ALIASES.items()
            if v.lower() == name.lower()
        ),
        name,
    )

    df = WORK_DATA if chamber == "All" else WORK_DATA[
        WORK_DATA.parliament_house == chamber
    ]

    df = df[
        df.state.fillna("").astype(str).str.lower() == raw.lower()
    ]

    if df.empty:
        return {
            "state": name,
            "found": False,
        }

    mps = (
        df.groupby(
            ["_mp_id", "mp_name", "parliament_house", "constituency"],
            dropna=False,
        )
        .agg(
            works=("work_id", "count"),
            high=("risk_level", lambda s: int((s == "HIGH").sum())),
            critical=(
                "risk_level",
                lambda s: int((s == "CRITICAL").sum()),
            ),
            expenditure=("total_expenditure", "sum"),
        )
        .reset_index()
        .sort_values(
            ["critical", "high", "works"],
            ascending=False,
        )
    )

    return {
        "found": True,
        "state": name,
        "raw_state": raw,
        "summary": {
            "total_works": int(len(df)),
            **risk_summary(df),
            **money_summary(df),
        },
        "mps": [
            {
                "mp_id": r["_mp_id"],
                "mp_name": r["mp_name"],
                "chamber": r["parliament_house"],
                "constituency": clean(r["constituency"]),
                "works": int(r["works"]),
                "high": int(r["high"]),
                "critical": int(r["critical"]),
                "expenditure": clean(r["expenditure"]),
            }
            for r in mps.to_dict("records")
        ],
        "critical_works": [
            api_work_record(r)
            for _, r in df[df.risk_level == "CRITICAL"]
            .sort_values("risk_score", ascending=False)
            .head(20)
            .iterrows()
        ],
        "high_works": [
            api_work_record(r)
            for _, r in df[df.risk_level == "HIGH"]
            .sort_values("risk_score", ascending=False)
            .head(20)
            .iterrows()
        ],
    }


@app.get("/api/mp/{mp_id}")
def mp_detail(mp_id: str):
    df = WORK_DATA[WORK_DATA._mp_id == mp_id].copy()

    if df.empty:
        return {"found": False}

    first = df.iloc[0]

    return {
        "found": True,
        "profile": {
            "mp_id": mp_id,
            "mp_name": clean(first.get("mp_name")),
            "party": clean(first.get("party")),
            "photo_url": clean(first.get("photo_url")),
            "chamber": clean(first.get("parliament_house")),
            "state": STATE_ALIASES.get(
                first.get("state"),
                first.get("state"),
            ),
            "constituency": (
                clean(first.get("constituency"))
                if first.get("parliament_house") == "Lok Sabha"
                else None
            ),
            "nodal_district": clean(
                first.get("nodal_district")
            ),
            "elected_nominated": clean(
                first.get("elected_nominated")
            ),
        },
        "summary": {
            "total_works": int(len(df)),
            **risk_summary(df),
            **money_summary(df),
        },
        "lifecycle": (
            df["lifecycle_status"]
            .fillna("Data Not Available")
            .value_counts()
            .head(10)
            .to_dict()
        ),
        # IMPORTANT: return ALL works, not only HIGH/CRITICAL.
        "works": [
            api_work_record(r)
            for _, r in df.sort_values(
                ["risk_score", "work_id"],
                ascending=[False, True],
                na_position="last",
            ).iterrows()
        ],
    }


@app.get("/api/work/{work_id:path}")
def work_detail(work_id: str):
    df = WORK_DATA[
        WORK_DATA.work_id.astype(str) == str(work_id)
    ]

    if df.empty:
        return {"found": False}

    row = df.iloc[0]

    payments = EXP[
        EXP.work_id.astype(str) == str(work_id)
    ].copy()

    deterministic = []
    raw_reasons = row.get("risk_reasons_json")

    if isinstance(raw_reasons, str):
        try:
            deterministic = json.loads(raw_reasons)
        except Exception:
            deterministic = []

    duplicate_matches = [
        p for p in analytics.get_duplicates()["pairs"]
        if p["work_a"]["work_id"] == str(work_id) or p["work_b"]["work_id"] == str(work_id)
    ]

    work_record = api_work_record(row)
    cost_overrun = analytics.cost_overrun_lookup(work_id)
    compliance = analytics.compliance_lookup(work_id)
    early_warning = analytics.early_warning_lookup(work_id)
    if early_warning:
        early_warning = explain.enrich_early_warning(early_warning)

    explanation = explain.build_work_explanation(
        work=work_record,
        deterministic_reasons=deterministic,
        cost_overrun=cost_overrun,
        compliance=compliance,
        duplicate_matches=duplicate_matches,
        ml_anomaly_percentile=row.get("ml_anomaly_percentile"),
    )

    return {
        "found": True,
        "work": work_record,
        "explanation": explanation,
        "payments": [
            {k: clean(v) for k, v in r.items()}
            for r in payments.to_dict("records")
        ],
        "cost_overrun": cost_overrun,
        "compliance": compliance,
        "prediction": analytics.prediction_lookup(work_id),
        "early_warning": early_warning,
        "duplicate_matches": duplicate_matches,
        "evidence": {
            "deterministic": deterministic,
            "statistical": {
                "stat_risk_score": clean(row.get("stat_risk_score")),
                "sanc_robust_zscore": clean(
                    row.get("sanc_robust_zscore")
                ),
                "exp_robust_zscore": clean(
                    row.get("exp_robust_zscore")
                ),
                "available": bool(
                    row.get("statistical_anomaly_available", False)
                ),
            },
            "ml": {
                "ml_anomaly_score": clean(
                    row.get("ml_anomaly_score")
                ),
                "ml_anomaly_percentile": clean(
                    row.get("ml_anomaly_percentile")
                ),
            },
        },
    }


@app.get("/api/critical")
def critical(
    page: int = 1,
    page_size: int = 25,
    q: Optional[str] = None,
    state: str = "All",
    sort: str = "risk_score",
):
    df = apply_filters(
        WORK_DATA[WORK_DATA.risk_level == "CRITICAL"],
        state=state,
        q=q,
    )

    sort_col = (
        sort
        if sort
        in [
            "risk_score",
            "rule_score",
            "stat_risk_score",
            "ml_anomaly_percentile",
        ]
        else "risk_score"
    )

    df = df.sort_values(sort_col, ascending=False)

    total = len(df)
    start = (page - 1) * page_size

    return {
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "rows": [
            api_work_record(r)
            for _, r in df.iloc[
                start : start + page_size
            ].iterrows()
        ],
    }


@app.get("/api/works")
def works(
    page: int = 1,
    page_size: int = 50,
    chamber: str = "All",
    state: str = "All",
    district: str = "All",
    constituency: str = "All",
    risk: str = "All",
    q: str = "",
    min_score: Optional[float] = None,
    max_score: Optional[float] = None,
):
    page_size = min(max(page_size, 1), 200)

    df = apply_filters(
        WORK_DATA,
        chamber,
        state,
        district,
        constituency,
        risk,
        q,
        min_score,
        max_score,
    )

    total = len(df)
    start = (page - 1) * page_size

    df = df.sort_values(
        "risk_score",
        ascending=False,
        na_position="last",
    )

    return {
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "rows": [
            api_work_record(r)
            for _, r in df.iloc[
                start : start + page_size
            ].iterrows()
        ],
    }


@app.get("/api/filters")
def filters(chamber: str = "All"):
    df = WORK_DATA if chamber == "All" else WORK_DATA[
        WORK_DATA.parliament_house == chamber
    ]

    score = pd.to_numeric(df.risk_score, errors="coerce")
    states = sorted(df.state.dropna().astype(str).unique().tolist())
    constituencies = sorted(df.constituency.dropna().astype(str).unique().tolist())

    # Dependent filters: only constituencies that actually occur inside the
    # selected state are returned. This prevents invalid state/constituency
    # combinations in the UI.
    by_state = {}
    state_constituency_map = {}
    if "state" in df.columns and "constituency" in df.columns:
        for st, g in df.groupby("state", dropna=False):
            if pd.isna(st):
                continue
            vals = sorted(g.constituency.dropna().astype(str).unique().tolist())
            by_state[str(st)] = vals
            for c in vals:
                state_constituency_map.setdefault(c, str(st))

    return {
        "states": states,
        "constituencies": constituencies,
        "constituencies_by_state": by_state,
        "constituency_state_map": state_constituency_map,
        "risk_levels": ["NORMAL", "REVIEW", "HIGH", "CRITICAL"],
        "score_min": float(score.min()) if score.notna().any() else 0.0,
        "score_max": float(score.max()) if score.notna().any() else 0.0,
    }


@app.get("/api/mps")
def mps(
    chamber: str = "All",
    state: str = "All",
    constituency: str = "All",
    q: str = "",
    sort: str = "mp_name",
    dir: str = "asc",
    page_size: int = 200,
):
    """Aggregated MP directory over the existing canonical WORK_DATA."""
    df = apply_filters(
        WORK_DATA,
        chamber=chamber,
        state=state,
        constituency=constituency,
        q=q,
    )
    if df.empty:
        return {"total": 0, "rows": []}

    g = df.groupby(
        ["_mp_id", "mp_name", "parliament_house", "state", "constituency"],
        dropna=False,
    ).agg(
        total_works=("work_id", "count"),
        normal_count=("risk_level", lambda s: int((s == "NORMAL").sum())),
        review_count=("risk_level", lambda s: int((s == "REVIEW").sum())),
        high_risk_count=("risk_level", lambda s: int((s == "HIGH").sum())),
        critical_count=("risk_level", lambda s: int((s == "CRITICAL").sum())),
        total_expenditure=("total_expenditure", "sum"),
    ).reset_index()
    g["risk_count"] = g["review_count"] + g["high_risk_count"] + g["critical_count"]

    sort_map = {
        "mp_name": "mp_name",
        "state": "state",
        "constituency": "constituency",
        "total_works": "total_works",
        "risk_count": "risk_count",
        "critical_count": "critical_count",
        "high_risk_count": "high_risk_count",
        "total_expenditure": "total_expenditure",
    }
    key = sort_map.get(sort, "mp_name")
    ascending = dir.lower() != "desc"
    g = g.sort_values(key, ascending=ascending, na_position="last")
    page_size = min(max(page_size, 1), 500)
    rows = []
    for _, r in g.head(page_size).iterrows():
        rows.append({
            "mp_id": r["_mp_id"],
            "mp_name": clean(r["mp_name"]),
            "parliament_house": clean(r["parliament_house"]),
            "state": clean(r["state"]),
            "state_display": STATE_ALIASES.get(r["state"], r["state"]),
            "constituency": clean(r["constituency"]),
            "total_works": int(r["total_works"]),
            "normal_count": int(r["normal_count"]),
            "review_count": int(r["review_count"]),
            "high_risk_count": int(r["high_risk_count"]),
            "critical_count": int(r["critical_count"]),
            "risk_count": int(r["risk_count"]),
            "total_expenditure": clean(r["total_expenditure"]),
        })
    return {"total": int(len(g)), "rows": rows}


@app.get("/api/quick/spending-outliers")
def spending_outliers(limit: int = 25):
    df = WORK_DATA.copy()

    z = pd.to_numeric(
        df.get("exp_robust_zscore"),
        errors="coerce",
    )

    df = df[z.notna()].copy()
    df["_abs_exp_z"] = z[z.notna()].abs()

    df = df.sort_values(
        ["_abs_exp_z", "risk_score"],
        ascending=False,
    ).head(limit)

    return {
        "method": (
            "Ranked by absolute expenditure robust "
            "Z-score from backend output"
        ),
        "rows": [
            api_work_record(r)
            | {
                "abs_exp_robust_zscore": clean(
                    r["_abs_exp_z"]
                )
            }
            for _, r in df.iterrows()
        ],
    }


@app.get("/api/meta")
def meta():
    return {
        "source_files": [
            "outputs/anomaly_results.csv",
            "data/processed/expenditures.csv",
            "data/processed/mp_allocation.csv",
            "works_master.csv when available",
        ],
        "works": int(len(WORK_DATA)),
        "anomaly_rows": int(len(ANOM)),
        "master_loaded": not WORKS.empty,
        "master_rows": int(len(WORKS)),
        "ml_weight": 0.30,
        "rule_weight": 0.50,
        "stat_weight": 0.20,
        "audit_disclaimer": (
            "This classification indicates potential "
            "audit-risk signals. It does not establish fraud."
        ),
        "rajya_sabha_nodal_district": False,
    }


# Static frontend last so /api/* remains available.
if FRONTEND.exists():
    app.mount(
        "/",
        StaticFiles(directory=str(FRONTEND), html=True),
        name="frontend",
    )
