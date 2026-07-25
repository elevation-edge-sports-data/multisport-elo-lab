import streamlit as st
import pandas as pd
import plotly.express as px

try:
    from metadata import load_teams, NFL_TEAMS, NHL_TEAMS, NBA_TEAMS
except ImportError:
    from metadata import NFL_TEAMS, NHL_TEAMS
    try:
        from metadata import NBA_TEAMS
    except ImportError:
        NBA_TEAMS = {}
    def load_teams(sport):
        return {"NFL": NFL_TEAMS, "NHL": NHL_TEAMS, "NBA": NBA_TEAMS}.get(sport, {})


def get_team_color_map(sport: str) -> dict:
    try:
        teams = load_teams(sport)
    except Exception:
        teams = NHL_TEAMS if sport == "NHL" else (NBA_TEAMS if sport == "NBA" else NFL_TEAMS)
    color_map = {}
    for abbr, data in teams.items():
        color = data.get("primary_color", "#888888")
        color_map[abbr] = color
        color_map[data.get("name", abbr)] = color
    return color_map


def render_elo_ratings_tab(sport="NFL"):
    st.header(f"{sport} Elo Ratings")

    if "simulation_results" not in st.session_state:
        st.info("Run a simulation from the sidebar to view Elo ratings.")
        return

    results = st.session_state.get("simulation_results", {})
    elo_evolution = results.get("elo_evolution", pd.DataFrame())

    if elo_evolution is None or (hasattr(elo_evolution, "empty") and elo_evolution.empty):
        st.warning("No Elo rating data available from the last simulation.")
        return

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
    st.dataframe(latest_elo, use_container_width=True)

    st.subheader("Elo Rating by Team")
    fig = px.bar(
        latest_elo,
        x="team",
        y="elo",
        color="team",
        color_discrete_map=color_map,
        title=f"{sport} Final Elo Ratings",
        labels={"elo": "Elo Rating", "team": "Team"},
    )
    fig.update_layout(xaxis_tickangle=-45, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

    st.caption("Note: These are simulated final Elo ratings based on the current season.")
