"""
Unified calibration + residual reporting for any probability model
(Elo configurations, Log5 baseline, future hybrids).

Builds on the existing diagnostics.py / metrics.py implementations.
"""

from typing import Any, Dict, List, Optional, Union

import numpy as np

from .diagnostics import calibration_and_decomposition
from .metrics import accuracy, brier_score, log_loss


def _as_arrays(
    probs: Union[np.ndarray, List[float]],
    actuals: Union[np.ndarray, List[int]],
) -> tuple[np.ndarray, np.ndarray]:
    p = np.asarray(probs, dtype=float)
    y = np.asarray(actuals, dtype=float)
    if p.shape != y.shape:
        raise ValueError(f"probs shape {p.shape} != actuals shape {y.shape}")
    return p, y


def residual_stats(
    probs: Union[np.ndarray, List[float]],
    actuals: Union[np.ndarray, List[int]],
) -> Dict[str, Any]:
    """
    Simple residual diagnostics (observed - predicted).
    Useful for residual-vs-predicted scatter and bias checks.
    """
    p, y = _as_arrays(probs, actuals)
    residuals = y - p
    return {
        "mean_residual": float(np.mean(residuals)),
        "std_residual": float(np.std(residuals)),
        "residuals": residuals,
    }


def full_calibration_report(
    probs: Union[np.ndarray, List[float]],
    actuals: Union[np.ndarray, List[int]],
    n_bins: int = 10,
    baselines: Optional[Dict[str, float]] = None,
) -> Dict[str, Any]:
    """
    Single entry-point used by the evaluation service / dashboard.

    Returns
    -------
    dict with:
      - core metrics: brier, log_loss, accuracy
      - calibration: ece, reliability, resolution, uncertainty
      - calibration_bins: list of per-bin stats (for reliability diagram)
      - residual diagnostics
      - optional deltas vs naïve baselines (home-win-rate, coin-flip, …)
    """
    p, y = _as_arrays(probs, actuals)

    # Core probabilistic metrics
    brier = brier_score(p, y)
    # log_loss in metrics.py is element-wise; take mean
    ll_vec = log_loss(p, y)
    ll = float(np.mean(ll_vec)) if np.ndim(ll_vec) > 0 else float(ll_vec)
    acc = accuracy(p, y)

    # Existing rich diagnostics
    decomp = calibration_and_decomposition(p, y, bins=n_bins)

    report: Dict[str, Any] = {
        "brier": brier,
        "log_loss": ll,
        "accuracy": acc,
        "ece": decomp.get("ece"),
        "reliability": decomp.get("reliability"),
        "resolution": decomp.get("resolution"),
        "uncertainty": decomp.get("uncertainty"),
        "calibration_bins": decomp.get("bins"),
        "n_games": int(len(p)),
        "base_rate": float(np.mean(y)),
    }

    # Residuals
    report.update(residual_stats(p, y))

    # Optional baseline deltas (e.g. {"home_win_rate": 0.55, "coin_flip": 0.5})
    if baselines:
        deltas = {}
        for name, base_p in baselines.items():
            base_arr = np.full_like(p, float(base_p))
            base_brier = brier_score(base_arr, y)
            deltas[name] = {
                "brier": base_brier,
                "brier_delta": brier - base_brier,  # negative = better than baseline
            }
        report["baseline_deltas"] = deltas

    return report


def compare_models(
    model_results: Dict[str, Dict[str, Any]],
):
    """
    Build a side-by-side comparison table from multiple
    full_calibration_report() outputs.

    model_results : {"Elo (HFA+EE)": report_dict, "Log5": report_dict, ...}

    Returns a pandas DataFrame sorted by Brier score (lower = better).
    """
    import pandas as pd

    rows = []
    for name, r in model_results.items():
        rows.append(
            {
                "model": name,
                "brier": r.get("brier"),
                "log_loss": r.get("log_loss"),
                "accuracy": r.get("accuracy"),
                "ece": r.get("ece"),
                "reliability": r.get("reliability"),
                "resolution": r.get("resolution"),
                "n_games": r.get("n_games"),
            }
        )
    return pd.DataFrame(rows).sort_values("brier")
