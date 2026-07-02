# Import Streamlit to build the page
import streamlit as st

# Import Pandas for displaying database results
import pandas as pd

# Import our reusalbe database functions
import database

st.set_page_config(page_title="Leads | Moore Agency CRM", layout="wide")

st.title("👥 Leads")
st.caption("Manage Potential clients and outreach opportunities.")

st.divider()

# Search Bar
search = st.text_input("🔍 Search Leads")

status_filter = st.selectbox(
    "Filter by Status",
    ["All", "New Lead", "Contacted", "Interested", "Not Interested", "Client"]
)

st.subheader("All Leads")

# Retrieve all leads from MySQL
df = database.fetch_data("""
SELECT
    business_name,
    contact_name,
    phone,
    city,
    website_status,
    lead_status
FROM leads
ORDER BY created_at DESC
""")

# Display the leads
st.dataframe(df, use_container_width=True)

