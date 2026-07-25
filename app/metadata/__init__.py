"""
Public metadata API for MultiSport Elo Lab.

This is the single preferred import location for team and venue data.
Other modules should import from here instead of reaching into the
individual team / venue modules.
"""

from typing import Any, Dict, List

from .nfl_teams import NFL_TEAMS
from .nhl_teams import NHL_TEAMS
from .nfl_venues import NFL_VENUES, get_elevation_bins as _nfl_bins, get_elevation_ft as _nfl_ft
from .nhl_venues import NHL_VENUES, get_elevation_bins as _nhl_bins, get_elevation_ft as _nhl_ft

# NBA is prepared but not yet fully integrated
try:
    from .nba_venues import NBA_VENUES, get_elevation_bins as _nba_bins, get_elevation_ft as _nba_ft
except ImportError:
    NBA_VENUES = {}
    def _nba_bins(): return {}
    def _nba_ft(): return {}

__all__ = [
    "NFL_TEAMS",
    "NHL_TEAMS",
    "NFL_VENUES",
    "NHL_VENUES",
    "NBA_VENUES",
    "load_teams",
    "load_venues",
    "get_elevation_bins",
    "get_elevation_ft",
    "get_team_metadata",
    "list_teams",
    "get_primary_color",
    "get_secondary_color",
    "get_sport_teams",
]


def load_teams(sport: str) -> Dict[str, Dict[str, Any]]:
    """Return the canonical team metadata dict for the given sport."""
    sport = sport.upper()
    if sport == "NFL":
        return NFL_TEAMS
    if sport == "NHL":
        return NHL_TEAMS
    raise ValueError(f"Unknown sport: {sport}. NBA teams not yet added.")


def load_venues(sport: str) -> Dict[str, Dict[str, Any]]:
    """Return venue metadata for the given sport."""
    sport = sport.upper()
    if sport == "NFL":
        return NFL_VENUES
    if sport == "NHL":
        return NHL_VENUES
    if sport == "NBA":
        return NBA_VENUES
    raise ValueError(f"Unknown sport: {sport}")


def get_elevation_bins(sport: str = "NFL") -> Dict[str, int]:
    """
    Return {team_abbr: elevation_bin} for Elevation Edge.
    Currently only NFL has meaningful bins.
    """
    sport = sport.upper()
    if sport == "NFL":
        return _nfl_bins()
    if sport == "NHL":
        return _nhl_bins()
    if sport == "NBA":
        return _nba_bins()
    return {}


def get_elevation_ft(sport: str) -> Dict[str, int]:
    """Return {team_abbr: elevation_ft} for the given sport."""
    sport = sport.upper()
    if sport == "NFL":
        return _nfl_ft()
    if sport == "NHL":
        return _nhl_ft()
    if sport == "NBA":
        return _nba_ft()
    return {}


def get_team_metadata(sport: str, abbr: str) -> Dict[str, Any]:
    """Return metadata for a single team (empty dict if unknown)."""
    return load_teams(sport).get(abbr, {})


def list_teams(sport: str) -> List[str]:
    """Sorted list of team abbreviations."""
    return sorted(load_teams(sport).keys())


def get_primary_color(sport: str, abbr: str, default: str = "#888888") -> str:
    return get_team_metadata(sport, abbr).get("primary_color", default)


def get_secondary_color(sport: str, abbr: str, default: str = "#CCCCCC") -> str:
    return get_team_metadata(sport, abbr).get("secondary_color", default)


def get_sport_teams(sport: str) -> Dict[str, Dict[str, Any]]:
    """Drop-in replacement for the old helper that lived in dashboard.py."""
    return load_teams(sport)
