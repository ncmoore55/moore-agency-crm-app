# My agency-crm-app

# Import the Streamlit library to build the web application
import streamlit as st

# Import our database connection function from database.py
import database

# Import pandas for displaying SQL data in tables
import pandas as pd

# Import altair for the two dashboard charts (bundled with Streamlit already)
import altair as alt

# Shared page styling (rounded cards, buttons, etc.) + the KPI bubble-card helper
from utils import styles

# Configure the page settings
st.set_page_config(
    page_title="Nik's Web Design CRM",
    page_icon="💼",
    layout="wide"
)

styles.inject_css()

# Sidebar title (real page navigation comes from the pages/ folder)
st.sidebar.title("Nik's Web Design CRM")

st.title("🏢 Nik's Web Design CRM")
st.caption("Professional Client & Project Management System")

# Dashboard Section
st.header("📊 Dashboard")

# Load lead counts by status from MySQL
total_leads = len(database.fetch_data("SELECT lead_id FROM leads"))

new_leads = len(database.fetch_data("SELECT lead_id FROM leads WHERE lead_status = 'New Lead'"))
contacted = len(database.fetch_data("SELECT lead_id FROM leads WHERE lead_status = 'Contacted'"))
interested = len(database.fetch_data("SELECT lead_id FROM leads WHERE lead_status = 'Interested'"))
website_building = len(database.fetch_data("SELECT lead_id FROM leads WHERE lead_status = 'Website Building'"))
demo_sent = len(database.fetch_data("SELECT lead_id FROM leads WHERE lead_status = 'Demo Sent'"))
negotiating = len(database.fetch_data("SELECT lead_id FROM leads WHERE lead_status = 'Negotiating'"))
paid = len(database.fetch_data("SELECT lead_id FROM leads WHERE lead_status = 'Paid'"))
completed = len(database.fetch_data("SELECT lead_id FROM leads WHERE lead_status = 'Completed'"))
not_interested = len(database.fetch_data("SELECT lead_id FROM leads WHERE lead_status = 'Not Interested'"))

open_tasks = len(database.fetch_data("""
SELECT task_id FROM tasks
WHERE status != 'Completed'
"""))

total_interactions = len(database.fetch_data("""
SELECT interactions_id FROM interactions
"""))

# Estimated revenue = sum of every price quoted so far, regardless of payment status
revenue_row = database.fetch_data("SELECT SUM(price_quoted) AS total FROM leads").iloc[0]
estimated_revenue = revenue_row["total"] if revenue_row["total"] else 0

# Display KPI cards (row 1) - colored bubble cards instead of plain st.metric
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    styles.kpi_card("👥", total_leads, "Total Leads", "violet")

with col2:
    styles.kpi_card("⚪", new_leads, "New Leads", "gray")

with col3:
    styles.kpi_card("🟡", contacted, "Contacted", "amber")

with col4:
    styles.kpi_card("🟢", interested, "Interested", "emerald")

with col5:
    styles.kpi_card("🟠", website_building, "Website Building", "amber")

# Display KPI cards (row 2)
col6, col7, col8, col9, col10 = st.columns(5)

with col6:
    styles.kpi_card("🔵", demo_sent, "Demo Sent", "blue")

with col7:
    styles.kpi_card("💰", paid, "Paid Clients", "emerald")

with col8:
    styles.kpi_card("📈", f"${estimated_revenue:,.2f}", "Estimated Revenue", "violet")

with col9:
    styles.kpi_card("📋", open_tasks, "Open Tasks", "rose")

with col10:
    styles.kpi_card("📞", total_interactions, "Interactions", "blue")

st.divider()

st.subheader("📊 Lead Pipeline")

# =====================================================
# Display the lead pipeline using progress bars
# =====================================================

total = max(total_leads, 1)

st.write(f"⚪ New Lead ({new_leads})")
st.progress(new_leads / total)

st.write(f"🟡 Contacted ({contacted})")
st.progress(contacted / total)

st.write(f"🟢 Interested ({interested})")
st.progress(interested / total)

st.write(f"🟠 Website Building ({website_building})")
st.progress(website_building / total)

st.write(f"🔵 Demo Sent ({demo_sent})")
st.progress(demo_sent / total)

st.write(f"🟣 Negotiating ({negotiating})")
st.progress(negotiating / total)

