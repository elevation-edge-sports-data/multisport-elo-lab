"""
Canonical engine state schema.

Defines the shared state structure exchanged between the
engine, transformation modules, and workflow scripts.
"""

from typing import Dict, Any, TypedDict


class EloState(TypedDict):
    """
    Canonical state object passed throughout the Elo engine
    during game execution.
    """
    
    home_elo: float
    away_elo: float

    context: Dict[str, Any]

    config: Dict[str, Any]

    postgame: Dict[str, Any]