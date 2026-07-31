"""
NFL Playoff simulation package for Multisport Elo Lab.

Public API
----------
- models.TeamStanding, GameResult, RoundResult, PlayoffResult
- seeding.seed_nfl_playoffs
- simulation.simulate_nfl_playoffs, run_nfl_playoff_from_standings
- adapter.extract_standings, NFL_TEAM_META
- workflow_hook.run_playoffs_after_season, accumulate_from_many_seasons
- integration.accumulate_playoff_probabilities  (original Monte-Carlo helper)
"""

from .models import GameResult, PlayoffResult, RoundResult, TeamStanding
from .seeding import seed_nfl_playoffs
from .simulation import run_nfl_playoff_from_standings, simulate_nfl_playoffs
from .adapter import extract_standings, NFL_TEAM_META
from .workflow_hook import run_playoffs_after_season, accumulate_from_many_seasons
from .integration import accumulate_playoff_probabilities

__all__ = [
    "TeamStanding",
    "GameResult",
    "RoundResult",
    "PlayoffResult",
    "seed_nfl_playoffs",
    "simulate_nfl_playoffs",
    "run_nfl_playoff_from_standings",
    "extract_standings",
    "NFL_TEAM_META",
    "run_playoffs_after_season",
    "accumulate_from_many_seasons",
    "accumulate_playoff_probabilities",
]
