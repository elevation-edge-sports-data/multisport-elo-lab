import streamlit as st
import pandas as pd
import plotly.express as px

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


def render_simulation_tab(sport="NFL"):
    st.header(f"{sport} Season Simulation Results")

    if "simulation_results" not in st.session_state:
        st.info("Run a simulation from the sidebar to see results.")
        return

    results = st.session_state.get("simulation_results", {})
    summary = results.get("summary", pd.DataFrame())
    distribution = results.get("distribution", pd.DataFrame())
    achievement_probs = results.get("achievement_probs", pd.DataFrame())

    if summary.empty:
        st.warning("No simulation results available yet.")
        return

    # ====================== FORCE SHOW ACHIEVEMENT TABLE ======================
    if not achievement_probs.empty:
        st.subheader("Regular Season Achievement Probabilities")

        rename_map = {
            "make_playoffs": "Make Playoffs",
            "home_ice": "Home Ice (Top 2 in Div)",
            "first_in_division": "1st in Division",
            "first_in_conference": "1st in Conference",
            "first_in_league": "1st in League"
        }

        display_df = achievement_probs.rename(columns=rename_map)

        if "Make Playoffs" in display_df.columns:
            display_df = display_df.sort_values("Make Playoffs", ascending=False)

        st.dataframe(display_df, use_container_width=True)
    else:
        st.warning("Achievement probability data is missing from results. This is a temporary display issue.")

    # ====================== TRADITIONAL STATS ======================
    if sport == "NHL":
        metric_col = "mean_points"
        metric_label = "Points"
    else:
        metric_col = "median_wins"
        metric_label = "Wins"

    st.subheader(f"Team {metric_label} Summary")

    if not summary.empty:
        display_df = summary.copy()
        if metric_col in display_df.columns:
            display_df = display_df.sort_values(metric_col, ascending=False)
        st.dataframe(display_df, use_container_width=True)

    # Distribution plot with team colors
    if not distribution.empty and "team" in distribution.columns:
        plot_col = "points" if sport == "NHL" and "points" in distribution.columns else "wins"
        if plot_col in distribution.columns:
            color_map = get_team_color_map(sport)
            fig = px.box(
                distribution,
                x="team",
                y=plot_col,
                color="team",
                color_discrete_map=color_map,
                title=f"Distribution of {metric_label} Across Simulations",
            )
            fig.update_layout(xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

    # Quick stats
    if not summary.empty and metric_col in summary.columns:
        st.subheader("Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            top_idx = summary[metric_col].idxmax()
            st.metric(f"Highest {metric_label}", summary.loc[top_idx, "team"], f"{summary.loc[top_idx, metric_col]:.1f}")
        with col2:
            st.metric(f"Average {metric_label}", f"{summary[metric_col].mean():.1f}")