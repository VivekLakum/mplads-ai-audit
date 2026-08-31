"""
Human-readable audit explanation layer.

Purpose (PS26102 gap — "make the system human-readable"):
The existing pipeline (src/rules.py, src/scoring.py) and the analytics
gap-modules (backend/analytics.py) already compute correct, well-evidenced
signals — deterministic rule reasons, statistical Z-scores, an ML anomaly
percentile, cost-overrun figures, compliance checks, early-warning signals
and risk-estimate priorities. What was still technical-first is how those
signals are *presented*: raw scores and percentiles as the primary text on
the work page.

This module does not compute any new risk signal and does not change any
score. It only translates the EXISTING signal text/values into plain
language, generically per signal *category* (never per individual work).
Every explanation below is produced dynamically from the actual row data
passed in; nothing here is a hardcoded, work-specific sentence.

Design note on "do not fabricate": every function here degrades to
"Not available" / omits a finding when the underlying value is missing,
rather than inventing a number or a narrative.
"""

from __future__ import annotations

import re
from typing import Optional


# ---------------------------------------------------------------------------
# 1. Deterministic rule-reason -> plain language
# ---------------------------------------------------------------------------
# Keyed on the exact category label used as the text before ":" in
# src/rules.py's `reasons.append(...)` calls. Each entry is a *generic*
# template; the specific numbers come from the row/reason text itself.
RULE_CATEGORY_INFO = {
    "Potential Duplicate Transaction Records": {
        "headline": "Duplicate-looking payment records",
        "why": (
            "Multiple ledger entries with identical attributes can mean the "
            "same payment was recorded (or paid) more than once."
        ),
        "weight": 55,
        "action": "Verify payment/expenditure records for duplicate billing.",
    },
    "Critical Financial Control": {
        "headline": "Expenditure exceeds the sanctioned amount",
        "why": (
            "Spending beyond what was formally sanctioned bypasses the "
            "financial control the sanction is meant to enforce."
        ),
        "weight": 90,
        "action": "Verify expenditure records against the sanction order.",
    },
    "Financial Control Anomaly": {
        "headline": "Completion amount exceeds the sanctioned amount",
        "why": (
            "The reported completion cost is higher than what was "
            "sanctioned, which should normally trigger a revised sanction."
        ),
        "weight": 80,
        "action": "Verify completion documentation against the sanction order.",
    },
    "Impossible Chronology": {
        "headline": "Recorded dates are out of order",
        "why": (
            "One recorded stage (sanction, payment or completion) is dated "
            "before an earlier stage it should follow. This usually points "
            "to a data-entry error, but can also mask irregular processing."
        ),
        "weight": 85,
        "action": "Review the sanction timeline and correct or verify the source records.",
    },
    "Process Inefficiency": {
        "headline": "Approval took unusually long",
        "why": (
            "The delay may indicate administrative inefficiency or an "
            "unusual approval process."
        ),
        "weight": 35,
        "action": "Review the approval timeline and identify the reason for the delay.",
    },
    "Unusual Payment Fragmentation": {
        "headline": "Payment split into an unusually high number of instalments",
        "why": (
            "Splitting a payment into many small disbursements can be used "
            "to stay under approval or scrutiny thresholds."
        ),
        "weight": 55,
        "action": "Verify expenditure records and the justification for the payment schedule.",
    },
    "Vendor Concentration Risk": {
        "headline": "Most of the money went to a single vendor",
        "why": (
            "A single vendor receiving most of the payments on a work can "
            "indicate reduced competition or a conflict of interest, though "
            "it can also be legitimate for a single-contractor work."
        ),
        "weight": 55,
        "action": "Review implementing agency and vendor records for this work.",
    },
    "Amount Outlier": {
        "headline": "Amount is unusually high compared to similar works",
        "why": (
            "The sanctioned or spent amount is far above what comparable "
            "works of the same type typically cost."
        ),
        "weight": 65,
        "action": "Verify expenditure records and compare against similar works.",
    },
    "Dormant Sanctioned Work": {
        "headline": "Work was sanctioned but shows no activity",
        "why": (
            "A work sanctioned a long time ago with no spending and no "
            "progress may be stalled, abandoned, or incorrectly recorded as "
            "sanctioned."
        ),
        "weight": 45,
        "action": "Conduct field verification to confirm the work's actual status.",
    },
    # These two categories are appended by src/scoring.py (not src/rules.py)
    # as supporting evidence when the deterministic rules above did not
    # already fire, so they use the same generic-category mapping approach.
    "ML Supporting Signal": {
        "headline": "Overall pattern flagged as statistically unusual",
        "why": (
            "An automated pattern-detection model (Isolation Forest) rates "
            "this work's overall combination of amounts and timings as "
            "unusual compared with comparable works. It is a general "
            "signal, not tied to one specific rule."
        ),
        "weight": 35,
        "action": "Review this work's records as part of routine risk-based sampling.",
    },
    "Peer Statistical Signal": {
        "headline": "Amount is a statistical outlier versus its peer group",
        "why": (
            "The amount is far from the typical range for similar works, "
            "based on a robust (outlier-resistant) statistical comparison."
        ),
        "weight": 40,
        "action": "Verify expenditure records and compare against similar works.",
    },
}

