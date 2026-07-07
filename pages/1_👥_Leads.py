# Import Streamlit to build the page
import streamlit as st

# Import Pandas for displaying database results
import pandas as pd

# Import our reusalbe database functions
import database

# The full lead status pipeline, used everywhere a lead status is picked
LEAD_STATUS_OPTIONS = [
    "New Lead",
    "Contacted",
    "Interested",
    "Website Building",
    "Demo Sent",
    "Negotiating",
    "Paid",
    "Completed",
    "Not Interested"
]

def status_icon(status):
    icons = {
        "New Lead": "⚪ New Lead",
        "Contacted": "🟡 Contacted",
        "Interested": "🟢 Interested",
        "Website Building": "🟠 Website Building",
        "Demo Sent": "🔵 Demo Sent",
        "Negotiating": "🟣 Negotiating",
        "Paid": "💰 Paid",
        "Completed": "✅ Completed",
        "Not Interested": "🔴 Not Interested",
        "Pending": "🟡 Pending",
        "In Progress": "🟠 In Progress"
    }

    return icons.get(status, status)

st.set_page_config(page_title="Leads | Nik's Web Design CRM", layout="wide")

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
        address = st.text_input("Address")
        google_maps_link = st.text_input("Google Maps Link")
        website_url = st.text_input("Website URL")
        website_status = st.selectbox("Website Status", ["No Website", "Outdated Website", "Good Website", "Unknown"])
        lead_status = st.selectbox("Lead Status", LEAD_STATUS_OPTIONS)
        source = st.text_input("Source")
        notes = st.text_area("Notes")

        submitted = st.form_submit_button("Add Lead")

        if submitted:
            sql = """
            INSERT INTO leads (
                business_name, industry, contact_name, email, phone,
                city, state, address, google_maps_link, website_url,
                website_status, lead_status, source, notes
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """

            values = (
                business_name, industry, contact_name, email, phone,
                city, state, address, google_maps_link, website_url,
                website_status, lead_status, source, notes
            )

            database.run_query(sql, values)

            st.success("Lead added successfully!")

st.divider()

# Search Bar
search = st.text_input("🔍 Search Leads")

status_filter = st.selectbox(
    "Filter by Status",
    ["All"] + LEAD_STATUS_OPTIONS,
    key="status_filter"
)

st.subheader("All Leads")

# Columns shared by every branch of the leads query below
LEADS_SELECT = """
SELECT
    lead_id,
    business_name,
    contact_name,
    email,
    phone,
    city,
    address,
    google_maps_link,
    industry,
    website_status,
    lead_status
FROM leads
"""

# Retrieve all leads from MySQL. Search/filter values are passed as
# parameters (not spliced into the SQL string) to avoid SQL injection.
if search and status_filter != "All":
    like_term = f"%{search}%"
    df = database.fetch_data(
        LEADS_SELECT + """
        WHERE (
            business_name LIKE %(like_term)s
            OR contact_name LIKE %(like_term)s
            OR city LIKE %(like_term)s
            OR lead_status LIKE %(like_term)s
        )
        AND lead_status = %(status)s
        ORDER BY created_at DESC
        """,
        params={"like_term": like_term, "status": status_filter}
    )

elif search:
    like_term = f"%{search}%"
    df = database.fetch_data(
        LEADS_SELECT + """
        WHERE business_name LIKE %(like_term)s
           OR contact_name LIKE %(like_term)s
           OR city LIKE %(like_term)s
           OR lead_status LIKE %(like_term)s
        ORDER BY created_at DESC
        """,
        params={"like_term": like_term}
    )

elif status_filter != "All":
    df = database.fetch_data(
        LEADS_SELECT + """
        WHERE lead_status = %(status)s
        ORDER BY created_at DESC
        """,
        params={"status": status_filter}
    )

else:
    df = database.fetch_data(LEADS_SELECT + "ORDER BY created_at DESC")

# Nothing to show for this search/filter combo - stop here so the rest of
# the page (which assumes a selected lead) doesn't crash on an empty result
if df.empty:
    st.info("No leads match your search/filter.")
    st.stop()

# Select a lead to view
selected_lead_name = st.selectbox(
    "Select a Lead",
    df["business_name"]
)

selected_lead_id = int(df[df["business_name"] == selected_lead_name]["lead_id"].iloc[0])

# Remember the selected lead so the Outreach and Website Builder pages
# can default to the same one
st.session_state["selected_lead_id"] = selected_lead_id

# Display the leads
st.dataframe(df, width="stretch")

st.divider()


st.divider()
st.subheader("Interaction History")

