# My agency-crm-app

# Import the Streamlit library to build the web application
import streamlit as st

# Import our database connection function from database.py
import database

# Import pandas for displaying SQL data in tables
import pandas as pd

# Configure the page settings
st.set_page_config(
    page_title="Nik's Web Design CRM",
    page_icon="💼",
    layout="wide"
)

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

# Display KPI cards (row 1)
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("👥 Total Leads", total_leads)

with col2:
    st.metric("⚪ New Leads", new_leads)

with col3:
    st.metric("🟡 Contacted", contacted)

with col4:
    st.metric("🟢 Interested", interested)

with col5:
    st.metric("🟠 Website Building", website_building)

# Display KPI cards (row 2)
col6, col7, col8, col9, col10 = st.columns(5)

with col6:
    st.metric("🔵 Demo Sent", demo_sent)

with col7:
    st.metric("💰 Paid Clients", paid)

with col8:
    st.metric("📈 Estimated Revenue", f"${estimated_revenue:,.2f}")

with col9:
    st.metric("📋 Open Tasks", open_tasks)

with col10:
    st.metric("📞 Interactions", total_interactions)

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
