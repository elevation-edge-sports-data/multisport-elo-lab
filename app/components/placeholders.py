import streamlit as st


def section_placeholder(
    title,
    description
):

    st.subheader(title)

    st.info(description)


    st.empty()