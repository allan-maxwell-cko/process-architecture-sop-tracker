import streamlit as st
import pandas as pd
from datetime import datetime
import os
import re

st.set_page_config(
    page_title="Compliance SOP Governance Board | Checkout.com",
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
        return {"type": "none", "label": "⚠️ No SOP Linked", "url": None}
    match = re.search(r'https?://[^\s)]+', val)
    if not match:
        return {"type": "none", "label": "⚠️ No SOP Linked", "url": None}
    url = match.group(0).rstrip('.,;:)')
    if "docs.google.com" in url:
        return {"type": "doc", "label": "📄 Draft Doc ↗", "url": url}
    elif "atlassian.net" in url:
        return {"type": "confluence", "label": "📘 SOP ↗", "url": url}
    else:
        return {"type": "link", "label": "🔗 Document ↗", "url": url}

def load_data():
    if os.path.exists(CSV_FILE):
        try:
            loaded_df = pd.read_csv(CSV_FILE, quotechar='"', skipinitialspace=True)
            if len(loaded_df) > 0 and "SOP_ID" in loaded_df.columns:
                return loaded_df
        except Exception:
            pass
    return pd.DataFrame()

if "tracker_data" not in st.session_state:
    st.session_state.tracker_data = load_data()

df_all = st.session_state.tracker_data

# Dark Mode UI styling
st.markdown("""
<style>
    .stApp {
        background-color: #0A0D14;
        color: #F1F5F9;
    }
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3.5rem;
        max-width: 98%;
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
    .kanban-header {
        font-size: 13px;
        font-weight: 700;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        padding: 8px 12px;
        border-radius: 6px;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .kh-blocked {
        background-color: rgba(239, 68, 68, 0.12);
        color: #F87171;
        border: 1px solid rgba(239, 68, 68, 0.25);
    }
    .kh-inprog {
        background-color: rgba(59, 130, 246, 0.12);
        color: #60A5FA;
        border: 1px solid rgba(59, 130, 246, 0.25);
    }
    .kh-backlog {
        background-color: rgba(148, 163, 184, 0.12);
        color: #94A3B8;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }
    .kh-done {
        background-color: rgba(16, 185, 129, 0.12);
        color: #34D399;
        border: 1px solid rgba(16, 185, 129, 0.25);
    }
    .jira-board-card {
        background-color: #121622;
        border: 1px solid #232B3C;
        border-radius: 8px;
        padding: 12px 14px;
        margin-bottom: 10px;
        transition: border-color 0.15s ease, background-color 0.15s ease;
    }
    .jira-board-card:hover {
        border-color: #3B82F6;
        background-color: #161C2C;
    }
    .jira-key-badge {
        font-family: monospace;
        font-size: 11.5px;
        font-weight: 700;
        padding: 2px 7px;
        border-radius: 4px;
        background: #1E293B;
        color: #60A5FA !important;
        text-decoration: none;
        border: 1px solid #334155;
    }
    .jira-key-badge:hover {
        background: #2563EB;
        color: #FFFFFF !important;
    }
    .domain-tag {
        font-size: 10.5px;
        font-weight: 600;
        color: #94A3B8;
        background: #1A202E;
        padding: 2px 7px;
        border-radius: 4px;
        border: 1px solid #252D3F;
    }
    .card-title {
        font-size: 14px;
        font-weight: 600;
        color: #F8FAFC;
        margin-top: 6px;
        margin-bottom: 6px;
        line-height: 1.3;
    }
    .card-summary {
        font-size: 12px;
        color: #94A3B8;
        line-height: 1.35;
        margin-bottom: 8px;
    }
    .blocker-box {
        font-size: 11.5px;
        line-height: 1.35;
        padding: 7px 9px;
        border-radius: 5px;
        margin-bottom: 8px;
    }
    .bb-blocked {
        background-color: rgba(239, 68, 68, 0.08);
        border-left: 3px solid #EF4444;
        color: #FCA5A5;
    }
    .bb-inprog {
        background-color: rgba(59, 130, 246, 0.08);
        border-left: 3px solid #3B82F6;
        color: #93C5FD;
    }
    .bb-backlog {
        background-color: rgba(148, 163, 184, 0.08);
        border-left: 3px solid #64748B;
        color: #CBD5E1;
    }
    .card-footer {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
        color: #64748B;
        margin-bottom: 6px;
    }
    .card-actions {
        display: flex;
        gap: 6px;
        flex-wrap: wrap;
        align-items: center;
    }
    .btn-action-jira {
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        background: #1E293B;
        color: #93C5FD !important;
        text-decoration: none;
        border: 1px solid #334155;
    }
    .btn-action-sop {
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        background: #0E2938;
        color: #38BDF8 !important;
        text-decoration: none;
        border: 1px solid #0284C7;
    }
    .btn-action-doc {
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        background: #0D2E22;
        color: #34D399 !important;
        text-decoration: none;
        border: 1px solid #059669;
    }
    .btn-action-unmapped {
        font-size: 11px;
        font-weight: 600;
        padding: 3px 8px;
        border-radius: 4px;
        background: #2D2013;
        color: #FBBF24;
        border: 1px dashed #D97706;
    }
</style>
""", unsafe_allow_html=True)

# Top Header
st.markdown("""
<div class="kicker">
    <span>COMPLIANCE OPS</span> &nbsp;·&nbsp; <span>JIRA SOP GOVERNANCE</span> &nbsp;·&nbsp; <span style="color: #60A5FA;">PROCESS ARCHITECTURE</span>
</div>
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; flex-wrap: wrap; gap: 14px;">
    <div>
        <h1 style="font-size: 32px; font-weight: 700; color: #FFFFFF; margin: 0; line-height: 1.15;">Compliance SOP Governance Board</h1>
        <div style="font-size: 12.5px; color: #94A3B8; margin-top: 4px;">
            Domain Lead: <strong style="color: #F8FAFC;">Bernard Ryan</strong> &nbsp;·&nbsp; 
            Process Architect: <strong style="color: #F8FAFC;">Allan Maxwell</strong> &nbsp;·&nbsp; 
            Senior Lead: <strong style="color: #F8FAFC;">Sunil Mudaliar</strong>
        </div>
    </div>
    <div style="display: flex; gap: 10px; align-items: center;">
        <div style="background-color: #172238; border: 1px solid #1E3A8A; color: #60A5FA; font-size: 11.5px; font-weight: 600; padding: 5px 12px; border-radius: 20px;">
            ● Live Interactive Mode
        </div>
        <a href="https://checkout.atlassian.net" target="_blank" style="color: #94A3B8; font-size: 12px; text-decoration: none; padding: 5px 10px; border: 1px solid #232B3C; border-radius: 6px; background: #131722;">
            Open Jira Workspace ↗
        </a>
    </div>
</div>
""", unsafe_allow_html=True)

# --- FILTER TOOLBAR ---
f_col1, f_col2, f_col3, f_col4, f_col5, f_col6 = st.columns([3, 2, 2, 2, 1, 1.2])

with f_col1:
    search_term = st.text_input("Search", placeholder="Search tickets, SOPs, keywords, blockers...", label_visibility="collapsed").strip().lower()

with f_col2:
    all_domains = ["Domain: All"] + sorted(list(df_all["DOMAIN"].dropna().unique()))
    sel_domain = st.selectbox("Domain", options=all_domains, label_visibility="collapsed")

with f_col3:
    all_stakeholders = ["Stakeholder: All"] + sorted(list(df_all["APPROVER"].dropna().unique()))
    sel_stakeholder = st.selectbox("Stakeholder", options=all_stakeholders, label_visibility="collapsed")

with f_col4:
    all_owners = ["Owner: All"] + sorted(list(df_all["UPDATE_OWNER"].dropna().unique()))
    sel_owner = st.selectbox("Owner", options=all_owners, label_visibility="collapsed")

with f_col5:
    if st.button("Reset", use_container_width=True):
        safe_rerun()

with f_col6:
    open_add = st.button("+ Add Ticket", type="primary", use_container_width=True)

if open_add:
    with st.expander("➕ Log New Jira Ticket to Board", expanded=True):
        with st.form("new_ticket_modal", clear_on_submit=True):
            m1, m2 = st.columns(2)
            with m1:
                t_id = st.text_input("Jira Ticket Key", placeholder="e.g. OEPT-3100")
                t_name = st.text_input("Procedure / SOP Name", placeholder="e.g. Sanctions RFI Procedure")
                t_domain = st.selectbox("Domain", ["Sanctions & Screening", "AML & KYC", "Governance & Policy", "Merchant Onboarding", "Quality Control & Audit"])
                t_owner = st.selectbox("Compliance Owner", ["Allan Maxwell", "Bernard Ryan", "Neema Nev", "Sunil Mudaliar"])
            with m2:
                t_summary = st.text_input("Requested Change / Summary", placeholder="Brief description of the change request")
                t_stakeholder = st.text_input("Requesting Stakeholder", placeholder="e.g. Pooja Lutchmun (QC)")
                t_status = st.selectbox("Initial Status", ["Blocked", "In progress", "Awaiting Review", "Backlog", "Signed Off"], index=1)
                t_sop_link = st.text_input("Confluence / Doc Link (optional)", placeholder="https://checkout.atlassian.net/wiki/...")
            t_blocker = st.text_input("Blocker or Next Step Note", placeholder="e.g. Awaiting reporter signoff")
            
            if st.form_submit_button("Add to Board", type="primary"):
                clean_jira = t_id if t_id.startswith("http") else f"https://checkout.atlassian.net/browse/{t_id.strip().upper()}"
                new_row = pd.DataFrame([{
                    "SOP_ID": t_id.strip().upper().replace("HTTPS://CHECKOUT.ATLASSIAN.NET/BROWSE/", ""),
                    "SOP_NAME": t_name,
                    "DOMAIN": t_domain,
                    "SOP_UPDATE_NAME": t_summary,
                    "JIRA_TICKET_LINK": clean_jira,
                    "CONFLUENCE_URL": t_sop_link,
                    "UPDATE_OWNER": t_owner,
                    "APPROVER": t_stakeholder,
                    "UPDATE_STATUS": t_status,
                    "PRIORITY": "Medium",
                    "TIMELINE": t_blocker
                }])
                st.session_state.tracker_data = pd.concat([st.session_state.tracker_data, new_row], ignore_index=True)
                st.session_state.tracker_data.to_csv(CSV_FILE, index=False)
                if hasattr(st, "toast"):
                    st.toast("Added ticket to board!", icon="✅")
                safe_rerun()

# Apply Filters
filtered = df_all.copy()

if sel_domain != "Domain: All":
    filtered = filtered[filtered["DOMAIN"] == sel_domain]

if sel_stakeholder != "Stakeholder: All":
    filtered = filtered[filtered["APPROVER"] == sel_stakeholder]

if sel_owner != "Owner: All":
    filtered = filtered[filtered["UPDATE_OWNER"] == sel_owner]

if search_term:
    filtered = filtered[
        filtered["SOP_NAME"].str.lower().str.contains(search_term, na=False) |
        filtered["SOP_UPDATE_NAME"].str.lower().str.contains(search_term, na=False) |
        filtered["UPDATE_OWNER"].str.lower().str.contains(search_term, na=False) |
        filtered["APPROVER"].str.lower().str.contains(search_term, na=False) |
        filtered["TIMELINE"].str.lower().str.contains(search_term, na=False) |
        filtered["SOP_ID"].str.lower().str.contains(search_term, na=False)
    ]

st.caption(f"Showing **{len(filtered)}** of {len(df_all)} open Jira change requests")

# --- KANBAN BOARD COLUMNS ---
c_blocked, c_inprog, c_backlog, c_done = st.columns(4)

blocked_df = filtered[filtered["UPDATE_STATUS"] == "Blocked"]
inprog_df = filtered[filtered["UPDATE_STATUS"].isin(["In progress", "Awaiting Review", "Under Review"])]
backlog_df = filtered[filtered["UPDATE_STATUS"].isin(["Not Started", "Backlog"])]
done_df = filtered[filtered["UPDATE_STATUS"] == "Signed Off"]

def render_board_card(row, idx, col_type):
    ticket_id = str(row.get("SOP_ID", ""))
    sop_name = str(row.get("SOP_NAME", ""))
    jira_url = str(row.get("JIRA_TICKET_LINK", f"https://checkout.atlassian.net/browse/{ticket_id}"))
    confluence_url = str(row.get("CONFLUENCE_URL", ""))
    sop_link_info = parse_sop_link(confluence_url)
    priority = str(row.get("PRIORITY", "Medium"))
    domain = str(row.get("DOMAIN", "Compliance"))
    owner = str(row.get("UPDATE_OWNER", ""))
    approver = str(row.get("APPROVER", ""))
    
    formatted_summary = auto_link_text(str(row.get("SOP_UPDATE_NAME", "")))
    formatted_blocker = auto_link_text(str(row.get("TIMELINE", "")))
    
    if col_type == "blocked":
        border_style = "border-top: 3px solid #EF4444;"
        blocker_class = "bb-blocked"
        callout_label = "⚠️ Blocker"
    elif col_type == "inprog":
        border_style = "border-top: 3px solid #3B82F6;"
        blocker_class = "bb-inprog"
        callout_label = "ℹ️ Next Step"
    elif col_type == "backlog":
        border_style = "border-top: 3px solid #64748B;"
        blocker_class = "bb-backlog"
        callout_label = "📌 Queue Note"
    else:
        border_style = "border-top: 3px solid #10B981;"
        blocker_class = "bb-inprog"
        callout_label = "✅ Status"

    if sop_link_info["type"] == "confluence":
        sop_badge = f'<a href="{sop_link_info["url"]}" target="_blank" class="btn-action-sop">📘 SOP ↗</a>'
    elif sop_link_info["type"] == "doc":
        sop_badge = f'<a href="{sop_link_info["url"]}" target="_blank" class="btn-action-doc">📄 Doc ↗</a>'
    else:
        sop_badge = f'<span class="btn-action-unmapped">⚠️ No SOP Linked</span>'

    card_html = f"""
    <div class="jira-board-card" style="{border_style}">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
            <div style="display: flex; align-items: center; gap: 6px;">
                <a href="{jira_url}" target="_blank" class="jira-key-badge">{ticket_id} ↗</a>
                <span class="domain-tag">{domain}</span>
            </div>
            <span style="font-size: 11px; font-weight: 600; color: #94A3B8;">{priority}</span>
        </div>
        <div class="card-title">{sop_name}</div>
        <div class="card-summary">{formatted_summary}</div>
        <div class="blocker-box {blocker_class}">
            <strong>{callout_label}:</strong> {formatted_blocker}
        </div>
        <div class="card-footer">
            <span>👤 <strong style="color: #CBD5E1;">{owner}</strong></span>
            <span>From: <strong style="color: #CBD5E1;">{approver}</strong></span>
        </div>
        <div class="card-actions">
            <a href="{jira_url}" target="_blank" class="btn-action-jira">🎫 Jira ↗</a>
            {sop_badge}
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)
    
    with st.expander(f"⚙️ Edit SOP / Status ({ticket_id})", expanded=False):
        new_confluence = st.text_input(
            "Impacted Confluence / SOP URL",
            value=confluence_url if pd.notna(confluence_url) else "",
            key=f"conf_input_{idx}",
            placeholder="https://checkout.atlassian.net/wiki/spaces/..."
        )
        status_opts = ["Blocked", "In progress", "Awaiting Review", "Backlog", "Signed Off"]
        curr_status = row.get("UPDATE_STATUS", "In progress")
        s_idx = status_opts.index(curr_status) if curr_status in status_opts else 1
        new_status = st.selectbox(
            "Move Status",
            options=status_opts,
            index=s_idx,
            key=f"status_move_{idx}"
        )
        if st.button("Save Updates", key=f"save_btn_{idx}", type="primary", use_container_width=True):
            st.session_state.tracker_data.at[idx, "CONFLUENCE_URL"] = new_confluence.strip()
            st.session_state.tracker_data.at[idx, "UPDATE_STATUS"] = new_status
            st.session_state.tracker_data.to_csv(CSV_FILE, index=False)
            if hasattr(st, "toast"):
                st.toast(f"Saved changes for {ticket_id}!", icon="✅")
            safe_rerun()

with c_blocked:
    st.markdown(f'<div class="kanban-header kh-blocked"><span>🔴 Blocked / On Hold</span><span>{len(blocked_df)}</span></div>', unsafe_allow_html=True)
    if len(blocked_df) == 0:
        st.caption("No blocked tickets in this filter.")
    else:
        for idx, row in blocked_df.iterrows():
            render_board_card(row, idx, "blocked")

with c_inprog:
    st.markdown(f'<div class="kanban-header kh-inprog"><span>🔵 In Progress & Review</span><span>{len(inprog_df)}</span></div>', unsafe_allow_html=True)
    if len(inprog_df) == 0:
        st.caption("No in-progress tickets in this filter.")
    else:
        for idx, row in inprog_df.iterrows():
            render_board_card(row, idx, "inprog")

with c_backlog:
    st.markdown(f'<div class="kanban-header kh-backlog"><span>⚪ Backlog / Queued</span><span>{len(backlog_df)}</span></div>', unsafe_allow_html=True)
    if len(backlog_df) == 0:
        st.caption("No backlog tickets in this filter.")
    else:
        for idx, row in backlog_df.iterrows():
            render_board_card(row, idx, "backlog")

with c_done:
    st.markdown(f'<div class="kanban-header kh-done"><span>🟢 Signed Off</span><span>{len(done_df)}</span></div>', unsafe_allow_html=True)
    if len(done_df) == 0:
        st.caption("No signed off tickets in this filter.")
    else:
        for idx, row in done_df.iterrows():
            render_board_card(row, idx, "done")

st.divider()

col_export, _ = st.columns([2, 8])
with col_export:
    st.download_button(
        label="📥 Export Master Roster to CSV",
        data=st.session_state.tracker_data.to_csv(index=False).encode('utf-8'),
        file_name=f"compliance_sop_tracker_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