interaction_df = database.fetch_data(
    """
    SELECT
        interaction_date,
        interaction_type,
        outcome,
        subject,
        notes
    FROM interactions
    WHERE lead_id = %(lead_id)s
    ORDER BY interaction_date DESC
    """,
    params={"lead_id": selected_lead_id}
)

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
            selected_lead_id,
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
task_df = database.fetch_data(
    """
    SELECT
        task_name,
        due_date,
        status
    FROM tasks
    WHERE lead_id = %(lead_id)s
    ORDER BY due_date ASC
    """,
    params={"lead_id": selected_lead_id}
)

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
        selected_lead_id,
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

edit_industry = st.text_input(
    "Industry",
    value=selected_row["industry"] or ""
)

edit_contact = st.text_input(
    "Contact Name",
    value=selected_row["contact_name"]
)

edit_email = st.text_input(
    "Email",
    value=selected_row["email"] or ""
)

edit_phone = st.text_input(
    "Phone",
    value=selected_row["phone"]
)

edit_city = st.text_input(
    "City",
    value=selected_row["city"]
)

edit_address = st.text_input(
    "Address",
    value=selected_row["address"] or ""
)

edit_google_maps_link = st.text_input(
    "Google Maps Link",
    value=selected_row["google_maps_link"] or ""
)

edit_website_status = st.selectbox(
    "Website Status",
    ["No Website", "Outdated Website", "Good Website", "Unknown"],
    index=["No Website", "Outdated Website", "Good Website", "Unknown"].index(selected_row["website_status"])
)

edit_lead_status = st.selectbox(
    "Lead Status",
    LEAD_STATUS_OPTIONS,
    index=LEAD_STATUS_OPTIONS.index(selected_row["lead_status"])
)

if st.button("Save Changes"):
    sql = """
    UPDATE leads
    SET
        business_name = %s,
        industry = %s,
        contact_name = %s,
        email = %s,
        phone = %s,
        city = %s,
        address = %s,
        google_maps_link = %s,
        website_status = %s,
        lead_status = %s
    WHERE lead_id = %s
    """

    values = (
        edit_business,
        edit_industry,
        edit_contact,
        edit_email,
        edit_phone,
        edit_city,
        edit_address,
        edit_google_maps_link,
        edit_website_status,
        edit_lead_status,
        selected_lead_id
    )

    database.run_query(sql, values)

    # Moved inside the if-block so this only fires on Save Changes click
    st.success("Lead updated successfully!")
    st.rerun()

st.divider()
st.subheader("Website Project")

# The main leads query above doesn't select these columns, so pull them
# separately for the selected lead
project_row = database.fetch_data(
    """
    SELECT
        website_project_status,
        base44_project_url,
        demo_url,
        price_quoted,
        payment_status,
        project_notes
    FROM leads
    WHERE lead_id = %(lead_id)s
    """,
    params={"lead_id": selected_lead_id}
).iloc[0]

project_status_options = [
    "Not Started",
    "Ready for Base44",
    "Building in Base44",
    "Demo Ready",
    "Demo Sent",
    "Revisions Needed",
    "Approved",
    "Completed"
]

payment_status_options = [
    "Not Quoted",
    "Quoted",
    "Invoice Sent",
    "Deposit Paid",
    "Paid in Full",
    "Unpaid"
]

edit_project_status = st.selectbox(
    "Website Project Status",
    project_status_options,
    index=project_status_options.index(project_row["website_project_status"])
    if project_row["website_project_status"] in project_status_options else 0
)

edit_base44_url = st.text_input(
    "Base44 Project URL",
    value=project_row["base44_project_url"] or ""
)

edit_demo_url = st.text_input(
    "Demo URL",
    value=project_row["demo_url"] or ""
)

edit_price_quoted = st.number_input(
    "Price Quoted",
    min_value=0.0,
    step=50.0,
    value=float(project_row["price_quoted"]) if project_row["price_quoted"] else 0.0
)

edit_payment_status = st.selectbox(
    "Payment Status",
    payment_status_options,
    index=payment_status_options.index(project_row["payment_status"])
    if project_row["payment_status"] in payment_status_options else 0
)

edit_project_notes = st.text_area(
    "Project Notes",
    value=project_row["project_notes"] or ""
)

if st.button("Save Website Project"):
    sql = """
    UPDATE leads
    SET
        website_project_status = %s,
        base44_project_url = %s,
        demo_url = %s,
        price_quoted = %s,
        payment_status = %s,
        project_notes = %s
    WHERE lead_id = %s
    """

    values = (
        edit_project_status,
        edit_base44_url,
        edit_demo_url,
        edit_price_quoted,
        edit_payment_status,
        edit_project_notes,
        selected_lead_id
    )

    database.run_query(sql, values)

    st.success("Website project updated successfully!")
    st.rerun()
