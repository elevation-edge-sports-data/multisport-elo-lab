"""
MultiSport Elo Lab – Streamlit dashboard

Version 12.0 — Simulate upcoming season

  - NHL / NFL / NBA with full playoff-bracket simulation
  - Warm-up Elo: actual regular-season + playoff results from user-chosen
    "Simulate from" season through the season before target, then Monte Carlo
    only the target season
  - Simulatable seasons exclude the seed year (history only)
  - Continuous Elevation Edge
  - Sport-specific home advantage labels (ice / court / field)
  - Log5 baseline + residual diagnostics + corrected baseline ladder
  - Precomputed default simulations loaded instantly on sport change
  - Export Results as quiet text-style control
  - Tabs: Regular Season Projections · Playoff Projections (default) · Model Comparison
"""

from __future__ import annotations

import pickle
from pathlib import Path

import bootstrap
import streamlit as st
import pandas as pd

from components.layout import configure_page
from tabs.simulation import render_simulation_tab
from tabs.elo_evolution import render_elo_evolution_tab
from tabs.evaluation import render_evaluation_tab

from services.simulation_service import run_simulation
from services.initial_ratings_service import (
    get_available_seasons,
    get_simulatable_seasons,
    get_seed_season,
    get_simulate_from_options,
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
    /* Quiet export control */
    div[data-testid="stDownloadButton"] button {
        background-color: transparent !important;
        color: #6b7280 !important;
        border: none !important;
        box-shadow: none !important;
        font-weight: 400 !important;
        text-decoration: underline;
        padding: 0.25rem 0 !important;
    }
    div[data-testid="stDownloadButton"] button:hover {
        color: #374151 !important;
        background-color: transparent !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("MultiSport Elo Lab")
st.caption("Simulate upcoming season · NFL / NHL / NBA | Version 12.0")


# ---------------------------------------------------------------------------
# Model config helpers
# ---------------------------------------------------------------------------
def build_model_config(home_field, margin_of_victory, elevation, k=20,
                       hfa_value=55, elev_value=1.0):
    """Build declarative model config. MOV is pure binary (scale fixed at 1.0)."""
    adjustments = {}
    if home_field:
        adjustments["home_field"] = {"enabled": True, "value": hfa_value}
    if margin_of_victory:
        # Pure binary: on = margin-scaled update with fixed scale 1.0
        adjustments["margin_of_victory"] = {"enabled": True, "scale": 1.0}
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
        f"Target season for Monte Carlo. Elo is warmed from the "
        f"'Simulate from' season up to the prior year"
        f"{f' (seed year {seed_year} is history-only)' if seed_year else ''}."
    ),
)
st.session_state["season"] = season

# ------------------------------------------------------------------
# Simulate from (explicit warm-up start)
# ------------------------------------------------------------------
from_options = get_simulate_from_options(sport, target_season=season)
if from_options:
    # Default = earliest possible
    default_from_idx = 0
    simulate_from = st.sidebar.selectbox(
        "Simulate from",
        from_options,
        index=default_from_idx,
        help=(
            "First season included in the Elo warm-up. "
            "History runs from this season through the year before the target. "
            "The earliest season in the data is seed-only and is not offered here."
        ),
    )
else:
    simulate_from = None
st.session_state["simulate_from"] = simulate_from

st.sidebar.divider()
st.sidebar.subheader("Adjustments")
home_field = st.sidebar.checkbox(_home["checkbox"], value=True)
margin_of_victory = st.sidebar.checkbox(
    "Margin of Victory",
    value=True,
    help="On = post-game Elo update is scaled by margin of victory. "
         "Off = update depends only on win/loss.",
)
elevation = st.sidebar.checkbox("Elevation Edge", value=False)
apply_regression = st.sidebar.checkbox(
    "Apply regression to mean",
    value=True,
    help="Pull ratings toward the league mean after ranking / between seasons.",
)

st.sidebar.divider()

# ------------------------------------------------------------------
# Grid Search hierarchy: master checkbox, then indented targets
# ------------------------------------------------------------------
optimize_params = st.sidebar.checkbox("Grid Search", value=False)
opt_hf = opt_mov = opt_elev = False
if optimize_params:
    st.sidebar.caption("Select which parameters to search:")
    if home_field:
        opt_hf = st.sidebar.checkbox(_home["optimize"], value=True, key="opt_hf")
    if margin_of_victory:
        opt_mov = st.sidebar.checkbox("Optimize MOV", value=True, key="opt_mov")
    if elevation:
        opt_elev = st.sidebar.checkbox("Optimize Elevation", value=False, key="opt_elev")

