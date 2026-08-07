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


# Full display names → abbr (schedule / B-R style). Used when metadata import fails.
NHL_FULL_NAME_TO_ABBR: Dict[str, str] = {
    "Anaheim Ducks": "ANA",
    "Arizona Coyotes": "UTA",  # legacy
    "Boston Bruins": "BOS",
    "Buffalo Sabres": "BUF",
    "Calgary Flames": "CGY",
    "Carolina Hurricanes": "CAR",
    "Chicago Blackhawks": "CHI",
    "Colorado Avalanche": "COL",
    "Columbus Blue Jackets": "CBJ",
    "Dallas Stars": "DAL",
    "Detroit Red Wings": "DET",
    "Edmonton Oilers": "EDM",
    "Florida Panthers": "FLA",
    "Los Angeles Kings": "LAK",
    "Minnesota Wild": "MIN",
    "Montreal Canadiens": "MTL",
    "Nashville Predators": "NSH",
    "New Jersey Devils": "NJD",
    "New York Islanders": "NYI",
    "New York Rangers": "NYR",
    "Ottawa Senators": "OTT",
    "Philadelphia Flyers": "PHI",
    "Pittsburgh Penguins": "PIT",
    "San Jose Sharks": "SJS",
    "Seattle Kraken": "SEA",
    "St. Louis Blues": "STL",
    "Tampa Bay Lightning": "TBL",
    "Toronto Maple Leafs": "TOR",
    "Utah Hockey Club": "UTA",
    "Utah Mammoth": "UTA",
    "Vancouver Canucks": "VAN",
    "Vegas Golden Knights": "VGK",
    "Washington Capitals": "WSH",
    "Winnipeg Jets": "WPG",
}


def _name_to_abbr() -> Dict[str, str]:
    """Map full team name and abbr → canonical abbreviation."""
    mapping: Dict[str, str] = {}
    # Hardcoded full names first (works even if metadata is not importable)
    for name, abbr in NHL_FULL_NAME_TO_ABBR.items():
        mapping[name] = abbr
        mapping[name.lower()] = abbr
        mapping[abbr] = abbr
        mapping[abbr.upper()] = abbr
    try:
        from metadata import load_teams
        for abbr, meta in load_teams("NHL").items():
            mapping[abbr] = abbr
            mapping[abbr.upper()] = abbr
            name = meta.get("name")
            if name:
                mapping[name] = abbr
                mapping[name.lower()] = abbr
    except Exception:
        pass
    for abbr in NHL_TEAM_META:
        mapping[abbr] = abbr
        mapping[abbr.upper()] = abbr
    return mapping


def _resolve_team_id(team: str, name_map: Dict[str, str]) -> str:
    """Resolve schedule/standings team label to NHL_TEAM_META key (abbr)."""
    if team in name_map:
        return name_map[team]
    if team.upper() in name_map:
        return name_map[team.upper()]
    if team.lower() in name_map:
        return name_map[team.lower()]
    return team


def extract_standings(
    standings_df: pd.DataFrame,
    team_elo: Optional[Mapping[str, float]] = None,
    team_meta: Optional[Mapping[str, Tuple[str, str]]] = None,
) -> List[TeamStanding]:
    """
    Convert a finished regular-season result into List[TeamStanding].

    Expected columns in standings_df (flexible):
      - team (required) — abbreviation or full name
      - points (preferred) or wins
      - wins, losses (optional)
      - elo (fallback if team_elo not supplied)

    Full names (e.g. "Colorado Avalanche") are resolved to abbreviations
    (e.g. "COL") so conference/division lookup against NHL_TEAM_META works.
    """
    if team_meta is None:
        team_meta = NHL_TEAM_META

    name_map = _name_to_abbr()

    if team_elo is None:
        if "elo" in standings_df.columns:
            # Build elo dict under both raw and resolved keys
            team_elo = {}
            for _, row in standings_df.iterrows():
                raw = str(row["team"])
                tid = _resolve_team_id(raw, name_map)
                team_elo[raw] = float(row["elo"])
                team_elo[tid] = float(row["elo"])
        else:
            team_elo = {}
    else:
        # Ensure elo lookup works for both full names and abbrs
        resolved_elo: Dict[str, float] = dict(team_elo)
        for k, v in list(team_elo.items()):
            tid = _resolve_team_id(str(k), name_map)
            resolved_elo[tid] = float(v)
            resolved_elo[str(k)] = float(v)
        team_elo = resolved_elo

    result: List[TeamStanding] = []

    for _, row in standings_df.iterrows():
        raw_team = str(row["team"])
        team = _resolve_team_id(raw_team, name_map)

        wins = float(row["wins"]) if "wins" in standings_df.columns and pd.notna(row.get("wins")) else 0.0
        losses = float(row["losses"]) if "losses" in standings_df.columns and pd.notna(row.get("losses")) else 0.0

        # NHL primary ranking metric is points
        if "points" in standings_df.columns and pd.notna(row.get("points")):
            points = float(row["points"])
        else:
            # Fallback: treat wins as points (2 pts per win approximation)
            points = wins * 2.0

        total_games = wins + losses
        win_pct = wins / total_games if total_games > 0 else 0.0

        conf, div = team_meta.get(team, ("UNKNOWN", "UNKNOWN"))

        elo_val = team_elo.get(team, team_elo.get(raw_team, row.get("elo", 1500.0)))
        try:
            elo_val = float(elo_val)
        except (TypeError, ValueError):
            elo_val = 1500.0

        result.append(
            TeamStanding(
                team_id=team,
                conference=conf,
                division=div,
                wins=wins,
                losses=losses,
                points=points,
                win_pct=win_pct,
                elo=elo_val,
            )
        )

    return result
