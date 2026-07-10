import plotly.graph_objects as go
import streamlit as st

from metadata.nfl_teams import NFL_TEAMS
from services.elo_evolution_service import get_elo_evolution


DEFAULT_TEAMS = [
    "DEN",
    "KC",
    "NE",
    "BUF",
    "BAL",
    "JAX",
]


def _add_team_line(
    fig,
    team_data,
    team,
    y_column,
    label,
):
    fig.add_trace(
        go.Scatter(
            x=team_data["week"],
            y=team_data[y_column],
            mode="lines",
            name=team,
            line=dict(
                width=3,
                color=NFL_TEAMS[team]["primary_color"],
            ),
            hovertemplate=(
                "<b>%{fullData.name}</b><br>"
                "Week: %{x}<br>"
                f"{label}: %{{y:.0f}}"
                "<extra></extra>"
            ),
        )
    )


def _build_layout(
    fig,
    title,
    y_title,
):

    fig.update_layout(

        title=title,

        height=650,

        hovermode="x unified",

        legend_title_text="Team",

        plot_bgcolor="white",

        margin=dict(
            l=30,
            r=30,
            t=60,
            b=40,
        ),

    )


    fig.update_xaxes(
        title="Week",
        showgrid=False,
        tickmode="linear",
        dtick=1,
    )


    fig.update_yaxes(
        title=y_title,
        gridcolor="#DDDDDD",
    )


def render_elo_evolution_tab():

    st.header("Elo Evolution")


    # ======================================================
    # HISTORICAL EVOLUTION
    # ======================================================

    st.subheader(
        "Historical Elo Evolution"
    )


    historical = get_elo_evolution()


    if historical.empty:

        st.info(
            "Historical Elo data unavailable."
        )

    else:

        available_teams = sorted(
            historical["team"].unique()
        )


        default_selection = [
            team
            for team in DEFAULT_TEAMS
            if team in available_teams
        ]


        selected_teams = st.multiselect(

            "Select teams",

            available_teams,

            default=default_selection,

            key="historical_elo_teams",

        )


        if selected_teams:

            fig = go.Figure()


            for team in selected_teams:

                team_data = (
                    historical[
                        historical["team"] == team
                    ]
                    .sort_values("week_index")
                )


                fig.add_trace(
                    go.Scatter(
                        x=team_data["week"],
                        y=team_data["elo"],
                        mode="lines",
                        name=team,
                        line=dict(
                            width=3,
                            color=NFL_TEAMS[team]["primary_color"],
                        ),
                        hovertemplate=(
                            "<b>%{fullData.name}</b><br>"
                            "Week: %{x}<br>"
                            "Historical Elo: %{y:.0f}"
                            "<extra></extra>"
                        ),
                    )
                )


            _build_layout(
                fig,
                "Historical Elo Rating Evolution",
                "Elo Rating",
            )


            st.plotly_chart(
                fig,
                use_container_width=True,
            )


    st.divider()


    # ======================================================
    # SIMULATED EVOLUTION
    # ======================================================

    st.subheader(
        "Simulated Elo Evolution"
    )


    if "simulation_results" not in st.session_state:

        st.info(
            "Run a season simulation first to view simulated Elo evolution."
        )

        return


    results = st.session_state["simulation_results"]


    if "elo_evolution" not in results:

        st.info(
            "Simulated Elo evolution data is unavailable."
        )

        return


    evolution = results["elo_evolution"].copy()


    if evolution.empty:

        st.warning(
            "No simulated Elo evolution data available."
        )

        return


    available_teams = sorted(
        evolution["team"].unique()
    )


    default_selection = [
        team
        for team in DEFAULT_TEAMS
        if team in available_teams
    ]


    selected_teams = st.multiselect(

        "Select teams",

        available_teams,

        default=default_selection,

        key="simulation_elo_teams",

    )


    if not selected_teams:

        st.info(
            "Select at least one team to display simulated Elo evolution."
        )

        return


    fig = go.Figure()


    for team in selected_teams:

        team_data = (
            evolution[
                evolution["team"] == team
            ]
            .sort_values("week")
        )


        # uncertainty band

        fig.add_trace(

            go.Scatter(

                x=list(team_data["week"])
                +
                list(team_data["week"][::-1]),

                y=list(team_data["p95_elo"])
                +
                list(team_data["p05_elo"][::-1]),

                fill="toself",

                fillcolor=NFL_TEAMS[team]["primary_color"],

                opacity=0.15,

                line=dict(
                    color="rgba(0,0,0,0)"
                ),

                showlegend=False,

                hoverinfo="skip",

            )

        )


        _add_team_line(
            fig,
            team_data,
            team,
            "mean_elo",
            "Mean Elo",
        )


    _build_layout(
        fig,
        "Simulated Elo Evolution Across Monte Carlo Simulations",
        "Mean Elo Rating",
    )


    st.plotly_chart(
        fig,
        use_container_width=True,
    )


    st.caption(
        "Mean postgame Elo across Monte Carlo simulations with 5th-95th percentile uncertainty bands."
    )