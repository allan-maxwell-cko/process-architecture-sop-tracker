import streamlit as st
import pandas as pd
from datetime import datetime
import re

st.set_page_config(
    page_title="Compliance SOP Governance | Checkout.com",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for crisp, enterprise styling
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
    }
    .sop-card {
        background-color: #1A1F2C;
        border: 1px solid #2B3245;
        border-radius: 8px;
        padding: 14px 16px;
        margin-bottom: 14px;
        transition: transform 0.15s ease, border-color 0.15s ease;
    }
    .sop-card:hover {
        border-color: #4A5568;
        transform: translateY(-2px);
    }
    .card-btn {
        display: inline-block;
        font-size: 11px;
        font-weight: 600;
        padding: 5px 10px;
        border-radius: 5px;
        text-decoration: none;
        margin-right: 6px;
        margin-top: 4px;
    }
    .btn-jira {
        background-color: #20293A;
        color: #90CAF9 !important;
        border: 1px solid #2E3B52;
    }
    .btn-jira:hover {
        background-color: #2B3850;
    }
    .btn-confluence {
        background-color: #172D3D;
        color: #80D8FF !important;
        border: 1px solid #1E4663;
    }
    .btn-confluence:hover {
        background-color: #21415B;
    }
    .btn-doc {
        background-color: #1B332A;
        color: #A7F3D0 !important;
        border: 1px solid #245242;
    }
    .btn-doc:hover {
        background-color: #244638;
    }
    .badge-unmapped {
        display: inline-block;
        background-color: #2E251E;
        color: #FFB74D;
        border: 1px dashed #B26A00;
        font-size: 11px;
        font-weight: 500;
        padding: 4px 8px;
        border-radius: 5px;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

def clean_url(val):
    if not isinstance(val, str):
        return None
    match = re.search(r'https?://[^\s)]+', val)
    return match.group(0) if match else None

def parse_sop_link(val):
    if not isinstance(val, str):
        return {"type": "none", "label": "⚠️ Needs SOP Mapping", "url": None}
    match = re.search(r'https?://[^\s)]+', val)
    if not match:
        return {"type": "none", "label": "⚠️ Needs SOP Mapping", "url": None}
    url = match.group(0)
    if "docs.google.com" in url:
        return {"type": "doc", "label": "📄 Working Draft Doc ↗", "url": url}
    elif "atlassian.net" in url:
        return {"type": "confluence", "label": "📘 Confluence SOP ↗", "url": url}
    else:
        return {"type": "link", "label": "🔗 Reference Link ↗", "url": url}

def categorize_status(s):
    s_lower = str(s).lower()
    if 'blocked' in s_lower or 'hold' in s_lower:
        return 'Blocked'
    elif 'in progress' in s_lower:
        return 'In Progress'
    else:
        return 'Backlog'

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv("Compliance_SOP_Change_Requests.csv")
    df["Clean_Jira_URL"] = df["Jira_Ticket"].apply(clean_url)
    df["Status_Group"] = df["Jira_Status"].apply(categorize_status)
    return df

df = load_data()

# --- SIDEBAR ---
st.sidebar.markdown("## 🛡️ Checkout.com")
st.sidebar.caption("Process Architecture · Compliance Governance")
st.sidebar.markdown("""
<div style="background-color: #171B24; padding: 12px 14px; border-radius: 8px; border-left: 3px solid #3F51B5; margin-bottom: 14px;">
    <div style="font-size: 11px; text-transform: uppercase; color: #8F9CAE; letter-spacing: 0.5px;">Executive Oversight</div>
    <div style="font-size: 13px; font-weight: 600; color: #F0F4F8; margin-top: 2px;">Sunil Mudaliar</div>
    <div style="font-size: 11px; color: #8F9CAE;">Senior Lead, Process Architecture</div>
</div>
<div style="background-color: #171B24; padding: 12px 14px; border-radius: 8px; border-left: 3px solid #00ACC1; margin-bottom: 18px;">
    <div style="font-size: 11px; text-transform: uppercase; color: #8F9CAE; letter-spacing: 0.5px;">Domain Governance</div>
    <div style="font-size: 13px; font-weight: 600; color: #F0F4F8; margin-top: 2px;">Bernard Ryan</div>
    <div style="font-size: 11px; color: #8F9CAE;">Domain Lead, Compliance</div>
    <div style="font-size: 13px; font-weight: 600; color: #F0F4F8; margin-top: 6px;">Allan Maxwell</div>
    <div style="font-size: 11px; color: #8F9CAE;">Process Architect</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.info("💡 **Tip:** Use this board to run live triage with Bernard and Pooja's team. Red cards highlight external dependencies blocking delivery.")

# --- TOP EXECUTIVE BAR ---
st.title("Compliance SOP Governance Hub")
st.caption("Active tracking for stakeholder-requested SOP updates, blockers, and documentation readiness.")

# Key metrics
total_cnt = len(df)
blocked_cnt = len(df[df["Status_Group"] == "Blocked"])
inprog_cnt = len(df[df["Status_Group"] == "In Progress"])
backlog_cnt = len(df[df["Status_Group"] == "Backlog"])

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Total Requests", total_cnt)
col_m2.metric("Blocked / On Hold", blocked_cnt, delta=f"{blocked_cnt} Blocked" if blocked_cnt > 0 else "None", delta_color="inverse")
col_m3.metric("In Progress", inprog_cnt, delta="Active Delivery" if inprog_cnt > 0 else None)
col_m4.metric("Backlog", backlog_cnt)

st.divider()

# --- TOP CONTROLS: QUICK FILTER BUTTONS & INSTANT SEARCH ---
ctrl_c1, ctrl_c2 = st.columns([3, 2])

with ctrl_c1:
    filter_choice = st.radio(
        "Filter by Queue:",
        options=[
            f"All ({total_cnt})",
            f"🔴 Blocked ({blocked_cnt})",
            "👤 Allan's Queue",
            "👤 Bernard's Queue",
            "🎯 Pooja / QC Team"
        ],
        horizontal=True,
        label_visibility="collapsed"
    )

with ctrl_c2:
    search_text = st.text_input("🔍 Quick Search", placeholder="Filter by ticket ID, keyword, or stakeholder...", label_visibility="collapsed").strip().lower()

# Apply Quick Filters
filtered_df = df.copy()

if "🔴 Blocked" in filter_choice:
    filtered_df = filtered_df[filtered_df["Status_Group"] == "Blocked"]
elif "Allan's" in filter_choice:
    filtered_df = filtered_df[filtered_df["Compliance_Owner"].str.contains("Allan", case=False, na=False)]
elif "Bernard's" in filter_choice:
    filtered_df = filtered_df[filtered_df["Compliance_Owner"].str.contains("Bernard", case=False, na=False)]
elif "Pooja" in filter_choice:
    filtered_df = filtered_df[filtered_df["Requesting_Stakeholder"].str.contains("Pooja|QC", case=False, na=False)]

# Apply Text Search
if search_text:
    filtered_df = filtered_df[
        filtered_df["SOP_Title"].str.lower().str.contains(search_text, na=False) |
        filtered_df["SOP_ID"].str.lower().str.contains(search_text, na=False) |
        filtered_df["Compliance_Owner"].str.lower().str.contains(search_text, na=False) |
        filtered_df["Requesting_Stakeholder"].str.lower().str.contains(search_text, na=False) |
        filtered_df["Jira_Summary"].str.lower().str.contains(search_text, na=False) |
        filtered_df["Key_Blockers_or_Notes"].str.lower().str.contains(search_text, na=False)
    ]

# --- TABS: 3-COLUMN BOARD & AUDIT TABLE ---
tab_board, tab_table = st.tabs(["📌 3-Column Action Board", "📑 Master Audit List & Export"])

def render_sop_card(item):
    sop_info = parse_sop_link(item["Confluence_URL"])
    status_grp = item["Status_Group"]
    
    if status_grp == "Blocked":
        card_border = "border-left: 4px solid #EF5350;"
        badge_bg = "rgba(239, 83, 80, 0.15)"
        badge_color = "#FF8A80"
        blocker_box = f'''
        <div style="background-color: rgba(239, 83, 80, 0.08); border-left: 3px solid #EF5350; border-radius: 4px; padding: 7px 9px; margin-bottom: 10px; font-size: 12px; color: #FFCDD2; line-height: 1.35;">
            <strong>⚠️ Blocker:</strong> {item["Key_Blockers_or_Notes"]}
        </div>
        '''
    elif status_grp == "In Progress":
        card_border = "border-left: 4px solid #42A5F5;"
        badge_bg = "rgba(66, 165, 245, 0.15)"
        badge_color = "#90CAF9"
        blocker_box = f'''
        <div style="background-color: rgba(66, 165, 245, 0.08); border-left: 3px solid #42A5F5; border-radius: 4px; padding: 7px 9px; margin-bottom: 10px; font-size: 12px; color: #BBDEFB; line-height: 1.35;">
            <strong>ℹ️ Next Step:</strong> {item["Key_Blockers_or_Notes"]}
        </div>
        '''
    else:
        card_border = "border-left: 4px solid #78909C;"
        badge_bg = "rgba(120, 144, 156, 0.15)"
        badge_color = "#B0BEC5"
        blocker_box = f'''
        <div style="background-color: rgba(120, 144, 156, 0.08); border-left: 3px solid #78909C; border-radius: 4px; padding: 7px 9px; margin-bottom: 10px; font-size: 12px; color: #CFD8DC; line-height: 1.35;">
            <strong>📌 Scope:</strong> {item["Key_Blockers_or_Notes"]}
        </div>
        '''

    if sop_info["type"] == "confluence":
        sop_html = f'<a href="{sop_info["url"]}" target="_blank" class="card-btn btn-confluence">{sop_info["label"]}</a>'
    elif sop_info["type"] == "doc":
        sop_html = f'<a href="{sop_info["url"]}" target="_blank" class="card-btn btn-doc">{sop_info["label"]}</a>'
    else:
        sop_html = f'<span class="badge-unmapped">{sop_info["label"]}</span>'

    jira_html = f'<a href="{item["Clean_Jira_URL"]}" target="_blank" class="card-btn btn-jira">🎫 Jira: {item["SOP_ID"]} ↗</a>' if item["Clean_Jira_URL"] else f'<span class="card-btn btn-jira">{item["SOP_ID"]}</span>'

    html = f'''
    <div class="sop-card" style="{card_border}">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <span style="font-family: monospace; font-size: 12px; font-weight: 700; color: #90CAF9; background: #131720; padding: 2px 6px; border-radius: 4px;">{item["SOP_ID"]}</span>
            <span style="background-color: {badge_bg}; color: {badge_color}; font-size: 11px; font-weight: 600; padding: 2px 7px; border-radius: 4px;">{item["Jira_Status"]}</span>
        </div>
        <div style="font-size: 14px; font-weight: 600; color: #F0F4F8; line-height: 1.3; margin-bottom: 6px;">
            {item["SOP_Title"]}
        </div>
        <div style="font-size: 12px; color: #8F9CAE; margin-bottom: 8px;">
            <strong style="color: #CBD5E1;">Owner:</strong> {item["Compliance_Owner"]} &nbsp;·&nbsp; <strong style="color: #CBD5E1;">From:</strong> {item["Requesting_Stakeholder"]}
        </div>
        <div style="background-color: #12151D; border-radius: 5px; padding: 7px 9px; font-size: 12px; color: #CBD5E1; line-height: 1.35; margin-bottom: 8px;">
            <strong style="color: #90CAF9;">Change:</strong> {item["Jira_Summary"]}
        </div>
        {blocker_box}
        <div style="margin-top: 6px;">
            {jira_html}
            {sop_html}
        </div>
    </div>
    '''
    return html

with tab_board:
    col_b, col_p, col_q = st.columns(3)
    
    blocked_cards = filtered_df[filtered_df["Status_Group"] == "Blocked"]
    inprog_cards = filtered_df[filtered_df["Status_Group"] == "In Progress"]
    backlog_cards = filtered_df[filtered_df["Status_Group"] == "Backlog"]
    
    with col_b:
        st.markdown(f"### 🔴 Blocked / On Hold ({len(blocked_cards)})")
        st.caption("External dependencies requiring resolution")
        if len(blocked_cards) == 0:
            st.info("No blocked tickets in this view.")
        else:
            for _, item in blocked_cards.iterrows():
                st.markdown(render_sop_card(item), unsafe_allow_html=True)
                
    with col_p:
        st.markdown(f"### 🔵 In Progress ({len(inprog_cards)})")
        st.caption("Active updates currently being drafted/reviewed")
        if len(inprog_cards) == 0:
            st.info("No in-progress tickets in this view.")
        else:
            for _, item in inprog_cards.iterrows():
                st.markdown(render_sop_card(item), unsafe_allow_html=True)
                
    with col_q:
        st.markdown(f"### ⚪ Backlog ({len(backlog_cards)})")
        st.caption("Queued for scoping or companion SOP rollout")
        if len(backlog_cards) == 0:
            st.info("No backlog tickets in this view.")
        else:
            for _, item in backlog_cards.iterrows():
                st.markdown(render_sop_card(item), unsafe_allow_html=True)

with tab_table:
    st.subheader("Master Compliance Change Log")
    st.caption("Audit roster of all stakeholder change requests with direct links to Atlassian trackers.")
    
    table_view = filtered_df[[
        "SOP_ID", "SOP_Title", "Compliance_Owner", "Jira_Status", 
        "Priority", "Requesting_Stakeholder", "Clean_Jira_URL", "Confluence_URL"
    ]].copy()
    
    st.dataframe(
        table_view,
        column_config={
            "SOP_ID": "Ticket ID",
            "SOP_Title": "SOP Title / Change Target",
            "Compliance_Owner": "Owner",
            "Jira_Status": "Status",
            "Priority": "Priority",
            "Requesting_Stakeholder": "Requested By",
            "Clean_Jira_URL": st.column_config.LinkColumn("Jira Ticket"),
            "Confluence_URL": "SOP / Document Target",
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.download_button(
        label="📥 Export Master Roster to CSV",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name=f"compliance_sop_master_log_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
