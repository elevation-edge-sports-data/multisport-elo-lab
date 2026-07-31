"""
NHL Playoff simulation package for Multisport Elo Lab.

Public API
----------
- models.TeamStanding, GameResult, SeriesResult, RoundResult, PlayoffResult
- seeding.seed_nhl_playoffs
- simulation.simulate_nhl_playoffs, run_nhl_playoff_from_standings
- adapter.extract_standings, NHL_TEAM_META
- workflow_hook.run_playoffs_after_season, accumulate_from_many_seasons
- integration.accumulate_playoff_probabilities
"""

from .models import GameResult, PlayoffResult, RoundResult, SeriesResult, TeamStanding
from .seeding import seed_nhl_playoffs
from .simulation import run_nhl_playoff_from_standings, simulate_nhl_playoffs
from .adapter import extract_standings, NHL_TEAM_META
from .workflow_hook import run_playoffs_after_season, accumulate_from_many_seasons
from .integration import accumulate_playoff_probabilities

__all__ = [
    "TeamStanding",
    "GameResult",
    "SeriesResult",
    "RoundResult",
    "PlayoffResult",
    "seed_nhl_playoffs",
    "simulate_nhl_playoffs",
    "run_nhl_playoff_from_standings",
    "extract_standings",
    "NHL_TEAM_META",
    "run_playoffs_after_season",
    "accumulate_from_many_seasons",
    "accumulate_playoff_probabilities",
]
