import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from metadata.nfl_teams import NFL_TEAMS
from metadata.nhl_teams import NHL_TEAMS


def get_team_color_map(sport):
    teams = NHL_TEAMS if sport == "NHL" else NFL_TEAMS
    color_map = {}
    for abbr, data in teams.items():
        color = data["primary_color"]
        color_map[abbr] = color
        color_map[data["name"]] = color
    return color_map


def hex_to_rgba(hex_color: str, alpha: float = 0.13) -> str:
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"


def render_elo_evolution_tab(sport="NFL"):
    st.header(f"{sport} Elo Trajectory")

    if "simulation_results" not in st.session_state:
        st.info("Run a simulation from the sidebar to see Elo trajectories.")
        return

    results = st.session_state.get("simulation_results", {})
    elo_evolution = results.get("elo_evolution", pd.DataFrame())

    if elo_evolution.empty:
        st.warning("No Elo trajectory data available.")
        return

    color_map = get_team_color_map(sport)
    all_teams = sorted(elo_evolution["team"].unique())

    # Default team selection
    if sport == "NHL":
        preferred = ["COL", "VGK", "DAL", "MIN", "CAR", "FLA"]
        name_to_abbr = {data["name"]: abbr for abbr, data in NHL_TEAMS.items()}
        default_teams = []
        for team in all_teams:
            if team in preferred:
                default_teams.append(team)
            elif team in name_to_abbr and name_to_abbr[team] in preferred:
                default_teams.append(team)
    else:
        preferred = ["JAX", "BAL", "KC", "DEN", "NE", "BUF"]
        default_teams = [t for t in all_teams if t in preferred]

    default_teams = list(dict.fromkeys(default_teams))

    selected_teams = st.multiselect(
        "Select teams to display",
        options=all_teams,
        default=default_teams
    )

    if not selected_teams:
        st.info("Please select at least one team.")
        return

    filtered = elo_evolution[elo_evolution["team"].isin(selected_teams)]

    # ====================== ELO TRAJECTORY ======================
    st.subheader("Elo Rating Over Time")

    fig_elo = px.line(
        filtered,
        x="games_played",
        y="mean_elo",
        color="team",
        color_discrete_map=color_map,
        title="Elo Trajectory (Mean)",
        labels={"mean_elo": "Elo Rating", "games_played": "Games Played"}
    )
    fig_elo.update_traces(line=dict(width=2.8))

    # Transparent team-colored confidence bands
    for team in selected_teams:
        team_data = filtered[filtered["team"] == team].sort_values("games_played")
        if team_data.empty:
            continue

        team_color = color_map.get(team, "#666666")
        fill_color = hex_to_rgba(team_color, alpha=0.13)

        fig_elo.add_trace(go.Scatter(
            x=team_data["games_played"],
            y=team_data["p95_elo"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip"
        ))

        fig_elo.add_trace(go.Scatter(
            x=team_data["games_played"],
            y=team_data["p05_elo"],
            mode="lines",
            fill="tonexty",
            fillcolor=fill_color,
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip"
        ))

    fig_elo.update_layout(hovermode="x unified")
    st.plotly_chart(fig_elo, use_container_width=True)

    st.caption("Shaded areas represent the 5th–95th percentile range across simulations.")