# Categories that describe an *absence* of a signal rather than a finding —
# these are never shown as a "key finding".
_NON_FINDING_CATEGORIES = {"Normal Work"}

_NO_ACTION_NEEDED = "No additional action beyond routine monitoring."


def _split_reason(reason: str) -> tuple[Optional[str], str]:
    """Split a rule_reasons string into (category, detail)."""
    if not isinstance(reason, str) or ":" not in reason:
        return None, str(reason) if reason is not None else ""
    category, _, detail = reason.partition(":")
    return category.strip(), detail.strip()


def _severity_word(weight: float) -> str:
    if weight >= 80:
        return "Critical concern"
    if weight >= 55:
        return "Serious concern"
    if weight >= 35:
        return "Moderate concern"
    return "Minor concern"


def humanize_rule_reason(reason: str) -> dict:
    """
    Turn one deterministic rule-reason string (already produced by
    src/rules.py) into a structured, plain-language finding:
    what happened / why it matters / how serious / recommended action.

    The category -> plain-language mapping is generic (fixed per category,
    not per work); the "what happened" text embeds the actual numbers that
    were already computed for this specific work.
    """
    category, detail = _split_reason(reason)
    info = RULE_CATEGORY_INFO.get(category)

    if info is None:
        # Unmapped category — degrade gracefully instead of fabricating a
        # category-specific narrative.
        return {
            "source": "rule",
            "headline": category or "Audit rule triggered",
            "what_happened": detail or reason,
            "why_it_matters": (
                "This pattern was flagged by an automated audit rule and "
                "has not yet been reviewed by a human auditor."
            ),
            "severity": "Moderate concern",
            "recommended_action": "Review the underlying records for this work.",
            "weight": 40,
        }

    return {
        "source": "rule",
        "headline": info["headline"],
        "what_happened": detail or info["headline"],
        "why_it_matters": info["why"],
        "severity": _severity_word(info["weight"]),
        "recommended_action": info["action"],
        "weight": info["weight"],
    }


# ---------------------------------------------------------------------------
# 2. Overall assessment banner
# ---------------------------------------------------------------------------
RISK_LEVEL_COPY = {
    "CRITICAL": (
        "CRITICAL — Strong audit evidence requires immediate review.",
        90,
    ),
    "HIGH": (
        "HIGH RISK — Multiple unusual patterns require human review.",
        70,
    ),
    "REVIEW": (
        "REQUIRES REVIEW — Some patterns warrant a closer look.",
        45,
    ),
    "NORMAL": (
        "LOW RISK — No significant audit concerns identified.",
        10,
    ),
}

# Plain-language display label. The underlying `risk_level` values
# (NORMAL/REVIEW/HIGH/CRITICAL) are left unchanged everywhere else in the
# system (other pages/filters key off them) — this is only an additional,
# more citizen-friendly label for the plain-language layer.
DISPLAY_LEVEL = {
    "CRITICAL": "CRITICAL",
    "HIGH": "HIGH",
    "REVIEW": "MEDIUM",
    "NORMAL": "LOW",
}


def overall_assessment(risk_level: Optional[str], finding_count: int = 0) -> dict:
    level = (risk_level or "NORMAL").upper()
    headline, weight = RISK_LEVEL_COPY.get(level, RISK_LEVEL_COPY["NORMAL"])
    display_level = DISPLAY_LEVEL.get(level, "LOW")

    if level == "NORMAL" or finding_count == 0:
        summary = (
            "No significant issues were identified for this work based on "
            "the available records. Routine monitoring is sufficient."
        )
    elif level == "CRITICAL":
        summary = (
            f"This work shows {finding_count} serious pattern(s) — "
            "including strong evidence-based signals — that require "
            "immediate human review. This does not confirm fraud or "
            "wrongdoing."
        )
    elif level == "HIGH":
        summary = (
            f"This work shows {finding_count} unusual pattern(s) that "
            "require review by an auditor or the implementing authority. "
            "This is a risk signal, not a finding of wrongdoing."
        )
    else:  # REVIEW
        summary = (
            f"This work shows {finding_count} pattern(s) that are somewhat "
            "unusual and worth a closer look, though the evidence is not "
            "strong enough to call it high risk."
        )

    return {
        "risk_level": level,
        "display_level": display_level,
        "headline": headline,
        "summary": summary,
        "weight": weight,
    }


