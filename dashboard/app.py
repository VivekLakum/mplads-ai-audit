import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as io
import json
import os
import sys

# Set Streamlit Page Config as VERY FIRST Streamlit command
st.set_page_config(
    page_title="MPLADS AI Anomaly & Fraud-Risk Detection System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROCESSED_DIR = os.path.join(BASE_DIR, "data", "processed")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")

@st.cache_data
def load_app_data():
    anomaly_df = pd.read_csv(os.path.join(OUTPUTS_DIR, "anomaly_results.csv"), low_memory=False)
    expenditures_df = pd.read_csv(os.path.join(PROCESSED_DIR, "expenditures.csv"), low_memory=False)
    allocation_df = pd.read_csv(os.path.join(PROCESSED_DIR, "mp_allocation.csv"), low_memory=False)
    calamity_df = pd.read_csv(os.path.join(PROCESSED_DIR, "calamity.csv"), low_memory=False)
    
    # Parse dates
    anomaly_df['recommended_date'] = pd.to_datetime(anomaly_df['recommended_date'], errors='coerce')
    anomaly_df['sanction_date'] = pd.to_datetime(anomaly_df['sanction_date'], errors='coerce')
    anomaly_df['completion_date'] = pd.to_datetime(anomaly_df['completion_date'], errors='coerce')
    expenditures_df['expenditure_date'] = pd.to_datetime(expenditures_df['expenditure_date'], errors='coerce')
    
    # Parse JSON risk reasons
    def parse_reasons(val):
        if pd.isna(val):
            return []
        try:
            return json.loads(val)
        except:
            return [str(val)]
            
    if 'risk_reasons_json' in anomaly_df.columns:
        anomaly_df['risk_reasons_list'] = anomaly_df['risk_reasons_json'].apply(parse_reasons)
    else:
        anomaly_df['risk_reasons_list'] = anomaly_df['primary_reason'].apply(lambda x: [x])
        
    return anomaly_df, expenditures_df, allocation_df, calamity_df

