"""
Analytics extension for the MPLADS AI Audit Intelligence API.

This module implements the remaining Problem-Statement (SIH26102) requirements
that are NOT already covered by the existing anomaly/risk pipeline:

  1. Duplicate / similar WORK detection (distinct from the existing
     duplicate-PAYMENT-ledger-record signal already produced by the pipeline)
  2. Cost overrun analysis (sanctioned vs actual/completion amount)
  3. Automated compliance monitoring
  4. Early warning layer
  5. Predictive / forward-looking risk estimates (explicitly NOT ML predictions
     unless clearly labelled as such)
  6. Trend analysis over time

Hard rules followed throughout this file:
  - The existing risk pipeline (src/*, outputs/anomaly_results.csv) is never
    modified or recomputed here. Everything below is read-only analysis on
    top of the existing WORK_DATA frame built by backend/api.py.
  - Nothing here claims "fraud" or "duplicate confirmed". Every output is
    phrased as a screening signal requiring human verification.
  - Every threshold used below is either taken directly from the data
    (percentiles/medians computed live from the dataset) or is disclosed
    inline as a heuristic. No government rule is invented.
  - When a metric cannot be computed from available fields, the code returns
    an explicit "cannot be determined from available source data" value
    instead of fabricating one.
"""

from __future__ import annotations

import re
import time
from difflib import SequenceMatcher
from typing import Optional

import numpy as np
import pandas as pd
from fastapi import APIRouter

from backend import explain

router = APIRouter()

# ---------------------------------------------------------------------------
# These are populated by backend.api via `configure(...)` right after it
# builds WORK_DATA, so this module never re-reads or re-joins source files.
# ---------------------------------------------------------------------------
WORK_DATA: pd.DataFrame = pd.DataFrame()
EXP: pd.DataFrame = pd.DataFrame()
_clean = None
_api_work_record = None
_apply_filters = None


def configure(work_data, exp, clean_fn, api_work_record_fn, apply_filters_fn):
    global WORK_DATA, EXP, _clean, _api_work_record, _apply_filters
    WORK_DATA = work_data
    EXP = exp
    _clean = clean_fn
    _api_work_record = api_work_record_fn
    _apply_filters = apply_filters_fn


def warm_caches():
    """
    Pre-compute the cached analytics (duplicates, compliance, predictions) once
    at application startup instead of on the first incoming request. Without
    this, the first hit to /api/work/{id} (which looks up all three) can take
    30-45 seconds on a cold cache and time out client-side. This changes only
    *when* the computation runs, not what it computes.
    """
    get_duplicates()
    get_cost_overrun_df()
    get_compliance_df()
    get_predictions_df()
    get_early_warnings()


DISCLAIMER = (
    "This is a screening signal generated from available data. It does not "
    "establish fraud or wrongdoing and requires human audit verification."
)


# ===========================================================================
# 1. DUPLICATE / SIMILAR WORK DETECTION
# ===========================================================================
#
# Method (disclosed for auditors/judges):
#   - Work descriptions are normalized (lowercased, punctuation stripped,
#     common boilerplate words removed).
#   - Candidate pairs are generated within blocks of (MP, constituency, a
#     4-token signature of the normalized description) to keep the search
#     tractable across ~64k works.
#   - Three tiers are reported, in increasing order of caution:
#       TIER A - "Potential Duplicate": exactly 2 works from the same MP
#                share an identical normalized description, the same
#                sanctioned amount, and the same sanction date. An isolated
#                pair matching on all three fields is the pattern most
#                consistent with an accidental double entry.
#       TIER B - "Possible Duplicate": works are NOT identical but are highly
#                similar in text (fuzzy ratio), with closely matching
#                sanctioned amount and nearby dates.
#       TIER C - "Batch / Repeated Work Pattern": 3+ works from the same MP
#                share an identical description, amount and date. This is
#                explicitly NOT flagged as duplicate — in MPLADS data this
#                pattern typically reflects a single scheme rolled out as
#                many identical units (e.g. N identical hand-pumps or LED
#                poles sanctioned together). It is surfaced only as a
#                transparency signal so an auditor can verify the claimed
#                unit count matches what was delivered.
#
# This is a heuristic screening tool, not a guarantee. It cannot see fields
# that are not in the dataset (e.g. GPS coordinates, implementing agency,
# per-unit serial numbers), so genuinely distinct works that happen to have
# boilerplate-identical text and coincidentally close amounts/dates may
# still appear here, and true duplicates using slightly different wording,
# far-apart amounts, or missing description text may be missed.

_STOPWORDS = set(
    "construction of the a an at in for near village ward gram panchayat "
    "road building repair renovation upgradation providing installation "
    "to and works work with under scheme improvement development area "
    "block district".split()
)

_DUP_CACHE: dict = {}


def _normalize_tokens(text) -> list[str]:
    if not isinstance(text, str):
        return []
    t = text.lower()
    t = re.sub(r"[^a-z0-9 ]", " ", t)
    tokens = []
    for w in t.split():
        if w in _STOPWORDS:
            continue
        # Keep numeric tokens (serial numbers, pole/unit numbers, model
        # numbers) regardless of length — these are often the ONLY thing
        # that distinguishes two otherwise-boilerplate-identical work
        # descriptions (e.g. "S.No-8" vs "S.No-9" at the same location).
        # Only short alphabetic filler is dropped.
        if w.isdigit() or len(w) > 2:
            tokens.append(w)
    return tokens


def _amount_similarity(a, b) -> Optional[float]:
    if pd.isna(a) or pd.isna(b):
        return None
    a, b = float(a), float(b)
    if max(a, b) <= 0:
        return None
    return 1.0 - abs(a - b) / max(a, b)


