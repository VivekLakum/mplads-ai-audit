import json
import numpy as np
import pandas as pd


def compute_composite_risk_scores(df_feat, rule_results_df, ml_results_df):
    """Computes transparent composite risk score (0-100), risk levels, and human-readable audit explanations."""
    df_merged = pd.merge(df_feat, rule_results_df, on="work_id", how="left")
    df_merged = pd.merge(df_merged, ml_results_df, on="work_id", how="left")

    # Statistical Risk Score (0-100 based on robust Z-scores).
    # Use a smooth bounded transformation so Z=4 is not automatically
    # identical to Z=40 or Z=176. Missing Z-scores contribute no statistical
    # evidence.
    sanc_abs_z = pd.to_numeric(
        df_merged["sanc_robust_zscore"], errors="coerce"
    ).abs()
    exp_abs_z = pd.to_numeric(
        df_merged["exp_robust_zscore"], errors="coerce"
    ).abs()

    max_z = pd.concat([sanc_abs_z, exp_abs_z], axis=1).max(axis=1, skipna=True)
    max_z = max_z.fillna(0.0)

    # 3.0 is the audit threshold used by the rules. The transformation
    # reaches 50 at Z=3 and approaches 100 smoothly for increasingly extreme
    # observations without hard-capping everything above Z=4.
    stat_risk_score = 100.0 * (1.0 - np.exp(-max_z / 6.0))
    stat_risk_score = np.clip(stat_risk_score, 0.0, 100.0)

    df_merged["stat_risk_score"] = np.round(stat_risk_score, 1)

    # Composite Risk Score Calculation
    # Weights: Rule Score 50%, ML Percentile 30%, Statistical Risk 20%
    composite_score = (
        (0.50 * df_merged["rule_score"])
        + (0.30 * df_merged["ml_anomaly_percentile"])
        + (0.20 * df_merged["stat_risk_score"])
    )

    df_merged["risk_score"] = np.round(
        np.clip(composite_score, 0.0, 100.0), 1
    )

    # Assign Explainable Risk Level with Evidence-Based Critical Gate.
    #
    # The composite score remains unchanged:
    #   50% deterministic rules
    #   30% Isolation Forest percentile
    #   20% peer statistical risk
    #
    # CRITICAL is reserved for strong audit evidence rather than statistical
    # or ML unusualness alone.
    def assign_level(row):
        score = (
            float(row["risk_score"])
            if pd.notnull(row["risk_score"])
            else 0.0
        )
        rule_score = (
            float(row["rule_score"])
            if pd.notnull(row["rule_score"])
            else 0.0
        )
        stat_score = (
            float(row["stat_risk_score"])
            if pd.notnull(row["stat_risk_score"])
            else 0.0
        )
        ml_pct = (
            float(row["ml_anomaly_percentile"])
            if pd.notnull(row["ml_anomaly_percentile"])
            else 0.0
        )

        # Base level from the unchanged composite score.
        if score >= 80.0:
            level = "CRITICAL"
        elif score >= 60.0:
            level = "HIGH"
        elif score >= 30.0:
            level = "REVIEW"
        else:
            level = "NORMAL"

        # ML is supporting evidence only. It cannot independently create
        # HIGH or CRITICAL.
        if rule_score <= 0.0 and stat_score <= 0.0:
            if level in ["HIGH", "CRITICAL"]:
                return "REVIEW"

        # Strong deterministic evidence can justify CRITICAL.
        strong_rule_evidence = rule_score >= 75.0

        # Meaningful deterministic evidence supported by another channel.
        rule_plus_stat = (
            rule_score >= 65.0
            and stat_score >= 70.0
        )
        rule_plus_ml = (
            rule_score >= 65.0
            and ml_pct >= 95.0
        )

        if level == "CRITICAL":
            if strong_rule_evidence or rule_plus_stat or rule_plus_ml:
                return "CRITICAL"

            # High composite score without sufficient direct audit evidence
            # remains HIGH for human review.
            return "HIGH"

        return level

    df_merged["risk_level"] = df_merged.apply(assign_level, axis=1)

    # Evidence metadata for dashboard/audit interpretation.
    # These fields do not change the composite score.
    df_merged["has_rule_evidence"] = (
        pd.to_numeric(df_merged["rule_score"], errors="coerce").fillna(0) > 0
    )
    df_merged["has_strong_rule_evidence"] = (
        pd.to_numeric(df_merged["rule_score"], errors="coerce").fillna(0) >= 75
    )
    df_merged["has_strong_statistical_evidence"] = (
        pd.to_numeric(df_merged["stat_risk_score"], errors="coerce").fillna(0) >= 70
    )
    df_merged["has_strong_ml_evidence"] = (
        pd.to_numeric(df_merged["ml_anomaly_percentile"], errors="coerce").fillna(0) >= 95
    )

    # Aggregate Human-Readable Audit Explanations.
    # Explanations distinguish deterministic audit rules, ML support, and
    # peer-statistical evidence. They do not claim confirmed fraud.
    def format_reasons(row):
        reasons = (
            list(row["rule_reasons"])
            if isinstance(row["rule_reasons"], list)
            else []
        )

        ml_pct = pd.to_numeric(
            pd.Series([row["ml_anomaly_percentile"]]), errors="coerce"
        ).iloc[0]
        if pd.notnull(ml_pct):
            if ml_pct >= 95.0:
                reasons.append(
                    f"ML Supporting Signal: Isolation Forest anomaly percentile "
                    f"is {ml_pct:.1f}%, placing this work among the rarest "
                    f"feature combinations in the evaluated population"
                )
            elif ml_pct >= 90.0 and len(reasons) == 0:
                reasons.append(
                    f"ML Supporting Signal: Isolation Forest anomaly percentile "
                    f"is {ml_pct:.1f}%, indicating a relatively unusual "
                    f"feature combination"
                )

        sanc_z = pd.to_numeric(
            pd.Series([row["sanc_robust_zscore"]]), errors="coerce"
        ).iloc[0]
        exp_z = pd.to_numeric(
            pd.Series([row["exp_robust_zscore"]]), errors="coerce"
        ).iloc[0]

        if pd.notnull(sanc_z) and abs(sanc_z) > 3.0 and not any(
            "Amount Outlier" in r for r in reasons
        ):
            reasons.append(
                f"Peer Statistical Signal: Sanctioned amount has robust "
                f"Z-score {sanc_z:.1f} relative to its defined peer group"
            )

        if pd.notnull(exp_z) and abs(exp_z) > 3.0 and not any(
            "Amount Outlier" in r for r in reasons
        ):
            reasons.append(
                f"Peer Statistical Signal: Total expenditure has robust "
                f"Z-score {exp_z:.1f} relative to its defined peer group"
            )

        if len(reasons) == 0:
            reasons.append(
                "Normal Work: No deterministic audit rule or supporting "
                "statistical/ML risk signal exceeded the configured thresholds"
            )

        return reasons

    df_merged["risk_reasons"] = df_merged.apply(format_reasons, axis=1)

    # Primary Reason for Table Views
    df_merged["primary_reason"] = df_merged["risk_reasons"].apply(
        lambda r: r[0] if len(r) > 0 else "Normal Work"
    )

    # Format JSON string for serialization
    df_merged["risk_reasons_json"] = df_merged["risk_reasons"].apply(
        lambda r: json.dumps(r)
    )

    return df_merged