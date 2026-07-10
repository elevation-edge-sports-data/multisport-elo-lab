import bootstrap
import streamlit as st

from components.layout import configure_page

from tabs.configuration import render_configuration_tab
from tabs.simulation import render_simulation_tab
from tabs.elo_ratings import render_elo_ratings_tab
from tabs.elo_evolution import render_elo_evolution_tab
from tabs.evaluation import render_evaluation_tab

from services.simulation_service import run_simulation


configure_page()


st.title("MultiSport Elo Lab")

st.caption(
    "Interactive sports modeling analytics platform | "
    "Version 6 Dashboard"
)


# ==========================================================
# SIDEBAR CONFIGURATION
# ==========================================================

st.sidebar.header("Model Configuration")


sport = st.sidebar.selectbox(
    "Sport",
    ["NFL"]
)


season = st.sidebar.selectbox(
    "Season",
    ["2025"]
)


st.sidebar.divider()


st.sidebar.subheader("Adjustments")


home_field = st.sidebar.checkbox(
    "Home Field Advantage",
    value=True
)


margin_of_victory = st.sidebar.checkbox(
    "Margin of Victory",
    value=True
)


elevation = st.sidebar.checkbox(
    "Elevation Edge",
    value=False
)


st.sidebar.divider()


simulation_options = [
    100,
    500,
    1000,
    5000,
    10000,
    50000,
]


simulation_count = st.sidebar.selectbox(
    "Simulation Count",
    simulation_options,
    index=2,
    format_func=lambda x: f"{x:,}",
)


runtime_estimates = {
    100: "~2 sec",
    500: "~10 sec",
    1000: "~20 sec",
    5000: "~1 min 30 sec",
    10000: "~3 min",
    50000: "~15 min",
}


st.sidebar.metric(
    "Estimated Runtime",
    runtime_estimates[simulation_count],
)


st.sidebar.divider()


# ==========================================================
# SIMULATION EXECUTION
# ==========================================================

if st.sidebar.button("▶ Run Simulation"):

    config = {
        "k": 20,
        "adjustments": {
            "home_field": {
                "enabled": home_field,
                "value": 55,
            },
            "margin_of_victory": {
                "enabled": margin_of_victory,
                "scale": 1.0,
            },
        },
    }


    # Temporary Version 7 validation initialization.
    # Replaces flat 1500 Elo to test simulation sensitivity.
    initial_ratings = {
        "ARI": 1340,
        "ATL": 1350,
        "BAL": 1360,
        "BUF": 1370,
        "CAR": 1380,
        "CHI": 1390,
        "CIN": 1400,
        "CLE": 1410,
        "DAL": 1420,
        "DEN": 1430,
        "DET": 1440,
        "GB": 1450,
        "HOU": 1460,
        "IND": 1470,
        "JAX": 1480,
        "KC": 1490,
        "LAC": 1500,
        "LAR": 1510,
        "LV": 1520,
        "MIA": 1530,
        "MIN": 1540,
        "NE": 1550,
        "NO": 1560,
        "NYG": 1570,
        "NYJ": 1580,
        "PHI": 1590,
        "PIT": 1600,
        "SEA": 1610,
        "SF": 1620,
        "TB": 1630,
        "TEN": 1640,
        "WAS": 1650,
    }


    with st.spinner(
        f"Running {simulation_count:,} simulations..."
    ):

        results = run_simulation(
            config=config,
            n_sims=simulation_count,
            initial_ratings=initial_ratings,
        )

        st.session_state["simulation_results"] = results
        st.session_state["simulation_count"] = simulation_count


    st.sidebar.success(
        "Simulation complete"
    )


# ==========================================================
# TABS
# ==========================================================

tabs = st.tabs(
    [
        "Model Configuration",
        "Season Simulation",
        "Elo Ratings",
        "Elo Evolution",
        "Model Evaluation",
    ]
)


with tabs[0]:

    render_configuration_tab(
        sport=sport,
        season=season,
        home_field=home_field,
        margin_of_victory=margin_of_victory,
        elevation=elevation,
        simulation_count=simulation_count,
    )


with tabs[1]:

    render_simulation_tab()


with tabs[2]:

    render_elo_ratings_tab()


with tabs[3]:

    render_elo_evolution_tab()


with tabs[4]:

    render_evaluation_tab()