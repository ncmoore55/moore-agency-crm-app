# My agency-crm-app 

# Import the Streamlit library to build the web application
import streamlit as st

# Import our database connection function from database.py
import database

# Import pandas for displaying SQL data in tables
import pandas as pd


st.set_page_config(page_title="Agency CRM", layout="wide")

st.title("🏢 Moore Agency CRM")
st.caption("Professional Client & Project Management System")

# Dashboard Section
st.header("📊 Dashboard")

# Load dashboard data from MySQL
total_leads = len(database.fetch_data("SELECT lead_id FROM leads"))

interested_leads = len(database.fetch_data("""
SELECT lead_id FROM leads
WHERE lead_status = 'Interested'
"""))

clients = len(database.fetch_data("""
SELECT lead_id FROM leads
WHERE lead_status = 'Client'
"""))

open_tasks = len(database.fetch_data("""
SELECT task_id FROM tasks
WHERE status != 'Completed'
"""))

total_interactions = len(database.fetch_data("""
SELECT interactions_id FROM interactions
"""))

# Display KPI cards
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("👥 Total Leads", total_leads)

with col2:
    st.metric("🟢 Interested", interested_leads)

with col3:
    st.metric("🔵 Clients", clients)

with col4:
    st.metric("📋 Open Tasks", open_tasks)

with col5:
    st.metric("📞 Interactions", total_interactions)

st.divider()

st.subheader("📊 Lead Pipeline")

new_leads = len(database.fetch_data("""
SELECT lead_id FROM leads
WHERE lead_status = 'New Lead'
"""))

contacted = len(database.fetch_data("""
SELECT lead_id FROM leads
WHERE lead_status = 'Contacted'
"""))

interested = len(database.fetch_data("""
SELECT lead_id FROM leads
WHERE lead_status = 'Interested'
"""))

clients = len(database.fetch_data("""
SELECT lead_id FROM leads
WHERE lead_status = 'Client'
"""))

# =====================================================
# Display the lead pipeline using progress bars
# =====================================================

total = max(total_leads, 1)

st.write(f"⚪ New Leads ({new_leads})")
st.progress(new_leads / total)

st.write(f"🟡 Contacted ({contacted})")
st.progress(contacted / total)

st.write(f"🟢 Interested ({interested})")
st.progress(interested / total)

st.write(f"🔵 Clients ({clients})")
st.progress(clients / total)

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