# ---------------------------------------------------------------------------
# 3. Cost overrun -> plain finding
# ---------------------------------------------------------------------------
def humanize_cost_overrun(co: Optional[dict]) -> Optional[dict]:
    if not co or not co.get("determinable"):
        return None
    if not co.get("is_overrun"):
        return None

    pct = co.get("overrun_percentage")
    band = co.get("risk_band") or "LOW"
    weight = {"HIGH": 85, "MEDIUM": 60, "LOW": 35}.get(band, 40)
    pct_text = f"{pct:.1f}%" if isinstance(pct, (int, float)) else "an undetermined amount"

    return {
        "source": "cost_overrun",
        "headline": "Actual cost exceeded the sanctioned amount",
        "what_happened": (
            f"The recorded cost for this work is {pct_text} above the "
            f"sanctioned amount ({band.title()} band, relative to other "
            f"works in this dataset)."
        ),
        "why_it_matters": (
            "Cost overruns without a revised sanction can indicate weak "
            "cost estimation, scope changes that were not formally "
            "approved, or financial irregularity."
        ),
        "severity": _severity_word(weight),
        "recommended_action": "Verify expenditure records and confirm whether a revised sanction was issued.",
        "weight": weight,
    }


# ---------------------------------------------------------------------------
# 4. Compliance failed-check -> plain finding
# ---------------------------------------------------------------------------
def humanize_compliance_failures(compliance: Optional[dict]) -> list[dict]:
    if not compliance or not compliance.get("checks_failed"):
        return []

    findings = []
    for text in compliance["checks_failed"]:
        low = text.lower()
        if "duplicate" in low:
            action = "Check whether this work overlaps with another sanctioned work."
        elif "approval duration" in low or "duration" in low:
            action = "Review the sanction timeline and identify the reason for the delay."
        elif "lifecycle" in low or "incomplete" in low:
            action = "Verify completion documentation for this work."
        else:
            action = "Review the failed compliance check against source records."

        findings.append({
            "source": "compliance",
            "headline": "Compliance check failed",
            "what_happened": text,
            "why_it_matters": (
                "This check compares the work against patterns observed "
                "across the dataset or against basic financial-control "
                "rules; a failure means it falls outside the normal range."
            ),
            "severity": "Serious concern",
            "recommended_action": action,
            "weight": 50,
        })
    return findings


# ---------------------------------------------------------------------------
# 5. Duplicate-work match -> plain finding
# ---------------------------------------------------------------------------
def humanize_duplicate_match(matches: Optional[list], work_id: str) -> Optional[dict]:
    if not matches:
        return None
    m = matches[0]
    other = (
        m["work_b"]["work_id"] if m["work_a"]["work_id"] == str(work_id)
        else m["work_a"]["work_id"]
    )
    tier = m.get("tier", "Possible Duplicate")
    similarity = m.get("similarity_score")
    sim_text = f"{similarity}% similar" if similarity is not None else "similar"

    weight = {"High Confidence": 75, "Possible Duplicate": 50}.get(tier, 45)

    return {
        "source": "duplicate",
        "headline": "Possible duplicate work",
        "what_happened": (
            f"This work is {sim_text} to work {other} ({tier}). "
            f"{len(matches)} potential match(es) were found in total."
        ),
        "why_it_matters": (
            "Two very similar work records can represent the same physical "
            "asset billed twice, or two genuinely separate works with a "
            "similar description (e.g. streetlights installed at different "
            "locations). Similarity alone does not establish duplicate "
            "billing."
        ),
        "severity": _severity_word(weight),
        "recommended_action": "Check whether the work overlaps with another sanctioned work.",
        "weight": weight,
    }