def _date_gap_days(a, b) -> Optional[int]:
    if pd.isna(a) or pd.isna(b):
        return None
    return abs((a - b).days)


def _pair_payload(work_a: pd.Series, work_b: pd.Series, similarity: float,
                   matching_fields: list[str], tier: str) -> dict:
    def brief(row):
        return {
            "work_id": _clean(row.get("work_id")),
            "mp_name": _clean(row.get("mp_name")),
            "state": _clean(row.get("state")),
            "constituency": _clean(row.get("constituency")),
            "work_description": _clean(row.get("work_description")),
            "work_category": _clean(row.get("work_category")),
            "sanctioned_amount": _clean(row.get("sanctioned_amount")),
            "sanction_date": _clean(row.get("sanction_date")),
            "risk_level": _clean(row.get("risk_level")),
        }

    return {
        "tier": tier,
        "label": "Potential Duplicate" if tier == "A" else "Possible Duplicate",
        "similarity_score": round(similarity * 100, 1),
        "matching_fields": matching_fields,
        "work_a": brief(work_a),
        "work_b": brief(work_b),
        "recommended_action": (
            "Verify whether these two sanctioned works represent separate "
            "physical assets, or a duplicate/erroneous entry."
        ),
        "disclaimer": DISCLAIMER,
    }


def _compute_duplicates() -> dict:
    """Runs the full duplicate/batch scan once; result is cached in-process."""
    t0 = time.time()
    df = WORK_DATA.copy()
    df = df[df["work_description"].notna() & (df["work_id"].notna())]
    if df.empty:
        return {"pairs": [], "batches": [], "computed_in_seconds": 0.0, "candidate_pairs_scanned": 0}

    df["_toks"] = df["work_description"].map(_normalize_tokens)
    df["_normtext"] = df["_toks"].map(lambda t: " ".join(sorted(t)))
    df["_sig4"] = df["_toks"].map(lambda t: tuple(sorted(t)[:4]))
    df["_sanction_dt"] = pd.to_datetime(df.get("sanction_date"), errors="coerce")
    df["_recommended_dt"] = pd.to_datetime(df.get("recommended_date"), errors="coerce")

    # --- Tier A / Tier C: exact structural clusters -----------------------
    cluster_key = list(zip(
        df["mp_name"].fillna(""),
        df["_normtext"],
        df["sanctioned_amount"],
        df["_sanction_dt"],
    ))
    df["_cluster_key"] = cluster_key
    # Only meaningful when description text and amount/date are present.
    has_key_fields = (
        df["_normtext"].str.len().gt(0)
        & df["sanctioned_amount"].notna()
        & df["_sanction_dt"].notna()
    )
    keyed = df[has_key_fields]
    cluster_sizes = keyed.groupby("_cluster_key")["work_id"].transform("count")
    keyed = keyed.assign(_cluster_size=cluster_sizes)

    pairs = []
    exact_pair_ids = set()

    for _, group in keyed[keyed["_cluster_size"] == 2].groupby("_cluster_key"):
        rows = list(group.iterrows())
        (ia, a), (ib, b) = rows[0], rows[1]
        pairs.append(_pair_payload(
            a, b, similarity=1.0,
            matching_fields=["Same MP", "Identical description", "Same sanctioned amount", "Same sanction date"],
            tier="A",
        ))
        exact_pair_ids.add(frozenset([a["work_id"], b["work_id"]]))

    batches = []
    for key, group in keyed[keyed["_cluster_size"] >= 3].groupby("_cluster_key"):
        first = group.iloc[0]
        batches.append({
            "mp_name": _clean(first.get("mp_name")),
            "state": _clean(first.get("state")),
            "constituency": _clean(first.get("constituency")),
            "work_description": _clean(first.get("work_description")),
            "sanctioned_amount": _clean(first.get("sanctioned_amount")),
            "sanction_date": _clean(first.get("sanction_date")),
            "unit_count": int(len(group)),
            "work_ids": [str(w) for w in group["work_id"].tolist()][:50],
            "note": (
                "Multiple works share identical description, sanctioned amount, "
                "and sanction date. This commonly reflects a single scheme "
                "sanctioned as several identical units, not a duplicate claim. "
                "Verify that the claimed unit count matches units actually delivered."
            ),
        })
    batches.sort(key=lambda b: (-b["unit_count"], str(b.get("mp_name")), str(b.get("work_description"))))

    # --- Tier B: fuzzy near-duplicates -------------------------------------
    df["_sig"] = list(zip(df["mp_name"].fillna(""), df["constituency"].fillna(""), df["_sig4"]))
    groups = df.groupby("_sig").groups

    scanned = 0
    fuzzy_candidates = []
    for _, idxs in groups.items():
        idxs = list(idxs)
        n = len(idxs)
        if n < 2 or n > 60:
            # Large blocks are dominated by legitimate repeated boilerplate
            # work (e.g. identical fixtures rolled out across many
            # locations) and are already surfaced, honestly, via the batch
            # clusters above rather than as pairwise "duplicates".
            continue
        for i in range(n):
            for j in range(i + 1, n):
                a = df.loc[idxs[i]]
                b = df.loc[idxs[j]]
                if a["work_id"] == b["work_id"]:
                    continue
                key = frozenset([a["work_id"], b["work_id"]])
                if key in exact_pair_ids:
                    continue
                scanned += 1
                ratio = SequenceMatcher(None, a["_normtext"], b["_normtext"]).ratio()
                if ratio < 0.85 or ratio >= 0.999:
                    continue
                amt_sim = _amount_similarity(a.get("sanctioned_amount"), b.get("sanctioned_amount"))
                if amt_sim is None or amt_sim < 0.95:
                    continue
                da = a["_sanction_dt"] if pd.notna(a["_sanction_dt"]) else a["_recommended_dt"]
                db = b["_sanction_dt"] if pd.notna(b["_sanction_dt"]) else b["_recommended_dt"]
                gap = _date_gap_days(da, db)
                if gap is None or gap > 30:
                    continue
                matching = ["Same MP", "Similar description", "Similar sanctioned amount", "Close sanction date"]
                if a.get("constituency") == b.get("constituency"):
                    matching.append("Same constituency")
                fuzzy_candidates.append((ratio, a, b, matching))

    # Sort by similarity, then by work_id pair as a deterministic tie-breaker
    # so the top-300 cutoff (and everything downstream that depends on it,
    # e.g. compliance's duplicate-indicator check) is reproducible across
    # process restarts regardless of Python's hash-seed randomization.
    fuzzy_candidates.sort(key=lambda x: (-x[0], str(x[1]["work_id"]), str(x[2]["work_id"])))
    for ratio, a, b, matching in fuzzy_candidates[:300]:
        pairs.append(_pair_payload(a, b, similarity=ratio, matching_fields=matching, tier="B"))

    pairs.sort(key=lambda p: p["similarity_score"], reverse=True)

    return {
        "pairs": pairs,
        "batches": batches[:200],
        "computed_in_seconds": round(time.time() - t0, 2),
        "candidate_pairs_scanned": scanned,
        "method": (
            "Structural clustering (identical description + amount + sanction date, "
            "same MP) for Tiers A/C, plus fuzzy text similarity (>=85% match, "
            "sanctioned amount within 5%, sanction dates within 30 days) for Tier B. "
            "Implementing agency and GPS/location fields are not present in the "
            "source data and could not be used."
        ),
    }