# Custom Styling (Dark Mode, Vibrant Color Tokens, Glassmorphism Cards)
st.markdown("""
<style>
    /* Dark Theme Colors */
    .stApp {
        background-color: #0e1117;
        color: #e6edf3;
    }
    .css-1d37w22, .css-6qob1r {
        background-color: #161b22;
    }
    
    /* Header & Title Banner */
    .banner-container {
        background: linear-gradient(135deg, #1e1b4b 0%, #311b92 50%, #0f172a 100%);
        border: 1px solid #4338ca;
        border-radius: 12px;
        padding: 24px 32px;
        margin-bottom: 24px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
    }
    .banner-title {
        font-size: 28px;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: -0.5px;
        margin-bottom: 4px;
    }
    .banner-subtitle {
        font-size: 14px;
        color: #c7d2fe;
        font-weight: 400;
    }
    
    /* Metric Cards */
    .metric-card {
        background: #161b22;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        transition: transform 0.2s, border-color 0.2s;
    }
    .metric-card:hover {
        transform: translateY(-2px);
        border-color: #6366f1;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 800;
        color: #f8fafc;
        margin-top: 4px;
    }
    .metric-label {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Risk Badges */
    .badge-critical {
        background-color: #7f1d1d;
        color: #fca5a5;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
    }
    .badge-high {
        background-color: #7c2d12;
        color: #fdba74;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
    }
    .badge-review {
        background-color: #713f12;
        color: #fde047;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
    }
    .badge-normal {
        background-color: #064e3b;
        color: #6ee7b7;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: 700;
        font-size: 12px;
    }
    
    /* Audit Explanation Box */
    .audit-box {
        background-color: #1e293b;
        border-left: 4px solid #6366f1;
        padding: 16px;
        border-radius: 0 8px 8px 0;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)

try:
    anomaly_df, expenditures_df, allocation_df, calamity_df = load_app_data()
except Exception as e:
    st.error(f"Error loading pipeline outputs: {e}. Please ensure `run_pipeline.py` has executed successfully.")
    st.stop()

# Sidebar Controls & Navigation
with st.sidebar:
    st.image("https://img.icons8.com/isometric/96/government.png", width=64)
    st.title("MPLADS AI Portal")
    st.caption("PS SIH26102 — Smart India Hackathon 2026")
    st.markdown("---")
    
    page = st.radio(
        "Navigation",
        [
            "1. Command Center",
            "2. Anomaly Explorer",
            "3. MP & State Analysis",
            "4. Lifecycle & Data Flow",
            "5. Investigation Deep-Dive",
            "6. Data Quality & Audit Log"
        ]
    )
    st.markdown("---")
    
    # Global House Filter
    house_filter = st.selectbox("Parliament Dimension", ["All", "Lok Sabha", "Rajya Sabha"])
    
    st.markdown("---")
    st.info("ℹ️ **Audit-Support Tool**: Flags represent potential anomalies or process inefficiencies requiring human verification.")

# Filter Data by House
if house_filter != "All":
    df_filtered = anomaly_df[anomaly_df['parliament_house'] == house_filter].copy()
    exp_filtered = expenditures_df[expenditures_df['parliament_house'] == house_filter].copy()
else:
    df_filtered = anomaly_df.copy()
    exp_filtered = expenditures_df.copy()

# ==============================================================================
# PAGE 1: COMMAND CENTER
# ==============================================================================
if page == "1. Command Center":
    st.markdown("""
    <div class="banner-container">
        <div class="banner-title">🛡️ MPLADS AI Command Center</div>
        <div class="banner-subtitle">Real-Time Anomaly, Fraud-Risk & Process Inefficiency Screening System for Hon'ble MPs' Development Funds</div>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Row
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    
    total_works = len(df_filtered)
    total_exp = expenditures_df[expenditures_df['work_id'].isin(df_filtered['work_id'])]['amount'].sum()
    total_sanc = df_filtered['sanctioned_amount'].sum()
    high_risk_cnt = len(df_filtered[df_filtered['risk_level'] == 'HIGH'])
    critical_cnt = len(df_filtered[df_filtered['risk_level'] == 'CRITICAL'])
    dup_cnt = df_filtered['duplicate_payment_count'].sum()
    
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Works</div><div class="metric-value">{total_works:,}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Expenditure</div><div class="metric-value">₹{total_exp/1e7:,.2f} Cr</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Total Sanctioned</div><div class="metric-value">₹{total_sanc/1e7:,.2f} Cr</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-label">High Risk Works</div><div class="metric-value" style="color:#fdba74;">{high_risk_cnt:,}</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Critical Works</div><div class="metric-value" style="color:#fca5a5;">{critical_cnt:,}</div></div>', unsafe_allow_html=True)
    with c6:
        st.markdown(f'<div class="metric-card"><div class="metric-label">Duplicate Payments</div><div class="metric-value" style="color:#fde047;">{dup_cnt:,}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    # Charts Row 1
    col_left, col_right = st.columns([1, 1])
    
    with col_left:
        st.subheader("📊 Risk Level Distribution")
        risk_counts = df_filtered['risk_level'].value_counts().reset_index()
        risk_counts.columns = ['Risk Level', 'Count']
        
        color_map = {
            "NORMAL": "#10b981",
            "REVIEW": "#f59e0b",
            "HIGH": "#f97316",
            "CRITICAL": "#ef4444"
        }
        
        fig_donut = px.pie(
            risk_counts, 
            names='Risk Level', 
            values='Count', 
            hole=0.55,
            color='Risk Level',
            color_discrete_map=color_map,
        )
        fig_donut.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5)
        )
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with col_right:
        st.subheader("🏛️ Expenditure Disbursal by Top 10 States")
        state_exp = df_filtered.groupby('state')['total_expenditure'].sum().reset_index()
        state_exp = state_exp.sort_values(by='total_expenditure', ascending=False).head(10)
        state_exp['total_exp_cr'] = state_exp['total_expenditure'] / 1e7
        
        fig_bar = px.bar(
            state_exp,
            x='total_exp_cr',
            y='state',
            orientation='h',
            labels={'total_exp_cr': 'Expenditure (₹ Crore)', 'state': 'State'},
            color='total_exp_cr',
            color_continuous_scale='Viridis'
        )
        fig_bar.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    # Charts Row 2
    c_bot1, c_bot2 = st.columns([1, 1])
    
    with c_bot1:
        st.subheader("🏷️ Works by Top 8 Development Categories")
        cat_counts = df_filtered['work_category'].value_counts().head(8).reset_index()
        cat_counts.columns = ['Category', 'Count']
        
        fig_cat = px.bar(
            cat_counts,
            x='Count',
            y='Category',
            orientation='h',
            color='Count',
            color_continuous_scale='Teal'
        )
        fig_cat.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0',
            yaxis=dict(autorange="reversed")
        )
        st.plotly_chart(fig_cat, use_container_width=True)
        
    with c_bot2:
        st.subheader("🔄 Lifecycle Stage Coverage Funnel")
        lifecycle_counts = df_filtered['lifecycle_status'].value_counts().reset_index()
        lifecycle_counts.columns = ['Lifecycle Status', 'Works']
        
        fig_funnel = px.funnel(
            lifecycle_counts,
            y='Lifecycle Status',
            x='Works',
            color='Lifecycle Status'
        )
        fig_funnel.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font_color='#e2e8f0'
        )
        st.plotly_chart(fig_funnel, use_container_width=True)

