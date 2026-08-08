"""
MultiSport Elo Lab – Streamlit dashboard

Version 11.5 – Warm-up Elo from recent actual seasons + multi-sport Monte Carlo

  - NHL / NFL / NBA with full playoff-bracket simulation
  - Warm-up Elo: actual regular-season + playoff results from recent completed
    seasons (playoff k×1.75, stronger regression toward 1500), then Monte Carlo
    only the target season (prior releases used a prior-only start)
  - Simulatable seasons exclude the seed year (history only)
  - Continuous Elevation Edge (Elo pts per 1000 ft)
  - Sport-specific home advantage labels (ice / court / field)
  - Log5 baseline + residual diagnostics
  - Precomputed default simulations loaded instantly on sport change
  - Global one-click full results export (multi-sheet Excel)
  - Team logos in Elo Ratings, Trajectory, and Simulation views
  - Tabs: Configuration, Season Simulation, Elo Ratings, Elo Trajectory, Model Evaluation
"""

from __future__ import annotations

import pickle
from pathlib import Path

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
    get_simulatable_seasons,
    get_seed_season,
    get_initial_ratings,
)
from services.export_service import build_full_export, make_export_filename
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
st.caption("Warm-up Elo from recent seasons · Monte Carlo target · NHL / NBA / NFL | Version 11.5")


# ---------------------------------------------------------------------------
# Model config helpers
# ---------------------------------------------------------------------------
def build_model_config(home_field, margin_of_victory, elevation, k=20,
                       hfa_value=55, mov_scale=1.0, elev_value=1.0):
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
# Precomputed default results loader
# ---------------------------------------------------------------------------
PRECOMPUTED_DIR = Path("data/precomputed")


def load_default_results(sport: str):
    """Return the precomputed simulation dict for `sport`, or None."""
    path = PRECOMPUTED_DIR / f"{sport}_default.pkl"
    if not path.exists():
        return None
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None


# Sport-specific home advantage display labels (config key remains "home_field")
_HOME_ADV_LABELS = {
    "NHL": {
        "checkbox": "Home-Ice Advantage",
        "slider": "Home-ice advantage value",
        "optimize": "Optimize Home Ice",
    },
    "NBA": {
        "checkbox": "Home-Court Advantage",
        "slider": "Home-court advantage value",
        "optimize": "Optimize Home Court",
    },
    "NFL": {
        "checkbox": "Home-Field Advantage",
        "slider": "Home-field advantage value",
        "optimize": "Optimize Home Field",
    },
}


# ---------------------------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------------------------
st.sidebar.header("Model Configuration")

# Sport + Season
sport = st.sidebar.selectbox("Sport", ["NHL", "NBA", "NFL"], index=0)
st.session_state["sport"] = sport  # available to evaluation tab before Run Simulation

# ------------------------------------------------------------------
# Auto-load precomputed defaults when sport changes (or on first load)
# ------------------------------------------------------------------
_prev_sport = st.session_state.get("_loaded_sport")
if (
    "simulation_results" not in st.session_state
    or _prev_sport != sport
):
    defaults = load_default_results(sport)
    if defaults is not None:
        st.session_state["simulation_results"] = defaults
        st.session_state["_loaded_sport"] = sport
        st.session_state["is_default_run"] = True
    else:
        # No precomputed file – clear any stale results from another sport
        if _prev_sport != sport:
            st.session_state.pop("simulation_results", None)
            st.session_state.pop("is_default_run", None)
        st.session_state["_loaded_sport"] = sport

_home = _HOME_ADV_LABELS.get(sport, _HOME_ADV_LABELS["NFL"])

season_options = get_simulatable_seasons(sport)
seed_year = get_seed_season(sport)
season = st.sidebar.selectbox(
    "Season",
    season_options,
    index=len(season_options) - 1 if season_options else 0,
    help=(
        f"Target season. Elo is warmed on actual results before this year"
        f" (history from {seed_year})."
        if seed_year else "Target season."
    ),
)
st.session_state["season"] = season

st.sidebar.divider()
st.sidebar.subheader("Adjustments")
home_field = st.sidebar.checkbox(_home["checkbox"], value=True)
margin_of_victory = st.sidebar.checkbox("Margin of Victory", value=True)
elevation = st.sidebar.checkbox("Elevation Edge", value=False)

st.sidebar.divider()
optimize_params = st.sidebar.checkbox("Optimize parameters", value=False)
opt_hf = opt_mov = opt_elev = False
if optimize_params:
    if home_field:
        opt_hf = st.sidebar.checkbox(_home["optimize"], value=True, key="opt_hf")
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
        _home["slider"], min_value=0, max_value=100, value=55, step=5
    )
    mov_scale = st.slider(
        "Margin-of-victory scale", min_value=0.0, max_value=3.0, value=1.0, step=0.1
    )
    elev_value = st.slider(
        "Elevation Edge (Elo pts per 1000 ft)",
        min_value=0.0,
        max_value=10.0,
        value=1.0,
        step=0.5,
        help="Home-team Elo boost = value × max(0, home_ft − away_ft) / 1000. "
             "Default 1.0. Optimization searches [0, 2, 4, 6, 8, 10].",
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

    initial_ratings = {}  # warm-up starts flat; actual history sets Elo

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
        st.session_state["last_config"] = final_config
        st.session_state["optimize_for"] = optimize_for
        st.session_state["final_config"] = final_config
        st.session_state["initial_ratings"] = initial_ratings
        st.session_state["rating_source"] = rating_source
        st.session_state["rating_basis"] = rating_basis
        st.session_state["apply_regression"] = apply_regression
        st.session_state["is_default_run"] = False          # custom run overrides defaults
        st.session_state["_loaded_sport"] = sport

        pb.progress(100, text="Complete!")
        status.update(label="Simulation complete!", state="complete")


# ---------------------------------------------------------------------------
# Global Export – top-right placement after defaults / simulation
# ---------------------------------------------------------------------------
if st.session_state.get("simulation_results") is not None:
    try:
        export_bytes = build_full_export(st.session_state)
        filename = make_export_filename(st.session_state)

        _left, _right = st.columns([3, 1])
        with _right:
            st.download_button(
                label="Download Full Results (.xlsx)",
                data=export_bytes,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help=(
                    "Downloads Config, Simulation Summary, Achievement/Playoff probabilities, "
                    "Elo Ratings, and Evaluation metrics in one Excel file."
                ),
                type="primary",
            )
    except Exception as e:
        # Never let export problems break the rest of the dashboard
        st.warning(f"Export temporarily unavailable: {e}")


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
    render_configuration_tab(
        sport=sport,
        season=season,
        home_field=home_field,
        margin_of_victory=margin_of_victory,
        elevation=elevation,
        simulation_count=simulation_count,
    )

with tabs[1]:
    # Optional caption when showing precomputed defaults
    if st.session_state.get("is_default_run"):
        st.caption(
            "Showing precomputed default simulation. "
            "Click **Run Simulation** in the sidebar to re-run with your current settings."
        )
    render_simulation_tab(sport=sport)

with tabs[2]:
    render_elo_ratings_tab(sport=sport)

with tabs[3]:
    render_elo_evolution_tab(sport=sport)

with tabs[4]:
    render_evaluation_tab()