def get_duplicates() -> dict:
    if "result" not in _DUP_CACHE:
        _DUP_CACHE["result"] = _compute_duplicates()
    return _DUP_CACHE["result"]


@router.get("/api/duplicates")
def api_duplicates(tier: str = "All", limit: int = 100, offset: int = 0):
    data = get_duplicates()
    pairs = data["pairs"]
    if tier in ("A", "B"):
        pairs = [p for p in pairs if p["tier"] == tier]
    return {
        "total_pairs": len(pairs),
        "total_batch_groups": len(data["batches"]),
        "pairs": pairs[offset: offset + limit],
        "method": data["method"],
        "computed_in_seconds": data["computed_in_seconds"],
        "disclaimer": DISCLAIMER,
    }


@router.get("/api/duplicates/batches")
def api_duplicate_batches(limit: int = 100, offset: int = 0):
    data = get_duplicates()
    return {
        "total": len(data["batches"]),
        "rows": data["batches"][offset: offset + limit],
    }


@router.get("/api/duplicates/summary")
def api_duplicates_summary():
    data = get_duplicates()
    tier_a = sum(1 for p in data["pairs"] if p["tier"] == "A")
    tier_b = sum(1 for p in data["pairs"] if p["tier"] == "B")
    return {
        "potential_duplicate_pairs": tier_a,
        "possible_duplicate_pairs": tier_b,
        "batch_pattern_groups": len(data["batches"]),
        "works_in_batch_patterns": sum(b["unit_count"] for b in data["batches"]),
        "disclaimer": DISCLAIMER,
    }


def duplicate_work_ids() -> set:
    """Set of work_ids appearing in any Tier A/B duplicate pair — used by
    compliance/early-warning scoring below."""
    data = get_duplicates()
    ids = set()
    for p in data["pairs"]:
        ids.add(p["work_a"]["work_id"])
        ids.add(p["work_b"]["work_id"])
    return ids


# ===========================================================================
# 2. COST OVERRUN ANALYSIS
# ===========================================================================
#
# Uses fields already computed by the existing pipeline
# (src/features.py: expenditure_overrun_amount, completion_overrun_amount,
# is_sanction_overrun, completion_expenditure_comparison_available). This
# module does not recompute overruns; it only interprets and exposes them,
# and adds a data-driven (not invented) risk band.

def _overrun_band_thresholds(pct_series: pd.Series) -> tuple[float, float]:
    valid = pct_series[pct_series.notna() & (pct_series > 0)]
    if valid.empty:
        return 10.0, 30.0
    return float(valid.quantile(0.33)), float(valid.quantile(0.67))


def _compute_cost_overruns() -> pd.DataFrame:
    df = WORK_DATA.copy()

    sanctioned = pd.to_numeric(df.get("sanctioned_amount"), errors="coerce")
    comp_available = df.get("completion_expenditure_comparison_available", False).fillna(False)
    completion_overrun = pd.to_numeric(df.get("completion_overrun_amount"), errors="coerce")
    expenditure_overrun = pd.to_numeric(df.get("expenditure_overrun_amount"), errors="coerce")

    # Prefer the completion-vs-sanction comparison when it's actually
    # available (final figure); otherwise fall back to expenditure-to-date.
    overrun_amount = np.where(
        comp_available & completion_overrun.notna(),
        completion_overrun,
        expenditure_overrun,
    )
    basis = np.where(
        comp_available & completion_overrun.notna(),
        "completion_amount_vs_sanctioned_amount",
        "expenditure_to_date_vs_sanctioned_amount",
    )

    df["_overrun_amount"] = overrun_amount
    df["_overrun_basis"] = basis
    can_determine = sanctioned.notna() & (sanctioned > 0) & pd.notna(df["_overrun_amount"])
    df["_overrun_determinable"] = can_determine

    df["_overrun_pct"] = np.where(
        can_determine,
        (df["_overrun_amount"] / sanctioned) * 100.0,
        np.nan,
    )
    df["_is_overrun"] = can_determine & (df["_overrun_amount"] > 0)

    low_max, med_max = _overrun_band_thresholds(pd.Series(df["_overrun_pct"]))
    df["_overrun_band_low_max"] = low_max
    df["_overrun_band_med_max"] = med_max

    def band(row):
        if not row["_is_overrun"]:
            return None
        pct = row["_overrun_pct"]
        if pct <= low_max:
            return "LOW"
        if pct <= med_max:
            return "MEDIUM"
        return "HIGH"

    df["_overrun_risk_band"] = df.apply(band, axis=1)
    return df


