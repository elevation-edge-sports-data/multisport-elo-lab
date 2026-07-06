"""
Home-field transformation.

Applies home-field advantage as a pregame Elo transformation.

This transformation modifies only the canonical state object.
It contains no orchestration logic and maintains no internal state.
"""

from typing import Any, Dict

# ==========================================================
# DEFAULT PARAMETERS
# ==========================================================

# Default home-field Elo adjustment (used if config value is missing)
DEFAULT_HFA = 55


# ==========================================================
# TRANSFORMATION
# ==========================================================

def apply(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Applies home-field Elo adjustment to the home team if enabled
    in the configuration.
    """

    config = state["config"]

    adjustment = config["adjustments"]["home_field"]

    if not adjustment["enabled"]:
        return state
    
    # Apply additive home-field Elo shift to home team only
    state["home_elo"] += adjustment.get(
        "value",
        DEFAULT_HFA,
    )

    return state