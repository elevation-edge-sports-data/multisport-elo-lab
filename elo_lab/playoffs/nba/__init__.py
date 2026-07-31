"""
NBA Playoff simulation package for Multisport Elo Lab.

Public API
----------
- models.TeamStanding, GameResult, SeriesResult, RoundResult, PlayoffResult
- seeding.seed_nba_playoffs
- simulation.simulate_nba_playoffs, run_nba_playoff_from_standings
- adapter.extract_standings, NBA_TEAM_META
- workflow_hook.run_playoffs_after_season, accumulate_from_many_seasons
- integration.accumulate_playoff_probabilities
"""

from .models import GameResult, PlayoffResult, RoundResult, SeriesResult, TeamStanding
from .seeding import seed_nba_playoffs
from .simulation import run_nba_playoff_from_standings, simulate_nba_playoffs
from .adapter import extract_standings, NBA_TEAM_META
from .workflow_hook import run_playoffs_after_season, accumulate_from_many_seasons
from .integration import accumulate_playoff_probabilities

__all__ = [
    "TeamStanding",
    "GameResult",
    "SeriesResult",
    "RoundResult",
    "PlayoffResult",
    "seed_nba_playoffs",
    "simulate_nba_playoffs",
    "run_nba_playoff_from_standings",
    "extract_standings",
    "NBA_TEAM_META",
    "run_playoffs_after_season",
    "accumulate_from_many_seasons",
    "accumulate_playoff_probabilities",
]
