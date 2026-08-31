import pandas as pd
import numpy as np
from src.cleaning import clean_dataframe, parse_amount, parse_date
from src.normalization import extract_strict_work_id, normalize_mp_name, normalize_state

def build_integrated_datasets(raw_dfs):
    """Builds unified works_master, expenditures, mp_allocation, and calamity datasets using fast vectorized processing."""
    cleaned = {key: clean_dataframe(df) for key, df in raw_dfs.items()}
    master_records = {}
    
    # 1. Process Recommended Datasets
    for house in ["LS", "RS"]:
        df = cleaned[(house, "recommended")]
        wid_col = "WORK"
        amt_col = [c for c in df.columns if "amount" in c.lower()][0]
        mp_col = [c for c in df.columns if "member" in c.lower() or "mp" in c.lower()][0]
        state_col = [c for c in df.columns if "state" in c.lower()][0]
        const_col = [c for c in df.columns if "constituency" in c.lower() or "elected" in c.lower()]
        const_col = const_col[0] if len(const_col) > 0 else None
        cat_col = [c for c in df.columns if "category" in c.lower()][0] if any("category" in c.lower() for c in df.columns) else "Work category"
        desc_col = [c for c in df.columns if "description" in c.lower()]
        desc_col = desc_col[0] if len(desc_col) > 0 else None
        date_col = "Recommended date"
        
        wids = df[wid_col].apply(extract_strict_work_id).values
        amounts = df[amt_col].apply(parse_amount).values
        dates = pd.to_datetime(df[date_col], errors='coerce').values
        mps = df[mp_col].apply(normalize_mp_name).values
        states = df[state_col].apply(normalize_state).values
        consts = df[const_col].values if const_col else [np.nan] * len(df)
        cats = df[cat_col].fillna("Normal/Others").astype(str).values
        descs = df[desc_col].fillna("").astype(str).values if desc_col else [""] * len(df)
        
        house_name = "Lok Sabha" if house == "LS" else "Rajya Sabha"
        
        for idx in range(len(df)):
            wid = wids[idx] or f"UNASSIGNED_{house}_REC_{idx+1}"
            rec_amt = amounts[idx]
            rec_date = dates[idx]
            mp_name = mps[idx]
            state = states[idx]
            const = consts[idx]
            cat = cats[idx]
            desc = descs[idx]
            
            if wid not in master_records:
                master_records[wid] = {
                    "work_id": wid,
                    "parliament_house": house_name,
                    "mp_name": mp_name,
                    "state": state,
                    "constituency": const if house == "LS" else np.nan,
                    "elected_nominated": const if house == "RS" else np.nan,
                    "work_category": cat,
                    "work_description": desc,
                    "recommended_amount": rec_amt,
                    "recommended_date": pd.to_datetime(rec_date),
                    "sanctioned_amount": np.nan,
                    "sanction_date": pd.NaT,
                    "completion_amount": np.nan,
                    "completion_date": pd.NaT,
                    "work_status_raw": np.nan,
                    "has_recommended": True,
                    "has_sanctioned": False,
                    "has_expenditure": False,
                    "has_completed": False
                }
            else:
                master_records[wid]["recommended_amount"] = rec_amt
                master_records[wid]["recommended_date"] = pd.to_datetime(rec_date)
                master_records[wid]["has_recommended"] = True

    # 2. Process Sanctioned Datasets
    for house in ["LS", "RS"]:
        df = cleaned[(house, "sanctioned")]
        wid_col = "Work"
        amt_col = [c for c in df.columns if "sanction amount" in c.lower() or "amount" in c.lower()][0]
        mp_col = [c for c in df.columns if "member" in c.lower() or "mp" in c.lower()][0]
        state_col = [c for c in df.columns if "state" in c.lower()][0]
        const_col = [c for c in df.columns if "constituency" in c.lower() or "elected" in c.lower()]
        const_col = const_col[0] if len(const_col) > 0 else None
        cat_col = [c for c in df.columns if "category" in c.lower()]
        cat_col = cat_col[0] if len(cat_col) > 0 else None
        desc_col = [c for c in df.columns if "description" in c.lower()]
        desc_col = desc_col[0] if len(desc_col) > 0 else None
        date_col = "Sanction Date"
        status_col = "Work Status" if "Work Status" in df.columns else None
        
        wids = df[wid_col].apply(extract_strict_work_id).values
        amounts = df[amt_col].apply(parse_amount).values
        dates = pd.to_datetime(df[date_col], errors='coerce').values
        rec_dates = pd.to_datetime(df["Recommended date"], errors='coerce').values if "Recommended date" in df.columns else [pd.NaT] * len(df)
        mps = df[mp_col].apply(normalize_mp_name).values
        states = df[state_col].apply(normalize_state).values
        consts = df[const_col].values if const_col else [np.nan] * len(df)
        cats = df[cat_col].fillna("Normal/Others").astype(str).values if cat_col else ["Normal/Others"] * len(df)
        descs = df[desc_col].fillna("").astype(str).values if desc_col else [""] * len(df)
        statuses = df[status_col].fillna("Sanctioned").astype(str).values if status_col else ["Sanctioned"] * len(df)
        
        house_name = "Lok Sabha" if house == "LS" else "Rajya Sabha"
        
        for idx in range(len(df)):
            wid = wids[idx] or f"UNASSIGNED_{house}_SANC_{idx+1}"
            sanc_amt = amounts[idx]
            sanc_date = dates[idx]
            rec_date = rec_dates[idx]
            mp_name = mps[idx]
            state = states[idx]
            const = consts[idx]
            cat = cats[idx]
            desc = descs[idx]
            status_raw = statuses[idx]
            
            if wid not in master_records:
                master_records[wid] = {
                    "work_id": wid,
                    "parliament_house": house_name,
                    "mp_name": mp_name,
                    "state": state,
                    "constituency": const if house == "LS" else np.nan,
                    "elected_nominated": const if house == "RS" else np.nan,
                    "work_category": cat,
                    "work_description": desc,
                    "recommended_amount": np.nan,
                    "recommended_date": pd.to_datetime(rec_date),
                    "sanctioned_amount": sanc_amt,
                    "sanction_date": pd.to_datetime(sanc_date),
                    "completion_amount": np.nan,
                    "completion_date": pd.NaT,
                    "work_status_raw": status_raw,
                    "has_recommended": pd.notna(rec_date),
                    "has_sanctioned": True,
                    "has_expenditure": False,
                    "has_completed": False
                }
            else:
                master_records[wid]["sanctioned_amount"] = sanc_amt
                master_records[wid]["sanction_date"] = pd.to_datetime(sanc_date)
                master_records[wid]["work_status_raw"] = status_raw
                master_records[wid]["has_sanctioned"] = True

    # 3. Process Completed Datasets
    for house in ["LS", "RS"]:
        df = cleaned[(house, "completed")]
        wid_col = "Work"
        amt_col = [c for c in df.columns if "disbursed" in c.lower() or "amount" in c.lower()][0]
        date_col = "Completion Date"
        mp_col = [c for c in df.columns if "member" in c.lower() or "mp" in c.lower()][0]
        state_col = [c for c in df.columns if "state" in c.lower()][0]
        const_col = [c for c in df.columns if "constituency" in c.lower() or "elected" in c.lower()]
        const_col = const_col[0] if len(const_col) > 0 else None
        cat_col = [c for c in df.columns if "category" in c.lower()]
        cat_col = cat_col[0] if len(cat_col) > 0 else None
        desc_col = [c for c in df.columns if "description" in c.lower()]
        desc_col = desc_col[0] if len(desc_col) > 0 else None
        
        wids = df[wid_col].apply(extract_strict_work_id).values
        amounts = df[amt_col].apply(parse_amount).values
        dates = pd.to_datetime(df[date_col], errors='coerce').values
        mps = df[mp_col].apply(normalize_mp_name).values
        states = df[state_col].apply(normalize_state).values
        consts = df[const_col].values if const_col else [np.nan] * len(df)
        cats = df[cat_col].fillna("Normal/Others").astype(str).values if cat_col else ["Normal/Others"] * len(df)
        descs = df[desc_col].fillna("").astype(str).values if desc_col else [""] * len(df)
        
        house_name = "Lok Sabha" if house == "LS" else "Rajya Sabha"
        
        for idx in range(len(df)):
            wid = wids[idx] or f"UNASSIGNED_{house}_COMP_{idx+1}"
            comp_amt = amounts[idx]
            comp_date = dates[idx]
            
            if wid in master_records:
                master_records[wid]["completion_amount"] = comp_amt
                master_records[wid]["completion_date"] = pd.to_datetime(comp_date)
                master_records[wid]["has_completed"] = True
            else:
                master_records[wid] = {
                    "work_id": wid,
                    "parliament_house": house_name,
                    "mp_name": mps[idx],
                    "state": states[idx],
                    "constituency": consts[idx] if house == "LS" else np.nan,
                    "elected_nominated": consts[idx] if house == "RS" else np.nan,
                    "work_category": cats[idx],
                    "work_description": descs[idx],
                    "recommended_amount": np.nan,
                    "recommended_date": pd.NaT,
                    "sanctioned_amount": np.nan,
                    "sanction_date": pd.NaT,
                    "completion_amount": comp_amt,
                    "completion_date": pd.to_datetime(comp_date),
                    "work_status_raw": "Work Completed",
                    "has_recommended": False,
                    "has_sanctioned": False,
                    "has_expenditure": False,
                    "has_completed": True
                }

    # 4. Process Expenditures Ledger
    expenditures_list = []
    for house in ["LS", "RS"]:
        df = cleaned[(house, "expenditure")]
        wid_col = "Work ID"
        amt_col = [c for c in df.columns if "disbursed" in c.lower() or "amount" in c.lower()][0]
        date_col = "Expenditure Date"
        vendor_col = "Vendor Name"
        status_col = "Payment Status"
        mp_col = [c for c in df.columns if "member" in c.lower() or "mp" in c.lower()][0]
        state_col = [c for c in df.columns if "state" in c.lower()][0]
        const_col = [c for c in df.columns if "constituency" in c.lower() or "elected" in c.lower()]
        const_col = const_col[0] if len(const_col) > 0 else None
        
        wids = df[wid_col].apply(extract_strict_work_id).values
        amounts = df[amt_col].apply(parse_amount).values
        dates = pd.to_datetime(df[date_col], errors='coerce').values
        vendors = df[vendor_col].fillna("Unknown Vendor").astype(str).str.strip().values
        statuses = df[status_col].fillna("Completed").astype(str).str.strip().values
        mps = df[mp_col].apply(normalize_mp_name).values
        states = df[state_col].apply(normalize_state).values
        consts = df[const_col].values if const_col else [np.nan] * len(df)
        
        house_name = "Lok Sabha" if house == "LS" else "Rajya Sabha"
        
        for idx in range(len(df)):
            wid = wids[idx] or f"UNASSIGNED_{house}_EXP_{idx+1}"
            exp_amt = amounts[idx]
            exp_date = dates[idx]
            
            expenditures_list.append({
                "expenditure_id": f"EXP_{house}_{idx+1}",
                "work_id": wid,
                "parliament_house": house_name,
                "expenditure_date": pd.to_datetime(exp_date),
                "vendor_name": vendors[idx],
                "payment_status": statuses[idx],
                "amount": exp_amt
            })
            
            if wid in master_records:
                master_records[wid]["has_expenditure"] = True
            else:
                master_records[wid] = {
                    "work_id": wid,
                    "parliament_house": house_name,
                    "mp_name": mps[idx],
                    "state": states[idx],
                    "constituency": consts[idx] if house == "LS" else np.nan,
                    "elected_nominated": consts[idx] if house == "RS" else np.nan,
                    "work_category": "Normal/Others",
                    "work_description": "",
                    "recommended_amount": np.nan,
                    "recommended_date": pd.NaT,
                    "sanctioned_amount": np.nan,
                    "sanction_date": pd.NaT,
                    "completion_amount": np.nan,
                    "completion_date": pd.NaT,
                    "work_status_raw": "In Progress",
                    "has_recommended": False,
                    "has_sanctioned": False,
                    "has_expenditure": True,
                    "has_completed": False
                }

    works_master_df = pd.DataFrame(list(master_records.values()))
    works_master_df["is_unmatched_work"] = works_master_df["work_id"].astype(str).str.startswith("UNASSIGNED_")

    def determine_lifecycle(row):
        # Completion is the terminal stage; expenditure alone does not mean complete.
        if row["has_sanctioned"] and row["has_completed"]:
            return "Sanctioned & Completed"
        elif row["has_sanctioned"] and row["has_expenditure"]:
            return "Sanctioned & In Progress"
        elif row["has_sanctioned"]:
            return "Sanctioned (Pending Disbursal)"
        elif row["has_recommended"]:
            return "Recommended (Pending Sanction)"
        else:
            return "Lifecycle Data Gap"

    works_master_df["lifecycle_status"] = works_master_df.apply(determine_lifecycle, axis=1)
    
    expenditures_df = pd.DataFrame(expenditures_list)
    
    # Process MP Allocations
    allocations_list = []
    for house in ["LS", "RS"]:
        df = cleaned[(house, "allocation")]
        mp_col = [c for c in df.columns if "member" in c.lower() or "mp" in c.lower()][0]
        state_col = [c for c in df.columns if "state" in c.lower()][0]
        const_col = [c for c in df.columns if "constituency" in c.lower() or "elected" in c.lower()]
        const_col = const_col[0] if len(const_col) > 0 else None
        amt_col = [c for c in df.columns if "amount" in c.lower()][0]
        
        mps = df[mp_col].apply(normalize_mp_name).values
        states = df[state_col].apply(normalize_state).values
        consts = df[const_col].values if const_col else [np.nan] * len(df)
        amounts = df[amt_col].apply(parse_amount).values
        house_name = "Lok Sabha" if house == "LS" else "Rajya Sabha"
        
        for idx in range(len(df)):
            allocations_list.append({
                "mp_id": f"MP_{house}_{idx+1}",
                "parliament_house": house_name,
                "mp_name": mps[idx],
                "state": states[idx],
                "constituency": consts[idx] if house == "LS" else np.nan,
                "elected_nominated": consts[idx] if house == "RS" else np.nan,
                "allocated_amount": amounts[idx]
            })
    mp_allocation_df = pd.DataFrame(allocations_list)

    # Process Calamity Consents
    calamity_list = []
    for house in ["LS", "RS"]:
        df = cleaned[(house, "calamity")]
        mp_col = [c for c in df.columns if "member" in c.lower() or "mp" in c.lower()][0]
        type_col = "Calamity Type" if "Calamity Type" in df.columns else df.columns[1]
        name_col = "Calamity Name" if "Calamity Name" in df.columns else df.columns[2]
        date_col = "Date of Consent" if "Date of Consent" in df.columns else df.columns[4]
        amt_col = [c for c in df.columns if "amount" in c.lower() or "consent" in c.lower()][-1]
        
        mps = df[mp_col].apply(normalize_mp_name).values
        types = df[type_col].astype(str).values
        names = df[name_col].astype(str).values
        dates = pd.to_datetime(df[date_col], errors='coerce').values
        amounts = df[amt_col].apply(parse_amount).values
        house_name = "Lok Sabha" if house == "LS" else "Rajya Sabha"
        
        for idx in range(len(df)):
            calamity_list.append({
                "calamity_id": f"CAL_{house}_{idx+1}",
                "parliament_house": house_name,
                "mp_name": mps[idx],
                "calamity_type": types[idx],
                "calamity_name": names[idx],
                "consent_date": pd.to_datetime(dates[idx]),
                "consent_amount": amounts[idx]
            })
    calamity_df = pd.DataFrame(calamity_list)
    
    return works_master_df, expenditures_df, mp_allocation_df, calamity_df
