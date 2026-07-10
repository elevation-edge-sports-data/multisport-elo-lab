from pathlib import Path

import plotly.graph_objects as go
import streamlit as st

from metadata.nfl_teams import NFL_TEAMS
from services.backtest_service import get_latest_elo_ratings


def render_elo_ratings_tab():

    st.header("Elo Ratings")

    ratings = get_latest_elo_ratings()

    if ratings.empty:

        st.warning(
            "No backtest results found.\n\n"
            "Run run_backtest.py first."
        )

        return

    ratings["Conference"] = ratings["team"].map(
        lambda t: NFL_TEAMS[t]["conference"]
    )

    ratings["Division"] = ratings["team"].map(
        lambda t: NFL_TEAMS[t]["division"]
    )

    ratings["Team"] = ratings["team"].map(
        lambda t: NFL_TEAMS[t]["name"]
    )

    conference = st.selectbox(
        "Conference",
        [
            "All",
            "AFC",
            "NFC",
        ],
    )

    if conference != "All":

        ratings = ratings[
            ratings["Conference"] == conference
        ]

    division = st.selectbox(
        "Division",
        [
            "All",
            "East",
            "North",
            "South",
            "West",
        ],
    )

    if division != "All":

        ratings = ratings[
            ratings["Division"] == division
        ]

    st.subheader("Current Elo Ratings")

    display = ratings[
        [
            "Rank",
            "Team",
            "Conference",
            "Division",
            "elo",
        ]
    ].rename(
        columns={
            "elo": "Elo",
        }
    )

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Current Elo Ratings")

    top = ratings.head(10)

    fig = go.Figure()

    fig.add_bar(

        x=top["team"],

        y=top["elo"],

        marker_color=[
            NFL_TEAMS[t]["primary_color"]
            for t in top["team"]
        ],

        text=[
            f"{x:.0f}"
            for x in top["elo"]
        ],

        textposition="outside",

        width=0.55,
    )

    fig.update_layout(

        height=600,

        showlegend=False,

        xaxis_title="",

        yaxis_title="Elo Rating",

        plot_bgcolor="white",

        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
    )

    fig.update_xaxes(

        tickangle=0,

        showgrid=False,

    )

    fig.update_yaxes(

        gridcolor="#DDDDDD",

    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )

    st.caption(
        "Ratings shown are the latest postgame Elo ratings from the most recent historical backtest."
    )