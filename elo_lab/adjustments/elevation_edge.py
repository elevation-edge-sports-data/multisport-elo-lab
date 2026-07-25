"""
Elevation Edge Adjustment

Gives the home team an advantage when playing at higher elevation.
Uses a binned elevation ranking system to avoid overfitting to raw elevation values.

Bins are now loaded from the central metadata layer (app/metadata/nfl_venues.py).
"""

from typing import Any, Dict

from metadata import get_elevation_bins


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

    bins = get_elevation_bins("NFL")  # currently only NFL uses elevation
    home_bin = bins.get(home_team, 0)
    away_bin = bins.get(away_team, 0)

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
