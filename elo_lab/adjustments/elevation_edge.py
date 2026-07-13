"""
Elevation Edge Adjustment

Gives the home team an advantage when playing at higher elevation.
Uses a binned elevation ranking system to avoid overfitting to raw elevation values.

Bin structure:
- Bin 5: Denver only
- Bin 4: Arizona + Las Vegas
- Bin 3: Atlanta + Kansas City + Buffalo
- Bin 2, 1, 0: Remaining teams (lower elevations)
"""

from typing import Any, Dict


ELEVATION_BINS: Dict[str, int] = {
    # Bin 5 (+5) — Highest elevation
    "DEN": 5,

    # Bin 4 (+4)
    "ARI": 4,
    "LV": 4,

    # Bin 3 (+3)
    "ATL": 3,
    "KC": 3,
    "BUF": 3,

    # Bin 2 (+2)
    "IND": 2,
    "PIT": 2,
    "CAR": 2,
    "GB": 2,
    "CIN": 2,
    "CLE": 2,

    # Bin 1 (+1)
    "CHI": 1,
    "MIN": 1,
    "TEN": 1,
    "JAX": 1,
    "PHI": 1,
    "BAL": 1,
    "WAS": 1,
    "DET": 1,
    "HOU": 1,

    # Bin 0 (0) — Sea level / lowest elevation
    "NYG": 0,
    "NYJ": 0,
    "MIA": 0,
    "TB": 0,
    "NO": 0,
    "LAC": 0,
    "LAR": 0,
    "SF": 0,
    "SEA": 0,
    "DAL": 0,
    "NE": 0,
}


def apply(state: Dict[str, Any], config: Dict[str, Any]) -> None:
    """
    Apply Elevation Edge adjustment to the game state.

    Adds a boost to the home team's rating when they have a higher
    elevation bin than the away team.
    """
    context = state.get("context", {})
    home_team = context.get("home_team")
    away_team = context.get("away_team")

    if not home_team or not away_team:
        return

    home_bin = ELEVATION_BINS.get(home_team, 0)
    away_bin = ELEVATION_BINS.get(away_team, 0)

    bin_advantage = max(0, home_bin - away_bin)

    if bin_advantage == 0:
        return

    # Get the tunable parameter (defaults to 0 if not set)
    elevation_config = (
        config.get("adjustments", {})
        .get("elevation_edge", {})
    )
    elevation_param = elevation_config.get("value", 0)

    if elevation_param == 0:
        return

    # Apply linear boost based on bin difference
    boost = elevation_param * bin_advantage

    # Apply boost to home team's rating (or rating difference)
    # Adjust this line if your state structure uses a different key
    if "ratings" in state:
        state["ratings"][home_team] = state["ratings"].get(home_team, 1500) + boost
    elif "rating_diff" in state:
        state["rating_diff"] += boost
    else:
        # Fallback: store in a custom key for later processing
        state.setdefault("elevation_boost", 0)
        state["elevation_boost"] += boost