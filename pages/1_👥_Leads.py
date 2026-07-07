# Import Streamlit to build the page
import streamlit as st

# Import Pandas for displaying database results
import pandas as pd

# Used to flag overdue follow-up tasks
from datetime import date

# Import our reusalbe database functions
import database

# Shared page styling (rounded cards, buttons, etc.)
from utils import styles

def safe_str(value):
    # pandas reads SQL NULLs back as NaN (not None) for these columns, and
    # NaN is truthy in Python, so a plain `value or ""` doesn't catch it
    return "" if pd.isna(value) else str(value)

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

PROJECT_STATUS_OPTIONS = [
    "Not Started",
    "Ready for Base44",
    "Building in Base44",
    "Demo Ready",
    "Demo Sent",
    "Revisions Needed",
    "Approved",
    "Completed"
]

PAYMENT_STATUS_OPTIONS = [
    "Not Quoted",
    "Quoted",
    "Invoice Sent",
    "Deposit Paid",
    "Paid in Full",
    "Unpaid"
]

# Color mappings so every status shows up as a color-coded st.badge
def lead_status_color(status):
    return {
        "New Lead": "gray",
        "Contacted": "yellow",
        "Interested": "green",
        "Website Building": "orange",
        "Demo Sent": "blue",
        "Negotiating": "violet",
        "Paid": "green",
        "Completed": "green",
        "Not Interested": "red"
    }.get(status, "gray")

def project_status_color(status):
    return {
        "Not Started": "gray",
        "Ready for Base44": "yellow",
        "Building in Base44": "orange",
        "Demo Ready": "blue",
        "Demo Sent": "blue",
        "Revisions Needed": "red",
        "Approved": "violet",
        "Completed": "green"
    }.get(status, "gray")

def payment_status_color(status):
    return {
        "Not Quoted": "gray",
        "Quoted": "yellow",
        "Invoice Sent": "orange",
        "Deposit Paid": "orange",
        "Paid in Full": "green",
        "Unpaid": "red"
    }.get(status, "gray")

def task_status_color(status):
    return {
        "Pending": "gray",
        "In Progress": "orange",
        "Completed": "green"
    }.get(status, "gray")

def outcome_color(outcome):
    return {
        "Interested": "green",
        "Not Interested": "red",
        "No Answer": "gray",
        "Left Voicemail": "yellow",
        "Proposal Sent": "blue",
        "Follow Up Needed": "orange",
        "Other": "gray"
    }.get(outcome, "gray")

@st.dialog("Delete Lead?")
def confirm_delete_lead(lead_id, business_name):
    st.warning(
        f"This will permanently delete **{business_name}** along with all of its "
        f"interactions and follow-up tasks. This cannot be undone."
    )

    cancel_col, delete_col = st.columns(2)

    with cancel_col:
        if st.button("Cancel", width="stretch"):
            st.rerun()

    with delete_col:
        if st.button("Yes, Delete", type="primary", width="stretch"):
            # Children first - interactions/tasks have a foreign key to leads
            database.run_query("DELETE FROM interactions WHERE lead_id = %s", (lead_id,))
            database.run_query("DELETE FROM tasks WHERE lead_id = %s", (lead_id,))
            database.run_query("DELETE FROM leads WHERE lead_id = %s", (lead_id,))

            st.session_state.pop("selected_lead_id", None)
            st.success(f"{business_name} was deleted.")
            st.rerun()

st.set_page_config(page_title="Leads | Nik's Web Design CRM", layout="wide")
styles.inject_css()

st.title("👥 Leads")
st.caption("Manage Potential clients and outreach opportunities.")

with st.expander("➕ Add New Lead"):

    with st.form("add_lead_form"):
        left, right = st.columns(2)

        with left:
            business_name = st.text_input("Business Name")
            contact_name = st.text_input("Contact Name")
            phone = st.text_input("Phone")
            city = st.text_input("City")
            address = st.text_input("Address")
            website_url = st.text_input("Website URL")
            source = st.text_input("Source")

        with right:
            industry = st.text_input("Industry")
            email = st.text_input("Email")
            state = st.text_input("State")
            google_maps_link = st.text_input("Google Maps Link")
            website_status = st.selectbox("Website Status", ["No Website", "Outdated Website", "Good Website", "Unknown"])
            lead_status = st.selectbox("Lead Status", LEAD_STATUS_OPTIONS)

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

# Search + filters
search_col, status_col, archive_col = st.columns([3, 2, 2])

with search_col:
    search = st.text_input("🔍 Search Leads")

