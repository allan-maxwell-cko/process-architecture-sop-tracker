import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re
import plotly.express as px

st.set_page_config(
    page_title="SOP Update Tracker | Checkout.com",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

CSV_FILE = "Compliance_SOP_Tracker_Master.csv"

def safe_rerun():
    if hasattr(st, "rerun"):
        st.rerun()
    elif hasattr(st, "experimental_rerun"):
        st.experimental_rerun()

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
        return f'<a href="https://checkout.atlassian.net/browse/{ticket}" target="_blank" style="color: #60A5FA; text-decoration: underline; font-weight: 600;">{ticket} ↗</a>'
    formatted = re.sub(r'\b([A-Z]{2,10}-\d+)\b', link_ticket, formatted)
    for idx, u in enumerate(urls):
        label = "📘 Confluence SOP ↗" if ("wiki" in u or "spaces" in u) else ("📄 Google Doc ↗" if "docs.google.com" in u else "🔗 Link ↗")
        replacement = f'<a href="{u}" target="_blank" style="color: #38BDF8; text-decoration: underline; font-weight: 500;">{label}</a>'
        formatted = formatted.replace(f"__LINK_TOKEN_{idx}__", replacement)
    return formatted

def parse_sop_link(val):
    if not isinstance(val, str) or not val.strip():
        return {"type": "none", "label": "⚠️ Unmapped SOP", "url": None}
    match = re.search(r'https?://[^\s)]+', val)
    if not match:
        return {"type": "none", "label": "⚠️ Unmapped SOP", "url": None}
    url = match.group(0).rstrip('.,;:)')
    if "docs.google.com" in url:
        return {"type": "doc", "label": "📄 Working Draft Doc ↗", "url": url}
    elif "atlassian.net" in url:
        return {"type": "confluence", "label": "📘 Live Confluence SOP ↗", "url": url}
    else:
        return {"type": "link", "label": "🔗 Document ↗", "url": url}

def load_data():
    if os.path.exists(CSV_FILE):
        return pd.read_csv(CSV_FILE, quotechar='"', skipinitialspace=True)
    return pd.DataFrame()

if "tracker_data" not in st.session_state:
    st.session_state.tracker_data = load_data()

df_all = st.session_state.tracker_data

# Styling: High-end enterprise dark mode
st.markdown("""
<style>
    .stApp {
        background-color: #0A0D14;
        color: #F1F5F9;
    }
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 96%;
    }
    .kicker {
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 1.2px;
        color: #94A3B8;
        text-transform: uppercase;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .health-bar-container {
        width: 100%;
        background-color: #1E293B;
        height: 6px;
        border-radius: 4px;
        overflow: hidden;
        display: flex;
        margin-top: 10px;
        margin-bottom: 22px;
    }
    .bar-signed-off { background-color: #10B981; }
    .bar-in-progress { background-color: #F59E0B; }
    .bar-awaiting { background-color: #F97316; }
    .bar-blocked { background-color: #EF4444; }
    .bar-not-started { background-color: #64748B; }

    .tracker-card {
        background-color: #121622;
        border: 1px solid #232B3C;
        border-radius: 8px;
        padding: 14px 18px;
        margin-bottom: 12px;
        transition: border-color 0.15s ease, background-color 0.15s ease;
    }
    .tracker-card:hover {
        border-color: #3B82F6;
        background-color: #161C2C;
    }
    .jira-pill {
        font-family: monospace;
        font-size: 12px;
        font-weight: 700;
        padding: 4px 9px;
        border-radius: 5px;
        background: #1E293B;
        color: #60A5FA !important;
        text-decoration: none;
        border: 1px solid #334155;
        display: inline-flex;
        align-items: center;
        gap: 4px;
    }
    .jira-pill:hover {
        background: #2563EB;
        color: #FFFFFF !important;
    }
    .sop-pill {
        font-size: 11px;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 5px;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 5px;
    }
    .sop-pill-confluence {
        background: #0E2938;
        color: #38BDF8 !important;
        border: 1px solid #0284C7;
    }
    .sop-pill-confluence:hover {
        background: #0284C7;
        color: #FFFFFF !important;
    }
    .sop-pill-doc {
        background: #0D2E22;
        color: #34D399 !important;
        border: 1px solid #059669;
    }
    .sop-pill-doc:hover {
        background: #059669;
        color: #FFFFFF !important;
    }
    .sop-pill-unmapped {
        background: #2D2013;
        color: #FBBF24;
        border: 1px dashed #D97706;
    }
</style>
""", unsafe_allow_html=True)

# --- HEADER SECTION ---
st.markdown("""
<div class="kicker">
    <span>COMPLIANCE OPS</span> &nbsp;·&nbsp; <span>INTERIM SINGLE SOURCE</span> &nbsp;·&nbsp; <span style="color: #60A5FA;">PROCESS ARCHITECTURE</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 6px; flex-wrap: wrap; gap: 14px;">
    <div>
        <h1 style="font-size: 34px; font-weight: 700; color: #FFFFFF; margin: 0; line-height: 1.15;">SOP Update Tracker</h1>
        <div style="font-size: 13px; color: #94A3B8; margin-top: 4px;">
            Governance Lead: <strong style="color: #F8FAFC;">Bernard Ryan</strong> &nbsp;·&nbsp; 
            Process Architect: <strong style="color: #F8FAFC;">Allan Maxwell</strong> &nbsp;·&nbsp; 
            Executive Oversight: <strong style="color: #F8FAFC;">Sunil Mudaliar</strong>
        </div>
    </div>
    <div style="display: flex; gap: 10px; align-items: center; flex-wrap: wrap;">
        <div style="background-color: #172238; border: 1px solid #1E3A8A; color: #60A5FA; font-size: 12px; font-weight: 600; padding: 6px 14px; border-radius: 20px; display: flex; align-items: center; gap: 6px;">
            <span style="height: 7px; width: 7px; background-color: #3B82F6; border-radius: 50%; display: inline-block;"></span>
            Owner Edit Mode · Live Sync
        </div>
        <a href="https://checkout.atlassian.net" target="_blank" style="color: #94A3B8; font-size: 12px; font-weight: 500; text-decoration: none; padding: 5px 10px; border: 1px solid #232B3C; border-radius: 6px; background: #131722;">
            Atlassian Sources ↗
        </a>
    </div>
</div>
<p style="color: #94A3B8; font-size: 13.5px; margin-bottom: 4px; max-width: 860px; line-height: 1.45;">
    Centralized governance hub tracking all requested procedure amendments in flight. Anyone can triage status and view dependencies. Filter, inspect blockers, or update delivery statuses directly in-line.
</p>
<div style="font-size: 11.5px; color: #64748B; margin-bottom: 12px;">
    Sources verified October 2026 ⓘ &nbsp;·&nbsp; Process Architecture Registry V2.4
</div>
""", unsafe_allow_html=True)

# Metrics calculation
total_cnt = len(df_all)
signed_off_cnt = len(df_all[df_all["UPDATE_STATUS"] == "Signed Off"])
in_progress_cnt = len(df_all[df_all["UPDATE_STATUS"] == "In progress"])
awaiting_cnt = len(df_all[df_all["UPDATE_STATUS"] == "Awaiting Review"])
under_review_cnt = len(df_all[df_all["UPDATE_STATUS"] == "Under Review"])
blocked_cnt = len(df_all[df_all["UPDATE_STATUS"] == "Blocked"])
not_started_cnt = len(df_all[df_all["UPDATE_STATUS"] == "Not Started"])

# Visual Health Progress Bar
if total_cnt > 0:
    pct_signed = (signed_off_cnt / total_cnt) * 100
    pct_inprog = (in_progress_cnt / total_cnt) * 100
    pct_awaiting = (awaiting_cnt / total_cnt) * 100
    pct_blocked = (blocked_cnt / total_cnt) * 100
    pct_notstart = (not_started_cnt / total_cnt) * 100
    st.markdown(f"""
    <div class="health-bar-container" title="Delivery Progress">
        <div class="bar-signed-off" style="width: {pct_signed}%;"></div>
        <div class="bar-in-progress" style="width: {pct_inprog}%;"></div>
        <div class="bar-awaiting" style="width: {pct_awaiting}%;"></div>
        <div class="bar-blocked" style="width: {pct_blocked}%;"></div>
        <div class="bar-not-started" style="width: {pct_notstart}%;"></div>
    </div>
    """, unsafe_allow_html=True)

# --- INTERACTIVE METRIC PULSE (Clickable Filters) ---
status_tabs = st.radio(
    "Filter by Status",
    options=[
        f"ALL UPDATES ({total_cnt})",
        f"⚪ NOT STARTED ({not_started_cnt})",
        f"🟡 IN PROGRESS ({in_progress_cnt})",
        f"🟠 AWAITING REVIEW ({awaiting_cnt})",
        f"🟢 SIGNED OFF ({signed_off_cnt})",
        f"🔴 BLOCKED ({blocked_cnt})"
    ],
    horizontal=True,
    label_visibility="collapsed"
)

# --- TOOLBAR: SEARCH & FILTERS ---
t_c1, t_c2, t_c3, t_c4, t_c5 = st.columns([4, 2, 2, 2, 2])

with t_c1:
    search_q = st.text_input("Search", placeholder="Search SOP name, update summary, Jira key, owner...", label_visibility="collapsed").strip().lower()

with t_c2:
    all_owners = ["Owner: any"] + sorted(list(df_all["UPDATE_OWNER"].dropna().unique()))
    sel_owner = st.selectbox("Owner", options=all_owners, label_visibility="collapsed")

with t_c3:
    all_approvers = ["Approver: any"] + sorted(list(df_all["APPROVER"].dropna().unique()))
    sel_approver = st.selectbox("Approver", options=all_approvers, label_visibility="collapsed")

with t_c4:
    if st.button("Reset Filters", use_container_width=True):
        safe_rerun()

with t_c5:
    open_add_modal = st.button("+ Add SOP update", type="primary", use_container_width=True)

# Modal Form for adding new updates
if open_add_modal:
    with st.expander("➕ Log New Stakeholder SOP Update", expanded=True):
        with st.form("new_sop_form", clear_on_submit=True):
            f1, f2 = st.columns(2)
            with f1:
                form_sop = st.text_input("SOP Title / Document Target", placeholder="e.g. Sanctions Transaction Screening SOP")
                form_update = st.text_input("Requested Change Summary", placeholder="e.g. Add mandatory RBA justification for Tier 2 RFIs")
                form_jira = st.text_input("Jira Ticket Key or URL", placeholder="e.g. OEPT-3012")
                form_confluence = st.text_input("Confluence URL (optional)", placeholder="https://checkout.atlassian.net/wiki/...")
            with f2:
                form_owner = st.selectbox("Update Owner", ["Allan Maxwell", "Bernard Ryan", "Neema Nev", "Sunil Mudaliar"])
                form_approver = st.text_input("Approver / Stakeholder", placeholder="e.g. Pooja Lutchmun (QC) / Kevin Gopaul")
                form_status = st.selectbox("Initial Status", ["Not Started", "In progress", "Awaiting Review", "Under Review", "Signed Off", "Blocked"], index=1)
                form_timeline = st.text_input("Target Date / Blocker Note", placeholder="e.g. Target: 15-November-2026")
            
            if st.form_submit_button("Save & Append to Register", type="primary"):
                clean_jira_link = form_jira if form_jira.startswith("http") else f"https://checkout.atlassian.net/browse/{form_jira.strip().upper()}"
                new_entry = pd.DataFrame([{
                    "SOP_ID": form_jira.strip().upper().replace("HTTPS://CHECKOUT.ATLASSIAN.NET/BROWSE/", ""),
                    "SOP_NAME": form_sop,
                    "SOP_UPDATE_NAME": form_update,
                    "JIRA_TICKET_LINK": clean_jira_link,
                    "CONFLUENCE_URL": form_confluence,
                    "UPDATE_OWNER": form_owner,
                    "APPROVER": form_approver,
                    "UPDATE_STATUS": form_status,
                    "PRIORITY": "Medium",
                    "TIMELINE": form_timeline,
                    "KEY_BLOCKER": form_timeline
                }])
                updated_master = pd.concat([st.session_state.tracker_data, new_entry], ignore_index=True)
                st.session_state.tracker_data = updated_master
                updated_master.to_csv(CSV_FILE, index=False)
                st.success("✅ New SOP update added to the register!")
                safe_rerun()

# Apply Filters
filtered_df = df_all.copy()

if "BLOCKED" in status_tabs:
    filtered_df = filtered_df[filtered_df["UPDATE_STATUS"] == "Blocked"]
elif "IN PROGRESS" in status_tabs:
    filtered_df = filtered_df[filtered_df["UPDATE_STATUS"] == "In progress"]
elif "AWAITING" in status_tabs:
    filtered_df = filtered_df[filtered_df["UPDATE_STATUS"] == "Awaiting Review"]
elif "SIGNED OFF" in status_tabs:
    filtered_df = filtered_df[filtered_df["UPDATE_STATUS"] == "Signed Off"]
elif "NOT STARTED" in status_tabs:
    filtered_df = filtered_df[filtered_df["UPDATE_STATUS"] == "Not Started"]

if sel_owner != "Owner: any":
    filtered_df = filtered_df[filtered_df["UPDATE_OWNER"] == sel_owner]

if sel_approver != "Approver: any":
    filtered_df = filtered_df[filtered_df["APPROVER"] == sel_approver]

if search_q:
    filtered_df = filtered_df[
        filtered_df["SOP_NAME"].str.lower().str.contains(search_q, na=False) |
        filtered_df["SOP_UPDATE_NAME"].str.lower().str.contains(search_q, na=False) |
        filtered_df["UPDATE_OWNER"].str.lower().str.contains(search_q, na=False) |
        filtered_df["APPROVER"].str.lower().str.contains(search_q, na=False) |
        filtered_df["TIMELINE"].str.lower().str.contains(search_q, na=False) |
        filtered_df["SOP_ID"].str.lower().str.contains(search_q, na=False)
    ]

st.write("")

# --- VIEW TABS ---
view_tab1, view_tab2, view_tab3 = st.tabs([
    f"⚡ Interactive Action Board ({len(filtered_df)})",
    "📊 Quick Data Grid (Bulk Editor)",
    "📈 Executive Delivery Analytics"
])

# ==========================================
# VIEW 1: ENHANCED INTERACTIVE ACTION BOARD
# ==========================================
with view_tab1:
    st.caption(f"Showing **{len(filtered_df)}** of {total_cnt} SOP updates · Click any row to inspect dependencies or launch docs")
    
    if len(filtered_df) == 0:
        st.info("No SOP updates match the selected filters. Click 'Reset Filters' above to view all records.")
    else:
        for idx, row in filtered_df.iterrows():
            sop_link_info = parse_sop_link(str(row.get("CONFLUENCE_URL", "")))
            ticket_id = str(row.get("SOP_ID", "TICKET"))
            jira_url = str(row.get("JIRA_TICKET_LINK", f"https://checkout.atlassian.net/browse/{ticket_id}"))
            current_status = str(row.get("UPDATE_STATUS", "In progress"))
            
            # Status styling
            if current_status == "Blocked":
                border_style = "border-left: 4px solid #EF4444;"
                badge_bg = "rgba(239, 68, 68, 0.15)"
                badge_txt = "#FCA5A5"
                dot = "🔴"
            elif current_status == "In progress":
                border_style = "border-left: 4px solid #F59E0B;"
                badge_bg = "rgba(245, 158, 11, 0.15)"
                badge_txt = "#FCD34D"
                dot = "🟡"
            elif current_status == "Signed Off":
                border_style = "border-left: 4px solid #10B981;"
                badge_bg = "rgba(16, 185, 129, 0.15)"
                badge_txt = "#6EE7B7"
                dot = "🟢"
            elif current_status in ["Awaiting Review", "Under Review"]:
                border_style = "border-left: 4px solid #F97316;"
                badge_bg = "rgba(249, 115, 22, 0.15)"
                badge_txt = "#FDBA74"
                dot = "🟠"
            else:
                border_style = "border-left: 4px solid #64748B;"
                badge_bg = "rgba(100, 116, 139, 0.15)"
                badge_txt = "#CBD5E1"
                dot = "⚪"

            if sop_link_info["type"] == "confluence":
                sop_btn_html = f'<a href="{sop_link_info["url"]}" target="_blank" class="sop-pill sop-pill-confluence">{sop_link_info["label"]}</a>'
            elif sop_link_info["type"] == "doc":
                sop_btn_html = f'<a href="{sop_link_info["url"]}" target="_blank" class="sop-pill sop-pill-doc">{sop_link_info["label"]}</a>'
            else:
                sop_btn_html = f'<span class="sop-pill sop-pill-unmapped">{sop_link_info["label"]}</span>'

            jira_btn_html = f'<a href="{jira_url}" target="_blank" class="jira-pill">🎫 {ticket_id} ↗</a>'
            
            blocker_text = str(row.get("KEY_BLOCKER", row.get("TIMELINE", "")))
            formatted_blocker = auto_link_text(blocker_text)
            formatted_summary = auto_link_text(str(row.get("SOP_UPDATE_NAME", "")))

            card_html = f"""
            <div class="tracker-card" style="{border_style}">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 8px;">
                    <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
                        {jira_btn_html}
                        <span style="font-size: 15px; font-weight: 700; color: #F8FAFC;">{row['SOP_NAME']}</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 10px;">
                        {sop_btn_html}
                        <span style="background-color: {badge_bg}; color: {badge_txt}; font-size: 11.5px; font-weight: 700; padding: 4px 10px; border-radius: 4px; display: inline-flex; align-items: center; gap: 5px;">
                            {dot} {current_status}
                        </span>
                    </div>
                </div>
                <div style="display: grid; grid-template-columns: 3fr 2fr; gap: 16px; background-color: #0E121B; padding: 10px 14px; border-radius: 6px; font-size: 12.5px; margin-top: 6px;">
                    <div>
                        <div style="color: #94A3B8; margin-bottom: 4px;">
                            <strong style="color: #E2E8F0;">Update Scope:</strong> {formatted_summary}
                        </div>
                        <div style="color: #64748B; font-size: 12px;">
                            <strong>Owner:</strong> <span style="color: #CBD5E1;">{row['UPDATE_OWNER']}</span> &nbsp;·&nbsp; 
                            <strong>Approver:</strong> <span style="color: #CBD5E1;">{row['APPROVER']}</span>
                        </div>
                    </div>
                    <div>
                        <div style="color: #94A3B8; margin-bottom: 4px;">
                            <strong style="color: #E2E8F0;">Timeline & Dependency:</strong>
                        </div>
                        <div style="color: #E2E8F0; font-size: 12px; line-height: 1.4;">
                            {formatted_blocker}
                        </div>
                    </div>
                </div>
            </div>
            """
            st.markdown(card_html, unsafe_allow_html=True)
            
            # Interactive Quick Triage Dropdown underneath each card
            c_status, c_msg, _ = st.columns([2, 3, 5])
            with c_status:
                status_choices = ["In progress", "Signed Off", "Blocked", "Awaiting Review", "Under Review", "Not Started"]
                current_idx = status_choices.index(current_status) if current_status in status_choices else 0
                new_status = st.selectbox(
                    f"Quick Status for {ticket_id}",
                    options=status_choices,
                    index=current_idx,
                    key=f"status_select_{idx}",
                    label_visibility="collapsed"
                )
                if new_status != current_status:
                    st.session_state.tracker_data.at[idx, "UPDATE_STATUS"] = new_status
                    st.session_state.tracker_data.to_csv(CSV_FILE, index=False)
                    st.toast(f"Updated {ticket_id} status to {new_status}!", icon="✅")
                    safe_rerun()
            with c_msg:
                st.caption(f"💡 Target: `{row.get('TIMELINE', 'In flight')}`")

# ==========================================
# VIEW 2: QUICK DATA GRID (BULK EDITOR)
# ==========================================
with view_tab2:
    st.markdown("#### 📊 Spreadsheet Bulk Editor")
    st.caption("Double-click any cell to edit details inline, copy-paste URLs, or update deadlines.")
    
    table_editor = st.data_editor(
        filtered_df,
        column_config={
            "SOP_ID": st.column_config.TextColumn("ID", width="small", disabled=True),
            "SOP_NAME": st.column_config.TextColumn("SOP Name", width="medium"),
            "SOP_UPDATE_NAME": st.column_config.TextColumn("Update Details", width="large"),
            "JIRA_TICKET_LINK": st.column_config.LinkColumn("Jira Ticket Link"),
            "CONFLUENCE_URL": st.column_config.LinkColumn("Confluence / Doc Link"),
            "UPDATE_OWNER": st.column_config.SelectboxColumn("Owner", options=["Allan Maxwell", "Bernard Ryan", "Neema Nev", "Sunil Mudaliar"]),
            "APPROVER": st.column_config.TextColumn("Approver"),
            "UPDATE_STATUS": st.column_config.SelectboxColumn("Status", options=["Not Started", "In progress", "Awaiting Review", "Under Review", "Signed Off", "Blocked"]),
            "TIMELINE": st.column_config.TextColumn("Timeline"),
            "KEY_BLOCKER": st.column_config.TextColumn("Blocker Dependency", width="large")
        },
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        key="bulk_data_editor"
    )
    
    col_save, col_dl, _ = st.columns([2, 2, 6])
    with col_save:
        if st.button("💾 Save Grid Changes", type="primary", use_container_width=True):
            st.session_state.tracker_data.update(table_editor)
            st.session_state.tracker_data.to_csv(CSV_FILE, index=False)
            st.success("✅ Changes successfully saved and published!")
            safe_rerun()
            
    with col_dl:
        st.download_button(
            label="📥 Export Tracker CSV",
            data=st.session_state.tracker_data.to_csv(index=False).encode('utf-8'),
            file_name=f"compliance_sop_tracker_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True
        )

# ==========================================
# VIEW 3: EXECUTIVE DELIVERY ANALYTICS
# ==========================================
with view_tab3:
    st.markdown("#### 📈 Compliance Governance & Bottleneck Intelligence")
    st.caption("Executive overview for Sunil Mudaliar and domain leads to identify dependencies holding up SOP releases.")
    
    ch_col1, ch_col2 = st.columns(2)
    
    with ch_col1:
        st.markdown("##### Status Breakdown")
        st_data = df_all["UPDATE_STATUS"].value_counts().reset_index()
        st_data.columns = ["Status", "Count"]
        fig_pie = px.pie(
            st_data,
            names="Status",
            values="Count",
            hole=0.6,
            color="Status",
            color_discrete_map={
                "Signed Off": "#10B981",
                "In progress": "#F59E0B",
                "Awaiting Review": "#F97316",
                "Under Review": "#3B82F6",
                "Blocked": "#EF4444",
                "Not Started": "#64748B"
            }
        )
        fig_pie.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#E2E8F0",
            height=280
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with ch_col2:
        st.markdown("##### Workload by Compliance Owner")
        owner_data = df_all["UPDATE_OWNER"].value_counts().reset_index()
        owner_data.columns = ["Owner", "Count"]
        fig_owner = px.bar(
            owner_data,
            x="Owner",
            y="Count",
            text="Count",
            color="Owner",
            color_discrete_sequence=["#2563EB", "#0284C7"]
        )
        fig_owner.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#E2E8F0",
            height=280,
            showlegend=False,
            xaxis_title="",
            yaxis=dict(dtick=1, tick0=0, tickformat="d", title="Procedures")
        )
        st.plotly_chart(fig_owner, use_container_width=True, config={"displayModeBar": False})
        
    st.markdown("##### Requests by Approver / Stakeholder")
    approver_data = df_all["APPROVER"].value_counts().reset_index()
    approver_data.columns = ["Approver", "Count"]
    fig_app = px.bar(
        approver_data,
        x="Count",
        y="Approver",
        orientation="h",
        text="Count",
        color_discrete_sequence=["#3B82F6"]
    )
    fig_app.update_layout(
        margin=dict(t=10, b=10, l=10, r=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#E2E8F0",
        height=300,
        yaxis=dict(autorange="reversed", title=""),
        xaxis=dict(dtick=1, tick0=0, tickformat="d", title="Change Requests")
    )
    st.plotly_chart(fig_app, use_container_width=True, config={"displayModeBar": False})
