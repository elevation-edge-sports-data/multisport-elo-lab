"""
Public metadata API for MultiSport Elo Lab.

This is the single preferred import location for team and venue data.
Other modules should import from here instead of reaching into the
individual team / venue modules.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from .nfl_teams import NFL_TEAMS
from .nhl_teams import NHL_TEAMS
from .nfl_venues import NFL_VENUES, get_elevation_bins as _nfl_bins, get_elevation_ft as _nfl_ft
from .nhl_venues import NHL_VENUES, get_elevation_bins as _nhl_bins, get_elevation_ft as _nhl_ft

# NBA teams + venues
try:
    from .nba_teams import NBA_TEAMS
except ImportError:
    NBA_TEAMS = {}

try:
    from .nba_venues import NBA_VENUES, get_elevation_bins as _nba_bins, get_elevation_ft as _nba_ft
except ImportError:
    NBA_VENUES = {}

    def _nba_bins():
        return {}

    def _nba_ft():
        return {}


# ---------------------------------------------------------------------------
# Logo asset resolution
# ---------------------------------------------------------------------------
# Preferred layout (sport subfolders):
#   app/assets/logos/nhl/COL.png
#   app/assets/logos/nfl/DEN.png
#   app/assets/logos/nba/BOS.png
#
# Fallback (legacy flat layout):
#   app/assets/logos/COL.png
_LOGO_ROOT = Path(__file__).resolve().parent.parent / "assets" / "logos"


__all__ = [
    "NFL_TEAMS",
    "NHL_TEAMS",
    "NBA_TEAMS",
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
    # Logo helpers
    "get_logo_dir",
    "get_logo_filename",
    "get_logo_path",
    "logo_exists",
    "resolve_team_abbr",
]


def load_teams(sport: str) -> Dict[str, Dict[str, Any]]:
    """Return the canonical team metadata dict for the given sport."""
    sport = sport.upper()
    if sport == "NFL":
        return NFL_TEAMS
    if sport == "NHL":
        return NHL_TEAMS
    if sport == "NBA":
        return NBA_TEAMS
    raise ValueError(f"Unknown sport: {sport}")


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
    abbr = resolve_team_abbr(sport, abbr)
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


# ---------------------------------------------------------------------------
# Logo helpers
# ---------------------------------------------------------------------------

def resolve_team_abbr(sport: str, team_key: str) -> str:
    """
    Map a team key (abbreviation OR full name) to the canonical abbreviation.

    Simulation results sometimes store full names ("Utah Hockey Club") while
    metadata and logo files are keyed by abbreviation ("UTA").
    """
    if not team_key:
        return team_key
    teams = load_teams(sport)
    if team_key in teams:
        return team_key
    # Case-insensitive abbr match
    upper = team_key.upper()
    if upper in teams:
        return upper
    # Full-name match
    for abbr, meta in teams.items():
        name = meta.get("name") or ""
        if name == team_key or name.lower() == team_key.lower():
            return abbr
    # Partial: last word match (e.g. "Hockey Club" won't work, but "Utah" edge cases)
    return team_key


def get_logo_dir(sport: Optional[str] = None) -> Path:
    """
    Absolute path to the logo directory.

    If sport is given, returns the sport subfolder
    (e.g. app/assets/logos/nhl/). Otherwise returns the root.
    """
    if sport:
        return _LOGO_ROOT / sport.lower()
    return _LOGO_ROOT


def get_logo_filename(sport: str, abbr: str) -> Optional[str]:
    """
    Return the logo filename declared in team metadata (e.g. 'UTA.png'),
    or None if the team has no logo entry.
    """
    abbr = resolve_team_abbr(sport, abbr)
    return load_teams(sport).get(abbr, {}).get("logo")


def get_logo_path(sport: str, abbr: str) -> Optional[Path]:
    """
    Resolve the on-disk path for a team's logo.

    Search order (after resolving abbr from full name if needed):
      1. app/assets/logos/{sport}/UTA.png   (preferred – sport subfolders)
      2. app/assets/logos/UTA.png           (legacy flat layout)
      3. Case-insensitive filename match inside the sport folder

    Returns a Path only when the file actually exists; otherwise None.
    """
    abbr = resolve_team_abbr(sport, abbr)
    filename = get_logo_filename(sport, abbr)
    if not filename:
        # Last resort: try {abbr}.png even if metadata has no logo field
        filename = f"{abbr}.png"

    sport_dir = _LOGO_ROOT / sport.lower()

    # 1. Exact path in sport subfolder
    candidate = sport_dir / filename
    if candidate.is_file():
        return candidate

    # 2. Legacy flat layout
    candidate = _LOGO_ROOT / filename
    if candidate.is_file():
        return candidate

    # 3. Case-insensitive scan of sport folder (Windows-friendly)
    if sport_dir.is_dir():
        target = filename.lower()
        for p in sport_dir.iterdir():
            if p.is_file() and p.name.lower() == target:
                return p
        # Also try abbr.png case-insensitively
        target2 = f"{abbr}.png".lower()
        for p in sport_dir.iterdir():
            if p.is_file() and p.name.lower() == target2:
                return p

    return None


def logo_exists(sport: str, abbr: str) -> bool:
    """True when a logo file is present on disk for the given team."""
    return get_logo_path(sport, abbr) is not None
