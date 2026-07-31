"""
Adapter that converts Multisport Elo Lab season-simulation output
into the List[TeamStanding] expected by elo_lab.playoffs.nfl.

Works with the current return signature of simulate_season:

    standings: pd.DataFrame   columns = team, wins, losses, points, elo
    team_elo:  dict[str, float]
    elo_history: pd.DataFrame  (ignored here)
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Tuple

import pandas as pd

from .models import TeamStanding


# ---------------------------------------------------------------------------
# Canonical NFL conference / division map
# (stable across the seasons currently in the dataset)
# ---------------------------------------------------------------------------
NFL_TEAM_META: Dict[str, Tuple[str, str]] = {
    # AFC East
    "BUF": ("AFC", "AFC East"),
    "MIA": ("AFC", "AFC East"),
    "NE":  ("AFC", "AFC East"),
    "NYJ": ("AFC", "AFC East"),
    # AFC North
    "BAL": ("AFC", "AFC North"),
    "CIN": ("AFC", "AFC North"),
    "CLE": ("AFC", "AFC North"),
    "PIT": ("AFC", "AFC North"),
    # AFC South
    "HOU": ("AFC", "AFC South"),
    "IND": ("AFC", "AFC South"),
    "JAX": ("AFC", "AFC South"),
    "TEN": ("AFC", "AFC South"),
    # AFC West
    "DEN": ("AFC", "AFC West"),
    "KC":  ("AFC", "AFC West"),
    "LAC": ("AFC", "AFC West"),
    "LV":  ("AFC", "AFC West"),
    # NFC East
    "DAL": ("NFC", "NFC East"),
    "NYG": ("NFC", "NFC East"),
    "PHI": ("NFC", "NFC East"),
    "WAS": ("NFC", "NFC East"),
    # NFC North
    "CHI": ("NFC", "NFC North"),
    "DET": ("NFC", "NFC North"),
    "GB":  ("NFC", "NFC North"),
    "MIN": ("NFC", "NFC North"),
    # NFC South
    "ATL": ("NFC", "NFC South"),
    "CAR": ("NFC", "NFC South"),
    "NO":  ("NFC", "NFC South"),
    "TB":  ("NFC", "NFC South"),
    # NFC West
    "ARI": ("NFC", "NFC West"),
    "LAR": ("NFC", "NFC West"),
    "SF":  ("NFC", "NFC West"),
    "SEA": ("NFC", "NFC West"),
}


def extract_standings(
    standings_df: pd.DataFrame,
    team_elo: Optional[Mapping[str, float]] = None,
    team_meta: Optional[Mapping[str, Tuple[str, str]]] = None,
) -> List[TeamStanding]:
    """
    Convert a finished regular-season result into List[TeamStanding].

    Parameters
    ----------
    standings_df
        DataFrame returned by simulate_season (columns: team, wins, losses, points, elo).
    team_elo
        Optional dict team → final Elo. If omitted, the "elo" column of the
        DataFrame is used.
    team_meta
        Optional mapping team_id → (conference, division).
        Defaults to the built-in NFL_TEAM_META.

    Returns
    -------
    List[TeamStanding]
        Ready to pass to run_nfl_playoff_from_standings / seed_nfl_playoffs.
    """
    if team_meta is None:
        team_meta = NFL_TEAM_META

    if team_elo is None:
        team_elo = dict(zip(standings_df["team"], standings_df["elo"]))

    result: List[TeamStanding] = []

    for _, row in standings_df.iterrows():
        team = str(row["team"])
        wins = float(row["wins"])
        losses = float(row["losses"])
        # Avoid division by zero for 0-0 edge cases
        total = wins + losses
        win_pct = wins / total if total > 0 else 0.0

        conf, div = team_meta.get(team, ("UNKNOWN", "UNKNOWN"))

        result.append(
            TeamStanding(
                team_id=team,
                conference=conf,
                division=div,
                wins=wins,
                losses=losses,
                win_pct=win_pct,
                elo=float(team_elo.get(team, row.get("elo", 1500.0))),
            )
        )

    return result
