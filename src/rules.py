import pandas as pd
import numpy as np

def evaluate_audit_rules(df_feat):
    """Evaluates 10 deterministic audit rules with monetary tolerance and generates human-readable explanations."""
    rule_results = []
    
    # House-specific duration thresholds and payment-count threshold.
    # Explicit NaN handling avoids relying on Python's truthiness for NaN.
    def _percentile_or_default(series, q, default):
        value = pd.to_numeric(series, errors='coerce').quantile(q)
        return float(value) if pd.notnull(value) else float(default)

    ls_sanc_p95 = _percentile_or_default(
        df_feat.loc[df_feat['parliament_house'] == 'Lok Sabha', 'recommendation_to_sanction_days'],
        0.95, 341.0
    )
    rs_sanc_p95 = _percentile_or_default(
        df_feat.loc[df_feat['parliament_house'] == 'Rajya Sabha', 'recommendation_to_sanction_days'],
        0.95, 407.0
    )

    ls_comp_p95 = _percentile_or_default(
        df_feat.loc[df_feat['parliament_house'] == 'Lok Sabha', 'sanction_to_completion_days'],
        0.95, 547.0
    )
    rs_comp_p95 = _percentile_or_default(
        df_feat.loc[df_feat['parliament_house'] == 'Rajya Sabha', 'sanction_to_completion_days'],
        0.95, 703.0
    )

    p_count_p97 = _percentile_or_default(
        df_feat.loc[df_feat['payment_count'] > 0, 'payment_count'],
        0.97, 10.0
    )

    for idx, row in df_feat.iterrows():
        reasons = []
        score = 0
        
        # Rule A: Potential Duplicate Transaction Records
        # Identical ledger attributes are a review signal, not proof of a
        # duplicate real-world payment.
        duplicate_records = row.get(
            'duplicate_transaction_record_count',
            row.get('duplicate_payment_count', 0)
        )
        if pd.notnull(duplicate_records) and duplicate_records > 0:
            score += 25
            dup_groups = row.get('potential_duplicate_group_count', 0)
            dup_amount = row.get('potential_duplicate_amount', 0.0)
            dup_groups = 0 if pd.isnull(dup_groups) else dup_groups
            dup_amount = 0.0 if pd.isnull(dup_amount) else dup_amount
            reason = (
                "Potential Duplicate Transaction Records: "
                f"{int(duplicate_records)} excess ledger record(s) across "
                f"{int(dup_groups)} identical attribute group(s)"
            )
            if float(dup_amount) > 0:
                reason += f", representing ₹{float(dup_amount):,.2f} in excess-record amount"
            reasons.append(reason)

        # Rule B: Expenditure Exceeds Sanction (with 1.0 Rupee tolerance)
        if (
            pd.notnull(row['sanctioned_amount'])
            and pd.notnull(row['total_expenditure'])
            and row['sanctioned_amount'] > 0
            and row['total_expenditure'] > (row['sanctioned_amount'] + 1.0)
        ):
            diff = row['total_expenditure'] - row['sanctioned_amount']
            score += 40
            reasons.append(f"Critical Financial Control: Total expenditure (₹{row['total_expenditure']:,.2f}) exceeds sanction (₹{row['sanctioned_amount']:,.2f}) by ₹{diff:,.2f}")
            
        # Rule C: Completion Amount Exceeds Sanction (with 1.0 Rupee tolerance)
        if (
            pd.notnull(row['sanctioned_amount'])
            and pd.notnull(row['completion_amount'])
            and row['sanctioned_amount'] > 0
            and row['completion_amount'] > (row['sanctioned_amount'] + 1.0)
        ):
            diff = row['completion_amount'] - row['sanctioned_amount']
            score += 30
            reasons.append(f"Financial Control Anomaly: Completion amount (₹{row['completion_amount']:,.2f}) exceeds sanction (₹{row['sanctioned_amount']:,.2f}) by ₹{diff:,.2f}")
            
        # Rule D: Impossible Chronology
        rec_sanc = row['recommendation_to_sanction_days']
        sanc_exp = row['sanction_to_first_expenditure_days']
        sanc_comp = row['sanction_to_completion_days']
        
        if pd.notnull(rec_sanc) and rec_sanc < 0:
            score += 30
            reasons.append("Impossible Chronology: Sanction date is earlier than Recommendation date")
        if pd.notnull(sanc_exp) and sanc_exp < 0:
            score += 30
            reasons.append("Impossible Chronology: First Expenditure date is earlier than Sanction date")
        if pd.notnull(sanc_comp) and sanc_comp < 0:
            score += 30
            reasons.append("Impossible Chronology: Completion date is earlier than Sanction date")

        # Rule E: Unusually Long Approval Cycle
        p95_sanc = ls_sanc_p95 if row['parliament_house'] == 'Lok Sabha' else rs_sanc_p95
        if pd.notnull(rec_sanc) and rec_sanc > p95_sanc:
            score += 15
            reasons.append(f"Process Inefficiency: Recommendation-to-Sanction duration ({int(rec_sanc)} days) exceeds 95th percentile ({int(p95_sanc)} days)")

        # Rule F: Unusually Long Completion Cycle
        p95_comp = ls_comp_p95 if row['parliament_house'] == 'Lok Sabha' else rs_comp_p95
        if pd.notnull(sanc_comp) and sanc_comp > p95_comp:
            score += 15
            reasons.append(f"Process Inefficiency: Sanction-to-Completion duration ({int(sanc_comp)} days) exceeds 95th percentile ({int(p95_comp)} days)")

        # Rule G: Unusual Payment Fragmentation
        if row['payment_count'] > p_count_p97:
            score += 20
            reasons.append(f"Unusual Payment Fragmentation: Payment count ({row['payment_count']} disbursements) exceeds 97th percentile threshold ({int(p_count_p97)})")

        # Rule H: Vendor Concentration Risk
        if row['payment_count'] >= 3 and row['vendor_concentration_score'] >= 0.80:
            pct = int(row['vendor_concentration_score'] * 100)
            score += 20
            reasons.append(f"Vendor Concentration Risk: Top vendor captures {pct}% of total work expenditure across {row['payment_count']} payments")

        # Rule I: Amount Outlier (Peer Group Robust Z-Score > 3.0)
        # Evaluate both available amount signals rather than hiding expenditure
        # evidence when sanction is also an outlier.
        sanc_z = row.get('sanc_robust_zscore', np.nan)
        exp_z = row.get('exp_robust_zscore', np.nan)

        outlier_messages = []
        if pd.notnull(sanc_z) and sanc_z > 3.0:
            outlier_messages.append(
                f"sanctioned amount (₹{row['sanctioned_amount']:,.2f}) "
                f"Robust Z = {sanc_z:.1f}"
            )
        if pd.notnull(exp_z) and exp_z > 3.0:
            outlier_messages.append(
                f"total expenditure (₹{row['total_expenditure']:,.2f}) "
                f"Robust Z = {exp_z:.1f}"
            )

        if outlier_messages:
            score += 20
            reasons.append(
                "Amount Outlier: " + "; ".join(outlier_messages) +
                ". Values are unusually high relative to the defined peer group."
            )

        # Rule J: Dormant Sanctioned Work
        if row['is_stalled_work'] == 1:
            score += 15
            reasons.append("Dormant Sanctioned Work: Work sanctioned over 180 days ago with zero expenditure and zero completion")

        rule_results.append({
            "work_id": row["work_id"],
            "rule_score": min(score, 100),
            "rule_reasons": reasons
        })
        
    return pd.DataFrame(rule_results)
