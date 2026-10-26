import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(
    page_title="Checkout.com | Process Architecture",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load data without persistent caching to prevent stale ECS data
def load_data():
    df = pd.read_csv("sop_data.csv")
    df["Next_Review_Due"] = pd.to_datetime(df["Next_Review_Due"])
    df["Last_Reviewed"] = pd.to_datetime(df["Last_Reviewed"])
    return df

df = load_data()

# --- SIDEBAR GOVERNANCE PANEL ---
st.sidebar.markdown("## 🛡️ Checkout.com")
st.sidebar.caption("Process Architecture & Governance")
st.sidebar.markdown(
    """
    <div style="background-color: #1C1F26; padding: 12px; border-radius: 8px; border-left: 4px solid #3F51B5; margin-bottom: 20px;">
        <span style="font-size: 11px; text-transform: uppercase; color: #9E9E9E; letter-spacing: 0.5px;">Executive Oversight</span><br>
        <span style="font-size: 14px; font-weight: 600; color: #FAFAFA;">Sunil Mudaliar</span><br>
        <span style="font-size: 12px; color: #B0BEC5;">Senior Lead, Process Architecture</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.subheader("🎯 Scope & Domain")
selected_domain = st.sidebar.selectbox(
    "Active Architecture Domain",
    options=["Compliance (Pilot)", "All Domains", "Merchant Ops", "Risk", "Finance Ops"],
    index=0
)

# Domain filter mapping
if selected_domain == "Compliance (Pilot)":
    scoped_df = df[df["Domain"] == "Compliance"]
elif selected_domain == "All Domains":
    scoped_df = df
else:
    scoped_df = df[df["Domain"] == selected_domain]

# Secondary filters
owners = st.sidebar.multiselect("Owner", options=sorted(scoped_df["Owner"].unique()), default=sorted(scoped_df["Owner"].unique()))
statuses = st.sidebar.multiselect("Status", options=sorted(scoped_df["Status"].unique()), default=sorted(scoped_df["Status"].unique()))
only_blockers = st.sidebar.toggle("⚠️ Show only active blockers")

# Apply filters
filtered_df = scoped_df[scoped_df["Owner"].isin(owners) & scoped_df["Status"].isin(statuses)]
if only_blockers:
    filtered_df = filtered_df[filtered_df["Jira_Status"].isin(["In Progress", "To Do", "Open", "In Review"])]

# --- MAIN DASHBOARD ---
st.title("🛡️ Process Architecture SOP Navigator")
lead_name = "Bernard Ryan" if selected_domain in ["Compliance (Pilot)", "Compliance"] else "All Domain Leads"
st.caption(f"Domain Focus: **{selected_domain}** | Domain Lead: **{lead_name}** | Senior Lead: **Sunil Mudaliar**")

# Top KPI Metric Row
total_sops = len(filtered_df)
compliant_sops = len(filtered_df[filtered_df["Status"] == "Compliant"])
action_required = len(filtered_df[filtered_df["Status"].isin(["Review Overdue", "Critical Action"])])
active_blockers = len(filtered_df[filtered_df["Jira_Status"].isin(["In Progress", "To Do", "Open", "In Review"])])

health_ratio = (compliant_sops / total_sops * 100) if total_sops > 0 else 0

c1, c2, c3, c4 = st.columns(4)
c1.metric("Active SOPs Tracked", total_sops)
c2.metric("Audit Ready Rate", f"{health_ratio:.0f}%", delta="Target: 95%")
c3.metric("Review Overdue", action_required, delta=f"-{action_required}" if action_required > 0 else "0", delta_color="inverse")
c4.metric("Jira Delivery Blockers", active_blockers, delta=f"{active_blockers} Issues" if active_blockers > 0 else "None", delta_color="inverse")

st.divider()

# --- TABS: VISUAL INSIGHTS vs REGISTRY ---
tab1, tab2 = st.tabs(["📊 Compliance Health & Breakdown", "📋 Operational SOP Roster"])

with tab1:
    chart_c1, chart_c2 = st.columns(2)
    
    with chart_c1:
        st.markdown("#### Review Status Distribution")
        status_data = filtered_df["Status"].value_counts().reset_index()
        status_data.columns = ["Status", "Count"]
        
        fig_status = px.pie(
            status_data, 
            names="Status", 
            values="Count", 
            hole=0.55,
            color="Status",
            color_discrete_map={
                "Compliant": "#2E7D32",
                "Needs Review": "#F9A825",
                "Review Overdue": "#E65100",
                "Critical Action": "#C62828"
            }
        )
        fig_status.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#FAFAFA",
            height=280
        )
        st.plotly_chart(fig_status, use_container_width=True, config={"displayModeBar": False})

    with chart_c2:
        st.markdown("#### SOP Risk Classification")
        if "Risk_Level" in filtered_df.columns:
            risk_data = filtered_df["Risk_Level"].value_counts().reset_index()
            risk_data.columns = ["Risk_Level", "Count"]
            
            fig_risk = px.bar(
                risk_data,
                x="Risk_Level",
                y="Count",
                color="Risk_Level",
                color_discrete_map={
                    "Critical": "#C62828",
                    "High": "#E65100",
                    "Medium": "#3F51B5",
                    "Low": "#2E7D32"
                }
            )
            fig_risk.update_layout(
                margin=dict(t=20, b=20, l=20, r=20),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#FAFAFA",
                height=280,
                showlegend=False,
                xaxis_title="",
                yaxis_title="Count"
            )
            st.plotly_chart(fig_risk, use_container_width=True, config={"displayModeBar": False})

with tab2:
    st.markdown("#### Active Registry & Governance Links")
    st.dataframe(
        filtered_df,
        column_config={
            "Confluence_URL": st.column_config.LinkColumn("Confluence Documentation"),
            "Next_Review_Due": st.column_config.DateColumn("Review Due", format="YYYY-MM-DD"),
            "Last_Reviewed": st.column_config.DateColumn("Last Validated", format="YYYY-MM-DD"),
            "SOP_ID": st.column_config.TextColumn("SOP Code", width="small"),
            "Risk_Level": st.column_config.TextColumn("Regulatory Risk", width="small"),
            "Jira_Blocker": st.column_config.TextColumn("Blocker Ticket", width="small"),
            "Jira_Status": st.column_config.TextColumn("Blocker State", width="small"),
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.download_button(
        label="📥 Export Compliance Report (.csv)",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name=f"compliance_sop_audit_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
