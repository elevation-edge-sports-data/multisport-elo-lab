"""
Log5 closed-form baseline using only historical win percentages.

Works with the current minimal game data (home/away teams + scores).
Computes running win% on the fly in chronological order — pure
evaluation baseline, zero training, no leakage.
"""

from typing import Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd


def _safe_win_pct(wins: int, games: int) -> float:
    if games <= 0:
        return 0.5
    return wins / games


def log5_proba(home_wp: float, away_wp: float) -> float:
    """
    Classic Log5 formula, clipped for numerical safety.

    p = (H - H*A) / (H + A - 2*H*A)
    """
    h = float(np.clip(home_wp, 1e-6, 1.0 - 1e-6))
    a = float(np.clip(away_wp, 1e-6, 1.0 - 1e-6))
    denom = h + a - 2.0 * h * a
    if abs(denom) < 1e-12:
        return 0.5
    p = (h - h * a) / denom
    return float(np.clip(p, 1e-6, 1.0 - 1e-6))


def compute_log5_predictions(
    games: pd.DataFrame,
    home_col: str = "home_team",
    away_col: str = "away_team",
    home_score_col: str = "home_score",
    away_score_col: str = "away_score",
    date_col: Optional[Union[str, List[str]]] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Walk games in chronological order, compute pre-game win%,
    emit Log5 probability and actual home-win indicator.

    Parameters
    ----------
    games : DataFrame with at least home/away teams and scores.
    date_col : column name (str) or list of columns (e.g. ["season", "week"])
               used for chronological sorting. If None, assumes already ordered.

    Returns
    -------
    probs : np.ndarray of shape (n_games,)
    actuals : np.ndarray of shape (n_games,)  (1 = home win, 0 = home loss)
    """
    df = games.copy()

    # Ensure chronological order
    if date_col is not None:
        if isinstance(date_col, (list, tuple)):
            df = df.sort_values(list(date_col))
        else:
            df = df.sort_values(date_col)

    # Running records: team -> [wins, games]
    records: Dict[str, List[int]] = {}

    probs: List[float] = []
    actuals: List[int] = []

    for _, row in df.iterrows():
        home = row[home_col]
        away = row[away_col]

        hw, hg = records.get(home, [0, 0])
        aw, ag = records.get(away, [0, 0])

        home_wp = _safe_win_pct(hw, hg)
        away_wp = _safe_win_pct(aw, ag)

        p = log5_proba(home_wp, away_wp)
        y = 1 if float(row[home_score_col]) > float(row[away_score_col]) else 0

        probs.append(p)
        actuals.append(y)

        # Update records *after* prediction (causal / no leakage)
        records[home] = [hw + y, hg + 1]
        records[away] = [aw + (1 - y), ag + 1]

    return np.asarray(probs, dtype=float), np.asarray(actuals, dtype=int)


def log5_baseline_report(
    games: pd.DataFrame,
    **kwargs,
) -> dict:
    """
    Convenience wrapper: compute Log5 predictions and basic metrics.
    Full calibration should be obtained via the shared diagnostics helpers.
    """
    from .metrics import accuracy, brier_score

    probs, actuals = compute_log5_predictions(games, **kwargs)

    # vectorized log-loss
    p = np.clip(probs, 1e-15, 1.0 - 1e-15)
    y = actuals.astype(float)
    ll = float(np.mean(-(y * np.log(p) + (1.0 - y) * np.log(1.0 - p))))

    return {
        "probs": probs,
        "actuals": actuals,
        "brier": brier_score(probs, actuals),
        "log_loss": ll,
        "accuracy": accuracy(probs, actuals),
        "n_games": len(probs),
    }
