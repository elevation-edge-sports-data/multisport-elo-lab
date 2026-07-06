"""
Game Runner (Elo Lab Engine Orchestrator)

Canonical game execution entry point for the Elo engine.

Responsibilities
----------------
- Build canonical state
- Validate state
- Execute transformation pipeline
- Compute win probability
- Perform Elo update
- Return standardized game results

This module contains no sport-specific logic.
"""

from typing import Any, Dict

from .pipeline import apply_adjustments
from .probability import win_probability
from .updates import update_ratings
from .state_validator import validate_state


# ==========================================================
# GAME EXECUTION
# ==========================================================

def run_game(
    home_elo: float,
    away_elo: float,
    context: Dict[str, Any],
    config: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Executes a single game through the complete Elo engine
    pipeline and returns standardized game results.
    """

    state = {
        "home_elo": float(home_elo),
        "away_elo": float(away_elo),
        "context": context,
        "config": config,
        "postgame": {},
    }

    validate_state(state)

    # ======================================================
    # TRANSFORMATION PIPELINE
    # ======================================================

    state = apply_adjustments(
        home_elo=state["home_elo"],
        away_elo=state["away_elo"],
        context=state["context"],
        config=state["config"],
    )
    # ======================================================
    # WIN PROBABILITY
    # ======================================================

    p_home = win_probability(
        state["home_elo"],
        state["away_elo"],
    )

    # ======================================================
    # GAME OUTCOME
    # ======================================================

    context = state["context"]

    if "actual" in context:
        actual = int(context["actual"])

    elif "home_score" in context and "away_score" in context:
        actual = int(
            context["home_score"] > context["away_score"]
        )

    else:
        raise ValueError(
            "Context must contain either 'actual' or both "
            "'home_score' and 'away_score'."
        )

    # ======================================================
    # ELO UPDATE
    # ======================================================

    multiplier = state["postgame"].get("mov_multiplier", 1.0)

    home_post, away_post = update_ratings(
        home_elo=home_elo,
        away_elo=away_elo,
        actual=actual,
        p_home=p_home,
        k=config.get("k", 20),
        multiplier=multiplier,
    )

    return {
        "home_elo_pre": home_elo,
        "away_elo_pre": away_elo,
        "home_elo_adjusted": state["home_elo"],
        "away_elo_adjusted": state["away_elo"],
        "p_home": float(p_home),
        "actual": actual,
        "multiplier": multiplier,
        "home_elo_post": float(home_post),
        "away_elo_post": float(away_post),
    }