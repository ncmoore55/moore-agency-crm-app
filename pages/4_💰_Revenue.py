# Import Streamlit to build the page
import streamlit as st

# Import our reusable database functions
import database

# Shared page styling (rounded cards, buttons, etc.)
from utils import styles

st.set_page_config(page_title="Revenue | Nik's Web Design CRM", layout="wide")
styles.inject_css()

st.title("💰 Revenue")
st.caption("Track quoted prices and payment status across all leads.")

# Only leads that have actually been quoted a price
quoted_df = database.fetch_data("""
SELECT
    business_name,
    price_quoted,
    payment_status,
    website_project_status
FROM leads
WHERE price_quoted IS NOT NULL AND price_quoted > 0
ORDER BY price_quoted DESC
""")

total_quoted = quoted_df["price_quoted"].sum() if not quoted_df.empty else 0

# Only "Paid in Full" counts as paid revenue — deposits are tracked separately
# under payment_status but aren't counted here to avoid guessing a partial amount
paid_df = quoted_df[quoted_df["payment_status"] == "Paid in Full"]
total_paid = paid_df["price_quoted"].sum() if not paid_df.empty else 0

unpaid_opportunities = total_quoted - total_paid

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("📊 Total Quoted", f"${total_quoted:,.2f}")

with col2:
    st.metric("✅ Total Paid", f"${total_paid:,.2f}")

with col3:
    st.metric("🕒 Unpaid Opportunities", f"${unpaid_opportunities:,.2f}")

st.divider()
st.subheader("Quoted Leads")

if quoted_df.empty:
    st.info("No leads have been quoted a price yet.")
else:
    st.dataframe(quoted_df, width="stretch")
