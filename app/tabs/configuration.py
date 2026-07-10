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

    st.subheader("Current Model Configuration")

    configuration = {
        "Model": "MOV_HFA",
        "K Factor": 20,
        "Home Field Advantage": "55 Elo",
        "Margin of Victory": "Enabled" if margin_of_victory else "Disabled",
        "Elevation Edge": "Enabled" if elevation else "Disabled",
    }

    for parameter, value in configuration.items():
        st.write(f"**{parameter}:** {value}")

    st.caption(
        "Interactive parameter controls will be introduced in a future version."
    )