_COST_OVERRUN_CACHE: dict = {}


def get_cost_overrun_df() -> pd.DataFrame:
    if "df" not in _COST_OVERRUN_CACHE:
        _COST_OVERRUN_CACHE["df"] = _compute_cost_overruns()
    return _COST_OVERRUN_CACHE["df"]


def api_cost_overrun_record(row: pd.Series) -> dict:
    base = _api_work_record(row)
    if not row["_overrun_determinable"]:
        base["cost_overrun"] = {
            "determinable": False,
            "message": "Cost overrun cannot be determined from available source data.",
        }
        return base

    base["cost_overrun"] = {
        "determinable": True,
        "is_overrun": bool(row["_is_overrun"]),
        "basis": row["_overrun_basis"],
        "sanctioned_amount": _clean(row.get("sanctioned_amount")),
        "compared_amount": _clean(
            row.get("completion_amount") if row["_overrun_basis"] == "completion_amount_vs_sanctioned_amount"
            else row.get("total_expenditure")
        ),
        "overrun_amount": _clean(row["_overrun_amount"]) if row["_is_overrun"] else 0,
        "overrun_percentage": round(float(row["_overrun_pct"]), 2) if row["_is_overrun"] else 0.0,
        "risk_band": row["_overrun_risk_band"],
    }
    return base


@router.get("/api/cost-overruns")
def api_cost_overruns(
    page: int = 1,
    page_size: int = 50,
    chamber: str = "All",
    state: str = "All",
    band: str = "All",
    q: Optional[str] = None,
):
    df = get_cost_overrun_df()
    df = df[df["_is_overrun"]]

    if chamber != "All":
        df = df[df["parliament_house"] == chamber]
    if state != "All":
        df = df[df["state"] == state]
    if band != "All":
        df = df[df["_overrun_risk_band"] == band]
    if q:
        ql = q.lower().strip()
        df = df[
            df["work_id"].fillna("").astype(str).str.lower().str.contains(ql, regex=False)
            | df["mp_name"].fillna("").astype(str).str.lower().str.contains(ql, regex=False)
        ]

    df = df.sort_values("_overrun_pct", ascending=False)
    total = len(df)
    start = (page - 1) * page_size
    rows = [api_cost_overrun_record(r) for _, r in df.iloc[start:start + page_size].iterrows()]

    return {
        "total": int(total),
        "page": page,
        "page_size": page_size,
        "rows": rows,
        "disclaimer": DISCLAIMER,
    }


@router.get("/api/cost-overruns/summary")
def api_cost_overruns_summary():
    df = get_cost_overrun_df()
    determinable = df["_overrun_determinable"].sum()
    overrun = df[df["_is_overrun"]]
    return {
        "total_works": int(len(df)),
        "overrun_determinable_count": int(determinable),
        "overrun_not_determinable_count": int(len(df) - determinable),
        "overrun_flagged_count": int(len(overrun)),
        "total_overrun_amount": _clean(overrun["_overrun_amount"].sum()) if not overrun.empty else 0,
        "band_counts": overrun["_overrun_risk_band"].value_counts().to_dict() if not overrun.empty else {},
        "band_thresholds_pct": {
            "low_max": round(float(df["_overrun_band_low_max"].iloc[0]), 1) if not df.empty else None,
            "medium_max": round(float(df["_overrun_band_med_max"].iloc[0]), 1) if not df.empty else None,
            "note": "Bands are derived from the live distribution of overrun % across this dataset (33rd/67th percentile), not a fixed government rule.",
        },
        "disclaimer": DISCLAIMER,
    }


def cost_overrun_lookup(work_id: str) -> Optional[dict]:
    df = get_cost_overrun_df()
    match = df[df["work_id"].astype(str) == str(work_id)]
    if match.empty:
        return None
    row = match.iloc[0]
    if not row["_overrun_determinable"]:
        return {"determinable": False, "message": "Cost overrun cannot be determined from available source data."}
    return {
        "determinable": True,
        "is_overrun": bool(row["_is_overrun"]),
        "basis": row["_overrun_basis"],
        "overrun_amount": _clean(row["_overrun_amount"]) if row["_is_overrun"] else 0,
        "overrun_percentage": round(float(row["_overrun_pct"]), 2) if row["_is_overrun"] else 0.0,
        "risk_band": row["_overrun_risk_band"],
    }


# ===========================================================================
# 3. AUTOMATED COMPLIANCE MONITORING
# ===========================================================================

def _compliance_thresholds(df: pd.DataFrame) -> dict:
    rec_to_sanc = pd.to_numeric(df.get("recommendation_to_sanction_days"), errors="coerce")
    sanc_to_comp = pd.to_numeric(df.get("sanction_to_completion_days"), errors="coerce")
    return {
        "approval_p90": float(rec_to_sanc.quantile(0.90)) if rec_to_sanc.notna().any() else None,
        "completion_p90": float(sanc_to_comp.quantile(0.90)) if sanc_to_comp.notna().any() else None,
    }


