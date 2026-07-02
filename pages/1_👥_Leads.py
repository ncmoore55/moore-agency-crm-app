# Import Streamlit to build the page
import streamlit as st

# Import Pandas for displaying database results
import pandas as pd

# Import our reusalbe database functions
import database

def status_icon(status):
    icons = {
        "New Lead": "⚪ New Lead",
        "Contacted": "🟡 Contacted",
        "Interested": "🟢 Interested",
        "Not Interested": "🔴 Not Interested",
        "Client": "🔵 Client",
        "Pending": "🟡 Pending",
        "In Progress": "🟠 In Progress",
        "Completed": "✅ Completed"
    }

    return icons.get(status, status)

st.set_page_config(page_title="Leads | Moore Agency CRM", layout="wide")

st.title("👥 Leads")
st.caption("Manage Potential clients and outreach opportunities.")

with st.expander("➕ Add New Lead"):

    with st.form("add_lead_form"):
        business_name = st.text_input("Business Name")
        industry = st.text_input("Industry")
        contact_name = st.text_input("Contact Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
        city = st.text_input("City")
        state = st.text_input("State")
        website_url = st.text_input("Website URL")
        website_status = st.selectbox("Website Status", ["No Website", "Outdated Website", "Good Website", "Unknown"])
        lead_status = st.selectbox("Lead Status", ["New Lead", "Contacted", "Interested", "Not Interested", "Client"])
        source = st.text_input("Source")
        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Add Lead")

        if submitted:
            conn = database.get_connection()
            cursor = conn.cursor()

            sql = """
            INSERT INTO leads (
                business_name, industry, contact_name, email, phone,
                city, state, website_url, website_status, lead_status,
                source, notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                business_name, industry, contact_name, email, phone,
                city, state, website_url, website_status, lead_status,
                source, notes
            )

            database.run_query(sql, values)

            st.success("Lead added successfully!")
        
st.divider()

# Search Bar
search = st.text_input("🔍 Search Leads")

status_filter = st.selectbox(
    "Filter by Status",
    ["All", "New Lead", "Contacted", "Interested", "Not Interested", "Client"],
    key="status_filter"
)

st.subheader("All Leads")

# Retrieve all leads from MySQL
if search and status_filter != "All":
    df = database.fetch_data(f"""
    SELECT
        lead_id,
        business_name,
        contact_name,
        phone,
        city,
        website_status,
        lead_status
    FROM leads
    WHERE (
        business_name LIKE '%{search}%'
        OR contact_name LIKE '%{search}%'
        OR city LIKE '%{search}%'
        OR lead_status LIKE '%{search}%'
    )
    AND lead_status = '{status_filter}'
    ORDER BY created_at DESC
    """)

elif search:
    df = database.fetch_data(f"""
    SELECT
        lead_id,
        business_name,
        contact_name,
        phone,
        city,
        website_status,
        lead_status
    FROM leads
    WHERE business_name LIKE '%{search}%'
       OR contact_name LIKE '%{search}%'
       OR city LIKE '%{search}%'
       OR lead_status LIKE '%{search}%'
    ORDER BY created_at DESC
    """)

elif status_filter != "All":
    df = database.fetch_data(f"""
    SELECT
        lead_id,
        business_name,
        contact_name,
        phone,
        city,
        website_status,
        lead_status
    FROM leads
    WHERE lead_status = '{status_filter}'
    ORDER BY created_at DESC
    """)

else:
    df = database.fetch_data("""
    SELECT
        lead_id,
        business_name,
        contact_name,
        phone,
        city,
        website_status,
        lead_status
    FROM leads
    ORDER BY created_at DESC
    """)

# Select a lead to view
selected_lead_name = st.selectbox(
    "Select a Lead",
    df["business_name"]
)

selected_lead_id = df[df["business_name"] == selected_lead_name]["lead_id"].iloc[0]

# Display the leads
st.dataframe(df, use_container_width=True)

st.divider()


st.divider()
st.subheader("Interaction History")

interaction_sql = f"""
SELECT
    interaction_date,
    interaction_type,
    outcome,
    subject,
    notes
FROM interactions
WHERE lead_id = {selected_lead_id}
ORDER BY interaction_date DESC
"""

interaction_df = database.fetch_data(interaction_sql)

if interaction_df.empty:
    st.info("No interactions recorded yet for this lead.")
else:
    for index, row in interaction_df.iterrows():

        with st.container(border=True):
            st.markdown(f"### 📞 {row['interaction_type']}")

            formatted_date = row["interaction_date"].strftime("%B %d, %Y • %I:%M %p")
            st.caption(formatted_date)

            st.write(f"**Outcome:** {row['outcome']}")
            st.write(f"**Subject:** {row['subject']}")
            st.write(row["notes"])

st.subheader("Add Interaction")

with st.form("add_interaction_form"):
    interaction_type = st.selectbox(
        "Interaction Type",
        ["Phone Call", "Email", "Text", "Meeting", "Other"]
    )

    outcome = st.selectbox(
        "Outcome",
        ["Interested", "Not Interested", "No Answer", "Left Voicemail", "Proposal Sent", "Follow Up Needed", "Other"]
    )

    subject = st.text_input("Subject")

    interaction_notes = st.text_area("Notes")

    add_interaction = st.form_submit_button("Add Interaction")

    if add_interaction:

        sql = """
        INSERT INTO interactions
        (lead_id, interaction_type, outcome, subject, notes)
        VALUES (%s, %s, %s, %s, %s)
        """

        values = (
            int(selected_lead_id),
            interaction_type,
            outcome,
            subject,
            interaction_notes
        )

        database.run_query(sql, values)

        st.success("Interaction added successfully!")

        st.rerun()

st.divider()
st.subheader("Follow-up Tasks")
task_sql = f"""
SELECT
    task_name,
    due_date,
    status
FROM tasks
WHERE lead_id = {selected_lead_id}
ORDER BY due_date ASC
"""

task_df = database.fetch_data(task_sql)

if task_df.empty:
    st.info("No follow-up tasks for this lead.")
else:
    for index, row in task_df.iterrows():

        with st.container(border=True):

            st.markdown(f"### 📋 {row['task_name']}")

            formatted_due = row["due_date"].strftime("%B %d, %Y")
            st.caption(f"Due: {formatted_due}")

            st.write(f"**Status:** {status_icon(row['status'])}")

st.subheader("Add Follow-up Task")

with st.form("add_task_form"):

    task_name = st.text_input("Task Name")

    due_date = st.date_input("Due Date")

    task_status = st.selectbox(
        "Task Status",
        ["Pending", "In Progress", "Completed"]
    )

    add_task = st.form_submit_button("Add Task")

if add_task:

    sql = """
    INSERT INTO tasks
    (lead_id, task_name, due_date, status)
    VALUES (%s, %s, %s, %s)
    """

    values = (
        int(selected_lead_id),
        task_name,
        due_date,
        task_status
    )

    database.run_query(sql, values)

    st.success("Task added successfully!")

    st.rerun()

st.subheader("Edit Lead")

selected_row = df[df["lead_id"] == selected_lead_id].iloc[0]

edit_business = st.text_input(
    "Business Name",
    value=selected_row["business_name"]
)

edit_contact = st.text_input(
    "Contact Name",
    value=selected_row["contact_name"]
)

edit_phone = st.text_input(
    "Phone",
    value=selected_row["phone"]
)

edit_city = st.text_input(
    "City",
    value=selected_row["city"]
)

edit_website_status = st.selectbox(
    "Website Status",
    ["No Website", "Outdated Website", "Good Website", "Unknown"],
    index=["No Website", "Outdated Website", "Good Website", "Unknown"].index(selected_row["website_status"])
)

edit_lead_status = st.selectbox(
    "Lead Status",
    ["New Lead", "Contacted", "Interested", "Not Interested", "Client"],
    index=["New Lead", "Contacted", "Interested", "Not Interested", "Client"].index(selected_row["lead_status"])
)

if st.button("Save Changes"):
    sql = """
    UPDATE leads
    SET
        business_name = %s,
        contact_name = %s,
        phone = %s,
        city = %s,
        website_status = %s,
        lead_status = %s
    WHERE lead_id = %s
    """

    values = (
        edit_business,
        edit_contact,
        edit_phone,
        edit_city,
        edit_website_status,
        edit_lead_status,
        int(selected_lead_id)
    )

    database.run_query(sql, values)

st.success("Lead updated successfully!")
st.rerun()