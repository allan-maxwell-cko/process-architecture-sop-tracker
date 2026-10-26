import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(
    page_title="Process Architecture | SOP Tracker",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Dataset
@st.cache_data
def load_data():
    df = pd.read_csv("sop_data.csv")
    df["Next_Review_Due"] = pd.to_datetime(df["Next_Review_Due"])
    return df

df = load_data()

# --- SIDEBAR DESIGN ---
st.sidebar.markdown("## 🛡️ Checkout.com")
st.sidebar.caption("Process Architecture Controls")
st.sidebar.info("👤 **Senior Lead:** Sunil Mudaliar")
st.sidebar.divider()

st.sidebar.subheader("🎯 Refine Dashboard")
domains = st.sidebar.multiselect("Select Domain(s)", options=sorted(df["Domain"].unique()), default=sorted(df["Domain"].unique()))
owners = st.sidebar.multiselect("Select Owner(s)", options=sorted(df["Owner"].unique()), default=sorted(df["Owner"].unique()))
statuses = st.sidebar.multiselect("Review Status", options=sorted(df["Status"].unique()), default=sorted(df["Status"].unique()))

st.sidebar.divider()
has_blocker = st.sidebar.toggle("⚠️ Show only active Jira blockers")

# Filter Logic
filtered_df = df[
    df["Domain"].isin(domains) & 
    df["Owner"].isin(owners) & 
    df["Status"].isin(statuses)
]
if has_blocker:
    filtered_df = filtered_df[filtered_df["Jira_Status"].isin(["In Progress", "To Do", "Open", "In Review"])]

# --- MAIN DASHBOARD HEADER ---
st.title("🧭 Process Architecture SOP Navigator")
st.markdown("**Governance & Review Hub** | Senior Lead: `Sunil Mudaliar`")
st.caption("Central registry tracking operational health, compliance audit readiness, and active delivery blockers across core business domains.")

# Executive Metric Cards
col1, col2, col3, col4 = st.columns(4)
total_count = len(filtered_df)
compliant_count = len(filtered_df[filtered_df["Status"] == "Compliant"])
overdue_count = len(filtered_df[filtered_df["Status"].isin(["Review Overdue", "Critical Action"])])
blocked_count = len(filtered_df[filtered_df["Jira_Status"].isin(["In Progress", "To Do", "Open", "In Review"])])

col1.metric("Tracked SOPs", total_count)
col2.metric("Compliant", compliant_count, delta="Audit Ready" if compliant_count > 0 else None)
col3.metric("Action Required", overdue_count, delta=f"-{overdue_count}" if overdue_count > 0 else None, delta_color="inverse")
col4.metric("Jira Blockers", blocked_count, delta=f"{blocked_count} Active" if blocked_count > 0 else "None", delta_color="inverse")

st.write("") 

# --- TABS FOR BETTER UX ---
tab1, tab2 = st.tabs(["📊 Executive Insights", "🗄️ Detailed SOP Registry"])

with tab1:
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        status_counts = filtered_df["Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        fig_donut = px.pie(
            status_counts, 
            names="Status", 
            values="Count", 
            hole=0.6, 
            title="SOP Compliance Status",
            color="Status",
            color_discrete_map={
                "Compliant": "#2E7D32", 
                "Needs Review": "#F9A825", 
                "Review Overdue": "#E65100", 
                "Critical Action": "#C62828"
            }
        )
        fig_donut.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            font_color="#FAFAFA",
            margin=dict(t=40, b=0, l=0, r=0)
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    with chart_col2:
        domain_counts = filtered_df["Domain"].value_counts().reset_index()
        domain_counts.columns = ["Domain", "Count"]
        fig_bar = px.bar(
            domain_counts, 
            x="Domain", 
            y="Count", 
            title="SOPs by Architecture Domain",
            color="Domain", 
            color_discrete_sequence=["#3F51B5", "#00ACC1", "#7E57C2", "#26A69A"]
        )
        fig_bar.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", 
            paper_bgcolor="rgba(0,0,0,0)", 
            font_color="#FAFAFA",
            margin=dict(t=40, b=0, l=0, r=0), 
            showlegend=False
        )
        st.plotly_chart(fig_bar, use_container_width=True)

with tab2:
    st.markdown("### Actionable SOP Roster")
    st.dataframe(
        filtered_df,
        column_config={
            "Confluence_URL": st.column_config.LinkColumn("Confluence Link"),
            "Next_Review_Due": st.column_config.DateColumn("Review Deadline", format="YYYY-MM-DD"),
            "Last_Reviewed": st.column_config.DateColumn("Last Reviewed", format="YYYY-MM-DD"),
            "SOP_ID": st.column_config.TextColumn("ID", width="small"),
            "Domain": st.column_config.TextColumn("Domain", width="medium"),
            "Domain_Lead": st.column_config.TextColumn("Lead", width="medium"),
            "Owner": st.column_config.TextColumn("Owner", width="medium"),
            "Status": st.column_config.TextColumn("Status", width="medium"),
            "Jira_Blocker": st.column_config.TextColumn("Blocker Key", width="small"),
            "Jira_Status": st.column_config.TextColumn("Ticket State", width="small"),
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.download_button(
        label="📥 Export Report to CSV",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name=f"pa_sop_report_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True
    )
