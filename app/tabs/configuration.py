import streamlit as st


def render_configuration_tab(
    sport,
    season,
    home_field,
    margin_of_victory,
    elevation,
    simulation_count,
):

    st.header("Model Configuration")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "Sport",
            sport,
        )

    with col2:
        st.metric(
            "Season",
            season,
        )

    with col3:
        st.metric(
            "Simulations",
            f"{simulation_count:,}",
        )

    st.divider()

    st.subheader("Active Model Components")

    components = {
        "Home Field Advantage": home_field,
        "Margin of Victory": margin_of_victory,
        "Elevation Edge": elevation,
    }

    for name, enabled in components.items():
        st.write(
            f"**{name}:** {'Enabled' if enabled else 'Disabled'}"
        )

    st.divider()

    # Show last run configuration + optimization scope
    last_config = st.session_state.get("last_config")
    optimize_for = st.session_state.get("optimize_for", [])

    if last_config:
        st.subheader("Last Run Configuration")

        st.write(f"**K Factor:** {last_config.get('k', 'N/A')}")

        adjustments = last_config.get("adjustments", {})
        if adjustments:
            st.write("**Enabled Adjustments:**")
            for adj_name in adjustments:
                st.write(f"  - **{adj_name}**")

        if optimize_for:
            st.write("**Parameters optimized for:**")
            for adj in optimize_for:
                st.write(f"  - **{adj}**")
        else:
            st.write("**Parameter optimization:** Not enabled for this run")

        st.caption("This reflects the exact settings used in the last simulation.")
    else:
        st.subheader("Current Model Configuration")
        st.info("Run a simulation from the sidebar to see the configuration that was used.")

    st.caption(
        "Interactive parameter controls will be introduced in a future version."
    )