# ==============================================================================
# PAGE 2: ANOMALY EXPLORER
# ==============================================================================
elif page == "2. Anomaly Explorer":
    st.title("🔍 Anomaly & Fraud-Risk Explorer")
    st.caption("Interactive multi-dimensional filtering grid with explainable risk evidence.")
    
    # Filter Controls
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        risk_sel = st.multiselect("Filter by Risk Level", ["CRITICAL", "HIGH", "REVIEW", "NORMAL"], default=["CRITICAL", "HIGH"])
    with f2:
        state_list = ["All"] + sorted(list(df_filtered['state'].dropna().unique()))
        state_sel = st.selectbox("Filter by State", state_list)
    with f3:
        mp_list = ["All"] + sorted(list(df_filtered['mp_name'].dropna().unique()))
        mp_sel = st.selectbox("Filter by MP Name", mp_list)
    with f4:
        reason_list = ["All", "Duplicate Payment", "Sanction Overrun", "Long Duration", "Payment Fragmentation", "Vendor Concentration", "Amount Outlier", "Dormant Work"]
        reason_sel = st.selectbox("Filter by Anomaly Signal", reason_list)
        
    # Apply Filters
    df_exp_view = df_filtered.copy()
    if risk_sel:
        df_exp_view = df_exp_view[df_exp_view['risk_level'].isin(risk_sel)]
    if state_sel != "All":
        df_exp_view = df_exp_view[df_exp_view['state'] == state_sel]
    if mp_sel != "All":
        df_exp_view = df_exp_view[df_exp_view['mp_name'] == mp_sel]
    if reason_sel != "All":
        df_exp_view = df_exp_view[df_exp_view['primary_reason'].str.contains(reason_sel, case=False, na=False)]
        
    st.markdown(f"**Showing {len(df_exp_view):,} matching works**")
    
    display_cols = [
        'work_id', 'parliament_house', 'risk_score', 'risk_level', 
        'mp_name', 'state', 'work_category', 'sanctioned_amount', 
        'total_expenditure', 'primary_reason'
    ]
    
    st.dataframe(
        df_exp_view[display_cols].sort_values(by='risk_score', ascending=False),
        column_config={
            "work_id": "Work ID",
            "parliament_house": "House",
            "risk_score": st.column_config.NumberColumn("Risk Score", format="%.1f"),
            "risk_level": "Risk Level",
            "mp_name": "MP Name",
            "state": "State",
            "work_category": "Category",
            "sanctioned_amount": st.column_config.NumberColumn("Sanction (₹)", format="₹%,.2f"),
            "total_expenditure": st.column_config.NumberColumn("Expenditure (₹)", format="₹%,.2f"),
            "primary_reason": "Primary Audit Signal"
        },
        use_container_width=True,
        height=500
    )

