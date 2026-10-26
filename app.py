import streamlit as st
import pandas as pd
from datetime import datetime
import re

st.set_page_config(
    page_title="Compliance SOP Governance Register | Checkout.com",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for executive register styling
st.markdown("""
<style>
    .stApp {
        background-color: #0E1117;
    }
    .register-row {
        background-color: #161A23;
        border-radius: 8px;
        border: 1px solid #232A3B;
        padding: 12px 16px;
        margin-bottom: 10px;
        transition: border-color 0.15s ease, background-color 0.15s ease;
    }
    .register-row:hover {
        border-color: #3B4760;
        background-color: #1A1F2C;
    }
    .badge-jira {
        font-family: monospace;
        font-size: 11px;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 4px;
        background: #1E2638;
        color: #90CAF9 !important;
        text-decoration: none;
        border: 1px solid #2B3850;
    }
    .badge-jira:hover {
        background: #2A364F;
    }
    .badge-sop {
        font-size: 11px;
        font-weight: 500;
        padding: 3px 8px;
        border-radius: 4px;
        text-decoration: none;
    }
    .sop-confluence {
        background: #142736;
        color: #80D8FF !important;
        border: 1px solid #1E4663;
    }
    .sop-confluence:hover {
        background: #1C384D;
    }
    .sop-doc {
        background: #172E24;
        color: #A7F3D0 !important;
        border: 1px solid #245242;
    }
    .sop-doc:hover {
        background: #203F31;
    }
    .sop-unmapped {
        background: #2B2117;
        color: #FFB74D;
        border: 1px dashed #B26A00;
    }
</style>
""", unsafe_allow_html=True)

def auto_link_text(text):
    if not isinstance(text, str) or not text.strip():
        return ""
    
    urls = []
    def save_url(m):
        raw = m.group(0)
        clean = raw.rstrip('.,;:)')
        trail = raw[len(clean):]
        idx = len(urls)
        urls.append(clean)
        return f"__LINK_TOKEN_{idx}__{trail}"
    
    formatted = re.sub(r'https?://[^\s]+', save_url, text)
    
    def link_ticket(m):
        ticket = m.group(1)
        return f'<a href="https://checkout.atlassian.net/browse/{ticket}" target="_blank" style="color: #90CAF9; text-decoration: underline; font-weight: 600;">{ticket} ↗</a>'
    
    formatted = re.sub(r'\b([A-Z]{2,10}-\d+)\b', link_ticket, formatted)
    
    for idx, u in enumerate(urls):
        if "wiki" in u or "spaces" in u:
            label = "📘 Confluence SOP ↗"
        elif "docs.google.com" in u:
            label = "📄 Google Doc ↗"
        elif "browse" in u:
            label = "🎫 Jira Ticket ↗"
        else:
            label = "🔗 Document Link ↗"
        replacement = f'<a href="{u}" target="_blank" style="color: #80D8FF; text-decoration: underline; font-weight: 500;">{label}</a>'
        formatted = formatted.replace(f"__LINK_TOKEN_{idx}__", replacement)
        
    return formatted

def parse_sop_link(val):
    if not isinstance(val, str) or not val.strip():
        return {"type": "none", "label": "⚠️ SOP Unmapped", "url": None}
    match = re.search(r'https?://[^\s)]+', val)
    if not match:
        return {"type": "none", "label": "⚠️ SOP Unmapped", "url": None}
    url = match.group(0).rstrip('.,;:)')
    if "docs.google.com" in url:
        return {"type": "doc", "label": "📄 Draft Doc ↗", "url": url}
    elif "atlassian.net" in url:
        return {"type": "confluence", "label": "📘 Confluence SOP ↗", "url": url}
    else:
        return {"type": "link", "label": "🔗 Document ↗", "url": url}

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
    df["Status_Group"] = df["Jira_Status"].apply(categorize_status)
    return df

df = load_data()

# --- SIDEBAR ---
st.sidebar.markdown("## 🛡️ Checkout.com")
st.sidebar.caption("Process Architecture · Compliance")
st.sidebar.markdown("""
<div style="background-color: #171B24; padding: 12px 14px; border-radius: 8px; border-left: 3px solid #3F51B5; margin-bottom: 12px;">
    <div style="font-size: 11px; text-transform: uppercase; color: #8F9CAE; letter-spacing: 0.5px;">Executive Oversight</div>
    <div style="font-size: 13px; font-weight: 600; color: #F0F4F8; margin-top: 2px;">Sunil Mudaliar</div>
    <div style="font-size: 11px; color: #8F9CAE;">Senior Lead, Process Architecture</div>
</div>
<div style="background-color: #171B24; padding: 12px 14px; border-radius: 8px; border-left: 3px solid #00ACC1; margin-bottom: 16px;">
    <div style="font-size: 11px; text-transform: uppercase; color: #8F9CAE; letter-spacing: 0.5px;">Domain Governance</div>
    <div style="font-size: 13px; font-weight: 600; color: #F0F4F8; margin-top: 2px;">Bernard Ryan</div>
    <div style="font-size: 11px; color: #8F9CAE;">Domain Lead, Compliance</div>
    <div style="font-size: 13px; font-weight: 600; color: #F0F4F8; margin-top: 6px;">Allan Maxwell</div>
    <div style="font-size: 11px; color: #8F9CAE;">Process Architect</div>
</div>
""", unsafe_allow_html=True)

st.sidebar.info("📌 **Compliance Registry:** Tracks the operational health of procedures, open stakeholder change requests, and unmapped SOPs.")

# --- TOP EXECUTIVE BAR ---
st.title("Compliance SOP Governance Register")
st.caption("Central registry tracking procedure updates, documentation health, and delivery dependencies.")

# Key metrics
total_cnt = len(df)
blocked_cnt = len(df[df["Status_Group"] == "Blocked"])
inprog_cnt = len(df[df["Status_Group"] == "In Progress"])
backlog_cnt = len(df[df["Status_Group"] == "Backlog"])

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Procedures in Scope", total_cnt)
col_m2.metric("Blocked / Action Required", blocked_cnt, delta=f"{blocked_cnt} Needs Unblocking" if blocked_cnt > 0 else "None", delta_color="inverse")
col_m3.metric("Under Active Review", inprog_cnt)
col_m4.metric("Queued for Scoping", backlog_cnt)

st.divider()

# --- TOP FILTER CONTROLS ---
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

# Apply filters
filtered_df = df.copy()

if "🔴 Blocked" in filter_choice:
    filtered_df = filtered_df[filtered_df["Status_Group"] == "Blocked"]
elif "Allan's" in filter_choice:
    filtered_df = filtered_df[filtered_df["Compliance_Owner"].str.contains("Allan", case=False, na=False)]
elif "Bernard's" in filter_choice:
    filtered_df = filtered_df[filtered_df["Compliance_Owner"].str.contains("Bernard", case=False, na=False)]
elif "Pooja" in filter_choice:
    filtered_df = filtered_df[filtered_df["Requesting_Stakeholder"].str.contains("Pooja|QC", case=False, na=False)]

if search_text:
    filtered_df = filtered_df[
        filtered_df["SOP_Title"].str.lower().str.contains(search_text, na=False) |
        filtered_df["SOP_ID"].str.lower().str.contains(search_text, na=False) |
        filtered_df["Compliance_Owner"].str.lower().str.contains(search_text, na=False) |
        filtered_df["Requesting_Stakeholder"].str.lower().str.contains(search_text, na=False) |
        filtered_df["Jira_Summary"].str.lower().str.contains(search_text, na=False) |
        filtered_df["Key_Blockers_or_Notes"].str.lower().str.contains(search_text, na=False)
    ]

# --- TABS ---
tab_register, tab_table = st.tabs(["📋 Status Register", "📑 Master Audit Table & CSV"])

def render_register_row(item):
    sop_info = parse_sop_link(item["Confluence_URL"])
    status_grp = item["Status_Group"]
    clean_jira_url = f"https://checkout.atlassian.net/browse/{item['SOP_ID']}"
    
    formatted_summary = auto_link_text(item["Jira_Summary"])
    formatted_blocker = auto_link_text(item["Key_Blockers_or_Notes"])
    
    if status_grp == "Blocked":
        badge_style = "background-color: rgba(239, 83, 80, 0.15); color: #FF8A80; border: 1px solid rgba(239, 83, 80, 0.3);"
        border_left = "4px solid #EF5350"
        dep_title = "⚠️ Blocker / Dependency:"
        dep_color = "#FFCDD2"
    elif status_grp == "In Progress":
        badge_style = "background-color: rgba(66, 165, 245, 0.15); color: #90CAF9; border: 1px solid rgba(66, 165, 245, 0.3);"
        border_left = "4px solid #42A5F5"
        dep_title = "ℹ️ Next Step / Status:"
        dep_color = "#BBDEFB"
    else:
        badge_style = "background-color: rgba(158, 158, 158, 0.15); color: #CFD8DC; border: 1px solid rgba(158, 158, 158, 0.3);"
        border_left = "4px solid #78909C"
        dep_title = "📌 Scope & Planned Review:"
        dep_color = "#CFD8DC"

    # SOP badge
    if sop_info["type"] == "confluence":
        sop_badge = f'<a href="{sop_info["url"]}" target="_blank" class="badge-sop sop-confluence">{sop_info["label"]}</a>'
    elif sop_info["type"] == "doc":
        sop_badge = f'<a href="{sop_info["url"]}" target="_blank" class="badge-sop sop-doc">{sop_info["label"]}</a>'
    else:
        sop_badge = f'<span class="badge-sop sop-unmapped">{sop_info["label"]}</span>'
        
    jira_badge = f'<a href="{clean_jira_url}" target="_blank" class="badge-jira">🎫 {item["SOP_ID"]} ↗</a>'

    # Build clean horizontal row
    parts = [
        f'<div class="register-row" style="border-left: {border_left};">',
        f'<div style="display: flex; justify-content: space-between; align-items: center; gap: 12px; margin-bottom: 8px;">',
        f'<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">',
        f'{jira_badge}',
        f'<span style="font-size: 14px; font-weight: 600; color: #F0F4F8;">{item["SOP_Title"]}</span>',
        f'</div>',
        f'<div style="display: flex; align-items: center; gap: 8px; flex-shrink: 0;">',
        f'{sop_badge}',
        f'<span style="font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 4px; {badge_style}">{item["Jira_Status"]}</span>',
        f'</div>',
        f'</div>',
        f'<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 16px; font-size: 12px; color: #8F9CAE; background: #11141C; padding: 9px 12px; border-radius: 6px;">',
        f'<div><strong style="color: #CBD5E1;">Owner:</strong> {item["Compliance_Owner"]} &nbsp;·&nbsp; <strong style="color: #CBD5E1;">Requested by:</strong> {item["Requesting_Stakeholder"]}<br><span style="color: #94A3B8; margin-top: 3px; display: inline-block;"><strong style="color: #90CAF9;">Requested Change:</strong> {formatted_summary}</span></div>',
        f'<div><strong style="color: #E2E8F0;">{dep_title}</strong><br><span style="color: {dep_color}; margin-top: 3px; display: inline-block;">{formatted_blocker}</span></div>',
        f'</div>',
        f'</div>'
    ]
    return "".join(parts)

with tab_register:
    blocked_rows = filtered_df[filtered_df["Status_Group"] == "Blocked"]
    inprog_rows = filtered_df[filtered_df["Status_Group"] == "In Progress"]
    backlog_rows = filtered_df[filtered_df["Status_Group"] == "Backlog"]
    
    if len(blocked_rows) > 0:
        st.markdown(f"#### 🔴 Action Required / External Dependencies ({len(blocked_rows)})")
        for _, row in blocked_rows.iterrows():
            st.markdown(render_register_row(row), unsafe_allow_html=True)
            
    if len(inprog_rows) > 0:
        st.markdown(f"#### 🔵 Active Policy Revisions ({len(inprog_rows)})")
        for _, row in inprog_rows.iterrows():
            st.markdown(render_register_row(row), unsafe_allow_html=True)
            
    if len(backlog_rows) > 0:
        st.markdown(f"#### ⚪ Queued for Scoping ({len(backlog_rows)})")
        for _, row in backlog_rows.iterrows():
            st.markdown(render_register_row(row), unsafe_allow_html=True)
            
    if len(filtered_df) == 0:
        st.info("No procedures match the selected filter.")

with tab_table:
    st.subheader("Master Governance Table")
    st.caption("Exportable roster with direct links to Jira issue keys and documentation.")
    
    table_view = filtered_df[[
        "SOP_ID", "SOP_Title", "Compliance_Owner", "Jira_Status", 
        "Priority", "Requesting_Stakeholder", "Confluence_URL"
    ]].copy()
    
    table_view["Jira_Link"] = "https://checkout.atlassian.net/browse/" + table_view["SOP_ID"]
    
    st.dataframe(
        table_view,
        column_config={
            "SOP_ID": "Ticket ID",
            "SOP_Title": "Procedure Name",
            "Compliance_Owner": "Owner",
            "Jira_Status": "Status",
            "Priority": "Priority",
            "Requesting_Stakeholder": "Requested By",
            "Jira_Link": st.column_config.LinkColumn("Jira Ticket"),
            "Confluence_URL": "SOP Link / Document Status",
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.download_button(
        label="📥 Download Register (.csv)",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name=f"compliance_sop_register_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
