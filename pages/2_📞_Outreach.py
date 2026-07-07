# Import Streamlit to build the page
import streamlit as st

# Import our reusable database functions
import database

st.set_page_config(page_title="Outreach | Nik's Web Design CRM", layout="wide")

st.title("📞 Outreach")
st.caption("Copy-ready text templates for reaching out to leads.")

# Pull every lead so we can pick one to build messages for
leads_df = database.fetch_data("SELECT lead_id, business_name FROM leads ORDER BY business_name")

if leads_df.empty:
    st.info("No leads yet. Add one on the Leads page first.")
    st.stop()

# Default to whichever lead was last selected on the Leads page, if any
default_lead_id = st.session_state.get("selected_lead_id")
lead_ids = leads_df["lead_id"].tolist()
default_index = lead_ids.index(default_lead_id) if default_lead_id in lead_ids else 0

selected_business_name = st.selectbox(
    "Select a Lead",
    leads_df["business_name"],
    index=default_index
)

selected_lead_id = int(leads_df[leads_df["business_name"] == selected_business_name]["lead_id"].iloc[0])
st.session_state["selected_lead_id"] = selected_lead_id

# Pull the fields we need to personalize the templates below
lead_row = database.fetch_data(
    """
    SELECT business_name, contact_name, demo_url, price_quoted
    FROM leads
    WHERE lead_id = %(lead_id)s
    """,
    params={"lead_id": selected_lead_id}
).iloc[0]

business_name = lead_row["business_name"]
demo_url = lead_row["demo_url"]
price_quoted = lead_row["price_quoted"]

st.divider()

# =====================================================
# First text message
# =====================================================
st.subheader("💬 First Text Message")
first_message = (
    f"Hi! This is Nik with Nik's Web Design. I help local businesses like "
    f"{business_name} get more calls with a modern website. Would you be open "
    f"to a free demo, no strings attached?"
)
st.code(first_message, language=None)

# =====================================================
# Follow-up text
# =====================================================
st.subheader("🔁 Follow-up Text")
follow_up_message = (
    f"Hi again! Just following up on the free website demo idea for "
    f"{business_name}. Happy to answer any questions or get started whenever "
    f"you're ready."
)
st.code(follow_up_message, language=None)

# =====================================================
# Demo sent message
# =====================================================
st.subheader("🌐 Demo Sent Message")

if demo_url:
    demo_message = (
        f"Hi! I put together a free demo website for {business_name} — "
        f"check it out here: {demo_url}. Let me know what you think!"
    )
    st.code(demo_message, language=None)
else:
    st.info("No demo URL saved for this lead yet. Add one in the Leads page's Website Project section first.")

# =====================================================
# Price response message
# =====================================================
st.subheader("💲 Price Response Message")

if price_quoted:
    price_message = (
        f"Thanks for checking out the demo! For a site like this, the price "
        f"would be ${price_quoted:,.2f}. Let me know if you'd like to move "
        f"forward and I can get it live for you."
    )
else:
    price_message = (
        f"Thanks for checking out the demo! I'll follow up shortly with "
        f"pricing for {business_name}'s site."
    )
st.code(price_message, language=None)
