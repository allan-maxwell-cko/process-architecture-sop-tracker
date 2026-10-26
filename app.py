import streamlit as st
import pandas as pd
from datetime import datetime
import os

st.set_page_config(
    page_title="SOP Update Tracker | Checkout.com",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling matching prototype
st.markdown("""
<style>
    .stApp {
        background-color: #0C0E14;
        color: #F1F5F9;
    }
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 96%;
    }
    .metric-container {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 10px;
        margin-bottom: 24px;
    }
    @media (max-width: 1200px) {
        .metric-container {
            grid-template-columns: repeat(4, 1fr);
        }
    }
    @media (max-width: 768px) {
        .metric-container {
            grid-template-columns: repeat(2, 1fr);
        }
    }
    .metric-card {
        background-color: #141822;
        border: 1px solid #232B3C;
        border-radius: 8px;
        padding: 12px 14px;
        display: flex;
        flex-direction: column;
        justify-content: space-between;
    }
    .metric-title {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.8px;
        color: #8F9CAE;
        text-transform: uppercase;
        display: flex;
        align-items: center;
        gap: 6px;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 26px;
        font-weight: 700;
        color: #FFFFFF;
        line-height: 1;
    }
    div[data-testid="stDataEditor"] {
        border: 1px solid #232B3C;
        border-radius: 8px;
        background-color: #12151D;
    }
    .stButton > button {
        border-radius: 6px;
        font-weight: 600;
        font-size: 13px;
        padding: 6px 14px;
    }
</style>
""", unsafe_allow_html=True)

CSV_FILE = "Compliance_SOP_Tracker.csv"

def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE, quotechar='"', skipinitialspace=True)
    return pd.DataFrame(columns=[
        "SOP_NAME", "SOP_UPDATE_NAME", "JIRA_TICKET_LINK",
        "UPDATE_OWNER", "APPROVER", "UPDATE_STATUS", "TIMELINE"
    ])

if "tracker_data" not in st.session_state:
    st.session_state.tracker_data = load_data()

# Header matching prototype
st.markdown("""
<div style="font-size: 11px; font-weight: 700; letter-spacing: 1.2px; color: #8F9CAE; text-transform: uppercase; margin-bottom: 4px;">COMPLIANCE OPS &nbsp;·&nbsp; INTERIM SINGLE SOURCE</div>
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; flex-wrap: wrap; gap: 12px;">
    <h1 style="font-size: 34px; font-weight: 700; color: #FFFFFF; margin: 0; line-height: 1.1;">SOP Update Tracker</h1>
    <div style="display: flex; gap: 12px; align-items: center;">
        <div style="background-color: #172238; border: 1px solid #1E3A8A; color: #60A5FA; font-size: 12px; font-weight: 600; padding: 6px 14px; border-radius: 20px; display: flex; align-items: center; gap: 6px;">
            <span style="height: 7px; width: 7px; background-color: #3B82F6; border-radius: 50%; display: inline-block;"></span>
            Owner edit · all fields
        </div>
        <a href="https://checkout.atlassian.net" target="_blank" style="color: #94A3B8; font-size: 13px; font-weight: 500; text-decoration: none; padding: 6px 10px;">Sources ↗</a>
    </div>
</div>
<p style="color: #94A3B8; font-size: 14px; margin-bottom: 8px; max-width: 820px; line-height: 1.45;">
    One place to see every SOP update in flight until a BAU solution is in place. Anyone can change an item's status. Only the tracker owner can edit details, add updates or add columns.
</p>
<div style="font-size: 12px; color: #64748B; margin-bottom: 20px;">
    Sources last checked 26-October-2026 at 10:06 ⓘ &nbsp;·&nbsp; Owner edits published 26-October-2026 at 17:59
</div>
""", unsafe_allow_html=True)

df_all = st.session_state.tracker_data

