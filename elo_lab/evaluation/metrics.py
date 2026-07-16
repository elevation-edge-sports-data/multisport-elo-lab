"""
Evaluation metrics for Elo model performance.

Implements standard classification and probabilistic scoring
metrics used across backtesting and parameter optimization.
"""

import numpy as np

def accuracy(probs, actuals):
    probs = np.array(probs)
    actuals = np.array(actuals)
    preds = (probs >= 0.5).astype(int)
    return np.mean(preds == actuals)


def log_loss(p, y):
    p = np.clip(p, 1e-15, 1 - 1e-15)
    return -(y * np.log(p) + (1 - y) * np.log(1 - p))


def brier(p, y):
    return (p - y) ** 2

def expected_calibration_error(
    probs: np.ndarray | list,
    actuals: np.ndarray | list,
    bins: int = 10,
) -> float:
    """Expected Calibration Error (ECE)."""
    from .diagnostics import brier_decomposition
    return brier_decomposition(probs, actuals, bins=bins)["ece"]


def brier_score(
    probs: np.ndarray | list,
    actuals: np.ndarray | list,
) -> float:
    """Mean Brier score (convenience wrapper)."""
    probs = np.asarray(probs, dtype=float)
    actuals = np.asarray(actuals, dtype=float)
    return float(np.mean((probs - actuals) ** 2))