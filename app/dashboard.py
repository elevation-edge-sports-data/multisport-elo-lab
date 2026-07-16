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
from elo_lab.workflows.optimize_parameters import optimize_parameters_for_config

from metadata.nfl_teams import NFL_TEAMS
from metadata.nhl_teams import NHL_TEAMS


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
st.caption("Interactive sports modeling analytics platform | Version 8 (NHL Integration)")

def get_sport_teams(sport):
    return NHL_TEAMS if sport == "NHL" else NFL_TEAMS

def get_available_seasons(sport):
    schedule_path = "data/nhl_games.csv" if sport == "NHL" else "data/nfl_games.csv"
    try:
        schedule = pd.read_csv(schedule_path)
        if "season" in schedule.columns:
            seasons = sorted([str(s) for s in schedule["season"].dropna().unique()])
            return seasons
    except:
        pass
    return ["2025-26"] if sport == "NHL" else ["2025"]

def get_initial_ratings(sport, schedule_path=None):
    if schedule_path is None:
        schedule_path = "data/nhl_games.csv" if sport == "NHL" else "data/nfl_games.csv"

    try:
        schedule = pd.read_csv(schedule_path)
        teams = pd.concat([schedule["home_team"], schedule["away_team"]]).unique()
    except:
        teams = list(NHL_TEAMS.keys()) if sport == "NHL" else list(NFL_TEAMS.keys())

    if sport == "NHL":
        # Initial Elo ratings derived from final 2025-26 regular season standings
        base_elo = {
            "COL": 1620, "CAR": 1590, "DAL": 1585, "BUF": 1570,
            "FLA": 1560, "VGK": 1555, "MIN": 1545, "MTL": 1540,
            "TBL": 1535, "NYR": 1530, "EDM": 1525, "WPG": 1520,
            "BOS": 1515, "LAK": 1510, "NSH": 1505, "PHI": 1500,
            "SEA": 1495, "VAN": 1490, "NYI": 1485, "WSH": 1480,
            "PIT": 1475, "DET": 1470, "CBJ": 1465, "OTT": 1460,
            "CGY": 1455, "TOR": 1450, "CHI": 1445, "ANA": 1440,
            "SJS": 1435, "UTA": 1430, "NJD": 1425,
        }
        return {team: base_elo.get(team, 1500) for team in teams}
    
    else:
        # NFL initial Elo ratings derived from final 2025 regular season standings
        # (same methodology as prior year: rank by final W-L-T / PCT, assign descending from ~1610 by steps of 10)
        # 2025 final standings: DEN/NE/SEA 14-3, JAX 13-4, BUF/HOU/LAR/SF 12-5, etc.
        # This places Denver near the top as the AFC #1 seed / co-best record.
        base_elo = {
            "DEN": 1610, "NE": 1600, "SEA": 1590, "JAX": 1580,
            "BUF": 1570, "HOU": 1560, "LAR": 1550, "SF": 1540,
            "CHI": 1530, "LAC": 1520, "PHI": 1510, "PIT": 1500,
            "GB": 1490, "DET": 1480, "MIN": 1470, "ATL": 1460,
            "BAL": 1450, "CAR": 1440, "TB": 1430, "IND": 1420,
            "DAL": 1410, "MIA": 1400, "CIN": 1390, "KC": 1380,
            "NO": 1370, "CLE": 1360, "WAS": 1350, "NYG": 1340,
            "ARI": 1330, "LV": 1320, "NYJ": 1310, "TEN": 1300,
        }
        return {team: base_elo.get(team, 1500) for team in teams}

def build_model_config(home_field, margin_of_victory, elevation):
    adjustments = {}
    if home_field: adjustments["home_field"] = {"enabled": True, "value": 55}
    if margin_of_victory: adjustments["margin_of_victory"] = {"enabled": True, "scale": 1.0}
    if elevation: adjustments["elevation_edge"] = {"enabled": True, "value": 0.0}
    return {"k": 20, "adjustments": adjustments}

def get_optimize_for(hf, mov, elev, opt_hf, opt_mov, opt_elev):
    opts = []
    if hf and opt_hf: opts.append("home_field")
    if mov and opt_mov: opts.append("margin_of_victory")
    if elev and opt_elev: opts.append("elevation_edge")
    return opts

# ==================== SIDEBAR ====================
st.sidebar.header("Model Configuration")

sport = st.sidebar.selectbox("Sport", ["NHL", "NFL"], index=0)  # Default = NHL

season_options = get_available_seasons(sport)
season = st.sidebar.selectbox("Season", season_options, index=0)

st.sidebar.divider()
st.sidebar.subheader("Adjustments")
home_field = st.sidebar.checkbox("Home Field Advantage", value=True)
margin_of_victory = st.sidebar.checkbox("Margin of Victory", value=True)
elevation = st.sidebar.checkbox("Elevation Edge", value=False)

st.sidebar.divider()
optimize_params = st.sidebar.checkbox("Optimize parameters", value=False)
opt_hf = opt_mov = opt_elev = False
if optimize_params:
    if home_field: opt_hf = st.sidebar.checkbox("Optimize Home Field", value=True, key="opt_hf")
    if margin_of_victory: opt_mov = st.sidebar.checkbox("Optimize Margin", value=True, key="opt_mov")
    if elevation: opt_elev = st.sidebar.checkbox("Optimize Elevation", value=False, key="opt_elev")

st.sidebar.divider()

simulation_options = [100, 500, 1000, 5000, 10000]
simulation_count = st.sidebar.selectbox(
    "Simulation Count",
    simulation_options,
    index=0,  # Default = 100
    format_func=lambda x: f"{x:,}"
)

if st.sidebar.button("Run Simulation"):
    config = build_model_config(home_field, margin_of_victory, elevation)
    optimize_for = get_optimize_for(home_field, margin_of_victory, elevation, opt_hf, opt_mov, opt_elev)
    
    schedule_path = "data/nhl_games.csv" if sport == "NHL" else "data/nfl_games.csv"
    initial_ratings = get_initial_ratings(sport, schedule_path)

    with st.sidebar.status("Running simulation...", expanded=True) as status:
        pb = st.sidebar.progress(0, text="Starting...")
        
        if optimize_for:
            pb.progress(20, "Optimizing parameters...")
            best_config, _ = optimize_parameters_for_config(base_config=config, optimize_for=optimize_for)
            final_config = best_config
            pb.progress(50, "Optimization complete")
        else:
            final_config = config
            pb.progress(50, "Running simulations...")

        pb.progress(70, "Running Monte Carlo simulations...")
        results = run_simulation(
            config=final_config,
            n_sims=simulation_count,
            initial_ratings=initial_ratings,
            sport=sport,
            season=season,
        )
        st.session_state["simulation_results"] = results
        st.session_state["sport"] = sport
        pb.progress(100, "Complete!")
        status.update(label="Simulation complete!", state="complete")

# ==================== TABS ====================
tabs = st.tabs([
    "Model Configuration",
    "Season Simulation",
    "Elo Ratings",
    "Elo Trajectory",
    "Model Evaluation"
])

with tabs[0]:
    render_configuration_tab(
        sport=sport, season=season,
        home_field=home_field, margin_of_victory=margin_of_victory,
        elevation=elevation, simulation_count=simulation_count
    )

with tabs[1]:
    render_simulation_tab(sport=sport)

with tabs[2]:
    render_elo_ratings_tab(sport=sport)

with tabs[3]:
    render_elo_evolution_tab(sport=sport)

with tabs[4]:
    render_evaluation_tab()