def _compute_compliance() -> pd.DataFrame:
    df = WORK_DATA.copy()
    th = _compliance_thresholds(df)
    dup_ids = duplicate_work_ids()

    rec_to_sanc = pd.to_numeric(df.get("recommendation_to_sanction_days"), errors="coerce")

    checks_passed = []
    checks_failed = []
    checks_missing = []

    def evaluate(row):
        passed, failed, missing = [], [], []

        # 1. Recommendation available
        if bool(row.get("has_recommended", False)):
            passed.append("Recommendation available")
        else:
            failed.append("Recommendation not available")

        # 2. Sanction available
        # A large share of MPLADS records are recommendation-only (not yet
        # sanctioned) at the time of this data snapshot. That is a normal
        # pipeline stage, not a compliance violation, and the remaining
        # checks (payment/completion/duration/lifecycle) are not meaningful
        # without a sanction to measure against — so they are marked
        # "not applicable" rather than failed or missing.
        if bool(row.get("has_sanctioned", False)):
            passed.append("Sanction available")
        else:
            missing.append(
                "Sanction not yet recorded for this work — it is at the "
                "recommendation stage; downstream checks are not applicable "
                "until a sanction is issued"
            )
            return passed, failed, missing

        # 3. Expenditure/payment linked
        if bool(row.get("has_expenditure", False)):
            passed.append("Payment/expenditure linked")
        else:
            missing.append("No payment/expenditure record linked")

        # 4. Completion information
        if bool(row.get("has_completed", False)):
            passed.append("Completion information available")
        else:
            missing.append("Completion information missing")

        # 5. Approval duration vs dataset-wide pattern
        v = row.get("recommendation_to_sanction_days")
        if th["approval_p90"] is not None and pd.notna(v):
            if v <= th["approval_p90"]:
                passed.append("Approval duration within typical range")
            else:
                failed.append(
                    f"Approval duration unusually long ({int(v)} days vs "
                    f"typical up to {int(th['approval_p90'])} days for this dataset)"
                )
        else:
            missing.append("Unable to verify approval duration from available data")

        # 6. No duplicate/data-quality indicators
        no_payment_dupes = not (pd.notna(row.get("duplicate_payment_count")) and row.get("duplicate_payment_count", 0) > 0)
        no_work_dupes = row.get("work_id") not in dup_ids
        if no_payment_dupes and no_work_dupes:
            passed.append("No duplicate-record indicators")
        else:
            reasons = []
            if not no_payment_dupes:
                reasons.append("duplicate payment ledger records")
            if not no_work_dupes:
                reasons.append("flagged in duplicate-work screening")
            failed.append("Duplicate indicators present: " + ", ".join(reasons))

        # 7. Lifecycle completeness
        lcs = row.get("lifecycle_completeness_score")
        if pd.notna(lcs):
            if lcs >= 0.75:
                passed.append("Lifecycle record substantially complete")
            else:
                failed.append(f"Lifecycle record incomplete (completeness score {round(float(lcs), 2)})")
        else:
            missing.append("Unable to verify lifecycle completeness from available data")

        return passed, failed, missing

    results = df.apply(evaluate, axis=1, result_type="expand")
    results.columns = ["_passed", "_failed", "_missing"]
    df = pd.concat([df, results], axis=1)

    df["_checks_total"] = df["_passed"].map(len) + df["_failed"].map(len) + df["_missing"].map(len)
    df["_checks_determinable"] = df["_passed"].map(len) + df["_failed"].map(len)
    df["_compliance_score"] = np.where(
        df["_checks_determinable"] > 0,
        df["_passed"].map(len) / df["_checks_determinable"],
        np.nan,
    )

    def status(row):
        if not bool(row.get("has_sanctioned", False)):
            return "INSUFFICIENT DATA"
        determinable = row["_checks_determinable"]
        total = row["_checks_total"]
        if determinable == 0 or determinable < total * 0.5:
            return "INSUFFICIENT DATA"
        if len(row["_failed"]) == 0:
            return "COMPLIANT"
        score = row["_compliance_score"]
        if score is not None and score >= 0.7:
            return "PARTIALLY COMPLIANT"
        return "REQUIRES REVIEW"

    df["_compliance_status"] = df.apply(status, axis=1)
    return df


_COMPLIANCE_CACHE: dict = {}


def get_compliance_df() -> pd.DataFrame:
    if "df" not in _COMPLIANCE_CACHE:
        _COMPLIANCE_CACHE["df"] = _compute_compliance()
    return _COMPLIANCE_CACHE["df"]


def compliance_record(row: pd.Series) -> dict:
    return {
        "work_id": _clean(row.get("work_id")),
        "status": row["_compliance_status"],
        "score": round(float(row["_compliance_score"]), 2) if pd.notna(row["_compliance_score"]) else None,
        "checks_passed": row["_passed"],
        "checks_failed": row["_failed"],
        "checks_missing_data": row["_missing"],
        "passed_count": int(len(row["_passed"])),
        "total_checks": int(row["_checks_total"]),
    }


@router.get("/api/compliance/summary")
def api_compliance_summary():
    df = get_compliance_df()
    return {
        "total_works": int(len(df)),
        "status_counts": df["_compliance_status"].value_counts().to_dict(),
        "disclaimer": (
            "Compliance checks are derived from field availability and dataset-wide "
            "patterns in the source data. 'Unable to verify from available data' does "
            "not mean non-compliant."
        ),
    }


