# Import Streamlit to build the page
import streamlit as st

# Shared page styling (rounded cards, buttons, etc.)
from utils import styles

st.set_page_config(page_title="Settings | Nik's Web Design CRM", layout="wide")
styles.inject_css()

st.title("⚙️ Settings")
st.caption("Nik's Web Design LLC")

st.info("More settings are coming soon — this page is a placeholder for now.")
