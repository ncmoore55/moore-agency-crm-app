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

# Retrieve all leads from the database
df_leads = database.fetch_data("SELECT * FROM leads")

# Count the total number of leads
total_leads = len(df_leads)

# Dashboard metric cards
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Total Leads", total_leads)

with col2:
    st.metric("Active Projects", 0)

with col3:
    st.metric("Revenue", "$0")

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

st.subheader("All Leads")

# Retrieve all leads from the database
conn = database.get_connection()

df = pd.read_sql(
    "SELECT * FROM leads ORDER BY created_at DESC",
    conn
)

conn.close()
# Display the leads in a table
st.dataframe(df, use_container_width=True)