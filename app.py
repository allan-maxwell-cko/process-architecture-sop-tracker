import streamlit as st
import pandas as pd
from datetime import datetime
import re
import plotly.express as px

st.set_page_config(
    page_title="Checkout.com | Compliance SOP Navigator",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

def clean_url(val):
    if not isinstance(val, str):
        return None
    match = re.search(r'https?://[^\s)]+', val)
    return match.group(0) if match else None

def load_data():
    df = pd.read_csv("Compliance_SOP_Change_Requests.csv")
    df["Clean_Confluence_URL"] = df["Confluence_URL"].apply(clean_url)
    df["Clean_Jira_URL"] = df["Jira_Ticket"].apply(clean_url)
    return df

df = load_data()

# --- SIDEBAR ---
st.sidebar.markdown("## 🛡️ Checkout.com")
st.sidebar.caption("Process Architecture & Governance")
st.sidebar.markdown(
    """
    <div style="background-color: #1C1F26; padding: 12px; border-radius: 8px; border-left: 4px solid #3F51B5; margin-bottom: 16px;">
        <span style="font-size: 11px; text-transform: uppercase; color: #9E9E9E; letter-spacing: 0.5px;">Executive Oversight</span><br>
        <span style="font-size: 14px; font-weight: 600; color: #FAFAFA;">Sunil Mudaliar</span><br>
        <span style="font-size: 12px; color: #B0BEC5;">Senior Lead, Process Architecture</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.markdown(
    """
    <div style="background-color: #1C1F26; padding: 12px; border-radius: 8px; border-left: 4px solid #00ACC1; margin-bottom: 20px;">
        <span style="font-size: 11px; text-transform: uppercase; color: #9E9E9E; letter-spacing: 0.5px;">Domain Governance</span><br>
        <span style="font-size: 13px; font-weight: 600; color: #FAFAFA;">Bernard Ryan</span> <span style="font-size: 11px; color: #9E9E9E;">(Domain Lead)</span><br>
        <span style="font-size: 13px; font-weight: 600; color: #FAFAFA;">Allan Maxwell</span> <span style="font-size: 11px; color: #9E9E9E;">(Process Architecture)</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.sidebar.subheader("🎯 Filter Change Requests")
owner_filter = st.sidebar.multiselect("Compliance Owner", options=sorted(df["Compliance_Owner"].unique()), default=sorted(df["Compliance_Owner"].unique()))
status_filter = st.sidebar.multiselect("Jira Status", options=sorted(df["Jira_Status"].unique()), default=sorted(df["Jira_Status"].unique()))
priority_filter = st.sidebar.multiselect("Priority", options=sorted(df["Priority"].unique()), default=sorted(df["Priority"].unique()))

# Apply filters
filtered_df = df[
    df["Compliance_Owner"].isin(owner_filter) &
    df["Jira_Status"].isin(status_filter) &
    df["Priority"].isin(priority_filter)
]

# --- MAIN DASHBOARD HEADER ---
st.title("🛡️ Compliance SOP Governance & Change Navigator")
st.markdown("**Process Architecture Command Center** | Executive Oversight: `Sunil Mudaliar` | Domain Lead: `Bernard Ryan`")
st.caption("Centralized repository tracking stakeholder-driven change requests, Jira delivery blockers, and Confluence documentation updates across Compliance runbooks.")

# --- TOP KPI METRICS ---
total_requests = len(filtered_df)
in_progress_count = len(filtered_df[filtered_df["Jira_Status"].str.contains("In Progress", case=False, na=False)])
blocked_count = len(filtered_df[filtered_df["Jira_Status"].str.contains("Blocked", case=False, na=False)])
backlog_count = len(filtered_df[filtered_df["Jira_Status"].str.contains("Backlog", case=False, na=False) & ~filtered_df["Jira_Status"].str.contains("Blocked", case=False, na=False)])

c1, c2, c3, c4 = st.columns(4)
c1.metric("Active Change Requests", total_requests)
c2.metric("In Progress", in_progress_count, delta="Active Delivery" if in_progress_count > 0 else None)
c3.metric("Blocked / On Hold", blocked_count, delta=f"{blocked_count} Blocked" if blocked_count > 0 else "None", delta_color="inverse")
c4.metric("Backlog", backlog_count, delta="Queued" if backlog_count > 0 else None)

st.divider()

# --- TABS ---
tab1, tab2, tab3 = st.tabs([
    "📖 SOP Deep Dive & Change Repository",
    "📊 Governance Pulse & Blocker Insights",
    "📋 Master Change Request Roster"
])

# --- TAB 1: SOP DEEP DIVE ---
with tab1:
    st.subheader("🔍 Individual SOP Change Inspector")
    st.caption("Select an SOP below to inspect its full change dossier, linked Jira ticket, Confluence documentation, and active blockers.")
    
    if len(filtered_df) == 0:
        st.warning("No SOP change requests match the current sidebar filter settings.")
    else:
        sop_titles = [f"[{row['SOP_ID']}] {row['SOP_Title']}" for _, row in filtered_df.iterrows()]
        selected_sop_label = st.selectbox("Select Procedure / Change Request:", options=sop_titles, index=0)
        
        selected_id = selected_sop_label.split("]")[0].replace("[", "").strip()
        sop_record = filtered_df[filtered_df["SOP_ID"] == selected_id].iloc[0]
        
        status_val = str(sop_record["Jira_Status"])
        if "Blocked" in status_val:
            badge_color = "#C62828"
        elif "In Progress" in status_val:
            badge_color = "#1565C0"
        else:
            badge_color = "#F57C00"
            
        st.markdown(
            f"""
            <div style="background-color: #1C1F26; border-radius: 10px; padding: 20px; border: 1px solid #2D3748; margin-top: 10px; margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <span style="font-size: 19px; font-weight: 700; color: #FAFAFA;">{sop_record['SOP_Title']}</span>
                    <span style="background-color: {badge_color}; color: white; padding: 4px 12px; border-radius: 12px; font-size: 12px; font-weight: 600;">{sop_record['Jira_Status']}</span>
                </div>
                <div style="display: flex; flex-wrap: wrap; gap: 20px; font-size: 13px; color: #B0BEC5;">
                    <div><strong>Ticket Key:</strong> <code style="color: #64B5F6;">{sop_record['SOP_ID']}</code></div>
                    <div><strong>Priority:</strong> <span style="color: #FFB74D;">{sop_record['Priority']}</span></div>
                    <div><strong>Compliance Owner:</strong> <span style="color: #FAFAFA;">{sop_record['Compliance_Owner']}</span></div>
                    <div><strong>Requesting Stakeholder:</strong> <span style="color: #81C784;">{sop_record['Requesting_Stakeholder']}</span></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col_left, col_right = st.columns([3, 2])
        
        with col_left:
            st.markdown("#### 📝 Requested Update Scope")
            st.info(f"**Stakeholder Request:** {sop_record['Jira_Summary']}")
            
            st.markdown("#### 🚨 Key Blockers & Operational Dependencies")
            if "Blocked" in status_val or "hold" in status_val.lower():
                st.error(f"**Critical Dependency:** {sop_record['Key_Blockers_or_Notes']}")
            else:
                st.warning(f"**Status / Next Step:** {sop_record['Key_Blockers_or_Notes']}")
                
        with col_right:
            st.markdown("#### 🔗 Direct Launch Links")
            
            if sop_record["Clean_Jira_URL"]:
                st.markdown(f"🎫 **Jira Ticket:** [{sop_record['SOP_ID']} on Atlassian ↗]({sop_record['Clean_Jira_URL']})")
            else:
                st.markdown(f"🎫 **Jira Ticket:** `{sop_record['Jira_Ticket']}`")
                
            if sop_record["Clean_Confluence_URL"]:
                if "docs.google.com" in sop_record["Clean_Confluence_URL"]:
                    st.markdown(f"📄 **Working Draft:** [Open Google Doc Draft ↗]({sop_record['Clean_Confluence_URL']})")
                else:
                    st.markdown(f"📄 **Confluence Page:** [Open Confluence Runbook ↗]({sop_record['Clean_Confluence_URL']})")
            else:
                st.caption(f"ℹ️ **Doc State:** {sop_record['Confluence_URL']}")
                
            st.markdown("---")
            st.markdown("#### 👥 Governance Matrix")
            st.markdown("- **Domain Lead:** Bernard Ryan")
            st.markdown(f"- **Action Assignee:** {sop_record['Compliance_Owner']}")
            st.markdown(f"- **Requesting Origin:** {sop_record['Requesting_Stakeholder']}")

# --- TAB 2: EXECUTIVE PULSE & CHARTS ---
with tab2:
    st.subheader("📊 Governance Pulse & Stakeholder Distribution")
    chart_c1, chart_c2 = st.columns(2)
    
    with chart_c1:
        st.markdown("#### Delivery Pipeline Breakdown")
        status_counts = filtered_df["Jira_Status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]
        
        fig_status = px.pie(
            status_counts,
            names="Status",
            values="Count",
            hole=0.55,
            color="Status",
            color_discrete_sequence=["#1565C0", "#C62828", "#F57C00", "#7E57C2", "#00897B"]
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
        st.markdown("#### Workload by Compliance Owner")
        owner_counts = filtered_df["Compliance_Owner"].value_counts().reset_index()
        owner_counts.columns = ["Owner", "Count"]
        
        fig_owner = px.bar(
            owner_counts,
            x="Owner",
            y="Count",
            color="Owner",
            color_discrete_sequence=["#3F51B5", "#00ACC1"]
        )
        fig_owner.update_layout(
            margin=dict(t=20, b=20, l=20, r=20),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="#FAFAFA",
            height=280,
            showlegend=False,
            xaxis_title="",
            yaxis_title="Change Requests"
        )
        st.plotly_chart(fig_owner, use_container_width=True, config={"displayModeBar": False})
        
    st.markdown("#### Originating Stakeholders")
    stakeholder_counts = filtered_df["Requesting_Stakeholder"].value_counts().reset_index()
    stakeholder_counts.columns = ["Stakeholder", "Count"]
    fig_sh = px.bar(
        stakeholder_counts,
        x="Count",
        y="Stakeholder",
        orientation="h",
        color="Count",
        color_continuous_scale="Viridis"
    )
    fig_sh.update_layout(
        margin=dict(t=10, b=10, l=20, r=20),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font_color="#FAFAFA",
        height=320,
        coloraxis_showscale=False,
        yaxis=dict(autorange="reversed")
    )
    st.plotly_chart(fig_sh, use_container_width=True, config={"displayModeBar": False})

# --- TAB 3: MASTER ROSTER ---
with tab3:
    st.subheader("📋 Master Compliance SOP Change Request Roster")
    st.caption("Full audit log of active stakeholder-requested modifications and their resolution status.")
    
    table_display = filtered_df[[
        "SOP_ID",
        "SOP_Title",
        "Compliance_Owner",
        "Jira_Status",
        "Priority",
        "Requesting_Stakeholder",
        "Clean_Jira_URL",
        "Clean_Confluence_URL"
    ]].copy()
    
    st.dataframe(
        table_display,
        column_config={
            "SOP_ID": st.column_config.TextColumn("Ticket ID", width="small"),
            "SOP_Title": st.column_config.TextColumn("SOP Title / Change Target", width="large"),
            "Compliance_Owner": st.column_config.TextColumn("Owner", width="medium"),
            "Jira_Status": st.column_config.TextColumn("Status", width="small"),
            "Priority": st.column_config.TextColumn("Priority", width="small"),
            "Requesting_Stakeholder": st.column_config.TextColumn("Stakeholder", width="medium"),
            "Clean_Jira_URL": st.column_config.LinkColumn("Jira Ticket"),
            "Clean_Confluence_URL": st.column_config.LinkColumn("Confluence / Doc"),
        },
        hide_index=True,
        use_container_width=True
    )
    
    st.download_button(
        label="📥 Export Compliance Governance Log (.csv)",
        data=filtered_df.to_csv(index=False).encode('utf-8'),
        file_name=f"compliance_sop_governance_log_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
