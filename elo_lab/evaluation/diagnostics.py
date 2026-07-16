"""
Calibration and probability diagnostics.

Provides utilities for evaluating probability calibration
and distribution statistics of model outputs.
"""

import numpy as np
from typing import Dict, List, Any, Optional


def calibration_bins(
    probs: np.ndarray | list,
    actuals: np.ndarray | list,
    bins: int = 10,
) -> List[Dict[str, Any]]:
    """
    Compute calibration statistics by binning predicted probabilities.

    For each non-empty bin returns:
        - bin index
        - mean predicted probability
        - empirical outcome rate
        - sample count

    Parameters
    ----------
    probs : array-like of shape (n_samples,)
        Predicted probabilities in [0, 1].
    actuals : array-like of shape (n_samples,)
        Binary outcomes (0 or 1).
    bins : int, default=10
        Number of equal-width bins.

    Returns
    -------
    list of dict
        One dict per non-empty bin.
    """
    probs = np.asarray(probs, dtype=float)
    actuals = np.asarray(actuals, dtype=float)

    bin_edges = np.linspace(0.0, 1.0, bins + 1)
    results = []

    for i in range(bins):
        if i == bins - 1:
            mask = (probs >= bin_edges[i]) & (probs <= bin_edges[i + 1])
        else:
            mask = (probs >= bin_edges[i]) & (probs < bin_edges[i + 1])

        count = int(np.sum(mask))
        if count == 0:
            continue

        results.append({
            "bin": i,
            "pred_prob": float(np.mean(probs[mask])),
            "actual_rate": float(np.mean(actuals[mask])),
            "count": count,
        })

    return results


def brier_decomposition(
    probs: np.ndarray | list,
    actuals: np.ndarray | list,
    bins: int = 10,
) -> Dict[str, float]:
    """
    Murphy Brier score decomposition + Expected Calibration Error (ECE).

    Brier = Reliability - Resolution + Uncertainty

    Parameters
    ----------
    probs : array-like of shape (n_samples,)
        Predicted probabilities in [0, 1].
    actuals : array-like of shape (n_samples,)
        Binary outcomes (0 or 1).
    bins : int, default=10
        Number of bins used for reliability / resolution / ECE.

    Returns
    -------
    dict with keys
        brier : float
            Mean Brier score.
        reliability : float
            Calibration term (lower is better).
        resolution : float
            Discrimination term (higher is better).
        uncertainty : float
            Inherent randomness of the outcomes (fixed for a dataset).
        ece : float
            Expected Calibration Error (weighted absolute calibration error).
    """
    probs = np.asarray(probs, dtype=float)
    actuals = np.asarray(actuals, dtype=float)
    n = len(probs)

    if n == 0:
        raise ValueError("probs and actuals must be non-empty")

    # Uncertainty (base-rate variance) – constant for the dataset
    base_rate = float(np.mean(actuals))
    uncertainty = base_rate * (1.0 - base_rate)

    # Mean Brier
    brier = float(np.mean((probs - actuals) ** 2))

    # Bin statistics (re-uses the existing helper)
    bin_stats = calibration_bins(probs, actuals, bins=bins)

    reliability = 0.0
    resolution = 0.0
    ece = 0.0

    for b in bin_stats:
        weight = b["count"] / n
        reliability += weight * (b["pred_prob"] - b["actual_rate"]) ** 2
        resolution += weight * (b["actual_rate"] - base_rate) ** 2
        ece += weight * abs(b["pred_prob"] - b["actual_rate"])

    return {
        "brier": brier,
        "reliability": float(reliability),
        "resolution": float(resolution),
        "uncertainty": float(uncertainty),
        "ece": float(ece),
    }


def calibration_and_decomposition(
    probs: np.ndarray | list,
    actuals: np.ndarray | list,
    bins: int = 10,
) -> Dict[str, Any]:
    """
    Convenience wrapper that returns both the bin-level calibration
    statistics and the full Brier decomposition + ECE in one call.

    Useful for the Model Evaluation tab (plot + metrics cards).
    """
    bin_stats = calibration_bins(probs, actuals, bins=bins)
    decomp = brier_decomposition(probs, actuals, bins=bins)
    return {
        "bins": bin_stats,
        **decomp,
    }


def probability_stats(probs):
    probs = np.array(probs)
    return {
        "mean": np.mean(probs),
        "std": np.std(probs),
        "min": np.min(probs),
        "max": np.max(probs)
    }