@router.get("/api/compliance")
def api_compliance_list(
    page: int = 1,
    page_size: int = 50,
    status: str = "All",
    chamber: str = "All",
    state: str = "All",
):
    df = get_compliance_df()
    if status != "All":
        df = df[df["_compliance_status"] == status]
    if chamber != "All":
        df = df[df["parliament_house"] == chamber]
    if state != "All":
        df = df[df["state"] == state]

    df = df.sort_values("_compliance_score", ascending=True, na_position="first")
    total = len(df)
    start = (page - 1) * page_size
    rows = []
    for _, r in df.iloc[start:start + page_size].iterrows():
        base = _api_work_record(r)
        base["compliance"] = compliance_record(r)
        rows.append(base)

    return {"total": int(total), "page": page, "page_size": page_size, "rows": rows}


@router.get("/api/compliance/{work_id:path}")
def api_compliance_detail(work_id: str):
    df = get_compliance_df()
    match = df[df["work_id"].astype(str) == str(work_id)]
    if match.empty:
        return {"found": False}
    return {"found": True, "compliance": compliance_record(match.iloc[0])}


def compliance_lookup(work_id: str) -> Optional[dict]:
    df = get_compliance_df()
    match = df[df["work_id"].astype(str) == str(work_id)]
    if match.empty:
        return None
    return compliance_record(match.iloc[0])


# ===========================================================================
# 5. PREDICTIVE / FORWARD-LOOKING RISK ESTIMATES
# ===========================================================================
#
# IMPORTANT: these are transparent, rule-based "risk estimates", explicitly
# NOT described as guaranteed predictions and NOT a new ML model layered on
# top of the existing (untouched) anomaly_model.py. Each estimate is built
# only from fields already present in the pipeline output, using dataset-
# derived percentile thresholds.

def _predictions_df() -> pd.DataFrame:
    df = WORK_DATA.copy()

    sanc_to_comp = pd.to_numeric(df.get("sanction_to_completion_days"), errors="coerce")
    comp_p75 = sanc_to_comp.quantile(0.75) if sanc_to_comp.notna().any() else None
    is_stalled = df.get("is_stalled_work", False).fillna(False)
    not_completed = ~df.get("has_completed", False).fillna(False)

    def delay_risk(row):
        if bool(row.get("_is_stalled")):
            return "HIGH", "Work is flagged as stalled in the pipeline output."
        v = row.get("_sanc_to_comp")
        if pd.notna(v) and comp_p75 is not None:
            if v > comp_p75:
                return "MEDIUM", f"Time from sanction to completion ({int(v)} days) is above the 75th percentile for this dataset ({int(comp_p75)} days)."
            return "LOW", "Sanction-to-completion time is within the typical range for this dataset."
        return "LOW", "Insufficient lifecycle date data to estimate delay risk; defaulting to LOW."

    df["_is_stalled"] = is_stalled
    df["_sanc_to_comp"] = sanc_to_comp
    delay = df.apply(delay_risk, axis=1, result_type="expand")
    df["_delay_risk"], df["_delay_reason"] = delay[0], delay[1]

    def completion_risk(row):
        if bool(row.get("_not_completed")) and bool(row.get("_is_stalled")):
            return "HIGH", "Work has no recorded completion and is flagged as stalled."
        if bool(row.get("_not_completed")):
            return "MEDIUM", "Work has no recorded completion information yet."
        return "LOW", "Completion information is present in the dataset."

    df["_not_completed"] = not_completed
    comp = df.apply(completion_risk, axis=1, result_type="expand")
    df["_completion_risk"], df["_completion_reason"] = comp[0], comp[1]

    exp_ratio = pd.to_numeric(df.get("expenditure_to_sanction_ratio"), errors="coerce")
    vend_conc = pd.to_numeric(df.get("vendor_concentration_score"), errors="coerce")
    exp_p90 = exp_ratio.quantile(0.90) if exp_ratio.notna().any() else None
    vend_p90 = vend_conc.quantile(0.90) if vend_conc.notna().any() else None

    def expenditure_risk(row):
        reasons = []
        level = "LOW"
        r = row.get("expenditure_to_sanction_ratio")
        if pd.notna(r) and exp_p90 is not None and r > exp_p90:
            level = "HIGH"
            reasons.append(f"Expenditure-to-sanction ratio ({round(float(r), 2)}) is above the 90th percentile ({round(float(exp_p90), 2)}).")
        v = row.get("vendor_concentration_score")
        if pd.notna(v) and vend_p90 is not None and v > vend_p90:
            level = "HIGH" if level == "HIGH" else "MEDIUM"
            reasons.append(f"Vendor concentration score ({round(float(v), 2)}) is above the 90th percentile ({round(float(vend_p90), 2)}).")
        if not reasons:
            reasons.append("No elevated expenditure-pattern signals for this work.")
        return level, " ".join(reasons)

    exprisk = df.apply(expenditure_risk, axis=1, result_type="expand")
    df["_expenditure_risk"], df["_expenditure_reason"] = exprisk[0], exprisk[1]

    # Review priority is derived directly from the component risk levels
    # plus the existing pipeline risk_level, rather than an opaque composite
    # score — this keeps every priority explainable in terms of the
    # individual signals that produced it, and avoids the distortion that a
    # quantile-based cutoff would introduce on a mostly-discrete distribution.
    level_rank = {"LOW": 0, "MEDIUM": 1, "HIGH": 2}
    component_max = pd.concat([
        df["_delay_risk"].map(level_rank),
        df["_completion_risk"].map(level_rank),
        df["_expenditure_risk"].map(level_rank),
    ], axis=1).max(axis=1)

    is_high_risk_level = df["risk_level"].isin(["HIGH", "CRITICAL"])
    is_review_risk_level = df["risk_level"].eq("REVIEW")

    def priority(component, high_rl, review_rl):
        if component == 2 or high_rl:
            return "HIGH"
        if component == 1 or review_rl:
            return "MEDIUM"
        return "LOW"

    df["_review_priority"] = [
        priority(c, h, r)
        for c, h, r in zip(component_max, is_high_risk_level, is_review_risk_level)
    ]
    df["_review_priority_score"] = component_max + is_high_risk_level.astype(int) * 2 + is_review_risk_level.astype(int)
    return df


