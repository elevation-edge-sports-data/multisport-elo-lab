import streamlit as st
import pandas as pd
import plotly.express as px

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


def get_team_color_map(sport):
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


def render_simulation_tab(sport="NFL"):
    st.header(f"{sport} Season Simulation Results")

    if "simulation_results" not in st.session_state:
        st.info("Run a simulation from the sidebar to see results.")
        return

    results = st.session_state.get("simulation_results", {})
    summary = results.get("summary", pd.DataFrame())
    distribution = results.get("distribution", pd.DataFrame())
    achievement_probs = results.get("achievement_probs", pd.DataFrame())
    playoff_probs = results.get("playoff_probs", {})

    if summary is None or (hasattr(summary, "empty") and summary.empty):
        st.warning("No simulation results available yet.")
        return

    # ------------------------------------------------------------------
    # NEW: Playoff Outlook (NFL only for now)
    # ------------------------------------------------------------------
    if sport == "NFL" and playoff_probs:
        st.subheader("Playoff Outlook")

        # Convert dict-of-dicts → DataFrame
        rows = []
        for team, probs in playoff_probs.items():
            row = {"team": team}
            row.update(probs)
            rows.append(row)
        playoff_df = pd.DataFrame(rows)

        # Friendly column names and ordering
        col_order = ["team", "Wild Card", "Divisional", "Conference", "Super Bowl", "Champion"]
        existing = [c for c in col_order if c in playoff_df.columns]
        playoff_df = playoff_df[existing]

        rename = {
            "Wild Card": "Reach Wild Card",
            "Divisional": "Reach Divisional",
            "Conference": "Reach Conference",
            "Super Bowl": "Reach Super Bowl",
            "Champion": "Win Super Bowl",
        }
        playoff_df = playoff_df.rename(columns=rename)

        # Sort by championship probability
        if "Win Super Bowl" in playoff_df.columns:
            playoff_df = playoff_df.sort_values("Win Super Bowl", ascending=False)

        # Display as percentages
        pct_cols = [c for c in playoff_df.columns if c != "team"]
        display_df = playoff_df.copy()
        for c in pct_cols:
            display_df[c] = (display_df[c] * 100).round(1)

        st.dataframe(display_df, use_container_width=True)

        # Simple bar chart of championship odds
        if "Win Super Bowl" in playoff_df.columns:
            chart_df = playoff_df.nlargest(12, "Win Super Bowl")
            color_map = get_team_color_map(sport)
            fig = px.bar(
                chart_df,
                x="team",
                y="Win Super Bowl",
                color="team",
                color_discrete_map=color_map,
                title="Super Bowl Win Probability (Top 12)",
                labels={"Win Super Bowl": "Probability"},
            )
            fig.update_layout(xaxis_tickangle=-45, showlegend=False, yaxis_tickformat=".0%")
            st.plotly_chart(fig, use_container_width=True)
    elif sport == "NFL":
        st.caption("Playoff probability data not available for this run.")

    # ------------------------------------------------------------------
    # Existing: Achievement probabilities
    # ------------------------------------------------------------------
    if achievement_probs is not None and not achievement_probs.empty:
        st.subheader("Regular Season Achievement Probabilities")
        rename_map = {
            "make_playoffs": "Make Playoffs",
            "home_ice": "Home Ice (Top 2 in Div)",
            "first_in_division": "1st in Division",
            "first_in_conference": "1st in Conference",
            "first_in_league": "1st in League",
        }
        display_df = achievement_probs.rename(columns=rename_map)
        if "Make Playoffs" in display_df.columns:
            display_df = display_df.sort_values("Make Playoffs", ascending=False)
        st.dataframe(display_df, use_container_width=True)
    else:
        st.caption("Achievement probability data not available for this run.")

    # ------------------------------------------------------------------
    # Existing: Summary stats
    # ------------------------------------------------------------------
    if sport == "NHL":
        metric_col = "mean_points" if "mean_points" in summary.columns else "median_wins"
        metric_label = "Points"
    else:
        metric_col = "median_wins" if "median_wins" in summary.columns else "mean_wins"
        metric_label = "Wins"

    st.subheader(f"Team {metric_label} Summary")
    if not summary.empty:
        display_df = summary.copy()
        if metric_col in display_df.columns:
            display_df = display_df.sort_values(metric_col, ascending=False)
        st.dataframe(display_df, use_container_width=True)

    # ------------------------------------------------------------------
    # Existing: Distribution box plot
    # ------------------------------------------------------------------
    if distribution is not None and not distribution.empty and "team" in distribution.columns:
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

    # ------------------------------------------------------------------
    # Existing: Quick stats
    # ------------------------------------------------------------------
    if not summary.empty and metric_col in summary.columns:
        st.subheader("Quick Stats")
        col1, col2 = st.columns(2)
        with col1:
            top_idx = summary[metric_col].idxmax()
            st.metric(
                f"Highest {metric_label}",
                summary.loc[top_idx, "team"],
                f"{summary.loc[top_idx, metric_col]:.1f}",
            )
        with col2:
            st.metric(f"Average {metric_label}", f"{summary[metric_col].mean():.1f}")
