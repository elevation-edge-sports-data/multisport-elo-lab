"""
Model evaluation workflow.

Aggregates historical backtest results and computes
predictive performance metrics for each model.
"""

import os
import pandas as pd

from elo_lab.evaluation.metrics import accuracy, log_loss, brier


def evaluate_models(output_dir="outputs"):
    """
    Evaluate every backtest contained in the output directory.

    Parameters
    ----------
    output_dir : str
        Directory containing backtest CSV files.

    Returns
    -------
    pandas.DataFrame
        Summary metrics for every available model.
    """

    os.makedirs(output_dir, exist_ok=True)

    files = sorted(os.listdir(output_dir))

    backtest_files = [
        f for f in files
        if f.startswith("backtest_") and f.endswith(".csv")
    ]

    model_summary = []

    for filename in backtest_files:

        model = (
            filename
            .replace("backtest_", "")
            .replace(".csv", "")
        )

        df = pd.read_csv(os.path.join(output_dir, filename))

        df["log_loss"] = df.apply(
            lambda r: log_loss(r.p_home, r.actual),
            axis=1,
        )

        df["brier"] = df.apply(
            lambda r: brier(r.p_home, r.actual),
            axis=1,
        )

        model_summary.append(
            {
                "model": model,
                "accuracy": accuracy(
                    df.p_home.values,
                    df.actual.values,
                ),
                "log_loss": df["log_loss"].mean(),
                "brier": df["brier"].mean(),
            }
        )

    comparison = pd.DataFrame(model_summary)

    if not comparison.empty:
        comparison = (
            comparison
            .sort_values("model")
            .reset_index(drop=True)
        )

    comparison.to_csv(
        os.path.join(output_dir, "model_comparison.csv"),
        index=False,
    )

    return comparison


if __name__ == "__main__":

    comparison = evaluate_models()

    print(comparison)