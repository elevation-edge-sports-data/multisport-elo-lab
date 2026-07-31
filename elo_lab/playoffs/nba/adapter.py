"""
Adapter that converts Multisport Elo Lab season-simulation output
into the List[TeamStanding] expected by elo_lab.playoffs.nba.
"""

from __future__ import annotations

from typing import Dict, List, Mapping, Optional, Tuple

import pandas as pd

from .models import TeamStanding


# ---------------------------------------------------------------------------
# Canonical NBA conference / division map
# ---------------------------------------------------------------------------
NBA_TEAM_META: Dict[str, Tuple[str, str]] = {
    # Eastern – Atlantic
    "BOS": ("Eastern", "Atlantic"),
    "BKN": ("Eastern", "Atlantic"),
    "NYK": ("Eastern", "Atlantic"),
    "PHI": ("Eastern", "Atlantic"),
    "TOR": ("Eastern", "Atlantic"),
    # Eastern – Central
    "CHI": ("Eastern", "Central"),
    "CLE": ("Eastern", "Central"),
    "DET": ("Eastern", "Central"),
    "IND": ("Eastern", "Central"),
    "MIL": ("Eastern", "Central"),
    # Eastern – Southeast
    "ATL": ("Eastern", "Southeast"),
    "CHA": ("Eastern", "Southeast"),
    "MIA": ("Eastern", "Southeast"),
    "ORL": ("Eastern", "Southeast"),
    "WAS": ("Eastern", "Southeast"),
    # Western – Northwest
    "DEN": ("Western", "Northwest"),
    "MIN": ("Western", "Northwest"),
    "OKC": ("Western", "Northwest"),
    "POR": ("Western", "Northwest"),
    "UTA": ("Western", "Northwest"),
    # Western – Pacific
    "GSW": ("Western", "Pacific"),
    "LAC": ("Western", "Pacific"),
    "LAL": ("Western", "Pacific"),
    "PHX": ("Western", "Pacific"),
    "SAC": ("Western", "Pacific"),
    # Western – Southwest
    "DAL": ("Western", "Southwest"),
    "HOU": ("Western", "Southwest"),
    "MEM": ("Western", "Southwest"),
    "NOP": ("Western", "Southwest"),
    "SAS": ("Western", "Southwest"),
}


def extract_standings(
    standings_df: pd.DataFrame,
    team_elo: Optional[Mapping[str, float]] = None,
    team_meta: Optional[Mapping[str, Tuple[str, str]]] = None,
) -> List[TeamStanding]:
    """
    Convert a finished regular-season result into List[TeamStanding].

    Expected columns: team, wins, losses (or points), elo (optional).
    """
    if team_meta is None:
        team_meta = NBA_TEAM_META

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
