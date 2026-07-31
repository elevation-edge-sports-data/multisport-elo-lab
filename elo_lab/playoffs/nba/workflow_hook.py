"""
Thin integration point for the existing season-simulation workflow.

Drop-in usage:

    from elo_lab.playoffs.nba.workflow_hook import run_playoffs_after_season

    standings_df, team_elo, elo_history = simulate_season(...)
    playoff_result = run_playoffs_after_season(standings_df, team_elo)
"""

from __future__ import annotations

import random
from typing import Dict, List, Mapping, Optional, Tuple

import pandas as pd

from .adapter import extract_standings
from .models import PlayoffResult, TeamStanding
from .simulation import run_nba_playoff_from_standings


def run_playoffs_after_season(
    standings_df: pd.DataFrame,
    team_elo: Optional[Mapping[str, float]] = None,
    home_advantage: float = 55.0,
    rng: Optional[random.Random] = None,
    team_meta: Optional[Mapping[str, Tuple[str, str]]] = None,
) -> PlayoffResult:
    """Convert season-sim output → NBA playoff simulation in one call."""
    standings: List[TeamStanding] = extract_standings(
        standings_df=standings_df,
        team_elo=team_elo,
        team_meta=team_meta,
    )
    return run_nba_playoff_from_standings(
        standings=standings,
        elo_lookup=dict(team_elo) if team_elo is not None else None,
        home_advantage=home_advantage,
        rng=rng,
    )


def accumulate_from_many_seasons(
    season_results: List[Tuple[pd.DataFrame, Dict[str, float]]],
    home_advantage: float = 55.0,
    base_seed: int = 42,
) -> Dict[str, Dict[str, float]]:
    """Convenience for Monte Carlo aggregation."""
    from collections import defaultdict

    counters: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    rounds = [
        "Play-In",
        "First Round",
        "Conference Semifinals",
        "Conference Finals",
        "NBA Finals",
        "Champion",
    ]
    n = len(season_results)

    for i, (standings_df, team_elo) in enumerate(season_results):
        rng = random.Random(base_seed + i)
        result = run_playoffs_after_season(
            standings_df=standings_df,
            team_elo=team_elo,
            home_advantage=home_advantage,
            rng=rng,
        )
        for team, reached in result.team_reached.items():
            for rnd in rounds:
                if reached.get(rnd, False):
                    counters[team][rnd] += 1

    return {
        team: {rnd: counts.get(rnd, 0) / n for rnd in rounds}
        for team, counts in counters.items()
    }
