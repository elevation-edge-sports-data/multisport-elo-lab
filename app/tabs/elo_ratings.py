import streamlit as st
import pandas as pd
import plotly.express as px

from metadata.nfl_teams import NFL_TEAMS
from metadata.nhl_teams import NHL_TEAMS


def get_team_color_map(sport):
    """Return a dict mapping team name/abbreviation → primary color"""
    teams = NHL_TEAMS if sport == "NHL" else NFL_TEAMS
    color_map = {}
    for abbr, data in teams.items():
        color = data["primary_color"]
        color_map[abbr] = color
        color_map[data["name"]] = color
    return color_map


def render_elo_ratings_tab(sport="NFL"):
    st.header(f"{sport} Elo Ratings")

    if "simulation_results" not in st.session_state:
        st.info("Run a simulation from the sidebar to view Elo ratings.")
        return

    results = st.session_state.get("simulation_results", {})
    elo_evolution = results.get("elo_evolution", pd.DataFrame())

    if elo_evolution.empty:
        st.warning("No Elo rating data available from the last simulation.")
        return

    # Get latest Elo per team
    if "games_played" in elo_evolution.columns:
        latest_elo = (
            elo_evolution.sort_values("games_played")
            .groupby("team")["mean_elo"]
            .last()
            .reset_index()
            .rename(columns={"mean_elo": "elo"})
            .sort_values("elo", ascending=False)
        )
    else:
        latest_elo = (
            elo_evolution.groupby("team")["mean_elo"]
            .last()
            .reset_index()
            .rename(columns={"mean_elo": "elo"})
            .sort_values("elo", ascending=False)
        )

    color_map = get_team_color_map(sport)

    st.subheader("Final Elo Ratings (Latest from Simulation)")

    # Table
    st.dataframe(latest_elo, use_container_width=True)

    # Bar chart with team colors
    st.subheader("Elo Rating by Team")

    fig = px.bar(
        latest_elo,
        x="team",
        y="elo",
        color="team",
        color_discrete_map=color_map,
        title=f"{sport} Final Elo Ratings",
        labels={"elo": "Elo Rating", "team": "Team"}
    )
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.caption("Note: These are simulated final Elo ratings based on the current season.")