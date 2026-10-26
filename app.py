import streamlit as st
import pandas as pd
import os

CSV_FILE = "sop_data.csv"

st.set_page_config(page_title="Checkout.com SOP Navigator", layout="wide", page_icon="🧭")

st.title("🧭 Process Architecture — SOP Navigator & Tracker")
st.caption("Live operational directory with editable titles, Jira blocker tracking, and Confluence links.")

# 1. Load Data
if "sop_data" not in st.session_state:
    if os.path.exists(CSV_FILE):
        st.session_state.sop_data = pd.read_csv(CSV_FILE)
    else:
        st.session_state.sop_data = pd.DataFrame([
            {
                "Team": "AML Transaction Monitoring",
                "Jira Key": "CDCR-32",
                "Display Title": "AML (Pay-in) TM – Recipient Review (L1)",
                "Raw Jira Title": "drafting fix for tm recipient - Tejash",
                "Doc Type": "Google Doc",
                "Status": "Awaiting Approval",
                "Blocker / Notes": "Drafted; awaiting final sign-off confirmation",
                "Owner": "Tejash Chunnoo",
                "Link": "https://docs.google.com",
                "Hide": False
            },
            {
                "Team": "AML Transaction Monitoring",
                "Jira Key": "OEPT-1154",
                "Display Title": "AML TM SOP – L1 Triage",
                "Raw Jira Title": "consolidate 3 sops into one L1 triage global",
                "Doc Type": "Confluence",
                "Status": "In Progress",
                "Blocker / Notes": "Consolidation pilot complete; awaiting go/no-go call",
                "Owner": "Bernard Ryan",
                "Link": "https://checkout.atlassian.net",
                "Hide": False
            },
            {
                "Team": "Merchant Screening & Sanctions",
                "Jira Key": "OEPT-1656",
                "Display Title": "Adverse Media Monitoring – L1 (Owlin)",
                "Raw Jira Title": "OEPT-1656 Owlin signoff blockers",
                "Doc Type": "Google Doc",
                "Status": "Blocked",
                "Blocker / Notes": "Awaiting decision on whether Owlin deprecates by EOY",
                "Owner": "Kevin Gopaul",
                "Link": "https://docs.google.com",
                "Hide": False
            },
            {
                "Team": "Merchant Screening & Sanctions",
                "Jira Key": "OEPT-2460",
                "Display Title": "Transaction Sanctions Screening – Fircosoft L1",
                "Raw Jira Title": "UAE audit finding external RFI SLA task",
                "Doc Type": "Confluence",
                "Status": "Stale (>14d)",
                "Blocker / Notes": "UAE audit finding: must show External RFI SLA (untouched)",
                "Owner": "Bernard Ryan",
                "Link": "https://checkout.atlassian.net",
                "Hide": False
            },
            {
                "Team": "Merchant Screening & Sanctions",
                "Jira Key": "OEPT-2827",
                "Display Title": "Exception Settlement Request (ESR) SOP",
                "Raw Jira Title": "ESR internal blocklist compliance fix",
                "Doc Type": "Google Doc",
                "Status": "Blocked",
                "Blocker / Notes": "Requires product-based fix (RA Tool/Genesis) before finalizing",
                "Owner": "Bernard Ryan",
                "Link": "https://docs.google.com",
                "Hide": False
            },
            {
                "Team": "Due Diligence & RFIs",
                "Jira Key": "OEPT-2939",
                "Display Title": "Brazil Onboarding Due Diligence Review SOP",
                "Raw Jira Title": "OEPT-2939 CPF tax id review",
                "Doc Type": "Google Doc",
                "Status": "Blocked",
                "Blocker / Notes": "Mandates local CPF tax ID; requires formal MLRO sign-off",
                "Owner": "Bernard Ryan",
                "Link": "https://docs.google.com",
                "Hide": False
            }
        ])
        st.session_state.sop_data.to_csv(CSV_FILE, index=False)

active_df = st.session_state.sop_data[~st.session_state.sop_data["Hide"]]

# 2. Executive Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Published SOPs", len(active_df[active_df["Doc Type"] == "Confluence"]))
c2.metric("In-Flight Drafts", len(active_df[active_df["Doc Type"] == "Google Doc"]))
c3.metric("Blocked", len(active_df[active_df["Status"] == "Blocked"]), delta="Action Required", delta_color="inverse")
c4.metric("Stale (>14d)", len(active_df[active_df["Status"].str.contains("Stale", na=False)]), delta="No Movement", delta_color="inverse")

st.write("")

# 3. Analyst Global Search Bar
search_query = st.text_input("🔎 Search any SOP, process keyword, or Jira key across all teams:", placeholder="e.g. Owlin, Brazil, Fircosoft, CDCR...")

