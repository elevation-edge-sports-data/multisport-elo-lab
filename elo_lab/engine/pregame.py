"""
Deterministic pregame engine calculations.

Computes adjusted Elo ratings and win probabilities
without sampling outcomes or updating ratings.
"""

from typing import Any, Dict

from .pipeline import apply_pregame_adjustments
from .probability import win_probability
from .state_validator import validate_state


def compute_pregame(
    home_elo: float,
    away_elo: float,
    context: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Computes canonical pregame Elo state.

    Returns adjusted Elo ratings and home win probability.

    Does not:
    - sample outcomes
    - execute postgame transformations
    - update Elo ratings
    """

    state = {
        "home_elo": float(home_elo),
        "away_elo": float(away_elo),
        "context": dict(context),
        "config": config,
        "postgame": {},
    }

    validate_state(state)

    state = apply_pregame_adjustments(
        home_elo=state["home_elo"],
        away_elo=state["away_elo"],
        context=state["context"],
        config=state["config"],
    )

    p_home = win_probability(
        state["home_elo"],
        state["away_elo"],
    )

    return {
        "home_elo_pre": float(home_elo),
        "away_elo_pre": float(away_elo),
        "home_elo_adjusted": state["home_elo"],
        "away_elo_adjusted": state["away_elo"],
        "p_home": float(p_home),
    }