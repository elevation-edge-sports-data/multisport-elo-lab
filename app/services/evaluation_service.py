"""
Evaluation service layer.

Provides both aggregate metrics and the raw prediction arrays
required by the Model Evaluation tab (Brier decomposition,
calibration plot, baselines, Log5 baseline, etc.).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple

import numpy as np
import pandas as pd

from elo_lab.workflows.evaluate_models import evaluate_models
from elo_lab.evaluation.log5 import compute_log5_predictions
from elo_lab.evaluation.calibration_report import full_calibration_report


# ---------------------------------------------------------------------------
# Public API – Elo backtest results
# ---------------------------------------------------------------------------

def get_model_metrics(output_dir: str = "outputs") -> pd.DataFrame:
    """
    Return the current model evaluation summary
    (one row per backtest model with accuracy / log_loss / brier).
    """
    return evaluate_models(output_dir=output_dir)


def get_backtest_path(
    model: str,
    output_dir: str = "outputs",
) -> Optional[Path]:
    """
    Return the Path to the backtest CSV for a given model name,
    or None if the file does not exist.
    """
    path = Path(output_dir) / f"backtest_{model}.csv"
    return path if path.is_file() else None


def get_model_predictions(
    model: str,
    output_dir: str = "outputs",
) -> Optional[pd.DataFrame]:
    """
    Load the raw backtest predictions for a single model.

    Returns
    -------
    pd.DataFrame or None
        DataFrame containing at least the columns ``p_home`` and ``actual``.
    """
    path = get_backtest_path(model, output_dir=output_dir)
    if path is None:
        return None

    try:
        df = pd.read_csv(path)
    except Exception:
        return None

    required = {"p_home", "actual"}
    if not required.issubset(df.columns):
        return None

    return df


def get_prediction_arrays(
    model: str,
    output_dir: str = "outputs",
) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """
    Convenience wrapper that returns (probs, actuals) as NumPy arrays.
    """
    df = get_model_predictions(model, output_dir=output_dir)
    if df is None:
        return None

    probs = df["p_home"].to_numpy(dtype=float)
    actuals = df["actual"].to_numpy(dtype=float)
    return probs, actuals


def list_available_models(output_dir: str = "outputs") -> list[str]:
    """
    Return a sorted list of model names that have a backtest CSV.
    """
    output = Path(output_dir)
    if not output.is_dir():
        return []

    models = []
    for p in sorted(output.glob("backtest_*.csv")):
        name = p.stem.replace("backtest_", "", 1)
        models.append(name)
    return models


# ---------------------------------------------------------------------------
# Log5 baseline (computed from original schedule CSVs)
# ---------------------------------------------------------------------------

def get_log5_arrays(
    sport: str = "NFL",
    data_dir: str = "data",
) -> Optional[Tuple[np.ndarray, np.ndarray]]:
    """
    Compute Log5 probabilities on the full schedule for the given sport.

    Returns (probs, actuals) or None if the schedule cannot be loaded.
    """
    sport = sport.upper()
    if sport == "NFL":
        path = Path(data_dir) / "nfl_games.csv"
        date_col: str | list[str] = ["season", "week"]
    elif sport == "NHL":
        path = Path(data_dir) / "nhl_games.csv"
        date_col = "date"
    else:
        return None

    if not path.is_file():
        return None

    try:
        df = pd.read_csv(path)
    except Exception:
        return None

    required = {"home_team", "away_team", "home_score", "away_score"}
    if not required.issubset(df.columns):
        return None

    probs, actuals = compute_log5_predictions(
        df,
        home_col="home_team",
        away_col="away_team",
        home_score_col="home_score",
        away_score_col="away_score",
        date_col=date_col,
    )
    return probs, actuals


def get_log5_report(
    sport: str = "NFL",
    data_dir: str = "data",
) -> Optional[dict]:
    """
    Full calibration report for the Log5 baseline on the given sport.
    """
    arrays = get_log5_arrays(sport=sport, data_dir=data_dir)
    if arrays is None:
        return None
    probs, actuals = arrays
    home_win_rate = float(np.mean(actuals))
    return full_calibration_report(
        probs,
        actuals,
        n_bins=10,
        baselines={"home_win_rate": home_win_rate, "coin_flip": 0.5},
    )
