"""
Elevation Edge Adjustment (continuous)

Gives the home team an advantage proportional to the elevation
difference in feet. Uses raw elevation_ft from the metadata layer.

Replaces the previous binned implementation.
"""

from typing import Any, Dict

from metadata import get_elevation_ft

# Default scale: Elo points per 1000 ft of elevation advantage.
# Tunable via config["adjustments"]["elevation_edge"]["value"]
DEFAULT_SCALE = 15.0  # ≈ 15 Elo points per 1000 ft


def apply(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply continuous Elevation Edge to home_elo.

    boost = scale * max(0, home_ft - away_ft) / 1000

    Matches the style of home_field.py:
    - reads config from state["config"]
    - mutates state["home_elo"]
    - returns state
    """
    config = state["config"]
    adj = config.get("adjustments", {}).get("elevation_edge", {})

    if not adj.get("enabled", False):
        return state

    context = state.get("context", {})
    home_team = context.get("home_team")
    away_team = context.get("away_team")
    sport = context.get("sport", "NFL").upper()

    if not home_team or not away_team:
        return state

    elev = get_elevation_ft(sport)
    home_ft = float(elev.get(home_team, 0) or 0)
    away_ft = float(elev.get(away_team, 0) or 0)

    delta_ft = max(0.0, home_ft - away_ft)
    if delta_ft == 0.0:
        return state

    scale = float(adj.get("value", DEFAULT_SCALE))
    boost = scale * (delta_ft / 1000.0)

    state["home_elo"] += boost
    # Optional diagnostic key (useful for logging / evaluation)
    state["elevation_boost"] = boost

    return state
