"""
Game Runner (Elo Lab Engine Orchestrator)

Canonical game execution entry point for the Elo engine.

Responsibilities
----------------
- Compute deterministic pregame state
- Execute postgame transformations
- Perform Elo update
- Return standardized game results

This module contains no sport-specific logic.
"""

from typing import Any, Dict

from .pregame import compute_pregame
from .pipeline import apply_postgame_adjustments
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
    Executes a completed game through the Elo engine.

    Workflow:
    1. Compute deterministic pregame adjusted probability
    2. Determine observed outcome
    3. Apply postgame transformations
    4. Update Elo ratings
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
    # PREGAME CALCULATION
    # ======================================================

    pregame = compute_pregame(
        home_elo=home_elo,
        away_elo=away_elo,
        context=context,
        config=config,
    )

    p_home = pregame["p_home"]

    # ======================================================
    # GAME OUTCOME
    # ======================================================

    if "actual" in context:
        actual = int(context["actual"])

    elif (
        "home_score" in context
        and "away_score" in context
    ):
        actual = int(
            context["home_score"]
            >
            context["away_score"]
        )

    else:
        raise ValueError(
            "Context must contain either 'actual' "
            "or both 'home_score' and 'away_score'."
        )

    # ======================================================
    # POSTGAME PIPELINE
    # ======================================================

    state = apply_postgame_adjustments(
        home_elo=home_elo,
        away_elo=away_elo,
        context=context,
        config=config,
    )

    multiplier = state["postgame"].get(
        "mov_multiplier",
        1.0,
    )

    # ======================================================
    # ELO UPDATE
    # ======================================================

    home_post, away_post = update_ratings(
        home_elo=home_elo,
        away_elo=away_elo,
        actual=actual,
        p_home=p_home,
        k=config.get(
            "k",
            20,
        ),
        multiplier=multiplier,
    )

    return {
        "home_elo_pre": home_elo,
        "away_elo_pre": away_elo,
        "home_elo_adjusted": pregame[
            "home_elo_adjusted"
        ],
        "away_elo_adjusted": pregame[
            "away_elo_adjusted"
        ],
        "p_home": float(p_home),
        "actual": actual,
        "multiplier": multiplier,
        "home_elo_post": float(home_post),
        "away_elo_post": float(away_post),
    }