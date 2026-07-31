"""
Adapter that converts Multisport Elo Lab season-simulation output
into the List[TeamStanding] expected by elo_lab.playoffs.nhl.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Tuple

import pandas as pd

from .models import TeamStanding


# ---------------------------------------------------------------------------
# Canonical NHL conference / division map
# ---------------------------------------------------------------------------
NHL_TEAM_META: Dict[str, Tuple[str, str]] = {
    # Eastern – Atlantic
    "BOS": ("Eastern", "Atlantic"),
    "BUF": ("Eastern", "Atlantic"),
    "DET": ("Eastern", "Atlantic"),
    "FLA": ("Eastern", "Atlantic"),
    "MTL": ("Eastern", "Atlantic"),
    "OTT": ("Eastern", "Atlantic"),
    "TBL": ("Eastern", "Atlantic"),
    "TOR": ("Eastern", "Atlantic"),
    # Eastern – Metropolitan
    "CAR": ("Eastern", "Metropolitan"),
    "CBJ": ("Eastern", "Metropolitan"),
    "NJD": ("Eastern", "Metropolitan"),
    "NYI": ("Eastern", "Metropolitan"),
    "NYR": ("Eastern", "Metropolitan"),
    "PHI": ("Eastern", "Metropolitan"),
    "PIT": ("Eastern", "Metropolitan"),
    "WSH": ("Eastern", "Metropolitan"),
    # Western – Central
    "CHI": ("Western", "Central"),
    "COL": ("Western", "Central"),
    "DAL": ("Western", "Central"),
    "MIN": ("Western", "Central"),
    "NSH": ("Western", "Central"),
    "STL": ("Western", "Central"),
    "UTA": ("Western", "Central"),
    "WPG": ("Western", "Central"),
    # Western – Pacific
    "ANA": ("Western", "Pacific"),
    "CGY": ("Western", "Pacific"),
    "EDM": ("Western", "Pacific"),
    "LAK": ("Western", "Pacific"),
    "SJS": ("Western", "Pacific"),
    "SEA": ("Western", "Pacific"),
    "VAN": ("Western", "Pacific"),
    "VGK": ("Western", "Pacific"),
}


def extract_standings(
    standings_df: pd.DataFrame,
    team_elo: Optional[Mapping[str, float]] = None,
    team_meta: Optional[Mapping[str, Tuple[str, str]]] = None,
) -> List[TeamStanding]:
    """
    Convert a finished regular-season result into List[TeamStanding].

    Expected columns in standings_df (flexible):
      - team (required)
      - points (preferred) or wins
      - wins, losses (optional)
      - elo (fallback if team_elo not supplied)
    """
    if team_meta is None:
        team_meta = NHL_TEAM_META

    if team_elo is None:
        if "elo" in standings_df.columns:
            team_elo = dict(zip(standings_df["team"], standings_df["elo"]))
        else:
            team_elo = {}

    result: List[TeamStanding] = []

    for _, row in standings_df.iterrows():
        team = str(row["team"])
        wins = float(row.get("wins", 0.0))
        losses = float(row.get("losses", 0.0))

        # NHL primary ranking metric is points
        if "points" in standings_df.columns:
            points = float(row["points"])
        else:
            # Fallback: treat wins as points (2 pts per win approximation)
            points = wins * 2.0

        total_games = wins + losses
        win_pct = wins / total_games if total_games > 0 else 0.0

        conf, div = team_meta.get(team, ("UNKNOWN", "UNKNOWN"))

        result.append(
            TeamStanding(
                team_id=team,
                conference=conf,
                division=div,
                wins=wins,
                losses=losses,
                points=points,
                win_pct=win_pct,
                elo=float(team_elo.get(team, row.get("elo", 1500.0))),
            )
        )

    return result
