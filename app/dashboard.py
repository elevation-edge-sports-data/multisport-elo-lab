import bootstrap
import streamlit as st

from components.layout import configure_page

from tabs.configuration import render_configuration_tab
from tabs.simulation import render_simulation_tab
from tabs.elo_ratings import render_elo_ratings_tab
from tabs.elo_evolution import render_elo_evolution_tab
from tabs.evaluation import render_evaluation_tab

from services.simulation_service import run_simulation
from elo_lab.workflows.optimize_parameters import optimize_parameters_for_config


configure_page()

# Broncos Orange theme for checkboxes and progress bar
st.markdown("""
<style>
    /* Progress bar color */
    .stProgress > div > div > div > div {
        background-color: #FB4F14 !important;
    }
    
    /* Checkbox checked color */
    .stCheckbox > label > div[role="checkbox"][aria-checked="true"] {
        background-color: #FB4F14 !important;
        border-color: #FB4F14 !important;
    }
</style>
""", unsafe_allow_html=True)


st.title("MultiSport Elo Lab")

st.caption(
    "Interactive sports modeling analytics platform | "
    "Version 6 Dashboard"
)


def build_model_config(
    home_field: bool,
    margin_of_victory: bool,
    elevation: bool,
) -> dict:
    """Build the model configuration from enabled adjustments."""
    adjustments_config = {}

    if home_field:
        adjustments_config["home_field"] = {"enabled": True, "value": 55}
    if margin_of_victory:
        adjustments_config["margin_of_victory"] = {"enabled": True, "scale": 1.0}
    if elevation:
        adjustments_config["elevation_edge"] = {"enabled": True, "value": 0.0}

    return {
        "k": 20,
        "adjustments": adjustments_config,
    }


def get_optimize_for(
    home_field: bool,
    margin_of_victory: bool,
    elevation: bool,
    opt_home_field: bool,
    opt_margin_of_victory: bool,
    opt_elevation: bool,
) -> list[str]:
    """Return list of adjustments the user wants to optimize parameters for."""
    optimize_for = []
    if home_field and opt_home_field:
        optimize_for.append("home_field")
    if margin_of_victory and opt_margin_of_victory:
        optimize_for.append("margin_of_victory")
    if elevation and opt_elevation:
        optimize_for.append("elevation_edge")
    return optimize_for


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

home_field = st.sidebar.checkbox("Home Field Advantage", value=True)
margin_of_victory = st.sidebar.checkbox("Margin of Victory", value=True)
elevation = st.sidebar.checkbox("Elevation Edge", value=False)

st.sidebar.divider()

# === Parameter Optimization Controls ===
optimize_params = st.sidebar.checkbox(
    "Optimize parameters for selected adjustments", value=False
)

opt_home_field = opt_margin_of_victory = opt_elevation = False

if optimize_params:
    st.sidebar.markdown("**Optimize parameters for:**")
    if home_field:
        opt_home_field = st.sidebar.checkbox("Home Field Advantage", value=True, key="opt_hfa")
    if margin_of_victory:
        opt_margin_of_victory = st.sidebar.checkbox("Margin of Victory", value=True, key="opt_mov")
    if elevation:
        opt_elevation = st.sidebar.checkbox("Elevation Edge", value=False, key="opt_elev")

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
    index=0,   # Default changed to 100
    format_func=lambda x: f"{x:,}",
)


st.sidebar.divider()


# ==========================================================
# SIMULATION EXECUTION
# ==========================================================

if st.sidebar.button("Run Simulation"):

    config = build_model_config(home_field, margin_of_victory, elevation)
    optimize_for = get_optimize_for(
        home_field, margin_of_victory, elevation,
        opt_home_field, opt_margin_of_victory, opt_elevation
    )

    st.session_state["last_config"] = config
    st.session_state["active_adjustments"] = list(config["adjustments"].keys())
    st.session_state["optimize_for"] = optimize_for

    # Progress indicator in the sidebar
    with st.sidebar.status("Running simulation...", expanded=True) as status:
        progress_bar = st.sidebar.progress(0, text="Starting...")

        if optimize_for:
            progress_bar.progress(20, text="Optimizing parameters...")
            best_config, opt_results = optimize_parameters_for_config(
                base_config=config,
                optimize_for=optimize_for
            )
            st.session_state["optimization_results"] = opt_results
            final_config = best_config

            best_params = {"k": best_config.get("k")}
            for adj, params in best_config.get("adjustments", {}).items():
                for key, value in params.items():
                    if key in ["value", "scale"]:
                        best_params[f"{adj}_{key}"] = value
            st.session_state["best_optimized_params"] = best_params

            progress_bar.progress(50, text="Optimization complete")
        else:
            final_config = config
            st.session_state["best_optimized_params"] = None
            progress_bar.progress(50, text="Running simulations...")

        # Run the actual Monte Carlo simulation
        progress_bar.progress(70, text="Running Monte Carlo simulations...")

        # Temporary Version 7 validation initialization.
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

        results = run_simulation(
            config=final_config,
            n_sims=simulation_count,
            initial_ratings=initial_ratings,
        )

        st.session_state["simulation_results"] = results
        st.session_state["simulation_count"] = simulation_count

        progress_bar.progress(100, text="Complete!")
        status.update(label="Simulation complete!", state="complete")
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