# Shared visual polish for every page - keeps the CSS/HTML bits in one place
# instead of copy-pasted across app.py and each page.

import streamlit as st

# Soft-tinted background + accent color per bubble-card theme
_KPI_THEMES = {
    "amber": ("rgba(245, 158, 11, 0.15)", "#F59E0B"),
    "rose": ("rgba(244, 63, 94, 0.15)", "#F43F5E"),
    "emerald": ("rgba(16, 185, 129, 0.15)", "#10B981"),
    "violet": ("rgba(139, 92, 246, 0.15)", "#8B5CF6"),
    "blue": ("rgba(59, 130, 246, 0.15)", "#3B82F6"),
    "gray": ("rgba(148, 163, 184, 0.12)", "#94A3B8"),
}

def inject_css():
    # Called once at the top of every page for a consistent, rounder, less
    # cramped look without changing any widget behavior.
    st.markdown(
        """
        <style>
        /* Rounder, roomier bordered containers (interaction/task/summary cards) */
        div[data-testid="stVerticalBlockBorderWrapper"] {
            border-radius: 16px !important;
        }
        div[data-testid="stVerticalBlockBorderWrapper"] > div {
            padding: 0.25rem 0.25rem;
        }

        /* Rounder, pill-style buttons with a subtle hover lift */
        .stButton > button, .stFormSubmitButton > button {
            border-radius: 10px !important;
            transition: transform 0.05s ease-in-out;
        }
        .stButton > button:hover, .stFormSubmitButton > button:hover {
            transform: translateY(-1px);
        }

        /* Softer, shorter dividers so sections don't feel like a hard wall */
        hr {
            margin: 1.2rem 0 !important;
            opacity: 0.25;
        }

        /* A little breathing room above each subheader/section title */
        h2, h3 {
            margin-top: 0.6rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def kpi_card(icon, value, label, theme="violet"):
    # One colored bubble stat card - used on the Dashboard's KPI row since
    # st.metric can't take a custom per-card background color.
    bg, accent = _KPI_THEMES.get(theme, _KPI_THEMES["violet"])

    st.markdown(
        f"""
        <div style="
            background: {bg};
            border: 1px solid {accent}33;
            border-radius: 18px;
            padding: 18px 20px;
            margin-bottom: 12px;
        ">
            <div style="font-size: 22px;">{icon}</div>
            <div style="font-size: 28px; font-weight: 700; color: #F5F5F5; margin-top: 6px;">{value}</div>
            <div style="font-size: 13px; color: #A0A6B2; margin-top: 2px;">{label}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
