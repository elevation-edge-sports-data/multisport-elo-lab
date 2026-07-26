import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path

from services.evaluation_service import (
    get_model_metrics,
    list_available_models,
    get_prediction_arrays,
    get_log5_arrays,
)
from elo_lab.evaluation.diagnostics import (
    calibration_and_decomposition,
)


def render_evaluation_tab():
    st.header("Model Evaluation")

    # ------------------------------------------------------------------
    # 1. Aggregate metrics
    # ------------------------------------------------------------------
    metrics = get_model_metrics()

    if metrics.empty:
        st.warning(
            "No evaluation results found.\n\n"
            "Run the backtesting workflow first."
        )
        return

    # --- Permanent Log5 baseline row ---
    sport = st.session_state.get("sport", "NFL")
    log5_arrays = get_log5_arrays(sport=sport)
    if log5_arrays is not None:
        log5_probs, log5_actuals = log5_arrays
        log5_acc = float(np.mean((log5_probs >= 0.5).astype(int) == log5_actuals))
        log5_p = np.clip(log5_probs, 1e-15, 1.0 - 1e-15)
        log5_ll = float(
            -np.mean(
                log5_actuals * np.log(log5_p)
                + (1 - log5_actuals) * np.log(1 - log5_p)
            )
        )
        log5_brier = float(np.mean((log5_probs - log5_actuals) ** 2))
        log5_row = pd.DataFrame(
            [
                {
                    "model": "Log5 (win%)",
                    "accuracy": log5_acc,
                    "log_loss": log5_ll,
                    "brier": log5_brier,
                }
            ]
        )
        metrics = pd.concat([metrics, log5_row], ignore_index=True)

    # Metric leaders (among Elo models only would be nicer, but keep simple)
    best_accuracy = metrics.loc[metrics["accuracy"].idxmax()]
    best_log_loss = metrics.loc[metrics["log_loss"].idxmin()]
    best_brier = metrics.loc[metrics["brier"].idxmin()]

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Highest Accuracy", f"{best_accuracy['accuracy']:.3f}")
        st.caption(f"Model: **{best_accuracy['model']}**")

    with col2:
        st.metric("Lowest Log Loss", f"{best_log_loss['log_loss']:.3f}")
        st.caption(f"Model: **{best_log_loss['model']}**")

    with col3:
        st.metric("Lowest Brier Score", f"{best_brier['brier']:.3f}")
        st.caption(f"Model: **{best_brier['model']}**")

    st.divider()

    # Model comparison table (Elo models + Log5)
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
        .sort_values("Brier Score", ascending=True)
        .reset_index(drop=True)
    )

    st.dataframe(
        comparison,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Includes Elo backtest models and the permanent Log5 (win%) baseline. "
        "Sorted by Brier Score (lower is better)."
    )

    st.divider()

    # ------------------------------------------------------------------
    # 2. Model selector + detailed diagnostics
    # ------------------------------------------------------------------
    st.subheader("Detailed Diagnostics")

    available_models = list_available_models()

    if not available_models:
        st.info("No backtest prediction files found for detailed diagnostics.")
        return

    # Default to the best Brier Elo model if it exists
    default_idx = 0
    elo_only = [m for m in available_models]
    if best_brier["model"] in elo_only:
        default_idx = elo_only.index(best_brier["model"])

    selected_model = st.selectbox(
        "Select model for detailed diagnostics",
        options=available_models,
        index=default_idx,
        help="Brier decomposition, ECE, calibration plot, and residuals "
        "are computed on this model’s predictions.",
    )

    arrays = get_prediction_arrays(selected_model)

    if arrays is None:
        st.error(f"Could not load predictions for model **{selected_model}**.")
        return

    probs, actuals = arrays

    # ------------------------------------------------------------------
    # 3a. Brier decomposition + ECE cards
    # ------------------------------------------------------------------
    result = calibration_and_decomposition(probs, actuals, bins=10)

    st.markdown(f"**Brier Decomposition & ECE** — `{selected_model}`")

    c1, c2, c3, c4, c5 = st.columns(5)

    with c1:
        st.metric("Brier Score", f"{result['brier']:.4f}")

    with c2:
        st.metric(
            "Reliability",
            f"{result['reliability']:.4f}",
            help="Calibration term. Lower is better (closer to 0 = better calibrated).",
        )

    with c3:
        st.metric(
            "Resolution",
            f"{result['resolution']:.4f}",
            help="Discrimination term. Higher is better (model separates outcomes).",
        )

    with c4:
        st.metric(
            "Uncertainty",
            f"{result['uncertainty']:.4f}",
            help="Inherent randomness of the outcomes (fixed for this dataset).",
        )

    with c5:
        st.metric(
            "ECE",
            f"{result['ece']:.4f}",
            help="Expected Calibration Error (weighted absolute calibration error). Lower is better.",
        )

    st.caption(
        "Brier = Reliability − Resolution + Uncertainty.  "
        "Use Reliability/ECE to judge calibration and Resolution to judge discrimination."
    )

    st.divider()

    # ------------------------------------------------------------------
    # 3b. Baseline comparisons (home-win-rate + coin-flip)
    # ------------------------------------------------------------------
    st.markdown("**Baseline Comparison**")

    def _constant_metrics(p_const: float, actuals_arr: np.ndarray) -> dict:
        p = np.full_like(actuals_arr, fill_value=p_const, dtype=float)
        preds = (p >= 0.5).astype(int)
        acc = float(np.mean(preds == actuals_arr))
        p_clip = np.clip(p, 1e-15, 1 - 1e-15)
        ll = float(
            -np.mean(
                actuals_arr * np.log(p_clip)
                + (1 - actuals_arr) * np.log(1 - p_clip)
            )
        )
        brier = float(np.mean((p - actuals_arr) ** 2))
        return {"accuracy": acc, "log_loss": ll, "brier": brier}

    home_win_rate = float(np.mean(actuals))
    coin_flip = 0.5

    baseline_home = _constant_metrics(home_win_rate, actuals)
    baseline_coin = _constant_metrics(coin_flip, actuals)

    model_metrics = {
        "accuracy": float(np.mean((probs >= 0.5).astype(int) == actuals)),
        "log_loss": float(
            -np.mean(
                actuals * np.log(np.clip(probs, 1e-15, 1 - 1e-15))
                + (1 - actuals)
                * np.log(1 - np.clip(probs, 1e-15, 1 - 1e-15))
            )
        ),
        "brier": result["brier"],
    }

    baseline_df = pd.DataFrame(
        [
            {
                "Model": selected_model,
                "Accuracy": model_metrics["accuracy"],
                "Log Loss": model_metrics["log_loss"],
                "Brier Score": model_metrics["brier"],
            },
            {
                "Model": f"Home Win Rate ({home_win_rate:.1%})",
                "Accuracy": baseline_home["accuracy"],
                "Log Loss": baseline_home["log_loss"],
                "Brier Score": baseline_home["brier"],
            },
            {
                "Model": "Coin Flip (0.5)",
                "Accuracy": baseline_coin["accuracy"],
                "Log Loss": baseline_coin["log_loss"],
                "Brier Score": baseline_coin["brier"],
            },
        ]
    )

    baseline_df["Δ Accuracy"] = baseline_df["Accuracy"] - baseline_home["accuracy"]
    baseline_df["Δ Log Loss"] = baseline_home["log_loss"] - baseline_df["Log Loss"]
    baseline_df["Δ Brier"] = baseline_home["brier"] - baseline_df["Brier Score"]

    display_df = baseline_df.copy()
    for col in ["Accuracy", "Log Loss", "Brier Score"]:
        display_df[col] = display_df[col].map(lambda x: f"{x:.4f}")
    for col in ["Δ Accuracy", "Δ Log Loss", "Δ Brier"]:
        display_df[col] = display_df[col].map(lambda x: f"{x:+.4f}")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
    )

    st.caption(
        "Δ columns show improvement versus the Home Win Rate baseline "
        "(positive = better). Home Win Rate uses the historical frequency "
        "of home wins as a constant probability."
    )

    # ------------------------------------------------------------------
    # 4. Calibration plot (reliability diagram)
    # ------------------------------------------------------------------
    st.subheader("Calibration Plot (Reliability Diagram)")

    bin_stats = result["bins"]

    if not bin_stats:
        st.info("No calibration bins available (empty predictions).")
    else:
        pred_probs = [b["pred_prob"] for b in bin_stats]
        actual_rates = [b["actual_rate"] for b in bin_stats]
        counts = [b["count"] for b in bin_stats]

        fig = go.Figure()

        fig.add_trace(
            go.Scatter(
                x=[0, 1],
                y=[0, 1],
                mode="lines",
                name="Perfect calibration",
                line=dict(color="gray", dash="dash"),
            )
        )

        fig.add_trace(
            go.Scatter(
                x=pred_probs,
                y=actual_rates,
                mode="markers+lines",
                name="Model",
                marker=dict(
                    size=[max(8, c / max(counts) * 30) for c in counts],
                    color="steelblue",
                    line=dict(width=1, color="DarkSlateGrey"),
                ),
                text=[f"n = {c}" for c in counts],
                hovertemplate=(
                    "Predicted: %{x:.3f}<br>"
                    "Observed: %{y:.3f}<br>"
                    "%{text}<extra></extra>"
                ),
            )
        )

        fig.update_layout(
            xaxis_title="Mean Predicted Win Probability",
            yaxis_title="Observed Win Rate",
            xaxis=dict(range=[0, 1], dtick=0.1),
            yaxis=dict(range=[0, 1], dtick=0.1),
            height=450,
            legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
            margin=dict(l=40, r=40, t=40, b=40),
        )

        st.plotly_chart(fig, use_container_width=True)

        st.caption(
            "Points above the diagonal = under-confident (actual wins more often than predicted).  "
            "Points below the diagonal = over-confident.  "
            "Marker size is proportional to the number of games in the bin."
        )

    # ------------------------------------------------------------------
    # 5. Residual diagnostics
    # ------------------------------------------------------------------
    st.divider()
    st.subheader("Residual Diagnostics")

    residuals = actuals - probs  # observed − predicted

    r1, r2 = st.columns(2)
    with r1:
        st.metric("Mean residual", f"{float(np.mean(residuals)):.4f}")
    with r2:
        st.metric("Std residual", f"{float(np.std(residuals)):.4f}")

    fig_res = go.Figure()
    fig_res.add_hline(y=0, line_dash="dash", line_color="gray")
    fig_res.add_trace(
        go.Scatter(
            x=probs,
            y=residuals,
            mode="markers",
            marker=dict(
                size=6,
                opacity=0.45,
                color=actuals,
                colorscale=[[0, "crimson"], [1, "steelblue"]],
                showscale=False,
            ),
            name="Games",
            hovertemplate="p=%{x:.3f}<br>residual=%{y:.3f}<extra></extra>",
        )
    )

    # Binned mean residual
    n_bins = 10
    bin_edges = np.linspace(0, 1, n_bins + 1)
    bin_centers = []
    bin_means = []
    for i in range(n_bins):
        mask = (probs >= bin_edges[i]) & (probs < bin_edges[i + 1])
        if mask.sum() == 0:
            continue
        bin_centers.append((bin_edges[i] + bin_edges[i + 1]) / 2)
        bin_means.append(float(np.mean(residuals[mask])))

    if bin_centers:
        fig_res.add_trace(
            go.Scatter(
                x=bin_centers,
                y=bin_means,
                mode="markers+lines",
                marker=dict(size=10, symbol="square", color="black"),
                name="Binned mean",
            )
        )

    fig_res.update_layout(
        xaxis_title="Predicted home-win probability",
        yaxis_title="Residual (actual − predicted)",
        height=420,
        margin=dict(l=40, r=40, t=40, b=40),
    )
    st.plotly_chart(fig_res, use_container_width=True)
    st.caption(
        "Points near zero are well-calibrated. Systematic curves indicate "
        "over-/under-confidence. Blue = home win, red = home loss."
    )

    # ------------------------------------------------------------------
    # 6. Grid Search Landscape
    # ------------------------------------------------------------------
    st.divider()
    st.subheader("Grid Search Landscape")

    search_path = Path("outputs/parameter_search.csv")

    if not search_path.is_file():
        st.info(
            "No parameter search results found (`outputs/parameter_search.csv`).\n\n"
            "Run the parameter optimization workflow first."
        )
    else:
        search_df = pd.read_csv(search_path)

        metric_cols = {"accuracy", "log_loss", "brier"}
        id_cols = {"label"}
        param_cols = [
            c
            for c in search_df.columns
            if c not in metric_cols | id_cols
            and pd.api.types.is_numeric_dtype(search_df[c])
        ]

        if len(param_cols) < 2:
            st.warning(
                "Need at least two numeric parameter columns to draw a heatmap. "
                f"Found: {param_cols}"
            )
        else:
            col_metric, col_x, col_y = st.columns(3)

            with col_metric:
                color_metric = st.selectbox(
                    "Color by metric",
                    options=["log_loss", "brier", "accuracy"],
                    format_func=lambda x: {
                        "log_loss": "Log Loss",
                        "brier": "Brier Score",
                        "accuracy": "Accuracy",
                    }[x],
                    index=0,
                )

            with col_x:
                x_param = st.selectbox(
                    "X-axis parameter", options=param_cols, index=0
                )

            with col_y:
                default_y = 1 if len(param_cols) > 1 else 0
                y_param = st.selectbox(
                    "Y-axis parameter", options=param_cols, index=default_y
                )

            pivot = (
                search_df.groupby([y_param, x_param], as_index=False)[color_metric]
                .mean()
                .pivot(index=y_param, columns=x_param, values=color_metric)
            )
            pivot = pivot.sort_index(axis=0).sort_index(axis=1)

            if color_metric == "accuracy":
                best_val = pivot.max().max()
                best_idx = pivot.stack().idxmax()
            else:
                best_val = pivot.min().min()
                best_idx = pivot.stack().idxmin()

            best_y, best_x = best_idx

            fig = go.Figure(
                data=go.Heatmap(
                    z=pivot.values,
                    x=[str(v) for v in pivot.columns],
                    y=[str(v) for v in pivot.index],
                    colorscale="RdYlGn_r" if color_metric != "accuracy" else "RdYlGn",
                    colorbar=dict(title=color_metric.replace("_", " ").title()),
                    hovertemplate=(
                        f"{x_param}: %{{x}}<br>"
                        f"{y_param}: %{{y}}<br>"
                        f"{color_metric}: %{{z:.4f}}<extra></extra>"
                    ),
                )
            )

            fig.add_trace(
                go.Scatter(
                    x=[str(best_x)],
                    y=[str(best_y)],
                    mode="markers",
                    marker=dict(
                        symbol="star",
                        size=16,
                        color="black",
                        line=dict(width=1, color="white"),
                    ),
                    name="Best",
                    hovertemplate=(
                        f"Best<br>"
                        f"{x_param}: {best_x}<br>"
                        f"{y_param}: {best_y}<br>"
                        f"{color_metric}: {best_val:.4f}<extra></extra>"
                    ),
                )
            )

            fig.update_layout(
                xaxis_title=x_param,
                yaxis_title=y_param,
                height=480,
                margin=dict(l=60, r=40, t=40, b=60),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    x=0.5,
                    xanchor="center",
                ),
            )

            st.plotly_chart(fig, use_container_width=True)

            st.caption(
                f"Star marks the best combination according to **{color_metric}**. "
                "Color scale is reversed for Log Loss / Brier (lower = greener)."
            )

            st.markdown("**Top combinations**")

            ascending = color_metric != "accuracy"
            top_n = (
                search_df.sort_values(color_metric, ascending=ascending)
                .head(10)
                .reset_index(drop=True)
            )

            display_cols = ["label"] + param_cols + ["accuracy", "log_loss", "brier"]
            display_cols = [c for c in display_cols if c in top_n.columns]

            top_display = top_n[display_cols].copy()
            for col in ["accuracy", "log_loss", "brier"]:
                if col in top_display.columns:
                    top_display[col] = top_display[col].map(lambda x: f"{x:.4f}")

            st.dataframe(
                top_display,
                use_container_width=True,
                hide_index=True,
            )
