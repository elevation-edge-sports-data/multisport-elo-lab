"""
Elo Lab

Version 5 — Architectural Framework Release

Public package interface.
"""

from .engine.game_runner import run_game

__version__ = "5.0"

__all__ = [
    "run_game",
]