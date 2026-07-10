import streamlit as st


def configure_page():

    st.set_page_config(
        page_title="MultiSport Elo Lab",
        page_icon="📈",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.markdown(
        """
        <style>

        /* =====================================================
           Main Page
        ===================================================== */

        .block-container {
            padding-top: 1.5rem;
            padding-bottom: 1.5rem;
        }

        h1 {
            font-size: 2.5rem;
        }

        div[data-testid="metric-container"] {
            border-radius: 8px;
            padding: 8px;
        }

        /* =====================================================
           Sidebar
        ===================================================== */

        section[data-testid="stSidebar"] .block-container {
            padding-top: 0.75rem;
            padding-bottom: 0.75rem;
            padding-left: 1rem;
            padding-right: 1rem;
        }

        section[data-testid="stSidebar"] h1,
        section[data-testid="stSidebar"] h2,
        section[data-testid="stSidebar"] h3 {
            margin-top: 0.25rem;
            margin-bottom: 0.25rem;
        }

        section[data-testid="stSidebar"] hr {
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }

        section[data-testid="stSidebar"] .stSelectbox,
        section[data-testid="stSidebar"] .stCheckbox,
        section[data-testid="stSidebar"] .stButton,
        section[data-testid="stSidebar"] [data-testid="metric-container"] {
            margin-top: 0.2rem;
            margin-bottom: 0.2rem;
        }

        section[data-testid="stSidebar"] p {
            margin-bottom: 0.25rem;
        }

        </style>
        """,
        unsafe_allow_html=True,
    )