"""
Elo Ratings tab – final simulated Elo rankings with team logos.

Final rankings prefer summary["mean_elo"] (end-of-season Elo averaged across
sims from the same standings that produce wins/points). Falls back to
elo_evolution only if summary has no mean_elo column.
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


def _latest_elo_from_summary(summary: pd.DataFrame) -> pd.DataFrame | None:
    """End-of-season mean Elo from the same standings as wins/points."""
    if summary is None or getattr(summary, "empty", True):
        return None
    if "mean_elo" not in summary.columns:
        return None
    out = (
        summary[["team", "mean_elo"]]
        .rename(columns={"mean_elo": "elo"})
        .sort_values("elo", ascending=False)
        .reset_index(drop=True)
    )
    return out


def _latest_elo_from_evolution(elo_evolution: pd.DataFrame) -> pd.DataFrame | None:
    """Fallback: last games_played row per team in elo_evolution."""
    if elo_evolution is None or getattr(elo_evolution, "empty", True):
        return None
    if "mean_elo" not in elo_evolution.columns:
        return None
    df = elo_evolution.copy()
    if "games_played" in df.columns:
        idx = df.groupby("team")["games_played"].idxmax()
        latest = df.loc[idx, ["team", "mean_elo"]]
    else:
        latest = (
            df.groupby("team")["mean_elo"]
            .last()
            .reset_index()
        )
    return (
        latest.rename(columns={"mean_elo": "elo"})
        .sort_values("elo", ascending=False)
        .reset_index(drop=True)
    )


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
    if not results:
        st.info(
            "Run a simulation from the sidebar (or wait for precomputed defaults) "
            "to see ranked Elo with team logos."
        )
        return

    summary = results.get("summary", pd.DataFrame())
    elo_evolution = results.get("elo_evolution", pd.DataFrame())

    latest_elo = _latest_elo_from_summary(summary)
    source = "end-of-season Elo (same standings as wins/points)"
    if latest_elo is None:
        latest_elo = _latest_elo_from_evolution(elo_evolution)
        source = "elo_evolution trajectory (fallback)"

    if latest_elo is None or latest_elo.empty:
        st.warning("No Elo rating data available from the last simulation.")
        return

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

    st.caption(f"Source: {source}. Logos from app/assets/logos/{{sport}}/.")
