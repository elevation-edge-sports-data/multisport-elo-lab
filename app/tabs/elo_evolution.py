"""
Elo Trajectory tab – historical / simulated Elo paths with uncertainty bands + logos.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

try:
    from metadata import load_teams, NFL_TEAMS, NHL_TEAMS, NBA_TEAMS
except ImportError:
    from metadata.nfl_teams import NFL_TEAMS
    from metadata.nhl_teams import NHL_TEAMS
    try:
        from metadata.nba_teams import NBA_TEAMS
    except ImportError:
        NBA_TEAMS = {}

    def load_teams(sport):
        return {"NFL": NFL_TEAMS, "NHL": NHL_TEAMS, "NBA": NBA_TEAMS}.get(sport, {})

try:
    from components.logos import render_logo_strip
except ImportError:
    def render_logo_strip(*args, **kwargs):
        pass


DEFAULT_FOCUS = {
    "NBA": ["DEN", "LAL", "SAS", "NYK", "BOS", "CLE"],
    "NHL": ["COL", "VGK", "DAL", "MIN", "CAR", "FLA"],
    "NFL": ["JAX", "BAL", "KC", "DEN", "NE", "BUF"],
}


def get_team_color_map(sport):
    try:
        teams = load_teams(sport)
    except Exception:
        teams = (
            NHL_TEAMS if sport == "NHL"
            else NBA_TEAMS if sport == "NBA"
            else NFL_TEAMS
        )
    color_map = {}
    for abbr, data in teams.items():
        color = data.get("primary_color", "#888888")
        color_map[abbr] = color
        color_map[data.get("name", abbr)] = color
    return color_map


def hex_to_rgba(hex_color: str, alpha: float = 0.13) -> str:
    hex_color = hex_color.lstrip("#")
    if len(hex_color) != 6:
        return f"rgba(128, 128, 128, {alpha})"
    rgb = tuple(int(hex_color[i : i + 2], 16) for i in (0, 2, 4))
    return f"rgba({rgb[0]}, {rgb[1]}, {rgb[2]}, {alpha})"


def render_elo_evolution_tab(sport="NFL"):
    st.header(f"{sport} Elo Trajectory")

    if "simulation_results" not in st.session_state:
        st.info("Run a simulation from the sidebar to see Elo trajectories.")
        return

    results = st.session_state.get("simulation_results", {})
    elo_evolution = results.get("elo_evolution", pd.DataFrame())

    if elo_evolution is None or (hasattr(elo_evolution, "empty") and elo_evolution.empty):
        st.warning("No Elo trajectory data available.")
        return

    color_map = get_team_color_map(sport)
    all_teams = sorted(elo_evolution["team"].unique().tolist())

    preferred = DEFAULT_FOCUS.get(sport, [])
    default_teams = [t for t in preferred if t in all_teams]
    try:
        teams_meta = load_teams(sport)
        name_to_abbr = {data.get("name", ""): abbr for abbr, data in teams_meta.items()}
        for team in all_teams:
            if team in name_to_abbr and name_to_abbr[team] in preferred:
                if team not in default_teams:
                    default_teams.append(team)
    except Exception:
        pass

    default_teams = list(dict.fromkeys(default_teams))

    selected_teams = st.multiselect(
        "Select teams to display",
        options=all_teams,
        default=default_teams,
        help=f"Default focus: {', '.join(preferred)}",
        key=f"elo_traj_teams_{sport}",
    )

    if not selected_teams:
        st.info("Please select at least one team.")
        return

    # Small logo strip for selected teams only (typically 4–8)
    st.caption("Selected teams")
    render_logo_strip(sport, selected_teams, width=36, max_show=12)

    filtered = elo_evolution[elo_evolution["team"].isin(selected_teams)]

    st.subheader("Elo Rating Over Time")

    x_col = "games_played" if "games_played" in filtered.columns else "week"

    fig_elo = px.line(
        filtered,
        x=x_col,
        y="mean_elo",
        color="team",
        color_discrete_map=color_map,
        title="Elo Trajectory (Mean)",
        labels={"mean_elo": "Elo Rating", x_col: "Games Played"},
    )
    fig_elo.update_traces(line=dict(width=2.8))

    for team in selected_teams:
        team_data = filtered[filtered["team"] == team].sort_values(x_col)
        if team_data.empty or "p95_elo" not in team_data.columns:
            continue

        team_color = color_map.get(team, "#666666")
        fill_color = hex_to_rgba(team_color, alpha=0.13)

        fig_elo.add_trace(go.Scatter(
            x=team_data[x_col],
            y=team_data["p95_elo"],
            mode="lines",
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        ))
        fig_elo.add_trace(go.Scatter(
            x=team_data[x_col],
            y=team_data["p05_elo"],
            mode="lines",
            fill="tonexty",
            fillcolor=fill_color,
            line=dict(width=0),
            showlegend=False,
            hoverinfo="skip",
        ))

    fig_elo.update_layout(hovermode="x unified")
    st.plotly_chart(fig_elo, use_container_width=True)

    st.caption("Shaded areas represent the 5th–95th percentile range across simulations.")
