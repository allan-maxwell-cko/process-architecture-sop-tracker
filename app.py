import streamlit as st
import pandas as pd
from datetime import datetime
import re
import plotly.express as px

st.set_page_config(
    page_title="Compliance SOP Updates",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def clean_url(val):
    if not isinstance(val, str):
        return None
    match = re.search(r'https?://[^\s)]+', val)
    return match.group(0) if match else None

@st.cache_data(ttl=60)
def load_data():
    df = pd.read_csv("Compliance_SOP_Change_Requests.csv")
    df["Clean_Confluence_URL"] = df["Confluence_URL"].apply(clean_url)
    df["Clean_Jira_URL"] = df["Jira_Ticket"].apply(clean_url)
    return df

df = load_data()

# --- SIDEBAR ---
st.sidebar.markdown("## 🛡️ Checkout.com")
st.sidebar.caption("Compliance Process Architecture")
st.sidebar.divider()

st.sidebar.markdown("**Senior Lead:** Sunil Mudaliar")
st.sidebar.markdown("**Domain Lead:** Bernard Ryan")
st.sidebar.divider()

# Hidden Filters (Dropdown)
with st.sidebar.expander("🔍 Filter Requests", expanded=False):
    owner_filter = st.multiselect("Owner", options=sorted(df["Compliance_Owner"].unique()), default=sorted(df["Compliance_Owner"].unique()))
    status_filter = st.multiselect("Status", options=sorted(df["Jira_Status"].unique()), default=sorted(df["Jira_Status"].unique()))
    priority_filter = st.multiselect("Priority", options=sorted(df["Priority"].unique()), default=sorted(df["Priority"].unique()))

# Apply filters
filtered_df = df[
    df["Compliance_Owner"].isin(owner_filter) &
    df["Jira_Status"].isin(status_filter) &
    df["Priority"].isin(priority_filter)
]

# --- MAIN HEADER ---
st.title("Compliance SOP Updates")
st.caption("Track and manage requested changes to Compliance procedures and runbooks.")

# --- METRICS ---
total_requests = len(filtered_df)
in_progress_count = len(filtered_df[filtered_df["Jira_Status"].str.contains("In Progress", case=False, na=False)])
blocked_count = len(filtered_df[filtered_df["Jira_Status"].str.contains("Blocked", case=False, na=False)])
backlog_count = len(filtered_df[filtered_df["Jira_Status"].str.contains("Backlog", case=False, na=False) & ~filtered_df["Jira_Status"].str.contains("Blocked", case=False, na=False)])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Requests", total_requests)
c2.metric("In Progress", in_progress_count)
c3.metric("Blocked", blocked_count)
c4.metric("Backlog", backlog_count)

st.divider()

# --- TABS (Plain English) ---
tab1, tab2, tab3 = st.tabs(["View Request Details", "Dashboard", "Full List"])

# --- TAB 1: DETAILS ---
with tab1:
    if len(filtered_df) == 0:
        st.warning("No requests match your filters.")
    else:
        sop_titles = [f"[{row['SOP_ID']}] {row['SOP_Title']}" for _, row in filtered_df.iterrows()]
        selected_sop_label = st.selectbox("Select a request:", options=sop_titles, index=0)
        
        selected_id = selected_sop_label.split("]")[0].replace("[", "").strip()
        sop_record = filtered_df[filtered_df["SOP_ID"] == selected_id].iloc[0]
        
        st.subheader(sop_record['SOP_Title'])
        
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.markdown("##### What needs to change")
            st.info(sop_record['Jira_Summary'])
            
            st.markdown("##### Blockers and next steps")
            if "Blocked" in str(sop_record["Jira_Status"]):
                st.error(sop_record['Key_Blockers_or_Notes'])
            else:
                st.warning(sop_record['Key_Blockers_or_Notes'])
                
        with col_right:
            st.markdown("##### Details")
            st.markdown(f"- **Status:** {sop_record['Jira_Status']}")
            st.markdown(f"- **Owner:** {sop_record['Compliance_Owner']}")
            st.markdown(f"- **Requested by:** {sop_record['Requesting_Stakeholder']}")
            
            st.markdown("##### Links")
            if sop_record["Clean_Jira_URL"]:
                st.markdown(f"🎫 [View Jira Ticket]({sop_record['Clean_Jira_URL']})")
            
            if sop_record["Clean_Confluence_URL"]:
                st.markdown(f"📄 [View Document]({sop_record['Clean_Confluence_URL']})")

# --- TAB 2: DASHBOARD ---
with tab2:
    chart_c1, chart_c2 = st.columns(2)
    
    # Unified, softer color palette for charts
    chart_colors = ["#2962FF", "#00B0FF", "#1DE9B6", "#F50057", "#FFC400"]
    
    with chart_c1:
        st.markdown("##### Requests by Status")
        status_counts = filtered_df["Jira_Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        
        fig_status = px.pie(status_counts, names="Status", values="Count", hole=0.6, color_discrete_sequence=chart_colors)
        fig_status.update_layout(margin=dict(t=20, b=20, l=20, r=20), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#E0E0E0", height=300)
        st.plotly_chart(fig_status, use_container_width=True, config={"displayModeBar": False})
        
    with chart_c2:
        st.markdown("##### Workload by Owner")
        owner_counts = filtered_df["Compliance_Owner"].value_counts().reset_index()
        owner_counts.columns = ["Owner", "Count"]
        
        fig_owner = px.bar(owner_counts, x="Owner", y="Count", color="Owner", color_discrete_sequence=chart_colors)
        fig_owner.update_layout(margin=dict(t=20, b=20, l=20, r=20), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#E0E0E0", height=300, showlegend=False, xaxis_title="", yaxis_title="Count")
        st.plotly_chart(fig_owner, use_container_width=True, config={"displayModeBar": False})
        
    st.markdown("##### Requested by")
    stakeholder_counts = filtered_df["Requesting_Stakeholder"].value_counts().reset_index()
    stakeholder_counts.columns = ["Stakeholder", "Count"]
    fig_sh = px.bar(stakeholder_counts, x="Count", y="Stakeholder", orientation="h", color_discrete_sequence=["#2962FF"])
    fig_sh.update_layout(margin=dict(t=10, b=10, l=10, r=10), plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)", font_color="#E0E0E0", height=250, yaxis=dict(autorange="reversed"), xaxis_title="Count", yaxis_title="")
    st.plotly_chart(fig_sh, use_container_width=True, config={"displayModeBar": False})

# --- TAB 3: FULL LIST ---
with tab3:
    table_display = filtered_df[[
        "SOP_ID", "SOP_Title", "Compliance_Owner", "Jira_Status", 
        "Priority", "Requesting_Stakeholder", "Clean_Jira_URL", "Clean_Confluence_URL"
    ]].copy()
    
    st.dataframe(
        table_display,
        column_config={
            "SOP_ID": "ID",
            "SOP_Title": "Title",
            "Compliance_Owner": "Owner",
            "Jira_Status": "Status",
            "Priority": "Priority",
            "Requesting_Stakeholder": "Requested By",
            "Clean_Jira_URL": st.column_config.LinkColumn("Jira"),
            "Clean_Confluence_URL": st.column_config.LinkColumn("Document"),
        },
        hide_index=True,
        use_container_width=True
    )
