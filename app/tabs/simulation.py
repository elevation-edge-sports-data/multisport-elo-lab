import plotly.graph_objects as go
import streamlit as st

from metadata.nfl_teams import NFL_TEAMS


def render_simulation_tab():

    st.header("Season Simulation")

    if "simulation_results" not in st.session_state:

        st.metric(
            "Simulation Status",
            "Not Running",
        )

        st.info(
            "Configure the model in the sidebar and "
            "click Run Simulation."
        )

        return

    results = st.session_state["simulation_results"]
    simulation_count = st.session_state.get("simulation_count")
    best_params = st.session_state.get("best_optimized_params")
    optimize_for = st.session_state.get("optimize_for", [])

    st.metric(
        "Simulation Status",
        "Complete",
    )

    if simulation_count:
        st.caption(
            f"{simulation_count:,} Monte Carlo simulations completed"
        )

    # === Show which configuration was used ===
    if best_params:
        st.success("**Using optimized parameters**")
        param_text = " | ".join([f"{k}: {v}" for k, v in best_params.items()])
        st.caption(f"Optimized parameters: {param_text}")
        if optimize_for:
            st.caption(f"Optimizations applied to: {', '.join(optimize_for)}")
    else:
        st.info("Using default/fixed parameters (no optimization)")

    st.divider()

    st.subheader(
        "Expected Wins"
    )

    st.dataframe(
        results["summary"],
        use_container_width=True,
        hide_index=True,
    )

    st.divider()

    st.subheader(
        "Win Distribution Explorer"
    )

    summary = results["summary"].copy()
    distribution = results["distribution"].copy()

    teams = sorted(
        summary["team"].unique()
    )

    selected_team = st.selectbox(
        "Select Team",
        teams,
        index=teams.index("DEN"),
    )

    summary_row = summary[
        summary["team"] == selected_team
    ].iloc[0]

    team_distribution = (
        distribution[
            distribution["team"] == selected_team
        ]
        .sort_values("wins")
        .reset_index(drop=True)
    )

    cumulative = (
        team_distribution["probability"]
        .cumsum()
    )

    lower_bound = team_distribution.loc[
        cumulative.ge(0.05).idxmax(),
        "wins",
    ]

    upper_bound = team_distribution.loc[
        cumulative.ge(0.95).idxmax(),
        "wins",
    ]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Expected Wins",
        f'{summary_row["mean"]:.1f}',
    )

    col2.metric(
        "Median Wins",
        f'{int(summary_row["median"])}',
    )

    col3.metric(
        "Std Dev",
        f'{summary_row["std"]:.1f}',
    )

    col4.metric(
        "90% Range",
        f"{lower_bound}-{upper_bound}",
    )

    st.subheader(
        f"{selected_team} Win Distribution"
    )

    team_color = NFL_TEAMS[selected_team][
        "primary_color"
    ]

    fig = go.Figure()

    fig.add_bar(
        x=team_distribution["wins"],
        y=team_distribution["probability"] * 100,
        marker_color=team_color,
        hovertemplate=(
            "<b>%{x} Wins</b><br>"
            "Probability: %{y:.2f}%"
            "<extra></extra>"
        ),
    )

    fig.update_layout(
        height=400,
        margin=dict(
            l=20,
            r=20,
            t=20,
            b=20,
        ),
        xaxis_title="Wins",
        yaxis_title="Probability (%)",
        showlegend=False,
    )

    fig.update_xaxes(
        tickmode="linear",
        dtick=1,
        tickangle=0,
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
    )