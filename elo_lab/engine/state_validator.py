"""
Engine state validation.

Performs lightweight validation of the canonical Elo engine
state before game execution.
"""

from .state_schema import EloState


def validate_state(state: dict) -> None:
    """
    Validates the required structure of the canonical engine
    state object before pipeline execution.
    """
    
    required_keys = ["home_elo", "away_elo", "context", "config", "postgame"]

    for key in required_keys:
        if key not in state:
            raise ValueError(f"Missing state field: {key}")

    if not isinstance(state["context"], dict):
        raise TypeError("context must be dict")

    if not isinstance(state["config"], dict):
        raise TypeError("config must be dict")

    if not isinstance(state["postgame"], dict):
        raise TypeError("postgame must be dict")