"""
Elo Ratings tab – final simulated Elo rankings with team logos.

Logos appear only in the ranked list / top strip (small N), never a full
alphabetical grid — that was too heavy for Streamlit's full-script rerun model.
"""

from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px

try:
    from metadata import (
        load_teams,
        NFL_TEAMS,
        NHL_TEAMS,
        NBA_TEAMS,
        get_team_metadata,
    )
except ImportError:
    from metadata import NFL_TEAMS, NHL_TEAMS
    try:
        from metadata import NBA_TEAMS
    except ImportError:
        NBA_TEAMS = {}

    def load_teams(sport):
        return {"NFL": NFL_TEAMS, "NHL": NHL_TEAMS, "NBA": NBA_TEAMS}.get(sport, {})

    def get_team_metadata(sport, abbr):
        return load_teams(sport).get(abbr, {})

from components.logos import (
    render_ranked_elo_list,
    render_logo_strip,
    team_display_name,
)


def get_team_color_map(sport: str) -> dict:
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


def _latest_elo_frame(elo_evolution: pd.DataFrame) -> pd.DataFrame:
    """Extract the most recent mean Elo per team, sorted descending."""
    if "games_played" in elo_evolution.columns:
        latest = (
            elo_evolution.sort_values("games_played")
            .groupby("team")["mean_elo"]
            .last()
            .reset_index()
            .rename(columns={"mean_elo": "elo"})
        )
    else:
        latest = (
            elo_evolution.groupby("team")["mean_elo"]
            .last()
            .reset_index()
            .rename(columns={"mean_elo": "elo"})
        )
    return latest.sort_values("elo", ascending=False).reset_index(drop=True)


def _apply_conference_filter(df: pd.DataFrame, sport: str, conference: str) -> pd.DataFrame:
    if conference == "All":
        return df
    teams_meta = load_teams(sport)
    keep = {
        abbr for abbr, meta in teams_meta.items()
        if meta.get("conference") == conference
    }
    name_to_abbr = {meta.get("name"): abbr for abbr, meta in teams_meta.items()}
    mask = df["team"].isin(keep) | df["team"].map(lambda t: name_to_abbr.get(t) in keep)
    return df[mask].reset_index(drop=True)


def render_elo_ratings_tab(sport: str = "NFL"):
    st.header(f"{sport} Elo Ratings")

    results = st.session_state.get("simulation_results")
    elo_evolution = None
    if results is not None:
        elo_evolution = results.get("elo_evolution", pd.DataFrame())
        if elo_evolution is not None and hasattr(elo_evolution, "empty") and elo_evolution.empty:
            elo_evolution = None

    if elo_evolution is None:
        st.info(
            "Run a simulation from the sidebar (or wait for precomputed defaults) "
            "to see ranked Elo with team logos."
        )
        return

    latest_elo = _latest_elo_frame(elo_evolution)

    conferences = ["All"]
    try:
        teams_meta = load_teams(sport)
        confs = sorted({
            m.get("conference") for m in teams_meta.values()
            if m.get("conference")
        })
        conferences.extend(confs)
    except Exception:
        pass

    col_f1, col_f2, _ = st.columns([2, 2, 4])
    with col_f1:
        selected_conf = st.selectbox(
            "Conference",
            options=conferences,
            index=0,
            help="Filter rankings by conference",
            key=f"elo_conf_{sport}",
        )
    with col_f2:
        show_all = st.checkbox("Show all teams", value=True, key=f"elo_all_{sport}")

    filtered = _apply_conference_filter(latest_elo, sport, selected_conf)
    display_df = filtered if show_all else filtered.head(16)

    top_teams = display_df["team"].head(8).tolist()
    if top_teams:
        st.caption("Top teams")
        render_logo_strip(sport, top_teams, width=36, max_show=8)

    st.subheader("Final Elo Rankings")
    render_ranked_elo_list(
        sport,
        display_df,
        max_rows=None if show_all else 16,
        logo_width=36,
    )

    st.subheader("Elo Rating by Team")
    color_map = get_team_color_map(sport)

    chart_df = display_df.copy()
    chart_df["display_name"] = chart_df["team"].map(
        lambda t: team_display_name(sport, t)
    )

    fig = px.bar(
        chart_df,
        x="display_name",
        y="elo",
        color="team",
        color_discrete_map=color_map,
        title=f"{sport} Final Elo Ratings",
        labels={"elo": "Elo Rating", "display_name": "Team"},
    )
    fig.update_layout(
        xaxis_tickangle=-45,
        showlegend=False,
        margin=dict(b=120),
        height=480,
    )
    st.plotly_chart(fig, use_container_width=True)

    st.caption(
        "Simulated final Elo ratings from the current run. "
        "Logos load from app/assets/logos/{sport}/."
    )