# Status counts
total_cnt = len(df_all)
not_started_cnt = len(df_all[df_all["UPDATE_STATUS"] == "Not Started"])
in_progress_cnt = len(df_all[df_all["UPDATE_STATUS"] == "In progress"])
awaiting_cnt = len(df_all[df_all["UPDATE_STATUS"] == "Awaiting Review"])
under_review_cnt = len(df_all[df_all["UPDATE_STATUS"] == "Under Review"])
signed_off_cnt = len(df_all[df_all["UPDATE_STATUS"] == "Signed Off"])
blocked_cnt = len(df_all[df_all["UPDATE_STATUS"] == "Blocked"])

# 7-Column Metric Bar
st.markdown(f"""
<div class="metric-container">
    <div class="metric-card">
        <div class="metric-title">ALL UPDATES <span style="font-size: 10px; color: #64748B;">ⓘ</span></div>
        <div class="metric-value">{total_cnt}</div>
    </div>
    <div class="metric-card">
        <div class="metric-title"><span style="color: #94A3B8;">⚪</span> NOT STARTED</div>
        <div class="metric-value">{not_started_cnt}</div>
    </div>
    <div class="metric-card">
        <div class="metric-title"><span style="color: #F59E0B;">🟡</span> IN PROGRESS</div>
        <div class="metric-value">{in_progress_cnt}</div>
    </div>
    <div class="metric-card">
        <div class="metric-title"><span style="color: #F97316;">🟠</span> AWAITING REVIEW</div>
        <div class="metric-value">{awaiting_cnt}</div>
    </div>
    <div class="metric-card">
        <div class="metric-title"><span style="color: #3B82F6;">🔵</span> UNDER REVIEW</div>
        <div class="metric-value">{under_review_cnt}</div>
    </div>
    <div class="metric-card">
        <div class="metric-title"><span style="color: #10B981;">🟢</span> SIGNED OFF</div>
        <div class="metric-value">{signed_off_cnt}</div>
    </div>
    <div class="metric-card">
        <div class="metric-title"><span style="color: #EF4444;">🔴</span> BLOCKED</div>
        <div class="metric-value">{blocked_cnt}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# Control & Filter Bar
ctrl_col1, ctrl_col2, ctrl_col3, ctrl_col4, ctrl_col5 = st.columns([4, 2, 2, 2, 2])

with ctrl_col1:
    search_q = st.text_input("Search", placeholder="Search SOP, update, owner, approver...", label_visibility="collapsed").strip().lower()

with ctrl_col2:
    owner_options = ["Owner: any"] + sorted(list(df_all["UPDATE_OWNER"].dropna().unique()))
    selected_owner = st.selectbox("Owner", options=owner_options, label_visibility="collapsed")

with ctrl_col3:
    status_options = ["Status: any", "Not Started", "In progress", "Awaiting Review", "Under Review", "Signed Off", "Blocked"]
    selected_status = st.selectbox("Status", options=status_options, label_visibility="collapsed")

with ctrl_col4:
    if st.button("Clear filters", use_container_width=True):
        safe_rerun()

with ctrl_col5:
    show_add_modal = st.button("+ Add SOP update", type="primary", use_container_width=True)

# Filter logic
filtered_df = df_all.copy()

if selected_owner != "Owner: any":
    filtered_df = filtered_df[filtered_df["UPDATE_OWNER"] == selected_owner]

if selected_status != "Status: any":
    filtered_df = filtered_df[filtered_df["UPDATE_STATUS"] == selected_status]

if search_q:
    filtered_df = filtered_df[
        filtered_df["SOP_NAME"].str.lower().str.contains(search_q, na=False) |
        filtered_df["SOP_UPDATE_NAME"].str.lower().str.contains(search_q, na=False) |
        filtered_df["UPDATE_OWNER"].str.lower().str.contains(search_q, na=False) |
        filtered_df["APPROVER"].str.lower().str.contains(search_q, na=False) |
        filtered_df["TIMELINE"].str.lower().str.contains(search_q, na=False)
    ]

# Expandable Add Form
if show_add_modal:
    with st.form("add_update_form", clear_on_submit=True):
        st.markdown("#### ➕ Add New SOP Update")
        f_c1, f_c2 = st.columns(2)
        with f_c1:
            new_sop = st.text_input("SOP Name", placeholder="e.g. Sanctions Screening SOP")
            new_jira = st.text_input("Jira Ticket URL", placeholder="https://checkout.atlassian.net/browse/OEPT-XXXX")
            new_owner = st.selectbox("Update Owner", ["Allan Maxwell", "Bernard Ryan", "Neema Nev", "Sunil Mudaliar"])
        with f_c2:
            new_update = st.text_input("SOP Update Name", placeholder="Brief description of the amendment")
            new_approver = st.text_input("Approver / Stakeholder", placeholder="e.g. Pooja Lutchmun")
            new_status = st.selectbox("Update Status", ["Not Started", "In progress", "Awaiting Review", "Under Review", "Signed Off", "Blocked"])
        new_timeline = st.text_input("Timeline", placeholder="e.g. Effective immediately or target date")
        
        if st.form_submit_button("Submit & Add to Tracker"):
            new_row = pd.DataFrame([{
                "SOP_NAME": new_sop,
                "SOP_UPDATE_NAME": new_update,
                "JIRA_TICKET_LINK": new_jira,
                "UPDATE_OWNER": new_owner,
                "APPROVER": new_approver,
                "UPDATE_STATUS": new_status,
                "TIMELINE": new_timeline
            }])
            updated_df = pd.concat([st.session_state.tracker_data, new_row], ignore_index=True)
            st.session_state.tracker_data = updated_df
            updated_df.to_csv(CSV_FILE, index=False)
            st.success("Added new update successfully!")
            safe_rerun()

st.caption(f"**{len(filtered_df)} of {len(df_all)} updates**")

# The Interactive Editable Table
edited_df = st.data_editor(
    filtered_df,
    column_config={
        "SOP_NAME": st.column_config.TextColumn(
            "SOP NAME",
            help="Name of the affected standard operating procedure",
            width="medium",
            required=True
        ),
        "SOP_UPDATE_NAME": st.column_config.TextColumn(
            "SOP UPDATE NAME",
            help="Description of the change or amendment requested",
            width="large",
            required=True
        ),
        "JIRA_TICKET_LINK": st.column_config.LinkColumn(
            "JIRA TICKET LINK",
            help="Direct Atlassian Jira issue link",
            width="medium"
        ),
        "UPDATE_OWNER": st.column_config.SelectboxColumn(
            "UPDATE OWNER",
            help="Team member responsible for updating the SOP",
            options=["Allan Maxwell", "Bernard Ryan", "Neema Nev", "Sunil Mudaliar"],
            width="small",
            required=True
        ),
        "APPROVER": st.column_config.TextColumn(
            "APPROVER",
            help="Requesting stakeholder or sign-off authority",
            width="medium"
        ),
        "UPDATE_STATUS": st.column_config.SelectboxColumn(
            "UPDATE STATUS",
            help="Current delivery status",
            options=["Not Started", "In progress", "Awaiting Review", "Under Review", "Signed Off", "Blocked"],
            width="small",
            required=True
        ),
        "TIMELINE": st.column_config.TextColumn(
            "TIMELINE",
            help="Target completion date or key blocker dependency",
            width="medium"
        ),
    },
    num_rows="dynamic",
    use_container_width=True,
    hide_index=True,
    key="sop_interactive_grid"
)

# Bottom Actions
save_c1, save_c2, _ = st.columns([2, 2, 6])

with save_c1:
    if st.button("💾 Publish Changes", type="primary", use_container_width=True):
        for col in edited_df.columns:
            st.session_state.tracker_data.loc[edited_df.index, col] = edited_df[col]
        st.session_state.tracker_data.to_csv(CSV_FILE, index=False)
        st.success("✅ Changes published to SOP tracker!")

with save_c2:
    st.download_button(
        label="📥 Export to CSV",
        data=st.session_state.tracker_data.to_csv(index=False).encode('utf-8'),
        file_name=f"compliance_sop_tracker_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