with status_col:
    status_filter = st.selectbox(
        "Filter by Status",
        ["All"] + LEAD_STATUS_OPTIONS,
        key="status_filter"
    )

with archive_col:
    st.write("")
    st.write("")
    show_archived = st.checkbox("Show archived leads")

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
    lead_status,
    is_archived
FROM leads
"""

# Build the WHERE clause from whichever filters are active. Every value is
# passed as a parameter (never spliced into the SQL string) to avoid SQL injection.
where_clauses = []
params = {}

if search:
    where_clauses.append("""(
        business_name LIKE %(like_term)s
        OR contact_name LIKE %(like_term)s
        OR city LIKE %(like_term)s
        OR lead_status LIKE %(like_term)s
    )""")
    params["like_term"] = f"%{search}%"

if status_filter != "All":
    where_clauses.append("lead_status = %(status)s")
    params["status"] = status_filter

if not show_archived:
    where_clauses.append("is_archived = 0")

where_sql = ("WHERE " + " AND ".join(where_clauses)) if where_clauses else ""

df = database.fetch_data(LEADS_SELECT + where_sql + " ORDER BY created_at DESC", params=params)

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
selected_row = df[df["lead_id"] == selected_lead_id].iloc[0]

# Remember the selected lead so the Outreach and Website Builder pages
# can default to the same one
st.session_state["selected_lead_id"] = selected_lead_id

# Display the leads
st.dataframe(df, width="stretch")

# Website Project fields aren't in the main SELECT above, so pull them once
# here and reuse for both the Summary Card and the Website Project section below
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

# =====================================================
# LEAD SUMMARY CARD
# =====================================================
st.divider()

with st.container(border=True):
    st.markdown(f"## 🏢 {selected_row['business_name']}")

    info_col1, info_col2, info_col3 = st.columns(3)
    with info_col1:
        st.write(f"📞 **Phone:** {selected_row['phone'] or 'Not set'}")
    with info_col2:
        st.write(f"📍 **City:** {selected_row['city'] or 'Not set'}")
    with info_col3:
        price = project_row["price_quoted"]
        st.write(f"💲 **Price Quoted:** {f'${price:,.2f}' if price else 'Not quoted'}")

    badge_col1, badge_col2, badge_col3, _ = st.columns([2, 2, 2, 3])
    with badge_col1:
        st.badge(selected_row["lead_status"], color=lead_status_color(selected_row["lead_status"]))
    with badge_col2:
        project_status = project_row["website_project_status"] or "Not Started"
        st.badge(project_status, color=project_status_color(project_status))
    with badge_col3:
        payment_status_value = project_row["payment_status"] or "Not Quoted"
        st.badge(payment_status_value, color=payment_status_color(payment_status_value))

    st.write("")
    action_col1, action_col2, _ = st.columns([1, 1, 3])
    with action_col1:
        is_archived = bool(selected_row["is_archived"])
        archive_label = "📤 Unarchive Lead" if is_archived else "📥 Archive Lead"
        if st.button(archive_label):
            database.run_query(
                "UPDATE leads SET is_archived = %s WHERE lead_id = %s",
                (0 if is_archived else 1, selected_lead_id)
            )
            st.success("Lead unarchived." if is_archived else "Lead archived.")
            st.rerun()

    with action_col2:
        if st.button("🗑️ Delete Lead"):
            confirm_delete_lead(selected_lead_id, selected_row["business_name"])

# =====================================================
# INTERACTION HISTORY
# =====================================================
st.divider()
st.subheader("📞 Interaction History")

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
            top_col, date_col = st.columns([3, 2])

            with top_col:
                st.badge(row["interaction_type"], icon="📞", color="blue")

            with date_col:
                formatted_date = row["interaction_date"].strftime("%B %d, %Y • %I:%M %p")
                st.markdown(
                    f"<div style='text-align: right; color: #A0A6B2;'>{formatted_date}</div>",
                    unsafe_allow_html=True
                )

            st.badge(row["outcome"], color=outcome_color(row["outcome"]))

            if row["subject"]:
                st.markdown(f"**{row['subject']}**")

            if row["notes"]:
                st.write(row["notes"])

st.subheader("Add Interaction")

with st.form("add_interaction_form"):
    form_col1, form_col2 = st.columns(2)

    with form_col1:
        interaction_type = st.selectbox(
            "Interaction Type",
            ["Phone Call", "Email", "Text", "Meeting", "Other"]
        )
        subject = st.text_input("Subject")

    with form_col2:
        outcome = st.selectbox(
            "Outcome",
            ["Interested", "Not Interested", "No Answer", "Left Voicemail", "Proposal Sent", "Follow Up Needed", "Other"]
        )

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

# =====================================================
# FOLLOW-UP TASKS
# =====================================================
st.divider()
st.subheader("📋 Follow-up Tasks")

task_df = database.fetch_data(
    """
    SELECT
        task_name,
        description,
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
            st.markdown(f"### {row['task_name']}")

            badge_col1, badge_col2, lead_col = st.columns([2, 2, 3])

            with badge_col1:
                st.badge(row["status"], color=task_status_color(row["status"]))

            with badge_col2:
                is_overdue = row["due_date"].date() < date.today() and row["status"] != "Completed"
                if is_overdue:
                    st.badge("Overdue", color="red")

            with lead_col:
                st.caption(f"For {selected_row['business_name']}")

            formatted_due = row["due_date"].strftime("%B %d, %Y")
            st.caption(f"📅 Due {formatted_due}")

            if row["description"]:
                st.write(row["description"])

