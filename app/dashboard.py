"""
MultiSport Elo Lab – Streamlit dashboard

Version 9 with:
  - NHL / NFL / NBA support
  - Multiseason-aware initial Elo (rating_source, rating_basis, apply_regression)
  - Existing adjustment toggles + parameter optimization
  - Tabs: Configuration, Season Simulation, Elo Ratings, Elo Trajectory, Model Evaluation
"""

import bootstrap
import streamlit as st
import pandas as pd

from components.layout import configure_page
from tabs.configuration import render_configuration_tab
from tabs.simulation import render_simulation_tab
from tabs.elo_ratings import render_elo_ratings_tab
from tabs.elo_evolution import render_elo_evolution_tab
from tabs.evaluation import render_evaluation_tab

from services.simulation_service import run_simulation
from services.initial_ratings_service import (
    get_available_seasons,
    get_initial_ratings,
)
from elo_lab.workflows.optimize_parameters import optimize_parameters_for_config

# Clean metadata API (single source of truth for teams + venues)
from metadata import NFL_TEAMS, NHL_TEAMS, NBA_TEAMS, get_sport_teams, load_teams


# ---------------------------------------------------------------------------
# Page setup
# ---------------------------------------------------------------------------
configure_page()

st.markdown("""
<style>
    .stProgress > div > div > div > div { background-color: #FB4F14 !important; }
    .stCheckbox > label > div[role="checkbox"][aria-checked="true"] {
        background-color: #FB4F14 !important; border-color: #FB4F14 !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("MultiSport Elo Lab")
st.caption("Interactive sports modeling analytics platform | Version 9 (Multiseason + NBA + Advanced parameters)")


# ---------------------------------------------------------------------------
# Model config helpers (unchanged behaviour)
# ---------------------------------------------------------------------------
def build_model_config(home_field, margin_of_victory, elevation, k=20,
                       hfa_value=55, mov_scale=1.0, elev_value=0.0):
    adjustments = {}
    if home_field:
        adjustments["home_field"] = {"enabled": True, "value": hfa_value}
    if margin_of_victory:
        adjustments["margin_of_victory"] = {"enabled": True, "scale": mov_scale}
    if elevation:
        adjustments["elevation_edge"] = {"enabled": True, "value": elev_value}
    return {"k": k, "adjustments": adjustments}


def get_optimize_for(hf, mov, elev, opt_hf, opt_mov, opt_elev):
    opts = []
    if hf and opt_hf:
        opts.append("home_field")
    if mov and opt_mov:
        opts.append("margin_of_victory")
    if elev and opt_elev:
        opts.append("elevation_edge")
    return opts


def _schedule_path(sport: str) -> str:
    mapping = {
        "NHL": "data/nhl_games.csv",
        "NFL": "data/nfl_games.csv",
        "NBA": "data/nba_games.csv",
    }
    return mapping.get(sport, f"data/{sport.lower()}_games.csv")


# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
st.sidebar.header("Model Configuration")

# Sport + Season
sport = st.sidebar.selectbox("Sport", ["NHL", "NBA", "NFL"], index=0)

season_options = get_available_seasons(sport)
season = st.sidebar.selectbox(
    "Season",
    season_options,
    index=len(season_options) - 1 if season_options else 0,
)

st.sidebar.divider()
st.sidebar.subheader("Adjustments")
home_field = st.sidebar.checkbox("Home Field Advantage", value=True)
margin_of_victory = st.sidebar.checkbox("Margin of Victory", value=True)
elevation = st.sidebar.checkbox("Elevation Edge", value=False)

st.sidebar.divider()
optimize_params = st.sidebar.checkbox("Optimize parameters", value=False)
opt_hf = opt_mov = opt_elev = False
if optimize_params:
    if home_field:
        opt_hf = st.sidebar.checkbox("Optimize Home Field", value=True, key="opt_hf")
    if margin_of_victory:
        opt_mov = st.sidebar.checkbox("Optimize Margin", value=True, key="opt_mov")
    if elevation:
        opt_elev = st.sidebar.checkbox("Optimize Elevation", value=False, key="opt_elev")

# ---------------------------------------------------------------------------
# Advanced expander – initial Elo flags + explicit parameter values
# ---------------------------------------------------------------------------
with st.sidebar.expander("Advanced parameters", expanded=False):
    st.markdown("**Initial Elo**")
    rating_source = st.selectbox(
        "Rating source",
        options=["playoffs", "regular_season"],
        index=0,
        help="playoffs (default) uses previous-season playoff results; "
             "regular_season uses final standings.",
    )
    rating_basis = st.selectbox(
        "Rating basis",
        options=["record", "elo"],
        index=0,
        help="record = games above .500 / points above pace → Elo. "
             "elo = previous-season Elo ratings.",
    )
    apply_regression = st.checkbox(
        "Apply regression to mean",
        value=False,
        help="Pull ratings toward the league mean after ranking.",
    )
    regression_strength = st.slider(
        "Regression strength",
        min_value=0.0,
        max_value=0.75,
        value=0.25,
        step=0.05,
        disabled=not apply_regression,
    )

    st.markdown("---")
    st.markdown("**Engine parameters**")
    k = st.slider("k-factor", min_value=5, max_value=40, value=20, step=1)
    hfa_value = st.slider(
        "Home-field advantage value", min_value=0, max_value=100, value=55, step=5
    )
    mov_scale = st.slider(
        "Margin-of-victory scale", min_value=0.0, max_value=3.0, value=1.0, step=0.1
    )
    elev_value = st.slider(
        "Elevation Edge value", min_value=0.0, max_value=50.0, value=0.0, step=1.0
    )

st.sidebar.divider()

simulation_options = [100, 500, 1000, 5000, 10000]
simulation_count = st.sidebar.selectbox(
    "Simulation Count",
    simulation_options,
    index=0,
    format_func=lambda x: f"{x:,}",
)

# ---------------------------------------------------------------------------
# Run Simulation
# ---------------------------------------------------------------------------
if st.sidebar.button("Run Simulation", type="primary"):
    config = build_model_config(
        home_field,
        margin_of_victory,
        elevation,
        k=k,
        hfa_value=hfa_value,
        mov_scale=mov_scale,
        elev_value=elev_value,
    )
    optimize_for = get_optimize_for(
        home_field, margin_of_victory, elevation, opt_hf, opt_mov, opt_elev
    )

    schedule_path = _schedule_path(sport)

    initial_ratings = get_initial_ratings(
        sport,
        schedule_path,
        season=season,
        rating_source=rating_source,
        rating_basis=rating_basis,
        apply_regression=apply_regression,
        regression_strength=regression_strength,
    )

    with st.sidebar.status("Running simulation...", expanded=True) as status:
        pb = st.sidebar.progress(0, text="Starting...")

        if optimize_for:
            pb.progress(20, text="Optimizing parameters...")
            best_config, _ = optimize_parameters_for_config(
                base_config=config,
                optimize_for=optimize_for,
            )
            final_config = best_config
            pb.progress(50, text="Optimization complete")
        else:
            final_config = config
            pb.progress(50, text="Running simulations...")

        pb.progress(70, text="Running Monte Carlo simulations...")
        results = run_simulation(
            config=final_config,
            n_sims=simulation_count,
            initial_ratings=initial_ratings,
            sport=sport,
            season=season,
        )

        # Store everything the tabs already know how to read
        st.session_state["simulation_results"] = results
        st.session_state["sport"] = sport
        st.session_state["season"] = season
        st.session_state["last_config"] = final_config          # used by configuration tab
        st.session_state["optimize_for"] = optimize_for         # used by configuration tab
        st.session_state["final_config"] = final_config
        st.session_state["initial_ratings"] = initial_ratings
        st.session_state["rating_source"] = rating_source
        st.session_state["rating_basis"] = rating_basis
        st.session_state["apply_regression"] = apply_regression

        pb.progress(100, text="Complete!")
        status.update(label="Simulation complete!", state="complete")


# ---------------------------------------------------------------------------
# Main tabs  – signatures match the existing tab modules exactly
# ---------------------------------------------------------------------------
tabs = st.tabs([
    "Model Configuration",
    "Season Simulation",
    "Elo Ratings",
    "Elo Trajectory",
    "Model Evaluation",
])

with tabs[0]:
    # Signature: (sport, season, home_field, margin_of_victory, elevation, simulation_count)
    render_configuration_tab(
        sport=sport,
        season=season,
        home_field=home_field,
        margin_of_victory=margin_of_victory,
        elevation=elevation,
        simulation_count=simulation_count,
    )

with tabs[1]:
    # Signature: (sport="NFL")
    render_simulation_tab(sport=sport)

with tabs[2]:
    # Signature: (sport="NFL")
    render_elo_ratings_tab(sport=sport)

with tabs[3]:
    # Signature: (sport="NFL")
    render_elo_evolution_tab(sport=sport)

with tabs[4]:
    # Signature: ()
    render_evaluation_tab()