# ==============================================================================
# PAGE 3: MP & STATE ANALYSIS
# ==============================================================================
elif page == "3. MP & State Analysis":
    st.title("👤 MP & State Utilization Analysis")
    st.caption("Audit-support analysis of MP development funds allocation, utilization, and risk indicators.")
    
    tab_mp, tab_state = st.tabs(["MP Development Profile", "State Performance"])
    
    with tab_mp:
        mp_selected = st.selectbox("Select MP Name to Audit", sorted(list(df_filtered['mp_name'].dropna().unique())))
        
        mp_works = df_filtered[df_filtered['mp_name'] == mp_selected]
        mp_alloc = allocation_df[allocation_df['mp_name'] == mp_selected]
        
        alloc_amt = mp_alloc['allocated_amount'].sum() if not mp_alloc.empty else 147000000.0
        total_sanc = mp_works['sanctioned_amount'].sum()
        total_exp = mp_works['total_expenditure'].sum()
        util_rate = (total_exp / alloc_amt) * 100.0 if alloc_amt > 0 else 0.0
        
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            st.metric("Allocated Limit", f"₹{alloc_amt/1e7:,.2f} Cr")
        with m2:
            st.metric("Sanctioned Amount", f"₹{total_sanc/1e7:,.2f} Cr")
        with m3:
            st.metric("Fund Expenditure", f"₹{total_exp/1e7:,.2f} Cr")
        with m4:
            st.metric("Fund Utilization Rate", f"{util_rate:.1f}%")
            
        st.subheader("Flagged Risk Signals for MP Works")
        mp_anomalies = mp_works[mp_works['risk_level'].isin(['HIGH', 'CRITICAL', 'REVIEW'])]
        if not mp_anomalies.empty:
            st.dataframe(
                mp_anomalies[['work_id', 'risk_score', 'risk_level', 'work_category', 'sanctioned_amount', 'total_expenditure', 'primary_reason']],
                use_container_width=True
            )
        else:
            st.success("No high or critical risk indicators detected for this MP.")

    with tab_state:
        st.subheader("State-Wise Risk Signal Summary")
        state_summary = df_filtered.groupby('state').agg(
            total_works=('work_id', 'count'),
            total_sanctioned=('sanctioned_amount', 'sum'),
            total_expenditure=('total_expenditure', 'sum'),
            high_critical_risk_works=('risk_level', lambda x: (x.isin(['HIGH', 'CRITICAL'])).sum())
        ).reset_index()
        
        st.dataframe(
            state_summary.sort_values(by='high_critical_risk_works', ascending=False),
            column_config={
                "state": "State",
                "total_works": "Total Works",
                "total_sanctioned": st.column_config.NumberColumn("Sanctioned (₹)", format="₹%,.2f"),
                "total_expenditure": st.column_config.NumberColumn("Expenditure (₹)", format="₹%,.2f"),
                "high_critical_risk_works": "High/Critical Risk Count"
            },
            use_container_width=True
        )

# ==============================================================================
# PAGE 4: LIFECYCLE & DATA FLOW
# ==============================================================================
elif page == "4. Lifecycle & Data Flow":
    st.title("🔄 Lifecycle Linkage & Data Gap Analysis")
    st.caption("Visualizing the 4-stage MPLADS workflow: Recommended → Sanctioned → Expenditure → Completed.")
    
    st.markdown("""
    > [!NOTE]  
    > **Data Gap vs Anomaly Distinction**: Works that exist in `Recommended` or `Expenditure` but lack a matching `Sanctioned` record in raw datasets are explicitly classified as **`Lifecycle Data Gap`**. They represent temporal dataset coverage limits, not fraudulent activity.
    """)
    
    l1, l2 = st.columns(2)
    with l1:
        st.subheader("Approval Cycle Duration (Days)")
        sanc_valid = df_filtered.dropna(subset=['recommendation_to_sanction_days'])
        fig_hist1 = px.histogram(
            sanc_valid,
            x='recommendation_to_sanction_days',
            nbins=30,
            labels={'recommendation_to_sanction_days': 'Recommendation to Sanction (Days)'},
            color_discrete_sequence=['#6366f1']
        )
        fig_hist1.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0')
        st.plotly_chart(fig_hist1, use_container_width=True)
        
    with l2:
        st.subheader("Completion Duration (Days)")
        comp_valid = df_filtered.dropna(subset=['sanction_to_completion_days'])
        fig_hist2 = px.histogram(
            comp_valid,
            x='sanction_to_completion_days',
            nbins=30,
            labels={'sanction_to_completion_days': 'Sanction to Completion (Days)'},
            color_discrete_sequence=['#10b981']
        )
        fig_hist2.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color='#e2e8f0')
        st.plotly_chart(fig_hist2, use_container_width=True)

