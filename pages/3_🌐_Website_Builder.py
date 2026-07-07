# Import Streamlit to build the page
import streamlit as st

# Import our reusable database functions
import database

# Shared page styling (rounded cards, buttons, etc.)
from utils import styles

st.set_page_config(page_title="Website Builder | Nik's Web Design CRM", layout="wide")
styles.inject_css()

st.title("🌐 Website Builder")
st.caption("This page does not build websites — it generates a Base44 prompt from a lead's info.")

# Pull every lead so we can pick one to build a prompt for
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

# Pull the fields the Base44 prompt is built from
lead_row = database.fetch_data(
    """
    SELECT business_name, industry, city, phone, email, address, notes
    FROM leads
    WHERE lead_id = %(lead_id)s
    """,
    params={"lead_id": selected_lead_id}
).iloc[0]

st.divider()

# These two inputs are only used to build the prompt below — they aren't saved to the database
review_notes = st.text_area("Google Rating / Review Notes (optional)")
real_photos_ok = st.checkbox("Owner approved using real photos")

st.divider()
st.subheader("📋 Base44 Prompt")

photo_instruction = (
    "The owner has approved using real business photos where provided."
    if real_photos_ok
    else "No real photos have been approved yet — use tasteful stock/placeholder images instead."
)

review_section = (
    f"Google rating / review notes: {review_notes}"
    if review_notes
    else "No review information provided — do not invent ratings or testimonials."
)

prompt = f"""Build a small business website with the following details:

Business Name: {lead_row['business_name']}
Industry: {lead_row['industry'] or 'Not specified'}
City: {lead_row['city'] or 'Not specified'}
Phone: {lead_row['phone'] or 'Not specified'}
Email: {lead_row['email'] or 'Not specified'}
Address: {lead_row['address'] or 'Not specified'}
Services / Notes: {lead_row['notes'] or 'Not specified'}
{review_section}

Goal: Help this business get more phone calls and quote requests from its website visitors.

Include these sections: Hero, Services, About, Gallery, Reviews, FAQ, Contact, Footer.

Important: Do not invent fake awards, licenses, certifications, testimonials, or guarantees.
Only use information provided above.

Photos: {photo_instruction}
"""

st.code(prompt, language=None)
