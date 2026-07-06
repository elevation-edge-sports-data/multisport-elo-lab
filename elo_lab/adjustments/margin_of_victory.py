"""
Margin-of-victory transformation.

Computes a postgame margin-of-victory multiplier used by the
Elo rating update step.

Attaches the result to the canonical state without modifying
Elo ratings directly.
"""

from typing import Any, Dict

import numpy as np

# ==========================================================
# DEFAULT PARAMETERS
# ==========================================================

DEFAULT_MOV_SCALE = 1.0

# Bounds applied to the margin-of-victory multiplier
MIN_MULTIPLIER = 0.25
MAX_MULTIPLIER = 3.00


# ==========================================================
# TRANSFORMATION
# ==========================================================

def apply(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes and attaches the margin-of-victory multiplier to the
    postgame state using score differential and configured scaling.
    """

    config = state["config"]

    adjustment = config["adjustments"]["margin_of_victory"]

    postgame = state.setdefault("postgame", {})

    if not adjustment["enabled"]:

        postgame["mov_multiplier"] = 1.0

        return state

    context = state["context"]

    margin = abs(context["home_score"] - context["away_score"])

    scale = adjustment.get("scale", DEFAULT_MOV_SCALE)

    multiplier = np.log(margin + 1) * scale

    multiplier = min(max(multiplier, MIN_MULTIPLIER), MAX_MULTIPLIER)

    postgame["mov_multiplier"] = float(multiplier)

    return state