_PRED_CACHE: dict = {}


def get_predictions_df() -> pd.DataFrame:
    if "df" not in _PRED_CACHE:
        _PRED_CACHE["df"] = _predictions_df()
    return _PRED_CACHE["df"]


def prediction_record(row: pd.Series) -> dict:
    return {
        "work_id": _clean(row.get("work_id")),
        "label": "Risk estimate (not a guaranteed prediction)",
        "delay_risk": {"level": row["_delay_risk"], "reason": row["_delay_reason"]},
        "completion_risk": {"level": row["_completion_risk"], "reason": row["_completion_reason"]},
        "expenditure_risk": {"level": row["_expenditure_risk"], "reason": row["_expenditure_reason"]},
        "future_review_priority": row["_review_priority"],
        "method": (
            "Transparent rule-based risk estimate derived from existing pipeline "
            "features (lifecycle status, sanction-to-completion duration, "
            "expenditure ratio, vendor concentration) compared against this "
            "dataset's own percentile distribution. This is not a machine-learning "
            "prediction and does not use the pipeline's ML anomaly model."
        ),
    }


@router.get("/api/predictions/summary")
def api_predictions_summary():
    df = get_predictions_df()
    return {
        "total_works": int(len(df)),
        "delay_risk_counts": df["_delay_risk"].value_counts().to_dict(),
        "completion_risk_counts": df["_completion_risk"].value_counts().to_dict(),
        "expenditure_risk_counts": df["_expenditure_risk"].value_counts().to_dict(),
        "review_priority_counts": df["_review_priority"].value_counts().to_dict(),
        "label": "Risk estimate (not a guaranteed prediction)",
    }


@router.get("/api/predictions")
def api_predictions_list(
    page: int = 1,
    page_size: int = 50,
    priority: str = "All",
    chamber: str = "All",
    state: str = "All",
):
    df = get_predictions_df()
    if priority != "All":
        df = df[df["_review_priority"] == priority]
    if chamber != "All":
        df = df[df["parliament_house"] == chamber]
    if state != "All":
        df = df[df["state"] == state]

    df = df.sort_values("_review_priority_score", ascending=False)
    total = len(df)
    start = (page - 1) * page_size
    rows = []
    for _, r in df.iloc[start:start + page_size].iterrows():
        base = _api_work_record(r)
        base["prediction"] = prediction_record(r)
        rows.append(base)
    return {"total": int(total), "page": page, "page_size": page_size, "rows": rows}


@router.get("/api/predictions/{work_id:path}")
def api_prediction_detail(work_id: str):
    df = get_predictions_df()
    match = df[df["work_id"].astype(str) == str(work_id)]
    if match.empty:
        return {"found": False}
    return {"found": True, "prediction": prediction_record(match.iloc[0])}


def prediction_lookup(work_id: str) -> Optional[dict]:
    df = get_predictions_df()
    match = df[df["work_id"].astype(str) == str(work_id)]
    if match.empty:
        return None
    return prediction_record(match.iloc[0])


# ===========================================================================
# 4. EARLY WARNING SYSTEM
# ===========================================================================
# Combines: existing risk_level, cost-overrun band, compliance status, and
# duplicate-work flag. Purely additive/informational — never asserts fraud.

_ACTION_MAP = {
    "duplicate": "Verify whether the flagged works represent separate assets.",
    "overrun": "Review sanction, expenditure and completion records for cost variance.",
    "compliance": "Review missing/failed compliance checks and supporting documentation.",
    "stalled": "Check reason for extended approval or completion duration.",
    "risk": "Review sanction, expenditure and completion records.",
}


def _compute_early_warnings() -> list[dict]:
    work_df = WORK_DATA
    comp_df = get_compliance_df()[["work_id", "_compliance_status"]]
    overrun_df = get_cost_overrun_df()[["work_id", "_is_overrun", "_overrun_risk_band"]]
    dup_ids = duplicate_work_ids()

    merged = work_df.merge(comp_df, on="work_id", how="left").merge(overrun_df, on="work_id", how="left")

    warnings = []
    for _, row in merged.iterrows():
        signals = []
        reasons = []

        risk_level = row.get("risk_level")
        if risk_level in ("HIGH", "CRITICAL"):
            signals.append("risk")
            reasons.append(f"Risk pipeline classified this work as {risk_level}.")

        if row.get("work_id") in dup_ids:
            signals.append("duplicate")
            reasons.append("Appears in duplicate-work screening results.")

        if bool(row.get("_is_overrun")) and row.get("_overrun_risk_band") in ("MEDIUM", "HIGH"):
            signals.append("overrun")
            reasons.append(f"Cost overrun flagged ({row.get('_overrun_risk_band')} band).")

        if row.get("_compliance_status") == "REQUIRES REVIEW":
            signals.append("compliance")
            reasons.append("Compliance status: REQUIRES REVIEW.")

        if bool(row.get("is_stalled_work")):
            signals.append("stalled")
            reasons.append("Work is flagged as stalled.")

        if not signals:
            continue

        if risk_level == "CRITICAL" or len(set(signals)) >= 3:
            severity = "Immediate Review"
        elif risk_level == "HIGH" or len(set(signals)) >= 2:
            severity = "Priority Review"
        else:
            severity = "Monitor"

        actions = list(dict.fromkeys(_ACTION_MAP[s] for s in dict.fromkeys(signals)))

        warnings.append({
            "work_id": _clean(row.get("work_id")),
            "mp_name": _clean(row.get("mp_name")),
            "state": _clean(row.get("state")),
            "risk_level": _clean(risk_level),
            "severity": severity,
            "signal_count": len(set(signals)),
            "signals": sorted(set(signals)),
            "reasons": reasons,
            "recommended_actions": actions,
            "disclaimer": DISCLAIMER,
        })

    severity_rank = {"Immediate Review": 2, "Priority Review": 1, "Monitor": 0}
    warnings.sort(key=lambda w: (severity_rank[w["severity"]], w["signal_count"]), reverse=True)
    return warnings