# Fixed (non-user-facing) initial-Elo policy:
#   rating_source always "playoffs"
#   rating_basis prefers "elo" when available, else falls back to "record"
rating_source = "playoffs"
rating_basis = "elo"

# ---------------------------------------------------------------------------
# Advanced expander – engine knobs only (Initial Elo UI removed)
# ---------------------------------------------------------------------------
with st.sidebar.expander("Customize Parameters", expanded=False):
    regression_strength = st.slider(
        "Regression strength",
        min_value=0.0,
        max_value=1.0,
        value=0.25,
        step=0.05,
        disabled=not apply_regression,
        help="How strongly ratings are pulled toward the league mean when "
             "regression is enabled.",
    )

    st.markdown("---")
    st.markdown("**Engine parameters**")
    k = st.slider(
        "k-factor",
        min_value=5,
        max_value=40,
        value=20,
        step=1,
        help="How much ratings move after each game. "
             "Higher k = more reactive (recent results dominate). "
             "Lower k = more stable (history carries more weight).",
    )
    hfa_value = st.slider(
        _home["slider"], min_value=0, max_value=100, value=55, step=5
    )
    # MOV scale removed – pure binary via the Adjustments checkbox
    elev_value = st.slider(
        "Elevation Edge",
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
# Run Simulation + Stop placement
# ---------------------------------------------------------------------------
run_clicked = st.sidebar.button("Run Simulation", type="primary")

# Placeholder for future async stop control (Streamlit runs are synchronous today).
# Kept under Run so the action cluster stays together.
if st.session_state.get("_sim_running"):
    st.sidebar.button("Stop Simulation", type="secondary", disabled=True,
                      help="Stop is not yet supported for in-progress runs. "
                           "Refresh the page to cancel.")

if run_clicked:
    config = build_model_config(
        home_field,
        margin_of_victory,
        elevation,
        k=k,
        hfa_value=hfa_value,
        elev_value=elev_value,
    )
    optimize_for = get_optimize_for(
        home_field, margin_of_victory, elevation, opt_hf, opt_mov, opt_elev
    )

    initial_ratings = {}  # warm-up starts flat; actual history sets Elo

    st.session_state["_sim_running"] = True
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
            from_season=simulate_from,
        )

        # Store everything the tabs already know how to read
        st.session_state["simulation_results"] = results
        st.session_state["sport"] = sport
        st.session_state["season"] = season
        st.session_state["simulate_from"] = simulate_from
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
    st.session_state["_sim_running"] = False


# ---------------------------------------------------------------------------
# Global Export – quiet text-style control
# ---------------------------------------------------------------------------
if st.session_state.get("simulation_results") is not None:
    try:
        export_bytes = build_full_export(st.session_state)
        filename = make_export_filename(st.session_state)

        _left, _right = st.columns([3, 1])
        with _right:
            st.download_button(
                label="Export Results (.xlsx)",
                data=export_bytes,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                help=(
                    "Downloads Config, Simulation Summary, Achievement/Playoff probabilities, "
                    "Elo Ratings, and Evaluation metrics in one Excel file."
                ),
                # type intentionally omitted / secondary so CSS can quiet it
            )
    except Exception as e:
        # Never let export problems break the rest of the dashboard
        st.warning(f"Export temporarily unavailable: {e}")


# ---------------------------------------------------------------------------
# Main tabs (v12 three-tab structure)
#   1. Regular Season Projections  (former Elo Trajectory)
#   2. Playoff Projections         (former Season Simulation) — default landing
#   3. Model Comparison            (former Model Evaluation)
#
# Streamlit st.tabs always opens the first tab. To make Playoff Projections the
# default landing view we place it first in the widget, while the visual/logical
# product order remains Regular → Playoff → Model via the labels below only if
# we accepted first-tab default = Regular. Instead we put Playoff first so the
# app lands on the primary fan-facing view.
# ---------------------------------------------------------------------------
tabs = st.tabs([
    "Playoff Projections",
    "Regular Season Projections",
    "Model Comparison",
])

with tabs[0]:
    # Default landing tab
    if st.session_state.get("is_default_run"):
        st.caption(
            "Showing precomputed default simulation. "
            "Click **Run Simulation** in the sidebar to re-run with your current settings."
        )
    render_simulation_tab(sport=sport)

with tabs[1]:
    render_elo_evolution_tab(sport=sport)

with tabs[2]:
    render_evaluation_tab()
