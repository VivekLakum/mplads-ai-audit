import pandas as pd
import numpy as np

def calculate_robust_zscore(series, group_series, valid_mask=None, min_group_size=10):
    """Calculate robust peer Z-scores only for valid, sufficiently large peer groups."""
    values = pd.to_numeric(series, errors="coerce")
    groups = group_series.astype(str)
    if valid_mask is None:
        valid_mask = values.notna()
    valid_mask = pd.Series(valid_mask, index=values.index).fillna(False).astype(bool)
    valid = pd.DataFrame({"val": values.where(valid_mask), "group": groups})
    medians = valid.groupby("group")["val"].transform("median")
    abs_dev = (valid["val"] - medians).abs()
    mads = abs_dev.groupby(valid["group"]).transform("median")
    valid_counts = valid.groupby("group")["val"].transform("count")
    mad_floor = np.maximum(0.10 * medians, 10000.0)
    effective_mads = np.maximum(mads, mad_floor)
    robust_z = (values - medians) / effective_mads
    eligible = valid_mask & (valid_counts >= min_group_size) & medians.notna() & effective_mads.notna()
    return medians.where(eligible), mads.where(eligible), effective_mads.where(eligible), robust_z.where(eligible), valid_counts

def build_work_features(works_master_df, expenditures_df):
    """Engineers work-level financial, lifecycle, transaction, and peer-group statistical features."""
    df = works_master_df.copy()
    
    # 1. Transaction-level Aggregations from Expenditures Ledger
    if not expenditures_df.empty:
        exp_agg = expenditures_df.groupby('work_id').agg(
            total_expenditure=('amount', 'sum'),
            payment_count=('expenditure_id', 'count'),
            vendor_count=('vendor_name', 'nunique'),
            first_payment_date=('expenditure_date', 'min'),
            last_payment_date=('expenditure_date', 'max'),
            max_single_payment=('amount', 'max')
        ).reset_index()
        
        # Vendor Concentration (top vendor payment ratio)
        top_vendor_exp = expenditures_df.groupby(['work_id', 'vendor_name'])['amount'].sum().reset_index()
        top_vendor_max = top_vendor_exp.groupby('work_id')['amount'].max().reset_index().rename(columns={'amount': 'top_vendor_amount'})
        exp_agg = pd.merge(exp_agg, top_vendor_max, on='work_id', how='left')
        exp_agg['vendor_concentration_score'] = np.where(
            exp_agg['total_expenditure'] > 0,
            exp_agg['top_vendor_amount'] / exp_agg['total_expenditure'],
            0.0
        )
        exp_agg['largest_payment_ratio'] = np.where(
            exp_agg['total_expenditure'] > 0,
            exp_agg['max_single_payment'] / exp_agg['total_expenditure'],
            0.0
        )
        
        # Payment Frequency Days
        days_span = (pd.to_datetime(exp_agg['last_payment_date']) - pd.to_datetime(exp_agg['first_payment_date'])).dt.days
        exp_agg['payment_frequency_days'] = np.where(
            exp_agg['payment_count'] > 1,
            days_span / (exp_agg['payment_count'] - 1),
            0.0
        )
        
        # Potential duplicate transaction-record detection.
        # Identical ledger rows are a review signal, not proof of duplicate payment.
        dup_cols = ['work_id', 'expenditure_date', 'vendor_name', 'payment_status', 'amount']
        dup_groups = (
            expenditures_df
            .groupby(dup_cols, dropna=False)
            .agg(
                duplicate_group_size=('expenditure_id', 'count'),
                duplicate_group_unit_amount=('amount', 'first')
            )
            .reset_index()
        )
        dup_groups = dup_groups[dup_groups['duplicate_group_size'] > 1].copy()

        if not dup_groups.empty:
            dup_groups['excess_records'] = dup_groups['duplicate_group_size'] - 1
            dup_groups['excess_amount'] = (
                dup_groups['excess_records'] * dup_groups['duplicate_group_unit_amount']
            )
            dup_df = (
                dup_groups
                .groupby('work_id')
                .agg(
                    potential_duplicate_group_count=('duplicate_group_size', 'size'),
                    potential_duplicate_excess_count=('excess_records', 'sum'),
                    potential_duplicate_amount=('excess_amount', 'sum')
                )
                .reset_index()
            )
        else:
            dup_df = pd.DataFrame(columns=[
                'work_id',
                'potential_duplicate_group_count',
                'potential_duplicate_excess_count',
                'potential_duplicate_amount'
            ])

        exp_agg = pd.merge(exp_agg, dup_df, on='work_id', how='left')
        exp_agg['potential_duplicate_group_count'] = exp_agg['potential_duplicate_group_count'].fillna(0).astype(int)
        exp_agg['potential_duplicate_excess_count'] = exp_agg['potential_duplicate_excess_count'].fillna(0).astype(int)
        exp_agg['potential_duplicate_amount'] = exp_agg['potential_duplicate_amount'].fillna(0.0)

        # Explicit terminology; retain the old column as a compatibility alias.
        exp_agg['duplicate_transaction_record_count'] = exp_agg['potential_duplicate_excess_count']
        exp_agg['duplicate_payment_count'] = exp_agg['duplicate_transaction_record_count']
        
        df = pd.merge(df, exp_agg, on='work_id', how='left')
    
    # Fill missing transaction metrics
    df['total_expenditure'] = df['total_expenditure'].fillna(0.0)
    df['payment_count'] = df['payment_count'].fillna(0).astype(int)
    df['vendor_count'] = df['vendor_count'].fillna(0).astype(int)
    df['vendor_concentration_score'] = df['vendor_concentration_score'].fillna(0.0)
    df['largest_payment_ratio'] = df['largest_payment_ratio'].fillna(0.0)
    df['payment_frequency_days'] = df['payment_frequency_days'].fillna(0.0)
    df['duplicate_payment_count'] = df['duplicate_payment_count'].fillna(0).astype(int)
    df['duplicate_transaction_record_count'] = df.get(
        'duplicate_transaction_record_count',
        pd.Series(0, index=df.index)
    ).fillna(0).astype(int)
    df['potential_duplicate_group_count'] = df.get(
        'potential_duplicate_group_count',
        pd.Series(0, index=df.index)
    ).fillna(0).astype(int)
    df['potential_duplicate_amount'] = df.get(
        'potential_duplicate_amount',
        pd.Series(0.0, index=df.index)
    ).fillna(0.0)
    df['potential_duplicate_amount_ratio'] = np.where(
        df['total_expenditure'] > 0,
        df['potential_duplicate_amount'] / df['total_expenditure'],
        0.0
    ).clip(0.0, 1.0)
    
    # 2. Lifecycle Durations (in days)
    rec_d = pd.to_datetime(df['recommended_date'], errors='coerce')
    sanc_d = pd.to_datetime(df['sanction_date'], errors='coerce')
    comp_d = pd.to_datetime(df['completion_date'], errors='coerce')
    first_exp_d = pd.to_datetime(df['first_payment_date'], errors='coerce') if 'first_payment_date' in df.columns else pd.Series(pd.NaT, index=df.index)
    
    df['recommendation_to_sanction_days'] = (sanc_d - rec_d).dt.days
    df['sanction_to_first_expenditure_days'] = (first_exp_d - sanc_d).dt.days
    df['sanction_to_completion_days'] = (comp_d - sanc_d).dt.days
    
    # Stalled Work Indicator (sanctioned > 180 days ago with zero expenditure and zero completion)
    cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=180)
    df['is_stalled_work'] = ((sanc_d < cutoff_date) & (df['total_expenditure'] == 0.0) & (df['completion_amount'] == 0.0)).astype(int)
    
    # Lifecycle Completeness Score (0.0 to 1.0)
    df['lifecycle_completeness_score'] = (
        df['has_recommended'].astype(int) * 0.25 +
        df['has_sanctioned'].astype(int) * 0.25 +
        df['has_expenditure'].astype(int) * 0.25 +
        df['has_completed'].astype(int) * 0.25
    )
    
    # 3. Financial Metrics & Overruns. Preserve missingness so an unavailable
    # sanction/completion amount cannot create a false overrun against zero.
    df['sanctioned_amount_available'] = df['has_sanctioned'].astype(bool) & pd.to_numeric(df['sanctioned_amount'], errors='coerce').notna()
    df['completion_amount_available'] = df['has_completed'].astype(bool) & pd.to_numeric(df['completion_amount'], errors='coerce').notna()
    df['recommended_amount_available'] = df['has_recommended'].astype(bool) & pd.to_numeric(df['recommended_amount'], errors='coerce').notna()
    df['sanctioned_amount'] = pd.to_numeric(df['sanctioned_amount'], errors='coerce')
    df['completion_amount'] = pd.to_numeric(df['completion_amount'], errors='coerce')
    df['recommended_amount'] = pd.to_numeric(df['recommended_amount'], errors='coerce')
    tolerance = 1.0
    valid_sanction = df['sanctioned_amount_available'] & df['sanctioned_amount'].notna()
    valid_completion = df['completion_amount_available'] & df['completion_amount'].notna()
    df['expenditure_overrun_amount'] = np.where(valid_sanction, np.maximum(0.0, df['total_expenditure'] - df['sanctioned_amount'] - tolerance), np.nan)
    df['completion_overrun_amount'] = np.where(valid_sanction & valid_completion, np.maximum(0.0, df['completion_amount'] - df['sanctioned_amount'] - tolerance), np.nan)
    df['is_sanction_overrun'] = (df['expenditure_overrun_amount'].fillna(0.0) > tolerance) | (df['completion_overrun_amount'].fillna(0.0) > tolerance)
    df['expenditure_to_sanction_ratio'] = np.where(valid_sanction & (df['sanctioned_amount'] > 0), df['total_expenditure'] / df['sanctioned_amount'], np.nan)
    df['completion_to_sanction_ratio'] = np.where(valid_sanction & valid_completion & (df['sanctioned_amount'] > 0), df['completion_amount'] / df['sanctioned_amount'], np.nan)

    # Descriptive only: completion and expenditure may come from different
    # reporting snapshots. This field must not be treated as a fraud rule.
    completion_exp_available = (
        valid_completion
        & df['has_expenditure'].astype(bool)
        & df['total_expenditure'].notna()
    )
    df['completion_minus_expenditure'] = np.where(
        completion_exp_available,
        df['completion_amount'] - df['total_expenditure'],
        np.nan
    )
    df['completion_expenditure_comparison_available'] = completion_exp_available.astype(bool)
    
    # 4. Peer-Group Robust Statistical Z-Scores
    df['peer_group'] = (df['parliament_house'].fillna('Unknown').astype(str) + "_" +
                        df['state'].fillna('Unknown').astype(str) + "_" +
                        df['work_category'].fillna('Unknown').astype(str))
    df['peer_group_size'] = df['peer_group'].map(df['peer_group'].value_counts()).fillna(0).astype(int)
    unmatched = df.get('is_unmatched_work', pd.Series(False, index=df.index)).fillna(False).astype(bool)
    sanc_valid = (~unmatched) & df['sanctioned_amount_available'] & df['sanctioned_amount'].notna()
    exp_valid = (~unmatched) & df['has_expenditure'].astype(bool) & df['total_expenditure'].notna()

    s_med, s_mad, s_eff_mad, s_z, s_valid_count = calculate_robust_zscore(df['sanctioned_amount'], df['peer_group'], sanc_valid, min_group_size=10)
    df['peer_sanc_median'] = s_med
    df['peer_sanc_mad'] = s_mad
    df['peer_sanc_effective_mad'] = s_eff_mad
    df['sanc_robust_zscore'] = s_z
    df['peer_sanc_valid_count'] = s_valid_count

    e_med, e_mad, e_eff_mad, e_z, e_valid_count = calculate_robust_zscore(df['total_expenditure'], df['peer_group'], exp_valid, min_group_size=10)
    df['peer_exp_median'] = e_med
    df['peer_exp_mad'] = e_mad
    df['peer_exp_effective_mad'] = e_eff_mad
    df['exp_robust_zscore'] = e_z
    df['peer_exp_valid_count'] = e_valid_count
    df['statistical_anomaly_available'] = df['sanc_robust_zscore'].notna() | df['exp_robust_zscore'].notna()

    return df
