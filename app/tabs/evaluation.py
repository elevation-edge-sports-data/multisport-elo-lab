import streamlit as st

from services.evaluation_service import get_model_metrics


def render_evaluation_tab():

    st.header("Model Evaluation")

    metrics = get_model_metrics()

    if metrics.empty:

        st.warning(
            "No evaluation results found.\n\n"
            "Run the backtesting workflow first."
        )

        return

    # ==========================================================
    # METRIC LEADERS
    # ==========================================================

    best_accuracy = metrics.loc[
        metrics["accuracy"].idxmax()
    ]

    best_log_loss = metrics.loc[
        metrics["log_loss"].idxmin()
    ]

    best_brier = metrics.loc[
        metrics["brier"].idxmin()
    ]

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Highest Accuracy",
            f"{best_accuracy['accuracy']:.3f}",
        )

        st.caption(
            f"Model: **{best_accuracy['model']}**"
        )

    with col2:

        st.metric(
            "Lowest Log Loss",
            f"{best_log_loss['log_loss']:.3f}",
        )

        st.caption(
            f"Model: **{best_log_loss['model']}**"
        )

    with col3:

        st.metric(
            "Lowest Brier Score",
            f"{best_brier['brier']:.3f}",
        )

        st.caption(
            f"Model: **{best_brier['model']}**"
        )

    st.divider()

    # ==========================================================
    # MODEL COMPARISON
    # ==========================================================

    st.subheader("Model Comparison")

    comparison = (
        metrics.rename(
            columns={
                "model": "Model",
                "accuracy": "Accuracy",
                "log_loss": "Log Loss",
                "brier": "Brier Score",
            }
        )
        .sort_values(
            "Accuracy",
            ascending=False,
        )
        .reset_index(drop=True)
    )

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Each metric highlights the model that performed best "
        "for that specific evaluation criterion. A single overall "
        "best model is not designated in Version 6."
    )