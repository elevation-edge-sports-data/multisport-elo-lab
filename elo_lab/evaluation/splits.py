"""
Chronological train / validation / hold-out splits.

Strict temporal splits with no leakage by construction.
Intended for backtesting, parameter optimization, and
fair comparison of Elo configs against baselines (e.g. Log5).
"""

from typing import List, Optional, Tuple, Union

import pandas as pd


def chronological_split(
    games: pd.DataFrame,
    train_end: Union[str, int, float],
    val_end: Union[str, int, float],
    date_col: Union[str, List[str]] = "date",
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Strict temporal split.

    Parameters
    ----------
    games : full game DataFrame
    train_end : last date/season/week included in training
    val_end   : last date/season/week included in validation
                (everything strictly after becomes hold-out)
    date_col  : column name (str) or list of columns used for ordering
                and filtering (e.g. "date", "season", or ["season", "week"])

    Returns
    -------
    train, val, hold : three DataFrames (reset index)
    """
    df = games.copy()

    if isinstance(date_col, (list, tuple)):
        cols = list(date_col)
        df = df.sort_values(cols)
        # Filter on the primary (first) column for season-style splits
        primary = cols[0]
        train = df[df[primary] <= train_end]
        val = df[(df[primary] > train_end) & (df[primary] <= val_end)]
        hold = df[df[primary] > val_end]
    else:
        df = df.sort_values(date_col)
        train = df[df[date_col] <= train_end]
        val = df[(df[date_col] > train_end) & (df[date_col] <= val_end)]
        hold = df[df[date_col] > val_end]

    return (
        train.reset_index(drop=True),
        val.reset_index(drop=True),
        hold.reset_index(drop=True),
    )


def chronological_split_by_fraction(
    games: pd.DataFrame,
    train_frac: float = 0.70,
    val_frac: float = 0.15,
    date_col: Optional[Union[str, List[str]]] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Convenience splitter that uses chronological order and
    fractional cut-points (useful when exact season boundaries
    are not yet known or for quick experiments).

    hold_frac is implied as 1 - train_frac - val_frac.
    """
    df = games.copy()

    if date_col is not None:
        if isinstance(date_col, (list, tuple)):
            df = df.sort_values(list(date_col))
        else:
            df = df.sort_values(date_col)

    n = len(df)
    if n == 0:
        empty = df.copy()
        return empty, empty, empty

    train_end_idx = int(n * train_frac)
    val_end_idx = int(n * (train_frac + val_frac))

    train = df.iloc[:train_end_idx]
    val = df.iloc[train_end_idx:val_end_idx]
    hold = df.iloc[val_end_idx:]

    return (
        train.reset_index(drop=True),
        val.reset_index(drop=True),
        hold.reset_index(drop=True),
    )
