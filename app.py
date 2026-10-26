import streamlit as st
import pandas as pd
from datetime import datetime
import re
import plotly.express as px

st.set_page_config(
    page_title="Compliance SOP Updates | Checkout.com",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def clean_url(val):
    if not isinstance(val, str):
        return None
    match = re.search(r'https?://[^\s)]+', val)
    return match.group(0) if match else None

def categorize_status(s):
    s_lower = str(s).lower()
    if 'blocked' in s_lower or 'hold' in s_lower:
        return 'Blocked / On Hold'
    elif 'in progress' in s_lower:
        return 'In Progress'
    else:
        return 'Backlog'

def categorize_team(s):
    s_lower = str(s).lower()
    if 'qc' in s_lower:
        return 'Quality Control (QC)'
    elif 'legal' in s_lower or 'cco' in s_lower:
        return 'Legal & CCO'
    elif 'audit' in s_lower or 'mlro' in s_lower:
        return 'Internal Audit / MLRO'
    elif 'leadership' in s_lower or 'mirabel' in s_lower:
        return 'Compliance Leadership'
    elif 'product' in s_lower or 'analytics' in s_lower:
        return 'Product & Analytics'
    elif 'ops' in s_lower or 'operations' in s_lower:
        return 'Operations'
    else:
        return 'Direct Stakeholders'

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv("Compliance_SOP_Change_Requests.csv")
    df["Clean_Confluence_URL"] = df["Confluence_URL"].apply(clean_url)
    df["Clean_Jira_URL"] = df["Jira_Ticket"].apply(clean_url)
    df["Status_Group"] = df["Jira_Status"].apply(categorize_status)
    df["Requesting_Team"] = df["Requesting_Stakeholder"].apply(categorize_team)
    return df

df = load_data()

# --- SIDEBAR ---
st.sidebar.markdown("## 🛡️ Checkout.com")
st.sidebar.caption("Process Architecture · Compliance")
st.sidebar.divider()

st.sidebar.markdown("**Senior Lead:** Sunil Mudaliar")
st.sidebar.markdown("**Domain Lead:** Bernard Ryan")
st.sidebar.divider()

# Clean collapsible filters
with st.sidebar.expander("🔍 Filter Options", expanded=False):
    selected_owner = st.multiselect(
        "Owner",
        options=sorted(df["Compliance_Owner"].unique()),
        default=sorted(df["Compliance_Owner"].unique())
    )
    selected_status = st.multiselect(
        "Status Group",
        options=["Blocked / On Hold", "In Progress", "Backlog"],
        default=["Blocked / On Hold", "In Progress", "Backlog"]
    )
    selected_teams = st.multiselect(
        "Requesting Team",
        options=sorted(df["Requesting_Team"].unique()),
        default=sorted(df["Requesting_Team"].unique())
    )

# Filter logic
filtered_df = df[
    df["Compliance_Owner"].isin(selected_owner) &
    df["Status_Group"].isin(selected_status) &
    df["Requesting_Team"].isin(selected_teams)
]

# --- MAIN HEADER ---
st.title("Compliance SOP Change Requests")
st.caption("Active tracking for stakeholder update requests, blockers, and documentation status.")

# Top Metric Cards
total_count = len(filtered_df)
blocked_count = len(filtered_df[filtered_df["Status_Group"] == "Blocked / On Hold"])
in_progress_count = len(filtered_df[filtered_df["Status_Group"] == "In Progress"])
backlog_count = len(filtered_df[filtered_df["Status_Group"] == "Backlog"])

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Requests", total_count)
m2.metric("In Progress", in_progress_count)
m3.metric("Blocked / On Hold", blocked_count, delta=f"{blocked_count} Blocked" if blocked_count > 0 else None, delta_color="inverse")
m4.metric("Backlog", backlog_count)

st.divider()

# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📋 All Requests", "📊 Summary Charts", "📑 Table View"])

# --- TAB 1: ALL REQUESTS ---
with tab1:
    search_query = st.text_input("🔍 Quick search by keyword, ticket ID, or owner:", "").strip().lower()
    
    display_df = filtered_df.copy()
    if search_query:
        display_df = display_df[
            display_df["SOP_Title"].str.lower().str.contains(search_query, na=False) |
            display_df["SOP_ID"].str.lower().str.contains(search_query, na=False) |
            display_df["Compliance_Owner"].str.lower().str.contains(search_query, na=False) |
            display_df["Requesting_Stakeholder"].str.lower().str.contains(search_query, na=False) |
            display_df["Jira_Summary"].str.lower().str.contains(search_query, na=False)
        ]

    st.caption(f"Showing **{len(display_df)}** of {len(df)} change requests")
    
    # 1. Blocked section (open by default)
    blocked_items = display_df[display_df["Status_Group"] == "Blocked / On Hold"]
    if len(blocked_items) > 0:
        st.markdown(f"### 🔴 Blocked / On Hold ({len(blocked_items)})")
        for _, item in blocked_items.iterrows():
            with st.expander(f"**[{item['SOP_ID']}]** {item['SOP_Title']} — *{item['Compliance_Owner']}*", expanded=True):
                c_left, c_right = st.columns([3, 1])
                with c_left:
                    st.markdown(f"**What needs to change:** {item['Jira_Summary']}")
                    st.error(f"**Blocker / Dependency:** {item['Key_Blockers_or_Notes']}")
                with c_right:
                    st.markdown(f"**Status:** `{item['Jira_Status']}`")
                    st.markdown(f"**Requested by:** {item['Requesting_Stakeholder']}")
                    if item["Clean_Jira_URL"]:
                        st.markdown(f"🎫 [Open Jira Ticket ↗]({item['Clean_Jira_URL']})")
                    if item["Clean_Confluence_URL"]:
                        st.markdown(f"📄 [Open Document ↗]({item['Clean_Confluence_URL']})")

    # 2. In Progress section
    inprogress_items = display_df[display_df["Status_Group"] == "In Progress"]
    if len(inprogress_items) > 0:
        st.markdown(f"### 🔵 In Progress ({len(inprogress_items)})")
        for _, item in inprogress_items.iterrows():
            with st.expander(f"**[{item['SOP_ID']}]** {item['SOP_Title']} — *{item['Compliance_Owner']}*", expanded=False):
                c_left, c_right = st.columns([3, 1])
                with c_left:
                    st.markdown(f"**What needs to change:** {item['Jira_Summary']}")
                    st.info(f"**Next Steps:** {item['Key_Blockers_or_Notes']}")
                with c_right:
                    st.markdown(f"**Status:** `{item['Jira_Status']}`")
                    st.markdown(f"**Requested by:** {item['Requesting_Stakeholder']}")
                    if item["Clean_Jira_URL"]:
                        st.markdown(f"🎫 [Open Jira Ticket ↗]({item['Clean_Jira_URL']})")
                    if item["Clean_Confluence_URL"]:
                        st.markdown(f"📄 [Open Document ↗]({item['Clean_Confluence_URL']})")

    # 3. Backlog section
    backlog_items = display_df[display_df["Status_Group"] == "Backlog"]
    if len(backlog_items) > 0:
        st.markdown(f"### ⚪ Backlog ({len(backlog_items)})")
        for _, item in backlog_items.iterrows():
            with st.expander(f"**[{item['SOP_ID']}]** {item['SOP_Title']} — *{item['Compliance_Owner']}*", expanded=False):
                c_left, c_right = st.columns([3, 1])
                with c_left:
                    st.markdown(f"**What needs to change:** {item['Jira_Summary']}")
                    st.markdown(f"**Notes:** {item['Key_Blockers_or_Notes']}")
                with c_right:
                    st.markdown(f"**Status:** `{item['Jira_Status']}`")
                    st.markdown(f"**Requested by:** {item['Requesting_Stakeholder']}")
                    if item["Clean_Jira_URL"]:
                        st.markdown(f"🎫 [Open Jira Ticket ↗]({item['Clean_Jira_URL']})")
                    if item["Clean_Confluence_URL"]:
                        st.markdown(f"📄 [Open Document ↗]({item['Clean_Confluence_URL']})")

# --- TAB 2: SUMMARY CHARTS (Whole Integers Only) ---
with tab2:
    ch1, ch2 = st.columns(2)
    
    with ch1:
        st.markdown("#### Status Breakdown")
        status_data = filtered_df["Status_Group"].value_counts().reset_index()
        status_data.columns = ["Status", "Count"]
        
        fig_pie = px.pie(
            status_data,
            names="Status",
            values="Count",
            hole=0.55,
            color="Status",
            color_discrete_map={
                "Blocked / On Hold": "#D32F2F",
                "In Progress": "#1976D2",
                "Backlog": "#757575"
            }
        )
        fig_pie.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#E0E0E0",
            height=280
        )
        st.plotly_chart(fig_pie, use_container_width=True, config={"displayModeBar": False})

    with ch2:
        st.markdown("#### Workload by Owner")
        owner_data = filtered_df["Compliance_Owner"].value_counts().reset_index()
        owner_data.columns = ["Owner", "Count"]
        
        fig_owner = px.bar(
            owner_data,
            x="Owner",
            y="Count",
            text="Count",
            color="Owner",
            color_discrete_sequence=["#1976D2", "#0097A7"]
        )
        fig_owner.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#E0E0E0",
            height=280,
            showlegend=False,
            xaxis_title="",
            yaxis=dict(dtick=1, tick0=0, tickformat="d", title="Requests")
        )
        st.plotly_chart(fig_owner, use_container_width=True, config={"displayModeBar": False})

    st.markdown("#### Requests by Originating Team")
    team_data = filtered_df["Requesting_Team"].value_counts().reset_index()
    team_data.columns = ["Team", "Count"]
    
    fig_team = px.bar(
        team_data,
        x="Count",
        y="Team",
        orientation="h",
        text="Count",
        color_discrete_sequence=["#1976D2"]
    )
    fig_team.update_layout(
        margin=dict(t=10, b=10, l=10, r=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#E0E0E0",
        height=260,
        yaxis=dict(autorange="reversed", title=""),
        xaxis=dict(dtick=1, tick0=0, tickformat="d", title="Requests")
    )
    st.plotly_chart(fig_team, use_container_width=True, config={"displayModeBar": False})

# --- TAB 3: TABLE VIEW ---
with tab3:
    st.markdown("#### Master Log")
    
    table_df = filtered_df[[
        "SOP_ID", "SOP_Title", "Compliance_Owner", "Jira_Status", 
        "Requesting_Stakeholder", "Clean_Jira_URL", "Clean_Confluence_URL"
    ]].copy()
    
    st.dataframe(
        table_df,
        column_config={
            "SOP_ID": "ID",
            "SOP_Title": "Procedure Name",
            "Compliance_Owner": "Owner",
            "Jira_Status": "Status",
            "Requesting_Stakeholder": "Requested By",
            "Clean_Jira_URL": st.column_config.LinkColumn("Jira Ticket"),
            "Clean_Confluence_URL": st.column_config.LinkColumn("Document Link"),
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.download_button(
        label="📥 Download Log (CSV)",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name=f"compliance_sop_requests_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