st.write(f"💰 Paid ({paid})")
st.progress(paid / total)

st.write(f"✅ Completed ({completed})")
st.progress(completed / total)

st.write(f"🔴 Not Interested ({not_interested})")
st.progress(not_interested / total)

# =====================================================
# CHARTS - monthly lead growth + status breakdown
# =====================================================

st.divider()
chart_col1, chart_col2 = st.columns([3, 2])

with chart_col1:
    with st.container(border=True):
        st.subheader("📈 Monthly Lead Growth")

        monthly_df = database.fetch_data("""
        SELECT
            DATE_FORMAT(created_at, '%Y-%m') AS month,
            COUNT(*) AS leads_added
        FROM leads
        WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
        GROUP BY month
        ORDER BY month
        """)

        # Fill in any months with zero leads so the line doesn't skip gaps
        last_6_months = pd.period_range(end=pd.Timestamp.today(), periods=6, freq="M").astype(str)
        monthly_df = (
            pd.DataFrame({"month": last_6_months})
            .merge(monthly_df, on="month", how="left")
            .fillna(0)
        )

        chart = (
            alt.Chart(monthly_df)
            .mark_line(point=True, color="#8B5CF6")
            .encode(
                x=alt.X("month:N", title=None),
                y=alt.Y("leads_added:Q", title="Leads Added"),
                tooltip=["month", "leads_added"]
            )
        )
        st.altair_chart(chart, use_container_width=True)

with chart_col2:
    with st.container(border=True):
        st.subheader("🥧 Leads by Status")

        status_df = database.fetch_data("""
        SELECT lead_status, COUNT(*) AS count
        FROM leads
        GROUP BY lead_status
        """)

        if status_df.empty:
            st.info("No leads yet.")
        else:
            donut = (
                alt.Chart(status_df)
                .mark_arc(innerRadius=55)
                .encode(
                    theta="count:Q",
                    color=alt.Color("lead_status:N", legend=alt.Legend(title=None)),
                    tooltip=["lead_status", "count"]
                )
            )
            st.altair_chart(donut, use_container_width=True)

# =====================================================
# TODAY'S TASKS
# =====================================================
# Show the next 5 open follow-up tasks so the dashboard
# tells us what needs attention first.

tasks_today = database.fetch_data("""
SELECT
    task_name,
    due_date,
    status
FROM tasks
WHERE status != 'Completed'
ORDER BY due_date ASC
LIMIT 5
""")

st.divider()
st.subheader("📋 Today's Tasks")

if tasks_today.empty:
    st.info("No open tasks right now 🎉")
else:
    for _, row in tasks_today.iterrows():

        # Format the due date so it is easier to read
        formatted_due = row["due_date"].strftime("%B %d, %Y")

        with st.container(border=True):
            st.markdown(f"### ☐ {row['task_name']}")
            st.caption(f"Due: {formatted_due}")
            st.write(f"**Status:** {row['status']}")


# =====================================================
# RECENT ACTIVITY
# =====================================================
# Show the 5 most recent interactions from all leads.

recent_activity = database.fetch_data("""
SELECT
    interaction_type,
    outcome,
    subject,
    interaction_date
FROM interactions
ORDER BY interaction_date DESC
LIMIT 5
""")

st.divider()
st.subheader("📞 Recent Activity")

if recent_activity.empty:
    st.info("No recent activity yet.")
else:
    for _, row in recent_activity.iterrows():

        # Format the interaction date for a cleaner dashboard
        formatted_date = row["interaction_date"].strftime("%B %d, %Y • %I:%M %p")

        with st.container(border=True):
            st.markdown(f"### 📞 {row['interaction_type']}")
            st.caption(formatted_date)
            st.write(f"**Outcome:** {row['outcome']}")
            st.write(f"**Subject:** {row['subject']}")

# =====================================================
# QUICK ACTIONS
# =====================================================
# Shortcuts to common actions.

st.divider()
st.subheader("⚡ Quick Actions")

col1, col2, col3 = st.columns(3)

with col1:
    st.page_link("pages/1_👥_Leads.py", label="➕ Add Lead")

with col2:
    st.page_link("pages/1_👥_Leads.py", label="📞 Log Interaction")

with col3:
    st.page_link("pages/1_👥_Leads.py", label="📋 Add Task")