# ==============================================================================
# PAGE 5: INVESTIGATION DEEP-DIVE
# ==============================================================================
elif page == "5. Investigation Deep-Dive":
    st.title("🔬 Work Investigation Deep-Dive")
    st.caption("Complete 360-degree audit trail and explainable evidence breakdown for a single Work ID.")
    
    # Select Work ID
    high_risk_wids = df_filtered[df_filtered['risk_level'].isin(['CRITICAL', 'HIGH'])]['work_id'].tolist()
    default_wid = high_risk_wids[0] if len(high_risk_wids) > 0 else df_filtered['work_id'].iloc[0]
    
    selected_wid = st.selectbox("Search or Select Work ID", df_filtered['work_id'].tolist(), index=df_filtered['work_id'].tolist().index(default_wid))
    
    work_row = df_filtered[df_filtered['work_id'] == selected_wid].iloc[0]
    work_exp = expenditures_df[expenditures_df['work_id'] == selected_wid]
    
    # Profile Card
    st.markdown(f"""
    <div class="banner-container" style="background: #1e293b; border-color: #475569;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span class="banner-title">{work_row['work_id']}</span>
                <div style="color: #94a3b8; margin-top: 4px;">{work_row['parliament_house']} | MP: <b>{work_row['mp_name']}</b> | State: <b>{work_row['state']}</b></div>
            </div>
            <div>
                <span class="badge-{work_row['risk_level'].lower()}" style="font-size: 16px; padding: 8px 16px;">
                    Risk Score: {work_row['risk_score']:.1f} — {work_row['risk_level']}
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Work Attributes
    a1, a2, a3, a4 = st.columns(4)
    with a1:
        st.markdown(f"**Work Category:** {work_row['work_category']}")
        st.markdown(f"**Sanction Date:** {work_row['sanction_date'].date() if pd.notnull(work_row['sanction_date']) else 'N/A'}")
    with a2:
        st.markdown(f"**Sanction Amount:** ₹{work_row['sanctioned_amount']:,.2f}")
        st.markdown(f"**Total Expenditure:** ₹{work_row['total_expenditure']:,.2f}")
    with a3:
        st.markdown(f"**Completed Amount:** ₹{work_row['completion_amount']:,.2f}")
        st.markdown(f"**Payment Count:** {work_row['payment_count']}")
    with a4:
        st.markdown(f"**Vendor Concentration:** {int(work_row['vendor_concentration_score']*100)}%")
        st.markdown(f"**Duplicate Payments:** {work_row['duplicate_payment_count']}")

    st.markdown("---")
    
    # Itemized Audit Explanations
    st.subheader("💡 Explainable Risk Evidence & Reasons")
    reasons_list = work_row['risk_reasons_list']
    
    for r in reasons_list:
        st.markdown(f"""
        <div class="audit-box">
            <div style="font-weight: 600; color: #f8fafc;">• {r}</div>
        </div>
        """, unsafe_allow_html=True)

    # Disbursal Ledger
    if not work_exp.empty:
        st.subheader("💳 Transaction Ledger & Disbursals")
        st.dataframe(
            work_exp[['expenditure_date', 'vendor_name', 'payment_status', 'amount']],
            column_config={
                "expenditure_date": "Date",
                "vendor_name": "Vendor Name",
                "payment_status": "Status",
                "amount": st.column_config.NumberColumn("Amount (₹)", format="₹%,.2f")
            },
            use_container_width=True
        )

# ==============================================================================
# PAGE 6: DATA QUALITY & AUDIT LOG
# ==============================================================================
elif page == "6. Data Quality & Audit Log":
    st.title("📋 Data Quality & Verification Audit Log")
    st.caption("Demonstrating robustness against imperfect government source data exports.")
    
    q1, q2 = st.columns(2)
    with q1:
        st.subheader("Raw CSV Ingestion vs Cleaned Row Counts")
        dq_report = pd.read_csv(os.path.join(OUTPUTS_DIR, "data_quality_report.csv"))
        st.dataframe(dq_report, use_container_width=True)
        
    with q2:
        st.subheader("Duplicate Payment Transactions Log")
        dup_exp = expenditures_df[expenditures_df.duplicated(subset=['work_id', 'expenditure_date', 'vendor_name', 'payment_status', 'amount'], keep=False)]
        st.markdown(f"Total duplicate payment records detected: **{len(dup_exp):,}**")
        st.dataframe(
            dup_exp[['work_id', 'expenditure_date', 'vendor_name', 'amount']].head(100),
            use_container_width=True
        )