if search_query:
    filtered = active_df[
        active_df["Display Title"].str.contains(search_query, case=False, na=False) |
        active_df["Jira Key"].str.contains(search_query, case=False, na=False) |
        active_df["Blocker / Notes"].str.contains(search_query, case=False, na=False)
    ]
    st.write(f"Found **{len(filtered)}** result(s) for *'{search_query}'*:")
    st.dataframe(
        filtered[["Team", "Display Title", "Jira Key", "Doc Type", "Status", "Blocker / Notes", "Owner", "Link"]],
        use_container_width=True,
        hide_index=True,
        column_config={"Link": st.column_config.LinkColumn("Document Link")}
    )
    st.divider()

# 4. Team Tabs & Admin Panel
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 AML Transaction Monitoring", 
    "🛡️ Merchant Screening & Sanctions", 
    "📋 Due Diligence & RFIs",
    "⚙️ PA Admin Panel"
])

def render_table(team_name):
    df = active_df[active_df["Team"] == team_name]
    st.dataframe(
        df[["Display Title", "Jira Key", "Doc Type", "Status", "Blocker / Notes", "Owner", "Link"]],
        use_container_width=True,
        hide_index=True,
        column_config={"Link": st.column_config.LinkColumn("Document Link")}
    )

with tab1:
    st.subheader("AML Transaction Monitoring")
    render_table("AML Transaction Monitoring")

with tab2:
    st.subheader("Merchant Screening & Sanctions")
    render_table("Merchant Screening & Sanctions")

with tab3:
    st.subheader("Due Diligence & RFIs")
    render_table("Due Diligence & RFIs")

with tab4:
    st.subheader("Process Architecture Control Panel")
    
    # 4A. Add New Item Form
    with st.expander("➕ Add New SOP or In-Flight Ticket", expanded=False):
        with st.form("add_sop_form", clear_on_submit=True):
            f_team = st.selectbox("Owning Team", ["AML Transaction Monitoring", "Merchant Screening & Sanctions", "Due Diligence & RFIs"])
            f_key = st.text_input("Jira Key", placeholder="e.g. OEPT-3042")
            f_title = st.text_input("Clean Display Title", placeholder="e.g. Card Issuing Level 2 SOP")
            f_type = st.selectbox("Document Type", ["Confluence", "Google Doc"])
            f_status = st.selectbox("Status", ["Published", "In Progress", "Awaiting Approval", "Blocked", "Stale (>14d)"])
            f_notes = st.text_input("Blocker / Context", placeholder="e.g. Awaiting Risk team sign-off")
            f_owner = st.text_input("Owner / PA", placeholder="e.g. Bernard Ryan")
            f_link = st.text_input("Document / Jira Link", placeholder="https://...")
            
            submitted = st.form_submit_button("Add to Tracker", type="primary")
            if submitted:
                if f_title and f_key:
                    new_row = {
                        "Team": f_team,
                        "Jira Key": f_key,
                        "Display Title": f_title,
                        "Raw Jira Title": f_title,
                        "Doc Type": f_type,
                        "Status": f_status,
                        "Blocker / Notes": f_notes,
                        "Owner": f_owner,
                        "Link": f_link if f_link else "https://checkout.com",
                        "Hide": False
                    }
                    st.session_state.sop_data = pd.concat([st.session_state.sop_data, pd.DataFrame([new_row])], ignore_index=True)
                    st.session_state.sop_data.to_csv(CSV_FILE, index=False)
                    st.success(f"Added '{f_title}'! Refreshing...")
                    st.rerun()
                else:
                    st.error("Please provide at least a Jira Key and Display Title.")

    st.write("---")
    st.markdown("**✏️ Edit Existing Titles or Hide Obsolete Items:**")
    st.caption("Double-click any title to clean it up. Check 'Hide?' to remove an item from the main tabs.")
    
    edited_data = st.data_editor(
        st.session_state.sop_data,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Hide": st.column_config.CheckboxColumn("Hide?", default=False),
            "Display Title": st.column_config.TextColumn("Clean Display Title (Double-click to edit)", required=True),
            "Raw Jira Title": st.column_config.TextColumn("Original Jira Title (Read-Only)", disabled=True),
            "Team": st.column_config.SelectboxColumn("Team", options=["AML Transaction Monitoring", "Merchant Screening & Sanctions", "Due Diligence & RFIs"])
        }
    )
    
    if st.button("💾 Apply & Save Overrides Permanently", type="primary"):
        st.session_state.sop_data = edited_data
        st.session_state.sop_data.to_csv(CSV_FILE, index=False)
        st.success("Changes saved permanently to disk!")
        st.rerun()
