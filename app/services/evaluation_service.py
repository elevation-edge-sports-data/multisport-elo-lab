"""
Evaluation service layer.

Provides both aggregate metrics and the raw prediction arrays
required by the Model Evaluation tab (Brier decomposition,
calibration plot, baselines, etc.).
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, Optional, Tuple, Union

import numpy as np
import pandas as pd

from elo_lab.workflows.evaluate_models import evaluate_models


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_model_metrics(output_dir: str = "outputs") -> pd.DataFrame:
    """
    Return the current model evaluation summary
    (one row per backtest model with accuracy / log_loss / brier).

    This is the original API and remains unchanged.
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

    Parameters
    ----------
    model : str
        Model identifier (the part between 'backtest_' and '.csv').
    output_dir : str
        Directory that contains the backtest_*.csv files.

    Returns
    -------
    pd.DataFrame or None
        DataFrame containing at least the columns
        ``p_home`` and ``actual``.  Returns None if the
        file is missing or unreadable.
    """
    path = get_backtest_path(model, output_dir=output_dir)
    if path is None:
        return None

    try:
        df = pd.read_csv(path)
    except Exception:
        return None

    # Minimal validation – the rest of the pipeline expects these columns
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

    Returns
    -------
    tuple of (np.ndarray, np.ndarray) or None
        (p_home, actual) ready to pass straight into
        brier_decomposition / calibration_bins / etc.
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

def get_model_metrics():
    """
    Returns the current model evaluation summary.
    """
    return evaluate_models()