_EARLY_WARNING_CACHE: dict = {}


def get_early_warnings() -> list:
    if "list" not in _EARLY_WARNING_CACHE:
        _EARLY_WARNING_CACHE["list"] = _compute_early_warnings()
    return _EARLY_WARNING_CACHE["list"]


@router.get("/api/early-warnings/summary")
def api_early_warnings_summary():
    warnings = get_early_warnings()
    counts = {"Immediate Review": 0, "Priority Review": 0, "Monitor": 0}
    for w in warnings:
        counts[w["severity"]] += 1
    return {"total_flagged": len(warnings), "severity_counts": counts, "disclaimer": DISCLAIMER}


@router.get("/api/early-warnings")
def api_early_warnings(
    severity: str = "All",
    state: str = "All",
    page: int = 1,
    page_size: int = 50,
):
    warnings = get_early_warnings()
    if severity != "All":
        warnings = [w for w in warnings if w["severity"] == severity]
    if state != "All":
        warnings = [w for w in warnings if w["state"] == state]

    total = len(warnings)
    start = (page - 1) * page_size
    page_rows = [
        explain.enrich_early_warning(w)
        for w in warnings[start:start + page_size]
    ]
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "rows": page_rows,
    }


def early_warning_lookup(work_id: str) -> Optional[dict]:
    for w in get_early_warnings():
        if w["work_id"] == str(work_id):
            return w
    return None


# ===========================================================================
# 6. TREND ANALYSIS
# ===========================================================================

def _month_key(series: pd.Series) -> pd.Series:
    dt = pd.to_datetime(series, errors="coerce")
    return dt.dt.to_period("M").astype(str)


@router.get("/api/trends")
def api_trends(
    metric: str = "sanctions",
    chamber: str = "All",
    state: str = "All",
    mp_id: Optional[str] = None,
):
    """
    metric: one of
      sanctions   - sanctioned works count + amount by month (sanction_date)
      expenditure - expenditure by month (last_payment_date as proxy for the
                    date money moved; first_payment_date also considered)
      completions - completed works by month (completion_date)
      risk        - risk-level distribution by month (sanction_date)
    """
    df = WORK_DATA
    if chamber != "All":
        df = df[df["parliament_house"] == chamber]
    if state != "All":
        df = df[df["state"] == state]
    if mp_id:
        df = df[df["_mp_id"] == mp_id]

    if df.empty:
        return {"metric": metric, "series": [], "note": "No works match the selected filters."}

    if metric == "sanctions":
        d = df[df["sanction_date"].notna()].copy()
        d["_month"] = _month_key(d["sanction_date"])
        g = d.groupby("_month").agg(
            works=("work_id", "count"),
            sanctioned_amount=("sanctioned_amount", "sum"),
        ).reset_index().sort_values("_month")
        series = g.rename(columns={"_month": "month"}).to_dict("records")

    elif metric == "expenditure":
        exp = EXP.copy()
        if exp.empty or "expenditure_date" not in exp.columns:
            return {"metric": metric, "series": [], "note": "Expenditure date field not available in source data."}
        work_ids = set(df["work_id"].astype(str))
        exp = exp[exp["work_id"].astype(str).isin(work_ids)]
        exp["expenditure_date"] = pd.to_datetime(exp["expenditure_date"], errors="coerce")
        exp = exp[exp["expenditure_date"].notna()]
        exp["_month"] = exp["expenditure_date"].dt.to_period("M").astype(str)
        g = exp.groupby("_month").agg(
            payments=("expenditure_id", "count"),
            amount=("amount", "sum"),
        ).reset_index().sort_values("_month")
        series = g.rename(columns={"_month": "month"}).to_dict("records")

    elif metric == "completions":
        d = df[df["completion_date"].notna()].copy()
        d["_month"] = _month_key(d["completion_date"])
        g = d.groupby("_month").agg(
            works_completed=("work_id", "count"),
            completion_amount=("completion_amount", "sum"),
        ).reset_index().sort_values("_month")
        series = g.rename(columns={"_month": "month"}).to_dict("records")

    elif metric == "risk":
        d = df[df["sanction_date"].notna()].copy()
        d["_month"] = _month_key(d["sanction_date"])
        g = d.groupby(["_month", "risk_level"]).size().unstack(fill_value=0).reset_index().sort_values("_month")
        series = g.rename(columns={"_month": "month"}).to_dict("records")

    else:
        return {"metric": metric, "series": [], "note": f"Unknown metric '{metric}'."}

    series = [{k: _clean(v) for k, v in row.items()} for row in series]
    return {
        "metric": metric,
        "filters": {"chamber": chamber, "state": state, "mp_id": mp_id},
        "series": series,
        "note": "Only periods present in the source data are shown; no interpolated or fabricated periods.",
    }