st.subheader("Add Follow-up Task")

with st.form("add_task_form"):
    task_name = st.text_input("Task Name")
    task_description = st.text_area("Description")

    form_col1, form_col2 = st.columns(2)

    with form_col1:
        due_date = st.date_input("Due Date")

    with form_col2:
        task_status = st.selectbox(
            "Task Status",
            ["Pending", "In Progress", "Completed"]
        )

    add_task = st.form_submit_button("Add Task")

if add_task:

    sql = """
    INSERT INTO tasks
    (lead_id, task_name, description, due_date, status)
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        selected_lead_id,
        task_name,
        task_description,
        due_date,
        task_status
    )

    database.run_query(sql, values)

    st.success("Task added successfully!")

    st.rerun()

# =====================================================
# EDIT LEAD
# =====================================================
st.divider()
st.subheader("✏️ Edit Lead")

with st.container(border=True):
    left, right = st.columns(2)

    with left:
        edit_business = st.text_input("Business Name", value=selected_row["business_name"])
        edit_contact = st.text_input("Contact Name", value=selected_row["contact_name"])
        edit_phone = st.text_input("Phone", value=selected_row["phone"])
        edit_address = st.text_input("Address", value=safe_str(selected_row["address"]))
        website_status_options = ["No Website", "Outdated Website", "Good Website", "Unknown"]
        edit_website_status = st.selectbox(
            "Website Status",
            website_status_options,
            index=website_status_options.index(selected_row["website_status"])
            if selected_row["website_status"] in website_status_options else 0
        )

    with right:
        edit_industry = st.text_input("Industry", value=safe_str(selected_row["industry"]))
        edit_email = st.text_input("Email", value=safe_str(selected_row["email"]))
        edit_city = st.text_input("City", value=selected_row["city"])
        edit_google_maps_link = st.text_input("Google Maps Link", value=safe_str(selected_row["google_maps_link"]))
        edit_lead_status = st.selectbox(
            "Lead Status",
            LEAD_STATUS_OPTIONS,
            index=LEAD_STATUS_OPTIONS.index(selected_row["lead_status"])
            if selected_row["lead_status"] in LEAD_STATUS_OPTIONS else 0
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

# =====================================================
# WEBSITE PROJECT
# =====================================================
st.divider()
st.subheader("🌐 Website Project")

with st.container(border=True):
    left, right = st.columns(2)

    with left:
        edit_project_status = st.selectbox(
            "Website Project Status",
            PROJECT_STATUS_OPTIONS,
            index=PROJECT_STATUS_OPTIONS.index(project_row["website_project_status"])
            if project_row["website_project_status"] in PROJECT_STATUS_OPTIONS else 0
        )
        edit_base44_url = st.text_input("Base44 Project URL", value=safe_str(project_row["base44_project_url"]))
        edit_demo_url = st.text_input("Demo URL", value=safe_str(project_row["demo_url"]))

    with right:
        edit_price_quoted = st.number_input(
            "Price Quoted",
            min_value=0.0,
            step=50.0,
            value=float(project_row["price_quoted"]) if project_row["price_quoted"] else 0.0
        )
        edit_payment_status = st.selectbox(
            "Payment Status",
            PAYMENT_STATUS_OPTIONS,
            index=PAYMENT_STATUS_OPTIONS.index(project_row["payment_status"])
            if project_row["payment_status"] in PAYMENT_STATUS_OPTIONS else 0
        )

    edit_project_notes = st.text_area("Project Notes", value=safe_str(project_row["project_notes"]))

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