# ---------------------------------------------------------------------------
# 6. Statistical / ML fallback finding (only when nothing else explains it)
# ---------------------------------------------------------------------------
def humanize_ml_signal(ml_percentile) -> Optional[dict]:
    if ml_percentile is None:
        return None
    try:
        p = float(ml_percentile)
    except (TypeError, ValueError):
        return None
    if p != p:  # NaN never carries meaning here — never fabricate a value.
        return None
    if p < 90:
        return None
    return {
        "source": "ml",
        "headline": "Overall pattern flagged as statistically unusual",
        "what_happened": (
            f"An automated pattern-detection model (Isolation Forest) rates "
            f"this work's overall combination of amounts and timings as "
            f"more unusual than {p:.1f}% of comparable works in this "
            f"dataset."
        ),
        "why_it_matters": (
            "This is a general statistical signal, not tied to one specific "
            "rule. It is worth a second look even though the model cannot "
            "say exactly what is unusual about it."
        ),
        "severity": _severity_word(35 if p < 97 else 55),
        "recommended_action": "Review this work's records as part of routine risk-based sampling.",
        "weight": 35 if p < 97 else 55,
    }


# ---------------------------------------------------------------------------
# 7. Top-level assembly
# ---------------------------------------------------------------------------
def build_work_explanation(
    *,
    work: dict,
    deterministic_reasons: list,
    cost_overrun: Optional[dict],
    compliance: Optional[dict],
    duplicate_matches: Optional[list],
    ml_anomaly_percentile,
    max_findings: int = 5,
) -> dict:
    """
    Assemble the Priority-1/Priority-2 plain-language explanation block for
    one work, from signals that are already computed elsewhere. Returns:
      - overall: {risk_level, headline}
      - key_findings: up to `max_findings` plain-language findings, most
        severe first
      - recommended_actions: de-duplicated action list, most-severe-first
    """
    findings: list[dict] = []

    for reason in (deterministic_reasons or []):
        category, _ = _split_reason(reason)
        if category in _NON_FINDING_CATEGORIES:
            continue
        findings.append(humanize_rule_reason(reason))

    dup_finding = humanize_duplicate_match(duplicate_matches, work.get("work_id"))
    if dup_finding:
        findings.append(dup_finding)

    co_finding = humanize_cost_overrun(cost_overrun)
    if co_finding:
        findings.append(co_finding)

    findings.extend(humanize_compliance_failures(compliance))

    # Only surface the generic ML signal when it isn't already implied by a
    # more specific finding above (keeps the list from being redundant).
    if not findings:
        ml_finding = humanize_ml_signal(ml_anomaly_percentile)
        if ml_finding:
            findings.append(ml_finding)

    findings.sort(key=lambda f: f["weight"], reverse=True)
    top_findings = findings[:max_findings]

    if top_findings:
        actions = list(dict.fromkeys(f["recommended_action"] for f in top_findings))
        top_action = top_findings[0]["recommended_action"]
    else:
        actions = [_NO_ACTION_NEEDED]
        top_action = _NO_ACTION_NEEDED

    return {
        "overall": overall_assessment(work.get("risk_level"), len(top_findings)),
        "key_findings": top_findings,
        "recommended_actions": actions,
        "top_recommended_action": top_action,
        "total_signals_detected": len(findings),
    }


# ---------------------------------------------------------------------------
# 8. Early-warning plain-language enrichment (Priority 6)
# ---------------------------------------------------------------------------
# Maps the existing early-warning `signals` codes (see backend/analytics.py
# _compute_early_warnings) to the PS-style plain issue titles, without
# changing how those signals are detected.
EARLY_WARNING_SIGNAL_COPY = {
    "risk": {
        "issue": "Expenditure or overall pattern is unusual",
        "why": "The automated risk pipeline classified this work's overall pattern as unusual enough to require review.",
    },
    "duplicate": {
        "issue": "Possible duplicate work",
        "why": "This work closely resembles another work in the dataset; it may be the same asset recorded twice, or a separate but similarly described work.",
    },
    "overrun": {
        "issue": "Cost exceeded the sanctioned amount",
        "why": "Actual spending or completion cost is higher than what was formally sanctioned for this work.",
    },
    "compliance": {
        "issue": "Compliance check requires review",
        "why": "One or more compliance checks for this work failed against dataset-wide patterns or basic financial-control rules.",
    },
    "stalled": {
        "issue": "Project is taking unusually long",
        "why": "This work was sanctioned a long time ago but shows no recorded expenditure or completion progress.",
    },
}


def enrich_early_warning(warning: dict) -> dict:
    """Add a `plain_language` list to an existing early-warning dict without
    altering any of its existing fields."""
    plain = []
    for signal in warning.get("signals", []):
        copy = EARLY_WARNING_SIGNAL_COPY.get(signal)
        if not copy:
            continue
        plain.append({
            "issue": copy["issue"],
            "why_it_matters": copy["why"],
        })
    enriched = dict(warning)
    enriched["plain_language"] = plain
    return enriched